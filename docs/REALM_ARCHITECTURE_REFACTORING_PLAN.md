# Realm Architecture Refactoring Plan

**Date:** January 15, 2025  
**Status:** 🎯 **REFACTORING PLAN**  
**Goal:** Separate MVP pillars into distinct realms, keep Business Enablement as shared services

---

## 🎯 Executive Summary

**Current State:**
- All MVP capabilities in `business_enablement` realm
- 1 DeliveryManagerService managing 4 orchestrators
- ~25 enabling services shared across pillars
- ~15+ agents per pillar

**Target State:**
- **Content Realm** - Data Ingestion & Transformation
- **Insights Realm** - Data Analysis
- **Journey Realm** - User Journey Development, Execution, and Orchestration (Operations)
- **Solution Realm** - Solution development, execution, and orchestration (Business Outcomes)
- **Business Enablement Realm** - Shared enabling services (like Smart City, not exposed)

**Key Insight:** Business Enablement becomes a **shared services realm** (like Smart City) that provides enabling services discoverable via Curator, but is not directly exposed to users.

---

## 🏗️ Target Architecture

### **New Realm Structure:**

```
content/ (new realm)
├── ContentManagerService (new manager)
├── orchestrators/
│   └── ContentAnalysisOrchestrator (moved from business_enablement)
├── agents/
│   ├── ContentLiaisonAgent (moved)
│   ├── ContentQueryAgent (moved)
│   └── ContentSpecialistAgent (moved)
└── mcp_server/
    └── content_mcp_server (moved)

insights/ (new realm)
├── InsightsManagerService (new manager)
├── orchestrators/
│   └── InsightsOrchestrator (moved from business_enablement)
├── agents/
│   ├── InsightsLiaisonAgent (moved)
│   ├── InsightsQueryAgent (moved)
│   └── InsightsBusinessAnalysisAgent (moved)
└── mcp_server/
    └── insights_mcp_server (moved)

journey/ (existing realm - add Operations)
├── JourneyManagerService (existing)
├── orchestrators/
│   ├── ... (existing journey orchestrators)
│   └── OperationsOrchestrator (NEW - build here)
├── agents/
│   ├── ... (existing journey agents)
│   └── OperationsLiaisonAgent (NEW)
└── mcp_server/
    └── operations_mcp_server (NEW)

solution/ (existing realm - add Business Outcomes)
├── SolutionManagerService (existing)
├── orchestrators/
│   ├── ... (existing solution orchestrators)
│   └── BusinessOutcomesOrchestrator (NEW - build here)
├── agents/
│   ├── ... (existing solution agents)
│   └── BusinessOutcomesLiaisonAgent (NEW)
└── mcp_server/
    └── business_outcomes_mcp_server (NEW)

business_enablement/ (refactored - shared services only)
├── NO Manager Service (not exposed, like Smart City)
├── enabling_services/ (~25 services - ALL stay here)
│   ├── file_parser_service
│   ├── data_analyzer_service
│   ├── semantic_enrichment_gateway
│   └── ... (all 25 services)
└── NO orchestrators (moved to content/insights)
└── NO agents (moved to content/insights)
```

---

## 📋 Refactoring Phases

### **Phase 1: Create Content Realm** (Week 1)

#### **1.1 Create Realm Structure**
```bash
backend/content/
├── __init__.py
├── ContentManagerService/
│   ├── content_manager_service.py
│   ├── modules/
│   │   ├── initialization.py
│   │   ├── utilities.py
│   │   └── soa_mcp.py
│   └── __init__.py
├── orchestrators/
│   └── content_orchestrator/
│       └── content_analysis_orchestrator.py
├── agents/
│   ├── content_liaison_agent.py
│   ├── content_query_agent.py
│   └── content_specialist_agent.py
└── mcp_server/
    └── content_mcp_server.py
```

