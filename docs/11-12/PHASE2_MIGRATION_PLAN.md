# Phase 2 Migration Plan: Legacy Registration Methods

## Overview

This document outlines the migration plan for updating all services to use the new Phase 2 registration pattern. The legacy methods have been replaced with proper implementations that use the new pattern while maintaining backward compatibility during migration.

## Status

✅ **Legacy methods replaced with proper implementations** (completed)
- All legacy methods now delegate to new pattern
- Backward compatibility maintained during migration
- Old in-memory registries maintained for compatibility

🔄 **Migration in progress**
- Services need to be updated to use new pattern directly
- Old method calls will continue to work but should be migrated

## Legacy Methods Replaced

### 1. `register_agent_with_curator()` → `register_agent()`

**Old Pattern:**
```python
await curator.register_agent_with_curator(
    agent_id="agent_123",
    agent_name="Content Analyst",
    agent_config={
        "capabilities": [...],
        "pillar": "content",
        "specialization": "content_analysis",
        "specialization_config": {...},
        "mcp_tools": [...],
        "agent_api": {...}
    },
    user_context=user_context
)
```

**New Pattern:**
```python
await curator.register_agent(
    agent_id="agent_123",
    agent_name="Content Analyst",
    characteristics={
        "capabilities": [...],
        "pillar": "content",
        "specialization": "content_analysis",
        "required_roles": [...],
        "agui_schema": {...}
    },
    contracts={
        "mcp_tools": [...],
        "agent_api": {...}
    },
    user_context=user_context
)
```

**Migration Steps:**
1. Extract `capabilities`, `pillar`, `specialization` from `agent_config` → `characteristics`
2. Extract `specialization_config.required_roles` and `specialization_config.agui_schema` → `characteristics`
3. Extract `mcp_tools` and `agent_api` from `agent_config` → `contracts`
4. Call `register_agent()` with new format

---

### 2. `register_capability()` (dict-based) → `register_domain_capability()`

**Old Pattern:**
```python
await curator.register_capability(
    capability_definition={
        "service_name": "file_parser",
        "interface_name": "IFileParser",
        "endpoints": ["/api/v1/parse"],
        "tools": ["parse_file_tool"],
        "description": "Parse files",
        "realm": "smart_city",
        "version": "1.0.0"
    },
    user_context=user_context
)
```

**New Pattern:**
```python
from foundations.curator_foundation.models.capability_definition import CapabilityDefinition

capability = CapabilityDefinition(
    service_name="file_parser",
    interface_name="IFileParser",
    endpoints=["/api/v1/parse"],
    tools=["parse_file_tool"],
    description="Parse files",
    realm="smart_city",
    version="1.0.0",
    semantic_mapping={
        "domain_capability": "content.parse_file",
        "semantic_api": "/api/v1/content-pillar/parse-file"
    },
    contracts={
        "soa_api": {...},
        "mcp_tool": {...},
        "rest_api": {...}
    }
)

await curator.register_domain_capability(capability, user_context)
```

**Migration Steps:**
1. Import `CapabilityDefinition` from `foundations.curator_foundation.models.capability_definition`
2. Convert dict to `CapabilityDefinition` object
3. Add `semantic_mapping` if available (domain capability → semantic API mapping)
4. Add `contracts` if available (SOA API, MCP tool, REST API contracts)
5. Call `register_domain_capability()` with `CapabilityDefinition` object

---

### 3. `register_soa_api()` → `register_domain_capability()` with contracts

**Old Pattern:**
```python
await curator.register_soa_api(
    service_name="file_parser",
    api_name="parse_file",
    endpoint="/api/v1/parse",
    handler=parse_file_handler,
    metadata={"method": "POST"},
    user_context=user_context
)
```

**New Pattern:**
```python
from foundations.curator_foundation.models.capability_definition import CapabilityDefinition

capability = CapabilityDefinition(
    service_name="file_parser",
    interface_name="IFileParser",
    endpoints=["/api/v1/parse"],
    tools=[],
    description="SOA API: parse_file",
    realm="smart_city",
    version="1.0.0",
    semantic_mapping=None,
    contracts={
        "soa_api": {
            "api_name": "parse_file",
            "endpoint": "/api/v1/parse",
            "handler": parse_file_handler,
            "metadata": {"method": "POST"}
        }
    }
)

await curator.register_domain_capability(capability, user_context)
```

**Migration Steps:**
1. Create `CapabilityDefinition` with SOA API info
2. Put SOA API details in `contracts["soa_api"]`
3. Call `register_domain_capability()` with `CapabilityDefinition` object

---

### 4. `register_mcp_tool()` → `register_domain_capability()` with contracts

