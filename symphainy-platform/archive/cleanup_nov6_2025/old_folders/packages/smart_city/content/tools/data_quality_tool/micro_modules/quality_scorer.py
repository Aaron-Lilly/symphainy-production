"""
Quality Scorer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


class QualityScorer:
    """
    Data quality scoring following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("QualityScorer micro-module initialized")
    
    async def calculate_score(self, df: pd.DataFrame, structural_results: Dict[str, Any]) -> float:
        """
        Calculate overall quality score based on structural analysis.
        
        Args:
            df: DataFrame to score
            structural_results: Results from structural checks
            
        Returns:
            Quality score (0-100)
        """
        try:
            # Start with perfect score
            score = 100.0
            
            # Deduct points for issues
            score = await self._deduct_for_issues(score, structural_results)
            
            # Deduct points for missing values
            score = await self._deduct_for_missing_values(score, df)
            
            # Deduct points for duplicates
            score = await self._deduct_for_duplicates(score, df)
            
            # Deduct points for data type issues
            score = await self._deduct_for_data_types(score, df)
            
            # Ensure score is between 0 and 100
            score = max(0.0, min(100.0, score))
            
            self.logger.info(f"Quality score calculated: {score:.1f}")
            return round(score, 1)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    async def _deduct_for_issues(self, score: float, structural_results: Dict[str, Any]) -> float:
        """Deduct points based on number of issues."""
        try:
            issue_count = len(structural_results.get("issues", []))
            alert_count = len(structural_results.get("alerts", []))
            
            # Deduct points for issues
            if issue_count > 0:
                # More severe deduction for more issues
                if issue_count >= 10:
                    score -= 30  # Many issues
                elif issue_count >= 5:
                    score -= 20  # Several issues
                elif issue_count >= 3:
                    score -= 15  # Some issues
                else:
                    score -= 10  # Few issues
            
            # Deduct additional points for alerts
            if alert_count > 0:
                score -= alert_count * 5  # 5 points per alert
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error deducting for issues: {e}")
            return score
    
    async def _deduct_for_missing_values(self, score: float, df: pd.DataFrame) -> float:
        """Deduct points for missing values."""
        try:
            null_counts = df.isnull().sum()
            total_rows = len(df)
            
            for column, null_count in null_counts.items():
                if null_count > 0:
                    percentage = (null_count / total_rows) * 100
                    
                    # More severe deduction for higher missing percentages
                    if percentage >= 50:
                        score -= 25  # Critical missing data
                    elif percentage >= 25:
                        score -= 15  # High missing data
                    elif percentage >= 10:
                        score -= 10  # Moderate missing data
                    else:
                        score -= 5   # Low missing data
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error deducting for missing values: {e}")
            return score
    
    async def _deduct_for_duplicates(self, score: float, df: pd.DataFrame) -> float:
        """Deduct points for duplicate rows."""
        try:
            duplicate_count = df.duplicated().sum()
            total_rows = len(df)
            
            if duplicate_count > 0:
                percentage = (duplicate_count / total_rows) * 100
                
                # More severe deduction for higher duplicate percentages
                if percentage >= 20:
                    score -= 20  # High duplicate rate
                elif percentage >= 10:
                    score -= 15  # Moderate duplicate rate
                elif percentage >= 5:
                    score -= 10  # Low duplicate rate
                else:
                    score -= 5   # Very low duplicate rate
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error deducting for duplicates: {e}")
            return score
    
    async def _deduct_for_data_types(self, score: float, df: pd.DataFrame) -> float:
        """Deduct points for data type issues."""
        try:
            type_issues = 0
            
            for column in df.columns:
                dtype = df[column].dtype
                
                # Check for object columns that might be numeric
                if dtype == 'object':
                    non_null_values = df[column].dropna()
                    if len(non_null_values) > 0:
                        try:
                            # Try to convert to numeric
                            pd.to_numeric(non_null_values, errors='raise')
                            type_issues += 1  # Numeric data stored as text
                        except (ValueError, TypeError):
                            # Check for mixed types
                            numeric_count = 0
                            for value in non_null_values:
                                try:
                                    pd.to_numeric(value, errors='raise')
                                    numeric_count += 1
                                except (ValueError, TypeError):
                                    pass
                            
                            if 0 < numeric_count < len(non_null_values):
                                type_issues += 1  # Mixed data types
            
            # Deduct points for type issues
            if type_issues > 0:
                score -= min(type_issues * 5, 20)  # Max 20 points deduction
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error deducting for data types: {e}")
            return score

