#!/usr/bin/env python3
"""EDA Analysis module for Data Analyzer Service."""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats


class EDAAnalysis:
    """EDA Analysis module for Data Analyzer Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
        self.utilities = service_instance.utilities_module
    
    def extract_schema_from_embeddings(
        self,
        embeddings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract schema information from semantic embeddings.
        
        Schema embeddings contain:
        - column_name
        - data_type
        - sample_values (from representative sampling)
        - metadata (statistics, constraints, etc.)
        
        Args:
            embeddings: List of embedding dictionaries
            
        Returns:
            Schema information dictionary:
            {
                "columns": List[str],
                "data_types": Dict[str, str],
                "sample_values": Dict[str, List],
                "metadata": Dict[str, Dict]
            }
        """
        schema = {
            "columns": [],
            "data_types": {},
            "sample_values": {},
            "metadata": {}
        }
        
        for emb in embeddings:
            column_name = emb.get("column_name") or emb.get("column") or emb.get("field_name")
            if not column_name:
                continue
            
            schema["columns"].append(column_name)
            
            # Normalize data type
            data_type = self.utilities.normalize_data_type(emb.get("data_type", "unknown"))
            schema["data_types"][column_name] = data_type
            
            # Extract sample values
            sample_values = emb.get("sample_values") or emb.get("samples") or emb.get("values", [])
            schema["sample_values"][column_name] = sample_values if isinstance(sample_values, list) else []
            
            # Extract metadata
            metadata = emb.get("metadata") or emb.get("stats") or {}
            schema["metadata"][column_name] = metadata if isinstance(metadata, dict) else {}
        
        return schema
    
    async def calculate_statistics(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate descriptive statistics from schema embeddings.
        
        Uses metadata from embeddings (which includes statistics from representative sampling).
        For numerical columns, calculates mean, median, std, min, max, count, null_count.
        For categorical columns, calculates unique_count, most_common, count, null_count.
        
        Args:
            schema_info: Schema information dictionary
            
        Returns:
            Statistics dictionary keyed by column name
        """
        statistics = {}
        
        for column_name in schema_info["columns"]:
            metadata = schema_info["metadata"].get(column_name, {})
            data_type = schema_info["data_types"].get(column_name, "unknown")
            
            # Normalize data type
            normalized_type = self.utilities.normalize_data_type(data_type)
            
            if normalized_type in ["int", "float", "number"]:
                # Numerical statistics
                statistics[column_name] = {
                    "type": "numerical",
                    "mean": metadata.get("mean"),
                    "median": metadata.get("median"),
                    "std": metadata.get("std") or metadata.get("standard_deviation"),
                    "min": metadata.get("min") or metadata.get("minimum"),
                    "max": metadata.get("max") or metadata.get("maximum"),
                    "count": metadata.get("count") or metadata.get("total_count", 0),
                    "null_count": metadata.get("null_count") or metadata.get("missing_count", 0)
                }
            elif normalized_type in ["string", "text", "object"]:
                # Categorical statistics
                statistics[column_name] = {
                    "type": "categorical",
                    "unique_count": metadata.get("unique_count") or metadata.get("nunique"),
                    "most_common": metadata.get("most_common") or metadata.get("top_values", []),
                    "count": metadata.get("count") or metadata.get("total_count", 0),
                    "null_count": metadata.get("null_count") or metadata.get("missing_count", 0)
                }
            else:
                # Unknown type - basic stats only
                statistics[column_name] = {
                    "type": "unknown",
                    "count": metadata.get("count") or metadata.get("total_count", 0),
                    "null_count": metadata.get("null_count") or metadata.get("missing_count", 0)
                }
        
        return statistics
    
    async def calculate_correlations(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate correlations between numerical columns.
        
        Uses correlation metadata from embeddings if available.
        If correlation metadata is not available, attempts to calculate from sample values.
        
        Args:
            schema_info: Schema information dictionary
            
        Returns:
            Correlation analysis dictionary:
            {
                "numerical_columns": List[str],
                "correlation_matrix": Dict[str, Dict[str, float]]
            }
        """
        # Find numerical columns
        numerical_columns = [
            col for col in schema_info["columns"]
            if self.utilities.normalize_data_type(schema_info["data_types"].get(col, "unknown")) in ["int", "float", "number"]
        ]
        
        if len(numerical_columns) < 2:
            return {
                "message": "Insufficient numerical columns for correlation analysis",
                "numerical_columns": numerical_columns,
                "correlation_matrix": {}
            }
        
        # Extract correlation metadata from embeddings
        correlations = {}
        
        for col1 in numerical_columns:
            metadata1 = schema_info["metadata"].get(col1, {})
            correlations[col1] = {}
            
            for col2 in numerical_columns:
                if col1 == col2:
                    correlations[col1][col2] = 1.0
                else:
                    # Try to get correlation from metadata
                    correlation_metadata = metadata1.get("correlations", {})
                    correlation_value = correlation_metadata.get(col2)
                    
                    if correlation_value is not None:
                        correlations[col1][col2] = float(correlation_value)
                    else:
                        # Try to calculate from sample values if available
                        sample1 = schema_info["sample_values"].get(col1, [])
                        sample2 = schema_info["sample_values"].get(col2, [])
                        
                        if len(sample1) == len(sample2) and len(sample1) >= 2:
                            try:
                                # Convert to numeric arrays
                                arr1 = pd.to_numeric(sample1, errors='coerce')
                                arr2 = pd.to_numeric(sample2, errors='coerce')
                                
                                # Remove NaN values
                                mask = ~(np.isnan(arr1) | np.isnan(arr2))
                                if mask.sum() >= 2:
                                    corr = np.corrcoef(arr1[mask], arr2[mask])[0, 1]
                                    correlations[col1][col2] = float(corr) if not np.isnan(corr) else 0.0
                                else:
                                    correlations[col1][col2] = 0.0
                            except Exception:
                                correlations[col1][col2] = 0.0
                        else:
                            correlations[col1][col2] = 0.0
        
        return {
            "numerical_columns": numerical_columns,
            "correlation_matrix": correlations
        }
    
    async def calculate_distributions(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate distribution information from schema embeddings.
        
        Uses sample values and metadata from embeddings.
        For numerical columns: skewness, kurtosis, quartiles (q1, q2, q3).
        For categorical columns: value_counts.
        
        Args:
            schema_info: Schema information dictionary
            
        Returns:
            Distribution information dictionary keyed by column name
        """
        distributions = {}
        
        for column_name in schema_info["columns"]:
            metadata = schema_info["metadata"].get(column_name, {})
            data_type = schema_info["data_types"].get(column_name, "unknown")
            sample_values = schema_info["sample_values"].get(column_name, [])
            
            # Normalize data type
            normalized_type = self.utilities.normalize_data_type(data_type)
            
            if normalized_type in ["int", "float", "number"]:
                # Numerical distribution
                distribution_info = {
                    "type": "numerical",
                    "skewness": metadata.get("skewness"),
                    "kurtosis": metadata.get("kurtosis"),
                    "quartiles": {
                        "q1": metadata.get("q1") or metadata.get("quartile_1"),
                        "q2": metadata.get("q2") or metadata.get("median") or metadata.get("quartile_2"),
                        "q3": metadata.get("q3") or metadata.get("quartile_3")
                    },
                    "sample_values": sample_values[:10]  # First 10 samples
                }
                
                # Try to calculate from sample values if metadata not available
                if distribution_info["skewness"] is None and len(sample_values) >= 3:
                    try:
                        arr = pd.to_numeric(sample_values, errors='coerce')
                        arr = arr[~np.isnan(arr)]
                        if len(arr) >= 3:
                            distribution_info["skewness"] = float(stats.skew(arr))
                            distribution_info["kurtosis"] = float(stats.kurtosis(arr))
                    except Exception:
                        pass
                
                distributions[column_name] = distribution_info
                
            elif normalized_type in ["string", "text", "object"]:
                # Categorical distribution
                distributions[column_name] = {
                    "type": "categorical",
                    "value_counts": metadata.get("value_counts", {}),
                    "sample_values": sample_values[:10]
                }
            else:
                distributions[column_name] = {
                    "type": "unknown",
                    "sample_values": sample_values[:10]
                }
        
        return distributions
    
    async def analyze_missing_values(
        self,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze missing values from schema embeddings.
        
        Uses metadata from embeddings to calculate:
        - total_count
        - null_count
        - missing_percentage
        - has_missing (boolean)
        
        Args:
            schema_info: Schema information dictionary
            
        Returns:
            Missing value analysis dictionary keyed by column name
        """
        missing_analysis = {}
        
        for column_name in schema_info["columns"]:
            metadata = schema_info["metadata"].get(column_name, {})
            
            total_count = metadata.get("count") or metadata.get("total_count", 0)
            null_count = metadata.get("null_count") or metadata.get("missing_count", 0)
            missing_percentage = (null_count / total_count * 100) if total_count > 0 else 0
            
            missing_analysis[column_name] = {
                "total_count": total_count,
                "null_count": null_count,
                "missing_percentage": round(missing_percentage, 2),
                "has_missing": null_count > 0
            }
        
        return missing_analysis


