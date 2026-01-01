#!/bin/bash
# Direct test script for file parsing endpoint
# Usage: ./test_parse_direct.sh <file_id>

FILE_ID=$1

if [ -z "$FILE_ID" ]; then
    echo "❌ Usage: ./test_parse_direct.sh <file_id>"
    echo ""
    echo "To get a file_id, upload a file via frontend first."
    exit 1
fi

echo "🧪 Testing file parsing for file_id: $FILE_ID"
echo ""

# Test via Traefik (production path)
API_BASE="http://localhost/api"
URL="${API_BASE}/v1/content-pillar/process-file/${FILE_ID}"

echo "📡 Testing endpoint: $URL"
echo ""

# Make request
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$URL" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"test_user\"}" \
    --max-time 180)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "📊 Response Status: $HTTP_CODE"
echo "📄 Response Body:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Request successful!"
    echo "$BODY" | grep -q "success.*true" && echo "✅ Parsing completed successfully" || echo "⚠️  Check response for details"
else
    echo "❌ Request failed with status $HTTP_CODE"
    echo "Check logs for details: docker-compose logs -f backend"
fi



