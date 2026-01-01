# Journey Realm Testing Plan

**Date:** December 2024  
**Status:** 📋 **Planning Phase**

---

## 🎯 TESTING STRATEGY

Following the proven **Business Enablement pattern**: test component parts first, then E2E journeys.

**Key Principle:** Validate individual components work correctly before testing complex integrations.

---

## 📊 TESTING PHASES

### **Phase 1: Component Tests (Foundation)**
Test individual Journey services in isolation to ensure they work correctly.

### **Phase 2: Integration Tests (Composition)**
Test how Journey services compose with Experience Foundation and Business Enablement.

### **Phase 3: Guide Agent Tests (Phase 1/Phase 2 Pattern)**
Test Guide Agent with mocked LLM first, then real API calls.

### **Phase 4: E2E Journey Tests**
Test complete user journeys from landing to completion.

---

## 🧩 PHASE 1: COMPONENT TESTS

### **1.1 MVP Journey Orchestrator** ✅
**Status:** ✅ Complete (14 tests passing)

**Tests:**
- ✅ Initialization and Experience Foundation integration
- ✅ Pillar configuration validation
- ✅ Journey lifecycle methods (start, navigate, progress, completion)

**File:** `test_mvp_journey_functional.py`

---

### **1.2 Session Journey Orchestrator**
**Status:** ⏳ To Do

**What to Test:**
- Initialization and Smart City integration (TrafficCop)
- Area-based navigation (free navigation)
- Area state tracking and persistence
- Area completion checking
- Session progress tracking
- Navigation history

**Test File:** `test_session_journey_orchestrator.py`

**Key Methods:**
- `navigate_to_area()`
- `update_area_state()`
- `check_area_completion()`
- `get_session_progress()`

---

### **1.3 Journey Analytics Service**
**Status:** ⏳ To Do

**What to Test:**
- Initialization and Smart City integration
- Journey performance analysis
- Optimization recommendations
- Journey comparison
- Benchmark retrieval

**Test File:** `test_journey_analytics.py`

**Key Methods:**
- `analyze_journey_performance()`
- `get_optimization_recommendations()`
- `compare_journeys()`
- `get_journey_benchmarks()`

---

### **1.4 Journey Milestone Tracker**
**Status:** ⏳ To Do

**What to Test:**
- Initialization and Smart City integration
- Milestone progress tracking
- Milestone state management
- Milestone analytics
- Milestone retry logic

**Test File:** `test_journey_milestone_tracker.py`

**Key Methods:**
- `get_journey_progress()`
- `get_milestone_analytics()`
- `retry_milestone()`
- `update_milestone_state()`

---

## 🔗 PHASE 2: INTEGRATION TESTS

### **2.1 Experience Foundation Integration**
**Status:** ⏳ To Do

**What to Test:**
- Journey services can compose Frontend Gateway
- Journey services can compose User Experience
- Journey services can compose Session Manager
- Experience Foundation SDK builders work correctly

**Test File:** `test_experience_foundation_integration.py` (partially done)

**Key Validations:**
- Frontend Gateway routes journey APIs correctly
- User Experience personalizes journey steps
- Session Manager persists journey state

---

### **2.2 Business Enablement Orchestrator Coordination**
**Status:** ⏳ To Do

**What to Test:**
- Journey services can discover Business Enablement orchestrators via Curator
- Journey services can call Content Analysis orchestrator
- Journey services can call Insights orchestrator
- Journey services can call Operations orchestrator
- Journey services can call Business Outcomes orchestrator

**Test File:** `test_business_enablement_coordination.py`

**Key Validations:**
- Service discovery works
- API calls succeed
- Error handling works correctly

---

### **2.3 MVP Journey Orchestrator → Session Journey Orchestrator Composition**
**Status:** ⏳ To Do

**What to Test:**
- MVP Journey Orchestrator correctly composes Session Journey Orchestrator
- Pillar navigation uses Session Journey Orchestrator under the hood
- Pillar state is tracked via Session Journey Orchestrator
- Progress tracking works end-to-end

**Test File:** `test_mvp_session_composition.py`

---

## 🤖 PHASE 3: GUIDE AGENT TESTS (Phase 1/Phase 2 Pattern)

### **3.1 Guide Agent - Phase 1 (Mocked LLM)**
**Status:** ⏳ To Do

**What to Test:**
- Guide Agent initialization
- Intent analysis logic (without LLM)
- Journey guidance logic (without LLM)
- Conversation history management
- Integration with MVP Journey Orchestrator (for recommendations)

**Test File:** `test_guide_agent_mocked.py`

