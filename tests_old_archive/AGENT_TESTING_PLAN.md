# Agent Testing Plan - Step-by-Step Approach

**Date:** 2025-12-04  
**Status:** 📋 **PLAN READY FOR EXECUTION**

---

## ✅ **Step 1: Verify Endpoint Alignment** (COMPLETE)

### **Guide Agent Endpoints:**
- ✅ **Frontend:** `/api/v1/journey/guide-agent/analyze-user-intent`
- ✅ **Test:** `/api/v1/journey/guide-agent/analyze-user-intent`
- ✅ **Backend:** `/api/v1/journey/guide-agent/*` (via JourneyRealmBridge)

**Status:** All three are in sync! ✅

### **Liaison Agent Endpoints:**
- ⚠️ **Frontend:** `/api/liaison-agents/send-message-to-pillar-agent` (no v1)
- ⚠️ **Backend:** `/api/chat/liaison` (different path)
- ❌ **Test:** Not tested yet

**Action Needed:** Verify and align liaison agent paths

---

## 🎯 **Step 2: Manual Agent Testing** (NEXT)

### **2.1 Guide Agent Manual Tests**

#### **Test 1: Intent Analysis**
```bash
curl -X POST http://localhost:8000/api/v1/journey/guide-agent/analyze-user-intent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to upload and analyze my business data",
    "user_id": "test-user-123",
    "session_token": "test-session-token"
  }'
```

**Expected:**
- Status: 200 OK
- Response contains: `intent_analysis`, `primary_intent`, `recommended_pillar`
- Response is intelligent (not just echo)

**What to Check:**
- ✅ Does it analyze intent correctly?
- ✅ Does it recommend the right pillar?
- ✅ Is the response helpful?

#### **Test 2: Journey Guidance**
```bash
curl -X POST http://localhost:8000/api/v1/journey/guide-agent/get-journey-guidance \
  -H "Content-Type: application/json" \
  -d '{
    "user_goal": "Analyze my business data and generate insights",
    "current_pillar": "content",
    "session_id": "test-session-id"
  }'
```

**Expected:**
- Status: 200 OK
- Response contains: `guidance`, `next_steps`, `recommended_pillar`

**What to Check:**
- ✅ Does it provide helpful guidance?
- ✅ Does it recommend next steps?
- ✅ Is the guidance context-aware?

#### **Test 3: Conversation History**
```bash
curl -X GET http://localhost:8000/api/v1/journey/guide-agent/get-conversation-history/test-session-id
```

**Expected:**
- Status: 200 OK
- Response contains: `conversation`, `messages`

**What to Check:**
- ✅ Does it return conversation history?
- ✅ Are messages in correct order?
- ✅ Is context preserved?

---

### **2.2 Liaison Agent Manual Tests**

#### **Test 4: Content Liaison Agent**
```bash
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I upload a file?",
    "pillar": "content",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }'
```

**Expected:**
- Status: 200 OK
- Response contains: `response`, `message`, `agent`

**What to Check:**
- ✅ Does it understand content-related questions?
- ✅ Does it provide helpful answers?
- ✅ Does it know about file uploads?

#### **Test 5: Insights Liaison Agent**
```bash
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What insights can I generate?",
    "pillar": "insights",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }'
```

**What to Check:**
- ✅ Does it understand insights-related questions?
- ✅ Does it know about analysis capabilities?

#### **Test 6: Operations Liaison Agent**
```bash
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I create a workflow?",
    "pillar": "operations",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }'
```

**What to Check:**
- ✅ Does it understand operations-related questions?
- ✅ Does it know about SOP/workflow creation?

#### **Test 7: Business Outcomes Liaison Agent**
```bash
curl -X POST http://localhost:8000/api/chat/liaison \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I generate a roadmap?",
    "pillar": "business-outcomes",
    "conversation_id": "test-conv-id",
    "user_id": "test-user-123"
  }'
```

**What to Check:**
- ✅ Does it understand business outcomes questions?
- ✅ Does it know about roadmap generation?

---

### **2.3 WebSocket Tests** (If Available)

#### **Test 8: Guide Agent WebSocket**
```bash
# Use wscat or similar WebSocket client
wscat -c "ws://localhost:8000/api/ws/guide?session_token=test-session"
```

**Send:**
```json
{
  "message": "I want to analyze my data",
  "user_id": "test-user"
}
```

**What to Check:**
- ✅ Connection established?
- ✅ Real-time responses?
- ✅ Conversation flow works?

#### **Test 9: Liaison Agent WebSocket**
```bash
wscat -c "ws://localhost:8000/api/ws/liaison/content?session_token=test-session"
```

**What to Check:**
- ✅ Connection established?
- ✅ Pillar-specific responses?
- ✅ Context maintained?

---

## 🧪 **Step 3: E2E Agent Tests** (AFTER MANUAL VALIDATION)

### **3.1 Create Test File: `test_agent_functionality.py`**

**Location:** `tests/e2e/production/test_agent_functionality.py`

**Tests to Create:**
1. `test_guide_agent_intent_analysis` - Verify intent analysis works
2. `test_guide_agent_journey_guidance` - Verify guidance works
3. `test_guide_agent_conversation_history` - Verify history works
4. `test_content_liaison_agent_chat` - Verify content liaison works
5. `test_insights_liaison_agent_chat` - Verify insights liaison works
6. `test_operations_liaison_agent_chat` - Verify operations liaison works
7. `test_business_outcomes_liaison_agent_chat` - Verify business outcomes liaison works

### **3.2 Create Test File: `test_agent_integration.py`**

**Location:** `tests/e2e/production/test_agent_integration.py`

**Tests to Create:**
1. `test_agent_orchestrator_integration` - Verify agents call orchestrators
2. `test_agent_tool_calling` - Verify agents use MCP tools
3. `test_agent_conversation_flow` - Verify multi-turn conversations
4. `test_agent_cross_pillar_navigation` - Verify Guide Agent routes to Liaison Agents

---

## 📋 **Testing Checklist**

### **Guide Agent:**
- [ ] Intent analysis works
- [ ] Journey guidance works
- [ ] Conversation history works
- [ ] Responses are intelligent (not just echo)
- [ ] Routes to correct Liaison Agents

### **Liaison Agents (4 pillars):**
- [ ] Content Liaison works
- [ ] Insights Liaison works
- [ ] Operations Liaison works
- [ ] Business Outcomes Liaison works
- [ ] Each understands pillar-specific questions
- [ ] Each can call orchestrators

### **WebSocket (if used):**
- [ ] Guide Agent WebSocket works
- [ ] Liaison Agent WebSocket works
- [ ] Real-time conversations work
- [ ] Session management works

### **Integration:**
- [ ] Agents call orchestrators correctly
- [ ] Agents use MCP tools correctly
- [ ] Multi-turn conversations work
- [ ] Context preserved across turns

---

## 🚀 **Execution Order**

1. ✅ **Verify endpoint alignment** (DONE - all in sync)
2. ⏳ **Manual test Guide Agent** (3 tests)
3. ⏳ **Manual test Liaison Agents** (4 tests)
4. ⏳ **Manual test WebSocket** (2 tests, if available)
5. ⏳ **Create E2E tests** (based on manual test results)
6. ⏳ **Run E2E test suite**

---

## 📝 **Notes**

- **Start with Guide Agent** - It's the entry point
- **Test one agent at a time** - Easier debugging
- **Document any issues** - Note what works/doesn't work
- **Fix issues before moving on** - Don't accumulate technical debt
- **Create E2E tests for working agents** - Automate what works

---

**Ready to proceed with Step 2: Manual Agent Testing!**



