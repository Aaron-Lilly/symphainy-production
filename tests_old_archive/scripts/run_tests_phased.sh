#!/bin/bash
# Phased Test Execution Script
# Runs tests in order of complexity, making it easy to identify and fix issues

set -e  # Exit on error (we'll handle this per phase)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test phases (in order of complexity)
PHASES=(
    "smoke:API Smoke Tests:tests/e2e/production/test_api_smoke.py"
    "config:Configuration Validation:tests/config/test_production_config_validation.py"
    "infra:Infrastructure Health:tests/infrastructure/test_infrastructure_health.py"
    "websocket:WebSocket Connectivity:tests/e2e/production/test_websocket_smoke.py"
    "auth:Authentication & Registration:tests/e2e/production/test_user_journey_smoke.py::TestUserJourneySmoke::test_user_registration_journey"
    "session:Session Management:tests/e2e/production/test_user_journey_smoke.py::TestUserJourneySmoke::test_user_registration_journey"
    "upload:File Upload (Basic):tests/e2e/production/test_real_file_upload_flow.py::TestRealFileUploadFlow::test_real_file_upload_complete_flow"
    "journey:User Journey (Basic):tests/e2e/production/test_user_journey_smoke.py::TestUserJourneySmoke::test_file_upload_journey"
    "cross:Cross-Pillar Workflows:tests/e2e/production/test_cross_pillar_workflows.py"
    "state:State Management:tests/e2e/production/test_state_management.py"
    "scenarios:Real User Scenarios:tests/e2e/production/test_real_user_scenarios.py"
    "integration:Complex Integration:tests/e2e/production/test_complex_integration_scenarios.py"
    "startup:Startup Sequence:tests/e2e/production/test_production_startup_sequence.py"
)

# Parse command line arguments
PHASE_FILTER=""
RUN_ALL=false
STOP_ON_FAILURE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            PHASE_FILTER="$2"
            shift 2
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --continue)
            STOP_ON_FAILURE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --phase PHASE    Run only a specific phase (e.g., 'smoke', 'config')"
            echo "  --all            Run all phases without stopping"
            echo "  --continue       Continue to next phase even if current phase fails"
            echo "  -v, --verbose    Verbose output"
            echo "  --help           Show this help message"
            echo ""
            echo "Available phases:"
            for phase in "${PHASES[@]}"; do
                IFS=':' read -r id name _ <<< "$phase"
                echo "  $id - $name"
            done
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to run a test phase
run_phase() {
    local phase_id=$1
    local phase_name=$2
    local test_path=$3
    
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}Phase: $phase_id - $phase_name${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
    
    if [ "$VERBOSE" = true ]; then
        python3 -m pytest "$test_path" -v --tb=short
    else
        python3 -m pytest "$test_path" -v --tb=line
    fi
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Phase $phase_id PASSED${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Phase $phase_id FAILED (exit code: $exit_code)${NC}"
        return $exit_code
    fi
}

# Function to print summary
print_summary() {
    local passed=$1
    local failed=$2
    local total=$3
    
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}Test Execution Summary${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo -e "Total Phases: $total"
    echo -e "${GREEN}Passed: $passed${NC}"
    echo -e "${RED}Failed: $failed${NC}"
    echo ""
}

# Set TEST_MODE to ensure tests use test Supabase project
export TEST_MODE=true

# Load test environment if available
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(dirname "$SCRIPT_DIR")"
ENV_TEST_FILE="$TESTS_DIR/.env.test"
if [ -f "$ENV_TEST_FILE" ]; then
    source "$ENV_TEST_FILE"
    echo -e "${GREEN}✅ Loaded test environment from .env.test${NC}"
fi

# Main execution
PASSED=0
FAILED=0
TOTAL=0
FAILED_PHASES=()

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}SymphAIny Platform - Phased Test Execution${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "Running tests in order of complexity..."
echo "Use Ctrl+C to stop at any time"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running on http://localhost:8000${NC}"
    echo "Please start the backend first:"
    echo "  docker-compose -f docker-compose.test.yml up -d"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running${NC}"
if [ -n "$TEST_SUPABASE_URL" ]; then
    echo -e "${GREEN}✅ Using test Supabase: ${TEST_SUPABASE_URL}${NC}"
fi
echo ""

# Run phases
for phase in "${PHASES[@]}"; do
    IFS=':' read -r phase_id phase_name test_path <<< "$phase"
    
    # Skip if phase filter is set and doesn't match
    if [ -n "$PHASE_FILTER" ] && [ "$phase_id" != "$PHASE_FILTER" ]; then
        continue
    fi
    
    TOTAL=$((TOTAL + 1))
    
    if run_phase "$phase_id" "$phase_name" "$test_path"; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
        FAILED_PHASES+=("$phase_id:$phase_name")
        
        if [ "$STOP_ON_FAILURE" = true ] && [ "$RUN_ALL" = false ]; then
            echo ""
            echo -e "${YELLOW}⚠️  Stopping due to failure in phase: $phase_id${NC}"
            echo "To continue to next phase, run with --continue"
            echo "To run all phases regardless of failures, run with --all"
            print_summary $PASSED $FAILED $TOTAL
            exit 1
        fi
    fi
    
    # Small delay between phases
    sleep 1
done

# Print final summary
print_summary $PASSED $FAILED $TOTAL

if [ ${#FAILED_PHASES[@]} -gt 0 ]; then
    echo -e "${RED}Failed Phases:${NC}"
    for failed_phase in "${FAILED_PHASES[@]}"; do
        IFS=':' read -r phase_id phase_name <<< "$failed_phase"
        echo -e "  ${RED}❌ $phase_id - $phase_name${NC}"
    done
    echo ""
    echo "To re-run a specific phase:"
    echo "  $0 --phase <phase_id>"
    exit 1
else
    echo -e "${GREEN}✅ All phases passed!${NC}"
    exit 0
fi

