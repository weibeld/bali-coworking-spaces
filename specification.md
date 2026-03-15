# Bali Coworking Spaces Dataset - Specification

The goal of this project is to create a verified, searchable dataset of coworking spaces in Bali, specifically identifying those suitable for remote workers. The geographic scope covers the major hubs within ~1–1.5 hours of Denpasar.

## 1. Data Structure (`data.json`)
The dataset uses objects for researched fields to ensure accountability.

### Field Definitions
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Name of the space |
| `area` | String | Consolidated Hub name |
| `website` | String | Official website URL |
| `pricing_page` | String | Direct link to membership/pricing |
| `access` | Object | start, end, source, accessed_at |
| `google_maps_rating` | Object | Star rating (from Places API) |
| `google_maps_rating_count` | Object | Review count (from Places API) |
| `google_maps_uri` | String | Direct link (from Places API) |
| `google_maps_place_id` | String | Unique ID (from Places API) |
| `google_maps_latitude` | Number | Latitude (from Places API) |
| `google_maps_longitude` | Number | Longitude (from Places API) |
| `notes` | String | Optional personal notes/experience |
| `visited` | Boolean | Whether I have visited the space (default: false) |

### Object Field Structures
Fields that are defined as Objects use the following structures to track verification metadata:

- **Researched Fields** (`access`):
  ```json
  { 
    "start": "HH:mm", 
    "end": "HH:mm", 
    "source": "...", 
    "accessed_at": "2026-03-13" 
  }
  ```
  *Note: 24/7 access is represented as `"start": "00:00", "end": "00:00"`.*

- **API-Driven Fields** (e.g., `google_maps_rating`):
  ```json
  { "value": 0, "accessed_at": "2026-03-13" }
  ```

## 2. Google Maps API Integration
We use the **Google Places API (New)** to fetch deterministic data about coworking spaces.

### Setup Process
1.  **Project:** Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  **API:** Enable the [Places API (New)](https://developers.google.com/maps/documentation/places/web-service).
3.  **Credentials:** Create an API Key in **APIs & Services > Credentials**.
4.  **Security:** Store the key in a local `.env` file (not committed to source control).

### Documentation Links
- [Places API (New) Overview](https://developers.google.com/maps/documentation/places/web-service)
- [Text Search (New)](https://developers.google.com/maps/documentation/places/web-service/text-search)
- [Place Details (New)](https://developers.google.com/maps/documentation/places/web-service/place-details)
- [Place IDs](https://developers.google.com/maps/documentation/places/web-service/place-id)

### Alternative Considered: Grounding Lite
[Grounding Lite](https://developers.google.com/maps/ai/grounding-lite) is an experimental service using the **Model Context Protocol (MCP)**. It was not chosen because the Places API provides more deterministic, structured metrics essential for maintaining long-term data integrity.

## 3. Research & Verification Process
- **Divide & Conquer:** Research one field or group of fields at a time.
- **Member-Centric:** Reported times must be for **weekly/monthly members**.
- **Source Priority:** 1. Official Website -> 2. In-person visit -> 3. Direct Enquiry -> 4. Verified User Reports.
- **Automated Updates:** Google Maps data fetches immediately initiate a file update. The standard CLI file-write confirmation serves as the verification step.
- **Manual Verification:** For qualitative fields (like `access`), findings and sources are presented before updating the dataset.

## 4. Geographic Hub Consolidation
To maintain a clean and searchable dataset, smaller neighborhoods are consolidated into primary "Hubs."

| Hub | Included Areas |
| :--- | :--- |
| **Canggu** | Canggu, Pererenan, Berawa (Tibubeneng), Seseh. |
| **Seminyak** | Seminyak, Kerobokan, Umalas. |
| **Kuta** | Kuta, Legian, Tuban. |
| **Uluwatu** | Uluwatu, Ungasan, Pecatu, Bingin, Jimbaran. |
| **Ubud** | Central Ubud, Nyuh Kuning, Penestanan, Sayan. |
| **Sanur** | Sanur, Renon. |

## 5. Presentation Layer
- **Source:** `data.json`
- **Dashboard:** `index.html` (using Grid.js)
- **Features:** A single unified table with sortable columns and global search. Pagination is disabled.
