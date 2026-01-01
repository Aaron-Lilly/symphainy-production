# WebSocket Strategy Analysis & Recommendation

**Date:** January 15, 2025  
**Context:** 5 Agents (1 Guide + 4 Liaison) requiring real-time chat  
**Question:** Is one websocket per agent the right approach, or should we use a unified routing strategy?

---

## 🔍 **Current State Analysis**

### **Current Pattern:**
- **Guide Agent:** `/api/ws/guide` (dedicated endpoint)
- **Liaison Agents:** `/api/ws/liaison/{pillar}` (single endpoint with pillar routing)

### **Potential Issues with Multiple Connections:**

1. **Resource Usage:**
   - 5 websocket connections per user (1 guide + 4 liaison)
   - Each connection consumes server resources (memory, file descriptors)
   - Browser limits: ~6 concurrent websocket connections per domain
   - Could be problematic for users with multiple tabs/windows

2. **Frontend Complexity:**
   - Managing 5 separate websocket connections
   - Connection lifecycle management (connect/disconnect/reconnect)
   - State synchronization across connections
   - Error handling for each connection

3. **Connection Lifecycle:**
   - When user switches pillars, do we:
     - Keep all connections open? (wasteful)
     - Disconnect/reconnect? (latency, state loss risk)
     - Lazy connect? (complexity)

4. **Session Management:**
   - Each connection needs session validation
   - Multiple session lookups per user
   - Conversation history per connection

5. **User Experience:**
   - Potential confusion: "Which agent am I talking to?"
   - Context switching between agents
   - Conversation history management

---

## 💡 **Recommended Approach: Unified WebSocket with Message Routing**

### **Architecture:**

**Single WebSocket Endpoint:** `/api/ws/agent`

**Message Format:**
```typescript
interface AgentMessage {
  agent_type: "guide" | "liaison";
  pillar?: "content" | "insights" | "operations" | "business_outcomes";  // Required for liaison
  message: string;
  conversation_id?: string;  // For conversation continuity
  session_token?: string;
  metadata?: {
    // Additional context (file_id, content_id, etc.)
  };
}
```

**Response Format:**
```typescript
interface AgentResponse {
  agent_type: "guide" | "liaison";
  pillar?: string;
  message: string;
  conversation_id: string;
  type: "message" | "error" | "visualization" | "analysis" | "drill_down";
  data?: any;  // AGUI components, analysis results, etc.
  visualization?: any;  // AGUI visualization component
}
```

### **How It Works:**

1. **Single Connection:**
   - Frontend opens ONE websocket connection: `/api/ws/agent`
   - Connection persists across pillar switches
   - Session validated once on connect

2. **Message Routing:**
   - Frontend includes `agent_type` and `pillar` in each message
   - Backend routes to appropriate agent based on message fields
   - Agent processes message and returns response
   - Response includes `agent_type` and `pillar` for frontend routing

3. **Agent Discovery:**
   ```python
   # Backend routing logic
   if message["agent_type"] == "guide":
       agent = await get_guide_agent()
   elif message["agent_type"] == "liaison":
       pillar = message["pillar"]
       orchestrator = await get_orchestrator_for_pillar(pillar)
       agent = await orchestrator.get_agent(f"{pillar.capitalize()}LiaisonAgent")
   ```

4. **Conversation Context:**
   - Each agent maintains its own conversation history
   - Conversation ID includes agent type and pillar: `{agent_type}_{pillar}_{session_id}`
   - Frontend manages which conversation is "active"
   - Backend routes to correct agent based on message

5. **Frontend State Management:**
   ```typescript
   // Single websocket connection
   const ws = new WebSocket('/api/ws/agent');
   
   // Frontend manages active agent
   const [activeAgent, setActiveAgent] = useState<{
     type: "guide" | "liaison";
     pillar?: string;
   }>({ type: "guide" });
   
   // Send message with agent context
   const sendMessage = (message: string) => {
     ws.send(JSON.stringify({
       agent_type: activeAgent.type,
       pillar: activeAgent.pillar,
       message: message,
       conversation_id: getConversationId(activeAgent)
     }));
   };
   ```

---

## ✅ **Benefits of Unified Approach**

1. **Resource Efficiency:**
   - Single connection per user (not 5)
   - Reduced server resource usage
   - Better scalability

2. **Simplified Frontend:**
   - One websocket connection to manage
   - Simpler state management
   - Easier error handling

3. **Better UX:**
   - Faster agent switching (no connection overhead)
   - Seamless context switching
   - Single conversation history management

4. **Flexible Routing:**
   - Easy to add new agents without new endpoints
   - Can route based on context (e.g., current pillar)
   - Supports agent delegation (guide → liaison)

5. **Session Management:**
   - Single session validation
   - Unified conversation history
   - Easier to implement cross-agent context

---

## 🔄 **Migration Strategy**

### **Phase 1: Implement Unified Endpoint (Parallel)**
- Create `/api/ws/agent` endpoint
- Keep existing endpoints (`/api/ws/guide`, `/api/ws/liaison/{pillar}`) for backward compatibility
- Test unified endpoint with new frontend code

### **Phase 2: Frontend Migration**
- Update frontend to use unified endpoint
- Implement agent switching logic
- Test all agent interactions

### **Phase 3: Deprecate Old Endpoints**
- Mark old endpoints as deprecated
- Monitor usage
- Remove after migration complete

---

## 📋 **Implementation Details**

### **Backend: Unified WebSocket Endpoint**

**File:** `backend/api/websocket_router.py`

