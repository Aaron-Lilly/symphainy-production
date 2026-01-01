#!/usr/bin/env python3
"""
Security Guard Service - Refactored with Clean Separation of Concerns

Pure enforcement service with no context building logic.
This is the refactored security capability with clean separation of concerns.

WHAT (Smart City Role): I handle security enforcement and resolution
HOW (Service Implementation): I use clean interfaces with pure enforcement logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

# Import context utilities (no enforcement logic)
from utilities.security_context_utility import SecurityContextUtility, SecurityContext, TraceContext
from utilities.tenant_context_utility import TenantContextUtility, TenantContext, IsolationContext, FeatureContext
from utilities.audit_context_utility import AuditContextUtility, AuditContext, SecurityEvent

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class EnforcementResult:
    """Enforcement result data structure."""
    success: bool
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class SecurityGuardService:
    """
    Security Guard Service - Refactored with Clean Separation of Concerns
    
    Pure enforcement service with no context building logic.
    This service only handles enforcement and resolution - it does not build context.
    """
    
    def __init__(self, 
                 security_context_utility: SecurityContextUtility,
                 tenant_context_utility: TenantContextUtility,
                 audit_context_utility: AuditContextUtility):
        """Initialize Security Guard Service with context utilities."""
        self.security_context = security_context_utility
        self.tenant_context = tenant_context_utility
        self.audit_context = audit_context_utility
        self.logger = self.service.di_container.get_logger("SecurityGuardService")
        
        # Enforcement state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.authorization_policies: Dict[str, List[str]] = {}
        
        self.logger.info("✅ Security Guard Service initialized with clean separation of concerns")
    
    # ============================================================================
    # AUTHENTICATION ENFORCEMENT (Pure Enforcement)
    # ============================================================================
    
    async def enforce_authentication(self, credentials: Dict[str, Any]) -> EnforcementResult:
        """Enforce authentication - pure enforcement logic."""
        try:
            # Build user context using utility (no enforcement decisions)
            user_context = await self.security_context.build_user_context_from_credentials(credentials)
            
            # Enforce authentication rules
            if not user_context.user_id:
                return EnforcementResult(
                    success=False,
                    message="Authentication failed: Invalid credentials",
                    context={"error": "invalid_credentials"}
                )
            
            # Check if user is active (enforcement rule)
            if not await self._is_user_active(user_context.user_id):
                return EnforcementResult(
                    success=False,
                    message="Authentication failed: User account is inactive",
                    context={"error": "user_inactive", "user_id": user_context.user_id}
                )
            
            # Audit authentication success
            trace_context = await self.security_context.build_trace_context("auth_request")
            audit_context = await self.audit_context.build_audit_context(
                user_context, "authenticate", "user", trace_context
            )
            await self._audit_security_event(audit_context)
            
            self.logger.info(f"✅ Authentication enforced for user: {user_context.user_id}")
            return EnforcementResult(
                success=True,
                message="Authentication successful",
                context={"user_id": user_context.user_id, "tenant_id": user_context.tenant_id}
            )
            
        except Exception as e:
            self.logger.error(f"Authentication enforcement error: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Authentication enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def enforce_token_validation(self, token: str) -> EnforcementResult:
        """Enforce token validation - pure enforcement logic."""
        try:
            # Build user context using utility (no enforcement decisions)
            user_context = await self.security_context.build_user_context(token)
            
            # Enforce token validation rules
            if not user_context.user_id:
                return EnforcementResult(
                    success=False,
                    message="Token validation failed: Invalid token",
                    context={"error": "invalid_token"}
                )
            
            # Check if token is not expired (enforcement rule)
            if not self.security_context.is_context_valid(user_context):
                return EnforcementResult(
                    success=False,
                    message="Token validation failed: Token expired",
                    context={"error": "token_expired", "user_id": user_context.user_id}
                )
            
            # Audit token validation success
            trace_context = await self.security_context.build_trace_context("token_validation")
            audit_context = await self.audit_context.build_audit_context(
                user_context, "validate_token", "user", trace_context
            )
            await self._audit_security_event(audit_context)
            
            self.logger.info(f"✅ Token validation enforced for user: {user_context.user_id}")
            return EnforcementResult(
                success=True,
                message="Token validation successful",
                context={"user_id": user_context.user_id, "tenant_id": user_context.tenant_id}
            )
            
        except Exception as e:
            self.logger.error(f"Token validation enforcement error: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Token validation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    # ============================================================================
    # AUTHORIZATION ENFORCEMENT (Pure Enforcement)
    # ============================================================================
    
    async def enforce_authorization(self, 
                                  user_context: SecurityContext,
                                  action: str, 
                                  resource: str) -> EnforcementResult:
        """Enforce authorization - pure enforcement logic."""
        try:
            # Build tenant isolation context using utility (no enforcement decisions)
            isolation_context = await self.tenant_context.build_tenant_isolation_context(
                user_context.tenant_id or "unknown", resource
            )
            
            # Enforce tenant isolation (enforcement rule)
            if not await self._validate_tenant_isolation(isolation_context):
                return EnforcementResult(
                    success=False,
                    message="Authorization failed: Cross-tenant access denied",
                    context={"error": "cross_tenant_access", "user_tenant": user_context.tenant_id, "resource": resource}
                )
            
            # Enforce authorization rules
            if not await self._validate_user_authorization(user_context, action, resource):
                return EnforcementResult(
                    success=False,
                    message=f"Authorization failed: Action '{action}' not authorized for resource '{resource}'",
                    context={"error": "unauthorized_action", "user_id": user_context.user_id, "action": action, "resource": resource}
                )
            
            # Audit authorization success
            trace_context = await self.security_context.build_trace_context("authorization_request")
            audit_context = await self.audit_context.build_audit_context(
                user_context, action, resource, trace_context
            )
            await self._audit_security_event(audit_context)
            
            self.logger.info(f"✅ Authorization enforced for user {user_context.user_id}, action {action}")
            return EnforcementResult(
                success=True,
                message="Authorization successful",
                context={"user_id": user_context.user_id, "action": action, "resource": resource}
            )
            
        except Exception as e:
            self.logger.error(f"Authorization enforcement error: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Authorization enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def enforce_feature_access(self, 
                                   user_context: SecurityContext,
                                   feature: str) -> EnforcementResult:
        """Enforce feature access - pure enforcement logic."""
        try:
            # Build feature access context using utility (no enforcement decisions)
            feature_context = await self.tenant_context.build_feature_access_context(
                user_context.tenant_id or "unknown", feature
            )
            
            # Enforce feature access rules
            if not feature_context.feature_available:
                return EnforcementResult(
                    success=False,
                    message=f"Feature access denied: Feature '{feature}' not available for tenant",
                    context={"error": "feature_not_available", "feature": feature, "tenant_id": user_context.tenant_id}
                )
            
            # Check usage limits (enforcement rule)
            if not await self._validate_usage_limits(feature_context):
                return EnforcementResult(
                    success=False,
                    message=f"Feature access denied: Usage limits exceeded for feature '{feature}'",
                    context={"error": "usage_limits_exceeded", "feature": feature, "tenant_id": user_context.tenant_id}
                )
            
            # Audit feature access success
            trace_context = await self.security_context.build_trace_context("feature_access_request")
            audit_context = await self.audit_context.build_audit_context(
                user_context, f"access_feature_{feature}", "feature", trace_context
            )
            await self._audit_security_event(audit_context)
            
            self.logger.info(f"✅ Feature access enforced for user {user_context.user_id}, feature {feature}")
            return EnforcementResult(
                success=True,
                message="Feature access successful",
                context={"user_id": user_context.user_id, "feature": feature}
            )
            
        except Exception as e:
            self.logger.error(f"Feature access enforcement error: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Feature access enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    # ============================================================================
    # SESSION ENFORCEMENT (Pure Enforcement)
    # ============================================================================
    
    async def enforce_session_management(self, 
                                       user_context: SecurityContext,
                                       session_action: str,
                                       session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session management - pure enforcement logic."""
        try:
            # Enforce session rules based on action
            if session_action == "create":
                result = await self._enforce_session_creation(user_context, session_data)
            elif session_action == "validate":
                result = await self._enforce_session_validation(user_context, session_data)
            elif session_action == "revoke":
                result = await self._enforce_session_revocation(user_context, session_data)
            else:
                return EnforcementResult(
                    success=False,
                    message=f"Invalid session action: {session_action}",
                    context={"error": "invalid_session_action", "action": session_action}
                )
            
            # Audit session management
            trace_context = await self.security_context.build_trace_context("session_management")
            audit_context = await self.audit_context.build_audit_context(
                user_context, f"session_{session_action}", "session", trace_context
            )
            await self._audit_security_event(audit_context)
            
            self.logger.info(f"✅ Session management enforced for user {user_context.user_id}, action {session_action}")
            return result
            
        except Exception as e:
            self.logger.error(f"Session management enforcement error: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session management enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    # ============================================================================
    # PRIVATE ENFORCEMENT METHODS (Pure Enforcement Logic)
    # ============================================================================
    
    async def _is_user_active(self, user_id: str) -> bool:
        """Check if user is active - pure enforcement logic."""
        try:
            # This would typically check against user database or cache
            # For now, return True (all users are active)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check user active status: {str(e)}")
            return False
    
    async def _validate_tenant_isolation(self, isolation_context: IsolationContext) -> bool:
        """Validate tenant isolation - pure enforcement logic."""
        try:
            # Enforce tenant isolation rules
            if isolation_context.isolation_required:
                return isolation_context.user_tenant == isolation_context.resource_tenant
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant isolation: {str(e)}")
            return False
    
    async def _validate_user_authorization(self, user_context: SecurityContext, action: str, resource: str) -> bool:
        """Validate user authorization - pure enforcement logic."""
        try:
            # Check user permissions
            if "admin" in user_context.roles:
                return True
            
            # Check specific permissions
            if action == "read" and "read" in user_context.permissions:
                return True
            
            if action == "write" and "write" in user_context.permissions:
                return True
            
            if action == "delete" and "delete" in user_context.permissions:
                return True
            
            # Check resource-specific permissions
            resource_permission = f"{action}:{resource}"
            if resource_permission in user_context.permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to validate user authorization: {str(e)}")
            return False
    
    async def _validate_usage_limits(self, feature_context: FeatureContext) -> bool:
        """Validate usage limits - pure enforcement logic."""
        try:
            # Check if feature is available
            if not feature_context.feature_available:
                return False
            
            # Check usage limits (simplified for now)
            # In real implementation, this would check current usage against limits
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate usage limits: {str(e)}")
            return False
    
    async def _enforce_session_creation(self, user_context: SecurityContext, session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session creation - pure enforcement logic."""
        try:
            # Check if user can create sessions
            if not await self._can_user_create_sessions(user_context):
                return EnforcementResult(
                    success=False,
                    message="Session creation denied: User cannot create sessions",
                    context={"error": "session_creation_denied", "user_id": user_context.user_id}
                )
            
            # Create session (simplified for now)
            session_id = f"session_{user_context.user_id}_{int(datetime.utcnow().timestamp())}"
            self.active_sessions[session_id] = {
                "user_id": user_context.user_id,
                "tenant_id": user_context.tenant_id,
                "created_at": datetime.utcnow().isoformat(),
                "data": session_data or {}
            }
            
            return EnforcementResult(
                success=True,
                message="Session created successfully",
                context={"session_id": session_id, "user_id": user_context.user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enforce session creation: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session creation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def _enforce_session_validation(self, user_context: SecurityContext, session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session validation - pure enforcement logic."""
        try:
            # Check if session exists and is valid
            session_id = session_data.get("session_id") if session_data else None
            if not session_id or session_id not in self.active_sessions:
                return EnforcementResult(
                    success=False,
                    message="Session validation failed: Session not found",
                    context={"error": "session_not_found", "session_id": session_id}
                )
            
            # Check if session belongs to user
            session = self.active_sessions[session_id]
            if session["user_id"] != user_context.user_id:
                return EnforcementResult(
                    success=False,
                    message="Session validation failed: Session does not belong to user",
                    context={"error": "session_mismatch", "session_id": session_id, "user_id": user_context.user_id}
                )
            
            return EnforcementResult(
                success=True,
                message="Session validation successful",
                context={"session_id": session_id, "user_id": user_context.user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enforce session validation: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session validation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def _enforce_session_revocation(self, user_context: SecurityContext, session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session revocation - pure enforcement logic."""
        try:
            # Check if session exists
            session_id = session_data.get("session_id") if session_data else None
            if not session_id or session_id not in self.active_sessions:
                return EnforcementResult(
                    success=False,
                    message="Session revocation failed: Session not found",
                    context={"error": "session_not_found", "session_id": session_id}
                )
            
            # Remove session
            del self.active_sessions[session_id]
            
            return EnforcementResult(
                success=True,
                message="Session revoked successfully",
                context={"session_id": session_id, "user_id": user_context.user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enforce session revocation: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session revocation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def _can_user_create_sessions(self, user_context: SecurityContext) -> bool:
        """Check if user can create sessions - pure enforcement logic."""
        try:
            # Check user permissions
            if "admin" in user_context.roles or "user" in user_context.roles:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check user session creation permission: {str(e)}")
            return False
    
    async def _audit_security_event(self, audit_context: AuditContext):
        """Audit security event - pure enforcement logic."""
        try:
            # Build audit log
            audit_log = await self.audit_context.build_audit_log(audit_context, "SecurityGuardService")
            
            # Store audit log (simplified for now)
            # In real implementation, this would send to audit system
            self.logger.info(f"🔒 Security event audited: {audit_log.get('action')} by user {audit_log.get('user_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to audit security event: {str(e)}")
    
    # ============================================================================
    # SERVICE STATUS
    # ============================================================================
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            "service_name": "SecurityGuardService",
            "status": "active",
            "capabilities": [
                "enforce_authentication",
                "enforce_authorization",
                "enforce_feature_access",
                "enforce_session_management"
            ],
            "active_sessions": len(self.active_sessions),
            "authorization_policies": len(self.authorization_policies),
            "timestamp": datetime.utcnow().isoformat()
        }