#### **1.2 Move Content Orchestrator**
- **From:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_orchestrator/`
- **To:** `backend/content/orchestrators/content_orchestrator/`
- **Changes:**
  - Update `realm_name="business_enablement"` → `realm_name="content"`
  - Update imports
  - Update Curator registration
  - Update manager reference (ContentManagerService instead of DeliveryManagerService)

#### **1.3 Move Content Agents**
- **From:** `backend/business_enablement/agents/`
- **To:** `backend/content/agents/`
- **Changes:**
  - Update `realm_name="business_enablement"` → `realm_name="content"`
  - Update orchestrator reference
  - Update imports

#### **1.4 Create Content Manager Service**
- **Pattern:** Follow JourneyManagerService / SolutionManagerService pattern
- **Responsibilities:**
  - Orchestrate Content realm startup
  - Discover Content Orchestrator via Curator
  - Provide SOA APIs for Content capabilities
  - Register with Curator

#### **1.5 Move Content MCP Server**
- **From:** `backend/business_enablement/delivery_manager/mcp_server/`
- **To:** `backend/content/mcp_server/`
- **Changes:**
  - Update service references
  - Update imports

#### **1.6 Update Enabling Service Discovery**
- Content Orchestrator discovers enabling services via Curator
- Pattern: `await self.get_enabling_service("file_parser_service")`
- Similar to how orchestrators discover Smart City services

---

### **Phase 2: Create Insights Realm** (Week 1-2)

#### **2.1 Create Realm Structure**
```bash
backend/insights/
├── __init__.py
├── InsightsManagerService/
│   ├── insights_manager_service.py
│   ├── modules/
│   │   ├── initialization.py
│   │   ├── utilities.py
│   │   └── soa_mcp.py
│   └── __init__.py
├── orchestrators/
│   └── insights_orchestrator/
│       └── insights_orchestrator.py
├── agents/
│   ├── insights_liaison_agent.py
│   ├── insights_query_agent.py
│   └── insights_business_analysis_agent.py
└── mcp_server/
    └── insights_mcp_server.py
```

#### **2.2 Move Insights Orchestrator**
- **From:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/`
- **To:** `backend/insights/orchestrators/insights_orchestrator/`
- **Changes:**
  - Update `realm_name="business_enablement"` → `realm_name="insights"`
  - Update imports
  - Update Curator registration
  - Update manager reference (InsightsManagerService instead of DeliveryManagerService)

#### **2.3 Move Insights Agents**
- **From:** `backend/business_enablement/agents/`
- **To:** `backend/insights/agents/`
- **Changes:**
  - Update `realm_name="business_enablement"` → `realm_name="insights"`
  - Update orchestrator reference
  - Update imports

#### **2.4 Create Insights Manager Service**
- **Pattern:** Follow ContentManagerService pattern
- **Responsibilities:**
  - Orchestrate Insights realm startup
  - Discover Insights Orchestrator via Curator
  - Provide SOA APIs for Insights capabilities
  - Register with Curator

#### **2.5 Move Insights MCP Server**
- **From:** `backend/business_enablement/delivery_manager/mcp_server/`
- **To:** `backend/insights/mcp_server/`
- **Changes:**
  - Update service references
  - Update imports

---

### **Phase 3: Build Operations in Journey Realm** (Week 2)

#### **3.1 Add Operations Orchestrator to Journey Realm**
```bash
backend/journey/orchestrators/
└── operations_orchestrator/
    └── operations_orchestrator.py
```

#### **3.2 Create Operations Orchestrator**
- **Pattern:** Follow InsightsOrchestrator pattern
- **Realm:** `journey` (not `business_enablement`)
- **Manager:** JourneyManagerService (existing)
- **Responsibilities:**
  - User Journey Development
  - Journey Execution
  - Journey Orchestration

#### **3.3 Create Operations Agents**
- **Location:** `backend/journey/agents/`
- **Agents:**
  - OperationsLiaisonAgent
  - OperationsQueryAgent
  - OperationsSpecialistAgent

