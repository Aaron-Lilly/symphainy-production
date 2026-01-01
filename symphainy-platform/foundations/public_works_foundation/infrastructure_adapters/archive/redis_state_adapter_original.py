#!/usr/bin/env python3
"""
Redis State Adapter - Raw Technology Client

Raw Redis client wrapper for session state management.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Redis operations for session state management
HOW (Infrastructure Implementation): I use real Redis client with no business logic
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class RedisStateAdapter:
    """
    Raw Redis client wrapper for state management - no business logic.
    
    This adapter provides direct access to Redis operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, host: str, port: int, db: int = 0, password: str = None):
        """Initialize Redis state adapter with real connection."""
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        
        # Create Redis client
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        
        logger.info(f"✅ Redis State adapter initialized with {host}:{port}/{db}")
    
    # ============================================================================
    # RAW STRING OPERATIONS
    # ============================================================================
    
    async def set_string(self, key: str, value: str, ttl: int = None) -> bool:
        """Raw string set - no business logic."""
        try:
            result = self.client.set(key, value, ex=ttl)
            logger.debug(f"✅ String set: {key}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to set string {key}: {e}")
            return False
    
    async def get_string(self, key: str) -> Optional[str]:
        """Raw string get - no business logic."""
        try:
            result = self.client.get(key)
            if result:
                logger.debug(f"✅ String retrieved: {key}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get string {key}: {e}")
            return None
    
    async def delete_string(self, key: str) -> bool:
        """Raw string delete - no business logic."""
        try:
            result = self.client.delete(key)
            logger.debug(f"✅ String deleted: {key}")
            return bool(result)
        except RedisError as e:
            logger.error(f"❌ Failed to delete string {key}: {e}")
            return False
    
    # ============================================================================
    # RAW HASH OPERATIONS
    # ============================================================================
    
    async def set_hash(self, key: str, field: str, value: str) -> bool:
        """Raw hash field set - no business logic."""
        try:
            result = self.client.hset(key, field, value)
            logger.debug(f"✅ Hash field set: {key}.{field}")
            return bool(result)
        except RedisError as e:
            logger.error(f"❌ Failed to set hash field {key}.{field}: {e}")
            return False
    
    async def get_hash(self, key: str, field: str) -> Optional[str]:
        """Raw hash field get - no business logic."""
        try:
            result = self.client.hget(key, field)
            if result:
                logger.debug(f"✅ Hash field retrieved: {key}.{field}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get hash field {key}.{field}: {e}")
            return None
    
    async def get_all_hash(self, key: str) -> Dict[str, str]:
        """Raw hash get all - no business logic."""
        try:
            result = self.client.hgetall(key)
            logger.debug(f"✅ Hash retrieved: {key} ({len(result)} fields)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get hash {key}: {e}")
            return {}
    
    async def set_multiple_hash(self, key: str, mapping: Dict[str, str], ttl: int = None) -> bool:
        """Raw hash set multiple - no business logic."""
        try:
            result = self.client.hset(key, mapping=mapping)
            if ttl:
                self.client.expire(key, ttl)
            logger.debug(f"✅ Hash set multiple: {key} ({len(mapping)} fields)")
            return bool(result)
        except RedisError as e:
            logger.error(f"❌ Failed to set hash multiple {key}: {e}")
            return False
    
    async def delete_hash_field(self, key: str, field: str) -> bool:
        """Raw hash field delete - no business logic."""
        try:
            result = self.client.hdel(key, field)
            logger.debug(f"✅ Hash field deleted: {key}.{field}")
            return bool(result)
        except RedisError as e:
            logger.error(f"❌ Failed to delete hash field {key}.{field}: {e}")
            return False
    
    # ============================================================================
    # RAW LIST OPERATIONS
    # ============================================================================
    
    async def push_list(self, key: str, value: str, side: str = "right") -> int:
        """Raw list push - no business logic."""
        try:
            if side == "left":
                result = self.client.lpush(key, value)
            else:
                result = self.client.rpush(key, value)
            logger.debug(f"✅ List pushed: {key} ({side})")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to push list {key}: {e}")
            return 0
    
    async def pop_list(self, key: str, side: str = "right") -> Optional[str]:
        """Raw list pop - no business logic."""
        try:
            if side == "left":
                result = self.client.lpop(key)
            else:
                result = self.client.rpop(key)
            if result:
                logger.debug(f"✅ List popped: {key} ({side})")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to pop list {key}: {e}")
            return None
    
    async def get_list_range(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Raw list range - no business logic."""
        try:
            result = self.client.lrange(key, start, end)
            logger.debug(f"✅ List range retrieved: {key} ({len(result)} items)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get list range {key}: {e}")
            return []
    
    async def get_list_length(self, key: str) -> int:
        """Raw list length - no business logic."""
        try:
            result = self.client.llen(key)
            logger.debug(f"✅ List length: {key} = {result}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get list length {key}: {e}")
            return 0
    
    # ============================================================================
    # RAW SET OPERATIONS
    # ============================================================================
    
    async def add_set(self, key: str, *values: str) -> int:
        """Raw set add - no business logic."""
        try:
            result = self.client.sadd(key, *values)
            logger.debug(f"✅ Set added: {key} ({len(values)} values)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to add set {key}: {e}")
            return 0
    
    async def get_set_members(self, key: str) -> set:
        """Raw set members - no business logic."""
        try:
            result = self.client.smembers(key)
            logger.debug(f"✅ Set members retrieved: {key} ({len(result)} members)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get set members {key}: {e}")
            return set()
    
    async def is_set_member(self, key: str, value: str) -> bool:
        """Raw set membership check - no business logic."""
        try:
            result = self.client.sismember(key, value)
            logger.debug(f"✅ Set membership check: {key}.{value} = {result}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to check set membership {key}.{value}: {e}")
            return False
    
    async def remove_set(self, key: str, *values: str) -> int:
        """Raw set remove - no business logic."""
        try:
            result = self.client.srem(key, *values)
            logger.debug(f"✅ Set removed: {key} ({len(values)} values)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to remove set {key}: {e}")
            return 0
    
    # ============================================================================
    # RAW SORTED SET OPERATIONS
    # ============================================================================
    
    async def add_sorted_set(self, key: str, mapping: Dict[str, float]) -> int:
        """Raw sorted set add - no business logic."""
        try:
            result = self.client.zadd(key, mapping)
            logger.debug(f"✅ Sorted set added: {key} ({len(mapping)} values)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to add sorted set {key}: {e}")
            return 0
    
    async def get_sorted_set_range(self, key: str, start: int = 0, end: int = -1, 
                                 with_scores: bool = False) -> List[Union[str, tuple]]:
        """Raw sorted set range - no business logic."""
        try:
            result = self.client.zrange(key, start, end, withscores=with_scores)
            logger.debug(f"✅ Sorted set range retrieved: {key} ({len(result)} items)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get sorted set range {key}: {e}")
            return []
    
    async def get_sorted_set_score(self, key: str, member: str) -> Optional[float]:
        """Raw sorted set score - no business logic."""
        try:
            result = self.client.zscore(key, member)
            if result is not None:
                logger.debug(f"✅ Sorted set score: {key}.{member} = {result}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get sorted set score {key}.{member}: {e}")
            return None
    
    # ============================================================================
    # RAW TTL OPERATIONS
    # ============================================================================
    
    async def set_ttl(self, key: str, ttl: int) -> bool:
        """Raw TTL set - no business logic."""
        try:
            result = self.client.expire(key, ttl)
            logger.debug(f"✅ TTL set: {key} = {ttl}s")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to set TTL {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Raw TTL get - no business logic."""
        try:
            result = self.client.ttl(key)
            logger.debug(f"✅ TTL retrieved: {key} = {result}s")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get TTL {key}: {e}")
            return -1
    
    async def remove_ttl(self, key: str) -> bool:
        """Raw TTL remove - no business logic."""
        try:
            result = self.client.persist(key)
            logger.debug(f"✅ TTL removed: {key}")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to remove TTL {key}: {e}")
            return False
    
    # ============================================================================
    # RAW KEY OPERATIONS
    # ============================================================================
    
    async def key_exists(self, key: str) -> bool:
        """Raw key existence check - no business logic."""
        try:
            result = self.client.exists(key)
            logger.debug(f"✅ Key exists: {key} = {bool(result)}")
            return bool(result)
        except RedisError as e:
            logger.error(f"❌ Failed to check key existence {key}: {e}")
            return False
    
    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Raw keys search - no business logic."""
        try:
            result = self.client.keys(pattern)
            logger.debug(f"✅ Keys found: {pattern} ({len(result)} keys)")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get keys {pattern}: {e}")
            return []
    
    async def delete_keys(self, *keys: str) -> int:
        """Raw keys delete - no business logic."""
        try:
            result = self.client.delete(*keys)
            logger.debug(f"✅ Keys deleted: {len(keys)} keys")
            return result
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
            result = self.client.set(key, json_data, ex=ttl)
            logger.debug(f"✅ JSON set: {key}")
            return result
        except (RedisError, json.JSONEncodeError) as e:
            logger.error(f"❌ Failed to set JSON {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Raw JSON get - no business logic."""
        try:
            result = self.client.get(key)
            if result:
                data = json.loads(result)
                logger.debug(f"✅ JSON retrieved: {key}")
                return data
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to get JSON {key}: {e}")
            return None
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_connection(self) -> bool:
        """Raw connection test - no business logic."""
        try:
            result = self.client.ping()
            logger.debug(f"✅ Connection test successful")
            return result
        except RedisError as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def get_info(self) -> Dict[str, Any]:
        """Raw Redis info - no business logic."""
        try:
            result = self.client.info()
            logger.debug(f"✅ Redis info retrieved")
            return result
        except RedisError as e:
            logger.error(f"❌ Failed to get Redis info: {e}")
            return {}
    
    async def close_connection(self) -> bool:
        """Raw connection close - no business logic."""
        try:
            self.client.close()
            logger.debug(f"✅ Connection closed")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to close connection: {e}")
            return False
