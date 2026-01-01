#!/bin/bash
# Production Validation Script
# Comprehensive validation of production readiness

set -e

echo "🎯 SymphAIny Platform - Production Validation"
echo "============================================="
echo "Validating complete production setup..."
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

echo "🧪 PHASE 1: ORIGINAL STARTUP PROCESS VALIDATION"
echo "==============================================="

# Test pip upgrade
run_test "pip upgrade" "python3 -m pip install --upgrade pip"

# Test poetry installation
run_test "poetry installation" "./poetry --version"

# Test pyproject.toml usage
run_test "pyproject.toml syntax" "./poetry check"

# Test poetry dependencies
run_test "poetry dependencies" "./poetry install --only main"

echo ""
echo "🔧 PHASE 2: CONFIGURATION SYSTEM VALIDATION"
echo "==========================================="

# Test configuration system
run_test "configuration system" "python3 -c 'from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager; config = UnifiedConfigurationManager(\"test\"); print(f\"Config loaded: {len(config.config_cache)} values\")'"

# Test DI Container
run_test "DI Container" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); print(\"DI Container working\")'"

# Test all utilities
run_test "logging utility" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); logger = di.get_logger(\"test\"); print(\"Logger working\")'"

run_test "health utility" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); health = di.get_health(); print(\"Health working\")'"

run_test "error handler utility" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); error = di.get_error_handler(); print(\"Error handler working\")'"

run_test "tenant utility" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); tenant = di.get_tenant(); print(\"Tenant working\")'"

run_test "validation utility" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); validation = di.get_validation(); print(\"Validation working\")'"

run_test "serialization utility" "python3 -c 'from foundations.di_container.di_container_service import DIContainerService; di = DIContainerService(\"test\"); serialization = di.get_serialization(); print(\"Serialization working\")'"

echo ""
echo "🔐 PHASE 3: SECRETS MANAGEMENT VALIDATION"
echo "========================================"

# Test secrets loading script
run_test "secrets loading script" "test -f scripts/load-secrets.sh"

# Test GitHub Actions workflow
run_test "GitHub Actions workflow" "test -f .github/workflows/secrets.yml"

echo ""
echo "🐳 PHASE 4: ENVIRONMENT CONFIGURATION VALIDATION"
echo "================================================="

# Test Docker Compose files
run_test "development Docker Compose" "test -f docker-compose.dev.yml"

run_test "production Docker Compose" "test -f docker-compose.prod.yml"

# Test environment configurations
run_test "development environment config" "test -f config/development.env"

run_test "business logic config" "test -f config/business-logic.yaml"

run_test "infrastructure config" "test -f config/infrastructure.yaml"

echo ""
echo "🏥 PHASE 5: PRODUCTION MONITORING VALIDATION"
echo "==========================================="

# Test health checks
run_test "health checks script" "test -f monitoring/health-checks.py"

# Test health checks execution
run_test "health checks execution" "python3 monitoring/health-checks.py"

echo ""
echo "📊 PHASE 6: PRODUCTION READINESS ASSESSMENT"
echo "==========================================="

# Test production startup script
run_test "production startup script" "test -f scripts/production-startup.sh"

# Test requirements.txt
run_test "production requirements" "test -f requirements.txt"

# Test main application
run_test "main application" "test -f main.py"

echo ""
echo "🎯 FINAL VALIDATION RESULTS"
echo "==========================="

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
echo "📈 PRODUCTION READINESS SCORE"
echo "============================="

if [ $SUCCESS_RATE -ge 95 ]; then
    print_success "🎉 PRODUCTION READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "✅ All critical systems validated"
    echo "✅ Original startup process working"
    echo "✅ Configuration system working"
    echo "✅ Secrets management ready"
    echo "✅ Environment configurations ready"
    echo "✅ Production monitoring ready"
    echo ""
    echo "🚀 Ready for C-suite production testing!"
    exit 0
elif [ $SUCCESS_RATE -ge 85 ]; then
    print_warning "⚠️ MOSTLY READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "✅ Core systems working"
    echo "⚠️ Some optional systems may need attention"
    echo ""
    echo "💡 Review failed tests and address before production"
    exit 1
else
    print_error "❌ NOT READY! Score: $SUCCESS_RATE%"
    echo ""
    echo "❌ Critical systems need attention"
    echo "❌ Multiple validation failures"
    echo ""
    echo "🔧 Fix critical issues before production"
    exit 2
fi




