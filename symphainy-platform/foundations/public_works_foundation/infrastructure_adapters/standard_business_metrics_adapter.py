#!/usr/bin/env python3
"""
Standard Business Metrics Adapter

Infrastructure adapter for standard business metrics calculation using pandas, numpy, scipy.

WHAT (Infrastructure Adapter Role): I provide standard business metrics calculation capabilities
HOW (Adapter Implementation): I wrap pandas, numpy, scipy for metrics analysis
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..abstraction_contracts.business_metrics_protocol import BusinessMetricsResult


class StandardBusinessMetricsAdapter:
    """
    Standard Business Metrics Adapter
    
    Provides standard business metrics calculation capabilities using pandas, numpy, scipy.
    """
    
    def __init__(self):
        """Initialize Standard Business Metrics Adapter."""
        self.logger = logging.getLogger("StandardBusinessMetricsAdapter")
        self.logger.info("🏗️ StandardBusinessMetricsAdapter initialized")
    
    async def calculate_kpis(self, business_data: Dict[str, Any]) -> BusinessMetricsResult:
        """
        Calculate Key Performance Indicators (KPIs).
        
        Args:
            business_data: Business data for KPI calculation
            
        Returns:
            BusinessMetricsResult: Result of the KPI calculation
        """
        try:
            self.logger.info("Calculating KPIs using standard statistical methods...")
            
            # Extract business metrics
            revenue = business_data.get("revenue", 0)
            costs = business_data.get("costs", 0)
            profit = revenue - costs
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            
            # Calculate efficiency ratios
            efficiency_ratio = (costs / revenue * 100) if revenue > 0 else 0
            growth_rate = business_data.get("growth_rate", 0)
            
            # Calculate performance metrics
            customer_satisfaction = business_data.get("customer_satisfaction", 0)
            employee_satisfaction = business_data.get("employee_satisfaction", 0)
            market_share = business_data.get("market_share", 0)
            
            # Calculate composite performance score
            performance_score = self._calculate_performance_score({
                "profit_margin": profit_margin,
                "efficiency_ratio": 100 - efficiency_ratio,  # Invert for scoring
                "growth_rate": growth_rate,
                "customer_satisfaction": customer_satisfaction,
                "employee_satisfaction": employee_satisfaction,
                "market_share": market_share
            })
            
            # Generate KPI insights
            insights = self._generate_kpi_insights({
                "profit_margin": profit_margin,
                "efficiency_ratio": efficiency_ratio,
                "growth_rate": growth_rate,
                "performance_score": performance_score
            })
            
            return BusinessMetricsResult(
                success=True,
                kpis={
                    "revenue": revenue,
                    "costs": costs,
                    "profit": profit,
                    "profit_margin": round(profit_margin, 2),
                    "efficiency_ratio": round(efficiency_ratio, 2),
                    "growth_rate": round(growth_rate, 2),
                    "customer_satisfaction": customer_satisfaction,
                    "employee_satisfaction": employee_satisfaction,
                    "market_share": market_share,
                    "performance_score": round(performance_score, 2)
                },
                insights=insights,
                recommendations=self._generate_recommendations(performance_score, insights),
                metadata={
                    "calculation_method": "standard",
                    "calculated_at": datetime.utcnow().isoformat(),
                    "data_points": len(business_data)
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate KPIs: {e}")
            return BusinessMetricsResult(
                success=False,
                kpis={},
                insights=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def benchmark_performance(self, metrics_data: Dict[str, Any], industry: str = "default") -> BusinessMetricsResult:
        """
        Benchmark performance against industry standards.
        
        Args:
            metrics_data: Business metrics data
            industry: Industry for benchmarking
            
        Returns:
            BusinessMetricsResult: Result of the benchmarking
        """
        try:
            self.logger.info(f"Benchmarking performance against {industry} industry standards...")
            
            # Get industry benchmarks
            industry_benchmarks = self._get_industry_benchmarks(industry)
            
            # Calculate performance vs benchmarks
            benchmark_results = {}
            performance_scores = {}
            
            for metric, value in metrics_data.items():
                if metric in industry_benchmarks:
                    benchmark = industry_benchmarks[metric]
                    benchmark_value = benchmark.get("average", 0)
                    benchmark_std = benchmark.get("std_dev", 0)
                    
                    # Calculate z-score (how many standard deviations from mean)
                    if benchmark_std > 0:
                        z_score = (value - benchmark_value) / benchmark_std
                    else:
                        z_score = 0
                    
                    # Convert z-score to percentile
                    percentile = stats.norm.cdf(z_score) * 100
                    
                    benchmark_results[metric] = {
                        "value": value,
                        "benchmark": benchmark_value,
                        "z_score": round(z_score, 2),
                        "percentile": round(percentile, 2),
                        "performance": self._classify_performance(percentile)
                    }
                    
                    performance_scores[metric] = percentile
            
            # Calculate overall benchmark score
            overall_score = np.mean(list(performance_scores.values())) if performance_scores else 0
            
            # Generate benchmark insights
            insights = self._generate_benchmark_insights(benchmark_results, overall_score)
            
            return BusinessMetricsResult(
                success=True,
                benchmark_results=benchmark_results,
                overall_benchmark_score=round(overall_score, 2),
                insights=insights,
                recommendations=self._generate_benchmark_recommendations(benchmark_results),
                metadata={
                    "benchmark_method": "industry_standard",
                    "industry": industry,
                    "benchmarked_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to benchmark performance: {e}")
            return BusinessMetricsResult(
                success=False,
                benchmark_results={},
                overall_benchmark_score=0,
                insights=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> BusinessMetricsResult:
        """
        Analyze business trends from historical data.
        
        Args:
            historical_data: Historical business data
            
        Returns:
            BusinessMetricsResult: Result of the trend analysis
        """
        try:
            self.logger.info("Analyzing business trends from historical data...")
            
            if not historical_data:
                return BusinessMetricsResult(
                    success=False,
                    trend_analysis={},
                    insights=[],
                    recommendations=[],
                    metadata={},
                    error="No historical data provided"
                )
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(historical_data)
            
            # Ensure date column exists and is properly formatted
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            else:
                # Create date index if no date column
                df['date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='M')
            
            # Calculate trend analysis for numeric columns
            trend_analysis = {}
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                if column != 'date':
                    values = df[column].dropna()
                    if len(values) > 1:
                        # Calculate linear trend
                        x = np.arange(len(values))
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                        
                        # Calculate growth rate
                        if len(values) > 1:
                            growth_rate = ((values.iloc[-1] - values.iloc[0]) / values.iloc[0] * 100) if values.iloc[0] != 0 else 0
                        else:
                            growth_rate = 0
                        
                        trend_analysis[column] = {
                            "slope": round(slope, 4),
                            "r_squared": round(r_value ** 2, 4),
                            "p_value": round(p_value, 4),
                            "growth_rate": round(growth_rate, 2),
                            "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                            "trend_strength": "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
                        }
            
            # Generate trend insights
            insights = self._generate_trend_insights(trend_analysis)
            
            return BusinessMetricsResult(
                success=True,
                trend_analysis=trend_analysis,
                insights=insights,
                recommendations=self._generate_trend_recommendations(trend_analysis),
                metadata={
                    "analysis_method": "linear_regression",
                    "data_points": len(historical_data),
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze trends: {e}")
            return BusinessMetricsResult(
                success=False,
                trend_analysis={},
                insights=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the adapter."""
        try:
            # Test basic functionality
            test_data = {
                "revenue": 100000,
                "costs": 80000,
                "growth_rate": 5.0,
                "customer_satisfaction": 85,
                "employee_satisfaction": 80,
                "market_share": 15
            }
            
            result = await self.calculate_kpis(test_data)
            
            return {
                "status": "healthy" if result.success else "unhealthy",
                "adapter": "StandardBusinessMetricsAdapter",
                "capabilities": [
                    "kpi_calculation",
                    "performance_benchmarking", 
                    "trend_analysis"
                ],
                "dependencies": {
                    "pandas": pd.__version__,
                    "numpy": np.__version__,
                    "scipy": stats.__version__
                },
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter": "StandardBusinessMetricsAdapter",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate composite performance score."""
        # Weighted average of normalized metrics
        weights = {
            "profit_margin": 0.25,
            "efficiency_ratio": 0.20,
            "growth_rate": 0.20,
            "customer_satisfaction": 0.15,
            "employee_satisfaction": 0.10,
            "market_share": 0.10
        }
        
        weighted_score = 0
        total_weight = 0
        
        for metric, value in metrics.items():
            if metric in weights:
                # Normalize value to 0-100 scale
                normalized_value = max(0, min(100, value))
                weighted_score += normalized_value * weights[metric]
                total_weight += weights[metric]
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
    def _generate_kpi_insights(self, metrics: Dict[str, float]) -> List[str]:
        """Generate insights from KPI metrics."""
        insights = []
        
        if metrics.get("profit_margin", 0) > 20:
            insights.append("Strong profit margins indicate healthy financial performance")
        elif metrics.get("profit_margin", 0) < 5:
            insights.append("Low profit margins suggest need for cost optimization")
        
        if metrics.get("growth_rate", 0) > 10:
            insights.append("High growth rate indicates strong market expansion")
        elif metrics.get("growth_rate", 0) < 0:
            insights.append("Negative growth rate requires immediate attention")
        
        if metrics.get("performance_score", 0) > 80:
            insights.append("Overall performance is excellent across all metrics")
        elif metrics.get("performance_score", 0) < 40:
            insights.append("Performance is below expectations and needs improvement")
        
        return insights
    
    def _generate_recommendations(self, performance_score: float, insights: List[str]) -> List[str]:
        """Generate recommendations based on performance."""
        recommendations = []
        
        if performance_score < 50:
            recommendations.append("Focus on improving operational efficiency")
            recommendations.append("Review and optimize cost structure")
            recommendations.append("Invest in customer satisfaction initiatives")
        elif performance_score < 75:
            recommendations.append("Maintain current performance levels")
            recommendations.append("Identify opportunities for growth")
        else:
            recommendations.append("Continue current successful strategies")
            recommendations.append("Consider expansion opportunities")
        
        return recommendations
    
    def _get_industry_benchmarks(self, industry: str) -> Dict[str, Dict[str, float]]:
        """Get industry benchmark data."""
        # Industry benchmark data (in a real implementation, this would come from a database)
        benchmarks = {
            "technology": {
                "profit_margin": {"average": 15.0, "std_dev": 5.0},
                "growth_rate": {"average": 12.0, "std_dev": 8.0},
                "customer_satisfaction": {"average": 80.0, "std_dev": 10.0},
                "employee_satisfaction": {"average": 75.0, "std_dev": 8.0},
                "market_share": {"average": 8.0, "std_dev": 4.0}
            },
            "manufacturing": {
                "profit_margin": {"average": 8.0, "std_dev": 3.0},
                "growth_rate": {"average": 5.0, "std_dev": 4.0},
                "customer_satisfaction": {"average": 75.0, "std_dev": 8.0},
                "employee_satisfaction": {"average": 70.0, "std_dev": 10.0},
                "market_share": {"average": 12.0, "std_dev": 6.0}
            },
            "default": {
                "profit_margin": {"average": 10.0, "std_dev": 4.0},
                "growth_rate": {"average": 6.0, "std_dev": 5.0},
                "customer_satisfaction": {"average": 78.0, "std_dev": 9.0},
                "employee_satisfaction": {"average": 72.0, "std_dev": 9.0},
                "market_share": {"average": 10.0, "std_dev": 5.0}
            }
        }
        
        return benchmarks.get(industry, benchmarks["default"])
    
    def _classify_performance(self, percentile: float) -> str:
        """Classify performance based on percentile."""
        if percentile >= 90:
            return "excellent"
        elif percentile >= 75:
            return "above_average"
        elif percentile >= 50:
            return "average"
        elif percentile >= 25:
            return "below_average"
        else:
            return "poor"
    
    def _generate_benchmark_insights(self, benchmark_results: Dict[str, Any], overall_score: float) -> List[str]:
        """Generate insights from benchmark results."""
        insights = []
        
        excellent_metrics = [k for k, v in benchmark_results.items() if v.get("percentile", 0) >= 90]
        poor_metrics = [k for k, v in benchmark_results.items() if v.get("percentile", 0) < 25]
        
        if excellent_metrics:
            insights.append(f"Excellent performance in: {', '.join(excellent_metrics)}")
        
        if poor_metrics:
            insights.append(f"Needs improvement in: {', '.join(poor_metrics)}")
        
        if overall_score >= 80:
            insights.append("Overall performance significantly exceeds industry standards")
        elif overall_score >= 60:
            insights.append("Overall performance meets or exceeds industry standards")
        elif overall_score >= 40:
            insights.append("Overall performance is below industry standards")
        else:
            insights.append("Overall performance significantly below industry standards")
        
        return insights
    
    def _generate_benchmark_recommendations(self, benchmark_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on benchmark results."""
        recommendations = []
        
        for metric, result in benchmark_results.items():
            percentile = result.get("percentile", 0)
            if percentile < 50:
                recommendations.append(f"Focus on improving {metric} (currently at {percentile:.1f}th percentile)")
        
        return recommendations
    
    def _generate_trend_insights(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis."""
        insights = []
        
        strong_trends = [k for k, v in trend_analysis.items() if v.get("trend_strength") == "strong"]
        increasing_trends = [k for k, v in trend_analysis.items() if v.get("trend_direction") == "increasing"]
        decreasing_trends = [k for k, v in trend_analysis.items() if v.get("trend_direction") == "decreasing"]
        
        if strong_trends:
            insights.append(f"Strong trends detected in: {', '.join(strong_trends)}")
        
        if increasing_trends:
            insights.append(f"Positive trends in: {', '.join(increasing_trends)}")
        
        if decreasing_trends:
            insights.append(f"Declining trends in: {', '.join(decreasing_trends)}")
        
        return insights
    
    def _generate_trend_recommendations(self, trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        for metric, analysis in trend_analysis.items():
            direction = analysis.get("trend_direction", "stable")
            strength = analysis.get("trend_strength", "weak")
            
            if direction == "decreasing" and strength == "strong":
                recommendations.append(f"Address declining trend in {metric}")
            elif direction == "increasing" and strength == "strong":
                recommendations.append(f"Leverage positive trend in {metric}")
        
        return recommendations
