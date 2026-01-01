#!/usr/bin/env python3
"""
Authorization Middleware for API Routing

Handles authorization for API requests across all realms.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class AuthorizationMiddleware:
    """Middleware for API request authorization."""
    
    def __init__(self, di_container):
        """Initialize authorization middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("AuthorizationMiddleware")
        self.authorization_guard = None
        
        # Initialize authorization guard if available
        try:
            self.authorization_guard = di_container.get_authorization_guard()
        except Exception as e:
            self.logger.warning(f"Authorization guard not available: {e}")
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process authorization for the request."""
        try:
            # Check if authorization is required
            if not self._requires_authorization(request_context):
                return await next_handler()
            
            # Check authorization
            if not await self._check_authorization(request_context, user_context):
                return self._create_forbidden_response(request_context, "Insufficient permissions")
            
            # Log successful authorization
            self.logger.info(f"✅ Request authorized: {user_context.user_id} - {request_context.method.value} {request_context.path}")
            
            # Continue to next handler
            return await next_handler()
            
        except Exception as e:
            self.logger.error(f"❌ Authorization middleware error: {e}")
            return self._create_forbidden_response(request_context, "Authorization failed")
    
    def _requires_authorization(self, request_context: RequestContext) -> bool:
        """Check if the request requires authorization."""
        # Skip authorization for health checks and public endpoints
        public_paths = [
            "/health",
            "/api/health",
            "/api/status",
            "/api/docs",
            "/api/openapi.json"
        ]
        
        return not any(request_context.path.startswith(path) for path in public_paths)
    
    async def _check_authorization(self, request_context: RequestContext, user_context: UserContext) -> bool:
        """Check if user is authorized for the request."""
        try:
            if not self.authorization_guard:
                return True  # No authorization guard, allow request
            
            # Determine required action and resource
            action = self._get_required_action(request_context)
            resource = self._get_resource_from_path(request_context.path)
            
            # Check authorization
            return self.authorization_guard.enforce(action, resource, user_context)
            
        except Exception as e:
            self.logger.error(f"❌ Authorization check failed: {e}")
            return False
    
    def _get_required_action(self, request_context: RequestContext) -> str:
        """Get required action from HTTP method."""
        action_mapping = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
            "HEAD": "read",
            "OPTIONS": "read"
        }
        
        return action_mapping.get(request_context.method.value, "read")
    
    def _get_resource_from_path(self, path: str) -> str:
        """Get resource from request path."""
        # Extract resource from path (e.g., /api/content/files -> content:files)
        path_parts = path.strip("/").split("/")
        if len(path_parts) >= 2:
            return f"{path_parts[1]}:{path_parts[2] if len(path_parts) > 2 else 'list'}"
        return "unknown"
    
    def _create_forbidden_response(self, request_context: RequestContext, message: str) -> ResponseContext:
        """Create forbidden response."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=403,
            body={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": message,
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            end_time=datetime.utcnow().isoformat()
        )


