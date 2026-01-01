# 🚀 Business Enablement Realm: Implementation Guide

**Date:** November 4, 2024  
**Strategy:** Hybrid Approach (Enabling Services + MVP Use Case Orchestrators)  
**Timeline:** Week 7-8 (1.5-2.5 weeks)  
**Key Principle:** Clean file names, archive old versions, zero parallel implementations

---

## 📋 FILE NAMING & ARCHIVING RULES

### **✅ CORRECT FILE NAMING**

```python
# ✅ GOOD: Clean, final names
file_parser_service.py
data_analyzer_service.py
content_analysis_orchestrator.py

# ❌ BAD: Temporary or versioned names
file_parser_service_new.py
file_parser_service_updated.py
file_parser_service_refactored.py
file_parser_service_v2.py
```

### **📦 ARCHIVING STRATEGY**

**Before creating new service:**
1. Move old implementation to `archive/` with timestamp
2. Create new service with clean name
3. Verify no imports reference archived code

**Example:**
```bash
# Step 1: Archive old pillar
mv backend/business_enablement/pillars/content_analysis/content_analysis_pillar.py \
   backend/business_enablement/archive/2024-11-04_content_analysis_pillar.py

# Step 2: Create new orchestrator with clean name
touch backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator.py

# Step 3: Verify no imports reference archived file
grep -r "from.*content_analysis_pillar" backend/
```

---

## 🏗️ TARGET ARCHITECTURE

```
backend/business_enablement/
├── archive/                             # All old code goes here
│   └── 2024-11-04_[old_file_name].py
│
├── enabling_services/                   # NEW: Atomic capability services
│   ├── file_parser_service/
│   │   ├── file_parser_service.py      # CLEAN NAME (no suffixes!)
│   │   ├── mcp_server/
│   │   │   └── file_parser_mcp_server.py
│   │   └── modules/
│   │       ├── initialization.py
│   │       ├── parsing.py
│   │       ├── format_detection.py
│   │       ├── soa_apis.py
│   │       └── mcp_tools.py
│   │
│   ├── data_analyzer_service/
│   ├── metrics_calculator_service/
│   ├── validation_engine_service/
│   ├── transformation_engine_service/
│   ├── schema_mapper_service/
│   ├── data_compositor_service/
│   └── ... (15-20 total)
│
└── business_orchestrator/               # NEW: Orchestration layer
    ├── business_orchestrator_service.py # Main orchestrator (CLEAN NAME!)
    ├── mcp_server/
    │   └── business_orchestrator_mcp_server.py
    │
    └── use_cases/                       # Use case orchestrators
        ├── mvp/
        │   ├── content_analysis_orchestrator.py    # Refactored from ContentAnalysisPillar
        │   ├── data_operations_orchestrator.py     # Refactored from DataOperationsPillar
        │   ├── insights_orchestrator.py            # Refactored from InsightsPillar
        │   └── operations_orchestrator.py          # Refactored from OperationsPillar
        │
        └── data_mash/                   # FUTURE
            └── data_mash_orchestrator.py
```

---

## 📝 IMPLEMENTATION CHECKLIST

### **PHASE 1: Setup & Planning (1-2 hours)**

```bash
☐ Create directory structure
  mkdir -p backend/business_enablement/enabling_services
  mkdir -p backend/business_enablement/business_orchestrator/use_cases/mvp
  mkdir -p backend/business_enablement/business_orchestrator/use_cases/data_mash
  mkdir -p backend/business_enablement/archive

☐ Create .gitkeep files for empty directories

☐ Review current pillar micro-modules
  # Identify which micro-modules become enabling services
  # Map pillar orchestration logic to use case orchestrators
```

---

### **PHASE 2: Create Enabling Services (30-60 hours)**

**For Each Micro-Module → Enabling Service:**

#### **Step 1: Archive Old Micro-Module**
```bash
☐ Move to archive with timestamp
  mv backend/business_enablement/pillars/[pillar]/modules/[module].py \
     backend/business_enablement/archive/2024-11-04_[module].py
```

