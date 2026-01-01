#!/usr/bin/env python3
"""
Redis State Adapter - Raw Technology Client (Compact)

Raw Redis client wrapper for session state management.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Redis operations for session state management
HOW (Infrastructure Implementation): I use real Redis client with no business logic
"""

import logging
import json
from typing import Dict, Any, Optional, List, Union
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class RedisStateAdapter:
    """Raw Redis client wrapper for state management - no business logic."""
    
    def __init__(self, host: str, port: int, db: int = 0, password: str = None):
        """Initialize Redis state adapter with real connection."""
        self.client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
        logger.info(f"✅ Redis State adapter initialized with {host}:{port}/{db}")
    
    # ============================================================================
    # RAW STRING OPERATIONS
    # ============================================================================
    
    async def set_string(self, key: str, value: str, ttl: int = None) -> bool:
        """Raw string set - no business logic."""
        try:
            return self.client.set(key, value, ex=ttl)
        except RedisError as e:
            logger.error(f"❌ Failed to set string {key}: {e}")
            return False
    
    async def get_string(self, key: str) -> Optional[str]:
        """Raw string get - no business logic."""
        try:
            return self.client.get(key)
        except RedisError as e:
            logger.error(f"❌ Failed to get string {key}: {e}")
            return None
    
    async def delete_string(self, key: str) -> bool:
        """Raw string delete - no business logic."""
        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            logger.error(f"❌ Failed to delete string {key}: {e}")
            return False
    
    # ============================================================================
    # RAW HASH OPERATIONS
    # ============================================================================
    
    async def set_hash(self, key: str, field: str, value: str) -> bool:
        """Raw hash field set - no business logic."""
        try:
            return bool(self.client.hset(key, field, value))
        except RedisError as e:
            logger.error(f"❌ Failed to set hash field {key}.{field}: {e}")
            return False
    
    async def get_hash(self, key: str, field: str) -> Optional[str]:
        """Raw hash field get - no business logic."""
        try:
            return self.client.hget(key, field)
        except RedisError as e:
            logger.error(f"❌ Failed to get hash field {key}.{field}: {e}")
            return None
    
    async def get_all_hash(self, key: str) -> Dict[str, str]:
        """Raw hash get all - no business logic."""
        try:
            return self.client.hgetall(key)
        except RedisError as e:
            logger.error(f"❌ Failed to get hash {key}: {e}")
            return {}
    
    async def set_multiple_hash(self, key: str, mapping: Dict[str, str], ttl: int = None) -> bool:
        """Raw hash set multiple - no business logic."""
        try:
            result = self.client.hset(key, mapping=mapping)
            if ttl:
                self.client.expire(key, ttl)
            return bool(result)
        except RedisError as e:
            logger.error(f"❌ Failed to set hash multiple {key}: {e}")
            return False
    
    # ============================================================================
    # RAW LIST OPERATIONS
    # ============================================================================
    
    async def push_list(self, key: str, value: str, side: str = "right") -> int:
        """Raw list push - no business logic."""
        try:
            return self.client.lpush(key, value) if side == "left" else self.client.rpush(key, value)
        except RedisError as e:
            logger.error(f"❌ Failed to push list {key}: {e}")
            return 0
    
    async def pop_list(self, key: str, side: str = "right") -> Optional[str]:
        """Raw list pop - no business logic."""
        try:
            return self.client.lpop(key) if side == "left" else self.client.rpop(key)
        except RedisError as e:
            logger.error(f"❌ Failed to pop list {key}: {e}")
            return None
    
    async def get_list_range(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Raw list range - no business logic."""
        try:
            return self.client.lrange(key, start, end)
        except RedisError as e:
            logger.error(f"❌ Failed to get list range {key}: {e}")
            return []
    
    # ============================================================================
    # RAW SET OPERATIONS
    # ============================================================================
    
    async def add_set(self, key: str, *values: str) -> int:
        """Raw set add - no business logic."""
        try:
            return self.client.sadd(key, *values)
        except RedisError as e:
            logger.error(f"❌ Failed to add set {key}: {e}")
            return 0
    
    async def get_set_members(self, key: str) -> set:
        """Raw set members - no business logic."""
        try:
            return self.client.smembers(key)
        except RedisError as e:
            logger.error(f"❌ Failed to get set members {key}: {e}")
            return set()
    
    async def is_set_member(self, key: str, value: str) -> bool:
        """Raw set membership check - no business logic."""
        try:
            return self.client.sismember(key, value)
        except RedisError as e:
            logger.error(f"❌ Failed to check set membership {key}.{value}: {e}")
            return False
    
    # ============================================================================
    # RAW SORTED SET OPERATIONS
    # ============================================================================
    
    async def add_sorted_set(self, key: str, mapping: Dict[str, float]) -> int:
        """Raw sorted set add - no business logic."""
        try:
            return self.client.zadd(key, mapping)
        except RedisError as e:
            logger.error(f"❌ Failed to add sorted set {key}: {e}")
            return 0
    
    async def get_sorted_set_range(self, key: str, start: int = 0, end: int = -1, 
                                 with_scores: bool = False) -> List[Union[str, tuple]]:
        """Raw sorted set range - no business logic."""
        try:
            return self.client.zrange(key, start, end, withscores=with_scores)
        except RedisError as e:
            logger.error(f"❌ Failed to get sorted set range {key}: {e}")
            return []
    
    # ============================================================================
    # RAW TTL OPERATIONS
    # ============================================================================
    
    async def set_ttl(self, key: str, ttl: int) -> bool:
        """Raw TTL set - no business logic."""
        try:
            return self.client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"❌ Failed to set TTL {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Raw TTL get - no business logic."""
        try:
            return self.client.ttl(key)
        except RedisError as e:
            logger.error(f"❌ Failed to get TTL {key}: {e}")
            return -1
    
    # ============================================================================
    # RAW KEY OPERATIONS
    # ============================================================================
    
    async def key_exists(self, key: str) -> bool:
        """Raw key existence check - no business logic."""
        try:
            return bool(self.client.exists(key))
        except RedisError as e:
            logger.error(f"❌ Failed to check key existence {key}: {e}")
            return False
    
    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Raw keys search - no business logic."""
        try:
            return self.client.keys(pattern)
        except RedisError as e:
            logger.error(f"❌ Failed to get keys {pattern}: {e}")
            return []
    
    async def delete_keys(self, *keys: str) -> int:
        """Raw keys delete - no business logic."""
        try:
            return self.client.delete(*keys)
        except RedisError as e:
            logger.error(f"❌ Failed to delete keys: {e}")
            return 0
    
    # ============================================================================
    # RAW JSON OPERATIONS
    # ============================================================================
    
    async def set_json(self, key: str, data: Dict[str, Any], ttl: int = None) -> bool:
        """Raw JSON set - no business logic."""
        try:
            json_data = json.dumps(data)
            return self.client.set(key, json_data, ex=ttl)
        except (RedisError, json.JSONEncodeError) as e:
            logger.error(f"❌ Failed to set JSON {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Raw JSON get - no business logic."""
        try:
            result = self.client.get(key)
            return json.loads(result) if result else None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to get JSON {key}: {e}")
            return None
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_connection(self) -> bool:
        """Raw connection test - no business logic."""
        try:
            return self.client.ping()
        except RedisError as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def get_info(self) -> Dict[str, Any]:
        """Raw Redis info - no business logic."""
        try:
            return self.client.info()
        except RedisError as e:
            logger.error(f"❌ Failed to get Redis info: {e}")
            return {}
    
    async def close_connection(self) -> bool:
        """Raw connection close - no business logic."""
        try:
            self.client.close()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to close connection: {e}")
            return False

