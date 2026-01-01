# Communication Foundation Services Refactoring Plan

**Date**: November 15, 2025  
**Status**: 📋 Ready to Implement

---

## Goal

Refactor the 3 "adapters" in Communication Foundation to be **Foundation Services** that:
1. Inherit from `FoundationServiceBase`
2. Receive Public Works abstractions via DI (like everyone else)
3. Are registered in DI Container
4. Can be accessed by Smart City services via `di_container.get_foundation_service()`
5. Avoid breaking changes in Smart City when swapping infrastructure

---

## Current State

**Problem**: These are "adapters" masquerading as infrastructure, but they're actually business logic wrappers:
- `communication_foundation/infrastructure_adapters/websocket_adapter.py`
- `communication_foundation/infrastructure_adapters/messaging_adapter.py`
- `communication_foundation/infrastructure_adapters/event_bus_adapter.py`

**Why They Exist**: To avoid breaking changes in Smart City when swapping infrastructure implementations (Redis → RabbitMQ → Kafka, etc.)

---

## Solution: Foundation Services Pattern

### Pattern Overview

```
┌─────────────────────────────────────────────────────────┐
│  Smart City Services (Post Office, etc.)                │
│  └─> di_container.get_foundation_service("...")        │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Communication Foundation Services                      │
│  ├─> WebSocketFoundationService                        │
│  ├─> MessagingFoundationService                         │
│  └─> EventBusFoundationService                          │
│  └─> Receive Public Works abstractions via DI          │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Public Works Foundation                                │
│  ├─> WebSocketAdapter (swappable)                      │
│  ├─> MessagingAbstraction (swappable)                   │
│  └─> EventManagementAbstraction (swappable)             │
└─────────────────────────────────────────────────────────┘
```

### Benefits

1. ✅ **No Breaking Changes**: Smart City services access foundation services, not infrastructure directly
2. ✅ **Swappable Infrastructure**: Public Works abstractions can be swapped without touching Smart City
3. ✅ **Consistent Pattern**: Foundation services follow same pattern as other foundation services
4. ✅ **Proper DI**: Foundation services receive abstractions via DI (like everyone else)
5. ✅ **Separation of Concerns**: Infrastructure in Public Works, business logic in Communication Foundation

---

## Implementation Plan

### Step 1: Create Foundation Service Base Classes

**Files to Create**:
1. `communication_foundation/foundation_services/websocket_foundation_service.py`
2. `communication_foundation/foundation_services/messaging_foundation_service.py`
3. `communication_foundation/foundation_services/event_bus_foundation_service.py`

**Pattern**:
```python
from bases.foundation_service_base import FoundationServiceBase
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

class WebSocketFoundationService(FoundationServiceBase):
    """Foundation service for WebSocket infrastructure."""
    
    def __init__(self, di_container, public_works_foundation: PublicWorksFoundationService):
        super().__init__(
            service_name="websocket_foundation",
            di_container=di_container
        )
        self.public_works_foundation = public_works_foundation
        
        # Get infrastructure from Public Works (via DI)
        self.websocket_adapter = None  # Will be set in initialize()
    
    async def initialize(self) -> bool:
        """Initialize foundation service."""
        # Get infrastructure from Public Works Foundation
        self.websocket_adapter = self.public_works_foundation.get_websocket_adapter()
        if not self.websocket_adapter:
            raise RuntimeError("WebSocket adapter not available from Public Works Foundation")
        
        await self.websocket_adapter.initialize()
        # ... rest of initialization
        
        return True
    
    # Business logic methods (realm routing, etc.)
    async def send_to_realm(self, realm: str, message: Dict[str, Any]) -> bool:
        """Send message to specific realm."""
        # Business logic for realm routing
        pass
```

### Step 2: Register in DI Container

**File**: `foundations/di_container/di_container_service.py`

```python
def get_websocket_foundation(self):
    """Get WebSocket Foundation Service."""
    if not self.websocket_foundation:
        from foundations.communication_foundation.foundation_services.websocket_foundation_service import WebSocketFoundationService
        
        self.websocket_foundation = WebSocketFoundationService(
            di_container=self,
            public_works_foundation=self.get_public_works_foundation()
        )
        await self.websocket_foundation.initialize()
    return self.websocket_foundation

# Similar for messaging_foundation and event_bus_foundation
```

### Step 3: Update Communication Foundation Service

**File**: `communication_foundation/communication_foundation_service.py`

**Changes**:
- Remove creation of "adapters"
- Get foundation services from DI container instead

```python
async def _initialize_infrastructure_adapters(self):
    """Initialize infrastructure foundation services."""
    self.logger.info("🔧 Initializing infrastructure foundation services...")
    
    # Get foundation services from DI Container
    self.websocket_foundation = self.di_container.get_websocket_foundation()
    self.messaging_foundation = self.di_container.get_messaging_foundation()
    self.event_bus_foundation = self.di_container.get_event_bus_foundation()
```

