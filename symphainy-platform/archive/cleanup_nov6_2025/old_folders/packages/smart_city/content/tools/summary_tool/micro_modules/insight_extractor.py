"""
Insight Extractor Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class InsightExtractor:
    """
    Insight extraction following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("InsightExtractor micro-module initialized")
    
    async def extract_insights(self, df: pd.DataFrame, summary_type: str) -> List[str]:
        """
        Extract key insights from data.
        
        Args:
            df: DataFrame to analyze
            summary_type: Type of summary being generated
            
        Returns:
            List of key insights
        """
        try:
            insights = []
            
            # Basic data insights
            insights.extend(await self._extract_basic_insights(df))
            
            # Statistical insights
            insights.extend(await self._extract_statistical_insights(df))
            
            # Pattern insights
            insights.extend(await self._extract_pattern_insights(df))
            
            # Quality insights
            insights.extend(await self._extract_quality_insights(df))
            
            # Limit to top insights
            return insights[:8]
            
        except Exception as e:
            self.logger.error(f"Error extracting insights: {e}")
            return ["Error extracting insights from data"]
    
    async def extract_highlights(self, df: pd.DataFrame) -> List[str]:
        """
        Extract data highlights.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of data highlights
        """
        try:
            highlights = []
            
            # Size highlights
            if len(df) > 10000:
                highlights.append(f"Large dataset with {len(df):,} records")
            elif len(df) > 1000:
                highlights.append(f"Substantial dataset with {len(df):,} records")
            else:
                highlights.append(f"Dataset with {len(df)} records")
            
            # Column highlights
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                highlights.append(f"{len(numeric_cols)} numeric columns for quantitative analysis")
            
            if len(categorical_cols) > 0:
                highlights.append(f"{len(categorical_cols)} categorical columns for grouping")
            
            # Data quality highlights
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_percentage < 5:
                highlights.append("Excellent data completeness")
            elif missing_percentage < 20:
                highlights.append("Good data completeness")
            else:
                highlights.append("Data completeness needs attention")
            
            # Unique value highlights
            if len(categorical_cols) > 0:
                col = categorical_cols[0]
                unique_count = df[col].nunique()
                total_count = len(df)
                uniqueness_ratio = unique_count / total_count
                
                if uniqueness_ratio > 0.9:
                    highlights.append(f"High uniqueness in '{col}' ({unique_count}/{total_count})")
                elif uniqueness_ratio < 0.1:
                    highlights.append(f"Low uniqueness in '{col}' ({unique_count}/{total_count})")
            
            return highlights[:5]  # Limit to 5 highlights
            
        except Exception as e:
            self.logger.error(f"Error extracting highlights: {e}")
            return ["Error extracting data highlights"]
    
    async def _extract_basic_insights(self, df: pd.DataFrame) -> List[str]:
        """Extract basic data insights."""
        try:
            insights = []
            
            # Dataset size insights
            if len(df) > 50000:
                insights.append("Very large dataset - consider sampling for analysis")
            elif len(df) > 10000:
                insights.append("Large dataset suitable for comprehensive analysis")
            elif len(df) > 1000:
                insights.append("Medium-sized dataset good for detailed analysis")
            else:
                insights.append("Small dataset - consider collecting more data")
            
            # Column insights
            if len(df.columns) > 20:
                insights.append("High-dimensional data with many features")
            elif len(df.columns) > 10:
                insights.append("Multi-dimensional dataset with several features")
            else:
                insights.append("Focused dataset with key features")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting basic insights: {e}")
            return []
    
    async def _extract_statistical_insights(self, df: pd.DataFrame) -> List[str]:
        """Extract statistical insights."""
        try:
            insights = []
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                return ["No numeric columns for statistical analysis"]
            
            # Analyze first numeric column
            col = numeric_cols[0]
            values = df[col].dropna()
            
            if len(values) > 0:
                mean_val = values.mean()
                std_val = values.std()
                skewness = values.skew()
                
                # Distribution insights
                if abs(skewness) > 1:
                    insights.append(f"Highly skewed distribution in '{col}' (skewness: {skewness:.2f})")
                elif abs(skewness) > 0.5:
                    insights.append(f"Moderately skewed distribution in '{col}' (skewness: {skewness:.2f})")
                else:
                    insights.append(f"Approximately normal distribution in '{col}'")
                
                # Variability insights
                cv = std_val / mean_val if mean_val != 0 else 0
                if cv > 1:
                    insights.append(f"High variability in '{col}' (CV: {cv:.2f})")
                elif cv < 0.1:
                    insights.append(f"Low variability in '{col}' (CV: {cv:.2f})")
                else:
                    insights.append(f"Moderate variability in '{col}' (CV: {cv:.2f})")
            
            # Correlation insights
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                strong_correlations = []
                
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            col1 = corr_matrix.columns[i]
                            col2 = corr_matrix.columns[j]
                            strong_correlations.append(f"'{col1}' and '{col2}' ({corr_val:.2f})")
                
                if strong_correlations:
                    insights.append(f"Strong correlations found: {', '.join(strong_correlations[:2])}")
                else:
                    insights.append("No strong correlations detected between numeric columns")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting statistical insights: {e}")
            return []
    
    async def _extract_pattern_insights(self, df: pd.DataFrame) -> List[str]:
        """Extract pattern insights."""
        try:
            insights = []
            
            # Missing value patterns
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                high_missing = missing_data[missing_data > len(df) * 0.1]
                if not high_missing.empty:
                    insights.append(f"High missing values in columns: {list(high_missing.index)}")
                
                # Check for systematic missing patterns
                if len(high_missing) > 1:
                    insights.append("Systematic missing data pattern detected")
            
            # Duplicate patterns
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                duplicate_percentage = (duplicate_count / len(df)) * 100
                if duplicate_percentage > 10:
                    insights.append(f"High duplicate rate: {duplicate_percentage:.1f}% of records")
                else:
                    insights.append(f"Some duplicate records found: {duplicate_count}")
            
            # Outlier patterns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outlier_columns = []
            
            for col in numeric_cols:
                values = df[col].dropna()
                if len(values) > 0:
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = values[(values < Q1 - 1.5 * IQR) | (values > Q3 + 1.5 * IQR)]
                    
                    if len(outliers) > len(values) * 0.05:  # More than 5% outliers
                        outlier_columns.append(col)
            
            if outlier_columns:
                insights.append(f"Outlier patterns detected in: {', '.join(outlier_columns)}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting pattern insights: {e}")
            return []
    
    async def _extract_quality_insights(self, df: pd.DataFrame) -> List[str]:
        """Extract data quality insights."""
        try:
            insights = []
            
            # Completeness insights
            total_cells = len(df) * len(df.columns)
            missing_cells = df.isnull().sum().sum()
            completeness = ((total_cells - missing_cells) / total_cells) * 100
            
            if completeness >= 95:
                insights.append("Excellent data completeness")
            elif completeness >= 80:
                insights.append("Good data completeness with minor gaps")
            elif completeness >= 60:
                insights.append("Moderate data completeness - some missing values")
            else:
                insights.append("Poor data completeness - significant missing values")
            
            # Consistency insights
            categorical_cols = df.select_dtypes(include=['object']).columns
            inconsistent_columns = []
            
            for col in categorical_cols:
                # Check for mixed data types
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    # Check if all values can be converted to the same type
                    try:
                        pd.to_numeric(non_null_values, errors='raise')
                        # All numeric - check if stored as text
                        if df[col].dtype == 'object':
                            inconsistent_columns.append(f"'{col}' (numeric data stored as text)")
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
                            inconsistent_columns.append(f"'{col}' (mixed data types)")
            
            if inconsistent_columns:
                insights.append(f"Data type inconsistencies: {', '.join(inconsistent_columns[:2])}")
            
            # Uniqueness insights
            if len(df.columns) > 0:
                unique_rows = len(df.drop_duplicates())
                uniqueness_ratio = unique_rows / len(df)
                
                if uniqueness_ratio < 0.9:
                    insights.append("Low row uniqueness - many duplicate records")
                elif uniqueness_ratio == 1.0:
                    insights.append("Perfect row uniqueness - no duplicates")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting quality insights: {e}")
            return []

