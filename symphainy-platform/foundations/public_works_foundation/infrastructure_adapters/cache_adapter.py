#!/usr/bin/env python3
"""
Cache Infrastructure Adapter

Raw cache client wrapper for LLM response caching.
Thin wrapper around cache libraries with no business logic.
"""

from typing import Dict, Any, Optional
import json
import os
import logging
from datetime import datetime

try:
    import redis
    from redis.exceptions import RedisError
except ImportError:
    redis = None
    RedisError = Exception


class CacheAdapter:
    """Raw cache adapter for LLM response caching."""
    
    def __init__(self, storage_type: str = "memory", **kwargs):
        """
        Initialize cache adapter.
        
        Args:
            storage_type: Storage type (memory, redis, file)
            **kwargs: Additional configuration
        """
        self.storage_type = storage_type
        self.logger = logging.getLogger("CacheAdapter")
        
        # Storage configuration
        self.redis_url = kwargs.get("redis_url", "redis://localhost:6379/1")
        self.cache_dir = kwargs.get("cache_dir", "cache/llm")
        
        # Storage clients
        self.redis_client = None
        self.memory_cache = {}
        self.access_times = {}
        
        # Initialize storage
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage backend."""
        try:
            if self.storage_type == "redis":
                self._initialize_redis()
            elif self.storage_type == "memory":
                self._initialize_memory()
            elif self.storage_type == "file":
                self._initialize_file()
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
        self.memory_cache = {}
        self.access_times = {}
        self.logger.info("✅ Memory storage initialized")
    
    def _initialize_file(self):
        """Initialize file storage."""
        os.makedirs(self.cache_dir, exist_ok=True)
        self.logger.info(f"✅ File storage initialized at {self.cache_dir}")
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Dict: Cached value or None
        """
        try:
            if self.storage_type == "redis":
                return await self._get_from_redis(key)
            elif self.storage_type == "memory":
                return await self._get_from_memory(key)
            elif self.storage_type == "file":
                return await self._get_from_file(key)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get from {self.storage_type} storage: {e}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            bool: Success status
        """
        try:
            if self.storage_type == "redis":
                return await self._set_in_redis(key, value, ttl)
            elif self.storage_type == "memory":
                return await self._set_in_memory(key, value, ttl)
            elif self.storage_type == "file":
                return await self._set_in_file(key, value, ttl)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set in {self.storage_type} storage: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: Success status
        """
        try:
            if self.storage_type == "redis":
                return await self._delete_from_redis(key)
            elif self.storage_type == "memory":
                return await self._delete_from_memory(key)
            elif self.storage_type == "file":
                return await self._delete_from_file(key)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete from {self.storage_type} storage: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: Key existence
        """
        try:
            if self.storage_type == "redis":
                return await self._exists_in_redis(key)
            elif self.storage_type == "memory":
                return await self._exists_in_memory(key)
            elif self.storage_type == "file":
                return await self._exists_in_file(key)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to check existence in {self.storage_type} storage: {e}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            bool: Success status
        """
        try:
            if self.storage_type == "redis":
                return await self._clear_redis()
            elif self.storage_type == "memory":
                return await self._clear_memory()
            elif self.storage_type == "file":
                return await self._clear_file()
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to clear {self.storage_type} storage: {e}")
            return False
    
    # Redis operations
    async def _get_from_redis(self, key: str) -> Optional[Dict[str, Any]]:
        """Get from Redis."""
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            self.logger.error(f"Failed to get from Redis: {e}")
            return None
    
    async def _set_in_redis(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set in Redis."""
        try:
            if ttl:
                self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                self.redis_client.set(key, json.dumps(value))
            return True
        except Exception as e:
            self.logger.error(f"Failed to set in Redis: {e}")
            return False
    
    async def _delete_from_redis(self, key: str) -> bool:
        """Delete from Redis."""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete from Redis: {e}")
            return False
    
    async def _exists_in_redis(self, key: str) -> bool:
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
    async def _get_from_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """Get from memory."""
        try:
            return self.memory_cache.get(key)
        except Exception as e:
            self.logger.error(f"Failed to get from memory: {e}")
            return None
    
    async def _set_in_memory(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set in memory."""
        try:
            self.memory_cache[key] = value
            self.access_times[key] = datetime.now()
            return True
        except Exception as e:
            self.logger.error(f"Failed to set in memory: {e}")
            return False
    
    async def _delete_from_memory(self, key: str) -> bool:
        """Delete from memory."""
        try:
            self.memory_cache.pop(key, None)
            self.access_times.pop(key, None)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete from memory: {e}")
            return False
    
    async def _exists_in_memory(self, key: str) -> bool:
        """Check existence in memory."""
        try:
            return key in self.memory_cache
        except Exception as e:
            self.logger.error(f"Failed to check existence in memory: {e}")
            return False
    
    async def _clear_memory(self) -> bool:
        """Clear memory."""
        try:
            self.memory_cache.clear()
            self.access_times.clear()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear memory: {e}")
            return False
    
    # File operations
    async def _get_from_file(self, key: str) -> Optional[Dict[str, Any]]:
        """Get from file."""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get from file: {e}")
            return None
    
    async def _set_in_file(self, key: str, value: Dict[str, Any], ttl: int = None) -> bool:
        """Set in file."""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.json")
            with open(file_path, 'w') as f:
                json.dump(value, f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set in file: {e}")
            return False
    
    async def _delete_from_file(self, key: str) -> bool:
        """Delete from file."""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete from file: {e}")
            return False
    
    async def _exists_in_file(self, key: str) -> bool:
        """Check existence in file."""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.json")
            return os.path.exists(file_path)
        except Exception as e:
            self.logger.error(f"Failed to check existence in file: {e}")
            return False
    
    async def _clear_file(self) -> bool:
        """Clear file storage."""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear file storage: {e}")
            return False
    
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
                health_status["current_size"] = len(self.memory_cache)
            elif self.storage_type == "file":
                health_status["storage_connected"] = os.path.exists(self.cache_dir)
                if not health_status["storage_connected"]:
                    health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }




