#!/usr/bin/env python3
"""
Enhanced Error Handling Middleware

Enhanced error handling middleware for API routing with realm-specific and service type-specific error handling.
Integrates with the new error handling infrastructure for comprehensive error management.

WHAT (Utility Role): I provide enhanced error handling for API routing
HOW (Utility Implementation): I integrate realm-specific and service type-specific error handling with API routing
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

from ...error.error_handler_factory import get_error_handler_factory
from ...error.service_type_error_handler import ServiceTypeErrorHandler, ServiceType as ErrorServiceType
from ...error.realm_error_handler_base import ErrorContext, ErrorResponse
from ..api_routing_utility import RequestContext, ResponseContext
from ..middleware_protocol import Middleware


class EnhancedErrorHandlingMiddleware:
    """
    Enhanced error handling middleware for API routing.
    
    Integrates realm-specific and service type-specific error handling
    with API routing for comprehensive error management.
    """
    
    def __init__(self, di_container):
        """Initialize enhanced error handling middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("EnhancedErrorHandlingMiddleware")
        
        # Get error handler factory
        self.error_handler_factory = get_error_handler_factory()
        
        # Cache for error handlers by realm and service type
        self.error_handler_cache: Dict[str, ServiceTypeErrorHandler] = {}
        
        self.logger.info("✅ Enhanced Error Handling Middleware initialized")
    
    async def __call__(self, request_context: RequestContext, user_context, next_handler: Callable) -> ResponseContext:
        """
        Execute enhanced error handling middleware.
        
        Args:
            request_context: The request context
            user_context: The user context
            next_handler: The next handler in the chain
            
        Returns:
            ResponseContext: The response context
        """
        try:
            # Add request ID and correlation ID if not present
            if not request_context.request_id:
                request_context.request_id = str(uuid.uuid4())
            if not request_context.correlation_id:
                request_context.correlation_id = str(uuid.uuid4())
            
            # Execute the next handler
            response_context = await next_handler()
            
            # Log successful request
            await self._log_successful_request(request_context, response_context, user_context)
            
            return response_context
            
        except Exception as error:
            # Handle error with enhanced error handling
            return await self._handle_error(request_context, user_context, error)
    
    async def _handle_error(self, request_context: RequestContext, user_context, error: Exception) -> ResponseContext:
        """Handle error with enhanced error handling."""
        try:
            # Determine service type from request context
            service_type = self._determine_service_type(request_context)
            
            # Get or create error handler
            error_handler = await self._get_error_handler(request_context.realm, service_type)
            
            # Create error context
            error_context = ErrorContext(
                realm=request_context.realm,
                service_type=service_type.value,
                service_name=request_context.pillar or "unknown",
                operation=f"{request_context.method.value} {request_context.path}",
                user_id=getattr(user_context, 'user_id', None),
                tenant_id=getattr(user_context, 'tenant_id', None),
                request_id=request_context.request_id,
                correlation_id=request_context.correlation_id,
                additional_context={
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value,
                    "realm": request_context.realm,
                    "pillar": request_context.pillar
                }
            )
            
            # Handle error with service type-specific error handler
            error_response = error_handler.handle_service_error(error, error_context, service_type)
            
            # Create response context from error response
            response_context = self._create_error_response_context(error_response, request_context)
            
            # Log error
            await self._log_error(request_context, user_context, error, error_response)
            
            return response_context
            
        except Exception as e:
            # Fallback error handling
            self.logger.error(f"❌ Enhanced error handling failed: {e}")
            return self._create_fallback_error_response(request_context, error)
    
    def _determine_service_type(self, request_context: RequestContext) -> ErrorServiceType:
        """Determine service type from request context."""
        # Check if it's an MCP server request
        if request_context.path.startswith("/mcp/") or "mcp" in request_context.pillar.lower():
            return ErrorServiceType.MCP_SERVER
        
        # Check if it's a foundation service
        if "foundation" in request_context.realm.lower():
            return ErrorServiceType.FOUNDATION_SERVICE
        
        # Check if it's an agent request
        if "agent" in request_context.pillar.lower() or "agent" in request_context.path:
            return ErrorServiceType.AGENT
        
        # Default to service
        return ErrorServiceType.SERVICE
    
    async def _get_error_handler(self, realm: str, service_type: ErrorServiceType) -> ServiceTypeErrorHandler:
        """Get or create error handler for realm and service type."""
        cache_key = f"{realm}:{service_type.value}"
        
        if cache_key not in self.error_handler_cache:
            # Get realm-specific error handler
            realm_error_handler = self.error_handler_factory.get_error_handler(realm)
            
            # Create service type-specific error handler
            error_handler = ServiceTypeErrorHandler(realm_error_handler)
            
            # Cache the error handler
            self.error_handler_cache[cache_key] = error_handler
            
            self.logger.debug(f"✅ Created error handler for {cache_key}")
        
        return self.error_handler_cache[cache_key]
    
    def _create_error_response_context(self, error_response: ErrorResponse, request_context: RequestContext) -> ResponseContext:
        """Create response context from error response."""
        # Determine HTTP status code from error severity
        status_code = self._get_http_status_code(error_response.severity)
        
        # Create response body
        response_body = {
            "success": error_response.success,
            "error_code": error_response.error_code,
            "error_message": error_response.error_message,
            "error_type": error_response.error_type,
            "severity": error_response.severity.value,
            "action": error_response.action.value,
            "recovery_suggestions": error_response.recovery_suggestions,
            "user_message": error_response.user_message,
            "request_id": request_context.request_id,
            "timestamp": error_response.timestamp,
            "realm": error_response.realm,
            "service_type": error_response.service_type
        }
        
        # Add technical details for debugging (only in development)
        if self._is_development_mode():
            response_body["technical_details"] = error_response.technical_details
        
        return ResponseContext(
            status_code=status_code,
            body=response_body,
            headers={
                "Content-Type": "application/json",
                "X-Request-ID": request_context.request_id,
                "X-Correlation-ID": request_context.correlation_id,
                "X-Error-Code": error_response.error_code,
                "X-Error-Severity": error_response.severity.value
            },
            metadata={
                "error_handled": True,
                "error_code": error_response.error_code,
                "error_severity": error_response.severity.value,
                "realm": error_response.realm,
                "service_type": error_response.service_type
            }
        )
    
    def _get_http_status_code(self, severity) -> int:
        """Get HTTP status code from error severity."""
        severity_mapping = {
            "low": 400,
            "medium": 400,
            "high": 500,
            "critical": 500
        }
        return severity_mapping.get(severity.value, 500)
    
    def _is_development_mode(self) -> bool:
        """Check if running in development mode."""
        try:
            config = self.di_container.get_config()
            return config.get_config_value("environment", "production").lower() == "development"
        except:
            return False
    
    def _create_fallback_error_response(self, request_context: RequestContext, error: Exception) -> ResponseContext:
        """Create fallback error response when enhanced error handling fails."""
        return ResponseContext(
            status_code=500,
            body={
                "success": False,
                "error_code": "ENHANCED_ERROR_HANDLING_FAILED",
                "error_message": "Enhanced error handling failed",
                "error_type": "ErrorHandlingError",
                "severity": "critical",
                "action": "escalate",
                "recovery_suggestions": ["Contact system administrator immediately"],
                "user_message": "System error - please contact support",
                "request_id": request_context.request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "realm": request_context.realm,
                "service_type": "unknown",
                "technical_details": {
                    "original_error": str(error),
                    "original_error_type": type(error).__name__,
                    "fallback_reason": "Enhanced error handling failed"
                }
            },
            headers={
                "Content-Type": "application/json",
                "X-Request-ID": request_context.request_id,
                "X-Correlation-ID": request_context.correlation_id,
                "X-Error-Code": "ENHANCED_ERROR_HANDLING_FAILED",
                "X-Error-Severity": "critical"
            },
            metadata={
                "error_handled": False,
                "error_code": "ENHANCED_ERROR_HANDLING_FAILED",
                "error_severity": "critical",
                "realm": request_context.realm,
                "service_type": "unknown"
            }
        )
    
    async def _log_successful_request(self, request_context: RequestContext, response_context: ResponseContext, user_context):
        """Log successful request."""
        try:
            # Get realm-specific logging service
            logging_service = self.di_container.get_realm_logging_service(request_context.realm)
            
            # Create log context
            from ...logging.realm_logging_service_base import LogContext
            log_context = LogContext(
                realm=request_context.realm,
                service_type="api_routing",
                service_name=request_context.pillar or "unknown",
                operation=f"{request_context.method.value} {request_context.path}",
                user_id=getattr(user_context, 'user_id', None),
                tenant_id=getattr(user_context, 'tenant_id', None),
                request_id=request_context.request_id,
                correlation_id=request_context.correlation_id
            )
            
            # Log successful request
            logging_service.log_info(
                f"API request successful: {request_context.method.value} {request_context.path}",
                log_context,
                {
                    "status_code": response_context.status_code,
                    "response_time": getattr(response_context, 'response_time', None),
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log successful request: {e}")
    
    async def _log_error(self, request_context: RequestContext, user_context, error: Exception, error_response: ErrorResponse):
        """Log error with enhanced logging."""
        try:
            # Get realm-specific logging service
            logging_service = self.di_container.get_realm_logging_service(request_context.realm)
            
            # Create log context
            from ...logging.realm_logging_service_base import LogContext
            log_context = LogContext(
                realm=request_context.realm,
                service_type="api_routing",
                service_name=request_context.pillar or "unknown",
                operation=f"{request_context.method.value} {request_context.path}",
                user_id=getattr(user_context, 'user_id', None),
                tenant_id=getattr(user_context, 'tenant_id', None),
                request_id=request_context.request_id,
                correlation_id=request_context.correlation_id
            )
            
            # Log error
            logging_service.log_error(
                f"API request error: {request_context.method.value} {request_context.path}",
                log_context,
                {
                    "error_code": error_response.error_code,
                    "error_type": error_response.error_type,
                    "severity": error_response.severity.value,
                    "action": error_response.action.value,
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value
                },
                {
                    "traceback": traceback.format_exc(),
                    "error_response": error_response.__dict__
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log error: {e}")
    
    def get_middleware_status(self) -> Dict[str, Any]:
        """Get middleware status and statistics."""
        return {
            "middleware_name": "EnhancedErrorHandlingMiddleware",
            "cached_error_handlers": len(self.error_handler_cache),
            "cache_keys": list(self.error_handler_cache.keys()),
            "middleware_initialized": True,
            "timestamp": datetime.utcnow().isoformat()
        }
