"""
Data Validator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class DataValidator:
    """
    Data validation for structured content following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("DataValidator micro-module initialized")
    
    async def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate structured data and return validation results.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            results = {
                "valid": True,
                "warnings": [],
                "errors": [],
                "metrics": {},
                "recommendations": []
            }
            
            # Basic validation checks
            await self._check_data_integrity(df, results)
            await self._check_data_consistency(df, results)
            await self._check_data_completeness(df, results)
            
            # Calculate validation metrics
            results["metrics"] = await self._calculate_validation_metrics(df)
            
            # Generate recommendations
            results["recommendations"] = await self._generate_recommendations(results)
            
            # Determine overall validity
            results["valid"] = len(results["errors"]) == 0
            
            self.logger.info(f"Data validation completed: {len(results['errors'])} errors, {len(results['warnings'])} warnings")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in data validation: {e}")
            return {
                "valid": False,
                "warnings": [],
                "errors": [f"Validation failed: {str(e)}"],
                "metrics": {},
                "recommendations": ["Please check your data and try again"]
            }
    
    async def _check_data_integrity(self, df: pd.DataFrame, results: Dict[str, Any]):
        """Check data integrity issues."""
        try:
            # Check for completely empty columns
            empty_columns = df.columns[df.isnull().all()].tolist()
            if empty_columns:
                results["errors"].append(f"Empty columns detected: {', '.join(empty_columns)}")
            
            # Check for completely empty rows
            empty_rows = df.isnull().all(axis=1).sum()
            if empty_rows > 0:
                results["warnings"].append(f"{empty_rows} completely empty rows found")
            
        except Exception as e:
            self.logger.error(f"Error checking data integrity: {e}")
            results["errors"].append(f"Data integrity check failed: {str(e)}")
    
    async def _check_data_consistency(self, df: pd.DataFrame, results: Dict[str, Any]):
        """Check data consistency issues."""
        try:
            # Check for mixed data types in object columns
            for column in df.select_dtypes(include=['object']).columns:
                non_null_values = df[column].dropna()
                if len(non_null_values) > 0:
                    # Check if column contains mixed types
                    numeric_count = 0
                    for value in non_null_values:
                        try:
                            pd.to_numeric(value, errors='raise')
                            numeric_count += 1
                        except (ValueError, TypeError):
                            pass
                    
                    if 0 < numeric_count < len(non_null_values):
                        results["warnings"].append(f"Column '{column}' contains mixed data types")
            
        except Exception as e:
            self.logger.error(f"Error checking data consistency: {e}")
            results["warnings"].append(f"Data consistency check failed: {str(e)}")
    
    async def _check_data_completeness(self, df: pd.DataFrame, results: Dict[str, Any]):
        """Check data completeness issues."""
        try:
            # Check for missing values
            null_counts = df.isnull().sum()
            total_rows = len(df)
            
            for column, null_count in null_counts.items():
                if null_count > 0:
                    percentage = (null_count / total_rows) * 100
                    if percentage > 50:
                        results["errors"].append(f"Column '{column}' has {percentage:.1f}% missing values")
                    elif percentage > 20:
                        results["warnings"].append(f"Column '{column}' has {percentage:.1f}% missing values")
            
            # Check for duplicate rows
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                duplicate_percentage = (duplicate_count / total_rows) * 100
                if duplicate_percentage > 10:
                    results["warnings"].append(f"High duplicate rate: {duplicate_percentage:.1f}% of rows are duplicates")
                else:
                    results["warnings"].append(f"{duplicate_count} duplicate rows found")
            
        except Exception as e:
            self.logger.error(f"Error checking data completeness: {e}")
            results["warnings"].append(f"Data completeness check failed: {str(e)}")
    
    async def _calculate_validation_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate validation metrics."""
        try:
            total_cells = len(df) * len(df.columns)
            null_cells = df.isnull().sum().sum()
            duplicate_rows = df.duplicated().sum()
            
            return {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "total_cells": total_cells,
                "null_cells": null_cells,
                "null_percentage": (null_cells / total_cells) * 100 if total_cells > 0 else 0,
                "duplicate_rows": duplicate_rows,
                "duplicate_percentage": (duplicate_rows / len(df)) * 100 if len(df) > 0 else 0,
                "empty_columns": df.isnull().all().sum(),
                "empty_rows": df.isnull().all(axis=1).sum()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating validation metrics: {e}")
            return {}
    
    async def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        try:
            # Recommendations based on errors
            if results["errors"]:
                recommendations.append("Address critical data issues before proceeding with analysis")
            
            # Recommendations based on warnings
            if any("missing" in warning.lower() for warning in results["warnings"]):
                recommendations.append("Consider data imputation for missing values")
            
            if any("duplicate" in warning.lower() for warning in results["warnings"]):
                recommendations.append("Review and remove duplicate records")
            
            if any("mixed" in warning.lower() for warning in results["warnings"]):
                recommendations.append("Standardize data types and formats")
            
            # Default recommendation if no specific issues
            if not recommendations and not results["errors"]:
                recommendations.append("Data validation completed successfully")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Please review data quality and implement appropriate solutions"]

