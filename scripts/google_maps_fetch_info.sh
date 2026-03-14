#!/bin/bash
# Fetches ratings, reviews, URI, and coordinates for a specific Google Place ID.

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
  echo "Error: GOOGLE_MAPS_API_KEY is missing in .env"
  exit 1
fi

PLACE_ID=$1

if [ -z "$PLACE_ID" ]; then
  echo "Usage: ./google_maps_fetch_info.sh <PLACE_ID>"
  exit 1
fi

# We add 'location' to the field mask to get coordinates
DETAILS_RESPONSE=$(curl -s -G "https://places.googleapis.com/v1/places/$PLACE_ID" \
  -H "X-Goog-Api-Key: $GOOGLE_MAPS_API_KEY" \
  -H 'X-Goog-FieldMask: rating,userRatingCount,googleMapsUri,location')

ACCESSED_AT=$(date +%Y-%m-%d)

echo "$DETAILS_RESPONSE" | jq --arg date "$ACCESSED_AT" '{
  google_maps_rating: { value: .rating, accessed_at: $date },
  google_maps_rating_count: { value: .userRatingCount, accessed_at: $date },
  google_maps_uri: .googleMapsUri,
  google_maps_latitude: .location.latitude,
  google_maps_longitude: .location.longitude
}'
