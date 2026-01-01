# Agent Testing Execution Plan

**Date:** 2025-12-04  
**Status:** 🚀 **READY TO EXECUTE**

---

## ✅ **Step 1: Endpoint Alignment - COMPLETE**

### **Guide Agent:**
- ✅ **Frontend:** `/api/v1/journey/guide-agent/analyze-user-intent`
- ✅ **Test:** `/api/v1/journey/guide-agent/analyze-user-intent`  
- ✅ **Backend:** `/api/v1/journey/guide-agent/*` (via JourneyRealmBridge)

**All three are in sync!** ✅

### **Liaison Agents:**
- ⚠️ **Frontend:** `/api/v1/liaison-agents/send-message-to-pillar-agent`
- ⚠️ **Backend:** `/api/chat/liaison` (different path)
- ❌ **Action Needed:** Align paths or add routing

---

## 🔍 **Step 1.5: Service Availability Check**

### **Issue Found:**
Guide Agent endpoint returns: `"MVP Journey Orchestrator not available"`

**This is a service initialization issue, not a routing issue.**

**Next Steps:**
1. Check if MVP Journey Orchestrator is initialized
2. Check if it's registered with Curator
3. Verify dependencies are available

---

## 🎯 **Step 2: Manual Agent Testing** (RECOMMENDED APPROACH)

### **Why Manual Testing First:**
- ✅ **Easier debugging** - See exact errors immediately
- ✅ **Faster iteration** - No test framework overhead
- ✅ **Better understanding** - See what actually works
- ✅ **Identify issues early** - Before writing E2E tests

### **Testing Order:**

#### **2.1 Guide Agent** (Start Here - Entry Point)
1. **Intent Analysis** - Does it understand user intent?
2. **Journey Guidance** - Does it provide helpful guidance?
3. **Conversation History** - Does it track conversations?

#### **2.2 Liaison Agents** (One at a Time)
1. **Content Liaison** - Test content-related questions
2. **Insights Liaison** - Test insights-related questions
3. **Operations Liaison** - Test operations-related questions
4. **Business Outcomes Liaison** - Test business outcomes questions

#### **2.3 WebSocket** (If Available)
1. **Guide Agent WebSocket** - Real-time conversations
2. **Liaison Agent WebSocket** - Pillar-specific real-time chat

---

## 📋 **Manual Test Commands**

### **Guide Agent Tests:**

#### **Test 1: Intent Analysis**
```bash
curl -X POST http://localhost:8000/api/v1/journey/guide-agent/analyze-user-intent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to upload and analyze my business data",
    "user_id": "test-user-123",
    "session_token": "test-session-token"
  }' | python3 -m json.tool
```

**Expected:** Intent analysis with recommended pillar

#### **Test 2: Journey Guidance**
```bash
curl -X POST http://localhost:8000/api/v1/journey/guide-agent/get-journey-guidance \
  -H "Content-Type: application/json" \
  -d '{
    "user_goal": "Analyze my business data and generate insights",
    "current_pillar": "content",
    "session_id": "test-session-id"
  }' | python3 -m json.tool
```

**Expected:** Guidance with next steps

#### **Test 3: Conversation History**
```bash
curl -X GET http://localhost:8000/api/v1/journey/guide-agent/get-conversation-history/test-session-id | python3 -m json.tool
```

**Expected:** Conversation history

### **Liaison Agent Tests:**

#### **Test 4: Content Liaison**
```bash
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I upload a file?",
    "pillar": "content",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }' | python3 -m json.tool
```

**Expected:** Helpful content-related response

#### **Test 5-7: Other Liaison Agents**
(Same pattern, change `pillar` to: `insights`, `operations`, `business-outcomes`)

---

## 🧪 **Step 3: E2E Tests** (After Manual Validation)

### **Create Test File: `test_agent_functionality.py`**

**Location:** `tests/e2e/production/test_agent_functionality.py`

**Tests:**
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
**Status:** Needs investigation
**Impact:** Guide Agent endpoints return 500/503
**Action:** Check service initialization

### **Issue 2: Liaison Agent Path Mismatch**
**Status:** Needs alignment
**Impact:** Frontend and backend use different paths
**Action:** Either:
- Update frontend to use `/api/chat/liaison`
- OR add routing from `/api/v1/liaison-agents/*` to `/api/chat/liaison`

---

## ✅ **Recommended Execution Order**

1. ✅ **Verify endpoint alignment** (DONE)
2. ⏳ **Fix MVP Journey Orchestrator availability** (if needed)
3. ⏳ **Manual test Guide Agent** (3 tests)
4. ⏳ **Fix Liaison Agent path mismatch**
5. ⏳ **Manual test Liaison Agents** (4 tests)
6. ⏳ **Create E2E tests** (based on manual results)
7. ⏳ **Run E2E test suite**

---

## 📝 **Notes**

- **Start with Guide Agent** - It's the entry point
- **Fix issues as you find them** - Don't accumulate technical debt
- **Document what works/doesn't work** - Helps with E2E test creation
- **One agent at a time** - Easier debugging

---

**Ready to proceed!** Let's start with investigating the MVP Journey Orchestrator issue, then move to manual testing.



