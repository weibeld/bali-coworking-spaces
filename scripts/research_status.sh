#!/bin/bash
# Scans data.json for null values and identifies the next research task.

DATA_FILE="data.json"

if [ ! -f "$DATA_FILE" ]; then
  echo "Error: $DATA_FILE not found."
  exit 1
fi

# 1. Total Stats
TOTAL_SPACES=$(jq '. | length' "$DATA_FILE")
MISSING_FIELDS=$(jq '[.[] | to_entries[].value | select(. == null or (.value? == null) or (.source? == null and .value? != null))] | length' "$DATA_FILE")

echo "📊 PROGRESS REPORT"
echo "-----------------"
echo "Spaces: $TOTAL_SPACES | Missing Fields: $MISSING_FIELDS"
echo ""

# 2. Find the first space with a null field
NEXT_TASK=$(jq -r '
  .[] | 
  select(
    (.access.value == null) or 
    (.access.source == null) or
    (.pricing_page == null) or 
    (.google_maps_place_id == null) or 
    (.google_maps_rating.value == null) or 
    (.google_maps_rating_count.value == null) or 
    (.google_maps_uri == null) or
    (.google_maps_latitude == null) or
    (.google_maps_longitude == null)
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
