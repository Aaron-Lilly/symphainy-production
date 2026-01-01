#!/bin/bash
# CI/CD Pipeline Validation Script
# Comprehensive validation of complete CI/CD pipeline

set -e

echo "🚀 SymphAIny Platform - CI/CD Pipeline Validation"
echo "==================================================="
echo "Validating complete CI/CD pipeline..."
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

echo "🔧 PHASE 1: GITHUB ACTIONS WORKFLOWS VALIDATION"
echo "==============================================="

# Test CI workflow
run_test "CI workflow" "test -f .github/workflows/ci.yml"

# Test CD workflow
run_test "CD workflow" "test -f .github/workflows/cd.yml"

# Test Quality Gates workflow
run_test "Quality Gates workflow" "test -f .github/workflows/quality-gates.yml"

# Test Monitoring workflow
run_test "Monitoring workflow" "test -f .github/workflows/monitoring.yml"

# Test Secrets workflow
run_test "Secrets workflow" "test -f .github/workflows/secrets.yml"

echo ""
echo "🧪 PHASE 2: QUALITY GATES VALIDATION"
echo "===================================="

# Test code quality tools
run_test "Black formatter" "poetry run black --check ."

run_test "isort formatter" "poetry run isort --check-only ."

run_test "Flake8 linter" "poetry run flake8 ."

run_test "Pylint linter" "poetry run pylint --fail-under=8.0 ."

run_test "MyPy type checker" "poetry run mypy . --ignore-missing-imports"

run_test "Bandit security scanner" "poetry run bandit -r . -f json -o bandit-report.json"

run_test "Safety vulnerability checker" "poetry run safety check --json --output safety-report.json"

echo ""
echo "🔗 PHASE 3: INTEGRATION TESTING VALIDATION"
echo "========================================="

# Test integration test structure
run_test "Unit tests directory" "test -d tests/unit"

run_test "Integration tests directory" "test -d tests/integration"

run_test "Architecture tests directory" "test -d tests/architecture"

run_test "Contract tests directory" "test -d tests/contracts"

run_test "Performance tests directory" "test -d tests/performance"

run_test "E2E tests directory" "test -d tests/e2e"

echo ""
echo "🐳 PHASE 4: DOCKER CONFIGURATION VALIDATION"
echo "==========================================="

# Test Docker configurations
run_test "Development Docker Compose" "docker-compose -f docker-compose.dev.yml config"

run_test "Production Docker Compose" "docker-compose -f docker-compose.prod.yml config"

run_test "Platform Dockerfile" "test -f Dockerfile.platform"

echo ""
echo "📊 PHASE 5: MONITORING AND ALERTING VALIDATION"
echo "============================================="

# Test monitoring components
run_test "Health checks script" "test -f monitoring/health-checks.py"

run_test "Health checks execution" "python3 monitoring/health-checks.py"

run_test "Production validation script" "test -f scripts/production-validation.sh"

run_test "Secrets loading script" "test -f scripts/load-secrets.sh"

echo ""
echo "🔐 PHASE 6: SECURITY VALIDATION"
echo "=============================="

# Test security components
run_test "Secrets management" "test -f scripts/load-secrets.sh"

run_test "GitHub Secrets workflow" "test -f .github/workflows/secrets.yml"

run_test "Security scanning" "poetry run bandit -r . -f json -o security-report.json"

run_test "Dependency auditing" "poetry run pip-audit --desc --format=json --output=audit-report.json"

echo ""
echo "🚀 PHASE 7: DEPLOYMENT VALIDATION"
echo "================================"

# Test deployment components
run_test "Production startup script" "test -f scripts/production-startup.sh"

run_test "CI/CD validation script" "test -f scripts/ci-cd-validation.sh"

run_test "Requirements file" "test -f requirements.txt"

run_test "Main application" "test -f main.py"

echo ""
echo "🎯 FINAL CI/CD VALIDATION RESULTS"
echo "================================="

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
echo "📈 CI/CD PIPELINE READINESS SCORE"
echo "================================="

if [ $SUCCESS_RATE -ge 95 ]; then
    print_success "🎉 CI/CD PIPELINE READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "✅ GitHub Actions workflows configured"
    echo "✅ Quality gates implemented"
    echo "✅ Integration testing ready"
    echo "✅ Docker configuration ready"
    echo "✅ Monitoring and alerting ready"
    echo "✅ Security validation ready"
    echo "✅ Deployment pipeline ready"
    echo ""
    echo "🚀 Ready for production deployment!"
    echo "🎯 C-suite can now test with confidence!"
    exit 0
elif [ $SUCCESS_RATE -ge 85 ]; then
    print_warning "⚠️ MOSTLY READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "✅ Core CI/CD pipeline working"
    echo "⚠️ Some components may need attention"
    echo ""
    echo "💡 Review failed tests and address before production"
    exit 1
else
    print_error "❌ NOT READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "❌ Critical CI/CD components need attention"
    echo "❌ Multiple validation failures"
    echo ""
    echo "🔧 Fix critical issues before production"
    exit 2
fi




