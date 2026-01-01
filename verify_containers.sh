#!/bin/bash
# Script to verify containers have latest changes

echo "=== Checking Backend Container ==="
echo "1. Checking if preview_parsed_file method exists:"
docker exec symphainy-backend-prod grep -c "async def preview_parsed_file" /app/backend/journey/orchestrators/content_journey_orchestrator/content_orchestrator.py 2>&1

echo ""
echo "2. Checking if process_file returns parsed_file_id:"
docker exec symphainy-backend-prod grep -A 2 '"parsed_file_id": parsed_file_id' /app/backend/journey/orchestrators/content_journey_orchestrator/content_orchestrator.py | head -3

echo ""
echo "=== Checking Frontend Container ==="
echo "3. Checking if ContentAPIManager includes parsed_file_id:"
docker exec symphainy-frontend-prod sh -c "find /app/.next -name '*.js' -type f -exec grep -l 'parsed_file_id.*data\.parsed_file_id' {} \; 2>&1 | wc -l"

echo ""
echo "4. Checking if ParsePreview checks parsedFileId:"
docker exec symphainy-frontend-prod sh -c "find /app/.next -name '*.js' -type f -exec grep -l 'if.*parsedFileId' {} \; 2>&1 | wc -l"

echo ""
echo "=== Source Files ==="
echo "5. Source ContentAPIManager has parsed_file_id:"
grep -c "parsed_file_id: data.parsed_file_id" symphainy-frontend/shared/managers/ContentAPIManager.ts

echo ""
echo "6. Source ParsePreview checks parsedFileId:"
grep -c "if (parsedFileId)" symphainy-frontend/app/pillars/content/components/ParsePreview.tsx



