# Clean Semantic Migration Plan
## Break and Fix: New Semantic Patterns → Test → Replace

## Philosophy

**No backward compatibility. Clean break.**
- Build new semantic APIs
- Test thoroughly (equivalent or better functionality)
- Replace old APIs completely
- Zero technical debt from dual endpoints

---

## Part 1: Migration Strategy

### Phase 1: Build New Semantic APIs (Parallel Development)
- Create new semantic endpoints
- Keep old endpoints running
- **No frontend changes yet**
- **Goal:** New APIs work, old APIs still work

### Phase 2: Comprehensive Testing
- Test new APIs match old functionality
- Test new APIs are better (more semantic, clearer)
- Validate all user journeys work
- **Goal:** Confidence new APIs are ready

### Phase 3: Frontend Migration
- Update frontend to use new APIs
- Update all API clients
- **Goal:** Frontend uses new APIs exclusively

### Phase 4: Remove Old APIs
- Delete old endpoint code
- Remove old service methods
- Clean up references
- **Goal:** Clean codebase, only semantic APIs

---

## Part 2: New Semantic API Structure

### Content Pillar

#### Old → New Mapping
```
POST /api/mvp/content/upload
  → POST /api/content-pillar/upload-file

POST /api/mvp/content/parse/{file_id}
  → POST /api/content-pillar/process-file/{file_id}

GET  /api/mvp/content/files
  → GET  /api/content-pillar/list-uploaded-files

GET  /api/mvp/content/health
  → GET  /api/content-pillar/health
```

#### New Semantic Endpoints
```python
# File Upload
POST /api/content-pillar/upload-file
  Body: multipart/form-data
  Response: {
    "success": true,
    "file_id": "uuid",
    "file_name": "example.csv",
    "file_type": "csv",
    "uploaded_at": "2025-11-08T...",
    "status": "uploaded"
  }

# File Processing
POST /api/content-pillar/process-file/{file_id}
  Body: {
    "copybook_file_id": "optional-uuid",  # For binary files
    "processing_options": {}
  }
  Response: {
    "success": true,
    "file_id": "uuid",
    "processing_status": "completed",
    "parsed_data": {...},
    "metadata": {...}
  }

# List Files
GET /api/content-pillar/list-uploaded-files
  Query: ?user_id=...&file_type=...&status=...
  Response: {
    "success": true,
    "files": [
      {
        "file_id": "uuid",
        "file_name": "example.csv",
        "file_type": "csv",
        "status": "processed",
        "uploaded_at": "...",
        "processed_at": "..."
      }
    ]
  }

# Get File Details
GET /api/content-pillar/get-file-details/{file_id}
  Response: {
    "success": true,
    "file": {
      "file_id": "uuid",
      "file_name": "example.csv",
      "file_type": "csv",
      "size": 1024,
      "status": "processed",
      "parsed_data": {...},
      "metadata": {...}
    }
  }
```

### Insights Pillar

#### Old → New Mapping
```
POST /api/mvp/insights/analyze
  → POST /api/insights-pillar/analyze-content-for-insights
```

#### New Semantic Endpoints
```python
# Analyze Content
POST /api/insights-pillar/analyze-content-for-insights
  Body: {
    "file_ids": ["uuid1", "uuid2"],
    "analysis_type": "comprehensive",  # or "quick", "detailed"
    "focus_areas": ["trends", "anomalies", "recommendations"]
  }
  Response: {
    "success": true,
    "analysis_id": "uuid",
    "key_findings": [...],
    "recommendations": [...],
    "visualizations": {...},
    "confidence_score": 0.95
  }

# Get Analysis Results
GET /api/insights-pillar/get-analysis-results/{analysis_id}
  Response: {
    "success": true,
    "analysis": {...},
    "findings": [...],
    "recommendations": [...]
  }

# Get Visualizations
GET /api/insights-pillar/get-visualizations/{analysis_id}
  Response: {
    "success": true,
    "visualizations": {
      "charts": [...],
      "graphs": [...],
      "summary_dashboard": {...}
    }
  }
```

### Operations Pillar

