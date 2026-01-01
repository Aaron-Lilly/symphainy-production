# Consul Capabilities & Service Discovery Architecture Analysis

**Date:** November 8, 2025  
**Purpose:** Comprehensive audit of Consul usage and Curator access patterns to design proper Public Works abstractions

---

## Executive Summary

Our platform currently has **SPAGHETTI ACCESS PATTERNS** for service discovery and registration:
- ✅ Consul infrastructure exists in Curator Foundation (5-layer pattern)
- ❌ NOT exposed through Public Works Foundation abstractions
- ❌ Multiple inconsistent patterns for accessing Curator
- ❌ Services directly couple to Curator implementation details
- ❌ No swap-ability for different service mesh technologies

**Goal:** Abstract service discovery through Public Works (like we do with Redis/event management) so we can swap Consul for Istio/Linkerd/other service mesh without breaking services.

---

## Part 1: Current Consul Infrastructure

### 1.1 Existing Consul Adapter (Layer 1)
**Location:** `foundations/curator_foundation/infrastructure_adapters/consul_adapter.py`

**Capabilities Exposed:**
```python
# Service Registration
await consul_adapter.register_service(service_name, service_data)
    - Registers service with Consul
    - Includes: address, port, tags, meta, health checks

# Service Discovery
await consul_adapter.discover_service(service_name) -> List[ServiceInfo]
    - Discovers healthy service instances
    - Returns: service_id, address, port, tags, meta, health_status

# Service Deregistration
await consul_adapter.deregister_service(service_name, service_id)
    - Removes service from Consul registry

# Health Checks
await consul_adapter.get_service_health(service_name) -> Dict
    - Returns health status of service instances

# Key-Value Store
await consul_adapter.put_kv(key, value)
await consul_adapter.get_kv(key) -> value
await consul_adapter.delete_kv(key)
    - Consul KV store for configuration management

# Watch Services
await consul_adapter.watch_service(service_name, callback)
    - Real-time notifications when service changes
```

### 1.2 Service Registration Abstraction (Layer 3)
**Location:** `foundations/curator_foundation/infrastructure_abstractions/service_registration_abstraction.py`

Adds business logic on top of Consul adapter:
- Service metadata validation
- Registration timestamp tracking
- Service status management
- Discovery with filtering

### 1.3 Curator Registry (Layer 5)
**Location:** `foundations/curator_foundation/infrastructure_registry/curator_registry.py`

Single point of exposure for Consul infrastructure:
- Builds complete 5-layer stack
- Provides composition services

---

## Part 2: Spaghetti Access Patterns (The Problem)

### 2.1 Pattern 1: Direct Curator Access via DI Container
**Used by:** Most realm services

```python
# Pattern 1A: get_foundation_service
curator = self.di_container.get_foundation_service("CuratorFoundationService")
await curator.register_service(service_instance, service_metadata)

# Pattern 1B: Direct attribute access
curator = self.di_container.curator
await curator.register_service(...)
```

**Problem:** Tightly coupled to Curator implementation. Can't swap service mesh.

### 2.2 Pattern 2: Via PlatformCapabilitiesMixin
**Used by:** Services inheriting from RealmServiceBase

```python
# Uses get_curator() helper
curator = self.get_curator()
await curator.register_service(...)

# For Smart City service discovery
librarian = await self.get_smart_city_api("Librarian")
# Internally calls curator.get_registered_services()
```

**Problem:** Still couples to Curator. Mixin assumes Curator exists.

### 2.3 Pattern 3: Manager Initialization Modules
**Used by:** Experience Manager, Journey Manager, Solution Manager

```python
# In initialization.py modules
curator = # ... get curator somehow ...
service_info = await curator.discover_service_by_name("SomeService")
```

**Problem:** Uses `discover_service_by_name()` which doesn't exist in Consul abstraction!

### 2.4 Pattern 4: SOA/MCP Registration Modules
**Used by:** Managers for capability registration

```python
# Different signatures!
await curator.register_service(service=self, capability=registration_data)  # Old
await curator.register_service(service_instance=self, service_metadata=data)  # New
```

**Problem:** Multiple incompatible method signatures across codebase.

### 2.5 Pattern 5: Main.py Direct Registration
**Used by:** Platform initialization for Smart City roles

