#!/usr/bin/env python3
"""
Authentication Middleware for API Routing

Handles authentication for API requests across all realms.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class AuthenticationMiddleware:
    """Middleware for API request authentication."""
    
    def __init__(self, di_container):
        """Initialize authentication middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("AuthenticationMiddleware")
        self.security_provider = None
        
        # Initialize security provider if available
        try:
            self.security_provider = di_container.get_security_provider()
        except Exception as e:
            self.logger.warning(f"Security provider not available: {e}")
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process authentication for the request."""
        try:
            # Check if authentication is required
            if not self._requires_authentication(request_context):
                return await next_handler()
            
            # Validate user context
            if not user_context or not user_context.user_id:
                return self._create_unauthorized_response(request_context, "Authentication required")
            
            # Validate tenant context
            if not user_context.tenant_id:
                return self._create_unauthorized_response(request_context, "Tenant context required")
            
            # Additional security validation if security provider is available
            if self.security_provider:
                if not await self._validate_security_context(user_context):
                    return self._create_unauthorized_response(request_context, "Invalid security context")
            
            # Log successful authentication
            self.logger.info(f"✅ Request authenticated: {user_context.user_id} ({user_context.tenant_id})")
            
            # Continue to next handler
            return await next_handler()
            
        except Exception as e:
            self.logger.error(f"❌ Authentication middleware error: {e}")
            return self._create_unauthorized_response(request_context, "Authentication failed")
    
    def _requires_authentication(self, request_context: RequestContext) -> bool:
        """Check if the request requires authentication."""
        # Skip authentication for health checks and public endpoints
        public_paths = [
            "/health",
            "/api/health",
            "/api/status",
            "/api/docs",
            "/api/openapi.json"
        ]
        
        return not any(request_context.path.startswith(path) for path in public_paths)
    
    async def _validate_security_context(self, user_context: UserContext) -> bool:
        """Validate security context using security provider."""
        try:
            if not self.security_provider:
                return True  # No security provider, allow request
            
            # Create security context
            security_context = self.security_provider.create_security_context(
                user_id=user_context.user_id,
                tenant_id=user_context.tenant_id,
                roles=user_context.roles or [],
                permissions=user_context.permissions or []
            )
            
            # Validate security context
            return security_context is not None
            
        except Exception as e:
            self.logger.error(f"❌ Security context validation failed: {e}")
            return False
    
    def _create_unauthorized_response(self, request_context: RequestContext, message: str) -> ResponseContext:
        """Create unauthorized response."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=401,
            body={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": message,
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            end_time=datetime.utcnow().isoformat()
        )


