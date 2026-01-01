#!/usr/bin/env python3
"""
Session Management Module - Traffic Cop Service

Handles session operations using Public Works session abstraction.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    SessionRequest, SessionResponse, SessionStatus
)


class SessionManagement:
    """Session management module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def create_session(self, request: SessionRequest, user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Create a new session using Public Works session abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "create_session_start",
            success=True,
            details={"session_id": request.session_id, "user_id": request.user_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "session_management", "write"):
                        await self.service.record_health_metric("create_session_access_denied", 1.0, {"session_id": request.session_id})
                        await self.service.log_operation_with_telemetry("create_session_complete", success=False)
                        return SessionResponse(
                            success=False,
                            session_id=request.session_id,
                            status=SessionStatus.INACTIVE,
                            error="Access denied: insufficient permissions"
                        )
            
            self.service.traffic_metrics["active_sessions"] += 1
            
            # Use Public Works session abstraction
            session_result = await self.service.session_abstraction.create_session(
                session_id=request.session_id,
                user_id=request.user_id,
                session_data={
                    "session_type": request.session_type,
                    "context": request.context,
                    "created_at": datetime.utcnow().isoformat(),
                    "ttl_seconds": request.ttl_seconds
                }
            )
            
            if session_result:
                # Record health metric
                await self.service.record_health_metric(
                    "session_created",
                    1.0,
                    {"session_id": request.session_id, "user_id": request.user_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "create_session_complete",
                    success=True,
                    details={"session_id": request.session_id, "user_id": request.user_id}
                )
                
                return SessionResponse(
                    success=True,
                    session_id=request.session_id,
                    status=SessionStatus.ACTIVE,
                    expires_at=(datetime.utcnow() + timedelta(seconds=request.ttl_seconds)).isoformat()
                )
            else:
                await self.service.record_health_metric("session_creation_failed", 1.0, {"session_id": request.session_id})
                await self.service.log_operation_with_telemetry("create_session_complete", success=False, details={"session_id": request.session_id, "reason": "creation_failed"})
                return SessionResponse(
                    success=False,
                    session_id=request.session_id,
                    status=SessionStatus.INACTIVE,
                    error="Failed to create session"
                )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "create_session")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "create_session_complete",
                success=False,
                details={"session_id": request.session_id, "error": str(e)}
            )
            
            return SessionResponse(
                success=False,
                session_id=request.session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    async def get_session(self, session_id: str, user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Get session information using Public Works session abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_session_start",
            success=True,
            details={"session_id": session_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "session_management", "read"):
                        await self.service.record_health_metric("get_session_access_denied", 1.0, {"session_id": session_id})
                        await self.service.log_operation_with_telemetry("get_session_complete", success=False)
                        return SessionResponse(
                            success=False,
                            session_id=session_id,
                            status=SessionStatus.INACTIVE,
                            error="Access denied: insufficient permissions"
                        )
            
            session_data = await self.service.session_abstraction.get_session(session_id)
            
            if session_data:
                # Record health metric
                await self.service.record_health_metric(
                    "session_retrieved",
                    1.0,
                    {"session_id": session_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_session_complete",
                    success=True,
                    details={"session_id": session_id}
                )
                
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    status=SessionStatus.ACTIVE
                )
            else:
                await self.service.record_health_metric("session_not_found", 1.0, {"session_id": session_id})
                await self.service.log_operation_with_telemetry("get_session_complete", success=False, details={"session_id": session_id, "reason": "not_found"})
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Session not found"
                )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_session")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_session_complete",
                success=False,
                details={"session_id": session_id, "error": str(e)}
            )
            
            return SessionResponse(
                success=False,
                session_id=session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    async def update_session(self, session_id: str, updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Update session data using Public Works session abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "update_session_start",
            success=True,
            details={"session_id": session_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "session_management", "write"):
                        await self.service.record_health_metric("update_session_access_denied", 1.0, {"session_id": session_id})
                        await self.service.log_operation_with_telemetry("update_session_complete", success=False)
                        return SessionResponse(
                            success=False,
                            session_id=session_id,
                            status=SessionStatus.INACTIVE,
                            error="Access denied: insufficient permissions"
                        )
            
            success = await self.service.session_abstraction.update_session(session_id, updates)
            
            if success:
                # Record health metric
                await self.service.record_health_metric(
                    "session_updated",
                    1.0,
                    {"session_id": session_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "update_session_complete",
                    success=True,
                    details={"session_id": session_id}
                )
                
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    status=SessionStatus.ACTIVE
                )
            else:
                await self.service.record_health_metric("session_update_failed", 1.0, {"session_id": session_id})
                await self.service.log_operation_with_telemetry("update_session_complete", success=False, details={"session_id": session_id, "reason": "update_failed"})
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Failed to update session"
                )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "update_session")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "update_session_complete",
                success=False,
                details={"session_id": session_id, "error": str(e)}
            )
            
            return SessionResponse(
                success=False,
                session_id=session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )
    
    async def destroy_session(self, session_id: str, user_context: Optional[Dict[str, Any]] = None) -> SessionResponse:
        """Destroy a session using Public Works session abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "destroy_session_start",
            success=True,
            details={"session_id": session_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "session_management", "write"):
                        await self.service.record_health_metric("destroy_session_access_denied", 1.0, {"session_id": session_id})
                        await self.service.log_operation_with_telemetry("destroy_session_complete", success=False)
                        return SessionResponse(
                            success=False,
                            session_id=session_id,
                            status=SessionStatus.INACTIVE,
                            error="Access denied: insufficient permissions"
                        )
            
            success = await self.service.session_abstraction.destroy_session(session_id)
            
            if success:
                self.service.traffic_metrics["active_sessions"] = max(0, self.service.traffic_metrics["active_sessions"] - 1)
                
                # Record health metric
                await self.service.record_health_metric(
                    "session_destroyed",
                    1.0,
                    {"session_id": session_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "destroy_session_complete",
                    success=True,
                    details={"session_id": session_id}
                )
                
                return SessionResponse(
                    success=True,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE
                )
            else:
                await self.service.record_health_metric("session_destroy_failed", 1.0, {"session_id": session_id})
                await self.service.log_operation_with_telemetry("destroy_session_complete", success=False, details={"session_id": session_id, "reason": "destroy_failed"})
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Failed to destroy session"
                )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "destroy_session")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "destroy_session_complete",
                success=False,
                details={"session_id": session_id, "error": str(e)}
            )
            
            return SessionResponse(
                success=False,
                session_id=session_id,
                status=SessionStatus.INACTIVE,
                error=str(e)
            )







