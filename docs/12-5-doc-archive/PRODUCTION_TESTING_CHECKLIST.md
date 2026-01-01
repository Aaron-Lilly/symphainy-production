# Production Testing Checklist

**Date:** 2025-12-04  
**Status:** 📋 **COMPREHENSIVE CHECKLIST**

---

## ✅ **Completed Tests**

### Agent Testing (Just Completed)
- ✅ **13/13 Agent Tests Passing**
  - Backend Health (`/health`)
  - Guide Agent (Intent Analysis, Journey Guidance, Conversation History)
  - All 4 Liaison Agent Pillars (Send Message, Conversation History)
  - Liaison Agents Health

### Infrastructure
- ✅ Traefik routing working
- ✅ Health endpoint accessible at `/health`
- ✅ Route discovery working
- ✅ All agent endpoints accessible through Traefik

---

## 📋 **Remaining Production Tests**

### **Phase 1: Critical Paths** (Do First - ~30 minutes)

#### **1. HTTP Endpoint Smoke Tests** ⏳
**File:** `tests/e2e/production/test_api_smoke.py`  
**Issue:** Tests are trying to connect to `localhost:8000` directly, need to update to use Traefik routes (`http://localhost/api/*`)

**Tests to Verify:**
- [ ] `/api/auth/register` - User registration
- [ ] `/api/auth/login` - User authentication  
- [ ] `/api/v1/session/create-user-session` - Session creation
- [ ] `/api/v1/content-pillar/upload-file` - File upload
- [ ] `/api/v1/insights-pillar/analyze-content` - Content analysis
- [ ] `/api/v1/operations-pillar/create-standard-operating-procedure` - SOP creation
- [ ] `/api/v1/business-outcomes-pillar/generate-strategic-roadmap` - Roadmap generation

**Action:** Update test to use `http://localhost/api/*` instead of `http://localhost:8000/*`

---

#### **2. WebSocket Connection Tests** ⏳
**File:** `tests/e2e/production/test_websocket_smoke.py`

**Tests to Verify:**
- [ ] `/api/ws/guide` - Guide Agent WebSocket
- [ ] `/api/ws/liaison/content` - Content Liaison WebSocket
- [ ] `/api/ws/liaison/insights` - Insights Liaison WebSocket
- [ ] `/api/ws/liaison/operations` - Operations Liaison WebSocket
- [ ] `/api/ws/liaison/business_outcomes` - Business Outcomes Liaison WebSocket

**Action:** Verify WebSocket connections work through Traefik

---

#### **3. Infrastructure Health Checks** ⏳
**File:** `tests/e2e/production/smoke_tests/test_platform_health.py` (or create new)

**Tests to Verify:**
- [ ] Core containers running (Consul, ArangoDB, Redis, Meilisearch)
- [ ] Consul accessible and healthy
- [ ] Redis accessible and healthy
- [ ] ArangoDB accessible and healthy
- [ ] Backend container healthy
- [ ] Frontend container healthy
- [ ] Traefik container healthy
- [ ] Observability services running (Loki, Grafana, Tempo, OTel Collector)

**Action:** Create/run infrastructure health check tests

---

#### **4. Production Startup Sequence** ⏳
**File:** `tests/e2e/production/test_production_startup_sequence.py`

**Tests to Verify:**
- [ ] All foundation services initialize
- [ ] Manager hierarchy bootstraps correctly
- [ ] Realm services initialize
- [ ] Service discovery works (Curator)
- [ ] Health checks pass
- [ ] No startup errors or warnings
- [ ] All routes registered with Curator

**Action:** Run startup sequence test

---

### **Phase 2: Core Functionality** (~1-2 hours)

#### **5. Content Pillar Capabilities** ⏳
**File:** `tests/e2e/production/test_content_pillar_capabilities.py`  
**Also:** `tests/e2e/production/smoke_tests/test_content_pillar_smoke.py`

**Tests to Verify:**
- [ ] File upload (CSV, Excel, PDF, DOCX, JSON, TXT, images, COBOL)
- [ ] File parsing
- [ ] File preview
- [ ] Metadata extraction
- [ ] File listing
- [ ] File details retrieval

