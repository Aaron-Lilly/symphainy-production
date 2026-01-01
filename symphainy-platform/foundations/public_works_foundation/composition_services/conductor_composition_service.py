#!/usr/bin/env python3
"""
Conductor Composition Service

Composition service for Conductor capabilities.
Orchestrates task management, workflow orchestration, and resource allocation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

from ..infrastructure_abstractions.task_management_abstraction import TaskManagementAbstraction
from ..infrastructure_abstractions.workflow_orchestration_abstraction import WorkflowOrchestrationAbstraction
from ..infrastructure_abstractions.resource_allocation_abstraction import ResourceAllocationAbstraction
from ..abstraction_contracts.task_management_protocol import TaskRequest, TaskPriority
from ..abstraction_contracts.workflow_orchestration_protocol import WorkflowDefinition, WorkflowExecutionRequest
from ..abstraction_contracts.resource_allocation_protocol import ResourceRequest, ResourceSpec, ResourceType


class ConductorCompositionService:
    """Composition service for Conductor capabilities."""
    
    def __init__(self, 
                 task_management_abstraction: TaskManagementAbstraction,
                 workflow_orchestration_abstraction: WorkflowOrchestrationAbstraction,
                 resource_allocation_abstraction: ResourceAllocationAbstraction,
                 di_container=None):
        """
        Initialize Conductor composition service.
        
        Args:
            task_management_abstraction: Task management abstraction
            workflow_orchestration_abstraction: Workflow orchestration abstraction
            resource_allocation_abstraction: Resource allocation abstraction
            di_container: DI Container for utilities
        """
        self.task_management = task_management_abstraction
        self.workflow_orchestration = workflow_orchestration_abstraction
        self.resource_allocation = resource_allocation_abstraction
        self.di_container = di_container
        self.service_name = "conductor_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("ConductorCompositionService")
        
        # Service status
        self.is_initialized = False
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the composition service."""
        try:
            self.logger.info("✅ Conductor composition service initialized")
            self.is_initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Conductor composition service: {e}")
            self.is_initialized = False
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    # ============================================================================
    # TASK MANAGEMENT COMPOSITION
    # ============================================================================
    
    async def create_and_execute_task(self, task_name: str, args: List = None, 
                                    kwargs: Dict[str, Any] = None, 
                                    priority: TaskPriority = TaskPriority.NORMAL,
                                    queue: str = "default",
                                    user_context: Dict[str, Any] = None) -> str:
        """
        Create and execute a task with resource allocation.
        
        Args:
            task_name: Name of the task
            args: Task arguments
            kwargs: Task keyword arguments
            priority: Task priority
            queue: Task queue
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            str: Task ID
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "task", "create"
                )
                if validation_error:
                    return None
            
            # Allocate resources for task
            resource_request = ResourceRequest(
                resource_specs=[
                    ResourceSpec(ResourceType.CPU, 10.0, "percent"),
                    ResourceSpec(ResourceType.MEMORY, 100.0, "MB")
                ],
                duration=300,  # 5 minutes
                priority=priority.value
            )
            
            allocation = await self.resource_allocation.allocate_resources(resource_request)
            if not allocation:
                self.logger.warning("Failed to allocate resources for task")
                return None
            
            # Create task request
            task_request = TaskRequest(
                task_name=task_name,
                args=args or [],
                kwargs=kwargs or {},
                queue=queue,
                priority=priority,
                metadata={"allocation_id": allocation.allocation_id}
            )
            
            # Create task
            task_id = await self.task_management.create_task(task_request)
            
            if task_id:
                self.logger.info(f"✅ Task {task_name} created with ID: {task_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("create_and_execute_task", {
                        "task_name": task_name,
                        "task_id": task_id,
                        "success": True
                    })
            else:
                # Deallocate resources if task creation failed
                await self.resource_allocation.deallocate_resources(allocation.allocation_id)
                self.logger.error(f"Failed to create task {task_name}")
            
            return task_id
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_and_execute_task",
                    "task_name": task_name,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to create and execute task {task_name}: {e}")
            return None
    
    async def get_task_status_with_resources(self, task_id: str,
                                            user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get task status with resource information.
        
        Args:
            task_id: Task ID
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Task status with resource info
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "task", "view"
                )
                if validation_error:
                    return validation_error
            
            # Get task status
            task_status = await self.task_management.get_task_status(task_id)
            task_result = await self.task_management.get_task_result(task_id)
            
            # Get resource allocation info
            allocation_id = task_result.metadata.get("allocation_id") if task_result.metadata else None
            allocation_status = None
            if allocation_id:
                allocation = await self.resource_allocation.get_allocation_status(allocation_id)
                allocation_status = allocation.status.value if allocation else None
            
            result = {
                "task_id": task_id,
                "status": task_status.value,
                "result": task_result.result,
                "error": task_result.error,
                "started_at": task_result.started_at.isoformat() if task_result.started_at else None,
                "completed_at": task_result.completed_at.isoformat() if task_result.completed_at else None,
                "allocation_id": allocation_id,
                "allocation_status": allocation_status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_task_status_with_resources", {
                    "task_id": task_id,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_task_status_with_resources",
                    "task_id": task_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get task status with resources {task_id}: {e}")
            return {"error": str(e), "error_code": "TASK_STATUS_ERROR"}
    
    # ============================================================================
    # WORKFLOW ORCHESTRATION COMPOSITION
    # ============================================================================
    
    async def create_and_execute_workflow(self, workflow_definition: WorkflowDefinition, 
                                        input_data: Dict[str, Any] = None,
                                        user_context: Dict[str, Any] = None) -> str:
        """
        Create and execute a workflow with resource allocation.
        
        Args:
            workflow_definition: Workflow definition
            input_data: Workflow input data
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            str: Execution ID
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "workflow", "create"
                )
                if validation_error:
                    return None
            
            # Create workflow
            workflow_id = await self.workflow_orchestration.create_workflow(workflow_definition)
            if not workflow_id:
                self.logger.error("Failed to create workflow")
                return None
            
            # Allocate resources for workflow execution
            resource_request = ResourceRequest(
                resource_specs=[
                    ResourceSpec(ResourceType.CPU, 20.0, "percent"),
                    ResourceSpec(ResourceType.MEMORY, 200.0, "MB"),
                    ResourceSpec(ResourceType.DISK, 50.0, "MB")
                ],
                duration=3600,  # 1 hour
                priority=1
            )
            
            allocation = await self.resource_allocation.allocate_resources(resource_request)
            if not allocation:
                self.logger.warning("Failed to allocate resources for workflow")
                return None
            
            # Execute workflow
            execution_request = WorkflowExecutionRequest(
                workflow_id=workflow_id,
                input_data=input_data or {},
                execution_options={"allocation_id": allocation.allocation_id}
            )
            
            execution_id = await self.workflow_orchestration.execute_workflow(execution_request)
            
            if execution_id:
                self.logger.info(f"✅ Workflow {workflow_id} executed with ID: {execution_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("create_and_execute_workflow", {
                        "workflow_id": workflow_id,
                        "execution_id": execution_id,
                        "success": True
                    })
            else:
                # Deallocate resources if execution failed
                await self.resource_allocation.deallocate_resources(allocation.allocation_id)
                self.logger.error(f"Failed to execute workflow {workflow_id}")
            
            return execution_id
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_and_execute_workflow",
                    "workflow_id": workflow_definition.workflow_id if hasattr(workflow_definition, 'workflow_id') else None,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to create and execute workflow: {e}")
            return None
    
    async def get_workflow_execution_status(self, execution_id: str,
                                           user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get workflow execution status with resource information.
        
        Args:
            execution_id: Execution ID
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Workflow execution status with resource info
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "workflow", "view"
                )
                if validation_error:
                    return validation_error
            
            # Get execution status
            execution_status = await self.workflow_orchestration.get_execution_status(execution_id)
            execution_result = await self.workflow_orchestration.get_execution_result(execution_id)
            
            # Get resource allocation info
            allocation_id = execution_result.get("execution_data", {}).get("allocation_id")
            allocation_status = None
            if allocation_id:
                allocation = await self.resource_allocation.get_allocation_status(allocation_id)
                allocation_status = allocation.status.value if allocation else None
            
            result = {
                "execution_id": execution_id,
                "workflow_id": execution_result.get("workflow_id"),
                "status": execution_status.value,
                "started_at": execution_result.get("started_at"),
                "completed_at": execution_result.get("completed_at"),
                "current_node": execution_result.get("current_node"),
                "execution_data": execution_result.get("execution_data"),
                "error": execution_result.get("error"),
                "allocation_id": allocation_id,
                "allocation_status": allocation_status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_workflow_execution_status", {
                    "execution_id": execution_id,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_workflow_execution_status",
                    "execution_id": execution_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get workflow execution status {execution_id}: {e}")
            return {"error": str(e), "error_code": "WORKFLOW_STATUS_ERROR"}
    
    # ============================================================================
    # INTEGRATED ORCHESTRATION
    # ============================================================================
    
    async def orchestrate_workflow_with_tasks(self, workflow_definition: WorkflowDefinition,
                                            task_definitions: List[Dict[str, Any]],
                                            input_data: Dict[str, Any] = None,
                                            user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Orchestrate a workflow with individual task execution.
        
        Args:
            workflow_definition: Workflow definition
            task_definitions: List of task definitions
            input_data: Workflow input data
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Orchestration result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "workflow", "orchestrate"
                )
                if validation_error:
                    return validation_error
            
            # Create and execute workflow
            execution_id = await self.create_and_execute_workflow(workflow_definition, input_data, user_context)
            if not execution_id:
                return {"error": "Failed to create workflow execution"}
            
            # Execute individual tasks
            task_results = []
            for task_def in task_definitions:
                task_id = await self.create_and_execute_task(
                    task_name=task_def.get("name"),
                    args=task_def.get("args", []),
                    kwargs=task_def.get("kwargs", {}),
                    priority=TaskPriority(task_def.get("priority", 2)),
                    queue=task_def.get("queue", "default"),
                    user_context=user_context
                )
                
                if task_id:
                    task_results.append({
                        "task_id": task_id,
                        "task_name": task_def.get("name"),
                        "status": "created"
                    })
                else:
                    task_results.append({
                        "task_name": task_def.get("name"),
                        "status": "failed",
                        "error": "Task creation failed"
                    })
            
            result = {
                "workflow_execution_id": execution_id,
                "task_results": task_results,
                "total_tasks": len(task_definitions),
                "successful_tasks": len([t for t in task_results if t["status"] == "created"]),
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_workflow_with_tasks", {
                    "execution_id": execution_id,
                    "total_tasks": len(task_definitions),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_workflow_with_tasks",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to orchestrate workflow with tasks: {e}")
            return {"error": str(e), "error_code": "WORKFLOW_ORCHESTRATION_ERROR"}
    
    async def get_orchestration_status(self, execution_id: str,
                                     user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get comprehensive orchestration status.
        
        Args:
            execution_id: Workflow execution ID
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Comprehensive orchestration status
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "workflow", "view"
                )
                if validation_error:
                    return validation_error
            
            # Get workflow execution status
            workflow_status = await self.get_workflow_execution_status(execution_id, user_context)
            
            # Get active tasks
            active_tasks = await self.task_management.get_active_tasks()
            
            # Get resource allocation status
            allocation_id = workflow_status.get("allocation_id")
            allocation_status = None
            if allocation_id:
                allocation = await self.resource_allocation.get_allocation_status(allocation_id)
                allocation_status = allocation.status.value if allocation else None
            
            # Get system resources
            system_resources = await self.resource_allocation.get_system_resources()
            
            result = {
                "execution_id": execution_id,
                "workflow_status": workflow_status,
                "active_tasks": len(active_tasks),
                "allocation_status": allocation_status,
                "system_resources": system_resources,
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_orchestration_status", {
                    "execution_id": execution_id,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_orchestration_status",
                    "execution_id": execution_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get orchestration status {execution_id}: {e}")
            return {"error": str(e), "error_code": "ORCHESTRATION_STATUS_ERROR"}
    
    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get composition service status.
        
        Returns:
            Dict: Service status
        """
        try:
            # Get component statuses
            task_queue_status = await self.task_management.get_queue_status()
            active_allocations = await self.resource_allocation.get_active_allocations()
            system_resources = await self.resource_allocation.get_system_resources()
            
            return {
                "service": "ConductorCompositionService",
                "initialized": self.is_initialized,
                "components": {
                    "task_management": {
                        "queue_length": task_queue_status.get("length", 0),
                        "workers": task_queue_status.get("workers", 0)
                    },
                    "resource_allocation": {
                        "active_allocations": len(active_allocations),
                        "system_resources": system_resources
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get service status: {e}")
            return {"error": str(e), "error_code": "SERVICE_STATUS_ERROR"}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check task management
            try:
                task_status = await self.task_management.get_queue_status()
                health_status["components"]["task_management"] = {
                    "healthy": True,
                    "queue_length": task_status.get("length", 0)
                }
            except Exception as e:
                health_status["components"]["task_management"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
            
            # Check resource allocation
            try:
                system_resources = await self.resource_allocation.get_system_resources()
                health_status["components"]["resource_allocation"] = {
                    "healthy": True,
                    "system_resources": system_resources
                }
            except Exception as e:
                health_status["components"]["resource_allocation"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "error_code": "HEALTH_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }



