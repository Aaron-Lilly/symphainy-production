#!/usr/bin/env python3
"""
LLM Rate Limiting Abstraction

Infrastructure abstraction for LLM request rate limiting.
Implements LLMRateLimitingProtocol using RateLimitingAdapter.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import time
import logging

from ..abstraction_contracts.llm_rate_limiting_protocol import (
    LLMRateLimitingProtocol, RateLimitRequest, RateLimitResponse, RateLimitStats
)
from ..infrastructure_adapters.rate_limiting_adapter import RateLimitingAdapter

class LLMRateLimitingAbstraction(LLMRateLimitingProtocol):
    """LLM rate limiting abstraction using rate limiting adapter."""
    
    def __init__(self, rate_limiting_adapter: RateLimitingAdapter, di_container=None, **kwargs):
        """
        Initialize LLM rate limiting abstraction.
        
        Args:
            rate_limiting_adapter: Rate limiting adapter instance
            di_container: DI Container for utilities (optional)
        """
        self.rate_limiting = rate_limiting_adapter
        self.di_container = di_container
        self.service_name = "llm_rate_limiting_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("LLMRateLimitingAbstraction")
        
        # Rate limiting configuration
        self.requests_per_minute = kwargs.get("requests_per_minute", 60)
        self.requests_per_hour = kwargs.get("requests_per_hour", 1000)
        self.tokens_per_minute = kwargs.get("tokens_per_minute", 100000)
        self.tokens_per_hour = kwargs.get("tokens_per_hour", 1000000)
        self.enabled = kwargs.get("enabled", True)
        
        # Rate limiting statistics
        self.stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "rate_limit_hits": 0
        }
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the LLM rate limiting abstraction."""
        try:
            self.logger.info("✅ LLM rate limiting abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM rate limiting abstraction: {e}")
            raise  # Re-raise for service layer to handle

        """Generate rate limiting key for request."""
        return f"rate_limit:requests:{user_id}:{model}:{window}"
    
    def _get_token_key(self, user_id: str, model: str, window: str) -> str:
        """Generate rate limiting key for tokens."""
        return f"rate_limit:tokens:{user_id}:{model}:{window}"
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResponse:
        """
        Check if request is within rate limits.
        
        Args:
            request: Rate limit request
            
        Returns:
            RateLimitResponse: Rate limit response
        """
        try:
            if not self.enabled:
                return RateLimitResponse(
                    allowed=True,
                    reason="rate_limiting_disabled",
                    retry_after=0,
                    current_requests=0,
                    current_tokens=0,
                    request_limit=self.requests_per_minute,
                    token_limit=self.tokens_per_minute
                )
            
            self.stats["total_requests"] += 1
            
            # Check request rate limits
            request_allowed = await self._check_request_rate_limit(request)
            if not request_allowed["allowed"]:
                self.stats["blocked_requests"] += 1
                self.stats["rate_limit_hits"] += 1
                return RateLimitResponse(
                    allowed=False,
                    reason=request_allowed["reason"],
                    retry_after=request_allowed["retry_after"],
                    current_requests=request_allowed["current_requests"],
                    current_tokens=0,
                    request_limit=self.requests_per_minute,
                    token_limit=self.tokens_per_minute
                )
            
            # Check token rate limits
            token_allowed = await self._check_token_rate_limit(request)
            if not token_allowed["allowed"]:
                self.stats["blocked_requests"] += 1
                self.stats["rate_limit_hits"] += 1
                return RateLimitResponse(
                    allowed=False,
                    reason=token_allowed["reason"],
                    retry_after=token_allowed["retry_after"],
                    current_requests=request_allowed["current_requests"],
                    current_tokens=token_allowed["current_tokens"],
                    request_limit=self.requests_per_minute,
                    token_limit=self.tokens_per_minute
                )
            
            # Record the request
            await self._record_request(request)
            
            self.stats["allowed_requests"] += 1
            
            response = RateLimitResponse(
                allowed=True,
                reason="within_limits",
                retry_after=0,
                current_requests=request_allowed["current_requests"] + 1,
                current_tokens=token_allowed["current_tokens"] + request.estimated_tokens,
                request_limit=self.requests_per_minute,
                token_limit=self.tokens_per_minute
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to check rate limit: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _check_request_rate_limit(self, request: RateLimitRequest) -> Dict[str, Any]:
        """Check request rate limits."""
        try:
            # Check per-minute limits
            minute_key = self._get_request_key(request.user_id, request.model, "minute")
            current_requests = await self.rate_limiting.get_counter(minute_key)
            
            if current_requests >= self.requests_per_minute:
                return {
                    "allowed": False,
                    "reason": "request_rate_limit_exceeded",
                    "retry_after": 60,  # 1 minute
                    "current_requests": current_requests
                }
            
            # Check per-hour limits
            hour_key = self._get_request_key(request.user_id, request.model, "hour")
            current_hourly_requests = await self.rate_limiting.get_counter(hour_key)
            
            if current_hourly_requests >= self.requests_per_hour:
                return {
                    "allowed": False,
                    "reason": "hourly_request_rate_limit_exceeded",
                    "retry_after": 3600,  # 1 hour
                    "current_requests": current_hourly_requests
                }
            
            return {
                "allowed": True,
                "current_requests": current_requests
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check request rate limit: {e}")
    
            raise  # Re-raise for service layer to handle

        """Check token rate limits."""
        try:
            # Check per-minute token limits
            minute_key = self._get_token_key(request.user_id, request.model, "minute")
            current_tokens = await self.rate_limiting.get_counter(minute_key)
            
            if current_tokens + request.estimated_tokens > self.tokens_per_minute:
                return {
                    "allowed": False,
                    "reason": "token_rate_limit_exceeded",
                    "retry_after": 60,  # 1 minute
                    "current_tokens": current_tokens
                }
            
            # Check per-hour token limits
            hour_key = self._get_token_key(request.user_id, request.model, "hour")
            current_hourly_tokens = await self.rate_limiting.get_counter(hour_key)
            
            if current_hourly_tokens + request.estimated_tokens > self.tokens_per_hour:
                return {
                    "allowed": False,
                    "reason": "hourly_token_rate_limit_exceeded",
                    "retry_after": 3600,  # 1 hour
                    "current_tokens": current_hourly_tokens
                }
            
            return {
                "allowed": True,
                "current_tokens": current_tokens
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check token rate limit: {e}")
    
            raise  # Re-raise for service layer to handle

        """Record request in rate limiting counters."""
        try:
            # Record per-minute request
            minute_request_key = self._get_request_key(request.user_id, request.model, "minute")
            await self.rate_limiting.increment_counter(minute_request_key, 60)
            
            # Record per-hour request
            hour_request_key = self._get_request_key(request.user_id, request.model, "hour")
            await self.rate_limiting.increment_counter(hour_request_key, 3600)
            
            # Record per-minute tokens
            minute_token_key = self._get_token_key(request.user_id, request.model, "minute")
            await self.rate_limiting.increment_counter(minute_token_key, 60)
            
            # Record per-hour tokens
            hour_token_key = self._get_token_key(request.user_id, request.model, "hour")
            await self.rate_limiting.increment_counter(hour_token_key, 3600)
            
        except Exception as e:
            self.logger.error(f"Failed to record request: {e}")
    
            raise  # Re-raise for service layer to handle

        """
        Get current rate limit status for user and model.
        
        Args:
            user_id: User ID
            model: Model name
            
        Returns:
            Dict: Rate limit status
        """
        try:
            # Get current counters
            minute_request_key = self._get_request_key(user_id, model, "minute")
            hour_request_key = self._get_request_key(user_id, model, "hour")
            minute_token_key = self._get_token_key(user_id, model, "minute")
            hour_token_key = self._get_token_key(user_id, model, "hour")
            
            current_minute_requests = await self.rate_limiting.get_counter(minute_request_key)
            current_hour_requests = await self.rate_limiting.get_counter(hour_request_key)
            current_minute_tokens = await self.rate_limiting.get_counter(minute_token_key)
            current_hour_tokens = await self.rate_limiting.get_counter(hour_token_key)
            
            status = {
                "user_id": user_id,
                "model": model,
                "current_minute_requests": current_minute_requests,
                "minute_request_limit": self.requests_per_minute,
                "current_hour_requests": current_hour_requests,
                "hour_request_limit": self.requests_per_hour,
                "current_minute_tokens": current_minute_tokens,
                "minute_token_limit": self.tokens_per_minute,
                "current_hour_tokens": current_hour_tokens,
                "hour_token_limit": self.tokens_per_hour,
                "minute_request_usage_percent": (current_minute_requests / self.requests_per_minute) * 100,
                "hour_request_usage_percent": (current_hour_requests / self.requests_per_hour) * 100,
                "minute_token_usage_percent": (current_minute_tokens / self.tokens_per_minute) * 100,
                "hour_token_usage_percent": (current_hour_tokens / self.tokens_per_hour) * 100
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get rate limit status: {e}")
            raise  # Re-raise for service layer to handle

        """
        Reset rate limits for user and model.
        
        Args:
            user_id: User ID
            model: Model name (None for all models)
            
        Returns:
            bool: Success status
        """
        try:
            if model:
                # Reset specific model
                keys_to_reset = [
                    self._get_request_key(user_id, model, "minute"),
                    self._get_request_key(user_id, model, "hour"),
                    self._get_token_key(user_id, model, "minute"),
                    self._get_token_key(user_id, model, "hour")
                ]
            else:
                # Reset all models (would need to enumerate all possible models)
                # For now, just reset common models
                common_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                keys_to_reset = []
                for m in common_models:
                    keys_to_reset.extend([
                        self._get_request_key(user_id, m, "minute"),
                        self._get_request_key(user_id, m, "hour"),
                        self._get_token_key(user_id, m, "minute"),
                        self._get_token_key(user_id, m, "hour")
                    ])
            
            # Delete all keys
            for key in keys_to_reset:
                await self.rate_limiting.delete_counter(key)
            
            self.logger.info(f"Rate limits reset for user: {user_id}, model: {model or 'all'}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset limits for user {user_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get overall rate limiting statistics.
        
        Returns:
            RateLimitStats: Rate limiting statistics
        """
        try:
            total_requests = self.stats["total_requests"]
            allowed_requests = self.stats["allowed_requests"]
            blocked_requests = self.stats["blocked_requests"]
            
            success_rate = 0.0
            if total_requests > 0:
                success_rate = (allowed_requests / total_requests) * 100
            
            stats = RateLimitStats(
                total_requests=total_requests,
                allowed_requests=allowed_requests,
                blocked_requests=blocked_requests,
                success_rate=success_rate,
                rate_limit_hits=self.stats["rate_limit_hits"],
                requests_per_minute_limit=self.requests_per_minute,
                tokens_per_minute_limit=self.tokens_per_minute,
                enabled=self.enabled,
                timestamp=datetime.now()
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get rate limit stats: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Get rate limiting adapter health
            adapter_health = await self.rate_limiting.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "rate_limiting_adapter": adapter_health,
                "abstraction": {
                    "enabled": self.enabled,
                    "requests_per_minute": self.requests_per_minute,
                    "tokens_per_minute": self.tokens_per_minute
                },
                "statistics": self.stats,
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

            raise  # Re-raise for service layer to handle
