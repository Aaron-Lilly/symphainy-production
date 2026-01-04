# Phase 3.2.5: Cross-Realm MCP Tool Access Pattern

## Problem Statement

Agents in one realm may need to access capabilities from another realm:
- **DataMappingAgent** (Insights realm) needs `get_parsed_file` from Content realm
- **Solution orchestrators** may need capabilities from Content, Insights, and Journey realms
- **Journey orchestrators** may need capabilities from multiple realms

**Requirement:** Agents must use MCP tools exclusively (no direct service access), but need a way to access tools from other realms' MCP servers.

## Design Principles

1. **Unified Pattern:** All agent access goes through MCP tools (no exceptions)
2. **Realm Discovery:** Agents can discover and access MCP servers from other realms
3. **Orchestrator Gateway:** Orchestrators act as gateways to their realm's MCP server
4. **Explicit Routing:** Tool names include realm prefix (e.g., `content_get_parsed_file`, `insights_execute_data_mapping_workflow`)
5. **No Direct Service Access:** Agents never call services directly, even across realms

## Architecture

### Pattern 1: Orchestrator-to-Orchestrator Discovery (Recommended)

**How it works:**
1. Each orchestrator registers its MCP server with Curator (or maintains a registry)
2. Agents can discover orchestrators from other realms via their orchestrator
3. Agents call `execute_mcp_tool(realm, tool_name, parameters)` which routes to the correct realm's MCP server

**Implementation:**
```python
# In BusinessSpecialistAgentBase
async def execute_mcp_tool(
    self,
    tool_name: str,
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    realm: Optional[str] = None  # NEW: Optional realm override
) -> Dict[str, Any]:
    """
    Execute MCP tool via orchestrator's MCP server.
    
    If realm is specified, discover and route to that realm's orchestrator.
    Otherwise, use the agent's own orchestrator (default behavior).
    
    Args:
        tool_name: Name of the MCP tool (e.g., "get_parsed_file" or "content_get_parsed_file")
        parameters: Dictionary of parameters for the tool
        user_context: Optional user context for authorization and auditing
        realm: Optional realm name to route to (e.g., "content", "insights")
    
    Returns:
        Dictionary containing the result of the tool execution
    """
    # If realm specified, discover orchestrator from that realm
    if realm:
        return await self._execute_cross_realm_tool(realm, tool_name, parameters, user_context)
    
    # Default: Use agent's own orchestrator
    if not self.orchestrator:
        raise ValueError(f"Orchestrator not set for {self.agent_name}")
    
    if not hasattr(self.orchestrator, 'mcp_server') or self.orchestrator.mcp_server is None:
        raise ValueError(f"Orchestrator '{self.orchestrator.service_name}' does not have an MCP server")
    
    return await self.orchestrator.mcp_server.execute_tool(tool_name, parameters, user_context)

async def _execute_cross_realm_tool(
    self,
    realm: str,
    tool_name: str,
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute MCP tool from another realm.
    
    Discovers the orchestrator for the specified realm and routes the tool call.
    """
    # Discover orchestrator for the realm
    realm_orchestrator = await self._discover_realm_orchestrator(realm)
    if not realm_orchestrator:
        raise ValueError(f"Orchestrator not found for realm '{realm}'")
    
    if not hasattr(realm_orchestrator, 'mcp_server') or realm_orchestrator.mcp_server is None:
        raise ValueError(f"Orchestrator '{realm_orchestrator.service_name}' does not have an MCP server")
    
    # Remove realm prefix from tool_name if present (e.g., "content_get_parsed_file" -> "get_parsed_file")
    if tool_name.startswith(f"{realm}_"):
        tool_name = tool_name[len(f"{realm}_"):]
    
    return await realm_orchestrator.mcp_server.execute_tool(tool_name, parameters, user_context)

async def _discover_realm_orchestrator(self, realm: str) -> Optional[Any]:
    """
    Discover orchestrator for a specific realm.
    
    Uses Curator to find the orchestrator, or falls back to orchestrator's discovery methods.
    """
    # Try to get orchestrator from agent's orchestrator (if it has discovery methods)
    if self.orchestrator and hasattr(self.orchestrator, 'get_realm_orchestrator'):
        return await self.orchestrator.get_realm_orchestrator(realm)
    
    # Try Curator discovery
    if hasattr(self, 'curator_foundation') and self.curator_foundation:
        try:
            # Discover orchestrator by realm name
            orchestrator = await self.curator_foundation.discover_service(
                service_type=f"{realm}_journey_orchestrator",
                realm_name=realm
            )
            return orchestrator
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover {realm} orchestrator via Curator: {e}")
    
    # Fallback: Try DI container
    if hasattr(self, 'di_container') and self.di_container:
        try:
            orchestrator_class_name = f"{realm.title()}JourneyOrchestrator"
            orchestrator = self.di_container.get_service(orchestrator_class_name)
            return orchestrator
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover {realm} orchestrator via DI container: {e}")
    
    return None
```

