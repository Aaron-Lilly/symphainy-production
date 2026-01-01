# Unified WebSocket Architecture

## Executive Summary

This document defines a **unified WebSocket architecture** that leverages existing `WebSocketFoundationService` (backend) and `WebSocketService` (frontend) to create a standardized, scalable, and maintainable real-time communication system across the platform.

**Key Principles:**
1. **Single Source of Truth**: One protocol, one message format, one service layer per side
2. **Separation of Concerns**: Infrastructure (WebSocket) vs Application (Chat/Agents)
3. **Realm-Aware**: Supports multi-realm architecture (smart_city, business_enablement, experience, journey_solution)
4. **Type-Safe**: Shared TypeScript/Python types for message formats
5. **Observable**: Built-in monitoring, metrics, and health checks

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  Components (React)                                             │
│  ├── GuideAgentProvider.tsx                                     │
│  ├── SecondaryChatbot.tsx                                       │
│  └── ContentLiaisonAgent.tsx                                    │
│                                                                  │
│  Hooks (React)                                                  │
│  ├── useGuideChat() → WebSocketService                          │
│  └── useLiaisonChat(pillar) → WebSocketService                 │
│                                                                  │
│  Service Layer (Pure TypeScript)                                │
│  └── WebSocketService (EXISTING - Enhanced)                    │
│      ├── Connection Management                                  │
│      ├── Message Queueing                                       │
│      ├── Auto-Reconnection                                      │
│      └── Heartbeat/Ping                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket Protocol (RFC 6455)
                              │ Standardized Message Format
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  API Router (FastAPI)                                           │
│  └── websocket_router.py                                        │
│      ├── /api/ws/guide                                         │
│      └── /api/ws/liaison/{pillar}                              │
│                                                                  │
│  Application Services                                           │
│  ├── ChatService (routes to agents)                            │
│  └── TrafficCopService (session management)                    │
│                                                                  │
│  Foundation Service (Infrastructure)                             │
│  └── WebSocketFoundationService (EXISTING - Enhanced)           │
│      ├── Realm-Aware Connection Management                      │
│      ├── Message Routing                                        │
│      ├── Health Monitoring                                      │
│      └── Telemetry                                              │
│                                                                  │
│  Infrastructure Abstraction                                     │
│  └── WebSocketAbstraction (Communication Foundation)            │
│      └── Uses Public Works WebSocket Adapter                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Standardized Message Protocol

**Location**: Shared between frontend and backend

**Backend**: `backend/bases/shared/communication/websocket_message_standard.py` (EXISTS)
**Frontend**: `shared/types/websocket-message.ts` (TO BE CREATED)

#### Message Format

```typescript
// Frontend TypeScript
interface WebSocketMessage {
  // Core fields
  type: MessageType;
  message_id?: string;
  timestamp: string; // ISO8601
  
  // Session management
  session_token: string;
  session_id?: string;
  
  // Agent/Role routing
  agent?: AgentType;
  role?: RoleType;
  pillar?: PillarType; // For liaison agents
  
  // Message content
  message?: string;
  data?: any;
  
  // File context
  file_uuid?: string;
  file_name?: string;
  file_url?: string;
  
  // Metadata
  metadata?: Record<string, any>;
  additional_info?: Record<string, any>;
  
  // Error handling
  error_code?: string;
  error_details?: Record<string, any>;
  
  // Status/Progress
  status?: string;
  progress?: number; // 0.0 to 1.0
  
  // Streaming
  is_streaming?: boolean;
  stream_index?: number;
}
```

```python
# Backend Python (EXISTS - websocket_message_standard.py)
class WebSocketMessage(BaseModel):
    type: MessageType
    message_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    session_token: Optional[str] = None
    session_id: Optional[str] = None
    
    agent: Optional[AgentType] = None
    role: Optional[RoleType] = None
    pillar: Optional[str] = None
    
    message: Optional[str] = None
    data: Optional[Any] = None
    
    file_uuid: Optional[str] = None
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    
    metadata: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None
    
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    status: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    is_streaming: bool = False
    stream_index: Optional[int] = None
```

