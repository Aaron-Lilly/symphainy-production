#!/usr/bin/env python3
"""
LLM Rate Limiting Protocol

Protocol definition for LLM rate limiting infrastructure abstractions.
"""

from typing import Protocol
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class RateLimitRequest:
    """Rate limit request definition."""
    user_id: str
    model: str
    estimated_tokens: int = 0


@dataclass
class RateLimitResponse:
    """Rate limit response definition."""
    allowed: bool
    reason: str
    retry_after: int
    current_requests: int
    current_tokens: int
    request_limit: int
    token_limit: int


@dataclass
class RateLimitStats:
    """Rate limit statistics definition."""
    total_requests: int
    allowed_requests: int
    blocked_requests: int
    success_rate: float
    rate_limit_hits: int
    requests_per_minute_limit: int
    tokens_per_minute_limit: int
    enabled: bool
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


class LLMRateLimitingProtocol(Protocol):
    """Protocol for LLM rate limiting infrastructure abstractions."""
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResponse:
        """Check if request is within rate limits."""
        ...
    
    async def get_rate_limit_status(self, user_id: str, model: str) -> Dict[str, Any]:
        """Get current rate limit status for user and model."""
        ...
    
    async def reset_user_limits(self, user_id: str, model: str = None) -> bool:
        """Reset rate limits for user and model."""
        ...
    
    async def get_rate_limit_stats(self) -> RateLimitStats:
        """Get overall rate limiting statistics."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        ...




