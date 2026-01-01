# WebSocket Chat Architecture Refactor Plan (Consolidated)

## Executive Summary

This plan addresses the original issue where the frontend attempts to connect to `/guide-agent` WebSocket endpoint that doesn't exist, and refactors the entire chat architecture to use WebSocket (best practice) while properly implementing the **Communication Foundation as Source of Truth** architecture pattern.

**Root Cause**: The architecture has multiple mismatches:
- **Backend**: Chat Service uses REST APIs (`/api/chat/guide`, `/api/chat/liaison`)
- **Frontend**: Attempts WebSocket connections (`/guide-agent`, `/api/ws/guide-chat`)
- **Communication Foundation**: Has WebSocket infrastructure but isn't being used correctly
- **Smart City Services**: Bypass Platform Gateway and access Public Works directly (should use Communication Foundation via Platform Gateway)
- **Architecture Pattern**: Missing clear separation between WHAT (Communication Foundation) and HOW (Agentic/Experience SDKs + Smart City SOA APIs)

**Solution**: Implement a unified architecture where:
1. **Communication Foundation** = Source of Truth (defines WHAT communication capabilities exist)
2. **Agentic/Experience Foundations** = SDK Providers (expose WebSocket via SDKs - HOW to use)
3. **Smart City Roles** = Controlled Access Layer (access Communication Foundation via Platform Gateway, expose SOA APIs)
4. **Guide Agent** = Composed Capabilities (uses SDKs + SOA APIs for advanced use cases)

---

## Architecture Principles

### 1. Communication Foundation = Source of Truth

**Role**: Defines WHAT communication capabilities exist
- WebSocket infrastructure
- Messaging infrastructure
- Event bus infrastructure
- Realm-aware routing

**Access Pattern**:
- Smart City roles access via **Platform Gateway** (not Public Works)
- Agentic/Experience Foundations use directly for SDKs
- All realms use Communication Foundation as the single source of truth

### 2. Agentic/Experience Foundations = SDK Providers

**Role**: Provide HOW to use communication capabilities
- **Agentic Foundation**: Provides `AgentWebSocketSDK` for agents
- **Experience Foundation**: Provides `ExperienceWebSocketSDK` for user experiences
- SDKs use Communication Foundation infrastructure internally
- Available to all realms (direct SDK access)

**Why SDKs?**
- Prevents spaghetti code (controlled access)
- Provides realm-specific capabilities
- Composable with Smart City SOA APIs

### 3. Smart City Roles = Controlled Access Layer

**Role**: Provide platform communication capabilities via SOA APIs
- **Traffic Cop**: Session/state management SOA APIs
- **Post Office**: Messaging/event bus SOA APIs
- **Conductor**: Workflow/orchestration SOA APIs

**Access Pattern**:
- Access Communication Foundation via **Platform Gateway** (not Public Works)
- Expose SOA APIs for controlled access
- Prevents direct access to infrastructure (spaghetti code prevention)

**Why SOA APIs?**
- Controlled access (not direct infrastructure access)
- Composable with SDKs for advanced capabilities
- Maintains Smart City's role in platform communication

### 4. Guide Agent = Composed Capabilities

**Role**: Uses SDKs + SOA APIs to create advanced capabilities
- Uses **Agentic Foundation WebSocket SDK** (for real-time communication)
- Uses **Traffic Cop SOA API** (for session/state management)
- Uses **Post Office SOA API** (for messaging/event bus)
- Uses **Conductor SOA API** (for workflow/orchestration)

**Why Composition?**
- Realms compose SDKs + SOA APIs + own capabilities
- Advanced capabilities through composition
- Clear separation of concerns

---

