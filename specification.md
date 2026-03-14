# Bali Coworking Spaces Dataset - Specification

The goal of this project is to create a verified, searchable dataset of coworking spaces in Bali, specifically identifying those suitable for members working outside of standard business hours (late-night or overnight). The geographic scope covers spaces within ~1–1.5 hours of Denpasar, including Canggu, Pererenan, Seminyak, Kerobokan, Kuta, Sanur, Ubud, and the Bukit Peninsula (Uluwatu/Ungasan).

## 1. Classification of Spaces
Spaces are categorized based on **member access hours**:

| Category | Access Definition |
| :--- | :--- |
| **Overnight** | 24/7 access. |
| **Late-night** | Access until **later than 20:00**. |
| **Daytime** | Access **until or before 20:00**. |

*Note: Access times refer to when members can stay in the space, even if the reception/cafe area closes earlier.*

## 2. Data Structure (`data.json`)
The dataset uses objects for researched fields to ensure accountability.

### Field Definitions
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Name of the space |
| `area` | String | Neighborhood/Region |
| `category` | String | Overnight, Late-night, or Daytime |
| `website` | String | Official website URL |
| `pricing_page` | String | Direct link to membership/pricing |
| `access` | Object | value, source, accessed_at |
| `google_maps_rating` | Object | Star rating (from Places API) |
| `google_maps_rating_count` | Object | Review count (from Places API) |
| `google_maps_uri` | String | Direct link (from Places API) |
| `google_maps_place_id` | String | Unique ID (from Places API) |
| `notes` | String | Optional personal notes/experience |
| `visited` | Boolean | Whether I have visited the space (default: false) |

### Object Field Structures
Fields that are defined as Objects use the following structures to track verification metadata:

- **Researched Fields** (e.g., `access`):
  ```json
  { "value": "...", "source": "...", "accessed_at": "2026-03-13" }
  ```
- **API-Driven Fields** (e.g., `google_maps_rating`):
  ```json
  { "value": 0, "accessed_at": "2026-03-13" }
  ```

## 3. Google Maps API Integration
We use the **Google Places API (New)** to fetch deterministic data about coworking spaces.

### Setup Process
1.  **Project:** Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **API:** Enable the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service).
3.  **Credentials:** Create an API Key in **APIs & Services > Credentials**.
4.  **Security:** Store the key in a local `.env` file (not committed to source control):
    ```text
    GOOGLE_MAPS_API_KEY=your_key_here
    ```

### Documentation Links
- [Places API (New) Overview](https://developers.google.com/maps/documentation/places/web-service)
- [Text Search (New)](https://developers.google.com/maps/documentation/places/web-service/text-search) - Used to resolve Place IDs.
- [Place Details (New)](https://developers.google.com/maps/documentation/places/web-service/place-details) - Used to fetch ratings and reviews.
- [Place IDs](https://developers.google.com/maps/documentation/places/web-service/place-id) - Deterministic identifiers for locations.

### Alternative Considered: Grounding Lite
[Grounding Lite](https://developers.google.com/maps/ai/grounding-lite) is an experimental service from Google Maps Platform that uses the **Model Context Protocol (MCP)** to provide AI agents and applications with real-time geospatial data. As an MCP server, it allows LLMs to "ground" their responses in accurate information by providing tools like `search_places` and `lookup_weather` that can be called autonomously by the model. 

While Grounding Lite is a powerful tool for AI-driven research and contextual summaries, it was not chosen for this project because our goal is to build a structured, deterministic dataset. The **Places API (New)** provides more direct access to raw, un-synthesized metrics (such as exact review counts and persistent Place IDs) which are essential for the "Divide & Conquer" research process and for maintaining long-term data integrity without LLM intervention.

## 4. Research & Verification Process
- **Divide & Conquer:** Research one field or group of fields at a time.
- **Member-Centric:** Reported times must be for **weekly/monthly members**.
- **Source Priority:** 1. Official Website -> 2. Verified User Reports -> 3. Direct Enquiry.
- **Deterministic Google Data:** Use `google_maps_place_id` for all rating/review updates once resolved.

## 5. Presentation Layer
- **Source:** `data.json`
- **Dashboard:** `index.html` (using Grid.js)
- **Features:** Separate tables per category, sortable columns, and global search. Pagination is disabled.
