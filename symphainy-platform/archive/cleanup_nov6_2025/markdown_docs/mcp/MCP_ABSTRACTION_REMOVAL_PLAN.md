# MCP Abstraction Removal Plan

## Strategic Decision

**MCP is a protocol standard** (like HTTP), not swappable infrastructure. We should use direct injection via DI Container instead of abstracting it.

## Current Architecture (WRONG)

```
Service → MCPCompositionService → MCPAbstraction → MCPAdapter → Real MCP Client
```

This is unnecessary abstraction of a protocol standard.

## Target Architecture (CORRECT)

```
Service → ClientSession (Direct Injection via DI)
```

Use MCP directly, like we use HTTP directly.

## Files to Modify

### 1. Remove MCP Abstraction Layer
- **DELETE**: `infrastructure_abstractions/mcp_abstraction.py`
- **DELETE**: `infrastructure_adapters/mcp_adapter.py` (partially done)
- **DELETE**: `composition_services/mcp_composition_service.py`

### 2. Update Public Works Foundation
**File**: `public_works_foundation_service.py`
**Lines**: 290-304

**Current**:
```python
# Create MCP adapter
mcp_adapter = MCPAdapter()
# Create MCP abstraction
self.mcp_abstraction = MCPAbstraction(mcp_adapter)
# Create MCP composition service
self.mcp_composition_service = MCPCompositionService(self.mcp_abstraction)
```

**Replace with**:
```python
# Import MCP client directly
from mcp import ClientSession
# Register MCP client factory in DI container
# MCP client will be injected directly into services that need it
```

### 3. Update DI Container Registration

**File**: `di_container_service.py`

**Add to `initialize_container()`**:
```python
# MCP Client - Direct injection (non-swappable protocol)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def create_mcp_client(server_name: str = "default"):
    """Factory for creating MCP clients."""
    # Configure client based on server_name
    config = await self.get_mcp_config(server_name)
    return ClientSession(**config)

# Register factory
self.register("mcp_client_factory", create_mcp_client)
```

### 4. Update Services to Inject MCP Client Directly

Instead of:
```python
def __init__(self, mcp_composition_service: MCPCompositionService):
    self.mcp_service = mcp_composition_service
```

Use:
```python
def __init__(self, mcp_client: ClientSession):
    self.mcp_client = mcp_client
```

## Benefits

1. **Simpler Architecture** - No unnecessary abstractions
2. **Better Performance** - Direct usage, no wrapper overhead
3. **Clearer Intent** - Use MCP as a protocol standard, not as infrastructure
4. **Easier Testing** - Mock ClientSession directly
5. **Protocol Compliance** - Use MCP as intended by the spec

## Implementation Steps

1. ✅ Update DI Container to register MCP client factory
2. ✅ Remove MCP abstraction classes
3. ✅ Update Public Works Foundation to use direct injection
4. ✅ Update any services using MCPCompositionService to inject ClientSession
5. ✅ Test simplified architecture

## Impact Analysis

**Services Currently Using MCP**:
- None detected in Smart City services (good!)
- Only used in Public Works Foundation initialization
- Easy to remove without breaking changes

**Breaking Changes**:
- None - MCP was never actually used by business services
- Only in foundation initialization

This is a **safe refactoring** that simplifies architecture without breaking functionality.
