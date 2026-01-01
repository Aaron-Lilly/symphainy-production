# Agent Testing - Recommended Approach

**Date:** 2025-12-04  
**Status:** ✅ **APPROACH VALIDATED - READY TO EXECUTE**

---

## ✅ **Your Approach is Perfect!**

Your suggested approach is exactly right:
1. ✅ Fix Guide Agent test to match backend (and ensure frontend is in sync)
2. ✅ Manually test each agent individually (easier debugging)
3. ✅ Then do E2E testing on the agents

**This is the optimal approach because:**
- **Manual testing first** catches issues quickly
- **One agent at a time** makes debugging easier
- **E2E tests** validate integration after manual validation

---

## 🔍 **Step 1: Endpoint Alignment - STATUS**

### **Guide Agent Endpoints:**
- ✅ **Frontend:** `/api/v1/journey/guide-agent/analyze-user-intent`
- ✅ **Test:** `/api/v1/journey/guide-agent/analyze-user-intent`
- ✅ **Backend:** `/api/v1/journey/guide-agent/*` (via JourneyRealmBridge)

**All three are in sync!** ✅

### **Current Issue:**
- ⚠️ **Service Discovery Bug:** JourneyRealmBridge uses wrong method (`get_service` instead of `discover_service_by_name`)
- ⚠️ **Service Not Available:** MVPJourneyOrchestratorService not being discovered
- ✅ **Fix Applied:** Updated JourneyRealmBridge to use correct discovery method

**Next:** Verify service is initialized and registered

---

## 🎯 **Step 2: Manual Agent Testing** (RECOMMENDED NEXT)

### **Why Manual Testing First:**
- ✅ **Faster debugging** - See errors immediately
- ✅ **Better understanding** - See what actually works
- ✅ **Identify issues early** - Before writing E2E tests
- ✅ **One agent at a time** - Easier to isolate problems

### **Testing Order:**

#### **2.1 Guide Agent** (Start Here - Entry Point)
**Test Commands:**

```bash
# Test 1: Intent Analysis
curl -X POST http://localhost:8000/api/v1/journey/guide-agent/analyze-user-intent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to upload and analyze my business data",
    "user_id": "test-user-123",
    "session_token": "test-session-token"
  }' | python3 -m json.tool

# Test 2: Journey Guidance
curl -X POST http://localhost:8000/api/v1/journey/guide-agent/get-journey-guidance \
  -H "Content-Type: application/json" \
  -d '{
    "user_goal": "Analyze my business data and generate insights",
    "current_pillar": "content",
    "session_id": "test-session-id"
  }' | python3 -m json.tool

# Test 3: Conversation History
curl -X GET http://localhost:8000/api/v1/journey/guide-agent/get-conversation-history/test-session-id | python3 -m json.tool
```

**What to Check:**
- ✅ Does it return 200 OK (not 503)?
- ✅ Does it analyze intent correctly?
- ✅ Does it provide helpful guidance?
- ✅ Are responses intelligent (not just echo)?

#### **2.2 Liaison Agents** (One at a Time)
**Test Commands:**

```bash
# Test 4: Content Liaison
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I upload a file?",
    "pillar": "content",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }' | python3 -m json.tool

# Test 5: Insights Liaison
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What insights can I generate?",
    "pillar": "insights",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }' | python3 -m json.tool

# Test 6: Operations Liaison
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I create a workflow?",
    "pillar": "operations",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }' | python3 -m json.tool

# Test 7: Business Outcomes Liaison
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I generate a roadmap?",
    "pillar": "business-outcomes",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }' | python3 -m json.tool
```

**What to Check:**
- ✅ Does each liaison understand pillar-specific questions?
- ✅ Does each provide helpful answers?
- ✅ Do they know about pillar capabilities?

---

## 🧪 **Step 3: E2E Tests** (After Manual Validation)

### **Create Test File: `test_agent_functionality.py`**

**Location:** `tests/e2e/production/test_agent_functionality.py`

**Tests to Create:**
1. `test_guide_agent_intent_analysis` - Based on manual test results
2. `test_guide_agent_journey_guidance` - Based on manual test results
3. `test_guide_agent_conversation_history` - Based on manual test results
4. `test_content_liaison_agent_chat` - Based on manual test results
5. `test_insights_liaison_agent_chat` - Based on manual test results
6. `test_operations_liaison_agent_chat` - Based on manual test results
7. `test_business_outcomes_liaison_agent_chat` - Based on manual test results

---

## 🚨 **Current Issues to Address**

### **Issue 1: MVP Journey Orchestrator Not Available**
**Status:** Service discovery method fixed, but service not being discovered
**Impact:** Guide Agent endpoints return 503
**Action:** 
1. ✅ Fixed discovery method (done)
2. ⏳ Check if service is initialized
3. ⏳ Check if service is registered with Curator

### **Issue 2: Liaison Agent Path Mismatch**
**Status:** Needs alignment
**Impact:** Frontend and backend use different paths
**Action:** Either:
- Update frontend to use `/api/chat/liaison`
- OR add routing from `/api/v1/liaison-agents/*` to `/api/chat/liaison`

---

## ✅ **Recommended Execution Order**

1. ✅ **Verify endpoint alignment** (DONE - all in sync)
2. ✅ **Fix service discovery method** (DONE)
3. ⏳ **Verify MVP Journey Orchestrator is initialized** (IN PROGRESS)
4. ⏳ **Manual test Guide Agent** (3 tests)
5. ⏳ **Fix Liaison Agent path mismatch** (if needed)
6. ⏳ **Manual test Liaison Agents** (4 tests)
7. ⏳ **Create E2E tests** (based on manual results)
8. ⏳ **Run E2E test suite**

---

## 📝 **Notes**

- **Start with Guide Agent** - It's the entry point
- **Fix issues as you find them** - Don't accumulate technical debt
- **Document what works/doesn't work** - Helps with E2E test creation
- **One agent at a time** - Easier debugging

---

**Your approach is perfect!** Let's proceed with:
1. Verifying MVP Journey Orchestrator initialization
2. Then manual testing Guide Agent
3. Then manual testing Liaison Agents
4. Then creating E2E tests



