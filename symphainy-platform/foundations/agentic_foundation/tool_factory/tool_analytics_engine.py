"""
Tool Analytics Engine

This module handles tool usage analytics, performance monitoring,
and optimization recommendations.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class ToolAnalyticsEngine:
    """
    Engine for analyzing tool usage patterns, performance metrics,
    and providing optimization recommendations.
    """
    
    def __init__(self, tool_factory_service):
        """
        Initialize the Tool Analytics Engine.
        
        Args:
            tool_factory_service: Reference to the Tool Factory Service
        """
        self.tool_factory = tool_factory_service
        self.usage_data = defaultdict(list)
        self.performance_metrics = defaultdict(list)
        self.error_logs = defaultdict(list)
        self.analytics_cache = {}
        self.cache_ttl = 300  # 5 minutes TTL
        
        logger.info("Tool Analytics Engine initialized")
    
    async def track_tool_usage(self, tool_name: str, context: Dict[str, Any], result: Dict[str, Any]):
        """
        Track tool usage for analytics.
        
        Args:
            tool_name: Name of the tool
            context: Tool execution context
            result: Tool execution result
        """
        try:
            usage_record = {
                "tool_name": tool_name,
                "timestamp": datetime.now().isoformat(),
                "context_size": len(json.dumps(context)),
                "result_size": len(json.dumps(result)),
                "success": result.get("success", True),
                "execution_time": result.get("_execution_metadata", {}).get("execution_time", 0),
                "server": result.get("_execution_metadata", {}).get("server", "unknown"),
                "domain": result.get("_execution_metadata", {}).get("domain", "unknown")
            }
            
            self.usage_data[tool_name].append(usage_record)
            
            # Track performance metrics
            if "execution_time" in usage_record:
                self.performance_metrics[tool_name].append(usage_record["execution_time"])
            
            # Track errors
            if not usage_record["success"]:
                error_record = {
                    "tool_name": tool_name,
                    "timestamp": usage_record["timestamp"],
                    "error": result.get("error", "Unknown error"),
                    "context": context
                }
                self.error_logs[tool_name].append(error_record)
            
            logger.debug(f"Tracked usage for tool: {tool_name}")
            
        except Exception as e:
            logger.error(f"Error tracking tool usage for {tool_name}: {e}")
    
    async def get_tool_usage_statistics(self, tool_name: str = None, time_period: int = 3600) -> Dict[str, Any]:
        """
        Get tool usage statistics.
        
        Args:
            tool_name: Specific tool name (None for all tools)
            time_period: Time period in seconds (default: 1 hour)
            
        Returns:
            Usage statistics
        """
        try:
            cache_key = f"usage_stats:{tool_name}:{time_period}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            cutoff_time = datetime.now() - timedelta(seconds=time_period)
            
            if tool_name:
                # Get statistics for specific tool
                tools_to_analyze = [tool_name]
            else:
                # Get statistics for all tools
                tools_to_analyze = list(self.usage_data.keys())
            
            statistics = {}
            
            for tool in tools_to_analyze:
                if tool not in self.usage_data:
                    continue
                
                # Filter by time period
                recent_usage = [
                    record for record in self.usage_data[tool]
                    if datetime.fromisoformat(record["timestamp"]) >= cutoff_time
                ]
                
                if not recent_usage:
                    continue
                
                # Calculate statistics
                total_calls = len(recent_usage)
                successful_calls = sum(1 for record in recent_usage if record["success"])
                failed_calls = total_calls - successful_calls
                
                execution_times = [record["execution_time"] for record in recent_usage if record["execution_time"] > 0]
                
                tool_stats = {
                    "tool_name": tool,
                    "total_calls": total_calls,
                    "successful_calls": successful_calls,
                    "failed_calls": failed_calls,
                    "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
                    "average_execution_time": statistics.mean(execution_times) if execution_times else 0,
                    "min_execution_time": min(execution_times) if execution_times else 0,
                    "max_execution_time": max(execution_times) if execution_times else 0,
                    "median_execution_time": statistics.median(execution_times) if execution_times else 0,
                    "average_context_size": statistics.mean([record["context_size"] for record in recent_usage]),
                    "average_result_size": statistics.mean([record["result_size"] for record in recent_usage])
                }
                
                statistics[tool] = tool_stats
            
            # Cache the results
            self.analytics_cache[cache_key] = statistics
            
            logger.debug(f"Generated usage statistics for {len(statistics)} tools")
            return statistics
            
        except Exception as e:
            logger.error(f"Error generating usage statistics: {e}")
            return {}
    
    async def get_performance_analysis(self, tool_name: str = None) -> Dict[str, Any]:
        """
        Get performance analysis for tools.
        
        Args:
            tool_name: Specific tool name (None for all tools)
            
        Returns:
            Performance analysis
        """
        try:
            cache_key = f"performance_analysis:{tool_name}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            if tool_name:
                tools_to_analyze = [tool_name]
            else:
                tools_to_analyze = list(self.performance_metrics.keys())
            
            analysis = {}
            
            for tool in tools_to_analyze:
                if tool not in self.performance_metrics:
                    continue
                
                execution_times = self.performance_metrics[tool]
                if not execution_times:
                    continue
                
                # Calculate performance metrics
                avg_time = statistics.mean(execution_times)
                median_time = statistics.median(execution_times)
                std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
                
                # Identify performance trends
                recent_times = execution_times[-10:] if len(execution_times) >= 10 else execution_times
                older_times = execution_times[:-10] if len(execution_times) >= 20 else []
                
                trend = "stable"
                if older_times:
                    recent_avg = statistics.mean(recent_times)
                    older_avg = statistics.mean(older_times)
                    if recent_avg > older_avg * 1.1:
                        trend = "degrading"
                    elif recent_avg < older_avg * 0.9:
                        trend = "improving"
                
                # Identify outliers
                outliers = []
                if len(execution_times) > 3:
                    q1 = statistics.quantiles(execution_times, n=4)[0]
                    q3 = statistics.quantiles(execution_times, n=4)[2]
                    iqr = q3 - q1
                    outlier_threshold = q3 + 1.5 * iqr
                    outliers = [t for t in execution_times if t > outlier_threshold]
                
                tool_analysis = {
                    "tool_name": tool,
                    "total_executions": len(execution_times),
                    "average_execution_time": avg_time,
                    "median_execution_time": median_time,
                    "standard_deviation": std_dev,
                    "min_execution_time": min(execution_times),
                    "max_execution_time": max(execution_times),
                    "trend": trend,
                    "outliers_count": len(outliers),
                    "outlier_percentage": len(outliers) / len(execution_times) * 100 if execution_times else 0,
                    "performance_grade": self._calculate_performance_grade(avg_time, std_dev, len(outliers))
                }
                
                analysis[tool] = tool_analysis
            
            # Cache the results
            self.analytics_cache[cache_key] = analysis
            
            logger.debug(f"Generated performance analysis for {len(analysis)} tools")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating performance analysis: {e}")
            return {}
    
    async def get_error_analysis(self, tool_name: str = None, time_period: int = 3600) -> Dict[str, Any]:
        """
        Get error analysis for tools.
        
        Args:
            tool_name: Specific tool name (None for all tools)
            time_period: Time period in seconds (default: 1 hour)
            
        Returns:
            Error analysis
        """
        try:
            cache_key = f"error_analysis:{tool_name}:{time_period}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            cutoff_time = datetime.now() - timedelta(seconds=time_period)
            
            if tool_name:
                tools_to_analyze = [tool_name]
            else:
                tools_to_analyze = list(self.error_logs.keys())
            
            analysis = {}
            
            for tool in tools_to_analyze:
                if tool not in self.error_logs:
                    continue
                
                # Filter by time period
                recent_errors = [
                    error for error in self.error_logs[tool]
                    if datetime.fromisoformat(error["timestamp"]) >= cutoff_time
                ]
                
                if not recent_errors:
                    continue
                
                # Analyze error patterns
                error_types = Counter([error["error"] for error in recent_errors])
                error_frequency = len(recent_errors)
                
                # Calculate error rate
                total_usage = len([
                    record for record in self.usage_data.get(tool, [])
                    if datetime.fromisoformat(record["timestamp"]) >= cutoff_time
                ])
                error_rate = error_frequency / total_usage if total_usage > 0 else 0
                
                tool_analysis = {
                    "tool_name": tool,
                    "error_count": error_frequency,
                    "error_rate": error_rate,
                    "total_usage": total_usage,
                    "most_common_error": error_types.most_common(1)[0] if error_types else None,
                    "error_types": dict(error_types),
                    "recent_errors": recent_errors[-5:]  # Last 5 errors
                }
                
                analysis[tool] = tool_analysis
            
            # Cache the results
            self.analytics_cache[cache_key] = analysis
            
            logger.debug(f"Generated error analysis for {len(analysis)} tools")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating error analysis: {e}")
            return {}
    
    async def get_optimization_recommendations(self, tool_name: str = None) -> List[Dict[str, Any]]:
        """
        Get optimization recommendations for tools.
        
        Args:
            tool_name: Specific tool name (None for all tools)
            
        Returns:
            List of optimization recommendations
        """
        try:
            recommendations = []
            
            # Get performance analysis
            performance_analysis = await self.get_performance_analysis(tool_name)
            
            for tool, analysis in performance_analysis.items():
                tool_recommendations = []
                
                # Check for performance issues
                if analysis["average_execution_time"] > 5.0:  # More than 5 seconds
                    tool_recommendations.append({
                        "type": "performance",
                        "priority": "high",
                        "message": f"Tool {tool} has high average execution time ({analysis['average_execution_time']:.2f}s)",
                        "recommendation": "Consider optimizing the tool implementation or adding caching"
                    })
                
                # Check for high variability
                if analysis["standard_deviation"] > analysis["average_execution_time"] * 0.5:
                    tool_recommendations.append({
                        "type": "consistency",
                        "priority": "medium",
                        "message": f"Tool {tool} has high execution time variability",
                        "recommendation": "Investigate factors causing inconsistent performance"
                    })
                
                # Check for outliers
                if analysis["outlier_percentage"] > 10:
                    tool_recommendations.append({
                        "type": "reliability",
                        "priority": "medium",
                        "message": f"Tool {tool} has {analysis['outliers_count']} execution outliers",
                        "recommendation": "Investigate and fix causes of outlier executions"
                    })
                
                # Check for degrading trend
                if analysis["trend"] == "degrading":
                    tool_recommendations.append({
                        "type": "trend",
                        "priority": "high",
                        "message": f"Tool {tool} performance is degrading over time",
                        "recommendation": "Investigate recent changes or resource constraints"
                    })
                
                recommendations.extend(tool_recommendations)
            
            # Get error analysis
            error_analysis = await self.get_error_analysis(tool_name)
            
            for tool, analysis in error_analysis.items():
                # Check for high error rate
                if analysis["error_rate"] > 0.1:  # More than 10% error rate
                    recommendations.append({
                        "type": "reliability",
                        "priority": "high",
                        "message": f"Tool {tool} has high error rate ({analysis['error_rate']:.1%})",
                        "recommendation": "Investigate and fix common error causes"
                    })
                
                # Check for specific error patterns
                if analysis["most_common_error"]:
                    error_type, count = analysis["most_common_error"]
                    if count > 5:
                        recommendations.append({
                            "type": "error_pattern",
                            "priority": "medium",
                            "message": f"Tool {tool} has recurring error: {error_type} ({count} occurrences)",
                            "recommendation": f"Fix the root cause of '{error_type}' errors"
                        })
            
            logger.debug(f"Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return []
    
    def _calculate_performance_grade(self, avg_time: float, std_dev: float, outlier_count: int) -> str:
        """Calculate performance grade based on metrics."""
        if avg_time < 1.0 and std_dev < 0.5 and outlier_count == 0:
            return "A"
        elif avg_time < 2.0 and std_dev < 1.0 and outlier_count < 3:
            return "B"
        elif avg_time < 5.0 and std_dev < 2.0 and outlier_count < 5:
            return "C"
        else:
            return "D"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached analytics result is still valid."""
        if cache_key not in self.analytics_cache:
            return False
        
        # Simple TTL check (in real implementation, store timestamps)
        return True  # For now, always return True
    
    def clear_analytics_data(self):
        """Clear all analytics data."""
        self.usage_data.clear()
        self.performance_metrics.clear()
        self.error_logs.clear()
        self.analytics_cache.clear()
        logger.info("Analytics data cleared")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        return {
            "total_tools_tracked": len(self.usage_data),
            "total_usage_records": sum(len(records) for records in self.usage_data.values()),
            "total_error_records": sum(len(errors) for errors in self.error_logs.values()),
            "cached_analytics": len(self.analytics_cache)
        }






