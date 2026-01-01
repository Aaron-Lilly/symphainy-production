"""
Correlation Analyzer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class CorrelationAnalyzer:
    """
    Correlation analysis following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("CorrelationAnalyzer micro-module initialized")
    
    async def analyze_correlations(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """
        Analyze correlations between numeric columns.
        
        Args:
            df: DataFrame to analyze
            numeric_cols: List of numeric column names
            
        Returns:
            Correlation analysis results
        """
        try:
            results = {
                "insights": [],
                "measures": {},
                "correlation_matrix": {},
                "strong_correlations": [],
                "weak_correlations": []
            }
            
            if len(numeric_cols) < 2:
                results["insights"].append("Need at least 2 numeric columns for correlation analysis")
                return results
            
            # Get numeric data
            numeric_data = df[numeric_cols].dropna()
            
            if len(numeric_data) == 0:
                results["insights"].append("No valid numeric data for correlation analysis")
                return results
            
            # Calculate correlation matrix
            corr_matrix = numeric_data.corr()
            results["correlation_matrix"] = corr_matrix.to_dict()
            
            # Find strong and weak correlations
            strong_correlations = []
            weak_correlations = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    
                    correlation_info = {
                        "column1": col1,
                        "column2": col2,
                        "correlation": float(corr_value),
                        "strength": self._classify_correlation_strength(abs(corr_value))
                    }
                    
                    if abs(corr_value) > 0.7:
                        strong_correlations.append(correlation_info)
                    elif abs(corr_value) < 0.3:
                        weak_correlations.append(correlation_info)
            
            results["strong_correlations"] = strong_correlations
            results["weak_correlations"] = weak_correlations
            
            # Generate insights
            results["insights"] = await self._generate_correlation_insights(
                strong_correlations, weak_correlations, corr_matrix
            )
            
            # Calculate measures
            results["measures"] = await self._calculate_correlation_measures(corr_matrix)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlations: {e}")
            return {
                "insights": [f"Error in correlation analysis: {str(e)}"],
                "measures": {},
                "correlation_matrix": {},
                "strong_correlations": [],
                "weak_correlations": []
            }
    
    async def _generate_correlation_insights(
        self, 
        strong_correlations: List[Dict[str, Any]], 
        weak_correlations: List[Dict[str, Any]], 
        corr_matrix: pd.DataFrame
    ) -> List[str]:
        """Generate insights from correlation analysis."""
        try:
            insights = []
            
            # Strong correlations insights
            if strong_correlations:
                insights.append(f"Found {len(strong_correlations)} strong correlations (|r| > 0.7)")
                
                # Highlight strongest correlation
                strongest = max(strong_correlations, key=lambda x: abs(x["correlation"]))
                insights.append(
                    f"Strongest correlation: {strongest['column1']} and {strongest['column2']} "
                    f"(r = {strongest['correlation']:.3f})"
                )
                
                # Check for positive vs negative correlations
                positive_strong = [c for c in strong_correlations if c["correlation"] > 0]
                negative_strong = [c for c in strong_correlations if c["correlation"] < 0]
                
                if len(positive_strong) > len(negative_strong):
                    insights.append("Most strong correlations are positive - variables tend to increase together")
                elif len(negative_strong) > len(positive_strong):
                    insights.append("Most strong correlations are negative - variables tend to move in opposite directions")
            else:
                insights.append("No strong correlations found (|r| > 0.7)")
            
            # Weak correlations insights
            if weak_correlations:
                insights.append(f"Found {len(weak_correlations)} weak correlations (|r| < 0.3)")
            else:
                insights.append("No weak correlations found - all variables show moderate to strong relationships")
            
            # Overall correlation pattern
            all_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    all_correlations.append(abs(corr_matrix.iloc[i, j]))
            
            if all_correlations:
                avg_correlation = np.mean(all_correlations)
                if avg_correlation > 0.5:
                    insights.append("High average correlation - variables are generally well-related")
                elif avg_correlation > 0.3:
                    insights.append("Moderate average correlation - some relationships between variables")
                else:
                    insights.append("Low average correlation - variables are largely independent")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating correlation insights: {e}")
            return ["Error generating correlation insights"]
    
    async def _calculate_correlation_measures(self, corr_matrix: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlation measures."""
        try:
            measures = {}
            
            # Get upper triangle correlations
            upper_triangle = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    upper_triangle.append(corr_matrix.iloc[i, j])
            
            if upper_triangle:
                measures["average_correlation"] = float(np.mean(upper_triangle))
                measures["max_correlation"] = float(np.max(upper_triangle))
                measures["min_correlation"] = float(np.min(upper_triangle))
                measures["correlation_std"] = float(np.std(upper_triangle))
                measures["correlation_count"] = len(upper_triangle)
                
                # Count by strength
                strong_count = sum(1 for c in upper_triangle if abs(c) > 0.7)
                moderate_count = sum(1 for c in upper_triangle if 0.3 <= abs(c) <= 0.7)
                weak_count = sum(1 for c in upper_triangle if abs(c) < 0.3)
                
                measures["strength_distribution"] = {
                    "strong": strong_count,
                    "moderate": moderate_count,
                    "weak": weak_count
                }
            
            return measures
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation measures: {e}")
            return {}
    
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
    
    async def find_multicollinearity(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """Find potential multicollinearity issues."""
        try:
            if len(numeric_cols) < 3:
                return {"message": "Need at least 3 numeric columns for multicollinearity analysis"}
            
            numeric_data = df[numeric_cols].dropna()
            
            if len(numeric_data) == 0:
                return {"message": "No valid data for multicollinearity analysis"}
            
            corr_matrix = numeric_data.corr()
            
            # Find high correlations that might indicate multicollinearity
            multicollinearity_pairs = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.8:  # High correlation threshold
                        multicollinearity_pairs.append({
                            "column1": corr_matrix.columns[i],
                            "column2": corr_matrix.columns[j],
                            "correlation": float(corr_value),
                            "severity": "high" if abs(corr_value) > 0.9 else "medium"
                        })
            
            return {
                "multicollinearity_pairs": multicollinearity_pairs,
                "count": len(multicollinearity_pairs),
                "severity": "high" if any(p["severity"] == "high" for p in multicollinearity_pairs) else "medium" if multicollinearity_pairs else "low"
            }
            
        except Exception as e:
            self.logger.error(f"Error finding multicollinearity: {e}")
            return {"message": f"Error in multicollinearity analysis: {str(e)}"}
    
    async def suggest_feature_selection(self, df: pd.DataFrame, target_col: str, numeric_cols: List[str]) -> Dict[str, Any]:
        """Suggest features for selection based on correlation with target."""
        try:
            if target_col not in numeric_cols:
                return {"message": "Target column must be numeric"}
            
            numeric_data = df[numeric_cols].dropna()
            
            if len(numeric_data) == 0:
                return {"message": "No valid data for feature selection analysis"}
            
            # Calculate correlations with target
            target_correlations = []
            
            for col in numeric_cols:
                if col != target_col:
                    corr_value = numeric_data[target_col].corr(numeric_data[col])
                    if not pd.isna(corr_value):
                        target_correlations.append({
                            "feature": col,
                            "correlation_with_target": float(corr_value),
                            "abs_correlation": float(abs(corr_value)),
                            "strength": self._classify_correlation_strength(abs(corr_value))
                        })
            
            # Sort by absolute correlation
            target_correlations.sort(key=lambda x: x["abs_correlation"], reverse=True)
            
            # Categorize features
            high_correlation_features = [f for f in target_correlations if f["abs_correlation"] > 0.7]
            medium_correlation_features = [f for f in target_correlations if 0.3 <= f["abs_correlation"] <= 0.7]
            low_correlation_features = [f for f in target_correlations if f["abs_correlation"] < 0.3]
            
            return {
                "target_correlations": target_correlations,
                "high_correlation_features": high_correlation_features,
                "medium_correlation_features": medium_correlation_features,
                "low_correlation_features": low_correlation_features,
                "recommendations": {
                    "include": [f["feature"] for f in high_correlation_features],
                    "consider": [f["feature"] for f in medium_correlation_features],
                    "exclude": [f["feature"] for f in low_correlation_features]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error suggesting feature selection: {e}")
            return {"message": f"Error in feature selection analysis: {str(e)}"}

