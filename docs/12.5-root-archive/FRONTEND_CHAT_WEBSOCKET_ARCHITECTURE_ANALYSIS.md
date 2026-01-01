# Frontend Chat/WebSocket Architecture Analysis

## Executive Summary

The frontend has **multiple parallel implementations** for chat/WebSocket functionality with **inconsistent patterns** and **missing liaison agent WebSocket connections**. This analysis maps the current state before finalizing the backend architecture.

---

## Current Frontend Architecture

### 1. Guide Agent Implementations (DUPLICATE)

#### A. `useExperienceChat.ts` Hook
**Location**: `shared/hooks/useExperienceChat.ts`

**WebSocket Endpoints:**
- Guide Agent: `/api/ws/guide-chat` (line 40)
- Specialist Agent: `/api/ws/agent-wise-chat` (line 82)

**Architecture:**
- Direct WebSocket connections (no service layer)
- Manages both `guide` and `specialist` agents in one hook
- Uses `activeAgent` state to switch between agents
- Message format:
  ```json
  {
    "event_type": "chat_message",
    "message": "user message",
    "session_token": "token",
    "user_id": "user"
  }
  ```

**Usage Pattern:**
- Hook-based (functional component pattern)
- Returns `{ messages, sendMessage, startGuideChat, startSpecialistChat }`
- Used by components that need chat functionality

**Issues:**
- Endpoint `/api/ws/guide-chat` doesn't exist in backend
- Endpoint `/api/ws/agent-wise-chat` doesn't exist in backend
- "Specialist" is ambiguous (could be Experience Specialist or Liaison agent)

---

#### B. `GuideAgentProvider.tsx` Context Provider
**Location**: `shared/agui/GuideAgentProvider.tsx`

**WebSocket Endpoint:**
- Guide Agent: `/guide-agent` (line 147)

**Architecture:**
- Uses `SimpleWebSocketService` (service layer abstraction)
- Context provider pattern (React Context API)
- More sophisticated with journey/solution creation
- Message format:
  ```json
  {
    "type": "guidance_request",
    "data": {
      "message": "user message",
      "session_token": "token",
      "user_context": {...},
      "conversation_history": [...]
    },
    "timestamp": 1234567890
  }
  ```

**Usage Pattern:**
- Provider-based (wraps app/component tree)
- Exposes `useGuideAgent()` hook
- Used by components that need Guide Agent context

**Issues:**
- Endpoint `/guide-agent` doesn't exist in backend
- Different message format than `useExperienceChat`
- Parallel implementation (duplication)

---

### 2. Liaison Agent Implementations (INCONSISTENT)

#### A. `SecondaryChatbot.tsx` Component
**Location**: `shared/components/chatbot/SecondaryChatbot.tsx`

**WebSocket Endpoint:**
- Unified: `/smart-chat` (line 75) - **NOT per-pillar**

**Architecture:**
- Single WebSocket connection for ALL liaison agents
- Routes messages via `agent_type` and `current_pillar` in message payload
- Message format:
  ```json
  {
    "message": "user message",
    "session_token": "token",
    "agent_type": "guide" | "currentPillar",
    "current_pillar": "content" | "insights" | "operations" | "business_outcomes",
    "file_context": {
      "file_uuid": "uuid"
    }
  }
  ```

**Usage Pattern:**
- Component-based (self-contained chat UI)
- Uses `agentInfo` from Jotai atoms to determine current agent
- Handles all liaison agents through one connection

**Issues:**
- Endpoint `/smart-chat` doesn't exist in backend
- Uses unified WebSocket (not separate per-pillar)
- Relies on Smart City system for routing (not explicit pillar endpoints)

---

#### B. `LiaisonAgentsAPIManager.ts` REST API Manager
**Location**: `shared/managers/LiaisonAgentsAPIManager.ts`

**REST API Endpoints:**
- Send Message: `/api/v1/liaison-agents/send-message-to-pillar-agent` (POST)
- Get History: `/api/v1/liaison-agents/get-pillar-conversation-history/{sessionId}/{pillar}` (GET)

**Architecture:**
- REST API calls (NOT WebSocket)
- Pillar-specific via `pillar` parameter
- Message format:
  ```json
  {
    "message": "user message",
    "pillar": "content" | "insights" | "operations" | "business-outcomes",
    "session_id": "session_id",
    "conversation_id": "conversation_id",
    "user_id": "user_id"
  }
  ```

**Usage Pattern:**
- Manager class (service layer pattern)
- Used by components that need REST API access
- Pillar-specific via parameter

**Issues:**
- Uses REST (not WebSocket) - inconsistent with Guide Agent
- Different pattern than SecondaryChatbot
- Not used by SecondaryChatbot (which uses WebSocket)

---

