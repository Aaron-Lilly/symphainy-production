# Curator Foundation as Central Registry Hub - MECE Design

**Date**: December 2024  
**Status**: 🎯 Strategic Design - Review Required

---

## Executive Summary

Analyzed all platform registries and their usage patterns to design Curator Foundation as the **central hub for platform registries** with MECE (Mutually Exclusive, Collectively Exhaustive) coverage. Design considers current Consul usage and future service mesh evolution with Consul Connect.

### Key Findings

- **8 distinct registries** currently exist across the platform
- **3 registration paths** for services (inconsistent)
- **Service Discovery** already abstracted through Public Works (good!)
- **Domain-specific registries** (AGUI, Specialization) should remain separate
- **Platform-wide registries** should flow through Curator

### Design Principles

1. **MECE Coverage**: Every platform capability registered exactly once
2. **Service Mesh Ready**: Design supports Consul Connect evolution
3. **Separation of Concerns**: Infrastructure (Public Works) vs Platform (Curator)
4. **Single Source of Truth**: Curator is authoritative for platform capabilities

---

## Current Registry Inventory

### 1. Service Discovery Registry (Public Works Foundation)

**Location**: `foundations/public_works_foundation/infrastructure_registry/service_discovery_registry.py`

**Purpose**: Infrastructure abstraction for service discovery (Consul/Istio/Linkerd)

**What It Registers**:
- Service instances (address, port, health checks)
- Service metadata (tags, labels)
- Health status

**Current Usage**:
- ✅ Abstracted through Public Works (good!)
- ✅ Used by Curator for Consul registration
- ✅ Swap-able (Consul → Istio → Linkerd)

**Should Go Through Curator?**: ❌ **NO** - This is infrastructure, not platform capability

**Reasoning**: Service Discovery is **HOW** (infrastructure), not **WHAT** (platform capability). Curator uses it but doesn't own it.

---

### 2. Capability Registry Service (Curator Foundation)

**Location**: `foundations/curator_foundation/services/capability_registry_service.py`

**Purpose**: Platform capability registration and discovery

**What It Registers**:
- Service capabilities (what services can do)
- Capability definitions (interface, endpoints, tools)
- Service-to-capability mappings

**Current Usage**:
- Used by `register_service()` to register capabilities
- Stores `CapabilityDefinition` objects
- Validates capability structure

**Should Go Through Curator?**: ✅ **YES** - This IS Curator (core function)

**Status**: ✅ Already in Curator

---

### 3. Service Registry (Curator Foundation)

**Location**: `foundations/curator_foundation/curator_foundation_service.py::registered_services`

**Purpose**: Platform service registration (instances + metadata)

**What It Registers**:
- Service instances
- Service metadata (name, type, realm, capabilities)
- Service status

**Current Usage**:
- `register_service()` method
- Local cache (Consul is source of truth)
- Used for service discovery via `get_registered_services()`

**Should Go Through Curator?**: ✅ **YES** - This IS Curator (core function)

**Status**: ✅ Already in Curator

---

### 4. SOA API Registry (Curator Foundation)

**Location**: `foundations/curator_foundation/curator_foundation_service.py::soa_api_registry`

**Purpose**: SOA API endpoint registration for realm consumption

**What It Registers**:
- SOA API endpoints (service_name.api_name)
- API handlers
- API metadata (method, description)

**Current Usage**:
- Services call `register_soa_api()` directly
- Separate from service registration
- Used for realm-to-realm communication

**Should Go Through Curator?**: ✅ **YES** - Platform capability exposure

**Status**: ✅ Already in Curator

---

### 5. MCP Tool Registry (Curator Foundation)

**Location**: `foundations/curator_foundation/curator_foundation_service.py::mcp_tool_registry`

**Purpose**: MCP tool registration for agent access

**What It Registers**:
- MCP tool definitions
- Tool handlers
- Tool metadata (service_name, tool_name)

**Current Usage**:
- Services call `register_mcp_tool()` directly
- Separate from service registration
- Used for agent-to-service communication

**Should Go Through Curator?**: ✅ **YES** - Platform capability exposure

**Status**: ✅ Already in Curator

---

### 6. Agent Capability Registry (Curator Foundation)

**Location**: `foundations/curator_foundation/services/agent_capability_registry_service.py`

**Purpose**: Agent capability registration and management

