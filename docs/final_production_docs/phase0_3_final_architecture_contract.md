# Phase 0.3: Final Architecture Contract

**Date:** January 2025  
**Status:** ✅ COMPLETE - Authoritative Architecture Document  
**Purpose:** Single source of truth for final architecture, incorporating all findings and decisions from Phase 0.1 and Phase 0.2

---

## Executive Summary

This document is the **authoritative architecture contract** for the Symphainy Platform. It incorporates:
- Findings from Phase 0.1 Deep Dive Analysis
- Decisions from Phase 0.2 Communication Pattern Pressure Test
- Decisions from Phase 0.2 Traffic Cop/Post Office Boundaries
- Content Steward/Data Steward consolidation decision

**This document becomes law** - all subsequent work must align with this contract.

---

## 1. Architectural North Star

Symphainy is a **purpose-driven, data-centric, city-governed platform**.

- **Infrastructure exists first**
- **Foundations exist before behavior**
- **Smart City governs activation**
- **Purpose (Solutions) drives execution**
- **Data enters once, meaning propagates everywhere**

Everything below enforces these truths.

---

## 2. Lifecycle Layers (Canonical)

```
┌─────────────────────────────────────────────┐
│ INFRASTRUCTURE (containers, networks, infra)│
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ UTILITIES (logging, config, DI, telemetry)  │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ FOUNDATIONS (Experience, Agentic, Data, etc)│
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ SMART CITY (City Manager, governance layer) │
│         (REALM with business logic)          │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ REALMS (Solution → Journey → Insights →     │
│        Content)                              │
└─────────────────────────────────────────────┘
```

**Key Principles:**
- **Experience is a Foundation**, not a realm
- **Agentic is a Foundation**, not a realm
- **Smart City is a Realm** (with business logic, not just governance)
- **Realms are called top-down by purpose**, not bottom-up by data

---

## 3. City Manager Lifecycle Contract

The **City Manager** is the *only* component allowed to:
- Decide *what* activates
- Decide *when* it activates
- Decide *why* it activates

Nothing else bootstraps realms.

### 3.1 City Manager Responsibilities

| Responsibility        | Description                       |
| --------------------- | --------------------------------- |
| Lifecycle Governance  | Owns platform startup states      |
| Dependency Resolution | Ensures prerequisites exist       |
| Lazy Activation       | Activates realms only when needed |
| Health Enforcement    | Prevents traffic until ready      |
| Contract Enforcement  | Ensures realms obey interfaces    |

**Note:** City Manager provides **lifecycle governance**, not business logic exclusion. Smart City is a realm with business logic.

### 3.2 City Manager States

```python
class CityManagerState(Enum):
    INFRA_WAIT = "infra_wait"
    UTILITIES_READY = "utilities_ready"
    FOUNDATIONS_READY = "foundations_ready"
    CITY_READY = "city_ready"
    PLATFORM_IDLE = "platform_idle"
    REALM_ACTIVE = "realm_active"
```

### 3.3 City Manager Interface

```python
class CityManager(Protocol):
    async def wait_for_infrastructure(self) -> None:
        """Block until all infrastructure dependencies are healthy"""
    
    async def initialize_utilities(self) -> None:
        """ConfigAdapter, DI container, logging, telemetry"""
    
    async def initialize_foundations(self) -> None:
        """Experience, Agentic, Data foundations"""
    
    async def start_city(self) -> None:
        """Smart City governance online"""
    
    async def activate_solution(self, solution_id: str) -> None:
        """Top-down activation entrypoint"""
    
    async def get_state(self) -> CityManagerState:
        """Current lifecycle state"""
```

**Critical rule:** Nothing outside Smart City may activate a realm directly.

---

## 4. Realm Activation Dependency Graph

**Execution flows opposite of data flow.**

### 4.1 Canonical Realm Roles

| Realm    | Role                                    |
| -------- | --------------------------------------- |
| Solution | WHY (business outcome)                  |
| Journey  | HOW (workflow orchestration)            |
| Insights | ANALYSIS (quality, semantics, meaning)  |
| Content  | DATA FRONT DOOR (data mash entry point) |

### 4.2 Dependency Graph (Activation)

```
Solution
   ↓
Journey
   ↓
Insights
   ↓
Content
```

**Interpretation:**
- A **Solution** determines *why* anything runs
- A **Journey** determines *how* it runs
- **Insights** determines *what meaning exists*
- **Content** supplies raw data (once, at the door)

### 4.3 Dependency Rules (Non-Negotiable)

1. Content is **never activated directly**
2. Insights activates Content **only if needed**
3. Journeys activate Insights **only if needed**
4. Solutions are the **only public entrypoint**

This preserves the **Data Mash vision**: "Clients leave their data at the door; meaning propagates."

---

## 5. Smart City Realm (Critical Clarification)

**Smart City IS a realm** and **DOES NOT have business logic exclusion**.

### 5.1 Smart City Role

**WHAT (Smart City Realm):** Orchestrate platform infrastructure capabilities and provide business functionality

**Key Principle:** Smart City provides **critical business functionality** and elevates platform infrastructure capabilities to **first-class citizens**.

### 5.2 Smart City Services (8 Services)

| Service | Business Functionality | Platform Capability Elevated |
|---------|----------------------|----------------------------|
| **City Manager** | Platform lifecycle governance, manager hierarchy orchestration, realm activation | Lifecycle Management |
| **Post Office** | Strategic communication orchestration, messaging, event distribution, WebSocket Gateway | Messaging & Routing |
| **Traffic Cop** | API Gateway routing, session management, state synchronization, rate limiting | Session & State, API Gateway |
| **Security Guard** | Zero-trust security, multi-tenancy, authentication/authorization, audit logging | Security |
| **Librarian** | Knowledge discovery, metadata governance, semantic search, content organization | Knowledge |
| **Nurse** | Health monitoring, telemetry collection, alert management, distributed tracing | Telemetry & Tracing |
| **Data Steward** | Data lifecycle management, file lifecycle, data governance, quality compliance | Data Management |
| **Conductor** | Workflow orchestration, task management, BPMN processing, cross-service coordination | Workflow & Orchestration |

**Note:** Content Steward has been **consolidated into Data Steward** (to be archived).

### 5.3 Smart City Business Logic

**All Smart City services have business logic:**
- Security Guard: Security policies, multi-tenancy rules
- Traffic Cop: Routing decisions, load balancing strategies
- Post Office: Message routing, event distribution logic
- Librarian: Knowledge discovery algorithms, search strategies
- Nurse: Health monitoring rules, alert thresholds
- Data Steward: Data governance policies, quality rules
- Conductor: Workflow orchestration patterns
- City Manager: Lifecycle governance, activation rules

**This is correct and expected** - Smart City is a realm with business logic.

### 5.4 Smart City Privilege

**Smart City services have direct abstraction access** (no Platform Gateway):
- Access Public Works abstractions directly
- Avoids circular dependencies
- Smart City privilege is architectural, not just convenience

**Other realms access Smart City capabilities via:**
- Post Office SOA APIs (for messaging/events/WebSocket)
- Platform Gateway (for other Smart City capabilities)
- Direct access only for Smart City services

---

## 6. Foundation Services

### 6.1 Foundation Inventory

| Foundation | Why Foundation | Business Logic | Access Pattern |
|------------|---------------|----------------|----------------|
| **Public Works** | Infrastructure swappability | No (pure infrastructure) | Via abstractions |
| **Curator** | All realms need pattern enforcement, registry | Yes (acceptable - all realms need) | Via DI Container |
| **Experience** | All realms need experience SDK | Yes (acceptable - all realms need) | Via SDK builders |
| **Agentic** | All realms need agentic SDK | Yes (acceptable - all realms need) | Via SDK components |
| **Platform Gateway** | All realms need abstraction access control | Yes (acceptable - all realms need) | Via Platform Gateway |

### 6.2 Foundation Principles

