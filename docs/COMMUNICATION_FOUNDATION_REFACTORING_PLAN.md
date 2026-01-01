# Communication Foundation Refactoring Plan
## Eliminating Communication Foundation and Distributing Responsibilities

**Date:** December 7, 2024  
**Status:** 🚀 **READY TO EXECUTE**  
**Timeline:** 2-3 weeks

---

## 📋 OVERVIEW

This plan eliminates Communication Foundation by distributing its responsibilities to their natural homes:
- **FastAPIRouterManager** → Utility (like DI Container)
- **WebSocket infrastructure** → Experience Foundation SDK
- **Messaging/Event Bus** → Post Office capabilities (SOA APIs)
- **SOA Client infrastructure** → Curator Realm
- **Realm bridges** → Experience realm SDK

**Key Principle:** Infrastructure utilities stay simple, business capabilities go to Smart City services, user-facing features go to Experience Foundation.

---

## 🎯 ARCHITECTURAL DECISIONS

### **Decision 1: FastAPIRouterManager → Utility (Like DI Container)**

**Rationale:**
- Pure infrastructure utility (no business logic)
- Similar to DI Container in role and complexity
- Should be simple, direct access (no abstractions)
- Platform-wide singleton pattern

**Location:** `utilities/api_routing/fastapi_router_manager.py`

**Access Pattern:**
```python
from utilities.api_routing.fastapi_router_manager import FastAPIRouterManager

router_manager = FastAPIRouterManager()
await router_manager.initialize()
```

### **Decision 2: WebSocket Infrastructure → Experience Foundation SDK**

**Rationale:**
- WebSockets are user-facing communication
- Experience Foundation handles all user-facing capabilities
- SDK pattern provides clean abstraction

**Location:** `foundations/experience_foundation/sdk/websocket_sdk.py`

### **Decision 3: Messaging/Event Bus → Post Office Capabilities**

**Rationale:**
- Post Office is the Smart City service for communication
- Redis → Kafka swap only affects Post Office (not all services)
- Services call Post Office SOA APIs, not abstractions directly

**Location:** Post Office service exposes SOA APIs

**Access Pattern:**
```python
post_office = await self.get_post_office_api()
await post_office.send_message(message)
await post_office.publish_event(event)
await post_office.subscribe_to_events(event_type, handler)
```

### **Decision 4: SOA Client Infrastructure → Curator Realm**

**Rationale:**
- Curator is the service registry
- SOA Client is how services discover and call each other
- Natural fit for Curator's responsibilities

**Location:** `foundations/curator_foundation/soa_client_service.py`

### **Decision 5: Realm Bridges → Experience Realm SDK**

**Rationale:**
- Realm bridges expose REST endpoints for external consumption
- Experience Foundation handles all user-facing APIs
- SDK pattern provides clean abstraction

**Location:** `foundations/experience_foundation/sdk/realm_bridges_sdk.py`

---

## 📝 IMPLEMENTATION TASKS

### **Phase 1: Move FastAPIRouterManager to Utilities (Week 1, Days 1-2)**

#### **Task 1.1: Create FastAPIRouterManager Utility**

