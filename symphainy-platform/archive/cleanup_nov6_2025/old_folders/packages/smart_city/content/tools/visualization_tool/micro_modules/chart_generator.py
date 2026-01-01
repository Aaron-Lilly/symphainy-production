"""
Chart Generator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class ChartGenerator:
    """
    Chart generation following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("ChartGenerator micro-module initialized")
    
    async def generate_config(self, chart_type: str, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """
        Generate chart configuration for frontend.
        
        Args:
            chart_type: Type of chart to generate
            data_points: Formatted data points
            context: Additional context
            
        Returns:
            Chart configuration dictionary
        """
        try:
            config = {
                "type": chart_type,
                "options": {},
                "data": {
                    "labels": [],
                    "datasets": []
                },
                "responsive": True,
                "maintainAspectRatio": False
            }
            
            # Generate configuration based on chart type
            if chart_type == "bar":
                config = await self._generate_bar_config(data_points, context)
            elif chart_type == "line":
                config = await self._generate_line_config(data_points, context)
            elif chart_type == "pie":
                config = await self._generate_pie_config(data_points, context)
            elif chart_type == "scatter":
                config = await self._generate_scatter_config(data_points, context)
            elif chart_type == "histogram":
                config = await self._generate_histogram_config(data_points, context)
            else:
                config = await self._generate_default_config(data_points, context)
            
            self.logger.info(f"Chart configuration generated for {chart_type}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error generating chart config: {e}")
            return self._get_default_config()
    
    async def _generate_bar_config(self, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate bar chart configuration."""
        try:
            if not data_points:
                return self._get_default_config()
            
            # Extract labels and values
            labels = [point.get("label", f"Item {i}") for i, point in enumerate(data_points)]
            values = [point.get("value", 0) for point in data_points]
            
            return {
                "type": "bar",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": "Values",
                        "data": values,
                        "backgroundColor": self._generate_colors(len(values)),
                        "borderColor": self._generate_border_colors(len(values)),
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"Bar Chart - {context}" if context else "Bar Chart"
                        },
                        "legend": {
                            "display": True
                        }
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True
                        }
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating bar config: {e}")
            return self._get_default_config()
    
    async def _generate_line_config(self, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate line chart configuration."""
        try:
            if not data_points:
                return self._get_default_config()
            
            # Extract labels and values
            labels = [point.get("label", f"Point {i}") for i, point in enumerate(data_points)]
            values = [point.get("value", 0) for point in data_points]
            
            return {
                "type": "line",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": "Trend",
                        "data": values,
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "tension": 0.1,
                        "fill": False
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"Line Chart - {context}" if context else "Line Chart"
                        }
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True
                        }
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating line config: {e}")
            return self._get_default_config()
    
    async def _generate_pie_config(self, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate pie chart configuration."""
        try:
            if not data_points:
                return self._get_default_config()
            
            # Extract labels and values
            labels = [point.get("label", f"Category {i}") for i, point in enumerate(data_points)]
            values = [point.get("value", 0) for point in data_points]
            
            return {
                "type": "pie",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "data": values,
                        "backgroundColor": self._generate_colors(len(values)),
                        "borderColor": self._generate_border_colors(len(values)),
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"Pie Chart - {context}" if context else "Pie Chart"
                        },
                        "legend": {
                            "position": "right"
                        }
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating pie config: {e}")
            return self._get_default_config()
    
    async def _generate_scatter_config(self, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate scatter plot configuration."""
        try:
            if not data_points:
                return self._get_default_config()
            
            # Extract x and y values
            scatter_data = []
            for point in data_points:
                if "x" in point and "y" in point:
                    scatter_data.append({
                        "x": point["x"],
                        "y": point["y"]
                    })
            
            return {
                "type": "scatter",
                "data": {
                    "datasets": [{
                        "label": "Data Points",
                        "data": scatter_data,
                        "backgroundColor": "rgba(255, 99, 132, 0.6)",
                        "borderColor": "rgba(255, 99, 132, 1)",
                        "pointRadius": 5
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"Scatter Plot - {context}" if context else "Scatter Plot"
                        }
                    },
                    "scales": {
                        "x": {
                            "type": "linear",
                            "position": "bottom"
                        },
                        "y": {
                            "beginAtZero": True
                        }
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating scatter config: {e}")
            return self._get_default_config()
    
    async def _generate_histogram_config(self, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate histogram configuration."""
        try:
            if not data_points:
                return self._get_default_config()
            
            # Extract values for histogram
            values = [point.get("value", 0) for point in data_points if "value" in point]
            
            # Create histogram bins
            bins = self._create_histogram_bins(values)
            
            return {
                "type": "bar",
                "data": {
                    "labels": [f"{bin_start}-{bin_end}" for bin_start, bin_end in bins],
                    "datasets": [{
                        "label": "Frequency",
                        "data": [self._count_in_bin(values, bin_start, bin_end) for bin_start, bin_end in bins],
                        "backgroundColor": "rgba(54, 162, 235, 0.6)",
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "borderWidth": 1
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": f"Histogram - {context}" if context else "Histogram"
                        }
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True
                        }
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating histogram config: {e}")
            return self._get_default_config()
    
    async def _generate_default_config(self, data_points: List[Dict[str, Any]], context: str) -> Dict[str, Any]:
        """Generate default configuration."""
        return self._get_default_config()
    
    def _generate_colors(self, count: int) -> List[str]:
        """Generate colors for chart elements."""
        colors = [
            "rgba(255, 99, 132, 0.6)",
            "rgba(54, 162, 235, 0.6)",
            "rgba(255, 205, 86, 0.6)",
            "rgba(75, 192, 192, 0.6)",
            "rgba(153, 102, 255, 0.6)",
            "rgba(255, 159, 64, 0.6)",
            "rgba(199, 199, 199, 0.6)",
            "rgba(83, 102, 255, 0.6)"
        ]
        return [colors[i % len(colors)] for i in range(count)]
    
    def _generate_border_colors(self, count: int) -> List[str]:
        """Generate border colors for chart elements."""
        colors = [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 205, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
            "rgba(255, 159, 64, 1)",
            "rgba(199, 199, 199, 1)",
            "rgba(83, 102, 255, 1)"
        ]
        return [colors[i % len(colors)] for i in range(count)]
    
    def _create_histogram_bins(self, values: List[float], num_bins: int = 10) -> List[tuple]:
        """Create histogram bins."""
        if not values:
            return []
        
        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / num_bins
        
        bins = []
        for i in range(num_bins):
            bin_start = min_val + i * bin_width
            bin_end = min_val + (i + 1) * bin_width
            bins.append((bin_start, bin_end))
        
        return bins
    
    def _count_in_bin(self, values: List[float], bin_start: float, bin_end: float) -> int:
        """Count values in a histogram bin."""
        count = 0
        for value in values:
            if bin_start <= value < bin_end:
                count += 1
        return count
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default chart configuration."""
        return {
            "type": "bar",
            "data": {
                "labels": ["No Data"],
                "datasets": [{
                    "label": "Values",
                    "data": [0],
                    "backgroundColor": "rgba(199, 199, 199, 0.6)"
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "No Data Available"
                    }
                }
            }
        }

