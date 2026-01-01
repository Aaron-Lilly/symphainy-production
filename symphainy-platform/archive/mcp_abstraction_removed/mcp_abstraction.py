#!/usr/bin/env python3
"""
MCP Abstraction - Layer 2 of 5-Layer Architecture

This abstraction provides infrastructure-level MCP capabilities by coordinating
MCP adapters and handling infrastructure concerns like connection pooling,
retry logic, and error handling.

WHAT (Infrastructure Role): I provide MCP infrastructure capabilities
HOW (Infrastructure Implementation): I coordinate MCP adapters and handle infrastructure concerns
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.mcp_protocol import MCPProtocol
from foundations.public_works_foundation.infrastructure_adapters.mcp_adapter import MCPAdapter


class MCPAbstraction(MCPProtocol):
    """
    MCP Infrastructure Abstraction.
    
    Provides infrastructure-level MCP capabilities by coordinating MCP adapters
    and handling infrastructure concerns like connection pooling, retry logic,
    and error handling.
    """
    
    def __init__(self, mcp_adapter: MCPAdapter):
        """Initialize MCP abstraction with MCP adapter."""
        self.mcp_adapter = mcp_adapter
        self.logger = logging.getLogger("MCPAbstraction")
        
        # Infrastructure configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        self.connection_pool_size = 10
        
        # Connection pool
        self.connection_pool: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("✅ MCP Infrastructure Abstraction initialized")
    
    async def connect_to_server(self, server_name: str, endpoint: str, 
                               tenant_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Connect to an MCP server with infrastructure-level handling.
        
        Args:
            server_name: Name of the server to connect to
            endpoint: Server endpoint URL
            tenant_context: Optional tenant context for multi-tenancy
            
        Returns:
            Dict containing connection result with success status and connection details
        """
        try:
            self.logger.info(f"🔌 Connecting to MCP server: {server_name}")
            
            # Check connection pool
            if server_name in self.connection_pool:
                self.logger.info(f"Using pooled connection for {server_name}")
                return {
                    "success": True,
                    "connection_id": self.connection_pool[server_name]["connection_id"],
                    "message": f"Using pooled connection for {server_name}"
                }
            
            # Attempt connection with retry logic
            for attempt in range(self.max_retries):
                try:
                    result = await self.mcp_adapter.connect_to_server(
                        server_name=server_name,
                        endpoint=endpoint,
                        tenant_context=tenant_context
                    )
                    
                    if result.get("success", False):
                        # Add to connection pool
                        self.connection_pool[server_name] = {
                            "connection_id": result.get("connection_id"),
                            "endpoint": endpoint,
                            "connected_at": datetime.now().isoformat(),
                            "tenant_context": tenant_context
                        }
                        
                        self.logger.info(f"✅ Connected to MCP server: {server_name}")
                        return result
                    else:
                        raise Exception(result.get("error", "Connection failed"))
                        
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"⚠️ Connection attempt {attempt + 1} failed for {server_name}: {e}")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    else:
                        raise e
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to MCP server {server_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to connect to {server_name} after {self.max_retries} attempts"
            }
    
    async def disconnect_from_server(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server with infrastructure-level handling.
        
        Args:
            server_name: Name of the server to disconnect from
            
        Returns:
            True if disconnected successfully, False otherwise
        """
        try:
            # Remove from connection pool
            if server_name in self.connection_pool:
                del self.connection_pool[server_name]
            
            # Disconnect from adapter
            result = await self.mcp_adapter.disconnect_from_server(server_name)
            
            self.logger.info(f"✅ Disconnected from MCP server: {server_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to disconnect from MCP server {server_name}: {e}")
            return False
    
    async def execute_tool(self, server_name: str, tool_name: str, 
                          parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on an MCP server with infrastructure-level handling.
        
        Args:
            server_name: Name of the server
            tool_name: Name of the tool to execute
            parameters: Parameters for tool execution
            
        Returns:
            Dict containing execution result with success status and result data
        """
        try:
            # Check if server is connected
            if server_name not in self.connection_pool:
                return {
                    "success": False,
                    "error": f"Server {server_name} not connected",
                    "message": "Server not in connection pool"
                }
            
            # Execute tool with retry logic
            for attempt in range(self.max_retries):
                try:
                    result = await self.mcp_adapter.execute_tool(
                        server_name=server_name,
                        tool_name=tool_name,
                        parameters=parameters
                    )
                    
                    if result.get("success", False):
                        self.logger.info(f"✅ Tool {tool_name} executed successfully on {server_name}")
                        return result
                    else:
                        raise Exception(result.get("error", "Tool execution failed"))
                        
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"⚠️ Tool execution attempt {attempt + 1} failed for {tool_name} on {server_name}: {e}")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    else:
                        raise e
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute tool {tool_name} on {server_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "server_name": server_name
            }
    
    async def get_server_health(self, server_name: str) -> Dict[str, Any]:
        """
        Get health status of an MCP server with infrastructure-level handling.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dict containing health status and details
        """
        try:
            # Check if server is in connection pool
            if server_name not in self.connection_pool:
                return {
                    "success": False,
                    "status": "not_connected",
                    "message": f"Server {server_name} not in connection pool"
                }
            
            # Get health from adapter
            result = await self.mcp_adapter.get_server_health(server_name)
            
            # Add infrastructure-level health information
            if result.get("success", False):
                result["infrastructure_status"] = "healthy"
                result["connection_pool_status"] = "active"
                result["pooled_at"] = self.connection_pool[server_name]["connected_at"]
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get health for {server_name}: {e}")
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "server_name": server_name
            }
    
    async def list_available_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List available tools on an MCP server with infrastructure-level handling.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of available tools with their descriptions
        """
        try:
            # Check if server is in connection pool
            if server_name not in self.connection_pool:
                self.logger.warning(f"⚠️ Server {server_name} not in connection pool")
                return []
            
            # Get tools from adapter
            tools = await self.mcp_adapter.list_available_tools(server_name)
            
            # Add infrastructure-level metadata
            for tool in tools:
                tool["infrastructure_managed"] = True
                tool["connection_pooled"] = True
            
            return tools
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list tools for {server_name}: {e}")
            return []
    
    async def get_server_capabilities(self, server_name: str) -> Dict[str, Any]:
        """
        Get capabilities of an MCP server with infrastructure-level handling.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dict containing server capabilities
        """
        try:
            # Check if server is in connection pool
            if server_name not in self.connection_pool:
                return {}
            
            # Get capabilities from adapter
            capabilities = await self.mcp_adapter.get_server_capabilities(server_name)
            
            # Add infrastructure-level capabilities
            capabilities["infrastructure_managed"] = True
            capabilities["connection_pooled"] = True
            capabilities["retry_enabled"] = True
            capabilities["max_retries"] = self.max_retries
            
            return capabilities
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get capabilities for {server_name}: {e}")
            return {}
    
    def get_connection_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status."""
        return {
            "pool_size": len(self.connection_pool),
            "max_pool_size": self.connection_pool_size,
            "connected_servers": list(self.connection_pool.keys()),
            "pool_utilization": len(self.connection_pool) / self.connection_pool_size,
            "status": "healthy"
        }
    
    def get_abstraction_health(self) -> Dict[str, Any]:
        """Get MCP abstraction health status."""
        return {
            "abstraction_name": "MCPAbstraction",
            "adapter_health": self.mcp_adapter.get_adapter_health(),
            "connection_pool_status": self.get_connection_pool_status(),
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "status": "healthy"
        }
