#!/bin/bash
# Helper script to start infrastructure and run Smart City integration tests.
#
# WHAT: Start infrastructure and run integration tests
# HOW: Docker Compose for infrastructure, pytest for tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"
cd "$PROJECT_ROOT"

echo -e "${GREEN}🚀 Smart City Integration Test Runner${NC}"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose is not installed or not in PATH${NC}"
    exit 1
fi

# Function to check if infrastructure is running
check_infrastructure() {
    echo -e "${YELLOW}📋 Checking infrastructure status...${NC}"
    
    SERVICES=("symphainy-redis" "symphainy-arangodb" "symphainy-meilisearch" "symphainy-consul")
    RUNNING=0
    
    for service in "${SERVICES[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${service}$"; then
            echo -e "  ✅ ${service} is running"
            RUNNING=$((RUNNING + 1))
        else
            echo -e "  ❌ ${service} is not running"
        fi
    done
    
    if [ $RUNNING -eq ${#SERVICES[@]} ]; then
        return 0  # All services running
    else
        return 1  # Some services not running
    fi
}

# Function to start infrastructure
start_infrastructure() {
    echo -e "${YELLOW}🏗️  Starting infrastructure services...${NC}"
    
    if [ ! -f "docker-compose.infrastructure.yml" ]; then
        echo -e "${RED}❌ docker-compose.infrastructure.yml not found${NC}"
        exit 1
    fi
    
    docker-compose -f docker-compose.infrastructure.yml up -d
    
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    sleep 10
    
    # Wait for services to be ready
    MAX_WAIT=120
    WAIT_TIME=0
    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        if check_infrastructure; then
            echo -e "${GREEN}✅ All infrastructure services are healthy${NC}"
            return 0
        fi
        echo -e "  ⏳ Waiting... (${WAIT_TIME}s/${MAX_WAIT}s)"
        sleep 5
        WAIT_TIME=$((WAIT_TIME + 5))
    done
    
    echo -e "${RED}❌ Infrastructure services did not become healthy within ${MAX_WAIT} seconds${NC}"
    echo -e "${YELLOW}💡 Check logs with: docker-compose -f docker-compose.infrastructure.yml logs${NC}"
    return 1
}

# Function to stop infrastructure
stop_infrastructure() {
    if [ "$1" = "--keep-running" ]; then
        echo -e "${YELLOW}ℹ️  Keeping infrastructure running (--keep-running flag)${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}🛑 Stopping infrastructure services...${NC}"
    docker-compose -f docker-compose.infrastructure.yml down
    echo -e "${GREEN}✅ Infrastructure stopped${NC}"
}

# Parse command line arguments
KEEP_RUNNING=false
RUN_TESTS=true
TEST_MARKER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-running)
            KEEP_RUNNING=true
            shift
            ;;
        --skip-tests)
            RUN_TESTS=false
            shift
            ;;
        --marker)
            TEST_MARKER="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --keep-running    Keep infrastructure running after tests"
            echo "  --skip-tests      Only start infrastructure, don't run tests"
            echo "  --marker MARKER   Run only tests with specific marker (e.g., real_infrastructure)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
echo ""

# Check if infrastructure is already running
if check_infrastructure; then
    echo -e "${GREEN}✅ Infrastructure is already running${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Infrastructure is not running${NC}"
    echo ""
    
    read -p "Start infrastructure now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! start_infrastructure; then
            exit 1
        fi
    else
        echo -e "${RED}❌ Cannot run tests without infrastructure${NC}"
        exit 1
    fi
fi

echo ""

# Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    echo -e "${GREEN}🧪 Running integration tests...${NC}"
    echo ""
    
    TEST_CMD="python3 -m pytest tests/integration/smart_city/ -v --tb=short"
    
    if [ -n "$TEST_MARKER" ]; then
        TEST_CMD="$TEST_CMD -m $TEST_MARKER"
        echo -e "${YELLOW}Running tests with marker: ${TEST_MARKER}${NC}"
    fi
    
    echo "Command: $TEST_CMD"
    echo ""
    
    if eval $TEST_CMD; then
        echo ""
        echo -e "${GREEN}✅ All integration tests passed!${NC}"
        TEST_RESULT=0
    else
        echo ""
        echo -e "${RED}❌ Some integration tests failed${NC}"
        TEST_RESULT=1
    fi
else
    echo -e "${YELLOW}⏭️  Skipping tests (--skip-tests flag)${NC}"
    TEST_RESULT=0
fi

echo ""

# Cleanup
if [ "$KEEP_RUNNING" = true ]; then
    stop_infrastructure --keep-running
else
    read -p "Stop infrastructure? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_infrastructure
    else
        echo -e "${YELLOW}ℹ️  Infrastructure will continue running${NC}"
        echo -e "${YELLOW}💡 Stop manually with: docker-compose -f docker-compose.infrastructure.yml down${NC}"
    fi
fi

echo ""
exit $TEST_RESULT

