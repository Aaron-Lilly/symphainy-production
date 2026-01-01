#!/usr/bin/env python3
"""
Security Guard Service - Integrated with Infrastructure

Pure enforcement service with infrastructure abstractions.
This integrates the refactored security capabilities with the 5-layer infrastructure.

WHAT (Smart City Role): I handle security enforcement and resolution using infrastructure
HOW (Service Implementation): I use infrastructure abstractions with pure enforcement logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

# Import context utilities (integrated with infrastructure)
from utilities.security_context_utility_integrated import SecurityContextUtilityIntegrated, SecurityContext, TraceContext
from utilities.tenant_context_utility_integrated import TenantContextUtilityIntegrated, TenantContext, IsolationContext, FeatureContext
from utilities.audit_context_utility_integrated import AuditContextUtilityIntegrated, AuditContext, SecurityEvent

# Import infrastructure abstractions
from contracts.authentication_protocol import AuthenticationProtocol
from contracts.authorization_protocol import AuthorizationProtocol
from contracts.session_protocol import SessionProtocol
from contracts.tenant_protocol import TenantProtocol
from contracts.policy_engine_protocol import PolicyEngine

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class EnforcementResult:
    """Enforcement result data structure."""
    success: bool
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class SecurityGuardServiceIntegrated:
    """
    Security Guard Service - Integrated with Infrastructure
    
    Pure enforcement service with infrastructure abstractions.
    This service only handles enforcement and resolution - it does not build context.
    """
    
    def __init__(self, 
                 # Context utilities (integrated with infrastructure)
                 security_context_utility: SecurityContextUtilityIntegrated,
                 tenant_context_utility: TenantContextUtilityIntegrated,
                 audit_context_utility: AuditContextUtilityIntegrated,
                 # Infrastructure abstractions
                 auth_abstraction: AuthenticationProtocol,
                 authorization_abstraction: AuthorizationProtocol,
                 session_abstraction: SessionProtocol,
                 tenant_abstraction: TenantProtocol,
                 policy_engine: PolicyEngine):
        """Initialize Security Guard Service with context utilities and infrastructure abstractions."""
        self.security_context = security_context_utility
        self.tenant_context = tenant_context_utility
        self.audit_context = audit_context_utility
        
        # Infrastructure abstractions
        self.auth_abstraction = auth_abstraction
        self.authorization_abstraction = authorization_abstraction
        self.session_abstraction = session_abstraction
        self.tenant_abstraction = tenant_abstraction
        self.policy_engine = policy_engine
        
        self.logger = self.service.di_container.get_logger("SecurityGuardServiceIntegrated")
        
        # Enforcement state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.authorization_policies: Dict[str, List[str]] = {}
        
        self.logger.info("✅ Security Guard Service Integrated initialized with infrastructure abstractions")
    
    # ============================================================================
    # AUTHENTICATION ENFORCEMENT (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def enforce_authentication(self, credentials: Dict[str, Any]) -> EnforcementResult:
        """Enforce authentication using infrastructure abstractions."""
        try:
            # Build user context using integrated utility
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
            
            self.logger.info(f"✅ Authentication enforced using infrastructure for user: {user_context.user_id}")
            return EnforcementResult(
                success=True,
                message="Authentication successful",
                context={"user_id": user_context.user_id, "tenant_id": user_context.tenant_id}
            )
            
        except Exception as e:
            self.logger.error(f"Authentication enforcement error using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Authentication enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def enforce_token_validation(self, token: str) -> EnforcementResult:
        """Enforce token validation using infrastructure abstractions."""
        try:
            # Build user context using integrated utility
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
            
            self.logger.info(f"✅ Token validation enforced using infrastructure for user: {user_context.user_id}")
            return EnforcementResult(
                success=True,
                message="Token validation successful",
                context={"user_id": user_context.user_id, "tenant_id": user_context.tenant_id}
            )
            
        except Exception as e:
            self.logger.error(f"Token validation enforcement error using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Token validation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    # ============================================================================
    # AUTHORIZATION ENFORCEMENT (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def enforce_authorization(self, 
                                  user_context: SecurityContext,
                                  action: str, 
                                  resource: str) -> EnforcementResult:
        """Enforce authorization using infrastructure abstractions."""
        try:
            # Build tenant isolation context using integrated utility
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
            
            # Enforce authorization rules using infrastructure abstraction
            if not await self.authorization_abstraction.enforce(action, resource, user_context):
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
            
            self.logger.info(f"✅ Authorization enforced using infrastructure for user {user_context.user_id}, action {action}")
            return EnforcementResult(
                success=True,
                message="Authorization successful",
                context={"user_id": user_context.user_id, "action": action, "resource": resource}
            )
            
        except Exception as e:
            self.logger.error(f"Authorization enforcement error using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Authorization enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def enforce_feature_access(self, 
                                   user_context: SecurityContext,
                                   feature: str) -> EnforcementResult:
        """Enforce feature access using infrastructure abstractions."""
        try:
            # Build feature access context using integrated utility
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
            
            self.logger.info(f"✅ Feature access enforced using infrastructure for user {user_context.user_id}, feature {feature}")
            return EnforcementResult(
                success=True,
                message="Feature access successful",
                context={"user_id": user_context.user_id, "feature": feature}
            )
            
        except Exception as e:
            self.logger.error(f"Feature access enforcement error using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Feature access enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    # ============================================================================
    # SESSION ENFORCEMENT (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def enforce_session_management(self, 
                                       user_context: SecurityContext,
                                       session_action: str,
                                       session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session management using infrastructure abstractions."""
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
            
            self.logger.info(f"✅ Session management enforced using infrastructure for user {user_context.user_id}, action {session_action}")
            return result
            
        except Exception as e:
            self.logger.error(f"Session management enforcement error using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session management enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    # ============================================================================
    # PRIVATE ENFORCEMENT METHODS (Using Infrastructure Abstractions)
    # ============================================================================
    
    async def _is_user_active(self, user_id: str) -> bool:
        """Check if user is active using infrastructure abstractions."""
        try:
            # This would typically check against user database or cache using infrastructure
            # For now, return True (all users are active)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check user active status using infrastructure: {str(e)}")
            return False
    
    async def _validate_tenant_isolation(self, isolation_context: IsolationContext) -> bool:
        """Validate tenant isolation using infrastructure abstractions."""
        try:
            # Enforce tenant isolation rules
            if isolation_context.isolation_required:
                return isolation_context.user_tenant == isolation_context.resource_tenant
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant isolation using infrastructure: {str(e)}")
            return False
    
    async def _validate_usage_limits(self, feature_context: FeatureContext) -> bool:
        """Validate usage limits using infrastructure abstractions."""
        try:
            # Check if feature is available
            if not feature_context.feature_available:
                return False
            
            # Check usage limits (simplified for now)
            # In real implementation, this would check current usage against limits using infrastructure
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate usage limits using infrastructure: {str(e)}")
            return False
    
    async def _enforce_session_creation(self, user_context: SecurityContext, session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session creation using infrastructure abstractions."""
        try:
            # Check if user can create sessions
            if not await self._can_user_create_sessions(user_context):
                return EnforcementResult(
                    success=False,
                    message="Session creation denied: User cannot create sessions",
                    context={"error": "session_creation_denied", "user_id": user_context.user_id}
                )
            
            # Create session using infrastructure abstraction
            session_id = await self.session_abstraction.create_session(
                user_context.user_id or "unknown",
                user_context.tenant_id or "unknown",
                session_data or {}
            )
            
            return EnforcementResult(
                success=True,
                message="Session created successfully",
                context={"session_id": session_id, "user_id": user_context.user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enforce session creation using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session creation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def _enforce_session_validation(self, user_context: SecurityContext, session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session validation using infrastructure abstractions."""
        try:
            # Check if session exists and is valid
            session_id = session_data.get("session_id") if session_data else None
            if not session_id:
                return EnforcementResult(
                    success=False,
                    message="Session validation failed: Session ID not provided",
                    context={"error": "session_id_missing", "session_id": session_id}
                )
            
            # Validate session using infrastructure abstraction
            session_context = await self.session_abstraction.validate_session(session_id)
            
            if not session_context.is_authenticated:
                return EnforcementResult(
                    success=False,
                    message="Session validation failed: Session not authenticated",
                    context={"error": "session_not_authenticated", "session_id": session_id}
                )
            
            return EnforcementResult(
                success=True,
                message="Session validation successful",
                context={"session_id": session_id, "user_id": user_context.user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enforce session validation using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session validation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def _enforce_session_revocation(self, user_context: SecurityContext, session_data: Dict[str, Any] = None) -> EnforcementResult:
        """Enforce session revocation using infrastructure abstractions."""
        try:
            # Check if session exists
            session_id = session_data.get("session_id") if session_data else None
            if not session_id:
                return EnforcementResult(
                    success=False,
                    message="Session revocation failed: Session ID not provided",
                    context={"error": "session_id_missing", "session_id": session_id}
                )
            
            # Revoke session using infrastructure abstraction
            revoked = await self.session_abstraction.revoke_session(session_id)
            
            if not revoked:
                return EnforcementResult(
                    success=False,
                    message="Session revocation failed: Session not found or already revoked",
                    context={"error": "session_not_found", "session_id": session_id}
                )
            
            return EnforcementResult(
                success=True,
                message="Session revoked successfully",
                context={"session_id": session_id, "user_id": user_context.user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enforce session revocation using infrastructure: {str(e)}")
            return EnforcementResult(
                success=False,
                message=f"Session revocation enforcement failed: {str(e)}",
                context={"error": "enforcement_error"}
            )
    
    async def _can_user_create_sessions(self, user_context: SecurityContext) -> bool:
        """Check if user can create sessions using infrastructure abstractions."""
        try:
            # Check user permissions
            if "admin" in user_context.roles or "user" in user_context.roles:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check user session creation permission using infrastructure: {str(e)}")
            return False
    
    async def _audit_security_event(self, audit_context: AuditContext):
        """Audit security event using infrastructure abstractions."""
        try:
            # Build audit log
            audit_log = await self.audit_context.build_audit_log(audit_context, "SecurityGuardServiceIntegrated")
            
            # Store audit log using infrastructure
            await self.audit_context.store_audit_log(audit_log)
            
            self.logger.info(f"🔒 Security event audited using infrastructure: {audit_log.get('action')} by user {audit_log.get('user_id')}")
            
        except Exception as e:
            self.logger.error(f"Failed to audit security event using infrastructure: {str(e)}")
    
    # ============================================================================
    # SERVICE STATUS
    # ============================================================================
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            "service_name": "SecurityGuardServiceIntegrated",
            "status": "active",
            "infrastructure_connected": True,
            "capabilities": [
                "enforce_authentication",
                "enforce_authorization",
                "enforce_feature_access",
                "enforce_session_management"
            ],
            "infrastructure_abstractions": [
                "AuthenticationProtocol",
                "AuthorizationProtocol", 
                "SessionProtocol",
                "TenantProtocol",
                "PolicyEngine"
            ],
            "active_sessions": len(self.active_sessions),
            "authorization_policies": len(self.authorization_policies),
            "timestamp": datetime.utcnow().isoformat()
        }
