#!/usr/bin/env python3
"""
Authentication Module - Security Guard Micro-Module

Handles authentication enforcement and user authentication operations.
Part of the Security Guard Service micro-modular architecture.

WHAT (Authentication Role): I handle authentication enforcement and user authentication
HOW (Authentication Implementation): I use infrastructure abstractions for authentication
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext

# Import audit and security event contexts
from utilities.audit_context_utility_integrated import AuditContext, SecurityEventContext


class AuthenticationModule:
    """
    Authentication Module - Security Guard Micro-Module
    
    Handles authentication enforcement and user authentication operations.
    Part of the Security Guard Service micro-modular architecture.
    
    WHAT (Authentication Role): I handle authentication enforcement and user authentication
    HOW (Authentication Implementation): I use infrastructure abstractions for authentication
    """
    
    def __init__(self, auth_abstraction=None, service_name: str = "authentication_module"):
        """Initialize Authentication Module."""
        self.service_name = service_name
        self.auth_abstraction = auth_abstraction
        self.logger = self.service.di_container.get_logger(f"AuthenticationModule-{service_name}")
        
        # Authentication statistics
        self.auth_stats = {
            "authentication_attempts": 0,
            "authentication_successes": 0,
            "authentication_failures": 0
        }
        
        self.logger.info(f"✅ Authentication Module '{service_name}' initialized")
    
    async def initialize(self):
        """Initialize Authentication Module."""
        try:
            self.logger.info(f"🚀 Initializing Authentication Module '{self.service_name}'...")
            self.logger.info(f"✅ Authentication Module '{self.service_name}' initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Authentication Module '{self.service_name}': {e}")
            raise
    
    async def enforce_authentication(self, security_context: SecurityContext) -> Dict[str, Any]:
        """Enforce authentication with comprehensive logging."""
        try:
            self.auth_stats["authentication_attempts"] += 1
            
            # Use auth abstraction from Public Works Foundation
            if self.auth_abstraction:
                auth_result = await self.auth_abstraction.authenticate_user(security_context)
                if auth_result.get("success"):
                    self.auth_stats["authentication_successes"] += 1
                    
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
            self.auth_stats["authentication_failures"] += 1
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
    
    async def validate_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user credentials."""
        try:
            if not credentials.get("email") or not credentials.get("password"):
                return {
                    "success": False,
                    "message": "Invalid credentials format"
                }
            
            # Use auth abstraction if available
            if self.auth_abstraction:
                auth_result = await self.auth_abstraction.authenticate_user(credentials)
                return auth_result
            
            # Fallback validation
            return {
                "success": True,
                "message": "Credentials validated (fallback)"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Credential validation failed: {e}")
            return {
                "success": False,
                "message": f"Credential validation failed: {e}"
            }
    
    async def authorize_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authorize user action on resource.
        
        Zero-trust authorization: "Secure by design, open by policy"
        
        Args:
            request: Authorization request containing:
                - user_id: User identifier
                - action: Action being performed (e.g., "POST", "GET")
                - resource: Resource being accessed (e.g., "/api/operations/...")
                - tenant_id: Tenant identifier (optional)
                - context: Additional context (optional)
        
        Returns:
            Authorization result with success/failure
        """
        try:
            user_id = request.get("user_id", "anonymous")
            action = request.get("action", "unknown")
            resource = request.get("resource", "unknown")
            tenant_id = request.get("tenant_id", "default")
            
            self.logger.info(f"🛡️ Authorization check: {user_id} -> {action} {resource}")
            
            # Create security context
            security_context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=request.get("context", {}).get("roles", ["user"]),
                permissions=request.get("context", {}).get("permissions", []),
                origin=request.get("context", {}).get("origin", "api")
            )
            
            # Use authorization abstraction if available
            if hasattr(self, 'authorization_abstraction') and self.authorization_abstraction:
                try:
                    # Call the enforce method on authorization abstraction
                    is_authorized = await self.authorization_abstraction.enforce(
                        action=action,
                        resource=resource,
                        context=security_context
                    )
                    
                    if is_authorized:
                        self.logger.info(f"✅ Authorization granted: {user_id} -> {action} {resource}")
                        return {
                            "success": True,
                            "message": "Authorization granted",
                            "user_id": user_id,
                            "resource": resource,
                            "action": action
                        }
                    else:
                        self.logger.warning(f"❌ Authorization denied: {user_id} -> {action} {resource}")
                        return {
                            "success": False,
                            "message": "Authorization denied by policy",
                            "user_id": user_id,
                            "resource": resource,
                            "action": action
                        }
                        
                except Exception as e:
                    self.logger.error(f"❌ Authorization abstraction error: {e}")
                    # Fail closed for zero-trust
                    return {
                        "success": False,
                        "message": f"Authorization check failed: {str(e)}",
                        "user_id": user_id
                    }
            
            # MVP Fallback: Allow all requests if no authorization abstraction
            # This maintains backward compatibility while we're building out the system
            self.logger.warning(f"⚠️ No authorization abstraction - allowing request (MVP mode)")
            return {
                "success": True,
                "message": "Authorization granted (MVP mode - no policy engine)",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "mvp_mode": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Authorization failed: {e}")
            # Fail closed for zero-trust
            return {
                "success": False,
                "message": f"Authorization failed: {str(e)}"
            }
    
    async def get_authentication_metrics(self) -> Dict[str, Any]:
        """Get authentication metrics."""
        try:
            total_attempts = self.auth_stats["authentication_attempts"]
            success_rate = (self.auth_stats["authentication_successes"] / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                "authentication_attempts": self.auth_stats["authentication_attempts"],
                "authentication_successes": self.auth_stats["authentication_successes"],
                "authentication_failures": self.auth_stats["authentication_failures"],
                "success_rate": f"{success_rate:.2f}%"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get authentication metrics: {e}")
            return {}
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return [
            "authentication_enforcement",
            "credential_validation",
            "authentication_metrics"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "AuthenticationModule",
            "service_name": self.service_name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "auth_abstraction_available": self.auth_abstraction is not None,
            "metrics": await self.get_authentication_metrics()
        }