### Pattern 2: Tool Name with Realm Prefix (Alternative)

**How it works:**
1. Tool names include realm prefix: `content_get_parsed_file`, `insights_execute_data_mapping_workflow`
2. `execute_mcp_tool()` automatically routes based on tool name prefix
3. No explicit realm parameter needed

**Implementation:**
```python
async def execute_mcp_tool(
    self,
    tool_name: str,  # e.g., "content_get_parsed_file" or "get_parsed_file"
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute MCP tool, automatically routing to correct realm based on tool name prefix.
    
    Tool names can include realm prefix:
    - "content_get_parsed_file" -> routes to Content realm MCP server
    - "insights_execute_data_mapping_workflow" -> routes to Insights realm MCP server
    - "get_parsed_file" (no prefix) -> routes to agent's own orchestrator
    """
    # Extract realm from tool name if present
    realm = None
    if "_" in tool_name:
        potential_realm = tool_name.split("_")[0]
        # Known realms
        if potential_realm in ["content", "insights", "solution", "journey", "business_enablement"]:
            realm = potential_realm
            tool_name = tool_name[len(f"{realm}_"):]
    
    if realm:
        return await self._execute_cross_realm_tool(realm, tool_name, parameters, user_context)
    
    # Default: Use agent's own orchestrator
    # ... (existing implementation)
```

## Recommended Approach

**Use Pattern 1 (Explicit Realm Parameter) with Pattern 2 (Tool Name Prefix) as Fallback:**

1. **Primary:** Tool name includes realm prefix (e.g., `content_get_parsed_file`)
2. **Fallback:** Explicit `realm` parameter if tool name doesn't have prefix
3. **Default:** Agent's own orchestrator if no realm specified

This provides:
- **Explicit routing** when needed
- **Convenience** via tool name prefix
- **Backward compatibility** with existing tool names

## Implementation Steps

1. **Update `BusinessSpecialistAgentBase.execute_mcp_tool()`:**
   - Add realm discovery logic
   - Support tool name prefix parsing
   - Add `_execute_cross_realm_tool()` helper
   - Add `_discover_realm_orchestrator()` helper

2. **Update OrchestratorBase:**
   - Add `get_realm_orchestrator(realm)` method for cross-realm discovery
   - Use Curator or DI container for discovery

3. **Update DataMappingAgent:**
   - Replace `_get_content_steward()` calls with `execute_mcp_tool("content_get_parsed_file", ...)`
   - Remove direct service access

4. **Documentation:**
   - Update agent development guide
   - Add examples of cross-realm tool usage

## Example Usage

```python
# In DataMappingAgent (Insights realm)
async def extract_source_schema(self, source_file_id: str, mapping_type: str):
    # OLD (anti-pattern):
    # content_steward = await self._get_content_steward()
    # parsed_file = await content_steward.get_parsed_file(source_file_id)
    
    # NEW (unified pattern):
    parsed_file_result = await self.execute_mcp_tool(
        "content_get_parsed_file",  # Realm prefix in tool name
        {"parsed_file_id": source_file_id}
    )
    
    if not parsed_file_result.get("success"):
        return {"error": "Failed to get parsed file"}
    
    parsed_file = parsed_file_result
    # ... continue with schema extraction
```

## Benefits

1. **Unified Pattern:** All agent access goes through MCP tools
2. **Discoverable:** Orchestrators are discoverable via Curator/DI container
3. **Explicit:** Tool names clearly indicate which realm they belong to
4. **Extensible:** Easy to add new realms without changing agent code
5. **Testable:** Can mock MCP servers for testing

## Edge Cases

1. **Circular Dependencies:** Ensure orchestrators don't create circular discovery chains
2. **Missing Orchestrators:** Graceful error handling when realm orchestrator not found
3. **Tool Name Conflicts:** Realm prefix prevents conflicts (e.g., `content_get_file` vs `insights_get_file`)
4. **Performance:** Cache orchestrator discoveries to avoid repeated lookups

