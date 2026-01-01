"""
Insights Anomaly Detection Tool - Smart City MCP Tool
Provides anomaly detection for Insights Pillar frontend
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
from .micro_modules.outlier_detector import OutlierDetector
from .micro_modules.statistical_analyzer import StatisticalAnalyzer
from .micro_modules.anomaly_reporter import AnomalyReporter


class InsightsAnomalyTool(BaseMCP):
    """
    Insights Anomaly Detection Tool for Insights Pillar
    Provides anomaly detection optimized for frontend display
    """
    
    def __init__(self):
        super().__init__()
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("InsightsAnomalyTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        self._logger.info("InsightsAnomalyTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.outlier_detector = OutlierDetector(self._logger, self._config)
            self.statistical_analyzer = StatisticalAnalyzer(self._logger, self._config)
            self.anomaly_reporter = AnomalyReporter(self._logger, self._config)
            
            self._logger.info("InsightsAnomalyTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing InsightsAnomalyTool micro-modules: {e}")
            raise e
    
    async def detect_anomalies(
        self, 
        data: Dict[str, Any], 
        detection_method: str = "zscore",
        threshold: float = 3.0,
        session_token: Optional[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Detect anomalies in data for frontend display.
        
        Args:
            data: Data to analyze (DataFrame as dict or file metadata)
            detection_method: Method for anomaly detection
            threshold: Threshold for anomaly detection
            session_token: Smart City session token
            context: Additional context for analysis
            
        Returns:
            Anomaly detection results for frontend display
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
            
            # Detect anomalies
            anomaly_results = await self._perform_anomaly_detection(df, detection_method, threshold, context)
            
            # Format for frontend display
            formatted_results = self._format_for_frontend(anomaly_results)
            
            # Add Smart City metadata
            formatted_results["metadata"] = self._create_metadata(session_token, "anomaly_detection")
            
            self._logger.info("Anomaly detection completed successfully")
            return formatted_results
            
        except Exception as e:
            self._logger.error(f"Error in anomaly detection: {e}")
            return self._create_error_response(f"Anomaly detection failed: {str(e)}")
    
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
    
    async def _perform_anomaly_detection(self, df: pd.DataFrame, method: str, threshold: float, context: str) -> Dict[str, Any]:
        """Perform anomaly detection using micro-modules."""
        results = {
            "anomalies": [],
            "summary": {},
            "statistics": {},
            "recommendations": [],
            "detection_method": method,
            "threshold": threshold
        }
        
        try:
            # Get numeric columns for analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                results["summary"]["message"] = "No numeric columns found for anomaly detection"
                return results
            
            # Detect outliers for each numeric column
            for col in numeric_cols:
                column_anomalies = await self.outlier_detector.detect_outliers(
                    df[col], col, method, threshold
                )
                results["anomalies"].extend(column_anomalies)
            
            # Generate statistical analysis
            stats = await self.statistical_analyzer.analyze_data(df, numeric_cols)
            results["statistics"] = stats
            
            # Generate summary
            summary = await self.anomaly_reporter.generate_summary(results["anomalies"], stats)
            results["summary"] = summary
            
            # Generate recommendations
            recommendations = await self.anomaly_reporter.generate_recommendations(
                results["anomalies"], stats, method
            )
            results["recommendations"] = recommendations
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error in anomaly detection: {e}")
            raise e
    
    def _format_for_frontend(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for frontend display."""
        return {
            "anomalies": results.get("anomalies", []),
            "summary": results.get("summary", {}),
            "statistics": results.get("statistics", {}),
            "recommendations": results.get("recommendations", []),
            "detection_method": results.get("detection_method", "zscore"),
            "threshold": results.get("threshold", 3.0)
        }
    
    def _create_metadata(self, session_token: Optional[str], operation: str) -> Dict[str, Any]:
        """Create Smart City metadata."""
        return {
            "smart_city_version": self._config.get("version", "1.0.0"),
            "session_token": session_token,
            "operation": operation,
            "tool": "InsightsAnomalyTool",
            "pillar": "insights",
            "architecture": "micro-module",
            "config_source": "unified_orchestrator"
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "anomalies": [],
            "summary": {"message": message},
            "statistics": {},
            "recommendations": ["Please check your data and try again"],
            "detection_method": "zscore",
            "threshold": 3.0,
            "metadata": {
                "error": message,
                "tool": "InsightsAnomalyTool",
                "pillar": "insights"
            }
        }
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities information."""
        return {
            "tool_name": "InsightsAnomalyTool",
            "pillar": "insights",
            "architecture": "micro-module",
            "capabilities": [
                "anomaly_detection",
                "outlier_identification",
                "statistical_analysis",
                "anomaly_reporting"
            ],
            "detection_methods": ["zscore", "iqr", "isolation_forest", "local_outlier_factor"],
            "input_formats": ["dataframe_json", "rows_columns", "dict"],
            "output_format": "frontend_anomaly_analysis",
            "micro_modules": [
                "outlier_detector",
                "statistical_analyzer",
                "anomaly_reporter"
            ]
        }

