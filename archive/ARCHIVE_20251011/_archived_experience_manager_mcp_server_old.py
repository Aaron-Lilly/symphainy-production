#!/usr/bin/env python3
"""
Experience Manager MCP Server

MCP server for the Experience Manager service, exposing experience management
capabilities as MCP tools for agentic communication.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.mcp_base import MCPBaseServer

logger = logging.getLogger(__name__)


class ExperienceManagerMCPServer(MCPBaseServer):
    """MCP Server for Experience Manager service."""
    
    def __init__(self):
        super().__init__(
            service_name="experience_manager_mcp",
            domain="experience"
        )
        self._service = None
    
    @property
    def experience_service(self):
        """Lazy load the experience manager service to avoid circular imports."""
        if self._service is None:
            from .experience_manager_service import experience_manager_service
            self._service = experience_manager_service
        return self._service
    
    async def initialize_service_integration(self):
        """Initialize integration with the Experience Manager service."""
        logger.info("🔗 Initializing Experience Manager service integration...")
        # The service is available via self.experience_service
        logger.info("✅ Experience Manager service integration initialized")
        
    async def register_tools(self):
        """Register MCP tools for experience management."""
        logger.info("🔧 Registering Experience Manager MCP tools...")
        
        # Session management tools
        await self.add_tool(
            name="initialize_experience_session",
            description="Initialize a new experience session for a user",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "session_type": {"type": "string"},
                    "context": {"type": "object"}
                },
                "required": ["user_id", "session_type"]
            }
        )
        
        await self.add_tool(
            name="get_session_state",
            description="Get the current state of an experience session",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            }
        )
        
        await self.add_tool(
            name="update_session_state",
            description="Update the state of an experience session",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "state": {"type": "object"}
                },
                "required": ["session_id", "state"]
            }
        )
        
        await self.add_tool(
            name="terminate_experience_session",
            description="Terminate an experience session",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            }
        )
        
        # UI state management tools
        await self.add_tool(
            name="manage_user_interface_state",
            description="Manage user interface state",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "ui_state": {"type": "object"}
                },
                "required": ["session_id", "ui_state"]
            }
        )
        
        # Real-time coordination tools
        await self.add_tool(
            name="manage_real_time_coordination",
            description="Manage real-time coordination between components",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "coordination_data": {"type": "object"}
                },
                "required": ["session_id", "coordination_data"]
            }
        )
        
        await self.add_tool(
            name="broadcast_real_time_update",
            description="Broadcast real-time updates to connected clients",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "update_data": {"type": "object"}
                },
                "required": ["session_id", "update_data"]
            }
        )
        
        # Frontend-backend integration tools
        await self.add_tool(
            name="coordinate_frontend_backend_integration",
            description="Coordinate frontend-backend integration",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "integration_data": {"type": "object"}
                },
                "required": ["session_id", "integration_data"]
            }
        )
        
        await self.add_tool(
            name="route_pillar_request",
            description="Route requests to appropriate business pillars",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "pillar": {"type": "string"},
                    "request_data": {"type": "object"}
                },
                "required": ["session_id", "pillar", "request_data"]
            }
        )
        
        # WebSocket management tools
        await self.add_tool(
            name="handle_websocket_connection",
            description="Handle WebSocket connections for real-time communication",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "connection_data": {"type": "object"}
                },
                "required": ["session_id", "connection_data"]
            }
        )
        
        await self.add_tool(
            name="get_available_pillars",
            description="Get list of available business pillars",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        logger.info("✅ Registered 11 Experience Manager MCP tools")
    
    async def register_resources(self):
        """Register MCP resources for experience management."""
        logger.info("🔧 Registering Experience Manager MCP resources...")
        
        await self.add_resource(
            uri="session_data",
            name="Session Data",
            description="Current session data and state",
            mime_type="application/json"
        )
        
        await self.add_resource(
            uri="ui_state",
            name="UI State",
            description="Current user interface state",
            mime_type="application/json"
        )
        
        await self.add_resource(
            uri="real_time_events",
            name="Real-Time Events",
            description="Real-time events and updates",
            mime_type="application/json"
        )
        
        await self.add_resource(
            uri="pillar_status",
            name="Pillar Status",
            description="Status of business pillars",
            mime_type="application/json"
        )
        
        await self.add_resource(
            uri="websocket_connections",
            name="WebSocket Connections",
            description="Active WebSocket connections",
            mime_type="application/json"
        )
        
        logger.info("✅ Registered 5 Experience Manager MCP resources")
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls."""
        try:
            if name == "initialize_experience_session":
                return await self.experience_service.initialize_session(arguments)
            elif name == "get_session_state":
                return await self.experience_service.get_session_state(arguments)
            elif name == "update_session_state":
                return await self.experience_service.update_session_state(arguments)
            elif name == "terminate_experience_session":
                return await self.experience_service.terminate_session(arguments)
            elif name == "manage_user_interface_state":
                return await self.experience_service.manage_ui_state(arguments)
            elif name == "manage_real_time_coordination":
                return await self.experience_service.coordinate_real_time(arguments)
            elif name == "broadcast_real_time_update":
                return await self.experience_service.broadcast_update(arguments)
            elif name == "coordinate_frontend_backend_integration":
                return await self.experience_service.coordinate_integration(arguments)
            elif name == "route_pillar_request":
                return await self.experience_service.route_pillar_request(arguments)
            elif name == "handle_websocket_connection":
                return await self.experience_service.handle_websocket(arguments)
            elif name == "get_available_pillars":
                return await self.experience_service.get_available_pillars(arguments)
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            logger.error(f"Error handling tool call {name}: {e}")
            return {"error": str(e)}
    
    async def handle_resource_read(self, uri: str) -> str:
        """Handle MCP resource reads."""
        try:
            if uri == "session_data":
                return await self.experience_service.get_session_data()
            elif uri == "ui_state":
                return await self.experience_service.get_ui_state()
            elif uri == "real_time_events":
                return await self.experience_service.get_real_time_events()
            elif uri == "pillar_status":
                return await self.experience_service.get_pillar_status()
            elif uri == "websocket_connections":
                return await self.experience_service.get_websocket_connections()
            else:
                return "Resource not found"
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return f"Error: {str(e)}"


# Create and export the MCP server instance
experience_manager_mcp_server = ExperienceManagerMCPServer()

if __name__ == "__main__":
    asyncio.run(experience_manager_mcp_server.run())
