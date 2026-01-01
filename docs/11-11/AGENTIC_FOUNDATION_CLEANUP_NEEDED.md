# Agentic Foundation Cleanup - Services in Wrong Location

**Date:** November 10, 2025  
**Issue:** Business services incorrectly placed in Agentic Foundation  
**Impact:** Architectural confusion and potential duplication

---

## 🎯 Core Principle (You're Absolutely Right!)

**Agentic Foundation should ONLY contain:**
- Agentic SDK infrastructure
- Tools to BUILD agents
- NOT business logic
- NOT orchestration logic
- NOT domain-specific enabling services

---

## ❌ Services Currently in WRONG Location

### **Location:** `foundations/agentic_foundation/infrastructure_enablement/`

**Services that SHOULD NOT be here:**

```
❌ data_analysis_service.py
   → Should be: backend/business_enablement/enabling_services/data_analyzer_service/
   → Already exists there! (452 lines)
   → This is a DUPLICATE!

❌ visualization_service.py
   → Should be: backend/business_enablement/enabling_services/visualization_engine_service/
   → Already exists there!
   → This is a DUPLICATE!

❌ metrics_calculation_service.py
   → Should be: backend/business_enablement/enabling_services/metrics_calculator_service/
   → Already exists there!
   → This is a DUPLICATE!

❌ insights_generation_service.py
   → Should be: backend/business_enablement/enabling_services/insights_generator_service/
   → Business logic, not agent infrastructure
   → Needs to be created or might be duplicate of something

❌ insights_orchestration_service.py (533 lines)
   → Should be: backend/business_enablement/enabling_services/insights_orchestrator_service/
   → Or possibly: business_orchestrator/services/ if it's cross-pillar orchestration
   → Orchestration logic, not agent infrastructure

❌ apg_processing_service.py
   → Should be: backend/business_enablement/enabling_services/apg_processor_service/
   → Business logic for APG mode, not agent infrastructure
```

---

## ✅ Services that SHOULD Stay in Agentic Foundation

### **Location:** `foundations/agentic_foundation/`

**These are legitimate Agentic SDK infrastructure:**

```
✅ agent_sdk/ 
   → SDK for building agents (CORRECT)

✅ agentic_foundation_service.py
   → Foundation service for agent infrastructure (CORRECT)

✅ agentic_manager_service.py
   → Manages agents (CORRECT)

✅ agent_dashboard_service.py
   → Agent monitoring (CORRECT)

✅ tool_factory/
   → Factory for creating MCP tools (CORRECT)

✅ specialization_registry.py
   → Agent specializations (CORRECT)

✅ agui_schema_registry.py
   → AGUI schemas for agents (CORRECT)

✅ agui_schema_helpers.py
   → AGUI helpers (CORRECT)
```

### **Location:** `foundations/agentic_foundation/infrastructure_enablement/`

**These might be legitimate (need review):**

```
✅? tool_registry_service.py
   → Registry of MCP tools (probably CORRECT if for agent tools)

✅? tool_discovery_service.py
   → Discovery of available tools (probably CORRECT if for agent tools)

✅? mcp_client_manager.py
   → MCP client management (CORRECT - agent infrastructure)

✅? agui_output_formatter.py
   → Format agent outputs (CORRECT - agent infrastructure)

✅? agui_schema_registry.py
   → AGUI schemas (CORRECT - agent infrastructure)

❓ policy_service.py
   → If agent policies: CORRECT
   → If business policies: WRONG location

❓ session_service.py
   → If agent sessions: CORRECT
   → If user sessions: WRONG location (should be in Journey realm)

❓ health_service.py
   → If agent health: CORRECT
   → If general health: WRONG location (should be infrastructure)
```

---

## 📊 Where Services SHOULD Live

### **1. Agentic Foundation (SDK Infrastructure Only)**
**Location:** `foundations/agentic_foundation/`

**Purpose:** Enable building and managing agents

```
✅ agent_sdk/              # SDK for building agents
✅ agentic_manager_service.py  # Manage agents
✅ tool_factory/            # Create MCP tools
✅ specialization_registry.py  # Agent specializations
✅ agui schemas & helpers   # Agent UI
✅ mcp_client_manager.py    # MCP infrastructure
✅ tool_registry_service.py # Tool registry
✅ tool_discovery_service.py # Tool discovery
```

