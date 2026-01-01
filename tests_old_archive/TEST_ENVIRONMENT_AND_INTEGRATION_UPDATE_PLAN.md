# Test Environment and Integration Test Update Plan

**Date:** December 2024  
**Status:** Planning Phase  
**Purpose:** Update test environment and integration tests to align with architectural overhaul

---

## 🎯 EXECUTIVE SUMMARY

The platform has undergone a **comprehensive architectural overhaul** across all realms:
- **Business Enablement Realm**: 18 agents + 4 orchestrators + 1 manager + MCP servers
- **Journey Realm**: 6 services + 1 manager + MCP server
- **Solution Realm**: 4 services + 1 manager + MCP server

**Key Architectural Changes:**
1. ✅ **Utility Methods**: All services use `log_operation_with_telemetry()`, `record_health_metric()`, `handle_error_with_audit()`
2. ✅ **user_context Parameter**: All SOA API methods accept `user_context: Optional[Dict[str, Any]] = None`
3. ✅ **Phase 2 Curator Registration**: All services use `CapabilityDefinition` structure with contracts
4. ✅ **MCP Servers**: Manager services expose capabilities via MCP servers
5. ✅ **Security & Tenant Validation**: Zero-trust security and multi-tenant isolation enforced

---

## 🏗️ TESTING PHILOSOPHY: BOTTOM-UP LAYERED APPROACH

**CRITICAL PRINCIPLE:** Complete bottom-up testing ensures issues are caught early when they're easiest to diagnose and fix.

**Test Order (MUST follow this sequence):**

1. **Layer 0: Platform Startup** - Does the platform start?
2. **Layer 1: Utilities Functionality** - Do utilities properly work?
3. **Layer 2: DI Container Functionality** - Does DI Container properly enable platform dependencies?
4. **Layer 3: Public Works Adapters** - Do adapters work with real infrastructure?
5. **Layer 4: Public Works Composition Services** - Do composition services work?
6. **Layer 5: Public Works Abstractions** - Do abstractions work?
7. **Layer 6: Other Foundations** - Do Curator, Communication, Agentic foundations work?
8. **Layer 7: Smart City & Platform Gateway** - Are platform capabilities properly exposed?
9. **Layer 8: Realm Service Composition** - Do realms properly compose services using SOA APIs from Curator and abstractions from Platform Gateway (agents, MCP servers/tools)?

**Each layer MUST pass before proceeding to the next layer.**

---

**Test Environment Gaps:**
- ❌ Test fixtures don't provide `user_context` by default
- ❌ Tests don't verify Phase 2 registration patterns
- ❌ Tests don't verify utility method usage
- ❌ Tests don't verify MCP server integration
- ❌ Test mocks don't align with new utility patterns

**Integration Test Gaps:**
- ❌ No tests for Journey realm refactoring
- ❌ No tests for Solution realm refactoring
- ❌ No tests for Phase 2 Curator registration
- ❌ No tests for MCP server functionality
- ❌ Existing tests don't use `user_context` parameter

---

## 📋 TEST ENVIRONMENT UPDATES

### **1. Update `conftest.py` Fixtures**

**File:** `tests/conftest.py`

**Required Updates:**

