#!/usr/bin/env python3
"""
Redis Messaging Adapter - Layer 1 of 5-Layer Architecture

This adapter provides raw, technology-specific bindings for Redis messaging.
It's a thin wrapper around the Redis client, exposing core messaging operations.

WHAT (Infrastructure Role): I provide raw Redis bindings for messaging
HOW (Infrastructure Implementation): I use Redis with direct commands
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.exceptions import RedisError

from foundations.public_works_foundation.abstraction_contracts.messaging_protocol import (
    MessageContext, MessagePriority, MessageStatus, MessageType
)

class RedisMessagingAdapter:
    """
    Redis Messaging Adapter.

    Provides raw Redis bindings for messaging operations.
    """

    def __init__(self, redis_client: redis.Redis, service_name: str = "redis_messaging_adapter", di_container=None):
        """Initialize Redis Messaging Adapter with a Redis client."""
        if not di_container:
            raise ValueError("DI Container is required for RedisMessagingAdapter initialization")
        self.redis_client = redis_client
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"RedisMessagingAdapter-{service_name}")
        self.is_connected = False
        
        # Messaging configuration
        self.message_prefix = "messages:"
        self.recipient_prefix = "recipient:"
        self.tenant_prefix = "tenant:"

        self.logger.info(f"✅ Redis Messaging Adapter '{service_name}' initialized")

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

    async def send_message(self, message_type: MessageType, sender: str, recipient: str,
                         message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                         correlation_id: Optional[str] = None, tenant_id: Optional[str] = None) -> Optional[MessageContext]:
        """
        Send a message.
        """
        if not self.is_connected:
            await self.connect()

        try:
            message_id = str(uuid.uuid4())
            
            # Create message context
            message_context = MessageContext(
                message_id=message_id,
                message_type=message_type,
                sender=sender,
                recipient=recipient,
                priority=priority,
                status=MessageStatus.PENDING,
                created_at=datetime.utcnow(),
                message_content=message_content,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            
            # Store message
            message_key = f"{self.message_prefix}{message_id}"
            await self.redis_client.hset(message_key, mapping={
                "message_id": message_id,
                "message_type": message_type.value,
                "sender": sender,
                "recipient": recipient,
                "priority": priority.value,
                "status": MessageStatus.PENDING.value,
                "created_at": message_context.created_at.isoformat(),
                "message_content": json.dumps(message_content),
                "correlation_id": correlation_id or "",
                "tenant_id": tenant_id or "",
                "retry_count": "0",
                "max_retries": "3"
            })
            
            # Add to recipient's message list
            recipient_key = f"{self.recipient_prefix}{recipient}"
            await self.redis_client.sadd(recipient_key, message_id)
            
            # Add to tenant's message list if tenant_id provided
            if tenant_id:
                tenant_key = f"{self.tenant_prefix}{tenant_id}"
                await self.redis_client.sadd(tenant_key, message_id)
            
            # Set TTL for message storage (7 days)
            await self.redis_client.expire(message_key, 604800)
            await self.redis_client.expire(recipient_key, 604800)
            if tenant_id:
                await self.redis_client.expire(tenant_key, 604800)

            self.logger.info(f"✅ Sent message {message_id} from {sender} to {recipient}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("send_message", {
                    "message_id": message_id,
                    "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type),
                    "sender": sender,
                    "recipient": recipient,
                    "success": True
                })
            
            return message_context
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_message",
                    "sender": sender,
                    "recipient": recipient,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error sending message: {e}")
            return None

    async def send_broadcast_message(self, message_type: MessageType, sender: str, recipients: List[str],
                                   message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                                   tenant_id: Optional[str] = None) -> List[MessageContext]:
        """
        Send a broadcast message to multiple recipients.
        """
        if not self.is_connected:
            await self.connect()

        try:
            message_contexts = []
            
            for recipient in recipients:
                message_context = await self.send_message(
                    message_type=message_type,
                    sender=sender,
                    recipient=recipient,
                    message_content=message_content,
                    priority=priority,
                    tenant_id=tenant_id
                )
                
                if message_context:
                    message_contexts.append(message_context)
            
            self.logger.info(f"✅ Sent broadcast message to {len(message_contexts)} recipients")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("send_broadcast_message", {
                    "recipient_count": len(recipients),
                    "sent_count": len(message_contexts),
                    "success": True
                })
            
            return message_contexts
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "send_broadcast_message",
                    "recipient_count": len(recipients),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error sending broadcast message: {e}")
            return []

    async def get_message(self, message_id: str) -> Optional[MessageContext]:
        """
        Get message by ID.
        """
        if not self.is_connected:
            await self.connect()

        try:
            message_key = f"{self.message_prefix}{message_id}"
            message_data = await self.redis_client.hgetall(message_key)
            
            if not message_data:
                return None
            
            # Reconstruct MessageContext
            message_context = MessageContext(
                message_id=message_data.get("message_id"),
                message_type=MessageType(message_data.get("message_type")),
                sender=message_data.get("sender"),
                recipient=message_data.get("recipient"),
                priority=MessagePriority(message_data.get("priority", "normal")),
                status=MessageStatus(message_data.get("status", "pending")),
                created_at=datetime.fromisoformat(message_data.get("created_at")),
                sent_at=datetime.fromisoformat(message_data.get("sent_at")) if message_data.get("sent_at") else None,
                delivered_at=datetime.fromisoformat(message_data.get("delivered_at")) if message_data.get("delivered_at") else None,
                message_content=json.loads(message_data.get("message_content", "{}")),
                correlation_id=message_data.get("correlation_id") or None,
                tenant_id=message_data.get("tenant_id") or None,
                retry_count=int(message_data.get("retry_count", 0)),
                max_retries=int(message_data.get("max_retries", 3))
            )
            
            self.logger.debug(f"✅ Retrieved message {message_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_message", {
                    "message_id": message_id,
                    "found": message_context is not None,
                    "success": True
                })
            
            return message_context
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_message",
                    "message_id": message_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting message {message_id}: {e}")
            return None

    async def get_messages_for_recipient(self, recipient: str, limit: int = 100) -> List[MessageContext]:
        """
        Get messages for a specific recipient.
        """
        if not self.is_connected:
            await self.connect()

        try:
            recipient_key = f"{self.recipient_prefix}{recipient}"
            message_ids = await self.redis_client.smembers(recipient_key)
            
            messages = []
            for message_id_bytes in list(message_ids)[:limit]:
                message_id = message_id_bytes.decode('utf-8')
                message_context = await self.get_message(message_id)
                if message_context:
                    messages.append(message_context)
            
            self.logger.debug(f"✅ Retrieved {len(messages)} messages for recipient {recipient}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_messages_for_recipient", {
                    "recipient": recipient,
                    "message_count": len(messages),
                    "success": True
                })
            
            return messages
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_messages_for_recipient",
                    "recipient": recipient,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting messages for recipient {recipient}: {e}")
            return []

    async def get_messages_by_type(self, message_type: MessageType, limit: int = 100) -> List[MessageContext]:
        """
        Get messages by type.
        """
        if not self.is_connected:
            await self.connect()

        try:
            # This would require scanning all message keys
            # In production, you'd use RedisSearch or maintain a type index
            pattern = f"{self.message_prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            messages = []
            for key in keys[:limit]:  # Limit for performance
                message_data = await self.redis_client.hgetall(key)
                if message_data.get("message_type") == message_type.value:
                    message_context = MessageContext(
                        message_id=message_data.get("message_id"),
                        message_type=MessageType(message_data.get("message_type")),
                        sender=message_data.get("sender"),
                        recipient=message_data.get("recipient"),
                        priority=MessagePriority(message_data.get("priority", "normal")),
                        status=MessageStatus(message_data.get("status", "pending")),
                        created_at=datetime.fromisoformat(message_data.get("created_at")),
                        message_content=json.loads(message_data.get("message_content", "{}")),
                        correlation_id=message_data.get("correlation_id") or None,
                        tenant_id=message_data.get("tenant_id") or None,
                        retry_count=int(message_data.get("retry_count", 0)),
                        max_retries=int(message_data.get("max_retries", 3))
                    )
                    messages.append(message_context)
            
            self.logger.debug(f"✅ Retrieved {len(messages)} messages of type {message_type.value}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_messages_by_type", {
                    "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type),
                    "message_count": len(messages),
                    "success": True
                })
            
            return messages
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_messages_by_type",
                    "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting messages by type {message_type.value}: {e}")
            return []

    async def get_messages_by_tenant(self, tenant_id: str, limit: int = 100) -> List[MessageContext]:
        """
        Get messages by tenant ID.
        """
        if not self.is_connected:
            await self.connect()

        try:
            tenant_key = f"{self.tenant_prefix}{tenant_id}"
            message_ids = await self.redis_client.smembers(tenant_key)
            
            messages = []
            for message_id_bytes in list(message_ids)[:limit]:
                message_id = message_id_bytes.decode('utf-8')
                message_context = await self.get_message(message_id)
                if message_context:
                    messages.append(message_context)
            
            self.logger.debug(f"✅ Retrieved {len(messages)} messages for tenant {tenant_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_messages_by_tenant", {
                    "tenant_id": tenant_id,
                    "message_count": len(messages),
                    "success": True
                })
            
            return messages
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_messages_by_tenant",
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting messages for tenant {tenant_id}: {e}")
            return []

    async def acknowledge_message(self, message_id: str) -> bool:
        """
        Acknowledge a message.
        """
        if not self.is_connected:
            await self.connect()

        try:
            message_key = f"{self.message_prefix}{message_id}"
            await self.redis_client.hset(message_key, "status", MessageStatus.DELIVERED.value)
            await self.redis_client.hset(message_key, "delivered_at", datetime.utcnow().isoformat())
            
            self.logger.info(f"✅ Acknowledged message {message_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("acknowledge_message", {
                    "message_id": message_id,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "acknowledge_message",
                    "message_id": message_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error acknowledging message {message_id}: {e}")
            return False

    async def retry_failed_message(self, message_id: str) -> bool:
        """
        Retry a failed message.
        """
        if not self.is_connected:
            await self.connect()

        try:
            message_key = f"{self.message_prefix}{message_id}"
            message_data = await self.redis_client.hgetall(message_key)
            
            if not message_data:
                return False
            
            retry_count = int(message_data.get("retry_count", 0))
            max_retries = int(message_data.get("max_retries", 3))
            
            if retry_count >= max_retries:
                self.logger.warning(f"⚠️ Message {message_id} has exceeded max retries")
                return False
            
            # Update retry count and status
            await self.redis_client.hset(message_key, "retry_count", str(retry_count + 1))
            await self.redis_client.hset(message_key, "status", MessageStatus.RETRYING.value)
            
            self.logger.info(f"✅ Retrying message {message_id} (attempt {retry_count + 1})")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("retry_failed_message", {
                    "message_id": message_id,
                    "retry_count": retry_count + 1,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "retry_failed_message",
                    "message_id": message_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error retrying message {message_id}: {e}")
            return False

    async def get_message_metrics(self) -> Dict[str, Any]:
        """
        Get messaging metrics.
        """
        if not self.is_connected:
            await self.connect()

        try:
            # Get message counts by status
            pattern = f"{self.message_prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            metrics = {
                "total_messages": len(keys),
                "status_counts": {
                    "pending": 0,
                    "sent": 0,
                    "delivered": 0,
                    "failed": 0,
                    "retrying": 0
                },
                "type_counts": {},
                "tenant_counts": {}
            }
            
            for key in keys:
                message_data = await self.redis_client.hgetall(key)
                status = message_data.get("status", "pending")
                message_type = message_data.get("message_type", "unknown")
                tenant_id = message_data.get("tenant_id", "unknown")
                
                # Count by status
                if status in metrics["status_counts"]:
                    metrics["status_counts"][status] += 1
                
                # Count by type
                if message_type not in metrics["type_counts"]:
                    metrics["type_counts"][message_type] = 0
                metrics["type_counts"][message_type] += 1
                
                # Count by tenant
                if tenant_id not in metrics["tenant_counts"]:
                    metrics["tenant_counts"][tenant_id] = 0
                    metrics["tenant_counts"][tenant_id] += 1
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_message_metrics", {
                    "total_messages": metrics.get("total_messages", 0),
                    "success": True
                })
            
            return metrics
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_message_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting message metrics: {e}")
            return {"error": str(e)}

    async def cleanup_old_messages(self, older_than_hours: int = 24) -> int:
        """
        Clean up old messages.
        """
        if not self.is_connected:
            await self.connect()

        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            pattern = f"{self.message_prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            cleaned_count = 0
            for key in keys:
                message_data = await self.redis_client.hgetall(key)
                if message_data.get("status") in [MessageStatus.DELIVERED.value, MessageStatus.FAILED.value]:
                    created_at = datetime.fromisoformat(message_data.get("created_at"))
                    if created_at < cutoff_time:
                        message_id = message_data.get("message_id")
                        recipient = message_data.get("recipient")
                        tenant_id = message_data.get("tenant_id")
                        
                        # Remove from recipient and tenant sets
                        if recipient:
                            recipient_key = f"{self.recipient_prefix}{recipient}"
                            await self.redis_client.srem(recipient_key, message_id)
                        
                        if tenant_id:
                            tenant_key = f"{self.tenant_prefix}{tenant_id}"
                            await self.redis_client.srem(tenant_key, message_id)
                        
                        # Delete message
                        await self.redis_client.delete(key)
                        cleaned_count += 1
            
            self.logger.info(f"✅ Cleaned up {cleaned_count} old messages")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("cleanup_old_messages", {
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
                    "operation": "cleanup_old_messages",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error cleaning up old messages: {e}")
            return 0



