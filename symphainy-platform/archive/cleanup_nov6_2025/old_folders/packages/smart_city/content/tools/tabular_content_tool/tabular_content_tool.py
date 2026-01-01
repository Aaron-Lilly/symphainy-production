"""
Tabular Content Tool - Smart City MCP Tool
Provides structured data analysis for Content Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import json

# Import micro-modules
from .micro_modules.content_parser import ContentParser
from .micro_modules.data_validator import DataValidator
from .micro_modules.statistics import ContentStatistics


class TabularContentTool(BaseMCP):
    """
    Tabular Content Tool for Content Pillar
    Provides structured data analysis optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("TabularContentTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("TabularContentTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.content_parser = ContentParser(self._logger, self._config)
            self.data_validator = DataValidator(self._logger, self._config)
            self.statistics = ContentStatistics(self._logger, self._config)
            
            self._logger.info("TabularContentTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing TabularContentTool micro-modules: {e}")
            raise e
    
    async def analyze_structured_data(
        self, 
        data: Dict[str, Any], 
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze structured data and return simplified format for frontend.
        
        Args:
            data: Structured data to analyze (DataFrame as dict or file metadata)
            session_token: Smart City session token
            context: Additional context for analysis
            
        Returns:
            Simplified structured data for frontend display
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
            
            # Perform structured data analysis
            analysis_results = await self._perform_structured_analysis(df, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(analysis_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "structured_data_analysis")
            
            self._logger.info("Structured data analysis completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in structured data analysis: {e}")
            return self._create_error_response(f"Structured data analysis failed: {str(e)}")
    
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
    
    async def _perform_structured_analysis(self, df: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Perform comprehensive structured data analysis using micro-modules."""
        results = {
            "columns": [],
            "rows": [],
            "summary": {
                "total_rows": 0,
                "total_columns": 0,
                "file_type": "CSV",
                "status": "parsed",
                "basic_insights": []
            },
            "analysis": {}
        }
        
        try:
            # Extract basic structure
            results["columns"] = df.columns.tolist()
            results["rows"] = df.head(100).fillna("").astype(str).values.tolist()  # Limit to 100 rows for frontend
            
            # Calculate summary metrics
            summary = await self._calculate_summary_metrics(df)
            results["summary"] = summary
            
            # Perform data validation
            validation_results = await self.data_validator.validate_data(df)
            results["analysis"]["validation"] = validation_results
            
            # Generate content statistics
            stats_results = await self.statistics.calculate_statistics(df)
            results["analysis"]["statistics"] = stats_results
            
            # Generate basic insights
            insights = await self._generate_basic_insights(df, validation_results, stats_results)
            results["summary"]["basic_insights"] = insights
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in structured analysis: {e}")
            raise e
    
    async def _calculate_summary_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary metrics for structured data."""
        try:
            return {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "file_type": "CSV",  # Default, could be determined from context
                "status": "parsed",
                "basic_insights": []  # Will be populated by generate_basic_insights
            }
        except Exception as e:
            self._logger.error(f"Error calculating summary metrics: {e}")
            return {
                "total_rows": 0,
                "total_columns": 0,
                "file_type": "Unknown",
                "status": "error",
                "basic_insights": ["Error calculating metrics"]
            }
    
    async def _generate_basic_insights(
        self, 
        df: pd.DataFrame, 
        validation_results: Dict[str, Any], 
        stats_results: Dict[str, Any]
    ) -> List[str]:
        """Generate basic insights for frontend display."""
        insights = []
        
        try:
            # Basic structure insights
            insights.append(f"Dataset contains {len(df)} rows and {len(df.columns)} columns")
            
            # Data type insights
            numeric_cols = df.select_dtypes(include=['number']).columns
            text_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                insights.append(f"Contains {len(numeric_cols)} numeric columns")
            if len(text_cols) > 0:
                insights.append(f"Contains {len(text_cols)} text columns")
            
            # Missing data insights
            null_count = df.isnull().sum().sum()
            if null_count > 0:
                null_percentage = (null_count / (len(df) * len(df.columns))) * 100
                insights.append(f"Missing data: {null_percentage:.1f}% of values")
            else:
                insights.append("No missing values detected")
            
            # Duplicate insights
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                duplicate_percentage = (duplicate_count / len(df)) * 100
                insights.append(f"Duplicate rows: {duplicate_percentage:.1f}% of data")
            else:
                insights.append("No duplicate rows found")
            
            return insights
            
        except Exception as e:
            self._logger.error(f"Error generating basic insights: {e}")
            return ["Error generating insights"]
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "columns": results.get("columns", []),
            "rows": results.get("rows", []),
            "summary": results.get("summary", {}),
            "analysis": results.get("analysis", {})
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "TabularContentTool",
            "pillar": "content",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "columns": [],
            "rows": [],
            "summary": {
                "total_rows": 0,
                "total_columns": 0,
                "file_type": "Unknown",
                "status": "error",
                "basic_insights": [message]
            },
            "metadata": {
                "error": message,
                "tool": "TabularContentTool",
                "pillar": "content"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "TabularContentTool",
            "pillar": "content",
            "architecture": "micro-module",
            "capabilities": [
                "structured_data_analysis",
                "data_validation",
                "content_statistics",
                "basic_insights_generation"
            ],
            "input_formats": ["dataframe_json", "rows_columns", "dict"],
            "output_format": "simplified_structured_data",
            "micro_modules": [
                "content_parser",
                "data_validator",
                "statistics"
            ]
        }

