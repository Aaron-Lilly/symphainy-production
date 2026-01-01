"""
Pattern Analyzer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class PatternAnalyzer:
    """
    Pattern analysis following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("PatternAnalyzer micro-module initialized")
    
    async def analyze_patterns(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """
        Analyze patterns in numeric columns.
        
        Args:
            df: DataFrame to analyze
            numeric_cols: List of numeric column names
            
        Returns:
            Pattern analysis results
        """
        try:
            results = {
                "insights": [],
                "measures": {},
                "pattern_analysis": {},
                "pattern_summary": {}
            }
            
            if len(numeric_cols) == 0:
                results["insights"].append("No numeric columns available for pattern analysis")
                return results
            
            # Analyze patterns for each numeric column
            pattern_analysis = {}
            pattern_measures = {}
            
            for col in numeric_cols:
                series = df[col].dropna()
                
                if len(series) < 3:
                    pattern_analysis[col] = {"message": "Insufficient data for pattern analysis"}
                    continue
                
                # Perform pattern analysis
                col_patterns = await self._analyze_column_patterns(series, col)
                pattern_analysis[col] = col_patterns
                
                # Extract measures
                if "measures" in col_patterns:
                    pattern_measures[col] = col_patterns["measures"]
            
            results["pattern_analysis"] = pattern_analysis
            results["measures"] = pattern_measures
            
            # Generate insights
            results["insights"] = await self._generate_pattern_insights(pattern_analysis)
            
            # Generate summary
            results["pattern_summary"] = await self._generate_pattern_summary(pattern_analysis)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}")
            return {
                "insights": [f"Error in pattern analysis: {str(e)}"],
                "measures": {},
                "pattern_analysis": {},
                "pattern_summary": {}
            }
    
    async def _analyze_column_patterns(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Analyze patterns for a single column."""
        try:
            if len(series) < 3:
                return {"message": "Insufficient data for pattern analysis"}
            
            values = series.values
            
            # Detect different types of patterns
            patterns = {
                "cyclical": await self._detect_cyclical_patterns(values),
                "seasonal": await self._detect_seasonal_patterns(values),
                "outlier_patterns": await self._detect_outlier_patterns(values),
                "clustering": await self._detect_clustering_patterns(values),
                "autocorrelation": await self._detect_autocorrelation_patterns(values)
            }
            
            # Calculate pattern measures
            measures = {
                "cyclical_strength": patterns["cyclical"]["strength"],
                "seasonal_strength": patterns["seasonal"]["strength"],
                "outlier_count": len(patterns["outlier_patterns"]["outliers"]),
                "clustering_score": patterns["clustering"]["score"],
                "autocorrelation_lag1": patterns["autocorrelation"]["lag1"],
                "pattern_complexity": await self._calculate_pattern_complexity(patterns)
            }
            
            # Generate pattern description
            description = await self._generate_pattern_description(patterns)
            
            return {
                "patterns": patterns,
                "measures": measures,
                "description": description,
                "pattern_types": [k for k, v in patterns.items() if v.get("detected", False)]
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing column patterns: {e}")
            return {"message": f"Error analyzing patterns for {column_name}: {str(e)}"}
    
    async def _detect_cyclical_patterns(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect cyclical patterns in data."""
        try:
            if len(values) < 6:
                return {"detected": False, "strength": 0, "period": 0, "message": "Insufficient data"}
            
            # Simple cyclical detection using autocorrelation
            autocorr = np.correlate(values, values, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks in autocorrelation (excluding lag 0)
            if len(autocorr) > 1:
                peaks = []
                for i in range(1, len(autocorr) - 1):
                    if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                        peaks.append((i, autocorr[i]))
                
                if peaks:
                    # Find strongest peak
                    strongest_peak = max(peaks, key=lambda x: x[1])
                    period = strongest_peak[0]
                    strength = strongest_peak[1] / autocorr[0]  # Normalize by autocorr at lag 0
                    
                    return {
                        "detected": strength > 0.3,  # Threshold for detection
                        "strength": float(strength),
                        "period": int(period),
                        "peaks": [(int(p[0]), float(p[1])) for p in peaks]
                    }
            
            return {"detected": False, "strength": 0, "period": 0, "peaks": []}
            
        except Exception as e:
            self.logger.error(f"Error detecting cyclical patterns: {e}")
            return {"detected": False, "strength": 0, "period": 0, "message": str(e)}
    
    async def _detect_seasonal_patterns(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect seasonal patterns in data."""
        try:
            if len(values) < 12:  # Need at least 12 points for seasonal analysis
                return {"detected": False, "strength": 0, "season_length": 0, "message": "Insufficient data"}
            
            # Try different seasonal periods
            best_season_length = 0
            best_strength = 0
            
            for season_length in [3, 4, 6, 12]:  # Common seasonal periods
                if len(values) >= season_length * 2:
                    strength = await self._calculate_seasonal_strength(values, season_length)
                    if strength > best_strength:
                        best_strength = strength
                        best_season_length = season_length
            
            return {
                "detected": best_strength > 0.3,
                "strength": float(best_strength),
                "season_length": int(best_season_length),
                "message": f"Best seasonal period: {best_season_length}" if best_season_length > 0 else "No seasonal pattern"
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting seasonal patterns: {e}")
            return {"detected": False, "strength": 0, "season_length": 0, "message": str(e)}
    
    async def _calculate_seasonal_strength(self, values: np.ndarray, season_length: int) -> float:
        """Calculate seasonal strength for a given period."""
        try:
            # Group values by season
            seasons = []
            for i in range(0, len(values), season_length):
                if i + season_length <= len(values):
                    seasons.append(values[i:i+season_length])
            
            if len(seasons) < 2:
                return 0.0
            
            # Calculate variance within seasons vs between seasons
            within_season_var = np.mean([np.var(season) for season in seasons])
            between_season_var = np.var([np.mean(season) for season in seasons])
            
            if within_season_var == 0:
                return 1.0 if between_season_var > 0 else 0.0
            
            # Seasonal strength (higher is more seasonal)
            strength = between_season_var / (within_season_var + between_season_var)
            return float(strength)
            
        except Exception as e:
            self.logger.error(f"Error calculating seasonal strength: {e}")
            return 0.0
    
    async def _detect_outlier_patterns(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect patterns in outliers."""
        try:
            if len(values) < 5:
                return {"detected": False, "outliers": [], "pattern": "none", "message": "Insufficient data"}
            
            # Detect outliers using IQR method
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            
            if IQR == 0:
                return {"detected": False, "outliers": [], "pattern": "none", "message": "No variation in data"}
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = []
            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    outliers.append({"index": i, "value": float(value)})
            
            # Analyze outlier patterns
            pattern = await self._analyze_outlier_pattern(outliers)
            
            return {
                "detected": len(outliers) > 0,
                "outliers": outliers,
                "pattern": pattern,
                "count": len(outliers),
                "percentage": len(outliers) / len(values) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting outlier patterns: {e}")
            return {"detected": False, "outliers": [], "pattern": "none", "message": str(e)}
    
    async def _analyze_outlier_pattern(self, outliers: List[Dict[str, Any]]) -> str:
        """Analyze the pattern of outliers."""
        try:
            if len(outliers) < 2:
                return "isolated"
            
            # Check if outliers are clustered
            indices = [outlier["index"] for outlier in outliers]
            indices.sort()
            
            # Calculate gaps between consecutive outliers
            gaps = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
            
            if not gaps:
                return "isolated"
            
            avg_gap = np.mean(gaps)
            gap_std = np.std(gaps)
            
            # If gaps are small and consistent, outliers are clustered
            if avg_gap < 5 and gap_std < 2:
                return "clustered"
            # If gaps are large and consistent, outliers are periodic
            elif avg_gap > 10 and gap_std < avg_gap * 0.5:
                return "periodic"
            # If gaps are very small, outliers are consecutive
            elif avg_gap < 2:
                return "consecutive"
            else:
                return "random"
                
        except Exception as e:
            self.logger.error(f"Error analyzing outlier pattern: {e}")
            return "unknown"
    
    async def _detect_clustering_patterns(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect clustering patterns in data."""
        try:
            if len(values) < 4:
                return {"detected": False, "score": 0, "clusters": 0, "message": "Insufficient data"}
            
            # Simple clustering detection using k-means with k=2
            from sklearn.cluster import KMeans
            
            # Reshape for sklearn
            X = values.reshape(-1, 1)
            
            # Try k=2 clustering
            kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X)
            
            # Calculate clustering score (inertia)
            score = kmeans.inertia_
            
            # Count points in each cluster
            cluster_counts = np.bincount(clusters)
            
            # Determine if clustering is meaningful
            balanced = min(cluster_counts) / max(cluster_counts) > 0.2  # Not too imbalanced
            separated = score < np.var(values) * 0.5  # Clusters are well separated
            
            return {
                "detected": balanced and separated,
                "score": float(score),
                "clusters": 2,
                "cluster_sizes": cluster_counts.tolist(),
                "balanced": balanced,
                "separated": separated
            }
            
        except ImportError:
            # Fallback if sklearn not available
            return {"detected": False, "score": 0, "clusters": 0, "message": "sklearn not available"}
        except Exception as e:
            self.logger.error(f"Error detecting clustering patterns: {e}")
            return {"detected": False, "score": 0, "clusters": 0, "message": str(e)}
    
    async def _detect_autocorrelation_patterns(self, values: np.ndarray) -> Dict[str, Any]:
        """Detect autocorrelation patterns."""
        try:
            if len(values) < 4:
                return {"detected": False, "lag1": 0, "max_lag": 0, "message": "Insufficient data"}
            
            # Calculate autocorrelation for different lags
            max_lag = min(len(values) // 2, 10)  # Limit max lag
            autocorrs = []
            
            for lag in range(1, max_lag + 1):
                if len(values) > lag:
                    # Calculate autocorrelation at this lag
                    corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
                    if not np.isnan(corr):
                        autocorrs.append((lag, corr))
            
            if not autocorrs:
                return {"detected": False, "lag1": 0, "max_lag": 0, "message": "No valid autocorrelations"}
            
            # Find strongest autocorrelation
            strongest = max(autocorrs, key=lambda x: abs(x[1]))
            lag1_corr = next((corr for lag, corr in autocorrs if lag == 1), 0)
            
            return {
                "detected": abs(strongest[1]) > 0.3,
                "lag1": float(lag1_corr),
                "max_lag": int(strongest[0]),
                "max_correlation": float(strongest[1]),
                "all_correlations": [(int(lag), float(corr)) for lag, corr in autocorrs]
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting autocorrelation patterns: {e}")
            return {"detected": False, "lag1": 0, "max_lag": 0, "message": str(e)}
    
    async def _calculate_pattern_complexity(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall pattern complexity score."""
        try:
            complexity = 0.0
            
            # Add complexity for each detected pattern
            if patterns["cyclical"]["detected"]:
                complexity += 0.3
            if patterns["seasonal"]["detected"]:
                complexity += 0.3
            if patterns["outlier_patterns"]["detected"]:
                complexity += 0.2
            if patterns["clustering"]["detected"]:
                complexity += 0.2
            if patterns["autocorrelation"]["detected"]:
                complexity += 0.1
            
            return min(1.0, complexity)
            
        except Exception as e:
            self.logger.error(f"Error calculating pattern complexity: {e}")
            return 0.0
    
    async def _generate_pattern_description(self, patterns: Dict[str, Any]) -> str:
        """Generate a description of detected patterns."""
        try:
            descriptions = []
            
            if patterns["cyclical"]["detected"]:
                period = patterns["cyclical"]["period"]
                descriptions.append(f"cyclical pattern (period: {period})")
            
            if patterns["seasonal"]["detected"]:
                season_length = patterns["seasonal"]["season_length"]
                descriptions.append(f"seasonal pattern (length: {season_length})")
            
            if patterns["outlier_patterns"]["detected"]:
                pattern = patterns["outlier_patterns"]["pattern"]
                count = patterns["outlier_patterns"]["count"]
                descriptions.append(f"outlier pattern ({pattern}, {count} outliers)")
            
            if patterns["clustering"]["detected"]:
                descriptions.append("clustering pattern")
            
            if patterns["autocorrelation"]["detected"]:
                lag1 = patterns["autocorrelation"]["lag1"]
                descriptions.append(f"autocorrelation pattern (lag1: {lag1:.3f})")
            
            if not descriptions:
                return "no significant patterns detected"
            
            return "data shows " + ", ".join(descriptions)
            
        except Exception as e:
            self.logger.error(f"Error generating pattern description: {e}")
            return "error in pattern description"
    
    async def _generate_pattern_insights(self, pattern_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from pattern analysis."""
        try:
            insights = []
            
            # Count patterns by type
            pattern_counts = {
                "cyclical": 0,
                "seasonal": 0,
                "outlier": 0,
                "clustering": 0,
                "autocorrelation": 0
            }
            
            for col, analysis in pattern_analysis.items():
                if "patterns" in analysis:
                    patterns = analysis["patterns"]
                    for pattern_type in pattern_counts:
                        if patterns[pattern_type]["detected"]:
                            pattern_counts[pattern_type] += 1
            
            # Generate insights
            for pattern_type, count in pattern_counts.items():
                if count > 0:
                    insights.append(f"{pattern_type.capitalize()} patterns detected in {count} columns")
            
            # High complexity patterns
            high_complexity_cols = [col for col, analysis in pattern_analysis.items() 
                                  if analysis.get("measures", {}).get("pattern_complexity", 0) > 0.7]
            if high_complexity_cols:
                insights.append(f"High pattern complexity in: {', '.join(high_complexity_cols)}")
            
            # Outlier patterns
            outlier_cols = [col for col, analysis in pattern_analysis.items() 
                          if analysis.get("patterns", {}).get("outlier_patterns", {}).get("detected", False)]
            if outlier_cols:
                insights.append(f"Outlier patterns detected in: {', '.join(outlier_cols)}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating pattern insights: {e}")
            return ["Error generating pattern insights"]
    
    async def _generate_pattern_summary(self, pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pattern summary."""
        try:
            summary = {
                "total_columns_analyzed": len(pattern_analysis),
                "pattern_types": {"cyclical": 0, "seasonal": 0, "outlier": 0, "clustering": 0, "autocorrelation": 0},
                "high_complexity_columns": 0,
                "total_outliers": 0
            }
            
            for col, analysis in pattern_analysis.items():
                if "patterns" in analysis:
                    patterns = analysis["patterns"]
                    for pattern_type in summary["pattern_types"]:
                        if patterns[pattern_type]["detected"]:
                            summary["pattern_types"][pattern_type] += 1
                
                if "measures" in analysis:
                    complexity = analysis["measures"].get("pattern_complexity", 0)
                    if complexity > 0.7:
                        summary["high_complexity_columns"] += 1
                
                if "patterns" in analysis and "outlier_patterns" in analysis["patterns"]:
                    outlier_count = analysis["patterns"]["outlier_patterns"].get("count", 0)
                    summary["total_outliers"] += outlier_count
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating pattern summary: {e}")
            return {}

