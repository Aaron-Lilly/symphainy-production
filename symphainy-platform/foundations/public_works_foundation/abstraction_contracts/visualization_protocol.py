#!/usr/bin/env python3
"""
Visualization Protocol

Abstraction contract for visualization capabilities.

WHAT (Protocol Role): I define the interface for visualization services
HOW (Protocol Implementation): I specify methods for creating visual displays
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class VisualizationResult:
    """Result from visualization operations."""
    success: bool
    visualization_type: str
    chart_data: Dict[str, Any]
    image_base64: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


class VisualizationProtocol(Protocol):
    """
    Protocol for visualization capabilities.
    
    Defines the interface for creating visual displays including:
    - Summary dashboards
    - Roadmap visualizations
    - Financial analysis charts
    - Business metrics dashboards
    """
    
    async def create_summary_dashboard(self, pillar_outputs: Dict[str, Any]) -> VisualizationResult:
        """
        Create summary dashboard showing outputs from all pillars.
        
        Args:
            pillar_outputs: Summary outputs from Data, Insights, and Operations pillars
            
        Returns:
            VisualizationResult: Dashboard visualization
        """
        ...
    
    async def create_roadmap_visualization(self, roadmap_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create roadmap visualization as standalone visual element.
        
        Args:
            roadmap_data: Roadmap data from Strategic Planning service
            
        Returns:
            VisualizationResult: Roadmap visualization
        """
        ...
    
    async def create_financial_visualization(self, financial_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create financial analysis visualization.
        
        Args:
            financial_data: Financial analysis data
            
        Returns:
            VisualizationResult: Financial visualization
        """
        ...
    
    async def create_metrics_dashboard(self, metrics_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create business metrics dashboard.
        
        Args:
            metrics_data: Business metrics data
            
        Returns:
            VisualizationResult: Metrics dashboard
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the visualization adapter.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        ...