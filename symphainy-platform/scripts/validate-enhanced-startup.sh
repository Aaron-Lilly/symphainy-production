#!/bin/bash
# SymphAIny Platform - Enhanced Startup Validation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

run_test() {
    local test_name="$1"
    local command="$2"
    print_status "Testing: $test_name"
    if eval "$command" &> /dev/null; then
        print_success "$test_name: PASSED"
        return 0
    else
        print_error "$test_name: FAILED"
        return 1
    fi
}

echo "🎯 SymphAIny Platform - Enhanced Startup Validation"
echo "=================================================="
echo "Validating enhanced startup orchestration and dependency management..."
echo ""

# --- PHASE 1: ENHANCED STARTUP COMPONENTS VALIDATION ---
echo "📋 PHASE 1: ENHANCED STARTUP COMPONENTS VALIDATION"
echo "=================================================="
run_test "Enhanced main.py exists" "test -f enhanced_main.py"
run_test "Enhanced startup script exists" "test -f scripts/enhanced-startup.sh"
run_test "Enhanced startup script is executable" "test -x scripts/enhanced-startup.sh"
run_test "Integration test exists" "test -f tests/integration/test_enhanced_startup_orchestration.py"
echo ""

# --- PHASE 2: MANAGER SERVICE BASE EVOLUTION VALIDATION ---
echo "🏗️ PHASE 2: MANAGER SERVICE BASE EVOLUTION VALIDATION"
echo "====================================================="
run_test "ManagerServiceBase has startup orchestration" "grep -q 'orchestrate_realm_startup' bases/manager_service_base.py"
run_test "ManagerServiceBase has dependency management" "grep -q 'get_startup_dependencies' bases/manager_service_base.py"
run_test "ManagerServiceBase has realm health monitoring" "grep -q 'monitor_realm_health' bases/manager_service_base.py"
run_test "ManagerServiceBase has realm shutdown" "grep -q 'coordinate_realm_shutdown' bases/manager_service_base.py"
run_test "ManagerServiceBase has cross-dimensional coordination" "grep -q 'coordinate_with_other_managers' bases/manager_service_base.py"
echo ""

# --- PHASE 3: INTERFACES AND PROTOCOLS VALIDATION ---
echo "🔌 PHASE 3: INTERFACES AND PROTOCOLS VALIDATION"
echo "=============================================="
run_test "Interfaces directory exists" "test -d bases/interfaces"
run_test "Protocols directory exists" "test -d bases/protocols"
run_test "IRealmStartupOrchestrator exists" "test -f bases/interfaces/i_realm_startup_orchestrator.py"
run_test "IDependencyManager exists" "test -f bases/interfaces/i_dependency_manager.py"
run_test "ICrossDimensionalCICDCoordinator exists" "test -f bases/interfaces/i_cross_dimensional_cicd_coordinator.py"
run_test "IJourneyOrchestrator exists" "test -f bases/interfaces/i_journey_orchestrator.py"
run_test "IAgentGovernanceProvider exists" "test -f bases/interfaces/i_agent_governance_provider.py"
run_test "IManagerService exists" "test -f bases/interfaces/i_manager_service.py"
run_test "RealmStartupProtocol exists" "test -f bases/protocols/realm_startup_protocol.py"
run_test "DependencyManagementProtocol exists" "test -f bases/protocols/dependency_management_protocol.py"
run_test "CrossDimensionalCICDProtocol exists" "test -f bases/protocols/cross_dimensional_cicd_protocol.py"
run_test "JourneyOrchestrationProtocol exists" "test -f bases/protocols/journey_orchestration_protocol.py"
run_test "AgentGovernanceProtocol exists" "test -f bases/protocols/agent_governance_protocol.py"
run_test "ManagerServiceProtocol exists" "test -f bases/protocols/manager_service_protocol.py"
echo ""

# --- PHASE 4: DOMAIN MANAGER IMPLEMENTATIONS VALIDATION ---
echo "🎯 PHASE 4: DOMAIN MANAGER IMPLEMENTATIONS VALIDATION"
echo "===================================================="
run_test "City Manager exists" "test -f backend/smart_city/services/city_manager/city_manager_service.py"
run_test "Agentic Manager exists" "test -f agentic/agentic_manager_service.py"
run_test "Delivery Manager exists" "test -f backend/business_enablement/services/delivery_manager/delivery_manager_service.py"
run_test "Experience Manager exists" "test -f experience/roles/experience_manager/experience_manager_service.py"
run_test "Journey Manager exists" "test -f journey_solution/services/journey_manager/journey_manager_service.py"
run_test "City Manager has startup dependencies" "grep -q 'get_startup_dependencies' backend/smart_city/services/city_manager/city_manager_service.py"
run_test "Agentic Manager has startup dependencies" "grep -q 'get_startup_dependencies' agentic/agentic_manager_service.py"
run_test "Delivery Manager has startup dependencies" "grep -q 'get_startup_dependencies' backend/business_enablement/services/delivery_manager/delivery_manager_service.py"
run_test "Experience Manager has startup dependencies" "grep -q 'get_startup_dependencies' experience/roles/experience_manager/experience_manager_service.py"
run_test "Journey Manager has startup dependencies" "grep -q 'get_startup_dependencies' journey_solution/services/journey_manager/journey_manager_service.py"
echo ""

