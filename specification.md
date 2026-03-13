# Bali Coworking Spaces Dataset - Specification

This document defines the requirements, data structure, and research process for the Bali Coworking Spaces dataset, with a focus on late-night and 24/7 access for remote workers.

## 1. Project Goal
To create a verified, searchable dataset of coworking spaces in Bali, specifically identifying those suitable for members working outside of standard business hours (late-night or overnight).

## 2. Geographic Scope
Coworking spaces within ~1–1.5 hours of Denpasar, including:
- Canggu, Pererenan, Seminyak, Kerobokan, Kuta, Sanur, Ubud, and the Bukit Peninsula (Uluwatu/Ungasan).

## 3. Classification of Spaces
Spaces are categorized based on **member access hours**:

| Category | Access Definition |
| :--- | :--- |
| **Overnight** | 24/7 access for members. |
| **Late-night** | Access until **later than 20:00**. |
| **Daytime** | Closes **at or before 20:00**. |

*Note: Access times refer to when members can stay in the space, even if the reception/cafe area closes earlier.*

## 4. Data Structure (`data.json`)
The master dataset is a JSON array of objects with the following fields:

| Field | Description | Source |
| :--- | :--- | :--- |
| `name` | Name of the space | Official |
| `area` | Neighborhood/Region | Official |
| `category` | Overnight, Late-night, or Daytime | Verified |
| `website` | Official website URL | Official |
| `pricing_page` | Direct link to membership/pricing | Official |
| `access_time` | Member access hours (e.g., "24/7", "08:00-22:00") | Official/Verified |
| `weekend_access` | Access details for Sat/Sun | Official/Verified |
| `google_rating` | Star rating | Google Places API |
| `google_reviews` | Number of reviews | Google Places API |
| `google_maps_uri` | Direct link to Google Maps | Google Places API |

## 5. Research & Verification Process
- **Divide & Conquer:** Research one field or group of fields (e.g., all `access_time` values) at a time.
- **Member-Centric:** Reported times must be for **weekly/monthly members**, not day-pass users (who often have restricted hours).
- **Source Priority:** 1. Official Website -> 2. Verified User Reports/Reviews -> 3. Direct Enquiry (if possible).
- **Google Data:** `google_rating`, `google_reviews`, and `google_maps_uri` must be fetched exclusively via the Google Places API.
- **Iterative Updates:** Present findings and sources to the user for approval before updating `data.json`.

## 6. Presentation Layer
- **Source:** `data.json`
- **Dashboard:** `index.html` (using Grid.js)
- **Features:** Separate tables per category, sortable columns, and global search. Pagination is disabled for easy scanning.
