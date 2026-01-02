# WebSocket Gateway Implementation Plan
## 3-Phase Production-Ready Architecture

**Date:** January 2025  
**Owner:** Post Office (Smart City)  
**Status:** 🚀 Ready for Implementation

---

## Executive Summary

This plan implements a production-ready WebSocket architecture with Post Office as the authoritative owner, following the Role=What, Service=How pattern. The 3-phase approach ensures each phase builds on the previous while anticipating production requirements.

**Key Principles:**
- **Post Office Role (WHAT)**: Orchestrates messaging and event distribution
- **WebSocket Gateway Service (HOW)**: Implements WebSocket transport for Post Office
- **Single Connection Boundary**: One authoritative gateway, all others consume via Post Office SOA APIs
- **Production-First Design**: Phase 1 & 2 anticipate Phase 3 requirements
- **Smart City Direct Access**: Post Office accesses Traffic Cop abstractions directly (no Platform Gateway, avoids circular dependencies)
- **Break and Fix**: No backward compatibility - clean architectural break to prevent anti-patterns
- **Agents via MCP Tools**: Agents access Post Office capabilities via MCP Tools (separate refactoring thread)
- **No Separate Orchestrator**: Post Office IS the orchestrator, WebSocket Gateway is the HOW implementation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Traefik (Edge Gateway)                      │
│              Routes: /ws → websocket-gateway                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│         Post Office Role (Smart City - WHAT)                     │
│  "I orchestrate messaging and event distribution"              │
├─────────────────────────────────────────────────────────────────┤
│  Services (HOW):                                                │
│  ├── WebSocket Gateway Service                                  │
│  │   ├── Connection Management (Phase 1)                        │
│  │   ├── Message Routing (Phase 1)                              │
│  │   ├── Session Integration (Phase 1)                          │
│  │   ├── Redis Fan-Out (Phase 3)                               │
│  │   ├── Backpressure Handling (Phase 3)                       │
│  │   └── Session Eviction (Phase 3)                            │
│  │                                                               │
│  ├── Event Bus Service                                          │
│  │   └── Redis Pub/Sub or NATS (Phase 2)                      │
│  │                                                               │
│  └── Message Routing Service                                    │
│      └── Channel-based routing (Phase 1)                       │
└─────────────────────────────────────────────────────────────────┘
         ↓ (exposes SOA APIs via Platform Gateway)
┌─────────────────────────────────────────────────────────────────┐
│              Other Realms (Consumers)                           │
│  - Experience Realm (frontend WebSocket client)                 │
│  - Business Enablement (agents via Post Office APIs)            │
│  - Journey/Solution Realms                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Stabilize (1-2 days)
**Goal:** Unblock browser testing, establish single connection boundary

### 1.1 Create WebSocket Gateway Service

**Location:** `backend/smart_city/services/post_office/websocket_gateway_service.py`

**Responsibilities:**
- Accept WebSocket connections (single ingress point)
- Validate sessions via Traffic Cop
- Route messages to Redis channels
- Manage connection lifecycle

**Key Features (Phase 1):**
```python
class WebSocketGatewayService:
    """
    WHAT (Post Office Role): I provide WebSocket transport for messaging
    HOW (Service Implementation): I accept connections, validate sessions, route to Redis
    """
    
    async def accept_connection(self, websocket: WebSocket, session_token: str):
        """Accept WebSocket connection, validate session, register with Traffic Cop"""
        
    async def route_message(self, connection_id: str, message: Dict[str, Any]):
        """Route message to appropriate Redis channel based on channel/pillar"""
        
    async def close_connection(self, connection_id: str, reason: str):
        """Close connection and cleanup state"""
```

**Dependencies:**
- Traffic Cop (session validation) - **Direct abstraction access** (Smart City privilege, no Platform Gateway)
- Redis (message channels) - **Direct abstraction access** via Public Works
- Post Office Role (orchestration) - **Parent role** (WHAT)

**Access Pattern:**
```python
# Post Office Service (Smart City) accesses abstractions directly
class WebSocketGatewayService:
    def __init__(self, di_container):
        # Direct Public Works access (Smart City privilege)
        self.session_abstraction = self.get_session_abstraction()  # Traffic Cop
        self.messaging_abstraction = self.get_messaging_abstraction()  # Redis
        # No Platform Gateway needed - avoids circular dependencies
```

**Health Check:**
```python
async def is_ready(self) -> bool:
    """Check if gateway is ready to accept connections"""
    return (
        self.redis_client.ping() and
        await self.traffic_cop.is_healthy() and
        await self.post_office.is_healthy()
    )
```

### 1.2 Create FastAPI WebSocket Endpoint

**Location:** `backend/api/websocket_gateway_router.py` (NEW, separate from existing router)