## Architecture Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              COMMUNICATION FOUNDATION (Source of Truth)          │
│                                                                  │
│  Provides:                                                       │
│  - WebSocketFoundationService                                   │
│  - MessagingFoundationService                                   │
│  - EventBusFoundationService                                    │
│                                                                  │
│  Access:                                                         │
│  - Smart City → Platform Gateway → Communication Foundation     │
│  - Agentic/Experience → Direct (for SDKs)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Used by
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│  AGENTIC FOUNDATION        │         │  EXPERIENCE FOUNDATION     │
│  (WebSocket SDK)            │         │  (WebSocket SDK)            │
│                             │         │                             │
│  AgentWebSocketSDK          │         │  ExperienceWebSocketSDK    │
│  └─ Uses Communication      │         │  └─ Uses Communication     │
│     Foundation               │         │     Foundation              │
│                             │         │                             │
│  Available to all realms    │         │  Available to all realms    │
└───────────────────────────┘         └───────────────────────────┘
        │                                           │
        │ SDK Access                                │
        │                                           │
        └───────────────────┬───────────────────────┘
                            │
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  GUIDE AGENT              │      │  SMART CITY ROLES         │
│  (Realm Service)           │      │  (Traffic Cop, Post       │
│                           │      │   Office, Conductor)       │
│  Uses:                     │      │                           │
│  ✅ Agentic WebSocket SDK  │      │  Access via:              │
│  ✅ Traffic Cop SOA API    │      │  ✅ Platform Gateway      │
│  ✅ Post Office SOA API    │      │     → Communication       │
│  ✅ Conductor SOA API      │      │     Foundation            │
│                           │      │                           │
│  Composes capabilities    │      │  Expose SOA APIs:         │
│  for advanced use cases   │      │  ✅ Session Management    │
│                           │      │  ✅ Messaging              │
│                           │      │  ✅ Event Routing          │
│                           │      │  ✅ Workflow Orchestration │
└───────────────────────────┘      └──────────────────────────┘
```

---

## Current State Analysis

### 1. Frontend WebSocket Usage

**Files:**
- `symphainy-frontend/shared/hooks/useExperienceChat.ts`
- `symphainy-frontend/shared/agui/GuideAgentProvider.tsx`

**Current Behavior:**
- `useExperienceChat.ts`: Tries to connect to `/api/ws/guide-chat` (line 40)
- `GuideAgentProvider.tsx`: Tries to connect to `/guide-agent` (line 147)
- Both expect WebSocket connections but backend doesn't provide them

**Issues:**
- Duplicate implementations (hook vs context provider)
- Missing liaison agent WebSocket connections
- Inconsistent message formats

### 2. Backend Current Architecture

**REST API Endpoints (Working):**
- `/api/chat/guide` - Guide Agent chat (REST)
- `/api/chat/liaison` - Liaison Agent chat (REST)
- `/api/chat/conversation/create` - Create conversation
- `/api/chat/conversation/history` - Get conversation history

**WebSocket Endpoints (Missing):**
- `/api/ws/guide` - **NOT REGISTERED** (should be created)
- `/api/ws/liaison/{pillar}` - **NOT REGISTERED** (should be created)

### 3. Communication Foundation Capabilities

**Available:**
- `WebSocketFoundationService` - Realm-aware WebSocket infrastructure
- `WebSocketAbstraction` - Abstraction layer for WebSocket operations
- Realm-specific connection managers (smart_city, business_enablement, experience, journey_solution)
- Realm-aware message routing

**Current Usage:**
- **NOT USED** by Smart City services (they bypass via Public Works)
- **NOT USED** by Chat Service
- **NOT EXPOSED** via Platform Gateway correctly

### 4. Platform Gateway Current State

**Smart City Realm Access:**
- Currently has "all access pass" (bypasses Platform Gateway)
- Direct access to Public Works abstractions via `InfrastructureAccessMixin`
- Has access to `messaging`, `event_management`, `websocket` abstractions (should be blocked)

**Other Realms:**
- Go through Platform Gateway
- Have explicit abstraction mappings
- Do NOT have access to communication abstractions (correct)

### 5. Smart City Roles Current State

**Traffic Cop:**
- Session management SOA APIs exist
- WebSocket connection tracking exists (`websocket_connections` dict)
- **NO WebSocket SOA APIs** for chat connections
- Accesses messaging/event via Public Works (should use Communication Foundation via Platform Gateway)

**Post Office:**
- Messaging SOA APIs exist
- Event routing SOA APIs exist
- Accesses messaging/event via Public Works (should use Communication Foundation via Platform Gateway)

**Conductor:**
- Workflow orchestration SOA APIs exist
- Accesses workflow infrastructure via Public Works (correct - not communication)

### 6. Frontend-Backend Pillar Mapping Challenge

**The Challenge:**
- **Frontend**: Uses "pillars" (content, insights, operations, business_outcomes) - a frontend concept
- **Backend**: Uses orchestrators (ContentAnalysisOrchestrator, InsightsOrchestrator, etc.) - backend implementation
- **All Liaison Agents**: Are in the same realm (`business_enablement`) but are conceptually separate (one per pillar/orchestrator)

**Mapping:**
```
Frontend Pillar          →  Backend Orchestrator Key    →  Orchestrator                    →  Liaison Agent
─────────────────────────────────────────────────────────────────────────────────────────────
content                  →  content_analysis            →  ContentAnalysisOrchestrator     →  ContentLiaisonAgent
insights                 →  insights                    →  InsightsOrchestrator            →  InsightsLiaisonAgent
operations               →  operations                  →  OperationsOrchestrator          →  OperationsLiaisonAgent
business_outcomes        →  business_outcomes           →  BusinessOutcomesOrchestrator    →  BusinessOutcomesLiaisonAgent
```

**Key Points:**
1. All orchestrators are in `DeliveryManager.mvp_pillar_orchestrators` dict
2. Each orchestrator has a `liaison_agent` property
3. All liaison agents are in `business_enablement` realm, but each is a separate instance
4. WebSocket routing needs to map frontend pillar → orchestrator → liaison agent

**Solution:**
- WebSocket router maintains pillar-to-orchestrator mapping
- Gets orchestrator from `DeliveryManager.mvp_pillar_orchestrators[orchestrator_key]`
- Gets liaison agent from `orchestrator.liaison_agent`
- Tracks pillar information in WebSocket session for proper routing

---

## Architecture Decision: Separate WebSocket Paths

### Decision: **Separate WebSocket Paths** (`/api/ws/guide`, `/api/ws/liaison/{pillar}`)

**Rationale:**
1. **Explicit Architecture**: Matches our role-based architecture (Guide vs Liaison are different roles)
2. **Realm Separation**: Guide Agent is in `journey_solution` realm, Liaison Agents are in `business_enablement` realm
3. **Frontend Alignment**: Frontend already expects separate connections
4. **Scalability**: Easier to add new agent types without changing routing logic
5. **Debugging**: Clear connection paths make troubleshooting easier

**WebSocket Endpoints:**
- `/api/ws/guide` - Guide Agent WebSocket
- `/api/ws/liaison/{pillar}` - Liaison Agent WebSocket (per pillar: content, insights, operations, business_outcomes)

### Important: Pillar-to-Orchestrator Mapping

**Challenge**: Frontend uses "pillars" (a frontend concept), but backend uses orchestrators. All liaison agents are in the same realm (`business_enablement`) but are conceptually separate (one per pillar/orchestrator).

**Mapping Strategy:**
- **Frontend Pillar** → **Backend Orchestrator Key** → **Orchestrator** → **Liaison Agent**
- `content` → `content_analysis` → `ContentAnalysisOrchestrator` → `ContentLiaisonAgent`
- `insights` → `insights` → `InsightsOrchestrator` → `InsightsLiaisonAgent`
- `operations` → `operations` → `OperationsOrchestrator` → `OperationsLiaisonAgent`
- `business_outcomes` → `business_outcomes` → `BusinessOutcomesOrchestrator` → `BusinessOutcomesLiaisonAgent`

**Implementation:**
- WebSocket router maps pillar name to orchestrator key
- Gets orchestrator from `DeliveryManager.mvp_pillar_orchestrators[orchestrator_key]`
- Gets liaison agent from `orchestrator.liaison_agent`
- All agents are in `business_enablement` realm, but each is a separate instance

---

## Implementation Plan

### Phase 1: Platform Gateway Changes (Foundation)

**Goal**: Block Smart City from accessing communication abstractions via Public Works, force them to use Communication Foundation via Platform Gateway.

#### 1.1 Update Platform Gateway Realm Mappings

**File**: `symphainy_source/symphainy-platform/platform_infrastructure/infrastructure/platform_gateway.py`

**Changes:**
```python
REALM_ABSTRACTION_MAPPINGS = {
    "smart_city": {
        "abstractions": [
            "session", "state", "auth", "authorization", "tenant",
            "file_management", "content_metadata", "content_schema", 
            "content_insights", "llm", "mcp", "policy", "cache",
            "api_gateway"
            # REMOVED: "messaging", "event_management", "websocket", "event_bus"
        ],
        "description": "Smart City - First-class citizen with full access (except communication abstractions)",
        "byoi_support": True
    },
    # ... other realms unchanged
}
```

**Rationale**: Smart City should get communication capabilities from Communication Foundation via Platform Gateway, not Public Works.

#### 1.2 Remove Smart City Bypass Logic

**File**: `symphainy_source/symphainy-platform/bases/mixins/infrastructure_access_mixin.py`

**Changes:**
- Remove special case logic (lines 73-125) that bypasses Platform Gateway for Smart City
- Make Smart City services go through Platform Gateway like all other realms
- Update `get_messaging_abstraction()`, `get_event_management_abstraction()`, `get_websocket_abstraction()` to:
  1. Try Platform Gateway first
  2. If blocked (ValueError), route to Communication Foundation via DI container

**Code Pattern:**
```python
async def get_messaging_abstraction(self):
    """Get messaging abstraction - routes to Communication Foundation if blocked by Platform Gateway."""
    try:
        # Try Platform Gateway first
        if self.platform_gateway:
            return self.platform_gateway.get_abstraction("smart_city", "messaging")
    except ValueError:
        # Blocked by Platform Gateway - route to Communication Foundation
        communication_foundation = self.di_container.get_communication_foundation()
        if communication_foundation:
            return communication_foundation.get_messaging_service()
    # Fallback (should not happen if Platform Gateway is configured correctly)
    raise ValueError("Messaging abstraction not available via Platform Gateway or Communication Foundation")
