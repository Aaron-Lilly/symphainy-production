"""
Content Parser Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd


class ContentParser:
    """
    Content parsing utilities following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("ContentParser micro-module initialized")
    
    async def parse_structured_content(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse structured content and extract key information.
        
        Args:
            df: DataFrame to parse
            
        Returns:
            Dictionary with parsed content information
        """
        try:
            results = {
                "structure": {},
                "content_summary": {},
                "key_columns": [],
                "parsing_metadata": {}
            }
            
            # Analyze structure
            results["structure"] = await self._analyze_structure(df)
            
            # Generate content summary
            results["content_summary"] = await self._generate_content_summary(df)
            
            # Identify key columns
            results["key_columns"] = await self._identify_key_columns(df)
            
            # Add parsing metadata
            results["parsing_metadata"] = await self._generate_parsing_metadata(df)
            
            self.logger.info("Content parsing completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error parsing structured content: {e}")
            return {
                "structure": {},
                "content_summary": {},
                "key_columns": [],
                "parsing_metadata": {"error": str(e)}
            }
    
    async def _analyze_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the structure of the DataFrame."""
        try:
            return {
                "dimensions": {
                    "rows": len(df),
                    "columns": len(df.columns)
                },
                "column_types": {
                    "numeric": len(df.select_dtypes(include=['number']).columns),
                    "text": len(df.select_dtypes(include=['object']).columns),
                    "datetime": len(df.select_dtypes(include=['datetime']).columns),
                    "boolean": len(df.select_dtypes(include=['bool']).columns)
                },
                "data_density": {
                    "total_cells": len(df) * len(df.columns),
                    "non_null_cells": (len(df) * len(df.columns)) - df.isnull().sum().sum(),
                    "density_percentage": ((len(df) * len(df.columns)) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100 if len(df) > 0 else 0
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing structure: {e}")
            return {}
    
    async def _generate_content_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate content summary."""
        try:
            summary = {
                "data_types": {},
                "value_ranges": {},
                "content_characteristics": []
            }
            
            # Analyze each column
            for column in df.columns:
                col_data = df[column]
                
                # Data type analysis
                summary["data_types"][column] = str(col_data.dtype)
                
                # Value range analysis
                if pd.api.types.is_numeric_dtype(col_data):
                    summary["value_ranges"][column] = {
                        "min": col_data.min(),
                        "max": col_data.max(),
                        "range": col_data.max() - col_data.min()
                    }
                elif pd.api.types.is_object_dtype(col_data):
                    non_null_data = col_data.dropna()
                    if len(non_null_data) > 0:
                        summary["value_ranges"][column] = {
                            "min_length": non_null_data.astype(str).str.len().min(),
                            "max_length": non_null_data.astype(str).str.len().max(),
                            "avg_length": non_null_data.astype(str).str.len().mean()
                        }
            
            # Generate content characteristics
            summary["content_characteristics"] = await self._identify_content_characteristics(df)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating content summary: {e}")
            return {}
    
    async def _identify_key_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify key columns in the dataset."""
        try:
            key_columns = []
            
            for column in df.columns:
                col_data = df[column]
                
                # Check if column is a potential identifier
                if col_data.nunique() == len(col_data):
                    key_columns.append(column)
                    continue
                
                # Check if column has high uniqueness
                uniqueness_ratio = col_data.nunique() / len(col_data)
                if uniqueness_ratio > 0.8:
                    key_columns.append(column)
                    continue
                
                # Check if column name suggests it's a key
                key_indicators = ['id', 'key', 'code', 'name', 'identifier']
                if any(indicator in column.lower() for indicator in key_indicators):
                    key_columns.append(column)
            
            return key_columns[:5]  # Limit to top 5 key columns
            
        except Exception as e:
            self.logger.error(f"Error identifying key columns: {e}")
            return []
    
    async def _identify_content_characteristics(self, df: pd.DataFrame) -> List[str]:
        """Identify content characteristics."""
        characteristics = []
        
        try:
            # Check for time series data
            datetime_columns = df.select_dtypes(include=['datetime']).columns
            if len(datetime_columns) > 0:
                characteristics.append("Contains time series data")
            
            # Check for categorical data
            categorical_columns = df.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                characteristics.append("Contains categorical data")
            
            # Check for numeric data
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                characteristics.append("Contains numeric data for analysis")
            
            # Check for geographic data
            geo_indicators = ['lat', 'lon', 'latitude', 'longitude', 'address', 'city', 'state', 'country']
            geo_columns = [col for col in df.columns if any(indicator in col.lower() for indicator in geo_indicators)]
            if geo_columns:
                characteristics.append("Contains geographic data")
            
            # Check for financial data
            financial_indicators = ['price', 'cost', 'revenue', 'amount', 'value', 'money', 'dollar']
            financial_columns = [col for col in df.columns if any(indicator in col.lower() for indicator in financial_indicators)]
            if financial_columns:
                characteristics.append("Contains financial data")
            
            return characteristics
            
        except Exception as e:
            self.logger.error(f"Error identifying content characteristics: {e}")
            return []
    
    async def _generate_parsing_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate parsing metadata."""
        try:
            return {
                "parsing_timestamp": pd.Timestamp.now().isoformat(),
                "data_shape": df.shape,
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "parsing_version": "1.0.0",
                "parser_type": "structured_content_parser"
            }
        except Exception as e:
            self.logger.error(f"Error generating parsing metadata: {e}")
            return {"error": str(e)}