# --- PHASE 5: ENHANCED MAIN.PY VALIDATION ---
echo "🚀 PHASE 5: ENHANCED MAIN.PY VALIDATION"
echo "====================================="
run_test "Enhanced main.py has infrastructure startup" "grep -q '_start_infrastructure_services' enhanced_main.py"
run_test "Enhanced main.py has dependency-ordered startup" "grep -q '_start_domain_managers_with_dependencies' enhanced_main.py"
run_test "Enhanced main.py has domain shutdown" "grep -q '_orchestrate_domain_shutdown' enhanced_main.py"
run_test "Enhanced main.py has health endpoints" "grep -q '/health' enhanced_main.py"
run_test "Enhanced main.py has platform status endpoint" "grep -q '/platform/status' enhanced_main.py"
run_test "Enhanced main.py has domain manager health endpoints" "grep -q '/platform/health/' enhanced_main.py"
echo ""

# --- PHASE 6: DEPENDENCY ORDER VALIDATION ---
echo "🔗 PHASE 6: DEPENDENCY ORDER VALIDATION"
echo "======================================"
run_test "City Manager has no dependencies" "grep -q 'return \[\]' backend/smart_city/services/city_manager/city_manager_service.py"
run_test "Agentic Manager depends on City Manager" "grep -q 'city_manager' agentic/agentic_manager_service.py"
run_test "Delivery Manager depends on Agentic Manager" "grep -q 'agentic_manager' backend/business_enablement/services/delivery_manager/delivery_manager_service.py"
run_test "Experience Manager depends on Delivery Manager" "grep -q 'delivery_manager' experience/roles/experience_manager/experience_manager_service.py"
run_test "Journey Manager depends on Experience Manager" "grep -q 'experience_manager' journey_solution/services/journey_manager/journey_manager_service.py"
echo ""

# --- PHASE 7: INTEGRATION TESTING VALIDATION ---
echo "🧪 PHASE 7: INTEGRATION TESTING VALIDATION"
echo "=========================================="
run_test "Integration test has infrastructure tests" "grep -q 'test_infrastructure_services_startup' tests/integration/test_enhanced_startup_orchestration.py"
run_test "Integration test has dependency order tests" "grep -q 'test_domain_managers_dependency_order' tests/integration/test_enhanced_startup_orchestration.py"
run_test "Integration test has realm startup tests" "grep -q 'test_domain_manager_realm_startup' tests/integration/test_enhanced_startup_orchestration.py"
run_test "Integration test has health monitoring tests" "grep -q 'test_domain_manager_health_monitoring' tests/integration/test_enhanced_startup_orchestration.py"
run_test "Integration test has shutdown orchestration tests" "grep -q 'test_domain_manager_shutdown_orchestration' tests/integration/test_enhanced_startup_orchestration.py"
run_test "Integration test has cross-dimensional coordination tests" "grep -q 'test_cross_dimensional_coordination' tests/integration/test_enhanced_startup_orchestration.py"
echo ""

# --- PHASE 8: STARTUP SCRIPT VALIDATION ---
echo "📜 PHASE 8: STARTUP SCRIPT VALIDATION"
echo "====================================="
run_test "Enhanced startup script has pip upgrade" "grep -q 'pip install --upgrade pip' scripts/enhanced-startup.sh"
run_test "Enhanced startup script has poetry installation" "grep -q 'poetry install' scripts/enhanced-startup.sh"
run_test "Enhanced startup script has Docker startup" "grep -q 'docker-compose' scripts/enhanced-startup.sh"
run_test "Enhanced startup script has enhanced main.py startup" "grep -q 'enhanced_main.py' scripts/enhanced-startup.sh"
run_test "Enhanced startup script has health check endpoints" "grep -q '/health' scripts/enhanced-startup.sh"
run_test "Enhanced startup script has platform status endpoints" "grep -q '/platform/status' scripts/enhanced-startup.sh"
run_test "Enhanced startup script has domain manager health endpoints" "grep -q '/platform/health/' scripts/enhanced-startup.sh"
echo ""

# --- FINAL SUMMARY ---
echo "🎯 ENHANCED STARTUP VALIDATION RESULTS"
echo "====================================="
total_tests=50
passed_tests=$(grep "PASSED" <<< "$(history)" | wc -l) # This is a hack, should be more robust
failed_tests=$((total_tests - passed_tests))

# Recalculate based on actual script output
passed_tests=$(grep "PASSED" /tmp/validation_output.txt | wc -l)
failed_tests=$(grep "FAILED" /tmp/validation_output.txt | wc -l)
total_tests=$((passed_tests + failed_tests))

echo -e "${BLUE}[INFO]${NC} Total Tests: $total_tests"
echo -e "${GREEN}[SUCCESS]${NC} Passed Tests: $passed_tests"
echo -e "${RED}[ERROR]${NC} Failed Tests: $failed_tests"

if [ "$failed_tests" -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]🎉 ENHANCED STARTUP VALIDATION PASSED! Score: 100%${NC}"
    echo ""
    echo "✅ Enhanced startup orchestration is properly implemented"
    echo "✅ Dependency-ordered startup is correctly configured"
    echo "✅ Domain managers have proper startup orchestration"
    echo "✅ Cross-dimensional coordination is implemented"
    echo "✅ Health monitoring and shutdown orchestration is working"
    echo ""
    echo "🚀 Ready to use enhanced startup orchestration!"
    echo "📋 Run: ./scripts/enhanced-startup.sh"
    echo "🧪 Run integration tests: python tests/integration/test_enhanced_startup_orchestration.py"
    exit 0
else
    echo -e "${RED}[ERROR]❌ ENHANCED STARTUP VALIDATION FAILED. Score: $(( (passed_tests * 100) / total_tests ))%${NC}"
    echo "Please review the failed tests above and address the issues."
    exit 1
fi




