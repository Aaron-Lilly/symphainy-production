#!/usr/bin/env python3
"""
Workflow Module - Conductor Service

Handles workflow operations using Workflow Orchestration Abstraction (Redis Graph).
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from bases.contracts.workflow_orchestration import (
    WorkflowDefinition, WorkflowNode, WorkflowEdge, NodeType,
    WorkflowExecutionRequest, WorkflowStatus
)


class Workflow:
    """Workflow module for Conductor Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def create_workflow(self, workflow_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create workflow using Workflow Orchestration Abstraction (Redis Graph)."""
        workflow_name = workflow_data.get("name", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "create_workflow_start",
            success=True,
            details={"workflow_name": workflow_name}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_management", "write"):
                        await self.service.record_health_metric("create_workflow_access_denied", 1.0, {"workflow_name": workflow_name})
                        await self.service.log_operation_with_telemetry("create_workflow_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to create workflow")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("create_workflow_tenant_denied", 1.0, {"workflow_name": workflow_name, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("create_workflow_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            workflow_id = str(uuid.uuid4())
            
            # Convert workflow_data to WorkflowDefinition
            nodes = [
                WorkflowNode(
                    id=node.get("id", str(uuid.uuid4())),
                    name=node.get("name", ""),
                    type=NodeType(node.get("type", "task"))
                )
                for node in workflow_data.get("tasks", [])
            ]
            
            edges = [
                WorkflowEdge(
                    id=edge.get("id", str(uuid.uuid4())),
                    source=edge.get("source"),
                    target=edge.get("target"),
                    condition=edge.get("condition")
                )
                for edge in workflow_data.get("dependencies", [])
            ]
            
            workflow_definition = WorkflowDefinition(
                id=workflow_id,
                name=workflow_name,
                description=workflow_data.get("description", ""),
                nodes=nodes,
                edges=edges,
                properties=workflow_data.get("properties", {}),
                created_at=datetime.utcnow()
            )
            
            # Create workflow via Workflow Orchestration Abstraction
            created_id = await self.service.workflow_orchestration_abstraction.create_workflow(workflow_definition)
            
            if created_id:
                self.service.workflow_templates[workflow_id] = workflow_definition
                
                # Record health metric
                await self.service.record_health_metric(
                    "workflow_created",
                    1.0,
                    {"workflow_id": workflow_id, "workflow_name": workflow_name}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "create_workflow_complete",
                    success=True,
                    details={"workflow_id": workflow_id, "workflow_name": workflow_name}
                )
                
                return workflow_id
            else:
                raise Exception("Failed to create workflow in Redis Graph")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "create_workflow")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "create_workflow_complete",
                success=False,
                details={"workflow_name": workflow_name, "error": str(e)}
            )
            raise
    
    async def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Execute workflow using Workflow Orchestration Abstraction (Redis Graph)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "execute_workflow_start",
            success=True,
            details={"workflow_id": workflow_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_management", "execute"):
                        await self.service.record_health_metric("execute_workflow_access_denied", 1.0, {"workflow_id": workflow_id})
                        await self.service.log_operation_with_telemetry("execute_workflow_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to execute workflow")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("execute_workflow_tenant_denied", 1.0, {"workflow_id": workflow_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("execute_workflow_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            execution_id = str(uuid.uuid4())
            
            # Create execution request
            execution_request = WorkflowExecutionRequest(
                workflow_id=workflow_id,
                input_data=parameters or {},
                execution_options={}
            )
            
            # Execute workflow via Workflow Orchestration Abstraction
            execution_id = await self.service.workflow_orchestration_abstraction.execute_workflow(execution_request)
            
            if execution_id:
                execution_context = {
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                    "parameters": parameters or {},
                    "started_at": datetime.utcnow().isoformat(),
                    "status": "running"
                }
                self.service.active_workflows[execution_id] = execution_context
                
                # Record health metric
                await self.service.record_health_metric(
                    "workflow_executed",
                    1.0,
                    {"execution_id": execution_id, "workflow_id": workflow_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "execute_workflow_complete",
                    success=True,
                    details={"execution_id": execution_id, "workflow_id": workflow_id}
                )
                
                return execution_id
            else:
                raise Exception("Failed to execute workflow in Redis Graph")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "execute_workflow")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "execute_workflow_complete",
                success=False,
                details={"workflow_id": workflow_id, "error": str(e)}
            )
            raise
    
    async def get_workflow_status(self, workflow_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get workflow status using Workflow Orchestration Abstraction (Redis Graph)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_workflow_status_start",
            success=True,
            details={"workflow_id": workflow_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_management", "read"):
                        await self.service.record_health_metric("get_workflow_status_access_denied", 1.0, {"workflow_id": workflow_id})
                        await self.service.log_operation_with_telemetry("get_workflow_status_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read workflow status")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_workflow_status_tenant_denied", 1.0, {"workflow_id": workflow_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_workflow_status_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get workflow status via Workflow Orchestration Abstraction
            execution = await self.service.workflow_orchestration_abstraction.get_workflow_execution(workflow_id)
            
            if execution:
                # Record health metric
                await self.service.record_health_metric(
                    "workflow_status_retrieved",
                    1.0,
                    {"workflow_id": workflow_id, "status": execution.status.value}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_workflow_status_complete",
                    success=True,
                    details={"workflow_id": workflow_id, "status": execution.status.value}
                )
                
                return {
                    "workflow_id": workflow_id,
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "current_node": execution.current_node,
                    "error": execution.error,
                    "success": True
                }
            else:
                await self.service.record_health_metric("workflow_status_not_found", 1.0, {"workflow_id": workflow_id})
                await self.service.log_operation_with_telemetry("get_workflow_status_complete", success=False, details={"workflow_id": workflow_id, "reason": "not_found"})
                return {
                    "workflow_id": workflow_id,
                    "status": "not_found",
                    "error": "Workflow not found",
                    "success": False
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_workflow_status")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_workflow_status_complete",
                success=False,
                details={"workflow_id": workflow_id, "error": str(e)}
            )
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def pause_workflow(self, workflow_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Pause workflow using Workflow Orchestration Abstraction (Redis Graph)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "pause_workflow_start",
            success=True,
            details={"workflow_id": workflow_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_management", "write"):
                        await self.service.record_health_metric("pause_workflow_access_denied", 1.0, {"workflow_id": workflow_id})
                        await self.service.log_operation_with_telemetry("pause_workflow_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to pause workflow")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Pause workflow via Workflow Orchestration Abstraction
            success = await self.service.workflow_orchestration_abstraction.pause_workflow(workflow_id)
            
            if success:
                await self.service.record_health_metric("workflow_paused", 1.0, {"workflow_id": workflow_id})
                await self.service.log_operation_with_telemetry("pause_workflow_complete", success=True, details={"workflow_id": workflow_id})
                return True
            else:
                await self.service.record_health_metric("workflow_pause_failed", 1.0, {"workflow_id": workflow_id})
                await self.service.log_operation_with_telemetry("pause_workflow_complete", success=False, details={"workflow_id": workflow_id})
                return False
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "pause_workflow")
            await self.service.log_operation_with_telemetry("pause_workflow_complete", success=False, details={"workflow_id": workflow_id, "error": str(e)})
            return False
    
    async def resume_workflow(self, workflow_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Resume workflow using Workflow Orchestration Abstraction (Redis Graph)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "resume_workflow_start",
            success=True,
            details={"workflow_id": workflow_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_management", "write"):
                        await self.service.record_health_metric("resume_workflow_access_denied", 1.0, {"workflow_id": workflow_id})
                        await self.service.log_operation_with_telemetry("resume_workflow_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to resume workflow")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Resume workflow via Workflow Orchestration Abstraction
            success = await self.service.workflow_orchestration_abstraction.resume_workflow(workflow_id)
            
            if success:
                await self.service.record_health_metric("workflow_resumed", 1.0, {"workflow_id": workflow_id})
                await self.service.log_operation_with_telemetry("resume_workflow_complete", success=True, details={"workflow_id": workflow_id})
                return True
            else:
                await self.service.record_health_metric("workflow_resume_failed", 1.0, {"workflow_id": workflow_id})
                await self.service.log_operation_with_telemetry("resume_workflow_complete", success=False, details={"workflow_id": workflow_id})
                return False
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "resume_workflow")
            await self.service.log_operation_with_telemetry("resume_workflow_complete", success=False, details={"workflow_id": workflow_id, "error": str(e)})
            return False