**Foundations exist because all realms need access:**
- Curator: Pattern enforcement, service discovery (all realms need)
- Experience: Frontend Gateway, Session Manager, User Experience SDK (all realms need)
- Agentic: Agent SDK, agent types, tool composition (all realms need)
- Platform Gateway: Realm abstraction access control (all realms need)

**Business logic in foundations is acceptable** when all realms need access to that business logic.

### 6.3 Public Works Foundation

**Primary Purpose:** Infrastructure swappability

**Key Principle:** Abstractions follow **HOW we would swap infrastructure**, even if not currently swappable (e.g., FastAPI, Pandas).

**5-Layer Architecture:**
1. **Layer 0:** Infrastructure Adapters (Raw Technology - Redis, Supabase, GCS, ArangoDB)
2. **Layer 1:** Infrastructure Abstractions (Business Logic - with injected adapters)
3. **Layer 2:** Composition Services (Orchestration)
4. **Layer 3:** Infrastructure Registries (Initialization & Discovery)
5. **Layer 4:** Foundation Service (Public Works Foundation Service)

**Swappable Abstractions:**
- Messaging (Redis → NATS/RabbitMQ)
- Event Management (Redis → NATS/Kafka)
- File Management (Supabase/GCS → S3/Azure)
- Session (Redis → Memcached/Database)

**Non-Swappable Infrastructure:**
- FastAPI, Pandas, asyncio, httpx → Used via **direct library injection** (correct pattern)

---

## 7. Communication Pattern (Phase 0.2 Decision)

**Decision:** ✅ **Smart City Roles (Traffic Cop + Post Office)** manage communications

### 7.1 Architecture

```
Smart City Realm
  ├── Post Office Role (WHAT: Orchestrate messaging & event distribution)
  │   ├── Messaging Service (HOW)
  │   ├── Event Distribution Service (HOW)
  │   └── WebSocket Gateway Service (HOW)
  │
  └── Traffic Cop Role (WHAT: Orchestrate session & routing)
      ├── Session Management Service (HOW)
      ├── API Gateway Routing Service (HOW)
      └── State Synchronization Service (HOW)
       ↓
All Realms (via Post Office SOA APIs + Platform Gateway)
  - Smart City: Direct access (no Platform Gateway)
  - Other Realms: Via Platform Gateway → Post Office SOA APIs
```

### 7.2 Rationale

1. **Already implemented** - WebSocket Gateway is Post Office capability (Phase 1-2 complete)
2. **No circular dependencies** - Smart City roles have direct abstraction access
3. **Smart City privilege required** - Communication requires direct abstraction access
4. **SOA API pattern** - Other realms access via Post Office SOA APIs (correct pattern)
5. **Business logic** - Communication involves business logic (routing decisions, messaging)

### 7.3 Why Not Communication Foundation?

- Would create circular dependencies (Communication Foundation ↔ Smart City)
- Would require major refactoring (WebSocket Gateway already Post Office)
- Communication requires Smart City privilege (direct abstraction access)
- Communication involves business logic (belongs in Smart City roles)

---

## 8. Traffic Cop vs Post Office Boundaries (Phase 0.2 Decision)

**Decision:** ✅ **Keep API Gateway and WebSocket Gateway separate**

### 8.1 Traffic Cop: Transport Routing

**WHAT:** Orchestrate transport routing and session/state infrastructure

**Responsibilities:**
1. **API Gateway Routing** (Transport)
   - HTTP request routing
   - Load balancing
   - Rate limiting
   - Request/response transformation
   - **Pure transport** - routes HTTP requests to services

2. **Session Management** (Infrastructure)
   - Session lifecycle (create/get/update/destroy)
   - Session validation
   - **Infrastructure capability** - used by both HTTP and WebSocket

3. **State Synchronization** (Infrastructure)
   - Cross-service state sync
   - State management
   - **Infrastructure capability** - platform-wide state

4. **Traffic Analytics** (Observability)
   - HTTP traffic metrics
   - Request analytics
   - Performance monitoring

**Boundary Rule:** Traffic Cop handles **transport routing** (HTTP → services) and **infrastructure capabilities** (sessions, state) used by transport.

