#!/usr/bin/env python3
"""
Insights Analysis Interface

Interface for insights analysis capabilities provided by the Insights Pillar role.
Defines the contract for data analysis, visualization, APG mode, and reporting operations.

WHAT (Business Enablement Role): I analyze data and generate insights for business decision-making
HOW (Interface): I define the contract for insights analysis operations
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from utilities import UserContext


class AnalysisType(Enum):
    """Types of analysis that can be performed."""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    TREND_ANALYSIS = "trend_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class VisualizationType(Enum):
    """Types of visualizations that can be generated."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    DASHBOARD = "dashboard"
    TABLE = "table"
    TREEMAP = "treemap"
    SANKEY_DIAGRAM = "sankey_diagram"
    NETWORK_GRAPH = "network_graph"


class APGMode(Enum):
    """APG (Advanced Pattern Generation) modes."""
    DISABLED = "disabled"
    ENABLED = "enabled"
    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class AnalysisRequest:
    """Request to perform data analysis."""
    data: Union[Dict[str, Any], List[Dict[str, Any]]]
    analysis_type: AnalysisType
    user_context: UserContext
    session_id: str
    options: Dict[str, Any] = None
    apg_mode: APGMode = APGMode.AUTO
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class AnalysisResponse:
    """Response from data analysis with agentic insights."""
    success: bool
    analysis_id: str
    analysis_type: AnalysisType
    results: Dict[str, Any]
    insights: List[str]
    confidence_score: float
    processing_time: float
    apg_insights: Optional[Dict[str, Any]] = None
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None
    # New agentic fields
    recommendations: Optional[List[Dict[str, Any]]] = None
    visualizations: Optional[Dict[str, Any]] = None
    agui_output: Optional[Dict[str, Any]] = None


@dataclass
class VisualizationRequest:
    """Request to generate visualization."""
    data: Dict[str, Any]
    visualization_type: VisualizationType
    user_context: UserContext
    session_id: str
    options: Dict[str, Any] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class VisualizationResponse:
    """Response from visualization generation."""
    success: bool
    visualization_id: str
    visualization_type: VisualizationType
    visualization_data: Dict[str, Any]
    chart_config: Dict[str, Any]
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class APGRequest:
    """Request for Advanced Pattern Generation."""
    data: Dict[str, Any]
    user_context: UserContext
    session_id: str
    pattern_types: List[str] = None
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.pattern_types is None:
            self.pattern_types = ["trends", "anomalies", "correlations", "clusters"]
        if self.options is None:
            self.options = {}


@dataclass
class APGResponse:
    """Response from Advanced Pattern Generation."""
    success: bool
    apg_id: str
    patterns: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence_scores: Dict[str, float]
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class ReportRequest:
    """Request to generate a report."""
    analysis_ids: List[str]
    visualization_ids: List[str]
    user_context: UserContext
    session_id: str
    report_format: str = "pdf"
    template: Optional[str] = None
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class ReportResponse:
    """Response from report generation."""
    success: bool
    report_id: str
    report_url: str
    report_data: bytes
    report_metadata: Dict[str, Any]
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


