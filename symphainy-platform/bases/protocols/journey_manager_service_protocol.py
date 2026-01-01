#!/usr/bin/env python3
"""
Journey Manager Service Protocol

Clean protocol definition for Journey Manager services - contracts only, no implementations.
Aligned with new architecture (Manager hierarchy, Experience Foundation SDK).

WHAT (Journey Manager Role): I define the contract for Journey Manager services
HOW (Journey Manager Protocol): I provide journey orchestration and experience composition capabilities
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from bases.protocols.manager_service_protocol import ManagerServiceProtocol


@runtime_checkable
class JourneyManagerServiceProtocol(ManagerServiceProtocol, Protocol):
    """
    Protocol for Journey Manager services.
    
    Journey Manager orchestrates journeys and coordinates experience flow (Journey → Experience Foundation).
    Extends ManagerServiceProtocol with journey-specific capabilities.
    
    Note: Experience is now a Foundation SDK, not a Manager.
    Journey Manager composes experience "head" using Experience Foundation SDK.
    """
    
    # Journey Design Methods
    async def design_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a journey based on context.
        
        Args:
            journey_context: Journey context with solution_id, solution_type, user_context
        
        Returns:
            Journey design result with journey_id, design_status, etc.
        """
        ...
    
    async def get_journey(self, journey_id: str) -> Optional[Dict[str, Any]]:
        """
        Get journey by ID.
        
        Args:
            journey_id: Journey identifier
        
        Returns:
            Journey data or None if not found
        """
        ...
    
    async def list_journeys(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List journeys with optional filters.
        
        Args:
            filters: Optional filters for journey listing
        
        Returns:
            List of journeys
        """
        ...
    
    # Experience Composition (via Experience Foundation SDK)
    async def compose_experience_head(self, realm_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compose experience "head" using Experience Foundation SDK.
        
        This creates Frontend Gateway and User Experience services via Experience Foundation.
        
        Args:
            realm_name: Name of the realm requesting experience composition
            config: Configuration for experience services
        
        Returns:
            Experience composition result with frontend_gateway, user_experience, etc.
        """
        ...
    
    # Journey Orchestration
    async def orchestrate_journey_execution(self, journey_id: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate journey execution.
        
        Args:
            journey_id: Journey identifier
            execution_context: Execution context for journey
        
        Returns:
            Journey execution result
        """
        ...
    
    # Journey Lifecycle
    async def start_journey(self, journey_id: str) -> Dict[str, Any]:
        """Start a journey execution."""
        ...
    
    async def pause_journey(self, journey_id: str) -> Dict[str, Any]:
        """Pause a journey execution."""
        ...
    
    async def resume_journey(self, journey_id: str) -> Dict[str, Any]:
        """Resume a paused journey execution."""
        ...
    
    async def complete_journey(self, journey_id: str) -> Dict[str, Any]:
        """Complete a journey execution."""
        ...