**File:** `utilities/api_routing/fastapi_router_manager.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""
FastAPI Router Manager - Platform Infrastructure Utility

WHAT (Infrastructure Utility): I provide unified FastAPI router management
HOW (Infrastructure Implementation): I consolidate all realm routers into a single router

Similar to DI Container - simple, direct, no abstractions needed.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, FastAPI
from datetime import datetime

logger = logging.getLogger(__name__)


class FastAPIRouterManager:
    """
    FastAPI Router Manager - Platform Infrastructure Utility
    
    Centralized FastAPI router management that consolidates all realm-specific
    routers into a unified communication infrastructure.
    
    Similar to DI Container - simple, direct access, no abstractions.
    """
    
    def __init__(self):
        """Initialize FastAPI Router Manager."""
        self.logger = logging.getLogger("FastAPIRouterManager")
        
        # Router registry
        self.realm_routers: Dict[str, APIRouter] = {}
        self.global_router = APIRouter()
        
        # Router metadata
        self.router_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Service state
        self.is_initialized = False
        
        self.logger.info("🏗️ FastAPI Router Manager initialized")
    
    async def initialize(self):
        """Initialize the router manager."""
        self.logger.info("🚀 Initializing FastAPI Router Manager...")
        
        try:
            # Initialize global router
            await self._setup_global_router()
            
            # Register health check endpoint
            await self._register_health_endpoints()
            
            self.is_initialized = True
            self.logger.info("✅ FastAPI Router Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize FastAPI Router Manager: {e}")
            raise
    
    async def register_realm_router(self, realm: str, router: APIRouter, metadata: Dict[str, Any] = None):
        """Register a realm-specific router."""
        self.logger.info(f"📝 Registering {realm} realm router...")
        
        try:
            # Store router
            self.realm_routers[realm] = router
            
            # Store metadata
            self.router_metadata[realm] = metadata or {}
            self.router_metadata[realm]["registered_at"] = datetime.utcnow().isoformat()
            
            # Include router in global router
            self.global_router.include_router(router)
            
            self.logger.info(f"✅ {realm} realm router registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register {realm} realm router: {e}")
            raise
    
    def get_unified_router(self) -> APIRouter:
        """Get the unified router for all realms."""
        if not self.is_initialized:
            raise RuntimeError("FastAPI Router Manager not initialized")
        
        return self.global_router
    
    def get_realm_router(self, realm: str) -> Optional[APIRouter]:
        """Get a specific realm router."""
        return self.realm_routers.get(realm)
    
    def list_registered_realms(self) -> List[str]:
        """List all registered realms."""
        return list(self.realm_routers.keys())
    
    async def _setup_global_router(self):
        """Setup global router with base configuration."""
        # Add health check endpoint
        @self.global_router.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "FastAPIRouterManager",
                "realms": list(self.realm_routers.keys())
            }
    
    async def _register_health_endpoints(self):
        """Register health check endpoints."""
        # Health check is registered in _setup_global_router
        pass
```

**Acceptance Criteria:**
- ✅ FastAPIRouterManager exists in `utilities/api_routing/`
- ✅ Can be imported and initialized directly
- ✅ Can register realm routers
- ✅ Can get unified router for FastAPI app
- ✅ No dependencies on Communication Foundation

#### **Task 1.2: Update main.py to Use FastAPIRouterManager Utility**

**File:** `main.py`

**Changes:**
1. Import FastAPIRouterManager from utilities
2. Initialize FastAPIRouterManager early (like DI Container)
3. Remove Communication Foundation dependency for router management
4. Register realm routers with FastAPIRouterManager

**Code Pattern:**
```python
# In PlatformOrchestrator.__init__ or initialize()
from utilities.api_routing.fastapi_router_manager import FastAPIRouterManager

self.router_manager = FastAPIRouterManager()
await self.router_manager.initialize()

# Later, when registering routers:
await self.router_manager.register_realm_router("experience", experience_router)
await self.router_manager.register_realm_router("smart_city", smart_city_router)

# In setup_platform_routes:
app.include_router(self.router_manager.get_unified_router())
```

**Acceptance Criteria:**
- ✅ Platform uses FastAPIRouterManager utility
- ✅ No Communication Foundation dependency for router management
- ✅ All realm routers registered correctly

---

### **Phase 2: Move WebSocket Infrastructure to Experience Foundation SDK (Week 1, Days 3-4)**

#### **Task 2.1: Create WebSocket SDK in Experience Foundation**

