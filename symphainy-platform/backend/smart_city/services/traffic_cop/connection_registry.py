#!/usr/bin/env python3
"""
Traffic Cop Connection Registry - Redis-backed WebSocket connection management

Manages WebSocket connection state in Redis for horizontal scaling.
Allows multiple Traffic Cop instances to coordinate connection state.

WHAT: I manage WebSocket connection state across Traffic Cop instances
HOW: I use Redis for distributed connection tracking

Key differences from Post Office ConnectionRegistry:
- Connections are keyed by session_id, agent_type, and pillar
- Supports Traffic Cop's nested connection structure
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class TrafficCopConnectionRegistry:
    """
    Redis-backed connection registry for Traffic Cop horizontal scaling.
    
    Manages WebSocket connection state in Redis, enabling:
    - Multiple Traffic Cop instances to coordinate
    - Connection recovery across instance restarts
    - Cross-instance connection lookup
    - Connection lifecycle tracking
    
    Connection structure:
    - Key: traffic_cop:session:{session_id}:websocket:{websocket_id}
    - Value: JSON with websocket_id, session_id, agent_type, pillar, metadata
    - Indexes: session_id -> [websocket_ids], agent_type -> [websocket_ids], pillar -> [websocket_ids]
    """
    
    def __init__(self, messaging_abstraction: Any):
        """
        Initialize Traffic Cop Connection Registry.
        
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
        
        # Default TTL for connections (1 hour, extendable via heartbeat)
        self.default_ttl = 3600  # seconds
        
        self.logger.info("✅ Traffic Cop Connection Registry initialized (Redis-backed)")
    
    async def register_connection(
        self,
        websocket_id: str,
        session_id: str,
        agent_type: Optional[str] = None,
        pillar: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register WebSocket connection in Redis.
        
        Args:
            websocket_id: Unique WebSocket connection identifier
            session_id: Traffic Cop session ID
            agent_type: Type of agent ("guide" or "liaison")
            pillar: Pillar name for liaison agents (content, insights, etc.)
            metadata: Additional connection metadata
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Build connection key
            connection_key = f"traffic_cop:session:{session_id}:websocket:{websocket_id}"
            
            # Prepare connection data
            connection_data = {
                "websocket_id": websocket_id,
                "session_id": session_id,
                "agent_type": agent_type or "",
                "pillar": pillar or "",
                "linked_at": datetime.utcnow().isoformat(),
                "status": "active",
                "metadata": json.dumps(metadata) if isinstance(metadata, dict) else (metadata or "{}")
            }
            
            # Store in Redis using direct Redis client
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
            
            # Set TTL
            expire_method = getattr(self.redis_client, 'expire', None)
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(connection_key, self.default_ttl)
            else:
                self.redis_client.expire(connection_key, self.default_ttl)
            
            # Add to session index
            session_index_key = f"traffic_cop:session:{session_id}:websockets"
            sadd_method = getattr(self.redis_client, 'sadd', None)
            if sadd_method and inspect.iscoroutinefunction(sadd_method):
                await self.redis_client.sadd(session_index_key, websocket_id)
            else:
                self.redis_client.sadd(session_index_key, websocket_id)
            
            if expire_method and inspect.iscoroutinefunction(expire_method):
                await self.redis_client.expire(session_index_key, self.default_ttl)
            else:
                self.redis_client.expire(session_index_key, self.default_ttl)
            
            # Add to agent_type index (if specified)
            if agent_type:
                agent_index_key = f"traffic_cop:agent_type:{agent_type}:websockets"
                if sadd_method and inspect.iscoroutinefunction(sadd_method):
                    await self.redis_client.sadd(agent_index_key, websocket_id)
                else:
                    self.redis_client.sadd(agent_index_key, websocket_id)
                
                if expire_method and inspect.iscoroutinefunction(expire_method):
                    await self.redis_client.expire(agent_index_key, self.default_ttl)
                else:
                    self.redis_client.expire(agent_index_key, self.default_ttl)
            
            # Add to pillar index (if specified)
            if pillar:
                pillar_index_key = f"traffic_cop:pillar:{pillar}:websockets"
                if sadd_method and inspect.iscoroutinefunction(sadd_method):
                    await self.redis_client.sadd(pillar_index_key, websocket_id)
                else:
                    self.redis_client.sadd(pillar_index_key, websocket_id)
                
                if expire_method and inspect.iscoroutinefunction(expire_method):
                    await self.redis_client.expire(pillar_index_key, self.default_ttl)
                else:
                    self.redis_client.expire(pillar_index_key, self.default_ttl)
            
            # Verify registration
            verify_conn = await self.get_connection(websocket_id, session_id)
            if verify_conn:
                self.logger.debug(f"✅ Connection registered in Redis: {websocket_id} (session: {session_id})")
            else:
                self.logger.warning(f"⚠️ Connection registration may have failed: {websocket_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register connection {websocket_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def get_connection(
        self,
        websocket_id: str,
        session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get connection metadata from Redis.
        
        Args:
            websocket_id: WebSocket connection identifier
            session_id: Optional session ID (if not provided, will search all sessions)
            
        Returns:
            Connection metadata dict or None if not found
        """
        try:
            # If session_id is provided, use direct lookup
            if session_id:
                connection_key = f"traffic_cop:session:{session_id}:websocket:{websocket_id}"
            else:
                # Search pattern (slower, but works if session_id unknown)
                # Try common session patterns first
                connection_key = None
                # For now, require session_id for efficiency
                if not session_id:
                    self.logger.warning("⚠️ get_connection called without session_id - may be inefficient")
                    return None
            
            if not connection_key:
                return None
            
            # Get connection data
            import inspect
            hgetall_method = getattr(self.redis_client, 'hgetall', None)
            if hgetall_method and inspect.iscoroutinefunction(hgetall_method):
                data = await self.redis_client.hgetall(connection_key)
            else:
                data = self.redis_client.hgetall(connection_key)
            
            # Convert bytes to strings if needed
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
            self.logger.error(f"❌ Failed to get connection {websocket_id}: {e}")
            return None
    
    async def get_session_connections(
        self,
        session_id: str,
        agent_type: Optional[str] = None,
        pillar: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all connections for a session, optionally filtered by agent_type and pillar.
        
        Args:
            session_id: Traffic Cop session ID
            agent_type: Optional filter by agent type
            pillar: Optional filter by pillar
            
        Returns:
            List of connection metadata dicts
        """
        try:
            connections = []
            
            # Get all websocket_ids for this session
            session_index_key = f"traffic_cop:session:{session_id}:websockets"
            import inspect
            smembers_method = getattr(self.redis_client, 'smembers', None)
            if smembers_method and inspect.iscoroutinefunction(smembers_method):
                websocket_ids = await self.redis_client.smembers(session_index_key)
            else:
                websocket_ids = self.redis_client.smembers(session_index_key)
            
            # Convert bytes to strings if needed
            if websocket_ids:
                websocket_ids = [w.decode('utf-8') if isinstance(w, bytes) else w for w in websocket_ids]
            
            # Get connection data for each websocket_id
            for websocket_id in websocket_ids:
                conn = await self.get_connection(websocket_id, session_id)
                if conn:
                    # Apply filters
                    if agent_type and conn.get("agent_type") != agent_type:
                        continue
                    if pillar and conn.get("pillar") != pillar:
                        continue
                    connections.append(conn)
            
            return connections
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session connections for {session_id}: {e}")
            return []
    
    async def unregister_connection(
        self,
        websocket_id: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Unregister connection from Redis.
        
        Args:
            websocket_id: WebSocket connection identifier
            session_id: Optional session ID (if not provided, will search)
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            # Get connection info before deletion
            conn = await self.get_connection(websocket_id, session_id)
            if not conn:
                return True  # Already removed
            
            session_id = conn.get("session_id") or session_id
            agent_type = conn.get("agent_type")
            pillar = conn.get("pillar")
            
            if not session_id:
                self.logger.warning(f"⚠️ Cannot unregister connection {websocket_id} - no session_id")
                return False
            
            # Remove from session index
            session_index_key = f"traffic_cop:session:{session_id}:websockets"
            import inspect
            srem_method = getattr(self.redis_client, 'srem', None)
            if srem_method and inspect.iscoroutinefunction(srem_method):
                await self.redis_client.srem(session_index_key, websocket_id)
            else:
                self.redis_client.srem(session_index_key, websocket_id)
            
            # Remove from agent_type index
            if agent_type:
                agent_index_key = f"traffic_cop:agent_type:{agent_type}:websockets"
                if srem_method and inspect.iscoroutinefunction(srem_method):
                    await self.redis_client.srem(agent_index_key, websocket_id)
                else:
                    self.redis_client.srem(agent_index_key, websocket_id)
            
            # Remove from pillar index
            if pillar:
                pillar_index_key = f"traffic_cop:pillar:{pillar}:websockets"
                if srem_method and inspect.iscoroutinefunction(srem_method):
                    await self.redis_client.srem(pillar_index_key, websocket_id)
                else:
                    self.redis_client.srem(pillar_index_key, websocket_id)
            
            # Delete connection record
            connection_key = f"traffic_cop:session:{session_id}:websocket:{websocket_id}"
            delete_method = getattr(self.redis_client, 'delete', None)
            if delete_method and inspect.iscoroutinefunction(delete_method):
                await self.redis_client.delete(connection_key)
            else:
                self.redis_client.delete(connection_key)
            
            self.logger.debug(f"✅ Connection unregistered from Redis: {websocket_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to unregister connection {websocket_id}: {e}")
            return False
    
    async def update_connection_activity(self, websocket_id: str, session_id: str) -> bool:
        """Update last activity timestamp for connection."""
        try:
            connection_key = f"traffic_cop:session:{session_id}:websocket:{websocket_id}"
            
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
            self.logger.error(f"❌ Failed to update activity for {websocket_id}: {e}")
            return False

