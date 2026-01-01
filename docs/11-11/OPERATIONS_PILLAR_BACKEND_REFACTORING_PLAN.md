# Operations Pillar Backend Refactoring Plan

**Date**: November 11, 2025  
**Status**: Planning  
**Pattern**: Follow Content & Insights refactoring approach

---

## 🎯 Goal

Refactor Operations Pillar backend to match Content and Insights architecture:
- **MVP Orchestrator** composes enabling services
- **Enabling Services** provide SOA APIs (extracted from micro-modules)
- **MCP Server** exposes tools from enabling services
- **Agents** use enabling services (not pillar service)

**Rule**: No mocks, stubs, placeholders, or hard-coded cheats. Production-quality code only.

---

## 📊 Current State Analysis

### ✅ What Exists (Good!)

**1. Operations Orchestrator** (`business_orchestrator/use_cases/mvp/operations_orchestrator/`)
- ✅ Extends `OrchestratorBase`
- ✅ Located in correct directory
- ❌ Only has 5 methods (needs 16 for semantic API)

**2. Micro-Modules** (`pillars/operations_pillar/micro_modules/`)
- `sop_builder_wizard.py` - Guided SOP creation
- `coexistence_evaluator.py` - AI-human coexistence analysis
- `process_optimizer.py` - Process optimization
- `sop_to_workflow_converter.py` - SOP → Workflow conversion
- `workflow_to_sop_converter.py` - Workflow → SOP conversion
- `sop_visualizer.py` - SOP visualization
- `workflow_visualizer.py` - Workflow visualization

**3. Business Services** (`pillars/operations_pillar/business_services/`)
- `sop_analysis_service.py` - SOP analysis business logic
- `coexistence_optimization_service.py` - Coexistence optimization

**4. MCP Server** (`pillars/operations_pillar/mcp_server/`)
- Exists but may need updating

**5. Agents** (`pillars/operations_pillar/agents/`)
- Exist but need to align with enabling services

### ❌ What's Wrong

**1. Operations Pillar Service** (`pillars/operations_pillar/operations_pillar_service.py`)
- ❌ 1,300+ lines of legacy code
- ❌ Contains composition logic (should be in orchestrator)
- ❌ Should be archived

**2. Micro-modules in Wrong Location**
- ❌ Should be in `enabling_services/` not `pillars/operations_pillar/micro_modules/`
- ❌ Not following RealmServiceBase pattern

**3. OperationsOrchestrator Incomplete**
- ❌ Missing 11 out of 16 semantic API methods
- ❌ Not composing all necessary enabling services

---

## 🏗️ Target Architecture

### Layer 1: MVP Orchestrator
```
business_orchestrator/use_cases/mvp/operations_orchestrator/
├── operations_orchestrator.py  (16 semantic API methods)
├── workflows/                  (Complex orchestration logic)
│   ├── sop_creation_workflow.py
│   ├── workflow_conversion_workflow.py
│   └── coexistence_analysis_workflow.py
├── agents/
│   └── operations_liaison_agent.py  (Uses enabling services via MCP)
└── mcp_server/
    └── operations_mcp_server.py     (Exposes enabling service tools)
```

### Layer 2: Enabling Services
```
business_enablement/enabling_services/
├── sop_builder_service/
│   └── sop_builder_service.py       (From sop_builder_wizard micro-module)
├── coexistence_analysis_service/
│   └── coexistence_analysis_service.py  (From coexistence_evaluator)
├── workflow_conversion_service/
│   ├── workflow_conversion_service.py
│   ├── sop_to_workflow_converter.py
│   └── workflow_to_sop_converter.py
├── process_optimization_service/
│   └── process_optimization_service.py  (From process_optimizer)
└── workflow_visualization_service/
    └── workflow_visualization_service.py  (From visualizers)
```

### Layer 3: Smart City (Infrastructure)
- Librarian, Conductor, DataSteward, etc. (already exists)

---

## 📋 Refactoring Steps

### Phase 1: Create Enabling Services (Extract from Micro-Modules)

**Step 1.1: Create SOPBuilderService**
- Source: `micro_modules/sop_builder_wizard.py`
- Target: `enabling_services/sop_builder_service/sop_builder_service.py`
- Pattern: Extend `RealmServiceBase`
- Capabilities:
  - `start_wizard()` - Initialize SOP wizard session
  - `process_wizard_step(session_token, user_input)` - Process wizard step
  - `complete_wizard(session_token)` - Finalize SOP
  - `validate_sop(sop_data)` - Validate SOP structure

