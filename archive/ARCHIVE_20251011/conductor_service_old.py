#!/usr/bin/env python3
"""
Conductor Service - Multi-Tenant Architecture

Refactored to adhere to the new architectural principles with multi-tenant awareness:
- Inherits from SOAServiceBase
- Uses simple micro-modules for business logic
- Implements interfaces (duck typing) without importing them directly
- Leverages environment configuration for dynamic behavior
- Provides tenant-aware workflow orchestration

WHAT (Smart City Role): I orchestrate workflows and coordinate tasks across the platform with tenant awareness
HOW (Service Implementation): I use foundation services and micro-modules for orchestration with tenant isolation
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment

# Import micro-modules
from .micro_modules.workflow_management import WorkflowManagementModule
from .micro_modules.workflow_execution import WorkflowExecutionModule
from .micro_modules.task_management import TaskManagementModule
from .micro_modules.workflow_scheduling import WorkflowSchedulingModule
from .micro_modules.orchestration_analytics import OrchestrationAnalyticsModule


class ConductorService(SOAServiceBase):
    """
    Conductor Service - Multi-Tenant Smart City Service
    
    Manages workflow orchestration and task coordination using:
    - Foundation services for infrastructure access
    - Micro-modules for focused business logic
    - Environment configuration for dynamic behavior
    - Duck typing for interface compliance
    - Multi-tenant awareness and tenant isolation
    
    WHAT (Smart City Role): I orchestrate workflows and coordinate tasks across the platform with tenant awareness
    HOW (Service Implementation): I use foundation services and micro-modules for orchestration with tenant isolation
    """
    
    def __init__(self, utility_foundation: UtilityFoundationService, curator_foundation: CuratorFoundationService = None, 
                 public_works_foundation: PublicWorksFoundationService = None, environment: Optional[Environment] = None):
        """Initialize Conductor Service with multi-tenant architecture."""
        super().__init__("ConductorService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.env_loader = EnvironmentLoader(environment)
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize SOA protocol
        self.soa_protocol = ConductorSOAProtocol("ConductorService", self, curator_foundation), public_works_foundation
        
        # Environment-specific configuration
        self.config = self.env_loader.get_all_config()
        self.api_config = self.env_loader.get_api_config()
        self.feature_flags = self.env_loader.get_feature_flags()
        
        # Initialize micro-modules (corrected architecture)
        self.workflow_management = WorkflowManagementModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.workflow_execution = WorkflowExecutionModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.task_management = TaskManagementModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.workflow_scheduling = WorkflowSchedulingModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.orchestration_analytics = OrchestrationAnalyticsModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        
        # Service capabilities
        self.capabilities = [
            "workflow_management",
            "workflow_execution",
            "task_management",
            "workflow_scheduling",
            "orchestration_analytics",
            "multi_tenant_workflow_orchestration"
        ]
        
        self.logger.info("🎭 Conductor Service initialized - Multi-Tenant Workflow Orchestration Hub")
    
    async def initialize(self):
        """Initialize the Conductor Service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Conductor Service with multi-tenant capabilities...")

            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")
            
            # Initialize micro-modules
            await self.workflow_management.initialize()
            await self.workflow_execution.initialize()
            await self.task_management.initialize()
            await self.workflow_scheduling.initialize()
            await self.orchestration_analytics.initialize()
            
            # Apply environment-specific settings
            await self._apply_environment_settings()
            
            self.logger.info("✅ Conductor Service initialized successfully")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_service_initialization")
            raise
    
    async def _apply_environment_settings(self):
        """Apply environment-specific settings."""
        try:
            current_env = self.env_loader.get_environment().value
            self.logger.info(f"🔧 Applied {current_env} settings")
            
            # Example: Adjust logging level based on environment
            if self.api_config.get("debug"):
                self.logger.setLevel("DEBUG")
            else:
                self.logger.setLevel("INFO")
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_environment_settings")
    
   
    
    # NEW: Abstraction Access Methods using Protocol
    async def get_abstraction(self, abstraction_name: str) -> Any:
        """Get a business abstraction through the protocol."""
        return self.soa_protocol.get_abstraction(abstraction_name)
    
    async def has_abstraction(self, abstraction_name: str) -> bool:
        """Check if a business abstraction is available through the protocol."""
        return self.soa_protocol.has_abstraction(abstraction_name)
    
    async def get_abstraction_for_role(self, role: str) -> Dict[str, Any]:
        """Get business abstractions for a specific role through the protocol."""
        return self.soa_protocol.get_abstraction_for_role(role)
    
    async def create_abstraction_context(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Create abstraction context for cross-role operations."""
        abstraction_context = {}
        
        # Get available abstractions through protocol
        available_abstractions = self.soa_protocol.get_abstraction_names()
        
        for abstraction_name in available_abstractions:
            abstraction = self.soa_protocol.get_abstraction(abstraction_name)
            if abstraction:
                abstraction_context[abstraction_name] = abstraction
        
        self.logger.info(f"✅ Created abstraction context with {len(abstraction_context)} abstractions")
        return abstraction_context
    
    # IWorkflowOrchestration Interface Implementation (duck typing)
    # The methods match the interface, but no explicit inheritance or import of IWorkflowOrchestration
    
    async def create_workflow(self, request: "WorkflowCreateRequest", user_context: Optional[UserContext] = None) -> "WorkflowDefinition":
        """Create a new workflow definition."""
        try:
            # Validate user context and permissions
            if user_context:
                has_permission = await self.security_service.check_permissions(
                    user_context.user_id, "workflow_creation", "write"
                )
                if not has_permission:
                    raise Exception("Insufficient permissions for workflow creation")
            # Delegate to workflow management module
            workflow_data = {
                "name": request.name,
                "description": request.description,
                "workflow_type": request.workflow_type.value if hasattr(request.workflow_type, 'value') else str(request.workflow_type),
                "steps": [step.dict() if hasattr(step, 'dict') else step for step in request.steps],
                "triggers": request.triggers,
                "conditions": request.conditions,
                "variables": request.variables,
                "tags": request.tags,
                "category": request.category
            }
            
            result = await self.workflow_management.create_workflow(
                workflow_data=workflow_data,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                # Track workflow creation for analytics
                await self.orchestration_analytics.track_workflow_creation(
                    workflow_id=result["workflow_id"],
                    workflow_type=request.workflow_type.value if hasattr(request.workflow_type, 'value') else str(request.workflow_type),
                    user_id=user_context.user_id if user_context else "system",
                    metadata={"steps_count": len(request.steps)}
                )
                
                # Record telemetry for workflow creation
                await self.telemetry_service.record_metric(
                    "workflow_creation_count", 1,
                    {"workflow_type": request.workflow_type.value if hasattr(request.workflow_type, 'value') else str(request.workflow_type),
                     "steps_count": len(request.steps), "category": request.category}
                )
                
                return result["workflow"]
            else:
                raise Exception(result.get("error", "Failed to create workflow"))
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_workflow_creation")
            raise
    
    async def get_workflow(self, workflow_id: str, user_context: Optional[UserContext] = None) -> Optional["WorkflowDefinition"]:
        """Get a workflow definition by ID."""
        try:
            result = await self.workflow_management.get_workflow(
                workflow_id=workflow_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                return result["workflow"]
            else:
                return None
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_get_workflow")
            return None
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any], user_context: Optional[UserContext] = None) -> bool:
        """Update a workflow definition."""
        try:
            result = await self.workflow_management.update_workflow(
                workflow_id=workflow_id,
                updates=updates,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return result["success"]
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_update_workflow")
            return False
    
    async def delete_workflow(self, workflow_id: str, user_context: Optional[UserContext] = None) -> bool:
        """Delete a workflow definition."""
        try:
            success = await self.workflow_management.delete_workflow(
                workflow_id=workflow_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return success
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_delete_workflow")
            return False
    
    async def search_workflows(self, request: "WorkflowSearchRequest", user_context: Optional[UserContext] = None) -> List["WorkflowDefinition"]:
        """Search workflow definitions."""
        try:
            result = await self.workflow_management.search_workflows(
                query=request.query,
                filters={
                    "workflow_type": request.workflow_type.value if hasattr(request.workflow_type, 'value') else str(request.workflow_type) if request.workflow_type else None,
                    "status": request.status.value if hasattr(request.status, 'value') else str(request.status) if request.status else None,
                    "category": request.category,
                    "tags": request.tags
                },
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                return result["results"]
            else:
                return []
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_search_workflows")
            return []
    
    async def execute_workflow(self, request: "WorkflowExecuteRequest", user_context: Optional[UserContext] = None) -> "WorkflowExecutionResult":
        """Execute a workflow."""
        try:
            start_time = datetime.utcnow()
            
            # Delegate to workflow execution module
            result = await self.workflow_execution.execute_workflow(
                workflow_id=request.workflow_id,
                input_data=request.input_data,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                execution_id = result["execution_id"]
                
                # Track execution for analytics
                end_time = datetime.utcnow()
                execution_duration = (end_time - start_time).total_seconds()
                
                await self.orchestration_analytics.track_workflow_execution(
                    execution_id=execution_id,
                    workflow_id=request.workflow_id,
                    user_id=user_context.user_id if user_context else "system",
                    execution_duration=execution_duration,
                    status="completed"
                )
                
                # Record telemetry for workflow execution
                await self.telemetry_service.record_metric(
                    "workflow_execution_count", 1,
                    {"workflow_id": request.workflow_id, "execution_duration": execution_duration, "status": "completed"}
                )
                
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "status": "completed",
                    "result": result.get("output_data", {}),
                    "execution_time": execution_duration
                }
            else:
                # Track failed execution
                end_time = datetime.utcnow()
                execution_duration = (end_time - start_time).total_seconds()
                
                await self.orchestration_analytics.track_workflow_execution(
                    execution_id="failed",
                    workflow_id=request.workflow_id,
                    user_id=user_context.user_id if user_context else "system",
                    execution_duration=execution_duration,
                    status="failed"
                )
                
                return {
                    "success": False,
                    "execution_id": None,
                    "status": "failed",
                    "error": result.get("error", "Workflow execution failed"),
                    "execution_time": execution_duration
                }
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_workflow_execution")
            return {
                "success": False,
                "execution_id": None,
                "status": "failed",
                "error": str(e),
                "execution_time": 0
            }
    
    async def get_execution(self, execution_id: str, user_context: Optional[UserContext] = None) -> Optional["WorkflowExecution"]:
        """Get workflow execution details."""
        try:
            result = await self.workflow_execution.get_execution(
                execution_id=execution_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                return result["execution"]
            else:
                return None
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_get_execution")
            return None
    
    async def cancel_execution(self, execution_id: str, user_context: Optional[UserContext] = None) -> bool:
        """Cancel a workflow execution."""
        try:
            success = await self.workflow_execution.cancel_execution(
                execution_id=execution_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return success
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_cancel_execution")
            return False
    
    async def pause_execution(self, execution_id: str, user_context: Optional[UserContext] = None) -> bool:
        """Pause a workflow execution."""
        try:
            success = await self.workflow_execution.pause_execution(
                execution_id=execution_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return success
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_pause_execution")
            return False
    
    async def resume_execution(self, execution_id: str, user_context: Optional[UserContext] = None) -> bool:
        """Resume a paused workflow execution."""
        try:
            success = await self.workflow_execution.resume_execution(
                execution_id=execution_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return success
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_resume_execution")
            return False
    
    async def get_execution_logs(self, execution_id: str, user_context: Optional[UserContext] = None) -> List[Dict[str, Any]]:
        """Get execution logs for a workflow."""
        try:
            result = await self.workflow_execution.get_execution_logs(
                execution_id=execution_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                return result["logs"]
            else:
                return []
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_get_execution_logs")
            return []
    
    async def create_task(self, task_data: Dict[str, Any], user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Create a new task."""
        try:
            result = await self.task_management.create_task(
                task_data=task_data,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_create_task")
            return {"success": False, "task_id": None, "error": str(e)}
    
    async def get_task(self, task_id: str, user_context: Optional[UserContext] = None) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        try:
            result = await self.task_management.get_task(
                task_id=task_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                return result["task"]
            else:
                return None
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_get_task")
            return None
    
    async def execute_task(self, task_id: str, task_data: Dict[str, Any], user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Execute a task."""
        try:
            start_time = datetime.utcnow()
            
            result = await self.task_management.execute_task(
                task_id=task_id,
                task_data=task_data,
                user_context=user_context.to_dict() if user_context else None
            )
            
            # Track task execution for analytics
            end_time = datetime.utcnow()
            execution_duration = (end_time - start_time).total_seconds()
            
            await self.orchestration_analytics.track_task_execution(
                task_id=task_id,
                task_type=task_data.get("task_type", "general"),
                user_id=user_context.user_id if user_context else "system",
                execution_duration=execution_duration,
                status="completed" if result["success"] else "failed"
            )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="conductor_execute_task")
            return {"success": False, "task_execution_id": None, "error": str(e)}
    
    # Note: Using standard FoundationServiceBase health check pattern
    # Custom health logic should be implemented in micro-modules, not in service health check
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_workflows(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get all workflows for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's workflows"}
            
            # Get tenant-specific workflows
            search_request = type('WorkflowSearchRequest', (), {
                'filters': {"tenant_id": tenant_id},
                'limit': 1000,
                'offset': 0
            })()
            
            workflows = await self.search_workflows(search_request, user_context)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_workflows", "conductor",
                    {"tenant_id": tenant_id, "workflow_count": len(workflows)}
                )
            
            return {"success": True, "workflows": workflows, "count": len(workflows)}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_workflows")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_workflow_metrics(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get workflow metrics for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's workflow metrics"}
            
            # Get tenant workflows
            tenant_workflows = await self.get_tenant_workflows(tenant_id, user_context)
            if not tenant_workflows.get("success"):
                return tenant_workflows
            
            workflows = tenant_workflows.get("workflows", [])
            
            # Calculate workflow metrics
            workflow_metrics = {
                "tenant_id": tenant_id,
                "total_workflows": len(workflows),
                "active_workflows": len([w for w in workflows if w.get("status") == "active"]),
                "completed_workflows": len([w for w in workflows if w.get("status") == "completed"]),
                "failed_workflows": len([w for w in workflows if w.get("status") == "failed"]),
                "average_execution_time": self._calculate_average_workflow_execution_time(workflows),
                "workflow_types": self._calculate_workflow_types(workflows)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_workflow_metrics", "conductor",
                    {"tenant_id": tenant_id, "total_workflows": workflow_metrics["total_workflows"]}
                )
            
            return {"success": True, "workflow_metrics": workflow_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_workflow_metrics")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_task_summary(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get task summary for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's task summary"}
            
            # Get tenant workflows to find associated tasks
            tenant_workflows = await self.get_tenant_workflows(tenant_id, user_context)
            if not tenant_workflows.get("success"):
                return tenant_workflows
            
            workflows = tenant_workflows.get("workflows", [])
            
            # Calculate task summary from workflows
            task_summary = {
                "tenant_id": tenant_id,
                "total_tasks": sum(w.get("task_count", 0) for w in workflows),
                "completed_tasks": sum(w.get("completed_tasks", 0) for w in workflows),
                "failed_tasks": sum(w.get("failed_tasks", 0) for w in workflows),
                "pending_tasks": sum(w.get("pending_tasks", 0) for w in workflows),
                "average_task_duration": self._calculate_average_task_duration(workflows),
                "task_types": self._calculate_task_types(workflows)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_task_summary", "conductor",
                    {"tenant_id": tenant_id, "total_tasks": task_summary["total_tasks"]}
                )
            
            return {"success": True, "task_summary": task_summary}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_task_summary")
            return {"success": False, "error": str(e)}
    
    def _calculate_average_workflow_execution_time(self, workflows: List[Any]) -> float:
        """Calculate average workflow execution time in minutes."""
        if not workflows:
            return 0.0
        
        execution_times = []
        for workflow in workflows:
            if hasattr(workflow, 'execution_time') and workflow.execution_time:
                execution_times.append(workflow.execution_time)
        
        return round(sum(execution_times) / len(execution_times), 2) if execution_times else 0.0
    
    def _calculate_workflow_types(self, workflows: List[Any]) -> Dict[str, int]:
        """Calculate distribution of workflow types."""
        type_counts = {}
        for workflow in workflows:
            workflow_type = getattr(workflow, 'workflow_type', 'unknown')
            type_counts[workflow_type] = type_counts.get(workflow_type, 0) + 1
        return type_counts
    
    def _calculate_average_task_duration(self, workflows: List[Any]) -> float:
        """Calculate average task duration in minutes."""
        if not workflows:
            return 0.0
        
        task_durations = []
        for workflow in workflows:
            if hasattr(workflow, 'task_durations') and workflow.task_durations:
                task_durations.extend(workflow.task_durations)
        
        return round(sum(task_durations) / len(task_durations), 2) if task_durations else 0.0
    
    def _calculate_task_types(self, workflows: List[Any]) -> Dict[str, int]:
        """Calculate distribution of task types."""
        type_counts = {}
        for workflow in workflows:
            if hasattr(workflow, 'task_types') and workflow.task_types:
                for task_type in workflow.task_types:
                    type_counts[task_type] = type_counts.get(task_type, 0) + 1
        return type_counts


class ConductorSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Conductor Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Conductor SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="ConductorService",
            version="1.0.0",
            description="Conductor Service - Multi-tenant workflow orchestration and task coordination",
            interface_name="IConductor",
            endpoints=self._create_all_endpoints(),
            tags=["workflow-orchestration", "task-coordination", "multi-tenant", "automation"],
            contact={"email": "conductor@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/conductor", "description": "Conductor Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Conductor Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Conductor specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/workflows",
                method="POST",
                summary="Create Workflow",
                description="Create a new workflow with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "object"}},
                        "metadata": {"type": "object"}
                    },
                    "required": ["name", "description", "steps"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Workflows", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/workflows/{workflow_id}",
                method="GET",
                summary="Get Workflow",
                description="Get workflow information",
                parameters=[
                    {
                        "name": "workflow_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Workflow ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "name": {"type": "string"},
                        "status": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "object"}}
                    }
                }),
                tags=["Workflows", "Information"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/workflows/{workflow_id}/execute",
                method="POST",
                summary="Execute Workflow",
                description="Execute a workflow with tenant awareness",
                parameters=[
                    {
                        "name": "workflow_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Workflow ID"
                    }
                ],
                request_schema={
                    "type": "object",
                    "properties": {
                        "parameters": {"type": "object"},
                        "priority": {"type": "string"}
                    }
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Workflows", "Execution"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tasks",
                method="GET",
                summary="List Tasks",
                description="List tasks for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tasks": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Tasks", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tasks/{task_id}",
                method="GET",
                summary="Get Task",
                description="Get task information",
                parameters=[
                    {
                        "name": "task_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Task ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "name": {"type": "string"},
                        "status": {"type": "string"},
                        "progress": {"type": "number"}
                    }
                }),
                tags=["Tasks", "Information"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/workflow-summary",
                method="GET",
                summary="Get Tenant Workflow Summary",
                description="Get workflow summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_workflows": {"type": "integer"},
                        "active_workflows": {"type": "integer"},
                        "completed_workflows": {"type": "integer"}
                    }
                }),
                tags=["Tenant", "Workflows"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/task-summary",
                method="GET",
                summary="Get Tenant Task Summary",
                description="Get task summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_tasks": {"type": "integer"},
                        "completed_tasks": {"type": "integer"},
                        "failed_tasks": {"type": "integer"},
                        "pending_tasks": {"type": "integer"}
                    }
                }),
                tags=["Tenant", "Tasks"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths
