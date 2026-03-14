# Bali Coworking Spaces Dataset - Specification

The goal of this project is to create a verified, searchable dataset of coworking spaces in Bali, specifically identifying those suitable for members working outside of standard business hours (late-night or overnight). The geographic scope covers spaces within ~1–1.5 hours of Denpasar, including Canggu, Pererenan, Seminyak, Kerobokan, Kuta, Sanur, Ubud, and the Bukit Peninsula (Uluwatu/Ungasan).

## 1. Classification of Spaces
Spaces are categorized based on **member access hours**:

| Category | Access Definition |
| :--- | :--- |
| **Overnight** | 24/7 access for members. |
| **Late-night** | Access until **later than 20:00** (up to 00:00). |
| **Daytime** | Closes **at or before 20:00**. |

*Note: Access times refer to when members can stay in the space, even if the reception/cafe area closes earlier.*

## 2. Data Structure (`data.json`)
The dataset uses objects for researched fields to ensure accountability.

### Field Structures
- **Researched Fields** (`access_time`):
  ```json
  { "value": "...", "source": "...", "accessed_at": "2026-03-13" }
  ```
- **API Fields** (`google_maps_rating`, `google_maps_rating_count`):
  ```json
  { "value": 0, "accessed_at": "2026-03-13" }
  ```
- **Simple Fields** (`name`, `area`, `category`, `website`, `pricing_page`, `google_maps_uri`, `google_maps_place_id`):
  Standard strings.

### Field Definitions
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Name of the space |
| `area` | String | Neighborhood/Region |
| `category` | String | Overnight, Late-night, or Daytime |
| `website` | String | Official website URL |
| `pricing_page` | String | Direct link to membership/pricing |
| `access_time` | Object | value, source, accessed_at |
| `google_maps_rating` | Object | Star rating (from Places API) |
| `google_maps_rating_count` | Object | Review count (from Places API) |
| `google_maps_uri` | String | Direct link (from Places API) |
| `google_maps_place_id` | String | Unique ID (from Places API) |

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

### Alternatives Considered
For fetching Google Maps data, several alternatives were evaluated:
- **[Grounding with Google Search](https://developers.google.com/maps/ai/grounding-lite):** A newer AI-driven approach for grounding information with real-world Google Search data. While promising for general information, the deterministic nature of the Places API (New) was preferred for this dataset to ensure exact matches via Place IDs.
- **Traditional Places API:** Replaced by the "New" version which offers better field masking and more granular control over data billing.

## 4. Research & Verification Process
- **Divide & Conquer:** Research one field or group of fields at a time.
- **Member-Centric:** Reported times must be for **weekly/monthly members**.
- **Source Priority:** 1. Official Website -> 2. Verified User Reports -> 3. Direct Enquiry.
- **Deterministic Google Data:** Use `google_maps_place_id` for all rating/review updates once resolved.

## 5. Presentation Layer
- **Source:** `data.json`
- **Dashboard:** `index.html` (using Grid.js)
- **Features:** Separate tables per category, sortable columns, and global search. Pagination is disabled.