**Single Endpoint:**
```python
@router.websocket("/ws")
async def websocket_gateway(
    websocket: WebSocket,
    session_token: str = Query(None)
):
    """
    Single WebSocket ingress point.
    All WebSocket connections go through Post Office Gateway.
    """
    gateway_service = get_websocket_gateway_service()  # From DI Container
    await gateway_service.handle_connection(websocket, session_token)
```

**Traefik Configuration:**
```yaml
# docker-compose.yml
labels:
  - "traefik.http.routers.websocket-gateway.rule=PathPrefix(`/ws`)"
  - "traefik.http.routers.websocket-gateway.entrypoints=web"
  - "traefik.http.routers.websocket-gateway.service=backend"
  - "traefik.http.routers.websocket-gateway.middlewares=websocket-chain@file"
  - "traefik.http.routers.websocket-gateway.priority=95"
```

### 1.3 Implement Logical Channel Routing

**Message Format:**
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

**Routing Logic:**
```python
async def _route_to_channel(self, message: Dict[str, Any], connection_id: str):
    """Route message to appropriate Redis channel"""
    channel = message.get("channel", "guide")
    
    # Map channel to Redis channel
    redis_channel = f"websocket:{channel}"
    
    # Publish to Redis (agents subscribe to these channels)
    await self.redis_client.publish(
        redis_channel,
        json.dumps({
            "connection_id": connection_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
    )
```

### 1.4 Integrate with Traffic Cop (Session Management)

**Connection Registration:**
```python
async def _register_connection(self, websocket: WebSocket, session_token: str):
    """Register WebSocket connection with Traffic Cop"""
    # Validate session
    session = await self.traffic_cop.validate_session(session_token)
    if not session:
        raise WebSocketRejected("Invalid session token")
    
    # Register connection
    connection_id = f"ws_{session['user_id']}_{uuid.uuid4().hex[:8]}"
    await self.traffic_cop.register_websocket_connection(
        session_token=session_token,
        connection_id=connection_id,
        metadata={
            "connected_at": datetime.utcnow().isoformat(),
            "user_id": session['user_id']
        }
    )
    
    return connection_id
```

### 1.5 Enforce Readiness Before Accept

**Startup Sequence:**
```python
# In main.py or startup
async def startup():
    # ... other initialization ...
    
    # Wait for WebSocket Gateway readiness
    gateway = di_container.get_service("WebSocketGatewayService")
    max_wait = 60  # seconds
    for _ in range(max_wait):
        if await gateway.is_ready():
            logger.info("✅ WebSocket Gateway ready")
            break
        await asyncio.sleep(1)
    else:
        raise RuntimeError("WebSocket Gateway failed to become ready")
```

**Health Check Endpoint:**
```python
@router.get("/health/websocket-gateway")
async def websocket_gateway_health():
    """Health check for WebSocket Gateway"""
    gateway = get_websocket_gateway_service()
    is_ready = await gateway.is_ready()
    return {
        "status": "ready" if is_ready else "not_ready",
        "dependencies": {
            "redis": gateway.redis_client.ping(),
            "traffic_cop": await gateway.traffic_cop.is_healthy(),
            "post_office": await gateway.post_office.is_healthy()
        }
    }
```

### 1.6 Remove Old WebSocket Implementations (Break and Fix)

**Architectural Decision:** Clean break - no backward compatibility to prevent hidden anti-patterns.

**Steps:**
1. **Remove** existing `websocket_router.py` entirely
2. **Remove** WebSocket handling from `foundations/experience_foundation/sdk/unified_agent_websocket_sdk.py`
3. **Remove** `foundations/public_works_foundation/foundation_services/websocket_foundation_service.py`
4. **Remove** `backend/smart_cities/enabling_services/communication/websocket_service.py` (if exists)
5. **Create** new `/ws` endpoint that routes to Post Office Gateway
6. **Update** frontend to use `/ws` endpoint immediately
7. **Update** all tests to use `/ws` endpoint

**No Legacy Endpoints:**
- ❌ No `/api/ws/guide`
- ❌ No `/api/ws/liaison`
- ❌ No `/api/ws/agent`
- ✅ Only `/ws` (Post Office Gateway)

**Rationale:** Clean architectural break ensures no hidden anti-patterns or misalignment. All code must use the new pattern.

---

## Phase 2: Architecture Cleanup (1-2 weeks)
**Goal:** Formalize platform layers, explicit contracts, service discovery

### 2.1 Formalize Platform Layers

**Layer Separation:**
```
Transport Layer (Traefik + WebSocket Gateway)
  ↓ (accepts connections, validates sessions)
Platform Services (Post Office - event routing)
  ↓ (routes messages to channels)
Domain Services (Experience Foundation SDK - user-facing)
  ↓ (composes Post Office APIs)
Agents (Guide/Liaison - business logic)
  ↓ (subscribe to Redis channels)
```

