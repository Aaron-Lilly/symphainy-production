#!/usr/bin/env python3
"""
Rate Limiting Infrastructure Adapter

Raw rate limiting client wrapper for LLM request rate limiting.
Thin wrapper around rate limiting libraries with no business logic.
"""

import logging
from typing import Dict, Any, Optional
import time
from datetime import datetime

try:
    import redis
    from redis.exceptions import RedisError
except ImportError:
    redis = None
    RedisError = Exception


class RateLimitingAdapter:
    """Raw rate limiting adapter for LLM request rate limiting."""
    
    def __init__(self, storage_type: str = "memory", **kwargs):
        """
        Initialize rate limiting adapter.
        
        Args:
            storage_type: Storage type (memory, redis)
            **kwargs: Additional configuration
        """
        self.storage_type = storage_type
        self.logger = logging.getLogger("RateLimitingAdapter")
        
        # Storage configuration
        self.redis_url = kwargs.get("redis_url", "redis://localhost:6379/1")
        
        # Storage clients
        self.redis_client = None
        self.memory_storage = {}
        
        # Initialize storage
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage backend."""
        try:
            if self.storage_type == "redis":
                self._initialize_redis()
            elif self.storage_type == "memory":
                self._initialize_memory()
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.storage_type} storage: {e}")
            # Fallback to memory
            self.storage_type = "memory"
            self._initialize_memory()
    
    def _initialize_redis(self):
        """Initialize Redis storage."""
        if redis is None:
            raise ImportError("Redis not available")
            
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()  # Test connection
            self.logger.info("✅ Redis storage initialized")
            
        except Exception as e:
            self.logger.error(f"Redis initialization failed: {e}")
            raise
    
    def _initialize_memory(self):
        """Initialize memory storage."""
        self.memory_storage = {}
        self.logger.info("✅ Memory storage initialized")
    
    async def increment_counter(self, key: str, ttl: int = 60) -> int:
        """
        Increment counter for key.
        
        Args:
            key: Counter key
            ttl: Time to live in seconds
            
        Returns:
            int: Current counter value
        """
        try:
            if self.storage_type == "redis":
                return await self._increment_redis_counter(key, ttl)
            elif self.storage_type == "memory":
                return await self._increment_memory_counter(key, ttl)
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Failed to increment counter: {e}")
            return 0
    
    async def get_counter(self, key: str) -> int:
        """
        Get counter value for key.
        
        Args:
            key: Counter key
            
        Returns:
            int: Counter value
        """
        try:
            if self.storage_type == "redis":
                return await self._get_redis_counter(key)
            elif self.storage_type == "memory":
                return await self._get_memory_counter(key)
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Failed to get counter: {e}")
            return 0
    
    async def set_counter(self, key: str, value: int, ttl: int = 60) -> bool:
        """
        Set counter value for key.
        
        Args:
            key: Counter key
            value: Counter value
            ttl: Time to live in seconds
            
        Returns:
            bool: Success status
        """
        try:
            if self.storage_type == "redis":
                return await self._set_redis_counter(key, value, ttl)
            elif self.storage_type == "memory":
                return await self._set_memory_counter(key, value, ttl)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set counter: {e}")
            return False
    
    async def delete_counter(self, key: str) -> bool:
        """
        Delete counter for key.
        
        Args:
            key: Counter key
            
        Returns:
            bool: Success status
        """
        try:
            if self.storage_type == "redis":
                return await self._delete_redis_counter(key)
            elif self.storage_type == "memory":
                return await self._delete_memory_counter(key)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete counter: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Key to check
            
        Returns:
            bool: Key existence
        """
        try:
            if self.storage_type == "redis":
                return await self._exists_redis(key)
            elif self.storage_type == "memory":
                return await self._exists_memory(key)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to check existence: {e}")
            return False
    
    async def clear_all(self) -> bool:
        """
        Clear all counters.
        
        Returns:
            bool: Success status
        """
        try:
            if self.storage_type == "redis":
                return await self._clear_redis()
            elif self.storage_type == "memory":
                return await self._clear_memory()
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to clear all: {e}")
            return False
    
    # Redis operations
    async def _increment_redis_counter(self, key: str, ttl: int) -> int:
        """Increment Redis counter."""
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl)
            results = pipe.execute()
            return results[0]
        except Exception as e:
            self.logger.error(f"Failed to increment Redis counter: {e}")
            return 0
    
    async def _get_redis_counter(self, key: str) -> int:
        """Get Redis counter."""
        try:
            value = self.redis_client.get(key)
            return int(value) if value else 0
        except Exception as e:
            self.logger.error(f"Failed to get Redis counter: {e}")
            return 0
    
    async def _set_redis_counter(self, key: str, value: int, ttl: int) -> bool:
        """Set Redis counter."""
        try:
            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set Redis counter: {e}")
            return False
    
    async def _delete_redis_counter(self, key: str) -> bool:
        """Delete Redis counter."""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete Redis counter: {e}")
            return False
    
    async def _exists_redis(self, key: str) -> bool:
        """Check existence in Redis."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            self.logger.error(f"Failed to check existence in Redis: {e}")
            return False
    
    async def _clear_redis(self) -> bool:
        """Clear Redis."""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear Redis: {e}")
            return False
    
    # Memory operations
    async def _increment_memory_counter(self, key: str, ttl: int) -> int:
        """Increment memory counter."""
        try:
            current_time = time.time()
            
            # Clean expired entries
            self._clean_memory_storage(current_time)
            
            # Increment counter
            if key not in self.memory_storage:
                self.memory_storage[key] = {"value": 0, "expires": current_time + ttl}
            
            self.memory_storage[key]["value"] += 1
            return self.memory_storage[key]["value"]
        except Exception as e:
            self.logger.error(f"Failed to increment memory counter: {e}")
            return 0
    
    async def _get_memory_counter(self, key: str) -> int:
        """Get memory counter."""
        try:
            current_time = time.time()
            
            if key in self.memory_storage:
                if current_time < self.memory_storage[key]["expires"]:
                    return self.memory_storage[key]["value"]
                else:
                    # Expired, remove it
                    del self.memory_storage[key]
            
            return 0
        except Exception as e:
            self.logger.error(f"Failed to get memory counter: {e}")
            return 0
    
    async def _set_memory_counter(self, key: str, value: int, ttl: int) -> bool:
        """Set memory counter."""
        try:
            current_time = time.time()
            self.memory_storage[key] = {
                "value": value,
                "expires": current_time + ttl
            }
            return True
        except Exception as e:
            self.logger.error(f"Failed to set memory counter: {e}")
            return False
    
    async def _delete_memory_counter(self, key: str) -> bool:
        """Delete memory counter."""
        try:
            if key in self.memory_storage:
                del self.memory_storage[key]
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete memory counter: {e}")
            return False
    
    async def _exists_memory(self, key: str) -> bool:
        """Check existence in memory."""
        try:
            current_time = time.time()
            
            if key in self.memory_storage:
                if current_time < self.memory_storage[key]["expires"]:
                    return True
                else:
                    # Expired, remove it
                    del self.memory_storage[key]
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to check existence in memory: {e}")
            return False
    
    async def _clear_memory(self) -> bool:
        """Clear memory storage."""
        try:
            self.memory_storage.clear()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear memory storage: {e}")
            return False
    
    def _clean_memory_storage(self, current_time: float):
        """Clean expired entries from memory storage."""
        try:
            expired_keys = [
                key for key, data in self.memory_storage.items()
                if current_time >= data["expires"]
            ]
            
            for key in expired_keys:
                del self.memory_storage[key]
                
        except Exception as e:
            self.logger.error(f"Failed to clean memory storage: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "storage_type": self.storage_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Test storage connectivity
            if self.storage_type == "redis":
                try:
                    self.redis_client.ping()
                    health_status["storage_connected"] = True
                except Exception as e:
                    health_status["storage_connected"] = False
                    health_status["error"] = str(e)
                    health_status["healthy"] = False
            elif self.storage_type == "memory":
                health_status["storage_connected"] = True
                health_status["current_entries"] = len(self.memory_storage)
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }




