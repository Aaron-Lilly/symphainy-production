"""
Insights Modeling Tool - Smart City MCP Tool
Provides modeling insights for Insights Pillar frontend
"""

from typing import Dict, Any, List, Optional
from backend.bases.smart_city.base_mcp import BaseMCP
from backend.bases.smart_city.base_tool import BaseTool
from backend.smart_city_library import get_logging_service, get_configuration_service
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
import pandas as pd
import numpy as np
import json

# Import micro-modules
from .micro_modules.correlation_analyzer import CorrelationAnalyzer
from .micro_modules.trend_detector import TrendDetector
from .micro_modules.pattern_analyzer import PatternAnalyzer
from .micro_modules.predictive_analyzer import PredictiveAnalyzer


class InsightsModelingTool(BaseMCP):
    """
    Insights Modeling Tool for Insights Pillar
    Provides modeling insights optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("InsightsModelingTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("InsightsModelingTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.correlation_analyzer = CorrelationAnalyzer(self._logger, self._config)
            self.trend_detector = TrendDetector(self._logger, self._config)
            self.pattern_analyzer = PatternAnalyzer(self._logger, self._config)
            self.predictive_analyzer = PredictiveAnalyzer(self._logger, self._config)
            
            self._logger.info("InsightsModelingTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing InsightsModelingTool micro-modules: {e}")
            raise e
    
    async def generate_modeling_insights(
        self, 
        data: Dict[str, Any], 
        analysis_type: str = "comprehensive",
        target_variable: Optional[str] = None,
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate modeling insights for frontend display.
        
        Args:
            data: Data to analyze (DataFrame as dict or file metadata)
            analysis_type: Type of analysis to perform
            target_variable: Target variable for prediction analysis
            session_token: Smart City session token
            context: Additional context for analysis
            
        Returns:
            Modeling insights for frontend display
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
            
            # Generate modeling insights
            insights_results = await self._perform_modeling_analysis(df, analysis_type, target_variable, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(insights_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "modeling_insights")
            
            self._logger.info("Modeling insights completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in modeling insights: {e}")
            return self._create_error_response(f"Modeling insights failed: {str(e)}")
    
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
    
    async def _perform_modeling_analysis(
        self, 
        df: pd.DataFrame, 
        analysis_type: str, 
        target_variable: Optional[str], 
        context: str
    ) -> Dict[str, Any]:
        """Perform modeling analysis using micro-modules."""
        results = {
            "insights": [],
            "statistical_measures": {},
            "model_recommendations": [],
            "data_quality_assessment": {},
            "predictive_analysis": {},
            "analysis_type": analysis_type,
            "target_variable": target_variable
        }
        
        try:
            # Get numeric columns for analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) == 0:
                results["insights"].append("No numeric columns found for modeling analysis")
                return results
            
            # Perform correlation analysis
            if analysis_type in ["comprehensive", "correlation"]:
                correlation_results = await self.correlation_analyzer.analyze_correlations(df, numeric_cols)
                results["insights"].extend(correlation_results.get("insights", []))
                results["statistical_measures"].update(correlation_results.get("measures", {}))
            
            # Perform trend analysis
            if analysis_type in ["comprehensive", "trend"]:
                trend_results = await self.trend_detector.detect_trends(df, numeric_cols)
                results["insights"].extend(trend_results.get("insights", []))
                results["statistical_measures"].update(trend_results.get("measures", {}))
            
            # Perform pattern analysis
            if analysis_type in ["comprehensive", "pattern"]:
                pattern_results = await self.pattern_analyzer.analyze_patterns(df, numeric_cols)
                results["insights"].extend(pattern_results.get("insights", []))
                results["statistical_measures"].update(pattern_results.get("measures", {}))
            
            # Perform predictive analysis
            if analysis_type in ["comprehensive", "prediction"] and target_variable:
                predictive_results = await self.predictive_analyzer.analyze_predictive_potential(
                    df, target_variable, numeric_cols
                )
                results["insights"].extend(predictive_results.get("insights", []))
                results["predictive_analysis"] = predictive_results.get("analysis", {})
                results["statistical_measures"].update(predictive_results.get("measures", {}))
            
            # Generate model recommendations
            results["model_recommendations"] = await self._generate_model_recommendations(
                df, analysis_type, target_variable, results["insights"]
            )
            
            # Assess data quality
            results["data_quality_assessment"] = await self._assess_data_quality(df, numeric_cols)
            
            # Limit insights to top findings
            results["insights"] = results["insights"][:10]
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in modeling analysis: {e}")
            raise e
    
    async def _generate_model_recommendations(
        self, 
        df: pd.DataFrame, 
        analysis_type: str, 
        target_variable: Optional[str], 
        insights: List[str]
    ) -> List[str]:
        """Generate model recommendations based on analysis."""
        try:
            recommendations = []
            
            # Analysis type specific recommendations
            if analysis_type == "prediction" and target_variable:
                recommendations.append("Consider using regression models for prediction")
                recommendations.append("Evaluate model performance with cross-validation")
            elif analysis_type == "correlation":
                recommendations.append("Use correlation analysis for feature selection")
                recommendations.append("Consider dimensionality reduction techniques")
            elif analysis_type == "trend":
                recommendations.append("Apply time series analysis for trend modeling")
                recommendations.append("Consider seasonal decomposition")
            elif analysis_type == "pattern":
                recommendations.append("Use clustering algorithms for pattern detection")
                recommendations.append("Consider anomaly detection methods")
            
            # Data quality recommendations
            if df.isnull().sum().sum() > 0:
                recommendations.append("Address missing values before modeling")
            
            if df.duplicated().sum() > 0:
                recommendations.append("Remove duplicate records for better model performance")
            
            # Insight-based recommendations
            for insight in insights:
                if "strong correlation" in insight.lower():
                    recommendations.append("Investigate causal relationships between correlated variables")
                elif "trend" in insight.lower():
                    recommendations.append("Consider time series forecasting methods")
                elif "pattern" in insight.lower():
                    recommendations.append("Apply machine learning algorithms for pattern recognition")
            
            return recommendations[:6]  # Limit to 6 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating model recommendations: {e}")
            return ["Review data quality and model requirements"]
    
    async def _assess_data_quality(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """Assess data quality for modeling."""
        try:
            quality_assessment = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": len(numeric_cols),
                "missing_values": df.isnull().sum().sum(),
                "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                "duplicate_rows": df.duplicated().sum(),
                "quality_score": 0.0,
                "modeling_readiness": "unknown"
            }
            
            # Calculate quality score
            quality_score = 100.0
            
            # Deduct for missing values
            missing_percentage = quality_assessment["missing_percentage"]
            quality_score -= min(missing_percentage * 2, 30)  # Max 30 point deduction
            
            # Deduct for duplicates
            duplicate_percentage = (quality_assessment["duplicate_rows"] / len(df)) * 100
            quality_score -= min(duplicate_percentage * 2, 20)  # Max 20 point deduction
            
            # Deduct for insufficient numeric columns
            if len(numeric_cols) < 2:
                quality_score -= 20
            
            # Deduct for small dataset
            if len(df) < 100:
                quality_score -= 15
            
            quality_assessment["quality_score"] = max(0.0, quality_score)
            
            # Assess modeling readiness
            if quality_score >= 90:
                quality_assessment["modeling_readiness"] = "excellent"
            elif quality_score >= 80:
                quality_assessment["modeling_readiness"] = "good"
            elif quality_score >= 70:
                quality_assessment["modeling_readiness"] = "fair"
            elif quality_score >= 60:
                quality_assessment["modeling_readiness"] = "poor"
            else:
                quality_assessment["modeling_readiness"] = "very_poor"
            
            return quality_assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing data quality: {e}")
            return {
                "total_rows": 0,
                "total_columns": 0,
                "numeric_columns": 0,
                "missing_values": 0,
                "missing_percentage": 0,
                "duplicate_rows": 0,
                "quality_score": 0.0,
                "modeling_readiness": "unknown"
            }
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "insights": results.get("insights", []),
            "statistical_measures": results.get("statistical_measures", {}),
            "model_recommendations": results.get("model_recommendations", []),
            "data_quality_assessment": results.get("data_quality_assessment", {}),
            "predictive_analysis": results.get("predictive_analysis", {}),
            "analysis_type": results.get("analysis_type", "comprehensive"),
            "target_variable": results.get("target_variable")
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "InsightsModelingTool",
            "pillar": "insights",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "insights": [f"Error: {message}"],
            "statistical_measures": {},
            "model_recommendations": ["Please check your data and try again"],
            "data_quality_assessment": {"quality_score": 0, "modeling_readiness": "error"},
            "predictive_analysis": {},
            "analysis_type": "comprehensive",
            "target_variable": None,
            "metadata": {
                "error": message,
                "tool": "InsightsModelingTool",
                "pillar": "insights"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "InsightsModelingTool",
            "pillar": "insights",
            "architecture": "micro-module",
            "capabilities": [
                "correlation_analysis",
                "trend_detection",
                "pattern_analysis",
                "predictive_analysis",
                "model_recommendations"
            ],
            "analysis_types": ["comprehensive", "correlation", "trend", "pattern", "prediction"],
            "input_formats": ["dataframe_json", "rows_columns", "dict"],
            "output_format": "frontend_modeling_insights",
            "micro_modules": [
                "correlation_analyzer",
                "trend_detector",
                "pattern_analyzer",
                "predictive_analyzer"
            ]
        }