#### Old → New Mapping
```
POST /api/mvp/operations/sop/create
  → POST /api/operations-pillar/create-standard-operating-procedure

POST /api/mvp/operations/workflow/create
  → POST /api/operations-pillar/create-workflow
```

#### New Semantic Endpoints
```python
# Create SOP
POST /api/operations-pillar/create-standard-operating-procedure
  Body: {
    "description": "Process for data migration",
    "file_ids": ["uuid1"],  # Optional: reference files
    "sop_type": "process",  # or "procedure", "checklist"
    "options": {}
  }
  Response: {
    "success": true,
    "sop_id": "uuid",
    "sop_title": "Data Migration Process",
    "sop_content": {...},
    "created_at": "..."
  }

# Create Workflow
POST /api/operations-pillar/create-workflow
  Body: {
    "name": "Data Migration Workflow",
    "description": "...",
    "sop_id": "optional-uuid",  # Convert from SOP
    "workflow_data": {...}
  }
  Response: {
    "success": true,
    "workflow_id": "uuid",
    "workflow": {...},
    "created_at": "..."
  }

# Convert SOP to Workflow
POST /api/operations-pillar/convert-sop-to-workflow
  Body: {
    "sop_id": "uuid",
    "conversion_options": {}
  }
  Response: {
    "success": true,
    "workflow_id": "uuid",
    "workflow": {...}
  }

# Convert Workflow to SOP
POST /api/operations-pillar/convert-workflow-to-sop
  Body: {
    "workflow_id": "uuid",
    "conversion_options": {}
  }
  Response: {
    "success": true,
    "sop_id": "uuid",
    "sop": {...}
  }

# List SOPs
GET /api/operations-pillar/list-standard-operating-procedures
  Query: ?user_id=...&sop_type=...
  Response: {
    "success": true,
    "sops": [...]
  }

# List Workflows
GET /api/operations-pillar/list-workflows
  Query: ?user_id=...
  Response: {
    "success": true,
    "workflows": [...]
  }
```

### Business Outcomes Pillar

#### Old → New Mapping
```
POST /api/mvp/business-outcomes/roadmap/create
  → POST /api/business-outcomes-pillar/generate-strategic-roadmap

POST /api/mvp/business-outcomes/poc-proposal/create
  → POST /api/business-outcomes-pillar/generate-proof-of-concept-proposal
```

#### New Semantic Endpoints
```python
# Generate Roadmap
POST /api/business-outcomes-pillar/generate-strategic-roadmap
  Body: {
    "pillar_outputs": {
      "content_pillar": {...},
      "insights_pillar": {...},
      "operations_pillar": {...}
    },
    "roadmap_options": {
      "timeline": "12-months",
      "phases": 3
    }
  }
  Response: {
    "success": true,
    "roadmap_id": "uuid",
    "roadmap": {
      "phases": [...],
      "milestones": [...],
      "timeline": {...}
    }
  }

# Generate POC Proposal
POST /api/business-outcomes-pillar/generate-proof-of-concept-proposal
  Body: {
    "pillar_outputs": {...},
    "proposal_options": {
      "scope": "full",
      "timeline": "90-days"
    }
  }
  Response: {
    "success": true,
    "proposal_id": "uuid",
    "proposal": {
      "objectives": [...],
      "scope": {...},
      "timeline": {...},
      "success_criteria": [...]
    }
  }

# Get Pillar Summaries
GET /api/business-outcomes-pillar/get-pillar-summaries
  Query: ?session_id=...
  Response: {
    "success": true,
    "summaries": {
      "content_pillar": {...},
      "insights_pillar": {...},
      "operations_pillar": {...}
    }
  }

# Get Journey Visualization
GET /api/business-outcomes-pillar/get-journey-visualization
  Query: ?session_id=...
  Response: {
    "success": true,
    "visualization": {
      "dashboard": {...},
      "charts": [...],
      "summary_display": {...}
    }
  }
```

### Guide Agent

#### Old → New Mapping
```
POST /api/global/agent/analyze
  → POST /api/guide-agent/analyze-user-intent
```

