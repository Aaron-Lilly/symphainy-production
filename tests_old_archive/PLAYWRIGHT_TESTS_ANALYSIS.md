# Playwright Tests Analysis & Update Plan

**Date:** December 2024  
**Status:** Analysis Complete - Updates Needed

---

## 📊 Current State

### **Frontend TypeScript Playwright Tests** (`symphainy-frontend/tests/e2e/`)

**Active Tests:**
1. ✅ `semantic-components.spec.ts` - Uses semantic APIs (mostly correct)
2. ✅ `critical-user-journeys.spec.ts` - Mostly commented out, basic page load tests
3. ⚠️ `mvp-4-pillar-journey.spec.ts` - **TEMPORARILY COMMENTED OUT** (needs test IDs)
4. ✅ `content-pillar.spec.ts` - Uses old API paths (needs update)
5. ⚠️ `operations-pillar.spec.ts` - Uses old API paths (needs update)
6. ✅ `landing-page.spec.ts` - Basic page load
7. ✅ `insights-parquet-e2e.spec.ts` - Specific feature test
8. ✅ `insights-multioutput.spec.ts` - Specific feature test
9. ✅ `experience-pillar.spec.ts` - Basic page load
10. ✅ `validation-test.spec.ts` - Basic validation

### **Python E2E Tests** (`tests/e2e/`)

**Active Tests:**
1. ✅ `test_api_endpoints_reality.py` - Uses `backend_server` fixture (ready)
2. ✅ `test_semantic_apis_e2e.py` - Uses `backend_server` fixture (ready)
3. ⚠️ `test_three_demo_scenarios_e2e.py` - Uses old API paths (needs update)

### **Integration Tests** (`tests/integration/layer_9_journey/`)

**Active Tests:**
1. ✅ `test_cto_demo_scenarios_e2e.py` - Uses MVP Journey Orchestrator (ready)
2. ✅ `test_journey_e2e.py` - Uses MVP Journey Orchestrator (ready)

---

## 🔍 Issues Found

### **1. API Path Mismatches**

#### **Frontend TypeScript Tests:**

**File:** `symphainy-frontend/tests/e2e/content-pillar.spec.ts`
- ❌ Line 52: `http://localhost:8000/fms/files` → Should be `/api/v1/content-pillar/list-uploaded-files`
- ❌ Uses old FMS paths instead of semantic API paths

**File:** `symphainy-frontend/tests/operations-pillar.spec.ts`
- ❌ Line 36: `**/api/operations/wizard/start` → Should be `/api/v1/operations-pillar/*`
- ❌ Line 67: `**/api/operations/files` → Should be `/api/v1/operations-pillar/*`
- ❌ Line 83: `**/api/operations/sop-to-workflow` → Should be `/api/v1/operations-pillar/convert-sop-to-workflow`

**File:** `symphainy-frontend/tests/e2e/critical-user-journeys.spec.ts`
- ⚠️ Line 221: `**/api/insights` → Should be `/api/v1/insights-pillar/*` (but test is commented out)

**File:** `symphainy-frontend/tests/e2e/mvp-4-pillar-journey.spec.ts`
- ⚠️ Lines 425, 627, 639: `**/api/insights/anomaly` → Should be `/api/v1/insights-pillar/*` (but test is commented out)

#### **Python E2E Tests:**

**File:** `tests/e2e/test_three_demo_scenarios_e2e.py`
- ❌ Line 75: `/api/global/session` → Should be `/api/v1/session/create-user-session`
- ❌ Line 151: `/api/global/agent/analyze` → Should be `/api/v1/guide-agent/analyze-user-intent`
- ❌ Line 201: `/api/mvp/content/upload` → Should be `/api/v1/content-pillar/upload-file`
- ❌ Line 266: `/api/mvp/content/parse/{file_id}` → Should be `/api/v1/content-pillar/process-file/{file_id}`
- ❌ Line 332: `/api/mvp/content/upload` → Should be `/api/v1/content-pillar/upload-file`
- ❌ Line 482: `/api/liaison/chat` → Should be `/api/v1/liaison-agents/send-message-to-pillar-agent`
- ❌ Line 615: `/api/liaison/chat` → Should be `/api/v1/liaison-agents/send-message-to-pillar-agent`
- ❌ Line 640: `/api/liaison/chat` → Should be `/api/v1/liaison-agents/send-message-to-pillar-agent`
- ❌ Line 680: `/api/operations/generate_workflow_from_sop` → Should be `/api/v1/operations-pillar/convert-sop-to-workflow`
- ❌ Line 723: `/api/operations/generate_sop_from_workflow` → Should be `/api/v1/operations-pillar/convert-workflow-to-sop`
- ❌ Line 854: `/api/business-outcomes-pillar/generate-strategic-roadmap` → Should be `/api/v1/business-outcomes-pillar/generate-strategic-roadmap` (may be correct, verify)

