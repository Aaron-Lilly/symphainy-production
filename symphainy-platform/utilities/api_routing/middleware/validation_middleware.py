#!/usr/bin/env python3
"""
Validation Middleware for API Routing

Handles request validation for API requests across all realms.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class ValidationMiddleware:
    """Middleware for API request validation."""
    
    def __init__(self, di_container):
        """Initialize validation middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("ValidationMiddleware")
        
        # Get validation utility
        try:
            self.validation_utility = di_container.get_validation()
        except Exception as e:
            self.logger.warning(f"Validation utility not available: {e}")
            self.validation_utility = None
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process validation for the request."""
        try:
            # Validate request structure
            validation_result = await self._validate_request(request_context)
            if not validation_result["valid"]:
                return self._create_validation_error_response(request_context, validation_result["errors"])
            
            # Validate user context if present
            if user_context:
                user_validation_result = await self._validate_user_context(user_context)
                if not user_validation_result["valid"]:
                    return self._create_validation_error_response(request_context, user_validation_result["errors"])
            
            # Continue to next handler
            return await next_handler()
            
        except Exception as e:
            self.logger.error(f"❌ Validation middleware error: {e}")
            return self._create_validation_error_response(request_context, [f"Validation error: {str(e)}"])
    
    async def _validate_request(self, request_context: RequestContext) -> Dict[str, Any]:
        """Validate request structure and content."""
        errors = []
        
        # Validate HTTP method
        if not request_context.method:
            errors.append("HTTP method is required")
        
        # Validate path
        if not request_context.path:
            errors.append("Request path is required")
        elif not request_context.path.startswith("/"):
            errors.append("Request path must start with '/'")
        
        # Validate headers
        if request_context.headers:
            for key, value in request_context.headers.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append(f"Header '{key}' must be a string")
        
        # Validate query parameters
        if request_context.query_params:
            for key, value in request_context.query_params.items():
                if not isinstance(key, str):
                    errors.append(f"Query parameter key '{key}' must be a string")
        
        # Validate request body
        if request_context.body:
            if not isinstance(request_context.body, dict):
                errors.append("Request body must be a dictionary")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _validate_user_context(self, user_context: UserContext) -> Dict[str, Any]:
        """Validate user context."""
        errors = []
        
        # Validate required fields
        if not user_context.user_id:
            errors.append("User ID is required")
        elif not isinstance(user_context.user_id, str):
            errors.append("User ID must be a string")
        
        if not user_context.tenant_id:
            errors.append("Tenant ID is required")
        elif not isinstance(user_context.tenant_id, str):
            errors.append("Tenant ID must be a string")
        
        # Validate optional fields
        if user_context.roles and not isinstance(user_context.roles, list):
            errors.append("Roles must be a list")
        
        if user_context.permissions and not isinstance(user_context.permissions, list):
            errors.append("Permissions must be a list")
        
        # Use validation utility if available
        if self.validation_utility:
            try:
                # Validate user context using validation utility
                validation_result = await self.validation_utility.validate_user_context(user_context)
                if not validation_result.get("valid", True):
                    errors.extend(validation_result.get("errors", []))
            except Exception as e:
                self.logger.warning(f"Validation utility error: {e}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _create_validation_error_response(self, request_context: RequestContext, errors: List[str]) -> ResponseContext:
        """Create validation error response."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=400,
            body={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": errors,
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            end_time=datetime.utcnow().isoformat()
        )