**File:** `foundations/experience_foundation/sdk/websocket_sdk.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""
WebSocket SDK - Experience Foundation

Provides WebSocket capabilities for user-facing communication.

WHAT (Experience SDK): I provide WebSocket infrastructure for user-facing communication
HOW (SDK Implementation): I expose WebSocket capabilities via Experience Foundation
"""

from typing import Dict, Any, Optional
from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService

class WebSocketSDK:
    """
    WebSocket SDK - Experience Foundation
    
    Provides WebSocket capabilities for user-facing communication.
    """
    
    def __init__(self, experience_foundation: ExperienceFoundationService):
        """Initialize WebSocket SDK."""
        self.experience_foundation = experience_foundation
        self.websocket_foundation = None
    
    async def initialize(self):
        """Initialize WebSocket SDK."""
        # Get WebSocket foundation from DI Container
        self.websocket_foundation = self.experience_foundation.di_container.get_websocket_foundation()
        if self.websocket_foundation and not self.websocket_foundation.is_initialized:
            await self.websocket_foundation.initialize()
    
    async def create_websocket_connection(self, connection_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create WebSocket connection."""
        if not self.websocket_foundation:
            raise RuntimeError("WebSocket foundation not available")
        
        return await self.websocket_foundation.create_connection(connection_id, user_context)
    
    async def send_websocket_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message via WebSocket."""
        if not self.websocket_foundation:
            raise RuntimeError("WebSocket foundation not available")
        
        return await self.websocket_foundation.send_message(connection_id, message)
    
    async def close_websocket_connection(self, connection_id: str) -> bool:
        """Close WebSocket connection."""
        if not self.websocket_foundation:
            raise RuntimeError("WebSocket foundation not available")
        
        return await self.websocket_foundation.close_connection(connection_id)
```

**Acceptance Criteria:**
- ✅ WebSocket SDK exists in Experience Foundation
- ✅ Can be accessed via Experience Foundation SDK
- ✅ Provides WebSocket capabilities for user-facing communication

#### **Task 2.2: Update Experience Foundation Service to Expose WebSocket SDK**

**File:** `foundations/experience_foundation/experience_foundation_service.py`

**Changes:**
1. Import WebSocketSDK
2. Initialize WebSocketSDK in `initialize()`
3. Expose via `get_websocket_sdk()` method

**Acceptance Criteria:**
- ✅ Experience Foundation exposes WebSocket SDK
- ✅ Can be accessed via `experience_foundation.get_websocket_sdk()`

---

### **Phase 3: Expand Post Office SOA APIs for Messaging/Events (Week 1, Days 5-7)**

#### **Task 3.1: Add Event Publishing SOA API to Post Office**

**File:** `backend/smart_city/services/post_office/modules/event_routing.py`

**Changes:**
1. Add `publish_event()` method that uses `event_management_abstraction` internally
2. Add to SOA API registry