---

#### **6. Insights Pillar Capabilities** ⏳
**File:** `tests/e2e/production/test_insights_pillar_capabilities.py`  
**Also:** `tests/e2e/production/smoke_tests/test_insights_pillar_smoke.py`

**Tests to Verify:**
- [ ] Analyze structured content
- [ ] Analyze unstructured content
- [ ] Get analysis results
- [ ] Get visualizations
- [ ] Query analysis
- [ ] Metadata validation

---

#### **7. Operations Pillar Capabilities** ⏳
**File:** `tests/e2e/production/test_operations_pillar_capabilities.py`  
**Also:** `tests/e2e/production/smoke_tests/test_operations_pillar_smoke.py`

**Tests to Verify:**
- [ ] Create SOP from file
- [ ] Create workflow from file
- [ ] List SOPs
- [ ] List workflows
- [ ] SOP→Workflow conversion
- [ ] Workflow optimization

---

#### **8. Business Outcomes Pillar Capabilities** ⏳
**File:** `tests/e2e/production/test_business_outcomes_pillar_capabilities.py`  
**Also:** `tests/e2e/production/smoke_tests/test_business_outcomes_smoke.py`

**Tests to Verify:**
- [ ] Generate strategic roadmap
- [ ] Generate POC plan
- [ ] Get journey visualization
- [ ] Track business outcomes
- [ ] Generate recommendations

---

### **Phase 3: Integration** (~1 hour)

#### **9. Cross-Pillar Workflows** ⏳
**File:** `tests/e2e/production/test_cross_pillar_workflows.py`

**Tests to Verify:**
- [ ] Content → Insights workflow (upload file → analyze → get insights)
- [ ] Insights → Operations workflow (analyze → create SOP/workflow)
- [ ] Operations → Business Outcomes workflow (SOP/workflow → roadmap)
- [ ] Complete MVP journey (all 4 pillars in sequence)

---

#### **10. Frontend-Backend Integration** ⏳
**File:** `tests/e2e/production/test_frontend_backend_integration_http.py`

**Tests to Verify:**
- [ ] Frontend can reach backend through Traefik
- [ ] API responses match frontend expectations
- [ ] CORS headers correct
- [ ] Error responses properly formatted
- [ ] Authentication flow works

---

#### **11. Real User Scenarios** ⏳
**File:** `tests/e2e/production/test_real_user_scenarios.py`

**Tests to Verify:**
- [ ] New user registration and onboarding
- [ ] Complete file upload and analysis workflow
- [ ] Multi-file upload and batch processing
- [ ] User switching between pillars
- [ ] Session persistence across pillar switches
- [ ] Error recovery scenarios

---

### **Phase 4: Advanced** (~1 hour)

#### **12. State Management** ⏳
**File:** `tests/e2e/production/test_state_management.py`

**Tests to Verify:**
- [ ] Session state persistence
- [ ] Conversation history persistence
- [ ] File state persistence
- [ ] Orchestrator context persistence
- [ ] State recovery after restart

---

#### **13. Real File Upload Flow** ⏳
**File:** `tests/e2e/production/test_real_file_upload_flow.py`

**Tests to Verify:**
- [ ] File upload to GCS
- [ ] Metadata storage in Supabase
- [ ] File parsing workflow
- [ ] Error handling for invalid files
- [ ] File cleanup on errors

---

#### **14. Complex Integration Scenarios** ⏳
**File:** `tests/e2e/production/test_complex_integration_scenarios.py`

**Tests to Verify:**
- [ ] Multiple concurrent users
- [ ] Large file uploads
- [ ] Long-running analysis jobs
- [ ] Service failure recovery
- [ ] Network interruption recovery

---

#### **15. User Journey Smoke Test** ⏳
**File:** `tests/e2e/production/test_user_journey_smoke.py`

**Tests to Verify:**
- [ ] Complete end-to-end user journey
- [ ] All pillars accessible
- [ ] Navigation between pillars works
- [ ] Data persists across pillar switches

---

