#!/usr/bin/env python3
"""
Coexistence Blueprint Protocol

Defines the interface contract for coexistence blueprint generation capabilities.
Used by infrastructure abstractions to ensure consistent blueprint generation.

WHAT (Protocol Role): I define the interface contract for coexistence blueprint generation
HOW (Protocol Implementation): I specify the methods that all blueprint generation implementations must follow
"""

from typing import Protocol
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class BlueprintResult:
    """Coexistence blueprint result data class."""
    success: bool
    blueprint: Dict[str, Any]
    implementation_roadmap: List[Dict[str, Any]]
    success_metrics: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: str = None


class CoexistenceBlueprintProtocol(Protocol):
    """
    Protocol for coexistence blueprint generation capabilities.
    
    Defines the interface contract that all blueprint generation implementations
    must follow to ensure consistent blueprint generation across the platform.
    """
    
    async def generate_coexistence_blueprint(self, coexistence_data: Dict[str, Any], 
                                           current_state: Dict[str, Any], target_state: Dict[str, Any]) -> BlueprintResult:
        """
        Generate coexistence blueprint from analysis data.
        
        Args:
            coexistence_data: Coexistence analysis results
            current_state: Current state data
            target_state: Target state data
            
        Returns:
            BlueprintResult with generated blueprint and metadata
        """
        ...
    
    async def create_coexistence_blueprint(self, requirements: Dict[str, Any], 
                                         constraints: Dict[str, Any], user_context: Dict[str, Any]) -> BlueprintResult:
        """
        Create coexistence blueprint directly from requirements.
        
        Args:
            requirements: Blueprint requirements
            constraints: Implementation constraints
            user_context: User context data
            
        Returns:
            BlueprintResult with created blueprint and metadata
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the coexistence blueprint service.
        
        Returns:
            Dict with health status information
        """
        ...