**Size:** Infrastructure only, NO business logic

---

### **2. Business Enablement Enabling Services**
**Location:** `backend/business_enablement/enabling_services/`

**Purpose:** Generic, reusable business capabilities (NOT MVP-specific)

```
✅ file_parser_service/          # Parse files
✅ data_analyzer_service/         # Analyze data (ALREADY EXISTS!)
✅ visualization_engine_service/  # Create visualizations (ALREADY EXISTS!)
✅ metrics_calculator_service/    # Calculate metrics (ALREADY EXISTS!)
✅ transformation_engine_service/ # Transform data
✅ validation_engine_service/     # Validate data
✅ report_generator_service/      # Generate reports
✅ workflow_manager_service/      # Manage workflows
✅ export_formatter_service/      # Format exports

➕ insights_generator_service/   # Generate insights (NEEDS TO MOVE)
➕ apg_processor_service/         # Process APG mode (NEEDS TO MOVE)
➕ insights_orchestrator_service/ # Orchestrate insights workflows (NEEDS TO MOVE)
```

**Pattern:**
- Each service extends `RealmServiceBase`
- Provides SOA APIs (discoverable via Curator)
- NO MCP tools at this level
- Uses Smart City services
- Uses Public Works abstractions
- Generic (not MVP-specific)

**Size:** ~300-500 lines each

---

### **3. Pillar Services (Thin Wrappers)**
**Location:** `backend/business_enablement/pillars/{pillar_name}/`

**Purpose:** Compose enabling services + micro-modules

```
✅ InsightsPillarService (should be 200-400 lines)
   ├─ Micro-modules (local capability modules)
   ├─ Integration with Smart City services
   ├─ Agents (built with Agentic SDK)
   └─ MCP servers (built with tool_factory)

✅ ContentPillarService (should be 200-400 lines)
   ├─ Micro-modules
   ├─ Integration with Smart City services
   ├─ Agents
   └─ MCP servers
```

**Pattern:**
- Thin RealmServiceBase implementation
- Initialize micro-modules
- Integrate Smart City services
- Initialize agents (from business_enablement/agents/)
- Initialize MCP servers
- NO orchestration logic
- NO MVP-specific workflows

**Size:** 200-400 lines max

---

### **4. MVP Orchestrators (Use Case-Specific)**
**Location:** `backend/business_enablement/business_orchestrator/use_cases/mvp/`

**Purpose:** MVP-specific workflows and UI integration

```
✅ ContentAnalysisOrchestrator (543 lines - GOOD!)
   ├─ Uses enabling services (FileParserService, DataAnalyzerService)
   ├─ Uses Smart City services
   ├─ MVP-specific workflows
   └─ Preserves UI contract

❌ InsightsOrchestrator (57 lines - INCOMPLETE!)
   ├─ Should use enabling services (InsightsOrchestratorService, etc.)
   ├─ Should use Smart City services
   ├─ Should have MVP workflows
   └─ Should preserve UI contract
```

**Pattern:**
- Extends `OrchestratorBase`
- Composes enabling services
- Uses Smart City services
- MVP-specific business logic
- Agents for use case
- MCP server for use case tools

**Size:** 400-600 lines

---

## 🔧 Required Actions

### **Phase 1: Assess Duplicates**
1. ✅ Compare `agentic_foundation/infrastructure_enablement/data_analysis_service.py` 
   vs `enabling_services/data_analyzer_service/`
2. ✅ Compare `visualization_service.py` vs `visualization_engine_service/`
3. ✅ Compare `metrics_calculation_service.py` vs `metrics_calculator_service/`
4. ✅ Determine which is canonical (likely enabling_services versions)

### **Phase 2: Move Services**
```bash
# Move from agentic_foundation to enabling_services
mv foundations/agentic_foundation/infrastructure_enablement/insights_generation_service.py \
   backend/business_enablement/enabling_services/insights_generator_service/

mv foundations/agentic_foundation/infrastructure_enablement/apg_processing_service.py \
   backend/business_enablement/enabling_services/apg_processor_service/

mv foundations/agentic_foundation/infrastructure_enablement/insights_orchestration_service.py \
   backend/business_enablement/enabling_services/insights_orchestrator_service/
```