**Implementation:**
- Remove WebSocket handling from Experience Foundation SDK (keep only API composition)
- Remove WebSocket handling from API router (keep only endpoint registration)
- Centralize all WebSocket logic in Post Office Gateway Service

### 2.2 Replace Implicit Networking with Explicit Contracts

**Service Discovery via Consul:**
```python
# In WebSocketGatewayService initialization
async def register_with_consul(self):
    """Register WebSocket Gateway with Consul"""
    await self.consul_client.agent.service.register(
        name="websocket-gateway",
        service_id=f"websocket-gateway-{socket.gethostname()}",
        address=self.host,
        port=self.port,
        tags=["websocket", "real-time", "post-office"],
        check={
            "http": f"http://{self.host}:{self.port}/health/websocket-gateway",
            "interval": "10s"
        }
    )
```

**Service Discovery for Agents:**
```python
# Agents discover WebSocket Gateway via Consul
async def get_websocket_gateway_url(self):
    """Discover WebSocket Gateway URL via Consul"""
    services = await self.consul_client.health.service(
        "websocket-gateway",
        passing=True
    )
    if not services:
        raise ServiceUnavailable("WebSocket Gateway not available")
    
    service = services[0]['Service']
    return f"ws://{service['Address']}:{service['Port']}/ws"
```

### 2.3 Move Connection State to Redis

**Connection Registry (Redis-backed):**
```python
class ConnectionRegistry:
    """Redis-backed connection registry for horizontal scaling"""
    
    async def register_connection(
        self,
        connection_id: str,
        session_token: str,
        channel: str,
        metadata: Dict[str, Any]
    ):
        """Register connection in Redis"""
        key = f"websocket:connection:{connection_id}"
        await self.redis_client.hset(
            key,
            mapping={
                "session_token": session_token,
                "channel": channel,
                "connected_at": datetime.utcnow().isoformat(),
                "metadata": json.dumps(metadata)
            }
        )
        # Set TTL (default 1 hour, extendable via heartbeat)
        await self.redis_client.expire(key, 3600)
        
        # Add to channel index
        await self.redis_client.sadd(f"websocket:channel:{channel}:connections", connection_id)
        
        # Add to user index (for session management)
        user_id = metadata.get("user_id")
        if user_id:
            await self.redis_client.sadd(f"websocket:user:{user_id}:connections", connection_id)
    
    async def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection metadata from Redis"""
        key = f"websocket:connection:{connection_id}"
        data = await self.redis_client.hgetall(key)
        if not data:
            return None
        
        return {
            "connection_id": connection_id,
            "session_token": data.get("session_token"),
            "channel": data.get("channel"),
            "connected_at": data.get("connected_at"),
            "metadata": json.loads(data.get("metadata", "{}"))
        }
    
    async def unregister_connection(self, connection_id: str):
        """Unregister connection from Redis"""
        # Get connection info before deletion
        conn = await self.get_connection(connection_id)
        if not conn:
            return
        
        # Remove from channel index
        await self.redis_client.srem(
            f"websocket:channel:{conn['channel']}:connections",
            connection_id
        )
        
        # Remove from user index
        user_id = conn['metadata'].get("user_id")
        if user_id:
            await self.redis_client.srem(
                f"websocket:user:{user_id}:connections",
                connection_id
            )
        
        # Delete connection record
        await self.redis_client.delete(f"websocket:connection:{connection_id}")
```

### 2.4 Implement Post Office SOA APIs

**Location:** `backend/smart_city/services/post_office/post_office_service.py`

**APIs for Realm Consumption:**
```python
class PostOfficeService:
    """Post Office Service - exposes SOA APIs for realm consumption"""
    
    async def get_websocket_endpoint(
        self,
        session_token: str,
        realm: str
    ) -> Dict[str, Any]:
        """
        Get WebSocket endpoint URL for realm.
        Used by Experience Realm to get WebSocket URL for frontend.
        
        Note: Realm access validation happens at Platform Gateway level,
        not here. This service trusts Platform Gateway has already validated.
        """
        
        # Get gateway URL from Consul
        gateway_url = await self._get_gateway_url()
        
        return {
            "websocket_url": f"{gateway_url}/ws?session_token={session_token}",
            "channels": ["guide", "pillar:content", "pillar:insights", ...],
            "message_format": {
                "channel": "string",
                "intent": "string",
                "payload": {}
            }
        }
    
    async def publish_to_agent_channel(
        self,
        channel: str,
        message: Dict[str, Any],
        realm: str
    ) -> Dict[str, Any]:
        """
        Publish message to agent channel.
        Used by Business Enablement agents to send messages via WebSocket.
        
        Note: Realm access validation happens at Platform Gateway level.
        This service trusts Platform Gateway has already validated.
        """
        
        # Publish to Redis channel
        redis_channel = f"websocket:{channel}"
        await self.redis_client.publish(
            redis_channel,
            json.dumps({
                "source": realm,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
        
        return {"status": "published", "channel": redis_channel}
    
    async def subscribe_to_channel(
        self,
        channel: str,
        callback: Callable,
        realm: str
    ):
        """
        Subscribe to channel for realm.
        Used by agents to receive messages from WebSocket connections.
        
        Note: Realm access validation happens at Platform Gateway level.
        This service trusts Platform Gateway has already validated.
        
        Future: Agents should access this via MCP Tools (separate refactoring thread).
        """
        
        # Subscribe to Redis channel
        redis_channel = f"websocket:{channel}"
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(redis_channel)
        
        # Start listening
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await callback(data)
```