**What It Registers**:
- Agent capabilities (what agents can do)
- Agent-to-capability mappings
- Capability usage tracking

**Current Usage**:
- Agents call `register_agent_capabilities()` via Agent SDK
- Tracks agent capabilities separately from service capabilities
- Used for agent discovery and health monitoring

**Should Go Through Curator?**: ✅ **YES** - Platform capability (agentic)

**Status**: ✅ Already in Curator

---

### 7. Communication Registry (Communication Foundation)

**Location**: `foundations/communication_foundation/infrastructure_registry/communication_registry.py`

**Purpose**: Communication infrastructure component tracking

**What It Registers**:
- Communication services
- Service relationships
- Communication endpoints
- Health status

**Current Usage**:
- Internal to Communication Foundation
- Tracks communication abstractions
- Not used by other foundations

**Should Go Through Curator?**: ❌ **NO** - This is infrastructure tracking, not platform capability

**Reasoning**: Similar to Service Discovery Registry - this is **HOW** (infrastructure), not **WHAT** (platform capability).

**Recommendation**: Keep internal to Communication Foundation, but register Communication Foundation's **capabilities** (not infrastructure) with Curator.

---

### 8. Specialization Registry (Agentic Foundation)

**Location**: `foundations/agentic_foundation/specialization_registry.py`

**Purpose**: Agent specialization configuration management

**What It Registers**:
- Specialization definitions
- Pillar-specific specializations
- Specialization configurations

**Current Usage**:
- Used by Curator's Agent Capability Registry
- Loaded from JSON config
- Domain-specific to agentic operations

**Should Go Through Curator?**: ⚠️ **PARTIAL** - Curator should reference it, but it's domain-specific

**Reasoning**: Specializations are **domain knowledge** (agentic), not **platform capabilities**. Curator should know about specializations but not own them.

**Recommendation**: Keep in Agentic Foundation, but Curator should register that Agentic Foundation **provides specialization management** as a capability.

---

### 9. AGUI Schema Registry (Agentic Foundation)

**Location**: `foundations/agentic_foundation/agui_schema_registry.py`

**Purpose**: AGUI output schema management for agents

**What It Registers**:
- AGUI schemas per agent
- Component types
- Schema versions

**Current Usage**:
- Used by Curator's AGUI Schema Documentation Service
- Domain-specific to agentic operations
- Loaded from JSON config

**Should Go Through Curator?**: ⚠️ **PARTIAL** - Curator should reference it, but it's domain-specific

**Reasoning**: AGUI schemas are **domain knowledge** (agentic), not **platform capabilities**. Curator should know about schemas but not own them.

**Recommendation**: Keep in Agentic Foundation, but Curator should register that Agentic Foundation **provides AGUI schema management** as a capability.

---

### 10. Tool Registry Service (Agentic Foundation)

**Location**: `foundations/agentic_foundation/infrastructure_enablement/tool_registry_service.py`

**Purpose**: Tool registration and discovery for agentic operations

**What It Registers**:
- Tool definitions
- Tool storage (via Tool Storage Abstraction)
- Tool-to-agent mappings

**Current Usage**:
- Integrates with Curator's Capability Registry
- Stores tools in infrastructure (via Public Works)
- Business service (orchestrates storage + Curator)

**Should Go Through Curator?**: ✅ **YES** - Already integrates with Curator

**Status**: ✅ Already integrated (registers with Curator)

---

### 11. Infrastructure Registries (Public Works Foundation)

**Locations**:
- `foundations/public_works_foundation/infrastructure_registry/content_metadata_registry.py`
- `foundations/public_works_foundation/infrastructure_registry/file_management_registry_gcs.py`
- `foundations/public_works_foundation/infrastructure_registry/security_registry.py`
- `foundations/public_works_foundation/infrastructure_registry/knowledge_infrastructure_registry.py`
- `foundations/public_works_foundation/infrastructure_registry/data_infrastructure_registry.py`

**Purpose**: Infrastructure abstraction exposure (Layer 5 pattern)

**What They Register**:
- Infrastructure abstractions (created by Public Works)
- Abstraction-to-adapter mappings
- Infrastructure component status

**Should Go Through Curator?**: ❌ **NO** - These are infrastructure exposure, not platform capabilities

**Reasoning**: These registries expose **HOW** (infrastructure abstractions), not **WHAT** (platform capabilities). Services use these abstractions, but Curator should know about the **services** that use them, not the abstractions themselves.

