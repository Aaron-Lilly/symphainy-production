#!/usr/bin/env python3
"""
Redis Adapter - Raw Technology Client

Real Redis client wrapper with no business logic.
This is Layer 1 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide raw Redis client operations
HOW (Infrastructure Implementation): I use real Redis client with no business logic
"""

import os
import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class RedisAdapter:
    """
    Raw Redis client wrapper - no business logic.
    
    This adapter provides direct access to Redis operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, host: str, port: int, db: int = 0, password: str = None):
        """Initialize Redis adapter with real connection."""
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
        
        logger.info(f"✅ Redis adapter initialized with {host}:{port}/{db}")
    
    # ============================================================================
    # RAW STRING OPERATIONS
    # ============================================================================
    
    async def set(self, key: str, value: str, ttl: int = None) -> bool:
        """Raw Redis SET operation - no business logic."""
        try:
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except RedisError as e:
            logger.error(f"Redis SET error: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Raw Redis GET operation - no business logic."""
        try:
            return self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Raw Redis DELETE operation - no business logic."""
        try:
            return self.client.delete(key) > 0
        except RedisError as e:
            logger.error(f"Redis DELETE error: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Raw Redis EXISTS operation - no business logic."""
        try:
            return self.client.exists(key) > 0
        except RedisError as e:
            logger.error(f"Redis EXISTS error: {str(e)}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Raw Redis EXPIRE operation - no business logic."""
        try:
            return self.client.expire(key, ttl)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error: {str(e)}")
            return False
    
    # ============================================================================
    # RAW HASH OPERATIONS
    # ============================================================================
    
    async def hset(self, key: str, field: str, value: str) -> bool:
        """Raw Redis HSET operation - no business logic."""
        try:
            return self.client.hset(key, field, value) >= 0
        except RedisError as e:
            logger.error(f"Redis HSET error: {str(e)}")
            return False
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Raw Redis HGET operation - no business logic."""
        try:
            return self.client.hget(key, field)
        except RedisError as e:
            logger.error(f"Redis HGET error: {str(e)}")
            return None
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Raw Redis HGETALL operation - no business logic."""
        try:
            return self.client.hgetall(key)
        except RedisError as e:
            logger.error(f"Redis HGETALL error: {str(e)}")
            return {}
    
    async def hdel(self, key: str, field: str) -> bool:
        """Raw Redis HDEL operation - no business logic."""
        try:
            return self.client.hdel(key, field) > 0
        except RedisError as e:
            logger.error(f"Redis HDEL error: {str(e)}")
            return False
    
    # ============================================================================
    # RAW SET OPERATIONS
    # ============================================================================
    
    async def sadd(self, key: str, member: str) -> bool:
        """Raw Redis SADD operation - no business logic."""
        try:
            return self.client.sadd(key, member) > 0
        except RedisError as e:
            logger.error(f"Redis SADD error: {str(e)}")
            return False
    
    async def srem(self, key: str, member: str) -> bool:
        """Raw Redis SREM operation - no business logic."""
        try:
            return self.client.srem(key, member) > 0
        except RedisError as e:
            logger.error(f"Redis SREM error: {str(e)}")
            return False
    
    async def smembers(self, key: str) -> List[str]:
        """Raw Redis SMEMBERS operation - no business logic."""
        try:
            return list(self.client.smembers(key))
        except RedisError as e:
            logger.error(f"Redis SMEMBERS error: {str(e)}")
            return []
    
    async def sismember(self, key: str, member: str) -> bool:
        """Raw Redis SISMEMBER operation - no business logic."""
        try:
            return self.client.sismember(key, member)
        except RedisError as e:
            logger.error(f"Redis SISMEMBER error: {str(e)}")
            return False
    
    # ============================================================================
    # RAW SORTED SET OPERATIONS
    # ============================================================================
    
    async def zadd(self, key: str, score: float, member: str) -> bool:
        """Raw Redis ZADD operation - no business logic."""
        try:
            return self.client.zadd(key, {member: score}) > 0
        except RedisError as e:
            logger.error(f"Redis ZADD error: {str(e)}")
            return False
    
    async def zrem(self, key: str, member: str) -> bool:
        """Raw Redis ZREM operation - no business logic."""
        try:
            return self.client.zrem(key, member) > 0
        except RedisError as e:
            logger.error(f"Redis ZREM error: {str(e)}")
            return False
    
    async def zrange(self, key: str, start: int, stop: int, withscores: bool = False) -> List:
        """Raw Redis ZRANGE operation - no business logic."""
        try:
            return self.client.zrange(key, start, stop, withscores=withscores)
        except RedisError as e:
            logger.error(f"Redis ZRANGE error: {str(e)}")
            return []
    
    async def zscore(self, key: str, member: str) -> Optional[float]:
        """Raw Redis ZSCORE operation - no business logic."""
        try:
            return self.client.zscore(key, member)
        except RedisError as e:
            logger.error(f"Redis ZSCORE error: {str(e)}")
            return None
    
    # ============================================================================
    # RAW LIST OPERATIONS
    # ============================================================================
    
    async def lpush(self, key: str, value: str) -> int:
        """Raw Redis LPUSH operation - no business logic."""
        try:
            return self.client.lpush(key, value)
        except RedisError as e:
            logger.error(f"Redis LPUSH error: {str(e)}")
            return 0
    
    async def rpush(self, key: str, value: str) -> int:
        """Raw Redis RPUSH operation - no business logic."""
        try:
            return self.client.rpush(key, value)
        except RedisError as e:
            logger.error(f"Redis RPUSH error: {str(e)}")
            return 0
    
    async def lpop(self, key: str) -> Optional[str]:
        """Raw Redis LPOP operation - no business logic."""
        try:
            return self.client.lpop(key)
        except RedisError as e:
            logger.error(f"Redis LPOP error: {str(e)}")
            return None
    
    async def rpop(self, key: str) -> Optional[str]:
        """Raw Redis RPOP operation - no business logic."""
        try:
            return self.client.rpop(key)
        except RedisError as e:
            logger.error(f"Redis RPOP error: {str(e)}")
            return None
    
    async def llen(self, key: str) -> int:
        """Raw Redis LLEN operation - no business logic."""
        try:
            return self.client.llen(key)
        except RedisError as e:
            logger.error(f"Redis LLEN error: {str(e)}")
            return 0
    
    # ============================================================================
    # RAW SESSION OPERATIONS (using existing patterns)
    # ============================================================================
    
    async def create_session(self, user_id: str, session_data: Dict[str, Any], ttl_seconds: int = 3600) -> str:
        """Raw session creation with Redis - no business logic."""
        try:
            session_id = str(uuid.uuid4())
            session_key = f"session:{session_id}"
            
            # Prepare session data
            session_info = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "data": json.dumps(session_data)
            }
            
            # Store session in Redis with TTL
            await self.hset(session_key, "data", json.dumps(session_info))
            await self.expire(session_key, ttl_seconds)
            
            # Store user session mapping for easy cleanup
            user_sessions_key = f"user_sessions:{user_id}"
            await self.sadd(user_sessions_key, session_id)
            await self.expire(user_sessions_key, ttl_seconds)
            
            logger.info(f"✅ Created session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Redis session creation failed: {e}")
            return str(uuid.uuid4())
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Raw session retrieval with Redis - no business logic."""
        try:
            session_key = f"session:{session_id}"
            session_data = await self.hgetall(session_key)
            
            if not session_data:
                return None
            
            # Parse session data
            session_info = json.loads(session_data.get("data", "{}"))
            return session_info
            
        except Exception as e:
            logger.error(f"Redis session retrieval failed: {e}")
            return None
    
    async def update_session(self, session_id: str, session_data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Raw session update with Redis - no business logic."""
        try:
            session_key = f"session:{session_id}"
            
            # Update session data
            session_info = {
                "user_id": session_data.get("user_id"),
                "created_at": session_data.get("created_at"),
                "last_accessed": datetime.utcnow().isoformat(),
                "data": json.dumps(session_data)
            }
            
            # Update session in Redis
            await self.hset(session_key, "data", json.dumps(session_info))
            await self.expire(session_key, ttl_seconds)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis session update failed: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Raw session deletion with Redis - no business logic."""
        try:
            session_key = f"session:{session_id}"
            
            # Get session data to find user_id
            session_data = await self.get_session(session_id)
            if session_data:
                user_id = session_data.get("user_id")
                if user_id:
                    # Remove from user sessions set
                    user_sessions_key = f"user_sessions:{user_id}"
                    await self.srem(user_sessions_key, session_id)
            
            # Delete session
            return await self.delete(session_key)
            
        except Exception as e:
            logger.error(f"Redis session deletion failed: {e}")
            return False
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Redis connection - no business logic."""
        try:
            # Test with a simple ping
            result = self.client.ping()
            return {
                "success": True,
                "message": "Redis connection successful",
                "host": self.host,
                "port": self.port,
                "db": self.db
            }
        except Exception as e:
            logger.error(f"Redis connection test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "host": self.host,
                "port": self.port,
                "db": self.db
            }
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get Redis connection information - no business logic."""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "has_password": bool(self.password),
            "client_initialized": self.client is not None
        }



