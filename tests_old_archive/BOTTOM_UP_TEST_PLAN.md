# Bottom-Up Test Plan - Complete Platform Validation

**Date:** December 2024  
**Status:** Planning Phase  
**Purpose:** Comprehensive bottom-up testing strategy ensuring each layer works before building on top

---

## 🎯 TESTING PHILOSOPHY

**CRITICAL PRINCIPLE:** Complete bottom-up testing ensures issues are caught early when they're easiest to diagnose and fix.

**Key Principles:**
1. ✅ **Each layer must pass before proceeding** - No skipping layers
2. ✅ **Test components individually AND together** - Validate both isolation and integration
3. ✅ **Use real infrastructure** - Catch actual issues, not mock issues
4. ✅ **Integration testing between layers** - Verify layers work together as we build up
5. ✅ **E2E testing only after all layers pass** - Final validation of complete system

---

## 📊 TEST LAYER STRUCTURE

```
Layer 0:  Platform Startup
Layer 1:  DI Foundation
Layer 2:  Public Works Foundation
  ├─ 2.1: Adapters
  ├─ 2.2: Composition Services
  └─ 2.3: Abstractions
Layer 3:  Curator Foundation
Layer 4:  Communication Foundation
Layer 5:  Agentic Foundation
Layer 6:  Experience Foundation
Layer 7:  Smart City Realm
Layer 8:  Business Enablement Realm
Layer 9:  Journey Realm
Layer 10: Solution Realm
Layer 11: Cross-Layer Integration Testing
Layer 12: End-to-End Testing
```

---

## 🔄 TEST EXECUTION FLOW

### **Phase 0: Test Environment Setup**

**Goal:** Prepare test infrastructure and fixtures

**Tasks:**
1. ✅ Update `conftest.py` with new fixtures (`user_context`, utility mocks, etc.)
2. ✅ Create realm-specific conftest files
3. ✅ Update test helpers (Phase 2 registration verification, etc.)
4. ✅ Set up real infrastructure (Docker Compose for Redis, ArangoDB, Meilisearch, etc.)
5. ✅ Verify fixtures work with existing tests

**Success Criteria:**
- All fixtures available
- Real infrastructure accessible
- Test helpers functional

---

### **Layer 0: Platform Startup Tests** 🔴 **CRITICAL - TEST FIRST**

**Goal:** Verify platform actually starts and initializes correctly.

**Files:**
- `tests/integration/layer_0_startup/test_platform_startup.py`
- `tests/integration/layer_0_startup/test_foundation_initialization.py`

**Component Tests (Individual Components):**
1. ✅ Platform startup script works (`startup.sh`, `main.py`)
2. ✅ DI Container initializes correctly
3. ✅ Configuration loading works
4. ✅ Logging system initializes
5. ✅ Error handling during startup (graceful failures)

**Integration Tests (Components Working Together):**
1. ✅ All foundations initialize in correct order
2. ✅ Platform Gateway initializes
3. ✅ API routers register successfully
4. ✅ Health checks work after startup
5. ✅ Platform shuts down gracefully

**Updates Needed:**
- Add `user_context` support to startup tests
- Verify utility services are initialized
- Verify Phase 2 Curator registration during startup

**Success Criteria:**
- Platform starts without errors
- All foundations accessible
- Health endpoints respond
- Can shutdown cleanly

**MUST PASS BEFORE PROCEEDING TO LAYER 1**

---

### **Layer 1: DI Foundation Tests** 🔴 **CRITICAL - TEST SECOND**

**Goal:** Verify DI Container actually enables platform dependencies.

**Files:**
- `tests/integration/layer_1_di_container/test_di_container_functionality.py`
- `tests/integration/layer_1_di_container/test_service_registration.py`
- `tests/integration/layer_1_di_container/test_service_retrieval.py`

**Component Tests (Individual Components):**
1. ✅ Service registration works (actually register services)
2. ✅ Service retrieval works (actually retrieve services)
3. ✅ Utility access works (actually get utilities)
4. ✅ Foundation service access works (`get_foundation_service`)
5. ✅ Service lifecycle works (start, stop, restart)
6. ✅ Error handling (missing services, circular dependencies)
7. ✅ Multi-tenant support works
8. ✅ Security integration works

**Integration Tests (Components Working Together):**
1. ✅ DI Container provides all utility foundations
2. ✅ Services can access dependencies via DI Container
3. ✅ Service discovery works across all registered services
4. ✅ Service lifecycle management works correctly
5. ✅ Error propagation through DI Container works

**Updates Needed:**
- Verify DI Container provides all utility foundations
- Test Phase 2 Curator registration via DI Container
- Test MCP server access via DI Container

**Success Criteria:**
- Can register and retrieve services
- Utilities accessible via DI Container
- Services can be started/stopped
- Error handling works correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 2**

---

### **Layer 2: Public Works Foundation Tests** 🟠 **HIGH PRIORITY**

**Goal:** Verify Public Works Foundation works correctly at all levels.

#### **Layer 2.1: Public Works Adapters** 🟠 **HIGH PRIORITY**

**Goal:** Verify Public Works adapters work with real infrastructure.

**Files:**
- `tests/integration/infrastructure_adapters/test_redis_adapter_real.py`
- `tests/integration/infrastructure_adapters/test_arangodb_adapter_real.py`
- `tests/integration/infrastructure_adapters/test_meilisearch_adapter_real.py`
- `tests/integration/infrastructure_adapters/test_all_adapters_initialization.py`

**Component Tests (Individual Adapters):**
1. ✅ Redis adapter works with real Redis
   - Connection works
   - `get()`, `set()`, `delete()` operations work
   - `expire()`, `ttl()` operations work
   - Redis Streams (event bus) works
   - Redis Graph operations work
2. ✅ ArangoDB adapter works with real ArangoDB
   - Connection works
   - `create_document()`, `update_document()`, `delete_document()` work
   - Graph operations work
   - Query operations work
3. ✅ Meilisearch adapter works with real Meilisearch
   - Connection works
   - `add_documents()`, `search()` work
   - Index creation and management work
4. ✅ All adapters initialize correctly
5. ✅ Adapter error handling works (connection failures, timeouts)

**Integration Tests (Adapters Working Together):**
1. ✅ All adapters work with real infrastructure simultaneously
2. ✅ Adapter connection pooling works
3. ✅ Adapter error recovery works
4. ✅ Adapter version compatibility verified (match requirements.txt)

**Success Criteria:**
- All adapters connect to real infrastructure
- All adapter operations work with real infrastructure
- Adapter versions match requirements.txt/pyproject.toml
- No mocks used (real infrastructure only)

**MUST PASS BEFORE PROCEEDING TO LAYER 2.2**

---

#### **Layer 2.2: Public Works Composition Services** 🟠 **HIGH PRIORITY**

**Goal:** Verify Public Works composition services work correctly.

**Files:**
- `tests/integration/foundations/test_public_works_composition.py`
- `tests/integration/foundations/test_document_intelligence_service.py`
- `tests/integration/foundations/test_workflow_orchestration_service.py`

**Component Tests (Individual Composition Services):**
1. ✅ Document Intelligence Service works
   - File parsing works
   - OCR works
   - Document analysis works
   - Error handling works
2. ✅ Workflow Orchestration Service works
   - Workflow definition works
   - Workflow execution works
   - Workflow state management works
   - Error handling works
3. ✅ All composition services initialize correctly
4. ✅ Composition service error handling works

**Integration Tests (Composition Services Working Together):**
1. ✅ Composition services use adapters correctly
2. ✅ Composition services expose abstractions correctly
3. ✅ Composition services integrate with Public Works Foundation
4. ✅ Composition services handle errors gracefully
5. ✅ Composition services work with real infrastructure

**Success Criteria:**
- All composition services work correctly
- Composition services use real adapters
- Composition services expose abstractions correctly
- Error handling works correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 2.3**

---

#### **Layer 2.3: Public Works Abstractions** 🟠 **HIGH PRIORITY**

**Goal:** Verify Public Works abstractions work correctly.

**Files:**
- `tests/integration/foundations/test_all_abstractions_initialization.py`
- `tests/integration/foundations/test_abstraction_exposure_registries.py`
- `tests/integration/foundations/test_smart_city_abstraction_access.py`
- `tests/integration/platform_gateway/test_realm_abstraction_access.py`

**Component Tests (Individual Abstractions):**
1. ✅ All abstractions initialize correctly
2. ✅ Abstractions use composition services correctly
3. ✅ Abstractions expose via registries correctly
4. ✅ Abstraction error handling works

