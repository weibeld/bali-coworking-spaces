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
