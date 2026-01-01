#!/usr/bin/env python3
"""
Security Decorators Module - Security Guard Micro-Module

Provides security enforcement decorators for service methods.
Part of the Security Guard Service micro-modular architecture.

WHAT (Decorators Role): I provide security enforcement decorators
HOW (Decorators Implementation): I create decorators that enforce security policies
"""

import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext


class SecurityDecorators:
    """
    Security Decorators Module - Security Guard Micro-Module
    
    Provides security enforcement decorators for service methods.
    Part of the Security Guard Service micro-modular architecture.
    
    WHAT (Decorators Role): I provide security enforcement decorators
    HOW (Decorators Implementation): I create decorators that enforce security policies
    """
    
    def __init__(self, service_name: str = "security_decorators_module"):
        """Initialize Security Decorators Module."""
        self.service_name = service_name
        self.logger = self.service.di_container.get_logger(f"SecurityDecorators-{service_name}")
        
        # Decorator usage statistics
        self.decorator_stats = {
            "authentication_checks": 0,
            "authorization_checks": 0,
            "tenant_access_checks": 0,
            "decorator_failures": 0
        }
        
        self.logger.info(f"✅ Security Decorators Module '{service_name}' initialized")
    
    async def initialize(self):
        """Initialize Security Decorators Module."""
        try:
            self.logger.info(f"🚀 Initializing Security Decorators Module '{self.service_name}'...")
            self.logger.info(f"✅ Security Decorators Module '{self.service_name}' initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Security Decorators Module '{self.service_name}': {e}")
            raise
    
    def require_authentication(self, func: Callable) -> Callable:
        """Decorator to require authentication."""
        @functools.wraps(func)
        async def wrapper(self, context: SecurityContext, *args, **kwargs):
            try:
                self.decorator_stats["authentication_checks"] += 1
                
                # Check if user is authenticated
                if not context.user_id:
                    self.decorator_stats["decorator_failures"] += 1
                    raise AuthenticationError("Authentication required")
                
                # Call the original function
                return await func(self, context, *args, **kwargs)
                
            except Exception as e:
                self.logger.error(f"❌ Authentication decorator failed: {e}")
                self.decorator_stats["decorator_failures"] += 1
                raise
        
        return wrapper
    
    def require_authorization(self, action: str, resource: str):
        """Decorator to require authorization."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(self, context: SecurityContext, *args, **kwargs):
                try:
                    self.decorator_stats["authorization_checks"] += 1
                    
                    # Check if user has permission for action on resource
                    if not self._check_authorization(action, resource, context):
                        self.decorator_stats["decorator_failures"] += 1
                        raise AuthorizationError(f"Authorization denied: {action} on {resource}")
                    
                    # Call the original function
                    return await func(self, context, *args, **kwargs)
                    
                except Exception as e:
                    self.logger.error(f"❌ Authorization decorator failed: {e}")
                    self.decorator_stats["decorator_failures"] += 1
                    raise
            
            return wrapper
        return decorator
    
    def require_tenant_access(self, tenant_field: str):
        """Decorator to require tenant access validation."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(self, context: SecurityContext, *args, **kwargs):
                try:
                    self.decorator_stats["tenant_access_checks"] += 1
                    
                    # Extract tenant from request or context
                    resource_tenant = getattr(context, tenant_field, None)
                    if not resource_tenant:
                        self.decorator_stats["decorator_failures"] += 1
                        raise ValueError(f"Tenant field '{tenant_field}' not found in context")
                    
                    # Check tenant access
                    if context.tenant_id != resource_tenant:
                        self.decorator_stats["decorator_failures"] += 1
                        raise TenantAccessError(f"Tenant access denied: {context.tenant_id} -> {resource_tenant}")
                    
                    # Call the original function
                    return await func(self, context, *args, **kwargs)
                    
                except Exception as e:
                    self.logger.error(f"❌ Tenant access decorator failed: {e}")
                    self.decorator_stats["decorator_failures"] += 1
                    raise
            
            return wrapper
        return decorator
    
    def require_permission(self, permission: str):
        """Decorator to require specific permission."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(self, context: SecurityContext, *args, **kwargs):
                try:
                    # Check if user has required permission
                    if permission not in context.permissions and "admin" not in context.permissions:
                        self.decorator_stats["decorator_failures"] += 1
                        raise AuthorizationError(f"Permission denied: {permission}")
                    
                    # Call the original function
                    return await func(self, context, *args, **kwargs)
                    
                except Exception as e:
                    self.logger.error(f"❌ Permission decorator failed: {e}")
                    self.decorator_stats["decorator_failures"] += 1
                    raise
            
            return wrapper
        return decorator
    
    def require_role(self, role: str):
        """Decorator to require specific role."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(self, context: SecurityContext, *args, **kwargs):
                try:
                    # Check if user has required role
                    if role not in context.roles and "admin" not in context.roles:
                        self.decorator_stats["decorator_failures"] += 1
                        raise AuthorizationError(f"Role denied: {role}")
                    
                    # Call the original function
                    return await func(self, context, *args, **kwargs)
                    
                except Exception as e:
                    self.logger.error(f"❌ Role decorator failed: {e}")
                    self.decorator_stats["decorator_failures"] += 1
                    raise
            
            return wrapper
        return decorator
    
    def _check_authorization(self, action: str, resource: str, context: SecurityContext) -> bool:
        """Check authorization for action on resource."""
        try:
            # Basic authorization check
            # In a real implementation, this would use the authorization abstraction
            if not context.user_id:
                return False
            
            # Check if user has permission for action
            action_permission = f"{action}:{resource}"
            if action_permission in context.permissions or "admin" in context.permissions:
                return True
            
            # Check for specific action permission
            if action in context.permissions or "admin" in context.permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Authorization check failed: {e}")
            return False
    
    async def get_decorator_metrics(self) -> Dict[str, Any]:
        """Get decorator usage metrics."""
        try:
            total_checks = (
                self.decorator_stats["authentication_checks"] +
                self.decorator_stats["authorization_checks"] +
                self.decorator_stats["tenant_access_checks"]
            )
            
            failure_rate = (self.decorator_stats["decorator_failures"] / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "authentication_checks": self.decorator_stats["authentication_checks"],
                "authorization_checks": self.decorator_stats["authorization_checks"],
                "tenant_access_checks": self.decorator_stats["tenant_access_checks"],
                "decorator_failures": self.decorator_stats["decorator_failures"],
                "failure_rate": f"{failure_rate:.2f}%"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get decorator metrics: {e}")
            return {}
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return [
            "authentication_decorator",
            "authorization_decorator",
            "tenant_access_decorator",
            "permission_decorator",
            "role_decorator",
            "decorator_metrics"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "SecurityDecorators",
            "service_name": self.service_name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "metrics": await self.get_decorator_metrics()
        }


# ============================================================================
# SECURITY EXCEPTIONS
# ============================================================================

class AuthenticationError(Exception):
    """Authentication error."""
    pass

class AuthorizationError(Exception):
    """Authorization error."""
    pass

class TenantAccessError(Exception):
    """Tenant access error."""
    pass



