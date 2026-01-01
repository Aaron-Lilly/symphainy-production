#!/usr/bin/env python3
"""
Event Bus Adapter - Event-driven Communication Infrastructure

Event Bus adapter that provides event-driven communication infrastructure
for all realms using existing Public Works event management abstractions.

WHAT (Infrastructure Adapter): I provide event-driven communication infrastructure
HOW (Infrastructure Implementation): I leverage Public Works event management abstractions
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Import Public Works Foundation for event management abstractions
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import DI Container for dependency injection
from foundations.di_container.di_container_service import DIContainerService

# Import existing event management abstractions from Public Works
from foundations.public_works_foundation.infrastructure_abstractions.event_management_abstraction import EventManagementAbstraction

logger = logging.getLogger(__name__)


class EventBusAdapter:
    """
    Event Bus Adapter - Event-driven Communication Infrastructure
    
    Provides event-driven communication infrastructure for all realms
    using existing Public Works event management abstractions.
    
    WHAT (Infrastructure Adapter): I provide event-driven communication infrastructure
    HOW (Infrastructure Implementation): I leverage Public Works event management abstractions
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize Event Bus Adapter."""
        self.logger = logging.getLogger("EventBusAdapter")
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Public Works event management abstraction
        self.event_management_abstraction = None
        
        # Event subscribers for different realms
        self.realm_subscribers = {
            "smart_city": {},
            "business_enablement": {},
            "experience": {},
            "journey_solution": {}
        }
        
        # Event handlers
        self.event_handlers = {}
        
        # Event bus configuration
        self.event_bus_config = {
            "default_retention_hours": 24,
            "max_events_per_type": 1000,
            "event_timeout_seconds": 300,
            "retry_attempts": 3,
            "retry_delay_seconds": 5
        }
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ Event Bus Adapter initialized")
    
    async def initialize(self):
        """Initialize Event Bus Adapter."""
        self.logger.info("🚀 Initializing Event Bus Adapter...")
        
        try:
            # Get event management abstraction from Public Works Foundation
            self.event_management_abstraction = self.public_works_foundation.get_event_management_abstraction()
            
            if not self.event_management_abstraction:
                # Create new event management abstraction if not available (migrated from Post Office)
                from foundations.public_works_foundation.infrastructure_adapters.redis_event_bus_adapter import RedisEventBusAdapter
                from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter
                
                redis_event_bus_adapter = RedisEventBusAdapter()
                config_adapter = ConfigAdapter()
                
                self.event_management_abstraction = EventManagementAbstraction(
                    event_bus_adapter=redis_event_bus_adapter,
                    config_adapter=config_adapter
                )
            
            # Initialize event management abstraction
            await self.event_management_abstraction.initialize()
            
            # Setup event handlers
            await self._setup_event_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ Event Bus Adapter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Event Bus Adapter: {e}")
            raise
    
    async def _setup_event_handlers(self):
        """Setup event handlers for different realms."""
        self.logger.info("🔧 Setting up event handlers...")
        
        # Setup realm-specific event handlers
        for realm in self.realm_subscribers.keys():
            await self._setup_realm_event_handler(realm)
        
        self.logger.info("✅ Event handlers setup complete")
    
    async def _setup_realm_event_handler(self, realm: str):
        """Setup event handler for specific realm."""
        self.logger.info(f"🔧 Setting up event handler for {realm}...")
        
        # Create realm-specific event handler
        async def realm_event_handler(event_data: Dict[str, Any]):
            """Handle events for specific realm."""
            try:
                # Process event
                await self._process_realm_event(realm, event_data)
                
            except Exception as e:
                self.logger.error(f"❌ Event handler error for {realm}: {e}")
        
        # Register handler
        self.event_handlers[realm] = realm_event_handler
        
        self.logger.info(f"✅ Event handler setup complete for {realm}")
    
    async def _process_realm_event(self, realm: str, event_data: Dict[str, Any]):
        """Process event for specific realm."""
        event_type = event_data.get("type", "unknown")
        event_content = event_data.get("content", {})
        
        if event_type == "user_action":
            await self._handle_user_action_event(realm, event_content)
        elif event_type == "system_event":
            await self._handle_system_event(realm, event_content)
        elif event_type == "business_event":
            await self._handle_business_event(realm, event_content)
        else:
            self.logger.warning(f"⚠️ Unknown event type: {event_type}")
    
    async def _handle_user_action_event(self, realm: str, event_content: Dict[str, Any]):
        """Handle user action event."""
        self.logger.info(f"📨 Handling user action event for {realm}: {event_content}")
        # This would be implemented with actual user action event handling
    
    async def _handle_system_event(self, realm: str, event_content: Dict[str, Any]):
        """Handle system event."""
        self.logger.info(f"📨 Handling system event for {realm}: {event_content}")
        # This would be implemented with actual system event handling
    
    async def _handle_business_event(self, realm: str, event_content: Dict[str, Any]):
        """Handle business event."""
        self.logger.info(f"📨 Handling business event for {realm}: {event_content}")
        # This would be implemented with actual business event handling
    
    async def start(self):
        """Start Event Bus Adapter."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting Event Bus Adapter...")
        
        try:
            # Start event management abstraction
            if self.event_management_abstraction:
                await self.event_management_abstraction.start()
            
            self.is_running = True
            self.logger.info("✅ Event Bus Adapter started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Event Bus Adapter: {e}")
            raise
    
    async def stop(self):
        """Stop Event Bus Adapter."""
        self.logger.info("🛑 Stopping Event Bus Adapter...")
        
        try:
            # Stop event management abstraction
            if self.event_management_abstraction:
                await self.event_management_abstraction.stop()
            
            self.is_running = False
            self.logger.info("✅ Event Bus Adapter stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop Event Bus Adapter: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown Event Bus Adapter."""
        await self.stop()
        self.logger.info("🔌 Event Bus Adapter shutdown complete")
    
    # Public API methods
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], 
                           source_realm: str = "system", priority: str = "normal") -> Optional[str]:
        """Publish event to event bus."""
        try:
            event_context = {
                "type": event_type,
                "data": event_data,
                "source_realm": source_realm,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use Public Works event management abstraction
            if self.event_management_abstraction:
                event_context = await self.event_management_abstraction.publish_event(
                    event_type=event_type,
                    source=source_realm,
                    target="*",  # Broadcast to all
                    event_data=event_data
                )
                
                if event_context:
                    self.logger.info(f"✅ Event published: {event_type}")
                    return event_context.event_id
                else:
                    self.logger.error(f"❌ Failed to publish event: {event_type}")
                    return None
            else:
                self.logger.error("❌ Event management abstraction not available")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to publish event: {e}")
            return None
    
    async def subscribe_to_event(self, realm: str, event_type: str, handler: Callable):
        """Subscribe to event type for realm."""
        try:
            if realm not in self.realm_subscribers:
                self.realm_subscribers[realm] = {}
            
            if event_type not in self.realm_subscribers[realm]:
                self.realm_subscribers[realm][event_type] = []
            
            self.realm_subscribers[realm][event_type].append(handler)
            
            self.logger.info(f"✅ Subscribed {realm} to {event_type}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to subscribe {realm} to {event_type}: {e}")
    
    async def unsubscribe_from_event(self, realm: str, event_type: str, handler: Callable):
        """Unsubscribe from event type for realm."""
        try:
            if realm in self.realm_subscribers and event_type in self.realm_subscribers[realm]:
                if handler in self.realm_subscribers[realm][event_type]:
                    self.realm_subscribers[realm][event_type].remove(handler)
                    self.logger.info(f"✅ Unsubscribed {realm} from {event_type}")
                else:
                    self.logger.warning(f"⚠️ Handler not found for {realm}/{event_type}")
            else:
                self.logger.warning(f"⚠️ No subscription found for {realm}/{event_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to unsubscribe {realm} from {event_type}: {e}")
    
    async def get_event_subscribers(self, realm: str) -> Dict[str, List[Callable]]:
        """Get event subscribers for realm."""
        return self.realm_subscribers.get(realm, {})
    
    async def get_event_bus_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "total_subscribers": sum(len(subscribers) for subscribers in self.realm_subscribers.values()),
            "realm_subscribers": {realm: len(subscribers) for realm, subscribers in self.realm_subscribers.items()},
            "is_running": self.is_running,
            "is_initialized": self.is_initialized
        }
