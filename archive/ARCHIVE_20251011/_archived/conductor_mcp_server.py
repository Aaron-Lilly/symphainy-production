#!/usr/bin/env python3
"""
Conductor MCP Server

MCP server that exposes Conductor service capabilities as MCP tools.
Provides workflow orchestration, task management, and scheduling tools.

WHAT (Smart City Role): I expose my orchestration capabilities via MCP tools
HOW (MCP Server): I implement the MCP protocol and expose Conductor operations
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.foundation_service_base import FoundationServiceBase
from foundations.curator_foundation.services import CapabilityRegistryService
from config.environment_loader import EnvironmentLoader
from config import Environment
from utilities import UserContext
from backend.smart_city.protocols.mcp_server_protocol import MCPServerProtocol, MCPTool, MCPServerInfo
from backend.smart_city.interfaces import (
    WorkflowCreateRequest, WorkflowSearchRequest, WorkflowExecuteRequest,
    WorkflowType, WorkflowStatus, WorkflowStep
)
from backend.smart_city.services.conductor.conductor_service import ConductorService


class ConductorMCPServer(MCPServerProtocol):
    """
    Conductor MCP Server
    
    Exposes Conductor service capabilities as MCP tools for external consumption.
    Provides comprehensive workflow orchestration, task management, and scheduling.
    
    WHAT (Smart City Role): I expose my orchestration capabilities via MCP tools
    HOW (MCP Server): I implement the MCP protocol and expose Conductor operations
    """
    
    def __init__(self, conductor_service: ConductorService, curator_foundation: CapabilityRegistryService = None):
        """Initialize Conductor MCP Server."""
        super().__init__(
            server_name="conductor_mcp_server",
            interface_class=ConductorService,  # The service class that implements the interface
            curator_foundation=curator_foundation
        )
        
        self.conductor_service = conductor_service
        self.tools = self._create_conductor_tools()
        
    def _create_conductor_tools(self) -> List[MCPTool]:
        """Create Conductor specific MCP tools."""
        return self._create_standard_tools() + [
            # Workflow Management Tools
            MCPTool(
                name="create_workflow",
                description="Create a new workflow definition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the workflow"},
                        "description": {"type": "string", "description": "Description of the workflow"},
                        "workflow_type": {"type": "string", "enum": ["sequential", "parallel", "conditional"], "description": "Type of workflow"},
                        "steps": {"type": "array", "items": {"type": "object"}, "description": "Workflow steps"},
                        "triggers": {"type": "array", "items": {"type": "string"}, "description": "Workflow triggers"},
                        "conditions": {"type": "array", "items": {"type": "object"}, "description": "Workflow conditions"},
                        "variables": {"type": "object", "description": "Workflow variables"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Workflow tags"},
                        "category": {"type": "string", "description": "Workflow category"}
                    },
                    "required": ["name", "workflow_type"]
                },
                handler=self._handle_create_workflow,
                tags=["workflow", "management", "orchestration"]
            ),
            
            MCPTool(
                name="get_workflow",
                description="Get a workflow definition by ID",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "ID of the workflow"}
                    },
                    "required": ["workflow_id"]
                },
                handler=self._handle_get_workflow,
                tags=["workflow", "retrieval", "management"]
            ),
            
            MCPTool(
                name="update_workflow",
                description="Update a workflow definition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "ID of the workflow"},
                        "updates": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "steps": {"type": "array", "items": {"type": "object"}},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "variables": {"type": "object"}
                            }
                        }
                    },
                    "required": ["workflow_id", "updates"]
                },
                handler=self._handle_update_workflow,
                tags=["workflow", "update", "management"]
            ),
            
            MCPTool(
                name="delete_workflow",
                description="Delete a workflow definition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "ID of the workflow"}
                    },
                    "required": ["workflow_id"]
                },
                handler=self._handle_delete_workflow,
                tags=["workflow", "delete", "management"]
            ),
            
            MCPTool(
                name="search_workflows",
                description="Search workflow definitions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "workflow_type": {"type": "string", "enum": ["sequential", "parallel", "conditional"], "description": "Filter by workflow type"},
                        "status": {"type": "string", "enum": ["draft", "active", "inactive"], "description": "Filter by status"},
                        "category": {"type": "string", "description": "Filter by category"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "description": "Maximum number of results"}
                    },
                    "required": ["query"]
                },
                handler=self._handle_search_workflows,
                tags=["workflow", "search", "discovery"]
            ),
            
            # Workflow Execution Tools
            MCPTool(
                name="execute_workflow",
                description="Execute a workflow",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "ID of the workflow to execute"},
                        "input_data": {"type": "object", "description": "Input data for the workflow"}
                    },
                    "required": ["workflow_id"]
                },
                handler=self._handle_execute_workflow,
                tags=["workflow", "execution", "orchestration"]
            ),
            
            MCPTool(
                name="get_execution",
                description="Get workflow execution details",
                input_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string", "description": "ID of the execution"}
                    },
                    "required": ["execution_id"]
                },
                handler=self._handle_get_execution,
                tags=["workflow", "execution", "monitoring"]
            ),
            
            MCPTool(
                name="cancel_execution",
                description="Cancel a workflow execution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string", "description": "ID of the execution to cancel"}
                    },
                    "required": ["execution_id"]
                },
                handler=self._handle_cancel_execution,
                tags=["workflow", "execution", "control"]
            ),
            
            MCPTool(
                name="pause_execution",
                description="Pause a workflow execution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string", "description": "ID of the execution to pause"}
                    },
                    "required": ["execution_id"]
                },
                handler=self._handle_pause_execution,
                tags=["workflow", "execution", "control"]
            ),
            
            MCPTool(
                name="resume_execution",
                description="Resume a paused workflow execution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string", "description": "ID of the execution to resume"}
                    },
                    "required": ["execution_id"]
                },
                handler=self._handle_resume_execution,
                tags=["workflow", "execution", "control"]
            ),
            
            MCPTool(
                name="get_execution_logs",
                description="Get execution logs for a workflow",
                input_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string", "description": "ID of the execution"}
                    },
                    "required": ["execution_id"]
                },
                handler=self._handle_get_execution_logs,
                tags=["workflow", "execution", "monitoring"]
            ),
            
            # Task Management Tools
            MCPTool(
                name="create_task",
                description="Create a new task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the task"},
                        "description": {"type": "string", "description": "Description of the task"},
                        "task_type": {"type": "string", "description": "Type of the task"},
                        "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"], "description": "Task priority"},
                        "input_data": {"type": "object", "description": "Input data for the task"},
                        "dependencies": {"type": "array", "items": {"type": "string"}, "description": "Task dependencies"},
                        "timeout": {"type": "integer", "description": "Task timeout in seconds"},
                        "max_retries": {"type": "integer", "description": "Maximum number of retries"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
                        "category": {"type": "string", "description": "Task category"}
                    },
                    "required": ["name", "task_type"]
                },
                handler=self._handle_create_task,
                tags=["task", "management", "orchestration"]
            ),
            
            MCPTool(
                name="get_task",
                description="Get a task by ID",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "ID of the task"}
                    },
                    "required": ["task_id"]
                },
                handler=self._handle_get_task,
                tags=["task", "retrieval", "management"]
            ),
            
            MCPTool(
                name="execute_task",
                description="Execute a task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "ID of the task to execute"},
                        "task_data": {"type": "object", "description": "Data for the task execution"}
                    },
                    "required": ["task_id", "task_data"]
                },
                handler=self._handle_execute_task,
                tags=["task", "execution", "orchestration"]
            ),
            
            # Scheduling Tools
            MCPTool(
                name="create_schedule",
                description="Create a workflow schedule",
                input_schema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "ID of the workflow to schedule"},
                        "name": {"type": "string", "description": "Name of the schedule"},
                        "description": {"type": "string", "description": "Description of the schedule"},
                        "schedule_type": {"type": "string", "enum": ["once", "repeating", "cron"], "description": "Type of schedule"},
                        "start_time": {"type": "string", "format": "date-time", "description": "Start time for the schedule"},
                        "end_time": {"type": "string", "format": "date-time", "description": "End time for the schedule"},
                        "cron_expression": {"type": "string", "description": "Cron expression for cron schedules"},
                        "interval_seconds": {"type": "integer", "description": "Interval in seconds for repeating schedules"},
                        "timezone": {"type": "string", "description": "Timezone for the schedule"},
                        "input_data": {"type": "object", "description": "Input data for scheduled executions"},
                        "max_executions": {"type": "integer", "description": "Maximum number of executions"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Schedule tags"},
                        "category": {"type": "string", "description": "Schedule category"}
                    },
                    "required": ["workflow_id", "name", "schedule_type"]
                },
                handler=self._handle_create_schedule,
                tags=["schedule", "management", "orchestration"]
            ),
            
            MCPTool(
                name="get_schedule",
                description="Get a schedule by ID",
                input_schema={
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "string", "description": "ID of the schedule"}
                    },
                    "required": ["schedule_id"]
                },
                handler=self._handle_get_schedule,
                tags=["schedule", "retrieval", "management"]
            ),
            
            MCPTool(
                name="pause_schedule",
                description="Pause a schedule",
                input_schema={
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "string", "description": "ID of the schedule to pause"}
                    },
                    "required": ["schedule_id"]
                },
                handler=self._handle_pause_schedule,
                tags=["schedule", "control", "management"]
            ),
            
            MCPTool(
                name="resume_schedule",
                description="Resume a paused schedule",
                input_schema={
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "string", "description": "ID of the schedule to resume"}
                    },
                    "required": ["schedule_id"]
                },
                handler=self._handle_resume_schedule,
                tags=["schedule", "control", "management"]
            ),
            
            MCPTool(
                name="cancel_schedule",
                description="Cancel a schedule",
                input_schema={
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "string", "description": "ID of the schedule to cancel"}
                    },
                    "required": ["schedule_id"]
                },
                handler=self._handle_cancel_schedule,
                tags=["schedule", "control", "management"]
            ),
            
            # Analytics Tools
            MCPTool(
                name="get_workflow_analytics",
                description="Get workflow analytics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "time_period": {"type": "string", "enum": ["7d", "30d", "90d"], "description": "Time period for analytics"},
                        "user_id": {"type": "string", "description": "User ID for user-specific analytics"}
                    },
                    "required": []
                },
                handler=self._handle_get_workflow_analytics,
                tags=["analytics", "metrics", "insights"]
            ),
            
            MCPTool(
                name="get_performance_metrics",
                description="Get performance metrics",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_performance_metrics,
                tags=["analytics", "metrics", "performance"]
            ),
            
            MCPTool(
                name="get_error_analytics",
                description="Get error analytics and patterns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "time_period": {"type": "string", "enum": ["7d", "30d", "90d"], "description": "Time period for analytics"}
                    },
                    "required": []
                },
                handler=self._handle_get_error_analytics,
                tags=["analytics", "errors", "insights"]
            ),
            
            # Service Management Tools
            MCPTool(
                name="get_service_status",
                description="Get the current status of the Conductor service",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self._handle_get_service_status,
                tags=["service", "status", "health"]
            )
        ]
    
    async def initialize(self, user_context: UserContext = None):
        """Initialize the Conductor MCP Server."""
        try:
            # Ensure the Conductor service is initialized
            if not hasattr(self.conductor_service, 'initialized') or not self.conductor_service.initialized:
                await self.conductor_service.initialize()
            
            # Register with Curator Foundation if available
            if self.curator_foundation:
                await self.register_with_curator(user_context)
            
            self.logger.info("✅ Conductor MCP Server initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Conductor MCP Server: {e}")
            raise
    
    def get_server_info(self) -> MCPServerInfo:
        """Get server information for MCP manifest generation."""
        return MCPServerInfo(
            server_name="conductor_mcp_server",
            version="1.0.0",
            description="Conductor MCP Server - Workflow orchestration, task management, and scheduling",
            interface_name="IWorkflowOrchestration",
            tools=[tool.name for tool in self.tools],
            capabilities=[
                "workflow_management",
                "workflow_execution",
                "task_management",
                "workflow_scheduling",
                "orchestration_analytics",
                "workflow_monitoring",
                "task_coordination"
            ]
        )
    
    def get_tools(self) -> List[MCPTool]:
        """Get all available MCP tools."""
        return self.tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Execute an MCP tool with given parameters."""
        try:
            # Find the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                return self._create_error_response(f"Tool '{tool_name}' not found")
            
            # Execute the tool
            return await tool.handler(parameters, user_context)
            
        except Exception as e:
            return self._create_error_response(f"Tool execution failed: {str(e)}")
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this server with Curator Foundation Service."""
        if not self.curator_foundation:
            return {"error": "Curator Foundation Service not available"}
        
        try:
            server_info = self.get_server_info()
            
            capability = {
                "interface": server_info.interface_name,
                "endpoints": [],  # MCP servers don't have HTTP endpoints
                "tools": server_info.tools,
                "description": server_info.description,
                "realm": "smart_city",
                "role": "conductor"
            }
            
            return await self.curator_foundation.register_capability(
                self.server_name,
                capability,
                user_context
            )
            
        except Exception as e:
            return {"error": f"Failed to register with Curator: {str(e)}"}
    
    # Tool Handlers
    
    async def _handle_create_workflow(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create workflow tool execution."""
        try:
            # Create workflow request
            request = WorkflowCreateRequest(
                name=parameters["name"],
                description=parameters.get("description", ""),
                workflow_type=WorkflowType(parameters["workflow_type"]),
                steps=[WorkflowStep(**step) if isinstance(step, dict) else step for step in parameters.get("steps", [])],
                triggers=parameters.get("triggers", []),
                conditions=parameters.get("conditions", []),
                variables=parameters.get("variables", {}),
                tags=parameters.get("tags", []),
                category=parameters.get("category", "general")
            )
            
            # Execute workflow creation
            workflow = await self.conductor_service.create_workflow(request, user_context)
            
            return self._create_success_response({
                "workflow_id": workflow["workflow_id"],
                "name": workflow["name"],
                "workflow_type": workflow["workflow_type"],
                "status": workflow["status"],
                "created_at": workflow["created_at"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Workflow creation failed: {str(e)}")
    
    async def _handle_get_workflow(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get workflow tool execution."""
        try:
            # Execute workflow retrieval
            workflow = await self.conductor_service.get_workflow(parameters["workflow_id"], user_context)
            
            if workflow:
                return self._create_success_response({
                    "workflow": workflow
                })
            else:
                return self._create_success_response({
                    "workflow": None,
                    "error": "Workflow not found"
                })
                
        except Exception as e:
            return self._create_error_response(f"Get workflow failed: {str(e)}")
    
    async def _handle_update_workflow(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle update workflow tool execution."""
        try:
            # Execute workflow update
            success = await self.conductor_service.update_workflow(
                parameters["workflow_id"], 
                parameters["updates"], 
                user_context
            )
            
            return self._create_success_response({
                "success": success,
                "workflow_id": parameters["workflow_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Update workflow failed: {str(e)}")
    
    async def _handle_delete_workflow(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle delete workflow tool execution."""
        try:
            # Execute workflow deletion
            success = await self.conductor_service.delete_workflow(parameters["workflow_id"], user_context)
            
            return self._create_success_response({
                "success": success,
                "workflow_id": parameters["workflow_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Delete workflow failed: {str(e)}")
    
    async def _handle_search_workflows(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle search workflows tool execution."""
        try:
            # Create search request
            request = WorkflowSearchRequest(
                query=parameters["query"],
                workflow_type=WorkflowType(parameters["workflow_type"]) if parameters.get("workflow_type") else None,
                status=WorkflowStatus(parameters["status"]) if parameters.get("status") else None,
                category=parameters.get("category"),
                tags=parameters.get("tags", []),
                limit=parameters.get("limit", 100)
            )
            
            # Execute search
            workflows = await self.conductor_service.search_workflows(request, user_context)
            
            return self._create_success_response({
                "workflows": workflows,
                "total_count": len(workflows)
            })
            
        except Exception as e:
            return self._create_error_response(f"Search workflows failed: {str(e)}")
    
    async def _handle_execute_workflow(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle execute workflow tool execution."""
        try:
            # Create execution request
            request = WorkflowExecuteRequest(
                workflow_id=parameters["workflow_id"],
                input_data=parameters.get("input_data", {})
            )
            
            # Execute workflow
            result = await self.conductor_service.execute_workflow(request, user_context)
            
            return self._create_success_response({
                "success": result["success"],
                "execution_id": result.get("execution_id"),
                "status": result["status"],
                "result": result.get("result", {}),
                "execution_time": result.get("execution_time", 0)
            })
            
        except Exception as e:
            return self._create_error_response(f"Execute workflow failed: {str(e)}")
    
    async def _handle_get_execution(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get execution tool execution."""
        try:
            # Execute execution retrieval
            execution = await self.conductor_service.get_execution(parameters["execution_id"], user_context)
            
            if execution:
                return self._create_success_response({
                    "execution": execution
                })
            else:
                return self._create_success_response({
                    "execution": None,
                    "error": "Execution not found"
                })
                
        except Exception as e:
            return self._create_error_response(f"Get execution failed: {str(e)}")
    
    async def _handle_cancel_execution(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle cancel execution tool execution."""
        try:
            # Execute execution cancellation
            success = await self.conductor_service.cancel_execution(parameters["execution_id"], user_context)
            
            return self._create_success_response({
                "success": success,
                "execution_id": parameters["execution_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Cancel execution failed: {str(e)}")
    
    async def _handle_pause_execution(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle pause execution tool execution."""
        try:
            # Execute execution pause
            success = await self.conductor_service.pause_execution(parameters["execution_id"], user_context)
            
            return self._create_success_response({
                "success": success,
                "execution_id": parameters["execution_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Pause execution failed: {str(e)}")
    
    async def _handle_resume_execution(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle resume execution tool execution."""
        try:
            # Execute execution resume
            success = await self.conductor_service.resume_execution(parameters["execution_id"], user_context)
            
            return self._create_success_response({
                "success": success,
                "execution_id": parameters["execution_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Resume execution failed: {str(e)}")
    
    async def _handle_get_execution_logs(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get execution logs tool execution."""
        try:
            # Execute logs retrieval
            logs = await self.conductor_service.get_execution_logs(parameters["execution_id"], user_context)
            
            return self._create_success_response({
                "logs": logs,
                "execution_id": parameters["execution_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Get execution logs failed: {str(e)}")
    
    async def _handle_create_task(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create task tool execution."""
        try:
            # Execute task creation
            result = await self.conductor_service.create_task(parameters, user_context)
            
            return self._create_success_response({
                "success": result["success"],
                "task_id": result.get("task_id"),
                "task": result.get("task")
            })
            
        except Exception as e:
            return self._create_error_response(f"Create task failed: {str(e)}")
    
    async def _handle_get_task(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get task tool execution."""
        try:
            # Execute task retrieval
            task = await self.conductor_service.get_task(parameters["task_id"], user_context)
            
            if task:
                return self._create_success_response({
                    "task": task
                })
            else:
                return self._create_success_response({
                    "task": None,
                    "error": "Task not found"
                })
                
        except Exception as e:
            return self._create_error_response(f"Get task failed: {str(e)}")
    
    async def _handle_execute_task(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle execute task tool execution."""
        try:
            # Execute task
            result = await self.conductor_service.execute_task(
                parameters["task_id"], 
                parameters["task_data"], 
                user_context
            )
            
            return self._create_success_response({
                "success": result["success"],
                "task_execution_id": result.get("task_execution_id"),
                "status": result.get("status")
            })
            
        except Exception as e:
            return self._create_error_response(f"Execute task failed: {str(e)}")
    
    async def _handle_create_schedule(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle create schedule tool execution."""
        try:
            # Execute schedule creation
            result = await self.conductor_service.workflow_scheduling.create_schedule(parameters, user_context.to_dict() if user_context else None)
            
            return self._create_success_response({
                "success": result["success"],
                "schedule_id": result.get("schedule_id"),
                "schedule": result.get("schedule")
            })
            
        except Exception as e:
            return self._create_error_response(f"Create schedule failed: {str(e)}")
    
    async def _handle_get_schedule(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get schedule tool execution."""
        try:
            # Execute schedule retrieval
            result = await self.conductor_service.workflow_scheduling.get_schedule(parameters["schedule_id"], user_context.to_dict() if user_context else None)
            
            if result["success"]:
                return self._create_success_response({
                    "schedule": result["schedule"]
                })
            else:
                return self._create_success_response({
                    "schedule": None,
                    "error": "Schedule not found"
                })
                
        except Exception as e:
            return self._create_error_response(f"Get schedule failed: {str(e)}")
    
    async def _handle_pause_schedule(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle pause schedule tool execution."""
        try:
            # Execute schedule pause
            success = await self.conductor_service.workflow_scheduling.pause_schedule(parameters["schedule_id"], user_context.to_dict() if user_context else None)
            
            return self._create_success_response({
                "success": success,
                "schedule_id": parameters["schedule_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Pause schedule failed: {str(e)}")
    
    async def _handle_resume_schedule(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle resume schedule tool execution."""
        try:
            # Execute schedule resume
            success = await self.conductor_service.workflow_scheduling.resume_schedule(parameters["schedule_id"], user_context.to_dict() if user_context else None)
            
            return self._create_success_response({
                "success": success,
                "schedule_id": parameters["schedule_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Resume schedule failed: {str(e)}")
    
    async def _handle_cancel_schedule(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle cancel schedule tool execution."""
        try:
            # Execute schedule cancellation
            success = await self.conductor_service.workflow_scheduling.cancel_schedule(parameters["schedule_id"], user_context.to_dict() if user_context else None)
            
            return self._create_success_response({
                "success": success,
                "schedule_id": parameters["schedule_id"]
            })
            
        except Exception as e:
            return self._create_error_response(f"Cancel schedule failed: {str(e)}")
    
    async def _handle_get_workflow_analytics(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get workflow analytics tool execution."""
        try:
            # Execute analytics retrieval
            result = await self.conductor_service.orchestration_analytics.get_workflow_analytics(
                time_period=parameters.get("time_period", "30d"),
                user_id=parameters.get("user_id")
            )
            
            return self._create_success_response({
                "success": result["success"],
                "analytics": result.get("analytics", {}),
                "time_period": parameters.get("time_period", "30d")
            })
            
        except Exception as e:
            return self._create_error_response(f"Get workflow analytics failed: {str(e)}")
    
    async def _handle_get_performance_metrics(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get performance metrics tool execution."""
        try:
            # Execute metrics retrieval
            result = await self.conductor_service.orchestration_analytics.get_performance_metrics()
            
            return self._create_success_response({
                "success": result["success"],
                "metrics": result.get("metrics", {})
            })
            
        except Exception as e:
            return self._create_error_response(f"Get performance metrics failed: {str(e)}")
    
    async def _handle_get_error_analytics(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get error analytics tool execution."""
        try:
            # Execute error analytics retrieval
            result = await self.conductor_service.orchestration_analytics.get_error_analytics(
                time_period=parameters.get("time_period", "30d")
            )
            
            return self._create_success_response({
                "success": result["success"],
                "analytics": result.get("analytics", {}),
                "time_period": parameters.get("time_period", "30d")
            })
            
        except Exception as e:
            return self._create_error_response(f"Get error analytics failed: {str(e)}")
    
    async def _handle_get_service_status(self, parameters: Dict[str, Any], user_context: UserContext = None) -> Dict[str, Any]:
        """Handle get service status tool execution."""
        try:
            # Execute status retrieval
            health = await self.conductor_service.get_service_health()
            
            return self._create_success_response({
                "service_status": health["status"],
                "environment": health["environment"],
                "architecture": health["architecture"],
                "micro_modules": health.get("micro_modules", {}),
                "environment_info": health.get("environment_info", {})
            })
            
        except Exception as e:
            return self._create_error_response(f"Get service status failed: {str(e)}")
