#!/usr/bin/env python3
"""
Security Guard Service - Enhanced with SmartCityServiceBase

Security Guard Service using the new SmartCityServiceBase with full security infrastructure access.
Implements the CTO's complete security vision with micro-modular compliance.

WHAT (Security Role): I provide comprehensive security enforcement and policy management
HOW (Security Implementation): I use SmartCityServiceBase with full infrastructure access
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import SmartCityServiceBase
from backend.smart_city.protocols.smart_city_service_base import SmartCityServiceBase

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext
from foundations.public_works_foundation.abstraction_contracts.authorization_protocol import AuthorizationProtocol
from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionProtocol
from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol

# Import audit and security event contexts
from utilities.audit_context_utility_integrated import AuditContext, SecurityEventContext

# Import DI Container
from foundations.di_container.di_container_service import DIContainerService

# Import foundation services
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService


class SecurityGuardService(SmartCityServiceBase):
    """
    Security Guard Service - Complete Security Implementation
    
    Security Guard Service using SmartCityServiceBase with full security infrastructure access.
    Implements the CTO's complete security vision with micro-modular compliance.
    
    WHAT (Security Role): I provide comprehensive security enforcement and policy management
    HOW (Security Implementation): I use SmartCityServiceBase with full infrastructure access
    """
    
    def __init__(self, service_name: str, di_container: DIContainerService,
                 security_provider=None, authorization_guard=None,
                 public_works_foundation: PublicWorksFoundationService = None,
                 curator_foundation: CuratorFoundationService = None):
        """Initialize Security Guard Service with SmartCityServiceBase."""
        super().__init__(
            service_name=service_name,
            di_container=di_container,
            security_provider=security_provider,
            authorization_guard=authorization_guard,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
        
        # Security Guard specific properties
        self.role_type = "security_guard"
        self.capabilities = [
            "authentication",
            "authorization", 
            "session_management",
            "tenant_isolation",
            "security_monitoring",
            "policy_enforcement",
            "audit_logging"
        ]
        
        # Security enforcement statistics
        self.enforcement_stats = {
            "authentication_attempts": 0,
            "authentication_successes": 0,
            "authorization_checks": 0,
            "authorization_allowed": 0,
            "tenant_isolation_checks": 0,
            "feature_access_checks": 0
        }
        
        self.logger.info(f"✅ Security Guard Service '{service_name}' initialized with SmartCityServiceBase")
    
    # ============================================================================
    # SECURITY ENFORCEMENT METHODS
    # ============================================================================
    
    async def enforce_authentication(self, security_context: SecurityContext) -> Dict[str, Any]:
        """Enforce authentication with comprehensive logging."""
        try:
            self.enforcement_stats["authentication_attempts"] += 1
            
            # Use auth abstraction from Public Works Foundation
            if self.auth_abstraction:
                auth_result = await self.auth_abstraction.authenticate_user(security_context)
                if auth_result.get("success"):
                    self.enforcement_stats["authentication_successes"] += 1
                    
                    # Create audit context
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
                    
                    # Create security event context
                    sec_event_ctx = SecurityEventContext(
                        event_id=str(uuid.uuid4()),
                        event_type="authentication_success",
                        user_id=security_context.user_id,
                        tenant_id=security_context.tenant_id,
                        severity="info"
                    )
                    
                    self.logger.info(f"Authentication successful for user {security_context.user_id}")
                    return {
                        "success": True,
                        "message": "Authentication successful",
                        "security_context": security_context,
                        "audit_context": audit_ctx,
                        "security_event_context": sec_event_ctx
                    }
            
            # Authentication failed
            self.logger.warning(f"Authentication failed for user {security_context.user_id}")
            return {
                "success": False,
                "message": "Authentication failed",
                "security_context": security_context
            }
            
        except Exception as e:
            self.logger.error(f"❌ Authentication enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Authentication enforcement failed: {e}",
                "security_context": security_context
            }
    
    async def enforce_authorization(self, action: str, resource: str, security_context: SecurityContext) -> Dict[str, Any]:
        """Enforce authorization with policy engine integration."""
        try:
            self.enforcement_stats["authorization_checks"] += 1
            
            # Use authorization abstraction from Public Works Foundation
            if self.authorization_abstraction:
                auth_result = await self.authorization_abstraction.authorize_action(action, resource, security_context)
                if auth_result:
                    self.enforcement_stats["authorization_allowed"] += 1
                    
                    # Create audit context
                    audit_ctx = AuditContext(
                        audit_id=str(uuid.uuid4()),
                        user_id=security_context.user_id,
                        tenant_id=security_context.tenant_id,
                        action=action,
                        resource=resource,
                        service_name=self.service_name,
                        outcome="success",
                        details={"authorization": "allowed"}
                    )
                    
                    self.logger.info(f"Authorization allowed: {action} on {resource} for user {security_context.user_id}")
                    return {
                        "success": True,
                        "message": "Authorization allowed",
                        "audit_context": audit_ctx
                    }
            
            # Authorization denied
            self.logger.warning(f"Authorization denied: {action} on {resource} for user {security_context.user_id}")
            return {
                "success": False,
                "message": "Authorization denied",
                "security_context": security_context
            }
            
        except Exception as e:
            self.logger.error(f"❌ Authorization enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Authorization enforcement failed: {e}",
                "security_context": security_context
            }
    
    async def enforce_tenant_isolation(self, user_tenant: str, resource_tenant: str, security_context: SecurityContext) -> Dict[str, Any]:
        """Enforce tenant isolation with comprehensive validation."""
        try:
            self.enforcement_stats["tenant_isolation_checks"] += 1
            
            # Use tenant abstraction from Public Works Foundation
            if self.tenant_abstraction:
                isolation_result = await self.tenant_abstraction.validate_tenant_access(user_tenant, resource_tenant)
                if isolation_result:
                    # Create audit context
                    audit_ctx = AuditContext(
                        audit_id=str(uuid.uuid4()),
                        user_id=security_context.user_id,
                        tenant_id=security_context.tenant_id,
                        action="tenant_access",
                        resource=f"tenant:{resource_tenant}",
                        service_name=self.service_name,
                        outcome="success",
                        details={"user_tenant": user_tenant, "resource_tenant": resource_tenant}
                    )
                    
                    self.logger.info(f"Tenant isolation validated: {user_tenant} -> {resource_tenant}")
                    return {
                        "success": True,
                        "message": "Tenant isolation validated",
                        "audit_context": audit_ctx
                    }
            
            # Tenant isolation failed
            self.logger.warning(f"Tenant isolation failed: {user_tenant} -> {resource_tenant}")
            return {
                "success": False,
                "message": "Tenant isolation failed",
                "security_context": security_context
            }
            
        except Exception as e:
            self.logger.error(f"❌ Tenant isolation enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Tenant isolation enforcement failed: {e}",
                "security_context": security_context
            }
    
    async def enforce_feature_access(self, feature: str, security_context: SecurityContext) -> Dict[str, Any]:
        """Enforce feature access control."""
        try:
            self.enforcement_stats["feature_access_checks"] += 1
            
            # Check if user has access to feature
            if feature in security_context.permissions or "admin" in security_context.permissions:
                # Create audit context
                audit_ctx = AuditContext(
                    audit_id=str(uuid.uuid4()),
                    user_id=security_context.user_id,
                    tenant_id=security_context.tenant_id,
                    action="feature_access",
                    resource=f"feature:{feature}",
                    service_name=self.service_name,
                    outcome="success",
                    details={"feature": feature}
                )
                
                self.logger.info(f"Feature access allowed: {feature} for user {security_context.user_id}")
                return {
                    "success": True,
                    "message": "Feature access allowed",
                    "audit_context": audit_ctx
                }
            
            # Feature access denied
            self.logger.warning(f"Feature access denied: {feature} for user {security_context.user_id}")
            return {
                "success": False,
                "message": "Feature access denied",
                "security_context": security_context
            }
            
        except Exception as e:
            self.logger.error(f"❌ Feature access enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Feature access enforcement failed: {e}",
                "security_context": security_context
            }
    
    # ============================================================================
    # SESSION MANAGEMENT
    # ============================================================================
    
    async def create_session(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Create session using session abstraction."""
        try:
            if self.session_abstraction:
                session_id = await self.session_abstraction.create_session(user_id, tenant_id)
                
                # Create audit context
                audit_ctx = AuditContext(
                    audit_id=str(uuid.uuid4()),
                    user_id=user_id,
                    tenant_id=tenant_id,
                    action="create_session",
                    resource="user_session",
                    service_name=self.service_name,
                    outcome="success",
                    details={"session_id": session_id}
                )
                
                self.logger.info(f"Session created: {session_id} for user {user_id}")
                return {
                    "success": True,
                    "session_id": session_id,
                    "audit_context": audit_ctx
                }
            
            return {
                "success": False,
                "message": "Session abstraction not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session creation failed: {e}")
            return {
                "success": False,
                "message": f"Session creation failed: {e}"
            }
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate session using session abstraction."""
        try:
            if self.session_abstraction:
                session_valid = await self.session_abstraction.validate_session(session_id)
                
                if session_valid:
                    self.logger.info(f"Session validated: {session_id}")
                    return {
                        "success": True,
                        "message": "Session valid"
                    }
            
            return {
                "success": False,
                "message": "Session invalid"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session validation failed: {e}")
            return {
                "success": False,
                "message": f"Session validation failed: {e}"
            }
    
    # ============================================================================
    # SECURITY MONITORING
    # ============================================================================
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security enforcement metrics."""
        try:
            total_attempts = self.enforcement_stats["authentication_attempts"]
            auth_success_rate = (self.enforcement_stats["authentication_successes"] / total_attempts * 100) if total_attempts > 0 else 0
            
            total_auth_checks = self.enforcement_stats["authorization_checks"]
            auth_allow_rate = (self.enforcement_stats["authorization_allowed"] / total_auth_checks * 100) if total_auth_checks > 0 else 0
            
            return {
                "authentication": {
                    "attempts": self.enforcement_stats["authentication_attempts"],
                    "successes": self.enforcement_stats["authentication_successes"],
                    "success_rate": f"{auth_success_rate:.2f}%"
                },
                "authorization": {
                    "checks": self.enforcement_stats["authorization_checks"],
                    "allowed": self.enforcement_stats["authorization_allowed"],
                    "allow_rate": f"{auth_allow_rate:.2f}%"
                },
                "tenant_isolation": {
                    "checks": self.enforcement_stats["tenant_isolation_checks"]
                },
                "feature_access": {
                    "checks": self.enforcement_stats["feature_access_checks"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get security metrics: {e}")
            return {}
    
    # ============================================================================
    # ENHANCED SERVICE LIFECYCLE
    # ============================================================================
    
    async def initialize(self):
        """Initialize Security Guard Service with SmartCityServiceBase."""
        try:
            self.logger.info(f"🚀 Initializing Security Guard Service '{self.service_name}'...")
            
            # Initialize base service
            await super().initialize()
            
            # Register capabilities with Curator Foundation
            await self.register_capabilities(self.capabilities)
            
            # Register service with Curator Foundation
            await self.register_service(service_type="smart_city", role_type="security_guard")
            
            self.logger.info(f"✅ Security Guard Service '{self.service_name}' initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Security Guard Service '{self.service_name}': {e}")
            raise
    
    async def get_security_guard_health(self) -> Dict[str, Any]:
        """Get Security Guard specific health information."""
        try:
            # Get base health
            health_data = await self.get_smart_city_health()
            
            # Add Security Guard specific information
            health_data.update({
                "role_type": self.role_type,
                "capabilities": self.capabilities,
                "enforcement_stats": self.enforcement_stats,
                "security_metrics": await self.get_security_metrics()
            })
            
            return health_data
            
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Security Guard Service status."""
        try:
            # Get base status
            base_status = await super().get_status()
            
            # Add Security Guard specific information
            base_status.update({
                "role_type": self.role_type,
                "capabilities": self.capabilities,
                "enforcement_stats": self.enforcement_stats,
                "security_metrics": await self.get_security_metrics()
            })
            
            return base_status
            
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
