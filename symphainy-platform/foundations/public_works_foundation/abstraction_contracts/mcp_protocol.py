#!/usr/bin/env python3
"""
MCP Protocol - Layer 0 of 5-Layer Architecture

Defines the contract for MCP (Model Context Protocol) infrastructure abstractions.
This protocol standardizes how MCP clients interact with role servers.

WHAT (Infrastructure Role): I define the contract for MCP communication
HOW (Infrastructure Implementation): I use protocols to ensure consistent interfaces
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime


class MCPProtocol(Protocol):
    """
    MCP Protocol - Contract for MCP infrastructure abstractions.
    
    Defines the standard interface for MCP client operations including
    server connections, tool execution, and health monitoring.
    """
    
    async def connect_to_server(self, server_name: str, endpoint: str, 
                               tenant_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Connect to an MCP server.
        
        Args:
            server_name: Name of the server to connect to
            endpoint: Server endpoint URL
            tenant_context: Optional tenant context for multi-tenancy
            
        Returns:
            Dict containing connection result with success status and connection details
        """
        ...
    
    async def disconnect_from_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server.
        
        Args:
            server_name: Name of the server to disconnect from
            
        Returns:
            True if disconnected successfully, False otherwise
        """
        ...
    
    async def execute_tool(self, server_name: str, tool_name: str, 
                          parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on an MCP server.
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to execute
            parameters: Parameters for tool execution
            
        Returns:
            Dict containing execution result with success status and result data
        """
        ...
    
    async def get_server_health(self, server_name: str) -> Dict[str, Any]:
        """
        Get health status of an MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dict containing health status and details
        """
        ...
    
    async def list_available_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List available tools on an MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of available tools with their descriptions
        """
        ...
    
    async def get_server_capabilities(self, server_name: str) -> Dict[str, Any]:
        """
        Get capabilities of an MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dict containing server capabilities
        """
        ...