#### **Step 2: Create New Service Directory**
```bash
☐ Create service structure
  mkdir -p backend/business_enablement/enabling_services/[service_name]_service
  mkdir -p backend/business_enablement/enabling_services/[service_name]_service/modules
  mkdir -p backend/business_enablement/enabling_services/[service_name]_service/mcp_server
```

#### **Step 3: Create Service File (Clean Name!)**
```python
☐ Create [service_name]_service.py (NO SUFFIXES!)

# Template:
"""
[Service Name] Service

WHAT: [Service capability description]
HOW: [How it provides the capability]
"""

from bases.realm_service_base import RealmServiceBase
from typing import Dict, Any, List, Optional

class [ServiceName]Service(RealmServiceBase):
    """[Service Name] enabling service for business enablement."""
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.file_management = None
        self.librarian = None
        # ... (infrastructure and Smart City services)
    
    async def initialize(self) -> bool:
        """Initialize service."""
        await super().initialize()
        
        # 1. Get infrastructure abstractions (via Platform Gateway)
        self.file_management = self.get_abstraction("file_management")
        # ... (other abstractions)
        
        # 2. Discover Smart City services (via Curator)
        self.librarian = await self.get_librarian_api()
        self.content_steward = await self.get_content_steward_api()
        self.data_steward = await self.get_data_steward_api()
        
        # 3. Register with Curator (one line!)
        await self.register_with_curator(
            capabilities=["[capability1]", "[capability2]"],
            soa_apis=["[api1]", "[api2]"],
            mcp_tools=["[tool1]", "[tool2]"]
        )
        
        self.logger.info(f"✅ {self.service_name} initialized")
        return True
    
    # ========================================================================
    # SOA APIs (3-5 core capabilities)
    # ========================================================================
    
    async def [core_capability_1](self, params) -> Dict[str, Any]:
        """[Capability description] (SOA API)."""
        # Use Smart City services via helpers
        result = await self.validate_data_quality(params, rules)
        storage = await self.store_document(result, metadata)
        await self.track_data_lineage(source, destination, transformation)
        return result
    
    async def [core_capability_2](self, params) -> Dict[str, Any]:
        """[Capability description] (SOA API)."""
        pass
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities."""
        return {
            "service_name": self.service_name,
            "capabilities": ["[capability1]", "[capability2]"],
            "soa_apis": ["[api1]", "[api2]"],
            "mcp_tools": ["[tool1]", "[tool2]"]
        }
```

#### **Step 4: Create Micro-Modules**
```bash
☐ Create modules/ (business logic)
  - initialization.py
  - [core_logic].py
  - soa_apis.py
  - mcp_tools.py
  - utilities.py
```

#### **Step 5: Create MCP Server**
```python
☐ Create mcp_server/[service_name]_mcp_server.py (CLEAN NAME!)

# Template:
from bases.mcp_server_base import MCPServerBase

class [ServiceName]MCPServer(MCPServerBase):
    """MCP Server for [Service Name] service."""
    
    def __init__(self, service: [ServiceName]Service, di_container):
        super().__init__(
            server_name="[service_name]_mcp",
            di_container=di_container,
            server_type="single_service"  # 1:1 for realm services
        )
        self.service = service
        self._register_tools()
    
    def _register_tools(self):
        """Register MCP tools."""
        self.register_tool(
            name="[tool_name]",
            description="[Tool description]",
            handler=self._[tool_name],
            input_schema={...}
        )
    
    async def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        """Execute tool by routing to service SOA API."""
        if tool_name == "[tool_name]":
            return await self.service.[soa_api_method](**parameters)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def _[tool_name](self, **kwargs) -> dict:
        """MCP tool wrapper."""
        return await self.service.[soa_api_method](**kwargs)
```

#### **Step 6: Test & Verify**
```bash
☐ Create unit tests
  tests/unit/enabling_services/test_[service_name]_service.py

☐ Create integration tests
  tests/integration/test_[service_name]_integration.py

☐ Run tests
  cd symphainy_source/tests
  python3 -m pytest unit/enabling_services/test_[service_name]_service.py -v
```

#### **Step 7: Verify Archiving**
```bash
☐ Confirm old code archived
  ls -la backend/business_enablement/archive/

☐ Verify no imports reference archived code
  grep -r "from.*[archived_module_name]" backend/

☐ Verify clean naming (no suffixes)
  find backend/business_enablement/enabling_services -name "*_new.py"
  find backend/business_enablement/enabling_services -name "*_updated.py"
  # Should return nothing!
```

---

### **ENABLING SERVICES TO CREATE (Priority Order)**

**Core Services (Week 7 - High Priority):**
1. ☐ `file_parser_service` - Parse files into structured formats
2. ☐ `data_analyzer_service` - Analyze data structure and content
3. ☐ `metrics_calculator_service` - Calculate metrics and KPIs
4. ☐ `validation_engine_service` - Validate data quality and compliance
5. ☐ `transformation_engine_service` - Transform data between formats
6. ☐ `schema_mapper_service` - Map schemas between systems

**Extended Services (Week 7-8 - Medium Priority):**
7. ☐ `data_compositor_service` - Compose virtual data views (Data Mash)
8. ☐ `workflow_manager_service` - Manage business workflows
9. ☐ `task_scheduler_service` - Schedule and execute tasks
10. ☐ `report_generator_service` - Generate reports and visualizations
11. ☐ `export_formatter_service` - Format exports for various systems
12. ☐ `reconciliation_service` - Reconcile data across systems

**Supporting Services (Week 8 - Lower Priority):**
13. ☐ `notification_service` - Business-level notifications
14. ☐ `audit_trail_service` - Business audit logging
15. ☐ `configuration_service` - Business configuration management
16. ☐ `template_service` - Template management
17. ☐ `batch_processor_service` - Batch processing orchestration
18. ☐ `cache_manager_service` - Business-level caching

---

### **PHASE 3: Create Business Orchestrator (8-12 hours)**

#### **Step 1: Archive Old Business Orchestrator (if exists)**
```bash
☐ Check if old orchestrator exists
  ls backend/business_enablement/business_orchestrator/

☐ Archive if exists
  mv backend/business_enablement/business_orchestrator/business_orchestrator.py \
     backend/business_enablement/archive/2024-11-04_old_business_orchestrator.py
```

