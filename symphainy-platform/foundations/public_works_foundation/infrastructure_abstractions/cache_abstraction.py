#!/usr/bin/env python3
"""
Cache Abstraction - Generic Infrastructure Implementation

Generic cache implementation for content/data caching (NOT messaging).
Swappable backends: Redis, Memcached, In-Memory, File-based.

WHAT (Infrastructure Role): I provide generic cache services for performance optimization
HOW (Infrastructure Implementation): I use CacheAdapter with swappable backends

**Architectural Distinction:**
- Cache Abstraction: For content/data caching (this file)
- Messaging Abstraction: For platform communication (Post Office's domain)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.cache_protocol import CacheProtocol
from foundations.public_works_foundation.infrastructure_adapters.cache_adapter import CacheAdapter
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter

logger = logging.getLogger(__name__)

class CacheAbstraction(CacheProtocol):
    """
    Generic cache abstraction for content/data caching.
    
    This abstraction implements the CacheProtocol using CacheAdapter,
    providing a generic interface for caching with swappable backends.
    
    **Use Cases:**
    - Content Steward: Cache file processing results
    - Data Steward: Cache validation results  
    - LLM Services: Cache API responses
    - Analytics: Cache computed metrics
    
    **Swappable Backends:**
    - Redis (production)
    - Memcached (production)
    - In-Memory (development/testing)
    - File-based (development/testing)
    """

    def __init__(self, cache_adapter: CacheAdapter, config_adapter: ConfigAdapter, di_container=None):
        """
        Initialize Cache abstraction with real adapters.
        
        Args:
            cache_adapter: Cache adapter
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.cache_adapter = cache_adapter
        self.config = config_adapter
        self.di_container = di_container
        self.service_name = "cache_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)

        # Cache configuration
        self.default_ttl = 3600  # 1 hour default
        self.max_key_length = 250

        self.logger.info(f"✅ Cache abstraction initialized with {cache_adapter.storage_type} backend")

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache.
        """
        try:
            value = await self.cache_adapter.get(key)
            if value:
                self.logger.debug(f"✅ Cache hit: {key}")
            else:
                self.logger.debug(f"⚠️ Cache miss: {key}")
            return value
        except Exception as e:
            self.logger.error(f"❌ Error getting from cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Set value in cache with optional TTL.
        """
        try:
            # Validate key length
            if len(key) > self.max_key_length:
                self.logger.warning(f"⚠️ Key too long (truncating): {key[:50]}...")
                key = key[:self.max_key_length]
            
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.default_ttl
            
            success = await self.cache_adapter.set(key, value, ttl)
            if success:
                self.logger.debug(f"✅ Cached: {key} (TTL: {ttl}s)")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error setting in cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Set value in cache (alias for backward compatibility).
        
        This method wraps non-dict values in a dict for storage.
        """
        try:
            # If value is not a dict, wrap it
            if not isinstance(value, dict):
                value = {"value": value, "cached_at": datetime.utcnow().isoformat()}
            
            return await self.set(key, value, ttl)
        except Exception as e:
            self.logger.error(f"❌ Error setting value in cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Delete value from cache.
        """
        try:
            success = await self.cache_adapter.delete(key)
            if success:
                self.logger.debug(f"✅ Deleted from cache: {key}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error deleting from cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Check if key exists in cache.
        """
        try:
            return await self.cache_adapter.exists(key)
        except Exception as e:
            self.logger.error(f"❌ Error checking cache existence: {e}")
            raise  # Re-raise for service layer to handle

        """
        Clear all cache entries.
        """
        try:
            success = await self.cache_adapter.clear()
            if success:
                self.logger.info("✅ Cache cleared")
                
            return success
        except Exception as e:
            self.logger.error(f"❌ Error clearing cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get multiple values from cache.
        """
        try:
            result = {}
            for key in keys:
                value = await self.get(key)
                if value is not None:
                    result[key] = value
            return result
        except Exception as e:
            self.logger.error(f"❌ Error getting many from cache: {e}")

            raise  # Re-raise for service layer to handle

    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.
        """
        try:
            success = True
            for key, value in items.items():
                if not await self.set(key, value, ttl):
                    success = False
            return success
        except Exception as e:
            self.logger.error(f"❌ Error setting many in cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Increment a numeric value in cache.
        """
        try:
            # Get current value
            current = await self.get(key)
            if current is None:
                # Initialize to amount
                await self.set(key, {"value": amount}, None)
                return amount
            
            # Increment
            current_value = current.get("value", 0)
            new_value = current_value + amount
            await self.set(key, {"value": new_value}, None)
            return new_value
        except Exception as e:
            self.logger.error(f"❌ Error incrementing in cache: {e}")
            raise  # Re-raise for service layer to handle

        """
        Decrement a numeric value in cache.
        """
        return await self.increment(key, -amount)

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache backend.
        """
        try:
            adapter_health = await self.cache_adapter.health_check()
            
            return {
                "healthy": adapter_health.get("healthy", False),
                "backend": self.cache_adapter.storage_type,
                "storage_connected": adapter_health.get("storage_connected", False),
                "timestamp": datetime.utcnow().isoformat(),
                "adapter_health": adapter_health
            }
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
