"""
Insights Analytics Composition Service - Composition service for insights analytics
Integrates Smart City services, DI utilities, Public Works abstractions, and analytics capabilities.
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

from ..infrastructure_abstractions.analytics_abstraction import AnalyticsAbstraction, AnalyticsCapabilities
from ..infrastructure_adapters.standard_analytics_adapter import StandardAnalyticsAdapter, StandardAnalyticsConfig
from ..infrastructure_adapters.huggingface_analytics_adapter import HuggingFaceAnalyticsAdapter, HuggingFaceModelConfig

logger = logging.getLogger(__name__)

@dataclass
class InsightsAnalyticsCompositionConfig:
    """Configuration for insights analytics composition service."""
    enable_standard_analytics: bool = True
    enable_advanced_analytics: bool = True
    enable_visualization: bool = True
    enable_insights_generation: bool = True
    
    # Standard analytics config
    standard_analytics_config: StandardAnalyticsConfig = None
    
    # HuggingFace models config
    huggingface_models: Dict[str, HuggingFaceModelConfig] = None

class InsightsAnalyticsCompositionService:
    """
    Insights Analytics Composition Service - Composition service for insights analytics.
    Integrates Smart City services, DI utilities, Public Works abstractions, and analytics capabilities.
    """
    
    def __init__(self, di_container=None, smart_city_services=None, 
                 config: InsightsAnalyticsCompositionConfig = None):
        """
        Initialize Insights Analytics Composition Service.
        
        Args:
            di_container: Dependency injection container
            smart_city_services: Smart City services
            config: Composition configuration
        """
        self.di_container = di_container
        self.smart_city_services = smart_city_services or {}
        self.config = config or InsightsAnalyticsCompositionConfig()
        
        # Initialize components
        self.analytics_abstraction = None
        self.standard_adapter = None
        self.huggingface_adapter = None
        
        # Initialize from DI container if available
        if self.di_container:
            self._initialize_from_di_container()
        
        logger.info("Insights Analytics Composition Service initialized")
    
    def _initialize_from_di_container(self):
        """Initialize components from DI container."""
        try:
            # Get standard packages from DI container
            if self.di_container:
                # These are standard packages that won't be swapped
                pandas = self.di_container.get('pandas')
                numpy = self.di_container.get('numpy')
                matplotlib = self.di_container.get('matplotlib')
                seaborn = self.di_container.get('seaborn')
                scipy = self.di_container.get('scipy')
                sklearn = self.di_container.get('sklearn')
                
                logger.info("Retrieved standard packages from DI container")
            
        except Exception as e:
            logger.warning(f"Could not initialize from DI container: {e}")
    
    async def initialize(self) -> bool:
        """Initialize the composition service."""
        try:
            # Initialize standard analytics adapter
            if self.config.enable_standard_analytics:
                self.standard_adapter = StandardAnalyticsAdapter(
                    config=self.config.standard_analytics_config
                )
                await self.standard_adapter.initialize()
                logger.info("Standard analytics adapter initialized")
            
            # Initialize HuggingFace analytics adapter
            if self.config.enable_advanced_analytics:
                self.huggingface_adapter = HuggingFaceAnalyticsAdapter(
                    model_configs=self.config.huggingface_models
                )
                await self.huggingface_adapter.initialize()
                logger.info("HuggingFace analytics adapter initialized")
            
            # Initialize analytics abstraction
            capabilities = AnalyticsCapabilities(
                standard_analytics=self.config.enable_standard_analytics,
                advanced_analytics=self.config.enable_advanced_analytics,
                visualization=self.config.enable_visualization,
                insights_generation=self.config.enable_insights_generation
            )
            
            self.analytics_abstraction = AnalyticsAbstraction(
                standard_adapter=self.standard_adapter,
                huggingface_adapter=self.huggingface_adapter,
                capabilities=capabilities
            )
            
            await self.analytics_abstraction.initialize()
            logger.info("Analytics abstraction initialized")
            
            logger.info("Insights Analytics Composition Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Insights Analytics Composition Service: {e}")
            return False
    
    async def analyze_data(self, data: Dict[str, Any], analysis_type: str = "comprehensive", 
                          user_context: Any = None) -> Dict[str, Any]:
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
            if not self.analytics_abstraction:
                return {"error": "Analytics abstraction not initialized"}
            
            return await self.analytics_abstraction.analyze_data(
                data, analysis_type, user_context
            )
            
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return {"error": str(e)}
    
    async def create_visualization(self, data: Dict[str, Any], viz_type: str, 
                                 user_context: Any = None) -> Dict[str, Any]:
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
            if not self.analytics_abstraction:
                return {"error": "Analytics abstraction not initialized"}
            
            return await self.analytics_abstraction.create_visualization(
                data, viz_type, user_context
            )
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return {"error": str(e)}
    
    async def generate_insights(self, data: Dict[str, Any], user_context: Any = None) -> Dict[str, Any]:
        """
        Generate insights using available analytics capabilities.
        
        Args:
            data: Data to analyze for insights
            user_context: User context for analysis
            
        Returns:
            Generated insights
        """
        try:
            if not self.analytics_abstraction:
                return {"error": "Analytics abstraction not initialized"}
            
            return await self.analytics_abstraction.generate_insights(
                data, user_context
            )
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return {"error": str(e)}
    
    async def get_available_capabilities(self, user_context: Any = None) -> Dict[str, Any]:
        """
        Get available analytics capabilities.
        
        Args:
            user_context: User context for capability check
            
        Returns:
            Available capabilities
        """
        try:
            if not self.analytics_abstraction:
                return {"error": "Analytics abstraction not initialized"}
            
            return await self.analytics_abstraction.get_available_capabilities(user_context)
            
        except Exception as e:
            logger.error(f"Capability check failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of composition service."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check analytics abstraction
        if self.analytics_abstraction:
            abstraction_health = await self.analytics_abstraction.health_check()
            health_status["components"]["analytics_abstraction"] = abstraction_health
        
        # Check standard adapter
        if self.standard_adapter:
            standard_health = await self.standard_adapter.health_check()
            health_status["components"]["standard_adapter"] = standard_health
        
        # Check HuggingFace adapter
        if self.huggingface_adapter:
            huggingface_health = await self.huggingface_adapter.health_check()
            health_status["components"]["huggingface_adapter"] = huggingface_health
        
        # Overall health
        all_healthy = all(
            component.get("status") == "healthy" 
            for component in health_status["components"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "unhealthy"
        
        return health_status




