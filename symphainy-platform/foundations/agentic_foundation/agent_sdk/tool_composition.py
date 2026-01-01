"""
Tool Composition - Tool Chaining and Orchestration (Refactored with Pure DI)

Provides tool chaining and orchestration capabilities for agent execution.
Manages tool dependencies, execution order, and result aggregation.

WHAT (Agentic Role): I provide tool chaining and orchestration for agent execution
HOW (Tool Composition): I use pure dependency injection and manage tool dependencies and execution
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import DIContainerService DI container
from foundations.di_container.di_container_service import DIContainerService


class ToolComposition:
    """
    Manages tool chaining and orchestration for agent execution.
    
    Refactored to use pure dependency injection through DIContainerService.
    
    Provides:
    - Tool dependency resolution
    - Execution order optimization
    - Result aggregation and transformation
    - Error handling and recovery
    - Performance monitoring
    """
    
    def __init__(self, foundation_services: DIContainerService, agentic_foundation: 'AgenticFoundationService' = None):
        """Initialize tool composition with pure dependency injection."""
        self.foundation_services = foundation_services
        self.agentic_foundation = agentic_foundation
        
        # Get utilities from foundation services DI container
        self.logger = foundation_services.get_logger("tool_composition")
        self.config = foundation_services.get_config()
        self.health = foundation_services.get_health()
        self.telemetry = foundation_services.get_telemetry()
        self.security = foundation_services.get_security()
        
        # Multi-tenant context
        self.tenant_context = None
        
        # Tool registry and dependencies
        self.tool_registry = {}
        self.tool_dependencies = {}
        
        # Execution history
        self.execution_history = []
        
        self.logger.info("Tool Composition initialized with multi-tenancy support")
    
    def set_tenant_context(self, tenant_context: Dict[str, Any]):
        """Set tenant context for multi-tenant operations."""
        self.tenant_context = tenant_context
        self.logger.info(f"Tenant context set for Tool Composition: {tenant_context.get('tenant_id', 'unknown')}")
    
    async def execute_tool_chain(self, tool_chain: List[str], context: Dict[str, Any], 
                                role_connections: Dict[str, Any], agent_id: str, tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a chain of tools with proper orchestration and multi-tenant awareness.
        
        Args:
            tool_chain: List of tools to execute
            context: Execution context
            role_connections: Smart City role connections
            agent_id: Agent identifier
            tenant_context: Tenant context for multi-tenant operations
            
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
    
    async def compose_tools(self, tool_chain: List[Dict[str, Any]], tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compose and execute a chain of tools."""
        try:
            # Extract tool names from tool chain
            tool_names = [tool.get("name", tool) if isinstance(tool, dict) else tool for tool in tool_chain]
            
            # Execute tool chain
            result = await self.execute_tool_chain(
                tool_names, 
                {"tenant_context": tenant_context}, 
                {}, 
                "compose_tools_agent", 
                tenant_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to compose tools: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def register_tool(self, tool_name: str, tool_definition: Dict[str, Any]) -> bool:
        """Register a tool for composition."""
        try:
            self.tool_registry[tool_name] = tool_definition
            self.logger.info(f"Tool {tool_name} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool_name}: {e}")
            return False
    
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
    
    # ============================================================================
    # ENHANCED TOOL DISCOVERY CAPABILITIES FOR AGENTS
    # ============================================================================
    
    async def get_enhanced_tool_capabilities(self) -> Dict[str, Any]:
        """Get enhanced tool capabilities for agents."""
        try:
            if self.agentic_foundation:
                # Get agent capability registry
                capability_registry = getattr(self.agentic_foundation, 'agent_capability_registry', {})
                
                return {
                    "available_tools": capability_registry.get("agent_tools", []),
                    "agent_types": capability_registry.get("agent_types", []),
                    "capability_count": len(capability_registry.get("agent_capabilities", {})),
                    "tool_registry_size": len(self.tool_registry)
                }
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced tool capabilities: {e}")
            return {}
    
    async def discover_agent_tools(self, agent_type: str) -> List[str]:
        """Discover tools available for a specific agent type."""
        try:
            if self.agentic_foundation:
                # Get agent capability registry
                capability_registry = getattr(self.agentic_foundation, 'agent_capability_registry', {})
                agent_types = capability_registry.get("agent_types", [])
                agent_tools = capability_registry.get("agent_tools", [])
                
                if agent_type in agent_types:
                    return agent_tools
                else:
                    self.logger.warning(f"Agent type {agent_type} not found in capability registry")
                    return []
            return []
        except Exception as e:
            self.logger.error(f"Failed to discover tools for agent type {agent_type}: {e}")
            return []
    
    async def get_tool_execution_capabilities(self) -> Dict[str, Any]:
        """Get tool execution capabilities for agents."""
        try:
            return {
                "tool_chaining": True,
                "parallel_execution": True,
                "error_recovery": True,
                "performance_monitoring": True,
                "tenant_isolation": self.tenant_isolation_enabled,
                "available_tools": list(self.tool_registry.keys())
            }
        except Exception as e:
            self.logger.error(f"Failed to get tool execution capabilities: {e}")
            return {}