**Integration Tests (Abstractions Working Together):**
1. ✅ Smart City can access abstractions directly (no Platform Gateway)
2. ✅ Other realms access abstractions via Platform Gateway only
3. ✅ Platform Gateway correctly validates realm access
4. ✅ Abstraction exposure patterns work correctly
5. ✅ All abstractions work with real infrastructure

**Success Criteria:**
- All abstractions work correctly
- Smart City has direct access to all abstractions
- Other realms access abstractions via Platform Gateway only
- Platform Gateway correctly validates realm access

**MUST PASS BEFORE PROCEEDING TO LAYER 3**

---

### **Layer 3: Curator Foundation Tests** 🟠 **HIGH PRIORITY**

**Goal:** Verify Curator Foundation works correctly for service discovery and registration.

**Files:**
- `tests/integration/foundations/test_curator_foundation.py`
- `tests/integration/foundations/test_curator_phase2_registration.py`
- `tests/integration/foundations/test_curator_service_discovery.py`

**Component Tests (Individual Components):**
1. ✅ Curator Foundation initializes correctly
2. ✅ Service registration works (Phase 2 pattern)
   - `CapabilityDefinition` structure validation
   - SOA API registration
   - MCP tool registration
   - Contract validation
3. ✅ Service discovery works
   - Service lookup by name
   - Service lookup by capability
   - Service lookup by realm
4. ✅ Service metadata management works
5. ✅ Service health tracking works
6. ✅ Error handling works

**Integration Tests (Components Working Together):**
1. ✅ Curator integrates with Public Works Foundation
2. ✅ Curator integrates with DI Container
3. ✅ Services register with Curator correctly
4. ✅ Services discover other services via Curator
5. ✅ Phase 2 registration pattern works end-to-end
6. ✅ Service discovery works across all realms

**Updates Needed:**
- Add Phase 2 Curator registration tests
- Test `CapabilityDefinition` structure
- Test service discovery patterns
- Test cross-realm service discovery

**Success Criteria:**
- Curator Foundation initializes correctly
- Services register with Curator using Phase 2 pattern
- Services discover other services via Curator
- Phase 2 registration pattern validated

**MUST PASS BEFORE PROCEEDING TO LAYER 4**

---

### **Layer 4: Communication Foundation Tests** 🟠 **HIGH PRIORITY**

**Goal:** Verify Communication Foundation works correctly for messaging and event handling.

**Files:**
- `tests/integration/foundations/test_communication_foundation.py`
- `tests/integration/foundations/test_communication_messaging.py`
- `tests/integration/foundations/test_communication_events.py`

**Component Tests (Individual Components):**
1. ✅ Communication Foundation initializes correctly
2. ✅ Message sending works
   - Point-to-point messaging
   - Broadcast messaging
   - Message routing works
3. ✅ Event publishing works
   - Event emission works
   - Event subscription works
   - Event filtering works
4. ✅ Message queue management works
5. ✅ Error handling works
6. ✅ Message persistence works (if applicable)

**Integration Tests (Components Working Together):**
1. ✅ Communication integrates with Public Works Foundation
2. ✅ Communication integrates with DI Container
3. ✅ Services can send messages via Communication Foundation
4. ✅ Services can publish/subscribe to events via Communication Foundation
5. ✅ Message routing works across services
6. ✅ Event propagation works across services

**Success Criteria:**
- Communication Foundation initializes correctly
- Services can send messages
- Services can publish/subscribe to events
- Message routing works correctly
- Event propagation works correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 5**

---

### **Layer 5: Agentic Foundation Tests** 🟠 **HIGH PRIORITY**

**Goal:** Verify Agentic Foundation works correctly for agent creation and management.

**Files:**
- `tests/integration/foundations/test_agentic_foundation.py`
- `tests/integration/foundations/test_agent_creation.py`
- `tests/integration/foundations/test_agent_registration.py`
- `tests/integration/agentic/test_agents_use_mcp_tools.py`

**Component Tests (Individual Components):**
1. ✅ Agentic Foundation initializes correctly
2. ✅ Agent creation works
   - Agent factory works
   - Agent configuration works
   - Agent capabilities set correctly
3. ✅ Agent registration works
   - Agents register with Curator
   - Agent metadata stored correctly
4. ✅ Agent discovery works
   - Agents discoverable by capability
   - Agents discoverable by realm
5. ✅ Agent lifecycle management works
6. ✅ Error handling works

**Integration Tests (Components Working Together):**
1. ✅ Agentic integrates with Public Works Foundation
2. ✅ Agentic integrates with DI Container
3. ✅ Agentic integrates with Curator Foundation
4. ✅ Agentic integrates with Communication Foundation
5. ✅ Agents can discover MCP tools via Curator
6. ✅ Agents can execute MCP tools
7. ✅ Agents use utility methods correctly

**Updates Needed:**
- Add agent creation tests
- Add agent registration tests
- Add MCP tool discovery tests
- Add MCP tool execution tests

**Success Criteria:**
- Agentic Foundation initializes correctly
- Agents can be created via factory
- Agents register with Curator
- Agents can discover and execute MCP tools
- Agents use utility methods correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 6**

---

### **Layer 6: Experience Foundation Tests** 🟠 **HIGH PRIORITY**

**Goal:** Verify Experience Foundation works correctly for user experience orchestration.

**Files:**
- `tests/integration/foundations/test_experience_foundation.py`
- `tests/integration/foundations/test_experience_orchestration.py`
- `tests/integration/foundations/test_experience_services.py`

**Component Tests (Individual Components):**
1. ✅ Experience Foundation initializes correctly
2. ✅ Experience orchestration works
   - Experience design works
   - Experience execution works
   - Experience state management works
3. ✅ Experience services work
   - Service discovery works
   - Service composition works
4. ✅ Error handling works
5. ✅ Experience analytics works

**Integration Tests (Components Working Together):**
1. ✅ Experience integrates with Public Works Foundation
2. ✅ Experience integrates with DI Container
3. ✅ Experience integrates with Curator Foundation
4. ✅ Experience integrates with Communication Foundation
5. ✅ Experience orchestrates services correctly
6. ✅ Experience uses utility methods correctly

**Success Criteria:**
- Experience Foundation initializes correctly
- Experience orchestration works
- Experience services work correctly
- Experience uses utility methods correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 7**

---

### **Layer 7: Smart City Realm Tests** 🟡 **MEDIUM PRIORITY**

**Goal:** Verify Smart City Realm services work correctly.

**Files:**
- `tests/integration/smart_city/test_smart_city_integration.py`
- `tests/integration/smart_city/test_all_services_initialization.py`
- `tests/integration/smart_city/test_smart_city_soa_apis.py`

**Component Tests (Individual Services):**
1. ✅ All Smart City services initialize correctly
   - Librarian Service
   - Conductor Service
   - Data Steward Service
   - Content Steward Service
   - Nurse Service
   - Post Office Service
   - City Manager Service
2. ✅ Smart City services use abstractions directly (no Platform Gateway)
3. ✅ Smart City services register with Curator (Phase 2)
4. ✅ Smart City services use utility methods
5. ✅ Smart City services accept `user_context` parameter

**Integration Tests (Services Working Together):**
1. ✅ Smart City services use SOA APIs from Curator
2. ✅ Smart City services use abstractions from Public Works
3. ✅ Smart City services compose correctly
4. ✅ City Manager orchestrates Smart City services
5. ✅ Smart City services use utility methods correctly
6. ✅ Smart City services validate security/tenant correctly

**Updates Needed:**
- Add Phase 2 Curator registration tests
- Add `user_context` parameter tests
- Add utility method usage tests
- Add security/tenant validation tests

**Success Criteria:**
- All Smart City services initialize correctly
- Smart City services use abstractions directly
- Smart City services register with Curator (Phase 2)
- Smart City services use utility methods correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 8**

---

### **Layer 8: Business Enablement Realm Tests** 🟡 **MEDIUM PRIORITY**

**Goal:** Verify Business Enablement Realm services work correctly.

**Files:**
- `tests/integration/business_enablement/test_enabling_services_utility_and_functionality.py`
- `tests/integration/business_enablement/test_enabling_services_functional.py`
- `tests/integration/orchestrators/test_content_analysis_orchestrator.py`
- `tests/integration/orchestrators/test_insights_orchestrator.py`
- `tests/integration/orchestrators/test_operations_orchestrator.py`
- `tests/integration/managers/test_delivery_manager.py`
- `tests/integration/business_enablement/test_mcp_servers_functional.py`

**Component Tests (Individual Components):**
1. ✅ All enabling services initialize correctly
   - All 22 enabling services
   - Services use SOA APIs from Curator
   - Services use abstractions from Platform Gateway
