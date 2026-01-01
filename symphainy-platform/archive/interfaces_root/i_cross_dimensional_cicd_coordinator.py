"""
ICrossDimensionalCICDCoordinator Interface
Interface for cross-dimensional CI/CD coordination
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ICrossDimensionalCICDCoordinator(ABC):
    """Interface for cross-dimensional CI/CD coordination."""
    
    @abstractmethod
    async def coordinate_cross_dimensional_cicd(self, cicd_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate CI/CD across dimensions."""
        pass
    
    @abstractmethod
    async def get_cross_dimensional_cicd_status(self) -> Dict[str, Any]:
        """Get cross-dimensional CI/CD status."""
        pass
    
    @abstractmethod
    async def coordinate_domain_deployment(self, domain: str, deployment_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate deployment for a specific domain."""
        pass
    
    @abstractmethod
    async def get_domain_deployment_status(self, domain: str) -> Dict[str, Any]:
        """Get deployment status for a specific domain."""
        pass
    
    @abstractmethod
    async def coordinate_cross_dimensional_testing(self, testing_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate testing across dimensions."""
        pass
    
    @abstractmethod
    async def get_cross_dimensional_test_results(self) -> Dict[str, Any]:
        """Get cross-dimensional test results."""
        pass




