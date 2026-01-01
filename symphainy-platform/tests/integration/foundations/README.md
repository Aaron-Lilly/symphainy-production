# Foundation Integration Tests

Comprehensive integration tests for all foundations with real infrastructure and utility compliance verification.

## Overview

These tests verify that:
1. **All foundations work together** with real infrastructure
2. **Utility compliance** - Services properly use error handling, telemetry, security, and multi-tenancy
3. **Zero-trust security** works in real scenarios
4. **Multi-tenant isolation** is enforced correctly
5. **Observability** through telemetry and health metrics

## Test Categories

### 1. Utility Compliance Tests (`test_utility_compliance_integration.py`)

Tests that verify all foundations properly leverage platform utilities:

- **Error Handling**: Services use `handle_error_with_audit()` and return proper `error_code`
- **Telemetry**: Services log operations with `log_operation_with_telemetry()` and record health metrics
- **Security**: Zero-trust security validation works with real user contexts
- **Multi-Tenancy**: Tenant validation and isolation work correctly
- **Health Metrics**: Success and failure metrics are recorded

**Test Classes**:
- `TestErrorHandlingCompliance` - Error handling utility compliance
- `TestTelemetryCompliance` - Telemetry utility compliance
- `TestSecurityCompliance` - Security (zero-trust) compliance
- `TestMultiTenantCompliance` - Multi-tenant compliance
- `TestHealthMetricsCompliance` - Health metrics compliance
- `TestComprehensiveUtilityCompliance` - All utilities working together

### 2. Foundation Integration Tests (`test_foundation_integration.py`)

Tests that verify foundations work together:

- **Initialization**: All foundations initialize together
- **Cross-Foundation Operations**: Operations that span multiple foundations
- **Utility Compliance in Integration**: Utilities work correctly in integration scenarios

**Test Classes**:
- `TestFoundationInitialization` - Foundation initialization
- `TestCrossFoundationOperations` - Cross-foundation operations
- `TestUtilityComplianceInIntegration` - Utility compliance in integration

## Prerequisites

1. **Docker and Docker Compose** installed and running
2. **Infrastructure services** available (Redis, ArangoDB, Meilisearch, Consul)

## Running Tests

### Quick Start

**Option 1: Use Helper Script (Recommended)**
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
./tests/integration/foundations/run_integration_tests.sh
```

**Option 2: Manual Steps**

1. **Start Infrastructure**:
   ```bash
   cd /home/founders/demoversion/symphainy_source/symphainy-platform
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```

2. **Wait for Services to be Healthy**:
   ```bash
   docker ps --filter "name=symphainy-"
   ```

3. **Run Tests**:
   ```bash
   python3 -m pytest tests/integration/foundations/ -v --tb=short
   ```

### Test Selection

**Run All Foundation Integration Tests**:
```bash
python3 -m pytest tests/integration/foundations/ -v
```

**Run Only Utility Compliance Tests**:
```bash
python3 -m pytest tests/integration/foundations/ -v -m "utility_compliance"
```

**Run Only Foundation Integration Tests**:
```bash
python3 -m pytest tests/integration/foundations/ -v -m "foundation_integration"
```

**Run Specific Test File**:
```bash
python3 -m pytest tests/integration/foundations/test_utility_compliance_integration.py -v
```

**Run Specific Test Class**:
```bash
python3 -m pytest tests/integration/foundations/test_utility_compliance_integration.py::TestSecurityCompliance -v
```

### Helper Script Options

```bash
./tests/integration/foundations/run_integration_tests.sh [OPTIONS]

Options:
  --keep-running         Keep infrastructure running after tests
  --skip-tests          Only start infrastructure, don't run tests
  --marker MARKER       Run only tests with specific marker
  --file FILE           Run specific test file
  --utility-compliance  Run only utility compliance tests
  --foundation-integration  Run only foundation integration tests
  --help                Show help message
```

**Examples**:
```bash
# Start infrastructure and run all tests
./tests/integration/foundations/run_integration_tests.sh

# Run only utility compliance tests
./tests/integration/foundations/run_integration_tests.sh --utility-compliance

# Run only foundation integration tests
./tests/integration/foundations/run_integration_tests.sh --foundation-integration

