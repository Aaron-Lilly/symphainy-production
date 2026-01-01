#!/usr/bin/env python3
"""
Redis Event Bus Adapter - Layer 1 of 5-Layer Architecture

This adapter provides raw, technology-specific bindings for Redis Streams event bus.
It's a thin wrapper around the Redis client, exposing core event operations.

WHAT (Infrastructure Role): I provide raw Redis Streams bindings for event bus
HOW (Infrastructure Implementation): I use Redis Streams with direct commands
"""

import json
import uuid
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.exceptions import RedisError

from foundations.public_works_foundation.abstraction_contracts.event_management_protocol import (
    EventContext, EventPriority, EventStatus
)

class RedisEventBusAdapter:
    """
    Redis Event Bus Adapter.

    Provides raw Redis Streams bindings for event bus operations.
    """

    def __init__(self, redis_client: redis.Redis, service_name: str = "redis_event_bus_adapter", di_container=None):
        """Initialize Redis Event Bus Adapter with a Redis client."""
        if not di_container:
            raise ValueError("DI Container is required for RedisEventBusAdapter initialization")
        self.redis_client = redis_client
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"RedisEventBusAdapter-{service_name}")
        self.is_connected = False
        
        # Event stream configuration
        self.stream_prefix = "events:"
        self.consumer_groups: Dict[str, str] = {}
        self.subscriptions: Dict[str, List[Callable]] = {}

        self.logger.info(f"✅ Redis Event Bus Adapter '{service_name}' initialized")

    async def connect(self) -> bool:
        """Test Redis connection."""
        try:
            await self.redis_client.ping()
            self.is_connected = True
            self.logger.info(f"✅ Redis connection established for '{self.service_name}'")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("connect", {
                    "service": self.service_name,
                    "success": True
                })
            
            return True
        except RedisError as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "connect",
                    "error_type": "RedisError",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to connect to Redis for '{self.service_name}': {e}")
            self.is_connected = False
            raise
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "connect",
                    "error_type": "Unexpected",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Unexpected error during Redis connection for '{self.service_name}': {e}")
            self.is_connected = False
            raise

    async def publish_event(self, event_type: str, source: str, target: str, 
                          event_data: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL,
                          correlation_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[EventContext]:
        """
        Publish an event to Redis Streams.
        """
        if not self.is_connected:
            await self.connect()

        try:
            event_id = str(uuid.uuid4())
            stream_name = f"{self.stream_prefix}{event_type}"
            
            # Create event context
            event_context = EventContext(
                event_id=event_id,
                event_type=event_type,
                source=source,
                target=target,
                priority=priority,
                status=EventStatus.PENDING,
                created_at=datetime.utcnow(),
                event_data=event_data,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Prepare stream data
            stream_data = {
                "event_id": event_id,
                "event_type": event_type,
                "source": source,
                "target": target,
                "priority": priority.value,
                "status": EventStatus.PENDING.value,
                "created_at": event_context.created_at.isoformat(),
                "event_data": json.dumps(event_data),
                "correlation_id": correlation_id or "",
                "tenant_id": tenant_id or ""
            }
            
            # Publish to Redis Stream
            stream_id = await self.redis_client.xadd(stream_name, stream_data)
            
            # Store event context for later retrieval
            event_key = f"event:{event_id}"
            await self.redis_client.hset(event_key, mapping={
                "event_id": event_id,
                "event_type": event_type,
                "source": source,
                "target": target,
                "priority": priority.value,
                "status": EventStatus.PENDING.value,
                "created_at": event_context.created_at.isoformat(),
                "event_data": json.dumps(event_data),
                "correlation_id": correlation_id or "",
                "tenant_id": tenant_id or ""
            })
            
            # Set TTL for event storage (24 hours)
            await self.redis_client.expire(event_key, 86400)

            self.logger.info(f"✅ Published event {event_id} to stream {stream_name}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("publish_event", {
                    "event_id": event_id,
                    "event_type": event_type,
                    "stream_name": stream_name,
                    "success": True
                })
            
            return event_context
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "publish_event",
                    "event_type": event_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error publishing event: {e}")
            return None

    async def subscribe_to_events(self, event_type: str, callback: Callable[[EventContext], None], 
                                 consumer_group: Optional[str] = None) -> bool:
        """
        Subscribe to events of a specific type.
        """
        if not self.is_connected:
            await self.connect()

        try:
            stream_name = f"{self.stream_prefix}{event_type}"
            group_name = consumer_group or f"group_{event_type}"
            
            # Create consumer group if it doesn't exist
            try:
                await self.redis_client.xgroup_create(stream_name, group_name, id="0", mkstream=True)
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise e
            
            # Store subscription
            if event_type not in self.subscriptions:
                self.subscriptions[event_type] = []
            self.subscriptions[event_type].append(callback)
            
            self.consumer_groups[event_type] = group_name
            
            self.logger.info(f"✅ Subscribed to events of type {event_type} with group {group_name}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("subscribe_to_events", {
                    "event_type": event_type,
                    "consumer_group": group_name,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "subscribe_to_events",
                    "event_type": event_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error subscribing to events: {e}")
            return False

    async def unsubscribe_from_events(self, event_type: str, consumer_group: Optional[str] = None) -> bool:
        """
        Unsubscribe from events of a specific type.
        """
        if not self.is_connected:
            await self.connect()

        try:
            if event_type in self.subscriptions:
                del self.subscriptions[event_type]
            
            if event_type in self.consumer_groups:
                del self.consumer_groups[event_type]
            
            self.logger.info(f"✅ Unsubscribed from events of type {event_type}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("unsubscribe_from_events", {
                    "event_type": event_type,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "unsubscribe_from_events",
                    "event_type": event_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error unsubscribing from events: {e}")
            return False

    async def get_event(self, event_id: str) -> Optional[EventContext]:
        """
        Get event by ID.
        """
        if not self.is_connected:
            await self.connect()

        try:
            event_key = f"event:{event_id}"
            event_data = await self.redis_client.hgetall(event_key)
            
            if not event_data:
                return None
            
            # Reconstruct EventContext
            event_context = EventContext(
                event_id=event_data.get("event_id"),
                event_type=event_data.get("event_type"),
                source=event_data.get("source"),
                target=event_data.get("target"),
                priority=EventPriority(event_data.get("priority", "normal")),
                status=EventStatus(event_data.get("status", "pending")),
                created_at=datetime.fromisoformat(event_data.get("created_at")),
                processed_at=datetime.fromisoformat(event_data.get("processed_at")) if event_data.get("processed_at") else None,
                event_data=json.loads(event_data.get("event_data", "{}")),
                correlation_id=event_data.get("correlation_id") or None,
                tenant_id=event_data.get("tenant_id") or None
            )
            
            self.logger.debug(f"✅ Retrieved event {event_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_event", {
                    "event_id": event_id,
                    "found": event_context is not None,
                    "success": True
                })
            
            return event_context
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_event",
                    "event_id": event_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting event {event_id}: {e}")
            return None

    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[EventContext]:
        """
        Get events by type.
        """
        if not self.is_connected:
            await self.connect()

        try:
            stream_name = f"{self.stream_prefix}{event_type}"
            
            # Read from stream
            streams = {stream_name: "0"}
            result = await self.redis_client.xread(streams, count=limit)
            
            events = []
            for stream, messages in result:
                for message_id, fields in messages:
                    event_context = EventContext(
                        event_id=fields.get("event_id"),
                        event_type=fields.get("event_type"),
                        source=fields.get("source"),
                        target=fields.get("target"),
                        priority=EventPriority(fields.get("priority", "normal")),
                        status=EventStatus(fields.get("status", "pending")),
                        created_at=datetime.fromisoformat(fields.get("created_at")),
                        event_data=json.loads(fields.get("event_data", "{}")),
                        correlation_id=fields.get("correlation_id") or None,
                        tenant_id=fields.get("tenant_id") or None
                    )
                    events.append(event_context)
            
            self.logger.debug(f"✅ Retrieved {len(events)} events of type {event_type}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_events_by_type", {
                    "event_type": event_type,
                    "event_count": len(events),
                    "success": True
                })
            
            return events
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_events_by_type",
                    "event_type": event_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting events by type {event_type}: {e}")
            return []

    async def get_events_by_tenant(self, tenant_id: str, limit: int = 100) -> List[EventContext]:
        """
        Get events by tenant ID.
        """
        if not self.is_connected:
            await self.connect()

        try:
            # This would require scanning all event keys
            # In production, you'd use RedisSearch or maintain a tenant index
            pattern = "event:*"
            keys = await self.redis_client.keys(pattern)
            
            events = []
            for key in keys[:limit]:  # Limit for performance
                event_data = await self.redis_client.hgetall(key)
                if event_data.get("tenant_id") == tenant_id:
                    event_context = EventContext(
                        event_id=event_data.get("event_id"),
                        event_type=event_data.get("event_type"),
                        source=event_data.get("source"),
                        target=event_data.get("target"),
                        priority=EventPriority(event_data.get("priority", "normal")),
                        status=EventStatus(event_data.get("status", "pending")),
                        created_at=datetime.fromisoformat(event_data.get("created_at")),
                        event_data=json.loads(event_data.get("event_data", "{}")),
                        correlation_id=event_data.get("correlation_id") or None,
                        tenant_id=event_data.get("tenant_id") or None
                    )
                    events.append(event_context)
            
            self.logger.debug(f"✅ Retrieved {len(events)} events for tenant {tenant_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_events_by_tenant", {
                    "tenant_id": tenant_id,
                    "event_count": len(events),
                    "success": True
                })
            
            return events
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_events_by_tenant",
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting events by tenant {tenant_id}: {e}")
            return []

    async def acknowledge_event(self, event_id: str, consumer_group: str) -> bool:
        """
        Acknowledge an event.
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Update event status
            event_key = f"event:{event_id}"
            await self.redis_client.hset(event_key, "status", EventStatus.COMPLETED.value)
            await self.redis_client.hset(event_key, "processed_at", datetime.utcnow().isoformat())
            
            self.logger.info(f"✅ Acknowledged event {event_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("acknowledge_event", {
                    "event_id": event_id,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "acknowledge_event",
                    "event_id": event_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error acknowledging event {event_id}: {e}")
            return False

    async def get_event_metrics(self) -> Dict[str, Any]:
        """
        Get event bus metrics.
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Get stream info for all event streams
            pattern = f"{self.stream_prefix}*"
            stream_names = await self.redis_client.keys(pattern)
            
            metrics = {
                "total_streams": len(stream_names),
                "active_subscriptions": len(self.subscriptions),
                "consumer_groups": len(self.consumer_groups),
                "streams": {}
            }
            
            for stream_name in stream_names:
                try:
                    info = await self.redis_client.xinfo_stream(stream_name)
                    metrics["streams"][stream_name] = {
                        "length": info.get("length", 0),
                        "groups": info.get("groups", 0),
                        "first_entry": info.get("first-entry"),
                        "last_entry": info.get("last-entry")
                    }
                except Exception as e:
                    # Use error handler for nested exception
                    error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                    if error_handler:
                        await error_handler.handle_error(e, {
                            "operation": "get_event_metrics",
                            "stream_name": stream_name,
                            "service": self.service_name
                        })
                    else:
                        self.logger.warning(f"⚠️ Could not get info for stream {stream_name}: {e}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_event_metrics", {
                    "total_streams": metrics.get("total_streams", 0),
                    "success": True
                })
            
            return metrics
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_event_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting event metrics: {e}")
            return {"error": str(e)}

    async def cleanup_processed_events(self, older_than_hours: int = 24) -> int:
        """
        Clean up processed events older than specified hours.
        """
        if not self.is_connected:
            await self.connect()

        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            pattern = "event:*"
            keys = await self.redis_client.keys(pattern)
            
            cleaned_count = 0
            for key in keys:
                event_data = await self.redis_client.hgetall(key)
                if event_data.get("status") == EventStatus.COMPLETED.value:
                    created_at = datetime.fromisoformat(event_data.get("created_at"))
                    if created_at < cutoff_time:
                        await self.redis_client.delete(key)
                        cleaned_count += 1
            
            self.logger.info(f"✅ Cleaned up {cleaned_count} processed events")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("cleanup_processed_events", {
                    "cleaned_count": cleaned_count,
                    "success": True
                })
            
            return cleaned_count
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "cleanup_processed_events",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error cleaning up processed events: {e}")
            return 0



