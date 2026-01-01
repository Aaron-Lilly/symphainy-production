#!/bin/bash
# Real-time log monitoring for E2E tests

echo "🔍 Starting real-time log monitoring for Phase 1 E2E tests..."
echo "Monitoring for:"
echo "  - handle_process_file_request"
echo "  - orchestrate_data_parse"
echo "  - ContentJourneyOrchestrator"
echo "  - process_file"
echo "  - FileParserService"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

cd /home/founders/demoversion/symphainy_source
docker-compose logs -f backend 2>&1 | grep --line-buffered -E "handle_process_file_request|orchestrate_data_parse|ContentJourneyOrchestrator|_discover_content_journey|process_file|FileParserService|workflow_id|error|ERROR|exception|Exception" | while read line; do
    echo "[$(date +%H:%M:%S)] $line"
done



