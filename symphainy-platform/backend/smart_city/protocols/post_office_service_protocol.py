#!/usr/bin/env python3
"""
Post Office Service Protocol

Realm-specific protocol for Post Office services.
Inherits standard methods from ServiceProtocol.

WHAT (Post Office Role): I orchestrate strategic communication and messaging
HOW (Post Office Protocol): I provide messaging, routing, and communication orchestration
"""

from typing import Protocol, Dict, Any, Optional
from bases.protocols.service_protocol import ServiceProtocol


class PostOfficeServiceProtocol(ServiceProtocol, Protocol):
    """
    Protocol for Post Office services.
    Inherits standard methods from ServiceProtocol.
    """
    
    # Messaging Methods
    async def send_message(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send message with routing and delivery."""
        ...
    
    async def get_messages(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get messages for recipient."""
        ...
    
    async def get_message_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get message delivery status."""
        ...
    
    # Event Routing
    async def route_event(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route event to appropriate service."""
        ...
    
    # Event Publishing
    async def publish_event(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Publish event via Post Office."""
        ...
    
    # Event Subscription
    async def subscribe_to_events(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Subscribe to events via Post Office."""
        ...
    
    async def unsubscribe_from_events(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Unsubscribe from events via Post Office."""
        ...
    
    # Agent Registration
    async def register_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Register agent for communication."""
        ...
    
    # Orchestration Methods
    async def orchestrate_pillar_coordination(self, pattern_name: str, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate communication between pillars."""
        ...
    
    async def orchestrate_realm_communication(self, source_realm: str, target_realm: str, 
                                            communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate communication between realms."""
        ...
    
    async def orchestrate_event_driven_communication(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate event-driven communication patterns."""
        ...
    
    async def orchestrate_service_discovery(self, service_type: str, realm: Optional[str] = None) -> Dict[str, Any]:
        """Orchestrate service discovery and location."""
        ...

