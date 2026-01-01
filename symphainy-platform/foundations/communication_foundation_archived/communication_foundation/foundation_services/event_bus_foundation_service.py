#!/usr/bin/env python3
"""
Event Bus Foundation Service

Infrastructure-level foundation service for event-driven communication.
Provides stable API for Smart City services while allowing infrastructure swapping.

WHAT (Foundation Service): I provide event bus infrastructure services
HOW (Service Implementation): I use Public Works Event Management abstraction via DI
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Import foundation base
from bases.foundation_service_base import FoundationServiceBase

# Import Public Works Foundation for infrastructure
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import DI Container
from foundations.di_container.di_container_service import DIContainerService


class EventBusFoundationService(FoundationServiceBase):
    """
    Event Bus Foundation Service - Infrastructure-level Event Bus Services
    
    Provides event bus infrastructure services for all realms using Public Works
    Event Management abstraction. Provides stable API to Smart City services while
    allowing infrastructure swapping without breaking changes.
    
    WHAT (Foundation Service): I provide event bus infrastructure services
    HOW (Service Implementation): I use Public Works Event Management abstraction via DI
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize Event Bus Foundation Service."""
        super().__init__(
            service_name="event_bus_foundation",
            di_container=di_container
        )
        self.public_works_foundation = public_works_foundation
        
        # Get infrastructure from Public Works (via DI)
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
        self.is_running = False
        
        self.logger.info("🏗️ Event Bus Foundation Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize foundation service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Event Bus Foundation Service...")
            
            # Get infrastructure from Public Works Foundation (via DI - required)
            self.event_management_abstraction = self.public_works_foundation.get_event_management_abstraction()
            
            if not self.event_management_abstraction:
                raise RuntimeError(
                    "Event management abstraction not available from Public Works Foundation. "
                    "Ensure Public Works Foundation is initialized and provides event_management abstraction."
                )
            
            # NOTE: EventManagementAbstraction doesn't have an initialize() method
            # It's initialized in __init__ and is ready to use immediately
            # No async initialization needed
            
            # Setup event handlers
            await self._setup_event_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ Event Bus Foundation Service initialized successfully")
            
            # Record success metric
            await self.record_health_metric("initialize_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "initialize")
            self.logger.error(f"❌ Failed to initialize Event Bus Foundation Service: {e}")
            self.service_health = "unhealthy"
            return False
    
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
                # Start telemetry tracking (using service's utilities)
                await self.log_operation_with_telemetry("realm_event_handler_start", success=True)
                
                # Process event
                await self._process_realm_event(realm, event_data)
                
                # Record success metric
                await self.record_health_metric("realm_event_handler_success", 1.0, {
                    "realm": realm,
                    "event_type": event_data.get("type", "unknown")
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("realm_event_handler_complete", success=True)
                
            except Exception as e:
                # Use enhanced error handling with audit (using service's utilities)
                await self.handle_error_with_audit(e, "realm_event_handler")
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
        """Start Event Bus Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("start_start", success=True)
            
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info("🚀 Starting Event Bus Foundation Service...")
            
            # Start event management abstraction
            if self.event_management_abstraction:
                await self.event_management_abstraction.start()
            
            self.is_running = True
            self.logger.info("✅ Event Bus Foundation Service started successfully")
            
            # Record success metric
            await self.record_health_metric("start_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("start_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "start")
            self.logger.error(f"❌ Failed to start Event Bus Foundation Service: {e}")
            raise
    
    async def stop(self):
        """Stop Event Bus Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("stop_start", success=True)
            
            self.logger.info("🛑 Stopping Event Bus Foundation Service...")
            
            # Stop event management abstraction
            if self.event_management_abstraction:
                await self.event_management_abstraction.stop()
            
            self.is_running = False
            self.logger.info("✅ Event Bus Foundation Service stopped successfully")
            
            # Record success metric
            await self.record_health_metric("stop_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("stop_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "stop")
            self.logger.error(f"❌ Failed to stop Event Bus Foundation Service: {e}")
            raise
    
    async def shutdown(self) -> bool:
        """Shutdown Event Bus Foundation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("shutdown_start", success=True)
            
            await self.stop()
            self.logger.info("🔌 Event Bus Foundation Service shutdown complete")
            
            # Record success metric
            await self.record_health_metric("shutdown_success", 1.0, {"service": self.service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("shutdown_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "shutdown")
            self.logger.error(f"❌ Failed to shutdown Event Bus Foundation Service: {e}")
            return False
    
    # Public API methods for Smart City services
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any], 
                           source_realm: str = "system", priority: str = "normal") -> Optional[str]:
        """Publish event to event bus."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("publish_event_start", success=True)
            
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
                    
                    # Record success metric
                    await self.record_health_metric("publish_event_success", 1.0, {
                        "event_type": event_type,
                        "source_realm": source_realm
                    })
                    
                    # End telemetry tracking
                    await self.log_operation_with_telemetry("publish_event_complete", success=True)
                    
                    return event_context.event_id
                else:
                    self.logger.error(f"❌ Failed to publish event: {event_type}")
                    await self.record_health_metric("publish_event_failed", 1.0, {"event_type": event_type})
                    await self.log_operation_with_telemetry("publish_event_complete", success=False)
                    return None
            else:
                self.logger.error("❌ Event management abstraction not available")
                await self.record_health_metric("publish_event_error", 1.0, {"error": "abstraction_not_available"})
                await self.log_operation_with_telemetry("publish_event_complete", success=False)
                return None
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "publish_event")
            self.logger.error(f"❌ Failed to publish event: {e}")
            return None
    
    async def subscribe_to_event(self, realm: str, event_type: str, handler: Callable):
        """Subscribe to event type for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("subscribe_to_event_start", success=True)
            
            if realm not in self.realm_subscribers:
                self.realm_subscribers[realm] = {}
            
            if event_type not in self.realm_subscribers[realm]:
                self.realm_subscribers[realm][event_type] = []
            
            self.realm_subscribers[realm][event_type].append(handler)
            
            self.logger.info(f"✅ Subscribed {realm} to {event_type}")
            
            # Record success metric
            await self.record_health_metric("subscribe_to_event_success", 1.0, {
                "realm": realm,
                "event_type": event_type
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("subscribe_to_event_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "subscribe_to_event")
            self.logger.error(f"❌ Failed to subscribe {realm} to {event_type}: {e}")
            raise
    
    async def unsubscribe_from_event(self, realm: str, event_type: str, handler: Callable):
        """Unsubscribe from event type for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("unsubscribe_from_event_start", success=True)
            
            if realm in self.realm_subscribers and event_type in self.realm_subscribers[realm]:
                if handler in self.realm_subscribers[realm][event_type]:
                    self.realm_subscribers[realm][event_type].remove(handler)
                    self.logger.info(f"✅ Unsubscribed {realm} from {event_type}")
                    
                    # Record success metric
                    await self.record_health_metric("unsubscribe_from_event_success", 1.0, {
                        "realm": realm,
                        "event_type": event_type
                    })
                    
                    # End telemetry tracking
                    await self.log_operation_with_telemetry("unsubscribe_from_event_complete", success=True)
                else:
                    self.logger.warning(f"⚠️ Handler not found for {realm}/{event_type}")
                    await self.record_health_metric("unsubscribe_from_event_warning", 1.0, {
                        "realm": realm,
                        "event_type": event_type,
                        "warning": "handler_not_found"
                    })
                    await self.log_operation_with_telemetry("unsubscribe_from_event_complete", success=False)
            else:
                self.logger.warning(f"⚠️ No subscription found for {realm}/{event_type}")
                await self.record_health_metric("unsubscribe_from_event_warning", 1.0, {
                    "realm": realm,
                    "event_type": event_type,
                    "warning": "subscription_not_found"
                })
                await self.log_operation_with_telemetry("unsubscribe_from_event_complete", success=False)
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "unsubscribe_from_event")
            self.logger.error(f"❌ Failed to unsubscribe {realm} from {event_type}: {e}")
            raise
    
    async def get_event_subscribers(self, realm: str, user_context: Dict[str, Any] = None) -> Dict[str, List[Callable]]:
        """Get event subscribers for realm."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_event_subscribers_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, f"realm_{realm}", "read"):
                        await self.record_health_metric("get_event_subscribers_access_denied", 1.0, {"realm": realm})
                        await self.log_operation_with_telemetry("get_event_subscribers_complete", success=False)
                        return {}
            
            result = self.realm_subscribers.get(realm, {})
            
            # Record success metric
            await self.record_health_metric("get_event_subscribers_success", 1.0, {"realm": realm, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_event_subscribers_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_event_subscribers")
            self.logger.error(f"❌ Failed to get event subscribers for {realm}: {e}")
            return {}
    
    async def get_event_bus_stats(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get event bus statistics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_event_bus_stats_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "event_bus_stats", "read"):
                        await self.record_health_metric("get_event_bus_stats_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_event_bus_stats_complete", success=False)
                        return {}
            
            result = {
                "total_subscribers": sum(len(subscribers) for subscribers in self.realm_subscribers.values()),
                "realm_subscribers": {realm: len(subscribers) for realm, subscribers in self.realm_subscribers.items()},
                "is_running": self.is_running,
                "is_initialized": self.is_initialized
            }
            
            # Record success metric
            await self.record_health_metric("get_event_bus_stats_success", 1.0, {"total_subscribers": result["total_subscribers"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_event_bus_stats_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_event_bus_stats")
            self.logger.error(f"❌ Failed to get event bus stats: {e}")
            return {}



