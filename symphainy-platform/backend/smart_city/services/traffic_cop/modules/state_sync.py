#!/usr/bin/env python3
"""
State Sync Module - Traffic Cop Service

Handles state synchronization using Public Works state management abstraction.
"""

import uuid
from typing import Optional, Dict, Any
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    StateSyncRequest, StateSyncResponse, StateSyncStatus
)


class StateSync:
    """State synchronization module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def sync_state(self, request: StateSyncRequest, user_context: Optional[Dict[str, Any]] = None) -> StateSyncResponse:
        """Synchronize state between pillars using Public Works state management abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "sync_state_start",
            success=True,
            details={"key": request.key, "source_pillar": request.source_pillar, "target_pillar": request.target_pillar}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "state_sync", "write"):
                        await self.service.record_health_metric("sync_state_access_denied", 1.0, {"key": request.key})
                        await self.service.log_operation_with_telemetry("sync_state_complete", success=False)
                        return StateSyncResponse(
                            success=False,
                            key=request.key,
                            sync_status=StateSyncStatus.FAILED,
                            error="Access denied: insufficient permissions"
                        )
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("sync_state_tenant_denied", 1.0, {"key": request.key, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("sync_state_complete", success=False)
                            return StateSyncResponse(
                                success=False,
                                key=request.key,
                                sync_status=StateSyncStatus.FAILED,
                                error=f"Tenant access denied: {tenant_id}"
                            )
            
            self.service.traffic_metrics["state_sync_operations"] += 1
            
            # Use Public Works state management abstraction
            sync_result = await self.service.state_management_abstraction.sync_state(
                key=request.key,
                source_pillar=request.source_pillar,
                target_pillar=request.target_pillar,
                state_data=request.state_data,
                sync_type=request.sync_type,
                priority=request.priority
            )
            
            if sync_result:
                sync_id = str(uuid.uuid4())
                
                # Record health metric
                await self.service.record_health_metric(
                    "state_synced",
                    1.0,
                    {"key": request.key, "source_pillar": request.source_pillar, "target_pillar": request.target_pillar, "sync_id": sync_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "sync_state_complete",
                    success=True,
                    details={"key": request.key, "sync_id": sync_id}
                )
                
                return StateSyncResponse(
                    success=True,
                    key=request.key,
                    sync_status=StateSyncStatus.COMPLETED,
                    sync_id=sync_id
                )
            else:
                await self.service.record_health_metric("state_sync_failed", 1.0, {"key": request.key})
                await self.service.log_operation_with_telemetry("sync_state_complete", success=False, details={"key": request.key, "reason": "sync_failed"})
                return StateSyncResponse(
                    success=False,
                    key=request.key,
                    sync_status=StateSyncStatus.FAILED,
                    error="Failed to synchronize state"
                )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "sync_state")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "sync_state_complete",
                success=False,
                details={"key": request.key, "error": str(e)}
            )
            
            return StateSyncResponse(
                success=False,
                key=request.key,
                sync_status=StateSyncStatus.FAILED,
                error=str(e)
            )
    
    async def get_state_sync_status(self, sync_id: str) -> StateSyncResponse:
        """Get state synchronization status."""
        try:
            # This would typically check the status from Redis
            # For now, return a mock status
            return StateSyncResponse(
                success=True,
                key="unknown",
                sync_status=StateSyncStatus.COMPLETED,
                sync_id=sync_id
            )
            
        except Exception as e:
            self.service._log("error", f"Failed to get state sync status: {e}")
            return StateSyncResponse(
                success=False,
                key="unknown",
                sync_status=StateSyncStatus.FAILED,
                error=str(e)
            )







