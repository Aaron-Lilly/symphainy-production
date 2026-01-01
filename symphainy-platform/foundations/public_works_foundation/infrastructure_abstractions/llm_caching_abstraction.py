#!/usr/bin/env python3
"""
LLM Caching Abstraction

Infrastructure abstraction for LLM response caching.
Implements LLMCachingProtocol using CacheAdapter.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib
import json
import uuid

from ..abstraction_contracts.llm_caching_protocol import (
    LLMCachingProtocol, CacheRequest, CacheResponse, CacheStats
)
from ..infrastructure_adapters.cache_adapter import CacheAdapter

class LLMCachingAbstraction(LLMCachingProtocol):
    """LLM caching abstraction using cache adapter."""
    
    def __init__(self, cache_adapter: CacheAdapter, di_container=None, **kwargs):
        """
        Initialize LLM caching abstraction.
        
        Args:
            cache_adapter: Cache adapter instance
            di_container: DI Container for utilities (optional)
        """
        self.cache_adapter = cache_adapter
        self.di_container = di_container
        self.service_name = "llm_caching_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("LLMCachingAbstraction")
        
        # Caching configuration
        self.default_ttl = kwargs.get("default_ttl", 3600)
        self.enabled = kwargs.get("enabled", True)
        self.cache_prefix = kwargs.get("cache_prefix", "llm_cache")
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the LLM caching abstraction."""
        try:
            self.logger.info("✅ LLM caching abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM caching abstraction: {e}")
            raise  # Re-raise for service layer to handle

        """Generate cache key for request."""
        try:
            # Create hash of request parameters
            key_data = {
                "prompt": request.prompt,
                "model": request.model,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "parameters": request.parameters or {}
            }
            
            key_string = json.dumps(key_data, sort_keys=True)
            key_hash = hashlib.sha256(key_string.encode()).hexdigest()
            
            return f"{self.cache_prefix}:{key_hash}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate cache key: {e}")
            # Fallback to simple hash
    
            raise  # Re-raise for service layer to handle
    
    async def get_cached_response(self, request: CacheRequest) -> Optional[CacheResponse]:
        """
        Get cached response for request.
        
        Args:
            request: Cache request
            
        Returns:
            Optional[CacheResponse]: Cached response if found
        """
        try:
            if not self.enabled:
                return None
            
            cache_key = self._generate_cache_key(request)
            
            # Get from cache
            cached_data = await self.cache_adapter.get(cache_key)
            
            if cached_data:
                # Check if cache entry is still valid
                if self._is_cache_valid(cached_data):
                    self.stats["hits"] += 1
                    self.stats["total_requests"] += 1
                    
                    response = CacheResponse(
                        response_id=cached_data["response_id"],
                        content=cached_data["content"],
                        model=cached_data["model"],
                        usage=cached_data["usage"],
                        timestamp=cached_data["timestamp"],
                        cached=True
                    )
                    
                    return response
                else:
                    # Cache expired, remove it
                    await self.cache_adapter.delete(cache_key)
                    self.stats["evictions"] += 1
            
            self.stats["misses"] += 1
            self.stats["total_requests"] += 1
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get cached response: {e}")
            raise  # Re-raise for service layer to handle

        """
        Cache response for future use.
        
        Args:
            request: Cache request
            response: Response to cache
            ttl: Time to live in seconds
            
        Returns:
            bool: Success status
        """
    async def store_response(self, request: CacheRequest, response: CacheResponse, ttl: int = None) -> bool:
        """Store response in cache."""
        try:
                if not self.enabled:
                    return False
                
                cache_key = self._generate_cache_key(request)
                
                # Prepare cache data
                cache_data = {
                    "response_id": response.response_id,
                    "content": response.content,
                    "model": response.model,
                    "usage": response.usage,
                    "timestamp": response.timestamp.isoformat(),
                    "ttl": ttl or self.default_ttl,
                    "cached_at": datetime.now().isoformat()
                }
                
                # Store in cache
                success = await self.cache_adapter.set(cache_key, cache_data, ttl or self.default_ttl)
                
                if success:
                    self.logger.debug(f"Response cached with key: {cache_key}")
                
                return success
            
        except Exception as e:
            self.logger.error(f"Failed to cache response: {e}")
            raise  # Re-raise for service layer to handle

        """Check if cached data is still valid."""
        try:
            timestamp = datetime.fromisoformat(cached_data["timestamp"])
            ttl = cached_data.get("ttl", self.default_ttl)
            expiry_time = timestamp + timedelta(seconds=ttl)
            
            return datetime.now() < expiry_time
            
        except Exception as e:
            self.logger.error(f"Failed to validate cache entry: {e}")
            raise  # Re-raise for service layer to handle

        """
        Invalidate cache entry for request.
        
        Args:
            request: Cache request
            
        Returns:
            bool: Success status
        """
        try:
            cache_key = self._generate_cache_key(request)
            success = await self.cache_adapter.delete(cache_key)
            
            if success:
                self.logger.info(f"Cache invalidated for key: {cache_key}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Clear all cache entries.
        
        Returns:
            bool: Success status
        """
        try:
            success = await self.cache_adapter.clear()
            
            if success:
                # Reset statistics
                self.stats = {
                    "hits": 0,
                    "misses": 0,
                    "evictions": 0,
                    "total_requests": 0
                }
                
                self.logger.info("Cache cleared successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get cache statistics.
        
        Returns:
            CacheStats: Cache statistics
        """
        try:
            hit_rate = 0.0
            if self.stats["total_requests"] > 0:
                hit_rate = self.stats["hits"] / self.stats["total_requests"]
            
            stats = CacheStats(
                hits=self.stats["hits"],
                misses=self.stats["misses"],
                evictions=self.stats["evictions"],
                total_requests=self.stats["total_requests"],
                hit_rate=hit_rate,
                enabled=self.enabled,
                timestamp=datetime.now()
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get cache stats: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Get cache adapter health
            adapter_health = await self.cache_adapter.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "cache_adapter": adapter_health,
                "abstraction": {
                    "enabled": self.enabled,
                    "default_ttl": self.default_ttl,
                    "cache_prefix": self.cache_prefix
                },
                "statistics": self.stats,
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

            raise  # Re-raise for service layer to handle