#### **Step 2: Create Business Orchestrator Service (Clean Name!)**
```python
☐ Create business_orchestrator_service.py (NO SUFFIXES!)

"""
Business Orchestrator Service

WHAT: Orchestrates enabling services for business use cases
HOW: Composes enabling services, delegates to use case orchestrators
"""

from bases.realm_service_base import RealmServiceBase
from typing import Dict, Any, Optional

class BusinessOrchestratorService(RealmServiceBase):
    """
    Business Orchestrator - Composes enabling services for ANY use case.
    
    Delegates to use case-specific orchestrators for complex workflows.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Enabling services (discovered via Curator)
        self.file_parser_service = None
        self.data_analyzer_service = None
        self.metrics_calculator_service = None
        # ... (all enabling services)
        
        # Use case orchestrators (initialized after enabling services)
        self.mvp_orchestrators = {}
        self.data_mash_orchestrator = None
    
    async def initialize(self) -> bool:
        """Initialize Business Orchestrator."""
        await super().initialize()
        
        # 1. Discover enabling services (via Curator)
        await self._discover_enabling_services()
        
        # 2. Initialize use case orchestrators
        self._init_mvp_orchestrators()
        
        # 3. Register with Curator
        await self.register_with_curator(
            capabilities=["business_orchestration", "use_case_composition"],
            soa_apis=["execute_use_case", "compose_services"],
            mcp_tools=["execute_use_case_tool"]
        )
        
        self.logger.info("✅ Business Orchestrator initialized")
        return True
    
    async def _discover_enabling_services(self):
        """Discover all enabling services via Curator."""
        curator = self.get_curator()
        if not curator:
            self.logger.error("❌ Curator not available")
            return
        
        # Discover each enabling service
        services = await curator.get_registered_services()
        
        for service_name, service_info in services.get("services", {}).items():
            if service_info.get("realm") == "business_enablement":
                service_instance = service_info.get("service_instance")
                
                # Map to orchestrator attributes
                if "file_parser" in service_name.lower():
                    self.file_parser_service = service_instance
                elif "data_analyzer" in service_name.lower():
                    self.data_analyzer_service = service_instance
                # ... (map all enabling services)
                
                self.logger.debug(f"✅ Discovered: {service_name}")
    
    def _init_mvp_orchestrators(self):
        """Initialize MVP use case orchestrators."""
        from .use_cases.mvp.content_analysis_orchestrator import ContentAnalysisOrchestrator
        from .use_cases.mvp.data_operations_orchestrator import DataOperationsOrchestrator
        from .use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        from .use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        self.mvp_orchestrators = {
            "content_analysis": ContentAnalysisOrchestrator(self),
            "data_operations": DataOperationsOrchestrator(self),
            "insights": InsightsOrchestrator(self),
            "operations": OperationsOrchestrator(self)
        }
        
        self.logger.info("✅ MVP orchestrators initialized")
    
    # ========================================================================
    # ORCHESTRATION APIs
    # ========================================================================
    
    async def execute_use_case(self, use_case: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute use case by routing to appropriate orchestrator.
        
        Args:
            use_case: Use case name (e.g., "mvp_content_analysis", "data_mash_pipeline")
            request: Use case request parameters
        
        Returns:
            Use case execution result
        """
        # Route to MVP orchestrators
        if use_case in ["content_analysis", "mvp_content_analysis"]:
            return await self.mvp_orchestrators["content_analysis"].execute(request)
        elif use_case in ["data_operations", "mvp_data_operations"]:
            return await self.mvp_orchestrators["data_operations"].execute(request)
        elif use_case in ["insights", "mvp_insights"]:
            return await self.mvp_orchestrators["insights"].execute(request)
        elif use_case in ["operations", "mvp_operations"]:
            return await self.mvp_orchestrators["operations"].execute(request)
        
        # Future: Data Mash
        elif use_case == "data_mash_pipeline":
            if self.data_mash_orchestrator:
                return await self.data_mash_orchestrator.execute(request)
            else:
                return {"error": "Data Mash orchestrator not available"}
        
        else:
            return {"error": f"Unknown use case: {use_case}"}
    
    async def compose_services(self, service_composition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose enabling services for custom workflows.
        
        For simple use cases that don't need a dedicated orchestrator.
        """
        results = {}
        
        for step in service_composition.get("steps", []):
            service_name = step.get("service")
            action = step.get("action")
            params = step.get("params", {})
            
            # Get service instance
            service = getattr(self, f"{service_name.lower()}_service", None)
            if not service:
                results[step.get("name", service_name)] = {"error": f"Service not found: {service_name}"}
                continue
            
            # Execute action
            if hasattr(service, action):
                result = await getattr(service, action)(**params)
                results[step.get("name", service_name)] = result
            else:
                results[step.get("name", service_name)] = {"error": f"Action not found: {action}"}
        
        return results
```

#### **Step 3: Create MCP Server**
```bash
☐ Create mcp_server/business_orchestrator_mcp_server.py (CLEAN NAME!)
```

#### **Step 4: Test Business Orchestrator**
```bash
☐ Create tests
  tests/unit/business_orchestrator/test_business_orchestrator_service.py
  tests/integration/test_business_orchestrator_integration.py

☐ Run tests
  python3 -m pytest tests/unit/business_orchestrator/ -v
```

---

### **PHASE 4: Refactor Pillars → MVP Use Case Orchestrators (12-16 hours)**

#### **For Each Pillar → Orchestrator:**

**Pillars to Refactor:**
1. ☐ ContentAnalysisPillar → `content_analysis_orchestrator.py`
2. ☐ DataOperationsPillar → `data_operations_orchestrator.py`
3. ☐ InsightsPillar → `insights_orchestrator.py`
4. ☐ OperationsPillar → `operations_orchestrator.py`