**Recommendation**: Keep in Public Works. Curator should register services that **use** these abstractions, not the abstractions themselves.

---

## MECE Structure for Curator Foundation

### Platform Capability Categories (MECE)

Curator should be the **single source of truth** for all **platform capabilities**. Capabilities are organized into mutually exclusive, collectively exhaustive categories:

#### 1. **Service Capabilities** (What services can do)
- **Registry**: `CapabilityRegistryService`
- **What**: Service capabilities, interfaces, endpoints, tools
- **Who Registers**: Services (via `register_service()` or `register_capability()`)
- **Service Mesh Impact**: Services register capabilities, service mesh handles routing

#### 2. **Service Instances** (Where services are)
- **Registry**: `registered_services` dict
- **What**: Service instances, metadata, status
- **Who Registers**: Services (via `register_service()`)
- **Service Mesh Impact**: Consul Connect will handle instance discovery and routing

#### 3. **API Endpoints** (How to call services)
- **Registry**: `soa_api_registry`
- **What**: SOA API endpoints for realm consumption
- **Who Registers**: Services (via `register_soa_api()`)
- **Service Mesh Impact**: Service mesh handles API routing and load balancing

#### 4. **Agent Tools** (What agents can use)
- **Registry**: `mcp_tool_registry`
- **What**: MCP tools for agent access
- **Who Registers**: Services (via `register_mcp_tool()`)
- **Service Mesh Impact**: Service mesh handles tool invocation routing

#### 5. **Agent Capabilities** (What agents can do)
- **Registry**: `AgentCapabilityRegistryService`
- **What**: Agent capabilities, specializations, health
- **Who Registers**: Agents (via `register_agent_capabilities()`)
- **Service Mesh Impact**: Service mesh handles agent-to-service communication

---

## Recommended Curator Architecture

### Core Registries (Curator Owns)

```
Curator Foundation
├── Service Registry (instances + metadata)
├── Capability Registry (what services can do)
├── SOA API Registry (realm-to-realm APIs)
├── MCP Tool Registry (agent-to-service tools)
└── Agent Capability Registry (what agents can do)
```

### Reference Registries (Curator References, Doesn't Own)

```
Curator Foundation
├── References: Specialization Registry (Agentic Foundation)
├── References: AGUI Schema Registry (Agentic Foundation)
└── Uses: Service Discovery Registry (Public Works Foundation)
```

### Infrastructure Registries (Not Curator's Concern)

```
Public Works Foundation
├── Service Discovery Registry (Consul/Istio/Linkerd)
├── Communication Registry (communication infrastructure)
└── Infrastructure Registries (abstractions exposure)
```

---

## Service Mesh Evolution Strategy

### Current State (Consul)

```
Service → Curator → Public Works → Consul
```

- Services register with Curator
- Curator registers with Consul (via Public Works)
- Consul handles service discovery

### Future State (Consul Connect)

```
Service → Curator → Public Works → Consul Connect
                                    ↓
                            Service Mesh (mTLS, routing, policies)
```

**Changes Required**:
1. **Service Registration**: Same (Curator still central hub)
2. **Service Discovery**: Enhanced (Consul Connect provides service mesh features)
3. **API Routing**: Service mesh handles routing (Curator provides endpoint registry)
4. **Security**: Service mesh handles mTLS (Curator provides capability metadata)
5. **Policies**: Service mesh enforces policies (Curator provides capability definitions)

**Key Insight**: Curator remains the **capability registry**, service mesh becomes the **execution layer**.

---

## Registration Flow Consolidation

### Current Problem: 3 Registration Paths

1. **City Manager Path**: `register_service()` → validates → converts → registers capabilities
2. **Direct Service Path**: `register_soa_api()` + `register_mcp_tool()` + `register_capability()`
3. **Agent Path**: `register_agent_capabilities()`

### Recommended: Unified Registration Flow

```
Service Initialization
  ├─> register_service() [REQUIRED]
  │    ├─> Validates service metadata
  │    ├─> Registers service instance
  │    └─> Registers service capabilities
  │
  ├─> register_soa_apis() [OPTIONAL - if service exposes SOA APIs]
  │    └─> Registers each SOA API endpoint
  │
  └─> register_mcp_tools() [OPTIONAL - if service exposes MCP tools]
       └─> Registers each MCP tool
```

