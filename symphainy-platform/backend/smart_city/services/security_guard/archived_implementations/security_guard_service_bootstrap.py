#!/usr/bin/env python3
"""
Security Guard Service - Bootstrap Pattern

Enforces security policies using bootstrap pattern to avoid circular references.
This service gets bootstrapped by foundation service, then works independently.

WHAT (Smart City Role): I enforce security policies using bootstrap pattern
HOW (Smart City Service): I bootstrap from foundation service, then work independently
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

# Add the project root to the Python path for local imports
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.smart_city.protocols.smart_city_service_base import SmartCityServiceBase
from utilities.security_context_utility_bootstrap import SecurityContext, SecurityContextUtilityBootstrap
from utilities.tenant_context_utility_bootstrap import TenantContextUtilityBootstrap, TenantFeatureContext, TenantIsolationContext
from utilities.audit_context_utility_bootstrap import AuditContext, AuditContextUtilityBootstrap, SecurityEventContext

logger = logging.getLogger(__name__)

@dataclass
class EnforcementResult:
    """Standardized result for enforcement actions."""
    success: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    security_context: Optional[SecurityContext] = None
    audit_context: Optional[AuditContext] = None
    security_event_context: Optional[SecurityEventContext] = None

class SecurityGuardServiceBootstrap(SmartCityServiceBase):
    """
    Security Guard Service - Bootstrap Pattern
    
    Enforces security policies using bootstrap pattern to avoid circular references.
    This service gets bootstrapped by foundation service, then works independently.
    """

    def __init__(self, service_name: str, public_works_foundation=None):
        """
        Initialize Security Guard Service with direct infrastructure access.
        
        Args:
            service_name (str): The name of the service.
            public_works_foundation: Public Works Foundation Service for infrastructure access
        """
        # SmartCityServiceBase expects foundation_services, public_works_foundation, curator_foundation
        # We'll create a minimal foundation_services mock to avoid the get_logger error
        class MockLogger:
            def __init__(self, service_name):
                self.logger = self.service.di_container.get_logger(f"SecurityGuardService-{service_name}")
            def info(self, msg):
                self.logger.info(msg)
            def error(self, msg):
                self.logger.error(msg)
            def warning(self, msg):
                self.logger.warning(msg)
            def debug(self, msg):
                self.logger.debug(msg)
        
        class MockFoundationServices:
            def get_logger(self, service_name):
                return MockLogger(service_name)
            def get_config(self):
                return {}
            def get_health(self):
                return None
            def get_telemetry(self):
                return None
            def get_security(self):
                return None
            def get_error_handler(self):
                return None
            def get_tenant(self):
                return None
            def get_validation(self):
                return None
            def get_serialization(self):
                return None
        
        super().__init__(
            service_name=service_name,
            foundation_services=MockFoundationServices(), # Mock to avoid get_logger error
            public_works_foundation=public_works_foundation, # Direct access to Public Works Foundation
            curator_foundation=None
        )
        
        # Infrastructure abstractions (direct access from Public Works Foundation)
        self.auth_abstraction = public_works_foundation.get_auth_abstraction() if public_works_foundation else None
        self.authorization_abstraction = public_works_foundation.get_authorization_abstraction() if public_works_foundation else None
        self.session_abstraction = public_works_foundation.get_session_abstraction() if public_works_foundation else None
        self.tenant_abstraction = public_works_foundation.get_tenant_abstraction() if public_works_foundation else None
        
        # Policy engines (direct access from Public Works Foundation)
        self.policy_engine = public_works_foundation.get_policy_engine("default") if public_works_foundation else None
        
        self.logger = self.service.di_container.get_logger(f"SecurityGuardService-{service_name}")
        self.logger.info(f"✅ Security Guard Service '{self.service_name}' initialized with direct infrastructure access")

    # No bootstrap method needed - Security Guard Service gets infrastructure directly from Public Works Foundation

    async def enforce_authentication(self, security_context: SecurityContext) -> EnforcementResult:
        """
        Enforce authentication based on the provided SecurityContext.
        This method assumes the context has been built (e.g., from a validated token or credentials).
        """
        # No bootstrap check needed - Security Guard Service gets infrastructure directly from Public Works Foundation
        
        if security_context.user_id:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                action="authenticate",
                resource="user_session",
                service_name=self.service_name,
                outcome="success",
                details={"method": security_context.origin}
            )
            sec_event_ctx = SecurityEventContext(
                event_id=str(uuid.uuid4()),
                event_type="authentication_success",
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                severity="info"
            )
            logger.info(f"Authentication successful for user {security_context.user_id}")
            return EnforcementResult(
                success=True,
                message="Authentication successful",
                security_context=security_context,
                audit_context=audit_ctx,
                security_event_context=sec_event_ctx
            )
        else:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id="anonymous",
                tenant_id=security_context.tenant_id,
                action="authenticate",
                resource="user_session",
                service_name=self.service_name,
                outcome="failure",
                details={"reason": "No user ID", "method": security_context.origin}
            )
            sec_event_ctx = SecurityEventContext(
                event_id=str(uuid.uuid4()),
                event_type="authentication_failure",
                user_id="anonymous",
                tenant_id=security_context.tenant_id,
                severity="warning",
                details={"reason": "No user ID"}
            )
            logger.warning(f"Authentication failed for anonymous user")
            return EnforcementResult(
                success=False,
                message="Authentication failed: No user ID",
                security_context=security_context,
                audit_context=audit_ctx,
                security_event_context=sec_event_ctx
            )

    async def enforce_authorization(self, security_context: SecurityContext, action: str, resource: str) -> EnforcementResult:
        """
        Enforce authorization based on the provided SecurityContext, action, and resource.
        Delegates the decision to the pluggable PolicyEngine.
        """
        # No bootstrap check needed - Security Guard Service gets infrastructure directly from Public Works Foundation
        
        if not security_context.user_id:
            return EnforcementResult(
                success=False,
                message="Authorization failed: No user ID",
                security_context=security_context
            )

        # Use policy engine for authorization decision
        is_allowed = True  # Default open policy
        if self.policy_engine:
            try:
                is_allowed = await self.policy_engine.is_allowed(action, resource, security_context)
            except Exception as e:
                logger.warning(f"Policy engine authorization failed: {e}")
                is_allowed = True  # Default to allowed

        if is_allowed:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                action=action,
                resource=resource,
                service_name=self.service_name,
                outcome="success",
                details={"policy_engine": self.policy_engine.__class__.__name__ if self.policy_engine else "default"},
                request_id=str(uuid.uuid4())
            )
            sec_event_ctx = SecurityEventContext(
                event_id=str(uuid.uuid4()),
                event_type="authorization_success",
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                severity="info",
                details={"action": action, "resource": resource}
            )
            logger.info(f"Authorization granted for user {security_context.user_id} to {action} on {resource}")
            return EnforcementResult(
                success=True,
                message="Authorization granted",
                security_context=security_context,
                audit_context=audit_ctx,
                security_event_context=sec_event_ctx
            )
        else:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                action=action,
                resource=resource,
                service_name=self.service_name,
                outcome="denied",
                details={"policy_engine": self.policy_engine.__class__.__name__ if self.policy_engine else "default"},
                request_id=str(uuid.uuid4())
            )
            sec_event_ctx = SecurityEventContext(
                event_id=str(uuid.uuid4()),
                event_type="authorization_denied",
                user_id=security_context.user_id,
                tenant_id=security_context.tenant_id,
                severity="warning",
                details={"action": action, "resource": resource, "reason": "Policy denied"}
            )
            logger.warning(f"Authorization denied for user {security_context.user_id} to {action} on {resource}")
            return EnforcementResult(
                success=False,
                message="Authorization denied by policy",
                security_context=security_context,
                audit_context=audit_ctx,
                security_event_context=sec_event_ctx
            )

    async def enforce_tenant_isolation(self, security_context: SecurityContext, target_resource_tenant_id: str) -> EnforcementResult:
        """
        Enforce tenant isolation rules.
        This method uses the TenantContextUtility to build the isolation context
        and the PolicyEngine to make the enforcement decision.
        """
        # No bootstrap check needed - Security Guard Service gets infrastructure directly from Public Works Foundation
        
        user_tenant_id = security_context.tenant_id
        if not user_tenant_id:
            return EnforcementResult(
                success=False,
                message="Tenant isolation check failed: User context missing tenant ID",
                security_context=security_context
            )

        # Build the isolation context directly (no bootstrap utility needed)
        isolation_ctx = TenantIsolationContext(
            source_tenant_id=user_tenant_id,
            target_tenant_id=target_resource_tenant_id,
            is_allowed=user_tenant_id == target_resource_tenant_id,  # Strict isolation by default
            reason="Strict isolation (default)"
        )

        # Use policy engine for tenant access decision
        is_allowed = isolation_ctx.is_allowed  # Default to context decision
        if self.policy_engine:
            try:
                is_allowed = await self.policy_engine.is_tenant_access_allowed(
                    user_tenant_id, target_resource_tenant_id, security_context
                )
            except Exception as e:
                logger.warning(f"Policy engine tenant access failed: {e}")
                is_allowed = isolation_ctx.is_allowed  # Fallback to context decision

        if is_allowed:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=user_tenant_id,
                action="access_tenant_resource",
                resource=f"tenant:{target_resource_tenant_id}",
                service_name=self.service_name,
                outcome="success",
                details={"source_tenant": user_tenant_id, "target_tenant": target_resource_tenant_id},
                request_id=str(uuid.uuid4())
            )
            logger.info(f"Tenant isolation granted: {user_tenant_id} can access {target_resource_tenant_id}")
            return EnforcementResult(
                success=True,
                message="Tenant isolation granted",
                security_context=security_context,
                audit_context=audit_ctx
            )
        else:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=user_tenant_id,
                action="access_tenant_resource",
                resource=f"tenant:{target_resource_tenant_id}",
                service_name=self.service_name,
                outcome="denied",
                details={"source_tenant": user_tenant_id, "target_tenant": target_resource_tenant_id, "reason": isolation_ctx.reason},
                request_id=str(uuid.uuid4())
            )
            logger.warning(f"Tenant isolation denied: {user_tenant_id} cannot access {target_resource_tenant_id}")
            return EnforcementResult(
                success=False,
                message=f"Tenant isolation denied: {isolation_ctx.reason}",
                security_context=security_context,
                audit_context=audit_ctx
            )

    async def enforce_feature_access(self, security_context: SecurityContext, feature_name: str) -> EnforcementResult:
        """
        Enforce access to a specific feature for a tenant.
        Delegates the decision to the pluggable PolicyEngine.
        """
        # No bootstrap check needed - Security Guard Service gets infrastructure directly from Public Works Foundation
        
        tenant_id = security_context.tenant_id
        if not tenant_id:
            return EnforcementResult(
                success=False,
                message="Feature access failed: User context missing tenant ID",
                security_context=security_context
            )

        # Build feature context directly (no bootstrap utility needed)
        feature_ctx = TenantFeatureContext(
            tenant_id=tenant_id,
            feature_name=feature_name,
            is_enabled=False,  # Default to disabled
            reason="Feature disabled (default)"
        )

        # Use policy engine for feature access decision
        is_allowed = feature_ctx.is_enabled  # Default to context decision
        if self.policy_engine:
            try:
                is_allowed = await self.policy_engine.is_feature_enabled(tenant_id, feature_name, security_context)
            except Exception as e:
                logger.warning(f"Policy engine feature access failed: {e}")
                is_allowed = feature_ctx.is_enabled  # Fallback to context decision

        if is_allowed:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=tenant_id,
                action="access_feature",
                resource=f"feature:{feature_name}",
                service_name=self.service_name,
                outcome="success",
                details={"feature": feature_name},
                request_id=str(uuid.uuid4())
            )
            logger.info(f"Feature '{feature_name}' access granted for tenant {tenant_id}")
            return EnforcementResult(
                success=True,
                message=f"Feature '{feature_name}' access granted",
                security_context=security_context,
                audit_context=audit_ctx
            )
        else:
            # Create audit context directly (no bootstrap utility needed)
            audit_ctx = AuditContext(
                audit_id=str(uuid.uuid4()),
                user_id=security_context.user_id,
                tenant_id=tenant_id,
                action="access_feature",
                resource=f"feature:{feature_name}",
                service_name=self.service_name,
                outcome="denied",
                details={"feature": feature_name, "reason": feature_ctx.reason},
                request_id=str(uuid.uuid4())
            )
            logger.warning(f"Feature '{feature_name}' access denied for tenant {tenant_id}")
            return EnforcementResult(
                success=False,
                message=f"Feature '{feature_name}' access denied",
                security_context=security_context,
                audit_context=audit_ctx
            )

    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Security Guard Service."""
        return {
            "service_name": self.service_name,
            "status": "active",
            "infrastructure_available": all([
                self.auth_abstraction is not None,
                self.authorization_abstraction is not None,
                self.session_abstraction is not None,
                self.tenant_abstraction is not None
            ]),
            "policy_engine": self.policy_engine.__class__.__name__ if self.policy_engine else "default",
            "timestamp": datetime.utcnow().isoformat()
        }