### 2.5 Update Platform Gateway Mappings

**Location:** `platform_infrastructure/infrastructure/platform_gateway.py`

**Add Post Office WebSocket Capabilities:**
```python
REALM_ABSTRACTION_MAPPINGS = {
    "smart_city": {
        "abstractions": [
            # ... existing abstractions ...
            "websocket_gateway",  # NEW: Post Office exposes WebSocket gateway
            "event_bus",          # NEW: Post Office exposes event bus
            "message_routing"      # NEW: Post Office exposes message routing
        ],
        # ...
    },
    "experience": {
        "abstractions": [
            # ... existing abstractions ...
            "websocket_endpoint",  # NEW: Can request WebSocket endpoint
            "agent_messaging"      # NEW: Can send messages to agents
        ],
        # ...
    },
    "business_enablement": {
        "abstractions": [
            # ... existing abstractions ...
            "agent_channel_publish",  # NEW: Can publish to agent channels
            "agent_channel_subscribe" # NEW: Can subscribe to agent channels
        ],
        # ...
    }
}
```

### 2.6 Architectural Clarifications

**Orchestrator Pattern Question:** Do we need a WebSocket orchestrator like DataSolutionOrchestrator?

**Answer: NO** - Post Office IS the orchestrator. The architecture is:
- **Post Office Role (WHAT)**: Orchestrates messaging and event distribution
- **WebSocket Gateway Service (HOW)**: Implements WebSocket transport
- **No separate orchestrator needed** - Post Office orchestrates, Gateway implements

**Comparison to DataSolutionOrchestrator:**
- DataSolutionOrchestrator orchestrates **multiple journey orchestrators** (complex composition)
- Post Office orchestrates **messaging capabilities** (single domain, simpler)
- WebSocket Gateway is a **service implementation**, not a separate orchestrator

**Agent Access Pattern (Separate Refactoring Thread):**
- **Current (Phase 1-2)**: Agents can use Post Office SOA APIs directly
- **Future (Separate Thread)**: Agents should access via MCP Tools
- **MCP Server Update Needed**: Post Office MCP Server needs to expose WebSocket capabilities as tools
- **This is noted but not blocking** - can be done in parallel or after Phase 3

**Cleanup Already Done in Phase 1:**
- ✅ Removed old WebSocket router (Phase 1.6)
- ✅ Removed Experience Foundation WebSocket SDK handling
- ✅ Removed Public Works WebSocket Foundation Service
- ✅ All code uses new `/ws` endpoint

---

## Phase 3: Production Hardening (2-3 weeks)
**Goal:** Socket fan-out, observability, backpressure, session eviction

### 3.1 Redis Fan-Out Architecture

**Problem:** Single WebSocket Gateway instance can't handle all connections at scale.

**Solution:** Multiple Gateway instances, Redis Pub/Sub for message distribution.

**Architecture:**
```
Frontend Clients
  ↓ (load balanced via Traefik)
Multiple WebSocket Gateway Instances (horizontal scaling)
  ↓ (publish to Redis)
Redis Pub/Sub Channels
  ↓ (subscribe)
Agent Instances (horizontal scaling)
```

