# Operations Pillar Backend Refactoring - Status

**Date**: November 11, 2025  
**Status**: ✅ Plan Complete - Ready to Execute  
**Estimated Time**: 8-10 hours

---

## 🎯 What We're Doing

Refactoring Operations Pillar to match Content & Insights pattern:
- Extract 7 micro-modules into 5 enabling services  
- Update OperationsOrchestrator with 16 semantic API methods
- Update Operations MCP Server with 16 MCP Tools
- Verify agents use MCP Tools properly
- Archive legacy code

---

## ✅ What's Already Done

### Frontend (Complete!)
- ✅ Universal gateway wired up
- ✅ FrontendGatewayService has 14 Operations handlers
- ✅ Universal router has Operations routing

### Planning (Complete!)
- ✅ Analyzed current state
- ✅ Identified real implementations (not mocks!)
- ✅ Created comprehensive refactoring plan
- ✅ Clarified architecture (Agent → MCP Tool → MCP Server → Orchestrator → Enabling Service)

---

## 📋 What Needs to Be Done

### Phase 1: Create 5 Enabling Services (3-4 hours)

**1. SOPBuilderService** ← Extract from `sop_builder_wizard.py`
- Source: 263 lines of real code
- Capabilities:
  - `start_wizard_session()`
  - `process_wizard_step(session_token, user_input)`
  - `complete_wizard(session_token)`
  - `create_sop(description, options)`
  - `validate_sop(sop_data)`

**2. CoexistenceAnalysisService** ← Extract from `coexistence_evaluator.py`
- Source: 248 lines of real code
- Capabilities:
  - `analyze_coexistence(sop_content, workflow_content)`
  - `optimize_coexistence(analysis_id)`
  - `create_blueprint(sop_id, workflow_id)`
  - `evaluate_patterns(current_state, target_state)`

**3. WorkflowConversionService** ← Extract from 2 conversion modules
- Sources: `sop_to_workflow_converter.py` + `workflow_to_sop_converter.py`
- Capabilities:
  - `convert_sop_to_workflow(sop_file_uuid)`
  - `convert_workflow_to_sop(workflow_file_uuid)`
  - `validate_conversion(conversion_id)`
  - `analyze_file(input_uuid, output_type)`

**4. ProcessOptimizationService** ← Extract from `process_optimizer.py`
- Source: Real optimization code
- Capabilities:
  - `optimize_process(process_id, options)`
  - `analyze_bottlenecks(process_id)`
  - `suggest_improvements(process_id)`

**5. WorkflowVisualizationService** ← Extract from 2 visualizer modules
- Sources: `sop_visualizer.py` + `workflow_visualizer.py`
- Capabilities:
  - `visualize_workflow(workflow_data)`
  - `visualize_sop(sop_data)`
  - `export_visualization(viz_id, format)`

**Requirements for Each Service**:
- Extend `RealmServiceBase`
- Implement `initialize()` method
- Register with Curator
- Integrate with Smart City (Librarian, etc.)
- Provide SOA APIs

---

### Phase 2: Update OperationsOrchestrator (2-3 hours)

Add **16 semantic API methods** that compose enabling services:

**Session Management** (2 methods):
1. `get_session_elements(session_token)` 
   - Check session state in Librarian
2. `clear_session_elements(session_token)` 
   - Clear session from Librarian

**Process Blueprint** (3 methods):
3. `generate_workflow_from_sop(session_token, sop_file_uuid)`
   - Call WorkflowConversionService.convert_sop_to_workflow()
4. `generate_sop_from_workflow(session_token, workflow_file_uuid)`
   - Call WorkflowConversionService.convert_workflow_to_sop()
5. `analyze_file(session_token, input_file_uuid, output_type)`
   - Call WorkflowConversionService.analyze_file()

**Coexistence Analysis** (2 methods):
6. `analyze_coexistence_files(session_token)`
   - Get files from session, call CoexistenceAnalysisService.analyze_coexistence()
7. `analyze_coexistence_content(session_token, sop_content, workflow_content)`
   - Call CoexistenceAnalysisService.analyze_coexistence()

**Wizard Mode** (3 methods):
8. `start_wizard()`
   - Call SOPBuilderService.start_wizard_session()
9. `wizard_chat(session_token, user_message)`
   - Get wizard state, process with SOPBuilderService + OperationsLiaisonAgent
10. `wizard_publish(session_token)`
   - Call SOPBuilderService.complete_wizard()

**Blueprint Management** (1 method):
11. `save_blueprint(blueprint, user_id)`
   - Call CoexistenceAnalysisService.create_blueprint()

**Liaison Agent** (4 methods):
12. `process_query(session_id, query, file_url, context)`
   - Delegate to OperationsLiaisonAgent (via MCP)
13. `process_conversation(session_id, message, context)`
   - Delegate to OperationsLiaisonAgent (via MCP)
14. `get_conversation_context(session_id)`
   - Get conversation history from Librarian
15. `analyze_intent(query)`
   - Use NLP service to analyze user intent

**Health Check** (1 method):
16. `health_check()` ✅ Already exists

---

### Phase 3: Update Operations MCP Server (1 hour)

Expose **16 MCP Tools** corresponding to orchestrator methods:
- `get_session_elements_tool`
- `clear_session_elements_tool`
- `generate_workflow_from_sop_tool`
- `generate_sop_from_workflow_tool`
- `analyze_file_tool`
- `analyze_coexistence_files_tool`
- `analyze_coexistence_content_tool`
- `start_wizard_tool`
- `wizard_chat_tool`
- `wizard_publish_tool`
- `save_blueprint_tool`
- `process_query_tool`
- `process_conversation_tool`
- `get_conversation_context_tool`
- `analyze_intent_tool`
- `health_check_tool`

Each tool should:
- Accept MCP-formatted input
- Call orchestrator method
- Return MCP-formatted output

---

### Phase 4: Verify Agents (1 hour)

Ensure OperationsLiaisonAgent:
- Uses MCP Tools (not direct calls)
- Does NOT call enabling services directly
- Does NOT call operations_pillar_service directly
- Follows: Agent → MCP Tool → MCP Server → Orchestrator → Enabling Service

---

### Phase 5: Cleanup (1 hour)

- Archive `operations_pillar_service.py`
- Archive `pillars/operations_pillar/micro_modules/`
- Archive `pillars/operations_pillar/business_services/`
- Update imports
- Update documentation

---

## 📊 Execution Approach

Given the scope (8-10 hours), we should:

**Option A: Do it all in one session** (ambitious)
- Create all 5 enabling services
- Update orchestrator with all 16 methods
- Update MCP server
- Test end-to-end

**Option B: Do it in phases** (safer)
- Phase 1: Create 2-3 enabling services, test
- Phase 2: Complete remaining services, update orchestrator
- Phase 3: MCP server + agents + cleanup

**Option C: Focus on critical path** (pragmatic)
- Create only the enabling services needed for the 16 methods
- Update orchestrator
- Update MCP server
- Defer visualization service (if not immediately needed)

---

## 🎯 Recommendation

**Start with Option C (Critical Path)**:

1. **SOPBuilderService** (needed for wizard methods)
2. **CoexistenceAnalysisService** (needed for coexistence methods)
3. **WorkflowConversionService** (needed for conversion methods)
4. Skip ProcessOptimizationService (can use WorkflowManager)
5. Skip WorkflowVisualizationService (can use VisualizationEngine)

This gets us to **functional** faster, then we can add the other services later.

---

**Decision needed**: Which option do you prefer?

A. All 5 services (8-10 hours)
B. Phased approach (spread over multiple sessions)
C. Critical path first (3 services, 4-6 hours)