```python
# Add user_context fixtures
@pytest.fixture
def user_context():
    """Standard user context for testing."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": ["read", "write", "execute"],
        "roles": ["user", "admin"]
    }

@pytest.fixture
def admin_user_context():
    """Admin user context for testing."""
    return {
        "user_id": "admin_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": ["read", "write", "execute", "admin"],
        "roles": ["admin", "super_admin"]
    }

@pytest.fixture
def invalid_user_context():
    """User context with no permissions."""
    return {
        "user_id": "restricted_user_123",
        "tenant_id": "test_tenant_456",
        "permissions": [],
        "roles": ["viewer"]
    }

@pytest.fixture
def invalid_tenant_context():
    """User context with invalid tenant."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "invalid_tenant_999",
        "permissions": ["read", "write", "execute"],
        "roles": ["user"]
    }

# Update utility service mocks to match new patterns
@pytest.fixture
def mock_telemetry_foundation():
    """Mock TelemetryFoundationService with new methods."""
    telemetry = AsyncMock()
    telemetry.record_platform_operation_event = AsyncMock(return_value=True)
    return telemetry

@pytest.fixture
def mock_health_foundation():
    """Mock HealthFoundationService with new methods."""
    health = AsyncMock()
    health.record_metric = AsyncMock(return_value=True)
    return health

@pytest.fixture
def mock_security_foundation():
    """Mock SecurityFoundationService with new methods."""
    security = AsyncMock()
    security.check_permissions = AsyncMock(return_value=True)
    return security

@pytest.fixture
def mock_tenant_foundation():
    """Mock TenantFoundationService with new methods."""
    tenant = AsyncMock()
    tenant.validate_tenant_access = AsyncMock(return_value=True)
    tenant.get_tenant_service = Mock(return_value=tenant)
    return tenant

@pytest.fixture
def mock_error_handling_foundation():
    """Mock ErrorHandlingFoundationService with new methods."""
    error_handler = AsyncMock()
    error_handler.handle_error_with_audit = AsyncMock(return_value=True)
    return error_handler

@pytest.fixture
def mock_curator_foundation():
    """Mock CuratorFoundationService with Phase 2 registration support."""
    curator = AsyncMock()
    curator.register_service = AsyncMock(return_value={"success": True})
    curator.get_service = AsyncMock(return_value=None)
    curator.discover_services = AsyncMock(return_value=[])
    return curator

@pytest.fixture
def mock_di_container_with_utilities(
    mock_telemetry_foundation,
    mock_health_foundation,
    mock_security_foundation,
    mock_tenant_foundation,
    mock_error_handling_foundation,
    mock_curator_foundation
):
    """DI Container with all utility foundations properly mocked."""
    container = Mock()
    
    def get_foundation_service(name):
        services = {
            "TelemetryFoundationService": mock_telemetry_foundation,
            "HealthFoundationService": mock_health_foundation,
            "SecurityFoundationService": mock_security_foundation,
            "TenantFoundationService": mock_tenant_foundation,
            "ErrorHandlingFoundationService": mock_error_handling_foundation,
            "CuratorFoundationService": mock_curator_foundation,
            "PlatformInfrastructureGateway": Mock(),
            "PublicWorksFoundationService": Mock(),
            "PolicyIntegrationService": Mock(),
            "AGUISchemaRegistry": Mock()
        }
        return services.get(name)
    
    container.get_foundation_service = Mock(side_effect=get_foundation_service)
    container.get_logger = Mock(return_value=Mock())
    container.get_config = Mock(return_value={})
    
    return container
```

---

### **2. Create Realm-Specific Test Fixtures**

**New Files:**
- `tests/integration/journey/conftest.py`
- `tests/integration/solution/conftest.py`

**Journey Realm Fixtures:**
```python
# tests/integration/journey/conftest.py
@pytest.fixture
async def journey_manager_service(mock_di_container_with_utilities, mock_platform_gateway):
    """Journey Manager Service fixture."""
    from backend.journey.services.journey_manager.journey_manager_service import JourneyManagerService
    
    service = JourneyManagerService(
        di_container=mock_di_container_with_utilities,
        platform_gateway=mock_platform_gateway
    )
    await service.initialize()
    return service
```

**Solution Realm Fixtures:**
```python
# tests/integration/solution/conftest.py
@pytest.fixture
async def solution_manager_service(mock_di_container_with_utilities, mock_platform_gateway):
    """Solution Manager Service fixture."""
    from backend.solution.services.solution_manager.solution_manager_service import SolutionManagerService
    
    service = SolutionManagerService(
        di_container=mock_di_container_with_utilities,
        platform_gateway=mock_platform_gateway
    )
    await service.initialize()
    return service
```

