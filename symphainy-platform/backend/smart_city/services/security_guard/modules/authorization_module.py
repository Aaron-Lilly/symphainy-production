#!/usr/bin/env python3
"""
Authorization Module - Security Guard Micro-Module

Handles authorization enforcement and permission management.
Part of the Security Guard Service micro-modular architecture.

WHAT (Authorization Role): I handle authorization enforcement and permission management
HOW (Authorization Implementation): I use infrastructure abstractions for authorization
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext

# Import audit context
from utilities.audit_context_utility_integrated import AuditContext


class AuthorizationModule:
    """
    Authorization Module - Security Guard Micro-Module
    
    Handles authorization enforcement and permission management.
    Part of the Security Guard Service micro-modular architecture.
    
    WHAT (Authorization Role): I handle authorization enforcement and permission management
    HOW (Authorization Implementation): I use infrastructure abstractions for authorization
    """
    
    def __init__(self, authorization_abstraction=None, service_name: str = "authorization_module"):
        """Initialize Authorization Module."""
        self.service_name = service_name
        self.authorization_abstraction = authorization_abstraction
        self.logger = self.service.di_container.get_logger(f"AuthorizationModule-{service_name}")
        
        # Authorization statistics
        self.authz_stats = {
            "authorization_checks": 0,
            "authorization_allowed": 0,
            "authorization_denied": 0
        }
        
        self.logger.info(f"✅ Authorization Module '{service_name}' initialized")
    
    async def initialize(self):
        """Initialize Authorization Module."""
        try:
            self.logger.info(f"🚀 Initializing Authorization Module '{self.service_name}'...")
            self.logger.info(f"✅ Authorization Module '{self.service_name}' initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Authorization Module '{self.service_name}': {e}")
            raise
    
    async def enforce_authorization(self, action: str, resource: str, security_context: SecurityContext) -> Dict[str, Any]:
        """
        Enforce authorization with policy engine integration.
        
        BOOTSTRAP PATTERN: This method PROVIDES security, so we use direct security abstraction access
        instead of get_security() utility to avoid circular dependency.
        """
        # Bootstrap Pattern: Direct security abstraction access (Security Guard PROVIDES security)
        # Note: This module uses self.authorization_abstraction which is set during initialization
        # We still use direct abstraction access pattern here
        
        try:
            self.authz_stats["authorization_checks"] += 1
            
            # Use authorization abstraction from Public Works Foundation (direct access - bootstrap pattern)
            if self.authorization_abstraction:
                # Call the enforce method (not authorize_action)
                auth_result = await self.authorization_abstraction.enforce(action, resource, security_context)
                if auth_result:
                    self.authz_stats["authorization_allowed"] += 1
                    
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
                    
                    # ✅ CAN USE: Telemetry utilities (Security Guard doesn't provide telemetry)
                    # Note: We need to access through service if available
                    if hasattr(self, 'service') and hasattr(self.service, 'log_operation_with_telemetry'):
                        await self.service.log_operation_with_telemetry(
                            "enforce_authorization_complete",
                            success=True,
                            details={"action": action, "resource": resource, "user_id": security_context.user_id}
                        )
                    
                    self.logger.info(f"Authorization allowed: {action} on {resource} for user {security_context.user_id}")
                    return {
                        "success": True,
                        "message": "Authorization allowed",
                        "audit_context": audit_ctx
                    }
            
            # Authorization denied
            self.authz_stats["authorization_denied"] += 1
            
            # ✅ CAN USE: Telemetry utilities for denial reporting
            if hasattr(self, 'service') and hasattr(self.service, 'log_operation_with_telemetry'):
                await self.service.log_operation_with_telemetry(
                    "enforce_authorization_complete",
                    success=False,
                    details={"action": action, "resource": resource, "user_id": security_context.user_id, "authorized": False}
                )
            
            self.logger.warning(f"Authorization denied: {action} on {resource} for user {security_context.user_id}")
            return {
                "success": False,
                "message": "Authorization denied",
                "security_context": security_context
            }
            
        except Exception as e:
            # ✅ CAN USE: Error handling utility (Security Guard doesn't provide error handling)
            if hasattr(self, 'service') and hasattr(self.service, 'handle_error_with_audit'):
                await self.service.handle_error_with_audit(e, "enforce_authorization")
            
            # ✅ CAN USE: Telemetry utilities for error reporting
            if hasattr(self, 'service') and hasattr(self.service, 'log_operation_with_telemetry'):
                await self.service.log_operation_with_telemetry(
                    "enforce_authorization_complete",
                    success=False,
                    details={"action": action, "resource": resource, "error": str(e)}
                )
            
            self.logger.error(f"❌ Authorization enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Authorization enforcement failed: {e}",
                "security_context": security_context
            }
    
    async def check_permission(self, permission: str, security_context: SecurityContext) -> bool:
        """Check if user has specific permission."""
        try:
            if permission in security_context.permissions or "admin" in security_context.permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Permission check failed: {e}")
            return False
    
    async def check_role(self, required_role: str, security_context: SecurityContext) -> bool:
        """Check if user has required role."""
        try:
            if required_role in security_context.roles or "admin" in security_context.roles:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Role check failed: {e}")
            return False
    
    async def get_authorization_metrics(self) -> Dict[str, Any]:
        """Get authorization metrics."""
        try:
            total_checks = self.authz_stats["authorization_checks"]
            allow_rate = (self.authz_stats["authorization_allowed"] / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "authorization_checks": self.authz_stats["authorization_checks"],
                "authorization_allowed": self.authz_stats["authorization_allowed"],
                "authorization_denied": self.authz_stats["authorization_denied"],
                "allow_rate": f"{allow_rate:.2f}%"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get authorization metrics: {e}")
            return {}
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return [
            "authorization_enforcement",
            "permission_checking",
            "role_checking",
            "authorization_metrics"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "AuthorizationModule",
            "service_name": self.service_name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "authorization_abstraction_available": self.authorization_abstraction is not None,
            "metrics": await self.get_authorization_metrics()
        }