```

#### 1.3 Update Communication Mixin

**File**: `symphainy_source/symphainy-platform/bases/mixins/communication_mixin.py`

**Changes:**
- Update `get_messaging_abstraction()`, `get_event_management_abstraction()`, `get_websocket_abstraction()` to:
  1. Try Platform Gateway first
  2. If blocked, get from Communication Foundation via DI container
  3. Ensure Communication Foundation is accessed via DI container (not direct import)

---

### Phase 2: Agentic Foundation WebSocket SDK

**Goal**: Create WebSocket SDK for agents that uses Communication Foundation infrastructure.

#### 2.1 Create Agent WebSocket SDK

**File**: `symphainy_source/symphainy-platform/foundations/agentic_foundation/agent_sdk/agent_websocket_sdk.py` (NEW)

**Responsibilities:**
- Provide WebSocket connection management for agents
- Use Communication Foundation WebSocket infrastructure
- Support agent-specific routing (Guide vs Liaison)
- Handle session management integration
- Support pillar-specific routing for liaison agents (all in same realm, but different instances)

**Key Methods:**
```python
class AgentWebSocketSDK:
    async def connect_guide_agent(self, session_token: str) -> str:
        """Connect Guide Agent WebSocket. Returns connection_id."""
        pass
    
    async def connect_liaison_agent(self, pillar: str, session_token: str) -> str:
        """
        Connect Liaison Agent WebSocket. Returns connection_id.
        
        Args:
            pillar: Frontend pillar name (content, insights, operations, business_outcomes)
            session_token: User session token
        
        Note: All liaison agents are in business_enablement realm, but each
        pillar has its own liaison agent instance. The SDK routes to the
        correct agent based on pillar name.
        """
        pass
    
    async def send_agent_message(self, connection_id: str, message: Dict) -> None:
        """Send message via WebSocket."""
        pass
    
    async def receive_agent_message(self, connection_id: str) -> Dict:
        """Receive message via WebSocket."""
        pass
    
    async def disconnect_agent(self, connection_id: str) -> None:
        """Disconnect WebSocket."""
        pass
```

#### 2.2 Integrate with Communication Foundation

**File**: `symphainy_source/symphainy-platform/foundations/agentic_foundation/agentic_foundation_service.py`

**Changes:**
- Add method to create Agent WebSocket SDK:
  ```python
  async def create_agent_websocket_sdk(self) -> AgentWebSocketSDK:
      """Create Agent WebSocket SDK using Communication Foundation."""
      communication_foundation = self.di_container.get_communication_foundation()
      websocket_foundation = communication_foundation.get_websocket_manager()
      return AgentWebSocketSDK(websocket_foundation, self.di_container)
  ```

---

### Phase 3: Smart City Roles Access Communication Foundation

**Goal**: Update Smart City roles to access Communication Foundation via Platform Gateway.

#### 3.1 Update Traffic Cop Service

**File**: `symphainy_source/symphainy-platform/backend/smart_city/services/traffic_cop/traffic_cop_service.py`

**Changes:**
- Update `initialize()` to access messaging/event via Platform Gateway (which routes to Communication Foundation)
- Remove direct Public Works access for communication abstractions
- Keep session/state abstractions from Public Works (not communication)

**Code Pattern:**
```python
async def initialize(self):
    # ✅ Session/state (not communication) - from Public Works via Platform Gateway
    self.session_abstraction = self.get_abstraction("session")  # Via Platform Gateway → Public Works
    
    # ✅ Messaging/event (communication) - from Communication Foundation via Platform Gateway
    self.messaging_abstraction = self.get_abstraction("messaging")  # Via Platform Gateway → Communication Foundation
    self.event_management_abstraction = self.get_abstraction("event_management")  # Via Platform Gateway → Communication Foundation
    
    # ❌ NO direct WebSocket access (WebSocket is via Agentic/Experience SDKs)
    # WebSocket SOA APIs will use Communication Foundation via Platform Gateway internally
