#!/bin/bash
# Helper script to run E2E tests locally
# Usage: ./scripts/run-tests-locally.sh [critical|full|single TEST_NAME]

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SymphAIny Local Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
export TEST_FRONTEND_URL="http://localhost:${FRONTEND_PORT}"
export TEST_BACKEND_URL="http://localhost:${BACKEND_PORT}"

# Determine test suite
TEST_SUITE=${1:-critical}
SPECIFIC_TEST=${2:-}

echo -e "\n${YELLOW}Test Suite:${NC} ${TEST_SUITE}"

# Check if services are running
check_service() {
    local url=$1
    local name=$2
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not running"
        return 1
    fi
}

echo -e "\n${YELLOW}Checking services...${NC}"

# Check backend
if ! check_service "http://localhost:${BACKEND_PORT}/health" "Backend"; then
    echo -e "${YELLOW}Starting backend...${NC}"
    cd symphainy-platform
    python3 main.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/symphainy-backend.pid
    cd ..
    sleep 5
    if ! check_service "http://localhost:${BACKEND_PORT}/health" "Backend"; then
        echo -e "${RED}Failed to start backend${NC}"
        exit 1
    fi
fi

# Check frontend
if ! check_service "http://localhost:${FRONTEND_PORT}" "Frontend"; then
    echo -e "${YELLOW}Starting frontend...${NC}"
    cd symphainy-frontend
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/symphainy-frontend.pid
    cd ..
    sleep 10
    if ! check_service "http://localhost:${FRONTEND_PORT}" "Frontend"; then
        echo -e "${RED}Failed to start frontend${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}✓${NC} All services running"

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
cd tests

case $TEST_SUITE in
    critical)
        echo -e "${YELLOW}Running 6 critical tests${NC}"
        pytest e2e/test_complete_cto_demo_journey.py \
               e2e/test_persistent_ui.py \
               e2e/test_content_pillar_smoke.py \
               e2e/test_insights_pillar_smoke.py \
               e2e/test_operations_pillar_smoke.py \
               e2e/test_business_outcomes_pillar_smoke.py \
               -v -s --timeout=300
        ;;
    full)
        echo -e "${YELLOW}Running full E2E test suite${NC}"
        pytest e2e/ -v -s --timeout=300
        ;;
    single)
        if [ -z "$SPECIFIC_TEST" ]; then
            echo -e "${RED}Error: Must specify test file for single test mode${NC}"
            echo -e "${YELLOW}Usage: ./run-tests-locally.sh single test_complete_cto_demo_journey.py${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Running single test: ${SPECIFIC_TEST}${NC}"
        pytest "e2e/${SPECIFIC_TEST}" -v -s --timeout=300
        ;;
    *)
        echo -e "${RED}Unknown test suite: ${TEST_SUITE}${NC}"
        echo -e "${YELLOW}Usage: ./run-tests-locally.sh [critical|full|single TEST_NAME]${NC}"
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

cd ..

# Show results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}✗ TESTS FAILED${NC}"
    echo -e "${RED}========================================${NC}"
fi

# Show screenshots location
if [ -d "tests/screenshots" ]; then
    echo -e "\n${YELLOW}Screenshots saved to:${NC} tests/screenshots/"
    echo -e "${YELLOW}View them to see what happened during tests${NC}"
fi

exit $TEST_EXIT_CODE




