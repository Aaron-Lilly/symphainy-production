#!/usr/bin/env python3
"""
Journey Orchestrator Interface

Defines the contract for the Journey Orchestrator Service, responsible for
orchestrating business outcome journeys across all dimensions.

WHAT (Journey Solution Role): I orchestrate business outcome journeys across all dimensions
HOW (Interface): I define the contract for journey creation, cross-dimensional execution, and solution architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from utilities import UserContext


class JourneyDimension(Enum):
    """Defines journey dimensions."""
    EXPERIENCE = "experience"
    BUSINESS_ENABLEMENT = "business_enablement"
    SMART_CITY = "smart_city"
    SOLUTION = "solution"
    
    def __str__(self):
        return self.value


class JourneyStatus(Enum):
    """Defines journey status states."""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    def __str__(self):
        return self.value


class IJourneyOrchestrator(ABC):
    """
    Journey Orchestrator Interface
    
    Defines the contract for the Journey Orchestrator Service.
    """
    
    @abstractmethod
    async def create_business_outcome_journey(self, business_outcome: str, use_case: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Create a complete business outcome journey across all dimensions.
        
        Args:
            business_outcome: The business outcome to achieve
            use_case: The use case for the journey
            user_context: User context data
            
        Returns:
            Dict containing journey creation result
        """
        pass

    @abstractmethod
    async def orchestrate_cross_dimensional_journey(self, business_outcome: str, use_case: str, solution_architecture: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Orchestrate cross-dimensional execution of a journey.
        
        Args:
            business_outcome: The business outcome to achieve
            use_case: The use case for the journey
            solution_architecture: Solution architecture data
            user_context: User context data
            
        Returns:
            Dict containing cross-dimensional orchestration result
        """
        pass

    @abstractmethod
    async def create_journey_record(self, business_outcome: str, use_case: str, journey_result: Dict[str, Any], user_context: UserContext) -> str:
        """
        Create a journey record for tracking.
        
        Args:
            business_outcome: The business outcome
            use_case: The use case
            journey_result: Journey execution result
            user_context: User context data
            
        Returns:
            Journey ID
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
    async def update_journey_status(self, journey_id: str, status: JourneyStatus) -> Dict[str, Any]:
        """
        Update status of a specific journey.
        
        Args:
            journey_id: ID of the journey
            status: New status
            
        Returns:
            Dict containing status update result
        """
        pass

    @abstractmethod
    async def get_active_journeys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get active journeys for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of active journeys
        """
        pass

    @abstractmethod
    async def get_journey_analytics(self, journey_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific journey.
        
        Args:
            journey_id: ID of the journey
            
        Returns:
            Dict containing journey analytics
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





