#!/usr/bin/env python3
"""
Error Handling Middleware for API Routing

Handles errors and creates standardized error responses for API requests.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class ErrorHandlingMiddleware:
    """Middleware for standardized error handling."""
    
    def __init__(self, di_container):
        """Initialize error handling middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("ErrorHandlingMiddleware")
        
        # Get error handler utility
        try:
            self.error_handler = di_container.get_error_handler()
        except Exception as e:
            self.logger.warning(f"Error handler utility not available: {e}")
            self.error_handler = None
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process error handling for the request."""
        try:
            # Execute next handler
            return await next_handler()
            
        except Exception as e:
            # Handle the error
            return await self._handle_error(request_context, e)
    
    async def _handle_error(self, request_context: RequestContext, error: Exception) -> ResponseContext:
        """Handle error and create standardized response."""
        try:
            # Log the error
            self.logger.error(f"❌ API Request Error: {type(error).__name__}: {str(error)}")
            
            # Use error handler utility if available
            if self.error_handler:
                error_info = self.error_handler.handle_error(error, {
                    "request_id": request_context.request_id,
                    "method": request_context.method.value,
                    "path": request_context.path,
                    "user_id": request_context.user_context.user_id if request_context.user_context else None,
                    "tenant_id": request_context.user_context.tenant_id if request_context.user_context else None
                })
                
                # Create response from error handler result
                return self._create_error_response_from_handler(request_context, error_info)
            else:
                # Create basic error response
                return self._create_basic_error_response(request_context, error)
                
        except Exception as handler_error:
            # Fallback error handling
            self.logger.error(f"❌ Error handler failed: {handler_error}")
            return self._create_fallback_error_response(request_context, error)
    
    def _create_error_response_from_handler(self, request_context: RequestContext, error_info: Dict[str, Any]) -> ResponseContext:
        """Create error response from error handler result."""
        # Determine status code based on error type
        status_code = self._get_status_code_from_error_type(error_info.get("error_type", "UNKNOWN_ERROR"))
        
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=status_code,
            body={
                "success": False,
                "error": {
                    "code": error_info.get("error_type", "UNKNOWN_ERROR"),
                    "message": error_info.get("error_message", "An error occurred"),
                    "request_id": request_context.request_id,
                    "timestamp": error_info.get("timestamp", datetime.utcnow().isoformat()),
                    "details": error_info.get("context", {}),
                    "handler_result": error_info.get("handler_result", {})
                }
            },
            end_time=datetime.utcnow().isoformat()
        )
    
    def _create_basic_error_response(self, request_context: RequestContext, error: Exception) -> ResponseContext:
        """Create basic error response without error handler utility."""
        status_code = self._get_status_code_from_exception(error)
        
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=status_code,
            body={
                "success": False,
                "error": {
                    "code": type(error).__name__.upper(),
                    "message": str(error),
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": type(error).__name__
                }
            },
            end_time=datetime.utcnow().isoformat()
        )
    
    def _create_fallback_error_response(self, request_context: RequestContext, error: Exception) -> ResponseContext:
        """Create fallback error response when error handler fails."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=500,
            body={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred",
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "fallback": True
                }
            },
            end_time=datetime.utcnow().isoformat()
        )
    
    def _get_status_code_from_error_type(self, error_type: str) -> int:
        """Get HTTP status code from error type."""
        error_type_mapping = {
            "VALIDATION_ERROR": 400,
            "AUTHENTICATION_ERROR": 401,
            "AUTHORIZATION_ERROR": 403,
            "NOT_FOUND_ERROR": 404,
            "CONFLICT_ERROR": 409,
            "RATE_LIMIT_ERROR": 429,
            "SERVICE_ERROR": 500,
            "INTEGRATION_ERROR": 502,
            "TIMEOUT_ERROR": 504
        }
        
        return error_type_mapping.get(error_type, 500)
    
    def _get_status_code_from_exception(self, error: Exception) -> int:
        """Get HTTP status code from exception type."""
        if isinstance(error, ValueError):
            return 400
        elif isinstance(error, PermissionError):
            return 403
        elif isinstance(error, FileNotFoundError):
            return 404
        elif isinstance(error, TimeoutError):
            return 504
        else:
            return 500


