# API Endpoint Comparison: Backend vs Frontend

**Date:** December 2024  
**Purpose:** Document all API endpoints to identify mismatches before testing  
**Principle:** Backend is source of truth - frontend should adapt to backend architecture

---

## 🎯 Backend API Architecture

### **Universal Router Pattern**
**File:** `symphainy-platform/backend/api/universal_pillar_router.py`

**Route Pattern:** `/api/v1/{pillar}/{path:path}`

**Supported Pillars:**
- `content-pillar` → ContentAnalysisOrchestrator
- `insights-pillar` → InsightsOrchestrator
- `operations-pillar` → OperationsOrchestrator
- `business-outcomes-pillar` → BusinessOutcomesOrchestrator

**How it works:**
1. Universal router receives all requests
2. Routes to `FrontendGatewayService.route_frontend_request()`
3. FrontendGatewayService routes to appropriate orchestrator
4. Response transformed for frontend

---

## 📋 Backend Endpoints (What Backend Provides)

### **Content Pillar** (`/api/v1/content-pillar/*`)
Based on FrontendGatewayService and ContentAnalysisOrchestrator:

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/content-pillar/upload-file` | Upload file (with optional copybook) | ✅ Expected |
| GET | `/api/v1/content-pillar/list-uploaded-files` | List user files | ✅ Expected |
| GET | `/api/v1/content-pillar/get-file-details/{file_id}` | Get file metadata | ✅ Expected |
| POST | `/api/v1/content-pillar/process-file/{file_id}` | Process file (parse, extract) | ✅ Expected |
| GET | `/api/v1/content-pillar/health` | Health check | ✅ Expected |

**Note:** Backend uses universal router, so any path under `/api/v1/content-pillar/*` is routed to FrontendGatewayService.

---

### **Insights Pillar** (`/api/v1/insights-pillar/*`)

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/insights-pillar/analyze-content-for-insights` | Analyze content | ✅ Expected |
| GET | `/api/v1/insights-pillar/get-analysis-results/{analysis_id}` | Get analysis results | ✅ Expected |
| GET | `/api/v1/insights-pillar/get-visualizations/{analysis_id}` | Get visualizations | ✅ Expected |
| GET | `/api/v1/insights-pillar/health` | Health check | ✅ Expected |

**Note:** Frontend uses `/api/v1/insights-pillar/analysis-results/{analysis_id}` and `/api/v1/insights-pillar/analysis-visualizations/{analysis_id}` - need to verify exact paths.

---

### **Operations Pillar** (`/api/v1/operations-pillar/*`)

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/operations-pillar/create-standard-operating-procedure` | Create SOP | ✅ Expected |
| GET | `/api/v1/operations-pillar/list-standard-operating-procedures` | List SOPs | ✅ Expected |
| POST | `/api/v1/operations-pillar/create-workflow` | Create workflow | ✅ Expected |
| GET | `/api/v1/operations-pillar/list-workflows` | List workflows | ✅ Expected |
| POST | `/api/v1/operations-pillar/convert-sop-to-workflow` | Convert SOP → Workflow | ✅ Expected |
| POST | `/api/v1/operations-pillar/convert-workflow-to-sop` | Convert Workflow → SOP | ✅ Expected |
| GET | `/api/v1/operations-pillar/health` | Health check | ✅ Expected |

---

### **Business Outcomes Pillar** (`/api/v1/business-outcomes-pillar/*`)

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/business-outcomes-pillar/generate-strategic-roadmap` | Generate roadmap | ✅ Expected |
| POST | `/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal` | Generate POC | ✅ Expected |
| GET | `/api/v1/business-outcomes-pillar/get-pillar-summaries` | Get summaries | ✅ Expected |
| GET | `/api/v1/business-outcomes-pillar/get-journey-visualization` | Get visualization | ✅ Expected |
| GET | `/api/v1/business-outcomes-pillar/health` | Health check | ✅ Expected |

---

### **Session Management** (`/api/v1/session/*`)

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/session/create-user-session` | Create session | ✅ Expected |
| GET | `/api/v1/session/get-session-details/{session_id}` | Get session details | ✅ Expected |
| GET | `/api/v1/session/get-session-state/{session_id}` | Get session state | ✅ Expected |
| GET | `/api/v1/session/health` | Health check | ✅ Expected |

---

### **Guide Agent** (`/api/v1/guide-agent/*`)

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/guide-agent/analyze-user-intent` | Analyze intent | ✅ Expected |
| POST | `/api/v1/guide-agent/get-journey-guidance` | Get guidance | ✅ Expected |
| GET | `/api/v1/guide-agent/get-conversation-history/{session_id}` | Get history | ✅ Expected |
| GET | `/api/v1/guide-agent/health` | Health check | ✅ Expected |

---

### **Liaison Agents** (`/api/v1/liaison-agents/*`)

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/liaison-agents/send-message-to-pillar-agent` | Send message | ✅ Expected |
| GET | `/api/v1/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}` | Get history | ✅ Expected |
| GET | `/api/v1/liaison-agents/health` | Health check | ✅ Expected |

---

## 📱 Frontend Endpoints (What Frontend Expects)

### **Content Pillar** - ContentAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/api/v1/content-pillar/list-uploaded-files` | List files | ✅ **MATCHES** |
| POST | `/api/v1/content-pillar/upload-file` | Upload file | ✅ **MATCHES** |
| GET | `/api/v1/content-pillar/get-file-details/{fileId}` | Get metadata | ✅ **MATCHES** |
| POST | `/api/v1/content-pillar/process-file/{fileId}` | Process file | ✅ **MATCHES** |
| DELETE | `/api/content/{fileId}` | Delete file | ⚠️ **LEGACY** (semantic endpoint may not exist) |
| POST | `/api/content/{fileId}/metadata` | Extract metadata | ⚠️ **LEGACY** |
| POST | `/api/content/{fileId}/analyze` | Analyze content | ⚠️ **LEGACY** |
| POST | `/api/content/search` | Search content | ⚠️ **LEGACY** |
| GET | `/api/content/health` | Health check | ⚠️ **LEGACY** |

**Analysis:**
- ✅ Core semantic APIs match perfectly
- ⚠️ Some legacy methods still use old endpoints (may need backend support or frontend update)

---

### **Insights Pillar** - InsightsAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/insights-pillar/analyze-content-for-insights` | Analyze content | ⚠️ **NEEDS VERIFICATION** |
| GET | `/api/v1/insights-pillar/analysis-results/{analysisId}` | Get results | ✅ **MATCHES** |
| GET | `/api/v1/insights-pillar/analysis-visualizations/{analysisId}` | Get visualizations | ✅ **MATCHES** |

**Analysis:**
- ✅ Analysis results and visualizations endpoints match perfectly!
- ⚠️ **NEEDS VERIFICATION:** Frontend uses `/analyze-content-for-insights` but backend uses `/analyze-content` - need to check if backend supports both

---

### **Operations Pillar** - OperationsAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/business_enablement/operations/create-standard-operating-procedure` | Create SOP | ❌ **WRONG PATH** |
| GET | `/api/v1/business_enablement/operations/list-standard-operating-procedures` | List SOPs | ❌ **WRONG PATH** |
| POST | `/api/v1/business_enablement/operations/create-workflow` | Create workflow | ❌ **WRONG PATH** |
| GET | `/api/v1/business_enablement/operations/list-workflows` | List workflows | ❌ **WRONG PATH** |
| POST | `/api/v1/operations-pillar/session/elements` | Get session elements | ⚠️ **NEEDS VERIFICATION** |
| POST | `/api/v1/operations-pillar/coexistence/analyze` | Analyze coexistence | ⚠️ **NEEDS VERIFICATION** |
| POST | `/api/v1/operations-pillar/process/{processId}/optimize` | Optimize process | ⚠️ **NEEDS VERIFICATION** |
| POST | `/api/v1/operations-pillar/compliance/check` | Check compliance | ⚠️ **NEEDS VERIFICATION** |
| GET | `/api/v1/operations-pillar/health` | Health check | ✅ **MATCHES** |

**Analysis:**
- ❌ **CRITICAL ISSUE:** Frontend uses `/api/v1/business_enablement/operations/*` but backend uses `/api/v1/operations-pillar/*`
- ⚠️ Some endpoints may not have semantic equivalents yet

**Recommendation:** Update frontend to use `/api/v1/operations-pillar/*` (backend is source of truth)

---

### **Business Outcomes Pillar** - BusinessOutcomesAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/business-outcomes-pillar/generate-strategic-roadmap` | Generate roadmap | ✅ **MATCHES** |
| POST | `/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal` | Generate POC | ✅ **MATCHES** |
| GET | `/api/v1/business-outcomes-pillar/get-pillar-summaries` | Get summaries | ✅ **MATCHES** |
| GET | `/api/v1/business-outcomes-pillar/get-journey-visualization` | Get visualization | ✅ **MATCHES** |

**Analysis:**
- ✅ All endpoints match perfectly!

---

### **Session Management** - SessionAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/session/create-user-session` | Create session | ⚠️ **PATH MISMATCH** |
| GET | `/api/session/get-session-details/{sessionId}` | Get details | ⚠️ **PATH MISMATCH** |
| GET | `/api/session/get-session-state/{sessionId}` | Get state | ⚠️ **PATH MISMATCH** |

**Analysis:**
- ⚠️ **ISSUE:** Frontend uses `/api/session/*` but backend expects `/api/v1/session/*`
- **Recommendation:** Update frontend to use `/api/v1/session/*` (backend is source of truth)

---

### **Guide Agent** - GuideAgentAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/v1/journey/guide-agent/analyze-user-intent` | Analyze intent | ⚠️ **PATH MISMATCH** |
| POST | `/api/v1/journey/guide-agent/get-journey-guidance` | Get guidance | ⚠️ **PATH MISMATCH** |
| GET | `/api/v1/journey/guide-agent/get-conversation-history/{sessionId}` | Get history | ⚠️ **PATH MISMATCH** |

**Analysis:**
- ⚠️ **ISSUE:** Frontend uses `/api/v1/journey/guide-agent/*` but backend expects `/api/v1/guide-agent/*`
- **Recommendation:** Update frontend to use `/api/v1/guide-agent/*` (backend is source of truth)

---

## 🔍 Identified Issues

### **Critical Mismatches** ❌

1. **Operations Pillar Path Mismatch** (CRITICAL)
   - Frontend: `/api/v1/business_enablement/operations/*`
   - Backend: `/api/v1/operations-pillar/*`
   - **Affected Methods:** `createSOP()`, `listSOPs()`, `createWorkflow()`, `listWorkflows()`, `convertSOPToWorkflow()`, `convertWorkflowToSOP()`
   - **Fix:** Update frontend OperationsAPIManager.ts (6 methods)
   - **File:** `symphainy-frontend/shared/managers/OperationsAPIManager.ts`
   - **Lines:** 150, 188, 214, 252, 278, 318

2. **Insights Pillar Paths** ✅ **ACTUALLY MATCHES!**
   - Frontend: `/api/v1/insights-pillar/analysis-results/{id}`
   - Backend: `/api/v1/insights-pillar/analysis-results/{id}` (FrontendGatewayService line 672)
   - **Status:** ✅ **NO FIX NEEDED** - Frontend is correct!

   - Frontend: `/api/v1/insights-pillar/analysis-visualizations/{id}`
   - Backend: `/api/v1/insights-pillar/analysis-visualizations/{id}` (FrontendGatewayService line 679)
   - **Status:** ✅ **NO FIX NEEDED** - Frontend is correct!

3. **Session Management Path Mismatch**
   - Frontend: `/api/session/*`
   - Backend: `/api/v1/session/*`
   - **Affected Methods:** `createUserSession()`, `getSessionDetails()`, `getSessionState()`
   - **Fix:** Update frontend SessionAPIManager.ts (3 methods)
   - **File:** `symphainy-frontend/shared/managers/SessionAPIManager.ts`
   - **Lines:** 62, 118, 156

4. **Guide Agent Path Mismatch**
   - Frontend: `/api/v1/journey/guide-agent/*`
   - Backend: `/api/v1/guide-agent/*`
   - **Affected Methods:** `analyzeUserIntent()`, `getJourneyGuidance()`, `getConversationHistory()`
   - **Fix:** Update frontend GuideAgentAPIManager.ts (3 methods)
   - **File:** `symphainy-frontend/shared/managers/GuideAgentAPIManager.ts`
   - **Lines:** 71, 117, 163

5. **Liaison Agents Path Mismatch**
   - Frontend: `/api/liaison-agents/*` (no v1)
   - Backend: `/api/v1/liaison-agents/*`
   - **Affected Methods:** `sendMessageToPillarAgent()`, `getPillarConversationHistory()`
   - **Fix:** Update frontend LiaisonAgentsAPIManager.ts (2 methods)
   - **File:** `symphainy-frontend/shared/managers/LiaisonAgentsAPIManager.ts`
   - **Lines:** 59, 108

### **Legacy Endpoints** ⚠️

These may need backend support or frontend migration:

- `/api/content/*` (legacy content endpoints)
- `/api/content/{fileId}/metadata`
- `/api/content/{fileId}/analyze`
- `/api/content/search`

### **Endpoints Needing Verification** ⚠️

- Operations pillar session/elements, coexistence, optimization, compliance endpoints
- Need to check if backend FrontendGatewayService handles these

### **Liaison Agents** - LiaisonAgentsAPIManager.ts

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/liaison-agents/send-message-to-pillar-agent` | Send message | ⚠️ **PATH MISMATCH** |
| GET | `/api/liaison-agents/get-pillar-conversation-history/{sessionId}/{pillar}` | Get history | ⚠️ **PATH MISMATCH** |

**Analysis:**
- ⚠️ **ISSUE:** Frontend uses `/api/liaison-agents/*` (no v1) but backend expects `/api/v1/liaison-agents/*`
- **Recommendation:** Update frontend to use `/api/v1/liaison-agents/*` (backend is source of truth)

---

## 📊 Summary

| Category | Count | Status |
|----------|-------|--------|
| ✅ Matching endpoints | ~22 | Excellent |
| ❌ Critical mismatches | 4 | Need frontend updates (14 method calls) |
| ⚠️ Needs verification | 1 | Check if backend supports frontend path |
| ⚠️ Legacy endpoints | ~5 | May need backend support or frontend migration |
| ⚠️ Needs verification | ~5 | Need to check backend support |

### **Mismatch Breakdown:**

1. **Operations Pillar:** 6 methods need path update (`/api/v1/business_enablement/operations/*` → `/api/v1/operations-pillar/*`)
2. **Insights Pillar:** 1 method needs verification (`/analyze-content-for-insights` vs `/analyze-content`)
3. **Session Management:** 3 methods need path update (`/api/session/*` → `/api/v1/session/*`)
4. **Guide Agent:** 3 methods need path update (`/api/v1/journey/guide-agent/*` → `/api/v1/guide-agent/*`)
5. **Liaison Agents:** 2 methods need path update (`/api/liaison-agents/*` → `/api/v1/liaison-agents/*`)

**Total:** 15 method calls across 5 API managers need updates/verification

---

## 🎯 Next Steps

1. ✅ **Complete reading all frontend API managers** - DONE
2. **Check FrontendGatewayService** to verify what endpoints it actually handles
3. ✅ **Create fix list** - DONE (see below)
4. **Prioritize fixes** (critical mismatches first)
5. **Update frontend** to match backend architecture (backend is source of truth)

---

## 🔧 Fix List (Frontend Updates Required)

### **Priority 1: Critical Path Mismatches** (Must Fix)

#### **1. OperationsAPIManager.ts** - 6 methods
**File:** `symphainy-frontend/shared/managers/OperationsAPIManager.ts`

**Changes needed:**
- Line 150: `/api/v1/business_enablement/operations/create-standard-operating-procedure` → `/api/v1/operations-pillar/create-standard-operating-procedure`
- Line 188: `/api/v1/business_enablement/operations/list-standard-operating-procedures` → `/api/v1/operations-pillar/list-standard-operating-procedures`
- Line 214: `/api/v1/business_enablement/operations/create-workflow` → `/api/v1/operations-pillar/create-workflow`
- Line 252: `/api/v1/business_enablement/operations/list-workflows` → `/api/v1/operations-pillar/list-workflows`
- Line 278: `/api/v1/business_enablement/operations/create-workflow` → `/api/v1/operations-pillar/convert-sop-to-workflow` (also fix conversion logic)
- Line 318: `/api/v1/business_enablement/operations/create-standard-operating-procedure` → `/api/v1/operations-pillar/convert-workflow-to-sop` (also fix conversion logic)

#### **2. InsightsAPIManager.ts** - 1 method needs verification
**File:** `symphainy-frontend/shared/managers/InsightsAPIManager.ts`

**Verification needed:**
- Line 67: Frontend uses `/api/v1/insights-pillar/analyze-content-for-insights` but backend uses `/api/v1/insights-pillar/analyze-content`
- **Action:** Check if backend FrontendGatewayService supports `/analyze-content-for-insights` or if frontend should use `/analyze-content`

**Note:** Lines 116 and 156 are CORRECT - backend supports `/analysis-results/{id}` and `/analysis-visualizations/{id}`

#### **3. SessionAPIManager.ts** - 3 methods
**File:** `symphainy-frontend/shared/managers/SessionAPIManager.ts`

**Changes needed:**
- Line 62: `/api/session/create-user-session` → `/api/v1/session/create-user-session`
- Line 118: `/api/session/get-session-details/{sessionId}` → `/api/v1/session/get-session-details/{sessionId}`
- Line 156: `/api/session/get-session-state/{sessionId}` → `/api/v1/session/get-session-state/{sessionId}`

#### **4. GuideAgentAPIManager.ts** - 3 methods
**File:** `symphainy-frontend/shared/managers/GuideAgentAPIManager.ts`

**Changes needed:**
- Line 71: `/api/v1/journey/guide-agent/analyze-user-intent` → `/api/v1/guide-agent/analyze-user-intent`
- Line 117: `/api/v1/journey/guide-agent/get-journey-guidance` → `/api/v1/guide-agent/get-journey-guidance`
- Line 163: `/api/v1/journey/guide-agent/get-conversation-history/{sessionId}` → `/api/v1/guide-agent/get-conversation-history/{sessionId}`

#### **5. LiaisonAgentsAPIManager.ts** - 2 methods
**File:** `symphainy-frontend/shared/managers/LiaisonAgentsAPIManager.ts`

**Changes needed:**
- Line 59: `/api/liaison-agents/send-message-to-pillar-agent` → `/api/v1/liaison-agents/send-message-to-pillar-agent`
- Line 108: `/api/liaison-agents/get-pillar-conversation-history/{sessionId}/{pillar}` → `/api/v1/liaison-agents/get-pillar-conversation-history/{sessionId}/{pillar}`

### **Priority 2: Legacy Endpoints** (May need backend support)

- ContentAPIManager.ts: Legacy endpoints (`/api/content/*`) - check if backend supports or migrate to semantic APIs

---

**Last Updated:** December 2024

