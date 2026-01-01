"""
IJourneyOrchestrator Interface
Interface for journey orchestration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IJourneyOrchestrator(ABC):
    """Interface for journey orchestration."""
    
    @abstractmethod
    async def orchestrate_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a user journey."""
        pass
    
    @abstractmethod
    async def get_journey_status(self, journey_id: str) -> Dict[str, Any]:
        """Get status of a specific journey."""
        pass
    
    @abstractmethod
    async def coordinate_journey_services(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate services for a journey."""
        pass
    
    @abstractmethod
    async def get_journey_health(self) -> Dict[str, Any]:
        """Get overall journey health."""
        pass
    
    @abstractmethod
    async def orchestrate_business_outcome_journey(self, outcome_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a business outcome journey."""
        pass
    
    @abstractmethod
    async def get_business_outcome_status(self, outcome_id: str) -> Dict[str, Any]:
        """Get status of a business outcome."""
        pass




