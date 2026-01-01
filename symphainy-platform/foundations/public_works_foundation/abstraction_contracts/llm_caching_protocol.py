#!/usr/bin/env python3
"""
LLM Caching Protocol

Protocol definition for LLM caching infrastructure abstractions.
"""

from typing import Protocol, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CacheRequest:
    """Cache request definition."""
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class CacheResponse:
    """Cache response definition."""
    response_id: str
    content: str
    model: str
    usage: Dict[str, Any]
    timestamp: datetime
    cached: bool = False


@dataclass
class CacheStats:
    """Cache statistics definition."""
    hits: int
    misses: int
    evictions: int
    total_requests: int
    hit_rate: float
    enabled: bool
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


class LLMCachingProtocol(Protocol):
    """Protocol for LLM caching infrastructure abstractions."""
    
    async def get_cached_response(self, request: CacheRequest) -> Optional[CacheResponse]:
        """Get cached response for request."""
        ...
    
    async def cache_response(self, request: CacheRequest, response: CacheResponse, 
                           ttl: Optional[int] = None) -> bool:
        """Cache response for future use."""
        ...
    
    async def invalidate_cache(self, request: CacheRequest) -> bool:
        """Invalidate cache entry for request."""
        ...
    
    async def clear_cache(self) -> bool:
        """Clear all cache entries."""
        ...
    
    async def get_cache_stats(self) -> CacheStats:
        """Get cache statistics."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        ...