**Step 1.2: Create CoexistenceAnalysisService**
- Source: `micro_modules/coexistence_evaluator.py` + `business_services/coexistence_optimization_service.py`
- Target: `enabling_services/coexistence_analysis_service/coexistence_analysis_service.py`
- Pattern: Extend `RealmServiceBase`
- Capabilities:
  - `analyze_coexistence(sop_content, workflow_content)` - Analyze SOP/Workflow alignment
  - `optimize_coexistence(analysis_id)` - Generate optimization recommendations
  - `create_blueprint(sop_id, workflow_id)` - Create coexistence blueprint

**Step 1.3: Create WorkflowConversionService**
- Source: `micro_modules/sop_to_workflow_converter.py` + `workflow_to_sop_converter.py`
- Target: `enabling_services/workflow_conversion_service/workflow_conversion_service.py`
- Pattern: Extend `RealmServiceBase`
- Capabilities:
  - `convert_sop_to_workflow(sop_file_uuid)` - Convert SOP → Workflow
  - `convert_workflow_to_sop(workflow_file_uuid)` - Convert Workflow → SOP
  - `validate_conversion(conversion_id)` - Validate conversion quality

**Step 1.4: Create ProcessOptimizationService**
- Source: `micro_modules/process_optimizer.py`
- Target: `enabling_services/process_optimization_service/process_optimization_service.py`
- Pattern: Extend `RealmServiceBase`
- Capabilities:
  - `optimize_process(process_id, options)` - Optimize process
  - `analyze_bottlenecks(process_id)` - Identify bottlenecks
  - `suggest_improvements(process_id)` - Generate improvement suggestions

**Step 1.5: Create WorkflowVisualizationService**
- Source: `micro_modules/sop_visualizer.py` + `workflow_visualizer.py`
- Target: `enabling_services/workflow_visualization_service/workflow_visualization_service.py`
- Pattern: Extend `RealmServiceBase`
- Capabilities:
  - `visualize_workflow(workflow_data)` - Create workflow visualization
  - `visualize_sop(sop_data)` - Create SOP visualization
  - `export_visualization(viz_id, format)` - Export visualization

---

### Phase 2: Update OperationsOrchestrator (Compose Enabling Services)

**Step 2.1: Add 16 Semantic API Methods**

The OperationsOrchestrator should have these 16 methods that compose enabling services:

**Session Management (2 methods)**:
1. `get_session_elements(session_token)` - Get session state
2. `clear_session_elements(session_token)` - Clear session state

**Process Blueprint (3 methods)**:
3. `generate_workflow_from_sop(session_token, sop_file_uuid)` → WorkflowConversionService
4. `generate_sop_from_workflow(session_token, workflow_file_uuid)` → WorkflowConversionService
5. `analyze_file(session_token, input_file_uuid, output_type)` → WorkflowConversionService

**Coexistence Analysis (2 methods)**:
6. `analyze_coexistence_files(session_token)` → CoexistenceAnalysisService
7. `analyze_coexistence_content(session_token, sop_content, workflow_content)` → CoexistenceAnalysisService

**Wizard Mode (3 methods)**:
8. `start_wizard()` → SOPBuilderService
9. `wizard_chat(session_token, user_message)` → SOPBuilderService + OperationsLiaisonAgent
10. `wizard_publish(session_token)` → SOPBuilderService

**Blueprint Management (1 method)**:
11. `save_blueprint(blueprint, user_id)` → CoexistenceAnalysisService

**Liaison Agent (4 methods)**:
12. `process_query(session_id, query, file_url, context)` → OperationsLiaisonAgent
13. `process_conversation(session_id, message, context)` → OperationsLiaisonAgent
14. `get_conversation_context(session_id)` → OperationsLiaisonAgent
15. `analyze_intent(query)` → OperationsLiaisonAgent (via NLP enabling service)

**Health Check (1 method)**:
16. `health_check()` ✅ (already exists)

---

### Phase 3: Update MCP Server

**Step 3.1: Update Operations MCP Server**
- Location: `business_orchestrator/use_cases/mvp/operations_orchestrator/mcp_server/`
- Expose **16 MCP Tools** corresponding to the 16 semantic API methods:

**Session Management Tools (2)**:
1. `get_session_elements_tool` → orchestrator.get_session_elements()
2. `clear_session_elements_tool` → orchestrator.clear_session_elements()

**Process Blueprint Tools (3)**:
3. `generate_workflow_from_sop_tool` → orchestrator.generate_workflow_from_sop()
4. `generate_sop_from_workflow_tool` → orchestrator.generate_sop_from_workflow()
5. `analyze_file_tool` → orchestrator.analyze_file()

**Coexistence Analysis Tools (2)**:
6. `analyze_coexistence_files_tool` → orchestrator.analyze_coexistence_files()
7. `analyze_coexistence_content_tool` → orchestrator.analyze_coexistence_content()

**Wizard Mode Tools (3)**:
8. `start_wizard_tool` → orchestrator.start_wizard()
9. `wizard_chat_tool` → orchestrator.wizard_chat()
10. `wizard_publish_tool` → orchestrator.wizard_publish()