#### C. `ContentLiaisonAgent.tsx` Component
**Location**: `components/liaison-agents/ContentLiaisonAgent.tsx`

**Architecture:**
- **NO WebSocket or REST API connection**
- Local state management only
- Simulated AI responses (setTimeout)
- Just UI component with no real backend integration

**Usage Pattern:**
- Standalone component
- Provides guidance UI but no actual chat functionality

**Issues:**
- Not connected to backend at all
- Simulated responses only

---

### 3. WebSocket Service Layers

#### A. `SimpleWebSocketService`
**Location**: `shared/services/SimpleServiceLayer.ts`

**Features:**
- Basic WebSocket connection management
- Connection pooling (Map of connections)
- Subscribe/unsubscribe pattern
- Used by `GuideAgentProvider`

**Limitations:**
- No automatic reconnection
- No message queuing
- No heartbeat/ping
- Basic error handling

---

#### B. `WebSocketService`
**Location**: `shared/services/WebSocketService.ts`

**Features:**
- Advanced WebSocket management
- Automatic reconnection with exponential backoff
- Message queuing
- Heartbeat/ping support
- Event listener pattern
- Session integration

**Status:**
- More sophisticated but **NOT USED** by current implementations
- Available but unused

---

## Architecture Issues Identified

### 1. **Duplicate Guide Agent Implementations**
- `useExperienceChat.ts` and `GuideAgentProvider.tsx` both implement Guide Agent chat
- Different endpoints, different message formats, different patterns
- No clear winner or consolidation

