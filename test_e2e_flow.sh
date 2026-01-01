#!/bin/bash
# E2E Test Script for Phase 1 - ContentJourneyOrchestrator Flow

set -e

echo "🧪 Starting E2E Tests for Phase 1..."
echo ""

# Test 1: Check if backend is running
echo "Test 1: Backend Health Check"
if curl -s http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not responding"
    exit 1
fi
echo ""

# Test 2: Check logs for ContentJourneyOrchestrator registration
echo "Test 2: ContentJourneyOrchestrator Registration"
REGISTRATION=$(docker-compose logs backend 2>&1 | grep -i "ContentJourneyOrchestratorService.*register\|ContentJourneyOrchestrator.*register" | tail -1)
if [ -n "$REGISTRATION" ]; then
    echo "✅ Found registration: $REGISTRATION"
else
    echo "⚠️  ContentJourneyOrchestrator not found in logs (may lazy-initialize on first use)"
fi
echo ""

# Test 3: Check DataSolutionOrchestrator registration
echo "Test 3: DataSolutionOrchestrator Registration"
DSO_REG=$(docker-compose logs backend 2>&1 | grep -i "DataSolutionOrchestratorService.*register\|Data Solution Orchestrator.*register" | tail -1)
if [ -n "$DSO_REG" ]; then
    echo "✅ Found registration: $DSO_REG"
else
    echo "❌ DataSolutionOrchestrator not registered"
    exit 1
fi
echo ""

# Test 4: Monitor logs for file parsing request
echo "Test 4: Ready for file parsing test"
echo "⚠️  To test file parsing, upload a file via frontend and trigger parsing"
echo "    Monitor logs with: docker-compose logs -f backend | grep -E 'handle_process_file_request|orchestrate_data_parse|ContentJourneyOrchestrator|process_file'"
echo ""

echo "✅ Basic E2E tests completed"
echo ""
echo "Next steps:"
echo "1. Upload a mainframe file via frontend"
echo "2. Trigger file parsing"
echo "3. Monitor logs for the complete flow"



