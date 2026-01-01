#!/usr/bin/env python3
"""
Rate Limiting Middleware for API Routing

Handles rate limiting for API requests across all realms.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from ..api_routing_utility import Middleware, RequestContext, ResponseContext
from utilities import UserContext


class RateLimitingMiddleware:
    """Middleware for API request rate limiting."""
    
    def __init__(self, di_container):
        """Initialize rate limiting middleware."""
        self.di_container = di_container
        self.logger = logging.getLogger("RateLimitingMiddleware")
        
        # Get configuration from DI container
        self.config = di_container.get_config()
        
        # Load rate limiting configuration from config
        self.rate_limits = self._load_rate_limit_config()
        
        # Request tracking
        self.request_history: Dict[str, deque] = defaultdict(deque)
        self.user_limits: Dict[str, Dict[str, Any]] = {}
    
    def _load_rate_limit_config(self) -> Dict[str, Dict[str, int]]:
        """Load rate limiting configuration from config service."""
        try:
            # Get rate limiting configuration from config
            rate_limit_config = self.config.get_config_value("api_rate_limits", {})
            
            # Default configuration if not found in config
            default_config = {
                "default": {"requests": 100, "window": 60},
                "content_pillar": {"requests": 50, "window": 60},
                "metadata_extraction": {"requests": 10, "window": 60},
            }
            
            # Merge config with defaults
            return {**default_config, **rate_limit_config}
            
        except Exception as e:
            self.logger.warning(f"Failed to load rate limit config: {e}, using defaults")
            return {
                "default": {"requests": 100, "window": 60},
                "content_pillar": {"requests": 50, "window": 60},
                "metadata_extraction": {"requests": 10, "window": 60},
            }
    
    async def __call__(
        self,
        request_context: RequestContext,
        user_context: UserContext,
        next_handler: callable
    ) -> ResponseContext:
        """Process rate limiting for the request."""
        try:
            # Check if rate limiting is required
            if not self._requires_rate_limiting(request_context):
                return await next_handler()
            
            # Check rate limit
            if not await self._check_rate_limit(request_context, user_context):
                return self._create_rate_limit_response(request_context)
            
            # Record request
            await self._record_request(request_context, user_context)
            
            # Continue to next handler
            return await next_handler()
            
        except Exception as e:
            self.logger.error(f"❌ Rate limiting middleware error: {e}")
            # Allow request on error (fail open)
            return await next_handler()
    
    def _requires_rate_limiting(self, request_context: RequestContext) -> bool:
        """Check if the request requires rate limiting."""
        # Skip rate limiting for health checks
        health_paths = ["/health", "/api/health", "/api/status"]
        return not any(request_context.path.startswith(path) for path in health_paths)
    
    async def _check_rate_limit(self, request_context: RequestContext, user_context: UserContext) -> bool:
        """Check if request is within rate limit."""
        try:
            # Get rate limit configuration
            rate_limit = self._get_rate_limit_config(request_context)
            
            # Get user identifier
            user_id = user_context.user_id if user_context else "anonymous"
            tenant_id = user_context.tenant_id if user_context else "default"
            user_key = f"{tenant_id}:{user_id}"
            
            # Get current time
            current_time = time.time()
            
            # Clean old requests
            self._clean_old_requests(user_key, current_time, rate_limit["window"])
            
            # Check if under limit
            request_count = len(self.request_history[user_key])
            if request_count >= rate_limit["requests"]:
                self.logger.warning(f"⚠️ Rate limit exceeded for user {user_key}: {request_count}/{rate_limit['requests']}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Rate limit check failed: {e}")
            return True  # Allow request on error
    
    def _get_rate_limit_config(self, request_context: RequestContext) -> Dict[str, int]:
        """Get rate limit configuration for the request."""
        # Check for pillar-specific limits
        if "/api/content/" in request_context.path:
            if "/metadata" in request_context.path:
                return self.rate_limits["metadata_extraction"]
            return self.rate_limits["content_pillar"]
        
        # Return default limit
        return self.rate_limits["default"]
    
    def _clean_old_requests(self, user_key: str, current_time: float, window_seconds: int):
        """Clean old requests from history."""
        cutoff_time = current_time - window_seconds
        user_history = self.request_history[user_key]
        
        # Remove requests older than the window
        while user_history and user_history[0] < cutoff_time:
            user_history.popleft()
    
    async def _record_request(self, request_context: RequestContext, user_context: UserContext):
        """Record the request for rate limiting."""
        try:
            user_id = user_context.user_id if user_context else "anonymous"
            tenant_id = user_context.tenant_id if user_context else "default"
            user_key = f"{tenant_id}:{user_id}"
            
            # Record request timestamp
            self.request_history[user_key].append(time.time())
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record request: {e}")
    
    def _create_rate_limit_response(self, request_context: RequestContext) -> ResponseContext:
        """Create rate limit exceeded response."""
        return ResponseContext(
            request_id=request_context.request_id,
            status_code=429,
            body={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Please try again later.",
                    "request_id": request_context.request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "retry_after": 60  # seconds
                }
            },
            end_time=datetime.utcnow().isoformat()
        )
