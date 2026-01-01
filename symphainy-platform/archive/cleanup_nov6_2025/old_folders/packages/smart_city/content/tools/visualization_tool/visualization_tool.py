"""
Content Visualization Tool - Smart City MCP Tool
Provides data visualization for Content Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import json

# Import micro-modules
from .micro_modules.chart_generator import ChartGenerator
from .micro_modules.data_formatter import DataFormatter
from .micro_modules.visual_insights import VisualInsights


class ContentVisualizationTool(BaseMCP):
    """
    Content Visualization Tool for Content Pillar
    Provides data visualization optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("ContentVisualizationTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("ContentVisualizationTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.chart_generator = ChartGenerator(self._logger, self._config)
            self.data_formatter = DataFormatter(self._logger, self._config)
            self.visual_insights = VisualInsights(self._logger, self._config)
            
            self._logger.info("ContentVisualizationTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing ContentVisualizationTool micro-modules: {e}")
            raise e
    
    async def generate_visualization(
        self, 
        data: Dict[str, Any], 
        chart_type: str = "bar",
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate data visualization for frontend display.
        
        Args:
            data: Data to visualize (DataFrame as dict or file metadata)
            chart_type: Type of chart to generate
            session_token: Smart City session token
            context: Additional context for visualization
            
        Returns:
            Visualization data for frontend display
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = await self._validate_session(session_token)
                if not session_valid:
                    return self._create_error_response("Invalid session token")
            
            # Convert data to DataFrame if needed
            df = await self._prepare_dataframe(data)
            if df is None:
                return self._create_error_response("Invalid data format")
            
            # Generate visualization
            visualization_results = await self._perform_visualization(df, chart_type, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(visualization_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "data_visualization")
            
            self._logger.info("Data visualization completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in data visualization: {e}")
            return self._create_error_response(f"Visualization failed: {str(e)}")
    
    async def _prepare_dataframe(self, data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Prepare DataFrame from various data formats."""
        try:
            if isinstance(data, dict):
                if "dataframe_json" in data:
                    # Data is already a DataFrame JSON
                    return pd.read_json(data["dataframe_json"])
                elif "rows" in data and "columns" in data:
                    # Data is structured as rows/columns
                    return pd.DataFrame(data["rows"], columns=data["columns"])
                else:
                    # Try to convert dict to DataFrame
                    return pd.DataFrame(data)
            return None
        except Exception as e:
            self._logger.error(f"Error preparing DataFrame: {e}")
            return None
    
    async def _perform_visualization(self, df: pd.DataFrame, chart_type: str, context: str) -> Dict[str, Any]:
        """Perform data visualization using micro-modules."""
        results = {
            "chart_type": chart_type,
            "data_points": [],
            "chart_config": {},
            "insights": [],
            "recommendations": []
        }
        
        try:
            # Format data for visualization
            formatted_data = await self.data_formatter.format_for_chart(df, chart_type)
            results["data_points"] = formatted_data
            
            # Generate chart configuration
            chart_config = await self.chart_generator.generate_config(chart_type, formatted_data, context)
            results["chart_config"] = chart_config
            
            # Generate visual insights
            insights = await self.visual_insights.generate_insights(df, chart_type, formatted_data)
            results["insights"] = insights
            
            # Generate recommendations
            recommendations = await self.visual_insights.generate_recommendations(chart_type, insights)
            results["recommendations"] = recommendations
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in visualization: {e}")
            raise e
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "chart_type": results.get("chart_type", "bar"),
            "data_points": results.get("data_points", []),
            "chart_config": results.get("chart_config", {}),
            "insights": results.get("insights", []),
            "recommendations": results.get("recommendations", [])
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "ContentVisualizationTool",
            "pillar": "content",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "chart_type": "bar",
            "data_points": [],
            "chart_config": {},
            "insights": [message],
            "recommendations": ["Please check your data and try again"],
            "metadata": {
                "error": message,
                "tool": "ContentVisualizationTool",
                "pillar": "content"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "ContentVisualizationTool",
            "pillar": "content",
            "architecture": "micro-module",
            "capabilities": [
                "data_visualization",
                "chart_generation",
                "visual_insights",
                "chart_recommendations"
            ],
            "supported_chart_types": ["bar", "line", "pie", "scatter", "histogram"],
            "input_formats": ["dataframe_json", "rows_columns", "dict"],
            "output_format": "frontend_visualization",
            "micro_modules": [
                "chart_generator",
                "data_formatter",
                "visual_insights"
            ]
        }

