#!/usr/bin/env python3
"""
Experience Manager Interface

Defines the contract for the Experience Manager, a Smart City role responsible for
orchestrating user experience across the platform and coordinating frontend-backend integration.

WHAT (Smart City Role): I orchestrate user experience across the platform
HOW (Interface): I define the contract for frontend-backend integration and user experience coordination
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from utilities import UserContext


class ExperienceType(Enum):
    """Defines types of user experiences the Experience Manager can handle."""
    DASHBOARD_VIEW = "dashboard_view"
    FILE_UPLOAD = "file_upload"
    DATA_ANALYSIS = "data_analysis"
    WORKFLOW_CREATION = "workflow_creation"
    STRATEGIC_PLANNING = "strategic_planning"
    CROSS_PILLAR_WORKFLOW = "cross_pillar_workflow"
    REAL_TIME_COLLABORATION = "real_time_collaboration"
    
    def __str__(self):
        return self.value


class SessionStatus(Enum):
    """Defines session status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    
    def __str__(self):
        return self.value


class IExperienceManager(ABC):
    """
    Experience Manager Interface
    
    Defines the contract for the Experience Manager, a Smart City role.
    """
    
    @abstractmethod
    async def create_user_experience_session(self, session_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user experience session.
        
        Args:
            session_spec: Session specification data
            
        Returns:
            Dict containing session creation result
        """
        pass

    @abstractmethod
    async def manage_ui_state(self, session_id: str, ui_state_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage UI state for a session.
        
        Args:
            session_id: ID of the session
            ui_state_update: UI state update data
            
        Returns:
            Dict containing UI state management result
        """
        pass

    @abstractmethod
    async def coordinate_real_time_communication(self, session_id: str, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate real-time communication for a session.
        
        Args:
            session_id: ID of the session
            communication_data: Communication data
            
        Returns:
            Dict containing communication coordination result
        """
        pass

    @abstractmethod
    async def orchestrate_frontend_backend_integration(self, integration_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate frontend-backend integration.
        
        Args:
            integration_request: Integration request data
            
        Returns:
            Dict containing integration orchestration result
        """
        pass

    @abstractmethod
    async def manage_cross_dimensional_experience(self, experience_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage cross-dimensional experience coordination.
        
        Args:
            experience_request: Experience request data
            
        Returns:
            Dict containing cross-dimensional experience management result
        """
        pass

    @abstractmethod
    async def coordinate_experience_services(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate experience services.
        
        Args:
            coordination_request: Coordination request data
            
        Returns:
            Dict containing service coordination result
        """
        pass

    @abstractmethod
    async def enforce_experience_governance(self, governance_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce experience governance policies.
        
        Args:
            governance_request: Governance request data
            
        Returns:
            Dict containing governance enforcement result
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