#### Message Types

```typescript
enum MessageType {
  // User messages
  USER_MESSAGE = "user_message",
  
  // Agent responses
  AGENT_MESSAGE = "agent_message",
  AGENT_STREAMING = "agent_streaming",
  AGENT_COMPLETE = "agent_complete",
  
  // System messages
  SYSTEM_MESSAGE = "system_message",
  ERROR_MESSAGE = "error_message",
  WARNING_MESSAGE = "warning_message",
  
  // Session management
  SESSION_CREATED = "session_created",
  SESSION_UPDATED = "session_updated",
  SESSION_EXPIRED = "session_expired",
  
  // File operations
  FILE_SELECTED = "file_selected",
  FILE_PROCESSING = "file_processing",
  FILE_COMPLETE = "file_complete",
  FILE_ERROR = "file_error",
  
  // Agent-specific
  QUESTION_ANSWER = "question_answer",
  VISUALIZATION_DATA = "visualization_data",
  ANALYSIS_RESULT = "analysis_result",
  WORKFLOW_GENERATED = "workflow_generated",
  SOP_GENERATED = "sop_generated",
  
  // Status updates
  STATUS_UPDATE = "status_update",
  PROGRESS_UPDATE = "progress_update",
}
```

---

### 2. Frontend: Enhanced WebSocketService

**Location**: `shared/services/WebSocketService.ts` (EXISTS - needs enhancement)

#### Current Capabilities ✅
- Connection pooling
- Automatic reconnection with exponential backoff
- Message queuing
- Heartbeat/ping support
- Event listener pattern
- Session integration

#### Enhancements Needed

1. **Standardized Message Format**
   - Use shared `WebSocketMessage` type
   - Validate messages against schema
   - Auto-serialize/deserialize

2. **Agent-Specific Connections**
   - Helper methods: `connectToGuide()`, `connectToLiaison(pillar)`
   - Connection naming: `guide`, `liaison:content`, `liaison:insights`, etc.

3. **Realm Awareness**
   - Track realm per connection
   - Route messages based on realm

4. **Error Handling**
   - Standardized error codes
   - Retry logic with backoff
   - Error event emission

5. **Type Safety**
   - TypeScript types matching backend
   - Type guards for message validation

#### Enhanced API

```typescript
class WebSocketService {
  // Agent-specific connection helpers
  async connectToGuide(sessionToken: string): Promise<string>
  async connectToLiaison(pillar: PillarType, sessionToken: string): Promise<string>
  
  // Message sending with type safety
  async sendMessage(connectionId: string, message: WebSocketMessage): Promise<void>
  
  // Event subscription with type safety
  subscribe<T extends WebSocketMessage>(
    connectionId: string,
    messageType: MessageType,
    handler: (message: T) => void
  ): () => void
  
  // Connection status
  getConnectionStatus(connectionId: string): ConnectionStatus
  isConnected(connectionId: string): boolean
  
  // Health monitoring
  getConnectionHealth(connectionId: string): ConnectionHealth
  getAllConnectionsHealth(): Map<string, ConnectionHealth>
}
```

---

### 3. Backend: Enhanced WebSocketFoundationService

**Location**: `foundations/communication_foundation/foundation_services/websocket_foundation_service.py` (EXISTS - needs enhancement)

#### Current Capabilities ✅
- Realm-specific connection managers
- Connection registry
- Realm-aware message routing
- Security validation
- Tenant validation
- Telemetry and metrics

#### Enhancements Needed

1. **Agent-Specific Routing**
   - Route messages to Guide vs Liaison agents
   - Pillar-specific routing for Liaison agents
   - Integration with ChatService

2. **Session Integration**
   - Link WebSocket connections to Traffic Cop sessions
   - Session persistence across reconnections
   - Session-based message routing

3. **Message Validation**
   - Validate against `WebSocketMessage` schema
   - Type checking for message types
   - Error handling for invalid messages

