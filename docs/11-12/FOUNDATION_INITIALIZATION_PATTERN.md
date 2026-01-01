# Foundation Initialization Pattern

## Overview

This document describes the architectural pattern for foundation service initialization in the DI Container.

## Core Principle

**Foundations are initialized in order by DI Container, and each foundation gets its infrastructure from Public Works Foundation (not from other foundations).**

## Initialization Order

The DI Container initializes foundations in the following order during `_initialize_manager_vision_support()`:

1. **Public Works Foundation** - Provides infrastructure abstractions (databases, messaging, caching, etc.)
2. **Curator Foundation** - Uses Public Works for infrastructure, provides service discovery and registry
3. **Communication Foundation** (lazy) - Uses Public Works for infrastructure and Curator for service discovery

## Architectural Pattern

### Public Works Foundation
- **Role**: Infrastructure provider for all other foundations
- **Dependencies**: None (base infrastructure layer)
- **Provides**: Database abstractions, messaging abstractions, caching abstractions, service discovery abstractions

### Curator Foundation
- **Role**: Service registry and discovery coordinator
- **Dependencies**: Public Works Foundation (for infrastructure)
- **Independence**: Curator is **independent** and does NOT depend on Communication Foundation
- **Provides**: Service registration, capability registry, pattern validation, anti-pattern detection

### Communication Foundation
- **Role**: Communication infrastructure (API Gateway, SOA Client, WebSocket, Messaging, Event Bus)
- **Dependencies**: 
  - Public Works Foundation (for infrastructure)
  - Curator Foundation (for service discovery)
- **Initialization**: Lazy (created when `get_communication_foundation()` is called)
- **Auto-retrieval**: Automatically gets Curator from DI Container if not provided

## Key Design Decisions

1. **Curator is Independent**: Curator Foundation does not depend on Communication Foundation. It can work standalone and gets all its infrastructure from Public Works.

2. **Communication Uses Curator**: Communication Foundation uses Curator for service discovery and registry, but this is a usage relationship, not a dependency for initialization.

3. **Auto-retrieval Pattern**: Communication Foundation automatically retrieves Curator from DI Container if not explicitly provided, making the pattern cleaner and less error-prone.

4. **Infrastructure from Public Works**: All foundations get their infrastructure (databases, messaging, etc.) from Public Works Foundation, not from each other.

## Code Examples

### DI Container Initialization

```python
def _initialize_manager_vision_support(self):
    # 1. Initialize Public Works Foundation (infrastructure provider)
    self.public_works_foundation = PublicWorksFoundationService(di_container=self)
    
    # 2. Initialize Curator Foundation (independent, uses Public Works)
    self.curator_foundation = CuratorFoundationService(
        foundation_services=self,
        public_works_foundation=self.public_works_foundation
    )
    
    # 3. Communication Foundation (lazy initialization)
    self.communication_foundation = None
```

### Communication Foundation Auto-retrieval

```python
def __init__(self, di_container, public_works_foundation, curator_foundation=None, ...):
    # Get Curator Foundation from DI Container if not provided
    if curator_foundation is None:
        curator_foundation = di_container.get_curator_foundation()
    self.curator_foundation = curator_foundation
```

## Benefits

1. **Clear Dependency Chain**: Public Works → Curator → Communication (usage, not initialization dependency)
2. **Independence**: Curator can work standalone without Communication Foundation
3. **Flexibility**: Communication Foundation can be created lazily when needed
4. **Consistency**: All foundations follow the same pattern of getting infrastructure from Public Works

## Migration Notes

This pattern replaces the old architectural remnant where Curator Foundation was created by Communication Foundation. The new pattern:

- Initializes Curator in DI Container (alongside Public Works)
- Makes Communication Foundation retrieve Curator from DI Container
- Ensures Curator is independent and can work without Communication Foundation

