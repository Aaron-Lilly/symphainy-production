"""
IManagerService Interface
Interface that EXACTLY matches ManagerServiceBase implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IManagerService(ABC):
    """
    Manager Service Interface - EXACTLY matches ManagerServiceBase implementation.
    
    This interface requires only the methods that ManagerServiceBase actually implements,
    preventing anti-patterns and ensuring perfect alignment.
    """
    
    # Core Manager Methods (exactly what ManagerServiceBase implements)
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the manager service."""
        pass
    
    @abstractmethod
    async def get_manager_status(self) -> Dict[str, Any]:
        """Get overall manager status."""
        pass
    
    @abstractmethod
    async def get_manager_health(self) -> Dict[str, Any]:
        """Get manager health status."""
        pass
    
    @abstractmethod
    async def get_manager_capabilities(self) -> Dict[str, Any]:
        """Get manager capabilities."""
        pass
    
    @abstractmethod
    async def get_manager_metrics(self) -> Dict[str, Any]:
        """Get manager metrics."""
        pass
    
    # Realm Management (exactly what ManagerServiceBase implements)
    @abstractmethod
    async def orchestrate_realm_startup(self) -> Dict[str, Any]:
        """Orchestrate startup of all services in this manager's realm."""
        pass
    
    @abstractmethod
    async def start_realm_services(self) -> Dict[str, Any]:
        """Start all services managed by this realm."""
        pass
    
    @abstractmethod
    async def monitor_realm_health(self) -> Dict[str, Any]:
        """Monitor health of all services in this realm."""
        pass
    
    @abstractmethod
    async def coordinate_realm_shutdown(self) -> Dict[str, Any]:
        """Coordinate shutdown of all services in this realm."""
        pass
    
    # Dependency Management (exactly what ManagerServiceBase implements)
    @abstractmethod
    async def get_startup_dependencies(self) -> List[str]:
        """Get list of other managers this manager depends on for startup."""
        pass
    
    @abstractmethod
    async def wait_for_dependency_managers(self, dependency_managers: List[str]) -> bool:
        """Wait for dependency managers to be ready."""
        pass
    
    @abstractmethod
    async def coordinate_with_other_managers(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate startup with other domain managers."""
        pass




