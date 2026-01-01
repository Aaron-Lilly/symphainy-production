# Migration Notes: Security Guard Old Server

## Date: 2024-01-15
## Reason: Replaced by SOA + MCPBaseServer architecture

## What Was Moved
- Source: `backend/smart_city/security_guard/server/`
- Destination: `_archived/old_smart_city_roles/security_guard_old_server/`
- Reason: Replaced by new SOA service implementation

## What Replaced It
- New implementation: `backend/smart_city/security_guard/service/`
- Key improvements:
  - Uses ServiceBase architecture
  - HTTP APIs with FastAPI
  - User context integration
  - Registry capability reporting
  - Enhanced security service integration
- Architecture: SOA + lightweight MCP + capability reporting

## Breaking Changes
- Old server implementation no longer used
- New service uses different base classes
- User context required for all operations
- Registry integration mandatory

## Migration Guide
1. Use new service implementation: `backend/smart_city/security_guard/service/security_guard_service.py`
2. Use new MCP server: `backend/smart_city/security_guard/mcp_server/security_guard_mcp_server.py`
3. All operations now require user context
4. Service automatically reports capabilities to Registry

## Rollback Instructions
1. Move this folder back to `backend/smart_city/security_guard/server/`
2. Update imports to use old implementation
3. Note: Old implementation lacks user context and registry integration

## Files Archived
- `security_guard_server.py` - Old server implementation
- `simple_test_security_guard.py` - Old test file
- `test_security_guard_server.py` - Old test file
- `base/` - Old base classes
- `integrations/` - Old integration patterns
- `prompts/` - Old MCP prompts
- `resources/` - Old MCP resources
- `tools/` - Old tool implementations









