#!/usr/bin/env python3
"""
Workflow Visualization Protocol

Defines the interface contract for workflow visualization capabilities.
Used by infrastructure abstractions to ensure consistent workflow visualization.

WHAT (Protocol Role): I define the interface contract for workflow visualization
HOW (Protocol Implementation): I specify the required methods and data structures
"""

from typing import Protocol
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class VisualizationType(Enum):
    """Types of workflow visualizations."""
    FLOWCHART = "flowchart"
    SWIMLANE = "swimlane"
    GANTT = "gantt"
    NETWORK = "network"


@dataclass
class VisualizationData:
    """Workflow visualization data class."""
    type: VisualizationType
    title: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class VisualizationResult:
    """Workflow visualization result data class."""
    success: bool
    visualization_data: Optional[VisualizationData]
    error: Optional[str]
    created_at: datetime


class WorkflowVisualizationProtocol(Protocol):
    """
    Protocol for workflow visualization capabilities.
    
    Defines the interface contract that all workflow visualization implementations
    must follow to ensure consistent workflow visualization across the platform.
    """
    
    async def create_flowchart(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create flowchart visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with flowchart data
        """
        ...
    
    async def create_swimlane_diagram(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create swimlane diagram visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with swimlane diagram data
        """
        ...
    
    async def create_gantt_chart(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create Gantt chart visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with Gantt chart data
        """
        ...
    
    async def create_network_diagram(self, workflow_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create network diagram visualization.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            VisualizationResult with network diagram data
        """
        ...
    
    async def get_supported_visualization_types(self) -> List[VisualizationType]:
        """
        Get list of supported visualization types.
        
        Returns:
            List of supported visualization types
        """
        ...
    
    async def validate_workflow_data(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow data for visualization.
        
        Args:
            workflow_data: Workflow data to validate
            
        Returns:
            Dict with validation results
        """
        ...


