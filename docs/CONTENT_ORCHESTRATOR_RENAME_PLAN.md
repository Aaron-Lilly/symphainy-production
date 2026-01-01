# ContentOrchestrator Rename Plan

**Date:** December 14, 2025  
**Purpose:** Rename `ContentAnalysisOrchestrator` to `ContentOrchestrator` to:
1. Simplify naming (remove redundant "Analysis")
2. Find all hidden references that might be causing discovery issues
3. Add debugging during rename to understand orchestrator discovery

---

## Rename Strategy

**Old Name:** `ContentAnalysisOrchestrator`  
**New Name:** `ContentOrchestrator`

**Key Changes:**
- Class name: `ContentAnalysisOrchestrator` → `ContentOrchestrator`
- Service name: `ContentAnalysisOrchestratorService` → `ContentOrchestratorService`
- Dictionary key: `"content_analysis"` → `"content"` (in DeliveryManager)
- Directory: `content_analysis_orchestrator/` → `content_orchestrator/`
- MCP Server: `ContentAnalysisMCPServer` → `ContentMCPServer`
- Agent references: `ContentAnalysisOrchestrator` → `ContentOrchestrator`

---

## Files to Update (30 files found)

### Core Implementation Files
1. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`
   - Class definition
   - Service name
   - Orchestrator name

2. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/__init__.py`
   - Export statement

3. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/mcp_server/content_analysis_mcp_server.py`
   - MCP Server class name
   - References to orchestrator

4. `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/*.py`
   - Agent references

### Service Registration Files
5. `backend/business_enablement/delivery_manager/delivery_manager_service.py`
   - Import statement
   - Dictionary key: `"content_analysis"` → `"content"`
   - Class instantiation

### Gateway/Router Files
6. `foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`
   - Discovery logic
   - Dictionary key lookups
   - Handler references
   - **ADD DEBUG LOGGING HERE**

7. `foundations/experience_foundation/experience_foundation_service.py`
   - Service references

8. `backend/api/universal_pillar_router.py`
   - Router references

9. `backend/api/websocket_router.py`
   - WebSocket references

### Foundation Services
10. `foundations/curator_foundation/curator_foundation_service.py`
11. `foundations/agentic_foundation/agentic_foundation_service.py`
12. `foundations/public_works_foundation/public_works_foundation_service.py`

### Bridge Files
13. `foundations/experience_foundation/realm_bridges/business_enablement_bridge.py`

### Journey Services
14. `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

### Test Files
15-30. Various test files (update after core rename)

---

## Debug Logging to Add

During the rename, add debug logging at key points:

1. **DeliveryManagerService** - When creating orchestrator:
   ```python
   self.logger.debug(f"🔍 Creating ContentOrchestrator: {type(content_orchestrator).__name__}")
   self.logger.debug(f"🔍 ContentOrchestrator object: {content_orchestrator is not None}")
   self.logger.debug(f"🔍 Storing in mvp_pillar_orchestrators['content']: {content_orchestrator}")
   ```

2. **FrontendGatewayService._discover_orchestrators()** - When discovering:
   ```python
   self.logger.debug(f"🔍 Delivery Manager mvp_pillar_orchestrators keys: {list(delivery_manager.mvp_pillar_orchestrators.keys())}")
   self.logger.debug(f"🔍 'content' in dict: {'content' in delivery_manager.mvp_pillar_orchestrators}")
   if 'content' in delivery_manager.mvp_pillar_orchestrators:
       orchestrator = delivery_manager.mvp_pillar_orchestrators['content']
       self.logger.debug(f"🔍 ContentOrchestrator object: {orchestrator is not None}, type: {type(orchestrator).__name__}")
   ```

3. **FrontendGatewayService.handle_upload_file_request()** - When checking:
   ```python
   self.logger.debug(f"🔍 self.content_orchestrator: {self.content_orchestrator is not None}")
   self.logger.debug(f"🔍 self.orchestrators.get('ContentOrchestrator'): {self.orchestrators.get('ContentOrchestrator') is not None}")
   self.logger.debug(f"🔍 orchestrators dict keys: {list(self.orchestrators.keys())}")
   ```

---

## Execution Order

1. **Rename directory** (to avoid import issues)
2. **Update class definition** (in renamed directory)
3. **Update DeliveryManagerService** (import + dictionary key)
4. **Update FrontendGatewayService** (discovery + handlers + debug logging)
5. **Update all other references**
6. **Test and verify**

---

## Verification Checklist

- [ ] Directory renamed
- [ ] Class renamed
- [ ] Service name updated
- [ ] Dictionary key changed from `"content_analysis"` to `"content"`
- [ ] All imports updated
- [ ] Debug logging added
- [ ] Backend starts successfully
- [ ] File upload works
- [ ] Orchestrator discovered correctly



