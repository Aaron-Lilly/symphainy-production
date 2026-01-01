# Integration Test Strategy

**Date**: December 20, 2024 (Updated)  
**Purpose**: Comprehensive integration testing strategy for Smart City services with real infrastructure and utility compliance verification

---

## Executive Summary

Integration tests verify that Smart City services **actually work** with real infrastructure capabilities AND properly leverage platform utilities (error handling, telemetry, security, multi-tenancy) before moving to Business Enablement realm testing. This ensures the platform foundation is solid, services can perform real operations, and the platform's true potential is enabled through proper utility usage.

---

## Testing Philosophy

### Why Integration Tests?

1. **Unit tests verify structure** - They check that code follows patterns and has correct methods
2. **Integration tests verify functionality** - They check that services actually work with real infrastructure
3. **Fail fast** - Catch infrastructure issues early, before building on top

### Testing Approach

- **Real Infrastructure**: Use Docker Compose to run actual Redis, ArangoDB, Meilisearch, etc.
- **Actual Operations**: Test real store, retrieve, search operations
- **Foundation Stack**: Test with full foundation stack (Public Works, Curator, Communication)
- **Error Handling**: Verify graceful error handling with real infrastructure
- **Utility Compliance**: Verify services properly use error handling, telemetry, security, and multi-tenancy utilities
- **Zero-Trust Security**: Verify security validation works in real scenarios
- **Multi-Tenant Isolation**: Verify tenant validation and filtering work correctly
- **Observability**: Verify telemetry and health metrics are being recorded

---

## Test Categories

### 1. Real Infrastructure Tests

**Purpose**: Verify Smart City services work with real infrastructure

**What We Test**:
- ✅ Services connect to real Redis, ArangoDB, Meilisearch
- ✅ Services can perform actual operations (store, retrieve, search)
- ✅ Infrastructure abstractions are properly connected
- ✅ SOA APIs work with real infrastructure
- ✅ Services handle errors gracefully
- ✅ Services register with Curator Foundation

**Test File**: `tests/integration/smart_city/test_smart_city_real_infrastructure.py`

**Key Tests**:
- `test_librarian_stores_knowledge_with_real_infrastructure` - Store knowledge using real Meilisearch/ArangoDB
- `test_librarian_retrieves_knowledge_with_real_infrastructure` - Retrieve knowledge from real infrastructure
- `test_librarian_searches_knowledge_with_real_infrastructure` - Search knowledge using real Meilisearch
- `test_librarian_infrastructure_abstractions_work` - Verify abstractions are connected
- `test_librarian_soa_apis_work_with_real_infrastructure` - Test SOA APIs with real infrastructure
- `test_services_register_with_curator` - Verify service registration

**Infrastructure Required**:
- Redis (port 6379)
- ArangoDB (port 8529)
- Meilisearch (port 7700)
- Consul (port 8500)

### 2. Foundation Integration Tests

**Purpose**: Verify Smart City services work with full foundation stack

**What We Test**:
- ✅ All foundations initialize together (Public Works, Curator, Communication)
- ✅ Smart City services use Public Works Foundation correctly
- ✅ Services register with Curator Foundation
- ✅ Services can use Communication Foundation
- ✅ City Manager orchestrates all foundations
- ✅ Shared infrastructure access works

**Test File**: `tests/integration/smart_city/test_smart_city_foundation_integration.py`

**Key Tests**:
- `test_foundations_initialize_together` - All foundations initialize correctly
- `test_smart_city_service_uses_public_works` - Services use Public Works Foundation
- `test_smart_city_service_registers_with_curator` - Services register with Curator
- `test_smart_city_service_can_use_communication` - Services can use Communication Foundation
- `test_city_manager_orchestrates_foundations` - City Manager orchestrates all foundations
- `test_foundations_provide_shared_infrastructure` - Shared infrastructure access

### 3. Utility Compliance Tests (NEW - Post-Refactoring)

**Purpose**: Verify services properly leverage platform utilities in real scenarios

**What We Test**:
- ✅ **Error Handling**: Services use `handle_error_with_audit()` for structured error handling
- ✅ **Telemetry**: Services record operations with `log_operation_with_telemetry()` and `record_health_metric()`
- ✅ **Security**: Zero-trust security validation works with real user contexts
- ✅ **Multi-Tenancy**: Tenant validation and filtering work correctly
- ✅ **Health Metrics**: Success and failure metrics are recorded
- ✅ **Error Codes**: Error responses include proper `error_code` fields
- ✅ **Audit Trail**: Errors are properly audited for compliance

**Test File**: `tests/integration/foundations/test_utility_compliance_integration.py`

**Key Tests**:

