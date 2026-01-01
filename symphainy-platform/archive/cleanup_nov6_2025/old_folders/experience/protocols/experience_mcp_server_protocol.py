#!/usr/bin/env python3
"""
Experience MCP Server Protocol

Defines the standard protocol for Experience Dimension MCP servers.

WHAT (MCP Protocol): I define the standard structure for Experience MCP servers
HOW (Protocol): I follow MCP patterns with tools, resources, and agent communication
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.mcp_base import MCPBaseServer
from utilities import UserContext


class ExperienceMCPToolType(Enum):
    """Defines types of MCP tools for Experience services."""
    SESSION_MANAGEMENT = "session_management"
    UI_STATE_UPDATE = "ui_state_update"
    REAL_TIME_BROADCAST = "real_time_broadcast"
    FRONTEND_ROUTING = "frontend_routing"
    JOURNEY_TRACKING = "journey_tracking"
    FLOW_NAVIGATION = "flow_navigation"
    API_REQUEST_HANDLER = "api_request_handler"
    WEBSOCKET_MANAGER = "websocket_manager"
    
    def __str__(self):
        return self.value


class ExperienceMCPResourceType(Enum):
    """Defines types of MCP resources for Experience services."""
    SESSION_DATA = "session_data"
    UI_STATE = "ui_state"
    JOURNEY_DATA = "journey_data"
    FLOW_CONFIGURATION = "flow_configuration"
    API_ENDPOINTS = "api_endpoints"
    WEBSOCKET_CONNECTIONS = "websocket_connections"
    
    def __str__(self):
        return self.value


class ExperienceMCPServerProtocol(ABC):
    """
    Experience MCP Server Protocol
    
    Abstract base class that defines the standard protocol for Experience MCP servers.
    """
    
    def __init__(self, server_name: str, service_client, utility_foundation=None):
        """Initialize experience MCP server protocol."""
        self.server_name = server_name
        self.service_client = service_client
        self.utility_foundation = utility_foundation
        self.tools = []
        self.resources = []
        self.is_initialized = False
        
    @abstractmethod
    async def initialize_server(self):
        """Initialize the MCP server."""
        pass
    
    @abstractmethod
    async def register_tools(self):
        """Register MCP tools."""
        pass
    
    @abstractmethod
    async def register_resources(self):
        """Register MCP resources."""
        pass
    
    @abstractmethod
    async def handle_tool_call(self, tool_name: str, parameters: Dict[str, Any], 
                              user_context: UserContext) -> Dict[str, Any]:
        """Handle a tool call."""
        pass
    
    @abstractmethod
    async def handle_resource_request(self, resource_name: str, 
                                     user_context: UserContext) -> Dict[str, Any]:
        """Handle a resource request."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the MCP server."""
        pass


class ExperienceMCPServerBase(MCPBaseServer):
    """
    Experience MCP Server Base Class
    
    Base class for Experience MCP servers, providing common functionality
    and integration with foundation services.
    """
    
    def __init__(self, server_name: str, service_client, utility_foundation=None):
        """Initialize experience MCP server base."""
        super().__init__(server_name, "experience")
        self.service_client = service_client
        self.utility_foundation = utility_foundation
        self.tools = []
        self.resources = []
        self.is_initialized = False
        
    async def initialize_server(self):
        """Initialize the MCP server."""
        try:
            self.logger.info(f"🔧 Initializing {self.server_name}...")
            
            # Register tools
            await self.register_tools()
            
            # Register resources
            await self.register_resources()
            
            # Connect to service
            await self._connect_to_service()
            
            self.is_initialized = True
            self.logger.info(f"✅ {self.server_name} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.server_name}: {e}")
            raise
    
    async def register_tools(self):
        """Register MCP tools."""
        # Override in subclasses
        pass
    
    async def register_resources(self):
        """Register MCP resources."""
        # Override in subclasses
        pass
    
    async def _connect_to_service(self):
        """Connect to the underlying service."""
        # Override in subclasses
        pass
    
    async def handle_tool_call(self, tool_name: str, parameters: Dict[str, Any], 
                              user_context: UserContext) -> Dict[str, Any]:
        """Handle a tool call."""
        try:
            # Find the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                return {"success": False, "error": f"Tool '{tool_name}' not found"}
            
            # Execute the tool
            result = await self._execute_tool(tool, parameters, user_context)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Tool call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_tool(self, tool, parameters: Dict[str, Any], 
                           user_context: UserContext) -> Dict[str, Any]:
        """Execute a specific tool."""
        # Override in subclasses
        return {"success": True, "message": "Tool executed successfully"}
    
    async def handle_resource_request(self, resource_name: str, 
                                     user_context: UserContext) -> Dict[str, Any]:
        """Handle a resource request."""
        try:
            # Find the resource
            resource = next((r for r in self.resources if r.name == resource_name), None)
            if not resource:
                return {"success": False, "error": f"Resource '{resource_name}' not found"}
            
            # Get the resource data
            result = await self._get_resource_data(resource, user_context)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Resource request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_resource_data(self, resource, user_context: UserContext) -> Dict[str, Any]:
        """Get data for a specific resource."""
        # Override in subclasses
        return {"success": True, "data": {}}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the MCP server."""
        return {
            "server_name": self.server_name,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "service_connected": self.service_client is not None
        }