**Benefits**:
- Single entry point (`register_service()`)
- Clear separation: service vs APIs vs tools
- Consistent validation
- Service mesh ready (all metadata in one place)

---

## Implementation Recommendations

### Phase 1: Consolidate Service Registration

**Goal**: Single registration path for all services

**Changes**:
1. Make `register_service()` the **only** way to register services
2. Remove direct `register_capability()` calls from services
3. Update `register_service()` to handle:
   - Service instance registration
   - Capability registration (from service metadata)
   - SOA API registration (from service metadata)
   - MCP tool registration (from service metadata)

**Service Metadata Format**:
```python
{
    "service_name": "NurseService",
    "service_type": "health_monitor",
    "realm": "smart_city",
    "capabilities": ["health_monitoring", "telemetry_collection"],
    "soa_apis": {
        "get_health_metrics": {
            "endpoint": "/api/v1/nurse/get_health_metrics",
            "method": "POST",
            "handler": self.get_health_metrics
        }
    },
    "mcp_tools": {
        "monitor_health": {
            "name": "monitor_health",
            "description": "Monitor service health",
            "handler": self._mcp_monitor_health
        }
    }
}
```

### Phase 2: Update Validation

**Goal**: Validate input format, not converted format

**Changes**:
1. Validate service metadata **before** format conversion
2. Make validation flexible (accept multiple formats)
3. Normalize internally to standard format
4. Remove validation of converted format (we control it)

### Phase 3: Service Mesh Preparation

**Goal**: Prepare for Consul Connect

**Changes**:
1. Add service mesh metadata to service registration:
   ```python
   {
       "service_mesh": {
           "connect_enabled": True,
           "intentions": [...],  # Service mesh policies
           "upstreams": [...],    # Service dependencies
           "downstreams": [...]   # Services that depend on this
       }
   }
   ```
2. Register service mesh policies with Curator
3. Update Public Works to support Consul Connect adapter

### Phase 4: Domain Registry Integration

**Goal**: Reference domain registries without owning them

**Changes**:
1. Curator registers that Agentic Foundation provides:
   - Specialization management capability
   - AGUI schema management capability
2. Curator references (doesn't duplicate) domain registries
3. Domain registries remain in their foundations

---

## MECE Coverage Matrix

| Capability Type | Registry | Curator Owns? | Service Mesh Impact |
|----------------|----------|---------------|-------------------|
| **Service Instances** | Service Registry | ✅ Yes | Consul Connect handles routing |
| **Service Capabilities** | Capability Registry | ✅ Yes | Metadata for service mesh policies |
| **SOA API Endpoints** | SOA API Registry | ✅ Yes | Service mesh handles API routing |
| **MCP Tools** | MCP Tool Registry | ✅ Yes | Service mesh handles tool invocation |
| **Agent Capabilities** | Agent Capability Registry | ✅ Yes | Metadata for agent routing |
| **Service Discovery** | Service Discovery Registry | ❌ No | Infrastructure (Public Works) |
| **Communication Infrastructure** | Communication Registry | ❌ No | Infrastructure (Communication Foundation) |
| **Agent Specializations** | Specialization Registry | ⚠️ Reference | Domain knowledge (Agentic Foundation) |
| **AGUI Schemas** | AGUI Schema Registry | ⚠️ Reference | Domain knowledge (Agentic Foundation) |
| **Infrastructure Abstractions** | Infrastructure Registries | ❌ No | Infrastructure (Public Works) |

---

## Questions for Review

1. **Service Registration Consolidation**: Should we consolidate all registration into `register_service()`, or keep separate methods for SOA APIs and MCP tools?

2. **Domain Registries**: Should Curator own Specialization and AGUI registries, or just reference them?

3. **Service Mesh Metadata**: Should service mesh policies (intentions, upstreams, downstreams) be registered with Curator, or managed separately?

4. **Validation Timing**: Should we validate input format, converted format, or both?

5. **Backward Compatibility**: How do we handle services that currently call `register_capability()` directly?

---

## Next Steps

1. ✅ **Review this design** - Confirm MECE structure
2. ⚠️ **Decide on registration consolidation** - Single path vs multiple paths
3. ⚠️ **Update validation** - Validate input format, normalize internally
4. ⚠️ **Service mesh preparation** - Add metadata structures
5. ⚠️ **Domain registry integration** - Reference vs own decision

---

**Last Updated**: December 2024

