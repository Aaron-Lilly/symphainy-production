# MCP Servers Base Migration Plan

**Date:** December 2024  
**Status:** 🚀 **IN PROGRESS**  
**Goal:** Migrate all MCP servers from OLD base to NEW base for proper utility integration

---

## 🎯 Decision: Use NEW Base

**Recommended Base:** `bases/mcp_server/mcp_server_base.py` (NEW)

**Why:**
- ✅ Built-in utility integration (`self.utilities.*`)
- ✅ Telemetry emission (`self.telemetry_emission`)
- ✅ Health monitoring (`self.health_monitoring`)
- ✅ Tool registry (`self.tool_registry`)
- ✅ Micro-module architecture
- ✅ Matches refactored code patterns

---

## 📋 Migration Changes Required

### 1. Import Change
**Before:**
```python
from bases.mcp_server_base import MCPServerBase
```

**After:**
```python
from bases.mcp_server.mcp_server_base import MCPServerBase
```

### 2. `__init__` Change
**Before:**
```python
super().__init__(
    server_name="server_name",
    di_container=di_container,
    server_type="single_orchestrator"
)
```

**After:**
```python
super().__init__(
    service_name="server_name",
    di_container=di_container
)
```

### 3. Tool Registration Method
**Before:**
```python
def _register_tools(self):
    self.register_tool(
        name="tool_name",
        description="...",
        handler=self._tool_handler,
        input_schema={...}
    )
```

**After:**
```python
def register_server_tools(self) -> None:
    self.register_tool(
        tool_name="tool_name",
        handler=self._tool_handler,
        input_schema={...},
        description="..."
    )
```

### 4. Required Abstract Methods
Must implement:
- `get_usage_guide() -> Dict[str, Any]`
- `get_tool_list() -> List[str]`
- `async get_health_status() -> Dict[str, Any]`
- `get_version_info() -> Dict[str, Any]`

### 5. `execute_tool()` Override
Keep custom `execute_tool()` with utility usage, but ensure signature compatibility.

---

## 🔄 Migration Steps

1. Update import statement
2. Update `__init__` call
3. Rename `_register_tools()` to `register_server_tools()`
4. Update all `register_tool()` calls (change `name=` to `tool_name=`)
5. Implement abstract methods
6. Test functionality

---

**Status:** Starting migration...





