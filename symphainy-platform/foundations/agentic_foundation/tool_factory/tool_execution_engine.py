"""
Tool Execution Engine

This module handles tool execution across all domains, including
connection pooling, load balancing, and error handling.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import uuid

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""
    pass


class ToolExecutionEngine:
    """
    Engine for executing tools across all domains with connection
    pooling, load balancing, and comprehensive error handling.
    """
    
    def __init__(self, tool_factory_service):
        """
        Initialize the Tool Execution Engine.
        
        Args:
            tool_factory_service: Reference to the Tool Factory Service
        """
        self.tool_factory = tool_factory_service
        self.connection_pool = {}
        self.execution_queue = asyncio.Queue()
        self.active_executions = {}
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "concurrent_executions": 0
        }
        
        logger.info("Tool Execution Engine initialized")
    
    async def execute_tool(self, tool_info: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a tool with the given context.
        
        Args:
            tool_info: Tool information from discovery
            context: Context data for tool execution
            
        Returns:
            Tool execution result
            
        Raises:
            ToolExecutionError: If tool execution fails
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            self.execution_stats["total_executions"] += 1
            self.execution_stats["concurrent_executions"] += 1
            self.active_executions[execution_id] = {
                "tool_name": tool_info["tool_name"],
                "server": tool_info["server"],
                "domain": tool_info["domain"],
                "start_time": start_time
            }
            
            logger.debug(f"Executing tool {tool_info['tool_name']} on {tool_info['server']}")
            
            # Get MCP client for the tool's server
            server_client = await self._get_mcp_client(tool_info["server"])
            
            # Execute the tool
            result = await server_client.call_tool(tool_info["tool_name"], context or {})
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_execution_stats(execution_time, True)
            
            # Add execution metadata
            result["_execution_metadata"] = {
                "execution_id": execution_id,
                "tool_name": tool_info["tool_name"],
                "server": tool_info["server"],
                "domain": tool_info["domain"],
                "execution_time": execution_time,
                "executed_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully executed tool {tool_info['tool_name']} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_execution_stats(execution_time, False)
            
            logger.error(f"Failed to execute tool {tool_info['tool_name']}: {e}")
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")
            
        finally:
            # Clean up
            self.execution_stats["concurrent_executions"] -= 1
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def execute_tool_chain(self, tool_chain: List[Dict[str, Any]], initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a chain of tools in sequence.
        
        Args:
            tool_chain: List of tool information objects
            initial_context: Initial context data
            
        Returns:
            Final execution result
        """
        try:
            logger.debug(f"Executing tool chain with {len(tool_chain)} tools")
            
            context = initial_context or {}
            results = []
            
            for i, tool_info in enumerate(tool_chain):
                logger.debug(f"Executing tool {i+1}/{len(tool_chain)}: {tool_info['tool_name']}")
                
                # Execute the tool
                result = await self.execute_tool(tool_info, context)
                results.append(result)
                
                # Update context with result (for next tool in chain)
                context = self._merge_context_with_result(context, result)
            
            # Return final result with chain metadata
            final_result = {
                "chain_results": results,
                "final_context": context,
                "chain_metadata": {
                    "total_tools": len(tool_chain),
                    "execution_time": sum(
                        r.get("_execution_metadata", {}).get("execution_time", 0) 
                        for r in results
                    ),
                    "executed_at": datetime.now().isoformat()
                }
            }
            
            logger.info(f"Successfully executed tool chain with {len(tool_chain)} tools")
            return final_result
            
        except Exception as e:
            logger.error(f"Failed to execute tool chain: {e}")
            raise ToolExecutionError(f"Tool chain execution failed: {str(e)}")
    
    async def execute_tools_parallel(self, tools: List[Dict[str, Any]], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute multiple tools in parallel.
        
        Args:
            tools: List of tool information objects
            context: Context data for all tools
            
        Returns:
            List of execution results
        """
        try:
            logger.debug(f"Executing {len(tools)} tools in parallel")
            
            # Create execution tasks
            tasks = [
                self.execute_tool(tool_info, context)
                for tool_info in tools
            ]
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Tool {tools[i]['tool_name']} failed: {result}")
                    processed_results.append({
                        "error": str(result),
                        "tool_name": tools[i]["tool_name"],
                        "success": False
                    })
                else:
                    processed_results.append(result)
            
            logger.info(f"Completed parallel execution of {len(tools)} tools")
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to execute tools in parallel: {e}")
            raise ToolExecutionError(f"Parallel tool execution failed: {str(e)}")
    
    async def _get_mcp_client(self, server_name: str):
        """
        Get MCP client for a server with connection pooling.
        
        Args:
            server_name: Name of the server
            
        Returns:
            MCP client for the server
        """
        try:
            # Check connection pool first
            if server_name in self.connection_pool:
                client = self.connection_pool[server_name]
                if await self._is_client_healthy(client):
                    return client
                else:
                    # Remove unhealthy client
                    del self.connection_pool[server_name]
            
            # Create new client
            logger.debug(f"Creating new MCP client for {server_name}")
            client = await self._create_mcp_client(server_name)
            
            # Add to connection pool
            self.connection_pool[server_name] = client
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to get MCP client for {server_name}: {e}")
            raise ToolExecutionError(f"Failed to connect to server {server_name}: {str(e)}")
    
    async def _create_mcp_client(self, server_name: str):
        """
        Create a new MCP client for a server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            New MCP client
        """
        # TODO: Implement actual MCP client creation
        # This will be implemented when we have the MCP client infrastructure
        raise NotImplementedError("MCP client creation not yet implemented")
    
    async def _is_client_healthy(self, client) -> bool:
        """
        Check if an MCP client is healthy.
        
        Args:
            client: MCP client to check
            
        Returns:
            True if client is healthy
        """
        try:
            # Simple health check
            await client.health_check()
            return True
        except Exception:
            return False
    
    def _merge_context_with_result(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge context with tool execution result.
        
        Args:
            context: Current context
            result: Tool execution result
            
        Returns:
            Merged context
        """
        try:
            # Create new context with result data
            new_context = context.copy()
            
            # Add result data to context
            if "data" in result:
                new_context.update(result["data"])
            
            # Add result metadata
            new_context["_last_result"] = result
            
            return new_context
            
        except Exception as e:
            logger.error(f"Error merging context with result: {e}")
            return context
    
    def _update_execution_stats(self, execution_time: float, success: bool):
        """Update execution statistics."""
        if success:
            self.execution_stats["successful_executions"] += 1
        else:
            self.execution_stats["failed_executions"] += 1
        
        # Update average execution time
        total_executions = self.execution_stats["total_executions"]
        current_avg = self.execution_stats["average_execution_time"]
        self.execution_stats["average_execution_time"] = (
            (current_avg * (total_executions - 1) + execution_time) / total_executions
        )
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "execution_stats": self.execution_stats.copy(),
            "active_executions": len(self.active_executions),
            "connection_pool_size": len(self.connection_pool),
            "active_execution_details": [
                {
                    "execution_id": exec_id,
                    "tool_name": details["tool_name"],
                    "server": details["server"],
                    "domain": details["domain"],
                    "duration": (datetime.now() - details["start_time"]).total_seconds()
                }
                for exec_id, details in self.active_executions.items()
            ]
        }
    
    def clear_connection_pool(self):
        """Clear the connection pool."""
        self.connection_pool.clear()
        logger.info("Connection pool cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Check connection pool health
            healthy_connections = 0
            for server_name, client in self.connection_pool.items():
                if await self._is_client_healthy(client):
                    healthy_connections += 1
            
            return {
                "status": "healthy",
                "total_connections": len(self.connection_pool),
                "healthy_connections": healthy_connections,
                "active_executions": len(self.active_executions),
                "execution_stats": self.execution_stats
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "execution_stats": self.execution_stats
            }