**Key Validations:**
- Agent can be instantiated
- Intent analysis structure is correct
- Journey guidance structure is correct
- Can access MVP Journey Orchestrator for recommendations
- Error handling works

---

### **3.2 Guide Agent - Phase 2 (Real LLM API Calls)**
**Status:** ⏳ To Do

**What to Test:**
- Real intent analysis with LLM
- Real journey guidance with LLM
- Response quality and critical thinking
- Alternative approach suggestions
- Cost optimization (use GPT-3.5-turbo for testing)

**Test File:** `test_guide_agent_real.py`

**Key Validations:**
- LLM responses are meaningful
- Intent analysis is accurate
- Journey guidance is helpful
- Responses show critical thinking

---

## 🎬 PHASE 4: E2E JOURNEY TESTS

### **4.1 Content Pillar E2E Flow**
**Status:** ⏳ To Do

**What to Test:**
- Start journey → Navigate to Content pillar
- Upload file → Parse file → Preview data
- Extract metadata (optional)
- Chat with ContentLiaisonAgent
- Mark Content pillar as complete

**Test File:** `test_content_pillar_e2e.py`

---

### **4.2 Insights Pillar E2E Flow**
**Status:** ⏳ To Do

**What to Test:**
- Navigate to Insights pillar
- Select file (from Content pillar)
- Generate business analysis
- Create visualization
- Generate insights summary
- Chat with InsightsLiaisonAgent
- Mark Insights pillar as complete

**Test File:** `test_insights_pillar_e2e.py`

---

### **4.3 Operations Pillar E2E Flow**
**Status:** ⏳ To Do

**What to Test:**
- Navigate to Operations pillar
- Select files (from Content pillar)
- Generate workflow
- Generate SOP
- Create coexistence blueprint
- Chat with OperationsLiaisonAgent
- Mark Operations pillar as complete

**Test File:** `test_operations_pillar_e2e.py`

---

### **4.4 Business Outcomes Pillar E2E Flow**
**Status:** ⏳ To Do

**What to Test:**
- Navigate to Business Outcomes pillar
- Review summaries from other pillars
- Add additional context
- Generate roadmap
- Generate POC proposal
- Chat with ExperienceLiaisonAgent
- Mark Business Outcomes pillar as complete

**Test File:** `test_business_outcomes_pillar_e2e.py`

---

### **4.5 Full MVP Journey E2E Flow**
**Status:** ⏳ To Do

**What to Test:**
- Complete journey from landing to completion
- All 4 pillars in sequence
- Guide Agent provides recommendations throughout
- Journey completion is tracked correctly
- All milestone states are correct

**Test File:** `test_full_mvp_journey_e2e.py`

---

## 📋 RECOMMENDED EXECUTION ORDER

### **Week 1: Component Foundation**
1. ✅ MVP Journey Orchestrator (already done)
2. Session Journey Orchestrator
3. Journey Analytics Service
4. Journey Milestone Tracker

### **Week 2: Integration & Guide Agent**
5. Experience Foundation Integration
6. Business Enablement Coordination
7. MVP → Session Composition
8. Guide Agent Phase 1 (Mocked)

### **Week 3: Real LLM & E2E**
9. Guide Agent Phase 2 (Real API)
10. Content Pillar E2E
11. Insights Pillar E2E
12. Operations Pillar E2E
13. Business Outcomes Pillar E2E
14. Full MVP Journey E2E

---

## ✅ SUCCESS CRITERIA

### **Phase 1: Component Tests**
- ✅ All Journey services initialize correctly
- ✅ All service methods are callable
- ✅ Services integrate with Smart City correctly
- ✅ Services register with Curator correctly

### **Phase 2: Integration Tests**
- ✅ Experience Foundation integration works
- ✅ Business Enablement coordination works
- ✅ Service composition works correctly

### **Phase 3: Guide Agent Tests**
- ✅ Guide Agent works with mocked LLM
- ✅ Guide Agent works with real LLM
- ✅ Responses are high quality

### **Phase 4: E2E Tests**
- ✅ All 4 pillars can be completed
- ✅ Full MVP journey works end-to-end
- ✅ Guide Agent provides helpful guidance throughout

---

## 🎯 BENEFITS OF THIS APPROACH

1. **Fast Feedback:** Component tests catch issues early
2. **Isolated Debugging:** Know exactly which component has issues
3. **Cost Effective:** Mock LLM first, then real API calls
4. **Comprehensive:** Test everything individually before E2E
5. **Proven Pattern:** Same approach that worked for Business Enablement

---

**Last Updated:** December 2024



