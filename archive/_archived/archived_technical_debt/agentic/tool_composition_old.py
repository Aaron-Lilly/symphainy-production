"""
Tool Composition - Tool Chaining and Orchestration

Provides tool chaining and orchestration capabilities for agent execution.
Manages tool dependencies, execution order, and result aggregation.
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from utilities import get_logging_service, get_error_handler


class ToolComposition:
    """
    Manages tool chaining and orchestration for agent execution.
    
    Provides:
    - Tool dependency resolution
    - Execution order optimization
    - Result aggregation and transformation
    - Error handling and recovery
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize tool composition."""
        self.logger = get_logging_service("tool_composition")
        self.error_handler = get_error_handler("tool_composition")
        
        # Tool registry and dependencies
        self.tool_registry = {}
        self.tool_dependencies = {}
        
        # Execution history
        self.execution_history = []
        
        self.logger.info("Tool Composition initialized")
    
    async def execute_tool_chain(self, tool_chain: List[str], context: Dict[str, Any], 
                                role_connections: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """
        Execute a chain of tools with proper orchestration.
        
        Args:
            tool_chain: List of tools to execute
            context: Execution context
            role_connections: Smart City role connections
            agent_id: Agent identifier
            
        Returns:
            Dict containing aggregated execution results
        """
        try:
            execution_id = f"exec_{int(datetime.now().timestamp())}"
            self.logger.info(f"Starting tool chain execution: {execution_id}")
            
            # Resolve tool dependencies and execution order
            ordered_tools = await self._resolve_tool_dependencies(tool_chain)
            
            # Execute tools in order
            execution_results = {}
            execution_metadata = {
                "execution_id": execution_id,
                "agent_id": agent_id,
                "start_time": datetime.now().isoformat(),
                "tools_executed": [],
                "errors": []
            }
            
            for tool in ordered_tools:
                try:
                    tool_result = await self._execute_single_tool(
                        tool, context, role_connections, execution_results
                    )
                    execution_results[tool] = tool_result
                    execution_metadata["tools_executed"].append(tool)
                    
                except Exception as e:
                    error_msg = f"Tool {tool} execution failed: {e}"
                    self.logger.error(error_msg)
                    execution_metadata["errors"].append(error_msg)
                    
                    # Decide whether to continue or fail
                    if await self._should_continue_on_error(tool, e):
                        execution_results[tool] = {"error": str(e), "status": "failed"}
                    else:
                        raise
            
            # Aggregate results
            aggregated_results = await self._aggregate_results(execution_results, context)
            
            # Record execution metadata
            execution_metadata.update({
                "end_time": datetime.now().isoformat(),
                "success": len(execution_metadata["errors"]) == 0,
                "total_tools": len(ordered_tools),
                "successful_tools": len(execution_metadata["tools_executed"])
            })
            
            # Store execution history
            self.execution_history.append(execution_metadata)
            
            self.logger.info(f"Tool chain execution completed: {execution_id}")
            
            return {
                "success": execution_metadata["success"],
                "results": aggregated_results,
                "metadata": execution_metadata,
                "execution_id": execution_id
            }
            
        except Exception as e:
            self.logger.error(f"Tool chain execution failed: {e}")
            self.error_handler.handle_error(e, "tool_chain_execution_failed")
            raise
    
    async def _resolve_tool_dependencies(self, tool_chain: List[str]) -> List[str]:
        """Resolve tool dependencies and determine execution order."""
        try:
            # Simple dependency resolution for now
            # In real implementation, this would use a dependency graph
            ordered_tools = []
            remaining_tools = tool_chain.copy()
            
            while remaining_tools:
                # Find tools with no unresolved dependencies
                ready_tools = []
                for tool in remaining_tools:
                    dependencies = self.tool_dependencies.get(tool, [])
                    if all(dep in ordered_tools for dep in dependencies):
                        ready_tools.append(tool)
                
                if not ready_tools:
                    # Circular dependency or missing dependency
                    self.logger.warning(f"Could not resolve dependencies for: {remaining_tools}")
                    ordered_tools.extend(remaining_tools)
                    break
                
                # Add ready tools to execution order
                ordered_tools.extend(ready_tools)
                for tool in ready_tools:
                    remaining_tools.remove(tool)
            
            return ordered_tools
            
        except Exception as e:
            self.logger.error(f"Failed to resolve tool dependencies: {e}")
            return tool_chain  # Fallback to original order
    
    async def _execute_single_tool(self, tool: str, context: Dict[str, Any], 
                                 role_connections: Dict[str, Any], 
                                 previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool."""
        try:
            # Determine which role should execute this tool
            role = await self._determine_tool_role(tool)
            
            if role not in role_connections:
                raise ValueError(f"No connection to role {role} for tool {tool}")
            
            # Prepare tool parameters
            parameters = await self._prepare_tool_parameters(tool, context, previous_results)
            
            # Execute tool via role connection
            # In real implementation, this would call actual MCP tool
            result = await self._simulate_tool_execution(tool, role, parameters)
            
            self.logger.info(f"Tool {tool} executed successfully via {role}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute tool {tool}: {e}")
            raise
    
    async def _determine_tool_role(self, tool: str) -> str:
        """Determine which Smart City role should execute the tool."""
        # Tool to role mapping
        tool_role_mapping = {
            "store_document": "librarian",
            "retrieve_document": "librarian",
            "search_documents": "librarian",
            "assess_data_quality": "data_steward",
            "manage_data_lifecycle": "data_steward",
            "create_workflow": "conductor",
            "execute_workflow": "conductor",
            "send_message": "post_office",
            "format_outputs": "post_office",
            "authenticate_user": "security_guard",
            "authorize_action": "security_guard",
            "monitor_health": "nurse",
            "collect_telemetry": "nurse",
            "enforce_policies": "city_manager",
            "manage_governance": "city_manager",
            "manage_sessions": "traffic_cop",
            "coordinate_requests": "traffic_cop"
        }
        
        return tool_role_mapping.get(tool, "conductor")  # Default to conductor
    
    async def _prepare_tool_parameters(self, tool: str, context: Dict[str, Any], 
                                     previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for tool execution."""
        try:
            parameters = context.copy()
            
            # Add results from previous tools as needed
            if tool in ["format_outputs", "send_message"] and previous_results:
                parameters["previous_results"] = previous_results
            
            # Add tool-specific parameters
            if tool == "assess_data_quality" and "data" in context:
                parameters["data_sample"] = context["data"][:100]  # Sample for quality assessment
            
            return parameters
            
        except Exception as e:
            self.logger.error(f"Failed to prepare parameters for tool {tool}: {e}")
            return context
    
    async def _simulate_tool_execution(self, tool: str, role: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate tool execution (placeholder for real MCP implementation)."""
        try:
            # Simulate different tool behaviors
            if tool == "store_document":
                return {
                    "success": True,
                    "document_id": f"doc_{int(datetime.now().timestamp())}",
                    "status": "stored",
                    "metadata": parameters.get("metadata", {})
                }
            elif tool == "assess_data_quality":
                return {
                    "success": True,
                    "quality_score": 0.85,
                    "issues": [],
                    "recommendations": ["Data quality is good"]
                }
            elif tool == "create_workflow":
                return {
                    "success": True,
                    "workflow_id": f"wf_{int(datetime.now().timestamp())}",
                    "status": "created",
                    "steps": parameters.get("steps", [])
                }
            elif tool == "send_message":
                return {
                    "success": True,
                    "message_id": f"msg_{int(datetime.now().timestamp())}",
                    "status": "sent",
                    "recipient": parameters.get("recipient", "unknown")
                }
            elif tool == "monitor_health":
                return {
                    "success": True,
                    "health_status": "healthy",
                    "metrics": {"cpu": 0.5, "memory": 0.6},
                    "alerts": []
                }
            else:
                return {
                    "success": True,
                    "message": f"Simulated execution of {tool}",
                    "parameters": parameters,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Tool execution simulation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _should_continue_on_error(self, tool: str, error: Exception) -> bool:
        """Determine whether to continue execution after tool error."""
        # Critical tools that should stop execution on failure
        critical_tools = ["authenticate_user", "authorize_action", "enforce_policies"]
        
        if tool in critical_tools:
            return False
        
        # Non-critical tools can fail without stopping execution
        return True
    
    async def _aggregate_results(self, execution_results: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from all executed tools."""
        try:
            aggregated = {
                "success": True,
                "tool_results": execution_results,
                "summary": {},
                "metadata": {
                    "total_tools": len(execution_results),
                    "successful_tools": sum(1 for r in execution_results.values() if r.get("success", False)),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Create summary based on tool results
            if "assess_data_quality" in execution_results:
                quality_result = execution_results["assess_data_quality"]
                aggregated["summary"]["data_quality"] = quality_result.get("quality_score", 0)
            
            if "monitor_health" in execution_results:
                health_result = execution_results["monitor_health"]
                aggregated["summary"]["system_health"] = health_result.get("health_status", "unknown")
            
            if "create_workflow" in execution_results:
                workflow_result = execution_results["create_workflow"]
                aggregated["summary"]["workflow_created"] = workflow_result.get("workflow_id")
            
            # Determine overall success
            failed_tools = [tool for tool, result in execution_results.items() 
                          if not result.get("success", False)]
            if failed_tools:
                aggregated["success"] = False
                aggregated["summary"]["failed_tools"] = failed_tools
            
            return aggregated
            
        except Exception as e:
            self.logger.error(f"Failed to aggregate results: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_results": execution_results
            }
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self.execution_history[-limit:] if self.execution_history else []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check tool composition health."""
        try:
            return {
                "status": "healthy",
                "tool_registry_size": len(self.tool_registry),
                "execution_history_entries": len(self.execution_history),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }



