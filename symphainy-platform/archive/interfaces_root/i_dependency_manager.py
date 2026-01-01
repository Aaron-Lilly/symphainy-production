"""
IDependencyManager Interface
Interface for dependency management
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IDependencyManager(ABC):
    """Interface for dependency management."""
    
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
    
    @abstractmethod
    async def wait_for_manager_health(self, manager_name: str) -> bool:
        """Wait for a specific manager to be healthy."""
        pass
    
    @abstractmethod
    async def get_other_managers(self) -> List[str]:
        """Get list of other managers to coordinate with."""
        pass
    
    @abstractmethod
    async def coordinate_with_manager(self, manager_name: str, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with a specific manager."""
        pass
