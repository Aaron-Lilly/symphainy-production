# MCP Server execute_tool Override Analysis

**Date:** 2025-12-05  
**Purpose:** Identify which MCP servers don't override `execute_tool` and whether they have the same `**kwargs` handler issue

## Summary

**Active MCP Servers WITHOUT `execute_tool` Override:**
1. ✅ **WaveMCPServer** - Uses `**kwargs` handlers (SAME ISSUE)
2. ✅ **PolicyTrackerMCPServer** - Uses `**kwargs` handlers (SAME ISSUE)
3. ⚠️ **SmartCityMCPServer** - Dynamically registers tools (needs investigation)

## Detailed Analysis

### 1. WaveMCPServer
**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/wave_orchestrator/mcp_server/wave_mcp_server.py`

**Status:** ❌ No `execute_tool` override

**Handler Pattern:** All handlers use `**kwargs`:
```python
async def _create_wave_tool(self, **kwargs) -> Dict[str, Any]:
async def _select_wave_candidates_tool(self, **kwargs) -> Dict[str, Any]:
async def _execute_wave_tool(self, **kwargs) -> Dict[str, Any]:
async def _rollback_wave_tool(self, **kwargs) -> Dict[str, Any]:
async def _get_wave_status_tool(self, **kwargs) -> Dict[str, Any]:
```

**Issue:** Same as InsuranceMigrationMCPServer - handlers expect `**kwargs` but base class `execute_tool` calls them incorrectly.

**Impact:** Will fail when declarative agents try to execute tools via this MCP server.

---

### 2. PolicyTrackerMCPServer
**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/policy_tracker_orchestrator/mcp_server/policy_tracker_mcp_server.py`

**Status:** ❌ No `execute_tool` override

**Handler Pattern:** All handlers use `**kwargs`:
```python
async def _register_policy_tool(self, **kwargs) -> Dict[str, Any]:
async def _update_migration_status_tool(self, **kwargs) -> Dict[str, Any]:
async def _get_policy_location_tool(self, **kwargs) -> Dict[str, Any]:
async def _validate_migration_tool(self, **kwargs) -> Dict[str, Any]:
async def _reconcile_systems_tool(self, **kwargs) -> Dict[str, Any]:
async def _get_policies_by_location_tool(self, **kwargs) -> Dict[str, Any]:
```

**Issue:** Same as InsuranceMigrationMCPServer - handlers expect `**kwargs` but base class `execute_tool` calls them incorrectly.

**Impact:** Will fail when declarative agents try to execute tools via this MCP server.

---

### 3. SmartCityMCPServer
**Location:** `backend/smart_city/mcp_server/smart_city_mcp_server.py`

**Status:** ❌ No `execute_tool` override

**Handler Pattern:** Tools are dynamically registered from Smart City services via Curator discovery. Handler signatures need investigation.

**Issue:** Unknown - needs investigation of how handlers are registered and their signatures.

**Impact:** Unknown until handlers are examined.

---

## MCP Servers WITH `execute_tool` Override (Working Correctly)

These servers already override `execute_tool` and handle `**kwargs` correctly:

1. ✅ **InsuranceMigrationMCPServer** - Fixed (uses pattern: `handler(**parameters, user_context=user_context)`)
2. ✅ **OperationsMCPServer** - Uses pattern: `handler(**parameters, user_context=user_context)`
3. ✅ **BusinessOutcomesMCPServer** - Uses pattern: `handler(**parameters, user_context=user_context)`
4. ✅ **ContentAnalysisMCPServer** - Adds user_context to parameters, then calls `handler(**parameters)`
5. ✅ **InsightsMCPServer** - Adds user_context to parameters, then calls `handler(**parameters)`
6. ✅ **DeliveryManagerMCPServer** - Uses pattern: `handler(**parameters, user_context=user_context)`
7. ✅ **JourneyManagerMCPServer** - Has override (needs signature check)
8. ✅ **SolutionManagerMCPServer** - Has override (needs signature check)