```python
curator = self.foundation_services.get("CuratorFoundationService")
await curator.register_service(
    service_instance=librarian,
    service_metadata={...}
)
```

**Problem:** Main.py knows about Curator implementation details.

---

## Part 3: Capabilities Needed by Services

### 3.1 Service Registration Capabilities
**Who needs it:** All services (Smart City, realm services, orchestrators)

```python
# What services need to do:
1. Register themselves with metadata
   - Service name, type, capabilities
   - Address, port, health check endpoint
   - Tags, metadata (realm, layer, etc.)

2. Unregister on shutdown
   - Clean deregistration

3. Update service metadata
   - Change status, capabilities, etc.
```

### 3.2 Service Discovery Capabilities
**Who needs it:** All services discovering dependencies

```python
# What services need to do:
1. Discover service by name
   - "Where is Librarian?"
   - Returns: address, port, capabilities

2. Discover services by capability
   - "Who can parse files?"
   - Returns: list of services with that capability

3. Discover services by tag/realm
   - "All Smart City services"
   - Returns: filtered list

4. Watch for service changes
   - Real-time notifications when dependencies change
```

### 3.3 Configuration Management Capabilities
**Who needs it:** Services needing distributed configuration

```python
# What services need to do:
1. Store configuration values
   - Feature flags, settings, thresholds

2. Retrieve configuration
   - Get current values

3. Watch configuration changes
   - Real-time updates when config changes
```

### 3.4 Health Check Capabilities
**Who needs it:** All services, monitoring, orchestration

```python
# What services need to do:
1. Register health check endpoint
   - HTTP/TCP health checks

2. Update health status
   - Mark service healthy/unhealthy

3. Query service health
   - Check if dependency is healthy
```

---

## Part 4: Proposed Public Works Architecture

### 4.1 Service Discovery Abstraction
**Location:** `foundations/public_works_foundation/infrastructure_abstractions/service_discovery_abstraction.py`

```python
class ServiceDiscoveryAbstraction:
    """
    Service Discovery Abstraction (Layer 3)
    
    Provides business logic for service registration and discovery.
    Technology-agnostic interface that can use Consul, Istio, Linkerd, etc.
    """
    
    def __init__(self, adapter: ServiceDiscoveryAdapter):
        self.adapter = adapter  # Could be ConsulAdapter, IstioAdapter, etc.
    
    # Core registration methods
    async def register_service(self, service_info: Dict[str, Any]) -> ServiceRegistration
    async def unregister_service(self, service_id: str) -> bool
    async def update_service(self, service_id: str, updates: Dict) -> bool
    
    # Core discovery methods
    async def discover_service(self, service_name: str) -> List[ServiceRegistration]
    async def discover_by_capability(self, capability: str) -> List[ServiceRegistration]
    async def discover_by_tags(self, tags: List[str]) -> List[ServiceRegistration]
    
    # Health management
    async def check_service_health(self, service_name: str) -> HealthStatus
    async def update_health_status(self, service_id: str, status: str) -> bool
    
    # Configuration management (Consul KV or equivalent)
    async def set_config(self, key: str, value: Any) -> bool
    async def get_config(self, key: str) -> Any
    async def watch_config(self, key: str, callback: Callable) -> WatchHandle
    
    # Service watching (real-time updates)
    async def watch_service(self, service_name: str, callback: Callable) -> WatchHandle
```

### 4.2 Consul Adapter (Layer 1 - Move to Public Works)
**Location:** `foundations/public_works_foundation/infrastructure_adapters/consul_service_discovery_adapter.py`

```python
class ConsulServiceDiscoveryAdapter(ServiceDiscoveryAdapter):
    """
    Consul-specific implementation of service discovery.
    Can be swapped for IstioAdapter, LinkerdAdapter, etc.
    """
    
    def __init__(self, consul_client: Consul):
        self.consul = consul_client
    
    # Implements ServiceDiscoveryAdapter protocol
    async def register_service(...):
        # Consul-specific registration
        self.consul.agent.service.register(...)
    
    async def discover_service(...):
        # Consul-specific discovery
        return self.consul.health.service(...)
    
    # ... other methods using Consul API
```

### 4.3 Service Discovery Registry (Layer 5)
**Location:** `foundations/public_works_foundation/infrastructure_registry/service_discovery_registry.py`