```python
@router.websocket("/api/ws/agent")
async def unified_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """
    Unified Agent WebSocket endpoint.
    
    Handles all agent communications (Guide + Liaison) via message routing.
    Single connection per user, routes messages to appropriate agent.
    """
    await websocket.accept()
    logger.info(f"🔌 Unified Agent WebSocket connection accepted (session_token: {session_token})")
    
    # Session validation (once)
    session = await validate_session(session_token)
    
    # Message loop
    try:
        while True:
            message_data = await websocket.receive_json()
            
            # Extract routing information
            agent_type = message_data.get("agent_type", "guide")
            pillar = message_data.get("pillar")
            user_message = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id")
            
            # Route to appropriate agent
            if agent_type == "guide":
                agent = await get_guide_agent()
                response = await agent.handle_user_message(
                    user_message,
                    session_token or "anonymous"
                )
            elif agent_type == "liaison":
                if not pillar:
                    await websocket.send_json({
                        "type": "error",
                        "message": "pillar is required for liaison agent"
                    })
                    continue
                
                orchestrator = await get_orchestrator_for_pillar(pillar)
                agent = await orchestrator.get_agent(f"{pillar.capitalize()}LiaisonAgent")
                
                user_context = UserContext(
                    user_id=session.get("user_id"),
                    tenant_id=session.get("tenant_id"),
                    session_id=session.get("session_id"),
                    roles=session.get("roles", [])
                )
                
                response = await agent.process_user_query(
                    query=user_message,
                    conversation_id=conversation_id or f"{pillar}_{session.get('session_id')}",
                    user_context=user_context
                )
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown agent_type: {agent_type}"
                })
                continue
            
            # Add routing metadata to response
            response["agent_type"] = agent_type
            if pillar:
                response["pillar"] = pillar
            
            # Send response
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info(f"🔌 Unified Agent WebSocket disconnected")
    except Exception as e:
        logger.error(f"❌ Error in Unified Agent WebSocket: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Internal error: {str(e)}"
        })
```

### **Frontend: Unified WebSocket Hook**

**File:** `frontend/shared/hooks/useUnifiedAgentChat.ts`

```typescript
interface ActiveAgent {
  type: "guide" | "liaison";
  pillar?: "content" | "insights" | "operations" | "business_outcomes";
}

export function useUnifiedAgentChat() {
  const [activeAgent, setActiveAgent] = useState<ActiveAgent>({ type: "guide" });
  const [messages, setMessages] = useState<Map<string, Message[]>>(new Map());
  const wsRef = useRef<WebSocket | null>(null);
  
  // Get conversation ID for active agent
  const getConversationId = (agent: ActiveAgent): string => {
    if (agent.type === "guide") {
      return `guide_${sessionId}`;
    } else {
      return `${agent.pillar}_liaison_${sessionId}`;
    }
  };
  
  // Connect to unified endpoint
  useEffect(() => {
    const ws = new WebSocket('/api/ws/agent?session_token=' + sessionToken);
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      const response: AgentResponse = JSON.parse(event.data);
      const conversationId = getConversationId({
        type: response.agent_type,
        pillar: response.pillar
      });
      
      // Add message to appropriate conversation
      setMessages(prev => {
        const newMap = new Map(prev);
        const conversation = newMap.get(conversationId) || [];
        conversation.push({
          role: "assistant",
          content: response.message,
          data: response.data,
          visualization: response.visualization
        });
        newMap.set(conversationId, conversation);
        return newMap;
      });
    };
    
    return () => ws.close();
  }, [sessionToken]);
  
  // Send message to active agent
  const sendMessage = (message: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }
    
    const conversationId = getConversationId(activeAgent);
    
    wsRef.current.send(JSON.stringify({
      agent_type: activeAgent.type,
      pillar: activeAgent.pillar,
      message: message,
      conversation_id: conversationId
    }));
    
    // Add user message to conversation
    setMessages(prev => {
      const newMap = new Map(prev);
      const conversation = newMap.get(conversationId) || [];
      conversation.push({
        role: "user",
        content: message
      });
      newMap.set(conversationId, conversation);
      return newMap;
    });
  };
  
  // Switch active agent
  const switchAgent = (agent: ActiveAgent) => {
    setActiveAgent(agent);
  };
  
  // Get messages for active agent
  const getActiveMessages = (): Message[] => {
    const conversationId = getConversationId(activeAgent);
    return messages.get(conversationId) || [];
  };
  
  return {
    activeAgent,
    messages: getActiveMessages(),
    sendMessage,
    switchAgent,
    getConversationHistory: (agent: ActiveAgent) => {
      const conversationId = getConversationId(agent);
      return messages.get(conversationId) || [];
    }
  };
}
```

---

## 🎯 **Recommendation**

**Use Unified WebSocket Approach** (`/api/ws/agent`) instead of separate endpoints per agent.

**Reasons:**
1. ✅ **Resource Efficient:** Single connection per user (not 5)
2. ✅ **Simpler Frontend:** One connection to manage
3. ✅ **Better UX:** Faster agent switching, seamless context
4. ✅ **Scalable:** Easy to add new agents without new endpoints
5. ✅ **Flexible:** Supports agent delegation and cross-agent context

**Migration Path:**
- Implement unified endpoint in parallel with existing endpoints
- Migrate frontend gradually
- Deprecate old endpoints after migration complete

---

## 📝 **Updated Phase 5 Plan**

Update Phase 5 to use unified websocket approach:

- [ ] Create unified endpoint `/api/ws/agent`
- [ ] Implement message routing logic
- [ ] Update InsightsLiaisonAgent to work with unified endpoint
- [ ] Create frontend hook `useUnifiedAgentChat`
- [ ] Update Insights pillar UI to use unified endpoint
- [ ] Test agent switching (guide ↔ liaison)
- [ ] Test conversation continuity across agent switches

