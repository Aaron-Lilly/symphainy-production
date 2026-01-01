# Smart City Phase 2 Pattern Migration - Summary

**Date:** November 21, 2025  
**Status:** ✅ In Progress

---

## Overview

Migrating Smart City services to Phase 2 capability-based registration pattern (simplified for platform enablers).

---

## Completed Services

### ✅ 1. Librarian Service
- **File**: `backend/smart_city/services/librarian/modules/soa_mcp.py`
- **Status**: Migrated to `register_with_curator()`
- **Capabilities**: 
  - `knowledge_management` (SOA API + MCP Tool)
  - `content_organization` (SOA API + MCP Tool)

### ✅ 2. Security Guard Service
- **File**: `backend/smart_city/services/security_guard/modules/soa_mcp.py`
- **Status**: Migrated to `register_with_curator()`
- **Capabilities**:
  - `authentication` (SOA API + MCP Tool)
  - `authorization` (SOA API + MCP Tool)
  - `zero_trust_policy` (SOA API + MCP Tool)

### ✅ 3. City Manager Service
- **File**: `backend/smart_city/services/city_manager/modules/soa_mcp.py`
- **Status**: Migrated to `register_with_curator()`
- **Capabilities**:
  - `platform_orchestration` (SOA API + MCP Tool)
- **Note**: City Manager no longer registers other Smart City services - they self-register

---

## Remaining Services (Template Pattern)

The following services need to be migrated using the same pattern:

### 4. Traffic Cop Service
- **File**: `backend/smart_city/services/traffic_cop/modules/soa_mcp.py`
- **Pattern**: Same as Security Guard

### 5. Nurse Service
- **File**: `backend/smart_city/services/nurse/modules/soa_mcp.py`
- **Pattern**: Same as Security Guard

### 6. Data Steward Service
- **File**: `backend/smart_city/services/data_steward/modules/soa_mcp.py`
- **Pattern**: Same as Librarian

### 7. Content Steward Service
- **File**: `backend/smart_city/services/content_steward/modules/soa_mcp.py`
- **Pattern**: Same as Librarian

### 8. Post Office Service
- **File**: `backend/smart_city/services/post_office/modules/soa_mcp.py`
- **Pattern**: Same as Security Guard

### 9. Conductor Service
- **File**: `backend/smart_city/services/conductor/modules/soa_mcp.py`
- **Pattern**: Same as Security Guard

---

## Migration Pattern Template

### Step 1: Update `register_capabilities()` in `soa_mcp.py`

Replace the old pattern (direct `CapabilityDefinition` registration) with:

```python
async def register_capabilities(self) -> Dict[str, Any]:
    """Register {ServiceName} capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
    try:
        # Build capabilities list with SOA API and MCP Tool contracts
        capabilities = []
        
        # Create capability 1 (combines related SOA APIs and MCP tools)
        capabilities.append({
            "name": "capability_name",
            "protocol": "{ServiceName}ServiceProtocol",
            "description": "Description of capability",
            "contracts": {
                "soa_api": {
                    "api_name": "primary_soa_api_name",
                    "endpoint": self.service.soa_apis.get("primary_soa_api_name", {}).get("endpoint", "/soa/{service}/{api}"),
                    "method": self.service.soa_apis.get("primary_soa_api_name", {}).get("method", "POST"),
                    "handler": getattr(self.service, "primary_soa_api_name", None),
                    "metadata": {
                        "description": "Description",
                        "apis": ["api1", "api2"]  # All related APIs
                    }
                },
                "mcp_tool": {
                    "tool_name": "{service}_{tool_name}",
                    "mcp_server": "smart_city_mcp_server",
                    "tool_definition": {
                        "name": "{service}_{tool_name}",
                        "description": "Description",
                        "input_schema": {}
                    }
                }
            }
        })
        
        # Add more capabilities as needed...
        
        # Register using register_with_curator (simplified Phase 2 pattern)
        soa_api_names = list(self.service.soa_apis.keys())
        mcp_tool_names = [f"{service_prefix}_{tool}" for tool in self.service.mcp_tools.keys()]
        
        success = await self.service.register_with_curator(
            capabilities=capabilities,
            soa_apis=soa_api_names,
            mcp_tools=mcp_tool_names,
            protocols=[{
                "name": "{ServiceName}ServiceProtocol",
                "definition": {
                    "methods": {api: {"input_schema": {}, "output_schema": {}} for api in soa_api_names}
                }
            }]
        )
        
        if success:
            if self.service.logger:
                self.service.logger.info(f"✅ {ServiceName} registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
        else:
            if self.service.logger:
                self.service.logger.warning(f"⚠️ Failed to register {ServiceName} with Curator")
                
    except Exception as e:
        if self.service.logger:
            self.service.logger.error(f"❌ Failed to register {ServiceName} capabilities: {e}")
            import traceback
            self.service.logger.error(f"Traceback: {traceback.format_exc()}")
    
    return {}
```

### Step 2: Update Service Initialization

In the service's `initialize()` method, replace:

```python
# OLD:
capabilities = await self.soa_mcp_module.register_capabilities()
await self.register_capability("ServiceName", capabilities)

# NEW:
await self.soa_mcp_module.register_capabilities()
```

---

## Key Differences from Public-Facing Realms

1. **No Semantic Mapping**: Smart City services don't have user-facing semantic APIs
2. **No REST API Contracts**: Smart City services don't expose REST APIs to end users
3. **SOA API + MCP Tool Focus**: Primary contracts are SOA API (realm consumption) and MCP Tool (agent access)
4. **Optional Service Mesh Policies**: Can be added later for Consul Connect evolution

---

## Benefits

1. **Consistency**: All services use same `register_with_curator()` pattern
2. **Discovery**: Smart City capabilities discoverable via Curator
3. **SOA API Registration**: SOA APIs registered for realm discovery
4. **MCP Tool Registration**: MCP tools registered for agent access
5. **Simplified**: No unnecessary semantic mapping or REST API contracts
6. **Future-Proof**: Can add service mesh policies later

---

## Next Steps

1. Migrate remaining 6 services using the template pattern
2. Test Smart City service registration and discovery
3. Verify SOA API discovery works
4. Verify MCP tool discovery works
5. Update documentation




