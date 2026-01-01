#!/bin/bash
# CTO Demo Test Runner - Production Platform
# 
# This script:
# 1. Starts the production platform (containers)
# 2. Waits for services to be healthy
# 3. Runs all 3 CTO demo tests
# 4. Validates platform functionality end-to-end
#
# Usage:
#   ./run_cto_demo_tests.sh [--skip-startup] [--skip-teardown]
#
# Options:
#   --skip-startup: Skip container startup (assumes platform is already running)
#   --skip-teardown: Skip container teardown after tests (keep platform running)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_STARTUP=false
SKIP_TEARDOWN=false

for arg in "$@"; do
    case $arg in
        --skip-startup)
            SKIP_STARTUP=true
            shift
            ;;
        --skip-teardown)
            SKIP_TEARDOWN=true
            shift
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $arg${NC}"
            shift
            ;;
    esac
done

# Configuration
BACKEND_URL="${TEST_BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${TEST_FRONTEND_URL:-http://localhost:3000}"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
HEALTH_CHECK_INTERVAL=5   # Check every 5 seconds

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CTO Demo Test Runner - Production Platform${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================================================
# STEP 1: Start Production Platform
# ============================================================================

if [ "$SKIP_STARTUP" = false ]; then
    echo -e "${BLUE}Step 1: Starting production platform...${NC}"
    echo ""
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ docker-compose not found. Please install Docker Compose.${NC}"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
        exit 1
    fi
    
    # Start containers
    echo -e "${YELLOW}Starting Docker containers...${NC}"
    docker-compose up -d
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to start Docker containers${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker containers started${NC}"
    echo ""
    
    # ============================================================================
    # STEP 2: Wait for Services to be Healthy
    # ============================================================================
    
    echo -e "${BLUE}Step 2: Waiting for services to be healthy...${NC}"
    echo ""
    
    # Wait for backend to be ready
    echo -e "${YELLOW}Waiting for backend API (${BACKEND_URL})...${NC}"
    BACKEND_READY=false
    ELAPSED=0
    
    while [ $ELAPSED -lt $HEALTH_CHECK_TIMEOUT ]; do
        if curl -f -s "${BACKEND_URL}/api/health" > /dev/null 2>&1; then
            BACKEND_READY=true
            break
        fi
        
        echo -e "${YELLOW}  Backend not ready yet... (${ELAPSED}s / ${HEALTH_CHECK_TIMEOUT}s)${NC}"
        sleep $HEALTH_CHECK_INTERVAL
        ELAPSED=$((ELAPSED + HEALTH_CHECK_INTERVAL))
    done
    
    if [ "$BACKEND_READY" = false ]; then
        echo -e "${RED}❌ Backend did not become healthy within ${HEALTH_CHECK_TIMEOUT}s${NC}"
        echo -e "${YELLOW}Checking container logs...${NC}"
        docker-compose logs --tail=50 backend || true
        exit 1
    fi
    
    echo -e "${GREEN}✅ Backend API is healthy${NC}"
    
    # Wait for frontend to be ready (optional - may not be needed for API tests)
    echo -e "${YELLOW}Checking frontend (${FRONTEND_URL})...${NC}"
    if curl -f -s "${FRONTEND_URL}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend not accessible (may not be needed for API tests)${NC}"
    fi
    
    # Wait for infrastructure services
    echo -e "${YELLOW}Checking infrastructure services...${NC}"
    
    # Check Consul
    if curl -f -s "http://localhost:8500/v1/status/leader" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Consul is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Consul not accessible${NC}"
    fi
    
    # Check Redis
    if docker exec symphainy-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis not accessible${NC}"
    fi
    
    # Check ArangoDB
    if curl -f -s "http://localhost:8529/_api/version" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ArangoDB is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  ArangoDB not accessible${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ All services are ready${NC}"
    echo ""
    
    # Give services a moment to fully initialize
    echo -e "${YELLOW}Waiting 10 seconds for services to fully initialize...${NC}"
    sleep 10
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping startup (--skip-startup flag set)${NC}"
    echo -e "${YELLOW}Verifying backend is accessible...${NC}"
    
    if ! curl -f -s "${BACKEND_URL}/api/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend is not accessible at ${BACKEND_URL}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Backend is accessible${NC}"
    echo ""
fi

# ============================================================================
# STEP 3: Run CTO Demo Tests
# ============================================================================

echo -e "${BLUE}Step 3: Running CTO demo tests...${NC}"
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Please install pytest.${NC}"
    exit 1
fi

# Check if demo files exist
DEMO_FILES_DIR="/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files"
if [ ! -d "$DEMO_FILES_DIR" ]; then
    echo -e "${YELLOW}⚠️  Demo files directory not found: ${DEMO_FILES_DIR}${NC}"
    echo -e "${YELLOW}   Some tests may be skipped${NC}"
fi

# Set environment variables for tests
export TEST_BACKEND_URL="${BACKEND_URL}"
export TEST_FRONTEND_URL="${FRONTEND_URL}"
export PYTHONPATH="${SCRIPT_DIR}/symphainy-platform:${PYTHONPATH}"

# Run the tests
echo -e "${YELLOW}Running CTO demo tests...${NC}"
echo ""

cd "${SCRIPT_DIR}"

# Run all 3 CTO demo tests
# Note: The tests use 'both_servers' fixture which should work with production containers
# If the fixture tries to start new servers, we may need to modify it or create a production-specific fixture
pytest tests/e2e/production/cto_demos/ \
    -v \
    --tb=short \
    --color=yes \
    -m "cto_demo" \
    --timeout=600 \
    -s \
    --maxfail=1

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ All CTO demo tests PASSED${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ Some CTO demo tests FAILED${NC}"
    echo -e "${RED}========================================${NC}"
fi

# ============================================================================
# STEP 4: Teardown (Optional)
# ============================================================================

if [ "$SKIP_TEARDOWN" = false ]; then
    echo ""
    echo -e "${BLUE}Step 4: Cleaning up...${NC}"
    echo ""
    
    read -p "Stop Docker containers? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Stopping Docker containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Containers stopped${NC}"
    else
        echo -e "${YELLOW}Keeping containers running${NC}"
    fi
else
    echo -e "${YELLOW}⏭️  Skipping teardown (--skip-teardown flag set)${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test run complete${NC}"
echo -e "${BLUE}========================================${NC}"

exit $TEST_EXIT_CODE