**Implementation:**
```python
class WebSocketGatewayService:
    """WebSocket Gateway with Redis fan-out support"""
    
    def __init__(self):
        # Connection management (local to this instance)
        self.local_connections: Dict[str, WebSocket] = {}
        
        # Redis for cross-instance communication
        self.redis_client = get_redis_client()
        self.pubsub = None
        
    async def handle_connection(self, websocket: WebSocket, session_token: str):
        """Handle WebSocket connection"""
        # Accept and register locally
        await websocket.accept()
        connection_id = await self._register_connection(websocket, session_token)
        
        # Subscribe to this connection's channel (for messages from other instances)
        await self._subscribe_to_connection_channel(connection_id)
        
        try:
            # Message loop
            async for message in websocket.iter_text():
                await self._handle_incoming_message(connection_id, message)
        except WebSocketDisconnect:
            await self._handle_disconnect(connection_id)
    
    async def _subscribe_to_connection_channel(self, connection_id: str):
        """Subscribe to Redis channel for this connection"""
        channel = f"websocket:connection:{connection_id}:messages"
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(channel)
        
        # Start background task to forward messages to WebSocket
        asyncio.create_task(self._forward_messages_to_websocket(connection_id))
    
    async def _forward_messages_to_websocket(self, connection_id: str):
        """Forward messages from Redis to WebSocket"""
        websocket = self.local_connections.get(connection_id)
        if not websocket:
            return
        
        channel = f"websocket:connection:{connection_id}:messages"
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await websocket.send_json(data)
                except Exception as e:
                    logger.error(f"Failed to forward message to {connection_id}: {e}")
                    break
    
    async def _handle_incoming_message(self, connection_id: str, message: str):
        """Handle incoming message from WebSocket"""
        # Parse message
        data = json.loads(message)
        channel = data.get("channel", "guide")
        
        # Publish to agent channel (any instance can handle)
        redis_channel = f"websocket:{channel}"
        await self.redis_client.publish(
            redis_channel,
            json.dumps({
                "connection_id": connection_id,
                "message": data,
                "gateway_instance": self.instance_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to connection (works across instances)"""
        # Check if connection is local
        if connection_id in self.local_connections:
            websocket = self.local_connections[connection_id]
            await websocket.send_json(message)
        else:
            # Connection is on another instance, publish to Redis
            channel = f"websocket:connection:{connection_id}:messages"
            await self.redis_client.publish(channel, json.dumps(message))
```

**Agent Subscription Pattern (Current - via SOA APIs):**
```python
# Agent subscribes via Post Office SOA API
class GuideAgent:
    async def initialize(self):
        """Initialize agent and subscribe to guide channel"""
        # Get Post Office API (via Platform Gateway for realms, or direct for Smart City)
        self.post_office = await self.get_post_office_api()
        
        # Subscribe to guide channel
        await self.post_office.subscribe_to_channel(
            channel="guide",
            callback=self._handle_message,
            realm=self.realm_name
        )
    
    async def _handle_message(self, message_data: Dict[str, Any]):
        """Handle messages from WebSocket connections"""
        connection_id = message_data['connection_id']
        user_message = message_data['message']['payload']['message']
        
        # Process message
        response = await self.process_message(user_message)
        
        # Send response back via Post Office
        await self.post_office.send_to_connection(
            connection_id=connection_id,
            message={
                "type": "response",
                "agent_type": "guide",
                "message": response
            }
        )
```

**Future Agent Access Pattern (via MCP Tools - Separate Refactoring):**
```python
# Future: Agent uses MCP Tool
# Tool: "post_office_subscribe_to_channel"
# Tool: "post_office_send_message"
# Implementation: Post Office MCP Server wraps SOA APIs as tools
# This is a separate refactoring thread - not blocking Phase 1-3
```

### 3.2 Observability & Telemetry

**Metrics Collection:**
```python
class WebSocketGatewayMetrics:
    """Metrics collection for WebSocket Gateway"""
    
    def __init__(self):
        self.metrics = {
            "connections_active": 0,
            "connections_total": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "latency_p50": 0,
            "latency_p95": 0,
            "latency_p99": 0
        }
    
    async def record_connection(self):
        """Record new connection"""
        self.metrics["connections_active"] += 1
        self.metrics["connections_total"] += 1
        await self._export_metrics()
    
    async def record_message(self, direction: str, latency_ms: float):
        """Record message with latency"""
        if direction == "sent":
            self.metrics["messages_sent"] += 1
        else:
            self.metrics["messages_received"] += 1
        
        # Update latency percentiles (simplified, use proper histogram in production)
        self._update_latency(latency_ms)
        await self._export_metrics()
    
    async def _export_metrics(self):
        """Export metrics to OpenTelemetry"""
        from opentelemetry import metrics
        
        meter = metrics.get_meter(__name__)
        
        # Gauge for active connections
        active_connections_gauge = meter.create_up_down_counter(
            "websocket.connections.active"
        )
        active_connections_gauge.add(self.metrics["connections_active"])
        
        # Counter for total connections
        total_connections_counter = meter.create_counter(
            "websocket.connections.total"
        )
        total_connections_counter.add(1)
        
        # Counter for messages
        messages_counter = meter.create_counter(
            f"websocket.messages.{direction}"
        )
        messages_counter.add(1)
```

