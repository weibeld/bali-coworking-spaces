#!/bin/bash
# Resolves a Google Place ID from a search query.

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
  echo "Error: GOOGLE_MAPS_API_KEY is missing in .env"
  exit 1
fi

NAME=$1

if [ -z "$NAME" ]; then
  echo "Usage: ./google_maps_get_place_id.sh \"Coworking Space Name\""
  exit 1
fi

SEARCH_RESPONSE=$(curl -s -X POST 'https://places.googleapis.com/v1/places:searchText' \
  -H 'Content-Type: application/json' \
  -H "X-Goog-Api-Key: $GOOGLE_MAPS_API_KEY" \
  -H 'X-Goog-FieldMask: places.id,places.displayName' \
  -d "{ \"textQuery\": \"$NAME Bali\" }")

PLACE_ID=$(echo "$SEARCH_RESPONSE" | jq -r '.places[0].id')

if [ "$PLACE_ID" == "null" ] || [ -z "$PLACE_ID" ]; then
  echo "Error: No place found for \"$NAME Bali\"" >&2
  exit 1
fi

echo "$PLACE_ID"