#### New Semantic Endpoints
```python
# Analyze User Intent
POST /api/guide-agent/analyze-user-intent
  Body: {
    "message": "I want to upload and analyze my business data",
    "user_id": "...",
    "session_token": "..."
  }
  Response: {
    "success": true,
    "intent_analysis": {
      "primary_intent": "upload_and_analyze",
      "confidence": 0.95,
      "recommended_pillar": "content",
      "recommended_actions": [...]
    },
    "session_id": "uuid"
  }

# Get Journey Guidance
POST /api/guide-agent/get-journey-guidance
  Body: {
    "user_goal": "...",
    "current_pillar": "...",
    "session_id": "..."
  }
  Response: {
    "success": true,
    "guidance": {
      "next_steps": [...],
      "recommended_pillar": "...",
      "suggested_actions": [...]
    }
  }

# Get Conversation History
GET /api/guide-agent/get-conversation-history/{session_id}
  Response: {
    "success": true,
    "conversation": {
      "messages": [...],
      "orchestrator_context": {...}
    }
  }
```

### Liaison Agents

#### Old → New Mapping
```
POST /api/liaison/chat
  → POST /api/liaison-agents/{pillar}/chat
```

#### New Semantic Endpoints
```python
# Chat with Content Liaison
POST /api/liaison-agents/content-pillar/chat
  Body: {
    "message": "...",
    "user_id": "...",
    "session_token": "...",
    "conversation_id": "optional"
  }
  Response: {
    "success": true,
    "response": {
      "message": "...",
      "agent": "content_liaison",
      "capabilities": [...]
    },
    "session_id": "uuid"
  }

# Chat with Insights Liaison
POST /api/liaison-agents/insights-pillar/chat

# Chat with Operations Liaison
POST /api/liaison-agents/operations-pillar/chat

# Chat with Business Outcomes Liaison
POST /api/liaison-agents/business-outcomes-pillar/chat
```

### Session Management

#### Old → New Mapping
```
POST /api/global/session
  → POST /api/session/create-user-session

GET  /api/global/session/{session_id}
  → GET  /api/session/get-session-state/{session_id}

DELETE /api/global/session/{session_id}
  → DELETE /api/session/end-user-session/{session_id}
```

#### New Semantic Endpoints
```python
# Create Session
POST /api/session/create-user-session
  Body: {
    "user_id": "...",
    "session_type": "mvp",
    "context": {}
  }
  Response: {
    "success": true,
    "session_id": "uuid",
    "session_token": "token",
    "orchestrator_states": {...},
    "orchestrator_context": {...},
    "conversations": {}
  }

# Get Session State
GET /api/session/get-session-state/{session_id}
  Response: {
    "success": true,
    "session": {
      "session_id": "uuid",
      "user_id": "...",
      "orchestrator_states": {...},
      "orchestrator_context": {...},
      "conversations": {...}
    }
  }

# Update Session State
PUT /api/session/update-session-state/{session_id}
  Body: {
    "state_updates": {...}
  }

# End Session
DELETE /api/session/end-user-session/{session_id}
  Response: {
    "success": true,
    "message": "Session ended"
  }

# Get Orchestrator Context
GET /api/session/get-orchestrator-context/{session_id}
  Response: {
    "success": true,
    "orchestrator_context": {...}
  }

# Get Conversation History
GET /api/session/get-conversation-history/{session_id}
  Query: ?agent_type=guide_agent|content_liaison|...
  Response: {
    "success": true,
    "conversations": {...}
  }
```

---

## Part 3: Implementation Plan

### Phase 1: Build New Semantic APIs (4-6 hours)

**Goal:** New semantic endpoints exist and work, old endpoints still work

**Tasks:**
1. Create new router files for semantic endpoints
2. Implement new endpoint handlers
3. Route to existing service methods (temporary)
4. Add comprehensive request/response models
5. Add API documentation

**Files to Create:**
```
backend/experience/api/semantic/
  ├── content_pillar_router.py
  ├── insights_pillar_router.py
  ├── operations_pillar_router.py
  ├── business_outcomes_pillar_router.py
  ├── guide_agent_router.py
  ├── liaison_agents_router.py
  └── session_router.py
```