**Distributed Tracing:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def handle_connection(self, websocket: WebSocket, session_token: str):
    """Handle connection with distributed tracing"""
    with tracer.start_as_current_span("websocket.connection") as span:
        span.set_attribute("session_token", session_token)
        span.set_attribute("gateway_instance", self.instance_id)
        
        try:
            await websocket.accept()
            connection_id = await self._register_connection(websocket, session_token)
            span.set_attribute("connection_id", connection_id)
            
            # Message loop with tracing
            async for message in websocket.iter_text():
                with tracer.start_as_current_span("websocket.message") as msg_span:
                    msg_span.set_attribute("connection_id", connection_id)
                    await self._handle_incoming_message(connection_id, message)
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise
```

**Health & Status Endpoint:**
```python
@router.get("/health/websocket-gateway/detailed")
async def websocket_gateway_detailed_health():
    """Detailed health check with metrics"""
    gateway = get_websocket_gateway_service()
    
    return {
        "status": "ready" if await gateway.is_ready() else "not_ready",
        "instance_id": gateway.instance_id,
        "metrics": {
            "connections_active": gateway.metrics.metrics["connections_active"],
            "connections_total": gateway.metrics.metrics["connections_total"],
            "messages_sent": gateway.metrics.metrics["messages_sent"],
            "messages_received": gateway.metrics.metrics["messages_received"],
            "errors": gateway.metrics.metrics["errors"]
        },
        "dependencies": {
            "redis": gateway.redis_client.ping(),
            "traffic_cop": await gateway.traffic_cop.is_healthy(),
            "post_office": await gateway.post_office.is_healthy()
        },
        "uptime_seconds": (datetime.utcnow() - gateway.started_at).total_seconds()
    }
