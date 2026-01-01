# Backend/Platform Semantic Alignment Plan
## Extending User-Focused Semantic Naming Throughout the Stack

## Executive Summary

Just as we're implementing semantic, user-focused selectors in the frontend, we should align the **entire platform stack** with the same semantic model. This creates:

1. **Consistency** - Same mental model from UI to API to services
2. **Developer Experience** - Intuitive naming that matches user journeys
3. **Maintainability** - Clear relationships between frontend actions and backend capabilities
4. **Onboarding** - New developers understand the system faster

---

## Part 1: Current State Analysis

### Current Backend Naming Patterns

#### API Endpoints (Current)
```
/api/mvp/content/upload          → Technical, implementation-focused
/api/mvp/content/parse/{file_id} → Technical action
/api/mvp/operations/sop/create   → Mixed (sop is acronym, create is action)
/api/global/agent/analyze        → Generic, unclear purpose
/api/liaison/chat                → Generic, doesn't indicate which pillar
```

#### Service/Orchestrator Names (Current)
```
ContentAnalysisOrchestrator      → Technical, implementation-focused
BusinessOrchestratorService      → Generic
OperationsPillarService          → Mixed (pillar is domain, service is technical)
ContentLiaisonAgent              → Good, but inconsistent with "Data" vs "Content"
```

#### Issues with Current Naming
1. **Inconsistent abstraction levels** - Mix of technical and domain terms
2. **Unclear user intent** - `analyze` doesn't tell you what's being analyzed
3. **Acronyms** - `sop`, `poc` require domain knowledge
4. **Generic terms** - `chat`, `analyze` don't indicate context
5. **Implementation details** - `parse`, `upload` are technical actions, not user goals

---

## Part 2: Semantic Naming Principles for Backend

### Principle 1: User Journey Alignment

**Frontend Action** → **Backend API** → **Service Method**

```
User clicks "Upload File" 
  → POST /api/content-pillar/upload-file
  → ContentPillarService.upload_file()
```

### Principle 2: Capability-Focused Naming

**Instead of:** What the code does (`parse`, `analyze`)
**Use:** What capability it provides (`extract-insights`, `process-content`)

### Principle 3: Context-Aware Naming

**Instead of:** Generic actions (`chat`, `analyze`)
**Use:** Contextual actions (`chat-with-guide-agent`, `analyze-content-for-insights`)

### Principle 4: Journey Continuity

**User Journey:** Upload → Process → Analyze → Generate
**API Journey:** `/upload-file` → `/process-file` → `/analyze-for-insights` → `/generate-roadmap`

---

## Part 3: Proposed Semantic API Structure

### Content Pillar (Content Management)

#### Current
```
POST /api/mvp/content/upload
POST /api/mvp/content/parse/{file_id}
GET  /api/mvp/content/files
```

#### Proposed (Semantic)
```
POST /api/content-pillar/upload-file
POST /api/content-pillar/process-file/{file_id}
POST /api/content-pillar/process-binary-with-copybook
GET  /api/content-pillar/list-uploaded-files
GET  /api/content-pillar/get-file-details/{file_id}
```

**Rationale:**
- `upload-file` - Clear user action
- `process-file` - User goal (not technical "parse")
- `process-binary-with-copybook` - Specific capability
- `list-uploaded-files` - Clear intent
- `get-file-details` - User-focused retrieval

### Insights Pillar (Data Analysis)

#### Current
```
POST /api/mvp/insights/analyze
```

#### Proposed (Semantic)
```
POST /api/insights-pillar/analyze-content-for-insights
POST /api/insights-pillar/generate-findings
POST /api/insights-pillar/generate-recommendations
GET  /api/insights-pillar/get-analysis-results
GET  /api/insights-pillar/get-visualizations
```

**Rationale:**
- `analyze-content-for-insights` - Clear purpose and outcome
- `generate-findings` - User-visible output
- `generate-recommendations` - Business value
- `get-analysis-results` - User-focused retrieval

### Operations Pillar (Process Optimization)

#### Current
```
POST /api/mvp/operations/sop/create
POST /api/mvp/operations/workflow/create
```

#### Proposed (Semantic)
```
POST /api/operations-pillar/create-standard-operating-procedure
POST /api/operations-pillar/create-workflow
POST /api/operations-pillar/convert-sop-to-workflow
POST /api/operations-pillar/convert-workflow-to-sop
GET  /api/operations-pillar/list-sops
GET  /api/operations-pillar/list-workflows
```

