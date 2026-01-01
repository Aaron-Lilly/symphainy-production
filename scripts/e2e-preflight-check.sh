#!/bin/bash
# E2E Test Pre-Flight Check
# Verifies all prerequisites for running E2E tests

set -e

echo "════════════════════════════════════════════════════════════════════════════"
echo "  🎯 E2E TEST PRE-FLIGHT CHECK"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECK_PASSED=0
CHECK_FAILED=0

# Function to check status
check_status() {
    local name="$1"
    local command="$2"
    
    echo -n "Checking $name... "
    
    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((CHECK_PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((CHECK_FAILED++))
        return 1
    fi
}

# Function to check port
check_port() {
    local name="$1"
    local port="$2"
    local url="$3"
    
    echo -n "Checking $name (port $port)... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        ((CHECK_PASSED++))
        return 0
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        ((CHECK_FAILED++))
        echo "  └─ Start with: See E2E_TEST_EXECUTION_PLAN.md"
        return 1
    fi
}

echo "──────────────────────────────────────────────────────────────────────────"
echo "  PART 1: Python Environment"
echo "──────────────────────────────────────────────────────────────────────────"
echo ""

check_status "Python 3" "python3 --version"
check_status "pip" "pip --version"
check_status "Playwright library" "python3 -c 'import playwright'"
check_status "pytest-playwright" "python3 -c 'import pytest_playwright'"
check_status "pytest-asyncio" "python3 -c 'import pytest_asyncio'"

echo ""
echo "──────────────────────────────────────────────────────────────────────────"
echo "  PART 2: Playwright Browser"
echo "──────────────────────────────────────────────────────────────────────────"
echo ""

# Check if Chromium is installed
echo -n "Checking Chromium browser... "
if [ -d "$HOME/.cache/ms-playwright/chromium"* ] 2>/dev/null; then
    CHROMIUM_VERSION=$(ls -d $HOME/.cache/ms-playwright/chromium-* 2>/dev/null | head -1 | sed 's/.*chromium-//')
    echo -e "${GREEN}✅ INSTALLED${NC} (version $CHROMIUM_VERSION)"
    ((CHECK_PASSED++))
else
    echo -e "${RED}❌ NOT INSTALLED${NC}"
    echo "  └─ Install with: python3 -m playwright install chromium"
    ((CHECK_FAILED++))
fi

echo ""
echo "──────────────────────────────────────────────────────────────────────────"
echo "  PART 3: Services"
echo "──────────────────────────────────────────────────────────────────────────"
echo ""

check_port "Frontend" "3000" "http://localhost:3000"
check_port "Backend" "8000" "http://localhost:8000/health"

echo ""
echo "──────────────────────────────────────────────────────────────────────────"
echo "  PART 4: Test Environment"
echo "──────────────────────────────────────────────────────────────────────────"
echo ""

# Check if test directory exists
echo -n "Checking test directory... "
if [ -d "tests/e2e" ]; then
    TEST_COUNT=$(find tests/e2e -name "test_*.py" -type f | wc -l)
    echo -e "${GREEN}✅ EXISTS${NC} ($TEST_COUNT test files)"
    ((CHECK_PASSED++))
else
    echo -e "${RED}❌ NOT FOUND${NC}"
    ((CHECK_FAILED++))
fi

# Check if critical test exists
echo -n "Checking critical test... "
if [ -f "tests/e2e/test_complete_cto_demo_journey.py" ]; then
    echo -e "${GREEN}✅ EXISTS${NC}"
    ((CHECK_PASSED++))
else
    echo -e "${RED}❌ NOT FOUND${NC}"
    ((CHECK_FAILED++))
fi

# Check environment variables
echo -n "Checking TEST_FRONTEND_URL... "
if [ -n "$TEST_FRONTEND_URL" ]; then
    echo -e "${GREEN}✅ SET${NC} ($TEST_FRONTEND_URL)"
    ((CHECK_PASSED++))
else
    echo -e "${YELLOW}⚠️  NOT SET${NC} (will default to http://localhost:3000)"
fi

echo -n "Checking TEST_BACKEND_URL... "
if [ -n "$TEST_BACKEND_URL" ]; then
    echo -e "${GREEN}✅ SET${NC} ($TEST_BACKEND_URL)"
    ((CHECK_PASSED++))
else
    echo -e "${YELLOW}⚠️  NOT SET${NC} (will default to http://localhost:8000)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "  SUMMARY"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "Checks Passed: ${GREEN}$CHECK_PASSED${NC}"
echo -e "Checks Failed: ${RED}$CHECK_FAILED${NC}"
echo ""

if [ $CHECK_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED! Ready to run E2E tests!${NC}"
    echo ""
    echo "Run the critical test:"
    echo "  pytest tests/e2e/test_complete_cto_demo_journey.py::test_complete_cto_demo_journey -v -s"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Next steps:"
    if ! python3 -c 'import playwright' &>/dev/null; then
        echo "  1. Install Playwright: pip install playwright pytest-playwright"
    fi
    if [ ! -d "$HOME/.cache/ms-playwright/chromium"* ] 2>/dev/null; then
        echo "  2. Install Chromium: python3 -m playwright install chromium"
    fi
    if ! curl -s http://localhost:8000/health &>/dev/null; then
        echo "  3. Start Backend: cd symphainy-platform && python3 main.py"
    fi
    if ! curl -s http://localhost:3000 &>/dev/null; then
        echo "  4. Start Frontend: cd symphainy-frontend && npm run dev"
    fi
    echo ""
    echo "See E2E_TEST_EXECUTION_PLAN.md for detailed instructions"
    echo ""
    exit 1
fi