```

#### 3.2 Update Post Office Service

**File**: `symphainy_source/symphainy-platform/backend/smart_city/services/post_office/post_office_service.py`

**Changes:**
- Update `initialize()` to access messaging/event via Platform Gateway (which routes to Communication Foundation)
- Remove direct Public Works access for communication abstractions

#### 3.3 Add WebSocket SOA APIs to Traffic Cop

**File**: `symphainy_source/symphainy-platform/backend/smart_city/services/traffic_cop/modules/soa_mcp.py`

**Add SOA APIs:**
```python
"websocket_session": {
    "endpoint": "/soa/websocket-session",
    "methods": ["POST", "GET", "PUT"],
    "description": "WebSocket session management (link WebSocket to Traffic Cop session)"
},
"websocket_message": {
    "endpoint": "/soa/websocket-message",
    "methods": ["POST"],
    "description": "Route WebSocket message through Traffic Cop with session context"
}
```

**Note**: Traffic Cop doesn't directly manage WebSocket connections (that's Agentic/Experience SDKs), but it links WebSocket connections to sessions and routes messages with session context.

#### 3.4 Implement WebSocket Session Management Module

**File**: `symphainy_source/symphainy-platform/backend/smart_city/services/traffic_cop/modules/websocket_session_management.py` (NEW)

**Responsibilities:**
- Link WebSocket connections (from Agentic SDK) to Traffic Cop sessions
- Track WebSocket connections per session
- Route WebSocket messages through session context
- Handle WebSocket reconnection with session persistence

**Key Methods:**
```python
class WebSocketSessionManagement:
    async def link_websocket_to_session(
        self, 
        websocket_id: str, 
        session_id: str,
        agent_type: str = None,  # "guide" or "liaison"
        pillar: str = None        # For liaison agents: "content", "insights", etc.
    ) -> Dict:
        """
        Link WebSocket connection (from Agentic SDK) to Traffic Cop session.
        
        Args:
            websocket_id: WebSocket connection ID from Agentic SDK
            session_id: Traffic Cop session ID
            agent_type: Type of agent ("guide" or "liaison")
            pillar: Pillar name for liaison agents (content, insights, operations, business_outcomes)
        """
        pass
    
    async def get_session_websockets(
        self, 
        session_id: str,
        agent_type: str = None,  # Filter by agent type
        pillar: str = None        # Filter by pillar (for liaison agents)
    ) -> List[str]:
        """
        Get all WebSocket connection IDs for a session.
        
        Args:
            session_id: Traffic Cop session ID
            agent_type: Optional filter by agent type
            pillar: Optional filter by pillar (for liaison agents)
        
        Returns:
            List of WebSocket connection IDs
        """
        pass
    
    async def route_websocket_message(self, websocket_id: str, message: Dict) -> Dict:
        """
        Route WebSocket message with session context.
        
        Args:
            websocket_id: WebSocket connection ID
            message: Message to route
        
        Returns:
            Routed message with session context
        """
        pass
```

---

### Phase 4: Guide Agent Composition

**Goal**: Update Guide Agent to use Agentic Foundation WebSocket SDK + Smart City SOA APIs.

#### 4.1 Update Guide Agent Initialization

**File**: `symphainy_source/symphainy-platform/backend/business_enablement/agents/guide_cross_domain_agent.py`

**Changes:**
```python
class GuideCrossDomainAgent(GlobalGuideAgent):
    async def initialize(self):
        # ✅ Get Agentic Foundation WebSocket SDK
        agentic_foundation = await self.get_foundation_service("AgenticFoundationService")
        self.websocket_sdk = await agentic_foundation.create_agent_websocket_sdk()
        
        # ✅ Get Smart City SOA APIs (via RealmServiceBase helpers)
        self.traffic_cop = await self.get_traffic_cop_api()  # Session/state management
        self.post_office = await self.get_post_office_api()  # Messaging/event bus
        self.conductor = await self.get_conductor_api()      # Workflow/orchestration
        
        # ✅ Connect WebSocket (uses Communication Foundation via SDK)
        self.websocket_connection_id = await self.websocket_sdk.connect_guide_agent(
            session_token=self.session_token
        )
        
        # ✅ Link WebSocket to Traffic Cop session
        await self.traffic_cop.call_soa_api(
            "websocket_session",
            {
                "action": "link",
                "websocket_id": self.websocket_connection_id,
                "session_token": self.session_token
            }
        )
```

#### 4.2 Update Guide Agent Message Handling

**File**: `symphainy_source/symphainy-platform/backend/business_enablement/agents/guide_cross_domain_agent.py`

**Changes:**
```python
async def handle_user_message(self, message: str, session_token: str):
    """Handle user message - composes all capabilities."""
    
    # ✅ Step 1: Session Management (via Traffic Cop SOA API)
    session = await self.traffic_cop.call_soa_api(
        "session_management",
        {
            "action": "get_or_create",
            "session_token": session_token
        }
    )
    
    # ✅ Step 2: Store Message in History (via Post Office SOA API)
    await self.post_office.call_soa_api(
        "send_message",
        {
            "message": message,
            "session_id": session["session_id"],
            "agent": "guide"
        }
    )
    
    # ✅ Step 3: Analyze Intent (agent's own capability)
    intent = await self.analyze_user_intent(message, session)
    
    # ✅ Step 4: Route to Liaison Agent if needed (via Conductor SOA API)
    if intent["needs_liaison"]:
        workflow_result = await self.conductor.call_soa_api(
            "execute_workflow",
            {
                "workflow_id": "liaison_routing",
                "parameters": {
                    "pillar": intent["pillar"],
                    "message": message
                }
            }
        )
    
    # ✅ Step 5: Send Response via WebSocket (via Agentic Foundation SDK)
    response = await self.generate_guidance_response(message, intent, session)
    await self.websocket_sdk.send_agent_message(
        connection_id=self.websocket_connection_id,
        message={
            "type": "chat_response",
            "agent_type": "guide",
            "message": response,
            "session_token": session_token
        }
    )
