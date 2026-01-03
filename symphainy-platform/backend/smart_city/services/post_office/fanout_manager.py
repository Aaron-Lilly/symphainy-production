#!/usr/bin/env python3
"""
Fan-Out Manager - Redis Message Distribution

Manages message fan-out to multiple WebSocket connections via Redis Pub/Sub.
Handles cross-instance message routing for horizontal scaling.

WHAT: I distribute messages to all WebSocket connections subscribed to channels
HOW: I use Redis Pub/Sub for efficient fan-out across gateway instances
"""

import json
import logging
import asyncio
from typing import Dict, Any, Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FanOutManager:
    """
    Manages message fan-out via Redis Pub/Sub.
    
    Enables horizontal scaling by allowing multiple gateway instances
    to coordinate message distribution to WebSocket connections.
    """
    
    def __init__(self, messaging_abstraction: Any, connection_registry: Any):
        """
        Initialize Fan-Out Manager.
        
        Args:
            messaging_abstraction: Redis messaging abstraction
            connection_registry: ConnectionRegistry instance
        """
        self.messaging_abstraction = messaging_abstraction
        self.connection_registry = connection_registry
        self.logger = logger
        
        # Active subscriptions per gateway instance
        self.active_subscriptions: Dict[str, Any] = {}  # channel -> pubsub
        
        # Background tasks
        self.subscription_tasks: Dict[str, asyncio.Task] = {}
        
        self.logger.info("✅ Fan-Out Manager initialized")
    
    async def start_channel_subscription(self, channel: str, gateway_instance_id: str, local_connections: Dict[str, Any]):
        """
        Start subscribing to Redis channel for message fan-out.
        
        Args:
            channel: Channel name (e.g., "guide", "pillar:content")
            gateway_instance_id: ID of this gateway instance
            local_connections: Dict of connection_id -> WebSocket for local connections
        """
        try:
            redis_channel = f"websocket:{channel}"
            
            # Check if already subscribed
            if redis_channel in self.active_subscriptions:
                self.logger.debug(f"Already subscribed to {redis_channel}")
                return
            
            # Create pubsub subscription
            if hasattr(self.messaging_abstraction, 'pubsub'):
                pubsub = self.messaging_abstraction.pubsub()
                await pubsub.subscribe(redis_channel)
                
                self.active_subscriptions[redis_channel] = pubsub
                
                # Start background task to handle messages
                task = asyncio.create_task(
                    self._handle_channel_messages(
                        redis_channel,
                        pubsub,
                        gateway_instance_id,
                        local_connections
                    )
                )
                self.subscription_tasks[redis_channel] = task
                
                self.logger.info(f"✅ Subscribed to {redis_channel} for fan-out")
            else:
                self.logger.warning(f"⚠️ Pub/Sub not available in messaging abstraction")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start subscription for {channel}: {e}")
    
    async def _handle_channel_messages(
        self,
        redis_channel: str,
        pubsub: Any,
        gateway_instance_id: str,
        local_connections: Dict[str, Any]
    ):
        """Background task to handle messages from Redis channel."""
        try:
            self.logger.debug(f"📡 Listening for messages on {redis_channel}")
            
            async for message in pubsub.listen():
                if message.get('type') == 'message':
                    try:
                        # Parse message
                        data = json.loads(message.get('data', '{}'))
                        
                        # Get all connections for this channel (from Redis)
                        connection_ids = await self.connection_registry.get_connections_by_channel(
                            redis_channel.replace("websocket:", "")
                        )
                        
                        # Filter to only local connections
                        local_connection_ids = [
                            conn_id for conn_id in connection_ids
                            if conn_id in local_connections
                        ]
                        
                        # Fan-out to local connections
                        for connection_id in local_connection_ids:
                            websocket = local_connections.get(connection_id)
                            if websocket:
                                try:
                                    await websocket.send_json(data)
                                    self.logger.debug(f"✅ Fanned out message to {connection_id}")
                                except Exception as e:
                                    self.logger.warning(f"⚠️ Failed to send to {connection_id}: {e}")
                                    # Connection might be dead, will be cleaned up by eviction
                        
                        # Log fan-out metrics
                        if len(local_connection_ids) > 0:
                            self.logger.debug(
                                f"📤 Fanned out message to {len(local_connection_ids)} local connections "
                                f"(total: {len(connection_ids)})"
                            )
                            
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"⚠️ Invalid JSON in message from {redis_channel}: {e}")
                    except Exception as e:
                        self.logger.error(f"❌ Error handling message from {redis_channel}: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Error in channel message handler for {redis_channel}: {e}")
            # Remove subscription on error
            if redis_channel in self.active_subscriptions:
                del self.active_subscriptions[redis_channel]
            if redis_channel in self.subscription_tasks:
                self.subscription_tasks[redis_channel].cancel()
                del self.subscription_tasks[redis_channel]
    
    async def publish_to_channel(
        self,
        channel: str,
        message: Dict[str, Any],
        source_connection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish message to Redis channel for fan-out.
        
        Args:
            channel: Channel name
            message: Message to publish
            source_connection_id: Optional connection ID that sent the message (to exclude from fan-out)
            
        Returns:
            Dict with publish status
        """
        try:
            redis_channel = f"websocket:{channel}"
            
            # Add metadata
            message_with_metadata = {
                "channel": channel,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "source_connection_id": source_connection_id
            }
            
            # Publish to Redis
            if hasattr(self.messaging_abstraction, 'publish'):
                subscribers = await self.messaging_abstraction.publish(
                    redis_channel,
                    json.dumps(message_with_metadata)
                )
                
                self.logger.debug(f"📤 Published to {redis_channel} ({subscribers} subscribers)")
                
                return {
                    "success": True,
                    "channel": redis_channel,
                    "subscribers": subscribers
                }
            elif hasattr(self.messaging_abstraction, 'send_message'):
                await self.messaging_abstraction.send_message(
                    redis_channel,
                    message_with_metadata
                )
                return {
                    "success": True,
                    "channel": redis_channel
                }
            else:
                return {
                    "success": False,
                    "error": "Publish not available in messaging abstraction"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to publish to channel {channel}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_channel_subscription(self, channel: str):
        """Stop subscribing to Redis channel."""
        try:
            redis_channel = f"websocket:{channel}"
            
            if redis_channel in self.active_subscriptions:
                pubsub = self.active_subscriptions[redis_channel]
                await pubsub.unsubscribe(redis_channel)
                del self.active_subscriptions[redis_channel]
            
            if redis_channel in self.subscription_tasks:
                task = self.subscription_tasks[redis_channel]
                task.cancel()
                del self.subscription_tasks[redis_channel]
            
            self.logger.info(f"✅ Stopped subscription to {redis_channel}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop subscription for {channel}: {e}")
    
    async def shutdown(self):
        """Shutdown fan-out manager and clean up subscriptions."""
        try:
            # Stop all subscriptions
            channels = list(self.active_subscriptions.keys())
            for redis_channel in channels:
                channel = redis_channel.replace("websocket:", "")
                await self.stop_channel_subscription(channel)
            
            # Cancel all tasks
            for task in self.subscription_tasks.values():
                task.cancel()
            
            self.logger.info("✅ Fan-Out Manager shut down")
            
        except Exception as e:
            self.logger.error(f"❌ Error shutting down Fan-Out Manager: {e}")