**Rationale:**
- `create-standard-operating-procedure` - Full term, no acronym
- `convert-sop-to-workflow` - Clear transformation
- `list-sops` - User-focused retrieval (acronym OK in list context)

### Business Outcomes Pillar (Strategic Planning)

#### Current
```
POST /api/mvp/business-outcomes/roadmap/create
POST /api/mvp/business-outcomes/poc-proposal/create
```

#### Proposed (Semantic)
```
POST /api/business-outcomes-pillar/generate-strategic-roadmap
POST /api/business-outcomes-pillar/generate-proof-of-concept-proposal
GET  /api/business-outcomes-pillar/get-pillar-summaries
GET  /api/business-outcomes-pillar/get-journey-visualization
```

**Rationale:**
- `generate-strategic-roadmap` - Clear business value
- `generate-proof-of-concept-proposal` - Full term, no acronym
- `get-pillar-summaries` - User-visible aggregation
- `get-journey-visualization` - User-focused visualization

### Guide Agent (Journey Navigation)

#### Current
```
POST /api/global/agent/analyze
```

#### Proposed (Semantic)
```
POST /api/guide-agent/analyze-user-intent
POST /api/guide-agent/get-journey-guidance
POST /api/guide-agent/navigate-to-pillar
GET  /api/guide-agent/get-conversation-history
```

**Rationale:**
- `analyze-user-intent` - Clear purpose
- `get-journey-guidance` - User-focused capability
- `navigate-to-pillar` - Clear action
- `get-conversation-history` - User-visible data

### Liaison Agents (Pillar-Specific Assistance)

#### Current
```
POST /api/liaison/chat
```

#### Proposed (Semantic)
```
POST /api/content-liaison-agent/chat-about-content
POST /api/insights-liaison-agent/chat-about-insights
POST /api/operations-liaison-agent/chat-about-operations
POST /api/business-outcomes-liaison-agent/chat-about-outcomes
```

**Alternative (More RESTful):**
```
POST /api/liaison-agents/content-pillar/chat
POST /api/liaison-agents/insights-pillar/chat
POST /api/liaison-agents/operations-pillar/chat
POST /api/liaison-agents/business-outcomes-pillar/chat
```

**Rationale:**
- Clear pillar context
- User-focused chat purpose
- Consistent with pillar naming

### Session Management

#### Current
```
POST /api/global/session
GET  /api/global/session/{session_id}
DELETE /api/global/session/{session_id}
```

#### Proposed (Semantic)
```
POST /api/session/create-user-session
GET  /api/session/get-session-state/{session_id}
PUT  /api/session/update-session-state/{session_id}
DELETE /api/session/end-user-session/{session_id}
GET  /api/session/get-orchestrator-context/{session_id}
GET  /api/session/get-conversation-history/{session_id}
```

**Rationale:**
- `create-user-session` - Clear action
- `get-session-state` - User-visible state
- `get-orchestrator-context` - Technical but necessary
- `get-conversation-history` - User-visible data

---

## Part 4: Service/Orchestrator Naming

### Current Service Names

```
ContentAnalysisOrchestrator
InsightsOrchestrator
OperationsOrchestrator
BusinessOutcomesOrchestrator
BusinessOrchestratorService
ContentPillarService
OperationsPillarService
```

### Proposed Semantic Service Names

```
ContentPillarOrchestrator          # Aligns with "Content" naming
InsightsPillarOrchestrator         # Consistent pillar naming
OperationsPillarOrchestrator       # Already good
BusinessOutcomesPillarOrchestrator  # Already good
BusinessOrchestratorService         # Keep as is (platform-level)
ContentPillarService               # Already good
InsightsPillarService              # Consistent
OperationsPillarService            # Already good
BusinessOutcomesPillarService      # Consistent
```

### Agent Naming

#### Current
```
GuideAgent
ContentLiaisonAgent
InsightsLiaisonAgent
OperationsLiaisonAgent
BusinessOutcomesLiaisonAgent
```

#### Proposed (Already Semantic)
```
GuideAgent                        # ✅ Good - clear purpose
ContentLiaisonAgent               # ✅ Good - aligns with Content pillar
InsightsLiaisonAgent              # ✅ Good
OperationsLiaisonAgent           # ✅ Good
BusinessOutcomesLiaisonAgent      # ✅ Good
```