---

### **3. Update Test Helpers**

**File:** `tests/utils/test_helpers.py`

**Add Helper Functions:**

```python
def assert_phase2_registration(call_args):
    """Assert that Curator registration uses Phase 2 pattern."""
    assert "service_id" in call_args
    assert "service_name" in call_args
    assert "service_type" in call_args
    assert "realm_name" in call_args
    assert "capabilities" in call_args
    assert isinstance(call_args["capabilities"], list)
    
    if call_args["capabilities"]:
        capability = call_args["capabilities"][0]
        assert "name" in capability
        assert "protocol" in capability
        assert "contracts" in capability
        assert "semantic_mapping" in capability

def assert_user_context_parameter(method):
    """Assert that method accepts user_context parameter."""
    import inspect
    sig = inspect.signature(method)
    params = list(sig.parameters.keys())
    assert "user_context" in params

def create_user_context(user_id="test_user", tenant_id="test_tenant", permissions=None):
    """Create a user context for testing."""
    if permissions is None:
        permissions = ["read", "write", "execute"]
    
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "permissions": permissions,
        "roles": ["user"]
    }
```

---

## 🔄 INTEGRATION TEST UPDATES (BOTTOM-UP LAYERED APPROACH)

**CRITICAL:** Tests must follow strict bottom-up order. Each layer must be fully tested and passing before moving to the next layer.

### **Layer 0: Platform Startup Tests** 🔴 **CRITICAL - TEST FIRST**

**Goal:** Verify platform actually starts and initializes correctly.

**Files:**
- `tests/integration/layer_0_startup/test_platform_startup.py` (update existing)
- `tests/integration/layer_0_startup/test_foundation_initialization.py` (update existing)

**Required Tests:**
1. ✅ Platform starts successfully (main.py, startup.sh)
2. ✅ All foundations initialize (Public Works, Curator, Communication, Agentic)
3. ✅ DI Container initializes correctly
4. ✅ Platform Gateway initializes
5. ✅ API routers register successfully
6. ✅ Platform shuts down gracefully
7. ✅ Error handling during startup (graceful failures)
8. ✅ Health checks work after startup

**Updates Needed:**
- Add `user_context` support to startup tests
- Verify utility services are initialized
- Verify Phase 2 Curator registration during startup

---

### **Layer 1: Utilities Functionality Tests** 🔴 **CRITICAL - TEST SECOND**

**Goal:** Verify utilities actually work (not just exist).

**Files:**
- `tests/integration/layer_2_utilities/test_utilities_functionality.py` (update existing)

**Required Tests:**
1. ✅ Logging utility works (actually logs messages)
2. ✅ Health utility works (actually reports health)
3. ✅ Telemetry utility works (actually emits metrics)
4. ✅ Security utility works (actually enforces security)
5. ✅ Tenant utility works (actually manages tenants)
6. ✅ Error handler utility works (actually handles errors)
7. ✅ Validation utility works (actually validates data)
8. ✅ Serialization utility works (actually serializes data)

**Updates Needed:**
- Verify new utility methods (`log_operation_with_telemetry`, `record_health_metric`, `handle_error_with_audit`)
- Test with real infrastructure where applicable
- Test utility integration with DI Container

---

### **Layer 2: DI Container Functionality Tests** 🔴 **CRITICAL - TEST THIRD**

**Goal:** Verify DI Container actually enables platform dependencies.

**Files:**
- `tests/integration/layer_1_di_container/test_di_container_functionality.py` (update existing)

**Required Tests:**
1. ✅ Service registration works (actually register services)
2. ✅ Service retrieval works (actually retrieve services)
3. ✅ Utility access works (actually get utilities)
4. ✅ Foundation service access works (get_foundation_service)
5. ✅ Service lifecycle works (start, stop, restart)
6. ✅ Error handling (missing services, circular dependencies)
7. ✅ Multi-tenant support works
8. ✅ Security integration works

