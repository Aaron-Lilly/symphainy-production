# CORS, Routing, and WebSocket Architecture Analysis

**Date:** December 16, 2025  
**Status:** 🔍 Analysis & Recommendations  
**Priority:** HIGH - Enables proper websocket integration

---

## 🎯 Executive Summary

This document analyzes the current CORS, routing, and websocket architecture to determine how websockets should properly fit into the centralized routing system and identify gaps in documentation.

**Key Findings:**
1. ✅ **Centralized routing exists** - Universal Pillar Router + FrontendGatewayService
2. ⚠️ **Websockets are separate** - Not integrated with centralized routing
3. ⚠️ **CORS handling is ad-hoc** - Custom middleware in main.py, not following routing patterns
4. ⚠️ **Documentation gap** - Developer Guide lacks CORS/routing/websocket patterns

---

## 📊 Current Architecture

### 1. HTTP REST API Routing (Centralized)

**Flow:**
```
Client Request
  ↓
Traefik (Gateway)
  ↓
FastAPI App (main.py)
  ↓
Universal Pillar Router (/api/v1/{pillar}/{path})
  ↓
FrontendGatewayService.route_frontend_request()
  ↓
Pillar Orchestrator (Content/Insights/Operations/BusinessOutcomes)
  ↓
Business Logic Services
```

**Key Components:**
- **Universal Pillar Router** (`backend/api/universal_pillar_router.py`)
  - Single router handles ALL pillars
  - Pattern: `/api/v1/{pillar}-pillar/{path:path}`
  - Routes to `FrontendGatewayService`
  
- **FrontendGatewayService** (`foundations/experience_foundation/services/frontend_gateway_service/`)
  - Centralized routing logic
  - Discovers orchestrators via Curator
  - Handles request transformation and validation

- **Registration** (`backend/api/__init__.py`)
  - `register_api_routers()` registers all routers
  - Order: Auth Router → Universal Router → WebSocket Router

### 2. WebSocket Routing (Separate)

**Flow:**
```
Client WebSocket Request
  ↓
Traefik (Gateway) - Bypasses ForwardAuth for /api/ws
  ↓
FastAPI App (main.py)
  ↓
Custom CORS Middleware (bypasses CORS for /api/ws)
  ↓
WebSocket Router (/api/ws/agent)
  ↓
UnifiedAgentWebSocketSDK
  ↓
Agent (Guide/Liaison)
```

**Key Components:**
- **WebSocket Router** (`backend/api/websocket_router.py`)
  - Separate router, not part of universal router
  - Endpoints: `/api/ws/agent`, `/api/ws/guide`, `/api/ws/liaison/{pillar}`
  - Direct agent communication (no FrontendGatewayService)

- **UnifiedAgentWebSocketSDK** (`foundations/experience_foundation/sdk/unified_agent_websocket_sdk.py`)
  - Routes messages to appropriate agents
  - Handles session management via Traffic Cop

### 3. CORS Handling (Ad-hoc)

**Current Implementation:**
- **Location:** `main.py` (lines 1446-1506)
- **Type:** Custom middleware (`CustomCORSMiddleware`)
- **Behavior:**
  - Bypasses CORS entirely for `/api/ws` paths
  - Standard CORS for all other paths
  - Not integrated with routing architecture

**Issues:**
1. ❌ CORS logic is in `main.py`, not with routing infrastructure
2. ❌ WebSocket CORS bypass is hardcoded, not configurable
3. ❌ No integration with `FrontendGatewayService` or routing utilities
4. ❌ Doesn't follow the same patterns as HTTP routing

---

## 🔍 Analysis: How Should Websockets Fit?

### Option A: Keep Separate (Current Approach)

**Pros:**
- ✅ Websockets are fundamentally different from HTTP (upgrade protocol)
- ✅ Direct agent communication is simpler
- ✅ No need to go through FrontendGatewayService

**Cons:**
- ❌ Inconsistent with centralized routing pattern
- ❌ CORS handling is ad-hoc
- ❌ Harder to maintain and extend

