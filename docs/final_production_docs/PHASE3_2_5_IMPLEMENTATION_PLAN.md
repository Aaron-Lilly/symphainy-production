# Phase 3.2.5: Unified MCP Pattern - Implementation Plan

## Overview

This plan implements a unified pattern where:
1. **Services define SOA APIs** via `_define_soa_api_handlers()` method
2. **MCP Servers expose SOA APIs as MCP Tools** automatically
3. **Services.get_soa_apis()** returns from MCP Server (single source of truth)
4. **Agents use MCP Tools exclusively** (no direct service access)

## Implementation Strategy: Incremental Rollout

### Phase 1: Foundation (Base Classes)
- Update `RealmServiceBase` to support unified pattern
- Update `OrchestratorBase` to initialize MCP servers
- Add `execute_mcp_tool()` helper to agent base classes
- Update `SmartCityRoleBase` to use unified pattern

### Phase 2: Proof of Concept (Content Realm)
- Create `ContentMCPServer` that exposes Content realm SOA APIs
- Update `ContentJourneyOrchestrator` to initialize MCP server
- Update one agent (`ContentProcessingAgent`) to use MCP tools
- Verify end-to-end: Agent → MCP Tool → Service

### Phase 3: Scale to All Realms
- Create/update MCP servers for all realms
- Update all orchestrators to initialize MCP servers
- Update all agents to use MCP tools
- Remove all direct service access from agents

### Phase 4: Verification
- Verify all MCP tools are functional (no false positives)
- Verify agents can complete workflows
- Verify no direct service access remains
- Update documentation

## Detailed Steps

### Step 1: Update Base Classes

#### 1.1 Update `RealmServiceBase`

Add methods to support unified pattern:

```python
# In RealmServiceBase
def _define_soa_api_handlers(self) -> Dict[str, Any]:
    """
    Define SOA API handlers (internal method).
    
    Services override this to define their SOA APIs.
    This is called by MCP Server during initialization.
    
    Returns:
        Dict of SOA API definitions:
        {
            "api_name": {
                "handler": method_reference,
                "input_schema": {...},
                "description": "..."
            }
        }
    """
    return {}

async def get_soa_apis(self) -> Dict[str, Any]:
    """
    Get SOA APIs exposed by this service.
    
    UNIFIED PATTERN: Returns SOA APIs from MCP Server registration.
    If MCP Server not initialized, returns empty dict (service not ready).
    """
    if hasattr(self, 'mcp_server') and self.mcp_server:
        return await self.mcp_server.get_soa_apis_from_tools()
    return {}
```

#### 1.2 Update `OrchestratorBase`

Add MCP server initialization pattern:

```python
# In OrchestratorBase
async def initialize(self) -> bool:
    # ... existing initialization ...
    
    # Initialize MCP server if service defines SOA APIs
    if hasattr(self, '_define_soa_api_handlers'):
        await self._initialize_mcp_server()
    
    # Set orchestrator on agents (for MCP tool access)
    for agent in self._agents.values():
        if hasattr(agent, 'set_orchestrator'):
            agent.set_orchestrator(self)

async def _initialize_mcp_server(self):
    """Initialize MCP server for this orchestrator."""
    # Subclasses override to create realm-specific MCP server
    pass
```

#### 1.3 Update Agent Base Classes

Add `execute_mcp_tool()` helper:

```python
# In BusinessSpecialistAgentBase or AgentBase
async def execute_mcp_tool(
    self,
    tool_name: str,
    parameters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute MCP tool via orchestrator's MCP server.
    
    This is the PRIMARY method for agents to interact with services.
    Agents should NEVER access services directly.
    """
    if not self.orchestrator:
        raise ValueError(
            f"Orchestrator not set for {self.agent_name}. "
            f"Cannot execute MCP tool '{tool_name}'. "
            f"Ensure orchestrator calls set_orchestrator(agent) during initialization."
        )
    
    if not hasattr(self.orchestrator, 'mcp_server') or self.orchestrator.mcp_server is None:
        raise ValueError(
            f"Orchestrator {self.orchestrator.__class__.__name__} does not have MCP server. "
            f"Cannot execute MCP tool '{tool_name}'."
        )
    
    # Use provided user_context or default
    final_user_context = user_context or getattr(self, 'user_context', None)
    
    return await self.orchestrator.mcp_server.execute_tool(
        tool_name,
        parameters,
        user_context=final_user_context
    )
```

### Step 2: Create Content Realm MCP Server (POC)

#### 2.1 Create `ContentMCPServer`

