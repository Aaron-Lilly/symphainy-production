#!/bin/bash
# Quick log checker - run this after triggering a test

echo "🔍 Checking recent logs for file parsing activity..."
echo ""

cd /home/founders/demoversion/symphainy_source

# Check last 100 lines for relevant activity
docker-compose logs backend --tail=100 2>&1 | grep -E "handle_process_file_request|orchestrate_data_parse|ContentJourneyOrchestrator|_discover_content_journey|process_file|FileParserService|workflow_id|error|ERROR|exception|Exception|Traceback" | tail -50

echo ""
echo "✅ Log check complete"
echo ""
echo "💡 To see more logs, run:"
echo "   docker-compose logs backend --tail=200 | grep -E 'handle_process_file|orchestrate_data_parse|ContentJourney'"