#### **16. Authentication Flow** ⏳
**File:** `tests/e2e/production/smoke_tests/test_authentication_flow.py`

**Tests to Verify:**
- [ ] User registration
- [ ] User login
- [ ] Session creation
- [ ] Authentication token validation
- [ ] Logout

---

#### **17. API Contracts** ⏳
**Files:** `tests/e2e/production/api_contracts/*.py`

**Tests to Verify:**
- [ ] API response structures match contracts
- [ ] Error handling follows contracts
- [ ] Semantic API contracts validated

---

## 🎯 **Recommended Testing Order**

### **Immediate Priority (Today)**
1. ✅ **Agent Testing** - DONE (13/13 passing)
2. ⏳ **HTTP Endpoint Smoke Tests** - Fix to use Traefik routes
3. ⏳ **WebSocket Tests** - Verify through Traefik
4. ⏳ **Infrastructure Health Checks** - Verify all services

### **High Priority (This Week)**
5. ⏳ **Production Startup Sequence** - Verify clean startup
6. ⏳ **Content Pillar Capabilities** - Core functionality
7. ⏳ **Insights Pillar Capabilities** - Core functionality
8. ⏳ **Cross-Pillar Workflows** - Integration

### **Medium Priority (Next Week)**
9. ⏳ **Operations Pillar Capabilities**
10. ⏳ **Business Outcomes Pillar Capabilities**
11. ⏳ **Frontend-Backend Integration**
12. ⏳ **Real User Scenarios**

### **Lower Priority (Before Full Production)**
13. ⏳ **State Management**
14. ⏳ **Real File Upload Flow**
15. ⏳ **Complex Integration Scenarios**
16. ⏳ **User Journey Smoke Test**
17. ⏳ **Authentication Flow**
18. ⏳ **API Contracts**

---

## 📊 **Test Status Summary**

| Category | Tests | Status | Priority |
|----------|-------|--------|----------|
| **Agent Testing** | 13/13 | ✅ Complete | ✅ Done |
| **HTTP Endpoints** | 0/9 | ⏳ Needs Fix | 🔴 High |
| **WebSockets** | ?/5 | ⏳ Pending | 🔴 High |
| **Infrastructure** | ?/8 | ⏳ Pending | 🔴 High |
| **Startup Sequence** | ?/6 | ⏳ Pending | 🔴 High |
| **Content Pillar** | ?/6 | ⏳ Pending | 🟡 Medium |
| **Insights Pillar** | ?/6 | ⏳ Pending | 🟡 Medium |
| **Operations Pillar** | ?/6 | ⏳ Pending | 🟡 Medium |
| **Business Outcomes** | ?/5 | ⏳ Pending | 🟡 Medium |
| **Cross-Pillar** | ?/4 | ⏳ Pending | 🟡 Medium |
| **Integration** | ?/5 | ⏳ Pending | 🟡 Medium |
| **User Scenarios** | ?/6 | ⏳ Pending | 🟢 Low |
| **State Management** | ?/5 | ⏳ Pending | 🟢 Low |
| **File Upload** | ?/5 | ⏳ Pending | 🟢 Low |
| **Complex Scenarios** | ?/5 | ⏳ Pending | 🟢 Low |

**Total Estimated Tests:** ~95 tests

---

## 🚀 **Next Immediate Steps**

1. **Fix HTTP Endpoint Smoke Tests** - Update to use Traefik routes (`http://localhost/api/*`)
2. **Run WebSocket Tests** - Verify real-time communication works through Traefik
3. **Run Infrastructure Health Checks** - Verify all services healthy
4. **Run Production Startup Sequence** - Verify clean startup

**Estimated Time:** 30-60 minutes for Phase 1 (Critical Paths)

---

## 📝 **Notes**

- All tests should use Traefik routes (`http://localhost/api/*` or `http://localhost/health`)
- Tests should not connect directly to `localhost:8000` or `localhost:3000`
- WebSocket tests should use `ws://localhost/api/ws/*`
- Infrastructure tests can use direct container access or Traefik routes

---

**Current Status:** Agent testing complete. Ready to proceed with Phase 1 (Critical Paths) testing.


