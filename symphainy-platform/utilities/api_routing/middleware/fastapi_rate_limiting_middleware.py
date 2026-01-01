#!/usr/bin/env python3
"""
FastAPI Rate Limiting Middleware

Rate limiting middleware for FastAPI that integrates with platform configuration
and follows the platform's middleware architecture patterns.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status

logger = logging.getLogger("RateLimitingMiddleware")


class FastAPIRateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    
    Integrates with UnifiedConfigurationManager for configuration.
    Uses in-memory storage (can be extended to Redis for distributed deployments).
    """
    
    def __init__(self, app, config_manager=None):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        self.config_manager = config_manager
        self.logger = logger
        
        # Load rate limiting configuration
        self.enabled = self._get_config_bool("RATE_LIMITING_ENABLED", True)
        self.default_requests = self._get_config_int("RATE_LIMIT_REQUESTS", 1000)  # Increased from 100 to 1000
        self.default_window = self._get_config_int("RATE_LIMIT_WINDOW", 3600)  # 1 hour
        
        # Endpoints excluded from rate limiting (read-only operations)
        self.excluded_paths = [
            "/health",
            "/api/health",
            "/api/status",
            "/platform/status",
            "/api/v1/content-pillar/list-uploaded-files",  # Read-only file listing
            "/api/v1/content-pillar/list-parsed-files",  # Read-only parsed file listing
            "/api/v1/content-pillar/get-file-details",  # Read-only file details
            "/api/v1/content-pillar/process-file",  # File processing - exclude from rate limiting during development
        ]
        
        # Request tracking (in-memory, can be extended to Redis)
        self.request_history: Dict[str, deque] = defaultdict(deque)
        
        if self.enabled:
            self.logger.info(f"✅ Rate limiting enabled: {self.default_requests} requests per {self.default_window}s")
            self.logger.info(f"   Excluded paths: {len(self.excluded_paths)} read-only endpoints")
        else:
            self.logger.info("⚠️ Rate limiting disabled")
    
    def _get_config_bool(self, key: str, default: bool) -> bool:
        """Get boolean config value."""
        if not self.config_manager:
            return default
        try:
            return self.config_manager.get_bool(key, default)
        except Exception:
            return default
    
    def _get_config_int(self, key: str, default: int) -> int:
        """Get integer config value."""
        if not self.config_manager:
            return default
        try:
            return self.config_manager.get_int(key, default)
        except Exception:
            return default
    
    async def dispatch(self, request: Request, call_next):
        """Process rate limiting for the request."""
        # Skip rate limiting if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for excluded paths (health checks, read-only endpoints)
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Get user identifier (from auth token or IP)
        user_id = self._get_user_id(request)
        client_ip = request.client.host if request.client else "unknown"
        user_key = f"{user_id}:{client_ip}"
        
        # Check rate limit
        if not self._check_rate_limit(user_key):
            self.logger.warning(f"⚠️ Rate limit exceeded for {user_key}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after": self.default_window
                    }
                },
                headers={"Retry-After": str(self.default_window)}
            )
        
        # Record request
        self._record_request(user_key)
        
        # Continue to next handler
        return await call_next(request)
    
    def _get_user_id(self, request: Request) -> str:
        """Get user ID from request (auth token or anonymous)."""
        # Try to get user ID from auth header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            # Extract user ID from token (simplified - should use proper JWT parsing)
            # In production, extract from JWT token
            return "authenticated"
        
        return "anonymous"
    
    def _check_rate_limit(self, user_key: str) -> bool:
        """Check if request is within rate limit."""
        try:
            current_time = time.time()
            
            # Clean old requests
            self._clean_old_requests(user_key, current_time)
            
            # Check if under limit
            request_count = len(self.request_history[user_key])
            if request_count >= self.default_requests:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Rate limit check failed: {e}")
            return True  # Allow request on error (fail open)
    
    def _clean_old_requests(self, user_key: str, current_time: float):
        """Clean old requests from history."""
        cutoff_time = current_time - self.default_window
        user_history = self.request_history[user_key]
        
        # Remove requests older than the window
        while user_history and user_history[0] < cutoff_time:
            user_history.popleft()
    
    def _record_request(self, user_key: str):
        """Record the request for rate limiting."""
        try:
            # Record request timestamp
            self.request_history[user_key].append(time.time())
        except Exception as e:
            self.logger.error(f"❌ Failed to record request: {e}")