```python
class ServiceDiscoveryRegistry:
    """
    Service Discovery Registry (Layer 5)
    
    Single point of exposure for service discovery infrastructure.
    Builds and manages the complete 5-layer stack.
    """
    
    def __init__(self):
        self.adapter = None  # ConsulAdapter or other
        self.abstraction = None  # ServiceDiscoveryAbstraction
        self.composition_service = None  # Optional composition layer
    
    async def build_infrastructure(self, config: Dict) -> bool:
        """Build the 5-layer service discovery infrastructure"""
        # Layer 1: Create adapter (Consul, Istio, etc.)
        adapter_type = config.get("adapter_type", "consul")
        if adapter_type == "consul":
            self.adapter = await self._build_consul_adapter(config)
        elif adapter_type == "istio":
            self.adapter = await self._build_istio_adapter(config)
        # ... other adapter types
        
        # Layer 3: Create abstraction
        self.abstraction = ServiceDiscoveryAbstraction(self.adapter)
        
        # Layer 4: Optional composition services
        # ... build composition layer if needed
        
        return True
    
    def get_service_discovery(self) -> ServiceDiscoveryAbstraction:
        """Get the service discovery abstraction"""
        return self.abstraction
```

### 4.4 Public Works Foundation Integration

```python
class PublicWorksFoundationService:
    def __init__(self, ...):
        # ... existing registries ...
        self.service_discovery_registry = None
    
    async def initialize_foundation(self):
        # ... existing initialization ...
        
        # Build service discovery infrastructure
        self.service_discovery_registry = ServiceDiscoveryRegistry()
        await self.service_discovery_registry.build_infrastructure({
            "adapter_type": "consul",  # From config
            "consul_host": os.getenv("CONSUL_HOST", "localhost"),
            "consul_port": int(os.getenv("CONSUL_PORT", 8500))
        })
        
        self.service_discovery_abstraction = self.service_discovery_registry.get_service_discovery()
    
    def get_abstraction(self, name: str) -> Any:
        abstraction_methods = {
            # ... existing abstractions ...
            "service_discovery": self.get_service_discovery_abstraction,
            "service_registry": self.get_service_discovery_abstraction,  # Alias
        }
        return abstraction_methods[name]()
    
    def get_service_discovery_abstraction(self):
        """Get service discovery abstraction"""
        if not self.service_discovery_abstraction:
            raise RuntimeError("Service discovery not initialized")
        return self.service_discovery_abstraction
```

---

## Part 5: Curator Foundation Refactor

### 5.1 New Curator Role
**After refactor, Curator should:**

```python
class CuratorFoundationService:
    """
    Curator Foundation coordinates pattern enforcement and capability tracking.
    NO LONGER manages service discovery infrastructure - that's Public Works!
    """
    
    def __init__(self, di_container, public_works_foundation):
        # Get service discovery from Public Works (the RIGHT way!)
        self.service_discovery = public_works_foundation.get_abstraction("service_discovery")
        
        # Curator-specific micro-services
        self.capability_registry = CapabilityRegistryService(...)
        self.pattern_validation = PatternValidationService(...)
        # ... etc
    
    async def register_service(self, service_instance, service_metadata):
        """
        Register service - delegates to Public Works for actual registration
        """
        # 1. Register capabilities with Curator's capability registry
        await self.capability_registry.register_capabilities(...)
        
        # 2. Register service with service discovery (via Public Works)
        await self.service_discovery.register_service(service_metadata)
        
        # 3. Store local cache for fast lookups
        self.registered_services[service_name] = {...}
    
    async def discover_service_by_name(self, service_name: str):
        """
        Discover service - delegates to Public Works
        """
        # Query service discovery (via Public Works)
        return await self.service_discovery.discover_service(service_name)
```

### 5.2 Service Access Pattern (After Refactor)

```python
# Services should access service discovery via Public Works directly!
class MyRealmService(RealmServiceBase):
    async def initialize(self):
        # Get service discovery from Public Works
        service_discovery = self.platform_gateway.public_works.get_abstraction("service_discovery")
        
        # Register myself
        await service_discovery.register_service({
            "service_name": self.service_name,
            "address": "localhost",
            "port": 8000,
            "capabilities": ["my_capability"],
            # ... metadata
        })
        
        # Discover dependencies
        librarian_info = await service_discovery.discover_service("Librarian")
```

**OR via PlatformGateway helper:**