### Step 4: Update Smart City Services

**Pattern for Smart City Services**:
```python
# In Post Office or other Smart City service:
async def initialize(self):
    # Get foundation services from DI Container
    self.websocket_foundation = self.di_container.get_foundation_service("websocket_foundation")
    self.messaging_foundation = self.di_container.get_foundation_service("messaging_foundation")
    self.event_bus_foundation = self.di_container.get_foundation_service("event_bus_foundation")
    
    # Use foundation services (not infrastructure directly)
    await self.websocket_foundation.send_to_realm("business_enablement", message)
```

### Step 5: Archive Old Adapters

**Files to Archive**:
- `communication_foundation/infrastructure_adapters/websocket_adapter.py` → `archive/`
- `communication_foundation/infrastructure_adapters/messaging_adapter.py` → `archive/`
- `communication_foundation/infrastructure_adapters/event_bus_adapter.py` → `archive/`

---

## File Structure

```
communication_foundation/
├── foundation_services/          # NEW
│   ├── websocket_foundation_service.py
│   ├── messaging_foundation_service.py
│   └── event_bus_foundation_service.py
├── infrastructure_adapters/      # OLD (to be archived)
│   ├── websocket_adapter.py     # → archive/
│   ├── messaging_adapter.py     # → archive/
│   └── event_bus_adapter.py     # → archive/
└── communication_foundation_service.py  # Updated
```

---

## Migration Checklist

- [ ] Create `foundation_services/` directory
- [ ] Create `WebSocketFoundationService` (inherit from `FoundationServiceBase`)
- [ ] Create `MessagingFoundationService` (inherit from `FoundationServiceBase`)
- [ ] Create `EventBusFoundationService` (inherit from `FoundationServiceBase`)
- [ ] Update all 3 services to receive Public Works abstractions via DI
- [ ] Register all 3 services in DI Container (`di_container_service.py`)
- [ ] Update `CommunicationFoundationService` to use foundation services from DI
- [ ] Update Smart City services to access foundation services via `get_foundation_service()`
- [ ] Archive old adapter files
- [ ] Update tests
- [ ] Verify no breaking changes

---

## Key Design Decisions

1. **Foundation Services vs Composition Services**: 
   - Foundation Services = Infrastructure-level services that multiple Smart City roles use
   - Composition Services = Business logic that composes multiple abstractions
   - These are Foundation Services (infrastructure-level)

2. **Why Not in Smart City?**:
   - To avoid breaking changes when swapping infrastructure
   - Foundation services provide stable API, infrastructure can change underneath

3. **Why Not in Public Works?**:
   - Public Works = Infrastructure only (adapters + abstractions)
   - Communication Foundation = Infrastructure services (business logic on top of infrastructure)
   - Separation: Infrastructure vs Infrastructure Services

---

## Example: WebSocketFoundationService

```python
#!/usr/bin/env python3
"""
WebSocket Foundation Service

Infrastructure-level service for WebSocket communication.
Provides stable API for Smart City services while allowing infrastructure swapping.

WHAT (Foundation Service): I provide WebSocket infrastructure services
HOW (Service Implementation): I use Public Works WebSocket adapter via DI
"""

from typing import Dict, Any, Optional, List
from bases.foundation_service_base import FoundationServiceBase
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

class WebSocketFoundationService(FoundationServiceBase):
    """Foundation service for WebSocket infrastructure."""
    
    def __init__(self, di_container, public_works_foundation: PublicWorksFoundationService):
        super().__init__(
            service_name="websocket_foundation",
            di_container=di_container
        )
        self.public_works_foundation = public_works_foundation
        self.websocket_adapter = None
        
        # Business logic state (realm routing, etc.)
        self.realm_connections = {
            "smart_city": {},
            "business_enablement": {},
            "experience": {},
            "journey_solution": {}
        }
    
    async def initialize(self) -> bool:
        """Initialize foundation service."""
        try:
            # Get infrastructure from Public Works Foundation (via DI)
            self.websocket_adapter = self.public_works_foundation.get_websocket_adapter()
            if not self.websocket_adapter:
                raise RuntimeError("WebSocket adapter not available from Public Works Foundation")
            
            await self.websocket_adapter.initialize()
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket Foundation Service: {e}")
            return False
    
    # Business logic methods (realm routing, etc.)
    async def send_to_realm(self, realm: str, message: Dict[str, Any]) -> bool:
        """Send message to specific realm via WebSocket."""
        # Business logic for realm routing
        if realm not in self.realm_connections:
            return False
        
        # Use infrastructure adapter
        # ... realm routing logic ...
        return True
```

---

**Status**: ✅ Ready to implement