**Updates Needed:**
- Verify DI Container provides all utility foundations
- Test Phase 2 Curator registration via DI Container
- Test MCP server access via DI Container

---

### **Layer 3: Public Works Adapters Tests** 🟠 **HIGH PRIORITY - TEST FOURTH**

**Goal:** Verify Public Works adapters work with real infrastructure.

**Files:**
- `tests/integration/infrastructure_adapters/test_redis_adapter_real.py` (update existing)
- `tests/integration/infrastructure_adapters/test_arangodb_adapter_real.py` (update existing)
- `tests/integration/infrastructure_adapters/test_meilisearch_adapter_real.py` (update existing)
- `tests/integration/infrastructure_adapters/test_all_adapters_initialization.py` (update existing)

**Required Tests:**
1. ✅ Redis adapter works with real Redis
2. ✅ ArangoDB adapter works with real ArangoDB
3. ✅ Meilisearch adapter works with real Meilisearch
4. ✅ All adapters initialize correctly
5. ✅ Adapter error handling works
6. ✅ Adapter connection pooling works

**Updates Needed:**
- Verify adapters use real infrastructure (not mocks)
- Test adapter integration with Public Works Foundation
- Test adapter error scenarios

---

### **Layer 4: Public Works Composition Services Tests** 🟠 **HIGH PRIORITY - TEST FIFTH**

**Goal:** Verify Public Works composition services work correctly.

**Files:**
- `tests/integration/foundations/test_public_works_composition.py` (new or update existing)

**Required Tests:**
1. ✅ Document Intelligence Service works
2. ✅ Workflow Orchestration Service works
3. ✅ All composition services initialize correctly
4. ✅ Composition services use adapters correctly
5. ✅ Composition services expose abstractions correctly

**Updates Needed:**
- Add tests for all composition services
- Verify composition services use real adapters
- Test composition service error handling

---

### **Layer 5: Public Works Abstractions Tests** 🟠 **HIGH PRIORITY - TEST SIXTH**

**Goal:** Verify Public Works abstractions work correctly.

**Files:**
- `tests/integration/foundations/test_all_abstractions_initialization.py` (update existing)
- `tests/integration/foundations/test_abstraction_exposure_registries.py` (update existing)

**Required Tests:**
1. ✅ All abstractions initialize correctly
2. ✅ Abstractions use composition services correctly
3. ✅ Abstractions expose via registries correctly
4. ✅ Smart City can access abstractions directly
5. ✅ Other realms access abstractions via Platform Gateway

**Updates Needed:**
- Verify abstraction exposure patterns
- Test abstraction access via Platform Gateway
- Test abstraction error handling

---

### **Layer 6: Other Foundations Tests** 🟠 **HIGH PRIORITY - TEST SEVENTH**

**Goal:** Verify all foundations work correctly.

**Files:**
- `tests/integration/foundations/test_foundation_integration.py` (update existing)
- `tests/integration/foundations/test_curator_foundation.py` (new)
- `tests/integration/foundations/test_communication_foundation.py` (new)
- `tests/integration/foundations/test_agentic_foundation.py` (new)

**Required Tests:**
1. ✅ Curator Foundation works (Phase 2 registration)
2. ✅ Communication Foundation works
3. ✅ Agentic Foundation works
4. ✅ All foundations initialize together
5. ✅ Foundations integrate correctly

**Updates Needed:**
- Add Phase 2 Curator registration tests
- Test foundation integration
- Verify utility usage in foundations

---

### **Layer 7: Smart City & Platform Gateway Tests** 🟠 **HIGH PRIORITY - TEST EIGHTH**

**Goal:** Verify Smart City and Platform Gateway properly expose platform capabilities.

**Files:**
- `tests/integration/smart_city/test_smart_city_integration.py` (update existing)
- `tests/integration/platform_gateway/test_realm_abstraction_access.py` (update existing)
- `tests/integration/smart_city/test_all_services_initialization.py` (update existing)