#### **3.4 Create Operations MCP Server**
- **Location:** `backend/journey/mcp_server/`
- **Pattern:** Follow insights_mcp_server pattern

#### **3.5 Update Journey Manager**
- Add Operations Orchestrator discovery
- Add Operations capabilities to Journey Manager SOA APIs

---

### **Phase 4: Build Business Outcomes in Solution Realm** (Week 2-3)

#### **4.1 Add Business Outcomes Orchestrator to Solution Realm**
```bash
backend/solution/orchestrators/
└── business_outcomes_orchestrator/
    └── business_outcomes_orchestrator.py
```

#### **4.2 Create Business Outcomes Orchestrator**
- **Pattern:** Follow InsightsOrchestrator pattern
- **Realm:** `solution` (not `business_enablement`)
- **Manager:** SolutionManagerService (existing)
- **Responsibilities:**
  - Solution development
  - Solution execution
  - Solution orchestration
  - Creation and delivery of business outcomes/deliverables

#### **4.3 Create Business Outcomes Agents**
- **Location:** `backend/solution/agents/`
- **Agents:**
  - BusinessOutcomesLiaisonAgent
  - BusinessOutcomesQueryAgent
  - BusinessOutcomesSpecialistAgent

#### **4.4 Create Business Outcomes MCP Server**
- **Location:** `backend/solution/mcp_server/`
- **Pattern:** Follow insights_mcp_server pattern

#### **4.5 Update Solution Manager**
- Add Business Outcomes Orchestrator discovery
- Add Business Outcomes capabilities to Solution Manager SOA APIs

---

### **Phase 5: Refactor Business Enablement to Shared Services** (Week 3)

#### **5.1 Remove Delivery Manager Service**
- **Action:** Delete `DeliveryManagerService`
- **Reason:** No longer needed - each realm has its own manager
- **Alternative:** Keep as legacy coordinator if needed for transition

#### **5.2 Keep All Enabling Services**
- **Location:** `backend/business_enablement/enabling_services/`
- **All 25 services stay here:**
  - file_parser_service
  - data_analyzer_service
  - semantic_enrichment_gateway
  - visualization_engine_service
  - ... (all 25 services)

#### **5.3 Make Enabling Services Discoverable**
- **Pattern:** Similar to Smart City services
- **Discovery Method:** `await self.get_enabling_service("file_parser_service")`
- **Implementation:** Add to `PlatformCapabilitiesMixin`:
  ```python
  async def get_enabling_service(self, service_name: str) -> Optional[Any]:
      """Get Business Enablement enabling service via Curator discovery."""
      # Similar to get_smart_city_api()
      curator = self.get_curator()
      if not curator:
          return None
      
      # Discover via Curator
      service = await curator.discover_service_by_name(f"{service_name}Service")
      return service
  ```

#### **5.4 Update Enabling Service Registration**
- **Ensure:** All enabling services register with Curator
- **Realm:** `business_enablement`
- **Pattern:** Same as current (Phase 2 Curator registration)

#### **5.5 Remove Orchestrators and Agents**
- **Action:** Delete moved orchestrators and agents
- **Verify:** All references updated before deletion

---

## 🔧 Technical Implementation Details

### **1. Realm Name Updates**

**Pattern to Update:**
```python
# OLD
realm_name="business_enablement"

# NEW (Content)
realm_name="content"

# NEW (Insights)
realm_name="insights"

# NEW (Journey - Operations)
realm_name="journey"

# NEW (Solution - Business Outcomes)
realm_name="solution"
```

**Files to Update:**
- All orchestrator `__init__` methods
- All agent `__init__` methods
- All service initialization
- All Curator registrations

---

### **2. Manager Service Pattern**