#### **Step 1: Archive Old Pillar**
```bash
☐ Move to archive with timestamp
  mv backend/business_enablement/pillars/[pillar]/[pillar]_pillar.py \
     backend/business_enablement/archive/2024-11-04_[pillar]_pillar.py
```

#### **Step 2: Create Orchestrator (Clean Name!)**
```python
☐ Create use_cases/mvp/[pillar]_orchestrator.py (NO SUFFIXES!)

"""
[Pillar Name] Orchestrator for MVP Use Case

WHAT: Orchestrates enabling services for MVP [pillar] features
HOW: Delegates to enabling services, preserves MVP UI integration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class [PillarName]Orchestrator:
    """
    [Pillar Name] Orchestrator for MVP use case.
    
    Preserves MVP UI integration while delegating to enabling services.
    Provides same API surface as old [PillarName]Pillar.
    """
    
    def __init__(self, business_orchestrator):
        self.business_orchestrator = business_orchestrator
        self.logger = business_orchestrator.logger
    
    # ========================================================================
    # MVP USE CASE APIs (Preserve UI Integration)
    # ========================================================================
    
    async def [mvp_capability_1](self, params) -> Dict[str, Any]:
        """
        [MVP capability description] (preserves UI integration).
        
        OLD: [PillarName]Pillar.[old_method_name]()
        NEW: Delegates to enabling services
        """
        # Delegate to enabling services via Business Orchestrator
        service1 = self.business_orchestrator.[enabling_service_1]
        result1 = await service1.[soa_api_method](params)
        
        service2 = self.business_orchestrator.[enabling_service_2]
        result2 = await service2.[soa_api_method](result1)
        
        # Use Smart City services via helpers
        await self.business_orchestrator.track_data_lineage(
            source=params.get("source"),
            destination=result2.get("id"),
            transformation={"type": "[transformation_type]"}
        )
        
        # Format response for MVP UI (preserves contract)
        return self._format_for_mvp_ui(result2)
    
    async def [mvp_capability_2](self, params) -> Dict[str, Any]:
        """[MVP capability description] (preserves UI integration)."""
        pass
    
    # ========================================================================
    # ORCHESTRATION HELPERS
    # ========================================================================
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute orchestration (called by Business Orchestrator).
        
        Routes to appropriate capability based on request.
        """
        action = request.get("action")
        params = request.get("params", {})
        
        if action == "[action_1]":
            return await self.[mvp_capability_1](params)
        elif action == "[action_2]":
            return await self.[mvp_capability_2](params)
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _format_for_mvp_ui(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format results for MVP UI (preserves API contract).
        
        Ensures UI receives data in expected format.
        """
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### **Step 3: Test Orchestrator**
```bash
☐ Create tests
  tests/unit/business_orchestrator/use_cases/mvp/test_[pillar]_orchestrator.py

☐ Test UI compatibility (integration test)
  tests/integration/test_mvp_ui_compatibility.py

☐ Run tests
  python3 -m pytest tests/unit/business_orchestrator/use_cases/mvp/ -v
