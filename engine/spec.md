# Datapilot Engine Specification (v2)

This document defines the "Engine" architecture for a goal-oriented, schema-driven data extraction system. It aims to achieve the most efficient data extraction by combining deterministic tools (APIs) and non-deterministic tools (LLMs) in a unified interface.

---

## 1. Core Concepts

### A. Goal-Oriented & Schema-Driven
The target data structure is the primary "Goal" of the system. The user provides a declarative specification of what the final data should look like (`schema`), and the Engine's purpose is to satisfy this schema.

### C. Field Specification Spectrum
"As efficient as possible, as accurate as necessary." Every field in the schema is defined by three components, each with a deterministic (`_raw`) or semantic (`_llm`) variant:

| Component | Deterministic (`_raw`) | Semantic (`_llm`) |
| :--- | :--- | :--- |
| **Source** | `source_raw`: API call/query template. | `source_llm`: Human intent/description. |
| **Extraction** | `extract_raw`: JSON/XPath mapping. | `extract_llm`: Human extraction rules. |
| **Constraints** | `constraints_raw`: Logical/Rule expression. | `constraints_llm`: Human filtering criteria. |

### D. State Preservation (Single Pass PoC)
While future versions will use a primary key/ID for state preservation across multiple passes, the initial Proof of Concept focuses on a single-pass execution where discovery and enrichment happen in a unified flow.

### E. Unified Hybrid Interface
The Engine's main value proposition is providing a single interface that blends traditional data tools (scripts, APIs) with AI capabilities, selecting the most efficient sub-tool for each specific field-extraction task.

### F. Variable Injection & Implicit Dependencies
Fields can reference the values of other fields using the `$field_name` syntax. The Engine is responsible for **Implicit Dependency Mapping**: it scans the configuration for these variables to automatically determine the correct execution order. 

Fields with **zero dependencies** are identified as "Root Fields," and their shared source is treated as the "Anchor Source" for initial discovery.

---

## 2. Input Configuration (`config.yaml`)

The Engine is governed by a declarative configuration file:
- **Schema:** The "What" (Goal), "Where" (Source), "How" (Extraction), and "Why" (Constraints).

---

## 3. Open Design Decisions

### A. Role of the LLM vs. Orchestrator
- **The Orchestrator:** A traditional program that invokes the LLM as a capability.
- **The LLM Role:** Interprets `_llm` specifications and "asks" the main program to execute specific tasks or use tools.
- **Terminology:** Should this program be called an "Agent"?

### B. LLM Mapping for Deterministic APIs
Even for `_raw` sources, should the LLM be used to "map" raw API responses to the schema? This avoids the tedious manual configuration of `extract_raw` paths.

### C. State Preservation Logic During Refinement
How does the Engine decide which fields to re-generate on subsequent passes? (Reserved for future multi-pass implementation).

### D. Grounded Discovery for Abstract Domains
Discovery must be grounded in a "Source of Truth" to avoid LLM hallucinations.
- **Source Selection:** How does the Engine guide the user to a grounded index (e.g., Google Books API, GitHub) when a geographic source like Google Maps isn't applicable?
- **Filtering vs. Generation:** The Engine must strictly filter results from the source rather than generating entities from the LLM's internal knowledge.

### E. Multiple Sources per Field
Future versions must handle data federation from multiple sources (e.g., getting a phone number from both Google Maps and an Official Website).
- **Conflicting Data:** How does the Engine resolve differences? (e.g., a "Confidence Scorer" or "Weighted Priority").
- **Unified Extraction:** Can the Engine be instructed to "Look at Source A, if not found, look at Source B"?

---

## 4. Implementation Details (Proof of Concept)

