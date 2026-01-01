"""
Analytics Abstraction - Infrastructure abstraction for analytics capabilities
Provides unified interface for both standard and advanced analytics capabilities.
"""

from typing import Dict, Any, List, Optional, Union
import logging
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from ..abstraction_contracts.data_analysis_protocol import DataAnalysisProtocol
from ..abstraction_contracts.insights_generation_protocol import InsightsGenerationProtocol
from ..abstraction_contracts.visualization_protocol import VisualizationProtocol

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsCapabilities:
    """Analytics capabilities configuration."""
    standard_analytics: bool = True
    advanced_analytics: bool = True
    visualization: bool = True
    insights_generation: bool = True

class AnalyticsAbstraction:
    """
    Analytics Abstraction - Infrastructure abstraction for analytics capabilities.
    Provides unified interface for both standard and advanced analytics capabilities.
    """
    
    def __init__(self, standard_adapter=None, huggingface_adapter=None, 
                 capabilities: AnalyticsCapabilities = None, di_container=None):
        """
        Initialize Analytics Abstraction.
        
        Args:
            standard_adapter: Standard analytics adapter (pandas, numpy, etc.)
            huggingface_adapter: HuggingFace analytics adapter
            capabilities: Analytics capabilities configuration
            di_container: Dependency injection container
        """
        self.standard_adapter = standard_adapter
        self.huggingface_adapter = huggingface_adapter
        self.capabilities = capabilities or AnalyticsCapabilities()
        self.initialized = False
        self.di_container = di_container
        self.service_name = "analytics_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Analytics Abstraction initialized")
    
    async def initialize(self) -> bool:
        """Initialize analytics abstraction."""
        try:
            # Initialize standard adapter if available
            if self.standard_adapter and self.capabilities.standard_analytics:
                await self.standard_adapter.initialize()
                self.logger.info("Standard analytics adapter initialized")
            
            # Initialize HuggingFace adapter if available
            if self.huggingface_adapter and self.capabilities.advanced_analytics:
                await self.huggingface_adapter.initialize()
                self.logger.info("HuggingFace analytics adapter initialized")
            
            self.initialized = True
            self.logger.info("✅ Analytics Abstraction initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Analytics Abstraction: {e}")
            raise  # Re-raise for service layer to handle

        """
        Analyze data using available analytics capabilities.
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis to perform
            user_context: User context for analysis
            
        Returns:
            Analysis results
        """
        try:
            results = {
                "analysis_type": analysis_type,
                "timestamp": datetime.utcnow().isoformat(),
                "capabilities_used": []
            }
            
            # Standard analytics
            if self.standard_adapter and self.capabilities.standard_analytics:
                standard_results = await self.standard_adapter.analyze_dataframe(
                    data, analysis_type, user_context
                )
                results["standard_analytics"] = standard_results
                results["capabilities_used"].append("standard_analytics")
            
            # Advanced analytics (HuggingFace)
            if self.huggingface_adapter and self.capabilities.advanced_analytics:
                if isinstance(data, dict) and "text_data" in data:
                    huggingface_results = await self.huggingface_adapter.generate_insights(
                        data, user_context
                    )
                    results["advanced_analytics"] = huggingface_results
                    results["capabilities_used"].append("advanced_analytics")
            
            self.logger.info(f"✅ Data analysis completed: {analysis_type}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Data analysis failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Create visualization using available capabilities.
        
        Args:
            data: Data to visualize
            viz_type: Type of visualization
            user_context: User context for visualization
            
        Returns:
            Visualization results
        """
        try:
            if not self.standard_adapter or not self.capabilities.visualization:
                return {"error": "Visualization capabilities not available"}
            
            result = await self.standard_adapter.create_visualization(
                data, viz_type, user_context
            )
            
            self.logger.info(f"✅ Visualization created: {viz_type}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Visualization creation failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate insights using available analytics capabilities.
        
        Args:
            data: Data to analyze for insights
            user_context: User context for analysis
            
        Returns:
            Generated insights
        """
        try:
            insights = {
                "timestamp": datetime.utcnow().isoformat(),
                "capabilities_used": []
            }
            
            # Standard insights from data analysis
            if self.standard_adapter and self.capabilities.standard_analytics:
                if isinstance(data, pd.DataFrame):
                    standard_insights = await self.standard_adapter.analyze_dataframe(
                        data, "comprehensive", user_context
                    )
                    insights["standard_insights"] = standard_insights
                    insights["capabilities_used"].append("standard_analytics")
            
            # Advanced insights from HuggingFace
            if self.huggingface_adapter and self.capabilities.advanced_analytics:
                huggingface_insights = await self.huggingface_adapter.generate_insights(
                    data, user_context
                )
                insights["advanced_insights"] = huggingface_insights
                insights["capabilities_used"].append("advanced_analytics")
            
            self.logger.info(f"✅ Insights generated")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Insights generation failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get available analytics capabilities.
        
        Args:
            user_context: User context for capability check
            
        Returns:
            Available capabilities
        """
        capabilities = {
            "standard_analytics": {
                "available": self.standard_adapter is not None and self.capabilities.standard_analytics,
                "features": [
                    "data_analysis", "statistical_analysis", "correlation_analysis",
                    "outlier_detection", "clustering", "visualization"
                ]
            },
            "advanced_analytics": {
                "available": self.huggingface_adapter is not None and self.capabilities.advanced_analytics,
                "features": [
                    "sentiment_analysis", "text_classification", "summarization",
                    "question_answering", "nlp_insights"
                ]
            },
            "visualization": {
                "available": self.standard_adapter is not None and self.capabilities.visualization,
                "features": [
                    "histogram", "scatter_plot", "correlation_heatmap",
                    "box_plot", "line_plot"
                ]
            }
        }
        
        return {
            "capabilities": capabilities,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of analytics abstraction."""
        health_status = {
            "status": "healthy" if self.initialized else "unhealthy",
            "initialized": self.initialized,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check standard adapter
        if self.standard_adapter:
            standard_health = await self.standard_adapter.health_check()
            health_status["standard_adapter"] = standard_health
        
        # Check HuggingFace adapter
        if self.huggingface_adapter:
            huggingface_health = await self.huggingface_adapter.health_check()
            health_status["huggingface_adapter"] = huggingface_health
        
        return health_status