**Required Tests:**
1. ✅ Smart City services initialize correctly
2. ✅ Smart City services use abstractions directly
3. ✅ Platform Gateway exposes abstractions to realms
4. ✅ Platform Gateway validates realm access
5. ✅ Smart City services register with Curator (Phase 2)

**Updates Needed:**
- Add Phase 2 Curator registration tests
- Add `user_context` parameter tests
- Add utility method usage tests
- Test Platform Gateway realm access patterns

---

### **Layer 8: Realm Service Composition Tests** 🟡 **MEDIUM PRIORITY - TEST NINTH**

**Goal:** Verify realms properly compose services using SOA APIs from Curator and abstractions from Platform Gateway.

**Test Order:**
1. **Business Enablement Realm** (test first - most mature)
2. **Journey Realm** (test second)
3. **Solution Realm** (test third)

#### **8.1 Business Enablement Realm Tests**

**Files:**
- `tests/integration/business_enablement/test_enabling_services_utility_and_functionality.py` (update existing)
- `tests/integration/business_enablement/test_enabling_services_functional.py` (update existing)
- `tests/integration/orchestrators/test_content_analysis_orchestrator.py` (update existing)
- `tests/integration/orchestrators/test_insights_orchestrator.py` (update existing)
- `tests/integration/orchestrators/test_operations_orchestrator.py` (update existing)
- `tests/integration/managers/test_delivery_manager.py` (new)

**Required Tests:**
1. ✅ All enabling services use SOA APIs from Curator
2. ✅ All enabling services use abstractions from Platform Gateway
3. ✅ All enabling services use `user_context` parameter
4. ✅ All enabling services use utility methods
5. ✅ All enabling services use Phase 2 Curator registration
6. ✅ All orchestrators compose enabling services correctly
7. ✅ Delivery Manager orchestrates orchestrators correctly
8. ✅ Agents use MCP tools correctly
9. ✅ MCP servers expose tools correctly

**Updates Needed:**
- Add `user_context` to all test method calls
- Verify Phase 2 Curator registration
- Verify utility method usage
- Add security/tenant validation tests
- Add MCP server tests

#### **8.2 Journey Realm Tests**

**Files:**
- `tests/integration/journey/test_journey_realm_refactoring.py` (new)

**Required Tests:**
1. ✅ Journey services use SOA APIs from Curator
2. ✅ Journey services use abstractions from Platform Gateway
3. ✅ Journey services use `user_context` parameter
4. ✅ Journey services use utility methods
5. ✅ Journey services use Phase 2 Curator registration
6. ✅ Journey Manager orchestrates journey services correctly
7. ✅ Journey Manager MCP Server exposes tools correctly
8. ✅ Journey services compose correctly

#### **8.3 Solution Realm Tests**

**Files:**
- `tests/integration/solution/test_solution_realm_refactoring.py` (new)

**Required Tests:**
1. ✅ Solution services use SOA APIs from Curator
2. ✅ Solution services use abstractions from Platform Gateway
3. ✅ Solution services use `user_context` parameter
4. ✅ Solution services use utility methods
5. ✅ Solution services use Phase 2 Curator registration
6. ✅ Solution Manager orchestrates solution services correctly
7. ✅ Solution Manager MCP Server exposes tools correctly
8. ✅ Solution services compose correctly

---

### **Layer 9: Cross-Realm Integration Tests** 🟡 **MEDIUM PRIORITY - TEST TENTH**

**Goal:** Verify cross-realm flows work correctly.

**Files:**
- `tests/integration/cross_realm/test_solution_to_journey.py` (update existing)
- `tests/integration/cross_realm/test_solution_to_journey_comprehensive.py` (update existing)
- `tests/integration/test_manager_top_down_flow.py` (update existing)

**Required Tests:**
1. ✅ Solution → Journey → Experience top-down flow
2. ✅ `user_context` propagates through layers
3. ✅ Utility methods propagate through layers
4. ✅ Security/tenant validation at each layer
5. ✅ MCP tools work across realms

