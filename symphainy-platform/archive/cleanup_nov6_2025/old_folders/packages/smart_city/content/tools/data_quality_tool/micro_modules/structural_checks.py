"""
Structural Checks Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class StructuralChecker:
    """
    Structural data quality checks following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("StructuralChecker micro-module initialized")
    
    async def perform_checks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform structural quality checks on DataFrame.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary with structural analysis results
        """
        try:
            results = {
                "issues": [],
                "alerts": [],
                "metrics": {},
                "summary": {}
            }
            
            # Basic structural metrics
            results["metrics"] = await self._calculate_basic_metrics(df)
            
            # Check for missing values
            missing_issues = await self._check_missing_values(df)
            results["issues"].extend(missing_issues)
            
            # Check for duplicates
            duplicate_issues = await self._check_duplicates(df)
            results["issues"].extend(duplicate_issues)
            
            # Check data types
            type_issues = await self._check_data_types(df)
            results["issues"].extend(type_issues)
            
            # Generate summary
            results["summary"] = await self._generate_summary(results)
            
            self.logger.info(f"Structural checks completed: {len(results['issues'])} issues found")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in structural checks: {e}")
            return {
                "issues": [f"Structural check failed: {str(e)}"],
                "alerts": ["Critical error in structural analysis"],
                "metrics": {},
                "summary": {"status": "error"}
            }
    
    async def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic structural metrics."""
        try:
            return {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "null_count": df.isnull().sum().sum(),
                "duplicate_rows": df.duplicated().sum(),
                "empty_rows": df.isnull().all(axis=1).sum()
            }
        except Exception as e:
            self.logger.error(f"Error calculating basic metrics: {e}")
            return {}
    
    async def _check_missing_values(self, df: pd.DataFrame) -> List[str]:
        """Check for missing values and generate issues."""
        issues = []
        
        try:
            null_counts = df.isnull().sum()
            total_rows = len(df)
            
            for column, null_count in null_counts.items():
                if null_count > 0:
                    percentage = (null_count / total_rows) * 100
                    if percentage > 50:
                        issues.append(f"Column '{column}' has {percentage:.1f}% missing values (critical)")
                    elif percentage > 20:
                        issues.append(f"Column '{column}' has {percentage:.1f}% missing values (warning)")
                    else:
                        issues.append(f"Column '{column}' has {null_count} missing values")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Error checking missing values: {e}")
            return [f"Error checking missing values: {str(e)}"]
    
    async def _check_duplicates(self, df: pd.DataFrame) -> List[str]:
        """Check for duplicate rows and generate issues."""
        issues = []
        
        try:
            duplicate_count = df.duplicated().sum()
            total_rows = len(df)
            
            if duplicate_count > 0:
                percentage = (duplicate_count / total_rows) * 100
                if percentage > 10:
                    issues.append(f"{duplicate_count} duplicate rows found ({percentage:.1f}% of data)")
                else:
                    issues.append(f"{duplicate_count} duplicate rows found")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Error checking duplicates: {e}")
            return [f"Error checking duplicates: {str(e)}"]
    
    async def _check_data_types(self, df: pd.DataFrame) -> List[str]:
        """Check data types and generate issues."""
        issues = []
        
        try:
            for column in df.columns:
                dtype = df[column].dtype
                
                # Check for mixed types
                if dtype == 'object':
                    # Check if column contains mixed types
                    non_null_values = df[column].dropna()
                    if len(non_null_values) > 0:
                        # Check if all values can be converted to the same type
                        try:
                            pd.to_numeric(non_null_values, errors='raise')
                            # All values are numeric, but stored as object
                            issues.append(f"Column '{column}' contains numeric data stored as text")
                        except (ValueError, TypeError):
                            # Check for mixed numeric and text
                            numeric_count = 0
                            for value in non_null_values:
                                try:
                                    pd.to_numeric(value, errors='raise')
                                    numeric_count += 1
                                except (ValueError, TypeError):
                                    pass
                            
                            if 0 < numeric_count < len(non_null_values):
                                issues.append(f"Column '{column}' contains mixed data types")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Error checking data types: {e}")
            return [f"Error checking data types: {str(e)}"]
    
    async def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of structural analysis."""
        try:
            issue_count = len(results["issues"])
            alert_count = len(results["alerts"])
            
            if issue_count == 0 and alert_count == 0:
                status = "excellent"
                message = "No structural issues found"
            elif issue_count <= 3 and alert_count == 0:
                status = "good"
                message = f"Minor structural issues found ({issue_count})"
            elif issue_count <= 10:
                status = "warning"
                message = f"Several structural issues found ({issue_count})"
            else:
                status = "critical"
                message = f"Many structural issues found ({issue_count})"
            
            return {
                "status": status,
                "message": message,
                "issue_count": issue_count,
                "alert_count": alert_count
            }
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return {
                "status": "error",
                "message": f"Error generating summary: {str(e)}",
                "issue_count": 0,
                "alert_count": 1
            }