### 2. **Missing Liaison Agent WebSocket**
- `SecondaryChatbot` uses unified `/smart-chat` endpoint (doesn't exist)
- `LiaisonAgentsAPIManager` uses REST APIs (inconsistent with Guide Agent)
- `ContentLiaisonAgent` has no backend connection at all
- **No per-pillar WebSocket endpoints** for liaison agents

### 3. **Inconsistent Patterns**
- Guide Agent: Two different implementations (hook vs context provider)
- Liaison Agents: Three different patterns (unified WebSocket, REST API, no connection)
- No standard message format
- No standard WebSocket endpoint pattern

### 4. **Endpoint Mismatches**
- Frontend expects: `/api/ws/guide-chat`, `/guide-agent`, `/smart-chat`, `/api/ws/agent-wise-chat`
- Backend provides: `/api/chat/guide` (REST), `/api/chat/liaison` (REST)
- **NO WebSocket endpoints exist in backend**

### 5. **Service Layer Underutilization**
- `WebSocketService` (advanced) exists but not used
- `SimpleWebSocketService` (basic) is used by GuideAgentProvider
- Direct WebSocket connections used by useExperienceChat and SecondaryChatbot
- No consistent service layer pattern

---

## Recommended Frontend Architecture (To Align With Backend)

### Option A: Unified WebSocket Service Layer (Recommended)

**Pattern:**
- Single `WebSocketService` instance (use existing advanced one)
- Standardized message format
- Per-agent WebSocket connections

**WebSocket Endpoints:**
- Guide Agent: `/api/ws/guide`
- Liaison Agents: `/api/ws/liaison/{pillar}` (per pillar: content, insights, operations, business_outcomes)

**Implementation:**
1. **Consolidate Guide Agent**: Choose one implementation (recommend `GuideAgentProvider` pattern, but update to use advanced `WebSocketService`)
2. **Create Liaison Agent Hook**: `useLiaisonChat(pillar)` hook that connects to `/api/ws/liaison/{pillar}`
3. **Standardize Message Format**: Use backend-defined format
4. **Update Components**: Use hooks/service layer, not direct WebSocket

**Pros:**
- Consistent pattern across all agents
- Per-pillar explicit routing (matches backend architecture)
- Reuses existing advanced WebSocketService
- Clear separation of concerns

**Cons:**
- Requires refactoring multiple components
- Need to choose between hook vs context provider pattern

---

### Option B: Unified WebSocket Endpoint (Alternative)

**Pattern:**
- Single WebSocket endpoint: `/api/ws/chat`
- Route messages via `agent_type` and `pillar` in message payload

**WebSocket Endpoint:**
- All Agents: `/api/ws/chat`

**Message Format:**
```json
{
  "type": "chat_message",
  "agent_type": "guide" | "liaison",
  "pillar": "content" | "insights" | "operations" | "business_outcomes" | null,
  "message": "user message",
  "session_token": "token",
  "conversation_id": "conversation_id"
}
```

**Pros:**
- Single connection per user
- Simpler routing logic
- Matches `SecondaryChatbot` current pattern

**Cons:**
- Less explicit (routing in message payload)
- Harder to debug (which agent is handling?)
- Doesn't match backend's role-based architecture

---

## Questions to Answer Before Backend Implementation

### 1. **Guide Agent Pattern**
- **Q**: Should we use hook pattern (`useExperienceChat`) or context provider pattern (`GuideAgentProvider`)?
- **Recommendation**: Context provider (more scalable, better for complex state)

### 2. **Liaison Agent Pattern**
- **Q**: Per-pillar WebSocket endpoints (`/api/ws/liaison/{pillar}`) or unified endpoint (`/api/ws/chat`)?
- **Recommendation**: Per-pillar (matches backend architecture, explicit routing)

### 3. **Message Format**
- **Q**: What is the standard message format for all agents?
- **Recommendation**: Use backend-defined format (to be determined)

### 4. **Service Layer**
- **Q**: Use existing `WebSocketService` (advanced) or create new one?
- **Recommendation**: Use existing `WebSocketService`, extend if needed

### 5. **Component Consolidation**
- **Q**: Consolidate `useExperienceChat` and `GuideAgentProvider`?
- **Recommendation**: Yes, consolidate to `GuideAgentProvider` pattern

### 6. **Liaison Agent Components**
- **Q**: How should `SecondaryChatbot`, `LiaisonAgentsAPIManager`, and `ContentLiaisonAgent` be unified?
- **Recommendation**: 
  - Create `useLiaisonChat(pillar)` hook
  - Update `SecondaryChatbot` to use hook
  - Deprecate `LiaisonAgentsAPIManager` REST calls (move to WebSocket)
  - Update `ContentLiaisonAgent` to use hook

---

## Frontend Implementation Plan (After Backend is Ready)

### Phase 1: Consolidate Guide Agent
1. Choose `GuideAgentProvider` as the standard
2. Update to use advanced `WebSocketService`
3. Update endpoint to `/api/ws/guide`
4. Deprecate `useExperienceChat` (or merge into GuideAgentProvider)

### Phase 2: Create Liaison Agent Hook
1. Create `useLiaisonChat(pillar: string)` hook
2. Use `WebSocketService` to connect to `/api/ws/liaison/{pillar}`
3. Standardize message format

### Phase 3: Update Components
1. Update `SecondaryChatbot` to use `useLiaisonChat` hook
2. Update `ContentLiaisonAgent` to use `useLiaisonChat` hook
3. Remove REST API calls from `LiaisonAgentsAPIManager` (or keep as fallback)

### Phase 4: Standardize Message Format
1. Create shared message format types
2. Update all components to use standard format
3. Ensure backend and frontend formats match

---

## Backend Endpoint Requirements (Based on Frontend Analysis)

### Required WebSocket Endpoints:
1. `/api/ws/guide` - Guide Agent WebSocket
2. `/api/ws/liaison/content` - Content Liaison Agent WebSocket
3. `/api/ws/liaison/insights` - Insights Liaison Agent WebSocket
4. `/api/ws/liaison/operations` - Operations Liaison Agent WebSocket
5. `/api/ws/liaison/business_outcomes` - Business Outcomes Liaison Agent WebSocket

### Message Format (To Be Standardized):
```typescript
interface WebSocketMessage {
  type: 'chat_message' | 'guidance_request' | 'liaison_query' | 'system';
  agent_type?: 'guide' | 'liaison';
  pillar?: 'content' | 'insights' | 'operations' | 'business_outcomes';
  message: string;
  session_token: string;
  conversation_id?: string;
  user_id?: string;
  metadata?: {
    timestamp?: string;
    context?: any;
  };
}
```

---

## Next Steps

1. **Answer Questions Above**: Decide on patterns before implementing backend
2. **Update Backend Plan**: Adjust `WEBSOCKET_CHAT_ARCHITECTURE_REFACTOR_PLAN.md` based on frontend requirements
3. **Create Frontend Refactor Plan**: Detailed plan for consolidating frontend implementations
4. **Implement Backend First**: Get WebSocket endpoints working
5. **Then Refactor Frontend**: Align frontend with backend architecture

---

## Files to Review/Update

### Frontend Files:
- `shared/hooks/useExperienceChat.ts` - Consolidate or deprecate
- `shared/agui/GuideAgentProvider.tsx` - Update to use `/api/ws/guide`
- `shared/components/chatbot/SecondaryChatbot.tsx` - Update to use per-pillar endpoints
- `shared/managers/LiaisonAgentsAPIManager.ts` - Deprecate REST or keep as fallback
- `components/liaison-agents/ContentLiaisonAgent.tsx` - Add real WebSocket connection
- `shared/services/WebSocketService.ts` - Use this as the standard service layer

### Backend Files (From Previous Plan):
- `backend/api/websocket_router.py` - Create with endpoints above
- `foundations/communication_foundation/...` - Expose WebSocket capabilities
- `backend/smart_city/services/traffic_cop/...` - Add WebSocket SOA APIs
- `foundations/experience_foundation/services/chat_service/...` - Refactor to WebSocket

