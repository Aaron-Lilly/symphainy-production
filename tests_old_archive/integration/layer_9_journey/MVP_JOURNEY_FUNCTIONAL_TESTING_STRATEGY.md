# MVP Journey Functional Testing Strategy

**Date:** December 2024  
**Status:** ✅ **Functional Test Suite Created**

---

## 🎯 PURPOSE

This document outlines the functional testing strategy for the **MVP Journey Realm**, validating that Journey services work end-to-end with the frontend implementation and MVP description.

**Key Principle:** Use the **actual frontend implementation** as the source of truth for expected behavior, validated against the MVP description document.

---

## 📋 TEST SCOPE

### **What We're Testing**

1. **MVP Journey Orchestrator Service**
   - Initialization and Experience Foundation integration
   - 4-pillar configuration (Content, Insights, Operations, Business Outcomes)
   - Journey lifecycle management (start, navigate, progress, completion)
   - Coordination with Business Enablement orchestrators

2. **Journey Flow Validation**
   - Landing page → Content → Insights → Operations → Business Outcomes
   - Free navigation between pillars (via navbar)
   - Pillar progress tracking and completion criteria
   - Journey completion checking

3. **Frontend Integration Points**
   - Guide Agent API endpoints (analyze intent, get journey guidance)
   - Pillar-specific operations (upload, parse, analyze, generate, etc.)
   - Session management and state persistence

4. **Experience Foundation Integration**
   - Frontend Gateway composition
   - User Experience service composition
   - Session Manager integration

---

## 🏗️ TEST STRUCTURE

### **Test File: `test_mvp_journey_functional.py`**

#### **1. MVP Journey Initialization Tests**
- ✅ `test_mvp_journey_orchestrator_initialization`: Verify orchestrator initializes correctly
- ✅ `test_mvp_journey_orchestrator_has_experience_foundation`: Verify Experience Foundation access
- ✅ `test_mvp_journey_orchestrator_has_session_orchestrator`: Verify Session Orchestrator composition

#### **2. MVP Journey Lifecycle Tests**
- `test_start_mvp_journey`: Start MVP journey with 4 pillars
- `test_navigate_to_pillar`: Navigate between pillars (free navigation)
- `test_get_pillar_state`: Get current pillar state
- `test_update_pillar_progress`: Update pillar progress (e.g., files uploaded, parsed)
- `test_get_mvp_progress`: Get overall MVP journey progress
- `test_check_mvp_completion`: Check if MVP journey is complete
- `test_get_recommended_next_pillar`: Get recommended next pillar (for Guide Agent)

#### **3. MVP Pillar Configuration Tests**
- ✅ `test_content_pillar_configuration`: Verify Content pillar matches MVP description
- ✅ `test_insights_pillar_configuration`: Verify Insights pillar matches MVP description
- ✅ `test_operations_pillar_configuration`: Verify Operations pillar matches MVP description
- ✅ `test_business_outcomes_pillar_configuration`: Verify Business Outcomes pillar matches MVP description

---

## 🔍 VALIDATION CRITERIA

### **MVP Description Alignment**

From `MVP_Description_For_Business_and_Technical_Readiness.md`:

1. **Content Pillar:**
   - ✅ File upload (multiple file types, including mainframe binary/copybooks)
   - ✅ File parsing (parquet, JSON Structured, JSON Chunks)
   - ✅ Data preview
   - ✅ Metadata extraction
   - ✅ ContentLiaisonAgent chatbot
   - ✅ Completion: files uploaded AND parsed

2. **Insights Pillar:**
   - ✅ File selection (from parsed files)
   - ✅ Business analysis (formatted text)
   - ✅ Visual/tabular representation (VARK learning style)
   - ✅ InsightsLiaisonAgent chatbot
   - ✅ Insights summary with recommendations
   - ✅ Completion: file selected AND analysis complete AND insights summary generated

3. **Operations Pillar:**
   - ✅ File selection or upload (redirects to Content) or generate from scratch
   - ✅ Workflow and SOP generation
   - ✅ Coexistence blueprint generation
   - ✅ OperationsLiaisonAgent chatbot
   - ✅ Completion: workflow generated AND SOP generated AND coexistence blueprint created

4. **Business Outcomes Pillar:**
   - ✅ Display summaries from other pillars
   - ✅ ExperienceLiaisonAgent chatbot
   - ✅ Roadmap generation
   - ✅ POC proposal generation
   - ✅ Completion: summaries reviewed AND roadmap generated AND POC proposal generated

### **Frontend Implementation Alignment**

From `symphainy-frontend`:

1. **Guide Agent APIs** (`GuideAgentAPIManager.ts`):
   - `/api/v1/journey/guide-agent/analyze-user-intent` (POST)
   - `/api/v1/journey/guide-agent/get-journey-guidance` (POST)
   - `/api/v1/journey/guide-agent/get-conversation-history/{sessionId}` (GET)

2. **Pillar Orchestrators** (`PillarOrchestrator.ts`):
   - Content: `uploadFile`, `processFile`, `getFileMetadata`
   - Insights: `generateInsights`, `getVARKAnalysis`
   - Operations: `analyzeCoexistence`, `generateWorkflow`, `generateSOP`
   - Experience: `createSession`, `getCrossPillarData`, `generateOutputs`

3. **Navigation Flow:**
   - Landing page (`app/page.tsx`) → `/pillars/content`
   - Navbar allows free navigation between pillars
   - Guide Agent provides recommendations for next steps

---

## 🧪 TEST EXECUTION

### **Running Tests**

```bash
# Run all MVP Journey functional tests
python3 -m pytest tests/integration/layer_9_journey/test_mvp_journey_functional.py -v

# Run specific test
python3 -m pytest tests/integration/layer_9_journey/test_mvp_journey_functional.py::test_start_mvp_journey -v

# Run with detailed logging
python3 -m pytest tests/integration/layer_9_journey/test_mvp_journey_functional.py -v -s --log-cli-level=INFO
```

### **Test Markers**

- `@pytest.mark.integration`: Integration test
- `@pytest.mark.functional`: Functional test
- `@pytest.mark.timeout_300`: 300-second timeout for infrastructure setup

---

## 📊 EXPECTED BEHAVIOR

### **Graceful Degradation**

Some tests may fail gracefully if:
- Methods are not yet implemented (logged as warnings, not failures)
- Dependencies are not available (e.g., Session Journey Orchestrator)
- External services are not connected (e.g., Business Enablement orchestrators)

**Test Philosophy:** Tests validate what **should** work, and log warnings for what **may** need implementation, allowing us to:
1. Identify what's working ✅
2. Identify what needs implementation ⚠️
3. Fix real issues 🔧

---

## 🔄 NEXT STEPS

### **Phase 1: Foundation Tests** ✅
- [x] MVP Journey Orchestrator initialization
- [x] Experience Foundation integration
- [x] Pillar configuration validation

### **Phase 2: Lifecycle Tests** (In Progress)
- [ ] Start MVP journey
- [ ] Navigate between pillars
- [ ] Update pillar progress
- [ ] Check journey completion

### **Phase 3: Integration Tests** (Future)
- [ ] Guide Agent integration
- [ ] Business Enablement orchestrator coordination
- [ ] Frontend Gateway API validation
- [ ] End-to-end journey flow

### **Phase 4: Real User Journey Tests** (Future)
- [ ] Complete Content pillar flow
- [ ] Complete Insights pillar flow
- [ ] Complete Operations pillar flow
- [ ] Complete Business Outcomes pillar flow
- [ ] Full MVP journey from landing to completion

---

## 📝 NOTES

- **Source of Truth:** Frontend implementation (`symphainy-frontend`) defines expected API contracts
- **MVP Description:** Provides business requirements and user journey flow
- **Journey Services:** Implement the orchestration logic that frontend consumes
- **Tests:** Validate that Journey services work as frontend expects

---

## ✅ SUCCESS CRITERIA

1. ✅ MVP Journey Orchestrator initializes correctly
2. ✅ Experience Foundation is accessible and integrated
3. ✅ All 4 pillars are configured correctly
4. ✅ Pillar configurations match MVP description
5. ⏳ Journey lifecycle methods work (start, navigate, progress, completion)
6. ⏳ Guide Agent integration works (if available)
7. ⏳ Business Enablement orchestrator coordination works

---

**Last Updated:** December 2024



