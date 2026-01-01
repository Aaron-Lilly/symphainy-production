"""
Tool Factory Service

This service provides cross-domain tool discovery and execution by leveraging
sophisticated pattern exposure logic to query domain managers for publicly
available tools and executing them on their original servers.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json

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
    Tool factory that leverages sophisticated pattern exposure logic to query
    domain managers for publicly available tools and provides a unified API
    for tool discovery and execution.
    """
    
    def __init__(self, service_name: str = "ToolFactoryService", city_manager_client=None, pattern_exposure_logic=None, config=None):
        """
        Initialize the Tool Factory Service.
        
        Args:
            service_name: Name of the service
            city_manager_client: MCP client for City Manager
            pattern_exposure_logic: Pattern exposure logic instance
            config: Configuration object for dependency injection
        """
        self.service_name = "ToolFactoryService"
        self.version = "2.0.0"
        
        # City Manager client for sophisticated pattern exposure
        self.city_manager_client = city_manager_client
        self.pattern_exposure_logic = pattern_exposure_logic
        
        # Domain managers (populated as they become available)
        self.domain_managers = {}
        
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
            "pattern_exposure_calls": 0
        }
        
        logger.info(f"Tool Factory Service {self.version} initialized with sophisticated pattern exposure")
    
    def register_domain_manager(self, domain: str, manager_client):
        """
        Register a domain manager client.
        
        Args:
            domain: Domain name (e.g., "smart_city", "business_pillars")
            manager_client: MCP client for the domain manager
        """
        self.domain_managers[domain] = manager_client
        logger.info(f"Registered domain manager: {domain}")
    
    async def get_tool(self, tool_name: str, context: Dict[str, Any] = None, requesting_server: str = None) -> Dict[str, Any]:
        """
        Get any publicly available tool from any domain using sophisticated pattern exposure logic.
        
        Args:
            tool_name: Name of the tool to execute
            context: Context data for tool execution
            requesting_server: Server requesting the tool (for access control)
            
        Returns:
            Tool execution result
            
        Raises:
            ToolNotFoundError: If tool is not found in any domain
        """
        try:
            self.execution_stats["total_calls"] += 1
            
            # Check cache first
            if self._is_cache_valid(tool_name):
                self.execution_stats["cache_hits"] += 1
                logger.debug(f"Cache hit for tool: {tool_name}")
                return await self.tool_cache[tool_name](context or {})
            
            self.execution_stats["cache_misses"] += 1
            logger.debug(f"Cache miss for tool: {tool_name}")
            
            # Use sophisticated pattern exposure logic if available
            if self.pattern_exposure_logic:
                self.execution_stats["pattern_exposure_calls"] += 1
                logger.debug(f"Using sophisticated pattern exposure logic for tool: {tool_name}")
                
                # Get publicly available tools using pattern exposure logic
                public_tools = await self.pattern_exposure_logic.get_public_tools(requesting_server)
                
                # Find the specific tool
                tool_info = None
                for tool in public_tools:
                    if tool.get("tool_name") == tool_name:
                        tool_info = tool
                        break
                
                if tool_info:
                    # Cache the tool executor
                    self.tool_cache[tool_name] = self._create_tool_executor(tool_info)
                    self.last_refresh[tool_name] = datetime.now()
                    
                    # Execute the tool
                    result = await self.tool_cache[tool_name](context or {})
                    self.execution_stats["successful_calls"] += 1
                    
                    logger.info(f"Successfully executed tool {tool_name} using pattern exposure logic")
                    return result
            
            # Fallback to domain managers if pattern exposure logic not available
            for domain, manager in self.domain_managers.items():
                try:
                    logger.debug(f"Querying {domain} for tool: {tool_name}")
                    tool_info = await manager.get_public_tool(tool_name)
                    
                    if tool_info:
                        # Cache the tool executor
                        self.tool_cache[tool_name] = self._create_tool_executor(tool_info)
                        self.last_refresh[tool_name] = datetime.now()
                        
                        # Execute the tool
                        result = await self.tool_cache[tool_name](context or {})
                        self.execution_stats["successful_calls"] += 1
                        
                        logger.info(f"Successfully executed tool {tool_name} from {domain}")
                        return result
                        
                except ToolNotPublicError:
                    logger.debug(f"Tool {tool_name} not public in {domain}")
                    continue
                except ServiceNotAvailableError:
                    logger.warning(f"Domain manager {domain} not available")
                    continue
                except Exception as e:
                    logger.error(f"Error querying {domain} for tool {tool_name}: {e}")
                    continue
            
            # Tool not found in any domain
            self.execution_stats["failed_calls"] += 1
            raise ToolNotFoundError(f"Tool {tool_name} not publicly available in any domain")
            
        except Exception as e:
            self.execution_stats["failed_calls"] += 1
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    async def execute_tool(self, tool_name: str, context: Dict[str, Any] = None, requesting_server: str = None) -> Dict[str, Any]:
        """
        Execute a tool by name (convenience wrapper around get_tool).
        
        Args:
            tool_name: Name of the tool to execute
            context: Context data for tool execution
            requesting_server: Server requesting the tool (for access control)
            
        Returns:
            Tool execution result
            
        Raises:
            ToolNotFoundError: If tool is not found in any domain
        """
        try:
            # Use the existing get_tool method
            result = await self.get_tool(tool_name, context, requesting_server)
            
            # Add execution metadata
            if isinstance(result, dict):
                result["_execution_metadata"] = {
                    "tool_name": tool_name,
                    "executed_via": "execute_tool",
                    "requesting_server": requesting_server,
                    "timestamp": datetime.now().isoformat()
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    async def discover_tools(self, criteria: Dict[str, Any] = None, requesting_server: str = None) -> List[Dict[str, Any]]:
        """
        Discover publicly available tools by criteria using sophisticated pattern exposure logic.
        
        Args:
            criteria: Search criteria (domain, capability, etc.)
            requesting_server: Server requesting tools (for access control)
            
        Returns:
            List of available tools
        """
        try:
            criteria = criteria or {}
            all_tools = []
            
            logger.debug(f"Discovering tools with criteria: {criteria}")
            
            # Use sophisticated pattern exposure logic if available
            if self.pattern_exposure_logic:
                self.execution_stats["pattern_exposure_calls"] += 1
                logger.debug("Using sophisticated pattern exposure logic for tool discovery")
                
                # Get publicly available tools using pattern exposure logic
                public_tools = await self.pattern_exposure_logic.get_public_tools(requesting_server)
                
                # Apply criteria filtering
                filtered_tools = self._filter_tools_by_criteria(public_tools, criteria)
                all_tools.extend(filtered_tools)
                
                logger.info(f"Discovered {len(filtered_tools)} tools using pattern exposure logic")
                return filtered_tools
            
            # Fallback to domain managers if pattern exposure logic not available
            for domain, manager in self.domain_managers.items():
                try:
                    tools = await manager.get_public_tools(criteria)
                    all_tools.extend(tools)
                    logger.debug(f"Found {len(tools)} tools in {domain}")
                    
                except ServiceNotAvailableError:
                    logger.warning(f"Domain manager {domain} not available for discovery")
                    continue
                except Exception as e:
                    logger.error(f"Error discovering tools in {domain}: {e}")
                    continue
            
            logger.info(f"Discovered {len(all_tools)} tools total")
            return all_tools
            
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
            return []
    
    async def get_tool_info(self, tool_name: str, requesting_server: str = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific tool using sophisticated pattern exposure logic.
        
        Args:
            tool_name: Name of the tool
            requesting_server: Server requesting tool info (for access control)
            
        Returns:
            Tool information or None if not found
        """
        try:
            # Use sophisticated pattern exposure logic if available
            if self.pattern_exposure_logic:
                logger.debug(f"Using sophisticated pattern exposure logic for tool info: {tool_name}")
                
                # Get publicly available tools using pattern exposure logic
                public_tools = await self.pattern_exposure_logic.get_public_tools(requesting_server)
                
                # Find the specific tool
                for tool in public_tools:
                    if tool.get("tool_name") == tool_name:
                        return tool
                
                return None
            
            # Fallback to domain managers if pattern exposure logic not available
            for domain, manager in self.domain_managers.items():
                try:
                    tool_info = await manager.get_public_tool(tool_name)
                    if tool_info:
                        return tool_info
                except (ToolNotPublicError, ServiceNotAvailableError):
                    continue
                except Exception as e:
                    logger.error(f"Error getting tool info from {domain}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting tool info for {tool_name}: {e}")
            return None
    
    async def get_domain_tools(self, domain: str, requesting_server: str = None) -> List[Dict[str, Any]]:
        """
        Get all tools from a specific domain using sophisticated pattern exposure logic.
        
        Args:
            domain: Domain name
            requesting_server: Server requesting tools (for access control)
            
        Returns:
            List of tools from the domain
        """
        try:
            # Use sophisticated pattern exposure logic if available
            if self.pattern_exposure_logic:
                logger.debug(f"Using sophisticated pattern exposure logic for domain tools: {domain}")
                
                # Get publicly available tools using pattern exposure logic
                public_tools = await self.pattern_exposure_logic.get_public_tools(requesting_server)
                
                # Filter by domain
                domain_tools = [tool for tool in public_tools if tool.get("domain") == domain]
                
                logger.info(f"Found {len(domain_tools)} tools in {domain} using pattern exposure logic")
                return domain_tools
            
            # Fallback to domain managers if pattern exposure logic not available
            if domain not in self.domain_managers:
                logger.warning(f"Domain {domain} not registered")
                return []
            
            manager = self.domain_managers[domain]
            tools = await manager.get_public_tools({})
            
            logger.info(f"Found {len(tools)} tools in {domain}")
            return tools
            
        except Exception as e:
            logger.error(f"Error getting tools from {domain}: {e}")
            return []
    
    def _filter_tools_by_criteria(self, tools: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter tools by search criteria.
        
        Args:
            tools: List of tools to filter
            criteria: Search criteria
            
        Returns:
            Filtered list of tools
        """
        try:
            filtered_tools = tools
            
            # Filter by domain
            if "domain" in criteria and criteria["domain"]:
                filtered_tools = [tool for tool in filtered_tools if tool.get("domain") == criteria["domain"]]
            
            # Filter by capability
            if "capability" in criteria and criteria["capability"]:
                capability = criteria["capability"].lower()
                filtered_tools = [
                    tool for tool in filtered_tools
                    if capability in tool.get("description", "").lower() or
                       capability in tool.get("tool_name", "").lower()
                ]
            
            # Filter by server
            if "server" in criteria and criteria["server"]:
                filtered_tools = [tool for tool in filtered_tools if tool.get("server") == criteria["server"]]
            
            # Filter by access level
            if "access_level" in criteria and criteria["access_level"]:
                filtered_tools = [tool for tool in filtered_tools if tool.get("access_level") == criteria["access_level"]]
            
            return filtered_tools
            
        except Exception as e:
            logger.error(f"Error filtering tools by criteria: {e}")
            return tools
    
    def _is_cache_valid(self, tool_name: str) -> bool:
        """Check if cached tool is still valid."""
        if tool_name not in self.tool_cache:
            return False
        
        if tool_name not in self.last_refresh:
            return False
        
        age = datetime.now() - self.last_refresh[tool_name]
        return age < timedelta(seconds=self.cache_ttl)
    
    def _create_tool_executor(self, tool_info: Dict[str, Any]):
        """Create a tool executor function."""
        async def executor(context: Dict[str, Any]) -> Dict[str, Any]:
            """Execute the tool with the given context."""
            try:
                # Get MCP client for the tool's server
                server_client = await self._get_mcp_client(tool_info["server"])
                
                # Execute the tool
                result = await server_client.call_tool(tool_info["tool_name"], context)
                
                # Add metadata
                result["_metadata"] = {
                    "tool_name": tool_info["tool_name"],
                    "server": tool_info["server"],
                    "domain": tool_info["domain"],
                    "executed_at": datetime.now().isoformat()
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_info['tool_name']}: {e}")
                raise
        
        return executor
    
    async def _get_mcp_client(self, server_name: str):
        """Get MCP client for a server (placeholder for now)."""
        # TODO: Implement MCP client factory
        # This will be implemented when we have the MCP client infrastructure
        raise NotImplementedError("MCP client factory not yet implemented")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tool factory statistics."""
        return {
            "service_name": self.service_name,
            "version": self.version,
            "pattern_exposure_available": self.pattern_exposure_logic is not None,
            "city_manager_available": self.city_manager_client is not None,
            "registered_domains": list(self.domain_managers.keys()),
            "cached_tools": len(self.tool_cache),
            "execution_stats": self.execution_stats.copy(),
            "cache_ttl": self.cache_ttl
        }
    
    def clear_cache(self):
        """Clear the tool cache."""
        self.tool_cache.clear()
        self.last_refresh.clear()
        logger.info("Tool cache cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Check domain manager availability
            domain_status = {}
            for domain, manager in self.domain_managers.items():
                try:
                    # Simple ping to check availability
                    await manager.health_check()
                    domain_status[domain] = "healthy"
                except Exception as e:
                    domain_status[domain] = f"unhealthy: {str(e)}"
            
            return {
                "status": "healthy",
                "service_name": self.service_name,
                "version": self.version,
                "domain_status": domain_status,
                "cached_tools": len(self.tool_cache),
                "execution_stats": self.execution_stats
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "service_name": self.service_name,
                "version": self.version
            }


# Global tool factory instance
_tool_factory = None


def get_tool_factory(city_manager_client=None, pattern_exposure_logic=None) -> ToolFactoryService:
    """Get the global tool factory instance."""
    global _tool_factory
    if _tool_factory is None:
        _tool_factory = ToolFactoryService(
            city_manager_client=city_manager_client,
            pattern_exposure_logic=pattern_exposure_logic
        )
    return _tool_factory
