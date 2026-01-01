"""
Statistical Analyzer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class StatisticalAnalyzer:
    """
    Statistical analysis following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("StatisticalAnalyzer micro-module initialized")
    
    async def analyze_data(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """
        Perform statistical analysis on data.
        
        Args:
            df: DataFrame to analyze
            numeric_columns: List of numeric column names
            
        Returns:
            Statistical analysis results
        """
        try:
            results = {
                "overall_stats": {},
                "column_stats": {},
                "correlation_analysis": {},
                "distribution_analysis": {},
                "data_quality_metrics": {}
            }
            
            # Overall statistics
            results["overall_stats"] = await self._calculate_overall_stats(df, numeric_columns)
            
            # Column-specific statistics
            results["column_stats"] = await self._calculate_column_stats(df, numeric_columns)
            
            # Correlation analysis
            results["correlation_analysis"] = await self._analyze_correlations(df, numeric_columns)
            
            # Distribution analysis
            results["distribution_analysis"] = await self._analyze_distributions(df, numeric_columns)
            
            # Data quality metrics
            results["data_quality_metrics"] = await self._calculate_quality_metrics(df, numeric_columns)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in statistical analysis: {e}")
            return {
                "overall_stats": {},
                "column_stats": {},
                "correlation_analysis": {},
                "distribution_analysis": {},
                "data_quality_metrics": {}
            }
    
    async def _calculate_overall_stats(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Calculate overall statistics."""
        try:
            if not numeric_columns:
                return {"message": "No numeric columns available"}
            
            numeric_data = df[numeric_columns]
            
            return {
                "total_rows": len(df),
                "numeric_columns_count": len(numeric_columns),
                "total_numeric_values": numeric_data.count().sum(),
                "missing_numeric_values": numeric_data.isnull().sum().sum(),
                "completeness_percentage": (numeric_data.count().sum() / (len(df) * len(numeric_columns))) * 100,
                "data_types": {col: str(df[col].dtype) for col in numeric_columns}
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating overall stats: {e}")
            return {}
    
    async def _calculate_column_stats(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Calculate statistics for each column."""
        try:
            column_stats = {}
            
            for col in numeric_columns:
                series = df[col].dropna()
                
                if len(series) == 0:
                    column_stats[col] = {"message": "No valid data"}
                    continue
                
                stats = {
                    "count": len(series),
                    "mean": float(series.mean()),
                    "median": float(series.median()),
                    "std": float(series.std()),
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "range": float(series.max() - series.min()),
                    "variance": float(series.var()),
                    "skewness": float(series.skew()),
                    "kurtosis": float(series.kurtosis()),
                    "quartiles": {
                        "q1": float(series.quantile(0.25)),
                        "q2": float(series.quantile(0.5)),
                        "q3": float(series.quantile(0.75))
                    }
                }
                
                # Additional metrics
                stats["coefficient_of_variation"] = float(stats["std"] / stats["mean"]) if stats["mean"] != 0 else 0
                stats["outlier_potential"] = self._assess_outlier_potential(series)
                stats["distribution_type"] = self._classify_distribution(series)
                
                column_stats[col] = stats
            
            return column_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating column stats: {e}")
            return {}
    
    async def _analyze_correlations(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Analyze correlations between numeric columns."""
        try:
            if len(numeric_columns) < 2:
                return {"message": "Need at least 2 numeric columns for correlation analysis"}
            
            numeric_data = df[numeric_columns].dropna()
            
            if len(numeric_data) == 0:
                return {"message": "No valid data for correlation analysis"}
            
            # Calculate correlation matrix
            corr_matrix = numeric_data.corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            "column1": corr_matrix.columns[i],
                            "column2": corr_matrix.columns[j],
                            "correlation": float(corr_value),
                            "strength": self._classify_correlation_strength(abs(corr_value))
                        })
            
            # Calculate average correlation
            corr_values = corr_matrix.values
            mask = ~np.isnan(corr_values)
            upper_triangle = corr_values[np.triu_indices_from(corr_values, k=1)]
            upper_triangle = upper_triangle[~np.isnan(upper_triangle)]
            
            return {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_correlations,
                "average_correlation": float(np.mean(np.abs(upper_triangle))) if len(upper_triangle) > 0 else 0,
                "max_correlation": float(np.max(np.abs(upper_triangle))) if len(upper_triangle) > 0 else 0,
                "correlation_count": len(strong_correlations)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {e}")
            return {}
    
    async def _analyze_distributions(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Analyze distributions of numeric columns."""
        try:
            distribution_analysis = {}
            
            for col in numeric_columns:
                series = df[col].dropna()
                
                if len(series) == 0:
                    distribution_analysis[col] = {"message": "No valid data"}
                    continue
                
                # Basic distribution metrics
                skewness = series.skew()
                kurtosis = series.kurtosis()
                
                # Distribution classification
                distribution_type = self._classify_distribution(series)
                
                # Normality test (simplified)
                is_normal = self._test_normality(series)
                
                # Outlier assessment
                outlier_potential = self._assess_outlier_potential(series)
                
                distribution_analysis[col] = {
                    "distribution_type": distribution_type,
                    "skewness": float(skewness),
                    "kurtosis": float(kurtosis),
                    "is_normal": is_normal,
                    "outlier_potential": outlier_potential,
                    "uniqueness_ratio": float(series.nunique() / len(series)),
                    "value_range": {
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "range": float(series.max() - series.min())
                    }
                }
            
            return distribution_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing distributions: {e}")
            return {}
    
    async def _calculate_quality_metrics(self, df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        try:
            if not numeric_columns:
                return {"message": "No numeric columns available"}
            
            numeric_data = df[numeric_columns]
            
            # Missing data analysis
            missing_counts = numeric_data.isnull().sum()
            missing_percentages = (missing_counts / len(df)) * 100
            
            # Duplicate analysis
            duplicate_rows = df.duplicated().sum()
            duplicate_percentage = (duplicate_rows / len(df)) * 100
            
            # Data type consistency
            type_consistency = {}
            for col in numeric_columns:
                try:
                    # Check if all non-null values can be converted to numeric
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        pd.to_numeric(non_null_values, errors='raise')
                        type_consistency[col] = "consistent"
                    else:
                        type_consistency[col] = "no_data"
                except (ValueError, TypeError):
                    type_consistency[col] = "inconsistent"
            
            # Overall quality score
            quality_score = self._calculate_overall_quality_score(
                missing_percentages, duplicate_percentage, type_consistency
            )
            
            return {
                "missing_data": {
                    "counts": missing_counts.to_dict(),
                    "percentages": missing_percentages.to_dict(),
                    "total_missing": int(missing_counts.sum()),
                    "average_missing_percentage": float(missing_percentages.mean())
                },
                "duplicates": {
                    "count": int(duplicate_rows),
                    "percentage": float(duplicate_percentage)
                },
                "type_consistency": type_consistency,
                "overall_quality_score": quality_score,
                "quality_assessment": self._assess_quality_level(quality_score)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {e}")
            return {}
    
    def _assess_outlier_potential(self, series: pd.Series) -> str:
        """Assess potential for outliers in a series."""
        try:
            if len(series) < 4:
                return "insufficient_data"
            
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR == 0:
                return "no_variation"
            
            # Count potential outliers
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_count = ((series < lower_bound) | (series > upper_bound)).sum()
            outlier_percentage = (outlier_count / len(series)) * 100
            
            if outlier_percentage > 10:
                return "high"
            elif outlier_percentage > 5:
                return "medium"
            elif outlier_percentage > 0:
                return "low"
            else:
                return "none"
                
        except Exception as e:
            self.logger.error(f"Error assessing outlier potential: {e}")
            return "unknown"
    
    def _classify_distribution(self, series: pd.Series) -> str:
        """Classify the distribution type of a series."""
        try:
            if len(series) < 3:
                return "insufficient_data"
            
            skewness = abs(series.skew())
            kurtosis = series.kurtosis()
            
            if skewness < 0.5 and -0.5 < kurtosis < 0.5:
                return "normal"
            elif skewness > 1:
                return "highly_skewed"
            elif skewness > 0.5:
                return "moderately_skewed"
            elif kurtosis > 3:
                return "heavy_tailed"
            elif kurtosis < -1:
                return "light_tailed"
            else:
                return "unknown"
                
        except Exception as e:
            self.logger.error(f"Error classifying distribution: {e}")
            return "unknown"
    
    def _test_normality(self, series: pd.Series) -> bool:
        """Simple normality test based on skewness and kurtosis."""
        try:
            if len(series) < 3:
                return False
            
            skewness = abs(series.skew())
            kurtosis = abs(series.kurtosis())
            
            # Simple heuristic: normal if skewness < 0.5 and kurtosis < 1
            return skewness < 0.5 and kurtosis < 1
            
        except Exception as e:
            self.logger.error(f"Error testing normality: {e}")
            return False
    
    def _classify_correlation_strength(self, abs_corr: float) -> str:
        """Classify correlation strength."""
        if abs_corr >= 0.9:
            return "very_strong"
        elif abs_corr >= 0.7:
            return "strong"
        elif abs_corr >= 0.5:
            return "moderate"
        elif abs_corr >= 0.3:
            return "weak"
        else:
            return "very_weak"
    
    def _calculate_overall_quality_score(self, missing_percentages: pd.Series, duplicate_percentage: float, type_consistency: Dict[str, str]) -> float:
        """Calculate overall data quality score."""
        try:
            score = 100.0
            
            # Deduct for missing data
            avg_missing = missing_percentages.mean()
            score -= min(avg_missing * 2, 40)  # Max 40 point deduction
            
            # Deduct for duplicates
            score -= min(duplicate_percentage * 2, 20)  # Max 20 point deduction
            
            # Deduct for type inconsistencies
            inconsistent_count = sum(1 for consistency in type_consistency.values() if consistency == "inconsistent")
            if inconsistent_count > 0:
                score -= min(inconsistent_count * 10, 20)  # Max 20 point deduction
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def _assess_quality_level(self, score: float) -> str:
        """Assess data quality level based on score."""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 60:
            return "poor"
        else:
            return "very_poor"

