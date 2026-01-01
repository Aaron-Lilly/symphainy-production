"""
Content Summary Tool - Smart City MCP Tool
Provides content summarization for Content Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import json

# Import micro-modules
from .micro_modules.content_summarizer import ContentSummarizer
from .micro_modules.insight_extractor import InsightExtractor
from .micro_modules.summary_formatter import SummaryFormatter


class ContentSummaryTool(BaseMCP):
    """
    Content Summary Tool for Content Pillar
    Provides content summarization optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("ContentSummaryTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("ContentSummaryTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.content_summarizer = ContentSummarizer(self._logger, self._config)
            self.insight_extractor = InsightExtractor(self._logger, self._config)
            self.summary_formatter = SummaryFormatter(self._logger, self._config)
            
            self._logger.info("ContentSummaryTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing ContentSummaryTool micro-modules: {e}")
            raise e
    
    async def generate_summary(
        self, 
        data: Dict[str, Any], 
        summary_type: str = "comprehensive",
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate content summary for frontend display.
        
        Args:
            data: Data to summarize (DataFrame as dict or file metadata)
            summary_type: Type of summary to generate
            session_token: Smart City session token
            context: Additional context for summary
            
        Returns:
            Summary data for frontend display
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
            
            # Generate summary
            summary_results = await self._perform_summarization(df, summary_type, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(summary_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "content_summarization")
            
            self._logger.info("Content summarization completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in content summarization: {e}")
            return self._create_error_response(f"Summarization failed: {str(e)}")
    
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
    
    async def _perform_summarization(self, df: pd.DataFrame, summary_type: str, context: str) -> Dict[str, Any]:
        """Perform content summarization using micro-modules."""
        results = {
            "summary": "",
            "key_insights": [],
            "data_highlights": [],
            "recommendations": [],
            "summary_metadata": {}
        }
        
        try:
            # Generate content summary
            summary = await self.content_summarizer.generate_summary(df, summary_type, context)
            results["summary"] = summary
            
            # Extract key insights
            insights = await self.insight_extractor.extract_insights(df, summary_type)
            results["key_insights"] = insights
            
            # Generate data highlights
            highlights = await self.insight_extractor.extract_highlights(df)
            results["data_highlights"] = highlights
            
            # Generate recommendations
            recommendations = await self.content_summarizer.generate_recommendations(df, insights)
            results["recommendations"] = recommendations
            
            # Add summary metadata
            results["summary_metadata"] = await self._generate_summary_metadata(df, summary_type)
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in summarization: {e}")
            raise e
    
    async def _generate_summary_metadata(self, df: pd.DataFrame, summary_type: str) -> Dict[str, Any]:
        """Generate metadata for the summary."""
        try:
            return {
                "data_rows": len(df),
                "data_columns": len(df.columns),
                "summary_type": summary_type,
                "numeric_columns": len(df.select_dtypes(include=['number']).columns),
                "text_columns": len(df.select_dtypes(include=['object']).columns),
                "missing_values": df.isnull().sum().sum(),
                "data_quality_score": await self._calculate_data_quality_score(df)
            }
        except Exception as e:
            self.logger.error(f"Error generating summary metadata: {e}")
            return {}
    
    async def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate a simple data quality score."""
        try:
            if df.empty:
                return 0.0
            
            score = 100.0
            
            # Deduct for missing values
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            score -= min(missing_percentage * 2, 30)  # Max 30 point deduction
            
            # Deduct for duplicates
            duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
            score -= min(duplicate_percentage * 2, 20)  # Max 20 point deduction
            
            # Deduct for empty columns
            empty_columns = df.isnull().all().sum()
            score -= min(empty_columns * 10, 20)  # Max 20 point deduction
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating data quality score: {e}")
            return 0.0
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "summary": results.get("summary", ""),
            "key_insights": results.get("key_insights", []),
            "data_highlights": results.get("data_highlights", []),
            "recommendations": results.get("recommendations", []),
            "summary_metadata": results.get("summary_metadata", {})
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "ContentSummaryTool",
            "pillar": "content",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "summary": f"Error: {message}",
            "key_insights": ["Unable to generate insights due to error"],
            "data_highlights": [],
            "recommendations": ["Please check your data and try again"],
            "metadata": {
                "error": message,
                "tool": "ContentSummaryTool",
                "pillar": "content"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "ContentSummaryTool",
            "pillar": "content",
            "architecture": "micro-module",
            "capabilities": [
                "content_summarization",
                "insight_extraction",
                "data_highlights",
                "recommendation_generation"
            ],
            "summary_types": ["comprehensive", "executive", "technical", "brief"],
            "input_formats": ["dataframe_json", "rows_columns", "dict"],
            "output_format": "frontend_summary",
            "micro_modules": [
                "content_summarizer",
                "insight_extractor",
                "summary_formatter"
            ]
        }