```

---

### Phase 4.5: Liaison Agent Composition

**Goal**: Update Liaison Agents to use Agentic Foundation WebSocket SDK + Smart City SOA APIs (same pattern as Guide Agent, but pillar-specific).

**Note**: All 4 MVP Liaison Agents (Content, Insights, Operations, Business Outcomes) follow the same pattern but are pillar-specific. They're all in the `business_enablement` realm but are separate instances.

#### 4.5.1 Update Liaison Agent Base Class

**File**: `symphainy_source/symphainy-platform/backend/business_enablement/protocols/business_liaison_agent_protocol.py`

**Changes:**
- Add WebSocket SDK and Smart City SOA API references to `BusinessLiaisonAgentBase`
- Add pillar property to track which pillar this liaison agent serves

**Code Pattern:**
```python
class BusinessLiaisonAgentBase(AgentBase):
    def __init__(self, ...):
        super().__init__(...)
        
        # WebSocket and Smart City SOA API references (initialized in initialize())
        self.websocket_sdk = None
        self.websocket_connection_id = None
        self.pillar = None  # Set by orchestrator (content, insights, operations, business_outcomes)
        self.traffic_cop = None
        self.post_office = None
        self.conductor = None
```

#### 4.5.2 Update Liaison Agent Initialization

**Files**: 
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/content_liaison_agent.py`
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/insights_liaison_agent.py`
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/agents/operations_liaison_agent.py`
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/agents/business_outcomes_liaison_agent.py`

**Changes:**
```python
async def initialize(self):
    """Initialize Liaison Agent with WebSocket SDK and Smart City SOA APIs."""
    
    # Call parent initialize first
    await super().initialize()
    
    # ✅ Get Agentic Foundation WebSocket SDK
    agentic_foundation = self.foundation_services.get_foundation_service("AgenticFoundationService")
    self.websocket_sdk = await agentic_foundation.create_agent_websocket_sdk()
    
    # ✅ Get Smart City SOA APIs (via OrchestratorBase helpers - inherited from parent)
    # Note: Liaison agents are created by orchestrators, which have access to Smart City APIs
    # We need to get these via the orchestrator or directly via PlatformCapabilitiesMixin
    self.traffic_cop = await self.get_traffic_cop_api()  # Session/state management
    self.post_office = await self.get_post_office_api()  # Messaging/event bus
    self.conductor = await self.get_conductor_api()      # Workflow/orchestration
    
    # ✅ Set pillar (from orchestrator context or domain name)
    # ContentLiaisonAgent → "content"
    # InsightsLiaisonAgent → "insights"
    # OperationsLiaisonAgent → "operations"
    # BusinessOutcomesLiaisonAgent → "business_outcomes"
    self.pillar = self._determine_pillar_from_agent_name()
    
    # Note: WebSocket connection is established per-session (not per-agent)
    # The connection is created when a user connects via the WebSocket endpoint
    # See Phase 5 for WebSocket endpoint implementation
```

#### 4.5.3 Update Liaison Agent Message Handling

**Files**: Same as 4.5.2

**Changes:**
```python
async def handle_user_message(self, message: str, session_token: str, pillar: str):
    """
    Handle user message - composes all capabilities.
    
    Args:
        message: User message
        session_token: User session token
        pillar: Pillar name (content, insights, operations, business_outcomes)
    """
    
    # ✅ Step 1: Session Management (via Traffic Cop SOA API)
    session = await self.traffic_cop.call_soa_api(
        "session_management",
        {
            "action": "get_or_create",
            "session_token": session_token
        }
    )
    
    # ✅ Step 2: Store Message in History (via Post Office SOA API)
    # Note: Conversation history is stored per agent_type (pillar-specific)
    agent_type = f"{pillar}_liaison"  # e.g., "content_liaison", "insights_liaison"
    await self.post_office.call_soa_api(
        "send_message",
        {
            "message": message,
            "session_id": session["session_id"],
            "agent": agent_type,
            "pillar": pillar
        }
    )
    
    # ✅ Step 3: Analyze Intent (agent's own capability)
    intent = await self.analyze_user_intent(message, session, pillar)
    
    # ✅ Step 4: Coordinate with Orchestrator (agent's own capability)
    orchestrator_response = await self.coordinate_with_orchestrator(intent, session)
    
    # ✅ Step 5: Send Response via WebSocket (via Agentic Foundation SDK)
    # Note: websocket_connection_id is passed from WebSocket endpoint (per-session)
    response = await self.generate_liaison_response(message, intent, session, pillar)
    
    # Return response (WebSocket endpoint will send it)
    return {
        "type": "chat_response",
        "agent_type": "liaison",
        "pillar": pillar,
        "message": response,
        "session_token": session_token,
        "session_id": session["session_id"]
    }
```

#### 4.5.4 Update Orchestrator Liaison Agent Initialization

**Files**:
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/insights_orchestrator.py`
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/operations_orchestrator.py`
- `symphainy_source/symphainy-platform/backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/business_outcomes_orchestrator.py`

**Changes:**
- After creating liaison agent via `initialize_agent()`, set the `pillar` property:
```python
# After initializing liaison agent
self.liaison_agent = await self.initialize_agent(...)

# Set pillar for this liaison agent
if self.liaison_agent:
    self.liaison_agent.pillar = "content"  # or "insights", "operations", "business_outcomes"
    # The liaison agent will use this pillar for WebSocket routing and conversation history
