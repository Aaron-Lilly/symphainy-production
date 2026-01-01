#!/usr/bin/env python3
"""
Communication Mixin

Focused mixin for communication patterns - extracts messaging and event
functionality from base classes into a reusable, testable component.

WHAT (Communication Role): I provide messaging and event communication patterns
HOW (Communication Mixin): I centralize communication patterns with Smart City SOA APIs
"""

from typing import Dict, Any, Optional


class CommunicationMixin:
    """
    Mixin for communication patterns and messaging.
    
    Provides consistent messaging, event publishing, and communication
    patterns across all services with proper error handling.
    """
    
    def _init_communication(self, di_container: Any):
        """Initialize communication patterns."""
        if not di_container:
            raise ValueError(
                "DI Container is required for CommunicationMixin initialization. "
                "Services must be created with a valid DI Container instance."
            )
        
        self.di_container = di_container
        
        # Get logger from DI Container (should be available - DI Container initializes logging in __init__)
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError(
                f"DI Container does not have get_logger method. "
                f"This indicates a platform initialization failure or incorrect DI Container instance."
            )
        
        try:
            # Use DI Container's get_logger method to create logger for this mixin
            logger_service = di_container.get_logger(f"{self.__class__.__name__}.communication")
            if not logger_service:
                raise RuntimeError(
                    f"DI Container.get_logger() returned None. "
                    f"Logging service should be available - this indicates a platform initialization failure."
                )
            # SmartCityLoggingService has .logger attribute and methods like .info(), .error(), etc.
            self.logger = logger_service
        except Exception as e:
            raise RuntimeError(
                f"Failed to get logger from DI Container: {e}. "
                f"DI Container must initialize logging utility before services can use it. "
                f"This indicates a platform initialization failure."
            ) from e
        
        # Communication utilities
        self.messaging_abstraction = None
        self.event_management_abstraction = None
        
        self.logger.debug("Communication mixin initialized")
    
    def get_messaging_abstraction(self) -> Optional[Any]:
        """Get messaging abstraction via Platform Gateway (not DI container)."""
        if not self.messaging_abstraction:
            try:
                # Use RealmServiceBase.get_abstraction() if available (via Platform Gateway)
                if hasattr(self, 'get_abstraction'):
                    self.messaging_abstraction = self.get_abstraction("messaging")
                elif hasattr(self, 'di_container'):
                    # Fallback for classes that don't have get_abstraction (should be rare)
                    self.logger.warning("⚠️ Using di_container.get_abstraction() - should use self.get_abstraction() instead")
                    self.messaging_abstraction = self.di_container.get_abstraction("messaging")
            except Exception as e:
                self.logger.debug(f"Messaging abstraction not available: {e}")
        
        return self.messaging_abstraction
    
    def get_event_management_abstraction(self) -> Optional[Any]:
        """Get event management abstraction via Platform Gateway (not DI container)."""
        if not self.event_management_abstraction:
            try:
                # Use RealmServiceBase.get_abstraction() if available (via Platform Gateway)
                if hasattr(self, 'get_abstraction'):
                    self.event_management_abstraction = self.get_abstraction("event_management")
                elif hasattr(self, 'di_container'):
                    # Fallback for classes that don't have get_abstraction (should be rare)
                    self.logger.warning("⚠️ Using di_container.get_abstraction() - should use self.get_abstraction() instead")
                    self.event_management_abstraction = self.di_container.get_abstraction("event_management")
            except Exception as e:
                self.logger.debug(f"Event management abstraction not available: {e}")
        
        return self.event_management_abstraction
    
    async def get_post_office_api(self) -> Optional[Any]:
        """
        Get Post Office service via Curator discovery.
        
        Uses PlatformCapabilitiesMixin method if available.
        """
        try:
            # Check if we have get_smart_city_api method (from PlatformCapabilitiesMixin)
            if hasattr(self, 'get_smart_city_api'):
                return await self.get_smart_city_api("PostOffice")
            else:
                self.logger.warning("⚠️ get_smart_city_api method not available (PlatformCapabilitiesMixin not included)")
                return None
        except Exception as e:
            self.logger.error(f"❌ Failed to get Post Office API: {e}")
            return None
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send message via Post Office service (NOT infrastructure abstraction).
        
        Uses Smart City service for business-level messaging orchestration.
        Falls back to infrastructure abstraction if Post Office not available.
        """
        try:
            # ✅ Use Post Office service (business-level)
            post_office = await self.get_post_office_api()
            if post_office:
                # Use Post Office service method
                if hasattr(post_office, 'send_message'):
                    return await post_office.send_message(message)
                else:
                    self.logger.warning("⚠️ Post Office service found but send_message method not available")
            else:
                # Fallback to infrastructure abstraction if Post Office not available
                self.logger.warning("⚠️ Post Office not available, falling back to messaging abstraction")
            
            # Fallback: Use infrastructure abstraction
            messaging = self.get_messaging_abstraction()
            if messaging:
                return await messaging.send_message(message)
            else:
                return {"status": "error", "error": "Messaging not available"}
                
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return {"status": "error", "error": str(e)}
    
    async def publish_event(self, event: Dict[str, Any]) -> bool:
        """
        Publish event via Post Office service (NOT infrastructure abstraction).
        
        Uses Smart City service for business-level event publishing.
        Falls back to infrastructure abstraction if Post Office not available.
        """
        try:
            # ✅ Use Post Office service (business-level)
            post_office = await self.get_post_office_api()
            if post_office:
                # Use Post Office service method
                if hasattr(post_office, 'publish_event'):
                    result = await post_office.publish_event({
                        "event_type": event.get("event_type", "generic"),
                        "event_data": event,
                        "source": event.get("source"),
                        "target": event.get("target"),
                        "priority": event.get("priority", "normal"),
                        "correlation_id": event.get("correlation_id"),
                        "tenant_id": event.get("tenant_id")
                    })
                    return result.get("success", False)
                else:
                    self.logger.warning("⚠️ Post Office service found but publish_event method not available")
            else:
                # Fallback to infrastructure abstraction if Post Office not available
                self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
            
            # Fallback: Use infrastructure abstraction
            event_mgmt = self.get_event_management_abstraction()
            if event_mgmt:
                return await event_mgmt.publish_event(event)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            return False
    
    async def subscribe_to_events(self, event_type: str, handler: Any) -> bool:
        """
        Subscribe to events via Post Office service (NOT infrastructure abstraction).
        
        Uses Smart City service for business-level event subscription.
        Falls back to infrastructure abstraction if Post Office not available.
        """
        try:
            # ✅ Use Post Office service (business-level)
            post_office = await self.get_post_office_api()
            if post_office:
                # Use Post Office service method
                if hasattr(post_office, 'subscribe_to_events'):
                    # Convert handler to handler_id (or store handler mapping)
                    # Simple ID generation - in production, you might want to store handler mapping
                    handler_id = str(id(handler))  # Simple ID generation
                    result = await post_office.subscribe_to_events({
                        "event_type": event_type,
                        "handler_id": handler_id
                    })
                    return result.get("success", False)
                else:
                    self.logger.warning("⚠️ Post Office service found but subscribe_to_events method not available")
            else:
                # Fallback to infrastructure abstraction
                self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
            
            # Fallback: Use infrastructure abstraction
            event_mgmt = self.get_event_management_abstraction()
            if event_mgmt:
                return await event_mgmt.subscribe(event_type, handler)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to subscribe to events {event_type}: {e}")
            return False
    
    async def unsubscribe_from_events(self, event_type: str, handler: Any) -> bool:
        """
        Unsubscribe from events via Post Office service (NOT infrastructure abstraction).
        
        Uses Smart City service for business-level event unsubscription.
        Falls back to infrastructure abstraction if Post Office not available.
        """
        try:
            # ✅ Use Post Office service (business-level)
            post_office = await self.get_post_office_api()
            if post_office:
                # Use Post Office service method
                if hasattr(post_office, 'unsubscribe_from_events'):
                    handler_id = str(id(handler))  # Simple ID generation (matches subscribe)
                    result = await post_office.unsubscribe_from_events({
                        "event_type": event_type,
                        "handler_id": handler_id
                    })
                    return result.get("success", False)
                else:
                    self.logger.warning("⚠️ Post Office service found but unsubscribe_from_events method not available")
            else:
                # Fallback to infrastructure abstraction
                self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
            
            # Fallback: Use infrastructure abstraction
            event_mgmt = self.get_event_management_abstraction()
            if event_mgmt:
                return await event_mgmt.unsubscribe(event_type, handler)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from events {event_type}: {e}")
            return False
    
    async def broadcast_message(self, message: Dict[str, Any], target_realms: Optional[list] = None) -> Dict[str, Any]:
        """Broadcast message to multiple realms."""
        try:
            messaging = self.get_messaging_abstraction()
            if messaging:
                return await messaging.broadcast_message(message, target_realms)
            else:
                self.logger.warning("Messaging abstraction not available")
                return {"status": "error", "error": "Messaging not available"}
                
        except Exception as e:
            self.logger.error(f"Failed to broadcast message: {e}")
            return {"status": "error", "error": str(e)}
    
    async def route_event(self, event: Dict[str, Any], target_service: str) -> bool:
        """
        Route event via Post Office service (NOT infrastructure abstraction).
        
        Uses Smart City service for business-level event routing.
        Falls back to infrastructure abstraction if Post Office not available.
        """
        try:
            # ✅ Use Post Office service (business-level)
            post_office = await self.get_post_office_api()
            if post_office and hasattr(post_office, 'route_event'):
                # Post Office route_event expects a request dict
                result = await post_office.route_event({
                    "event_type": event.get("event_type", "generic"),
                    "event_data": event,
                    "source": event.get("source"),
                    "target": target_service,
                    "priority": event.get("priority", "normal"),
                    "correlation_id": event.get("correlation_id"),
                    "tenant_id": event.get("tenant_id")
                })
                return result.get("success", False)
            else:
                # Fallback to infrastructure abstraction
                self.logger.warning("⚠️ Post Office not available, falling back to event management abstraction")
                event_mgmt = self.get_event_management_abstraction()
                if event_mgmt:
                    return await event_mgmt.route_event(event, target_service)
                else:
                    self.logger.warning("Event management abstraction not available")
                    return False
                
        except Exception as e:
            self.logger.error(f"Failed to route event to {target_service}: {e}")
            return False
    
    def is_communication_available(self) -> bool:
        """Check if communication capabilities are available."""
        return (self.get_messaging_abstraction() is not None or 
                self.get_event_management_abstraction() is not None)

