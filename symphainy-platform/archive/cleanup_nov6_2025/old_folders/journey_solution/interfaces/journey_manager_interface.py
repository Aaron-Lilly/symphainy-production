#!/usr/bin/env python3
"""
Journey Manager Interface

Defines the contract for the Journey Manager Service, responsible for
cross-dimensional orchestration of Journey Solution services.

WHAT (Journey Solution Role): I orchestrate journey services within the Journey Solution domain
HOW (Interface): I define the contract for journey orchestration, service management, and cross-dimensional coordination
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from utilities import UserContext


class JourneyServiceType(Enum):
    """Defines types of journey services."""
    JOURNEY_ORCHESTRATOR = "journey_orchestrator"
    BUSINESS_OUTCOME_LANDING_PAGE = "business_outcome_landing_page"
    JOURNEY_PERSISTENCE = "journey_persistence"
    
    def __str__(self):
        return self.value


class JourneyAgentType(Enum):
    """Defines types of journey agents."""
    JOURNEY_COORDINATOR = "journey_coordinator"
    OUTCOME_TRACKER = "outcome_tracker"
    
    def __str__(self):
        return self.value


class IJourneyManager(ABC):
    """
    Journey Manager Interface
    
    Defines the contract for the Journey Manager Service.
    """
    
    @abstractmethod
    async def orchestrate_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a user journey using service registry for composition.
        
        Args:
            journey_context: Journey context data including requirements and capabilities
            
        Returns:
            Dict containing journey orchestration result
        """
        pass

    @abstractmethod
    async def orchestrate_mvp_journey(self, journey_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate MVP journey across all 4 pillars with solution context.
        
        Args:
            journey_request: MVP journey request data
            
        Returns:
            Dict containing MVP journey orchestration result
        """
        pass

    @abstractmethod
    async def get_journey_status(self, journey_id: str) -> Dict[str, Any]:
        """
        Get status of a specific journey.
        
        Args:
            journey_id: ID of the journey
            
        Returns:
            Dict containing journey status
        """
        pass

    @abstractmethod
    async def start_service(self, service_name: str) -> Dict[str, Any]:
        """
        Start a specific journey service.
        
        Args:
            service_name: Name of the service to start
            
        Returns:
            Dict containing service start result
        """
        pass

    @abstractmethod
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status of a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dict containing service health status
        """
        pass

    @abstractmethod
    async def shutdown_service(self, service_name: str) -> Dict[str, Any]:
        """
        Shutdown a specific service.
        
        Args:
            service_name: Name of the service to shutdown
            
        Returns:
            Dict containing service shutdown result
        """
        pass

    @abstractmethod
    async def get_startup_dependencies(self) -> List[str]:
        """
        Get startup dependencies for the Journey Manager.
        
        Returns:
            List of manager dependencies
        """
        pass

    @abstractmethod
    async def coordinate_with_manager(self, manager_name: str, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Coordinate with a specific manager.
        
        Args:
            manager_name: Name of the manager to coordinate with
            startup_context: Optional startup context data
            
        Returns:
            Dict containing coordination result
        """
        pass

    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """
        Get service capabilities.
        
        Returns:
            Dict containing service capabilities
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict containing health status
        """
        pass





