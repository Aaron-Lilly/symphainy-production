"""
Data Quality Tool - Smart City MCP Tool
Provides simplified data quality analysis for Content Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import json

# Import micro-modules
from .micro_modules.structural_checks import StructuralChecker
from .micro_modules.quality_scorer import QualityScorer
from .micro_modules.recommendations import QualityRecommendations


class DataQualityTool(BaseMCP):
    """
    Data Quality Tool for Content Pillar
    Provides simplified data quality analysis optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("DataQualityTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("DataQualityTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.structural_checker = StructuralChecker(self._logger, self._config)
            self.quality_scorer = QualityScorer(self._logger, self._config)
            self.recommendations = QualityRecommendations(self._logger, self._config)
            
            self._logger.info("DataQualityTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing DataQualityTool micro-modules: {e}")
            raise e
    
    async def analyze_quality(
        self, 
        data: Dict[str, Any], 
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze data quality and return simplified metrics for frontend.
        
        Args:
            data: Data to analyze (DataFrame as dict or file metadata)
            session_token: Smart City session token
            context: Additional context for analysis
            
        Returns:
            Simplified quality metrics for frontend display
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
            
            # Perform quality analysis using micro-modules
            quality_results = await self._perform_quality_analysis(df, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(quality_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "data_quality_analysis")
            
            self._logger.info("Data quality analysis completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in data quality analysis: {e}")
            return self._create_error_response(f"Quality analysis failed: {str(e)}")
    
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
    
    async def _perform_quality_analysis(self, df: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Perform comprehensive quality analysis using micro-modules."""
        results = {
            "overall_score": 0.0,
            "status": "good",
            "top_issues": [],
            "recommendation": "",
            "detailed_analysis": {}
        }
        
        try:
            # Structural quality checks
            structural_results = await self.structural_checker.perform_checks(df)
            results["detailed_analysis"]["structural"] = structural_results
            
            # Calculate overall quality score
            overall_score = await self.quality_scorer.calculate_score(df, structural_results)
            results["overall_score"] = overall_score
            
            # Determine status based on score
            if overall_score >= 80:
                results["status"] = "good"
            elif overall_score >= 60:
                results["status"] = "warning"
            else:
                results["status"] = "error"
            
            # Generate top issues (simplified for frontend)
            top_issues = await self._extract_top_issues(structural_results)
            results["top_issues"] = top_issues
            
            # Generate recommendation
            recommendation = await self.recommendations.generate_recommendation(
                overall_score, top_issues, context
            )
            results["recommendation"] = recommendation
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in quality analysis: {e}")
            raise e
    
    async def _extract_top_issues(self, structural_results: Dict[str, Any]) -> List[str]:
        """Extract top 3 issues for frontend display."""
        issues = []
        
        try:
            # Extract issues from structural analysis
            if "issues" in structural_results:
                for issue in structural_results["issues"][:3]:  # Top 3 only
                    if isinstance(issue, dict) and "description" in issue:
                        issues.append(issue["description"])
                    elif isinstance(issue, str):
                        issues.append(issue)
            
            # Add default issues if none found
            if not issues:
                issues = ["No major quality issues detected"]
            
            return issues
            
        except Exception as e:
            self._logger.error(f"Error extracting top issues: {e}")
            return ["Quality analysis completed with warnings"]
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "overall_score": results.get("overall_score", 0),
            "status": results.get("status", "good"),
            "top_issues": results.get("top_issues", []),
            "recommendation": results.get("recommendation", "No recommendations available"),
            "detailed_analysis": results.get("detailed_analysis", {})
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "DataQualityTool",
            "pillar": "content",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "overall_score": 0,
            "status": "error",
            "top_issues": [message],
            "recommendation": "Please check your data and try again",
            "metadata": {
                "error": message,
                "tool": "DataQualityTool",
                "pillar": "content"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "DataQualityTool",
            "pillar": "content",
            "architecture": "micro-module",
            "capabilities": [
                "data_quality_analysis",
                "structural_checks",
                "quality_scoring",
                "recommendation_generation"
            ],
            "input_formats": ["dataframe_json", "rows_columns", "dict"],
            "output_format": "simplified_frontend_metrics",
            "micro_modules": [
                "structural_checks",
                "quality_scorer", 
                "recommendations"
            ]
        }

