#!/usr/bin/env python3
"""
CORS Middleware for API Routing

Handles Cross-Origin Resource Sharing for API requests.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class CORSMiddleware:
    """Middleware for Cross-Origin Resource Sharing."""
    
    def __init__(self, di_container):
        """Initialize CORS middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("CORSMiddleware")
        
        # Get configuration from DI container
        self.config = di_container.get_config()
        
        # Load CORS configuration from config
        self.allowed_origins = self._load_cors_origins()
        self.allowed_methods = self._load_cors_methods()
        self.allowed_headers = self._load_cors_headers()
        self.max_age = self._load_cors_max_age()
    
    def _load_cors_origins(self) -> List[str]:
        """Load allowed origins from configuration."""
        try:
            origins = self.config.get_config_value("cors_allowed_origins", [])
            if origins:
                return origins
            
            # Default origins if not configured
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "https://symphainy.com",
            ]
        except Exception as e:
            self.logger.warning(f"Failed to load CORS origins: {e}, using defaults")
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "https://symphainy.com",
            ]
    
    def _load_cors_methods(self) -> List[str]:
        """Load allowed methods from configuration."""
        try:
            methods = self.config.get_config_value("cors_allowed_methods", [])
            if methods:
                return methods
            
            # Default methods if not configured
            return ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        except Exception as e:
            self.logger.warning(f"Failed to load CORS methods: {e}, using defaults")
            return ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    
    def _load_cors_headers(self) -> List[str]:
        """Load allowed headers from configuration."""
        try:
            headers = self.config.get_config_value("cors_allowed_headers", [])
            if headers:
                return headers
            
            # Default headers if not configured
            return [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-API-Key",
                "X-Tenant-ID",
                "X-User-ID"
            ]
        except Exception as e:
            self.logger.warning(f"Failed to load CORS headers: {e}, using defaults")
            return [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-API-Key",
                "X-Tenant-ID",
                "X-User-ID"
            ]
    
    def _load_cors_max_age(self) -> int:
        """Load max age from configuration."""
        try:
            max_age = self.config.get_config_value("cors_max_age", 86400)
            return int(max_age)
        except Exception as e:
            self.logger.warning(f"Failed to load CORS max age: {e}, using default")
            return 86400  # 24 hours
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process CORS for the request."""
        try:
            # Handle preflight OPTIONS request
            if request_context.method.value == "OPTIONS":
                return self._handle_preflight_request(request_context)
            
            # Process regular request
            response_context = await next_handler()
            
            # Add CORS headers to response
            self._add_cors_headers(request_context, response_context)
            
            return response_context
            
        except Exception as e:
            self.logger.error(f"❌ CORS middleware error: {e}")
            # Continue without CORS on error
            return await next_handler()
    
    def _handle_preflight_request(self, request_context: RequestContext) -> ResponseContext:
        """Handle CORS preflight OPTIONS request."""
        origin = request_context.headers.get("Origin", "")
        method = request_context.headers.get("Access-Control-Request-Method", "")
        headers = request_context.headers.get("Access-Control-Request-Headers", "")
        
        # Check if origin is allowed
        if not self._is_origin_allowed(origin):
            return self._create_cors_error_response(request_context, "Origin not allowed")
        
        # Check if method is allowed
        if method and method not in self.allowed_methods:
            return self._create_cors_error_response(request_context, "Method not allowed")
        
        # Check if headers are allowed
        if headers and not self._are_headers_allowed(headers):
            return self._create_cors_error_response(request_context, "Headers not allowed")
        
        # Create preflight response
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=200,
            headers=self._get_cors_headers(origin),
            body={"success": True, "message": "CORS preflight successful"},
            end_time=datetime.utcnow().isoformat()
        )
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        if not origin:
            return False
        
        # Allow all origins in development
        if origin.startswith("http://localhost"):
            return True
        
        # Check against allowed origins
        return origin in self.allowed_origins
    
    def _are_headers_allowed(self, headers: str) -> bool:
        """Check if headers are allowed."""
        if not headers:
            return True
        
        requested_headers = [h.strip().lower() for h in headers.split(",")]
        allowed_headers_lower = [h.lower() for h in self.allowed_headers]
        
        return all(header in allowed_headers_lower for header in requested_headers)
    
    def _add_cors_headers(self, request_context: RequestContext, response_context: ResponseContext):
        """Add CORS headers to response."""
        origin = request_context.headers.get("Origin", "")
        
        if self._is_origin_allowed(origin):
            cors_headers = self._get_cors_headers(origin)
            response_context.headers.update(cors_headers)
    
    def _get_cors_headers(self, origin: str) -> Dict[str, str]:
        """Get CORS headers for response."""
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
            "Access-Control-Max-Age": str(self.max_age),
            "Access-Control-Allow-Credentials": "true"
        }
    
    def _create_cors_error_response(self, request_context: RequestContext, message: str) -> ResponseContext:
        """Create CORS error response."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=403,
            headers=self._get_cors_headers(request_context.headers.get("Origin", "")),
            body={
                "success": False,
                "error": {
                    "code": "CORS_ERROR",
                    "message": message,
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            end_time=datetime.utcnow().isoformat()
        )
