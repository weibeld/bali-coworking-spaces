#!/bin/bash
# Scans data.json for null values and identifies the next research task.

DATA_FILE="data.json"

if [ ! -f "$DATA_FILE" ]; then
  echo "Error: $DATA_FILE not found."
  exit 1
fi

# 1. Total Stats
TOTAL_SPACES=$(jq '. | length' "$DATA_FILE")

# Count only required fields that are null or missing values in objects
# Excludes 'notes' and 'visited' which are allowed to be null
MISSING_FIELDS=$(jq '[.[] | to_entries[] | 
  select(.key != "notes" and .key != "visited") | 
  .value as $v |
  select(
    ($v == null) or 
    ($v | type == "object" and $v.value == null and $v != "N/A") or 
    ($v | type == "object" and has("source") and $v.source == null and $v.value != null)
  )
] | length' "$DATA_FILE")

echo "📊 PROGRESS REPORT"
echo "-----------------"
echo "Spaces: $TOTAL_SPACES | Missing Fields: $MISSING_FIELDS"
echo ""

# 2. Find the first space with a null required field
NEXT_TASK=$(jq -r '
  .[] | 
  select(
    (.access.value == null) or 
    (.access.source == null) or
    (.pricing_page == null) or 
    (.google_maps_place_id == null) or 
    (.google_maps_rating.value == null and .google_maps_rating != "N/A") or 
    (.google_maps_rating_count.value == null and .google_maps_rating_count != "N/A") or 
    (.google_maps_uri == null and .google_maps_uri != "N/A") or
    (.google_maps_latitude == null and .google_maps_latitude != "N/A") or
    (.google_maps_longitude == null and .google_maps_longitude != "N/A")
  ) | 
  {
    name: .name,
    field: (
      if .access.value == null then "access_value"
      elif .access.source == null then "access_source"
      elif .pricing_page == null then "pricing_page"
      elif .google_maps_place_id == null then "google_maps_place_id"
      elif (.google_maps_rating.value == null or .google_maps_rating_count.value == null or .google_maps_uri == null or .google_maps_latitude == null) then "google_maps_info_bundle"
      else "unknown"
      end
    )
  } | 
  "\(.name) -> \(.field)"
' "$DATA_FILE" | head -n 1)

if [ -z "$NEXT_TASK" ]; then
  echo "✅ ALL FIELDS VERIFIED! Dataset is complete."
else
  echo "👉 NEXT TASK: $NEXT_TASK"
  echo "-----------------"
fi
