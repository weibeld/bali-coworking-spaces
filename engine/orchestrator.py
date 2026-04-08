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
        self.sources = self.config.get("sources", {})
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

    async def fetch_docs(self, url: str) -> str:
        """Fetches documentation content to ground the LLM."""
        print(f"   🌐 Fetching Documentation: {url}...")
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, follow_redirects=True)
                # Simple text extraction (strip HTML tags)
                text = re.sub('<[^<]+?>', '', resp.text)
                text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
                return text[:15000] # Limit context size
            except Exception as e:
                print(f"   ⚠️ Could not fetch docs: {e}")
                return "Documentation not available."

    async def synthesize_anchor_call(self) -> Dict[str, Any]:
        """Ask LLM to compile the root source intent into an API call using provided docs."""
        first_field = self.root_fields[0]
        source_id = self.schema[first_field].get("source_id")
        source_config = self.sources.get(source_id, {})
        source_desc = source_config.get("description", "Unknown Source")
        docs_url = source_config.get("docs")
        
        docs_content = await self.fetch_docs(docs_url) if docs_url else "No documentation provided."
        
        root_specs = {f: self.schema[f] for f in self.root_fields}

        prompt = f"""
        TASK: Construct a functional API request for SOURCE: {source_desc}.
        
        GROUNDING DOCUMENTATION:
        {docs_content}

        TARGET SCHEMA (Fields to satisfy in this request):
        {json.dumps(root_specs, indent=2)}

        INSTRUCTIONS:
        1. Read the provided documentation carefully. 
        2. Identify the correct modern endpoint URL, HTTP method, and JSON body/query schema.
        3. Use 'YOUR_API_KEY' as a placeholder for any required authentication.
        4. For Google Places (New), remember that circles are only supported in 'locationBias', not 'locationRestriction'.
        5. Return ONLY a JSON object with keys: url, method, headers, body.
        """
        
        if self.interactive:
            print(f"\n[DEBUG] --- LLM REQUEST: SYNTHESIS (Grounded) ---")
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        if self.interactive:
            print(f"\n[DEBUG] --- LLM RESPONSE: SYNTHESIS ---")
            print(response.text)
        
        return json.loads(response.text)

    async def extract_fields_from_raw(self, raw_data: Any, field_names: List[str]) -> Dict[str, Any]:
        """Uses LLM to extract multiple fields from a raw chunk of data."""
        specs = {f: self.schema[f] for f in field_names}
        
        prompt = f"""
        RAW DATA:
        {json.dumps(raw_data, indent=2)}

        TARGET FIELDS & INTENT:
        {json.dumps(specs, indent=2)}

        INSTRUCTION:
        Extract the values for each field from the raw data based on the provided intent and constraints.
        Return ONLY a JSON object where keys are the field names.
        """
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        try:
            return json.loads(response.text)
        except:
            return {}

    async def execute_join(self, field_name: str, row: Dict[str, Any]) -> Any:
        """Executes LLM join for a dependent field, optionally grounded in a source."""
        spec = self.schema[field_name]
        source_id = spec.get("source_id")
        
        # Determine the contextual intent/description
        if source_id and source_id in self.sources:
            source_config = self.sources[source_id]
            source_desc = source_config.get("description", "")
            docs_url = source_config.get("docs")
            docs_content = await self.fetch_docs(docs_url) if docs_url else "Documentation not available."
        else:
            source_desc = spec.get("description", "")
            docs_content = "No technical documentation provided."

        # Resolve variables
        for k, v in row.items():
            source_desc = source_desc.replace(f"${k}", str(v))

        extract_instr = spec.get("extract", "")
        for k, v in row.items():
            extract_instr = extract_instr.replace(f"${k}", str(v))

        prompt = f"""
        SOURCE CONTEXT: {source_desc}
        
        GROUNDING DOCUMENTATION:
        {docs_content}

        INSTRUCTION: {extract_instr}
        
        Return JSON: {{ '{field_name}': ... }}
        """
        
        if self.interactive:
            print(f"\n   [DEBUG] --- LLM REQUEST: JOIN {field_name} (Grounded) ---")
        
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

        cols = ["name", "rating", "rating_count", "coworking_confidence", "website_url"]
        widths = {c: len(c) + 2 for c in cols}
        for row in data:
            for c in cols:
                val = str(row.get(c, ""))[:40]
                widths[c] = max(widths[c], len(val) + 2)

        print("\n" + "┌" + "┬".join("─" * widths[c] for c in cols) + "┐")
        print("│" + "│".join(c.upper().center(widths[c]) for c in cols) + "│")
        print("├" + "┼".join("─" * widths[c] for c in cols) + "┤")
        for row in data:
            line = "│"
            for c in cols:
                val = str(row.get(c, ""))[:widths[c]-2]
                line += val.ljust(widths[c]) + "│"
            print(line)
        print("└" + "┴".join("─" * widths[c] for c in cols) + "┘")

    async def execute(self, limit: int = 3):
        # 1. ANCHORING
        print("\n⚓ ANCHORING: Preparing initial data fetch...")
        req = await self.synthesize_anchor_call()
        
        url = req.get('url')
        method = req.get('method', 'GET').upper()
        headers = req.get('headers', {})
        body = req.get('body')

        # Inject API keys
        for k, v in headers.items():
            if v == "YOUR_API_KEY": headers[k] = self.maps_key
        if body:
            body_str = json.dumps(body).replace("YOUR_API_KEY", self.maps_key)
            body = json.loads(body_str)
        url = url.replace("YOUR_API_KEY", self.maps_key)

        # Fallback for Google Maps New API
        if "google" in url and "X-Goog-Api-Key" not in headers:
            headers["X-Goog-Api-Key"] = self.maps_key

        headers = {k: str(v) for k, v in headers.items() if v is not None}

        if self.interactive:
            print(f"\n[DEBUG] --- API REQUEST: DATA FETCHING ---")
            print(f"URL: {url}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Body: {json.dumps(body, indent=2)}")

        # 2. FETCHING
        print("📡 FETCHING: Executing primary source request...")
        async with httpx.AsyncClient() as client:
            if method == "POST":
                resp = await client.post(url, json=body, headers=headers)
            else:
                resp = await client.get(url, params=body, headers=headers)
                
            if resp.status_code != 200:
                print(f"❌ API Error: {resp.text}")
                return
            raw_data = resp.json()
        
        # Find the list of items
        data_root = None
        if isinstance(raw_data, list):
            data_root = raw_data
        elif isinstance(raw_data, dict):
            for key in ['places', 'results', 'items', 'data']:
                if key in raw_data and isinstance(raw_data[key], list):
                    data_root = raw_data[key]
                    break
            if not data_root:
                data_root = [raw_data]

        print(f"✅ FOUND: {len(data_root)} potential candidates.")
        
        final_dataset = []
        count = 0
        
        # 3. UNIFIED PROCESSING LOOP
        for p in data_root:
            if count >= limit: break
            
            # Semantic Extraction for Root Fields
            row = await self.extract_fields_from_raw(p, self.root_fields)
            
            # Check constraints for root fields
            keep = True
            for f in self.root_fields:
                spec = self.schema[f]
                val = row.get(f)
                if "constraints" in spec:
                    # Very simple constraint check for PoC
                    # For complex constraints, we could use the LLM
                    rule = str(spec["constraints"])
                    if ">=" in rule:
                        try:
                            threshold = int(rule.split(">=")[1].strip())
                            if val is None or int(val) < threshold: keep = False
                        except: pass
            
            if not keep: continue
            
            count += 1
            name = row.get('name', 'Unknown')
            
            print(f"\n" + "━"*80)
            print(f"📦 [{count}/{limit}] {name}")
            print("━"*80)
            print(f"   [FETCHED DATA]: {json.dumps(row, indent=2)}")
            
            # Execute Joins
            for field in self.execution_order:
                if field in self.root_fields: continue
                if self.interactive: print(f"   -> Joining: '{field}'...")
                val = await self.execute_join(field, row)
                row[field] = val
                if self.interactive: print(f"      ✅ Result: {val}")
                
                spec = self.schema[field]
                if "constraints" in spec:
                    rule = str(spec["constraints"])
                    try:
                        if ">=" in rule and int(val) < int(rule.split(">=")[1]):
                            print(f"   ❌ REJECTED: {field} ({val}) failed {rule}")
                            row = None
                            break
                    except: pass
            
            if row: 
                final_dataset.append(row)
                if self.interactive:
                    print(f"\n✅ COMPLETE: Final dataset for {name} updated.")
            
            if self.interactive and count < limit:
                input("\n[PAUSE] Press ENTER to continue to next candidate... ")

        print("\n" + "=" * 80)
        print("🎉 DATAPILOT RUN COMPLETE!")
        print("=" * 80)
        
        self.print_table(final_dataset)
        
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