4. **FastAPI Integration**
   - Register FastAPI WebSocket endpoints
   - Handle WebSocket handshake
   - Integrate with FastAPI middleware

5. **Connection Lifecycle**
   - Proper cleanup on disconnect
   - Connection state management
   - Reconnection handling

#### Enhanced API

```python
class WebSocketFoundationService:
    # Agent-specific connection registration
    async def register_agent_connection(
        self,
        websocket: WebSocket,
        agent_type: str,
        pillar: Optional[str] = None,
        session_token: str = None
    ) -> str:  # Returns connection_id
    
    # Message routing
    async def route_agent_message(
        self,
        connection_id: str,
        message: WebSocketMessage
    ) -> bool
    
    # Session integration
    async def link_connection_to_session(
        self,
        connection_id: str,
        session_id: str
    ) -> bool
    
    # FastAPI integration
    async def handle_fastapi_websocket(
        self,
        websocket: WebSocket,
        endpoint: str,
        session_token: Optional[str] = None
    ) -> None
```

---

## Implementation Layers

### Layer 1: Protocol Definition (Shared)

**Files:**
- `backend/bases/shared/communication/websocket_message_standard.py` (EXISTS)
- `frontend/shared/types/websocket-message.ts` (TO BE CREATED - mirror of Python)

**Responsibilities:**
- Define message format
- Define message types
- Define agent types
- Define error codes
- Shared validation logic

---

### Layer 2: Infrastructure Services

#### Backend: WebSocketFoundationService

**Responsibilities:**
- Connection management (realm-aware)
- Message routing (agent-aware)
- Session integration (Traffic Cop)
- Health monitoring
- Telemetry

**Integration Points:**
- Public Works WebSocket Adapter (infrastructure)
- Traffic Cop Service (session management)
- Chat Service (message routing to agents)

#### Frontend: WebSocketService

**Responsibilities:**
- Connection management (agent-aware)
- Message queuing
- Auto-reconnection
- Heartbeat/ping
- Event emission

**Integration Points:**
- Session Provider (authentication)
- React Context (state management)
- Component hooks (UI integration)

---

### Layer 3: Application Services

#### Backend: ChatService + WebSocket Router

**WebSocket Router** (`backend/api/websocket_router.py`):
```python
@router.websocket("/api/ws/guide")
async def guide_agent_websocket(
    websocket: WebSocket,
    session_token: str = Query(None)
):
    """Guide Agent WebSocket endpoint."""
    # 1. Validate session via Traffic Cop
    # 2. Register connection via WebSocketFoundationService
    # 3. Link to Traffic Cop session
    # 4. Message loop: receive → route via ChatService → send
    pass

@router.websocket("/api/ws/liaison/{pillar}")
async def liaison_agent_websocket(
    websocket: WebSocket,
    pillar: str,
    session_token: str = Query(None)
):
    """Liaison Agent WebSocket endpoint."""
    # Similar to guide but with pillar-specific routing
    pass
```

**ChatService Integration:**
- Receives messages from WebSocket router
- Routes to appropriate agent (Guide or Liaison)
- Returns agent responses
- Handles streaming responses

#### Frontend: React Hooks

**useGuideChat()**:
```typescript
export function useGuideChat(sessionToken: string) {
  const wsService = useWebSocketService();
  const [connectionId, setConnectionId] = useState<string | null>(null);
  
  useEffect(() => {
    wsService.connectToGuide(sessionToken).then(setConnectionId);
    return () => connectionId && wsService.disconnect(connectionId);
  }, [sessionToken]);
  
  const sendMessage = useCallback((message: string) => {
    if (!connectionId) return;
    wsService.sendMessage(connectionId, {
      type: MessageType.USER_MESSAGE,
      message,
      session_token: sessionToken,
      agent: AgentType.GUIDE_AGENT,
    });
  }, [connectionId, sessionToken]);
  
  // ... rest of hook
}
```

