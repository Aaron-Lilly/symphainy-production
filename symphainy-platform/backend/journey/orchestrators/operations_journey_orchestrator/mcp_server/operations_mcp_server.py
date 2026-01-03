#!/usr/bin/env python3
"""
Operations Realm MCP Server - Unified Pattern (Phase 3.2.5)

Exposes Operations Journey Orchestrator SOA APIs as MCP Tools for agent consumption.

UNIFIED PATTERN:
- Orchestrator defines SOA APIs via _define_soa_api_handlers()
- MCP Server automatically registers tools from SOA API definitions
- get_soa_apis() returns from MCP Server (single source of truth)
"""

from typing import Dict, Any, Optional
from bases.mcp_server.mcp_server_base import MCPServerBase


class OperationsMCPServer(MCPServerBase):
    """
    Operations Realm MCP Server - Unified Pattern (Phase 3.2.5)
    
    Exposes Operations Journey Orchestrator SOA APIs as MCP Tools.
    Tools are automatically registered from orchestrator's _define_soa_api_handlers().
    
    Architecture:
    - Orchestrator defines SOA APIs via _define_soa_api_handlers()
    - MCP Server registers tools from SOA API definitions during initialize()
    - Agents use MCP Tools exclusively (never direct service access)
    """
    
    def __init__(self, orchestrator, di_container):
        """
        Initialize Operations Realm MCP Server.
        
        Args:
            orchestrator: OperationsJourneyOrchestrator instance
            di_container: DI Container for platform services
        """
        super().__init__(
            service_name="operations_mcp",
            di_container=di_container
        )
        self.orchestrator = orchestrator
        self.soa_api_registry = {}  # Track SOA API → MCP Tool mapping
    
    async def initialize(self):
        """
        Initialize MCP Server and register tools from orchestrator SOA APIs.
        
        UNIFIED PATTERN: Automatically registers tools from _define_soa_api_handlers().
        """
        try:
            self.logger.info("🔧 Initializing Operations Realm MCP Server (unified pattern)...")
            
            # Get SOA API definitions from orchestrator
            if not hasattr(self.orchestrator, '_define_soa_api_handlers'):
                self.logger.warning(
                    f"⚠️ Orchestrator {self.orchestrator.__class__.__name__} does not define SOA APIs. "
                    f"No tools will be registered."
                )
                await super().initialize()
                return True
            
            soa_apis = self.orchestrator._define_soa_api_handlers()
            
            if not soa_apis:
                self.logger.warning("⚠️ No SOA APIs defined by orchestrator. No tools will be registered.")
                await super().initialize()
                return True
            
            # Register each SOA API as an MCP Tool
            registered_count = 0
            for api_name, api_def in soa_apis.items():
                try:
                    # Get handler from SOA API definition
                    handler = api_def.get("handler")
                    if not handler:
                        self.logger.warning(f"⚠️ SOA API '{api_name}' missing handler, skipping")
                        continue
                    
                    # Create tool name (realm prefix - use "journey" since this is in Journey realm)
                    tool_name = f"journey_{api_name}"
                    
                    # Create async wrapper that calls the handler
                    # IMPORTANT: Capture api_name and handler in closure to avoid Python closure bug
                    def create_tool_handler(api_name_inner, handler_inner):
                        """Factory function to create tool handler with proper closure."""
                        async def tool_handler(parameters: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
                            """MCP tool handler that wraps SOA API handler."""
                            # Call orchestrator handler with parameters
                            # Handler should accept **kwargs or specific parameters
                            if callable(handler_inner):
                                # Try calling with parameters unpacked
                                if user_context:
                                    parameters["user_context"] = user_context
                                return await handler_inner(**parameters)
                            else:
                                raise ValueError(f"Handler for '{api_name_inner}' is not callable")
                        return tool_handler
                    
                    tool_handler = create_tool_handler(api_name, handler)
                    
                    # Get input schema from SOA API definition
                    input_schema = api_def.get("input_schema", {})
                    if not input_schema:
                        # Create minimal schema if not provided
                        input_schema = {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    
                    # Register tool
                    self.register_tool(
                        tool_name=tool_name,
                        handler=tool_handler,
                        input_schema=input_schema,
                        description=api_def.get("description", f"Operations realm: {api_name}")
                    )
                    
                    # Track mapping
                    self.soa_api_registry[api_name] = tool_name
                    registered_count += 1
                    self.logger.info(f"✅ Registered MCP tool: {tool_name} (from SOA API: {api_name})")
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to register tool for SOA API '{api_name}': {e}")
                    continue
            
            self.logger.info(
                f"✅ Operations Realm MCP Server initialized with {registered_count} tools "
                f"(from {len(soa_apis)} SOA APIs)"
            )
            
            # Call parent initialize
            await super().initialize()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Operations Realm MCP Server: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_soa_apis_from_tools(self) -> Dict[str, Any]:
        """
        Return SOA API definitions from registered MCP tools.
        
        This is the single source of truth for SOA APIs.
        Services call this via get_soa_apis() to get what's actually exposed.
        
        Returns:
            Dict of SOA API definitions with MCP tool mappings
        """
        result = {}
        for api_name, tool_name in self.soa_api_registry.items():
            tool = self.get_tool(tool_name)
            if tool:
                result[api_name] = {
                    "endpoint": f"/mcp/{tool_name}",
                    "method": "POST",
                    "mcp_tool": tool_name,
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("input_schema", {})
                }
        return result
    
    # ============================================================================
    # MCP SERVER BASE ABSTRACT METHODS
    # ============================================================================
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for Operations Realm MCP Server."""
        return {
            "server_name": "operations_mcp",
            "realm": "journey",
            "description": "Operations Realm MCP Server - exposes Operations Journey Orchestrator capabilities",
            "tools": list(self.soa_api_registry.values()),
            "usage": "Agents use MCP tools to interact with Operations realm capabilities"
        }
    
    def get_tool_list(self) -> list:
        """Return list of available tool names."""
        return list(self.soa_api_registry.values())
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "server_name": "operations_mcp",
            "status": "healthy" if self.is_initialized else "unhealthy",
            "tools_registered": len(self.soa_api_registry),
            "orchestrator_available": self.orchestrator is not None
        }
    
    def get_version_info(self) -> Dict[str, Any]:
        """Return version info."""
        return {
            "server_name": "operations_mcp",
            "version": "3.2.5",
            "pattern": "unified",
            "realm": "journey"
        }
    
    async def execute_tool(self, tool_name: str, parameters: dict, user_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Execute MCP tool (delegates to base class tool registry).
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            user_context: Optional user context
        
        Returns:
            Tool execution result
        """
        # Delegate to base class tool registry
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "available_tools": self.get_tool_list()
            }
        
        # Execute tool handler
        handler = tool.get("handler")
        if not handler:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' has no handler"
            }
        
        try:
            result = await handler(parameters, user_context)
            return result
        except Exception as e:
            self.logger.error(f"❌ Tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

