#!/usr/bin/env python3
"""
Logging Middleware for API Routing

Handles request/response logging for API requests across all realms.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class LoggingMiddleware:
    """Middleware for API request/response logging."""
    
    def __init__(self, di_container):
        """Initialize logging middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("LoggingMiddleware")
        
        # Get logger utility
        try:
            self.logger_utility = di_container.get_logger("api_routing")
        except Exception as e:
            self.logger.warning(f"Logger utility not available: {e}")
            self.logger_utility = None
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process logging for the request."""
        start_time = time.time()
        
        try:
            # Log request start
            await self._log_request_start(request_context, user_context)
            
            # Execute next handler
            response_context = await next_handler()
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            response_context.processing_time_ms = processing_time
            
            # Log request completion
            await self._log_request_completion(request_context, response_context)
            
            return response_context
            
        except Exception as e:
            # Log request error
            processing_time = (time.time() - start_time) * 1000
            await self._log_request_error(request_context, e, processing_time)
            
            # Re-raise the exception
            raise
    
    async def _log_request_start(self, request_context: RequestContext, user_context: UserContext) -> None:
        """Log request start."""
        log_data = {
            "event": "request_start",
            "request_id": request_context.request_id,
            "method": request_context.method.value,
            "path": request_context.path,
            "user_id": user_context.user_id if user_context else None,
            "tenant_id": user_context.tenant_id if user_context else None,
            "timestamp": request_context.start_time,
            "headers": self._sanitize_headers(request_context.headers),
            "query_params": request_context.query_params
        }
        
        if self.logger_utility:
            self.logger_utility.info("API Request Started", extra=log_data)
        else:
            self.logger.info(f"🚀 API Request Started: {request_context.method.value} {request_context.path} - {request_context.request_id}")
    
    async def _log_request_completion(self, request_context: RequestContext, response_context: ResponseContext) -> None:
        """Log request completion."""
        log_data = {
            "event": "request_completed",
            "request_id": request_context.request_id,
            "method": request_context.method.value,
            "path": request_context.path,
            "status_code": response_context.status_code,
            "processing_time_ms": response_context.processing_time_ms,
            "timestamp": response_context.end_time,
            "success": 200 <= response_context.status_code < 300
        }
        
        if self.logger_utility:
            if log_data["success"]:
                self.logger_utility.info("API Request Completed", extra=log_data)
            else:
                self.logger_utility.warning("API Request Failed", extra=log_data)
        else:
            status_emoji = "✅" if log_data["success"] else "❌"
            self.logger.info(f"{status_emoji} API Request Completed: {request_context.method.value} {request_context.path} - {response_context.status_code} ({response_context.processing_time_ms:.2f}ms)")
    
    async def _log_request_error(self, request_context: RequestContext, error: Exception, processing_time: float) -> None:
        """Log request error."""
        log_data = {
            "event": "request_error",
            "request_id": request_context.request_id,
            "method": request_context.method.value,
            "path": request_context.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "processing_time_ms": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.logger_utility:
            self.logger_utility.error("API Request Error", extra=log_data)
        else:
            self.logger.error(f"❌ API Request Error: {request_context.method.value} {request_context.path} - {type(error).__name__}: {str(error)}")
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize headers to remove sensitive information."""
        sensitive_headers = {
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "x-access-token", "x-refresh-token", "x-csrf-token"
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized


