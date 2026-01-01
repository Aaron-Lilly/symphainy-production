# MCP Servers Refactoring Plan

**Date:** December 2024  
**Status:** 🚀 **IN PROGRESS**  
**Goal:** Refactor all 5 MCP Servers to use full utility patterns and Phase 2 Curator registration

---

## 📊 MCP Servers Inventory

### Status Overview
1. ✅ **content_analysis_mcp_server** - **ALREADY REFACTORED** (Reference implementation)
2. ⏳ **insights_mcp_server** - Needs utility usage updates
3. ⏳ **operations_mcp_server** - Needs utility usage updates
4. ⏳ **business_outcomes_mcp_server** - Needs utility usage updates
5. ⏳ **delivery_manager_mcp_server** - Needs full refactoring (uses old MCPBaseServer)

---

## 🎯 Refactoring Goals

### 1. Utility Usage Pattern
All MCP Servers must use:
- ✅ Telemetry tracking (`self.utilities.telemetry`)
- ✅ Security validation (`self.utilities.security`)
- ✅ Tenant validation (`self.utilities.tenant`)
- ✅ Error handling (`self.utilities.error_handler`)
- ✅ Health metrics (`self.utilities.health`)

### 2. Tool Execution Pattern
All `execute_tool()` and individual tool methods must:
- Start telemetry tracking
- Validate security (if `user_context` provided)
- Validate tenant (if `user_context` provided)
- Execute tool logic
- Record health metrics
- End telemetry tracking
- Handle errors with audit

### 3. User Context Pattern
All tool methods must:
- Accept `user_context: Optional[Dict[str, Any]] = None`
- Use `Dict[str, Any]` (not `UserContext`)

### 4. Phase 2 Curator Registration
All MCP Servers must:
- Register with Curator using Phase 2 `CapabilityDefinition` pattern
- Include `mcp_tool` contracts in capabilities
- Register tool metadata with Curator

---

## 📋 Reference Implementation

**File:** `content_analysis_mcp_server.py`

**Pattern:**
```python
async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
    """Execute tool with full utility usage."""
    # Start telemetry tracking
    self.telemetry_emission.emit_tool_execution_start_telemetry(tool_name, parameters)
    
    try:
        # Security validation
        if user_context:
            security = self.utilities.security
            if security:
                if not await security.check_permissions(user_context, f"mcp_tool.{tool_name}", "execute"):
                    self.health_monitoring.record_tool_execution_health(tool_name, success=False)
                    self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                    raise PermissionError("Access denied")
        
        # Tenant validation
        if user_context:
            tenant = self.utilities.tenant
            if tenant:
                tenant_id = user_context.get("tenant_id")
                if tenant_id:
                    if not await tenant.validate_tenant_access(tenant_id):
                        self.health_monitoring.record_tool_execution_health(tool_name, success=False)
                        self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
        
        # Execute tool
        handler = tool_handlers.get(tool_name)
        if handler:
            result = await handler(**parameters, user_context=user_context)
            self.health_monitoring.record_tool_execution_health(tool_name, success=True)
            self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=True)
            return result
        else:
            return {"error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        self.utilities.error_handler.handle_error_with_audit(e, f"mcp_tool_execution_{tool_name}", user_context=user_context)
        self.health_monitoring.record_tool_execution_health(tool_name, success=False, details={"error": str(e)})
        self.telemetry_emission.emit_tool_execution_complete_telemetry(tool_name, success=False, details={"error": str(e)})
        return {"error": f"Failed to execute tool {tool_name}: {str(e)}"}
```

---

## 🔄 Refactoring Steps

### Phase 1: Reference Implementation (insights_mcp_server)
1. Review current implementation
2. Add full utility usage to `execute_tool()`
3. Add full utility usage to all tool methods
4. Add `user_context` parameter to all tool methods
5. Test functionality

### Phase 2: Batch Refactor Remaining 3
1. **operations_mcp_server** - Apply same pattern
2. **business_outcomes_mcp_server** - Apply same pattern
3. **delivery_manager_mcp_server** - Full refactoring (migrate from MCPBaseServer to MCPServerBase)

### Phase 3: Testing
1. Test all MCP Servers for utility usage
2. Test tool execution functionality
3. Test error handling
4. Test user context validation

---

## 📝 Files to Refactor

1. `delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/mcp_server/insights_mcp_server.py`
2. `delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/mcp_server/operations_mcp_server.py`
3. `delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/mcp_server/business_outcomes_mcp_server.py`
4. `delivery_manager/mcp_server/delivery_manager_mcp_server.py`

---

## ✅ Success Criteria

- [x] All MCP Servers use MCPServerBase
- [ ] All MCP Servers have full utility usage
- [ ] All tool methods accept `user_context: Optional[Dict[str, Any]]`
- [ ] All tool methods include security validation
- [ ] All tool methods include tenant validation
- [ ] All tool methods include telemetry tracking
- [ ] All tool methods include error handling
- [ ] All tool methods include health metrics
- [ ] All MCP Servers register with Curator (Phase 2)
- [ ] All MCP Servers tested and functional

---

**Status:** 🚀 Starting with insights_mcp_server as reference