### 8.2 Post Office: Messaging Routing

**WHAT:** Orchestrate messaging and event distribution

**Responsibilities:**
1. **Messaging** (Logical Routing)
   - Send/get messages
   - Message routing (logical - channels, recipients)
   - Message delivery
   - **Logical routing** - messages → channels/recipients

2. **Event Distribution** (Logical Routing)
   - Publish/subscribe events
   - Event routing (logical - channels, event types)
   - Event-driven communication
   - **Logical routing** - events → channels/subscribers

3. **WebSocket Gateway** (Transport + Logical Routing)
   - Accept WebSocket connections (transport)
   - Validate sessions via Traffic Cop (uses session abstraction)
   - Route messages to Redis channels (logical routing)
   - Connection lifecycle management
   - **Both transport and logical routing** - WebSocket → channels → agents

4. **Orchestration** (Coordination)
   - Pillar coordination
   - Realm communication
   - Service discovery routing

**Boundary Rule:** Post Office handles **messaging routing** (channels, events, logical routing) and **WebSocket Gateway** (transport + logical routing together).

### 8.3 Key Distinctions

**Transport Routing (Traffic Cop):**
- Protocol: HTTP
- Pattern: Request → Service
- Routing Logic: Based on path, method, headers
- State: Stateless (request/response)
- Purpose: Route HTTP requests to appropriate service

**Messaging Routing (Post Office):**
- Protocol: WebSocket, Redis Pub/Sub, Events
- Pattern: Message → Channel → Agent/Service
- Routing Logic: Based on channel, intent, recipient
- State: Stateful (persistent connections, subscriptions)
- Purpose: Route messages/events to appropriate channels/agents

### 8.4 Why WebSocket Gateway is Post Office (Not Traffic Cop)

**WebSocket Gateway is NOT pure transport:**
1. **Logical Routing:** Routes messages to channels (guide, pillar:content, etc.) - this is messaging logic
2. **Channel-Based:** Uses channel routing (not service routing) - this is messaging pattern
3. **Message Format:** Parses message format (channel, intent, payload) - this is messaging concern
4. **Agent Communication:** Routes to agents via channels - this is messaging domain

**WebSocket Gateway IS transport + messaging:**
- **Transport:** Accepts WebSocket connections (transport layer)
- **Messaging:** Routes messages to channels (logical routing layer)
- **Both:** Needs both transport and messaging capabilities

**Therefore:** WebSocket Gateway belongs in Post Office (messaging domain), not Traffic Cop (transport domain).

---

## 9. Utility Bootstrap Pattern

### 9.1 Bootstrap-Aware Utilities

**Security Authorization Utility:**
- Bootstraps from Public Works Foundation
- Enhanced by Security Guard Service
- All services use via `get_security()` method

**Telemetry Reporting Utility:**
- Bootstraps from Public Works Foundation
- Enhanced by Nurse Service
- All services use via `log_operation_with_telemetry()` method

### 9.2 Bootstrap Sequence

1. DI Container initializes (utilities created but not bootstrapped)
2. Public Works Foundation initializes (bootstraps Security and Telemetry utilities with foundation implementation)
3. Smart City services initialize (Security Guard and Nurse can enhance utilities with Smart City capabilities)
4. All services can use utilities via mixin methods

### 9.3 Critical Pattern

**Bootstrap pattern enables circular dependency avoidance:**
- Services use utilities (via mixin methods)
- Utilities bootstrap from services (foundation or Smart City)
- Pattern is critical - changing would have high impact

**Do not change this pattern** without thorough analysis.

---

## 10. Post Office Evolution

### 10.1 Original Purpose

**Routing** - Post Office was originally designed for routing messages between roles and services based on destination and priority.

### 10.2 Current State

**Strategic Communication Orchestration** - Post Office now focuses on:
- Messaging (send/get messages, message routing)
- Event distribution (publish/subscribe events)
- WebSocket Gateway (transport + logical routing)
- Orchestration (pillar/realm coordination)

### 10.3 Evolution Path

