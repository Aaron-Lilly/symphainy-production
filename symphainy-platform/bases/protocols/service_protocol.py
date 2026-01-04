#!/usr/bin/env python3
"""
Base Service Protocol

Standard protocol for ALL services - defines common methods that every service
must implement regardless of realm or type.

WHAT (Base Service Role): I define the standard contract for all services
HOW (Base Service Protocol): I provide common lifecycle, health, and communication methods
"""

from typing import Protocol, Dict, Any, Optional, runtime_checkable
from datetime import datetime


@runtime_checkable
class ServiceProtocol(Protocol):
    """
    Base protocol for ALL services.
    
    Defines standard methods that every service must implement regardless of
    realm, type, or specific functionality.
    """
    
    # Core Properties (all services have these)
    service_name: str
    is_initialized: bool
    service_health: str
    start_time: datetime
    
    # Lifecycle Methods (all services need these)
    async def initialize(self) -> bool:
        """Initialize the service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the service gracefully."""
        ...
    
    # Health and Monitoring (all services need these)
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        ...
    
    # Communication (OPTIONAL - only services that need communication implement these)
    # Foundation services (infrastructure) don't need communication methods
    # Realm services and Smart City services implement these via CommunicationMixin
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via Smart City communication APIs (optional - not all services need this)."""
        ...
    
    async def publish_event(self, event: Dict[str, Any]) -> bool:
        """Publish event via Smart City event APIs (optional - not all services need this)."""
        ...
    
    # Infrastructure Access (all services need these)
    def get_infrastructure_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction by name."""
        ...
    
    def get_utility(self, name: str) -> Any:
        """Get utility service by name."""
        ...
    
    # Configuration and Metadata (all services need these)
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        ...
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        ...
