# Layer 3 Testing Plan - Component Functionality Tests

## Overview

Layer 3 tests verify that enabling services **actually work** (not just initialize). These tests require Smart City services to be available, so they use the `smart_city_infrastructure` fixture.

## Test Categories

### 1. Service Discovery Verification
**Purpose**: Verify that enabling services can discover and use Smart City services via Curator.

**Tests**:
- Verify services can discover Librarian via `get_librarian_api()`
- Verify services can discover Data Steward via `get_data_steward_api()`
- Verify services can discover Content Steward via `get_content_steward_api()`
- Verify services are registered with Curator (capability registration)
- Verify SOA APIs are callable and return expected results

### 2. Functionality Tests (Priority Services)
**Purpose**: Verify core functionality of priority enabling services.

**Services**:
1. File Parser - File parsing functionality
2. Validation Engine - Data validation functionality
3. Transformation Engine - Data transformation functionality
4. Data Analyzer - Data analysis functionality
5. Schema Mapper - Schema mapping functionality
6. Workflow Manager - Workflow management functionality
7. Report Generator - Report generation functionality
8. Visualization Engine - Visualization functionality

### 3. Utility Utilization Verification
**Purpose**: Verify that services properly use platform utilities (logging, telemetry, error handling, security, multi-tenancy).

**Verification Points**:
- **Logging**: Services log operations via utility access
- **Telemetry**: Services track operations with telemetry
- **Error Handling**: Services handle errors with audit trail
- **Security**: Services validate permissions (zero-trust)
- **Multi-tenancy**: Services validate tenant access

## Test Structure

### Layer 2 vs Layer 3

**Layer 2 (Initialization Tests)**:
- Simple tests that verify services initialize
- Don't require Smart City services to be fully functional
- Use basic `test_infrastructure` fixture (just PWF, Curator, Platform Gateway)
- **Status**: Already complete ✅

**Layer 3 (Functionality Tests)**:
- Tests that verify services actually work
- Require Smart City services (Librarian, Data Steward, Content Steward)
- Use `smart_city_infrastructure` fixture (full Smart City stack)
- **Status**: In progress ⏳

## Implementation Plan

### Phase 1: Service Discovery Tests (New)
**Goal**: Verify enabling services can discover and use Smart City services.

**Tests to Create**:
1. `test_service_discovery_librarian.py` - Verify Librarian discovery
2. `test_service_discovery_data_steward.py` - Verify Data Steward discovery
3. `test_service_discovery_content_steward.py` - Verify Content Steward discovery
4. `test_curator_registration.py` - Verify services register with Curator

**Pattern**:
```python
@pytest.mark.asyncio
async def test_service_discovers_librarian(self, smart_city_infrastructure):
    """Verify enabling service can discover Librarian via Curator."""
    infra = smart_city_infrastructure
    service = MyService(...)
    await service.initialize()
    
    # Verify service can discover Librarian
    librarian = await service.get_librarian_api()
    assert librarian is not None, "Service should discover Librarian"
    
    # Verify SOA API is callable
    result = await librarian.get_document("test_id")
    # Verify result structure
```

### Phase 2: Utility Utilization Tests (New)
**Goal**: Verify services properly use platform utilities.

**Tests to Create**:
1. `test_utility_utilization.py` - Comprehensive utility usage verification

**Verification Points**:
```python
@pytest.mark.asyncio
async def test_service_uses_logging(self, smart_city_infrastructure):
    """Verify service uses logging utility."""
    # Check that service logs operations
    # Verify log entries are created
    # Verify log format is correct

@pytest.mark.asyncio
async def test_service_uses_telemetry(self, smart_city_infrastructure):
    """Verify service tracks operations with telemetry."""
    # Check that telemetry is tracked
    # Verify telemetry data structure
    # Verify telemetry includes operation details

@pytest.mark.asyncio
async def test_service_handles_errors(self, smart_city_infrastructure):
    """Verify service handles errors with audit."""
    # Trigger an error condition
    # Verify error is handled with audit trail
    # Verify error details are logged

@pytest.mark.asyncio
async def test_service_validates_security(self, smart_city_infrastructure):
    """Verify service validates permissions (zero-trust)."""
    # Test with insufficient permissions
    # Verify access is denied
    # Verify security validation is called

@pytest.mark.asyncio
async def test_service_validates_tenant(self, smart_city_infrastructure):
    """Verify service validates tenant access (multi-tenancy)."""
    # Test with invalid tenant
    # Verify tenant access is validated
    # Verify multi-tenant isolation
```