**Files to Modify:**
- `backend/experience/api/main_api.py` - Register new routers
- Keep old routers for now (will delete in Phase 4)

**Acceptance Criteria:**
- ✅ All new semantic endpoints exist
- ✅ All new endpoints return proper responses
- ✅ Old endpoints still work
- ✅ API documentation updated

---

### Phase 2: Comprehensive Testing (3-4 hours)

**Goal:** Validate new APIs are equivalent or better than old APIs

**Tasks:**
1. Create test suite for new semantic APIs
2. Create test suite for old APIs (baseline)
3. Compare functionality side-by-side
4. Test all user journeys with new APIs
5. Validate error handling
6. Performance comparison

**Test Files to Create:**
```
tests/e2e/semantic_api/
  ├── test_content_pillar_semantic.py
  ├── test_insights_pillar_semantic.py
  ├── test_operations_semantic.py
  ├── test_business_outcomes_semantic.py
  ├── test_guide_agent_semantic.py
  ├── test_liaison_agents_semantic.py
  └── test_session_semantic.py

tests/e2e/legacy_api/
  ├── test_content_pillar_legacy.py  # Baseline
  ├── test_insights_pillar_legacy.py
  └── ...
```

**Test Strategy:**
```python
# Example: Compare old vs new
async def test_upload_file_equivalence():
    """Test new semantic API matches old API functionality"""
    
    # Test old API
    old_response = await client.post("/api/mvp/content/upload", ...)
    old_file_id = old_response.json()["file_id"]
    
    # Test new API
    new_response = await client.post("/api/content-pillar/upload-file", ...)
    new_file_id = new_response.json()["file_id"]
    
    # Verify same functionality
    assert old_response.status_code == new_response.status_code
    assert old_file_id is not None
    assert new_file_id is not None
    
    # Verify file is same
    old_file = await get_file(old_file_id)
    new_file = await get_file(new_file_id)
    assert old_file == new_file
```

**Acceptance Criteria:**
- ✅ All new API tests pass
- ✅ New APIs match old API functionality
- ✅ New APIs have better error messages
- ✅ New APIs have clearer response structures
- ✅ Performance is equivalent or better

---

### Phase 3: Frontend Migration (4-5 hours)

**Goal:** Frontend uses new semantic APIs exclusively

**Tasks:**
1. Update API client constants
2. Update all API call methods
3. Update component API calls
4. Update error handling
5. Test all frontend flows

**Files to Modify:**
```
symphainy-frontend/lib/api/
  ├── contentPillarApi.ts
  ├── insightsPillarApi.ts
  ├── operationsPillarApi.ts
  ├── businessOutcomesPillarApi.ts
  ├── guideAgentApi.ts
  ├── liaisonAgentsApi.ts
  └── sessionApi.ts
```

**Example Migration:**
```typescript
// Before
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return await api.post('/api/mvp/content/upload', formData);
};

// After
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return await api.post('/api/content-pillar/upload-file', formData);
};
```

**Acceptance Criteria:**
- ✅ All frontend API calls use new endpoints
- ✅ All user journeys work
- ✅ Error handling works
- ✅ E2E tests pass

---

### Phase 4: Remove Old APIs (2-3 hours)

**Goal:** Clean codebase, only semantic APIs remain

**Tasks:**
1. Delete old router files
2. Remove old endpoint registrations
3. Remove old service method aliases
4. Update all documentation
5. Clean up imports and references

**Files to Delete:**
```
backend/experience/api/
  ├── mvp_content_router.py          # DELETE
  ├── mvp_insights_router.py          # DELETE
  ├── mvp_operations_router.py        # DELETE
  ├── mvp_business_outcomes_router.py # DELETE
  └── guide_agent_router.py           # DELETE (old version)
```

**Files to Modify:**
- `backend/experience/api/main_api.py` - Remove old router registrations
- All documentation files
- README files

**Acceptance Criteria:**
- ✅ Old API code removed
- ✅ No references to old endpoints
- ✅ Documentation updated
- ✅ All tests pass
- ✅ Codebase is clean

---

## Part 4: Service Method Updates

### Rename Orchestrators