**Content Manager Service Example:**
```python
class ContentManagerService(ManagerServiceBase, ManagerServiceProtocol):
    """Content Manager Service - Orchestrates Content realm."""
    
    def __init__(self, di_container: Any, platform_gateway: Any = None):
        super().__init__(
            service_name="ContentManagerService",
            realm_name="content",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        self.manager_type = ManagerServiceType.CONTENT_MANAGER
        self.orchestration_scope = OrchestrationScope.DOMAIN_SPECIFIC
        self.governance_level = GovernanceLevel.MODERATE
    
    async def get_content_orchestrator(self):
        """Discover Content Orchestrator via Curator."""
        curator = self.get_curator()
        if not curator:
            return None
        
        orchestrator = await curator.discover_service_by_name("ContentAnalysisOrchestrator")
        return orchestrator
```

---

### **3. Enabling Service Discovery Pattern**

**Add to PlatformCapabilitiesMixin:**
```python
async def get_enabling_service(self, service_name: str) -> Optional[Any]:
    """
    Get Business Enablement enabling service via Curator discovery.
    
    Similar to get_smart_city_api(), but for business_enablement realm services.
    """
    # Check cache first
    cache_key = f"enabling_{service_name}"
    if cache_key in self._service_cache:
        return self._service_cache[cache_key]
    
    # Get Curator
    curator = self.get_curator()
    if not curator:
        self.logger.warning(f"⚠️ Curator not available - cannot discover {service_name}")
        return None
    
    # Discover service
    service_variants = [
        service_name,
        f"{service_name}Service",
        service_name.replace("_", "").title() + "Service"
    ]
    
    for variant in service_variants:
        service = await curator.discover_service_by_name(variant)
        if service:
            self._service_cache[cache_key] = service
            return service
    
    return None
```

**Usage in Orchestrators:**
```python
# In ContentAnalysisOrchestrator
async def parse_file(self, file_path: str):
    """Parse file using enabling service."""
    # Discover enabling service
    file_parser = await self.get_enabling_service("file_parser_service")
    if not file_parser:
        raise Exception("File parser service not available")
    
    # Use service
    result = await file_parser.parse_file(file_path=file_path)
    return result
```

---

### **4. Startup Orchestration Updates**

**Update main.py or startup orchestrator:**
```python
# OLD
delivery_manager = DeliveryManagerService(...)
await delivery_manager.initialize()
await delivery_manager.orchestrate_realm_startup()

# NEW
# Start Content Realm
content_manager = ContentManagerService(...)
await content_manager.initialize()
await content_manager.orchestrate_realm_startup()

# Start Insights Realm
insights_manager = InsightsManagerService(...)
await insights_manager.initialize()
await insights_manager.orchestrate_realm_startup()

# Start Journey Realm (includes Operations)
journey_manager = JourneyManagerService(...)
await journey_manager.initialize()
await journey_manager.orchestrate_realm_startup()

# Start Solution Realm (includes Business Outcomes)
solution_manager = SolutionManagerService(...)
await solution_manager.initialize()
await solution_manager.orchestrate_realm_startup()
```

---

### **5. Curator Registration Updates**

**Enabling Services (stay in business_enablement):**
```python
# In file_parser_service
await self.register_with_curator(
    capabilities=["file_parsing", "format_detection"],
    soa_apis=["parse_file", "detect_file_type"],
    mcp_tools=["parse_file_tool", "detect_file_type_tool"],
    realm_name="business_enablement"  # Stay in business_enablement
)
```

**Orchestrators (move to new realms):**
```python
# In ContentAnalysisOrchestrator
await self.register_with_curator(
    capabilities=["content_analysis", "document_processing"],
    soa_apis=["analyze_content", "process_document"],
    realm_name="content"  # New realm
)
```

---

## 📊 Migration Checklist