#### **Error Handling Tests**:
- `test_services_handle_errors_with_audit` - Verify `handle_error_with_audit()` is called on exceptions
- `test_error_responses_include_error_code` - Verify error responses include `error_code` field
- `test_errors_are_audited` - Verify errors are properly audited
- `test_graceful_error_handling` - Verify services handle errors gracefully without crashing

#### **Telemetry Tests**:
- `test_operations_log_telemetry` - Verify `log_operation_with_telemetry()` is called at method start/end
- `test_health_metrics_recorded` - Verify `record_health_metric()` is called on success paths
- `test_telemetry_includes_context` - Verify telemetry includes proper context metadata
- `test_failure_metrics_recorded` - Verify failure metrics are recorded (access denied, tenant denied, etc.)

#### **Security Tests (Zero-Trust)**:
- `test_security_validation_works` - Verify `check_permissions()` is called with user_context
- `test_access_denied_returns_properly` - Verify access denied returns proper error response
- `test_security_validation_without_user_context` - Verify methods work without user_context (optional)
- `test_security_metrics_recorded` - Verify access denied attempts are recorded in metrics
- `test_security_validation_real_scenarios` - Test security validation with real user contexts and permissions

#### **Multi-Tenant Tests**:
- `test_tenant_validation_works` - Verify `validate_tenant_access()` is called with tenant_id
- `test_tenant_denied_returns_properly` - Verify tenant denied returns proper error response
- `test_tenant_filtering_works` - Verify list methods filter by tenant correctly
- `test_tenant_isolation_enforced` - Verify tenants cannot access other tenants' data
- `test_tenant_metrics_recorded` - Verify tenant denied attempts are recorded in metrics
- `test_multi_tenant_real_scenarios` - Test tenant validation with real tenant contexts

#### **Health Metrics Tests**:
- `test_success_metrics_recorded` - Verify success metrics are recorded for all operations
- `test_failure_metrics_recorded` - Verify failure metrics are recorded (access denied, errors, etc.)
- `test_metrics_include_metadata` - Verify metrics include proper metadata (resource_id, tenant_id, etc.)
- `test_health_metrics_accessible` - Verify health metrics can be queried from health service

**Test Pattern Example**:
```python
async def test_service_security_validation_works(service, user_context):
    """Test that service validates security with real user context."""
    # Test with valid user context
    result = await service.method_name(resource_id="test", user_context=user_context)
    assert result["success"] == True
    
    # Test with invalid permissions
    invalid_user = {**user_context, "permissions": []}
    result = await service.method_name(resource_id="test", user_context=invalid_user)
    assert result["success"] == False
    assert result["error_code"] == "ACCESS_DENIED"
    
    # Verify metric was recorded
    metrics = await service.get_health_metrics()
    assert "method_name_access_denied" in metrics
```

**Infrastructure Required**:
- All foundation services initialized
- Security service (from Public Works Foundation)
- Tenant service (from Public Works Foundation)
- Telemetry service (from Public Works Foundation)
- Health service (from Public Works Foundation)

---

## Running Integration Tests

### Prerequisites

1. **Docker and Docker Compose** installed and running
2. **Infrastructure services** available (Redis, ArangoDB, Meilisearch, Consul)

### Quick Start

**Option 1: Use Helper Script (Recommended)**
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
./tests/integration/smart_city/run_integration_tests.sh
```

**Option 2: Manual Steps**

1. **Start Infrastructure**:
   ```bash
   cd /home/founders/demoversion/symphainy_source/symphainy-platform
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```

2. **Wait for Services to be Healthy**:
   ```bash
   # Check service health
   docker ps --filter "name=symphainy-"
   ```

3. **Run Tests**:
   ```bash
   python3 -m pytest tests/integration/smart_city/ -v --tb=short
   ```

### Test Selection

**Run All Integration Tests**:
```bash
python3 -m pytest tests/integration/smart_city/ -v
```

**Run Only Real Infrastructure Tests**:
```bash
python3 -m pytest tests/integration/smart_city/ -v -m "real_infrastructure"
```

**Skip Real Infrastructure Tests**:
```bash
python3 -m pytest tests/integration/smart_city/ -v -m "not real_infrastructure"
```

**Run Specific Test File**:
```bash
python3 -m pytest tests/integration/smart_city/test_smart_city_real_infrastructure.py -v
```

### Helper Script Options

```bash
./tests/integration/smart_city/run_integration_tests.sh [OPTIONS]

Options:
  --keep-running    Keep infrastructure running after tests
  --skip-tests      Only start infrastructure, don't run tests
  --marker MARKER   Run only tests with specific marker
  --help            Show help message
```

**Examples**:
```bash
# Start infrastructure and run all tests
./tests/integration/smart_city/run_integration_tests.sh

# Start infrastructure, run tests, keep infrastructure running
./tests/integration/smart_city/run_integration_tests.sh --keep-running

