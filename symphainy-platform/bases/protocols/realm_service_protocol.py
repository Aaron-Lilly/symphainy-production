#!/usr/bin/env python3
"""
Realm Service Protocol

Clean protocol definition for realm services - contracts only, no implementations.
Aligned with new architecture (Platform Gateway, Curator, Communication patterns).

WHAT (Realm Service Role): I define the contract for all realm services
HOW (Realm Service Protocol): I provide type-safe contracts with realm-specific capabilities
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from datetime import datetime


@runtime_checkable
class RealmServiceProtocol(Protocol):
    """
    Protocol for Realm Services.
    
    Realm services operate within specific realms and use Platform Gateway
    for controlled access to Public Works abstractions.
    """
    
    # Core Properties
    service_name: str
    realm_name: str
    platform_gateway: Any  # PlatformInfrastructureGateway
    di_container: Any  # DIContainerService
    start_time: datetime
    is_initialized: bool
    service_health: str
    
    # Lifecycle Methods
    async def initialize(self) -> bool:
        """Initialize the realm service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the realm service gracefully."""
        ...
    
    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        ...
    
    # Platform Gateway Integration
    def get_abstraction(self, abstraction_name: str) -> Any:
        """Get abstraction through Platform Gateway."""
        ...
    
    def get_realm_abstractions(self) -> Dict[str, Any]:
        """Get all allowed abstractions for this realm."""
        ...
    
    # Realm-Specific Methods
    def get_realm_context(self) -> Dict[str, Any]:
        """Get realm-specific context and configuration."""
        ...
    
    def validate_realm_access(self, resource: str, action: str) -> bool:
        """Validate access within realm context."""
        ...
    
    # Communication (via Smart City SOA APIs)
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via Smart City communication APIs."""
        ...
    
    async def publish_event(self, event: Dict[str, Any]) -> bool:
        """Publish event via Smart City event APIs."""
        ...
    
    # Configuration and Metadata
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        ...
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        ...