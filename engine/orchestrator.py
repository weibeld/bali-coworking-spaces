import os
import yaml
import json
import re
import httpx
import asyncio
import sys
from typing import Any, Dict, List, Set, Optional
from google import genai
from dotenv import load_dotenv
from jsonpath_ng import jsonpath, parse

# Setup paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Load keys with explicit paths
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env")) # Root .env
load_dotenv(dotenv_path=os.path.join(SCRIPT_DIR, ".env"), override=True) # engine/.env

class DatapilotEngine:
    def __init__(self, config_path: str, interactive: bool = False):
        print(f"📖 Loading Config: {config_path}...")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        self.client = genai.Client(api_key=self.gemini_key)
        self.schema = self.config.get("schema", {})
        self.model_id = "gemini-flash-latest"
        self.interactive = interactive
        
        # Build Dependency Graph & Order
        self.dependencies = self._get_dependencies()
        self.execution_order = self._determine_execution_order()
        self.root_fields = [f for f, d in self.dependencies.items() if len(d) == 0]

    def _get_dependencies(self) -> Dict[str, Set[str]]:
        deps = {}
        for field, spec in self.schema.items():
            spec_str = str(spec)
            found = re.findall(r"\$(\w+)", spec_str)
            deps[field] = set(found)
        return deps

    def _determine_execution_order(self) -> List[str]:
        ordered = []
        visited = set()
        def visit(node):
            if node in visited: return
            for dep in self.dependencies.get(node, []):
                visit(dep)
            visited.add(node)
            ordered.append(node)
        for node in self.schema:
            visit(node)
        return ordered

    def extract_raw_json(self, data: Any, path: str) -> Any:
        """Uses JSONPath to extract data. Handles both absolute and relative paths."""
        try:
            # If path refers to the root list but we are in a single item, strip the prefix
            if path.startswith("$.places[*]"):
                path = "$" + path[len("$.places[*]"):]
            
            jsonpath_expr = parse(path)
            matches = jsonpath_expr.find(data)
            if not matches: return None
            return [m.value for m in matches] if len(matches) > 1 else matches[0].value
        except Exception as e:
            print(f"   ⚠️ Extraction Error: {e}")
            return None

    def synthesize_anchor_call(self) -> Dict[str, Any]:
        """Ask LLM to compile the root source intent into an API call."""
        anchor_source = self.schema[self.root_fields[0]].get("source_llm")
        root_specs = [self.schema[f] for f in self.root_fields]

        prompt = f"""
        Construct a Google Places API (New) 'searchText' request for SOURCE: {anchor_source}.
        ENDPOINT: https://places.googleapis.com/v1/places:searchText
        METHOD: POST
        
        CRITICAL SCHEMA RULES (v1):
        1. Use camelCase for all keys (e.g., 'textQuery', 'locationBias').
        2. CIRCLES: Only supported in 'locationBias', NOT 'locationRestriction'.
           Example: {{"textQuery": "...", "locationBias": {{"circle": {{"center": {{"latitude": -8.748, "longitude": 115.167}}, "radius": 40000.0}}}}}}
        3. RECTANGLES: Supported in both 'locationBias' and 'locationRestriction'.
        4. FieldMask (Header): "places.id,places.displayName,places.location,places.rating,places.userRatingCount,places.websiteUri,places.googleMapsUri"

        FIELDS TO SATISFY: {json.dumps(root_specs, indent=2)}
        
        RETURN JSON with keys: url, method, headers, body.
        """
        if self.interactive:
            print(f"\n[DEBUG] --- LLM REQUEST: SYNTHESIS ---")
            print(prompt)
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        if self.interactive:
            print(f"\n[DEBUG] --- LLM RESPONSE: SYNTHESIS ---")
            print(response.text)
        
        return json.loads(response.text)

    async def fetch_initial_data(self) -> List[Dict[str, Any]]:
        """Synthesizes, executes, and maps the root source data."""
        req = self.synthesize_anchor_call()
        if self.interactive:
            print(f"\n[DEBUG] --- API REQUEST: DATA FETCHING ---")
            print(f"URL: {req['url']}")
            print(f"Headers: {json.dumps(req['headers'], indent=2)}")
            print(f"Body: {json.dumps(req['body'], indent=2)}")
        
        headers = req['headers']
        headers["X-Goog-Api-Key"] = self.maps_key
        headers = {k: str(v) for k, v in headers.items() if v is not None}

        async with httpx.AsyncClient() as client:
            resp = await client.post(req['url'], json=req.get('body', {}), headers=headers)
            if self.interactive:
                print(f"\n[DEBUG] --- API RESPONSE: DATA FETCHING ---")
                print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Error Content: {resp.text}")
                return []
            raw_data = resp.json()
        
        places = raw_data.get("places", [])
        print(f"\n   ✅ Received {len(places)} candidates from API.")
        
        results = []
        for p in places:
            row = {}
            keep = True
            for f in self.root_fields:
                spec = self.schema[f]
                val = self.extract_raw_json(p, spec.get("extract_raw", ""))
                
                if "constraints_raw" in spec:
                    rule = spec["constraints_raw"]
                    if ">=" in rule:
                        try:
                            threshold = int(rule.split(">=")[1].strip())
                            if val is None or int(val) < threshold: keep = False
                        except: pass
                
                row[f] = val
            
            if keep: 
                results.append(row)
                if self.interactive:
                    print(f"      📍 Fetched: {row.get('name')} (Rating: {row.get('rating')})")
        
        print(f"   🎯 {len(results)} candidates satisfied initial constraints.")
        return results

    def execute_join(self, field_name: str, row: Dict[str, Any]) -> Any:
        """Executes LLM join for a dependent field."""
        spec = self.schema[field_name]
        source_text = spec.get("source_llm", "")
        extract_instr = spec.get("extract_llm", "")
        for k, v in row.items():
            source_text = source_text.replace(f"${k}", str(v))
            extract_instr = extract_instr.replace(f"${k}", str(v))

        prompt = f"CONTEXT: {source_text}\n\nINSTRUCTION: {extract_instr}\n\nReturn JSON: {{ '{field_name}': ... }}"
        if self.interactive:
            print(f"\n   [DEBUG] --- LLM REQUEST: JOIN {field_name} ---")
            print(prompt)
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        if self.interactive:
            print(f"\n   [DEBUG] --- LLM RESPONSE: JOIN {field_name} ---")
            print(response.text)
        
        try:
            res = json.loads(response.text)
            return res.get(field_name)
        except:
            return response.text

    def print_table(self, data: List[Dict[str, Any]]):
        """Prints the final result set in a readable ASCII table."""
        if not data:
            print("\n⚠️ No data found to display.")
            return

        # Select columns to display
        cols = ["name", "rating", "rating_count", "coworking_confidence", "website_url"]
        widths = {c: len(c) + 2 for c in cols}
        
        # Calculate max widths
        for row in data:
            for c in cols:
                val = str(row.get(c, ""))[:40] # Truncate long strings
                widths[c] = max(widths[c], len(val) + 2)

        # Print Header
        print("\n" + "┌" + "┬".join("─" * widths[c] for c in cols) + "┐")
        print("│" + "│".join(c.upper().center(widths[c]) for c in cols) + "│")
        print("├" + "┼".join("─" * widths[c] for c in cols) + "┤")

        # Print Rows
        for row in data:
            line = "│"
            for c in cols:
                val = str(row.get(c, ""))[:widths[c]-2]
                line += val.ljust(widths[c]) + "│"
            print(line)

        print("└" + "┴".join("─" * widths[c] for c in cols) + "┘")

    async def execute(self, limit: int = 3):
        print("\n🚀 STEP 1: INITIAL DATA FETCHING")
        print("-" * 40)
        rows = await self.fetch_initial_data()
        
        print("\n🚀 STEP 2: EXECUTING JOINS")
        print("-" * 40)
        final_dataset = []
        
        for i, row in enumerate(rows[:limit]):
            name = row.get('name', 'Unknown')
            if self.interactive:
                print(f"\n" + "="*80)
                print(f"📦 [{i+1}/{len(rows[:limit])}] PROCESSING: {name}")
                print("="*80)
                print(f"   Current Data: {json.dumps(row, indent=2)}")
            else:
                print(f"📦 [{i+1}/{len(rows[:limit])}] Processing: {name}...")
            
            for field in self.execution_order:
                if field in self.root_fields: continue
                
                if self.interactive:
                    print(f"   -> Executing Join: '{field}'...")
                
                val = self.execute_join(field, row)
                row[field] = val
                
                if self.interactive:
                    print(f"      ✅ Result: {val}")
                
                spec = self.schema[field]
                if "constraints_raw" in spec:
                    rule = spec["constraints_raw"]
                    try:
                        if ">=" in rule and int(val) < int(rule.split(">=")[1]):
                            if self.interactive:
                                print(f"   ❌ Rejected: {field} value {val} failed {rule}")
                            row = None
                            break
                    except: pass
            
            if row: 
                final_dataset.append(row)
                if self.interactive:
                    print(f"\n✅ SUCCESS: Final Row for {name}:")
                    print(json.dumps(row, indent=2))
            
            if self.interactive and i < len(rows[:limit]) - 1:
                input("\n[PAUSE] Press ENTER to continue to next candidate... ")

        print("\n" + "=" * 80)
        print("🎉 DATAPILOT RUN COMPLETE!")
        print("=" * 80)
        
        self.print_table(final_dataset)
        
        # Save to data.json for safety
        with open("../data.json", "w") as f:
            json.dump(final_dataset, f, indent=2)
        print(f"\n💾 Results saved to data.json")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--config", type=str, default="../config.yaml")
    args = parser.parse_args()

    engine = DatapilotEngine(args.config, interactive=args.interactive)
    asyncio.run(engine.execute(limit=args.limit))