```

**Key Differences from Guide Agent:**
1. **Pillar-Specific**: Each liaison agent is tied to a specific pillar
2. **Per-Session WebSocket**: WebSocket connections are created per-session (not per-agent instance)
3. **Conversation History**: Stored per `agent_type` (pillar-specific) in SessionManagerService
4. **Orchestrator Context**: Liaison agents coordinate with their specific orchestrator

---

### Phase 5: Backend WebSocket Endpoints

**Goal**: Create FastAPI WebSocket endpoints that use the new architecture.

#### 5.1 Create WebSocket Router

**File**: `symphainy_source/symphainy-platform/backend/api/websocket_router.py` (NEW)

**Key Challenge**: Frontend uses "pillars" (content, insights, operations, business_outcomes) but backend uses orchestrators (ContentAnalysisOrchestrator, InsightsOrchestrator, etc.). All liaison agents are in the same realm (`business_enablement`) but are conceptually separate (one per pillar/orchestrator).

**Pillar-to-Orchestrator Mapping:**
```python
PILLAR_TO_ORCHESTRATOR_MAP = {
    "content": {
        "orchestrator_key": "content_analysis",  # Key in DeliveryManager.mvp_pillar_orchestrators
        "orchestrator_name": "ContentAnalysisOrchestrator",
        "liaison_agent_name": "ContentLiaisonAgent"
    },
    "insights": {
        "orchestrator_key": "insights",
        "orchestrator_name": "InsightsOrchestrator",
        "liaison_agent_name": "InsightsLiaisonAgent"
    },
    "operations": {
        "orchestrator_key": "operations",
        "orchestrator_name": "OperationsOrchestrator",
        "liaison_agent_name": "OperationsLiaisonAgent"
    },
    "business_outcomes": {
        "orchestrator_key": "business_outcomes",
        "orchestrator_name": "BusinessOutcomesOrchestrator",
        "liaison_agent_name": "BusinessOutcomesLiaisonAgent"
    }
}
```

**Endpoints:**
```python
@router.websocket("/api/ws/guide")
async def guide_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """Guide Agent WebSocket endpoint."""
    # 1. Accept WebSocket connection
    await websocket.accept()
    
    # 2. Validate session via Traffic Cop SOA API
    traffic_cop = await get_traffic_cop_service()
    session = await traffic_cop.call_soa_api("session_management", {
        "action": "get_or_create",
        "session_token": session_token
    })
    
    # 3. Get Guide Agent (via Journey Manager or Delivery Manager)
    guide_agent = await get_guide_agent()
    
    # 4. Connect Guide Agent WebSocket (via Agentic Foundation SDK)
    agentic_foundation = await get_agentic_foundation()
    websocket_sdk = await agentic_foundation.create_agent_websocket_sdk()
    connection_id = await websocket_sdk.connect_guide_agent(session_token)
    
    # 5. Link WebSocket to Traffic Cop session
    await traffic_cop.call_soa_api("websocket_session", {
        "action": "link",
        "websocket_id": connection_id,
        "session_id": session["session_id"]
    })
    
    # 6. Message loop
    try:
        while True:
            message = await websocket.receive_json()
            # Route to Guide Agent (which handles via its composed capabilities)
            response = await guide_agent.handle_user_message(
                message["message"],
                session_token
            )
            await websocket.send_json(response)
    except WebSocketDisconnect:
        # Cleanup
        await websocket_sdk.disconnect_agent(connection_id)
        await traffic_cop.call_soa_api("websocket_session", {
            "action": "unlink",
            "websocket_id": connection_id
        })

@router.websocket("/api/ws/liaison/{pillar}")
async def liaison_agent_websocket(websocket: WebSocket, pillar: str, session_token: str = Query(None)):
    """
    Liaison Agent WebSocket endpoint (per pillar).
    
    Args:
        pillar: Frontend pillar name (content, insights, operations, business_outcomes)
        session_token: User session token
    
    Architecture:
    - Frontend pillar → Backend orchestrator → Liaison agent
    - All liaison agents are in business_enablement realm
    - Each orchestrator has its own liaison_agent property
    - Conversation history persists in SessionManagerService (survives pillar switches)
    """
    # 1. Accept WebSocket connection
    await websocket.accept()
    
    # 2. Validate pillar name
    if pillar not in PILLAR_TO_ORCHESTRATOR_MAP:
        await websocket.close(code=4004, reason=f"Invalid pillar: {pillar}")
        return
    
    pillar_config = PILLAR_TO_ORCHESTRATOR_MAP[pillar]
    
    # 3. Get SessionManagerService for conversation history persistence
    session_manager = await get_session_manager_service()
    
    # 4. Get or create session (via SessionManagerService)
    session_result = await session_manager.get_or_create_session(
        user_id=session_token,  # Use session_token as user_id for now
        context={"pillar": pillar}
    )
    session_id = session_result["session"]["session_id"]
    
    # 5. Map pillar to agent_type for conversation history
    agent_type_map = {
        "content": "content_liaison",
        "insights": "insights_liaison",
        "operations": "operations_liaison",
        "business_outcomes": "business_outcomes_liaison"
    }
    agent_type = agent_type_map[pillar]
    
    # 6. Restore conversation history from SessionManagerService
    conversation_history = await session_manager.get_conversation_history(
        session_id=session_id,
        agent_type=agent_type
    )
    
    # 7. Send conversation history to frontend (so UI can restore chat)
    if conversation_history["success"] and conversation_history["messages"]:
        await websocket.send_json({
            "type": "conversation_restored",
            "agent_type": agent_type,
            "pillar": pillar,
            "messages": conversation_history["messages"],
            "message_count": len(conversation_history["messages"])
        })
    
    # 8. Validate session via Traffic Cop SOA API (for session linking)
    traffic_cop = await get_traffic_cop_service()
    traffic_cop_session = await traffic_cop.call_soa_api("session_management", {
        "action": "get_or_create",
        "session_token": session_token
    })
    
    # 9. Get orchestrator from Delivery Manager
    delivery_manager = await get_delivery_manager()
    orchestrator = delivery_manager.mvp_pillar_orchestrators.get(pillar_config["orchestrator_key"])
    
    if not orchestrator:
        await websocket.close(code=4005, reason=f"Orchestrator not available: {pillar_config['orchestrator_name']}")
        return
    
    # 10. Get liaison agent from orchestrator
    liaison_agent = orchestrator.liaison_agent
    
    if not liaison_agent:
        await websocket.close(code=4006, reason=f"Liaison agent not available: {pillar_config['liaison_agent_name']}")
        return
    
    # 11. Connect Liaison Agent WebSocket (via Agentic Foundation SDK)
    agentic_foundation = await get_agentic_foundation()
    websocket_sdk = await agentic_foundation.create_agent_websocket_sdk()
    connection_id = await websocket_sdk.connect_liaison_agent(
        pillar=pillar,
        session_token=session_token
    )
    
    # 12. Link WebSocket to Traffic Cop session
    await traffic_cop.call_soa_api("websocket_session", {
        "action": "link",
        "websocket_id": connection_id,
        "session_id": traffic_cop_session["session_id"],
        "agent_type": "liaison",
        "pillar": pillar
    })
    
    # 13. Message loop (with conversation history persistence)
    try:
        while True:
            message = await websocket.receive_json()
            
            # Store user message in conversation history
            await session_manager.add_conversation_message(
                session_id=session_id,
                agent_type=agent_type,
                role="user",
                content=message.get("message", ""),
                orchestrator_context={"pillar": pillar}
            )
            
            # Route to Liaison Agent (which handles via its orchestrator)
            response = await liaison_agent.handle_user_message(
                message["message"],
                session_token,
                pillar=pillar
            )
            
            # Store agent response in conversation history
            await session_manager.add_conversation_message(
                session_id=session_id,
                agent_type=agent_type,
                role="assistant",
                content=response.get("message", ""),
                orchestrator_context={"pillar": pillar}
            )
            
            await websocket.send_json(response)
    except WebSocketDisconnect:
        # Cleanup
        await websocket_sdk.disconnect_agent(connection_id)
        await traffic_cop.call_soa_api("websocket_session", {
            "action": "unlink",
            "websocket_id": connection_id
        })
