"""
Content Summarizer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class ContentSummarizer:
    """
    Content summarization following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("ContentSummarizer micro-module initialized")
    
    async def generate_summary(self, df: pd.DataFrame, summary_type: str, context: str) -> str:
        """
        Generate content summary based on data and type.
        
        Args:
            df: DataFrame to summarize
            summary_type: Type of summary to generate
            context: Additional context
            
        Returns:
            Generated summary string
        """
        try:
            if df.empty:
                return "No data available for summarization."
            
            # Generate summary based on type
            if summary_type == "comprehensive":
                return await self._generate_comprehensive_summary(df, context)
            elif summary_type == "executive":
                return await self._generate_executive_summary(df, context)
            elif summary_type == "technical":
                return await self._generate_technical_summary(df, context)
            elif summary_type == "brief":
                return await self._generate_brief_summary(df, context)
            else:
                return await self._generate_default_summary(df, context)
            
        except Exception as e:
            self.logger.error(f"Error generating content summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def generate_recommendations(self, df: pd.DataFrame, insights: List[str]) -> List[str]:
        """
        Generate recommendations based on data and insights.
        
        Args:
            df: DataFrame analyzed
            insights: Generated insights
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Data quality recommendations
            if df.isnull().sum().sum() > 0:
                recommendations.append("Address missing values to improve data quality")
            
            if df.duplicated().sum() > 0:
                recommendations.append("Remove duplicate records for cleaner analysis")
            
            # Size-based recommendations
            if len(df) < 100:
                recommendations.append("Consider collecting more data for robust analysis")
            elif len(df) > 10000:
                recommendations.append("Consider data sampling for better performance")
            
            # Column-based recommendations
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                recommendations.append("Perform statistical analysis on numeric columns")
            
            if len(categorical_cols) > 0:
                recommendations.append("Analyze categorical patterns and distributions")
            
            # Insight-based recommendations
            for insight in insights:
                if "trend" in insight.lower():
                    recommendations.append("Investigate trend patterns and their causes")
                elif "outlier" in insight.lower():
                    recommendations.append("Examine outliers for data quality issues")
                elif "correlation" in insight.lower():
                    recommendations.append("Explore relationships between variables")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Review data quality and analysis requirements"]
    
    async def _generate_comprehensive_summary(self, df: pd.DataFrame, context: str) -> str:
        """Generate comprehensive summary."""
        try:
            summary_parts = []
            
            # Basic information
            summary_parts.append(f"This dataset contains {len(df)} rows and {len(df.columns)} columns.")
            
            # Data types
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                summary_parts.append(f"It includes {len(numeric_cols)} numeric columns suitable for quantitative analysis.")
            
            if len(categorical_cols) > 0:
                summary_parts.append(f"It contains {len(categorical_cols)} categorical columns for grouping and classification.")
            
            # Data quality
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / (len(df) * len(df.columns))) * 100
                summary_parts.append(f"Data quality: {missing_percentage:.1f}% of values are missing.")
            else:
                summary_parts.append("Data quality: No missing values detected.")
            
            # Key statistics for numeric columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                values = df[col].dropna()
                if len(values) > 0:
                    summary_parts.append(f"Key statistics for '{col}': mean={values.mean():.2f}, std={values.std():.2f}, range=[{values.min():.2f}, {values.max():.2f}].")
            
            # Context-specific information
            if context:
                summary_parts.append(f"Context: {context}")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive summary: {e}")
            return "Error generating comprehensive summary."
    
    async def _generate_executive_summary(self, df: pd.DataFrame, context: str) -> str:
        """Generate executive summary."""
        try:
            summary_parts = []
            
            # High-level overview
            summary_parts.append(f"Dataset Overview: {len(df)} records across {len(df.columns)} data fields.")
            
            # Key metrics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary_parts.append(f"Quantitative data available in {len(numeric_cols)} fields.")
            
            # Data quality status
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_percentage < 5:
                summary_parts.append("Data quality is excellent with minimal missing values.")
            elif missing_percentage < 20:
                summary_parts.append("Data quality is good with some missing values requiring attention.")
            else:
                summary_parts.append("Data quality needs improvement due to significant missing values.")
            
            # Business value
            if context and "business" in context.lower():
                summary_parts.append("This dataset is suitable for business intelligence and decision-making.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            return "Error generating executive summary."
    
    async def _generate_technical_summary(self, df: pd.DataFrame, context: str) -> str:
        """Generate technical summary."""
        try:
            summary_parts = []
            
            # Technical specifications
            summary_parts.append(f"Technical Specifications: {len(df)} rows × {len(df.columns)} columns.")
            summary_parts.append(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB.")
            
            # Data types breakdown
            dtype_counts = df.dtypes.value_counts()
            for dtype, count in dtype_counts.items():
                summary_parts.append(f"{count} columns of type {dtype}.")
            
            # Missing data analysis
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                summary_parts.append("Missing data analysis:")
                for col, missing_count in missing_data[missing_data > 0].items():
                    percentage = (missing_count / len(df)) * 100
                    summary_parts.append(f"  {col}: {missing_count} missing ({percentage:.1f}%)")
            
            # Duplicate analysis
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                summary_parts.append(f"Duplicate records: {duplicate_count} ({duplicate_count/len(df)*100:.1f}%)")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating technical summary: {e}")
            return "Error generating technical summary."
    
    async def _generate_brief_summary(self, df: pd.DataFrame, context: str) -> str:
        """Generate brief summary."""
        try:
            summary_parts = []
            
            # Essential information only
            summary_parts.append(f"Dataset: {len(df)} rows, {len(df.columns)} columns.")
            
            # Data quality status
            missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_percentage < 10:
                summary_parts.append("Good data quality.")
            else:
                summary_parts.append("Data quality issues present.")
            
            # Key insight
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary_parts.append(f"Contains {len(numeric_cols)} numeric fields for analysis.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating brief summary: {e}")
            return "Error generating brief summary."
    
    async def _generate_default_summary(self, df: pd.DataFrame, context: str) -> str:
        """Generate default summary."""
        return await self._generate_comprehensive_summary(df, context)

