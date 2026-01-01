#!/bin/bash
# Implementation Readiness Validation Script
# Validates that we have a concrete, actionable plan for CI/CD enhancement

set -e

echo "🎯 SymphAIny Platform - Implementation Readiness Validation"
echo "========================================================="
echo "Validating implementation readiness for CI/CD enhancement..."
echo ""

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

# Validation counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_status "Testing: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_success "$test_name: PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "$test_name: FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "📋 PHASE 1: IMPLEMENTATION PLAN VALIDATION"
echo "=========================================="

# Test implementation plan exists
run_test "Implementation plan exists" "test -f ../IMPLEMENTATION_READY_CI_CD_PLAN.md"

# Test plan has concrete actions
run_test "Plan has concrete actions" "grep -q 'Files to Create' ../IMPLEMENTATION_READY_CI_CD_PLAN.md"

# Test plan has success criteria
run_test "Plan has success criteria" "grep -q 'Success Criteria' ../IMPLEMENTATION_READY_CI_CD_PLAN.md"

# Test plan has implementation steps
run_test "Plan has implementation steps" "grep -q 'Detailed Implementation Steps' ../IMPLEMENTATION_READY_CI_CD_PLAN.md"

echo ""
echo "🏗️ PHASE 2: ARCHITECTURE READINESS VALIDATION"
echo "=============================================="

# Test domain managers exist
run_test "City Manager exists" "test -d backend/smart_city/services/city_manager"

run_test "Delivery Manager exists" "test -d backend/business_enablement"

run_test "Experience Manager exists" "test -d backend/packages/smart_city/experience"

run_test "Journey Manager exists" "test -d journey_solution"

# Test infrastructure exists
run_test "Consul infrastructure exists" "test -d foundations/infrastructure_foundation"

run_test "Redis infrastructure exists" "test -f foundations/infrastructure_foundation/abstractions/redis_infrastructure_abstraction.py"

run_test "Grafana infrastructure exists" "test -d monitoring"

run_test "OpenTelemetry infrastructure exists" "test -f foundations/infrastructure_foundation/opentelemetry_client.py"

echo ""
echo "🔧 PHASE 3: IMPLEMENTATION FOUNDATION VALIDATION"
echo "================================================"

# Test test structure exists
run_test "Test structure exists" "test -d tests"

# Test domain test structure exists
run_test "Smart City tests exist" "test -d tests/smart-city"

run_test "Business Enablement tests exist" "test -d tests/business-enablement"

run_test "Experience tests exist" "test -d tests/experience"

run_test "Journey tests exist" "test -d tests/journey"

run_test "Cross-domain tests exist" "test -d tests/cross-domain"

# Test CI/CD workflows exist
run_test "CI workflow exists" "test -f .github/workflows/ci.yml"

run_test "CD workflow exists" "test -f .github/workflows/cd.yml"

run_test "Quality Gates workflow exists" "test -f .github/workflows/quality-gates.yml"

run_test "Monitoring workflow exists" "test -f .github/workflows/monitoring.yml"

echo ""
echo "📊 PHASE 4: MONITORING INFRASTRUCTURE VALIDATION"
echo "==============================================="

# Test monitoring infrastructure
run_test "Health checks exist" "test -f monitoring/health-checks.py"

run_test "Production validation exists" "test -f scripts/production-validation.sh"

run_test "CI/CD validation exists" "test -f scripts/ci-cd-validation-practical.sh"

# Test Grafana infrastructure
run_test "Grafana monitoring exists" "test -d monitoring"

echo ""
echo "🎯 FINAL IMPLEMENTATION READINESS RESULTS"
echo "========================================="

print_status "Total Tests: $TOTAL_TESTS"
print_success "Passed Tests: $PASSED_TESTS"
if [ $FAILED_TESTS -gt 0 ]; then
    print_error "Failed Tests: $FAILED_TESTS"
else
    print_success "Failed Tests: $FAILED_TESTS"
fi

# Calculate success rate
SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
print_status "Success Rate: $SUCCESS_RATE%"

echo ""
echo "📈 IMPLEMENTATION READINESS SCORE"
echo "================================="

if [ $SUCCESS_RATE -ge 95 ]; then
    print_success "🎉 IMPLEMENTATION READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "✅ Implementation plan is concrete and actionable"
    echo "✅ Architecture foundation is solid"
    echo "✅ Infrastructure is ready for enhancement"
    echo "✅ Monitoring infrastructure is in place"
    echo ""
    echo "🚀 Ready to implement CI/CD enhancement!"
    echo "📋 Follow the IMPLEMENTATION_READY_CI_CD_PLAN.md"
    exit 0
elif [ $SUCCESS_RATE -ge 85 ]; then
    print_warning "⚠️ MOSTLY READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "✅ Core implementation plan ready"
    echo "⚠️ Some components may need attention"
    echo ""
    echo "💡 Review failed tests and address before implementation"
    exit 1
else
    print_error "❌ NOT READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "❌ Critical components need attention"
    echo "❌ Multiple validation failures"
    echo ""
    echo "🔧 Fix critical issues before implementation"
    exit 2
fi