### **Phase 3: Delete Duplicates**
```bash
# Delete duplicates from agentic_foundation
rm foundations/agentic_foundation/infrastructure_enablement/data_analysis_service.py
rm foundations/agentic_foundation/infrastructure_enablement/visualization_service.py
rm foundations/agentic_foundation/infrastructure_enablement/metrics_calculation_service.py
```

### **Phase 4: Update Imports**
- Update any imports from `agentic_foundation.infrastructure_enablement`
- Point to `business_enablement.enabling_services` instead

### **Phase 5: Verify Agentic Foundation Purity**
After cleanup, `agentic_foundation/` should only contain:
- Agent SDK infrastructure
- Tool factory
- Agent management
- MCP client infrastructure
- AGUI infrastructure
- NO business logic
- NO orchestration logic

---

## 📋 Corrected Architecture

```
foundations/agentic_foundation/
  ├─ agent_sdk/                    # ✅ SDK infrastructure
  ├─ tool_factory/                 # ✅ Tool creation
  ├─ agentic_manager_service.py    # ✅ Agent management
  └─ mcp_client_manager.py         # ✅ MCP infrastructure

backend/business_enablement/
  ├─ enabling_services/             # ✅ Generic business capabilities
  │  ├─ data_analyzer_service/      # ✅ Analyze data
  │  ├─ visualization_engine_service/ # ✅ Create visualizations
  │  ├─ metrics_calculator_service/ # ✅ Calculate metrics
  │  ├─ insights_generator_service/ # ➕ Generate insights (MOVED)
  │  ├─ apg_processor_service/      # ➕ Process APG (MOVED)
  │  └─ insights_orchestrator_service/ # ➕ Orchestrate insights (MOVED)
  │
  ├─ pillars/                       # ✅ Thin wrappers
  │  ├─ insights_pillar/
  │  │  ├─ insights_pillar_service.py (200-400 lines)
  │  │  ├─ micro_modules/
  │  │  ├─ agents/ (built with Agentic SDK)
  │  │  └─ mcp_server/
  │  └─ content_pillar/
  │     └─ content_pillar_service.py (200-400 lines)
  │
  └─ business_orchestrator/
     └─ use_cases/mvp/              # ✅ MVP orchestrators
        ├─ content_analysis_orchestrator/ (543 lines ✅)
        └─ insights_orchestrator/    (needs implementation)
```

---

## ✅ Correct Insights Pillar Service Dependencies

### **InsightsOrchestrator (MVP Use Case) will use:**

```python
class InsightsOrchestrator(OrchestratorBase):
    """MVP Insights Orchestrator."""
    
    async def initialize(self):
        # Get enabling services from business_enablement
        self.insights_orchestrator = await self.get_service(
            "insights_orchestrator_service"  # From enabling_services/
        )
        self.data_analyzer = await self.get_service(
            "data_analyzer_service"  # From enabling_services/
        )
        self.visualization_engine = await self.get_service(
            "visualization_engine_service"  # From enabling_services/
        )
        
        # Get Smart City services
        self.data_steward = await self.get_data_steward_api()
        self.librarian = await self.get_librarian_api()
        
    async def analyze_structured_content(self, ...):
        # Use enabling services for capabilities
        # Use Smart City services for data access
        # Apply MVP-specific business logic
        pass
```

**All services used by InsightsOrchestrator live in:**
- ✅ `backend/business_enablement/enabling_services/` (enabling services)
- ✅ `backend/smart_city/services/` (Smart City services)
- ✅ `foundations/public_works_foundation/` (infrastructure abstractions)
- ❌ NOT in `foundations/agentic_foundation/` (that's only for agent SDK)

---

## 🎯 Summary

**Problem:** Business services incorrectly placed in Agentic Foundation

**Solution:**
1. Move insights-related services to `enabling_services/`
2. Delete duplicate services from `agentic_foundation/`
3. Keep only agent SDK infrastructure in `agentic_foundation/`
4. Update imports

**Result:** Clean separation of concerns
- Agentic Foundation = Agent SDK only
- Enabling Services = Business capabilities
- Pillar Services = Thin wrappers
- MVP Orchestrators = Use case workflows

---

## 💡 Key Principle

**Agentic Foundation is for building agents, NOT for business logic!**

If a service provides business capabilities (data analysis, visualization, insights), it belongs in `enabling_services/`, NOT `agentic_foundation/`.

Agents are BUILT in the realm where they're used (business_enablement), USING the Agentic SDK infrastructure.




