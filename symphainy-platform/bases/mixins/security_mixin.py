#!/usr/bin/env python3
"""
Security Mixin

Focused mixin for security patterns - extracts zero-trust and multi-tenancy
functionality from base classes into a reusable, testable component.

WHAT (Security Role): I provide zero-trust security and multi-tenancy patterns
HOW (Security Mixin): I centralize security validation and context management
"""

from typing import Dict, Any, Optional


class SecurityMixin:
    """
    Mixin for zero-trust security and multi-tenancy patterns.
    
    Provides consistent security validation, context management, and access control
    across all services with proper error handling.
    """
    
    def _init_security(self, di_container: Optional[Any] = None,
                      security_provider: Optional[Any] = None, 
                      authorization_guard: Optional[Any] = None):
        """Initialize security patterns."""
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        self.current_security_context = None
        
        # Get logger from DI Container if available
        if di_container:
            if not hasattr(di_container, 'get_logger'):
                raise RuntimeError(
                    f"DI Container does not have get_logger method. "
                    f"This indicates a platform initialization failure or incorrect DI Container instance."
                )
            
            try:
                logger_service = di_container.get_logger(f"{self.__class__.__name__}.security")
                if not logger_service:
                    raise RuntimeError(
                        f"DI Container.get_logger() returned None. "
                        f"Logging service should be available - this indicates a platform initialization failure."
                    )
                self.logger = logger_service
            except Exception as e:
                raise RuntimeError(
                    f"Failed to get logger from DI Container: {e}. "
                    f"DI Container must initialize logging utility before services can use it. "
                    f"This indicates a platform initialization failure."
                ) from e
        else:
            raise ValueError(
                "DI Container is required for SecurityMixin initialization. "
                "Services must be created with a valid DI Container instance."
            )
        
        self.logger.debug("Security mixin initialized")
    
    def get_security_context(self) -> Optional[Dict[str, Any]]:
        """Get current security context."""
        return self.current_security_context
    
    def set_security_context(self, context: Dict[str, Any]) -> bool:
        """Set security context with validation."""
        try:
            if self.security_provider:
                validated_context = self.security_provider.validate_context(context)
                self.current_security_context = validated_context
                self.logger.debug(f"Security context set: {validated_context.get('user_id', 'unknown')}")
                return True
            else:
                self.current_security_context = context
                self.logger.warning("Security context set without validation (no security provider)")
                return True
        except Exception as e:
            self.logger.error(f"Failed to set security context: {e}")
            return False
    
    def validate_access(self, resource: str, action: str) -> bool:
        """Validate access to resource for action using zero-trust principles."""
        try:
            if not self.current_security_context:
                self.logger.warning("No security context available for access validation")
                return False
            
            if self.authorization_guard:
                return self.authorization_guard.check_permission(
                    self.current_security_context, resource, action
                )
            else:
                self.logger.warning("No authorization guard available for access validation")
                return False
                
        except Exception as e:
            self.logger.error(f"Access validation failed for {resource}:{action}: {e}")
            return False
    
    def get_tenant_id(self) -> Optional[str]:
        """Get current tenant ID from security context."""
        if self.current_security_context:
            return self.current_security_context.get("tenant_id")
        return None
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID from security context."""
        if self.current_security_context:
            return self.current_security_context.get("user_id")
        return None
    
    def get_user_roles(self) -> list:
        """Get user roles from security context."""
        if self.current_security_context:
            return self.current_security_context.get("roles", [])
        return []
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.get_user_roles()
    
    def validate_tenant_access(self, tenant_id: str) -> bool:
        """Validate access to specific tenant."""
        current_tenant = self.get_tenant_id()
        if not current_tenant:
            return False
        
        # Multi-tenancy validation
        if current_tenant == tenant_id:
            return True
        
        # Check for cross-tenant permissions
        if self.has_role("admin") or self.has_role("cross_tenant"):
            return True
        
        return False
    
    def clear_security_context(self):
        """Clear current security context."""
        self.current_security_context = None
        self.logger.debug("Security context cleared")