### **Content Realm Migration:**
- [ ] Create `backend/content/` directory structure
- [ ] Create `ContentManagerService`
- [ ] Move `ContentAnalysisOrchestrator` to `backend/content/orchestrators/`
- [ ] Update orchestrator `realm_name` to `"content"`
- [ ] Move Content agents to `backend/content/agents/`
- [ ] Update agent `realm_name` to `"content"`
- [ ] Move Content MCP server to `backend/content/mcp_server/`
- [ ] Update all imports
- [ ] Update Curator registrations
- [ ] Update enabling service discovery calls
- [ ] Test Content realm startup
- [ ] Test Content orchestrator functionality
- [ ] Test Content agent functionality

### **Insights Realm Migration:**
- [ ] Create `backend/insights/` directory structure
- [ ] Create `InsightsManagerService`
- [ ] Move `InsightsOrchestrator` to `backend/insights/orchestrators/`
- [ ] Update orchestrator `realm_name` to `"insights"`
- [ ] Move Insights agents to `backend/insights/agents/`
- [ ] Update agent `realm_name` to `"insights"`
- [ ] Move Insights MCP server to `backend/insights/mcp_server/`
- [ ] Update all imports
- [ ] Update Curator registrations
- [ ] Update enabling service discovery calls
- [ ] Test Insights realm startup
- [ ] Test Insights orchestrator functionality
- [ ] Test Insights agent functionality

### **Operations in Journey Realm:**
- [ ] Create `OperationsOrchestrator` in `backend/journey/orchestrators/`
- [ ] Set `realm_name="journey"`
- [ ] Create Operations agents in `backend/journey/agents/`
- [ ] Create Operations MCP server
- [ ] Update Journey Manager to discover Operations Orchestrator
- [ ] Test Operations functionality

### **Business Outcomes in Solution Realm:**
- [ ] Create `BusinessOutcomesOrchestrator` in `backend/solution/orchestrators/`
- [ ] Set `realm_name="solution"`
- [ ] Create Business Outcomes agents in `backend/solution/agents/`
- [ ] Create Business Outcomes MCP server
- [ ] Update Solution Manager to discover Business Outcomes Orchestrator
- [ ] Test Business Outcomes functionality

### **Business Enablement Refactoring:**
- [ ] Remove DeliveryManagerService (or keep as legacy coordinator)
- [ ] Verify all enabling services stay in `business_enablement`
- [ ] Add `get_enabling_service()` to `PlatformCapabilitiesMixin`
- [ ] Update all enabling service Curator registrations
- [ ] Remove moved orchestrators from `business_enablement`
- [ ] Remove moved agents from `business_enablement`
- [ ] Test enabling service discovery from other realms
- [ ] Update documentation

---

## 🎯 Success Criteria

**Refactoring is complete when:**
- ✅ Content realm is independent and functional
- ✅ Insights realm is independent and functional
- ✅ Operations is built in Journey realm
- ✅ Business Outcomes is built in Solution realm
- ✅ Business Enablement is a shared services realm (like Smart City)
- ✅ All enabling services are discoverable via Curator
- ✅ All orchestrators can discover enabling services
- ✅ All tests pass
- ✅ All imports updated
- ✅ All Curator registrations updated
- ✅ Startup orchestration works correctly

---

## 📝 Notes

1. **Business Enablement as Shared Services:**
   - Similar to Smart City - provides services but not directly exposed
   - Discoverable via Curator
   - No manager service needed (or minimal coordinator)

2. **Timing:**
   - Now is the perfect time (only 2 of 4 pillars complete)
   - Easier to move 2 than extract 4 later
   - Build remaining 2 in proper homes

3. **Frontend Alignment:**
   - Operations = Journey (rename in frontend)
   - Business Outcomes = Solution (rename in frontend)

4. **Shared Services:**
   - All ~25 enabling services stay in `business_enablement`
   - Discoverable via `get_enabling_service()`
   - Pattern similar to `get_smart_city_api()`

---

**Status:** ✅ **REFACTORING PLAN COMPLETE - READY FOR IMPLEMENTATION**

