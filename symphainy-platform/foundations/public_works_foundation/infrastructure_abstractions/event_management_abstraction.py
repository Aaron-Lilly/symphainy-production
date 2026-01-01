#!/usr/bin/env python3
"""
Event Management Abstraction - Generic Infrastructure Implementation

Generic event management implementation using real adapters.
This is Layer 3 of the 5-layer architecture for Post Office event management.

WHAT (Infrastructure Role): I provide generic event management services
HOW (Infrastructure Implementation): I use real adapters with generic interfaces
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.event_management_protocol import (
    EventManagementProtocol, EventContext, EventPriority, EventStatus
)
from foundations.public_works_foundation.infrastructure_adapters.redis_event_bus_adapter import RedisEventBusAdapter
from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter

logger = logging.getLogger(__name__)

class EventManagementAbstraction(EventManagementProtocol):
    """
    Generic event management abstraction using real adapters.

    This abstraction implements the EventManagementProtocol using a real
    RedisEventBusAdapter and ConfigAdapter, providing a generic interface.
    """

    def __init__(self, event_bus_adapter: RedisEventBusAdapter, config_adapter: ConfigAdapter, di_container=None):
        """
        Initialize Event Management abstraction with real adapters.
        
        Args:
            event_bus_adapter: Redis event bus adapter
            config_adapter: Configuration adapter
            di_container: Dependency injection container
        """
        self.event_bus_adapter = event_bus_adapter
        self.config = config_adapter
        self.di_container = di_container
        self.service_name = "event_management_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)

        # Event management configuration
        self.default_retention_hours = 24
        self.max_events_per_type = 1000

        self.logger.info("✅ Event Management abstraction initialized with real adapters")

    async def publish_event(self, event_type: str, source: str, target: str, 
                          event_data: Dict[str, Any], priority: EventPriority = EventPriority.NORMAL) -> EventContext:
        """
        Publish an event.
        """
        try:
            event_context = await self.event_bus_adapter.publish_event(
                event_type=event_type,
                source=source,
                target=target,
                event_data=event_data,
                priority=priority,
                correlation_id=correlation_id,
                tenant_id=tenant_id
            )
            if event_context:
                self.logger.info(f"✅ Published event {event_context.event_id} of type {event_type}")
            
            return event_context
        except Exception as e:
            self.logger.error(f"❌ Error publishing event: {e}")
            raise  # Re-raise for service layer to handle
    
    async def subscribe_to_events(self, event_type: str, callback: Callable[[EventContext], None], 
                                 consumer_group: Optional[str] = None) -> bool:
        """
        Subscribe to events of a specific type.
        """
        try:
            success = await self.event_bus_adapter.subscribe_to_events(
                event_type=event_type,
                callback=callback,
                consumer_group=consumer_group
            )
            if success:
                self.logger.info(f"✅ Subscribed to events of type {event_type}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error subscribing to events: {e}")
            raise  # Re-raise for service layer to handle

        """
        Unsubscribe from events of a specific type.
        """
        try:
            success = await self.event_bus_adapter.unsubscribe_from_events(
                event_type=event_type,
                consumer_group=consumer_group
            )
            if success:
                self.logger.info(f"✅ Unsubscribed from events of type {event_type}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error unsubscribing from events: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get event by ID.
        """
        try:
            event_context = await self.event_bus_adapter.get_event(event_id)
            if event_context:
                self.logger.debug(f"✅ Retrieved event {event_id}")
            return event_context
        except Exception as e:
            self.logger.error(f"❌ Error getting event {event_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get events by type.
        """
        try:
            events = await self.event_bus_adapter.get_events_by_type(event_type, limit)
            self.logger.debug(f"✅ Retrieved {len(events)} events of type {event_type}")
            return events
        except Exception as e:
            self.logger.error(f"❌ Error getting events by type {event_type}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get events by tenant ID.
        """
        try:
            events = await self.event_bus_adapter.get_events_by_tenant(tenant_id, limit)
            self.logger.debug(f"✅ Retrieved {len(events)} events for tenant {tenant_id}")
            return events
        except Exception as e:
            self.logger.error(f"❌ Error getting events by tenant {tenant_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Acknowledge an event.
        """
        try:
            success = await self.event_bus_adapter.acknowledge_event(event_id, consumer_group)
            if success:
                self.logger.info(f"✅ Acknowledged event {event_id}")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error acknowledging event {event_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get event management metrics.
        """
        try:
            metrics = await self.event_bus_adapter.get_event_metrics()
            self.logger.debug("✅ Retrieved event metrics")
            return metrics
        except Exception as e:
            self.logger.error(f"❌ Error getting event metrics: {e}")
            raise  # Re-raise for service layer to handle

        """
        Clean up processed events.
        """
        try:
            cleaned_count = await self.event_bus_adapter.cleanup_processed_events(older_than_hours)
            self.logger.info(f"✅ Cleaned up {cleaned_count} processed events")
            
            return cleaned_count
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up processed events: {e}")

            raise  # Re-raise for service layer to handle
