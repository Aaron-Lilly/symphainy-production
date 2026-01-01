#!/usr/bin/env python3
"""
Tool Factory Service - Enhanced Agentic Dimension

Enhanced tool factory service with existing infrastructure integration.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json

from foundations.public_works_foundation.abstractions.tool_registry_abstraction import ToolRegistryAbstraction
from foundations.public_works_foundation.abstractions.service_discovery_abstraction import ServiceDiscoveryAbstraction

logger = logging.getLogger(__name__)

class ToolNotFoundError(Exception):
    """Raised when a tool is not found in any domain."""
    pass

class ToolNotPublicError(Exception):
    """Raised when a tool is not publicly available."""
    pass

class ServiceNotAvailableError(Exception):
    """Raised when a domain manager service is not available."""
    pass

class ToolFactoryService:
    """
    Enhanced tool factory service with existing infrastructure integration.
    
    Provides comprehensive tool management for the agentic dimension:
    - Tool discovery and registration
    - MCP server integration
    - Tool analytics and monitoring
    """
    
    def __init__(self, service_name: str = "ToolFactoryService", 
                 tool_registry_abstraction: ToolRegistryAbstraction = None,
                 service_discovery_abstraction: ServiceDiscoveryAbstraction = None,
                 config=None):
        """
        Initialize the Tool Factory Service.
        
        Args:
            service_name: Name of the service
            tool_registry_abstraction: Tool registry business abstraction
            service_discovery_abstraction: Service discovery business abstraction
            config: Configuration object for dependency injection
        """
        self.service_name = service_name
        self.version = "3.0.0"
        
        # Business abstractions
        self.tool_registry = tool_registry_abstraction
        self.service_discovery = service_discovery_abstraction
        
        # MCP server integrations
        self.mcp_servers = {}
        
        # Tool discovery cache
        self.tool_cache = {}
        self.cache_ttl = 300  # 5 minutes TTL
        self.last_refresh = {}
        
        # Tool execution statistics
        self.execution_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "mcp_discoveries": 0
        }
        
        logger.info(f"Tool Factory Service {self.version} initialized with existing infrastructure integration")
    
    async def register_mcp_server(self, server_name: str, base_url: str, capabilities: List[str] = None):
        """Register an MCP server with the tool factory."""
        try:
            self.mcp_servers[server_name] = {
                "base_url": base_url,
                "capabilities": capabilities or [],
                "registered_at": datetime.utcnow().isoformat()
            }
            
            # Register with service discovery
            if self.service_discovery:
                await self.service_discovery.register_service({
                    "name": server_name,
                    "address": base_url.split("://")[1].split(":")[0],
                    "port": int(base_url.split(":")[-1]) if ":" in base_url else 8000,
                    "tags": ["mcp_server", "tool_provider"],
                    "meta": {
                        "capabilities": ",".join(capabilities or []),
                        "type": "mcp_server"
                    },
                    "health_check": {
                        "http": f"{base_url}/health",
                        "interval": "30s",
                        "timeout": "5s"
                    }
                })
            
            # Discover and register tools from MCP server
            await self._discover_and_register_mcp_tools(server_name, base_url)
            
            logger.info(f"Registered MCP server: {server_name} at {base_url}")
            
        except Exception as e:
            logger.error(f"Failed to register MCP server {server_name}: {e}")
            raise
    
    async def _discover_and_register_mcp_tools(self, server_name: str, base_url: str):
        """Discover and register tools from an MCP server."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Get tool list
                async with session.get(f"{base_url}/list_tools") as response:
                    if response.status == 200:
                        tool_list = await response.json()
                        
                        # Get usage guide for detailed tool information
                        async with session.get(f"{base_url}/usage_guide") as response:
                            if response.status == 200:
                                usage_guide = await response.json()
                                
                                # Register each tool
                                for tool_name in tool_list:
                                    await self._register_mcp_tool(
                                        server_name, base_url, tool_name, usage_guide
                                    )
                                
                                self.execution_stats["mcp_discoveries"] += 1
                                logger.info(f"Discovered and registered {len(tool_list)} tools from {server_name}")
                            else:
                                logger.error(f"Failed to get usage guide from {server_name}: {response.status}")
                    else:
                        logger.error(f"Failed to get tool list from {server_name}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error discovering tools from {server_name}: {e}")
    
    async def _register_mcp_tool(self, server_name: str, base_url: str, tool_name: str, usage_guide: Dict[str, Any]):
        """Register a single MCP tool."""
        try:
            # Extract tool information from usage guide
            tool_info = None
            for capability in usage_guide.get("capabilities", []):
                if capability.get("name") == tool_name:
                    tool_info = capability
                    break
            
            if not tool_info:
                logger.warning(f"Tool {tool_name} not found in usage guide for {server_name}")
                return
            
            # Extract schema
            schema = usage_guide.get("schemas", {}).get(tool_name, {})
            
            # Extract capabilities
            capabilities = tool_info.get("tags", [])
            
            # Register tool using business abstraction
            if self.tool_registry:
                result = await self.tool_registry.register_mcp_tool(
                    tool_name=tool_name,
                    description=tool_info.get("summary", ""),
                    schema=schema,
                    mcp_server=server_name,
                    capabilities=capabilities
                )
                
                if result["success"]:
                    logger.info(f"Registered MCP tool: {tool_name} from {server_name}")
                else:
                    logger.error(f"Failed to register MCP tool {tool_name}: {result.get('error')}")
                    
        except Exception as e:
            logger.error(f"Error registering MCP tool {tool_name}: {e}")
    
    async def discover_tools(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Discover tools using the registry."""
        try:
            if not self.tool_registry:
                return []
            
            if not filters:
                # Get all tools (would need to implement this in tool_registry_abstraction)
                return []
            
            # Apply filters
            if "capability" in filters:
                return await self.tool_registry.discover_tools_by_capability(filters["capability"])
            elif "mcp_server" in filters:
                return await self.tool_registry.discover_tools_by_mcp_server(filters["mcp_server"])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
            return []
    
    async def execute_tool(self, tool_name: str, context: Dict[str, Any] = None, requesting_agent: str = None) -> Dict[str, Any]:
        """Execute a tool by name."""
        try:
            self.execution_stats["total_calls"] += 1
            
            # Check cache first
            if self._is_cache_valid(tool_name):
                self.execution_stats["cache_hits"] += 1
                logger.debug(f"Cache hit for tool: {tool_name}")
                return await self.tool_cache[tool_name](context or {})
            
            self.execution_stats["cache_misses"] += 1
            logger.debug(f"Cache miss for tool: {tool_name}")
            
            # Find tool in registry
            tools = await self.discover_tools({"name": tool_name})
            
            if not tools:
                self.execution_stats["failed_calls"] += 1
                raise ToolNotFoundError(f"Tool {tool_name} not found in registry")
            
            tool = tools[0]
            mcp_server = tool.get("mcp_server")
            
            if not mcp_server or mcp_server not in self.mcp_servers:
                self.execution_stats["failed_calls"] += 1
                raise ServiceNotAvailableError(f"MCP server {mcp_server} not available")
            
            # Execute tool via MCP server
            result = await self._execute_mcp_tool(mcp_server, tool_name, context or {})
            
            # Cache the tool executor
            self.tool_cache[tool_name] = lambda ctx: self._execute_mcp_tool(mcp_server, tool_name, ctx)
            self.last_refresh[tool_name] = datetime.now()
            
            # Record tool usage
            if requesting_agent and self.tool_registry:
                await self.tool_registry.record_tool_usage(tool.get("_key", tool_name), requesting_agent, context or {})
            
            self.execution_stats["successful_calls"] += 1
            logger.info(f"Successfully executed tool {tool_name} via {mcp_server}")
            return result
            
        except Exception as e:
            self.execution_stats["failed_calls"] += 1
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    async def _execute_mcp_tool(self, mcp_server: str, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via MCP server."""
        try:
            import aiohttp
            
            server_info = self.mcp_servers[mcp_server]
            base_url = server_info["base_url"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{base_url}/tool/{tool_name}", json=context) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result", result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"MCP tool execution failed: {error_text}")
                        
        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name} on {mcp_server}: {e}")
            raise
    
    def _is_cache_valid(self, tool_name: str) -> bool:
        """Check if tool cache is valid."""
        if tool_name not in self.tool_cache:
            return False
        
        if tool_name not in self.last_refresh:
            return False
        
        cache_age = datetime.now() - self.last_refresh[tool_name]
        return cache_age.total_seconds() < self.cache_ttl
    
    async def get_registry_health(self) -> Dict[str, Any]:
        """Get comprehensive registry health status."""
        try:
            health_status = {
                "overall_health": "healthy",
                "tool_factory": {
                    "status": "healthy",
                    "mcp_servers": len(self.mcp_servers),
                    "cached_tools": len(self.tool_cache)
                },
                "infrastructure": {
                    "tool_registry": "available" if self.tool_registry else "unavailable",
                    "service_discovery": "available" if self.service_discovery else "unavailable"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting registry health: {e}")
            return {
                "overall_health": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        return {
            **self.execution_stats,
            "cache_hit_rate": (
                self.execution_stats["cache_hits"] / 
                max(1, self.execution_stats["cache_hits"] + self.execution_stats["cache_misses"])
            ),
            "success_rate": (
                self.execution_stats["successful_calls"] / 
                max(1, self.execution_stats["total_calls"])
            )
        }








