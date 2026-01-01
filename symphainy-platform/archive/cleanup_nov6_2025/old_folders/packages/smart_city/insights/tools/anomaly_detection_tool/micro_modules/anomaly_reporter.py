"""
Anomaly Reporter Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class AnomalyReporter:
    """
    Anomaly reporting following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("AnomalyReporter micro-module initialized")
    
    async def generate_summary(self, anomalies: List[Dict[str, Any]], statistics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of anomaly detection results.
        
        Args:
            anomalies: List of detected anomalies
            statistics: Statistical analysis results
            
        Returns:
            Summary dictionary
        """
        try:
            summary = {
                "total_anomalies": len(anomalies),
                "anomaly_summary": {},
                "data_quality_summary": {},
                "key_findings": [],
                "severity_breakdown": {}
            }
            
            # Anomaly summary
            if anomalies:
                summary["anomaly_summary"] = await self._summarize_anomalies(anomalies)
                summary["severity_breakdown"] = await self._breakdown_by_severity(anomalies)
            else:
                summary["anomaly_summary"] = {"message": "No anomalies detected"}
                summary["severity_breakdown"] = {}
            
            # Data quality summary
            summary["data_quality_summary"] = await self._summarize_data_quality(statistics)
            
            # Key findings
            summary["key_findings"] = await self._generate_key_findings(anomalies, statistics)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating anomaly summary: {e}")
            return {
                "total_anomalies": 0,
                "anomaly_summary": {"message": "Error generating summary"},
                "data_quality_summary": {},
                "key_findings": ["Error in summary generation"],
                "severity_breakdown": {}
            }
    
    async def generate_recommendations(
        self, 
        anomalies: List[Dict[str, Any]], 
        statistics: Dict[str, Any], 
        method: str
    ) -> List[str]:
        """
        Generate recommendations based on anomaly detection results.
        
        Args:
            anomalies: List of detected anomalies
            statistics: Statistical analysis results
            method: Detection method used
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Anomaly-based recommendations
            if anomalies:
                recommendations.extend(await self._generate_anomaly_recommendations(anomalies))
            else:
                recommendations.append("No anomalies detected - data appears clean")
            
            # Statistical-based recommendations
            recommendations.extend(await self._generate_statistical_recommendations(statistics))
            
            # Method-specific recommendations
            recommendations.extend(await self._generate_method_recommendations(method, anomalies))
            
            # Data quality recommendations
            recommendations.extend(await self._generate_quality_recommendations(statistics))
            
            # Limit to top recommendations
            return recommendations[:8]
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Review data quality and analysis parameters"]
    
    async def _summarize_anomalies(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize detected anomalies."""
        try:
            if not anomalies:
                return {"message": "No anomalies detected"}
            
            # Group by column
            column_anomalies = {}
            for anomaly in anomalies:
                column = anomaly.get("column", "unknown")
                if column not in column_anomalies:
                    column_anomalies[column] = []
                column_anomalies[column].append(anomaly)
            
            # Calculate summary statistics
            summary = {
                "total_anomalies": len(anomalies),
                "affected_columns": len(column_anomalies),
                "column_breakdown": {},
                "method_distribution": {},
                "severity_distribution": {}
            }
            
            # Column breakdown
            for column, column_anomalies_list in column_anomalies.items():
                summary["column_breakdown"][column] = {
                    "count": len(column_anomalies_list),
                    "severity_breakdown": self._count_by_severity(column_anomalies_list)
                }
            
            # Method distribution
            methods = [anomaly.get("method", "unknown") for anomaly in anomalies]
            summary["method_distribution"] = {method: methods.count(method) for method in set(methods)}
            
            # Severity distribution
            severities = [anomaly.get("severity", "unknown") for anomaly in anomalies]
            summary["severity_distribution"] = {severity: severities.count(severity) for severity in set(severities)}
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error summarizing anomalies: {e}")
            return {"message": "Error summarizing anomalies"}
    
    async def _breakdown_by_severity(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Break down anomalies by severity level."""
        try:
            severity_breakdown = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
            
            for anomaly in anomalies:
                severity = anomaly.get("severity", "low")
                if severity in severity_breakdown:
                    severity_breakdown[severity].append(anomaly)
            
            # Add counts
            for severity in severity_breakdown:
                severity_breakdown[severity] = {
                    "count": len(severity_breakdown[severity]),
                    "anomalies": severity_breakdown[severity]
                }
            
            return severity_breakdown
            
        except Exception as e:
            self.logger.error(f"Error breaking down by severity: {e}")
            return {}
    
    async def _summarize_data_quality(self, statistics: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize data quality metrics."""
        try:
            quality_metrics = statistics.get("data_quality_metrics", {})
            
            if not quality_metrics:
                return {"message": "No quality metrics available"}
            
            summary = {
                "overall_quality_score": quality_metrics.get("overall_quality_score", 0),
                "quality_assessment": quality_metrics.get("quality_assessment", "unknown"),
                "missing_data": quality_metrics.get("missing_data", {}),
                "duplicates": quality_metrics.get("duplicates", {}),
                "type_consistency": quality_metrics.get("type_consistency", {})
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error summarizing data quality: {e}")
            return {}
    
    async def _generate_key_findings(self, anomalies: List[Dict[str, Any]], statistics: Dict[str, Any]) -> List[str]:
        """Generate key findings from analysis."""
        try:
            findings = []
            
            # Anomaly findings
            if anomalies:
                total_anomalies = len(anomalies)
                critical_anomalies = len([a for a in anomalies if a.get("severity") == "critical"])
                high_anomalies = len([a for a in anomalies if a.get("severity") == "high"])
                
                if critical_anomalies > 0:
                    findings.append(f"Critical anomalies detected: {critical_anomalies} severe outliers found")
                elif high_anomalies > 0:
                    findings.append(f"High-severity anomalies detected: {high_anomalies} significant outliers found")
                elif total_anomalies > 0:
                    findings.append(f"Moderate anomalies detected: {total_anomalies} outliers found")
                else:
                    findings.append("No significant anomalies detected in the data")
            else:
                findings.append("Data appears clean with no anomalies detected")
            
            # Statistical findings
            column_stats = statistics.get("column_stats", {})
            if column_stats:
                # Find columns with high variability
                high_variability_cols = []
                for col, stats in column_stats.items():
                    cv = stats.get("coefficient_of_variation", 0)
                    if cv > 1:
                        high_variability_cols.append(col)
                
                if high_variability_cols:
                    findings.append(f"High variability detected in columns: {', '.join(high_variability_cols)}")
                
                # Find skewed distributions
                skewed_cols = []
                for col, stats in column_stats.items():
                    skewness = abs(stats.get("skewness", 0))
                    if skewness > 1:
                        skewed_cols.append(col)
                
                if skewed_cols:
                    findings.append(f"Skewed distributions detected in columns: {', '.join(skewed_cols)}")
            
            # Correlation findings
            correlation_analysis = statistics.get("correlation_analysis", {})
            strong_correlations = correlation_analysis.get("strong_correlations", [])
            if strong_correlations:
                findings.append(f"Strong correlations found between {len(strong_correlations)} column pairs")
            
            # Quality findings
            quality_metrics = statistics.get("data_quality_metrics", {})
            quality_score = quality_metrics.get("overall_quality_score", 0)
            if quality_score < 70:
                findings.append(f"Data quality needs attention (score: {quality_score:.1f})")
            elif quality_score >= 90:
                findings.append(f"Excellent data quality (score: {quality_score:.1f})")
            
            return findings[:5]  # Limit to 5 key findings
            
        except Exception as e:
            self.logger.error(f"Error generating key findings: {e}")
            return ["Error generating key findings"]
    
    async def _generate_anomaly_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on anomalies."""
        try:
            recommendations = []
            
            if not anomalies:
                return ["No anomalies detected - data appears clean"]
            
            # Severity-based recommendations
            critical_count = len([a for a in anomalies if a.get("severity") == "critical"])
            high_count = len([a for a in anomalies if a.get("severity") == "high"])
            
            if critical_count > 0:
                recommendations.append("Immediate attention required for critical anomalies")
                recommendations.append("Investigate data collection processes for systematic errors")
            
            if high_count > 0:
                recommendations.append("Review high-severity anomalies for data quality issues")
            
            # Column-based recommendations
            column_anomalies = {}
            for anomaly in anomalies:
                column = anomaly.get("column", "unknown")
                if column not in column_anomalies:
                    column_anomalies[column] = 0
                column_anomalies[column] += 1
            
            high_anomaly_columns = [col for col, count in column_anomalies.items() if count > 5]
            if high_anomaly_columns:
                recommendations.append(f"Focus on columns with many anomalies: {', '.join(high_anomaly_columns)}")
            
            # Method-specific recommendations
            methods = [a.get("method", "unknown") for a in anomalies]
            if "zscore" in methods:
                recommendations.append("Consider adjusting Z-score threshold if too many/few anomalies detected")
            if "iqr" in methods:
                recommendations.append("IQR method may be more robust for skewed distributions")
            
            return recommendations[:4]  # Limit to 4 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating anomaly recommendations: {e}")
            return []
    
    async def _generate_statistical_recommendations(self, statistics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on statistical analysis."""
        try:
            recommendations = []
            
            # Correlation recommendations
            correlation_analysis = statistics.get("correlation_analysis", {})
            strong_correlations = correlation_analysis.get("strong_correlations", [])
            if strong_correlations:
                recommendations.append("Investigate strong correlations for potential causal relationships")
            
            # Distribution recommendations
            distribution_analysis = statistics.get("distribution_analysis", {})
            for col, dist_info in distribution_analysis.items():
                if dist_info.get("is_normal", False):
                    recommendations.append(f"Column '{col}' follows normal distribution - suitable for parametric tests")
                elif dist_info.get("outlier_potential") == "high":
                    recommendations.append(f"Column '{col}' has high outlier potential - consider robust statistical methods")
            
            return recommendations[:3]  # Limit to 3 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating statistical recommendations: {e}")
            return []
    
    async def _generate_method_recommendations(self, method: str, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate method-specific recommendations."""
        try:
            recommendations = []
            
            if method == "zscore":
                recommendations.append("Z-score method assumes normal distribution - verify data normality")
                if len(anomalies) > 0:
                    recommendations.append("Consider using modified Z-score for more robust outlier detection")
            elif method == "iqr":
                recommendations.append("IQR method is robust to outliers and works well with skewed data")
            elif method == "modified_zscore":
                recommendations.append("Modified Z-score uses median and MAD - more robust than standard Z-score")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating method recommendations: {e}")
            return []
    
    async def _generate_quality_recommendations(self, statistics: Dict[str, Any]) -> List[str]:
        """Generate data quality recommendations."""
        try:
            recommendations = []
            
            quality_metrics = statistics.get("data_quality_metrics", {})
            quality_score = quality_metrics.get("overall_quality_score", 0)
            
            if quality_score < 60:
                recommendations.append("Data quality is poor - immediate cleaning required")
            elif quality_score < 80:
                recommendations.append("Data quality needs improvement - address missing values and duplicates")
            
            # Missing data recommendations
            missing_data = quality_metrics.get("missing_data", {})
            avg_missing = missing_data.get("average_missing_percentage", 0)
            if avg_missing > 20:
                recommendations.append("High missing data percentage - investigate data collection processes")
            elif avg_missing > 5:
                recommendations.append("Moderate missing data - consider imputation strategies")
            
            # Duplicate recommendations
            duplicates = quality_metrics.get("duplicates", {})
            duplicate_percentage = duplicates.get("percentage", 0)
            if duplicate_percentage > 10:
                recommendations.append("High duplicate rate - implement deduplication processes")
            elif duplicate_percentage > 0:
                recommendations.append("Some duplicates detected - review data entry processes")
            
            return recommendations[:3]  # Limit to 3 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating quality recommendations: {e}")
            return []
    
    def _count_by_severity(self, anomalies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count anomalies by severity level."""
        try:
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            
            for anomaly in anomalies:
                severity = anomaly.get("severity", "low")
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            return severity_counts
            
        except Exception as e:
            self.logger.error(f"Error counting by severity: {e}")
            return {"critical": 0, "high": 0, "medium": 0, "low": 0}

