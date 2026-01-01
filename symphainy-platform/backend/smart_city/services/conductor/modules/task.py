#!/usr/bin/env python3
"""
Task Module - Conductor Service

Handles task operations using Task Management Abstraction (Celery).
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from foundations.public_works_foundation.abstraction_contracts.task_management_protocol import (
    TaskRequest, TaskPriority, TaskStatus
)


class Task:
    """Task module for Conductor Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def submit_task(self, task_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Submit task using Task Management Abstraction (Celery)."""
        task_type = task_data.get("task_type", "generic_task")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "submit_task_start",
            success=True,
            details={"task_type": task_type}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "task_management", "write"):
                        await self.service.record_health_metric("submit_task_access_denied", 1.0, {"task_type": task_type})
                        await self.service.log_operation_with_telemetry("submit_task_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to submit task")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("submit_task_tenant_denied", 1.0, {"task_type": task_type, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("submit_task_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Create task request
            task_request = TaskRequest(
                task_name=task_type,
                args=task_data.get("parameters", {}).get("args", []),
                kwargs=task_data.get("parameters", {}).get("kwargs", {}),
                queue=task_data.get("queue", "default"),
                priority=TaskPriority(task_data.get("priority", "normal").upper()) if isinstance(task_data.get("priority"), str) else TaskPriority.NORMAL,
                retries=task_data.get("retries", 3),
                timeout=task_data.get("timeout", 300),
                metadata=task_data.get("metadata", {})
            )
            
            # Submit task via Task Management Abstraction (Celery)
            task_id = await self.service.task_management_abstraction.create_task(task_request)
            
            if task_id:
                task_definition = {
                    "task_id": task_id,
                    "task_type": task_type,
                    "parameters": task_data.get("parameters", {}),
                    "priority": task_data.get("priority", "normal"),
                    "submitted_at": datetime.utcnow().isoformat(),
                    "status": "submitted"
                }
                self.service.task_queue.append(task_definition)
                
                # Record health metric
                await self.service.record_health_metric(
                    "task_submitted",
                    1.0,
                    {"task_id": task_id, "task_type": task_type}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "submit_task_complete",
                    success=True,
                    details={"task_id": task_id, "task_type": task_type}
                )
                
                return task_id
            else:
                raise Exception("Failed to submit task in Celery")
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "submit_task")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "submit_task_complete",
                success=False,
                details={"task_type": task_type, "error": str(e)}
            )
            raise
    
    async def get_task_status(self, task_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get task status using Task Management Abstraction (Celery)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_task_status_start",
            success=True,
            details={"task_id": task_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "task_management", "read"):
                        await self.service.record_health_metric("get_task_status_access_denied", 1.0, {"task_id": task_id})
                        await self.service.log_operation_with_telemetry("get_task_status_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read task status")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_task_status_tenant_denied", 1.0, {"task_id": task_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_task_status_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get task status via Task Management Abstraction
            task_info = await self.service.task_management_abstraction.get_task_info(task_id)
            task_result = await self.service.task_management_abstraction.get_task_result(task_id)
            
            if task_info or task_result:
                status = task_result.status if task_result else (task_info.status if task_info else TaskStatus.PENDING)
                
                # Record health metric
                await self.service.record_health_metric(
                    "task_status_retrieved",
                    1.0,
                    {"task_id": task_id, "status": status.value}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_task_status_complete",
                    success=True,
                    details={"task_id": task_id, "status": status.value}
                )
                
                return {
                    "task_id": task_id,
                    "status": status.value,
                    "result": task_result.result if task_result else None,
                    "error": task_result.error if task_result else None,
                    "started_at": (task_result.started_at.isoformat() if task_result and task_result.started_at else None) or (task_info.started_at.isoformat() if task_info and task_info.started_at else None),
                    "completed_at": task_result.completed_at.isoformat() if task_result and task_result.completed_at else None,
                    "retry_count": task_result.retry_count if task_result else (task_info.retry_count if task_info else 0),
                    "success": True
                }
            else:
                await self.service.record_health_metric("task_status_not_found", 1.0, {"task_id": task_id})
                await self.service.log_operation_with_telemetry("get_task_status_complete", success=False, details={"task_id": task_id, "reason": "not_found"})
                return {
                    "task_id": task_id,
                    "status": "not_found",
                    "error": "Task not found",
                    "success": False
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_task_status")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_task_status_complete",
                success=False,
                details={"task_id": task_id, "error": str(e)}
            )
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    async def cancel_task(self, task_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Cancel task using Task Management Abstraction (Celery)."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "cancel_task_start",
            success=True,
            details={"task_id": task_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "task_management", "write"):
                        await self.service.record_health_metric("cancel_task_access_denied", 1.0, {"task_id": task_id})
                        await self.service.log_operation_with_telemetry("cancel_task_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to cancel task")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Cancel task via Task Management Abstraction
            success = await self.service.task_management_abstraction.cancel_task(task_id)
            
            if success:
                await self.service.record_health_metric("task_cancelled", 1.0, {"task_id": task_id})
                await self.service.log_operation_with_telemetry("cancel_task_complete", success=True, details={"task_id": task_id})
                return True
            else:
                await self.service.record_health_metric("task_cancel_failed", 1.0, {"task_id": task_id})
                await self.service.log_operation_with_telemetry("cancel_task_complete", success=False, details={"task_id": task_id})
                return False
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "cancel_task")
            await self.service.log_operation_with_telemetry("cancel_task_complete", success=False, details={"task_id": task_id, "error": str(e)})
            return False







