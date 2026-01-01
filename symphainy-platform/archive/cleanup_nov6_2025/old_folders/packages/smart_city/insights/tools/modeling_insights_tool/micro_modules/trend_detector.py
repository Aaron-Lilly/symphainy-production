"""
Trend Detector Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class TrendDetector:
    """
    Trend detection following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("TrendDetector micro-module initialized")
    
    async def detect_trends(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """
        Detect trends in numeric columns.
        
        Args:
            df: DataFrame to analyze
            numeric_cols: List of numeric column names
            
        Returns:
            Trend detection results
        """
        try:
            results = {
                "insights": [],
                "measures": {},
                "trend_analysis": {},
                "trend_summary": {}
            }
            
            if len(numeric_cols) == 0:
                results["insights"].append("No numeric columns available for trend analysis")
                return results
            
            # Analyze trends for each numeric column
            trend_analysis = {}
            trend_measures = {}
            
            for col in numeric_cols:
                series = df[col].dropna()
                
                if len(series) < 3:
                    trend_analysis[col] = {"message": "Insufficient data for trend analysis"}
                    continue
                
                # Perform trend analysis
                col_trend = await self._analyze_column_trend(series, col)
                trend_analysis[col] = col_trend
                
                # Extract measures
                if "measures" in col_trend:
                    trend_measures[col] = col_trend["measures"]
            
            results["trend_analysis"] = trend_analysis
            results["measures"] = trend_measures
            
            # Generate insights
            results["insights"] = await self._generate_trend_insights(trend_analysis)
            
            # Generate summary
            results["trend_summary"] = await self._generate_trend_summary(trend_analysis)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error detecting trends: {e}")
            return {
                "insights": [f"Error in trend detection: {str(e)}"],
                "measures": {},
                "trend_analysis": {},
                "trend_summary": {}
            }
    
    async def _analyze_column_trend(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Analyze trend for a single column."""
        try:
            if len(series) < 3:
                return {"message": "Insufficient data for trend analysis"}
            
            # Convert to numpy array for analysis
            values = series.values
            
            # Simple linear trend analysis
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Calculate trend strength
            trend_strength = await self._calculate_trend_strength(values, slope)
            
            # Classify trend direction
            trend_direction = self._classify_trend_direction(slope)
            
            # Calculate trend consistency
            trend_consistency = await self._calculate_trend_consistency(values)
            
            # Detect trend changes
            trend_changes = await self._detect_trend_changes(values)
            
            # Calculate measures
            measures = {
                "slope": float(slope),
                "intercept": float(intercept),
                "trend_strength": trend_strength,
                "trend_direction": trend_direction,
                "trend_consistency": trend_consistency,
                "trend_changes": len(trend_changes),
                "r_squared": await self._calculate_r_squared(values, slope, intercept)
            }
            
            return {
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "trend_consistency": trend_consistency,
                "trend_changes": trend_changes,
                "measures": measures,
                "description": self._generate_trend_description(trend_direction, trend_strength, trend_consistency)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing column trend: {e}")
            return {"message": f"Error analyzing trend for {column_name}: {str(e)}"}
    
    async def _calculate_trend_strength(self, values: np.ndarray, slope: float) -> str:
        """Calculate trend strength."""
        try:
            # Calculate coefficient of variation
            cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
            
            # Calculate slope relative to data range
            data_range = np.max(values) - np.min(values)
            relative_slope = abs(slope) / data_range if data_range != 0 else 0
            
            # Classify strength
            if relative_slope > 0.1 and cv < 0.5:
                return "strong"
            elif relative_slope > 0.05 and cv < 1.0:
                return "moderate"
            elif relative_slope > 0.01:
                return "weak"
            else:
                return "none"
                
        except Exception as e:
            self.logger.error(f"Error calculating trend strength: {e}")
            return "unknown"
    
    def _classify_trend_direction(self, slope: float) -> str:
        """Classify trend direction."""
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    async def _calculate_trend_consistency(self, values: np.ndarray) -> str:
        """Calculate trend consistency."""
        try:
            if len(values) < 4:
                return "insufficient_data"
            
            # Split data into segments and check consistency
            segment_size = max(2, len(values) // 3)
            segments = [values[i:i+segment_size] for i in range(0, len(values), segment_size)]
            
            if len(segments) < 2:
                return "insufficient_segments"
            
            # Calculate slopes for each segment
            segment_slopes = []
            for segment in segments:
                if len(segment) >= 2:
                    x = np.arange(len(segment))
                    slope, _ = np.polyfit(x, segment, 1)
                    segment_slopes.append(slope)
            
            if len(segment_slopes) < 2:
                return "insufficient_slopes"
            
            # Check consistency
            positive_slopes = sum(1 for s in segment_slopes if s > 0)
            negative_slopes = sum(1 for s in segment_slopes if s < 0)
            
            if positive_slopes == len(segment_slopes):
                return "consistently_increasing"
            elif negative_slopes == len(segment_slopes):
                return "consistently_decreasing"
            elif abs(positive_slopes - negative_slopes) <= 1:
                return "mixed"
            else:
                return "mostly_consistent"
                
        except Exception as e:
            self.logger.error(f"Error calculating trend consistency: {e}")
            return "unknown"
    
    async def _detect_trend_changes(self, values: np.ndarray) -> List[Dict[str, Any]]:
        """Detect trend changes in the data."""
        try:
            if len(values) < 6:
                return []
            
            trend_changes = []
            
            # Use a sliding window to detect trend changes
            window_size = max(3, len(values) // 4)
            
            for i in range(window_size, len(values) - window_size):
                # Calculate slope for left and right windows
                left_window = values[i-window_size:i]
                right_window = values[i:i+window_size]
                
                if len(left_window) >= 2 and len(right_window) >= 2:
                    left_x = np.arange(len(left_window))
                    right_x = np.arange(len(right_window))
                    
                    left_slope, _ = np.polyfit(left_x, left_window, 1)
                    right_slope, _ = np.polyfit(right_x, right_window, 1)
                    
                    # Check for significant change
                    slope_change = abs(right_slope - left_slope)
                    if slope_change > 0.1:  # Threshold for significant change
                        trend_changes.append({
                            "index": i,
                            "left_slope": float(left_slope),
                            "right_slope": float(right_slope),
                            "slope_change": float(slope_change),
                            "change_type": self._classify_change_type(left_slope, right_slope)
                        })
            
            return trend_changes
            
        except Exception as e:
            self.logger.error(f"Error detecting trend changes: {e}")
            return []
    
    def _classify_change_type(self, left_slope: float, right_slope: float) -> str:
        """Classify the type of trend change."""
        if left_slope > 0 and right_slope < 0:
            return "peak"
        elif left_slope < 0 and right_slope > 0:
            return "trough"
        elif left_slope > 0 and right_slope > 0:
            return "acceleration"
        elif left_slope < 0 and right_slope < 0:
            return "deceleration"
        else:
            return "change"
    
    async def _calculate_r_squared(self, values: np.ndarray, slope: float, intercept: float) -> float:
        """Calculate R-squared for trend line."""
        try:
            x = np.arange(len(values))
            y_pred = slope * x + intercept
            
            # Calculate R-squared
            ss_res = np.sum((values - y_pred) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            
            if ss_tot == 0:
                return 0.0
            
            r_squared = 1 - (ss_res / ss_tot)
            return float(r_squared)
            
        except Exception as e:
            self.logger.error(f"Error calculating R-squared: {e}")
            return 0.0
    
    def _generate_trend_description(self, direction: str, strength: str, consistency: str) -> str:
        """Generate a description of the trend."""
        descriptions = []
        
        if strength != "none":
            descriptions.append(f"{strength} {direction} trend")
        else:
            descriptions.append("stable trend")
        
        if consistency in ["consistently_increasing", "consistently_decreasing"]:
            descriptions.append("with consistent direction")
        elif consistency == "mixed":
            descriptions.append("with mixed direction")
        
        return " ".join(descriptions)
    
    async def _generate_trend_insights(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis."""
        try:
            insights = []
            
            # Count trends by direction
            increasing_trends = []
            decreasing_trends = []
            stable_trends = []
            
            for col, analysis in trend_analysis.items():
                if "trend_direction" in analysis:
                    direction = analysis["trend_direction"]
                    if direction == "increasing":
                        increasing_trends.append(col)
                    elif direction == "decreasing":
                        decreasing_trends.append(col)
                    else:
                        stable_trends.append(col)
            
            # Generate insights
            if increasing_trends:
                insights.append(f"Increasing trends detected in {len(increasing_trends)} columns: {', '.join(increasing_trends)}")
            
            if decreasing_trends:
                insights.append(f"Decreasing trends detected in {len(decreasing_trends)} columns: {', '.join(decreasing_trends)}")
            
            if stable_trends:
                insights.append(f"Stable trends detected in {len(stable_trends)} columns: {', '.join(stable_trends)}")
            
            # Strong trends
            strong_trends = [col for col, analysis in trend_analysis.items() 
                           if analysis.get("trend_strength") == "strong"]
            if strong_trends:
                insights.append(f"Strong trends detected in: {', '.join(strong_trends)}")
            
            # Trend changes
            total_changes = sum(len(analysis.get("trend_changes", [])) for analysis in trend_analysis.values())
            if total_changes > 0:
                insights.append(f"Total trend changes detected: {total_changes}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating trend insights: {e}")
            return ["Error generating trend insights"]
    
    async def _generate_trend_summary(self, trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend summary."""
        try:
            summary = {
                "total_columns_analyzed": len(trend_analysis),
                "trend_directions": {"increasing": 0, "decreasing": 0, "stable": 0},
                "trend_strengths": {"strong": 0, "moderate": 0, "weak": 0, "none": 0},
                "trend_consistencies": {"consistently_increasing": 0, "consistently_decreasing": 0, "mixed": 0, "mostly_consistent": 0},
                "total_trend_changes": 0
            }
            
            for col, analysis in trend_analysis.items():
                if "trend_direction" in analysis:
                    direction = analysis["trend_direction"]
                    if direction in summary["trend_directions"]:
                        summary["trend_directions"][direction] += 1
                
                if "trend_strength" in analysis:
                    strength = analysis["trend_strength"]
                    if strength in summary["trend_strengths"]:
                        summary["trend_strengths"][strength] += 1
                
                if "trend_consistency" in analysis:
                    consistency = analysis["trend_consistency"]
                    if consistency in summary["trend_consistencies"]:
                        summary["trend_consistencies"][consistency] += 1
                
                if "trend_changes" in analysis:
                    summary["total_trend_changes"] += len(analysis["trend_changes"])
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating trend summary: {e}")
            return {}