```python
class PlatformGateway:
    async def register_service(self, service_info):
        """Convenience method - delegates to Public Works"""
        service_discovery = self.public_works.get_abstraction("service_discovery")
        return await service_discovery.register_service(service_info)
    
    async def discover_service(self, service_name):
        """Convenience method - delegates to Public Works"""
        service_discovery = self.public_works.get_abstraction("service_discovery")
        return await service_discovery.discover_service(service_name)
```

---

## Part 6: Migration Plan

### Phase 1: Build Public Works Service Discovery Infrastructure
1. ✅ Move `consul_adapter.py` to Public Works infrastructure adapters
2. ✅ Create `ServiceDiscoveryAbstraction` in Public Works
3. ✅ Create `ServiceDiscoveryRegistry` in Public Works
4. ✅ Integrate into Public Works Foundation initialization
5. ✅ Expose via `get_abstraction("service_discovery")`

### Phase 2: Update Curator to Use Public Works
1. ✅ Remove Curator's internal Consul infrastructure
2. ✅ Get service discovery from Public Works
3. ✅ Update `register_service()` to delegate to Public Works
4. ✅ Update `discover_service_by_name()` to delegate to Public Works

### Phase 3: Update Service Access Patterns
1. ✅ Update `RealmServiceBase` to use Public Works for registration
2. ✅ Update `PlatformCapabilitiesMixin` to use Public Works for discovery
3. ✅ Update managers to use consistent discovery pattern
4. ✅ Remove direct Curator access where possible

### Phase 4: Update Main.py
1. ✅ Use Public Works for Smart City role registration
2. ✅ Remove direct Curator calls for infrastructure concerns

### Phase 5: Testing & Validation
1. ✅ Test service registration flows
2. ✅ Test service discovery flows
3. ✅ Test health checks
4. ✅ Validate Consul integration still works
5. ✅ Document new patterns

---

## Part 7: Benefits of This Architecture

### 7.1 Swap-ability
```python
# Easy to swap Consul for Istio
config = {
    "adapter_type": "istio",  # Was "consul"
    "istio_host": "...",
}
# All services continue working - no code changes!
```

### 7.2 Consistent Patterns
```python
# ONE way to register services
await platform_gateway.register_service(service_info)

# ONE way to discover services
await platform_gateway.discover_service(service_name)
```

### 7.3 Proper Separation of Concerns
- **Public Works:** Infrastructure (HOW to register/discover)
- **Curator:** Pattern enforcement and capability tracking (WHAT is registered)
- **Services:** Business logic (use registration/discovery)

### 7.4 Service Mesh Ready
- Consul → Consul Connect (service mesh) just upgrade adapter
- Consul → Istio just swap adapter
- Multi-cluster federation ready

---

## Part 8: Files Requiring Changes

### Create New Files
- `foundations/public_works_foundation/infrastructure_adapters/consul_service_discovery_adapter.py`
- `foundations/public_works_foundation/infrastructure_abstractions/service_discovery_abstraction.py`
- `foundations/public_works_foundation/infrastructure_registry/service_discovery_registry.py`
- `foundations/public_works_foundation/abstraction_contracts/service_discovery_protocol.py`

### Modify Existing Files
- `foundations/public_works_foundation/public_works_foundation_service.py` - Add service discovery
- `foundations/curator_foundation/curator_foundation_service.py` - Remove Consul, use Public Works
- `bases/realm_service_base.py` - Update registration pattern
- `bases/mixins/platform_capabilities_mixin.py` - Update discovery pattern
- `main.py` - Use Public Works for registration
- All manager `initialization.py` modules - Update discovery pattern

### Move/Archive Files
- `foundations/curator_foundation/infrastructure_adapters/consul_adapter.py` → Move to Public Works
- `foundations/curator_foundation/infrastructure_abstractions/service_registration_abstraction.py` → Archive
- `foundations/curator_foundation/infrastructure_registry/curator_registry.py` → Archive

---

## Conclusion

This refactor transforms service discovery from a **Curator-specific implementation detail** into a **first-class Public Works abstraction**, enabling:
- ✅ Technology swap-ability (Consul → Istio → Linkerd)
- ✅ Consistent access patterns
- ✅ Proper architectural layering
- ✅ Service mesh readiness
- ✅ Federation support

**Next Step:** User approval to proceed with implementation.