1. **Original:** Routing-focused (message routing between roles/services)
2. **Evolution:** Added messaging capabilities (send/get messages)
3. **Evolution:** Added event distribution (publish/subscribe events)
4. **Evolution:** Added orchestration (pillar/realm coordination)
5. **Current:** WebSocket Gateway integrated (Phase 1-2 complete, Phase 3 in progress)
6. **Current:** Both routing and messaging exist - routing still present but messaging is primary focus

### 10.4 WebSocket Gateway Integration

**Status:** ✅ Implemented (Phase 1-2 complete, Phase 3 in progress)

**Location:** `backend/smart_city/services/post_office/websocket_gateway_service.py`

**Integration Pattern:**
- WebSocket Gateway Service is instantiated by Post Office Service during initialization
- Post Office Service owns WebSocket Gateway (Role=WHAT, Service=HOW)
- WebSocket Gateway extends `SmartCityRoleBase` (direct abstraction access)
- Single `/ws` endpoint via `backend/api/websocket_gateway_router.py`
- Logical channel routing (guide, pillar:content, etc.)

**Current Usage:**
- Single WebSocket endpoint `/ws` for all connections
- Channel-based message routing (not socket-based)
- Traffic Cop integration for session validation
- Redis Pub/Sub for message distribution
- Connection registry (Redis-backed)
- Phase 3 components: FanOutManager, BackpressureManager, SessionEvictionManager (implemented)

---

## 11. Content Steward/Data Steward Consolidation

### 11.1 Decision

**Content Steward to be ARCHIVED**, Data Steward is the consolidated service.

### 11.2 Rationale

- Data Steward already claims consolidation and has file_lifecycle module from Content Steward
- Content Steward functionality overlaps with Data Steward (both handle files, content, metadata)
- Consolidation eliminates duplication and simplifies architecture
- Data Steward's broader scope (data governance, lifecycle, quality) encompasses Content Steward's capabilities

### 11.3 Actions Required

1. **Verify Data Steward capabilities:**
   - ✅ file_lifecycle (already present)
   - Verify: file_processing, parsed_file_processing, content_processing, content_validation, content_metadata
   - Add missing modules to Data Steward if needed

2. **Update Data Steward:**
   - Update `DataStewardServiceProtocol` to include all Content Steward methods
   - Ensure Data Steward SOA APIs expose all Content Steward capabilities
   - Update Data Steward documentation to reflect consolidation

3. **Migrate references:**
   - Update ContentManagerService to use Data Steward API
   - Update EmbeddingService to use Data Steward API
   - Update any other services referencing Content Steward

4. **Archive Content Steward:**
   - Move to `/archive/smart_city/services/content_steward/`
   - Add README explaining why archived and what replaced it
   - Update service registry to remove Content Steward

**Timing:** These actions will be completed during Phase 0.4 (Audit & Catalog) and Phase 3 (Smart City Layer cleanup).

---

## 12. Service Message Flow

### 12.1 HTTP Request Flow

```
User Request
  ↓
Traefik (Edge Gateway)
  ↓
FastAPI App (main.py)
  ↓
Traffic Cop API Gateway (Transport Routing)
  ↓
Service Instance (via load balancing)
  ↓
Response
```

### 12.2 WebSocket Message Flow

```
User WebSocket Connection
  ↓
Traefik (Edge Gateway - /ws route)
  ↓
FastAPI WebSocket Endpoint (/ws)
  ↓
Post Office WebSocket Gateway Service
  ├── Accept connection (transport)
  ├── Validate session via Traffic Cop (infrastructure)
  └── Route message to Redis channel (logical routing)
       ↓
Redis Pub/Sub Channel (websocket:guide, websocket:pillar:content, etc.)
  ↓
Agent Instance (subscribes to channel)
  ↓
Response via Post Office WebSocket Gateway
  ↓
User WebSocket Connection
```

### 12.3 Realm Communication Flow

```
Realm Service
  ↓
Platform Gateway (validates realm access)
  ↓
Post Office SOA API (get_websocket_endpoint, publish_to_agent_channel, etc.)
  ↓
Post Office Service (messaging, events, WebSocket Gateway)
  ↓
Target Realm/Agent
```