```

### 3.3 Backpressure Handling

**Problem:** Agents can't process messages fast enough, Redis channels fill up.

**Solution:** Implement backpressure with circuit breakers and message queuing.

**Implementation:**
```python
class BackpressureManager:
    """Manages backpressure for WebSocket message flow"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
    
    async def publish_with_backpressure(
        self,
        channel: str,
        message: Dict[str, Any],
        max_queue_size: int = 1000
    ) -> Dict[str, Any]:
        """Publish message with backpressure handling"""
        # Get or create circuit breaker for channel
        circuit_breaker = self.circuit_breakers.get(channel)
        if not circuit_breaker:
            circuit_breaker = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30
            )
            self.circuit_breakers[channel] = circuit_breaker
        
        # Check circuit breaker state
        if circuit_breaker.is_open():
            # Circuit is open, queue message instead
            return await self._queue_message(channel, message, max_queue_size)
        
        try:
            # Try to publish
            redis_channel = f"websocket:{channel}"
            subscribers = await self.redis_client.pubsub_numsub(redis_channel)
            
            if subscribers == 0:
                # No subscribers, queue message
                return await self._queue_message(channel, message, max_queue_size)
            
            # Publish to Redis
            await self.redis_client.publish(redis_channel, json.dumps(message))
            circuit_breaker.record_success()
            
            return {"status": "published", "queued": False}
            
        except Exception as e:
            circuit_breaker.record_failure()
            # Queue message on failure
            return await self._queue_message(channel, message, max_queue_size)
    
    async def _queue_message(
        self,
        channel: str,
        message: Dict[str, Any],
        max_queue_size: int
    ) -> Dict[str, Any]:
        """Queue message when backpressure is detected"""
        queue = self.message_queues.get(channel)
        if not queue:
            queue = asyncio.Queue(maxsize=max_queue_size)
            self.message_queues[channel] = queue
            # Start background worker to drain queue
            asyncio.create_task(self._drain_queue(channel))
        
        try:
            queue.put_nowait(message)
            return {"status": "queued", "queued": True}
        except asyncio.QueueFull:
            # Queue is full, reject message
            logger.warning(f"Queue full for channel {channel}, rejecting message")
            return {
                "status": "rejected",
                "queued": False,
                "reason": "queue_full"
            }
    
    async def _drain_queue(self, channel: str):
        """Background worker to drain message queue"""
        queue = self.message_queues.get(channel)
        if not queue:
            return
        
        while True:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Try to publish
                redis_channel = f"websocket:{channel}"
                await self.redis_client.publish(redis_channel, json.dumps(message))
                
                queue.task_done()
            except asyncio.TimeoutError:
                # No messages, check if we should continue
                if queue.empty():
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error draining queue for {channel}: {e}")
                await asyncio.sleep(1)


class CircuitBreaker:
    """Simple circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half_open"
                    return False
            return True
        return False
    
    def record_success(self):
        """Record successful operation"""
        if self.state == "half_open":
            self.state = "closed"
        self.failure_count = 0
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
```

### 3.4 Session Eviction Strategy

**Problem:** Stale connections consume resources, need cleanup strategy.

**Solution:** Heartbeat-based connection management with automatic eviction.

**Implementation:**
```python
class SessionEvictionManager:
    """Manages session eviction for WebSocket connections"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.heartbeat_interval = 30  # seconds
        self.max_idle_time = 300  # 5 minutes
        self.eviction_check_interval = 60  # 1 minute
    
    async def start_heartbeat_monitor(self, connection_id: str, websocket: WebSocket):
        """Start heartbeat monitoring for connection"""
        last_heartbeat = datetime.utcnow()
        
        while True:
            try:
                # Send ping
                await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat()})
                
                # Update last heartbeat in Redis
                await self.redis_client.hset(
                    f"websocket:connection:{connection_id}",
                    "last_heartbeat",
                    datetime.utcnow().isoformat()
                )
                
                # Extend TTL
                await self.redis_client.expire(
                    f"websocket:connection:{connection_id}",
                    self.max_idle_time
                )
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except WebSocketDisconnect:
                # Connection closed, stop monitoring
                await self._evict_connection(connection_id, "heartbeat_failed")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat for {connection_id}: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def start_eviction_worker(self):
        """Background worker to evict stale connections"""
        while True:
            try:
                await self._evict_stale_connections()
                await asyncio.sleep(self.eviction_check_interval)
            except Exception as e:
                logger.error(f"Error in eviction worker: {e}")
                await asyncio.sleep(self.eviction_check_interval)
    
    async def _evict_stale_connections(self):
        """Find and evict stale connections"""
        # Get all connection keys
        pattern = "websocket:connection:*"
        cursor = 0
        
        while True:
            cursor, keys = await self.redis_client.scan(
                cursor,
                match=pattern,
                count=100
            )
            
            for key in keys:
                connection_id = key.split(":")[-1]
                
                # Check last heartbeat
                last_heartbeat_str = await self.redis_client.hget(
                    key,
                    "last_heartbeat"
                )
                
                if not last_heartbeat_str:
                    # No heartbeat, evict
                    await self._evict_connection(connection_id, "no_heartbeat")
                    continue
                
                last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                idle_time = (datetime.utcnow() - last_heartbeat).total_seconds()
                
                if idle_time > self.max_idle_time:
                    # Stale connection, evict
                    await self._evict_connection(connection_id, "idle_timeout")
            
            if cursor == 0:
                break
    
    async def _evict_connection(self, connection_id: str, reason: str):
        """Evict a connection"""
        logger.info(f"Evicting connection {connection_id}, reason: {reason}")
        
        # Get connection metadata
        conn = await self.connection_registry.get_connection(connection_id)
        if not conn:
            return
        
        # Close WebSocket if local
        if connection_id in self.local_connections:
            websocket = self.local_connections[connection_id]
            try:
                await websocket.close(code=1008, reason=reason)
            except:
                pass
        
        # Unregister from registry
        await self.connection_registry.unregister_connection(connection_id)
        
        # Notify Traffic Cop
        await self.traffic_cop.unregister_websocket_connection(connection_id)
        
        # Emit eviction event
        await self.redis_client.publish(
            "websocket:events",
            json.dumps({
                "event": "connection_evicted",
                "connection_id": connection_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
```

**Connection Lifecycle:**
```python
async def handle_connection(self, websocket: WebSocket, session_token: str):
    """Handle connection with heartbeat and eviction"""
    connection_id = await self._register_connection(websocket, session_token)
    
    # Start heartbeat monitor
    heartbeat_task = asyncio.create_task(
        self.eviction_manager.start_heartbeat_monitor(connection_id, websocket)
    )
    
    try:
        # Message loop
        async for message in websocket.iter_text():
            # Update last activity
            await self.redis_client.hset(
                f"websocket:connection:{connection_id}",
                "last_activity",
                datetime.utcnow().isoformat()
            )
            
            await self._handle_incoming_message(connection_id, message)
    except WebSocketDisconnect:
        await self._handle_disconnect(connection_id)
    finally:
        # Cancel heartbeat
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
```

---

## Implementation Checklist

### Phase 1: Stabilize (1-2 days)
- [ ] Create `WebSocketGatewayService` in `backend/smart_city/services/post_office/`
- [ ] Implement direct abstraction access (Traffic Cop, Redis) - no Platform Gateway
- [ ] Create FastAPI endpoint `/ws` in `backend/api/websocket_gateway_router.py`
- [ ] Implement logical channel routing (guide, pillar:content, etc.)
- [ ] Integrate with Traffic Cop for session validation (direct access)
- [ ] Implement readiness check (`is_ready()`)
- [ ] Add health check endpoint `/health/websocket-gateway`
- [ ] Update Traefik configuration for `/ws` route
- [ ] **Remove** old WebSocket router (`websocket_router.py`) - break and fix
- [ ] **Remove** WebSocket handling from Experience Foundation SDK
- [ ] **Remove** Public Works WebSocket Foundation Service
- [ ] Update frontend to use `/ws` endpoint
- [ ] Write unit tests for gateway service
- [ ] Write integration tests for WebSocket flow

### Phase 2: Architecture Cleanup (1-2 weeks)
- [ ] Register WebSocket Gateway with Consul
- [ ] Implement service discovery for gateway URL (for realms, not agents)
- [ ] Move connection state to Redis (ConnectionRegistry)
- [ ] Implement Post Office SOA APIs (`get_websocket_endpoint`, `publish_to_agent_channel`, `subscribe_to_channel`)
- [ ] Update Platform Gateway mappings for WebSocket capabilities
- [ ] Update all agents to use Post Office SOA APIs (direct API calls)
- [ ] **Note:** Agent MCP Tool refactoring is separate thread (not blocking)
- [ ] Update documentation
- [ ] Write integration tests for SOA APIs
- [ ] Clarify orchestrator pattern (Post Office IS orchestrator, no separate orchestrator needed)

### Phase 3: Production Hardening (2-3 weeks)
- [ ] Implement Redis fan-out architecture
- [ ] Add distributed tracing (OpenTelemetry)
- [ ] Add metrics collection (connections, messages, latency)
- [ ] Implement backpressure handling (circuit breakers, queues)
- [ ] Implement session eviction (heartbeat, idle timeout)
- [ ] Add detailed health check endpoint
- [ ] Add Grafana dashboards for WebSocket metrics
- [ ] Load testing with multiple gateway instances
- [ ] Documentation for production deployment
- [ ] Runbook for common issues

---

## Success Criteria

### Phase 1
- ✅ Single WebSocket endpoint `/ws` accepts all connections
- ✅ Browser testing unblocked
- ✅ No more ambiguous routing errors
- ✅ All connections go through Post Office Gateway

### Phase 2
- ✅ Clear layer separation (transport → platform → domain → agents)
- ✅ Service discovery via Consul working
- ✅ Connection state in Redis (horizontal scaling ready)
- ✅ Realms consume via Post Office SOA APIs

### Phase 3
- ✅ Multiple gateway instances handle load
- ✅ Observability (metrics, tracing) in place
- ✅ Backpressure prevents message loss
- ✅ Stale connections automatically evicted
- ✅ Production-ready for customer deployment

---

## Risk Mitigation

### Risk: Breaking existing functionality
**Mitigation:** Clean break approach - all code updated simultaneously, comprehensive testing before deployment. No backward compatibility to prevent anti-patterns.

### Risk: Circular dependencies (Post Office ↔ Traffic Cop)
**Mitigation:** Smart City services access abstractions directly (no Platform Gateway), avoiding circular dependencies.

### Risk: Performance degradation
**Mitigation:** Load testing in Phase 3, Redis optimization, connection pooling

### Risk: Service discovery failures
**Mitigation:** Fallback to environment variables, health checks, circuit breakers

### Risk: Message loss during backpressure
**Mitigation:** Message queuing, persistence, retry logic

---

## Timeline

- **Phase 1:** 1-2 days (stabilize)
- **Phase 2:** 1-2 weeks (architecture cleanup)
- **Phase 3:** 2-3 weeks (production hardening)
- **Total:** 4-6 weeks to production-ready WebSocket architecture

---

## Architectural Decisions Summary

### 1. Smart City Direct Access
- **Decision:** Post Office (Smart City) accesses Traffic Cop and Redis abstractions directly
- **Rationale:** Avoids circular dependencies (Post Office ↔ Traffic Cop)
- **Implementation:** Use `get_infrastructure_abstraction()` which checks `realm_name == "smart_city"` and accesses Public Works directly

### 2. Break and Fix (No Backward Compatibility)
- **Decision:** Remove all old WebSocket implementations immediately
- **Rationale:** Prevents hidden anti-patterns and architectural misalignment
- **Implementation:** All code updated simultaneously, no legacy endpoints

### 3. Agents via MCP Tools (Separate Thread)
- **Decision:** Agents should access Post Office capabilities via MCP Tools
- **Rationale:** Aligns with agent architecture pattern
- **Status:** Separate refactoring thread - not blocking Phase 1-3
- **Current:** Agents use Post Office SOA APIs directly
- **Future:** Post Office MCP Server exposes WebSocket capabilities as tools

### 4. No Separate Orchestrator
- **Decision:** Post Office IS the orchestrator, WebSocket Gateway is the HOW implementation
- **Rationale:** Post Office orchestrates messaging (single domain), no need for separate orchestrator like DataSolutionOrchestrator
- **Comparison:** DataSolutionOrchestrator orchestrates multiple journey orchestrators (complex), Post Office orchestrates messaging (simpler)

---

## Next Steps

1. Review and approve this plan
2. Create implementation tickets for Phase 1
3. Set up development environment for testing
4. Begin Phase 1 implementation (break and fix approach)

---

**Document Status:** ✅ Ready for Implementation  
**Last Updated:** January 2025