**useLiaisonChat(pillar)**:
```typescript
export function useLiaisonChat(pillar: PillarType, sessionToken: string) {
  // Similar to useGuideChat but connects to liaison endpoint
}
```

---

### Layer 4: UI Components

**Components use hooks, hooks use WebSocketService:**

```typescript
// GuideAgentProvider.tsx
export const GuideAgentProvider = ({ children }) => {
  const { sessionToken } = useGlobalSession();
  const guideChat = useGuideChat(sessionToken);
  
  return (
    <GuideAgentContext.Provider value={guideChat}>
      {children}
    </GuideAgentContext.Provider>
  );
};

// SecondaryChatbot.tsx
export default function SecondaryChatbot() {
  const { agentInfo } = useAtomValue(chatbotAgentInfoAtom);
  const { sessionToken } = useGlobalSession();
  const pillar = getPillarFromAgent(agentInfo.agent);
  const liaisonChat = useLiaisonChat(pillar, sessionToken);
  
  // Use liaisonChat.sendMessage, liaisonChat.messages, etc.
}
```

---

## Best Practices Implementation

### 1. Centralized WebSocket Management ✅

**Backend:**
- `WebSocketFoundationService` is the single point of WebSocket management
- All connections go through this service
- Realm-aware connection registry

**Frontend:**
- `WebSocketService` is the single point of WebSocket management
- All components use this service (via hooks)
- Connection pooling and reuse

---

### 2. Clear Communication Protocol ✅

**Message Format:**
- Standardized `WebSocketMessage` type (shared between frontend/backend)
- Type-safe message types (enum)
- Validation on both sides

**Documentation:**
- TypeScript types serve as documentation
- Python Pydantic models serve as documentation
- Shared schema ensures consistency

---

### 3. Robust Connection Management ✅

**Reconnection Logic:**
- Frontend: Automatic reconnection with exponential backoff
- Backend: Connection state tracking and cleanup

**Resource Cleanup:**
- Frontend: Cleanup on component unmount
- Backend: Cleanup on disconnect, timeout handling

**Heartbeat/Ping:**
- Frontend: Sends heartbeat every 30 seconds
- Backend: Tracks last ping, closes stale connections

---

### 4. Security Measures ✅

**Authentication:**
- Session token in WebSocket handshake (query param or header)
- Token validation via Traffic Cop
- User context extraction

**Authorization:**
- Realm-based access control
- Agent-specific permissions
- Zero-trust security model

**Data Validation:**
- Message schema validation (Pydantic on backend, TypeScript on frontend)
- Type checking
- Error handling for invalid messages

---

### 5. Performance and Scalability ✅

**Connection Pooling:**
- Frontend: Reuses connections per agent type
- Backend: Efficient connection registry

**Message Efficiency:**
- JSON message format (lightweight)
- Optional compression for large messages
- Streaming support for long responses

**Monitoring:**
- Backend: Telemetry and metrics (already in WebSocketFoundationService)
- Frontend: Connection health tracking
- Both: Error logging and monitoring

---

### 6. Consistent API Contracts ✅

**Endpoints:**
- `/api/ws/guide` - Guide Agent
- `/api/ws/liaison/{pillar}` - Liaison Agents (per pillar)

**Message Format:**
- Standardized `WebSocketMessage` type
- Consistent field names
- Type-safe enums

**Error Handling:**
- Standardized error codes
- Error message format
- Retry logic

---

## Implementation Plan

### Phase 1: Protocol Standardization

1. **Create Frontend Types** (`shared/types/websocket-message.ts`)
   - Mirror backend `WebSocketMessage` type
   - Export TypeScript enums matching Python enums
   - Type guards for validation

2. **Update Backend Types** (if needed)
   - Ensure `websocket_message_standard.py` is complete
   - Add any missing fields
   - Document all fields

---

### Phase 2: Enhance WebSocketFoundationService

1. **Add Agent-Specific Routing**
   - `register_agent_connection()` method
   - `route_agent_message()` method
   - Integration with ChatService

2. **Add FastAPI Integration**
   - `handle_fastapi_websocket()` method
   - WebSocket handshake handling
   - Session validation