---

## 13. Ownership Boundaries

### 13.1 What Owns What

| Component | Owner | Rationale |
|-----------|-------|-----------|
| **API Gateway** | Traffic Cop | Transport routing (HTTP) |
| **WebSocket Gateway** | Post Office | Transport + messaging (WebSocket + channels) |
| **Session Management** | Traffic Cop | Infrastructure capability (used by both HTTP and WebSocket) |
| **Messaging** | Post Office | Logical routing (channels, recipients) |
| **Event Distribution** | Post Office | Logical routing (channels, subscribers) |
| **State Synchronization** | Traffic Cop | Infrastructure capability (cross-service state) |
| **Lifecycle Governance** | City Manager | Platform lifecycle states |
| **Data Lifecycle** | Data Steward | Complete data management (consolidated from Content Steward) |
| **Knowledge Management** | Librarian | Knowledge discovery, metadata governance |
| **Security** | Security Guard | Zero-trust, multi-tenancy, authentication/authorization |
| **Telemetry** | Nurse | Health monitoring, telemetry collection, tracing |
| **Workflow** | Conductor | Workflow orchestration, task management |

### 13.2 What Does NOT Exist Anymore

**Explicitly Removed:**
- ❌ Communication Foundation (archived - use Smart City roles instead)
- ❌ Content Steward (to be archived - consolidated into Data Steward)
- ❌ Multiple WebSocket endpoints (only `/ws` exists)
- ❌ Old WebSocket router implementations
- ❌ Experience Foundation WebSocket handling (WebSocket Gateway is Post Office)

**No Legacy Endpoints:**
- ❌ No `/api/ws/guide`
- ❌ No `/api/ws/liaison`
- ❌ No `/api/ws/agent`
- ✅ Only `/ws` (Post Office Gateway)

---

## 14. Access Patterns

### 14.1 Smart City Services

**Direct Abstraction Access:**
- Smart City services access Public Works abstractions directly
- No Platform Gateway (avoids circular dependencies)
- Smart City privilege is architectural

**Example:**
```python
# Smart City service (Post Office)
self.session_abstraction = self.get_session_abstraction()  # Direct access
self.messaging_abstraction = self.get_messaging_abstraction()  # Direct access
```

### 14.2 Other Realms

**Via Platform Gateway:**
- Other realms access abstractions via Platform Gateway
- Platform Gateway validates realm access
- Platform Gateway grants access to abstractions

**Via Post Office SOA APIs:**
- Other realms access communication capabilities via Post Office SOA APIs
- Post Office SOA APIs exposed via Platform Gateway
- Realms use SOA APIs for messaging, events, WebSocket

**Example:**
```python
# Realm service
post_office_api = await self.get_post_office_api()  # Via Platform Gateway
websocket_endpoint = await post_office_api.get_websocket_endpoint(session_token, realm)
```

### 14.3 Foundations

**All Realms Need Access:**
- Curator: Via DI Container (initialized before Smart City)
- Experience: Via SDK builders (all realms can create experience components)
- Agentic: Via SDK components (all realms can use agent types)
- Platform Gateway: Via Platform Gateway (all realms access abstractions)

---

## 15. Base Classes & Protocols

### 15.1 Base Class Hierarchy

```
ServiceProtocol (base protocol)
  ↓
FoundationServiceProtocol (foundations)
  ↓
FoundationServiceBase (foundation implementations)

ServiceProtocol (base protocol)
  ↓
RealmServiceProtocol (realms)
  ↓
RealmServiceBase (realm implementations)

ServiceProtocol (base protocol)
  ↓
SmartCityRoleProtocol (Smart City roles)
  ↓
SmartCityRoleBase (Smart City implementations)

ServiceProtocol (base protocol)
  ↓
ManagerServiceProtocol (managers)
  ↓
ManagerServiceBase (manager implementations)
```

### 15.2 Protocol Update Principle

**Update protocols to match service implementations**, not vice versa.