```

#### 5.2 Register WebSocket Router

**File**: `symphainy_source/symphainy-platform/main.py`

**Changes:**
- Import WebSocket router
- Register with FastAPI app: `app.include_router(websocket_router)`
- Ensure it's registered after API routers but before startup completion

---

### Phase 6: Frontend Alignment

**Goal**: Update frontend to use correct WebSocket endpoints and message format.

#### 6.1 Consolidate Guide Agent Implementation

**File**: `symphainy_source/symphainy-frontend/shared/agui/GuideAgentProvider.tsx`

**Changes:**
- Update endpoint: `/guide-agent` → `/api/ws/guide`
- Use existing `WebSocketService` (advanced service layer)
- Update message format to match backend standard
- Handle WebSocket reconnection with session persistence

#### 6.2 Create Liaison Agent Hook

**File**: `symphainy_source/symphainy-frontend/shared/hooks/useLiaisonChat.ts` (NEW)

**Implementation:**
```typescript
export function useLiaisonChat(pillar: 'content' | 'insights' | 'operations' | 'business_outcomes') {
  const [messages, setMessages] = useState<Message[]>([]);
  const [connected, setConnected] = useState(false);
  const websocketService = useWebSocketService();
  
  useEffect(() => {
    const connection = websocketService.connect(`/api/ws/liaison/${pillar}`);
    
    connection.on('message', (message: WebSocketMessage) => {
      setMessages(prev => [...prev, message]);
    });
    
    connection.on('connect', () => setConnected(true));
    connection.on('disconnect', () => setConnected(false));
    
    return () => {
      websocketService.disconnect(connection.id);
    };
  }, [pillar]);
  
  const sendMessage = (message: string) => {
    websocketService.send(connection.id, {
      type: 'chat_message',
      agent_type: 'liaison',
      pillar: pillar,
      message: message,
      session_token: getSessionToken()
    });
  };
  
  return { messages, sendMessage, connected };
}
```

#### 6.3 Update Components

**Files:**
- `symphainy_source/symphainy-frontend/shared/components/chatbot/SecondaryChatbot.tsx`
- `symphainy_source/symphainy-frontend/components/liaison-agents/ContentLiaisonAgent.tsx`

**Changes:**
- Use `useLiaisonChat(pillar)` hook instead of direct WebSocket
- Remove duplicate implementations
- Standardize message format

#### 6.4 Deprecate Duplicate Implementations

**File**: `symphainy_source/symphainy-frontend/shared/hooks/useExperienceChat.ts`

**Changes:**
- Deprecate or merge into `GuideAgentProvider`
- Remove duplicate Guide Agent implementation

---

## Implementation Order

### Step 1: Platform Gateway Changes (Foundation)
1. Update Platform Gateway realm mappings (block communication abstractions for Smart City)
2. Remove Smart City bypass logic in InfrastructureAccessMixin
3. Update Communication Mixin to route to Communication Foundation
4. **Test**: Verify Smart City roles can access Communication Foundation via Platform Gateway

### Step 2: Agentic Foundation WebSocket SDK
1. Create Agent WebSocket SDK
2. Integrate with Communication Foundation
3. Add SDK creation method to Agentic Foundation Service
4. **Test**: Verify SDK can create WebSocket connections using Communication Foundation

### Step 3: Smart City Roles Access Communication Foundation
1. Update Traffic Cop to use Platform Gateway for communication abstractions
2. Update Post Office to use Platform Gateway for communication abstractions
3. Add WebSocket SOA APIs to Traffic Cop
4. Implement WebSocket session management module
5. **Test**: Verify Smart City roles can access Communication Foundation and expose SOA APIs

### Step 4: Guide Agent Composition
1. Update Guide Agent to use Agentic Foundation WebSocket SDK
2. Update Guide Agent to use Smart City SOA APIs
3. Update Guide Agent message handling to compose capabilities
4. **Test**: Verify Guide Agent can handle messages using composed capabilities

### Step 4.5: Liaison Agent Composition
1. Update BusinessLiaisonAgentBase to include WebSocket SDK and Smart City SOA API references
2. Update all 4 MVP Liaison Agents (Content, Insights, Operations, Business Outcomes) initialization
3. Update Liaison Agent message handling to compose capabilities (pillar-specific)
4. Update orchestrators to set pillar property on liaison agents
5. **Test**: Verify Liaison Agents can handle messages using composed capabilities (per pillar)

### Step 5: Backend WebSocket Endpoints
1. Create WebSocket router
2. Implement WebSocket handlers
3. Register with FastAPI app
4. **Test**: Verify WebSocket endpoints work end-to-end

### Step 6: Frontend Alignment
1. Consolidate Guide Agent implementation
2. Create Liaison Agent hook
3. Update components
4. Deprecate duplicate implementations
5. **Test**: Verify frontend can connect to WebSocket endpoints

---

## Testing Strategy

### Unit Tests
- Platform Gateway realm access validation
- Communication Foundation WebSocket methods
- Agentic Foundation WebSocket SDK
- Traffic Cop WebSocket SOA APIs
- Guide Agent capability composition
- Liaison Agent capability composition (per pillar)

### Integration Tests
- WebSocket connection establishment (Agentic SDK → Communication Foundation)
- Message routing through Traffic Cop → Guide Agent
- Message routing through Traffic Cop → Liaison Agents (per pillar)
- Session persistence across WebSocket reconnections
- Multi-agent WebSocket connections (Guide + multiple Liaison agents)
- Smart City roles accessing Communication Foundation via Platform Gateway

### End-to-End Tests
- Frontend → Backend WebSocket connection
- Guide Agent chat via WebSocket
- Liaison Agent chat via WebSocket (per pillar)
- Session management with WebSocket
- Error handling and reconnection
- Capability composition (SDKs + SOA APIs)

---

## Success Criteria

1. ✅ Frontend can connect to `/api/ws/guide` WebSocket endpoint
2. ✅ Frontend can connect to `/api/ws/liaison/{pillar}` WebSocket endpoints
3. ✅ Messages are routed correctly through Traffic Cop → Guide Agent
4. ✅ Sessions persist across WebSocket reconnections
5. ✅ Smart City services use Communication Foundation via Platform Gateway (not Public Works)
6. ✅ Platform Gateway blocks Smart City from accessing communication abstractions via Public Works
7. ✅ Agentic Foundation provides WebSocket SDK that uses Communication Foundation
8. ✅ Guide Agent composes SDKs + SOA APIs for advanced capabilities
9. ✅ All realms use consistent access patterns (via Platform Gateway or SDKs)
10. ✅ No spaghetti code (controlled access via SDKs and SOA APIs)

---

## Rollback Strategy

### If Issues Arise:
1. **Keep REST APIs**: Maintain REST API endpoints as fallback
2. **Feature Flag**: Add feature flag to enable/disable WebSocket (fallback to REST)
3. **Gradual Rollout**: Enable WebSocket for Guide Agent first, then Liaison agents
4. **Monitoring**: Add extensive logging and metrics for WebSocket connections
5. **Platform Gateway**: Can temporarily revert to allow Smart City direct Public Works access if needed

---

## Conversation History Persistence Across Pillar Switches

### The Challenge

When users switch between pillars (content → insights → back to content), they disconnect and reconnect WebSocket connections. **Question**: Do they lose their conversation context?

### The Solution: SessionManagerService Integration

**Key Insight**: Conversation history is stored in `SessionManagerService` per agent type, NOT in the liaison agent's in-memory state.

**Session Structure:**
```python
session = {
    "session_id": "session_123",
    "user_id": "user_456",
    "conversations": {
        "content_liaison": {
            "conversation_id": "conv_content_session_123",
            "messages": [
                {"role": "user", "content": "How do I upload a file?", "timestamp": "..."},
                {"role": "assistant", "content": "You can upload files by...", "timestamp": "..."}
            ],
            "orchestrator_context": {"pillar": "content"}
        },
        "insights_liaison": {
            "conversation_id": "conv_insights_session_123",
            "messages": [...],
            "orchestrator_context": {"pillar": "insights"}
        },
        # ... other liaison agents
    }
}
```

### How It Works

1. **On WebSocket Connect**:
   - Get session from `SessionManagerService` (using `session_token`)
   - Retrieve conversation history for the specific agent type (`content_liaison`, `insights_liaison`, etc.)
   - Send conversation history to frontend so UI can restore chat
   - Liaison agent receives conversation history as context

2. **During Conversation**:
   - Each message (user + agent) is stored via `SessionManagerService.add_conversation_message()`
   - Messages are stored with `agent_type` (pillar-specific) and `session_id`
   - Conversation history persists even if WebSocket disconnects

3. **On Pillar Switch**:
   - Frontend disconnects from `/api/ws/liaison/content`
   - Frontend connects to `/api/ws/liaison/insights`
   - New connection retrieves `insights_liaison` conversation history
   - When user switches back to content, `content_liaison` conversation history is restored

4. **On Reconnect**:
   - Same `session_token` → Same `session_id` → Same conversation history
   - Frontend receives `conversation_restored` message with all previous messages
   - UI can restore chat UI with full history

### Benefits

✅ **No Context Loss**: Conversation history persists across pillar switches  
✅ **Per-Pillar Isolation**: Each pillar has its own conversation thread  
✅ **Session Persistence**: Conversations survive page refreshes (stored in Redis/ArangoDB)  
✅ **Orchestrator Context**: Can track orchestrator workflows in conversation context  
✅ **Multi-Connection Support**: User can have Guide + multiple Liaison connections simultaneously

### Implementation Details

**WebSocket Handler Pattern:**
```python
# On connect: Restore conversation history
conversation_history = await session_manager.get_conversation_history(
    session_id=session_id,
    agent_type="content_liaison"  # pillar-specific
)

