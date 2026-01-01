#!/usr/bin/env python3
"""
Enhanced Logging Middleware

Enhanced logging middleware for API routing with realm-specific and service type-specific logging.
Integrates with the new logging infrastructure for comprehensive request/response logging.

WHAT (Utility Role): I provide enhanced logging for API routing
HOW (Utility Implementation): I integrate realm-specific and service type-specific logging with API routing
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

from ...logging.logging_service_factory import get_logging_service_factory
from ...logging.service_type_logging_service import ServiceTypeLoggingService, ServiceType as LoggingServiceType
from ...logging.realm_logging_service_base import LogContext, LogLevel, LogCategory
from ..api_routing_utility import RequestContext, ResponseContext
from ..middleware_protocol import Middleware


class EnhancedLoggingMiddleware:
    """
    Enhanced logging middleware for API routing.
    
    Integrates realm-specific and service type-specific logging
    with API routing for comprehensive request/response logging.
    """
    
    def __init__(self, di_container):
        """Initialize enhanced logging middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("EnhancedLoggingMiddleware")
        
        # Get logging service factory
        self.logging_service_factory = get_logging_service_factory()
        
        # Cache for logging services by realm and service type
        self.logging_service_cache: Dict[str, ServiceTypeLoggingService] = {}
        
        # Request tracking
        self.request_count = 0
        self.request_times: Dict[str, float] = {}
        
        self.logger.info("✅ Enhanced Logging Middleware initialized")
    
    async def __call__(self, request_context: RequestContext, user_context, next_handler: Callable) -> ResponseContext:
        """
        Execute enhanced logging middleware.
        
        Args:
            request_context: The request context
            user_context: The user context
            next_handler: The next handler in the chain
            
        Returns:
            ResponseContext: The response context
        """
        # Start timing
        start_time = time.time()
        request_id = request_context.request_id or str(uuid.uuid4())
        request_context.request_id = request_id
        
        # Log request start
        await self._log_request_start(request_context, user_context)
        
        try:
            # Execute the next handler
            response_context = await next_handler()
            
            # Calculate response time
            response_time = time.time() - start_time
            response_context.response_time = response_time
            
            # Log request success
            await self._log_request_success(request_context, response_context, user_context, response_time)
            
            return response_context
            
        except Exception as error:
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log request error
            await self._log_request_error(request_context, user_context, error, response_time)
            
            # Re-raise the error for error handling middleware
            raise
    
    async def _log_request_start(self, request_context: RequestContext, user_context):
        """Log request start."""
        try:
            # Determine service type
            service_type = self._determine_service_type(request_context)
            
            # Get or create logging service
            logging_service = await self._get_logging_service(request_context.realm, service_type)
            
            # Create log context
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
            
            # Log request start
            logging_service.log_service_operation(
                f"API request started: {request_context.method.value} {request_context.path}",
                log_context,
                service_type,
                "api_request_start",
                {
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value,
                    "realm": request_context.realm,
                    "pillar": request_context.pillar,
                    "user_agent": request_context.headers.get("User-Agent"),
                    "content_type": request_context.headers.get("Content-Type"),
                    "request_size": len(str(request_context.body or {}))
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log request start: {e}")
    
    async def _log_request_success(self, request_context: RequestContext, response_context: ResponseContext, 
                                 user_context, response_time: float):
        """Log request success."""
        try:
            # Determine service type
            service_type = self._determine_service_type(request_context)
            
            # Get or create logging service
            logging_service = await self._get_logging_service(request_context.realm, service_type)
            
            # Create log context
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
            
            # Log request success
            logging_service.log_service_operation(
                f"API request successful: {request_context.method.value} {request_context.path}",
                log_context,
                service_type,
                "api_request_success",
                {
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value,
                    "status_code": response_context.status_code,
                    "response_time": response_time,
                    "response_size": len(str(response_context.body or {})),
                    "realm": request_context.realm,
                    "pillar": request_context.pillar
                }
            )
            
            # Log performance metric
            logging_service.log_performance_metric(
                log_context,
                service_type,
                "api_response_time",
                response_time,
                "seconds",
                {
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value,
                    "status_code": response_context.status_code
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log request success: {e}")
    
    async def _log_request_error(self, request_context: RequestContext, user_context, error: Exception, response_time: float):
        """Log request error."""
        try:
            # Determine service type
            service_type = self._determine_service_type(request_context)
            
            # Get or create logging service
            logging_service = await self._get_logging_service(request_context.realm, service_type)
            
            # Create log context
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
            
            # Log request error
            logging_service.log_service_error(
                log_context,
                service_type,
                request_context.pillar or "unknown",
                error,
                {
                    "api_endpoint": request_context.path,
                    "http_method": request_context.method.value,
                    "response_time": response_time,
                    "realm": request_context.realm,
                    "pillar": request_context.pillar
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to log request error: {e}")
    
    def _determine_service_type(self, request_context: RequestContext) -> LoggingServiceType:
        """Determine service type from request context."""
        # Check if it's an MCP server request
        if request_context.path.startswith("/mcp/") or "mcp" in request_context.pillar.lower():
            return LoggingServiceType.MCP_SERVER
        
        # Check if it's a foundation service
        if "foundation" in request_context.realm.lower():
            return LoggingServiceType.FOUNDATION_SERVICE
        
        # Check if it's an agent request
        if "agent" in request_context.pillar.lower() or "agent" in request_context.path:
            return LoggingServiceType.AGENT
        
        # Default to service
        return LoggingServiceType.SERVICE
    
    async def _get_logging_service(self, realm: str, service_type: LoggingServiceType) -> ServiceTypeLoggingService:
        """Get or create logging service for realm and service type."""
        cache_key = f"{realm}:{service_type.value}"
        
        if cache_key not in self.logging_service_cache:
            # Get realm-specific logging service
            realm_logging_service = self.logging_service_factory.get_logging_service(realm)
            
            # Create service type-specific logging service
            logging_service = ServiceTypeLoggingService(realm_logging_service)
            
            # Cache the logging service
            self.logging_service_cache[cache_key] = logging_service
            
            self.logger.debug(f"✅ Created logging service for {cache_key}")
        
        return self.logging_service_cache[cache_key]
    
    def get_middleware_status(self) -> Dict[str, Any]:
        """Get middleware status and statistics."""
        return {
            "middleware_name": "EnhancedLoggingMiddleware",
            "cached_logging_services": len(self.logging_service_cache),
            "cache_keys": list(self.logging_service_cache.keys()),
            "request_count": self.request_count,
            "middleware_initialized": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.request_times:
            return {
                "total_requests": 0,
                "average_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0
            }
        
        response_times = list(self.request_times.values())
        return {
            "total_requests": len(response_times),
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times)
        }
