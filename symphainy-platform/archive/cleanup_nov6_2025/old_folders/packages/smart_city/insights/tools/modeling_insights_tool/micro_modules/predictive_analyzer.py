"""
Predictive Analyzer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class PredictiveAnalyzer:
    """
    Predictive analysis following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("PredictiveAnalyzer micro-module initialized")
    
    async def analyze_predictive_potential(
        self, 
        df: pd.DataFrame, 
        target_variable: str, 
        numeric_cols: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze predictive potential of features for a target variable.
        
        Args:
            df: DataFrame to analyze
            target_variable: Name of target variable
            numeric_cols: List of numeric column names
            
        Returns:
            Predictive analysis results
        """
        try:
            results = {
                "insights": [],
                "measures": {},
                "analysis": {
                    "target_variable": target_variable,
                    "feature_importance": {},
                    "correlation_analysis": {},
                    "model_recommendations": [],
                    "data_readiness": {}
                }
            }
            
            # Check if target variable exists and is numeric
            if target_variable not in df.columns:
                results["insights"].append(f"Target variable '{target_variable}' not found in data")
                return results
            
            if target_variable not in numeric_cols:
                results["insights"].append(f"Target variable '{target_variable}' is not numeric")
                return results
            
            # Get feature columns (exclude target)
            feature_cols = [col for col in numeric_cols if col != target_variable]
            
            if len(feature_cols) == 0:
                results["insights"].append("No feature columns available for predictive analysis")
                return results
            
            # Analyze feature importance
            feature_importance = await self._analyze_feature_importance(df, target_variable, feature_cols)
            results["analysis"]["feature_importance"] = feature_importance
            
            # Analyze correlations with target
            correlation_analysis = await self._analyze_target_correlations(df, target_variable, feature_cols)
            results["analysis"]["correlation_analysis"] = correlation_analysis
            
            # Assess data readiness
            data_readiness = await self._assess_data_readiness(df, target_variable, feature_cols)
            results["analysis"]["data_readiness"] = data_readiness
            
            # Generate model recommendations
            model_recommendations = await self._generate_model_recommendations(
                feature_importance, correlation_analysis, data_readiness
            )
            results["analysis"]["model_recommendations"] = model_recommendations
            
            # Generate insights
            results["insights"] = await self._generate_predictive_insights(
                feature_importance, correlation_analysis, data_readiness
            )
            
            # Calculate measures
            results["measures"] = await self._calculate_predictive_measures(
                feature_importance, correlation_analysis, data_readiness
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing predictive potential: {e}")
            return {
                "insights": [f"Error in predictive analysis: {str(e)}"],
                "measures": {},
                "analysis": {
                    "target_variable": target_variable,
                    "feature_importance": {},
                    "correlation_analysis": {},
                    "model_recommendations": [],
                    "data_readiness": {}
                }
            }
    
    async def _analyze_feature_importance(
        self, 
        df: pd.DataFrame, 
        target_variable: str, 
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """Analyze feature importance for prediction."""
        try:
            # Get clean data
            data = df[[target_variable] + feature_cols].dropna()
            
            if len(data) < 10:
                return {"message": "Insufficient data for feature importance analysis"}
            
            target = data[target_variable]
            features = data[feature_cols]
            
            # Calculate correlation-based importance
            correlations = {}
            for col in feature_cols:
                corr = target.corr(features[col])
                if not pd.isna(corr):
                    correlations[col] = {
                        "correlation": float(corr),
                        "abs_correlation": float(abs(corr)),
                        "importance_score": float(abs(corr))
                    }
            
            # Sort by importance
            sorted_features = sorted(
                correlations.items(), 
                key=lambda x: x[1]["abs_correlation"], 
                reverse=True
            )
            
            # Categorize features
            high_importance = [f for f, info in sorted_features if info["abs_correlation"] > 0.7]
            medium_importance = [f for f, info in sorted_features if 0.3 <= info["abs_correlation"] <= 0.7]
            low_importance = [f for f, info in sorted_features if info["abs_correlation"] < 0.3]
            
            return {
                "correlations": correlations,
                "sorted_features": [f for f, _ in sorted_features],
                "high_importance": high_importance,
                "medium_importance": medium_importance,
                "low_importance": low_importance,
                "top_features": [f for f, _ in sorted_features[:5]]  # Top 5 features
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing feature importance: {e}")
            return {"message": f"Error in feature importance analysis: {str(e)}"}
    
    async def _analyze_target_correlations(
        self, 
        df: pd.DataFrame, 
        target_variable: str, 
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """Analyze correlations between features and target."""
        try:
            data = df[[target_variable] + feature_cols].dropna()
            
            if len(data) < 3:
                return {"message": "Insufficient data for correlation analysis"}
            
            target = data[target_variable]
            features = data[feature_cols]
            
            # Calculate correlations
            correlations = {}
            for col in feature_cols:
                corr = target.corr(features[col])
                if not pd.isna(corr):
                    correlations[col] = {
                        "correlation": float(corr),
                        "strength": self._classify_correlation_strength(abs(corr)),
                        "direction": "positive" if corr > 0 else "negative"
                    }
            
            # Find strongest correlations
            if correlations:
                strongest_positive = max(
                    [(col, info) for col, info in correlations.items() if info["correlation"] > 0],
                    key=lambda x: x[1]["correlation"],
                    default=(None, None)
                )
                strongest_negative = min(
                    [(col, info) for col, info in correlations.items() if info["correlation"] < 0],
                    key=lambda x: x[1]["correlation"],
                    default=(None, None)
                )
            else:
                strongest_positive = (None, None)
                strongest_negative = (None, None)
            
            return {
                "correlations": correlations,
                "strongest_positive": strongest_positive[0] if strongest_positive[0] else None,
                "strongest_negative": strongest_negative[0] if strongest_negative[0] else None,
                "average_correlation": float(np.mean([info["correlation"] for info in correlations.values()])) if correlations else 0,
                "correlation_count": len(correlations)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing target correlations: {e}")
            return {"message": f"Error in correlation analysis: {str(e)}"}
    
    async def _assess_data_readiness(
        self, 
        df: pd.DataFrame, 
        target_variable: str, 
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """Assess data readiness for predictive modeling."""
        try:
            data = df[[target_variable] + feature_cols]
            
            # Basic data metrics
            total_rows = len(data)
            missing_rows = data.isnull().any(axis=1).sum()
            complete_rows = total_rows - missing_rows
            
            # Target variable analysis
            target_stats = {
                "total_values": len(data[target_variable]),
                "missing_values": data[target_variable].isnull().sum(),
                "unique_values": data[target_variable].nunique(),
                "data_type": str(data[target_variable].dtype)
            }
            
            # Feature analysis
            feature_stats = {}
            for col in feature_cols:
                feature_stats[col] = {
                    "missing_values": data[col].isnull().sum(),
                    "missing_percentage": (data[col].isnull().sum() / total_rows) * 100,
                    "unique_values": data[col].nunique(),
                    "data_type": str(data[col].dtype)
                }
            
            # Calculate readiness score
            readiness_score = await self._calculate_readiness_score(
                total_rows, missing_rows, target_stats, feature_stats
            )
            
            # Assess readiness level
            readiness_level = self._assess_readiness_level(readiness_score)
            
            return {
                "total_rows": total_rows,
                "complete_rows": complete_rows,
                "missing_rows": missing_rows,
                "completeness_percentage": (complete_rows / total_rows) * 100,
                "target_stats": target_stats,
                "feature_stats": feature_stats,
                "readiness_score": readiness_score,
                "readiness_level": readiness_level,
                "recommendations": await self._generate_readiness_recommendations(
                    total_rows, missing_rows, target_stats, feature_stats
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing data readiness: {e}")
            return {"message": f"Error in data readiness assessment: {str(e)}"}
    
    async def _calculate_readiness_score(
        self, 
        total_rows: int, 
        missing_rows: int, 
        target_stats: Dict[str, Any], 
        feature_stats: Dict[str, Any]
    ) -> float:
        """Calculate data readiness score."""
        try:
            score = 100.0
            
            # Deduct for missing data
            missing_percentage = (missing_rows / total_rows) * 100
            score -= min(missing_percentage * 2, 40)  # Max 40 point deduction
            
            # Deduct for small dataset
            if total_rows < 100:
                score -= 20
            elif total_rows < 50:
                score -= 40
            
            # Deduct for target variable issues
            if target_stats["missing_values"] > 0:
                target_missing_pct = (target_stats["missing_values"] / total_rows) * 100
                score -= min(target_missing_pct * 3, 30)  # Max 30 point deduction
            
            # Deduct for feature issues
            high_missing_features = 0
            for col, stats in feature_stats.items():
                if stats["missing_percentage"] > 50:
                    high_missing_features += 1
            
            score -= min(high_missing_features * 10, 20)  # Max 20 point deduction
            
            return max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error calculating readiness score: {e}")
            return 0.0
    
    def _assess_readiness_level(self, score: float) -> str:
        """Assess data readiness level."""
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
    
    async def _generate_readiness_recommendations(
        self, 
        total_rows: int, 
        missing_rows: int, 
        target_stats: Dict[str, Any], 
        feature_stats: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improving data readiness."""
        try:
            recommendations = []
            
            # Dataset size recommendations
            if total_rows < 100:
                recommendations.append("Collect more data - current dataset is too small for reliable modeling")
            elif total_rows < 500:
                recommendations.append("Consider collecting more data for better model performance")
            
            # Missing data recommendations
            missing_percentage = (missing_rows / total_rows) * 100
            if missing_percentage > 20:
                recommendations.append("Address missing data - high percentage of incomplete records")
            elif missing_percentage > 5:
                recommendations.append("Consider imputation strategies for missing values")
            
            # Target variable recommendations
            if target_stats["missing_values"] > 0:
                recommendations.append("Clean target variable - missing values will prevent modeling")
            
            # Feature recommendations
            high_missing_features = [col for col, stats in feature_stats.items() 
                                   if stats["missing_percentage"] > 50]
            if high_missing_features:
                recommendations.append(f"Remove or fix high-missing features: {', '.join(high_missing_features)}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating readiness recommendations: {e}")
            return []
    
    async def _generate_model_recommendations(
        self, 
        feature_importance: Dict[str, Any], 
        correlation_analysis: Dict[str, Any], 
        data_readiness: Dict[str, Any]
    ) -> List[str]:
        """Generate model recommendations based on analysis."""
        try:
            recommendations = []
            
            # Based on feature importance
            high_importance = feature_importance.get("high_importance", [])
            if high_importance:
                recommendations.append(f"Use {', '.join(high_importance[:3])} as primary features")
            
            # Based on correlation strength
            avg_correlation = correlation_analysis.get("average_correlation", 0)
            if avg_correlation > 0.7:
                recommendations.append("Strong correlations detected - linear models should work well")
            elif avg_correlation < 0.3:
                recommendations.append("Weak correlations - consider non-linear models or feature engineering")
            
            # Based on data readiness
            readiness_level = data_readiness.get("readiness_level", "unknown")
            if readiness_level == "excellent":
                recommendations.append("Data is ready for advanced modeling techniques")
            elif readiness_level == "good":
                recommendations.append("Data is suitable for most modeling approaches")
            elif readiness_level in ["fair", "poor"]:
                recommendations.append("Data needs cleaning before modeling")
            else:
                recommendations.append("Data requires significant preparation for modeling")
            
            # Based on dataset size
            total_rows = data_readiness.get("total_rows", 0)
            if total_rows > 10000:
                recommendations.append("Large dataset - consider using ensemble methods")
            elif total_rows < 1000:
                recommendations.append("Small dataset - use simple models to avoid overfitting")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating model recommendations: {e}")
            return []
    
    async def _generate_predictive_insights(
        self, 
        feature_importance: Dict[str, Any], 
        correlation_analysis: Dict[str, Any], 
        data_readiness: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from predictive analysis."""
        try:
            insights = []
            
            # Feature importance insights
            top_features = feature_importance.get("top_features", [])
            if top_features:
                insights.append(f"Top predictive features: {', '.join(top_features)}")
            
            high_importance = feature_importance.get("high_importance", [])
            if high_importance:
                insights.append(f"High importance features detected: {len(high_importance)} features")
            
            # Correlation insights
            strongest_positive = correlation_analysis.get("strongest_positive")
            strongest_negative = correlation_analysis.get("strongest_negative")
            
            if strongest_positive:
                insights.append(f"Strongest positive correlation: {strongest_positive}")
            if strongest_negative:
                insights.append(f"Strongest negative correlation: {strongest_negative}")
            
            # Data readiness insights
            readiness_level = data_readiness.get("readiness_level", "unknown")
            completeness = data_readiness.get("completeness_percentage", 0)
            
            insights.append(f"Data readiness: {readiness_level} ({completeness:.1f}% complete)")
            
            # Overall assessment
            if readiness_level in ["excellent", "good"] and high_importance:
                insights.append("Data shows strong predictive potential")
            elif readiness_level in ["fair", "poor"]:
                insights.append("Data needs improvement before modeling")
            else:
                insights.append("Data requires significant preparation for predictive modeling")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating predictive insights: {e}")
            return ["Error generating predictive insights"]
    
    async def _calculate_predictive_measures(
        self, 
        feature_importance: Dict[str, Any], 
        correlation_analysis: Dict[str, Any], 
        data_readiness: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate predictive measures."""
        try:
            measures = {
                "feature_count": len(feature_importance.get("correlations", {})),
                "high_importance_count": len(feature_importance.get("high_importance", [])),
                "average_correlation": correlation_analysis.get("average_correlation", 0),
                "readiness_score": data_readiness.get("readiness_score", 0),
                "completeness_percentage": data_readiness.get("completeness_percentage", 0),
                "predictive_potential": 0.0
            }
            
            # Calculate predictive potential score
            potential_score = 0.0
            
            # Feature importance component (40%)
            if measures["high_importance_count"] > 0:
                potential_score += 0.4
            
            # Correlation component (30%)
            if measures["average_correlation"] > 0.5:
                potential_score += 0.3
            elif measures["average_correlation"] > 0.3:
                potential_score += 0.2
            
            # Data readiness component (30%)
            readiness_score = measures["readiness_score"]
            if readiness_score >= 80:
                potential_score += 0.3
            elif readiness_score >= 60:
                potential_score += 0.2
            elif readiness_score >= 40:
                potential_score += 0.1
            
            measures["predictive_potential"] = min(1.0, potential_score)
            
            return measures
            
        except Exception as e:
            self.logger.error(f"Error calculating predictive measures: {e}")
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

