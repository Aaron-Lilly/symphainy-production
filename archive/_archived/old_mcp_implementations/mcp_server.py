"""
Public Works MCP Server Implementation

Exposes 17 infrastructure tools that enable all domain MCP servers.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
    Tool, TextContent
)

# Import the base class
from common.utilities.domain_bases import InfrastructureMCPBase

from .public_works_server import public_works_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PublicWorksMCPServer")

class PublicWorksMCPServer(InfrastructureMCPBase):
    """Public Works MCP Server that exposes 17 infrastructure tools."""
    
    def __init__(self):
        # Initialize base class with service name and domain
        super().__init__("public_works_mcp", "infrastructure")
        
        # Create MCP server instance
        self.server = Server("public-works-mcp-server")
        self.public_works_server = public_works_server
        
        # Setup MCP handlers
        self._setup_handlers()
        
        logger.info("Public Works MCP Server initialized with InfrastructureMCPBase")
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all 17 infrastructure tools."""
            return self._get_tools()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls by delegating to Public Works server."""
            try:
                result = await self.public_works_server.handle_tool_call(name, arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result))]
                )
            except Exception as e:
                logger.error(f"Tool call failed: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
                )
    
    def _get_tools(self) -> List[Tool]:
        """Get the list of 17 infrastructure tools."""
        return [
            # Smart City MCP Server Infrastructure Tools
            Tool(
                name="data_steward_infrastructure",
                description="Enable infrastructure for Data Steward MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "data_steward"}
                    }
                }
            ),
            Tool(
                name="librarian_infrastructure",
                description="Enable infrastructure for Librarian MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "librarian"}
                    }
                }
            ),
            Tool(
                name="traffic_cop_infrastructure",
                description="Enable infrastructure for Traffic Cop MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "traffic_cop"}
                    }
                }
            ),
            Tool(
                name="post_office_infrastructure",
                description="Enable infrastructure for Post Office MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "post_office"}
                    }
                }
            ),
            Tool(
                name="security_guard_infrastructure",
                description="Enable infrastructure for Security Guard MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "security_guard"}
                    }
                }
            ),
            Tool(
                name="nurse_infrastructure",
                description="Enable infrastructure for Nurse MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "nurse"}
                    }
                }
            ),
            Tool(
                name="conductor_infrastructure",
                description="Enable infrastructure for Conductor MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "conductor"}
                    }
                }
            ),
            Tool(
                name="curator_infrastructure",
                description="Enable infrastructure for Curator MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "curator"}
                    }
                }
            ),
            Tool(
                name="city_manager_infrastructure",
                description="Enable infrastructure for City Manager MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "default": "city_manager"}
                    }
                }
            ),
            # Business Pillar Infrastructure Tools
            Tool(
                name="content_pillar_infrastructure",
                description="Enable infrastructure for Content Pillar MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "default": "content_pillar"}
                    }
                }
            ),
            Tool(
                name="insights_pillar_infrastructure",
                description="Enable infrastructure for Insights Pillar MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "default": "insights_pillar"}
                    }
                }
            ),
            Tool(
                name="operations_pillar_infrastructure",
                description="Enable infrastructure for Operations Pillar MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "default": "operations_pillar"}
                    }
                }
            ),
            Tool(
                name="business_outcomes_pillar_infrastructure",
                description="Enable infrastructure for Business Outcomes Pillar MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "default": "business_outcomes_pillar"}
                    }
                }
            ),
            Tool(
                name="experience_pillar_infrastructure",
                description="Enable infrastructure for Experience Pillar MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "default": "experience_pillar"}
                    }
                }
            ),
            Tool(
                name="delivery_manager_infrastructure",
                description="Enable infrastructure for Delivery Manager MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillar": {"type": "string", "default": "delivery_manager"}
                    }
                }
            ),
            # Core 4 Infrastructure Tools
            Tool(
                name="file_broker_infrastructure",
                description="Enable infrastructure for File Broker MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "broker": {"type": "string", "default": "file_broker"}
                    }
                }
            ),
            Tool(
                name="database_broker_infrastructure",
                description="Enable infrastructure for Database Broker MCP Server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "broker": {"type": "string", "default": "database_broker"}
                    }
                }
            )
        ]

# Create the MCP server instance
server_instance = PublicWorksMCPServer()
server = server_instance.server

# Main entry point for MCP server
if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
