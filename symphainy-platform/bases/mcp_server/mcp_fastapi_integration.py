#!/usr/bin/env python3
"""
MCP FastAPI Integration

Handles FastAPI app creation and required endpoint setup for MCP servers.

WHAT (Micro-Module Role): I provide FastAPI integration for MCP servers
HOW (Micro-Module Implementation): I create FastAPI apps and setup required endpoints
"""

from typing import Dict, Any, List, Callable
from fastapi import FastAPI
# FIX: Lazy import to avoid circular dependency
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService


class MCPFastAPIIntegration:
    """
    FastAPI integration for MCP servers.
    
    Handles FastAPI app creation and required endpoint setup per CTO guidance.
    """
    
    def __init__(self, di_container: 'DIContainerService', service_name: str):
        """Initialize FastAPI integration."""
        # FIX: Lazy import to avoid circular dependency
        from foundations.di_container.di_container_service import DIContainerService
        self.di_container = di_container
        self.service_name = service_name
        self.app = None
    
    def create_fastapi_app(self, title: str = None, description: str = None) -> FastAPI:
        """Create FastAPI app for MCP server."""
        app_title = title or f"{self.service_name} MCP Server"
        app_description = description or f"MCP server for {self.service_name} operations"
        
        self.app = self.di_container.create_fastapi_app(
            title=app_title,
            description=app_description
        )
        
        return self.app
    
    def setup_required_endpoints(self, mcp_server):
        """Setup required FastAPI endpoints per CTO guidance."""
        if not self.app:
            raise ValueError("FastAPI app must be created first")
        
        @self.app.get("/usage_guide")
        async def usage_guide():
            """Return machine + human readable usage guide."""
            return mcp_server.get_usage_guide()
            
        @self.app.get("/list_tools")
        async def list_tools():
            """Return list of available tool names."""
            return mcp_server.get_tool_list()
            
        @self.app.get("/health")
        async def health():
            """Return health status with upstream dependency checks."""
            return await mcp_server.get_health_status()
            
        @self.app.get("/version")
        async def version():
            """Return version and compatibility info."""
            return mcp_server.get_version_info()
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI app."""
        if not self.app:
            raise ValueError("FastAPI app not created yet")
        return self.app
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default FastAPI configuration."""
        return self.di_container.get_fastapi_default_config()




