**Note:** Agent names are already well-aligned with semantic principles!

---

## Part 5: Implementation Strategy

### Phase 1: API Endpoint Alignment (4-6 hours)

**Approach:** Add new semantic endpoints alongside existing ones (backward compatibility)

**Tasks:**
1. Add new semantic endpoints to routers
2. Route new endpoints to existing service methods
3. Update API documentation
4. Add deprecation warnings to old endpoints
5. Update frontend to use new endpoints

**Example Implementation:**
```python
# mvp_content_router.py

# Keep existing for backward compatibility
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file_legacy(...):
    """Legacy endpoint - use /upload-file instead"""
    logger.warning("Legacy endpoint /upload used - migrate to /upload-file")
    return await upload_file_semantic(...)

# New semantic endpoint
@router.post("/upload-file", response_model=FileUploadResponse)
async def upload_file_semantic(...):
    """Upload a file to the content pillar"""
    # Same implementation, better naming
    ...
```

**Files to Modify:**
- `backend/experience/api/mvp_content_router.py`
- `backend/experience/api/mvp_insights_router.py`
- `backend/experience/api/mvp_operations_router.py`
- `backend/experience/api/mvp_business_outcomes_router.py`
- `backend/experience/api/guide_agent_router.py`
- `backend/experience/api/liaison_agent_router.py`
- `backend/experience/api/session_router.py`

---

### Phase 2: Service Method Naming (2-3 hours)

**Approach:** Add semantic method aliases, keep existing methods

**Tasks:**
1. Add semantic method names to services
2. Keep existing methods for internal calls
3. Update API routers to use semantic methods
4. Document method naming conventions

**Example Implementation:**
```python
# content_pillar_service.py

class ContentPillarService:
    # Existing method (keep for internal use)
    async def parse_file(self, file_id: str):
        """Parse a file - internal method"""
        ...
    
    # New semantic method (for API)
    async def process_file(self, file_id: str):
        """Process a file for analysis - semantic method"""
        return await self.parse_file(file_id)
    
    # Or use alias
    process_file = parse_file  # Alias for semantic naming
```

**Files to Modify:**
- `backend/business_enablement/pillars/content_pillar/content_pillar_service.py`
- `backend/business_enablement/pillars/insights_pillar/insights_pillar_service.py`
- `backend/business_enablement/pillars/operations_pillar/operations_pillar_service.py`
- `backend/business_enablement/pillars/business_outcomes_pillar/business_outcomes_pillar_service.py`

---

### Phase 3: Orchestrator Naming (1-2 hours)

**Approach:** Rename orchestrators to align with pillar naming

**Tasks:**
1. Rename `ContentAnalysisOrchestrator` → `ContentPillarOrchestrator`
2. Update all references
3. Update configuration files
4. Update documentation

**Files to Modify:**
- `backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator/` → rename directory
- All imports and references
- Configuration files

---

### Phase 4: Frontend API Client Updates (2-3 hours)

**Approach:** Update frontend to use new semantic endpoints

**Tasks:**
1. Update API client methods
2. Update API endpoint constants
3. Update component API calls
4. Test all API interactions

**Files to Modify:**
- `symphainy-frontend/lib/api/` (or wherever API client is)
- All components that make API calls

---

### Phase 5: Documentation & Deprecation (1-2 hours)

**Tasks:**
1. Update API documentation with new endpoints
2. Add deprecation notices to old endpoints
3. Create migration guide
4. Update OpenAPI/Swagger specs

---

## Part 6: Backward Compatibility Strategy

### Option A: Dual Endpoints (Recommended)

**Keep old endpoints, add new ones:**
- ✅ Zero breaking changes
- ✅ Gradual migration
- ✅ Can deprecate old endpoints later
- ❌ More code to maintain initially

### Option B: Alias Pattern

**Route new endpoints to old implementations:**
```python
# New semantic endpoint
@router.post("/upload-file")
async def upload_file(...):
    return await upload(...)  # Call existing implementation

# Old endpoint (deprecated)
@router.post("/upload")
async def upload_legacy(...):
    logger.warning("Deprecated: Use /upload-file instead")
    return await upload_file(...)
```

### Option C: Versioning

**Use API versioning:**
```
/api/v1/mvp/content/upload          # Old
/api/v2/content-pillar/upload-file # New
```

