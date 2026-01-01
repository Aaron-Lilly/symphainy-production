# Routing Ownership Strategy: Clarification

**Date**: December 2024  
**Status**: ✅ Finalized  
**Context**: Aligned with routing mess discovery and CURATOR_CENTRAL_HUB_DESIGN.md

---

## The Question

Should routing metadata be:
- **Domain-owned** (domains manage, Curator reports)?
- **Curator-owned** (Curator manages routing metadata)?
- **Hybrid** (domains define, Curator tracks)?

---

## The Answer: Hybrid Approach

**Routes**: Domains define, Curator tracks centrally  
**Service Mesh Policies**: Domains own, Curator reports/aggregates

---

## Key Insight from CURATOR_CENTRAL_HUB_DESIGN.md

> "API Routing: Service mesh handles routing (Curator provides endpoint registry)"

This means:
- **Curator PROVIDES endpoint registry** (tracks routes centrally for discovery)
- **Service mesh HANDLES routing** (executes routes)
- **Domains DEFINE routes** (when registering capabilities/SOA APIs)

---

## Routing Ownership Breakdown

### 1. Route Definitions (Domain-Owned)

**Who Defines Routes**: Domains (when registering capabilities/SOA APIs)

**When Routes Are Defined**:
- When services register capabilities (routes are part of capability metadata)
- When services register SOA APIs (routes are part of SOA API metadata)
- Routes are defined as part of service registration

**Example**:
```python
# Domain defines route when registering capability
capability = CapabilityDefinition(
    service_name="FileParserService",
    capability_name="file_parsing",
    # Route is part of capability metadata
    contracts={
        "rest_api": {
            "endpoint": "/api/v1/content-pillar/upload-file",
            "method": "POST"
        }
    }
)
```

---

### 2. Route Tracking (Curator-Owned)

**Who Tracks Routes**: Curator (endpoint registry)

**Why Curator Tracks**:
- **Fix routing mess**: Routes weren't being tracked anywhere (the problem we discovered)
- **Route discovery**: Services need to discover available routes
- **Service mesh evolution**: Curator provides endpoint registry for Consul Connect
- **Platform governance**: Centralized route tracking for platform visibility

**How Routes Are Tracked**:
- Routes automatically registered when capabilities/SOA APIs are registered
- Routes stored in Curator's endpoint registry
- Routes discoverable via `curator.discover_routes()`

**Example**:
```python
# Curator tracks route in endpoint registry
await curator.register_route({
    "route_id": "...",
    "path": "/api/v1/content-pillar/upload-file",
    "method": "POST",
    "pillar": "content-pillar",
    "realm": "business_enablement",
    "defined_by": "business_enablement_realm"  # Domain attribution
})
```

---

### 3. Service Mesh Policies (Domain-Owned, Curator Reports)

**Who Owns Policies**: Domains (load balancing, timeouts, circuit breakers)

**Who Reports Policies**: Curator (aggregates and reports, doesn't manage)

**Why Domain-Owned**:
- Policies are domain-specific (each domain knows its requirements)
- Domains control their own routing policies
- Service mesh enforces policies (domains define, service mesh executes)

**Why Curator Reports**:
- Aggregates policies from all domains
- Provides unified view for service mesh configuration
- Supports service mesh evolution (Consul Connect)

**Example**:
```python
# Domain reports policies (domain owns)
await curator.report_service_mesh_policies(
    service_name="FileParserService",
    policies={
        "source": "business_enablement_realm",  # Domain owns
        "policies": {
            "load_balancing": "round_robin",  # Domain-defined
            "timeout": "30s",  # Domain-defined
            "circuit_breakers": {...}  # Domain-defined
        }
    }
)

# Curator aggregates and reports (doesn't manage)
report = await curator.get_service_mesh_policy_report("FileParserService")
```

---

## Comparison: Original vs Revised vs Final

### Original Approach (Before Routing Mess Discovery)
- ❌ Unclear routing ownership
- ❌ Routes not tracked anywhere
- ❌ No endpoint registry

### Revised Approach (After Routing Mess Discovery, Before Clarification)
- ✅ Domain-owned routing metadata (Curator reports)
- ⚠️ Unclear if this applies to route tracking or just policies

### Final Approach (After Clarification)
- ✅ **Routes**: Domains define, Curator tracks centrally (endpoint registry)
- ✅ **Policies**: Domains own, Curator reports/aggregates
- ✅ Clear separation: route tracking vs policy reporting

---

## Implementation in Phase 2

### 2.4: Route Registry (NEW)
- **Purpose**: Track routes centrally (Curator owns endpoint registry)
- **Routes defined by**: Domains (when registering capabilities/SOA APIs)
- **Routes tracked by**: Curator (for discovery and service mesh evolution)

### 2.5: Service Mesh Policy Reporter (NEW)
- **Purpose**: Report service mesh policies (domain owns, Curator reports)
- **Policies owned by**: Domains (load balancing, timeouts, circuit breakers)
- **Policies reported by**: Curator (aggregates and reports)

---

## Benefits of Final Approach

1. **Fixes Routing Mess**: Routes tracked centrally (solves the problem we discovered)
2. **Route Discovery**: Services can discover routes via Curator
3. **Service Mesh Ready**: Curator provides endpoint registry for Consul Connect
4. **Domain Control**: Domains define routes and policies (domain autonomy)
5. **Platform Governance**: Centralized tracking for platform visibility
6. **Clear Ownership**: Routes tracked by Curator, policies owned by domains

---

## Summary

| Aspect | Ownership | Purpose |
|--------|-----------|---------|
| **Route Definitions** | Domains define | Routes defined when registering capabilities/SOA APIs |
| **Route Tracking** | Curator tracks | Endpoint registry for discovery and service mesh evolution |
| **Service Mesh Policies** | Domains own | Load balancing, timeouts, circuit breakers |
| **Policy Reporting** | Curator reports | Aggregates policies from domains |

**Key Principle**: 
- **Routes**: Domains define, Curator tracks (endpoint registry)
- **Policies**: Domains own, Curator reports (aggregation)

---

**End of Routing Ownership Strategy Document**








