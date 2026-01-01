#!/usr/bin/env python3
"""
Solution Manager Service Protocol

Clean protocol definition for Solution Manager services - contracts only, no implementations.
Aligned with new architecture (Manager hierarchy, Journey orchestration).

WHAT (Solution Manager Role): I define the contract for Solution Manager services
HOW (Solution Manager Protocol): I provide solution design and journey orchestration capabilities
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from bases.protocols.manager_service_protocol import ManagerServiceProtocol


@runtime_checkable
class SolutionManagerServiceProtocol(ManagerServiceProtocol, Protocol):
    """
    Protocol for Solution Manager services.
    
    Solution Manager orchestrates solutions and coordinates journey flow (Solution → Journey).
    Extends ManagerServiceProtocol with solution-specific capabilities.
    """
    
    # Solution Design Methods
    async def design_solution(self, solution_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design a solution based on requirements.
        
        Args:
            solution_request: Solution request with solution_type and requirements
        
        Returns:
            Solution design result with solution_id, design_status, etc.
        """
        ...
    
    async def discover_solutions(self) -> Dict[str, Any]:
        """
        Discover available solutions on the platform.
        
        Returns:
            Dictionary with available solutions and their capabilities
        """
        ...
    
    async def orchestrate_solution(self, solution_type: str, solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a specific solution type with context.
        
        Args:
            solution_type: Type of solution to orchestrate
            solution_context: Context for solution orchestration
        
        Returns:
            Orchestration result
        """
        ...
    
    async def generate_poc(self, poc_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proof of concept for a solution.
        
        Args:
            poc_request: POC request with solution_type and scope
        
        Returns:
            POC generation result
        """
        ...
    
    # Journey Orchestration Methods
    async def orchestrate_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate journey by calling Journey Manager.
        
        This implements the top-down flow: Solution Manager → Journey Manager
        
        Args:
            journey_context: Journey context with solution_id, solution_type, user_context
        
        Returns:
            Journey orchestration result
        """
        ...
    
    # Solution Management
    async def get_solution(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get solution by ID.
        
        Args:
            solution_id: Solution identifier
        
        Returns:
            Solution data or None if not found
        """
        ...
    
    async def list_solutions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List solutions with optional filters.
        
        Args:
            filters: Optional filters for solution listing
        
        Returns:
            List of solutions
        """
        ...