**Recommendation:** Use **Option A (Dual Endpoints)** for Phase 1, then migrate to Option B (Alias Pattern) once frontend is updated.

---

## Part 7: Benefits of Full-Stack Semantic Alignment

### 1. Developer Experience

**Before:**
```python
# Developer sees this in frontend
<button data-testid="upload-file">Upload</button>

# But API is
POST /api/mvp/content/upload  # Different mental model
```

**After:**
```python
# Frontend
<button data-testid="upload-file-to-content-pillar">Upload</button>

# API
POST /api/content-pillar/upload-file  # Same mental model!
```

### 2. Code Discoverability

**Developer wants to find "file upload" code:**
- Frontend: Search for `upload-file`
- API: Search for `upload-file`
- Service: Search for `upload_file`
- **All use same semantic model!**

### 3. Documentation Clarity

**API Documentation:**
```
POST /api/content-pillar/upload-file
  → Uploads a file to the content pillar
  → Returns file metadata
  → Triggers file processing workflow
```

**Matches user journey exactly!**

### 4. Testing Alignment

**E2E Test:**
```python
# Test action
await page.locator("[data-testid='upload-file-to-content-pillar']").click()

# API call (same semantic model)
response = await client.post("/api/content-pillar/upload-file", ...)
```

**Same naming throughout!**

---

## Part 8: Migration Timeline

### Week 1: Foundation
- Phase 1: Add semantic API endpoints (dual endpoints)
- Phase 3: Rename orchestrators
- **Result:** New endpoints available, old ones still work

### Week 2: Frontend Migration
- Phase 4: Update frontend to use new endpoints
- Phase 2: Update service method names
- **Result:** Frontend uses semantic endpoints

### Week 3: Cleanup
- Phase 5: Documentation updates
- Deprecate old endpoints (with warnings)
- **Result:** Full semantic alignment

### Week 4: Monitoring
- Monitor old endpoint usage
- Plan removal timeline
- **Result:** Clear migration path

---

## Part 9: Example: Complete Semantic Flow

### User Journey: Upload File → Process → Analyze

**Frontend (User Action):**
```tsx
<button 
  data-testid="upload-file-to-content-pillar"
  onClick={() => uploadFile()}
>
  Upload File
</button>
```

**Frontend API Call:**
```typescript
await api.post('/api/content-pillar/upload-file', formData)
```

**Backend API Endpoint:**
```python
@router.post("/upload-file")
async def upload_file_to_content_pillar(...):
    """Upload a file to the content pillar"""
    return await content_pillar_service.upload_file(...)
```

**Service Method:**
```python
class ContentPillarService:
    async def upload_file(self, file_data, ...):
        """Upload and process a file"""
        return await self.content_orchestrator.handle_file_upload(...)
```

**Orchestrator:**
```python
class ContentPillarOrchestrator:
    async def handle_file_upload(self, file_data, ...):
        """Orchestrate file upload workflow"""
        ...
```

**All use the same semantic model: `upload-file` / `upload_file` / `handle_file_upload`**

---

## Part 10: Recommendations

### Immediate (This Sprint)
1. ✅ **Add semantic API endpoints** alongside existing ones
2. ✅ **Rename ContentAnalysisOrchestrator** → ContentPillarOrchestrator
3. ✅ **Update frontend to use new endpoints** (once available)

### Short-term (Next Sprint)
1. ✅ **Update service method names** to semantic versions
2. ✅ **Update all documentation**
3. ✅ **Add deprecation warnings** to old endpoints

### Long-term (3-6 months)
1. ✅ **Remove old endpoints** (after migration period)
2. ✅ **Establish semantic naming standards** for all new features
3. ✅ **Create naming convention documentation**

---

## Conclusion

**Yes, absolutely update the backend/platform to use semantic, user-focused naming!**

This creates:
- ✅ **Consistency** across entire stack
- ✅ **Better developer experience** - intuitive naming
- ✅ **Easier onboarding** - clear mental models
- ✅ **Better maintainability** - aligned naming
- ✅ **Professional architecture** - thoughtful design

**The effort is worth it** - especially since you're already doing it for the frontend. Extending it to the backend creates a cohesive, professional platform.

**Recommended Start:** Phase 1 (API Endpoint Alignment) - can be done incrementally with zero breaking changes.






