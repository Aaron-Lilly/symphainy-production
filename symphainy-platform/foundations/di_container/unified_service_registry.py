#!/usr/bin/env python3
"""
Unified Service Registry - Cloud-Ready DI Container Registry

Single source of truth for all services with metadata and lifecycle management.

WHAT (DI Container Component): I provide unified service registry with lifecycle management
HOW (Implementation): I track services with metadata, dependencies, and state
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Service type enumeration."""
    FOUNDATION = "foundation"
    INFRASTRUCTURE = "infrastructure"
    REALM = "realm"
    UTILITY = "utility"
    ORCHESTRATOR = "orchestrator"
    AGENT = "agent"


class ServiceLifecycleState(Enum):
    """Service lifecycle state."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceMetadata:
    """Service metadata."""
    service_name: str
    service_type: ServiceType
    instance: Any
    dependencies: List[str] = field(default_factory=list)
    state: ServiceLifecycleState = ServiceLifecycleState.UNINITIALIZED
    registered_at: datetime = field(default_factory=datetime.utcnow)
    initialized_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedServiceRegistry:
    """
    Unified service registry with lifecycle management.
    
    Provides a single source of truth for all services with:
    - Service metadata tracking
    - Dependency resolution
    - Lifecycle state management
    - Service discovery support
    """
    
    def __init__(self):
        """Initialize unified registry."""
        self.services: Dict[str, ServiceMetadata] = {}
        self.logger = logging.getLogger("UnifiedServiceRegistry")
        self.logger.info("🏗️ Unified Service Registry initialized")
    
    def register(
        self,
        service_name: str,
        service_type: ServiceType,
        instance: Any,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Register a service.
        
        Args:
            service_name: Unique name for the service
            service_type: Type of service (foundation, infrastructure, realm, etc.)
            instance: Service instance
            dependencies: List of service names this service depends on
            metadata: Additional metadata dictionary
        
        Returns:
            True if registration successful, False otherwise
        """
        if service_name in self.services:
            self.logger.warning(f"⚠️ Service {service_name} already registered, updating...")
        
        self.services[service_name] = ServiceMetadata(
            service_name=service_name,
            service_type=service_type,
            instance=instance,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self.logger.info(f"✅ Registered {service_type.value} service: {service_name}")
        return True
    
    def get(self, service_name: str) -> Optional[Any]:
        """
        Get service instance.
        
        Args:
            service_name: Name of the service to retrieve
        
        Returns:
            Service instance if found, None otherwise
        """
        if service_name in self.services:
            return self.services[service_name].instance
        return None
    
    def get_metadata(self, service_name: str) -> Optional[ServiceMetadata]:
        """
        Get service metadata.
        
        Args:
            service_name: Name of the service
        
        Returns:
            ServiceMetadata if found, None otherwise
        """
        return self.services.get(service_name)
    
    def list_services(self, service_type: Optional[ServiceType] = None) -> List[str]:
        """
        List all services, optionally filtered by type.
        
        Args:
            service_type: Optional service type filter
        
        Returns:
            List of service names
        """
        if service_type:
            return [
                name for name, meta in self.services.items()
                if meta.service_type == service_type
            ]
        return list(self.services.keys())
    
    def update_state(self, service_name: str, state: ServiceLifecycleState) -> bool:
        """
        Update service lifecycle state.
        
        Args:
            service_name: Name of the service
            state: New lifecycle state
        
        Returns:
            True if update successful, False otherwise
        """
        if service_name not in self.services:
            self.logger.warning(f"⚠️ Service {service_name} not found, cannot update state")
            return False
        
        metadata = self.services[service_name]
        metadata.state = state
        
        if state == ServiceLifecycleState.RUNNING:
            metadata.initialized_at = datetime.utcnow()
        
        self.logger.info(f"✅ Updated {service_name} state to {state.value}")
        return True
    
    def resolve_dependencies(self) -> List[str]:
        """
        Resolve service dependency order using topological sort.
        
        Returns:
            Ordered list of service names (dependencies first)
        """
        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}
        
        for service_name, metadata in self.services.items():
            graph[service_name] = metadata.dependencies.copy()
            in_degree[service_name] = len(metadata.dependencies)
        
        # Topological sort (Kahn's algorithm)
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            service_name = queue.pop(0)
            result.append(service_name)
            
            # Reduce in-degree for dependent services
            for dependent_name, dependencies in graph.items():
                if service_name in dependencies:
                    in_degree[dependent_name] -= 1
                    if in_degree[dependent_name] == 0:
                        queue.append(dependent_name)
        
        # Check for circular dependencies
        if len(result) != len(self.services):
            circular = set(self.services.keys()) - set(result)
            self.logger.error(f"❌ Circular dependency detected: {circular}")
            raise ValueError(f"Circular dependency detected: {circular}")
        
        self.logger.info(f"✅ Resolved dependency order: {len(result)} services")
        return result
    
    def get_dependencies(self, service_name: str) -> List[str]:
        """
        Get dependencies for a service.
        
        Args:
            service_name: Name of the service
        
        Returns:
            List of dependency service names
        """
        metadata = self.get_metadata(service_name)
        if metadata:
            return metadata.dependencies
        return []
    
    def get_dependents(self, service_name: str) -> List[str]:
        """
        Get services that depend on this service.
        
        Args:
            service_name: Name of the service
        
        Returns:
            List of dependent service names
        """
        dependents = []
        for name, metadata in self.services.items():
            if service_name in metadata.dependencies:
                dependents.append(name)
        return dependents
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        stats = {
            "total_services": len(self.services),
            "by_type": {},
            "by_state": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for service_name, metadata in self.services.items():
            # Count by type
            type_name = metadata.service_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
            
            # Count by state
            state_name = metadata.state.value
            stats["by_state"][state_name] = stats["by_state"].get(state_name, 0) + 1
        
        return stats









