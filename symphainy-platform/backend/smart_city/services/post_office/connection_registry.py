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
            
            # Store in Redis (using messaging abstraction)
            if hasattr(self.messaging_abstraction, 'set'):
                # Direct Redis set
                await self.messaging_abstraction.set(
                    connection_key,
                    json.dumps(connection_data),
                    ex=self.default_ttl
                )
            elif hasattr(self.messaging_abstraction, 'store'):
                # Abstraction store method
                await self.messaging_abstraction.store(
                    connection_key,
                    connection_data,
                    ttl=self.default_ttl
                )
            else:
                # Fallback: Use hset for hash structure
                if hasattr(self.messaging_abstraction, 'hset'):
                    await self.messaging_abstraction.hset(
                        connection_key,
                        mapping=connection_data
                    )
                    await self.messaging_abstraction.expire(connection_key, self.default_ttl)
            
            # Add to channel index
            channel_key = f"websocket:channel:{channel}:connections"
            if hasattr(self.messaging_abstraction, 'sadd'):
                await self.messaging_abstraction.sadd(channel_key, connection_id)
                await self.messaging_abstraction.expire(channel_key, self.default_ttl)
            
            # Add to user index (for session management)
            user_id = metadata.get("user_id")
            if user_id:
                user_key = f"websocket:user:{user_id}:connections"
                if hasattr(self.messaging_abstraction, 'sadd'):
                    await self.messaging_abstraction.sadd(user_key, connection_id)
                    await self.messaging_abstraction.expire(user_key, self.default_ttl)
            
            # Add to gateway instance index
            gateway_key = f"websocket:gateway:{gateway_instance_id}:connections"
            if hasattr(self.messaging_abstraction, 'sadd'):
                await self.messaging_abstraction.sadd(gateway_key, connection_id)
                await self.messaging_abstraction.expire(gateway_key, self.default_ttl)
            
            self.logger.debug(f"✅ Connection registered in Redis: {connection_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register connection {connection_id}: {e}")
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
            
            # Get from Redis
            data = None
            if hasattr(self.messaging_abstraction, 'get'):
                raw_data = await self.messaging_abstraction.get(connection_key)
                if raw_data:
                    data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            elif hasattr(self.messaging_abstraction, 'hgetall'):
                data = await self.messaging_abstraction.hgetall(connection_key)
            
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
                if hasattr(self.messaging_abstraction, 'srem'):
                    await self.messaging_abstraction.srem(channel_key, connection_id)
            
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
                if hasattr(self.messaging_abstraction, 'srem'):
                    await self.messaging_abstraction.srem(user_key, connection_id)
            
            # Remove from gateway instance index
            gateway_instance_id = conn.get("gateway_instance_id")
            if gateway_instance_id:
                gateway_key = f"websocket:gateway:{gateway_instance_id}:connections"
                if hasattr(self.messaging_abstraction, 'srem'):
                    await self.messaging_abstraction.srem(gateway_key, connection_id)
            
            # Delete connection record
            connection_key = f"websocket:connection:{connection_id}"
            if hasattr(self.messaging_abstraction, 'delete'):
                await self.messaging_abstraction.delete(connection_key)
            elif hasattr(self.messaging_abstraction, 'del'):
                await self.messaging_abstraction.del_(connection_key)
            
            self.logger.debug(f"✅ Connection unregistered from Redis: {connection_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister connection {connection_id}: {e}")
            return False
    
    async def update_connection_activity(self, connection_id: str) -> bool:
        """Update last activity timestamp for connection."""
        try:
            connection_key = f"websocket:connection:{connection_id}"
            
            if hasattr(self.messaging_abstraction, 'hset'):
                await self.messaging_abstraction.hset(
                    connection_key,
                    "last_activity",
                    datetime.utcnow().isoformat()
                )
                # Extend TTL
                await self.messaging_abstraction.expire(connection_key, self.default_ttl)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update activity for {connection_id}: {e}")
            return False
    
    async def update_connection_heartbeat(self, connection_id: str) -> bool:
        """Update last heartbeat timestamp and extend TTL."""
        try:
            connection_key = f"websocket:connection:{connection_id}"
            
            if hasattr(self.messaging_abstraction, 'hset'):
                await self.messaging_abstraction.hset(
                    connection_key,
                    "last_heartbeat",
                    datetime.utcnow().isoformat()
                )
                # Extend TTL
                await self.messaging_abstraction.expire(connection_key, self.default_ttl)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update heartbeat for {connection_id}: {e}")
            return False
    
    async def get_connections_by_channel(self, channel: str) -> List[str]:
        """Get all connection IDs for a channel."""
        try:
            channel_key = f"websocket:channel:{channel}:connections"
            
            if hasattr(self.messaging_abstraction, 'smembers'):
                connections = await self.messaging_abstraction.smembers(channel_key)
                return list(connections) if connections else []
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connections for channel {channel}: {e}")
            return []
    
    async def get_connections_by_user(self, user_id: str) -> List[str]:
        """Get all connection IDs for a user."""
        try:
            user_key = f"websocket:user:{user_id}:connections"
            
            if hasattr(self.messaging_abstraction, 'smembers'):
                connections = await self.messaging_abstraction.smembers(user_key)
                return list(connections) if connections else []
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connections for user {user_id}: {e}")
            return []
    
    async def get_connections_by_gateway(self, gateway_instance_id: str) -> List[str]:
        """Get all connection IDs for a gateway instance."""
        try:
            gateway_key = f"websocket:gateway:{gateway_instance_id}:connections"
            
            if hasattr(self.messaging_abstraction, 'smembers'):
                connections = await self.messaging_abstraction.smembers(gateway_key)
                return list(connections) if connections else []
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connections for gateway {gateway_instance_id}: {e}")
            return []
    
    async def add_channel_subscription(self, connection_id: str, channel: str) -> bool:
        """Add channel subscription for connection."""
        try:
            channel_key = f"websocket:channel:{channel}:connections"
            
            if hasattr(self.messaging_abstraction, 'sadd'):
                await self.messaging_abstraction.sadd(channel_key, connection_id)
                await self.messaging_abstraction.expire(channel_key, self.default_ttl)
                
                # Update connection's channel list
                connection_key = f"websocket:connection:{connection_id}"
                if hasattr(self.messaging_abstraction, 'hset'):
                    await self.messaging_abstraction.hset(
                        connection_key,
                        "channel",
                        channel
                    )
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add channel subscription: {e}")
            return False
    
    async def remove_channel_subscription(self, connection_id: str, channel: str) -> bool:
        """Remove channel subscription for connection."""
        try:
            channel_key = f"websocket:channel:{channel}:connections"
            
            if hasattr(self.messaging_abstraction, 'srem'):
                await self.messaging_abstraction.srem(channel_key, connection_id)
                return True
            
            return False
            
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
            if hasattr(self.messaging_abstraction, 'keys'):
                pattern = "websocket:connection:*"
                keys = await self.messaging_abstraction.keys(pattern)
                stats["total"] = len(keys) if keys else 0
            
            # Count by channel
            if hasattr(self.messaging_abstraction, 'keys'):
                channel_pattern = "websocket:channel:*:connections"
                channel_keys = await self.messaging_abstraction.keys(channel_pattern)
                for channel_key in (channel_keys or []):
                    channel_name = channel_key.split(":")[2]  # Extract channel name
                    if hasattr(self.messaging_abstraction, 'scard'):
                        count = await self.messaging_abstraction.scard(channel_key)
                        stats["by_channel"][channel_name] = count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection count: {e}")
            return {"total": 0, "by_channel": {}, "by_gateway": {}}