2. ✅ All orchestrators initialize correctly
   - Content Analysis Orchestrator
   - Insights Orchestrator
   - Operations Orchestrator
   - Business Outcomes Orchestrator
3. ✅ Delivery Manager initializes correctly
4. ✅ All agents initialize correctly (18 agents)
5. ✅ MCP servers initialize correctly
   - Delivery Manager MCP Server
6. ✅ All services use `user_context` parameter
7. ✅ All services use utility methods
8. ✅ All services use Phase 2 Curator registration

**Integration Tests (Components Working Together):**
1. ✅ Enabling services compose correctly
2. ✅ Orchestrators compose enabling services correctly
3. ✅ Delivery Manager orchestrates orchestrators correctly
4. ✅ Agents use MCP tools correctly
5. ✅ MCP servers expose tools correctly
6. ✅ Services use SOA APIs from Curator
7. ✅ Services use abstractions from Platform Gateway
8. ✅ Services validate security/tenant correctly

**Updates Needed:**
- Add `user_context` to all test method calls
- Verify Phase 2 Curator registration
- Verify utility method usage
- Add security/tenant validation tests
- Add MCP server tests

**Success Criteria:**
- All Business Enablement services initialize correctly
- Services compose correctly using SOA APIs and abstractions
- Services use utility methods correctly
- Services validate security/tenant correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 9**

---

### **Layer 9: Journey Realm Tests** 🟡 **MEDIUM PRIORITY**

**Goal:** Verify Journey Realm services work correctly.

**Files:**
- `tests/integration/journey/test_journey_realm_refactoring.py`
- `tests/integration/journey/test_journey_services.py`
- `tests/integration/journey/test_journey_manager.py`

**Component Tests (Individual Components):**
1. ✅ All Journey services initialize correctly
   - Journey Analytics Service
   - Journey Milestone Tracker Service
   - Structured Journey Orchestrator Service
   - Session Journey Orchestrator Service
   - MVP Journey Orchestrator Service
   - Journey Manager Service
2. ✅ Journey Manager MCP Server initializes correctly
3. ✅ All services use `user_context` parameter
4. ✅ All services use utility methods
5. ✅ All services use Phase 2 Curator registration

**Integration Tests (Components Working Together):**
1. ✅ Journey services use SOA APIs from Curator
2. ✅ Journey services use abstractions from Platform Gateway
3. ✅ Journey services compose correctly
4. ✅ Journey Manager orchestrates Journey services correctly
5. ✅ Journey Manager MCP Server exposes tools correctly
6. ✅ Journey services validate security/tenant correctly

**Success Criteria:**
- All Journey services initialize correctly
- Journey services compose correctly using SOA APIs and abstractions
- Journey services use utility methods correctly
- Journey services validate security/tenant correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 10**

---

### **Layer 10: Solution Realm Tests** 🟡 **MEDIUM PRIORITY**

**Goal:** Verify Solution Realm services work correctly.

**Files:**
- `tests/integration/solution/test_solution_realm_refactoring.py`
- `tests/integration/solution/test_solution_services.py`
- `tests/integration/solution/test_solution_manager.py`

**Component Tests (Individual Components):**
1. ✅ All Solution services initialize correctly
   - Solution Composer Service
   - Solution Analytics Service
   - Solution Deployment Manager Service
   - Solution Manager Service
2. ✅ Solution Manager MCP Server initializes correctly
3. ✅ All services use `user_context` parameter
4. ✅ All services use utility methods
5. ✅ All services use Phase 2 Curator registration

**Integration Tests (Components Working Together):**
1. ✅ Solution services use SOA APIs from Curator
2. ✅ Solution services use abstractions from Platform Gateway
3. ✅ Solution services compose correctly
4. ✅ Solution Manager orchestrates Solution services correctly
5. ✅ Solution Manager MCP Server exposes tools correctly
6. ✅ Solution services validate security/tenant correctly

**Success Criteria:**
- All Solution services initialize correctly
- Solution services compose correctly using SOA APIs and abstractions
- Solution services use utility methods correctly
- Solution services validate security/tenant correctly

**MUST PASS BEFORE PROCEEDING TO LAYER 11**

---

### **Layer 11: Cross-Layer Integration Testing** 🟡 **MEDIUM PRIORITY**

**Goal:** Verify layers work together correctly across the entire stack.

**Files:**
- `tests/integration/cross_realm/test_solution_to_journey.py`
- `tests/integration/cross_realm/test_solution_to_journey_comprehensive.py`
- `tests/integration/test_manager_top_down_flow.py`
- `tests/integration/cross_layer/test_foundation_integration.py`

**Integration Tests (Cross-Layer):**
1. ✅ Solution → Journey → Experience top-down flow
2. ✅ `user_context` propagates through layers
3. ✅ Utility methods propagate through layers
4. ✅ Security/tenant validation at each layer
5. ✅ MCP tools work across realms
6. ✅ Service discovery works across realms
7. ✅ Message/event propagation works across layers
8. ✅ Agent discovery and execution works across realms

**Success Criteria:**
- Cross-layer flows work correctly
- `user_context` propagates correctly
- Utility methods propagate correctly
- Security/tenant validation works at each layer

**MUST PASS BEFORE PROCEEDING TO LAYER 12**

---

### **Layer 12: End-to-End Testing** 🟢 **FINAL VALIDATION**

**Goal:** Verify complete system works end-to-end.

**Files:**
- `tests/e2e/test_complete_platform_e2e.py`
- `tests/e2e/test_mvp_user_journey_e2e.py`
- `tests/e2e/test_cto_demo_scenarios.py`

**E2E Test Scenarios:**
1. ✅ Complete platform startup and initialization
2. ✅ User journey from Solution → Journey → Experience
3. ✅ Agent execution with MCP tools
4. ✅ Service orchestration across all realms
5. ✅ Error handling and recovery
6. ✅ Performance and scalability
7. ✅ Security and multi-tenancy

**Success Criteria:**
- Complete system works end-to-end
- All user journeys work
- All error scenarios handled gracefully
- Performance meets requirements

---

## ✅ SUCCESS CRITERIA SUMMARY

### **Test Environment:**
- [ ] All fixtures provide `user_context` by default
- [ ] All utility services are properly mocked
- [ ] Phase 2 registration can be verified
- [ ] MCP servers can be tested
- [ ] Real infrastructure available for testing

### **Layer-by-Layer Testing:**
- [ ] Layer 0: Platform Startup passes
- [ ] Layer 1: DI Foundation passes
- [ ] Layer 2: Public Works Foundation passes (all sub-layers)
- [ ] Layer 3: Curator Foundation passes
- [ ] Layer 4: Communication Foundation passes
- [ ] Layer 5: Agentic Foundation passes
- [ ] Layer 6: Experience Foundation passes
- [ ] Layer 7: Smart City Realm passes
- [ ] Layer 8: Business Enablement Realm passes
- [ ] Layer 9: Journey Realm passes
- [ ] Layer 10: Solution Realm passes
- [ ] Layer 11: Cross-Layer Integration passes
- [ ] Layer 12: E2E Testing passes

### **Architectural Compliance:**
- [ ] All services use `user_context` parameter
- [ ] All services use utility methods
- [ ] All services use Phase 2 registration
- [ ] All MCP servers tested
- [ ] Security/tenant validation tested

---

## 🚀 QUICK START GUIDE

### **1. Set Up Test Environment**
```bash
cd /home/founders/demoversion/symphainy_source/tests
# Update conftest.py with new fixtures
# Set up real infrastructure (Docker Compose)
```

### **2. Run Tests Layer by Layer**
```bash
# Layer 0: Platform Startup
pytest tests/integration/layer_0_startup/ -v

# Layer 1: DI Foundation
pytest tests/integration/layer_1_di_container/ -v

# Layer 2: Public Works Foundation
pytest tests/integration/infrastructure_adapters/ -v  # 2.1
pytest tests/integration/foundations/test_public_works_composition.py -v  # 2.2
pytest tests/integration/foundations/test_all_abstractions_initialization.py -v  # 2.3

# Layer 3: Curator Foundation
pytest tests/integration/foundations/test_curator_foundation.py -v

# Continue for each layer...
```

### **3. Run Integration Tests**
```bash
# Cross-layer integration
pytest tests/integration/cross_layer/ -v

# Cross-realm integration
pytest tests/integration/cross_realm/ -v
```

### **4. Run E2E Tests**
```bash
# End-to-end tests
pytest tests/e2e/ -v
```

---

**Ready for implementation!** 🚀

