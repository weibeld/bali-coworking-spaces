# Bali Coworking Spaces - Specification (v2)

This specification defines a two-phase data pipeline—**Discovery** and **Enrichment**—aligned with the Datapilot architecture. It prioritises source fidelity, deterministic routing for structured data, and human-in-the-loop verification.

---

## 1. Pipeline Overview

The project operates as a sequential pipeline:
**[Sources]** $\rightarrow$ **[Discovery Phase]** $\rightarrow$ **(discovery_candidates.json)** $\rightarrow$ **[Enrichment Phase]** $\rightarrow$ **(data.json)**

---

## 2. Phase 1: Discovery (Identification & Characterisation)

The goal of this phase is to mine a primary source to identify potential entities and characterise them to determine if they meet the project criteria.

### A. Harvesting (Deterministic)
- **Source:** Google Places API (New).
- **Procedure:** Bulk search for "coworking space" within a 40km radius of DPS Airport (-8.7481, 115.1671), restricted to the main island of Bali.
- **Filter:** Minimum 20 reviews.
- **Internal Output:** Raw list of Place IDs, Names, Google Category Labels, Top 5 Reviews, and Website URLs. (User does not interact with this raw state).

### B. Analysis & Reasoning (AI-Driven)
For each harvested listing, the AI agent performs a human-like analysis:
1.  **Source Triangulation:** Cross-reference Google Labels, Review Content (what are people actually doing there?), and the Official Website.
2.  **Reasoning:** Determine if the space provides **intended explicit coworking services** (e.g., selling day passes/memberships) rather than just "side-effect" laptop friendliness.
3.  **Characterisation:** Assign a tentative **Type of Place** (e.g., "Dedicated Coworking", "Hybrid Cafe/Coworking", "Normal Cafe").

### C. Discovery Verification (Human-in-the-loop)
- **Output:** `discovery_candidates.json`.
- **User Action:** Review the AI characterisation and evidence. The user approves or rejects candidates. Only approved candidates proceed to Phase 2.

---

## 3. Phase 2: Enrichment (Completing the Profile)

The goal of this phase is to build a full profile for approved candidates by pulling distributed data from secondary sources.

### A. Research & Extraction (Deterministic & AI-Driven)
For each sanctioned candidate, the agent performs a hybrid research task:
1.  **Source Access (Deterministic):** Accesses specific information sources (e.g., official websites, social media profiles).
2.  **Analysis & Extraction (AI-Driven):** The AI analyses the content of these sources to decide on the data values to extract (e.g., interpreting complex pricing structures or identifying member-only access hours).

**Targeted Fields:**
- **Access Times:** Find exact member "Open" and "Close" hours.
- **Pricing:** Locate the direct pricing/membership URL.

### B. Enrichment Verification (Human-in-the-loop)
- **User Action:** Verify the findings and sources presented by the agent. The user also provides subjective data (notes and visit status) at this stage.
- **Final Output:** The record is moved to the master `data.json`.

---

## 4. Data Structure (`data.json`)

| Field | Type | Description | Source Binding |
| :--- | :--- | :--- | :--- |
| `name` | String | Name of the space | Google API |
| `area` | String | Consolidated Hub name | Mapping Rule |
| `website` | String | Official website URL | Google API / Web |
| `pricing_page` | String | Direct link to membership/pricing | Web Search |
| `access` | Object | start, end, source, accessed_at | Web / In-person |
| `google_maps_rating` | Object | value, accessed_at | Google API |
| `google_maps_rating_count` | Object | value, accessed_at | Google API |
| `google_maps_uri` | String | Direct link to Maps | Google API |
| `google_maps_place_id` | String | Unique ID | Google API |
| `google_maps_latitude` | Number | Latitude | Google API |
| `google_maps_longitude` | Number | Longitude | Google API |
| `notes` | String | User-provided personal notes | User |
| `visited` | Boolean | User-provided visit status | User |

---

## 5. Geographic Hub Consolidation
Areas are consolidated into primary hubs to maintain searchability:
- **Canggu:** Canggu, Pererenan, Berawa, Seseh.
- **Seminyak:** Seminyak, Kerobokan, Umalas.
- **Kuta:** Kuta, Legian, Tuban.
- **Uluwatu:** Uluwatu, Ungasan, Pecatu, Bingin, Jimbaran.
- **Ubud:** Central Ubud, Nyuh Kuning, Penestanan, Sayan.
- **Sanur:** Sanur, Renon.

---

## 6. Procedural Rules
- **Source Fidelity:** API data (ratings, IDs, coordinates) must come from the Google Places API script, never from LLM hallucination.
- **Incremental Progress:** The agent uses a status script to identify the "Next Task" in the pipeline.
- **Accountability:** Every non-API researched field must include a `source` URL and `accessed_at` date.