**Implementation:**
```python
async def publish_event(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Publish event via Post Office.
    
    Uses event_management_abstraction internally (Redis → Kafka swap only affects Post Office).
    """
    try:
        event_data = request.get("event_data", {})
        event_type = request.get("event_type", "generic")
        
        # Use event_management_abstraction internally
        if not self.service.event_management_abstraction:
            return {
                "success": False,
                "error": "Event management abstraction not available"
            }
        
        # Publish event via abstraction
        event_context = await self.service.event_management_abstraction.publish_event({
            "event_type": event_type,
            "event_data": event_data,
            "user_context": user_context,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "event_id": event_context.get("event_id"),
            "event_type": event_type,
            "published_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        self.service.logger.error(f"❌ Failed to publish event: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Acceptance Criteria:**
- ✅ Post Office has `publish_event()` SOA API
- ✅ Uses `event_management_abstraction` internally
- ✅ Registered in SOA API registry

#### **Task 3.2: Add Event Subscription SOA APIs to Post Office**

**File:** `backend/smart_city/services/post_office/modules/event_routing.py`

**Changes:**
1. Add `subscribe_to_events()` method
2. Add `unsubscribe_from_events()` method
3. Add to SOA API registry

**Implementation:**
```python
async def subscribe_to_events(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Subscribe to events via Post Office.
    
    Uses event_management_abstraction internally.
    """
    try:
        event_type = request.get("event_type")
        handler_id = request.get("handler_id")
        
        if not event_type or not handler_id:
            return {
                "success": False,
                "error": "event_type and handler_id required"
            }
        
        # Use event_management_abstraction internally
        if not self.service.event_management_abstraction:
            return {
                "success": False,
                "error": "Event management abstraction not available"
            }
        
        # Subscribe via abstraction
        success = await self.service.event_management_abstraction.subscribe(event_type, handler_id)
        
        return {
            "success": success,
            "event_type": event_type,
            "handler_id": handler_id,
            "subscribed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        self.service.logger.error(f"❌ Failed to subscribe to events: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def unsubscribe_from_events(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Unsubscribe from events via Post Office.
    
    Uses event_management_abstraction internally.
    """
    try:
        event_type = request.get("event_type")
        handler_id = request.get("handler_id")
        
        if not event_type or not handler_id:
            return {
                "success": False,
                "error": "event_type and handler_id required"
            }
        
        # Use event_management_abstraction internally
        if not self.service.event_management_abstraction:
            return {
                "success": False,
                "error": "Event management abstraction not available"
            }
        
        # Unsubscribe via abstraction
        success = await self.service.event_management_abstraction.unsubscribe(event_type, handler_id)
        
        return {
            "success": success,
            "event_type": event_type,
            "handler_id": handler_id,
            "unsubscribed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        self.service.logger.error(f"❌ Failed to unsubscribe from events: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Acceptance Criteria:**
- ✅ Post Office has `subscribe_to_events()` SOA API
- ✅ Post Office has `unsubscribe_from_events()` SOA API
- ✅ Both use `event_management_abstraction` internally
- ✅ Registered in SOA API registry

#### **Task 3.3: Update Post Office Service Protocol**

**File:** `backend/smart_city/protocols/post_office_service_protocol.py`

**Changes:**
1. Add `publish_event()` to protocol
2. Add `subscribe_to_events()` to protocol
3. Add `unsubscribe_from_events()` to protocol

**Acceptance Criteria:**
- ✅ Protocol includes all event methods
- ✅ Protocol matches implementation

#### **Task 3.4: Update Post Office Service to Expose Event Methods**

**File:** `backend/smart_city/services/post_office/post_office_service.py`

**Changes:**
1. Add `publish_event()` method that delegates to event_routing_module
2. Add `subscribe_to_events()` method that delegates to event_routing_module
3. Add `unsubscribe_from_events()` method that delegates to event_routing_module

**Acceptance Criteria:**
- ✅ Post Office service exposes all event methods
- ✅ Methods delegate to modules correctly

---

### **Phase 4: Update CommunicationMixin to Use Post Office SOA APIs (Week 2, Days 1-2)**

#### **Task 4.1: Update CommunicationMixin.publish_event()**

**File:** `bases/mixins/communication_mixin.py`

**Changes:**
1. Change `publish_event()` to delegate to Post Office SOA API
2. Remove direct abstraction access

**Before:**
```python
async def publish_event(self, event: Dict[str, Any]) -> bool:
    event_mgmt = self.get_event_management_abstraction()
    if event_mgmt:
        return await event_mgmt.publish_event(event)
    return False
```

**After:**
```python
async def publish_event(self, event: Dict[str, Any]) -> bool:
    """
    Publish event via Post Office service (NOT infrastructure abstraction).
    
    Uses Smart City service for business-level event publishing.
    Falls back to infrastructure abstraction if Post Office not available.
    """
    try:
        # ✅ Use Post Office service (business-level)
        post_office = await self.get_post_office_api()
        if post_office:
            # Use Post Office service method
            if hasattr(post_office, 'publish_event'):
                result = await post_office.publish_event({
                    "event_type": event.get("event_type", "generic"),
                    "event_data": event
                })
                return result.get("success", False)
            else:
                self.logger.warning("⚠️ Post Office service found but publish_event method not available")
        else:
            # Fallback to infrastructure abstraction if Post Office not available
            self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
        
        # Fallback: Use infrastructure abstraction
        event_mgmt = self.get_event_management_abstraction()
        if event_mgmt:
            return await event_mgmt.publish_event(event)
        else:
            return False
                
    except Exception as e:
        self.logger.error(f"Failed to publish event: {e}")
        return False
```

**Acceptance Criteria:**
- ✅ `publish_event()` delegates to Post Office SOA API
- ✅ Falls back to abstraction if Post Office not available
- ✅ No direct abstraction access (except fallback)

#### **Task 4.2: Update CommunicationMixin.subscribe_to_events()**

**File:** `bases/mixins/communication_mixin.py`

**Changes:**
1. Change `subscribe_to_events()` to delegate to Post Office SOA API
2. Remove direct abstraction access

**After:**
```python
async def subscribe_to_events(self, event_type: str, handler: Any) -> bool:
    """
    Subscribe to events via Post Office service (NOT infrastructure abstraction).
    
    Uses Smart City service for business-level event subscription.
    Falls back to infrastructure abstraction if Post Office not available.
    """
    try:
        # ✅ Use Post Office service (business-level)
        post_office = await self.get_post_office_api()
        if post_office:
            # Use Post Office service method
            if hasattr(post_office, 'subscribe_to_events'):
                # Convert handler to handler_id (or store handler mapping)
                handler_id = str(id(handler))  # Simple ID generation
                result = await post_office.subscribe_to_events({
                    "event_type": event_type,
                    "handler_id": handler_id
                })
                return result.get("success", False)
            else:
                self.logger.warning("⚠️ Post Office service found but subscribe_to_events method not available")
        else:
            # Fallback to infrastructure abstraction
            self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
        
        # Fallback: Use infrastructure abstraction
        event_mgmt = self.get_event_management_abstraction()
        if event_mgmt:
            return await event_mgmt.subscribe(event_type, handler)
        else:
            return False
                
    except Exception as e:
        self.logger.error(f"Failed to subscribe to events {event_type}: {e}")
        return False
```

**Acceptance Criteria:**
- ✅ `subscribe_to_events()` delegates to Post Office SOA API
- ✅ Falls back to abstraction if Post Office not available

#### **Task 4.3: Update CommunicationMixin.unsubscribe_from_events()**

**File:** `bases/mixins/communication_mixin.py`

**Changes:**
1. Change `unsubscribe_from_events()` to delegate to Post Office SOA API
2. Remove direct abstraction access

**After:**
```python
async def unsubscribe_from_events(self, event_type: str, handler: Any) -> bool:
    """
    Unsubscribe from events via Post Office service (NOT infrastructure abstraction).
    
    Uses Smart City service for business-level event unsubscription.
    Falls back to infrastructure abstraction if Post Office not available.
    """
    try:
        # ✅ Use Post Office service (business-level)
        post_office = await self.get_post_office_api()
        if post_office:
            # Use Post Office service method
            if hasattr(post_office, 'unsubscribe_from_events'):
                handler_id = str(id(handler))  # Simple ID generation
                result = await post_office.unsubscribe_from_events({
                    "event_type": event_type,
                    "handler_id": handler_id
                })
                return result.get("success", False)
            else:
                self.logger.warning("⚠️ Post Office service found but unsubscribe_from_events method not available")
        else:
            # Fallback to infrastructure abstraction
            self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
        
        # Fallback: Use infrastructure abstraction
        event_mgmt = self.get_event_management_abstraction()
        if event_mgmt:
            return await event_mgmt.unsubscribe(event_type, handler)
        else:
            return False
                
    except Exception as e:
        self.logger.error(f"Failed to unsubscribe from events {event_type}: {e}")
        return False
```

**Acceptance Criteria:**
- ✅ `unsubscribe_from_events()` delegates to Post Office SOA API
- ✅ Falls back to abstraction if Post Office not available

---

### **Phase 5: Update InfrastructureAccessMixin (Week 2, Days 3-4)**

#### **Task 5.1: Remove Special Routing for Messaging/Event Management**

**File:** `bases/mixins/infrastructure_access_mixin.py`

**Changes:**
1. Remove special routing logic for `messaging` and `event_management` (lines 106-126)
2. These abstractions should only be accessible to Post Office (Smart City privilege)
3. Other services should use Post Office SOA APIs

**Before:**
```python
communication_abstractions = ["messaging", "event_management", "websocket", "event_bus"]
if name in communication_abstractions:
    if logger:
        logger.info(f"Routing '{name}' to Communication Foundation (blocked by Platform Gateway)")
    
    if hasattr(self, 'di_container') and self.di_container:
        try:
            communication_foundation = self.di_container.get_foundation_service("CommunicationFoundationService")
            # ... routing logic ...
```

**After:**
```python
# Messaging and event_management are now Post Office capabilities
# Services should use Post Office SOA APIs, not abstractions directly
# Only Post Office (Smart City privilege) can access these abstractions
communication_abstractions = ["websocket"]  # WebSocket moved to Experience Foundation SDK
if name in communication_abstractions:
    # Route to Experience Foundation SDK
    # ... routing logic ...
```

**Acceptance Criteria:**
- ✅ Special routing for messaging/event_management removed
- ✅ Only Post Office can access messaging/event_management abstractions
- ✅ Other services must use Post Office SOA APIs

---

### **Phase 6: Move SOA Client Infrastructure to Curator (Week 2, Days 5-7)**

#### **Task 6.1: Create SOA Client Service in Curator Foundation**

**File:** `foundations/curator_foundation/soa_client_service.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""
SOA Client Service - Curator Foundation

Provides SOA client capabilities for inter-service communication.

WHAT (Curator Service): I provide SOA client for service discovery and communication
HOW (Service Implementation): I use Curator registry for service discovery
"""

from typing import Dict, Any, Optional
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

class SOAClientService:
    """
    SOA Client Service - Curator Foundation
    
    Provides SOA client capabilities for inter-service communication.
    """
    
    def __init__(self, curator_foundation: CuratorFoundationService):
        """Initialize SOA Client Service."""
        self.curator_foundation = curator_foundation
        self.soa_services = {}
    
    async def initialize(self):
        """Initialize SOA Client Service."""
        # Discover services from Curator registry
        await self._discover_services()
    
    async def call_service(self, service_name: str, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call service via SOA API."""
        # Discover service from Curator
        service_info = await self.curator_foundation.discover_service(service_name)
        if not service_info:
            return {
                "success": False,
                "error": f"Service {service_name} not found in registry"
            }
        
        # Call service SOA API
        # Implementation depends on service discovery mechanism
        # ...
```

**Acceptance Criteria:**
- ✅ SOA Client Service exists in Curator Foundation
- ✅ Uses Curator registry for service discovery
- ✅ Can call services via SOA APIs

---

### **Phase 7: Move Realm Bridges to Experience Foundation SDK (Week 3, Days 1-3)**

#### **Task 7.1: Create Realm Bridges SDK in Experience Foundation**

**File:** `foundations/experience_foundation/sdk/realm_bridges_sdk.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""
Realm Bridges SDK - Experience Foundation

Provides realm bridge capabilities for exposing Smart City services via REST.

WHAT (Experience SDK): I provide realm bridges for exposing services via REST
HOW (SDK Implementation): I create FastAPI routers for each realm
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService

class RealmBridgesSDK:
    """
    Realm Bridges SDK - Experience Foundation
    
    Provides realm bridge capabilities for exposing Smart City services via REST.
    """
    
    def __init__(self, experience_foundation: ExperienceFoundationService):
        """Initialize Realm Bridges SDK."""
        self.experience_foundation = experience_foundation
        self.realm_bridges = {}
    
    async def initialize(self):
        """Initialize Realm Bridges SDK."""
        # Create realm bridges for each realm
        await self._create_realm_bridges()
    
    async def get_realm_router(self, realm: str) -> Optional[APIRouter]:
        """Get router for a specific realm."""
        return self.realm_bridges.get(realm)
    
    async def _create_realm_bridges(self):
        """Create realm bridges for each realm."""
        # Create Smart City bridge
        from foundations.communication_foundation.realm_bridges.smart_city_bridge import SmartCityRealmBridge
        # ... create and register bridges ...
```

**Acceptance Criteria:**
- ✅ Realm Bridges SDK exists in Experience Foundation
- ✅ Can create routers for each realm
- ✅ Exposes Smart City services via REST

---

### **Phase 8: Audit and Migration (Week 3, Days 4-7)**

#### **Task 8.1: Audit Direct Abstraction Usage**

**Script:** `scripts/audit_communication_abstractions.py`

**Purpose:**
- Find all direct calls to `get_messaging_abstraction()`
- Find all direct calls to `get_event_management_abstraction()`
- Find all MCP tools that use messaging/events
- Generate migration report

**Acceptance Criteria:**
- ✅ Audit script identifies all direct abstraction usage
- ✅ Migration report generated

#### **Task 8.2: Migrate Services to Post Office SOA APIs**

**Files:** All services identified in audit

**Changes:**
1. Replace `get_messaging_abstraction()` calls with Post Office SOA API calls
2. Replace `get_event_management_abstraction()` calls with Post Office SOA API calls
3. Update MCP tools to use Post Office SOA APIs

**Acceptance Criteria:**
- ✅ All services use Post Office SOA APIs
- ✅ No direct abstraction access (except Post Office itself)

#### **Task 8.3: Remove Communication Foundation**

**Files:**
- `foundations/communication_foundation/` (entire directory)

**Changes:**
1. Archive Communication Foundation code
2. Remove from `main.py` initialization
3. Update all imports/references

**Acceptance Criteria:**
- ✅ Communication Foundation removed
- ✅ No broken imports
- ✅ Platform starts successfully

---

## ✅ SUCCESS CRITERIA

| Requirement | Status | Notes |
|-------------|--------|-------|
| FastAPIRouterManager is utility | ⬜ | Like DI Container |
| WebSocket in Experience Foundation SDK | ⬜ | User-facing |
| Messaging/Events via Post Office SOA APIs | ⬜ | Redis → Kafka swap only affects Post Office |
| SOA Client in Curator Foundation | ⬜ | Service discovery |
| Realm bridges in Experience Foundation SDK | ⬜ | REST endpoints |
| CommunicationMixin uses Post Office | ⬜ | No direct abstraction access |
| InfrastructureAccessMixin updated | ⬜ | No special routing |
| All services migrated | ⬜ | No direct abstraction access |
| Communication Foundation removed | ⬜ | Platform starts successfully |

---

## 🔄 REDIS → KAFKA SWAP IMPACT

**Before (all services use abstractions):**
```
Service → messaging_abstraction → Redis adapter
Service → messaging_abstraction → Kafka adapter  ❌ All services need changes
```

**After (Post Office exposes capabilities):**
```
Service → Post Office SOA API → Post Office → messaging_abstraction → Redis adapter
Service → Post Office SOA API → Post Office → messaging_abstraction → Kafka adapter  ✅ Only Post Office changes
```

**Migration Steps:**
1. Update Post Office's `messaging_abstraction` initialization
2. Swap Redis adapter → Kafka adapter in Post Office
3. No changes needed in other services (they use Post Office SOA APIs)

---

## 📝 NOTES

- **FastAPIRouterManager** is a utility (like DI Container) - simple, direct access
- **Post Office** uses abstractions internally, exposes SOA APIs externally
- **CommunicationMixin** delegates to Post Office, falls back to abstractions if needed
- **InfrastructureAccessMixin** no longer routes messaging/events to Communication Foundation
- **Redis → Kafka swap** only affects Post Office (other services use SOA APIs)

---

**Status:** 🚀 **READY TO EXECUTE**

