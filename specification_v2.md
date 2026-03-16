# Datapilot Engine Specification (v2)

This document defines the "Engine" architecture for a goal-oriented, schema-driven data extraction system. It aims to achieve the most efficient data extraction by combining deterministic tools (APIs) and non-deterministic tools (LLMs) in a unified interface.

---

## 1. Core Concepts

### A. Goal-Oriented & Schema-Driven
The target data structure is the primary "Goal" of the system. The user defines what the final data should look like (`target_schema`), and the Engine's purpose is to populate this schema.

### C. Field Specification Spectrum
"As efficient as possible, as accurate as necessary." Field extraction is defined on a spectrum:
- **Deterministic:** Specific API calls or rules where accuracy is paramount.
- **Fuzzy:** LLM-driven reasoning/instructions where the tool's flexibility is the most efficient choice.

### D. Iterative Refinement & State Preservation
Usage follows an exploratory loop. A user may start with "fuzzy" specifications to test the waters and then "narrow down" to deterministic rules as needed. The Engine must preserve previously extracted data during these refinement passes, allowing for incremental improvements without starting from scratch.

### E. Unified Hybrid Interface
The Engine's main value proposition is providing a single interface that blends traditional data tools (scripts, APIs) with AI capabilities, selecting the most efficient sub-tool for each specific field-extraction task.

---

## 2. Input Configuration (`config.yaml`)

The Engine is governed by a declarative configuration file:
- **Target Schema:** The "What" (Goal).
- **Discovery Intent:** The "Where" (Source + Goal-based criteria).
- **Enrichment Strategy:** The "How" (Field-by-field instructions, ranging from API bindings to LLM directives).

---

## 3. Open Design Decisions

### A. Role of the LLM vs. Orchestrator
Is the main program a "Traditional Orchestrator" that explicitly calls the LLM for fuzzy fields, or is it an "Agentic Loop" where the LLM drives the overall flow?

### B. LLM Mapping for Deterministic APIs
Even for deterministic API calls, should the LLM be used to "map" the raw API response to the schema? This would reduce the user's burden of studying API documentation and specifying exact JSON paths (e.g., "Extract the rating from this Google API response").

### C. State Preservation Logic During Refinement Passes
How does the Engine decide which fields to re-generate on subsequent passes?
- Re-extract fields only if the field's specification changes?
- Should fuzzy fields always be re-tried if the instruction changes, while deterministic fields are only re-tried if the source changes?
- How does the "Unified Review" look? Does the user see a side-by-side comparison of old vs. new data during a refinement pass?

### D. Grounded Discovery for Abstract Domains
Discovery must be grounded in a "Source of Truth" to avoid LLM hallucinations. The design challenge is how to implement this for abstract topics (e.g., "Kubernetes Books") where a single source isn't as obvious as Google Maps.
- **Source Selection:** How does the Engine guide the user to a grounded index (e.g., Google Books API, GitHub, arXiv)? 
- **Query Translation:** How does the Engine translate a fuzzy user intent ("General Kubernetes books") into a precise search query for that source (`intitle:Kubernetes`)?
- **Filtering vs. Generation:** The Engine must strictly **filter** results returned by the source rather than **generating** new ones from the LLM's internal weights.
