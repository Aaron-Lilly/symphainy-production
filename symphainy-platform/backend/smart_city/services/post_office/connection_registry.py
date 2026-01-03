#!/usr/bin/env python3
"""
Connection Registry - Redis-backed connection management

Manages WebSocket connection state in Redis for horizontal scaling.
Allows multiple gateway instances to coordinate connection state.

WHAT: I manage WebSocket connection state across gateway instances
HOW: I use Redis for distributed connection tracking
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Set, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionRegistry:
    """
    Redis-backed connection registry for horizontal scaling.
    
    Manages WebSocket connection state in Redis, enabling:
    - Multiple gateway instances to coordinate
    - Connection recovery across instance restarts
    - Cross-instance message routing
    - Connection lifecycle tracking
    """
    
    def __init__(self, messaging_abstraction: Any):
        """
        Initialize Connection Registry.
        
        Args:
            messaging_abstraction: Redis messaging abstraction (direct access - Smart City privilege)
        """
        self.messaging_abstraction = messaging_abstraction
        self.logger = logger
        
        # Get Redis client from messaging abstraction's adapter
        # messaging_abstraction -> messaging_adapter -> redis_client
        self.redis_client = None
        if hasattr(messaging_abstraction, 'messaging_adapter'):
            if hasattr(messaging_abstraction.messaging_adapter, 'redis_client'):
                self.redis_client = messaging_abstraction.messaging_adapter.redis_client
        
        if not self.redis_client:
            raise ValueError("Redis client not available from messaging abstraction")
        
        # Verify redis client is async (redis.asyncio.Redis)
        # If it's not async, we need to handle it differently
        import inspect
        if not inspect.iscoroutinefunction(getattr(self.redis_client, 'smembers', None)):
            # If smembers is not async, it might be a sync client wrapped
            # Try to get the actual async client or use a wrapper
            self.logger.warning("⚠️ Redis client may not be async - checking methods")
            # For now, assume it's async and let errors surface
        
        # Default TTL for connections (1 hour, extendable via heartbeat)
        self.default_ttl = 3600  # seconds
        
        self.logger.info("✅ Connection Registry initialized (Redis-backed)")
    
    async def register_connection(
        self,
        connection_id: str,
        session_token: str,
        channel: str,
        metadata: Dict[str, Any],
        gateway_instance_id: str
    ) -> bool:
        """
        Register connection in Redis.
        
        Args:
            connection_id: Unique connection identifier
            session_token: Session token for the connection
            channel: Initial channel subscription
            metadata: Connection metadata (user_id, connected_at, etc.)
            gateway_instance_id: ID of gateway instance handling this connection
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Build connection key
            connection_key = f"websocket:connection:{connection_id}"
            
            # Prepare connection data
            connection_data = {
                "connection_id": connection_id,
                "session_token": session_token,
                "channel": channel,
                "connected_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "last_heartbeat": datetime.utcnow().isoformat(),
                "gateway_instance_id": gateway_instance_id,
                "metadata": json.dumps(metadata) if isinstance(metadata, dict) else metadata
            }
            
            # Store in Redis using direct Redis client
            # Use hset for hash structure (better for connection metadata)
            import inspect
            hset_method = getattr(self.redis_client, 'hset', None)
            if hset_method and inspect.iscoroutinefunction(hset_method):
                await self.redis_client.hset(
                    connection_key,
                    mapping=connection_data
                )
            else:
                self.redis_client.hset(
                    connection_key,
                    mapping=connection_data
                )
            
            expire_method = getattr(self.redis_client, 'expire', None)
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(connection_key, self.default_ttl)
            else:
                self.redis_client.expire(connection_key, self.default_ttl)
            
            # Add to channel index
            channel_key = f"websocket:channel:{channel}:connections"
            sadd_method = getattr(self.redis_client, 'sadd', None)
            if sadd_method and inspect.iscoroutinefunction(sadd_method):
                await self.redis_client.sadd(channel_key, connection_id)
            else:
                self.redis_client.sadd(channel_key, connection_id)
            
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(channel_key, self.default_ttl)
            else:
                self.redis_client.expire(channel_key, self.default_ttl)
            
            # Add to user index (for session management)
            user_id = metadata.get("user_id")
            if user_id:
                user_key = f"websocket:user:{user_id}:connections"
                if sadd_method and inspect.iscoroutinefunction(sadd_method):
                    await self.redis_client.sadd(user_key, connection_id)
                else:
                    self.redis_client.sadd(user_key, connection_id)
                
                if expire_method and inspect.iscoroutinefunction(expire_method):
                    await self.redis_client.expire(user_key, self.default_ttl)
                else:
                    self.redis_client.expire(user_key, self.default_ttl)
            
            # Add to gateway instance index
            gateway_key = f"websocket:gateway:{gateway_instance_id}:connections"
            if sadd_method and inspect.iscoroutinefunction(sadd_method):
                await self.redis_client.sadd(gateway_key, connection_id)
            else:
                self.redis_client.sadd(gateway_key, connection_id)
            
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(gateway_key, self.default_ttl)
            else:
                self.redis_client.expire(gateway_key, self.default_ttl)
            
            # Verify registration was successful
            verify_conn = await self.get_connection(connection_id)
            if verify_conn:
                self.logger.info(f"✅ Connection registered in Redis: {connection_id} (verified)")
            else:
                self.logger.warning(f"⚠️ Connection registration may have failed: {connection_id} (not found in verification)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register connection {connection_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get connection metadata from Redis.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            Connection metadata dict or None if not found
        """
        try:
            connection_key = f"websocket:connection:{connection_id}"
            
            # Check if redis_client is async
            import inspect
            hgetall_method = getattr(self.redis_client, 'hgetall', None)
            if hgetall_method and inspect.iscoroutinefunction(hgetall_method):
                data = await self.redis_client.hgetall(connection_key)
            else:
                # Fallback: try calling directly (might be sync)
                data = self.redis_client.hgetall(connection_key)
            
            # Convert bytes to strings if needed (redis-py returns bytes)
            if data:
                data = {k.decode('utf-8') if isinstance(k, bytes) else k: 
                       v.decode('utf-8') if isinstance(v, bytes) else v 
                       for k, v in data.items()}
            
            if not data:
                return None
            
            # Parse metadata if it's a JSON string
            if isinstance(data.get("metadata"), str):
                try:
                    data["metadata"] = json.loads(data["metadata"])
                except:
                    data["metadata"] = {}
            
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection {connection_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def unregister_connection(self, connection_id: str) -> bool:
        """
        Unregister connection from Redis.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            # Get connection info before deletion
            conn = await self.get_connection(connection_id)
            if not conn:
                return True  # Already removed
            
            # Remove from channel index
            channel = conn.get("channel")
            if channel:
                channel_key = f"websocket:channel:{channel}:connections"
                await self.redis_client.srem(channel_key, connection_id)
            
            # Remove from user index
            metadata = conn.get("metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            user_id = metadata.get("user_id")
            if user_id:
                user_key = f"websocket:user:{user_id}:connections"
                await self.redis_client.srem(user_key, connection_id)
            
            # Remove from gateway instance index
            gateway_instance_id = conn.get("gateway_instance_id")
            if gateway_instance_id:
                gateway_key = f"websocket:gateway:{gateway_instance_id}:connections"
                await self.redis_client.srem(gateway_key, connection_id)
            
            # Delete connection record
            connection_key = f"websocket:connection:{connection_id}"
            import inspect
            delete_method = getattr(self.redis_client, 'delete', None)
            if delete_method and inspect.iscoroutinefunction(delete_method):
                await self.redis_client.delete(connection_key)
            else:
                self.redis_client.delete(connection_key)
            
            self.logger.debug(f"✅ Connection unregistered from Redis: {connection_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister connection {connection_id}: {e}")
            return False
    
    async def update_connection_activity(self, connection_id: str) -> bool:
        """Update last activity timestamp for connection."""
        try:
            connection_key = f"websocket:connection:{connection_id}"
            
            import inspect
            hset_method = getattr(self.redis_client, 'hset', None)
            if hset_method and inspect.iscoroutinefunction(hset_method):
                await self.redis_client.hset(
                    connection_key,
                    "last_activity",
                    datetime.utcnow().isoformat()
                )
            else:
                self.redis_client.hset(
                    connection_key,
                    "last_activity",
                    datetime.utcnow().isoformat()
                )
            
            # Extend TTL
            expire_method = getattr(self.redis_client, 'expire', None)
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(connection_key, self.default_ttl)
            else:
                self.redis_client.expire(connection_key, self.default_ttl)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update activity for {connection_id}: {e}")
            return False
    
    async def update_connection_heartbeat(self, connection_id: str) -> bool:
        """Update last heartbeat timestamp and extend TTL."""
        try:
            connection_key = f"websocket:connection:{connection_id}"
            
            import inspect
            hset_method = getattr(self.redis_client, 'hset', None)
            if hset_method and inspect.iscoroutinefunction(hset_method):
                await self.redis_client.hset(
                    connection_key,
                    "last_heartbeat",
                    datetime.utcnow().isoformat()
                )
            else:
                self.redis_client.hset(
                    connection_key,
                    "last_heartbeat",
                    datetime.utcnow().isoformat()
                )
            
            # Extend TTL
            expire_method = getattr(self.redis_client, 'expire', None)
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(connection_key, self.default_ttl)
            else:
                self.redis_client.expire(connection_key, self.default_ttl)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update heartbeat for {connection_id}: {e}")
            return False
    
    async def get_connections_by_channel(self, channel: str) -> List[str]:
        """Get all connection IDs for a channel."""
        try:
            channel_key = f"websocket:channel:{channel}:connections"
            
            # Check if redis_client is async (redis.asyncio.Redis)
            # If smembers is a coroutine, await it; otherwise call it directly
            import inspect
            smembers_method = getattr(self.redis_client, 'smembers', None)
            if smembers_method and inspect.iscoroutinefunction(smembers_method):
                connections = await self.redis_client.smembers(channel_key)
            else:
                # Fallback: try calling directly (might be sync)
                connections = self.redis_client.smembers(channel_key)
            
            if connections:
                # Convert bytes to strings if needed, and convert set to list
                if isinstance(connections, set):
                    connections = list(connections)
                return [conn.decode('utf-8') if isinstance(conn, bytes) else str(conn) for conn in connections]
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connections for channel {channel}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def get_connections_by_user(self, user_id: str) -> List[str]:
        """Get all connection IDs for a user."""
        try:
            user_key = f"websocket:user:{user_id}:connections"
            
            # Check if redis_client is async
            import inspect
            smembers_method = getattr(self.redis_client, 'smembers', None)
            if smembers_method and inspect.iscoroutinefunction(smembers_method):
                connections = await self.redis_client.smembers(user_key)
            else:
                connections = self.redis_client.smembers(user_key)
            
            if connections:
                # Convert bytes to strings if needed, and convert set to list
                if isinstance(connections, set):
                    connections = list(connections)
                return [conn.decode('utf-8') if isinstance(conn, bytes) else str(conn) for conn in connections]
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connections for user {user_id}: {e}")
            return []
    
    async def get_connections_by_gateway(self, gateway_instance_id: str) -> List[str]:
        """Get all connection IDs for a gateway instance."""
        try:
            gateway_key = f"websocket:gateway:{gateway_instance_id}:connections"
            
            # Check if redis_client is async
            import inspect
            smembers_method = getattr(self.redis_client, 'smembers', None)
            if smembers_method and inspect.iscoroutinefunction(smembers_method):
                connections = await self.redis_client.smembers(gateway_key)
            else:
                connections = self.redis_client.smembers(gateway_key)
            
            if connections:
                # Convert bytes to strings if needed, and convert set to list
                if isinstance(connections, set):
                    connections = list(connections)
                return [conn.decode('utf-8') if isinstance(conn, bytes) else str(conn) for conn in connections]
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connections for gateway {gateway_instance_id}: {e}")
            return []
    
    async def add_channel_subscription(self, connection_id: str, channel: str) -> bool:
        """Add channel subscription for connection."""
        try:
            channel_key = f"websocket:channel:{channel}:connections"
            
            self.logger.debug(f"📝 Adding channel subscription: connection_id={connection_id}, channel={channel}, channel_key={channel_key}")
            
            # Check if redis_client is async
            import inspect
            sadd_method = getattr(self.redis_client, 'sadd', None)
            if sadd_method and inspect.iscoroutinefunction(sadd_method):
                result = await self.redis_client.sadd(channel_key, connection_id)
            else:
                result = self.redis_client.sadd(channel_key, connection_id)
            
            self.logger.debug(f"✅ SADD result for {channel_key}: {result} (1=added, 0=already exists)")
            
            # Set TTL on channel key
            expire_method = getattr(self.redis_client, 'expire', None)
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(channel_key, self.default_ttl)
            else:
                self.redis_client.expire(channel_key, self.default_ttl)
            
            # Update connection's channel in connection record
            connection_key = f"websocket:connection:{connection_id}"
            hset_method = getattr(self.redis_client, 'hset', None)
            if hset_method and inspect.iscoroutinefunction(hset_method):
                await self.redis_client.hset(
                    connection_key,
                    "channel",
                    channel
                )
            else:
                self.redis_client.hset(
                    connection_key,
                    "channel",
                    channel
                )
            
            # Verify subscription was added
            smembers_method = getattr(self.redis_client, 'smembers', None)
            if smembers_method and inspect.iscoroutinefunction(smembers_method):
                verify_connections = await self.redis_client.smembers(channel_key)
            else:
                verify_connections = self.redis_client.smembers(channel_key)
            
            if verify_connections:
                if isinstance(verify_connections, set):
                    verify_connections = list(verify_connections)
                verify_list = [str(c) for c in verify_connections]
                self.logger.debug(f"✅ Verified channel subscription: {channel_key} has {len(verify_list)} connections: {verify_list}")
                if connection_id in verify_list or str(connection_id) in verify_list:
                    self.logger.info(f"✅ Channel subscription confirmed: {connection_id} -> {channel}")
                else:
                    self.logger.warning(f"⚠️ Channel subscription not found in verification: {connection_id} not in {verify_list}")
            else:
                self.logger.warning(f"⚠️ Channel subscription set is empty after adding: {channel_key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add channel subscription: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def remove_channel_subscription(self, connection_id: str, channel: str) -> bool:
        """Remove channel subscription for connection."""
        try:
            channel_key = f"websocket:channel:{channel}:connections"
            
            import inspect
            srem_method = getattr(self.redis_client, 'srem', None)
            if srem_method and inspect.iscoroutinefunction(srem_method):
                await self.redis_client.srem(channel_key, connection_id)
            else:
                self.redis_client.srem(channel_key, connection_id)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove channel subscription: {e}")
            return False
    
    async def get_connection_count(self) -> Dict[str, int]:
        """Get connection statistics."""
        try:
            stats = {
                "total": 0,
                "by_channel": {},
                "by_gateway": {}
            }
            
            # Count total connections (scan for all connection keys)
            # Note: This is expensive, use sparingly. In production, maintain counters.
            import inspect
            pattern = "websocket:connection:*"
            keys_method = getattr(self.redis_client, 'keys', None)
            if keys_method and inspect.iscoroutinefunction(keys_method):
                keys = await self.redis_client.keys(pattern)
            else:
                keys = self.redis_client.keys(pattern)
            stats["total"] = len(keys) if keys else 0
            
            # Count by channel
            channel_pattern = "websocket:channel:*:connections"
            if keys_method and inspect.iscoroutinefunction(keys_method):
                channel_keys = await self.redis_client.keys(channel_pattern)
            else:
                channel_keys = self.redis_client.keys(channel_pattern)
            
            scard_method = getattr(self.redis_client, 'scard', None)
            for channel_key in (channel_keys or []):
                # Convert bytes to string if needed
                channel_key_str = channel_key.decode('utf-8') if isinstance(channel_key, bytes) else channel_key
                channel_name = channel_key_str.split(":")[2]  # Extract channel name
                if scard_method and inspect.iscoroutinefunction(scard_method):
                    count = await self.redis_client.scard(channel_key_str)
                else:
                    count = self.redis_client.scard(channel_key_str)
                stats["by_channel"][channel_name] = count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection count: {e}")
            return {"total": 0, "by_channel": {}, "by_gateway": {}}

