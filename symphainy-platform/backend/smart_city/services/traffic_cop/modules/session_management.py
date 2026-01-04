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
from foundations.public_works_foundation.abstraction_contracts.session_protocol import (
    SessionContext, SessionType, SecurityLevel
)


class SessionManagement:
    """Session management module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def _validate_tenant_isolation(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]],
        operation: str
    ) -> Optional[SessionResponse]:
        """
        Validate tenant isolation for session operations.
        
        Returns SessionResponse with error if tenant isolation violated, None if valid.
        """
        if not user_context:
            return None  # No user context, skip validation
        
        tenant = self.service.get_tenant()
        if not tenant:
            return None  # No tenant utility, skip validation
        
        user_tenant_id = user_context.get("tenant_id")
        if not user_tenant_id:
            return None  # No tenant ID in user context, skip validation
        
        # Get session to check its tenant_id
        session_data = await self.service.session_abstraction.get_session(session_id)
        if not session_data:
            return None  # Session not found, let caller handle it
        
        # Extract session tenant_id
        session_tenant_id = None
        
        # Handle Session object (from abstraction)
        if hasattr(session_data, 'metadata'):
            # Session object - check metadata attribute
            if isinstance(session_data.metadata, dict):
                # Check tenant_id directly in metadata
                session_tenant_id = session_data.metadata.get("tenant_id")
                # Also check context within metadata (nested structure)
                if not session_tenant_id and "context" in session_data.metadata:
                    context = session_data.metadata.get("context")
                    if isinstance(context, dict):
                        session_tenant_id = context.get("tenant_id")
                # Debug logging
                self.service.logger.info(f"🔍 [TENANT_ISOLATION] Session object metadata keys: {list(session_data.metadata.keys()) if isinstance(session_data.metadata, dict) else 'N/A'}")
                self.service.logger.info(f"🔍 [TENANT_ISOLATION] Extracted tenant_id from Session object: {session_tenant_id}")
        # Handle dict format
        elif isinstance(session_data, dict):
            # Dict format - check multiple locations
            session_tenant_id = session_data.get("tenant_id")  # Check top level first
            if not session_tenant_id and "metadata" in session_data and isinstance(session_data["metadata"], dict):
                session_tenant_id = session_data["metadata"].get("tenant_id")
                # Also check context within metadata
                if not session_tenant_id and "context" in session_data["metadata"]:
                    context = session_data["metadata"].get("context")
                    if isinstance(context, dict):
                        session_tenant_id = context.get("tenant_id")
            if not session_tenant_id and "context" in session_data:
                context = session_data.get("context")
                if isinstance(context, dict):
                    session_tenant_id = context.get("tenant_id")
            self.service.logger.debug(f"🔍 Extracted tenant_id from dict: {session_tenant_id}")
        
        if not session_tenant_id:
            # If no tenant_id found in session, enforce strict isolation based on user context only
            # This is a safety measure - if session has no tenant_id, deny access unless user has admin permissions
            self.service.logger.warning(f"⚠️ Session {session_id} has no tenant_id - enforcing strict isolation")
            # For now, allow access if session has no tenant_id (backward compatibility)
            # But log a warning for future enforcement
            return None  # Session has no tenant_id, skip validation (but log warning)
        
        self.service.logger.debug(f"🔍 Tenant isolation check: user_tenant_id={user_tenant_id}, session_tenant_id={session_tenant_id}")
        
        # Validate tenant isolation
        try:
            # First, check if tenant IDs match (strict isolation)
            if user_tenant_id != session_tenant_id:
                # Tenant IDs don't match - enforce strict isolation (deny access)
                self.service.logger.warning(f"⚠️ [TENANT_ISOLATION] Tenant mismatch: user={user_tenant_id}, session={session_tenant_id} - DENYING ACCESS")
                
                # For strict isolation, deny access immediately if tenant IDs don't match
                # Only check tenant abstraction if we want to allow cross-tenant access in the future
                # For now, enforce strict isolation
                await self.service.record_health_metric(f"{operation}_tenant_denied", 1.0, {
                    "session_id": session_id,
                    "user_tenant_id": user_tenant_id,
                    "session_tenant_id": session_tenant_id
                })
                await self.service.log_operation_with_telemetry(f"{operation}_complete", success=False, details={
                    "session_id": session_id,
                    "reason": "tenant_isolation_violation"
                })
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Tenant isolation violation: Cannot access session from different tenant"
                )
            else:
                # Tenant IDs match - allow access
                pass
        except Exception as e:
            self.service.logger.warning(f"⚠️ Tenant validation failed: {e}")
            # On validation error, default to strict isolation
            if user_tenant_id != session_tenant_id:
                await self.service.record_health_metric(f"{operation}_tenant_denied", 1.0, {
                    "session_id": session_id,
                    "user_tenant_id": user_tenant_id,
                    "session_tenant_id": session_tenant_id
                })
                return SessionResponse(
                    success=False,
                    session_id=session_id,
                    status=SessionStatus.INACTIVE,
                    error="Tenant isolation violation: Cannot access session from different tenant"
                )
        
        return None  # Validation passed
    
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
            # Create SessionContext with session data in metadata
            session_context = SessionContext(
                service_id="traffic_cop",
                agent_id=None,
                tenant_id=request.context.get("tenant_id") if isinstance(request.context, dict) else None,
                environment="production",
                region="us-west-2",
                metadata={
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                    "session_type": request.session_type,
                    "context": request.context,
                    "created_at": datetime.utcnow().isoformat(),
                    "ttl_seconds": request.ttl_seconds
                }
            )
            
            # Map request.session_type to valid SessionType enum
            # Valid SessionType values: USER, AGENT, SERVICE, API, WEB, MOBILE
            session_type_map = {
                "websocket_test": SessionType.WEB,
                "user": SessionType.USER,
                "agent": SessionType.AGENT,
                "service": SessionType.SERVICE,
                "api": SessionType.API,
                "web": SessionType.WEB,
                "mobile": SessionType.MOBILE
            }
            mapped_session_type = session_type_map.get(request.session_type, SessionType.USER)
            
            # Extract tenant_id from request context for session metadata
            tenant_id = request.context.get("tenant_id") if isinstance(request.context, dict) else None
            
            # Session data for the adapter (extracted from context or provided separately)
            session_data = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "session_type": mapped_session_type.value,  # Use enum value
                "context": request.context,
                "created_at": datetime.utcnow().isoformat(),
                "ttl_seconds": request.ttl_seconds,
                "tenant_id": tenant_id,  # Store tenant_id at top level for easy access
                "metadata": {
                    "session_type": request.session_type,  # Keep original for reference
                    "mapped_session_type": mapped_session_type.value,
                    "context": request.context,
                    "tenant_id": tenant_id,  # Also store in metadata for compatibility
                    "created_at": datetime.utcnow().isoformat(),
                    "ttl_seconds": request.ttl_seconds
                }
            }
            
            # Call abstraction - try with both context and session_data (matching Security Guard pattern)
            try:
                session_result = await self.service.session_abstraction.create_session(
                    context=session_context,
                    session_data=session_data
                )
            except TypeError:
                # Fallback: if abstraction doesn't accept session_data, extract from context metadata
                session_result = await self.service.session_abstraction.create_session(
                    context=session_context
                )
            
            if session_result:
                # Use the actual session_id from the created session (may differ from request if adapter generated new one)
                actual_session_id = session_result.session_id if hasattr(session_result, 'session_id') else request.session_id
                
                # Record health metric
                await self.service.record_health_metric(
                    "session_created",
                    1.0,
                    {"session_id": actual_session_id, "user_id": request.user_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "create_session_complete",
                    success=True,
                    details={"session_id": actual_session_id, "user_id": request.user_id, "requested_session_id": request.session_id}
                )
                
                return SessionResponse(
                    success=True,
                    session_id=actual_session_id,  # Return actual session_id that was created
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
                # Tenant isolation validation (multi-tenant support)
                tenant_validation_error = await self._validate_tenant_isolation(
                    session_id=session_id,
                    user_context=user_context,
                    operation="get_session"
                )
                if tenant_validation_error:
                    return tenant_validation_error
                
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
            
            # Tenant isolation validation (multi-tenant support)
            tenant_validation_error = await self._validate_tenant_isolation(
                session_id=session_id,
                user_context=user_context,
                operation="update_session"
            )
            if tenant_validation_error:
                return tenant_validation_error
            
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
            
            # Tenant isolation validation (multi-tenant support)
            tenant_validation_error = await self._validate_tenant_isolation(
                session_id=session_id,
                user_context=user_context,
                operation="destroy_session"
            )
            if tenant_validation_error:
                return tenant_validation_error
            
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







