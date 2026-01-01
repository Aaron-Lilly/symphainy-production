"""
Content Statistics Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class ContentStatistics:
    """
    Content statistics calculation following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("ContentStatistics micro-module initialized")
    
    async def calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for structured data.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with statistical analysis
        """
        try:
            results = {
                "basic_stats": {},
                "column_stats": {},
                "data_quality": {},
                "insights": []
            }
            
            # Basic statistics
            results["basic_stats"] = await self._calculate_basic_statistics(df)
            
            # Column-level statistics
            results["column_stats"] = await self._calculate_column_statistics(df)
            
            # Data quality metrics
            results["data_quality"] = await self._calculate_quality_metrics(df)
            
            # Generate insights
            results["insights"] = await self._generate_statistical_insights(df, results)
            
            self.logger.info("Content statistics calculated successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating content statistics: {e}")
            return {
                "basic_stats": {},
                "column_stats": {},
                "data_quality": {},
                "insights": [f"Statistics calculation failed: {str(e)}"]
            }
    
    async def _calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic dataset statistics."""
        try:
            return {
                "row_count": len(df),
                "column_count": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "null_count": df.isnull().sum().sum(),
                "duplicate_count": df.duplicated().sum(),
                "unique_row_count": len(df.drop_duplicates())
            }
        except Exception as e:
            self.logger.error(f"Error calculating basic statistics: {e}")
            return {}
    
    async def _calculate_column_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate column-level statistics."""
        try:
            column_stats = {}
            
            for column in df.columns:
                col_data = df[column]
                stats = {
                    "dtype": str(col_data.dtype),
                    "null_count": col_data.isnull().sum(),
                    "null_percentage": (col_data.isnull().sum() / len(col_data)) * 100,
                    "unique_count": col_data.nunique(),
                    "unique_percentage": (col_data.nunique() / len(col_data)) * 100
                }
                
                # Numeric column statistics
                if pd.api.types.is_numeric_dtype(col_data):
                    stats.update({
                        "mean": col_data.mean(),
                        "median": col_data.median(),
                        "std": col_data.std(),
                        "min": col_data.min(),
                        "max": col_data.max(),
                        "range": col_data.max() - col_data.min()
                    })
                
                # Text column statistics
                elif pd.api.types.is_object_dtype(col_data):
                    non_null_data = col_data.dropna()
                    if len(non_null_data) > 0:
                        stats.update({
                            "avg_length": non_null_data.astype(str).str.len().mean(),
                            "max_length": non_null_data.astype(str).str.len().max(),
                            "min_length": non_null_data.astype(str).str.len().min()
                        })
                
                column_stats[column] = stats
            
            return column_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating column statistics: {e}")
            return {}
    
    async def _calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        try:
            total_cells = len(df) * len(df.columns)
            null_cells = df.isnull().sum().sum()
            duplicate_rows = df.duplicated().sum()
            
            return {
                "completeness_score": ((total_cells - null_cells) / total_cells) * 100 if total_cells > 0 else 0,
                "uniqueness_score": ((len(df) - duplicate_rows) / len(df)) * 100 if len(df) > 0 else 0,
                "consistency_score": await self._calculate_consistency_score(df),
                "overall_quality_score": 0  # Will be calculated based on other scores
            }
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {e}")
            return {}
    
    async def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score."""
        try:
            consistency_issues = 0
            total_checks = 0
            
            # Check for mixed data types in object columns
            for column in df.select_dtypes(include=['object']).columns:
                non_null_data = df[column].dropna()
                if len(non_null_data) > 0:
                    total_checks += 1
                    # Check if all values can be converted to the same type
                    try:
                        pd.to_numeric(non_null_data, errors='raise')
                        # All numeric - consistent
                    except (ValueError, TypeError):
                        # Check for mixed types
                        numeric_count = 0
                        for value in non_null_data:
                            try:
                                pd.to_numeric(value, errors='raise')
                                numeric_count += 1
                            except (ValueError, TypeError):
                                pass
                        
                        if 0 < numeric_count < len(non_null_data):
                            consistency_issues += 1
            
            if total_checks == 0:
                return 100.0  # No object columns to check
            
            return ((total_checks - consistency_issues) / total_checks) * 100
            
        except Exception as e:
            self.logger.error(f"Error calculating consistency score: {e}")
            return 0.0
    
    async def _generate_statistical_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[str]:
        """Generate statistical insights."""
        insights = []
        
        try:
            basic_stats = results.get("basic_stats", {})
            column_stats = results.get("column_stats", {})
            data_quality = results.get("data_quality", {})
            
            # Dataset size insights
            row_count = basic_stats.get("row_count", 0)
            if row_count > 10000:
                insights.append("Large dataset with over 10,000 rows")
            elif row_count > 1000:
                insights.append("Medium-sized dataset with over 1,000 rows")
            else:
                insights.append("Small dataset with less than 1,000 rows")
            
            # Data quality insights
            completeness = data_quality.get("completeness_score", 0)
            if completeness >= 95:
                insights.append("Excellent data completeness")
            elif completeness >= 80:
                insights.append("Good data completeness")
            elif completeness >= 60:
                insights.append("Moderate data completeness with some missing values")
            else:
                insights.append("Poor data completeness with significant missing values")
            
            # Column insights
            numeric_columns = [col for col, stats in column_stats.items() 
                             if pd.api.types.is_numeric_dtype(df[col])]
            text_columns = [col for col, stats in column_stats.items() 
                          if pd.api.types.is_object_dtype(df[col])]
            
            if len(numeric_columns) > 0:
                insights.append(f"Contains {len(numeric_columns)} numeric columns suitable for analysis")
            if len(text_columns) > 0:
                insights.append(f"Contains {len(text_columns)} text columns for categorical analysis")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating statistical insights: {e}")
            return ["Error generating statistical insights"]