File: `backend/content/mcp_server/content_mcp_server.py`

```python
class ContentMCPServer(MCPServerBase):
    """MCP Server for Content Realm - exposes Content realm SOA APIs as MCP tools."""
    
    def __init__(self, orchestrator, di_container):
        super().__init__(
            service_name="content_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
        self.soa_api_registry = {}  # Track SOA API → MCP Tool mapping
    
    async def initialize(self):
        """Initialize MCP Server and register tools from orchestrator SOA APIs."""
        # Get SOA API definitions from orchestrator
        soa_apis = await self.orchestrator._define_soa_api_handlers()
        
        # Register each SOA API as an MCP Tool
        for api_name, api_def in soa_apis.items():
            tool_name = f"content_{api_name}"
            
            # Create MCP tool handler that wraps SOA API handler
            handler = api_def.get("handler")
            if not handler:
                self.logger.warning(f"SOA API '{api_name}' missing handler, skipping")
                continue
            
            # Create async wrapper
            async def tool_handler(parameters: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
                # Call orchestrator handler with parameters
                return await handler(**parameters)
            
            # Register tool
            self.register_tool(
                tool_name=tool_name,
                handler=tool_handler,
                input_schema=api_def.get("input_schema", {}),
                description=api_def.get("description", f"Content realm: {api_name}")
            )
            
            # Track mapping
            self.soa_api_registry[api_name] = tool_name
        
        await super().initialize()
    
    async def get_soa_apis_from_tools(self) -> Dict[str, Any]:
        """Return SOA API definitions from registered MCP tools."""
        result = {}
        for api_name, tool_name in self.soa_api_registry.items():
            tool = self.get_tool(tool_name)
            if tool:
                result[api_name] = {
                    "endpoint": f"/mcp/{tool_name}",
                    "method": "POST",
                    "mcp_tool": tool_name,
                    "description": tool.get("description", "")
                }
        return result
```

#### 2.2 Update `ContentJourneyOrchestrator`

Add `_define_soa_api_handlers()` and MCP server initialization:

```python
class ContentJourneyOrchestrator(OrchestratorBase):
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """Define Content Journey orchestrator SOA APIs."""
        return {
            "upload_file": {
                "handler": self.handle_content_upload,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_data": {"type": "string", "format": "binary"},
                        "filename": {"type": "string"},
                        "file_type": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["file_data", "filename"]
                },
                "description": "Upload file to Content realm"
            },
            "process_file": {
                "handler": self.process_file,
                "input_schema": {...},
                "description": "Process file (parse, analyze, etc.)"
            }
        }
    
    async def _initialize_mcp_server(self):
        """Initialize Content MCP Server."""
        from backend.content.mcp_server.content_mcp_server import ContentMCPServer
        
        self.mcp_server = ContentMCPServer(
            orchestrator=self,
            di_container=self.di_container
        )
        await self.mcp_server.initialize()
```

#### 2.3 Update `ContentProcessingAgent`

Replace direct service access with MCP tools:

```python
# BEFORE:
content_steward = await self.get_content_steward_api()
result = await content_steward.process_upload(...)

# AFTER:
result = await self.execute_mcp_tool(
    "content_upload_file",
    {
        "file_data": file_data,
        "filename": filename,
        "file_type": file_type,
        "user_context": user_context
    }
)
```

### Step 3: Scale to All Realms

Repeat Step 2 for:
- Insights Realm
- Solution Realm
- Business Enablement Realm
- Journey orchestrators (update existing MCP servers)

### Step 4: Verification

1. **Code Audit:**
   - Search for `get_content_steward_api()`, `get_file_parser_service()`, etc. in agent files
   - Should find zero results (or only in orchestrators/services, not agents)

2. **Functional Testing:**
   - Test agent operations using MCP tools
   - Verify agents can complete workflows
   - Verify error handling works correctly

3. **MCP Tool Verification:**
   - List all registered MCP tools
   - Test each tool execution
   - Verify no false positives (all tools functional)

## Success Criteria

- ✅ Single unified pattern (no parallel implementations)
- ✅ MCP Server is single source of truth
- ✅ All SOA APIs exposed as MCP Tools
- ✅ All agents use MCP Tools (zero direct service access)
- ✅ All tools functional (no false positives)
- ✅ get_soa_apis() returns from MCP Server

## Timeline

- **Day 1:** Update base classes (Step 1)
- **Day 2:** Create Content Realm MCP Server POC (Step 2)
- **Day 3:** Scale to all realms (Step 3)
- **Day 4:** Verification and testing (Step 4)