**Old Pattern:**
```python
await curator.register_mcp_tool(
    tool_name="parse_file_tool",
    tool_definition={
        "name": "parse_file",
        "description": "Parse files",
        "endpoint": "/mcp/parse_file",
        "handler": parse_file_handler
    },
    metadata={
        "service_name": "file_parser",
        "tool_name": "parse_file_tool"
    },
    user_context=user_context
)
```

**New Pattern:**
```python
from foundations.curator_foundation.models.capability_definition import CapabilityDefinition

capability = CapabilityDefinition(
    service_name="file_parser",
    interface_name="IFileParser",
    endpoints=["/mcp/parse_file"],
    tools=["parse_file_tool"],
    description="MCP Tool: parse_file_tool",
    realm="agentic",
    version="1.0.0",
    semantic_mapping=None,
    contracts={
        "mcp_tool": {
            "tool_name": "parse_file_tool",
            "tool_definition": {
                "name": "parse_file",
                "description": "Parse files",
                "endpoint": "/mcp/parse_file",
                "handler": parse_file_handler
            },
            "metadata": {
                "service_name": "file_parser",
                "tool_name": "parse_file_tool"
            }
        }
    }
)

await curator.register_domain_capability(capability, user_context)
```

**Migration Steps:**
1. Create `CapabilityDefinition` with MCP tool info
2. Put MCP tool details in `contracts["mcp_tool"]`
3. Call `register_domain_capability()` with `CapabilityDefinition` object

---

## Unified Registration Pattern (Recommended)

The best approach is to use `RealmServiceBase.register_with_curator()` which provides a unified registration flow:

```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "file_parsing",
            "protocol": "IFileParser",
            "description": "Parse files into structured formats",
            "semantic_mapping": {
                "domain_capability": "content.upload_file",
                "semantic_api": "/api/v1/content-pillar/upload-file"
            },
            "contracts": {
                "soa_api": {
                    "api_name": "parse_file",
                    "endpoint": "/api/v1/parse",
                    "method": "POST"
                },
                "mcp_tool": {
                    "tool_name": "parse_file_tool",
                    "tool_definition": {...}
                },
                "rest_api": {
                    "endpoint": "/api/v1/content-pillar/upload-file",
                    "method": "POST"
                }
            }
        }
    ],
    soa_apis=["parse_file", "detect_file_type"],
    mcp_tools=["parse_file_tool", "detect_file_type_tool"],
    protocols=[{
        "name": "IFileParser",
        "definition": {"methods": {...}}
    }],
    routing_metadata={
        "policies": {
            "load_balancing": "round_robin",
            "timeout": "30s"
        }
    }
)
```

This unified method:
- Registers capabilities with `CapabilityDefinition`
- Registers service protocols
- Registers routes in endpoint registry
- Reports service mesh policies
- Registers with service discovery

---

## Migration Strategy

### Phase 1: Identify All Callers

Find all usages of legacy methods:
```bash
grep -r "register_agent_with_curator" --include="*.py"
grep -r "register_capability(" --include="*.py"
grep -r "register_soa_api" --include="*.py"
grep -r "register_mcp_tool" --include="*.py"
```

### Phase 2: Update Service Registration

For each service:
1. Update `register_capabilities()` method in `soa_mcp.py` modules
2. Replace legacy method calls with new pattern
3. Use `RealmServiceBase.register_with_curator()` when possible
4. Test registration still works

### Phase 3: Remove Backward Compatibility

Once all callers are migrated:
1. Remove backward compatibility code from legacy methods
2. Remove old in-memory registries (`soa_api_registry`, `mcp_tool_registry`)
3. Remove legacy methods entirely
4. Update documentation

---

## Files to Update

### Smart City Services
- `backend/smart_city/services/*/modules/soa_mcp.py` - All services
- `backend/smart_city/services/*/modules/*_service.py` - Service registration

### Foundation Services
- `foundations/agentic_foundation/agent_sdk/agent_base.py` - Agent registration
- `foundations/communication_foundation/communication_foundation_service.py` - Communication registration

### Test Files
- `tests/integration/foundations/test_*.py` - Update test registration calls

---

## Testing

After migration:
1. Run integration tests to verify registration works
2. Verify capabilities are discoverable via Curator
3. Verify routes are registered in endpoint registry
4. Verify service mesh policies are reported
5. Verify backward compatibility still works (during migration)

---

## Timeline

- ✅ **Week 1**: Replace legacy methods with proper implementations
- 🔄 **Week 2**: Migrate all service registration calls
- 📅 **Week 3**: Remove backward compatibility code
- 📅 **Week 4**: Final testing and documentation

---

## Questions?

See:
- `docs/11-12/CURATOR_CENTRAL_HUB_DESIGN.md` - Curator architecture
- `docs/11-12/ROUTING_OWNERSHIP_STRATEGY.md` - Routing strategy
- `docs/11-12/PHASE2_APPROACH_ALIGNMENT.md` - Phase 2 alignment