# Only start infrastructure (don't run tests)
./tests/integration/smart_city/run_integration_tests.sh --skip-tests

# Run only real infrastructure tests
./tests/integration/smart_city/run_integration_tests.sh --marker real_infrastructure
```

---

## Test Infrastructure

### Docker Compose Services

The `docker-compose.infrastructure.yml` file defines the following services:

- **Redis** (port 6379) - Cache and message broker
- **ArangoDB** (port 8529) - Graph database for metadata
- **Meilisearch** (port 7700) - Search engine
- **Consul** (port 8500) - Service discovery
- **Tempo** (port 3200) - Distributed tracing
- **OpenTelemetry Collector** (ports 4317, 4318) - Telemetry collection
- **Grafana** (port 3000) - Visualization
- **OPA** (port 8181) - Policy engine

### Service Health Checks

All services have health checks configured. The helper script waits for services to be healthy before running tests.

### Port Conflicts

If ports are already in use, you can:
1. Stop conflicting services
2. Modify port mappings in `docker-compose.infrastructure.yml`
3. Use different ports via environment variables

---

## Success Criteria

### ✅ Integration Tests Pass When:

1. **Infrastructure Connectivity**:
   - All services connect to infrastructure successfully
   - Infrastructure abstractions are properly initialized
   - No connection errors or timeouts

2. **Actual Operations Work**:
   - Services can store data (Librarian stores knowledge)
   - Services can retrieve data (Librarian retrieves knowledge)
   - Services can search data (Librarian searches knowledge)
   - Operations return expected results

3. **Foundation Integration**:
   - All foundations initialize together
   - Services register with Curator
   - Services can use Communication Foundation
   - City Manager orchestrates correctly

4. **Error Handling**:
   - Services handle missing data gracefully
   - Services handle connection errors gracefully
   - No unhandled exceptions
   - **NEW**: Services use `handle_error_with_audit()` for structured error handling
   - **NEW**: Error responses include `error_code` field
   - **NEW**: Errors are properly audited

5. **Service Registration**:
   - Services register with Curator Foundation
   - SOA APIs are discoverable
   - MCP Tools are registered

6. **Utility Compliance** (NEW):
   - **Telemetry**: Services record operations with `log_operation_with_telemetry()` at start and end
   - **Health Metrics**: Services record success/failure metrics with `record_health_metric()`
   - **Security**: Services validate permissions with `check_permissions()` when user_context provided
   - **Multi-Tenancy**: Services validate tenant access with `validate_tenant_access()` when tenant_id provided
   - **Tenant Filtering**: List methods filter results by tenant_id when user_context provided
   - **Error Codes**: All error responses include proper `error_code` field
   - **Audit Trail**: All errors are properly audited via `handle_error_with_audit()`

7. **Zero-Trust Security** (NEW):
   - Security validation works with real user contexts
   - Access denied returns proper error response with `error_code: "ACCESS_DENIED"`
   - Access denied attempts are recorded in health metrics
   - Services work without user_context (optional parameter)

8. **Multi-Tenant Isolation** (NEW):
   - Tenant validation works with real tenant contexts
   - Tenant denied returns proper error response with `error_code: "TENANT_ACCESS_DENIED"`
   - Tenant filtering works in list methods
   - Tenants cannot access other tenants' data
   - Tenant denied attempts are recorded in health metrics

---

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

---

## Test Execution Flow

1. **Setup Phase**:
   - Check if infrastructure is available
   - Start infrastructure if needed
   - Wait for services to be healthy

2. **Test Execution**:
   - Initialize DI Container
   - Initialize Public Works Foundation (connects to real infrastructure)
   - Initialize Curator Foundation (with utility compliance)
   - Initialize Communication Foundation (with utility compliance)
   - Initialize Smart City services
   - Run integration tests
   - Verify actual operations work
   - **NEW**: Verify utility compliance (error handling, telemetry, security, tenant)
   - **NEW**: Verify zero-trust security works in real scenarios
   - **NEW**: Verify multi-tenant isolation works correctly

3. **Cleanup Phase**:
   - Shutdown services
   - Stop infrastructure (if not keeping it running)
   - Report results

---

## Integration with CI/CD

### Continuous Integration

Integration tests should run in CI/CD pipeline:
1. Start infrastructure services in CI environment
2. Run integration tests
3. Report results
4. Cleanup infrastructure

### Local Development

Developers can run integration tests locally:
1. Use helper script for easy execution
2. Keep infrastructure running for faster iteration
3. Run specific test categories as needed

---

## Next Steps

After integration tests pass:
1. ✅ Smart City services work with real infrastructure
2. ✅ Foundation stack works together
3. ✅ Services can perform actual operations
4. ✅ **Services properly leverage platform utilities** (error handling, telemetry, security, multi-tenancy)
5. ✅ **Zero-trust security model is enforced** in real scenarios
6. ✅ **Multi-tenant isolation is enforced** in real scenarios
7. ✅ **Observability is enabled** through proper telemetry and health metrics
8. ✅ Ready to test Business Enablement realm

## Utility Compliance Verification

### Why Utility Compliance Matters

The platform's utilities (error handling, telemetry, security, multi-tenancy) are **foundational capabilities** that enable:
- **Observability**: Understanding what's happening in production
- **Security**: Zero-trust security model enforcement
- **Compliance**: Audit trails and error tracking
- **Multi-Tenancy**: Proper tenant isolation and data protection
- **Reliability**: Structured error handling and recovery

### Integration Test Verification

Integration tests should verify that utilities work **in real scenarios**, not just that they're present in code:

1. **Error Handling**: Verify errors are caught, audited, and returned with proper error codes
2. **Telemetry**: Verify operations are tracked and metrics are recorded
3. **Security**: Verify access control works with real user contexts and permissions
4. **Multi-Tenancy**: Verify tenant isolation works with real tenant data

### Test Coverage

- ✅ **All user-facing methods** should be tested for utility compliance
- ✅ **Real user contexts** should be used to test security validation
- ✅ **Real tenant contexts** should be used to test tenant validation
- ✅ **Real error scenarios** should be tested to verify error handling
- ✅ **Real operations** should be tested to verify telemetry recording

---

## Related Documents

- [Strategic Testing Roadmap](./STRATEGIC_TESTING_ROADMAP.md)
- [Smart City Realm Tests](../symphainy-platform/tests/layer_4_realms/smart_city/README.md)
- [Foundation Test Plans](./PUBLIC_WORKS_FOUNDATION_TEST_PLAN.md)
- [Curator Foundation Lessons Learned](./CURATOR_LESSONS_LEARNED.md) - Patterns and best practices from utility compliance work
- [Foundation Utility Compliance Approach](./FOUNDATION_UTILITY_COMPLIANCE_APPROACH.md) - Standard patterns for utility usage
- [Curator Foundation Completion Report](./CURATOR_FOUNDATION_COMPLETION_REPORT.md) - Reference implementation status

## Utility Compliance Reference

### Standard Pattern for Integration Tests

When testing services, verify they follow the standard utility pattern:

```python
async def test_service_method_utility_compliance(service, user_context):
    """Test that service method properly uses utilities."""
    # 1. Verify telemetry is recorded
    initial_metrics = await service.get_health_metrics()
    
    # 2. Call method with user_context
    result = await service.method_name(resource_id="test", user_context=user_context)
    
    # 3. Verify telemetry was recorded
    final_metrics = await service.get_health_metrics()
    assert "method_name_start" in final_metrics
    assert "method_name_complete" in final_metrics
    assert "method_name_success" in final_metrics
    
    # 4. Verify security validation (if user_context provided)
    if user_context:
        # Test with invalid permissions
        invalid_user = {**user_context, "permissions": []}
        result = await service.method_name(resource_id="test", user_context=invalid_user)
        assert result["success"] == False
        assert result["error_code"] == "ACCESS_DENIED"
        assert "method_name_access_denied" in final_metrics
    
    # 5. Verify tenant validation (if tenant_id provided)
    if user_context and user_context.get("tenant_id"):
        # Test with invalid tenant
        invalid_tenant = {**user_context, "tenant_id": "invalid_tenant"}
        result = await service.method_name(resource_id="test", user_context=invalid_tenant)
        assert result["success"] == False
        assert result["error_code"] == "TENANT_ACCESS_DENIED"
        assert "method_name_tenant_denied" in final_metrics
    
    # 6. Verify error handling
    try:
        await service.method_name(resource_id="invalid", user_context=user_context)
    except Exception as e:
        # Verify error was handled with audit
        assert "method_name" in service.get_error_audit_log()
```

### Utility Compliance Checklist

For each service method tested:
- [ ] Telemetry is recorded at method start (`log_operation_with_telemetry("method_name_start")`)
- [ ] Telemetry is recorded at method end (`log_operation_with_telemetry("method_name_complete")`)
- [ ] Health metric is recorded on success (`record_health_metric("method_name_success")`)
- [ ] Security validation is performed (if user_context provided)
- [ ] Tenant validation is performed (if tenant_id provided)
- [ ] Errors are handled with audit (`handle_error_with_audit()`)
- [ ] Error responses include `error_code` field
- [ ] Access denied returns `error_code: "ACCESS_DENIED"`
- [ ] Tenant denied returns `error_code: "TENANT_ACCESS_DENIED"`
- [ ] Failure metrics are recorded (access denied, tenant denied, errors)