### Option B: Integrate with Centralized Routing

**Approach:**
- Extend `FrontendGatewayService` to handle websocket routing
- Register websocket endpoints through routing system
- Use routing utilities for CORS configuration

**Pros:**
- ✅ Consistent architecture
- ✅ Centralized configuration
- ✅ Easier to maintain

**Cons:**
- ⚠️ Websockets are different protocol (upgrade vs HTTP)
- ⚠️ May add unnecessary complexity
- ⚠️ FrontendGatewayService designed for HTTP REST

### Option C: Hybrid Approach (Recommended)

**Approach:**
- Keep websocket router separate (different protocol)
- Integrate CORS handling with routing architecture
- Use routing utilities for configuration
- Document as "special case" in architecture

**Implementation:**
1. Move CORS configuration to routing utilities
2. Create `WebSocketRoutingHelper` in routing utilities
3. Use same configuration patterns as HTTP routing
4. Document websockets as "special protocol" in Developer Guide

---

## 🏗️ Recommended Architecture

### 1. CORS Configuration (Centralized)

**Location:** `utilities/api_routing/middleware/cors_middleware.py`

**Enhancement:**
```python
class CORSMiddleware:
    """CORS middleware with websocket support."""
    
    def __init__(self, di_container):
        # Load CORS config from DI container
        self.allowed_origins = self._load_cors_origins()
        self.websocket_paths = self._load_websocket_paths()  # NEW
        self.websocket_cors_bypass = self._load_websocket_cors_bypass()  # NEW
    
    async def __call__(self, request_context, user_context, next_handler):
        # Check if websocket path
        if self._is_websocket_path(request_context.path):
            # Handle websocket CORS
            return await self._handle_websocket_cors(request_context, next_handler)
        
        # Standard HTTP CORS handling
        return await self._handle_http_cors(request_context, next_handler)
```

### 2. WebSocket Routing Helper

**Location:** `utilities/api_routing/websocket_routing_helper.py` (NEW)

**Purpose:**
- Centralize websocket routing configuration
- Provide helpers for websocket CORS
- Integrate with routing utilities

**Implementation:**
```python
class WebSocketRoutingHelper:
    """Helper for websocket routing configuration."""
    
    @staticmethod
    def is_websocket_path(path: str) -> bool:
        """Check if path is a websocket endpoint."""
        return path.startswith("/api/ws")
    
    @staticmethod
    def get_websocket_cors_config() -> Dict[str, Any]:
        """Get CORS configuration for websockets."""
        # Load from config, with sensible defaults
        return {
            "bypass_cors": True,  # Websockets handle auth via session_token
            "allowed_origins": "*",  # Or from config
            "allowed_methods": ["GET", "POST"],
            "allowed_headers": ["*"]
        }
```

### 3. FastAPI Integration

**Location:** `main.py`

**Enhancement:**
```python
# Use routing utilities for CORS
from utilities.api_routing.middleware.cors_middleware import CORSMiddleware
from utilities.api_routing.websocket_routing_helper import WebSocketRoutingHelper

# Initialize CORS middleware with routing utilities
cors_middleware = CORSMiddleware(di_container)
app.add_middleware(cors_middleware)

# WebSocket routing helper for configuration
websocket_helper = WebSocketRoutingHelper()
```

---

## 📝 Documentation Updates Needed

### Developer Guide Section: "Routing Architecture"

**Location:** `symphainy-platform/docs/DEVELOPER_GUIDE.md`

