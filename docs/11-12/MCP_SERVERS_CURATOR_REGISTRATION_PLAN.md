# MCP Servers Curator Registration Plan

**Date:** December 2024  
**Status:** 📋 **PLAN COMPLETE** | 🚀 **READY FOR IMPLEMENTATION**

---

## 🎯 Objective

Add Curator registration to all MCP servers so their MCP Tools are discoverable and trackable by the platform.

---

## 📋 Current Curator Pattern

### CapabilityDefinition Structure (Phase 2)

```python
@dataclass
class CapabilityDefinition:
    capability_name: str  # Unique identifier (e.g., "analyze_document_tool")
    service_name: str  # Which service provides this (e.g., "content_analysis_mcp")
    protocol_name: str  # Protocol class name (e.g., "ContentAnalysisMCPServerProtocol")
    description: str  # What this capability does
    realm: str  # Which realm (e.g., "business_enablement", "smart_city")
    contracts: Dict[str, Any]  # REQUIRED: At least one contract
    semantic_mapping: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
```

### Contract Structure for MCP Tools

```python
contracts = {
    "mcp_tool": {
        "tool_name": "analyze_document_tool",
        "tool_definition": {
            "name": "analyze_document_tool",
            "description": "Analyze document with structure analysis...",
            "input_schema": {...},
            "handler": <function reference>,
            # ... other tool metadata
        },
        "metadata": {
            "server_name": "content_analysis_mcp",
            "realm": "business_enablement",
            "orchestrator": "content_analysis_orchestrator"
        }
    }
}
```

### Registration Method

```python
await curator.register_domain_capability(
    capability=CapabilityDefinition(...),
    user_context=user_context
)
```

---

## 🔍 What Should Be Registered

### For Each MCP Server:

1. **Server-Level Registration** (Optional but recommended):
   - Register the MCP server itself as a service capability
   - Indicates the server provides MCP tools

2. **Tool-Level Registration** (Required):
   - Register each MCP tool as a separate capability
   - Each tool becomes discoverable independently
   - Enables tool-level discovery and usage tracking

---

## 🏗️ Implementation Pattern

### Base Class Method

Add to `MCPServerBase`:

```python
async def register_with_curator(self, user_context: Dict[str, Any] = None) -> bool:
    """
    Register MCP server and all tools with Curator.
    
    Registers:
    1. Server-level capability (optional)
    2. Each tool as individual capability
    
    Args:
        user_context: Optional user context for security/tenant validation
        
    Returns:
        True if registration successful, False otherwise
    """
    try:
        curator = self.get_curator()
        if not curator:
            self.logger.warning("⚠️ Curator not available, skipping registration")
            return False
        
        from foundations.curator_foundation.models.capability_definition import CapabilityDefinition
        
        registered_count = 0
        
        # Register each tool as a capability
        for tool_name, tool_def in self.get_registered_tools().items():
            capability = CapabilityDefinition(
                capability_name=tool_name,
                service_name=self.service_name,
                protocol_name=f"{self.service_name.replace('_', ' ').title().replace(' ', '')}Protocol",
                description=tool_def.get("description", f"MCP Tool: {tool_name}"),
                realm=self._get_realm(),  # Determine realm from service_name or config
                contracts={
                    "mcp_tool": {
                        "tool_name": tool_name,
                        "tool_definition": tool_def,
                        "metadata": {
                            "server_name": self.service_name,
                            "realm": self._get_realm(),
                            "registered_at": datetime.utcnow().isoformat()
                        }
                    }
                },
                version="1.0.0"
            )
            
            success = await curator.register_domain_capability(capability, user_context)
            if success:
                registered_count += 1
                self.logger.debug(f"✅ Registered MCP tool '{tool_name}' with Curator")
            else:
                self.logger.warning(f"⚠️ Failed to register MCP tool '{tool_name}' with Curator")
        
        self.logger.info(f"✅ Registered {registered_count}/{len(self.get_registered_tools())} MCP tools with Curator")
        return registered_count > 0
        
    except Exception as e:
        self.logger.error(f"❌ Failed to register MCP server with Curator: {e}")
        return False

def get_curator(self):
    """Get Curator Foundation service."""
    if hasattr(self, 'di_container') and self.di_container:
        return self.di_container.get_curator()
    return None

def _get_realm(self) -> str:
    """Determine realm from service name or configuration."""
    # Business Enablement MCP servers
    if "business_enablement" in self.service_name or any(x in self.service_name for x in ["content_analysis", "insights", "operations", "business_outcomes", "delivery_manager"]):
        return "business_enablement"
    # Smart City MCP server
    elif "smart_city" in self.service_name:
        return "smart_city"
    # Default
    else:
        return "agentic"  # MCP servers are agentic by nature
```

---

## 📝 Implementation Steps

1. ✅ **Add `get_curator()` helper** to `MCPServerBase`
2. ✅ **Add `_get_realm()` helper** to `MCPServerBase`
3. ✅ **Add `register_with_curator()` method** to `MCPServerBase`
4. ✅ **Call registration** in server initialization (after tools are registered)
5. ✅ **Test registration** for all 6 MCP servers

---

## 🔄 Registration Timing

**When to register:**
- After `register_server_tools()` completes (tools are registered)
- During server initialization (in `__init__` or async `initialize()`)
- Can be called manually if needed

**Registration should be:**
- Non-blocking (don't fail server startup if Curator unavailable)
- Idempotent (safe to call multiple times)
- Logged (track registration success/failure)

---

## ✅ Benefits

1. **Tool Discovery** - Agents can discover available MCP tools via Curator
2. **Usage Tracking** - Track which tools are used and by whom
3. **Service Mesh Integration** - Tools become part of service mesh routing
4. **Capability Management** - Centralized capability registry
5. **Multi-Tenancy** - Tool access can be tenant-scoped

---

**Status:** 📋 **PLAN COMPLETE**  
**Next:** Implement registration methods in `MCPServerBase` and all MCP servers