# Start infrastructure, run tests, keep infrastructure running
./tests/integration/foundations/run_integration_tests.sh --keep-running

# Only start infrastructure (don't run tests)
./tests/integration/foundations/run_integration_tests.sh --skip-tests
```

## Test Structure

### Fixtures

- `di_container` - DI Container with Public Works Foundation initialized
- `curator_foundation` - Curator Foundation initialized
- `communication_foundation` - Communication Foundation initialized
- `agentic_foundation` - Agentic Foundation initialized
- `experience_foundation` - Experience Foundation initialized
- `full_foundation_stack` - All foundations initialized together
- `valid_user_context` - Valid user context for testing
- `invalid_user_context` - Invalid user context (no permissions)
- `invalid_tenant_context` - Invalid tenant context

### Helper Functions

- `verify_error_handling()` - Verify error handling compliance
- `verify_telemetry_recorded()` - Verify telemetry was recorded
- `verify_health_metric_recorded()` - Verify health metric was recorded

## Success Criteria

### ✅ Tests Pass When:

1. **All Foundations Initialize**:
   - Public Works Foundation initializes with real infrastructure
   - Curator Foundation initializes
   - Communication Foundation initializes
   - Agentic Foundation initializes
   - Experience Foundation initializes

2. **Utility Compliance**:
   - Error handling: Services use `handle_error_with_audit()` and return `error_code`
   - Telemetry: Services log operations with `log_operation_with_telemetry()`
   - Health metrics: Services record success/failure metrics
   - Security: Services validate permissions with `check_permissions()`
   - Multi-tenancy: Services validate tenant access with `validate_tenant_access()`

3. **Zero-Trust Security**:
   - Security validation works with real user contexts
   - Access denied returns proper error response with `error_code: "ACCESS_DENIED"`
   - Services work without user_context (optional parameter)

4. **Multi-Tenant Isolation**:
   - Tenant validation works with real tenant contexts
   - Tenant denied returns proper error response with `error_code: "TENANT_ACCESS_DENIED"`
   - Tenants cannot access other tenants' data

5. **Cross-Foundation Operations**:
   - Services can register with Curator Foundation
   - Communication Foundation can register SOA APIs
   - Foundations share infrastructure through Public Works Foundation

## Troubleshooting

### Infrastructure Not Available

**Error**: `pytest.skip("Infrastructure not available")`

**Solution**:
1. Check if Docker is running: `docker ps`
2. Start infrastructure: `docker-compose -f docker-compose.infrastructure.yml up -d`
3. Wait for services to be healthy: `docker ps --filter "name=symphainy-"`

### Connection Timeouts

**Error**: Connection refused or timeout errors

**Solution**:
1. Check service health: `docker-compose -f docker-compose.infrastructure.yml ps`
2. Check service logs: `docker-compose -f docker-compose.infrastructure.yml logs [service-name]`
3. Verify ports are not in use: `netstat -tuln | grep [port]`
4. Wait longer for services to start (some services take 30-60 seconds)

### Initialization Failures

**Error**: Service failed to initialize

**Solution**:
1. Check infrastructure logs: `docker-compose -f docker-compose.infrastructure.yml logs`
2. Verify environment variables are set correctly
3. Check service dependencies (e.g., ArangoDB must be ready before services that use it)
4. Verify configuration files exist and are valid

### Async Fixture Errors

**Error**: `'async_generator' object has no attribute '...'`

**Solution**:
- Ensure `asyncio_mode = "auto"` is set in `pyproject.toml`
- Use `@pytest.mark.asyncio` decorator on async test functions
- Ensure pytest-asyncio is installed: `pip install pytest-asyncio`

## Related Documents

- [Integration Test Strategy](../../../docs/11-12/INTEGRATION_TEST_STRATEGY.md) - Comprehensive testing strategy
- [Foundation Utility Compliance Approach](../../../docs/11-12/FOUNDATION_UTILITY_COMPLIANCE_APPROACH.md) - Standard patterns for utility usage
- [Curator Foundation Lessons Learned](../../../docs/11-12/CURATOR_LESSONS_LEARNED.md) - Patterns and best practices


