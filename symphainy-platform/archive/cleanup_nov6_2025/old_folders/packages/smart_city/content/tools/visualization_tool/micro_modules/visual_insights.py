"""
Visual Insights Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class VisualInsights:
    """
    Visual insights generation following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("VisualInsights micro-module initialized")
    
    async def generate_insights(self, df: pd.DataFrame, chart_type: str, data_points: List[Dict[str, Any]]) -> List[str]:
        """
        Generate visual insights from data and chart.
        
        Args:
            df: Original DataFrame
            chart_type: Type of chart generated
            data_points: Formatted data points
            
        Returns:
            List of visual insights
        """
        try:
            insights = []
            
            # Basic data insights
            insights.extend(await self._generate_basic_insights(df, chart_type))
            
            # Chart-specific insights
            insights.extend(await self._generate_chart_insights(chart_type, data_points))
            
            # Statistical insights
            insights.extend(await self._generate_statistical_insights(df, chart_type))
            
            # Limit to top insights
            return insights[:5]
            
        except Exception as e:
            self.logger.error(f"Error generating visual insights: {e}")
            return ["Error generating visual insights"]
    
    async def generate_recommendations(self, chart_type: str, insights: List[str]) -> List[str]:
        """
        Generate recommendations based on insights.
        
        Args:
            chart_type: Type of chart
            insights: Generated insights
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Chart-specific recommendations
            recommendations.extend(await self._generate_chart_recommendations(chart_type))
            
            # Insight-based recommendations
            recommendations.extend(await self._generate_insight_recommendations(insights))
            
            # General recommendations
            recommendations.extend(await self._generate_general_recommendations())
            
            # Limit to top recommendations
            return recommendations[:3]
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Review your data and chart configuration"]
    
    async def _generate_basic_insights(self, df: pd.DataFrame, chart_type: str) -> List[str]:
        """Generate basic data insights."""
        try:
            insights = []
            
            # Data size insights
            if len(df) > 1000:
                insights.append(f"Large dataset with {len(df)} rows - consider sampling for better performance")
            elif len(df) > 100:
                insights.append(f"Medium dataset with {len(df)} rows - good for detailed analysis")
            else:
                insights.append(f"Small dataset with {len(df)} rows - consider collecting more data")
            
            # Column insights
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                insights.append(f"Contains {len(numeric_cols)} numeric columns suitable for quantitative analysis")
            
            if len(categorical_cols) > 0:
                insights.append(f"Contains {len(categorical_cols)} categorical columns for grouping and classification")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating basic insights: {e}")
            return []
    
    async def _generate_chart_insights(self, chart_type: str, data_points: List[Dict[str, Any]]) -> List[str]:
        """Generate chart-specific insights."""
        try:
            insights = []
            
            if not data_points:
                return ["No data points available for analysis"]
            
            if chart_type == "bar":
                insights.extend(await self._analyze_bar_chart(data_points))
            elif chart_type == "line":
                insights.extend(await self._analyze_line_chart(data_points))
            elif chart_type == "pie":
                insights.extend(await self._analyze_pie_chart(data_points))
            elif chart_type == "scatter":
                insights.extend(await self._analyze_scatter_chart(data_points))
            elif chart_type == "histogram":
                insights.extend(await self._analyze_histogram(data_points))
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating chart insights: {e}")
            return []
    
    async def _analyze_bar_chart(self, data_points: List[Dict[str, Any]]) -> List[str]:
        """Analyze bar chart data."""
        try:
            insights = []
            values = [point.get("value", 0) for point in data_points]
            
            if not values:
                return ["No values to analyze"]
            
            max_value = max(values)
            min_value = min(values)
            avg_value = sum(values) / len(values)
            
            # Find highest and lowest values
            max_point = next(point for point in data_points if point.get("value") == max_value)
            min_point = next(point for point in data_points if point.get("value") == min_value)
            
            insights.append(f"Highest value: {max_point.get('label', 'Unknown')} ({max_value})")
            insights.append(f"Lowest value: {min_point.get('label', 'Unknown')} ({min_value})")
            insights.append(f"Average value: {avg_value:.2f}")
            
            # Variation analysis
            if max_value > avg_value * 2:
                insights.append("High variation detected - some values are significantly above average")
            elif max_value < avg_value * 1.5:
                insights.append("Low variation detected - values are relatively consistent")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing bar chart: {e}")
            return []
    
    async def _analyze_line_chart(self, data_points: List[Dict[str, Any]]) -> List[str]:
        """Analyze line chart data."""
        try:
            insights = []
            values = [point.get("value", 0) for point in data_points]
            
            if len(values) < 2:
                return ["Insufficient data points for trend analysis"]
            
            # Trend analysis
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg * 1.1:
                insights.append("Upward trend detected in the data")
            elif second_avg < first_avg * 0.9:
                insights.append("Downward trend detected in the data")
            else:
                insights.append("Stable trend detected in the data")
            
            # Peak and valley analysis
            max_value = max(values)
            min_value = min(values)
            insights.append(f"Peak value: {max_value}, Valley value: {min_value}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing line chart: {e}")
            return []
    
    async def _analyze_pie_chart(self, data_points: List[Dict[str, Any]]) -> List[str]:
        """Analyze pie chart data."""
        try:
            insights = []
            values = [point.get("value", 0) for point in data_points]
            total = sum(values)
            
            if total == 0:
                return ["No data to analyze"]
            
            # Find largest and smallest segments
            percentages = [(value / total) * 100 for value in values]
            max_idx = percentages.index(max(percentages))
            min_idx = percentages.index(min(percentages))
            
            max_label = data_points[max_idx].get("label", "Unknown")
            min_label = data_points[min_idx].get("label", "Unknown")
            
            insights.append(f"Largest segment: {max_label} ({percentages[max_idx]:.1f}%)")
            insights.append(f"Smallest segment: {min_label} ({percentages[min_idx]:.1f}%)")
            
            # Distribution analysis
            if percentages[max_idx] > 50:
                insights.append("Highly concentrated distribution - one segment dominates")
            elif max(percentages) < 30:
                insights.append("Balanced distribution - no single segment dominates")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing pie chart: {e}")
            return []
    
    async def _analyze_scatter_chart(self, data_points: List[Dict[str, Any]]) -> List[str]:
        """Analyze scatter plot data."""
        try:
            insights = []
            
            if not data_points:
                return ["No data points to analyze"]
            
            x_values = [point.get("x", 0) for point in data_points]
            y_values = [point.get("y", 0) for point in data_points]
            
            if len(x_values) < 2:
                return ["Insufficient data points for correlation analysis"]
            
            # Basic statistics
            x_avg = sum(x_values) / len(x_values)
            y_avg = sum(y_values) / len(y_values)
            
            insights.append(f"X-axis average: {x_avg:.2f}, Y-axis average: {y_avg:.2f}")
            
            # Simple correlation analysis
            correlation = await self._calculate_correlation(x_values, y_values)
            
            if correlation > 0.7:
                insights.append("Strong positive correlation detected")
            elif correlation < -0.7:
                insights.append("Strong negative correlation detected")
            elif abs(correlation) < 0.3:
                insights.append("Weak correlation - variables appear independent")
            else:
                insights.append("Moderate correlation detected")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing scatter chart: {e}")
            return []
    
    async def _analyze_histogram(self, data_points: List[Dict[str, Any]]) -> List[str]:
        """Analyze histogram data."""
        try:
            insights = []
            values = [point.get("value", 0) for point in data_points]
            
            if not values:
                return ["No data to analyze"]
            
            # Distribution analysis
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            insights.append(f"Mean: {mean_val:.2f}, Standard deviation: {std_dev:.2f}")
            
            # Distribution shape
            if std_dev < mean_val * 0.1:
                insights.append("Tight distribution - values are clustered around the mean")
            elif std_dev > mean_val * 0.5:
                insights.append("Wide distribution - values are spread out")
            else:
                insights.append("Normal distribution spread")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error analyzing histogram: {e}")
            return []
    
    async def _generate_statistical_insights(self, df: pd.DataFrame, chart_type: str) -> List[str]:
        """Generate statistical insights."""
        try:
            insights = []
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                return ["No numeric columns for statistical analysis"]
            
            # Basic statistics for first numeric column
            col = numeric_cols[0]
            values = df[col].dropna()
            
            if len(values) > 0:
                mean_val = values.mean()
                median_val = values.median()
                std_val = values.std()
                
                insights.append(f"Statistical summary: Mean={mean_val:.2f}, Median={median_val:.2f}, Std={std_val:.2f}")
                
                # Skewness analysis
                if abs(values.skew()) > 1:
                    insights.append("Highly skewed distribution detected")
                elif abs(values.skew()) > 0.5:
                    insights.append("Moderately skewed distribution")
                else:
                    insights.append("Approximately normal distribution")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating statistical insights: {e}")
            return []
    
    async def _generate_chart_recommendations(self, chart_type: str) -> List[str]:
        """Generate chart-specific recommendations."""
        try:
            recommendations = []
            
            if chart_type == "bar":
                recommendations.append("Consider sorting bars by value for better readability")
                recommendations.append("Use consistent colors for related categories")
            elif chart_type == "line":
                recommendations.append("Consider adding data point markers for clarity")
                recommendations.append("Use different line styles for multiple series")
            elif chart_type == "pie":
                recommendations.append("Limit to 5-7 segments for better readability")
                recommendations.append("Consider using a donut chart for better space utilization")
            elif chart_type == "scatter":
                recommendations.append("Add trend line to show correlation")
                recommendations.append("Use different colors for different groups")
            elif chart_type == "histogram":
                recommendations.append("Adjust bin size to show distribution clearly")
                recommendations.append("Consider adding normal distribution overlay")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating chart recommendations: {e}")
            return []
    
    async def _generate_insight_recommendations(self, insights: List[str]) -> List[str]:
        """Generate recommendations based on insights."""
        try:
            recommendations = []
            
            for insight in insights:
                if "trend" in insight.lower():
                    recommendations.append("Consider time series analysis for trend modeling")
                elif "correlation" in insight.lower():
                    recommendations.append("Investigate causal relationships between variables")
                elif "variation" in insight.lower():
                    recommendations.append("Analyze factors causing high variation")
                elif "concentrated" in insight.lower():
                    recommendations.append("Consider segmenting data for deeper analysis")
            
            return recommendations[:2]  # Limit to 2 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating insight recommendations: {e}")
            return []
    
    async def _generate_general_recommendations(self) -> List[str]:
        """Generate general recommendations."""
        return [
            "Consider interactive charts for better user engagement",
            "Add data labels and legends for clarity",
            "Use consistent color schemes across all visualizations"
        ]
    
    async def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate simple correlation coefficient."""
        try:
            if len(x_values) != len(y_values) or len(x_values) < 2:
                return 0.0
            
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            sum_y2 = sum(y * y for y in y_values)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return 0.0

