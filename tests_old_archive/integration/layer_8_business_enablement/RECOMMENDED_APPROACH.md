# Recommended Approach - Layer 3+ Testing

## Overview

Based on your feedback, here's the recommended approach:

1. **Only add `smart_city_infrastructure` fixture to Layer 3+ tests** (functionality tests)
2. **Keep Layer 2 tests using `test_infrastructure`** (initialization tests don't need Smart City services)
3. **Add service discovery verification tests** (verify services can discover Smart City services)
4. **Add utility utilization verification tests** (verify logging, telemetry, error handling, security, multi-tenancy)

## Current State

### Layer 2 (Initialization) - ✅ Complete
- Uses `test_infrastructure` fixture (PWF, Curator, Platform Gateway only)
- Tests verify services initialize correctly
- **Status**: All 25 services tested ✅

### Layer 3 (Functionality) - ⏳ In Progress
- Needs Smart City services (Librarian, Data Steward, Content Steward)
- Should use `smart_city_infrastructure` fixture
- **Status**: Partial (some tests exist, need to update to use new fixture)

### Utility Utilization Tests - ⚠️ Partial
- Existing tests use **mocks** (`test_enabling_services_utility_and_functionality.py`)
- Need **real infrastructure tests** to verify actual utility usage
- **Status**: Need to add real infrastructure verification

## Recommended Implementation Plan

### Phase 1: Service Discovery Tests (New - High Priority)

**Create**: `test_service_discovery.py`

**Purpose**: Verify enabling services can discover and use Smart City services via Curator.

**Tests**:
```python
@pytest.mark.asyncio
async def test_enabling_service_discovers_librarian(self, smart_city_infrastructure):
    """Verify enabling service can discover Librarian via Curator."""
    infra = smart_city_infrastructure
    
    # Test with Validation Engine (example)
    service = ValidationEngineService(...)
    await service.initialize()
    
    # Verify discovery
    librarian = await service.get_librarian_api()
    assert librarian is not None, "Should discover Librarian"
    
    # Verify SOA API is callable
    # (Test with actual call if possible)

@pytest.mark.asyncio
async def test_enabling_service_discovers_data_steward(self, smart_city_infrastructure):
    """Verify enabling service can discover Data Steward via Curator."""
    # Similar pattern

@pytest.mark.asyncio
async def test_enabling_service_discovers_content_steward(self, smart_city_infrastructure):
    """Verify enabling service can discover Content Steward via Curator."""
    # Similar pattern

@pytest.mark.asyncio
async def test_enabling_service_registered_with_curator(self, smart_city_infrastructure):
    """Verify enabling service is registered with Curator."""
    infra = smart_city_infrastructure
    curator = infra["curator"]
    
    service = ValidationEngineService(...)
    await service.initialize()
    
    # Verify service is registered
    # Check curator.registered_services or capability registry
```

### Phase 2: Utility Utilization Tests (New - High Priority)

**Create**: `test_utility_utilization_real.py` (to distinguish from mock tests)

**Purpose**: Verify services actually use platform utilities with real infrastructure.

**Tests**:
```python
@pytest.mark.asyncio
async def test_service_uses_logging(self, smart_city_infrastructure):
    """Verify service logs operations via utility access."""
    infra = smart_city_infrastructure
    service = ValidationEngineService(...)
    
    # Initialize service
    await service.initialize()
    
    # Perform operation
    result = await service.validate_data(...)
    
    # Verify logging occurred
    # Check DI container logger was called
    # Verify log entries contain expected information

@pytest.mark.asyncio
async def test_service_uses_telemetry(self, smart_city_infrastructure):
    """Verify service tracks operations with telemetry."""
    infra = smart_city_infrastructure
    service = ValidationEngineService(...)
    
    await service.initialize()
    
    # Perform operation
    result = await service.validate_data(...)
    
    # Verify telemetry was tracked
    # Check telemetry abstraction was called
    # Verify telemetry data structure

@pytest.mark.asyncio
async def test_service_handles_errors_with_audit(self, smart_city_infrastructure):
    """Verify service handles errors with audit trail."""
    infra = smart_city_infrastructure
    service = ValidationEngineService(...)
    
    await service.initialize()
    
    # Trigger error condition (e.g., invalid data_id)
    result = await service.validate_data(
        data_id="non_existent_id",
        validation_rules={...}
    )
    
    # Verify error was handled
    assert result.get("success") is False, "Should handle error"
    
    # Verify audit trail was created
    # Check error handler was called
    # Verify error details are logged

@pytest.mark.asyncio
async def test_service_validates_security(self, smart_city_infrastructure):
    """Verify service validates permissions (zero-trust)."""
    infra = smart_city_infrastructure
    service = ValidationEngineService(...)
    
    await service.initialize()
    
    # Test with insufficient permissions
    # (This requires mocking security or using test security context)
    user_context = {
        "user_id": "test_user",
        "tenant_id": "test_tenant",
        "permissions": []  # No permissions
    }
    
    # Attempt operation
    # Verify access is denied
    # Verify security validation was called

@pytest.mark.asyncio
async def test_service_validates_tenant(self, smart_city_infrastructure):
    """Verify service validates tenant access (multi-tenancy)."""
    infra = smart_city_infrastructure
    service = ValidationEngineService(...)
    
    await service.initialize()
    
    # Test with invalid tenant
    user_context = {
        "user_id": "test_user",
        "tenant_id": "invalid_tenant"
    }
    
    # Attempt operation
    # Verify tenant access is validated
    # Verify multi-tenant isolation
```

### Phase 3: Update Existing Functionality Tests

**Update**: `test_enabling_services_comprehensive.py`

**Changes**:
- Keep `TestEnablingServicesInitialization` using `test_infrastructure` (Layer 2)
- Update `TestEnablingServicesFunctionality` to use `smart_city_infrastructure` (Layer 3)

**Pattern**:
```python
class TestEnablingServicesInitialization:
    """Layer 2: Initialization tests - don't need Smart City services."""
    
    @pytest.fixture
    async def test_infrastructure(self):
        # Keep existing fixture (PWF, Curator, Platform Gateway only)
        ...

class TestEnablingServicesFunctionality:
    """Layer 3: Functionality tests - need Smart City services."""
    
    # Use smart_city_infrastructure fixture (from test_smart_city_infrastructure.py)
    @pytest.mark.asyncio
    async def test_validation_engine_validates_data(self, smart_city_infrastructure):
        # Use new fixture
        ...
```

### Phase 4: Add Comprehensive Functionality Tests

**Continue**: Adding functionality tests for priority services using `smart_city_infrastructure` fixture.

## Implementation Order

### Step 1: Create Service Discovery Tests (1-2 hours)
- Create `test_service_discovery.py`
- Test Librarian, Data Steward, Content Steward discovery
- Test Curator registration

### Step 2: Create Utility Utilization Tests (2-3 hours)
- Create `test_utility_utilization_real.py`
- Test logging, telemetry, error handling, security, multi-tenancy
- Use real infrastructure (not mocks)

### Step 3: Update Existing Functionality Tests (1 hour)
- Update `test_enabling_services_comprehensive.py`
- Change Layer 3 tests to use `smart_city_infrastructure`
- Keep Layer 2 tests using `test_infrastructure`

### Step 4: Continue Functionality Tests (Ongoing)
- Add functionality tests for remaining priority services
- Use `smart_city_infrastructure` fixture

## Test File Structure

```
tests/integration/layer_8_business_enablement/
├── test_smart_city_infrastructure.py          # ✅ Created (fixture)
├── test_enabling_services_comprehensive.py    # ⏳ Update (Layer 2 + Layer 3)
├── test_service_discovery.py                  # ⏳ Create (new)
├── test_utility_utilization_real.py           # ⏳ Create (new)
└── test_file_parser_core.py                  # ✅ Existing (may need update)
```

## Key Decisions

### ✅ Layer 2 Tests
- **Keep using `test_infrastructure`** (PWF, Curator, Platform Gateway only)
- Don't need Smart City services for initialization tests
- Simpler, faster tests

### ✅ Layer 3 Tests
- **Use `smart_city_infrastructure`** (full Smart City stack)
- Need Smart City services for functionality tests
- More comprehensive, realistic tests

### ✅ Utility Utilization
- **Real infrastructure tests** (not mocks)
- Verify actual utility usage in production-like environment
- Test logging, telemetry, error handling, security, multi-tenancy

### ✅ Service Discovery
- **Verify via Curator** (proper architecture)
- Test SOA API discovery and usage
- Verify services are registered

## Success Criteria

### Service Discovery
- ✅ All enabling services can discover Librarian
- ✅ All enabling services can discover Data Steward
- ✅ All enabling services can discover Content Steward
- ✅ Services are registered with Curator
- ✅ SOA APIs are callable

### Utility Utilization
- ✅ Services use logging utility (verify log entries)
- ✅ Services track operations with telemetry (verify telemetry calls)
- ✅ Services handle errors with audit trail (verify error handling)
- ✅ Services validate permissions (verify security checks)
- ✅ Services validate tenant access (verify multi-tenancy)

### Functionality
- ✅ Priority services work correctly
- ✅ Business logic is verified
- ✅ Error cases are handled
- ✅ Edge cases are tested

## Next Immediate Steps

1. **Create `test_service_discovery.py`** - Verify Smart City service discovery
2. **Create `test_utility_utilization_real.py`** - Verify utility usage with real infrastructure
3. **Update `test_enabling_services_comprehensive.py`** - Use new fixture for Layer 3 tests
4. **Continue functionality tests** - Add tests for remaining priority services

## Notes

- **Layer 2 vs Layer 3**: Clear separation - Layer 2 doesn't need Smart City services
- **Utility Utilization**: Focus on real infrastructure, not mocks
- **Service Discovery**: Critical for architecture validation
- **Incremental Approach**: Build tests incrementally, verify as we go

