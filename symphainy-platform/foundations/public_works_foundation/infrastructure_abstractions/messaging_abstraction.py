#!/usr/bin/env python3
"""
Messaging Abstraction - Generic Infrastructure Implementation

Generic messaging implementation using real adapters.
This is Layer 3 of the 5-layer architecture for Post Office messaging.

WHAT (Infrastructure Role): I provide generic messaging services
HOW (Infrastructure Implementation): I use real adapters with generic interfaces
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.messaging_protocol import (
    MessagingProtocol, MessageContext, MessagePriority, MessageStatus, MessageType
)
from foundations.public_works_foundation.infrastructure_adapters.redis_messaging_adapter import RedisMessagingAdapter
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter

logger = logging.getLogger(__name__)

class MessagingAbstraction(MessagingProtocol):
    """
    Generic messaging abstraction using real adapters.

    This abstraction implements the MessagingProtocol using a real
    RedisMessagingAdapter and ConfigAdapter, providing a generic interface.
    """

    def __init__(self, messaging_adapter: RedisMessagingAdapter, config_adapter: ConfigAdapter, di_container=None):
        """
        Initialize Messaging abstraction with real adapters.
        
        Args:
            messaging_adapter: Redis messaging adapter
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.messaging_adapter = messaging_adapter
        self.config = config_adapter
        self.di_container = di_container
        self.service_name = "messaging_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)

        # Messaging configuration
        self.default_retention_hours = 168  # 7 days
        self.max_messages_per_recipient = 1000

        self.logger.info("✅ Messaging abstraction initialized with real adapters")

    async def send_message(self, message_type: MessageType, sender: str, recipient: str,
                         message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> Optional[MessageContext]:
        """
        Send a message.
        
        Returns:
            MessageContext if successful, None otherwise
        """
        start_time = time.time()
        try:
            message_context = await self.messaging_adapter.send_message(
                message_type=message_type,
                sender=sender,
                recipient=recipient,
                message_content=message_content,
                priority=priority,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            if message_context:
                duration_ms = (time.time() - start_time) * 1000
                self.logger.info(f"✅ Sent message {message_context.message_id} from {sender} to {recipient} (took {duration_ms:.2f}ms)")
            
            return message_context
        except Exception as e:
            self.logger.error(f"❌ Error sending message from {sender} to {recipient}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def send_broadcast_message(self, message_type: MessageType, sender: str, recipients: List[str],
                                   message_content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> List[MessageContext]:
        """
        Send a broadcast message to multiple recipients.
        """
        start_time = time.time()
        try:
            message_contexts = await self.messaging_adapter.send_broadcast_message(
                message_type=message_type,
                sender=sender,
                recipients=recipients,
                message_content=message_content,
                priority=priority,
                tenant_id=tenant_id
            )
            duration_ms = (time.time() - start_time) * 1000
            self.logger.info(f"✅ Sent broadcast message to {len(message_contexts)} recipients (took {duration_ms:.2f}ms)")
            
            return message_contexts
        except Exception as e:
            self.logger.error(f"❌ Error sending broadcast message to {len(recipients)} recipients: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_message(self, message_id: str) -> Optional[MessageContext]:
        """
        Get message by ID.
        """
        try:
            message_context = await self.messaging_adapter.get_message(message_id)
            if message_context:
                self.logger.debug(f"✅ Retrieved message {message_id}")
            return message_context
        except Exception as e:
            self.logger.error(f"❌ Error getting message {message_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_messages_for_recipient(self, recipient: str, limit: int = 100) -> List[MessageContext]:
        """
        Get messages for a specific recipient.
        """
        try:
            messages = await self.messaging_adapter.get_messages_for_recipient(recipient, limit)
            self.logger.debug(f"✅ Retrieved {len(messages)} messages for recipient {recipient}")
            return messages
        except Exception as e:
            self.logger.error(f"❌ Error getting messages for recipient {recipient}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_messages_by_type(self, message_type: MessageType, limit: int = 100) -> List[MessageContext]:
        """
        Get messages by type.
        """
        try:
            messages = await self.messaging_adapter.get_messages_by_type(message_type, limit)
            self.logger.debug(f"✅ Retrieved {len(messages)} messages of type {message_type.value}")
            return messages
        except Exception as e:
            self.logger.error(f"❌ Error getting messages by type {message_type.value}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_messages_by_tenant(self, tenant_id: str, limit: int = 100) -> List[MessageContext]:
        """
        Get messages by tenant ID.
        """
        try:
            messages = await self.messaging_adapter.get_messages_by_tenant(tenant_id, limit)
            self.logger.debug(f"✅ Retrieved {len(messages)} messages for tenant {tenant_id}")
            return messages
        except Exception as e:
            self.logger.error(f"❌ Error getting messages by tenant {tenant_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def acknowledge_message(self, message_id: str) -> bool:
        """
        Acknowledge a message.
        """
        try:
            success = await self.messaging_adapter.acknowledge_message(message_id)
            if success:
                self.logger.info(f"✅ Acknowledged message {message_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error acknowledging message {message_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def retry_failed_message(self, message_id: str) -> bool:
        """
        Retry a failed message.
        """
        try:
            success = await self.messaging_adapter.retry_failed_message(message_id)
            if success:
                self.logger.info(f"✅ Retrying message {message_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error retrying message {message_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_message_metrics(self) -> Dict[str, Any]:
        """
        Get messaging metrics.
        """
        try:
            metrics = await self.messaging_adapter.get_message_metrics()
            self.logger.debug("✅ Retrieved messaging metrics")
            return metrics
        except Exception as e:
            self.logger.error(f"❌ Error getting messaging metrics: {e}")
            raise  # Re-raise for service layer to handle
    
    async def cleanup_old_messages(self, older_than_hours: int = 24) -> int:
        """
        Clean up old messages.
        """
        try:
            cleaned_count = await self.messaging_adapter.cleanup_old_messages(older_than_hours)
            self.logger.info(f"✅ Cleaned up {cleaned_count} old messages")
            return cleaned_count
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up old messages: {e}")
            raise  # Re-raise for service layer to handle