**Updates Needed:**
- Add `user_context` to all service method calls
- Verify utility methods propagate
- Test security/tenant validation at each layer

---

### **Layer 10: MCP Server Integration Tests** 🟡 **MEDIUM PRIORITY - TEST ELEVENTH**

**Goal:** Verify MCP servers work correctly.

**Files:**
- `tests/integration/mcp_servers/test_manager_mcp_servers.py` (new)

**Required Tests:**
1. ✅ All manager MCP servers registered
2. ✅ MCP tools execute correctly
3. ✅ MCP tools use `user_context` parameter
4. ✅ MCP tools validate security/tenant
5. ✅ MCP tools use utility methods

---

### **Layer 11: Agent Integration Tests** 🟡 **MEDIUM PRIORITY - TEST TWELFTH**

**Goal:** Verify agents use MCP tools correctly.

**Files:**
- `tests/integration/agentic/test_agents_use_mcp_tools.py` (new)

**Required Tests:**
1. ✅ Agents can discover MCP tools via Curator
2. ✅ Agents can execute MCP tools
3. ✅ Agents pass `user_context` to MCP tools
4. ✅ Agents handle MCP tool errors correctly

---

## 📊 TEST EXECUTION STRATEGY (BOTTOM-UP LAYERED APPROACH)

**CRITICAL PRINCIPLE:** Each layer must be fully tested and passing before moving to the next layer. This ensures issues are caught early when they're easiest to diagnose and fix.

### **Phase 1: Test Environment Setup** (Day 1 Morning)

1. ✅ Update `conftest.py` with new fixtures
2. ✅ Create realm-specific conftest files
3. ✅ Update test helpers
4. ✅ Verify fixtures work with existing tests

---

### **Phase 2: Layer 0 - Platform Startup** (Day 1 Morning)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test platform startup
2. ✅ Test foundation initialization
3. ✅ Test DI Container initialization
4. ✅ Test Platform Gateway initialization
5. ✅ Verify all layers initialize correctly

**Success Criteria:** Platform starts without errors, all foundations accessible

---

### **Phase 3: Layer 1 - Utilities Functionality** (Day 1 Afternoon)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test all utility methods work
2. ✅ Test utility integration with DI Container
3. ✅ Test utility error handling
4. ✅ Verify new utility methods (`log_operation_with_telemetry`, `record_health_metric`, `handle_error_with_audit`)

**Success Criteria:** All utilities work correctly, accessible via DI Container

---

### **Phase 4: Layer 2 - DI Container Functionality** (Day 1 Afternoon)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test service registration/retrieval
2. ✅ Test foundation service access
3. ✅ Test utility access
4. ✅ Test service lifecycle
5. ✅ Test error handling

**Success Criteria:** DI Container enables all platform dependencies correctly

---

### **Phase 5: Layer 3 - Public Works Adapters** (Day 2 Morning)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test Redis adapter with real Redis
2. ✅ Test ArangoDB adapter with real ArangoDB
3. ✅ Test Meilisearch adapter with real Meilisearch
4. ✅ Test all adapters initialize correctly
5. ✅ Test adapter error handling

**Success Criteria:** All adapters work with real infrastructure

---

### **Phase 6: Layer 4 - Public Works Composition Services** (Day 2 Morning)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test Document Intelligence Service
2. ✅ Test Workflow Orchestration Service
3. ✅ Test all composition services
4. ✅ Verify composition services use adapters correctly

**Success Criteria:** All composition services work correctly

---

### **Phase 7: Layer 5 - Public Works Abstractions** (Day 2 Afternoon)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test all abstractions initialize
2. ✅ Test abstraction exposure patterns
3. ✅ Test Smart City direct access
4. ✅ Test Platform Gateway realm access

**Success Criteria:** Abstractions work correctly, exposure patterns validated

---