**Blueprint Management Tools (1)**:
11. `save_blueprint_tool` → orchestrator.save_blueprint()

**Liaison Agent Tools (4)**:
12. `process_query_tool` → orchestrator.process_query()
13. `process_conversation_tool` → orchestrator.process_conversation()
14. `get_conversation_context_tool` → orchestrator.get_conversation_context()
15. `analyze_intent_tool` → orchestrator.analyze_intent()

**Health Check Tools (1)**:
16. `health_check_tool` → orchestrator.health_check()

**Architecture Flow**:
```
Agent → MCP Tool → MCP Server → Orchestrator Method → Enabling Service(s) → Smart City
```

---

### Phase 4: Update Agents

**Step 4.1: Ensure Operations Liaison Agent Uses MCP Tools**
- Location: `business_orchestrator/use_cases/mvp/operations_orchestrator/agents/`
- Agents use MCP Tools (via Operations MCP Server)
- MCP Tools call enabling services
- Agents should NOT call enabling services directly
- Agents should NOT call operations_pillar_service directly

**Architecture Flow**:
```
Agent → MCP Tool → MCP Server → Enabling Service → Smart City
```

---

### Phase 5: Cleanup

**Step 5.1: Archive Legacy Code**
- Archive: `pillars/operations_pillar/operations_pillar_service.py`
- Archive: `pillars/operations_pillar/micro_modules/` (after extraction)
- Archive: `pillars/operations_pillar/business_services/` (after extraction)

---

## 📊 Implementation Checklist

### Phase 1: Enabling Services ✅
- [ ] Create `enabling_services/sop_builder_service/`
- [ ] Create `enabling_services/coexistence_analysis_service/`
- [ ] Create `enabling_services/workflow_conversion_service/`
- [ ] Create `enabling_services/process_optimization_service/`
- [ ] Create `enabling_services/workflow_visualization_service/`
- [ ] All services extend `RealmServiceBase`
- [ ] All services register with Curator
- [ ] All services integrate with Smart City

### Phase 2: Orchestrator ✅
- [ ] Add all 16 semantic API methods
- [ ] Methods compose enabling services (no business logic)
- [ ] Session management implemented
- [ ] Process blueprint implemented
- [ ] Coexistence analysis implemented
- [ ] Wizard mode implemented
- [ ] Liaison agent integration implemented
- [ ] Blueprint management implemented

### Phase 3: MCP Server ✅
- [ ] Update `operations_mcp_server.py`
- [ ] Expose 6+ tools from enabling services
- [ ] Tools follow MCP protocol

### Phase 4: Agents ✅
- [ ] Operations Liaison Agent uses MCP tools
- [ ] No direct calls to pillar service
- [ ] Agents aligned with enabling services

### Phase 5: Cleanup ✅
- [ ] Archive `operations_pillar_service.py`
- [ ] Archive old micro-modules
- [ ] Archive old business_services
- [ ] Remove old imports
- [ ] Update documentation

---

## 🎯 Success Criteria

1. **All 16 semantic API methods work** ✅
2. **All methods use enabling services** (no business logic in orchestrator) ✅
3. **All enabling services extend RealmServiceBase** ✅
4. **All enabling services register with Curator** ✅
5. **MCP Server exposes tools from enabling services** ✅
6. **Agents use enabling services via MCP** ✅
7. **No mock implementations** ✅
8. **Frontend gateway connects to orchestrator** ✅
9. **End-to-end tests pass** ✅

---

## 📝 Notes

### Key Differences from Content/Insights

**Operations has more complexity**:
- Session management (wizard state)
- Bi-directional conversion (SOP ↔ Workflow)
- Coexistence analysis (2 documents)
- Conversational wizard (liaison agent + wizard)

**Operations needs more enabling services**:
- Content: 2-3 enabling services
- Insights: 3-4 enabling services
- Operations: 5+ enabling services

### Reuse Opportunities

**From Content Pillar**:
- File handling patterns
- Metadata extraction patterns

**From Insights Pillar**:
- DataInsightsQueryService (for NLP in wizard)
- Analysis workflow patterns

**From Operations Existing Code**:
- Real implementations in micro-modules (not mocks!)
- Business services with real logic
- MCP server structure

---

## ⏱️ Estimated Timeline

- **Phase 1** (Enabling Services): 3-4 hours
- **Phase 2** (Orchestrator): 2-3 hours
- **Phase 3** (MCP Server): 1 hour
- **Phase 4** (Agents): 1 hour
- **Phase 5** (Cleanup): 1 hour

**Total**: 8-10 hours

---

**Status**: Ready to begin  
**Next Step**: Create first enabling service (SOPBuilderService)

