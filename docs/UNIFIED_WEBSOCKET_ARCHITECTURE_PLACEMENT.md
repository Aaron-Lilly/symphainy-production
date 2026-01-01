# Unified WebSocket Architecture Placement

**Date:** January 15, 2025  
**Question:** Where should the unified agent websocket live in the platform architecture?

---

## 🎯 **Architectural Analysis**

### **Current State:**

1. **Experience Foundation:**
   - `WebSocketSDK` - General user-facing websocket capabilities
   - Provides connection management, messaging, broadcasting
   - User-facing communication infrastructure

2. **Agentic Foundation:**
   - `AgentWebSocketSDK` - Agent-specific websocket connections
   - Handles guide/liaison agent connections
   - Agent discovery and routing

3. **Public Works Foundation:**
   - `WebSocketFoundationService` - Infrastructure-level websocket services
   - Low-level connection management
   - Infrastructure abstraction

4. **API Layer:**
   - `websocket_router.py` - FastAPI websocket endpoints
   - Currently has separate endpoints per agent type

---

## 💡 **Recommended Approach: Experience Foundation SDK with Agentic Composition**

### **Decision: Create `UnifiedAgentWebSocketSDK` in Experience Foundation**

**Rationale:**

1. **User-Facing Capability:**
   - Unified websocket is a **user-facing communication channel**
   - Frontend connects to it (Experience Foundation domain)
   - Handles user sessions, conversation history (Experience Foundation domain)

2. **Agent Routing via Composition:**
   - Uses **Agentic Foundation SDK** for agent discovery/routing
   - Composes agent capabilities, doesn't own them
   - Clean separation: Experience = user-facing, Agentic = agent capabilities

3. **Follows Existing Patterns:**
   - Experience Foundation already has `WebSocketSDK` for general websockets
   - Similar to how Experience Foundation composes other capabilities
   - SDK pattern (not service) - realms use it directly

---

## 🏗️ **Implementation Architecture**

### **Layer 1: Experience Foundation SDK**

**File:** `foundations/experience_foundation/sdk/unified_agent_websocket_sdk.py`

```python
class UnifiedAgentWebSocketSDK:
    """
    Unified Agent WebSocket SDK - Experience Foundation
    
    Provides unified websocket endpoint for all agents (Guide + Liaison).
    Single connection per user, routes messages to appropriate agent.
    
    WHAT (Experience SDK): I provide unified agent websocket for user-facing communication
    HOW (SDK Implementation): I compose Experience WebSocketSDK + Agentic Foundation for routing
    """
    
    def __init__(self, experience_foundation: Any):
        self.experience_foundation = experience_foundation
        self.websocket_sdk = None  # Experience Foundation WebSocketSDK
        self.agentic_foundation = None  # For agent discovery/routing
        self.di_container = experience_foundation.di_container
    
    async def initialize(self):
        # Get Experience Foundation WebSocketSDK
        self.websocket_sdk = await self.experience_foundation.get_websocket_sdk()
        
        # Get Agentic Foundation for agent routing
        self.agentic_foundation = self.di_container.get_foundation_service("AgenticFoundationService")
    
    async def handle_agent_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        session_token: str
    ) -> Dict[str, Any]:
        """
        Handle agent message with routing.
        
        Routes to appropriate agent based on message.agent_type and message.pillar.
        """
        agent_type = message.get("agent_type", "guide")
        pillar = message.get("pillar")
        user_message = message.get("message", "")
        
        # Route to agent via Agentic Foundation
        if agent_type == "guide":
            agent = await self._get_guide_agent()
        elif agent_type == "liaison":
            agent = await self._get_liaison_agent(pillar)
        else:
            return {"type": "error", "message": f"Unknown agent_type: {agent_type}"}
        
        # Process message with agent
        response = await agent.process_user_query(...)
        
        # Add routing metadata
        response["agent_type"] = agent_type
        if pillar:
            response["pillar"] = pillar
        
        return response
    
    async def _get_guide_agent(self):
        """Get Guide Agent via Agentic Foundation."""
        # Use Agentic Foundation SDK for agent discovery
        pass
    
    async def _get_liaison_agent(self, pillar: str):
        """Get Liaison Agent via orchestrator discovery."""
        # Use Curator to find orchestrator, then get agent
        pass
```

### **Layer 2: API Endpoint (Uses SDK)**

**File:** `backend/api/websocket_router.py` (update existing)

