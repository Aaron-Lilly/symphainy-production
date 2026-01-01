# Registry Alignment Analysis: Services vs Capabilities

**Date:** November 21, 2025  
**Purpose:** Analyze what's actually being registered and ensure lifecycle management aligns with capability-based registration

---

## Executive Summary

**Issue Identified**: There's a **mismatch** between what's being registered (capabilities) and what lifecycle management handles (services).

**Current State**:
- ✅ Services register **capabilities** via `register_with_curator()` → `register_domain_capability()`
- ✅ Services ALSO register **service instance** via `register_service()` (for Consul service discovery)
- ⚠️ Lifecycle management only handles **services**, not **capabilities**

**Recommendation**: Lifecycle management should handle **both** services AND capabilities, with capabilities as the primary unit of registration.

---

## Part 1: What's Actually Being Registered

### 1.1 Registration Flow (Phase 2 Pattern)

**Business Enablement Services** (e.g., FileParserService):
```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "file_parsing",
            "protocol": "FileParserServiceProtocol",
            "description": "Parse files into structured formats",
            "contracts": {
                "soa_api": {...},
                "rest_api": {...},
                "mcp_tool": {...}
            }
        }
    ],
    soa_apis=["parse_file", "detect_file_type"],
    mcp_tools=["parse_file_tool"]
)
```

**What Happens**:
1. ✅ Capabilities registered via `register_domain_capability()` → **Capability Registry**
2. ✅ Protocols registered via `register_service_protocol()` → **Protocol Registry**
3. ✅ Routes tracked (if route metadata provided) → **Route Registry**
4. ✅ Service mesh policies reported → **Service Mesh Metadata Reporter**
5. ✅ Service instance registered via `register_service()` → **Service Registry** (for Consul)

### 1.2 Registration Flow (Legacy Pattern)

**Smart City Services** (e.g., City Manager):
```python
await curator.register_service(
    service_instance=service_instance,
    service_metadata={
        "service_name": "TrafficCop",
        "service_type": "smart_city",
        "realm": "smart_city",
        "capabilities": ["traffic_management", "load_balancing"]
    }
)
```

**What Happens**:
1. ✅ Service instance registered → **Service Registry** (for Consul)
2. ⚠️ Capabilities registered as strings → **Capability Registry** (minimal metadata)
3. ❌ No protocol registration
4. ❌ No route tracking
5. ❌ No service mesh policy reporting

---

## Part 2: Current Registry Structure

### 2.1 Service Registry (`CuratorFoundationService.registered_services`)

**Purpose**: Service discovery (Consul integration)

**Stores**:
- Service instance
- Service metadata (name, type, realm, capabilities list)
- Service ID (for Consul)
- Registration timestamp
- Service state

**Managed By**:
- `register_service()` - Registers service instance
- `unregister_service()` - Removes service instance
- `update_service()` - Updates service metadata
- `update_service_state()` - Updates service lifecycle state

**Lifecycle Management**: ✅ **IMPLEMENTED** (just completed)

### 2.2 Capability Registry (`CapabilityRegistryService.capability_registry`)

**Purpose**: Capability discovery and management

**Stores**:
- `CapabilityDefinition` objects (keyed by `service_name.capability_name`)
- Capability metadata (protocol, contracts, semantic mapping)
- Service-to-capability mappings

**Managed By**:
- `register_capability_definition()` - Registers capability
- `register_domain_capability()` - Registers via CuratorFoundationService
- `unregister_capability()` - Removes capability (by service_name)

**Lifecycle Management**: ❌ **NOT IMPLEMENTED**

**Issues**:
- No `update_capability()` method
- No capability lifecycle states
- No graceful capability deprecation
- `unregister_capability()` only removes by service_name (not individual capabilities)

---

## Part 3: The Mismatch

### 3.1 What Should Be Managed

**According to Phase 2 Design**:
- ✅ **Capabilities** are the primary unit of registration
- ✅ Services are containers for capabilities
- ✅ Capabilities have contracts (SOA API, REST API, MCP Tool)
- ✅ Capabilities have semantic mappings
- ✅ Capabilities have lifecycle states

**Current Lifecycle Management**:
- ✅ Services have lifecycle management
- ❌ Capabilities do NOT have lifecycle management
- ⚠️ Service lifecycle doesn't cascade to capabilities

### 3.2 Example Problem

**Scenario**: Service adds a new capability

**Current Flow**:
1. Service calls `register_with_curator()` with new capability
2. New capability registered in Capability Registry
3. Service metadata updated in Service Registry
4. ✅ Works, but...

**What's Missing**:
- ❌ No way to update existing capability metadata
- ❌ No way to deprecate a capability
- ❌ No way to mark capability as "maintenance"
- ❌ No capability versioning

---

## Part 4: Alignment Recommendations

### 4.1 Add Capability Lifecycle Management

**New Methods Needed**:

1. **`update_capability()`**
   ```python
   async def update_capability(
       self,
       service_name: str,
       capability_name: str,
       updates: Dict[str, Any],
       user_context: Dict[str, Any] = None
   ) -> Dict[str, Any]:
       """Update capability metadata."""
   ```

