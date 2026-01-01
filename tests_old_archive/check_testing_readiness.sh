#!/bin/bash
# Quick readiness check before running full testing gauntlet

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🔍 TESTING READINESS CHECK"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

READY=true

# Check 1: Backend running
echo "📌 Check 1: Backend Status"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend running at http://localhost:8000"
else
    echo "   ❌ Backend NOT running"
    echo "      Start: cd symphainy-platform && python3 main.py"
    READY=false
fi

# Check 2: Frontend running
echo ""
echo "📌 Check 2: Frontend Status"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend running at http://localhost:3000"
else
    echo "   ⚠️  Frontend NOT running (optional for some tests)"
    echo "      Start: cd symphainy-frontend && npm run dev"
fi

# Check 3: Demo files generated
echo ""
echo "📌 Check 3: Demo Files"
DEMO_DIR="scripts/mvpdemoscript/demo_files"
if [ -d "$DEMO_DIR" ]; then
    DEFENSE_FILES=$(find "$DEMO_DIR" -name "*Defense*" -type d 2>/dev/null | wc -l)
    UNDERWRITING_FILES=$(find "$DEMO_DIR" -name "*Underwriting*" -type d 2>/dev/null | wc -l)
    COEXISTENCE_FILES=$(find "$DEMO_DIR" -name "*Coexistence*" -type d 2>/dev/null | wc -l)
    
    if [ $DEFENSE_FILES -gt 0 ] && [ $UNDERWRITING_FILES -gt 0 ] && [ $COEXISTENCE_FILES -gt 0 ]; then
        echo "   ✅ All 3 demo scenarios generated"
        echo "      - Defense T&E: $DEFENSE_FILES directories"
        echo "      - Underwriting: $UNDERWRITING_FILES directories"
        echo "      - Coexistence: $COEXISTENCE_FILES directories"
    else
        echo "   ❌ Demo files incomplete"
        echo "      Generate: cd scripts/mvpdemoscript && python3 generate_symphainy_demo.py"
        READY=false
    fi
else
    echo "   ❌ Demo files directory not found"
    echo "      Generate: cd scripts/mvpdemoscript && python3 generate_symphainy_demo.py"
    READY=false
fi

# Check 4: Test dependencies
echo ""
echo "📌 Check 4: Test Dependencies"
if python3 -c "import pytest" 2>/dev/null; then
    echo "   ✅ pytest installed"
else
    echo "   ❌ pytest not installed"
    echo "      Install: pip install pytest pytest-asyncio"
    READY=false
fi

if python3 -c "import httpx" 2>/dev/null; then
    echo "   ✅ httpx installed"
else
    echo "   ❌ httpx not installed"
    echo "      Install: pip install httpx"
    READY=false
fi

if python3 -c "import websockets" 2>/dev/null; then
    echo "   ✅ websockets installed"
else
    echo "   ❌ websockets not installed"
    echo "      Install: pip install websockets"
    READY=false
fi

# Check 5: Test files exist
echo ""
echo "📌 Check 5: Test Suite Files"
TEST_FILES=(
    "tests/e2e/test_demo_files_integration.py"
    "tests/e2e/test_api_endpoints_reality.py"
    "tests/e2e/test_websocket_endpoints_reality.py"
    "tests/e2e/test_content_pillar_functional.py"
    "tests/e2e/test_document_generation_functional.py"
    "tests/e2e/test_complete_user_journeys_functional.py"
)

MISSING_FILES=0
for test_file in "${TEST_FILES[@]}"; do
    if [ -f "$test_file" ]; then
        echo "   ✅ $test_file"
    else
        echo "   ❌ $test_file - MISSING"
        MISSING_FILES=$((MISSING_FILES + 1))
        READY=false
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "   ✅ All critical test files present"
fi

# Check 6: Backend API endpoints (sample)
echo ""
echo "📌 Check 6: Backend API Sample"
if curl -s http://localhost:8000/api/global/session -X POST > /dev/null 2>&1; then
    echo "   ✅ Session API responding"
else
    echo "   ⚠️  Session API not responding"
    echo "      (Backend may be starting up or missing API endpoints)"
fi

# Final verdict
echo ""
echo "═══════════════════════════════════════════════════════════════════"
if [ "$READY" = true ]; then
    echo "🎉 READY TO RUN TESTING GAUNTLET!"
    echo ""
    echo "Run the complete test suite:"
    echo "  ./tests/run_complete_testing_gauntlet.sh"
    echo ""
else
    echo "❌ NOT READY - Fix issues above first"
    echo ""
    echo "Once fixed, run this check again:"
    echo "  ./tests/check_testing_readiness.sh"
    echo ""
fi
echo "═══════════════════════════════════════════════════════════════════"
echo ""

