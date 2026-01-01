"""
Outlier Detector Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class OutlierDetector:
    """
    Outlier detection following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("OutlierDetector micro-module initialized")
    
    async def detect_outliers(
        self, 
        series: pd.Series, 
        column_name: str, 
        method: str = "zscore", 
        threshold: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Detect outliers in a pandas Series.
        
        Args:
            series: Pandas Series to analyze
            column_name: Name of the column
            method: Detection method to use
            threshold: Threshold for detection
            
        Returns:
            List of outlier information dictionaries
        """
        try:
            # Remove null values for analysis
            clean_series = series.dropna()
            
            if len(clean_series) == 0:
                return []
            
            # Detect outliers based on method
            if method == "zscore":
                return await self._detect_zscore_outliers(clean_series, column_name, threshold)
            elif method == "iqr":
                return await self._detect_iqr_outliers(clean_series, column_name)
            elif method == "modified_zscore":
                return await self._detect_modified_zscore_outliers(clean_series, column_name, threshold)
            else:
                return await self._detect_zscore_outliers(clean_series, column_name, threshold)
            
        except Exception as e:
            self.logger.error(f"Error detecting outliers: {e}")
            return []
    
    async def _detect_zscore_outliers(self, series: pd.Series, column_name: str, threshold: float) -> List[Dict[str, Any]]:
        """Detect outliers using Z-score method."""
        try:
            outliers = []
            
            # Calculate Z-scores
            mean_val = series.mean()
            std_val = series.std()
            
            if std_val == 0:
                return []
            
            z_scores = np.abs((series - mean_val) / std_val)
            outlier_mask = z_scores > threshold
            
            # Get outlier information
            outlier_indices = series[outlier_mask].index.tolist()
            outlier_values = series[outlier_mask].tolist()
            outlier_z_scores = z_scores[outlier_mask].tolist()
            
            for i, (idx, value, z_score) in enumerate(zip(outlier_indices, outlier_values, outlier_z_scores)):
                outliers.append({
                    "index": int(idx),
                    "value": float(value),
                    "z_score": float(z_score),
                    "column": column_name,
                    "method": "zscore",
                    "threshold": threshold,
                    "severity": self._calculate_severity(z_score, threshold)
                })
            
            return outliers
            
        except Exception as e:
            self.logger.error(f"Error in Z-score outlier detection: {e}")
            return []
    
    async def _detect_iqr_outliers(self, series: pd.Series, column_name: str) -> List[Dict[str, Any]]:
        """Detect outliers using IQR method."""
        try:
            outliers = []
            
            # Calculate IQR
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR == 0:
                return []
            
            # Define outlier bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Find outliers
            outlier_mask = (series < lower_bound) | (series > upper_bound)
            outlier_indices = series[outlier_mask].index.tolist()
            outlier_values = series[outlier_mask].tolist()
            
            for idx, value in zip(outlier_indices, outlier_values):
                # Calculate how far outside the bounds
                if value < lower_bound:
                    distance = (lower_bound - value) / IQR
                else:
                    distance = (value - upper_bound) / IQR
                
                outliers.append({
                    "index": int(idx),
                    "value": float(value),
                    "column": column_name,
                    "method": "iqr",
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "iqr": float(IQR),
                    "distance_from_bounds": float(distance),
                    "severity": self._calculate_iqr_severity(distance)
                })
            
            return outliers
            
        except Exception as e:
            self.logger.error(f"Error in IQR outlier detection: {e}")
            return []
    
    async def _detect_modified_zscore_outliers(self, series: pd.Series, column_name: str, threshold: float) -> List[Dict[str, Any]]:
        """Detect outliers using modified Z-score method."""
        try:
            outliers = []
            
            # Calculate modified Z-scores using median absolute deviation
            median_val = series.median()
            mad = np.median(np.abs(series - median_val))
            
            if mad == 0:
                return []
            
            modified_z_scores = 0.6745 * (series - median_val) / mad
            outlier_mask = np.abs(modified_z_scores) > threshold
            
            # Get outlier information
            outlier_indices = series[outlier_mask].index.tolist()
            outlier_values = series[outlier_mask].tolist()
            outlier_scores = modified_z_scores[outlier_mask].tolist()
            
            for idx, value, score in zip(outlier_indices, outlier_values, outlier_scores):
                outliers.append({
                    "index": int(idx),
                    "value": float(value),
                    "modified_z_score": float(score),
                    "column": column_name,
                    "method": "modified_zscore",
                    "threshold": threshold,
                    "median": float(median_val),
                    "mad": float(mad),
                    "severity": self._calculate_severity(abs(score), threshold)
                })
            
            return outliers
            
        except Exception as e:
            self.logger.error(f"Error in modified Z-score outlier detection: {e}")
            return []
    
    def _calculate_severity(self, score: float, threshold: float) -> str:
        """Calculate severity level based on score and threshold."""
        if score > threshold * 2:
            return "critical"
        elif score > threshold * 1.5:
            return "high"
        elif score > threshold:
            return "medium"
        else:
            return "low"
    
    def _calculate_iqr_severity(self, distance: float) -> str:
        """Calculate severity level for IQR outliers."""
        if distance > 3:
            return "critical"
        elif distance > 2:
            return "high"
        elif distance > 1.5:
            return "medium"
        else:
            return "low"
    
    async def get_outlier_statistics(self, outliers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about detected outliers."""
        try:
            if not outliers:
                return {
                    "total_outliers": 0,
                    "severity_distribution": {},
                    "method_distribution": {},
                    "column_distribution": {}
                }
            
            # Count by severity
            severity_counts = {}
            for outlier in outliers:
                severity = outlier.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by method
            method_counts = {}
            for outlier in outliers:
                method = outlier.get("method", "unknown")
                method_counts[method] = method_counts.get(method, 0) + 1
            
            # Count by column
            column_counts = {}
            for outlier in outliers:
                column = outlier.get("column", "unknown")
                column_counts[column] = column_counts.get(column, 0) + 1
            
            return {
                "total_outliers": len(outliers),
                "severity_distribution": severity_counts,
                "method_distribution": method_counts,
                "column_distribution": column_counts
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating outlier statistics: {e}")
            return {
                "total_outliers": 0,
                "severity_distribution": {},
                "method_distribution": {},
                "column_distribution": {}
            }

