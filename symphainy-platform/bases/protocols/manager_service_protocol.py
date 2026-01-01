#!/usr/bin/env python3
"""
Manager Service Protocol

Clean protocol definition for manager services - contracts only, no implementations.
Aligned with new architecture for stateful orchestration and lifecycle coordination.

WHAT (Manager Service Role): I define the contract for all manager services
HOW (Manager Service Protocol): I provide stateful orchestration and lifecycle management
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from datetime import datetime


@runtime_checkable
class ManagerServiceProtocol(Protocol):
    """
    Protocol for Manager Services.
    
    Manager services are stateful orchestrators and lifecycle coordinators
    that extend realm services with management-specific capabilities.
    """
    
    # Core Properties (extends RealmServiceProtocol)
    service_name: str
    realm_name: str
    platform_gateway: Any  # PlatformInfrastructureGateway
    di_container: Any  # DIContainerService
    start_time: datetime
    is_initialized: bool
    service_health: str
    
    # Manager-Specific Properties
    managed_services: Dict[str, Any]
    service_registry: Dict[str, Any]
    lifecycle_state: str
    
    # Lifecycle Methods
    async def initialize(self) -> bool:
        """Initialize the manager service."""
        ...
    
    async def shutdown(self) -> bool:
        """Shutdown the manager service gracefully."""
        ...
    
    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        ...
    
    # Service Management
    async def register_service(self, service_name: str, service_instance: Any) -> bool:
        """Register a service under management."""
        ...
    
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister a service from management."""
        ...
    
    async def get_managed_services(self) -> Dict[str, Any]:
        """Get all managed services."""
        ...
    
    # Lifecycle Coordination
    async def start_managed_services(self) -> Dict[str, bool]:
        """Start all managed services."""
        ...
    
    async def stop_managed_services(self) -> Dict[str, bool]:
        """Stop all managed services."""
        ...
    
    async def restart_managed_services(self) -> Dict[str, bool]:
        """Restart all managed services."""
        ...
    
    # State Management
    async def get_lifecycle_state(self) -> str:
        """Get current lifecycle state."""
        ...
    
    async def set_lifecycle_state(self, state: str) -> bool:
        """Set lifecycle state."""
        ...
    
    # Orchestration
    async def orchestrate_services(self, orchestration_request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate managed services for complex workflows."""
        ...
    
    async def coordinate_service_interactions(self, service_a: str, service_b: str, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate interactions between managed services."""
        ...
    
    # Configuration and Metadata
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        ...
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        ...