**Rationale:**
- Services are well-constructed
- Protocols may not have kept pace with implementations
- Update contracts to match reality

### 15.3 Smart City Protocol Requirements

**Smart City protocols must allow business logic:**
- Security Guard Protocol: Security policies, multi-tenancy rules
- Traffic Cop Protocol: Routing decisions, load balancing strategies
- Post Office Protocol: Message routing, event distribution logic
- All Smart City protocols: Business logic is expected and required

---

## 16. Configuration Contract

### 16.1 Single Source of Truth

**Location:** `utilities/configuration/platform_config.py`

**Requirements:**
- Single validated config schema
- Environment variable mapping
- Default values
- Validation rules
- Fail fast on invalid config

### 16.2 Config Access Pattern

**All config access goes through platform_config:**
- No direct `os.getenv()` calls (except in platform_config itself)
- No hardcoded values
- No duplicate config files
- Config validated at startup

---

## 17. WebSocket Pattern

### 17.1 Single Endpoint

**Only `/ws` endpoint exists:**
- All WebSocket connections go through Post Office Gateway
- No other WebSocket endpoints
- Logical channel routing (not socket routing)

### 17.2 Message Format

```json
{
  "channel": "guide" | "pillar:content" | "pillar:insights" | "pillar:operations" | "pillar:business_outcomes",
  "intent": "chat" | "query" | "command",
  "payload": {
    "message": "user message",
    "conversation_id": "optional",
    "metadata": {}
  }
}
```

### 17.3 Response Format

```json
{
  "type": "response" | "error" | "system",
  "message": "response message",
  "agent_type": "guide" | "liaison",
  "pillar": "pillar name" (if liaison),
  "conversation_id": "conversation ID",
  "data": {...},
  "timestamp": "ISO timestamp"
}
```

### 17.4 Pattern Application

**WebSocket pattern implemented but may not be applied to all bases/services yet:**
- Need to verify all bases/services use new WebSocket pattern
- Need to remove old WebSocket implementations
- Need to update services referencing old pattern

---

## 18. What Does NOT Exist Anymore

### 18.1 Explicitly Removed

- ❌ Communication Foundation (archived - use Smart City roles)
- ❌ Content Steward (to be archived - consolidated into Data Steward)
- ❌ Multiple WebSocket endpoints (only `/ws` exists)
- ❌ Old WebSocket router implementations
- ❌ Experience Foundation WebSocket handling (WebSocket Gateway is Post Office)
- ❌ Public Works WebSocket Foundation Service (removed)

### 18.2 No Legacy Endpoints

- ❌ No `/api/ws/guide`
- ❌ No `/api/ws/liaison`
- ❌ No `/api/ws/agent`
- ✅ Only `/ws` (Post Office Gateway)

### 18.3 No Parallel Implementations

**Only one implementation per concern:**
- One WebSocket Gateway (Post Office)
- One API Gateway (Traffic Cop)
- One messaging system (Post Office)
- One event distribution system (Post Office)
- One session management system (Traffic Cop)

**Everything else is archived or deleted.**

---

## 19. Architectural Decisions Summary

### 19.1 Smart City is a Realm

- **Decision:** Smart City is a realm with business logic, not just governance
- **Rationale:** Smart City provides critical business functionality and elevates platform capabilities to first-class citizens
- **Impact:** All Smart City services have business logic (correct and expected)

### 19.2 Communication Pattern

- **Decision:** Smart City roles (Traffic Cop + Post Office) manage communications
- **Rationale:** Already implemented, no circular dependencies, Smart City privilege required, business logic belongs in Smart City roles
- **Impact:** Other realms access via Post Office SOA APIs

### 19.3 Gateway Boundaries

- **Decision:** Keep API Gateway and WebSocket Gateway separate
- **Rationale:** API Gateway is pure transport (Traffic Cop), WebSocket Gateway is transport + messaging (Post Office)
- **Impact:** Clear separation of concerns, single responsibility

### 19.4 Content Steward Consolidation

