#!/usr/bin/env python3
"""
Traffic Cop MCP Server

Exposes Traffic Cop Service capabilities as MCP tools.
Provides session management, state coordination, and cross-dimensional orchestration tools.
"""

import os
import sys
from typing import Dict, Any, List, Optional, Callable
import asyncio
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
from backend.smart_city.protocols.mcp_server_protocol import MCPBaseServer
from backend.smart_city.protocols.mcp_server_protocol import MCPServerProtocol, MCPTool, MCPServerInfo
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment


class TrafficCopMCPServer(MCPBaseServer):
    """
    Traffic Cop MCP Server

    Exposes Traffic Cop Service capabilities as MCP tools.
    """

    def __init__(self, environment_loader=None, logger=None):
        """Initialize Traffic Cop MCP Server."""
        super().__init__(environment_loader, logger)
        
        # Initialize Traffic Cop Service
        self.traffic_cop_service = TrafficCopService(environment_loader, logger)
        
        # Initialize MCP protocol
        self.mcp_protocol = TrafficCopMCPProtocol("TrafficCopMCPServer", self, None)
        
        # Server info
        self.server_info = MCPServerInfo(
            server_name="TrafficCopMCPServer",
            version="1.0.0",
            description="MCP server for Traffic Cop Service - session management, state coordination, and cross-dimensional orchestration",
            interface_name="TrafficCopInterface",
            tools=[],
            capabilities=["session_management", "state_coordination", "cross_dimensional_orchestration", "health_monitoring"]
        )
        
        self.logger.info("🚦 Traffic Cop MCP Server initialized")

    async def initialize(self):
        """Initialize the MCP server."""
        try:
            await super().initialize()
            
            # Initialize MCP protocol
            await self.mcp_protocol.initialize()
            self.logger.info("✅ MCP Protocol initialized")
            
            await self.traffic_cop_service.initialize()
            self.logger.info("✅ Traffic Cop MCP Server initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Traffic Cop MCP Server: {e}")
            raise

    async def initialize_service_integration(self):
        """Initialize integration with the Traffic Cop Service."""
        try:
            self.logger.info("🔗 Initializing Traffic Cop Service integration...")
            
            # Initialize the underlying service
            await self.traffic_cop_service.initialize()
            
            self.logger.info("✅ Traffic Cop Service integration initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Traffic Cop Service integration: {e}")
            raise

    def register_tools(self):
        """Register MCP tools with the server."""
        try:
            self.logger.info("🔧 Registering Traffic Cop MCP tools...")
            
            # Tools are registered dynamically in get_tools()
            # This method is called during server initialization
            
            self.logger.info("✅ Traffic Cop MCP tools registered")
        except Exception as e:
            self.logger.error(f"❌ Failed to register Traffic Cop MCP tools: {e}")
            raise

    async def get_server_info(self) -> MCPServerInfo:
        """Get server information."""
        return self.server_info

    async def get_tools(self) -> List[MCPTool]:
        """Get available MCP tools."""
        return [
            # Session Management Tools
            MCPTool(
                name="create_session",
                description="Create a new session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID"},
                        "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Session dimensions"},
                        "metadata": {"type": "object", "description": "Session metadata"},
                        "expires_at": {"type": "string", "description": "Session expiration time"},
                        "state_scope": {"type": "string", "description": "State scope (local, global, shared, temp)"},
                        "priority": {"type": "integer", "description": "Session priority"}
                    },
                    "required": ["user_id"]
                },
                handler=self._handle_create_session,
                tags=["session", "create", "management"]
            ),
            MCPTool(
                name="validate_session",
                description="Validate a session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_validate_session,
                tags=["session", "validate", "management"]
            ),
            MCPTool(
                name="update_session_state",
                description="Update session state",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "key": {"type": "string", "description": "State key"},
                        "value": {"type": "object", "description": "State value"},
                        "scope": {"type": "string", "description": "State scope"},
                        "priority": {"type": "integer", "description": "State priority"},
                        "metadata": {"type": "object", "description": "State metadata"}
                    },
                    "required": ["session_id", "key", "value"]
                },
                handler=self._handle_update_session_state,
                tags=["session", "state", "update"]
            ),
            MCPTool(
                name="get_session_state",
                description="Get session state",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "key": {"type": "string", "description": "State key (optional)"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_session_state,
                tags=["session", "state", "get"]
            ),
            MCPTool(
                name="terminate_session",
                description="Terminate a session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_terminate_session,
                tags=["session", "terminate", "management"]
            ),
            MCPTool(
                name="get_session_health",
                description="Get session health metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_session_health,
                tags=["session", "health", "metrics"]
            ),

            # State Coordination Tools
            MCPTool(
                name="share_state",
                description="Share state across dimensions or sessions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "State key"},
                        "value": {"type": "object", "description": "State value"},
                        "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Target dimensions"},
                        "sessions": {"type": "array", "items": {"type": "string"}, "description": "Target sessions"},
                        "scope": {"type": "string", "description": "State scope"},
                        "priority": {"type": "integer", "description": "State priority"},
                        "metadata": {"type": "object", "description": "State metadata"}
                    },
                    "required": ["key", "value"]
                },
                handler=self._handle_share_state,
                tags=["state", "share", "coordination"]
            ),
            MCPTool(
                name="resolve_state_conflict",
                description="Resolve state conflicts between sessions or dimensions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "conflict_id": {"type": "string", "description": "Conflict ID"},
                        "strategy": {"type": "string", "description": "Resolution strategy (merge, override, preserve, conflict)"},
                        "conflicting_states": {"type": "array", "items": {"type": "object"}, "description": "Conflicting states"}
                    },
                    "required": ["conflicting_states"]
                },
                handler=self._handle_resolve_state_conflict,
                tags=["state", "conflict", "resolution"]
            ),
            MCPTool(
                name="synchronize_states",
                description="Synchronize states across sessions or dimensions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_session": {"type": "string", "description": "Source session ID"},
                        "target_sessions": {"type": "array", "items": {"type": "string"}, "description": "Target session IDs"},
                        "state_keys": {"type": "array", "items": {"type": "string"}, "description": "State keys to sync"},
                        "strategy": {"type": "string", "description": "Sync strategy (push, pull, bidirectional)"}
                    },
                    "required": ["source_session", "target_sessions"]
                },
                handler=self._handle_synchronize_states,
                tags=["state", "sync", "coordination"]
            ),
            MCPTool(
                name="get_shared_states",
                description="Get shared states by scope or dimension",
                input_schema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "State scope"},
                        "dimension": {"type": "string", "description": "Dimension name"}
                    }
                },
                handler=self._handle_get_shared_states,
                tags=["state", "get", "shared"]
            ),
            MCPTool(
                name="get_state_conflicts",
                description="Get unresolved state conflicts",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_state_conflicts,
                tags=["state", "conflicts", "get"]
            ),

            # Cross-Dimensional Orchestration Tools
            MCPTool(
                name="create_cross_dimensional_session",
                description="Create a cross-dimensional session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Session dimensions"},
                        "metadata": {"type": "object", "description": "Session metadata"},
                        "coordination_strategy": {"type": "string", "description": "Coordination strategy"}
                    },
                    "required": ["dimensions"]
                },
                handler=self._handle_create_cross_dimensional_session,
                tags=["session", "cross_dimensional", "orchestration"]
            ),
            MCPTool(
                name="coordinate_dimensions",
                description="Coordinate activities across dimensions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "type": {"type": "string", "description": "Coordination type (state_sync, workflow_coordination, resource_sharing)"},
                        "target_dimensions": {"type": "array", "items": {"type": "string"}, "description": "Target dimensions"},
                        "payload": {"type": "object", "description": "Coordination payload"}
                    },
                    "required": ["session_id", "type"]
                },
                handler=self._handle_coordinate_dimensions,
                tags=["coordination", "dimensions", "orchestration"]
            ),
            MCPTool(
                name="execute_cross_dimensional_workflow",
                description="Execute a workflow across multiple dimensions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Workflow dimensions"},
                        "steps": {"type": "array", "items": {"type": "object"}, "description": "Workflow steps"},
                        "strategy": {"type": "string", "description": "Execution strategy (sequential, parallel)"}
                    },
                    "required": ["dimensions", "steps"]
                },
                handler=self._handle_execute_cross_dimensional_workflow,
                tags=["workflow", "cross_dimensional", "execution"]
            ),
            MCPTool(
                name="get_dimension_status",
                description="Get status of dimensions in a session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "dimension": {"type": "string", "description": "Specific dimension (optional)"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_dimension_status,
                tags=["dimension", "status", "orchestration"]
            ),
            MCPTool(
                name="get_orchestration_metrics",
                description="Get orchestration metrics for a session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_orchestration_metrics,
                tags=["orchestration", "metrics", "analytics"]
            ),

            # Health Monitoring Tools
            MCPTool(
                name="collect_metrics",
                description="Collect health and performance metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "metric_type": {"type": "string", "description": "Metric type (performance, resource, error, activity)"},
                        "metric_name": {"type": "string", "description": "Metric name"},
                        "metric_value": {"type": "object", "description": "Metric value"},
                        "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Metric dimensions"},
                        "metadata": {"type": "object", "description": "Metric metadata"}
                    },
                    "required": ["session_id", "metric_name", "metric_value"]
                },
                handler=self._handle_collect_metrics,
                tags=["metrics", "collect", "monitoring"]
            ),
            MCPTool(
                name="get_session_health_detailed",
                description="Get comprehensive health status for a session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_session_health_detailed,
                tags=["health", "detailed", "monitoring"]
            ),
            MCPTool(
                name="set_alert_threshold",
                description="Set alert thresholds for metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string", "description": "Metric name"},
                        "threshold_value": {"type": "number", "description": "Threshold value"},
                        "threshold_type": {"type": "string", "description": "Threshold type (greater_than, less_than, equals)"},
                        "alert_message": {"type": "string", "description": "Alert message"}
                    },
                    "required": ["metric_name", "threshold_value"]
                },
                handler=self._handle_set_alert_threshold,
                tags=["alert", "threshold", "monitoring"]
            ),
            MCPTool(
                name="get_health_alerts",
                description="Get health alerts",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID (optional)"}
                    }
                },
                handler=self._handle_get_health_alerts,
                tags=["alerts", "health", "monitoring"]
            ),
            MCPTool(
                name="get_performance_metrics",
                description="Get performance metrics for a session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"},
                        "metric_name": {"type": "string", "description": "Specific metric name (optional)"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_performance_metrics,
                tags=["performance", "metrics", "monitoring"]
            ),

            # Service Management Tools
            MCPTool(
                name="get_service_health",
                description="Get comprehensive health status of the Traffic Cop Service",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_service_health,
                tags=["service", "health", "status"]
            ),
            MCPTool(
                name="get_service_metrics",
                description="Get service metrics and statistics",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_service_metrics,
                tags=["service", "metrics", "statistics"]
            )
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute an MCP tool."""
        try:
            handler = getattr(self, f"_handle_{tool_name}", None)
            if handler:
                return await handler(arguments, user_context)
            else:
                raise ValueError(f"Tool '{tool_name}' not found.")
        except Exception as e:
            self.logger.error(f"❌ Error executing tool '{tool_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }

    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================

    # Session Management Handlers
    async def _handle_create_session(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_session tool."""
        return await self.traffic_cop_service.create_session(arguments, user_context)

    async def _handle_validate_session(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle validate_session tool."""
        return await self.traffic_cop_service.validate_session(arguments["session_id"], user_context)

    async def _handle_update_session_state(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle update_session_state tool."""
        return await self.traffic_cop_service.update_session_state(
            arguments["session_id"],
            arguments,
            user_context
        )

    async def _handle_get_session_state(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_session_state tool."""
        return await self.traffic_cop_service.get_session_state(
            arguments["session_id"],
            arguments.get("key"),
            user_context
        )

    async def _handle_terminate_session(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle terminate_session tool."""
        return await self.traffic_cop_service.terminate_session(arguments["session_id"], user_context)

    async def _handle_get_session_health(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_session_health tool."""
        return await self.traffic_cop_service.get_session_health(arguments["session_id"], user_context)

    # State Coordination Handlers
    async def _handle_share_state(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle share_state tool."""
        return await self.traffic_cop_service.share_state(arguments, user_context)

    async def _handle_resolve_state_conflict(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle resolve_state_conflict tool."""
        return await self.traffic_cop_service.resolve_state_conflict(arguments, user_context)

    async def _handle_synchronize_states(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle synchronize_states tool."""
        return await self.traffic_cop_service.synchronize_states(arguments, user_context)

    async def _handle_get_shared_states(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_shared_states tool."""
        return await self.traffic_cop_service.get_shared_states(
            arguments.get("scope"),
            arguments.get("dimension"),
            user_context
        )

    async def _handle_get_state_conflicts(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_state_conflicts tool."""
        return await self.traffic_cop_service.get_state_conflicts(user_context)

    # Cross-Dimensional Orchestration Handlers
    async def _handle_create_cross_dimensional_session(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_cross_dimensional_session tool."""
        return await self.traffic_cop_service.create_cross_dimensional_session(arguments, user_context)

    async def _handle_coordinate_dimensions(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle coordinate_dimensions tool."""
        return await self.traffic_cop_service.coordinate_dimensions(
            arguments["session_id"],
            arguments,
            user_context
        )

    async def _handle_execute_cross_dimensional_workflow(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle execute_cross_dimensional_workflow tool."""
        return await self.traffic_cop_service.execute_cross_dimensional_workflow(arguments, user_context)

    async def _handle_get_dimension_status(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_dimension_status tool."""
        return await self.traffic_cop_service.get_dimension_status(
            arguments["session_id"],
            arguments.get("dimension"),
            user_context
        )

    async def _handle_get_orchestration_metrics(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_orchestration_metrics tool."""
        return await self.traffic_cop_service.get_orchestration_metrics(arguments["session_id"], user_context)

    # Health Monitoring Handlers
    async def _handle_collect_metrics(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle collect_metrics tool."""
        return await self.traffic_cop_service.collect_metrics(arguments, user_context)

    async def _handle_get_session_health_detailed(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_session_health_detailed tool."""
        return await self.traffic_cop_service.get_session_health_detailed(arguments["session_id"], user_context)

    async def _handle_set_alert_threshold(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle set_alert_threshold tool."""
        return await self.traffic_cop_service.set_alert_threshold(arguments, user_context)

    async def _handle_get_health_alerts(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_health_alerts tool."""
        return await self.traffic_cop_service.get_health_alerts(
            arguments.get("session_id"),
            user_context
        )

    async def _handle_get_performance_metrics(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_performance_metrics tool."""
        return await self.traffic_cop_service.get_performance_metrics(
            arguments["session_id"],
            arguments.get("metric_name"),
            user_context
        )

    # Service Management Handlers
    async def _handle_get_service_health(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_service_health tool."""
        return await self.traffic_cop_service.get_health_status()

    async def _handle_get_service_metrics(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_service_metrics tool."""
        return await self.traffic_cop_service.get_metrics()

    async def cleanup(self):
        """Cleanup MCP server resources."""
        try:
            await self.traffic_cop_service.cleanup()
            await super().cleanup()
            self.logger.info("✅ Traffic Cop MCP Server cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup Traffic Cop MCP Server: {e}")


class TrafficCopMCPProtocol(MCPServerProtocol):
    """MCP Protocol implementation for Traffic Cop MCP Server."""
    
    def __init__(self, server_name: str, server_instance, curator_foundation=None):
        """Initialize Traffic Cop MCP Protocol."""
        super().__init__(server_name, None, curator_foundation)
        self.server_instance = server_instance
        self.server_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the MCP server."""
        # Create server info with multi-tenant metadata
        self.server_info = MCPServerInfo(
            server_name="TrafficCopMCPServer",
            version="1.0.0",
            description="Traffic Cop MCP Server - Multi-tenant session and state management tools",
            interface_name="ITrafficCopMCP",
            tools=self._create_all_tools(),
            capabilities=["session-management", "state-management", "multi-tenant", "routing"],
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_server_info(self) -> MCPServerInfo:
        """Get server information for MCP manifest generation."""
        return self.server_info
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available MCP tools."""
        return self.server_info.tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute an MCP tool with given parameters."""
        # Find the tool
        tool = None
        for t in self.server_info.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return self._create_error_response(f"Tool '{tool_name}' not found", "TOOL_NOT_FOUND")
        
        # Validate tenant context if required
        if tool.requires_tenant:
            validation = self._validate_tenant_context(user_context, tool)
            if not validation["valid"]:
                return self._create_error_response(validation["error"], "TENANT_CONTEXT_REQUIRED")
        
        try:
            # Execute the tool handler
            result = await tool.handler(parameters, user_context)
            return self._create_success_response(result)
        except Exception as e:
            return self._create_error_response(str(e), "TOOL_EXECUTION_ERROR")
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this server with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.server_info.interface_name,
                "endpoints": [],  # MCP servers don't have HTTP endpoints
                "tools": [tool.name for tool in self.server_info.tools],
                "description": self.server_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.server_info.multi_tenant_enabled,
                "tenant_isolation_level": self.server_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.server_name,
                capability,
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_tools(self) -> List[MCPTool]:
        """Create all tools for Traffic Cop MCP Server."""
        tools = []
        
        # Standard tools
        tools.extend(self._create_standard_tools())
        tools.extend(self._create_tenant_aware_tools())
        
        # Traffic Cop specific tools
        tools.extend([
            MCPTool(
                name="create_session",
                description="Create a new session with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_type": {"type": "string", "description": "Type of session"},
                        "metadata": {"type": "object", "description": "Session metadata"},
                        "duration_hours": {"type": "integer", "description": "Session duration in hours"}
                    },
                    "required": ["session_type"]
                },
                handler=self._handle_create_session,
                tags=["session", "management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="get_session",
                description="Get session information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string", "description": "Session ID"}
                    },
                    "required": ["session_id"]
                },
                handler=self._handle_get_session,
                tags=["session", "information"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="set_state",
                description="Set state with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "State key"},
                        "value": {"type": "object", "description": "State value"},
                        "pillar": {"type": "string", "description": "Pillar name"}
                    },
                    "required": ["key", "value", "pillar"]
                },
                handler=self._handle_set_state,
                tags=["state", "management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="get_state",
                description="Get state by key with tenant awareness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "State key"}
                    },
                    "required": ["key"]
                },
                handler=self._handle_get_state,
                tags=["state", "information"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            MCPTool(
                name="get_tenant_state_summary",
                description="Get state summary for a specific tenant",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string", "description": "Tenant ID"}
                    },
                    "required": ["tenant_id"]
                },
                handler=self._handle_get_tenant_state_summary,
                tags=["tenant", "state"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return tools
    
    async def _handle_create_session(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create_session tool execution."""
        session_type = parameters.get("session_type")
        metadata = parameters.get("metadata", {})
        duration_hours = parameters.get("duration_hours", 24)
        
        if not session_type:
            return {"error": "Session type required"}
        
        result = await self.server_instance.traffic_cop_service.create_session(
            session_type, metadata, duration_hours, user_context
        )
        return result
    
    async def _handle_get_session(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_session tool execution."""
        session_id = parameters.get("session_id")
        if not session_id:
            return {"error": "Session ID required"}
        
        result = await self.server_instance.traffic_cop_service.get_session(
            session_id, user_context
        )
        return result
    
    async def _handle_set_state(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle set_state tool execution."""
        key = parameters.get("key")
        value = parameters.get("value")
        pillar = parameters.get("pillar")
        
        if not all([key, value, pillar]):
            return {"error": "All parameters required"}
        
        result = await self.server_instance.traffic_cop_service.set_state(
            key, value, pillar, user_context
        )
        return result
    
    async def _handle_get_state(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_state tool execution."""
        key = parameters.get("key")
        if not key:
            return {"error": "Key required"}
        
        result = await self.server_instance.traffic_cop_service.get_state(
            key, user_context
        )
        return result
    
    async def _handle_get_tenant_state_summary(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get_tenant_state_summary tool execution."""
        tenant_id = parameters.get("tenant_id")
        if not tenant_id:
            return {"error": "Tenant ID required"}
        
        result = await self.server_instance.traffic_cop_service.get_tenant_state_summary(
            tenant_id, user_context
        )
        return result
