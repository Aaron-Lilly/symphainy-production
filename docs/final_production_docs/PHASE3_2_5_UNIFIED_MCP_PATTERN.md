# Phase 3.2.5: Unified MCP Server Architecture Pattern

## Problem Statement

**Current Anti-Pattern:**
- Services expose SOA APIs via multiple patterns (SoaMcp module, override method, direct dict)
- MCP Servers and SOA APIs are disconnected
- Agents access services directly instead of using MCP Tools
- No single source of truth for what capabilities are exposed

**Risk:**
- Parallel implementation patterns create inconsistency
- False positives (tools registered but not working)
- Agents bypass architectural boundaries

## Unified Pattern Design

### Core Principle: **MCP Server is the Single Source of Truth**

```
Service (defines SOA APIs)
  ↓
MCP Server (exposes SOA APIs as MCP Tools)
  ↓
Agent (uses MCP Tools exclusively)
```

### Pattern Flow

1. **Service Defines SOA APIs**
   - Service implements `get_soa_apis()` method
   - Returns dict of SOA API definitions with handler references
   - Format: `{"api_name": {"handler": method, "endpoint": "...", "method": "...", ...}}`

2. **MCP Server Registers Tools from SOA APIs**
   - MCP Server calls `service.get_soa_apis()` during initialization
   - For each SOA API, creates an MCP Tool
   - Tool name: `{realm}_{api_name}` (e.g., `content_upload_file`)
   - Tool handler: Wraps SOA API handler with MCP tool interface

3. **Service.get_soa_apis() Returns from MCP Server**
   - `get_soa_apis()` queries the MCP Server for registered tools
   - Returns the same format, but sourced from MCP Server
   - Ensures consistency: what's in MCP Server is what's exposed

4. **Agents Use MCP Tools**
   - Agents call `execute_mcp_tool(tool_name, parameters)`
   - Never access services directly
   - MCP Server routes to service handler

### Implementation Details

#### Service Base Class Pattern

```python
class RealmServiceBase:
    async def get_soa_apis(self) -> Dict[str, Any]:
        """
        Get SOA APIs exposed by this service.
        
        UNIFIED PATTERN: Returns SOA APIs from MCP Server registration.
        If MCP Server not initialized, returns empty dict (service not ready).
        
        Services should:
        1. Define SOA API handlers (methods)
        2. Initialize MCP Server during initialize()
        3. MCP Server automatically registers tools from get_soa_apis()
        4. This method returns what MCP Server has registered
        """
        # Query MCP Server for registered tools
        if hasattr(self, 'mcp_server') and self.mcp_server:
            return self.mcp_server.get_soa_apis_from_tools()
        return {}
    
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """
        Define SOA API handlers (internal method).
        
        Services override this to define their SOA APIs.
        This is called by MCP Server during initialization.
        """
        return {}
```

#### MCP Server Pattern

```python
class RealmMCPServer(MCPServerBase):
    def __init__(self, service, di_container):
        super().__init__(service_name=f"{realm}_mcp", di_container=di_container)
        self.service = service
        self.soa_api_registry = {}  # Track SOA API → MCP Tool mapping
    
    async def initialize(self):
        """Initialize MCP Server and register tools from service SOA APIs."""
        # Get SOA API definitions from service
        soa_apis = await self.service._define_soa_api_handlers()
        
        # Register each SOA API as an MCP Tool
        for api_name, api_def in soa_apis.items():
            tool_name = f"{self.realm}_{api_name}"
            
            # Create MCP tool handler that wraps SOA API handler
            async def tool_handler(parameters: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
                # Extract handler from SOA API definition
                handler = api_def.get("handler")
                if not handler:
                    raise ValueError(f"SOA API '{api_name}' missing handler")
                
                # Call service handler with parameters
                return await handler(**parameters)
            
            # Register tool
            self.register_tool(
                tool_name=tool_name,
                handler=tool_handler,
                input_schema=api_def.get("input_schema", {}),
                description=api_def.get("description", f"SOA API: {api_name}")
            )
            
            # Track mapping
            self.soa_api_registry[api_name] = tool_name
        
        await super().initialize()
    
    def get_soa_apis_from_tools(self) -> Dict[str, Any]:
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

#### Service Implementation Pattern

```python
class ContentManagerService(RealmServiceBase):
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """Define Content realm SOA APIs."""
        return {
            "upload_file": {
                "handler": self.upload_file,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_data": {"type": "string", "format": "binary"},
                        "filename": {"type": "string"},
                        "file_type": {"type": "string"}
                    },
                    "required": ["file_data", "filename"]
                },
                "description": "Upload file to Content realm"
            },
            "parse_file": {
                "handler": self.parse_file,
                "input_schema": {...},
                "description": "Parse file into structured format"
            }
        }
    
    async def initialize(self):
        # Initialize MCP Server
        self.mcp_server = ContentMCPServer(
            service=self,
            di_container=self.di_container
        )
        await self.mcp_server.initialize()
        
        # ... rest of initialization ...
```

#### Agent Pattern

```python
class ContentProcessingAgent(SpecialistAgentBase):
    async def process_upload(self, file_data: bytes, filename: str):
        """Process file upload using MCP tool."""
        # ✅ USE: MCP tool via orchestrator's MCP server
        result = await self.execute_mcp_tool(
            "content_upload_file",
            {
                "file_data": file_data,
                "filename": filename,
                "file_type": self._detect_file_type(filename)
            }
        )
        return result
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool (from base class)."""
        if not self.orchestrator or not hasattr(self.orchestrator, 'mcp_server'):
            raise ValueError(f"Orchestrator or MCP server not available for tool '{tool_name}'")
        
        return await self.orchestrator.mcp_server.execute_tool(
            tool_name,
            parameters,
            user_context=self.user_context
        )
```

## Implementation Steps

### Step 1: Update Base Classes
- Update `RealmServiceBase.get_soa_apis()` to query MCP Server
- Add `_define_soa_api_handlers()` abstract method
- Update `MCPServerBase` to support SOA API → MCP Tool registration

### Step 2: Create Realm MCP Servers
- Content Realm MCP Server
- Insights Realm MCP Server
- Solution Realm MCP Server
- Business Enablement Realm MCP Server
- Update Journey orchestrator MCP servers

### Step 3: Update Services
- All services implement `_define_soa_api_handlers()`
- All services initialize MCP Server in `initialize()`
- Remove SoaMcp module pattern (consolidate into unified pattern)

### Step 4: Update Agents
- Remove all direct service access
- Add `execute_mcp_tool()` helper to agent base classes
- Update all agents to use MCP tools

### Step 5: Verification
- Verify all MCP tools are registered
- Verify all tools are functional (no false positives)
- Verify agents can complete workflows
- Verify no direct service access in agents

## Success Criteria

- ✅ Single unified pattern (no parallel implementations)
- ✅ MCP Server is single source of truth
- ✅ All SOA APIs exposed as MCP Tools
- ✅ All agents use MCP Tools (zero direct service access)
- ✅ All tools functional (no false positives)
- ✅ get_soa_apis() returns from MCP Server

## Benefits

1. **Consistency:** One pattern, no confusion
2. **Reliability:** MCP Server registration ensures tools work
3. **Architectural Compliance:** Agents can't bypass boundaries
4. **Maintainability:** Single place to manage capabilities
5. **Testability:** Easy to verify what's exposed

