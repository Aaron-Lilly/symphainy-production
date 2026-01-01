#!/usr/bin/env python3
"""
Journey Manager Interface

Defines the contract for the Journey Manager, a Smart City role responsible for
managing user journeys and experience flows across the platform.

WHAT (Smart City Role): I manage user journeys and experience flows
HOW (Interface): I define the contract for journey tracking, flow management, and experience optimization
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from utilities import UserContext


class JourneyStage(Enum):
    """Defines stages in a user journey."""
    ONBOARDING = "onboarding"
    EXPLORATION = "exploration"
    ENGAGEMENT = "engagement"
    MASTERY = "mastery"
    ADVANCED = "advanced"
    
    def __str__(self):
        return self.value


class JourneyStatus(Enum):
    """Defines journey status states."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    
    def __str__(self):
        return self.value


class FlowType(Enum):
    """Defines types of user flows."""
    LINEAR = "linear"
    BRANCHING = "branching"
    PARALLEL = "parallel"
    ITERATIVE = "iterative"
    
    def __str__(self):
        return self.value


class IJourneyManager(ABC):
    """
    Journey Manager Interface
    
    Defines the contract for the Journey Manager, a Smart City role.
    """
    
    @abstractmethod
    async def create_user_journey(self, journey_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user journey.
        
        Args:
            journey_spec: Journey specification data
            
        Returns:
            Dict containing journey creation result
        """
        pass

    @abstractmethod
    async def update_user_journey(self, journey_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing user journey.
        
        Args:
            journey_id: ID of the journey to update
            updates: Update data
            
        Returns:
            Dict containing journey update result
        """
        pass

    @abstractmethod
    async def execute_user_journey(self, journey_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a user journey.
        
        Args:
            journey_id: ID of the journey to execute
            user_context: User context data
            
        Returns:
            Dict containing journey execution result
        """
        pass

    @abstractmethod
    async def track_journey_progress(self, journey_id: str, user_id: str) -> Dict[str, Any]:
        """
        Track progress in a user journey.
        
        Args:
            journey_id: ID of the journey
            user_id: ID of the user
            
        Returns:
            Dict containing journey progress tracking result
        """
        pass

    @abstractmethod
    async def optimize_journey_flow(self, journey_id: str, optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize the flow of a user journey.
        
        Args:
            journey_id: ID of the journey
            optimization_data: Optimization data
            
        Returns:
            Dict containing journey flow optimization result
        """
        pass

    @abstractmethod
    async def get_journey_analytics(self, journey_id: str, analytics_type: str) -> Dict[str, Any]:
        """
        Get analytics for a user journey.
        
        Args:
            journey_id: ID of the journey
            analytics_type: Type of analytics to retrieve
            
        Returns:
            Dict containing journey analytics
        """
        pass

    @abstractmethod
    async def manage_journey_milestones(self, journey_id: str, milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Manage milestones in a user journey.
        
        Args:
            journey_id: ID of the journey
            milestones: List of milestone data
            
        Returns:
            Dict containing milestone management result
        """
        pass

    @abstractmethod
    async def execute_operation(self, operation_type, operation_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a journey operation.
        
        Args:
            operation_type: Type of operation to execute
            operation_data: Operation data
            user_context: User context data
            
        Returns:
            Dict containing operation execution result
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