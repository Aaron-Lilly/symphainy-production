#!/usr/bin/env python3
"""
Visualization Abstraction

Infrastructure abstraction for visualization capabilities, coordinating standard and AI adapters.

WHAT (Infrastructure Abstraction Role): I coordinate visualization adapters
HOW (Abstraction Implementation): I delegate to standard and AI adapters as appropriate
"""

from typing import Dict, Any, Optional
import logging

from ..abstraction_contracts.visualization_protocol import VisualizationProtocol, VisualizationResult
from ..infrastructure_adapters.standard_visualization_adapter import StandardVisualizationAdapter

class VisualizationAbstraction(VisualizationProtocol):
    """
    Visualization Infrastructure Abstraction
    
    Coordinates standard and AI visualization adapters to provide comprehensive
    visualization capabilities for the Business Outcomes Pillar.
    """
    
    def __init__(self, standard_adapter: StandardVisualizationAdapter, di_container=None):
        """
        Initialize Visualization Abstraction.
        
        Args:
            standard_adapter: Standard visualization adapter (required via DI)
            di_container: Dependency injection container
        """
        if not standard_adapter:
            raise ValueError("VisualizationAbstraction requires standard_adapter via dependency injection")
        
        self.standard_adapter = standard_adapter
        self.di_container = di_container
        self.service_name = "visualization_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Visualization Abstraction initialized")
    
    async def create_summary_dashboard(self, pillar_outputs: Dict[str, Any]) -> VisualizationResult:
        """
        Create summary dashboard showing outputs from all pillars.
        
        Delegates to standard adapter for reliable visualization.
        """
        try:
            self.logger.info("Creating summary dashboard via standard adapter...")
            result = await self.standard_adapter.create_summary_dashboard(pillar_outputs)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to create summary dashboard: {e}")
            raise  # Re-raise for service layer to handle
    
            raise  # Re-raise for service layer to handle

        """
        Create roadmap visualization as standalone visual element.
        
        Delegates to standard adapter for reliable roadmap visualization.
        """
        try:
            self.logger.info("Creating roadmap visualization via standard adapter...")
            result = await self.standard_adapter.create_roadmap_visualization(roadmap_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to create roadmap visualization: {e}")
            raise  # Re-raise for service layer to handle
    
            raise  # Re-raise for service layer to handle

        """
        Create financial analysis visualization.
        
        Delegates to standard adapter for reliable financial visualization.
        """
        try:
            self.logger.info("Creating financial visualization via standard adapter...")
            result = await self.standard_adapter.create_financial_visualization(financial_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to create financial visualization: {e}")
            raise  # Re-raise for service layer to handle

        """
        Create business metrics dashboard.
        
        Delegates to standard adapter for reliable metrics visualization.
        """
        try:
            self.logger.info("Creating metrics dashboard via standard adapter...")
            result = await self.standard_adapter.create_metrics_dashboard(metrics_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to create metrics dashboard: {e}")
            raise  # Re-raise for service layer to handle

        """Perform health check on the visualization abstraction."""
        try:
            standard_health = await self.standard_adapter.health_check()
            
            result = {
                "status": "healthy" if standard_health.get("status") == "healthy" else "unhealthy",
                "abstraction": "VisualizationAbstraction",
                "adapters": {
                    "standard": standard_health
                },
                "capabilities": [
                    "summary_dashboard",
                    "roadmap_visualization", 
                    "financial_visualization",
                    "metrics_dashboard"
                ],
                "last_check": standard_health.get("last_check")
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform health check: {e}")

            raise  # Re-raise for service layer to handle
