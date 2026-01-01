"""
Data Formatter Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class DataFormatter:
    """
    Data formatting for visualization following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("DataFormatter micro-module initialized")
    
    async def format_for_chart(self, df: pd.DataFrame, chart_type: str) -> List[Dict[str, Any]]:
        """
        Format DataFrame for chart visualization.
        
        Args:
            df: DataFrame to format
            chart_type: Type of chart to format for
            
        Returns:
            List of formatted data points
        """
        try:
            if df.empty:
                return []
            
            # Format based on chart type
            if chart_type == "bar":
                return await self._format_for_bar_chart(df)
            elif chart_type == "line":
                return await self._format_for_line_chart(df)
            elif chart_type == "pie":
                return await self._format_for_pie_chart(df)
            elif chart_type == "scatter":
                return await self._format_for_scatter_chart(df)
            elif chart_type == "histogram":
                return await self._format_for_histogram(df)
            else:
                return await self._format_for_default_chart(df)
            
        except Exception as e:
            self.logger.error(f"Error formatting data for chart: {e}")
            return []
    
    async def _format_for_bar_chart(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format data for bar chart."""
        try:
            data_points = []
            
            # Use first two columns for bar chart
            if len(df.columns) >= 2:
                label_col = df.columns[0]
                value_col = df.columns[1]
                
                for _, row in df.head(20).iterrows():  # Limit to 20 items
                    data_points.append({
                        "label": str(row[label_col]),
                        "value": float(row[value_col]) if pd.notna(row[value_col]) else 0
                    })
            else:
                # Single column - use index as labels
                for idx, value in df.iloc[:, 0].head(20).items():
                    data_points.append({
                        "label": f"Item {idx}",
                        "value": float(value) if pd.notna(value) else 0
                    })
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error formatting for bar chart: {e}")
            return []
    
    async def _format_for_line_chart(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format data for line chart."""
        try:
            data_points = []
            
            # Use first two columns for line chart
            if len(df.columns) >= 2:
                label_col = df.columns[0]
                value_col = df.columns[1]
                
                for _, row in df.head(50).iterrows():  # Limit to 50 points
                    data_points.append({
                        "label": str(row[label_col]),
                        "value": float(row[value_col]) if pd.notna(row[value_col]) else 0
                    })
            else:
                # Single column - use index as x-axis
                for idx, value in df.iloc[:, 0].head(50).items():
                    data_points.append({
                        "label": f"Point {idx}",
                        "value": float(value) if pd.notna(value) else 0
                    })
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error formatting for line chart: {e}")
            return []
    
    async def _format_for_pie_chart(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format data for pie chart."""
        try:
            data_points = []
            
            # Use first two columns for pie chart
            if len(df.columns) >= 2:
                label_col = df.columns[0]
                value_col = df.columns[1]
                
                # Group by label and sum values
                grouped = df.groupby(label_col)[value_col].sum().head(10)  # Limit to 10 categories
                
                for label, value in grouped.items():
                    data_points.append({
                        "label": str(label),
                        "value": float(value) if pd.notna(value) else 0
                    })
            else:
                # Single column - count occurrences
                value_counts = df.iloc[:, 0].value_counts().head(10)
                
                for label, count in value_counts.items():
                    data_points.append({
                        "label": str(label),
                        "value": int(count)
                    })
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error formatting for pie chart: {e}")
            return []
    
    async def _format_for_scatter_chart(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format data for scatter plot."""
        try:
            data_points = []
            
            # Need at least two numeric columns for scatter plot
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) >= 2:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
                
                for _, row in df.head(100).iterrows():  # Limit to 100 points
                    if pd.notna(row[x_col]) and pd.notna(row[y_col]):
                        data_points.append({
                            "x": float(row[x_col]),
                            "y": float(row[y_col]),
                            "label": f"Point {len(data_points)}"
                        })
            else:
                # Not enough numeric columns
                return []
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error formatting for scatter chart: {e}")
            return []
    
    async def _format_for_histogram(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format data for histogram."""
        try:
            data_points = []
            
            # Use first numeric column for histogram
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                values = df[col].dropna()
                
                for value in values.head(1000):  # Limit to 1000 values
                    data_points.append({
                        "value": float(value),
                        "label": f"Value {len(data_points)}"
                    })
            else:
                # No numeric columns
                return []
            
            return data_points
            
        except Exception as e:
            self.logger.error(f"Error formatting for histogram: {e}")
            return []
    
    async def _format_for_default_chart(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format data for default chart (bar chart)."""
        return await self._format_for_bar_chart(df)
    
    async def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary of data for visualization recommendations."""
        try:
            summary = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
                "categorical_columns": len(df.select_dtypes(include=['object']).columns),
                "datetime_columns": len(df.select_dtypes(include=['datetime']).columns),
                "recommended_charts": []
            }
            
            # Recommend chart types based on data
            if summary["numeric_columns"] >= 2:
                summary["recommended_charts"].extend(["scatter", "line"])
            
            if summary["categorical_columns"] > 0:
                summary["recommended_charts"].extend(["bar", "pie"])
            
            if summary["numeric_columns"] > 0:
                summary["recommended_charts"].extend(["histogram", "bar"])
            
            # Remove duplicates and limit
            summary["recommended_charts"] = list(set(summary["recommended_charts"]))[:5]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting data summary: {e}")
            return {
                "total_rows": 0,
                "total_columns": 0,
                "numeric_columns": 0,
                "categorical_columns": 0,
                "datetime_columns": 0,
                "recommended_charts": ["bar"]
            }

