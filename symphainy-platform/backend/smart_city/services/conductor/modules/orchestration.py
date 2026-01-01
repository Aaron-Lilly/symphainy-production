#!/usr/bin/env python3
"""
Orchestration Module - Conductor Service

Handles orchestration pattern operations using Workflow Orchestration Abstraction (Redis Graph).
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from bases.contracts.workflow_orchestration import (
    WorkflowDefinition, WorkflowNode, WorkflowEdge, NodeType,
    WorkflowExecutionRequest, WorkflowStatus
)


class Orchestration:
    """Orchestration module for Conductor Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def create_orchestration_pattern(self, pattern_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create orchestration pattern using Graph DSL via Workflow Orchestration Abstraction."""
        pattern_name = pattern_data.get("name", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "create_orchestration_pattern_start",
            success=True,
            details={"pattern_name": pattern_name}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_orchestration", "write"):
                        await self.service.record_health_metric("create_orchestration_pattern_access_denied", 1.0, {"pattern_name": pattern_name})
                        await self.service.log_operation_with_telemetry("create_orchestration_pattern_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to create orchestration pattern")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("create_orchestration_pattern_tenant_denied", 1.0, {"pattern_name": pattern_name, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("create_orchestration_pattern_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            pattern_id = str(uuid.uuid4())
            
            # Convert pattern_data to WorkflowDefinition (Graph DSL)
            nodes = [
                WorkflowNode(
                    id=node.get("id", str(uuid.uuid4())),
                    name=node.get("name", ""),
                    type=NodeType(node.get("type", "task"))
                )
                for node in pattern_data.get("nodes", [])
            ]
            
            edges = [
                WorkflowEdge(
                    id=edge.get("id", str(uuid.uuid4())),
                    source=edge.get("source"),
                    target=edge.get("target"),
                    condition=edge.get("condition")
                )
                for edge in pattern_data.get("edges", [])
            ]
            
            workflow_definition = WorkflowDefinition(
                id=pattern_id,
                name=pattern_name,
                description=pattern_data.get("description", ""),
                nodes=nodes,
                edges=edges,
                properties=pattern_data.get("properties", {}),
                created_at=datetime.utcnow()
            )
            
            # Create pattern via Workflow Orchestration Abstraction (Redis Graph)
            created_id = await self.service.workflow_orchestration_abstraction.create_workflow(workflow_definition)
            
            if created_id:
                self.service.orchestration_patterns[pattern_id] = workflow_definition
                
                # Record health metric
                await self.service.record_health_metric(
                    "orchestration_pattern_created",
                    1.0,
                    {"pattern_id": pattern_id, "pattern_name": pattern_name}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "create_orchestration_pattern_complete",
                    success=True,
                    details={"pattern_id": pattern_id, "pattern_name": pattern_name}
                )
                
                return pattern_id
            else:
                raise Exception("Failed to create orchestration pattern in Redis Graph")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "create_orchestration_pattern")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "create_orchestration_pattern_complete",
                success=False,
                details={"pattern_name": pattern_name, "error": str(e)}
            )
            raise
    
    async def execute_orchestration_pattern(self, pattern_id: str, context: Dict[str, Any] = None, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Execute orchestration pattern using Workflow Orchestration Abstraction (Redis Graph)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "execute_orchestration_pattern_start",
            success=True,
            details={"pattern_id": pattern_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_orchestration", "execute"):
                        await self.service.record_health_metric("execute_orchestration_pattern_access_denied", 1.0, {"pattern_id": pattern_id})
                        await self.service.log_operation_with_telemetry("execute_orchestration_pattern_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to execute orchestration pattern")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("execute_orchestration_pattern_tenant_denied", 1.0, {"pattern_id": pattern_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("execute_orchestration_pattern_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            execution_id = str(uuid.uuid4())
            
            # Create execution request
            execution_request = WorkflowExecutionRequest(
                workflow_id=pattern_id,
                input_data=context or {},
                execution_options={}
            )
            
            # Execute pattern via Workflow Orchestration Abstraction
            execution_id = await self.service.workflow_orchestration_abstraction.execute_workflow(execution_request)
            
            if execution_id:
                execution_context = {
                    "execution_id": execution_id,
                    "pattern_id": pattern_id,
                    "context": context or {},
                    "started_at": datetime.utcnow().isoformat(),
                    "status": "running"
                }
                self.service.active_orchestrations[execution_id] = execution_context
                
                # Record health metric
                await self.service.record_health_metric(
                    "orchestration_pattern_executed",
                    1.0,
                    {"execution_id": execution_id, "pattern_id": pattern_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "execute_orchestration_pattern_complete",
                    success=True,
                    details={"execution_id": execution_id, "pattern_id": pattern_id}
                )
                
                return execution_id
            else:
                raise Exception("Failed to execute orchestration pattern in Redis Graph")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "execute_orchestration_pattern")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "execute_orchestration_pattern_complete",
                success=False,
                details={"pattern_id": pattern_id, "error": str(e)}
            )
            raise
    
    async def get_orchestration_status(self, execution_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get orchestration execution status using Workflow Orchestration Abstraction (Redis Graph)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_orchestration_status_start",
            success=True,
            details={"execution_id": execution_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "workflow_orchestration", "read"):
                        await self.service.record_health_metric("get_orchestration_status_access_denied", 1.0, {"execution_id": execution_id})
                        await self.service.log_operation_with_telemetry("get_orchestration_status_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read orchestration status")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_orchestration_status_tenant_denied", 1.0, {"execution_id": execution_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_orchestration_status_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get execution status via Workflow Orchestration Abstraction
            execution = await self.service.workflow_orchestration_abstraction.get_workflow_execution(execution_id)
            
            if execution:
                # Record health metric
                await self.service.record_health_metric(
                    "orchestration_status_retrieved",
                    1.0,
                    {"execution_id": execution_id, "status": execution.status.value}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_orchestration_status_complete",
                    success=True,
                    details={"execution_id": execution_id, "status": execution.status.value}
                )
                
                return {
                    "execution_id": execution_id,
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "current_node": execution.current_node,
                    "error": execution.error,
                    "success": True
                }
            else:
                await self.service.record_health_metric("orchestration_status_not_found", 1.0, {"execution_id": execution_id})
                await self.service.log_operation_with_telemetry("get_orchestration_status_complete", success=False, details={"execution_id": execution_id, "reason": "not_found"})
                return {
                    "execution_id": execution_id,
                    "status": "not_found",
                    "error": "Orchestration execution not found",
                    "success": False
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_orchestration_status")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_orchestration_status_complete",
                success=False,
                details={"execution_id": execution_id, "error": str(e)}
            )
            return {
                "execution_id": execution_id,
                "status": "error",
                "error": str(e),
                "success": False
            }