# Send to frontend for UI restoration
await websocket.send_json({
    "type": "conversation_restored",
    "messages": conversation_history["messages"]
})

# During conversation: Persist each message
await session_manager.add_conversation_message(
    session_id=session_id,
    agent_type="content_liaison",
    role="user",
    content=user_message
)
```

---

## Open Questions

1. **Agentic Foundation**: Do Guide and Liaison agents support WebSocket/streaming responses?
2. **Backward Compatibility**: Should we maintain REST API endpoints for non-WebSocket clients?
3. **Session Persistence**: How long should WebSocket sessions persist? Should they survive page refreshes?
   - **Answer**: Yes, via `SessionManagerService` - conversations are stored in Redis/ArangoDB, not just in-memory
4. **Multi-Connection**: Can a user have multiple WebSocket connections (Guide + multiple Liaison agents) simultaneously?
   - **Answer**: Yes, each connection is tracked separately in Traffic Cop's WebSocket session management
5. **Rate Limiting**: Should WebSocket connections be rate-limited differently than REST APIs?
6. **Experience Foundation SDK**: Should Experience Foundation also provide a WebSocket SDK, or is Agentic Foundation sufficient?
7. **Conversation History Size**: Should we limit conversation history size? How many messages per agent type?
   - **Recommendation**: Implement pagination or message windowing (e.g., last 100 messages) to prevent unbounded growth

---

## Next Steps

1. **Review this plan** with the team
2. **Answer open questions** before implementation
3. **Create detailed implementation tickets** for each phase
4. **Start with Phase 1** (Platform Gateway changes) as foundation
5. **Test incrementally** after each phase

---

## References

- Communication Foundation Architecture
- Platform Gateway Realm Mappings
- Traffic Cop SOA API Documentation
- Agentic Foundation Service
- Frontend WebSocket Usage Patterns
- Frontend Chat/WebSocket Architecture Analysis
- Unified WebSocket Architecture