**Current:**
```
ContentAnalysisOrchestrator
```

**New:**
```
ContentPillarOrchestrator
```

**Files to Rename:**
```
backend/business_enablement/business_orchestrator/use_cases/mvp/
  content_analysis_orchestrator/
    → content_pillar_orchestrator/
      content_analysis_orchestrator.py → content_pillar_orchestrator.py
```

**Files to Update:**
- All imports of `ContentAnalysisOrchestrator`
- Configuration files
- Documentation

---

## Part 5: Testing Strategy

### Test Coverage Requirements

1. **Functional Equivalence**
   - Every old endpoint has equivalent new endpoint
   - Same inputs produce same outputs
   - Same error conditions handled

2. **Semantic Improvement**
   - New endpoints have clearer names
   - Better error messages
   - More informative responses

3. **User Journey Validation**
   - Complete CTO demo journey works
   - All three demo scenarios work
   - All pillar workflows work

4. **Performance**
   - New APIs perform as well or better
   - No regression in response times

### Test Execution Plan

```bash
# Step 1: Run old API tests (baseline)
pytest tests/e2e/legacy_api/ -v

# Step 2: Run new API tests
pytest tests/e2e/semantic_api/ -v

# Step 3: Run equivalence tests
pytest tests/e2e/semantic_api/test_equivalence.py -v

# Step 4: Run E2E journey tests
pytest tests/e2e/test_complete_cto_demo_journey.py -v
pytest tests/e2e/test_three_demo_scenarios_e2e.py -v

# Step 5: Run frontend E2E tests
cd symphainy-frontend && npm run test:e2e
```

---

## Part 6: Rollback Plan

**If issues found during migration:**

1. **Phase 1-2:** No rollback needed (old APIs still work)
2. **Phase 3:** Revert frontend changes, keep using old APIs
3. **Phase 4:** Revert git commit, restore old API code

**Git Strategy:**
```bash
# Create feature branch
git checkout -b semantic-api-migration

# Phase 1-2: Build and test
git commit -m "Add semantic APIs (Phase 1-2)"

# Phase 3: Frontend migration
git commit -m "Migrate frontend to semantic APIs (Phase 3)"

# Phase 4: Remove old APIs
git commit -m "Remove legacy APIs (Phase 4)"

# If rollback needed
git revert <commit-hash>
```

---

## Part 7: Timeline

### Day 1: Build New APIs
- Morning: Create semantic router files
- Afternoon: Implement endpoints, test basic functionality
- **Deliverable:** New APIs exist and work

### Day 2: Comprehensive Testing
- Morning: Create test suites, equivalence tests
- Afternoon: Run all tests, compare old vs new
- **Deliverable:** Confidence new APIs are ready

### Day 3: Frontend Migration
- Morning: Update API clients
- Afternoon: Update components, test flows
- **Deliverable:** Frontend uses new APIs

### Day 4: Cleanup
- Morning: Remove old API code
- Afternoon: Documentation, final testing
- **Deliverable:** Clean codebase, only semantic APIs

**Total: 4 days (32 hours)**

---

## Part 8: Success Criteria

### Technical
- ✅ All new semantic APIs implemented
- ✅ All tests pass (new APIs)
- ✅ Frontend fully migrated
- ✅ Old APIs removed
- ✅ No breaking changes to functionality

### Quality
- ✅ New APIs are more semantic
- ✅ Better error messages
- ✅ Clearer response structures
- ✅ Improved developer experience

### Documentation
- ✅ API documentation updated
- ✅ Migration guide created
- ✅ Examples provided
- ✅ README updated

---

## Part 9: Next Steps

1. **Review this plan** with team
2. **Create feature branch** for migration
3. **Start Phase 1** - Build new semantic APIs
4. **Execute phases sequentially** with testing at each step
5. **Merge when complete** - clean semantic codebase

---

## Conclusion

**Clean break. No backward compatibility.**

This approach:
- ✅ Eliminates technical debt
- ✅ Creates clean, semantic codebase
- ✅ Better developer experience
- ✅ Professional architecture

**Recommended Start:** Phase 1 (Build New Semantic APIs) - can begin immediately.