### A. Technology Stack
- **Language:** Python 3.10+
- **LLM SDK:** [Google GenAI SDK for Python](https://pypi.org/project/google-genai/)
- **Orchestration:** Custom Python script using `Pydantic` for schema validation and `PyYAML` for configuration management.

### B. LLM Backend
- **Provider:** Google Gemini
- **Model:** `gemini-flash-latest` (or latest available via AI Studio)
- **Interface:** AI Studio (Gemini Developer API) for simplified PoC access.

---

## 5. Setup Requirements

### A. Gemini API & Google Cloud Setup
1.  **Generate an API Key:** Go to [Google AI Studio (API Keys)](https://aistudio.google.com/app/apikey).
2.  **Enable Paid Tier (Tier 1):** 
    - Click **"Set up billing"** for your project.
    - Link a Google Cloud Billing account (reopen an existing one or create a new "Personal Billing Account").
    - Ensure your project reflects **"Paid Tier"** or **"Tier 1"** in AI Studio to avoid strict rate limits (up to 2,000 RPM).
3.  **Project ID:** If using multiple projects, ensure your API key belongs to the one linked to your billing account.
4.  **Store the key:** Save in `engine/.env`:
    ```env
    GEMINI_API_KEY=your_api_key_here
    GOOGLE_MAPS_API_KEY=your_maps_key_here
    ```

### B. Python Environment
1.  **Create a virtual environment:** `python3 -m venv engine/.venv`
2.  **Activate and install dependencies:**
    ```bash
    source engine/.venv/bin/activate
    pip install google-genai PyYAML pydantic httpx python-dotenv jsonpath-ng
    ```

---

## 6. Competitive Analysis: Firecrawl Agent

The **Firecrawl Agent** ([Website](https://www.firecrawl.dev/app/agent) | [Docs](https://docs.firecrawl.dev/features/agent) | [GitHub](https://github.com/mendableai/firecrawl)) is an autonomous web research tool designed to handle complex, multi-step extraction tasks. It allows users to start with a natural language prompt, and the agent autonomously navigates the web using its internal **FIRE-1** web action agent to identify relevant URLs and extract structured data (JSON/CSV) based on an intent-driven schema.

### Key Capabilities of Firecrawl Agent:
- **Autonomous Source Discovery:** It can find its own sources and navigate deep into site structures, including "hard-to-reach" places requiring interaction (clicks, scrolls).
- **Parallel Research:** It supports batch processing of hundreds of queries simultaneously for high-throughput extraction.
- **Model Tiers:** Users can choose between **Spark 1 Mini** (optimized for cost/efficiency) and **Spark 1 Pro** (optimized for complex reasoning and accuracy).
- **LLM-Ready Output:** Deliver clean Markdown or structured data specifically formatted for immediate consumption by AI agents.

### How Datapilot Differs (and Improves):

While Firecrawl is an industry leader for broad, autonomous research, **Datapilot** is designed for high-precision scenarios where the user needs explicit, deterministic control over the "Source of Truth."

1.  **Pinned Data Sources vs. Opaque Discovery:** Firecrawl autonomously finds URLs, which can lead to "Agent Drift" or data from untrusted sources. Datapilot allows the user to explicitly pin logical sources (e.g., "Google Places search" vs "Official Venue Website"), ensuring the data provenance is deterministic and verifiable.
2.  **Grounded API Integration:** Datapilot supports grounding the LLM in real-world API documentation. Instead of relying on general LLM knowledge to "scrape" a page, the Datapilot orchestrator fetches technical docs so the LLM can construct precise, valid API calls (e.g., using specific `locationBias` rules in Google Maps).
3.  **Schema Generation Model:** While both tools use schemas, Firecrawl typically relies on an LLM to "propose" or "map" a schema based on general intent. In contrast, Datapilot uses an **Orchestrator-driven Compilation** approach. The formal JSON Schema is inferred directly from the user's structured declarative configuration at startup, ensuring the engine adheres strictly to the user's defined goals rather than the LLM's probabilistic interpretation.
4.  **Fine-Grained Transparency:** Datapilot acts as a "White Box" engine. Every data point is tied to a specific field intent and a specific grounded source, providing a clear audit trail that is often missing in purely autonomous "Black Box" research agents.
