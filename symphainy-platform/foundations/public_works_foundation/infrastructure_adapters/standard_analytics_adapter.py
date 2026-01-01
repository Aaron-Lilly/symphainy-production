"""
Standard Analytics Adapter - Non-swappable infrastructure using standard packages
Provides standard data analysis capabilities using pandas, numpy, matplotlib, etc.
These are passed directly via DI Container as they're unlikely to be swapped.
"""

from typing import Dict, Any, List, Optional, Union
import logging
from dataclasses import dataclass
from datetime import datetime
import json

# Standard packages (DI Container)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

from ..abstraction_contracts.data_analysis_protocol import DataAnalysisProtocol
from ..abstraction_contracts.visualization_protocol import VisualizationProtocol

logger = logging.getLogger(__name__)

@dataclass
class StandardAnalyticsConfig:
    """Configuration for standard analytics operations."""
    default_figure_size: tuple = (10, 6)
    color_palette: str = "viridis"
    correlation_threshold: float = 0.7
    outlier_threshold: float = 3.0  # Standard deviations

class StandardAnalyticsAdapter:
    """
    Standard Analytics Adapter - Non-swappable infrastructure using standard packages.
    Provides standard data analysis capabilities using pandas, numpy, matplotlib, etc.
    """
    
    def __init__(self, config: StandardAnalyticsConfig = None):
        """
        Initialize Standard Analytics Adapter.
        
        Args:
            config: Configuration for analytics operations
        """
        self.config = config or StandardAnalyticsConfig()
        self.initialized = False
        
        # Set matplotlib style
        plt.style.use('default')
        sns.set_palette(self.config.color_palette)
        
        logger.info("Standard Analytics Adapter initialized")
    
    async def initialize(self) -> bool:
        """Initialize standard analytics adapter."""
        try:
            # Test imports
            _ = pd.DataFrame()
            _ = np.array([1, 2, 3])
            _ = plt.figure()
            
            self.initialized = True
            logger.info("Standard Analytics Adapter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Standard Analytics Adapter: {e}")
            return False
    
    async def analyze_dataframe(self, df: pd.DataFrame, analysis_type: str = "basic", user_context: Any = None) -> Dict[str, Any]:
        """
        Analyze DataFrame using standard pandas operations.
        
        Args:
            df: DataFrame to analyze
            analysis_type: Type of analysis to perform
            user_context: User context for analysis
            
        Returns:
            Analysis results
        """
        try:
            results = {
                "basic_stats": self._get_basic_statistics(df),
                "data_quality": self._assess_data_quality(df),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if analysis_type == "correlation":
                results["correlation_analysis"] = await self._analyze_correlations(df)
            elif analysis_type == "outliers":
                results["outlier_analysis"] = self._detect_outliers(df)
            elif analysis_type == "clustering":
                results["clustering_analysis"] = await self._perform_clustering(df)
            
            return results
            
        except Exception as e:
            logger.error(f"DataFrame analysis failed: {e}")
            return {"error": str(e)}
    
    def _get_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistics for DataFrame."""
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
            "memory_usage": df.memory_usage(deep=True).sum()
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess data quality of DataFrame."""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()
        
        return {
            "completeness": (total_cells - missing_cells) / total_cells,
            "missing_percentage": (missing_cells / total_cells) * 100,
            "duplicate_rows": duplicate_rows,
            "duplicate_percentage": (duplicate_rows / len(df)) * 100,
            "data_types": df.dtypes.value_counts().to_dict()
        }
    
    async def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations in DataFrame."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {"error": "Not enough numeric columns for correlation analysis"}
        
        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) >= self.config.correlation_threshold:
                    strong_correlations.append({
                        "variable1": correlation_matrix.columns[i],
                        "variable2": correlation_matrix.columns[j],
                        "correlation": corr_value
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "correlation_threshold": self.config.correlation_threshold
        }
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in DataFrame."""
        numeric_df = df.select_dtypes(include=[np.number])
        outliers = {}
        
        for column in numeric_df.columns:
            z_scores = np.abs(stats.zscore(numeric_df[column].dropna()))
            outlier_indices = np.where(z_scores > self.config.outlier_threshold)[0]
            
            if len(outlier_indices) > 0:
                outliers[column] = {
                    "count": len(outlier_indices),
                    "percentage": (len(outlier_indices) / len(numeric_df[column])) * 100,
                    "indices": outlier_indices.tolist()
                }
        
        return {
            "outliers_by_column": outliers,
            "outlier_threshold": self.config.outlier_threshold
        }
    
    async def _perform_clustering(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """Perform clustering analysis on DataFrame."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {"error": "Not enough numeric columns for clustering"}
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df.fillna(numeric_df.mean()))
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # Add cluster labels to original DataFrame
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = cluster_labels
        
        return {
            "n_clusters": n_clusters,
            "cluster_labels": cluster_labels.tolist(),
            "cluster_centers": kmeans.cluster_centers_.tolist(),
            "inertia": kmeans.inertia_,
            "silhouette_score": self._calculate_silhouette_score(scaled_data, cluster_labels)
        }
    
    def _calculate_silhouette_score(self, data: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering."""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(data, labels)
        except:
            return 0.0
    
    async def create_visualization(self, data: Union[pd.DataFrame, Dict[str, Any]], 
                                 viz_type: str, user_context: Any = None) -> Dict[str, Any]:
        """
        Create visualizations using matplotlib/seaborn.
        
        Args:
            data: Data to visualize
            viz_type: Type of visualization
            user_context: User context for visualization
            
        Returns:
            Visualization results
        """
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            else:
                df = data
            
            fig, ax = plt.subplots(figsize=self.config.default_figure_size)
            
            if viz_type == "histogram":
                await self._create_histogram(df, ax)
            elif viz_type == "scatter":
                await self._create_scatter_plot(df, ax)
            elif viz_type == "correlation_heatmap":
                await self._create_correlation_heatmap(df, ax)
            elif viz_type == "box_plot":
                await self._create_box_plot(df, ax)
            elif viz_type == "line_plot":
                await self._create_line_plot(df, ax)
            else:
                return {"error": f"Unsupported visualization type: {viz_type}"}
            
            # Save plot
            plot_path = f"/tmp/visualization_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "visualization_type": viz_type,
                "plot_path": plot_path,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return {"error": str(e)}
    
    async def _create_histogram(self, df: pd.DataFrame, ax: plt.Axes):
        """Create histogram visualization."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            df[numeric_columns[0]].hist(ax=ax, bins=30)
            ax.set_title(f"Histogram of {numeric_columns[0]}")
            ax.set_xlabel(numeric_columns[0])
            ax.set_ylabel("Frequency")
    
    async def _create_scatter_plot(self, df: pd.DataFrame, ax: plt.Axes):
        """Create scatter plot visualization."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) >= 2:
            ax.scatter(df[numeric_columns[0]], df[numeric_columns[1]], alpha=0.6)
            ax.set_xlabel(numeric_columns[0])
            ax.set_ylabel(numeric_columns[1])
            ax.set_title(f"Scatter Plot: {numeric_columns[0]} vs {numeric_columns[1]}")
    
    async def _create_correlation_heatmap(self, df: pd.DataFrame, ax: plt.Axes):
        """Create correlation heatmap visualization."""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            correlation_matrix = numeric_df.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
            ax.set_title("Correlation Heatmap")
    
    async def _create_box_plot(self, df: pd.DataFrame, ax: plt.Axes):
        """Create box plot visualization."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            df[numeric_columns].boxplot(ax=ax)
            ax.set_title("Box Plot of Numeric Variables")
            ax.set_ylabel("Values")
    
    async def _create_line_plot(self, df: pd.DataFrame, ax: plt.Axes):
        """Create line plot visualization."""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            for column in numeric_columns[:3]:  # Limit to 3 lines for readability
                ax.plot(df.index, df[column], label=column)
            ax.set_title("Line Plot of Numeric Variables")
            ax.set_xlabel("Index")
            ax.set_ylabel("Values")
            ax.legend()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of Standard Analytics Adapter."""
        try:
            scipy_version = stats.__version__
        except AttributeError:
            scipy_version = "unknown"
        
        return {
            "status": "healthy" if self.initialized else "unhealthy",
            "initialized": self.initialized,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "matplotlib_version": plt.matplotlib.__version__,
            "seaborn_version": sns.__version__,
            "scipy_version": scipy_version,
            "timestamp": datetime.utcnow().isoformat()
        }