**New Section:**
```markdown
## 🌐 Routing Architecture

### HTTP REST API Routing

All HTTP REST API requests flow through the centralized routing system:

1. **Universal Pillar Router** - Single router for all pillars
2. **FrontendGatewayService** - Centralized routing logic
3. **Pillar Orchestrators** - Business logic handlers

**Pattern:** `/api/v1/{pillar}-pillar/{path:path}`

### WebSocket Routing (Special Protocol)

WebSocket connections use a separate router due to protocol differences:

1. **WebSocket Router** - Handles websocket upgrades
2. **UnifiedAgentWebSocketSDK** - Routes messages to agents
3. **Agents** - Direct communication (no FrontendGatewayService)

**Pattern:** `/api/ws/{endpoint}`

**Why Separate?**
- Websockets use upgrade protocol (not HTTP)
- Direct agent communication is simpler
- Authentication via `session_token` query parameter
- CORS handling is different (bypass for websockets)

### CORS Configuration

CORS is handled centrally through routing utilities:

- **Location:** `utilities/api_routing/middleware/cors_middleware.py`
- **Configuration:** Via DI container config
- **WebSocket Handling:** Automatic bypass for `/api/ws` paths

**Adding New Endpoints:**
1. HTTP REST: Add to Universal Router pattern
2. WebSocket: Add to WebSocket Router
3. CORS: Automatically handled by middleware
```

---

## ✅ Implementation Plan

### Phase 1: Refactor CORS Handling

1. **Move CORS logic to routing utilities**
   - Update `utilities/api_routing/middleware/cors_middleware.py`
   - Add websocket path detection
   - Integrate with DI container config

2. **Create WebSocketRoutingHelper**
   - New file: `utilities/api_routing/websocket_routing_helper.py`
   - Centralize websocket configuration
   - Provide helpers for websocket CORS

3. **Update main.py**
   - Remove custom CORS middleware
   - Use routing utilities CORS middleware
   - Integrate WebSocketRoutingHelper

### Phase 2: Documentation

1. **Update Developer Guide**
   - Add "Routing Architecture" section
   - Document HTTP vs WebSocket routing
   - Explain CORS configuration

2. **Create Architecture Diagram**
   - Show routing flow for HTTP and WebSocket
   - Document CORS handling points
   - Show integration points

### Phase 3: Testing

1. **Test HTTP REST routing** (should be unchanged)
2. **Test WebSocket routing** (verify CORS bypass works)
3. **Test CORS configuration** (verify configurable)

---

## 🎯 Success Criteria

1. ✅ CORS handling uses routing utilities (not ad-hoc in main.py)
2. ✅ WebSocket routing documented as "special protocol"
3. ✅ Configuration centralized and consistent
4. ✅ Developer Guide updated with routing patterns
5. ✅ WebSocket CORS bypass works correctly
6. ✅ HTTP REST routing unchanged

---

## 📚 References

- Universal Pillar Router: `backend/api/universal_pillar_router.py`
- FrontendGatewayService: `foundations/experience_foundation/services/frontend_gateway_service/`
- WebSocket Router: `backend/api/websocket_router.py`
- CORS Middleware: `utilities/api_routing/middleware/cors_middleware.py`
- Routing Documentation: `docs/HOW_EVERYTHING_WORKS_TOGETHER.md`

---

## 🔄 Next Steps

1. Review this analysis with team
2. Decide on approach (Option C recommended)
3. Review Production Readiness Assessment (`PRODUCTION_READINESS_ASSESSMENT_WEBSOCKET_CORS.md`)
4. Implement Phase 1 (CORS refactoring + security hardening)
5. Update documentation
6. Test thoroughly
7. Deploy

---

## 📊 Production Readiness Summary

**See:** `PRODUCTION_READINESS_ASSESSMENT_WEBSOCKET_CORS.md` for detailed assessment.

**Quick Summary:**
- ✅ **Architecture:** Sound and aligned with best practices
- ⚠️ **Security:** Good foundation, needs origin validation and rate limiting
- ⚠️ **Configuration:** Needs environment-aware setup
- ⚠️ **Observability:** Needs metrics and monitoring
- **Overall:** **7/10** - Good foundation, needs enhancements before production

**Critical Enhancements Needed:**
1. Origin validation (even if CORS bypassed)
2. Connection limits (per-user and global)
3. Rate limiting for websocket messages
4. Environment-aware configuration
5. Comprehensive metrics and monitoring

