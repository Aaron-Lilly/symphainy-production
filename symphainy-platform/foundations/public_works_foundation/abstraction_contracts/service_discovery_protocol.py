#!/usr/bin/env python3
"""
Service Discovery Protocol - Abstraction Contract

Defines the interface for service discovery and registration operations.
Technology-agnostic contract that can be implemented by Consul, Istio, Linkerd, etc.

WHAT: I define the contract for service registration and discovery
WHY: To enable swap-ability between different service mesh technologies
"""

from typing import Dict, Any, List, Optional, Callable, Protocol
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(str, Enum):
    """Service health status enumeration"""
    PASSING = "passing"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ServiceRegistration:
    """
    Service registration data structure.
    
    Contains all information about a registered service instance.
    """
    service_id: str
    service_name: str
    service_type: str
    address: str
    port: int
    tags: List[str]
    meta: Dict[str, Any]
    health_status: HealthStatus = HealthStatus.UNKNOWN
    endpoints: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    realm: Optional[str] = None
    health_check_endpoint: Optional[str] = None


@dataclass
class ServiceHealth:
    """Service health check information"""
    service_id: str
    service_name: str
    status: HealthStatus
    last_check: datetime = field(default_factory=datetime.utcnow)
    message: Optional[str] = None
    checks: List[Dict[str, Any]] = field(default_factory=list)


class ServiceDiscoveryAdapter(Protocol):
    """
    Service Discovery Adapter Protocol.
    
    Defines the interface that all service discovery adapters must implement.
    This enables swap-ability between Consul, Istio, Linkerd, etc.
    """
    
    async def connect(self) -> bool:
        """
        Establish connection to service discovery backend.
        
        Returns:
            bool: True if connection successful
        """
        ...
    
    async def register_service(self, service_name: str, service_data: Dict[str, Any]) -> bool:
        """
        Register a service with the discovery backend.
        
        Args:
            service_name: Name of the service
            service_data: Service registration data (address, port, tags, meta, etc.)
        
        Returns:
            bool: True if registration successful
        """
        ...
    
    async def deregister_service(self, service_name: str, service_id: Optional[str] = None) -> bool:
        """
        Deregister a service from the discovery backend.
        
        Args:
            service_name: Name of the service
            service_id: Optional specific service instance ID
        
        Returns:
            bool: True if deregistration successful
        """
        ...
    
    async def discover_service(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Discover service instances by name.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            List[Dict]: List of service instances with their metadata
        """
        ...
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status of service instances.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Dict: Health status information
        """
        ...
    
    async def update_service_health(self, service_id: str, status: str) -> bool:
        """
        Update health status of a service instance.
        
        Args:
            service_id: Service instance ID
            status: New health status
        
        Returns:
            bool: True if update successful
        """
        ...
    
    async def get_all_services(self) -> List[str]:
        """
        Get list of all registered service names.
        
        Returns:
            List[str]: List of service names
        """
        ...
    
    # Configuration management (KV store or equivalent)
    async def put_config(self, key: str, value: Any) -> bool:
        """
        Store configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def get_config(self, key: str) -> Optional[Any]:
        """
        Retrieve configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            Configuration value or None if not found
        """
        ...
    
    async def delete_config(self, key: str) -> bool:
        """
        Delete configuration value.
        
        Args:
            key: Configuration key
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def watch_service(self, service_name: str, callback: Callable) -> Any:
        """
        Watch for changes to a service.
        
        Args:
            service_name: Name of service to watch
            callback: Callback function to invoke on changes
        
        Returns:
            Watch handle (implementation-specific)
        """
        ...
    
    async def watch_config(self, key: str, callback: Callable) -> Any:
        """
        Watch for changes to a configuration key.
        
        Args:
            key: Configuration key to watch
            callback: Callback function to invoke on changes
        
        Returns:
            Watch handle (implementation-specific)
        """
        ...


class ServiceDiscoveryProtocol(Protocol):
    """
    Service Discovery Protocol (Layer 3 interface).
    
    Defines the business logic interface for service discovery operations.
    This is what services and Curator will actually use.
    """
    
    async def register_service(self, service_info: Dict[str, Any]) -> ServiceRegistration:
        """
        Register a service with business logic validation.
        
        Args:
            service_info: Service information including name, type, address, port, capabilities, etc.
        
        Returns:
            ServiceRegistration: Registration information
        """
        ...
    
    async def unregister_service(self, service_id: str) -> bool:
        """
        Unregister a service.
        
        Args:
            service_id: Service instance ID
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def discover_service(self, service_name: str) -> List[ServiceRegistration]:
        """
        Discover service instances by name.
        
        Args:
            service_name: Service name
        
        Returns:
            List[ServiceRegistration]: List of service instances
        """
        ...
    
    async def discover_by_capability(self, capability: str) -> List[ServiceRegistration]:
        """
        Discover services by capability.
        
        Args:
            capability: Capability name
        
        Returns:
            List[ServiceRegistration]: Services with this capability
        """
        ...
    
    async def discover_by_tags(self, tags: List[str]) -> List[ServiceRegistration]:
        """
        Discover services by tags.
        
        Args:
            tags: List of tags to match
        
        Returns:
            List[ServiceRegistration]: Services matching tags
        """
        ...
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """
        Check health of a service.
        
        Args:
            service_name: Service name
        
        Returns:
            ServiceHealth: Health information
        """
        ...
    
    async def get_all_services(self) -> List[str]:
        """
        Get all registered service names.
        
        Returns:
            List[str]: Service names
        """
        ...
    
    async def set_config(self, key: str, value: Any) -> bool:
        """Store configuration value"""
        ...
    
    async def get_config(self, key: str) -> Optional[Any]:
        """Retrieve configuration value"""
        ...
    
    async def watch_service(self, service_name: str, callback: Callable) -> Any:
        """Watch for service changes"""
        ...

