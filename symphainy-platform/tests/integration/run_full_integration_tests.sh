#!/bin/bash
# Full Platform Integration Test Runner
# 
# This script:
# 1. Checks infrastructure health
# 2. Verifies backend is running
# 3. Runs comprehensive integration tests
# 4. Generates test reports

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🧪 Full Platform Integration Test Runner${NC}"
echo "=========================================="
echo ""

# Check if backend is running
echo -e "${BLUE}📡 Checking backend health...${NC}"
if curl -s http://localhost:8000/api/auth/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    BACKEND_HEALTH=$(curl -s http://localhost:8000/api/auth/health | python3 -m json.tool 2>/dev/null || echo "{}")
    echo "$BACKEND_HEALTH" | head -10
else
    echo -e "${RED}❌ Backend is not running on port 8000${NC}"
    echo -e "${YELLOW}⚠️  Please start the backend first:${NC}"
    echo "   cd $PROJECT_ROOT && ./startup.sh"
    exit 1
fi

# Check infrastructure services
echo ""
echo -e "${BLUE}🔍 Checking infrastructure services...${NC}"

check_service() {
    local name=$1
    local url=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $name is not accessible${NC}"
        return 1
    fi
}

check_service "Redis" "http://localhost:6379" || true
check_service "ArangoDB" "http://localhost:8529/_api/version" || true
check_service "Consul" "http://localhost:8500/v1/status/leader" || true

# Run tests
echo ""
echo -e "${BLUE}🚀 Running integration tests...${NC}"
echo ""

# Run pytest with coverage and reporting
pytest tests/integration/test_full_platform_integration.py \
    tests/integration/test_auth_integration.py \
    -v \
    --asyncio-mode=auto \
    --tb=short \
    --junitxml=tests/integration/results.xml \
    --html=tests/integration/report.html \
    --self-contained-html \
    "$@"

TEST_EXIT_CODE=$?

# Report results
echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All integration tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo ""
echo -e "${BLUE}📊 Test reports generated:${NC}"
echo "   - JUnit XML: tests/integration/results.xml"
echo "   - HTML Report: tests/integration/report.html"

exit $TEST_EXIT_CODE