## Recommended Fix Pattern

All MCP servers with `**kwargs` handlers should override `execute_tool` using this pattern:

```python
async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
    """
    Execute tool by routing to orchestrator.
    
    Includes full utility usage:
    - Telemetry tracking
    - Security validation (zero-trust)
    - Tenant validation (multi-tenancy)
    - Error handling with audit
    - Health metrics
    """
    # Start telemetry tracking
    if self.utilities.telemetry:
        try:
            await self.utilities.telemetry.collect_metric({
                "name": "execute_tool_start",
                "value": 1.0,
                "type": "counter",
                "labels": {"tool_name": tool_name, "mcp_server": self.service_name}
            })
        except Exception:
            pass  # Telemetry is optional
    
    # Security validation (zero-trust: secure by design)
    if user_context:
        security = self.utilities.security
        if security:
            if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                raise PermissionError(f"Access denied: insufficient permissions to execute tool '{tool_name}'")
    
    # Tenant validation (multi-tenancy support)
    if user_context:
        tenant = self.utilities.tenant
        if tenant:
            tenant_id = user_context.get("tenant_id") if isinstance(user_context, dict) else getattr(user_context, "tenant_id", None)
            if tenant_id:
                if not tenant.validate_tenant_access(tenant_id, tenant_id):
                    raise PermissionError(f"Tenant access denied for tool '{tool_name}': {tenant_id}")
    
    # Map tool names to handlers
    tool_handlers = {
        "tool1": self._tool1_handler,
        "tool2": self._tool2_handler,
        # ... etc
    }
    
    handler = tool_handlers.get(tool_name)
    if handler:
        # Add user_context to parameters if not present (for handlers that use **kwargs)
        if user_context and "user_context" not in parameters:
            parameters["user_context"] = user_context
        
        # Call handler with **parameters (handlers use **kwargs)
        result = await handler(**parameters)
        
        # End telemetry tracking
        if self.utilities.telemetry:
            try:
                await self.utilities.telemetry.collect_metric({
                    "name": "execute_tool_complete",
                    "value": 1.0,
                    "type": "counter",
                    "labels": {"tool_name": tool_name, "status": "success" if result.get("success", True) else "failed"}
                })
            except Exception:
                pass
        
        return result
    else:
        # Record health metric (tool not found)
        if self.utilities.health:
            try:
                await self.utilities.health.record_metric("execute_tool_not_found", 1.0, {"tool_name": tool_name})
            except Exception:
                pass
        
        return {"error": f"Unknown tool: {tool_name}"}
```

## Action Items

1. ✅ **InsuranceMigrationMCPServer** - Fixed
2. ✅ **WaveMCPServer** - Fixed (added `execute_tool` override with **kwargs pattern)
3. ✅ **PolicyTrackerMCPServer** - Fixed (added `execute_tool` override with **kwargs pattern)
4. ✅ **SmartCityMCPServer** - Fixed (added `execute_tool` override with (parameters, user_context) pattern)
5. ✅ **MCPServerBase** - Made `execute_tool` abstract (enforces pattern for all future MCP servers)

## Implementation Complete

All active MCP servers now override `execute_tool` with the correct pattern:
- **WaveMCPServer & PolicyTrackerMCPServer**: Use `handler(**parameters)` pattern (handlers use **kwargs)
- **SmartCityMCPServer**: Uses `handler(parameters, user_context)` pattern (handlers have different signature)
- **Base Class**: `execute_tool` is now abstract, enforcing the pattern for all future MCP servers

## Benefits

1. ✅ **Pattern Enforcement**: Abstract method ensures all MCP servers implement the correct pattern
2. ✅ **No Broken Fallbacks**: Removed the broken base class implementation
3. ✅ **Ready for Agent Migration**: All MCP servers are ready for declarative agent migration
4. ✅ **Consistent Security**: All servers implement security/tenant validation
5. ✅ **Consistent Telemetry**: All servers implement telemetry tracking