```python
@router.websocket("/api/ws/agent")
async def unified_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """
    Unified Agent WebSocket endpoint.
    
    Uses Experience Foundation UnifiedAgentWebSocketSDK.
    """
    await websocket.accept()
    
    # Get Experience Foundation
    experience_foundation = await get_experience_foundation()
    unified_sdk = await experience_foundation.get_unified_agent_websocket_sdk()
    
    # Message loop
    try:
        while True:
            message_data = await websocket.receive_json()
            response = await unified_sdk.handle_agent_message(
                websocket=websocket,
                message=message_data,
                session_token=session_token
            )
            await websocket.send_json(response)
    except WebSocketDisconnect:
        pass
```

### **Layer 3: Agentic Foundation Enhancement (Optional)**

**File:** `foundations/agentic_foundation/agent_sdk/agent_routing_helper.py` (new)

```python
class AgentRoutingHelper:
    """
    Agent Routing Helper - Agentic Foundation
    
    Provides agent discovery and routing capabilities.
    Used by UnifiedAgentWebSocketSDK for agent routing.
    """
    
    async def get_guide_agent(self, di_container: Any) -> Any:
        """Get Guide Agent instance."""
        # Discovery logic
        pass
    
    async def get_liaison_agent(self, pillar: str, di_container: Any) -> Any:
        """Get Liaison Agent instance for pillar."""
        # Discovery logic via orchestrator
        pass
```

---

## 📋 **File Structure**

```
foundations/
├── experience_foundation/
│   ├── sdk/
│   │   ├── websocket_sdk.py (existing - general websockets)
│   │   └── unified_agent_websocket_sdk.py (NEW - unified agent websocket)
│   └── experience_foundation_service.py (expose unified SDK)
│
├── agentic_foundation/
│   └── agent_sdk/
│       ├── agent_websocket_sdk.py (existing - agent connections)
│       └── agent_routing_helper.py (NEW - agent discovery/routing)
│
backend/
└── api/
    └── websocket_router.py (update - use unified SDK)
```

---

## ✅ **Benefits of This Approach**

1. **Clear Separation of Concerns:**
   - Experience Foundation = User-facing communication
   - Agentic Foundation = Agent capabilities
   - Public Works = Infrastructure

2. **Follows Existing Patterns:**
   - SDK pattern (not service)
   - Composition over inheritance
   - Foundation provides capabilities, realms use them

3. **Reusable:**
   - Unified SDK can be used by any realm
   - Agent routing helper can be used by other services
   - Clean abstraction layers

4. **Maintainable:**
   - Changes to agent routing don't affect websocket infrastructure
   - Changes to websocket infrastructure don't affect agent logic
   - Clear ownership boundaries

---

## 🔄 **Migration Path**

### **Phase 1: Create Unified SDK**
- Create `UnifiedAgentWebSocketSDK` in Experience Foundation
- Create `AgentRoutingHelper` in Agentic Foundation
- Test SDK independently

### **Phase 2: Update API Endpoint**
- Update `websocket_router.py` to use unified SDK
- Keep existing endpoints for backward compatibility
- Test unified endpoint

### **Phase 3: Frontend Migration**
- Update frontend to use unified endpoint
- Test all agent interactions

### **Phase 4: Deprecate Old Endpoints**
- Mark old endpoints as deprecated
- Remove after migration complete

---

## 📝 **Updated Experience Foundation Service**

**File:** `foundations/experience_foundation/experience_foundation_service.py`

```python
class ExperienceFoundationService(FoundationServiceBase):
    # ... existing code ...
    
    # Add unified agent websocket SDK
    self._unified_agent_websocket_sdk: Optional[UnifiedAgentWebSocketSDK] = None
    
    async def get_unified_agent_websocket_sdk(self) -> Optional[UnifiedAgentWebSocketSDK]:
        """
        Get Unified Agent WebSocket SDK instance.
        
        Returns:
            UnifiedAgentWebSocketSDK instance, or None if not available
        """
        if not self._unified_agent_websocket_sdk:
            try:
                self.logger.info("🔧 Initializing Unified Agent WebSocket SDK...")
                self._unified_agent_websocket_sdk = UnifiedAgentWebSocketSDK(self)
                await self._unified_agent_websocket_sdk.initialize()
                self.logger.info("✅ Unified Agent WebSocket SDK initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Unified Agent WebSocket SDK: {e}")
                return None
        
        return self._unified_agent_websocket_sdk
```

---

## 🎯 **Recommendation**

**Place unified agent websocket in Experience Foundation SDK** with composition of Agentic Foundation for agent routing.

**Reasons:**
1. ✅ User-facing capability (Experience Foundation domain)
2. ✅ Follows existing SDK patterns
3. ✅ Clean separation of concerns
4. ✅ Composable architecture
5. ✅ Reusable across realms

**Implementation:**
- Create `UnifiedAgentWebSocketSDK` in Experience Foundation
- Create `AgentRoutingHelper` in Agentic Foundation (optional, for cleaner separation)
- Update API endpoint to use unified SDK
- Migrate frontend to unified endpoint