3. **Add Session Integration**
   - `link_connection_to_session()` method
   - Session persistence
   - Reconnection handling

---

### Phase 3: Enhance Frontend WebSocketService

1. **Add Standardized Message Format**
   - Use shared `WebSocketMessage` type
   - Message validation
   - Auto-serialization

2. **Add Agent-Specific Helpers**
   - `connectToGuide()` method
   - `connectToLiaison(pillar)` method
   - Connection naming

3. **Add Type Safety**
   - TypeScript types matching backend
   - Type guards
   - Compile-time type checking

---

### Phase 4: Create WebSocket Router

1. **Create `backend/api/websocket_router.py`**
   - `/api/ws/guide` endpoint
   - `/api/ws/liaison/{pillar}` endpoints
   - Integration with WebSocketFoundationService

2. **Register Router in FastAPI**
   - Add to `main.py`
   - Ensure proper middleware order

---

### Phase 5: Create React Hooks

1. **Create `useGuideChat()` hook**
   - Uses WebSocketService
   - Manages Guide Agent connection
   - Exposes sendMessage, messages, etc.

2. **Create `useLiaisonChat(pillar)` hook**
   - Uses WebSocketService
   - Manages Liaison Agent connection
   - Pillar-specific

---

### Phase 6: Update Components

1. **Update GuideAgentProvider**
   - Use `useGuideChat()` hook
   - Remove direct WebSocket code
   - Use standardized message format

2. **Update SecondaryChatbot**
   - Use `useLiaisonChat(pillar)` hook
   - Remove direct WebSocket code
   - Use standardized message format

3. **Deprecate Old Implementations**
   - Mark `useExperienceChat` as deprecated
   - Update to use new hooks
   - Remove duplicate code

---

## Testing Strategy

### Unit Tests

**Frontend:**
- WebSocketService connection management
- Message serialization/deserialization
- Reconnection logic
- Error handling

**Backend:**
- WebSocketFoundationService connection management
- Message routing
- Session integration
- Error handling

---

### Integration Tests

- Frontend → Backend WebSocket connection
- Message routing through all layers
- Session persistence
- Reconnection handling
- Multi-agent connections

---

### End-to-End Tests

- Guide Agent chat flow
- Liaison Agent chat flow (per pillar)
- Error scenarios
- Network interruption handling
- Session expiration handling

---

## Migration Path

### Step 1: Parallel Implementation
- Implement new architecture alongside existing
- Feature flag to switch between old/new
- Gradual migration

### Step 2: Component Migration
- Migrate GuideAgentProvider first
- Then SecondaryChatbot
- Then other components

### Step 3: Deprecation
- Mark old implementations as deprecated
- Remove after migration complete
- Update documentation

---

## Success Criteria

1. ✅ Single WebSocket service per side (frontend/backend)
2. ✅ Standardized message format (shared types)
3. ✅ Type-safe communication (TypeScript + Python)
4. ✅ Realm-aware routing (multi-realm support)
5. ✅ Agent-specific endpoints (Guide + Liaison per pillar)
6. ✅ Session integration (Traffic Cop)
7. ✅ Robust error handling (standardized errors)
8. ✅ Health monitoring (metrics and telemetry)
9. ✅ Auto-reconnection (frontend)
10. ✅ Resource cleanup (both sides)

---

## Open Questions

1. **Message Compression**: Should we compress large messages?
2. **Rate Limiting**: Should WebSocket connections be rate-limited?
3. **Connection Limits**: Maximum connections per user?
4. **Message Size Limits**: Maximum message size?
5. **Streaming**: How to handle streaming responses (agent_streaming type)?

---

## References

- Backend: `foundations/communication_foundation/foundation_services/websocket_foundation_service.py`
- Backend: `backend/bases/shared/communication/websocket_message_standard.py`
- Frontend: `shared/services/WebSocketService.ts`
- WebSocket RFC 6455: https://tools.ietf.org/html/rfc6455
- FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/

