"""
IRealmStartupOrchestrator Interface
Interface for realm startup orchestration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IRealmStartupOrchestrator(ABC):
    """Interface for realm startup orchestration."""
    
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
    
    @abstractmethod
    async def get_realm_services(self) -> List[str]:
        """Get list of services managed by this realm."""
        pass
    
    @abstractmethod
    async def start_service(self, service_name: str) -> Dict[str, Any]:
        """Start a specific service."""
        pass
    
    @abstractmethod
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status of a specific service."""
        pass
    
    @abstractmethod
    async def shutdown_service(self, service_name: str) -> Dict[str, Any]:
        """Shutdown a specific service."""
        pass