2. **`update_capability_state()`**
   ```python
   async def update_capability_state(
       self,
       service_name: str,
       capability_name: str,
       state: CapabilityState,  # active, deprecated, maintenance
       user_context: Dict[str, Any] = None
   ) -> Dict[str, Any]:
       """Update capability lifecycle state."""
   ```

3. **`unregister_capability()` (enhanced)**
   ```python
   async def unregister_capability(
       self,
       service_name: str,
       capability_name: Optional[str] = None,  # If None, unregister all
       user_context: Dict[str, Any] = None
   ) -> Dict[str, Any]:
       """Unregister capability (individual or all for service)."""
   ```

### 4.2 Link Service and Capability Lifecycle

**When Service Unregisters**:
- ✅ Unregister all capabilities for that service
- ✅ Unregister service from Consul
- ✅ Remove from Service Registry

**When Service Updates**:
- ✅ Update service metadata
- ✅ Optionally update capabilities (if capability updates provided)

**When Capability Updates**:
- ✅ Update capability in Capability Registry
- ✅ Optionally update service metadata (if service-level changes)

### 4.3 Capability States

**New Enum**:
```python
class CapabilityState(str, Enum):
    ACTIVE = "active"           # Capability is available
    DEPRECATED = "deprecated"   # Capability is deprecated (will be removed)
    MAINTENANCE = "maintenance" # Capability is in maintenance
    EXPERIMENTAL = "experimental" # Capability is experimental
```

---

## Part 5: Implementation Plan

### Phase 1: Add Capability Lifecycle Management

1. **Add `CapabilityState` enum**
   - Location: `foundations/curator_foundation/curator_foundation_service.py`
   - States: active, deprecated, maintenance, experimental

2. **Add `update_capability()` method**
   - Location: `foundations/curator_foundation/curator_foundation_service.py`
   - Updates capability metadata in Capability Registry
   - Updates service metadata if needed

3. **Add `update_capability_state()` method**
   - Location: `foundations/curator_foundation/curator_foundation_service.py`
   - Updates capability lifecycle state

4. **Enhance `unregister_capability()` method**
   - Location: `foundations/curator_foundation/services/capability_registry_service.py`
   - Support individual capability unregistration
   - Support service-wide capability unregistration

### Phase 2: Link Service and Capability Lifecycle

1. **Update `unregister_service()` to cascade**
   - When service unregisters, unregister all its capabilities
   - Already does this, but verify it's complete

2. **Update `update_service()` to handle capability updates**
   - If capability updates provided, update capabilities
   - Already does this partially, but needs enhancement

### Phase 3: Add Capability Versioning

1. **Support capability versioning**
   - Multiple versions of same capability
   - Version-based routing

---

## Part 6: Current Registration Audit

### 6.1 What Each Realm Registers

**Business Enablement Realm**:
- ✅ Uses `register_with_curator()` (Phase 2 pattern)
- ✅ Registers capabilities with full metadata
- ✅ Registers protocols
- ✅ Registers routes (via capability contracts)
- ✅ Reports service mesh policies
- ✅ Registers service instance (for Consul)

**Journey Realm**:
- ✅ Uses `register_with_curator()` (Phase 2 pattern)
- ✅ Registers capabilities
- ✅ Registers service instance

**Solution Realm**:
- ✅ Uses `register_with_curator()` (Phase 2 pattern)
- ✅ Registers capabilities
- ✅ Registers service instance

**Smart City Realm**:
- ⚠️ Uses direct `register_service()` (legacy pattern)
- ⚠️ Registers capabilities as strings (minimal metadata)
- ❌ No protocol registration
- ❌ No route tracking
- ❌ No service mesh policy reporting

---

## Part 7: Recommendations

### 7.1 Immediate Actions

1. **Add capability lifecycle management** (Phase 1 above)
   - Priority: 🔴 HIGH
   - Reason: Capabilities are primary unit, but have no lifecycle management

2. **Verify service unregistration cascades to capabilities**
   - Priority: 🔴 HIGH
   - Reason: Currently implemented, but needs verification

3. **Enhance capability update support**
   - Priority: 🟡 MEDIUM
   - Reason: Services need to update capability metadata

### 7.2 Future Enhancements

1. **Migrate Smart City to Phase 2 pattern**
   - Priority: 🟡 MEDIUM
   - Reason: Align with capability-based registration

2. **Add capability versioning**
   - Priority: 🟢 LOW
   - Reason: Support multiple capability versions

---

## Conclusion

**Current State**: 
- ✅ Service lifecycle management implemented
- ❌ Capability lifecycle management missing
- ⚠️ Mismatch between what's registered (capabilities) and what's managed (services)

**Recommendation**: 
- Add capability lifecycle management to align with Phase 2 capability-based registration
- Ensure service lifecycle cascades to capabilities
- Support capability updates and state management

**Next Steps**:
1. Review this analysis
2. Decide on implementation priority
3. Implement capability lifecycle management if approved