### **Phase 8: Layer 6 - Other Foundations** (Day 2 Afternoon)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test Curator Foundation (Phase 2 registration)
2. ✅ Test Communication Foundation
3. ✅ Test Agentic Foundation
4. ✅ Test foundation integration

**Success Criteria:** All foundations work correctly, integrate together

---

### **Phase 9: Layer 7 - Smart City & Platform Gateway** (Day 3 Morning)

**MUST PASS BEFORE PROCEEDING**

1. ✅ Test Smart City services initialization
2. ✅ Test Smart City abstraction access
3. ✅ Test Platform Gateway realm access
4. ✅ Test Phase 2 Curator registration
5. ✅ Test utility method usage

**Success Criteria:** Smart City and Platform Gateway expose capabilities correctly

---

### **Phase 10: Layer 8 - Realm Service Composition** (Day 3 Morning/Afternoon)

**Test in order: Business Enablement → Journey → Solution**

#### **10.1 Business Enablement Realm** (Day 3 Morning)

1. ✅ Update enabling services tests
2. ✅ Update orchestrator tests
3. ✅ Test Delivery Manager
4. ✅ Test MCP servers
5. ✅ Test agents

#### **10.2 Journey Realm** (Day 3 Afternoon)

1. ✅ Create Journey realm tests
2. ✅ Test all Journey services
3. ✅ Test Journey Manager
4. ✅ Test Journey Manager MCP Server

#### **10.3 Solution Realm** (Day 3 Afternoon)

1. ✅ Create Solution realm tests
2. ✅ Test all Solution services
3. ✅ Test Solution Manager
4. ✅ Test Solution Manager MCP Server

**Success Criteria:** All realms compose services correctly using SOA APIs and abstractions

---

### **Phase 11: Layer 9 - Cross-Realm Integration** (Day 4 Morning)

1. ✅ Update cross-realm tests
2. ✅ Test top-down flows
3. ✅ Test `user_context` propagation
4. ✅ Test utility method propagation

**Success Criteria:** Cross-realm flows work correctly

---

### **Phase 12: Layer 10 - MCP Server Integration** (Day 4 Morning)

1. ✅ Create MCP server tests
2. ✅ Test all manager MCP servers
3. ✅ Test MCP tool execution
4. ✅ Test MCP tool security

**Success Criteria:** All MCP servers work correctly

---

### **Phase 13: Layer 11 - Agent Integration** (Day 4 Afternoon)

1. ✅ Create agent integration tests
2. ✅ Test agents use MCP tools
3. ✅ Test agent discovery
4. ✅ Test agent execution

**Success Criteria:** Agents use MCP tools correctly

---

### **Phase 14: Validation & Cleanup** (Day 4 Afternoon)

1. ✅ Run full test suite
2. ✅ Fix any failures
3. ✅ Update documentation
4. ✅ Create test execution guide

---

## ✅ SUCCESS CRITERIA

### **Test Environment:**
- [ ] All fixtures provide `user_context` by default
- [ ] All utility services are properly mocked
- [ ] Phase 2 registration can be verified
- [ ] MCP servers can be tested

### **Integration Tests:**
- [ ] Journey realm fully tested
- [ ] Solution realm fully tested
- [ ] All services use `user_context` parameter
- [ ] All services use utility methods
- [ ] All services use Phase 2 registration
- [ ] All MCP servers tested
- [ ] Security/tenant validation tested

---

## 🚀 QUICK START GUIDE

### **1. Update Test Environment**
```bash
cd /home/founders/demoversion/symphainy_source/tests
# Edit conftest.py to add new fixtures
```

### **2. Create Realm Tests**
```bash
# Create Journey realm tests
touch tests/integration/journey/test_journey_realm_refactoring.py

# Create Solution realm tests
touch tests/integration/solution/test_solution_realm_refactoring.py
```

### **3. Run Tests**
```bash
# Run Journey realm tests
pytest tests/integration/journey/ -v

# Run Solution realm tests
pytest tests/integration/solution/ -v
```

---

**Ready for implementation!** 🚀