- **Decision:** Content Steward to be archived, Data Steward is consolidated service
- **Rationale:** Eliminates duplication, Data Steward's broader scope encompasses Content Steward
- **Impact:** Need to verify Data Steward has all capabilities, migrate references

### 19.5 Public Works Swappability

- **Decision:** Abstractions follow HOW to swap infrastructure, even if not currently swappable
- **Rationale:** Infrastructure swappability is primary concern, more important than business logic exclusion
- **Impact:** Non-swappable infrastructure (FastAPI, Pandas) uses direct library injection

### 19.6 Foundation Business Logic

- **Decision:** Foundations can have business logic when all realms need access
- **Rationale:** Curator, Experience, Agentic have business logic because all realms need access
- **Impact:** Business logic exclusion rule is overridden for foundations

### 19.7 Protocol Update Principle

- **Decision:** Update protocols to match service implementations, not vice versa
- **Rationale:** Services are well-constructed, protocols may not have kept pace
- **Impact:** Review all protocols and update to match actual implementations

### 19.8 Utility Bootstrap Pattern

- **Decision:** Preserve bootstrap pattern for Security and Telemetry utilities
- **Rationale:** Pattern is critical, changing would have high impact, enables circular dependency avoidance
- **Impact:** Do not change bootstrap pattern without thorough analysis

---

## 20. Success Criteria

### 20.1 Architecture Alignment

- ✅ All services follow final architecture vision
- ✅ Lifecycle layers are explicit and enforced
- ✅ City Manager owns lifecycle
- ✅ Realms follow activation dependency graph
- ✅ Smart City is realm with business logic
- ✅ Communication pattern is Smart City roles
- ✅ Gateway boundaries are clear

### 20.2 Anti-Pattern Elimination

- ✅ No parallel implementations of same concept
- ✅ Tests validate outcomes, not internal structure
- ✅ Transport logic separate from domain logic
- ✅ Config has single source of truth
- ✅ Abstractions are stable and clear

### 20.3 Code Quality

- ✅ No duplicate code
- ✅ No unreachable code
- ✅ No commented-out code
- ✅ Clear contracts everywhere
- ✅ Clear documentation

### 20.4 Production Readiness

- ✅ Deterministic startup
- ✅ Health checks at all layers
- ✅ Single WebSocket gateway
- ✅ Clear observability
- ✅ Scaling safety

---

## 21. Implementation Guidelines

### 21.1 When Creating New Services

1. **Determine layer:** Infrastructure → Utilities → Foundations → Smart City → Realms
2. **Choose base class:** FoundationServiceBase, RealmServiceBase, SmartCityRoleBase, ManagerServiceBase
3. **Define protocol:** Create protocol that matches implementation (not vice versa)
4. **Access patterns:** Smart City direct access, other realms via Platform Gateway
5. **Business logic:** Allowed in Smart City and realms, allowed in foundations when all realms need access

### 21.2 When Refactoring Services

1. **Preserve well-constructed services:** Rebuild/refactor, don't delete
2. **Update contracts:** Update protocols to match implementations
3. **Maintain boundaries:** Respect Traffic Cop (transport) vs Post Office (messaging) boundaries
4. **Preserve bootstrap patterns:** Don't change Security/Telemetry bootstrap without analysis
5. **Follow swappability:** Abstractions follow HOW to swap infrastructure

### 21.3 When Adding Communication

1. **HTTP requests:** Use Traffic Cop API Gateway
2. **WebSocket connections:** Use Post Office WebSocket Gateway
3. **Messaging:** Use Post Office messaging APIs
4. **Events:** Use Post Office event APIs
5. **Sessions:** Use Traffic Cop session APIs

---

## 22. Next Steps

This contract is now **law** for all subsequent work:

1. **Phase 0.4:** Audit & Catalog - Use this contract to classify all code
2. **Phase 0.5:** Establish Bases & Protocols - Update to match this contract
3. **Phase 1-7:** Cleanup & Refactoring - Align all code with this contract

---

**Document Status:** ✅ COMPLETE - Authoritative Architecture Contract  
**Last Updated:** January 2025  
**This document is LAW** - all subsequent work must align with this contract.

