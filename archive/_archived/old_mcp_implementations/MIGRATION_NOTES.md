# Migration Notes: Old MCP Implementations

## Date: 2024-01-15
## Reason: Replaced by BrokerBase/MCPBaseServer architecture

## What Was Moved
- Source: Various `*_mcp.py` files
- Destination: `_archived/old_mcp_implementations/`
- Reason: Replaced by new BrokerBase/MCPBaseServer implementations

## What Replaced Them
- New implementations: `*_mcp.py` (renamed from `*_mcp_v2.py`)
- Key improvements:
  - Uses BrokerBase for brokers
  - Uses MCPBaseServer for MCP servers
  - Consistent base class patterns
  - Better error handling
  - Registry integration
  - User context support
- Architecture: SOA + lightweight MCP + capability reporting

## Files Archived
- `file_broker_mcp.py` - Old file broker MCP implementation
- `database_broker_mcp.py` - Old database broker MCP implementation
- `context_broker_mcp.py` - Old context broker MCP implementation
- `mcp_server.py` - Old public works MCP implementation

## Breaking Changes
- Old MCP implementations no longer used
- New implementations use different base classes
- Registry integration mandatory
- User context support added

## Migration Guide
1. Use new implementations: `*_mcp.py` (renamed from v2)
2. All implementations now use BrokerBase or MCPBaseServer
3. Registry integration is automatic
4. User context support is built-in

## Rollback Instructions
1. Move files back to their original locations
2. Rename v2 files back to v2 suffix
3. Update imports to use old implementations
4. Note: Old implementations lack registry integration and user context

## New Architecture Benefits
- Consistent base class patterns
- Automatic registry integration
- User context support
- Better error handling
- Cleaner code organization
- Easier maintenance