```

#### **Step 4: Verify Archiving & Naming**
```bash
☐ Confirm old pillar archived
  ls -la backend/business_enablement/archive/*[pillar]*

☐ Verify no imports reference archived pillar
  grep -r "from.*[pillar]_pillar" backend/

☐ Verify clean naming (no suffixes)
  find backend/business_enablement/business_orchestrator -name "*_new.py"
  find backend/business_enablement/business_orchestrator -name "*_updated.py"
  # Should return nothing!
```

---

### **PHASE 5: Integration & Testing (12-16 hours)**

#### **End-to-End Testing**
```bash
☐ Test UI → Orchestrators → Enabling Services flow
  tests/e2e/test_business_enablement_e2e.py

☐ Verify UI compatibility (no regression)
  # Use existing UI integration tests
  # Verify same endpoints work with same responses

☐ Performance testing
  # Compare response times: old pillars vs new orchestrators

☐ Load testing
  # Ensure no performance degradation
```

#### **Verification Checklist**
```bash
☐ All enabling services registered with Curator
  # Check Curator registry

☐ All orchestrators initialized
  # Check Business Orchestrator logs

☐ UI endpoints working
  # Test all MVP endpoints

☐ No archived code in active imports
  grep -r "from.*archive" backend/

☐ Clean file naming (no suffixes)
  find backend/business_enablement -name "*_new.py" -o -name "*_updated.py" -o -name "*_v2.py"
  # Should return nothing!

☐ All old code archived
  ls -la backend/business_enablement/archive/
```

---

### **PHASE 6: Deployment (4-6 hours)**

```bash
☐ Deploy to staging
☐ Run smoke tests
☐ User acceptance testing
☐ Monitor logs for errors
☐ Deploy to production
☐ Monitor production metrics
```

---

## ⏱️ ESTIMATED TIMELINE

| Phase | Tasks | Hours | Days (with team) |
|-------|-------|-------|------------------|
| **Phase 1** | Setup & Planning | 1-2 | 0.25 |
| **Phase 2** | Enabling Services (15-20) | 30-60 | 4-8 |
| **Phase 3** | Business Orchestrator | 8-12 | 1-1.5 |
| **Phase 4** | MVP Orchestrators (4) | 12-16 | 1.5-2 |
| **Phase 5** | Integration & Testing | 12-16 | 1.5-2 |
| **Phase 6** | Deployment | 4-6 | 0.5-1 |
| **TOTAL** | | **67-112 hours** | **9-15 days** |

**With 2-3 developers:** 1.5-2.5 weeks  
**With 1 developer:** 3-4 weeks

---

## ✅ FINAL VERIFICATION

**Before marking complete:**

```bash
# 1. Verify clean naming (no suffixes)
find backend/business_enablement -name "*_new.py" \
                                  -o -name "*_updated.py" \
                                  -o -name "*_v2.py" \
                                  -o -name "*_refactored.py"
# Expected: No results

# 2. Verify all old code archived
ls -la backend/business_enablement/archive/
# Expected: All old files with 2024-11-04 timestamps

# 3. Verify no imports reference archived code
grep -r "from.*archive" backend/business_enablement/
# Expected: No results

# 4. Verify UI endpoints working
curl http://localhost:8000/business_enablement/content_analysis/analyze_document
# Expected: 200 OK

# 5. Verify all services registered
# Check Curator registry
curl http://localhost:8000/curator/services
# Expected: All enabling services + Business Orchestrator listed

# 6. Run full test suite
cd symphainy_source/tests
python3 -m pytest tests/unit/enabling_services/ -v
python3 -m pytest tests/unit/business_orchestrator/ -v
python3 -m pytest tests/integration/ -v
python3 -m pytest tests/e2e/ -v
# Expected: All tests passing
```

---

## 🎯 SUCCESS CRITERIA

✅ **Architecture:**
- All enabling services use RealmServiceBase
- All orchestrators delegate (not implement)
- Clean separation: capabilities vs. use cases

✅ **File Naming:**
- All files use clean, final names (no suffixes)
- No parallel implementations
- All old code archived with timestamps

✅ **UI Compatibility:**
- All MVP endpoints working
- Same response formats
- No regression

✅ **Platform Readiness:**
- All services registered with Curator
- All services have SOA APIs + MCP Servers
- Ready for Data Mash (future use case)

---

## 📚 REFERENCE DOCUMENTS

- **`PILLAR_SERVICES_HYBRID_STRATEGY.md`** - Strategic analysis
- **`REALM_SERVICE_BASE_ENHANCEMENTS_COMPLETE.md`** - RealmServiceBase features
- **`BUSINESS_ENABLEMENT_STRATEGIC_REFACTORING_PLAN.md`** - Original detailed plan
- **`MVP_Description_For_Business_and_Technical_Readiness.md`** - MVP scope

---

**Ready to start Week 7-8 refactoring!** 🚀