### Phase 3: Functionality Tests (Priority Services)
**Goal**: Verify core functionality of priority services.

**Approach**:
- Use `smart_city_infrastructure` fixture
- Test actual service methods (not just initialization)
- Verify business logic works correctly
- Test error cases and edge cases

**Pattern**:
```python
@pytest.mark.asyncio
async def test_validation_engine_validates_data(self, smart_city_infrastructure):
    """Test Validation Engine can validate data."""
    infra = smart_city_infrastructure
    service = ValidationEngineService(...)
    await service.initialize()
    
    # Store test data via Content Steward
    storage_result = await service.store_document(...)
    data_id = storage_result["document_id"]
    
    # Test validation
    result = await service.validate_data(
        data_id=data_id,
        validation_rules={...},
        user_context={...}
    )
    
    # Verify result
    assert result["success"], "Validation should succeed"
    assert result["status"] in ["passed", "failed"], "Status should be set"
```

## Test File Organization

### New Test Files

1. **`test_service_discovery.py`** - Service discovery verification
   - Test Librarian discovery
   - Test Data Steward discovery
   - Test Content Steward discovery
   - Test Curator registration

2. **`test_utility_utilization.py`** - Utility usage verification
   - Test logging usage
   - Test telemetry usage
   - Test error handling
   - Test security validation
   - Test multi-tenancy validation

3. **`test_enabling_services_functionality.py`** - Functionality tests (update existing)
   - Use `smart_city_infrastructure` fixture
   - Test actual service methods
   - Verify business logic

### Updated Test Files

1. **`test_enabling_services_comprehensive.py`** - Update functionality tests
   - Change `test_infrastructure` → `smart_city_infrastructure` for Layer 3 tests
   - Keep `test_infrastructure` for Layer 2 initialization tests

## Migration Strategy

### Step 1: Create Service Discovery Tests
- Create `test_service_discovery.py`
- Verify services can discover Smart City services
- Verify SOA APIs are callable

### Step 2: Create Utility Utilization Tests
- Create `test_utility_utilization.py`
- Verify logging, telemetry, error handling, security, multi-tenancy
- Test with sample services (File Parser, Validation Engine)

### Step 3: Update Functionality Tests
- Update `test_enabling_services_comprehensive.py`
- Change Layer 3 tests to use `smart_city_infrastructure`
- Keep Layer 2 tests using `test_infrastructure`

### Step 4: Add Comprehensive Functionality Tests
- Add functionality tests for all priority services
- Use `smart_city_infrastructure` fixture
- Test actual business logic

## Success Criteria

### Service Discovery
- ✅ All enabling services can discover Librarian
- ✅ All enabling services can discover Data Steward
- ✅ All enabling services can discover Content Steward
- ✅ Services are registered with Curator
- ✅ SOA APIs are callable

### Utility Utilization
- ✅ Services use logging utility
- ✅ Services track operations with telemetry
- ✅ Services handle errors with audit trail
- ✅ Services validate permissions (zero-trust)
- ✅ Services validate tenant access (multi-tenancy)

### Functionality
- ✅ Priority services work correctly
- ✅ Business logic is verified
- ✅ Error cases are handled
- ✅ Edge cases are tested

## Next Steps

1. **Create Service Discovery Tests** - Verify Smart City service discovery
2. **Create Utility Utilization Tests** - Verify platform utility usage
3. **Update Existing Functionality Tests** - Use new fixture
4. **Add Comprehensive Functionality Tests** - Test all priority services

## Notes

- **Layer 2 tests** (initialization) don't need Smart City services - keep using `test_infrastructure`
- **Layer 3 tests** (functionality) need Smart City services - use `smart_city_infrastructure`
- **Utility utilization** is critical for platform quality - verify it's working
- **Service discovery** is critical for architecture - verify it's working

