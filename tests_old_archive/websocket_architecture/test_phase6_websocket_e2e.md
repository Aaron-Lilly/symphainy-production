# Phase 6: End-to-End WebSocket Testing Guide

## Overview

This guide provides manual and automated testing procedures for verifying WebSocket connections work correctly after Phase 6 implementation.

## Test Scenarios

### 1. Guide Agent WebSocket Connection

**Endpoint:** `ws://127.0.0.1:8000/api/ws/guide?session_token={token}`

**Test Steps:**
1. Open browser DevTools → Network → WS tab
2. Navigate to frontend application
3. Open Guide Agent chat
4. Verify WebSocket connection appears in Network tab
5. Send a test message: "Hello, Guide Agent"
6. Verify response is received

**Expected Results:**
- ✅ WebSocket connection established (status: 101 Switching Protocols)
- ✅ Connection shows as "Connected" in frontend
- ✅ Message sent: `{ "message": "Hello, Guide Agent" }`
- ✅ Response received: `{ "type": "chat_response", "agent_type": "guide", "message": "..." }`
- ✅ Message appears in chat UI

**Backend Logs to Check:**
```
✅ Guide Agent WebSocket connection accepted
✅ WebSocket {connection_id} linked to session {session_id}
✅ Guide Agent response sent
```

---

### 2. Liaison Agent WebSocket Connection (Per Pillar)

**Endpoints:**
- Content: `ws://127.0.0.1:8000/api/ws/liaison/content?session_token={token}`
- Insights: `ws://127.0.0.1:8000/api/ws/liaison/insights?session_token={token}`
- Operations: `ws://127.0.0.1:8000/api/ws/liaison/operations?session_token={token}`
- Business Outcomes: `ws://127.0.0.1:8000/api/ws/liaison/business_outcomes?session_token={token}`

**Test Steps:**
1. Navigate to a pillar page (e.g., `/pillars/content`)
2. Open secondary chat (liaison agent)
3. Verify WebSocket connection established
4. Send a test message
5. Verify response received
6. Switch to another pillar
7. Verify new WebSocket connection for new pillar
8. Verify conversation history restored for new pillar

**Expected Results:**
- ✅ WebSocket connection established for current pillar
- ✅ If previous conversation exists, `conversation_restored` event received
- ✅ Message sent: `{ "message": "test message" }`
- ✅ Response received: `{ "type": "chat_response", "agent_type": "liaison", "pillar": "...", "message": "..." }`
- ✅ When switching pillars, old connection closes, new connection opens
- ✅ Conversation history restored for new pillar (if exists)

**Backend Logs to Check:**
```
✅ Liaison Agent WebSocket connection accepted (pillar: content)
✅ Restored {N} messages for content_liaison
✅ WebSocket {connection_id} linked to session {session_id}
✅ User message stored in conversation history
✅ Agent response stored in conversation history
```

---

### 3. Conversation History Persistence

**Test Steps:**
1. Navigate to Content pillar
2. Send 3 messages to Content Liaison Agent
3. Navigate to Insights pillar
4. Send 2 messages to Insights Liaison Agent
5. Navigate back to Content pillar
6. Verify Content conversation history is restored
7. Navigate to Insights pillar again
8. Verify Insights conversation history is restored

**Expected Results:**
- ✅ Content messages persist when switching away
- ✅ Insights messages persist when switching away
- ✅ Each pillar's conversation history is isolated
- ✅ No cross-pillar message leakage
- ✅ History restored on reconnection to same pillar

**Backend Logs to Check:**
```
✅ Restored 3 messages for content_liaison
✅ Restored 2 messages for insights_liaison
```

---

### 4. Error Handling

**Test Scenarios:**

#### 4.1 Invalid Pillar Name
- Connect to: `ws://127.0.0.1:8000/api/ws/liaison/invalid`
- **Expected:** Connection closed with code 4004, reason: "Invalid pillar: invalid"

#### 4.2 Missing Session Token
- Connect to: `ws://127.0.0.1:8000/api/ws/guide`
- **Expected:** Connection may succeed but session validation may fail

#### 4.3 WebSocket Disconnect
- Establish connection
- Close connection manually
- **Expected:** Clean disconnect, no errors in logs

#### 4.4 Invalid Message Format
- Send: `{ "invalid": "format" }`
- **Expected:** Error response: `{ "type": "error", "message": "Message is required" }`

---

### 5. Frontend Integration Tests

**Test Components:**
1. `GuideAgentProvider.tsx`
   - ✅ Connects to `/api/ws/guide`
   - ✅ Sends messages in correct format
   - ✅ Handles responses correctly
   - ✅ Updates UI with messages

2. `SecondaryChatbot.tsx`
   - ✅ Uses `useLiaisonChat` hook
   - ✅ Determines pillar from route
   - ✅ Connects to correct endpoint
   - ✅ Displays messages correctly

3. `useLiaisonChat` hook
   - ✅ Connects on mount (if autoConnect=true)
   - ✅ Handles conversation restoration
   - ✅ Sends messages correctly
   - ✅ Updates state on new messages
   - ✅ Handles errors gracefully

---

## Automated Test Script

See `test_phase6_websocket_e2e.py` for automated WebSocket testing.

**Run Tests:**
```bash
cd /home/founders/demoversion/symphainy_source
python3 tests/websocket_architecture/test_phase6_websocket_e2e.py
```

---

## Troubleshooting

### Connection Fails
1. Check backend is running: `docker ps | grep backend`
2. Check WebSocket endpoint is registered: Look for `/api/ws/guide` and `/api/ws/liaison/{pillar}` in backend logs
3. Check CORS settings (if connecting from different origin)
4. Check firewall/network settings

### Messages Not Received
1. Check WebSocket connection status in browser DevTools
2. Check backend logs for errors
3. Verify message format matches backend expectations
4. Check session token is valid

### Conversation History Not Restored
1. Verify SessionManagerService is initialized
2. Check backend logs for `get_conversation_history` calls
3. Verify agent_type mapping is correct
4. Check that messages were stored with correct agent_type

### Pillar Switching Issues
1. Verify pillar name matches `PILLAR_TO_ORCHESTRATOR_MAP` in backend
2. Check that old WebSocket connection is closed before opening new one
3. Verify `useLiaisonChat` hook is re-initialized with new pillar

---

## Success Criteria

✅ All WebSocket endpoints connect successfully
✅ Messages are sent and received correctly
✅ Conversation history persists across pillar switches
✅ Error handling works correctly
✅ Frontend components integrate properly
✅ No memory leaks (connections properly closed)
✅ No cross-pillar message leakage