---

## ✅ What's Already Correct

### **Frontend TypeScript Tests:**

**File:** `symphainy-frontend/tests/e2e/semantic-components.spec.ts`
- ✅ Uses semantic API paths correctly:
  - `/api/content-pillar/upload-file`
  - `/api/content-pillar/list-uploaded-files`
  - `/api/content-pillar/process-file/{fileId}`
  - `/api/content-pillar/get-file-details/{fileId}`

**File:** `symphainy-frontend/tests/e2e/global-setup.ts`
- ✅ Uses `/api/auth/register` and `/api/auth/login` (correct, not versioned)

---

## 📋 Update Plan

### **Priority 1: Python E2E Tests** (High Priority)

**File:** `tests/e2e/test_three_demo_scenarios_e2e.py`

**Updates Needed:**
1. Replace `/api/global/session` → `/api/v1/session/create-user-session`
2. Replace `/api/global/agent/analyze` → `/api/v1/guide-agent/analyze-user-intent`
3. Replace `/api/mvp/content/upload` → `/api/v1/content-pillar/upload-file`
4. Replace `/api/mvp/content/parse/{file_id}` → `/api/v1/content-pillar/process-file/{file_id}`
5. Replace `/api/liaison/chat` → `/api/v1/liaison-agents/send-message-to-pillar-agent`
6. Replace `/api/operations/generate_workflow_from_sop` → `/api/v1/operations-pillar/convert-sop-to-workflow`
7. Replace `/api/operations/generate_sop_from_workflow` → `/api/v1/operations-pillar/convert-workflow-to-sop`
8. Add `both_servers` fixture for Playwright tests
9. Update request payloads to match new API structure

**Estimated Time:** 2-3 hours

---

### **Priority 2: Frontend TypeScript Tests** (Medium Priority)

**File:** `symphainy-frontend/tests/e2e/content-pillar.spec.ts`

**Updates Needed:**
1. Replace `http://localhost:8000/fms/files` → `/api/v1/content-pillar/list-uploaded-files`
2. Update all API calls to use semantic paths
3. Add proper request headers and payloads

**File:** `symphainy-frontend/tests/operations-pillar.spec.ts`

**Updates Needed:**
1. Replace `**/api/operations/wizard/start` → `/api/v1/operations-pillar/*`
2. Replace `**/api/operations/files` → `/api/v1/operations-pillar/list-workflows` or similar
3. Replace `**/api/operations/sop-to-workflow` → `/api/v1/operations-pillar/convert-sop-to-workflow`
4. Update request payloads

**Estimated Time:** 1-2 hours

---

### **Priority 3: Enable Commented Tests** (Low Priority)

**File:** `symphainy-frontend/tests/e2e/mvp-4-pillar-journey.spec.ts`

**Status:** Entirely commented out - needs frontend test IDs

**Action:** 
- Coordinate with frontend team to add `data-testid` attributes
- Update API paths when uncommenting
- Add `both_servers` fixture support (if converting to Python)

**Estimated Time:** 4-6 hours (depends on frontend work)

---

## 🎯 CTO Demo Scenarios Alignment

### **Current CTO Demo Tests:**

1. ✅ **Integration Tests** (`test_cto_demo_scenarios_e2e.py`):
   - Uses MVP Journey Orchestrator (correct)
   - Tests backend orchestration (not HTTP)
   - ✅ **No updates needed**

2. ⚠️ **E2E HTTP Tests** (`test_three_demo_scenarios_e2e.py`):
   - Tests HTTP API endpoints
   - Uses old API paths
   - ❌ **Needs updates** (Priority 1)

3. ⚠️ **Frontend Playwright Tests** (`mvp-4-pillar-journey.spec.ts`):
   - Entirely commented out
   - Needs frontend test IDs
   - ⚠️ **Future work** (Priority 3)

---

## 🚀 Recommended Next Steps

1. **Update Python E2E Tests** (Priority 1)
   - Fix `test_three_demo_scenarios_e2e.py` API paths
   - Add `both_servers` fixture
   - Test with actual frontend

2. **Update Frontend TypeScript Tests** (Priority 2)
   - Fix `content-pillar.spec.ts` API paths
   - Fix `operations-pillar.spec.ts` API paths
   - Verify tests pass with updated APIs

3. **Create New Playwright E2E Tests** (Priority 3)
   - Create Python Playwright tests for CTO scenarios
   - Use `both_servers` fixture
   - Test full user journey through frontend

---

## 📝 Notes

- **Frontend API Managers:** Already updated ✅
- **Backend Handlers:** Already added ✅
- **Test Fixtures:** Already created ✅
- **API Path Updates:** Needed in test files ❌

**Last Updated:** December 2024

