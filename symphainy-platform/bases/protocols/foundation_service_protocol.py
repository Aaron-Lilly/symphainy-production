#!/usr/bin/env python3
"""
Foundation Service Protocol

Clean protocol definition for foundation services - contracts only, no implementations.
Aligned with new architecture (Platform Gateway, Curator, Communication patterns).

WHAT (Foundation Role): I define the contract for all foundation services
HOW (Foundation Protocol): I provide type-safe contracts with clear responsibilities
"""

from typing import Protocol, Dict, Any, Optional, List
from datetime import datetime


class FoundationServiceProtocol(Protocol):
    """
    Protocol for Foundation Services.
    
    Foundation services provide core platform capabilities to all other services.
    They are the foundational layer that enables the entire platform.
    """
    
    # Core Properties
    service_name: str
    di_container: Any  # DIContainerService
    start_time: datetime
    is_initialized: bool
    service_health: str
    
    # Lifecycle Methods
    async def initialize(self) -> bool:
        """Initialize the foundation service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the foundation service gracefully."""
        ...
    
    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        ...
    
    # Infrastructure Access
    def get_infrastructure_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction by name."""
        ...
    
    def get_utility(self, name: str) -> Any:
        """Get utility service by name."""
        ...
    
    # Security Integration
    def get_security_context(self) -> Optional[Dict[str, Any]]:
        """Get current security context."""
        ...
    
    def validate_access(self, resource: str, action: str) -> bool:
        """Validate access to resource for action."""
        ...
    
    # Configuration and Metadata
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        ...
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        ...