class IInsightsAnalysis(ABC):
    """
    Insights Analysis Interface
    
    Defines the contract for insights analysis operations provided by the Insights Pillar role.
    Handles data analysis, visualization, APG mode, and reporting operations.
    
    WHAT (Business Enablement Role): I analyze data and generate insights for business decision-making
    HOW (Interface): I define the contract for insights analysis operations
    """
    
    @abstractmethod
    async def analyze_data(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Perform data analysis on provided dataset.
        
        Args:
            request: Analysis request with data and analysis type
            
        Returns:
            AnalysisResponse with analysis results and insights
        """
        pass
    
    @abstractmethod
    async def generate_visualization(self, request: VisualizationRequest) -> VisualizationResponse:
        """
        Generate visualization for data.
        
        Args:
            request: Visualization request with data and chart type
            
        Returns:
            VisualizationResponse with visualization data and configuration
        """
        pass
    
    @abstractmethod
    async def enable_apg_mode(self, request: APGRequest) -> APGResponse:
        """
        Enable Advanced Pattern Generation mode for enhanced insights.
        
        Args:
            request: APG request with data and pattern types
            
        Returns:
            APGResponse with generated patterns and insights
        """
        pass
    
    @abstractmethod
    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        """
        Generate comprehensive report from analysis and visualizations.
        
        Args:
            request: Report request with analysis and visualization IDs
            
        Returns:
            ReportResponse with generated report
        """
        pass
    
    @abstractmethod
    async def get_analysis_history(self, user_context: UserContext, 
                                  limit: int = 100, offset: int = 0) -> List[AnalysisResponse]:
        """
        Get analysis history for a user.
        
        Args:
            user_context: User context for authorization
            limit: Maximum number of analyses to return
            offset: Number of analyses to skip
            
        Returns:
            List of previous analysis responses
        """
        pass
    
    @abstractmethod
    async def get_visualization_history(self, user_context: UserContext,
                                      limit: int = 100, offset: int = 0) -> List[VisualizationResponse]:
        """
        Get visualization history for a user.
        
        Args:
            user_context: User context for authorization
            limit: Maximum number of visualizations to return
            offset: Number of visualizations to skip
            
        Returns:
            List of previous visualization responses
        """
        pass
    
    @abstractmethod
    async def get_analysis_by_id(self, analysis_id: str, user_context: UserContext) -> Optional[AnalysisResponse]:
        """
        Get specific analysis by ID.
        
        Args:
            analysis_id: The analysis ID to retrieve
            user_context: User context for authorization
            
        Returns:
            AnalysisResponse or None if not found
        """
        pass
    
    @abstractmethod
    async def get_visualization_by_id(self, visualization_id: str, user_context: UserContext) -> Optional[VisualizationResponse]:
        """
        Get specific visualization by ID.
        
        Args:
            visualization_id: The visualization ID to retrieve
            user_context: User context for authorization
            
        Returns:
            VisualizationResponse or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_analysis(self, analysis_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Delete an analysis and its associated data.
        
        Args:
            analysis_id: The analysis ID to delete
            user_context: User context for authorization
            
        Returns:
            Dict with deletion status
        """
        pass
    
    @abstractmethod
    async def delete_visualization(self, visualization_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Delete a visualization and its associated data.
        
        Args:
            visualization_id: The visualization ID to delete
            user_context: User context for authorization
            
        Returns:
            Dict with deletion status
        """
        pass
    
    @abstractmethod
    async def search_analyses(self, query: str, user_context: UserContext,
                             analysis_type: Optional[AnalysisType] = None,
                             limit: int = 100) -> List[AnalysisResponse]:
        """
        Search analyses by content or metadata.
        
        Args:
            query: Search query string
            user_context: User context for authorization
            analysis_type: Optional analysis type filter
            limit: Maximum number of results
            
        Returns:
            List of matching analysis responses
        """
        pass
    
    @abstractmethod
    async def get_insights_analytics(self, user_context: UserContext,
                                    time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Get insights analysis analytics and statistics.
        
        Args:
            user_context: User context for analytics
            time_range: Optional time range for analytics
            
        Returns:
            Dict with analytics data
        """
        pass
    
    @abstractmethod
    async def batch_analyze_data(self, requests: List[AnalysisRequest]) -> List[AnalysisResponse]:
        """
        Perform multiple analyses in a batch operation.
        
        Args:
            requests: List of analysis requests
            
        Returns:
            List of analysis responses
        """
        pass
    
    @abstractmethod
    async def batch_generate_visualizations(self, requests: List[VisualizationRequest]) -> List[VisualizationResponse]:
        """
        Generate multiple visualizations in a batch operation.
        
        Args:
            requests: List of visualization requests
            
        Returns:
            List of visualization responses
        """
        pass
    
    @abstractmethod
    async def get_supported_analysis_types(self) -> List[AnalysisType]:
        """
        Get list of supported analysis types.
        
        Returns:
            List of supported analysis types
        """
        pass
    
    @abstractmethod
    async def get_supported_visualization_types(self) -> List[VisualizationType]:
        """
        Get list of supported visualization types.
        
        Returns:
            List of supported visualization types
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Get health status of the insights analysis service.
        
        Returns:
            Dict with health status information
        """
        pass



