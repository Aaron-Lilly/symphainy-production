#!/usr/bin/env python3
"""
Cache Protocol - Infrastructure Contract

Defines the contract for cache operations (Redis/Memcached/etc).
This is for content/data caching, NOT platform messaging (which is Post Office's domain).

WHAT (Infrastructure Contract): I define cache operations for performance optimization
HOW (Protocol): I specify the interface for swappable cache backends (Redis, Memcached, etc.)
"""

from typing import Dict, Any, Optional, Protocol
from datetime import datetime


class CacheProtocol(Protocol):
    """
    Cache Protocol - Infrastructure Contract
    
    Defines cache operations for content and data caching.
    Swappable backends: Redis, Memcached, In-Memory, File-based
    
    **Architectural Distinction:**
    - Cache Abstraction: For content/data caching (performance optimization)
    - Messaging Abstraction: For platform communication (Post Office's domain)
    
    **Use Cases:**
    - Content Steward: Cache file processing results
    - Data Steward: Cache validation results
    - LLM Services: Cache API responses
    - Analytics: Cache computed metrics
    
    **NOT For:**
    - Inter-service messaging (use Post Office)
    - Event routing (use Post Office)
    - Pub/sub patterns (use Post Office)
    """
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        ...
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = no expiration)
            
        Returns:
            Success status
        """
        ...
    
    async def set_value(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache (alias for backward compatibility).
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            Success status
        """
        ...
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Success status
        """
        ...
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        ...
    
    async def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            Success status
        """
        ...
    
    async def get_many(self, keys: list[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs (missing keys omitted)
        """
        ...
    
    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.
        
        Args:
            items: Dictionary of key-value pairs
            ttl: Time to live in seconds
            
        Returns:
            Success status
        """
        ...
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if key doesn't exist
        """
        ...
    
    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement a numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to decrement by
            
        Returns:
            New value or None if key doesn't exist
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache backend.
        
        Returns:
            Health status with connectivity and performance metrics
        """
        ...






