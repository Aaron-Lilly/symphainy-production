#!/usr/bin/env python3
"""
Coexistence Blueprint Abstraction

Infrastructure abstraction for coexistence blueprint generation capabilities.
Implements CoexistenceBlueprintProtocol using CoexistenceBlueprintAdapter.

WHAT (Infrastructure Abstraction Role): I provide unified coexistence blueprint infrastructure
HOW (Infrastructure Abstraction Implementation): I coordinate coexistence blueprint adapters
"""

from typing import Dict, Any
import logging

from ..abstraction_contracts.coexistence_blueprint_protocol import CoexistenceBlueprintProtocol, BlueprintResult
from ..infrastructure_adapters.coexistence_blueprint_adapter import CoexistenceBlueprintAdapter

class CoexistenceBlueprintAbstraction(CoexistenceBlueprintProtocol):
    """Coexistence blueprint abstraction using coexistence blueprint adapter."""
    
    def __init__(self, coexistence_blueprint_adapter: CoexistenceBlueprintAdapter, di_container=None, **kwargs):
        """
        Initialize coexistence blueprint abstraction.
        
        Args:
            coexistence_blueprint_adapter: Coexistence blueprint adapter instance
            di_container: Dependency injection container
        """
        self.coexistence_blueprint_adapter = coexistence_blueprint_adapter
        self.di_container = di_container
        self.service_name = "coexistence_blueprint_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Coexistence Blueprint Abstraction initialized")
    
    async def initialize(self):
        """Initialize the coexistence blueprint abstraction."""
        try:
            self.logger.info("Initializing coexistence blueprint abstraction...")
            # Adapter is already initialized
            self.logger.info("✅ Coexistence Blueprint Abstraction initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize coexistence blueprint abstraction: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def generate_coexistence_blueprint(self, coexistence_data: Dict[str, Any], 
                                           current_state: Dict[str, Any], target_state: Dict[str, Any]) -> BlueprintResult:
        """
        Generate coexistence blueprint from analysis data.
        
        Args:
            coexistence_data: Coexistence analysis results
            current_state: Current state data
            target_state: Target state data
            
        Returns:
            BlueprintResult with generated blueprint and metadata
        """
        try:
            # Use adapter to generate blueprint
            result = await self.coexistence_blueprint_adapter.generate_coexistence_blueprint(
                coexistence_data, current_state, target_state
            )
            
            if result.get("success"):
                blueprint_result = BlueprintResult(
                    success=True,
                    blueprint=result.get("blueprint", {}),
                    implementation_roadmap=result.get("implementation_roadmap", []),
                    success_metrics=result.get("success_metrics", []),
                    metadata=result.get("metadata", {}),
                    error=None
                )
                
                return blueprint_result
            else:
                return BlueprintResult(
                    success=False,
                    blueprint={},
                    implementation_roadmap=[],
                    success_metrics=[],
                    metadata={},
                    error=result.get("error", "Blueprint generation failed")
                )
                
        except Exception as e:
            self.logger.error(f"❌ Coexistence blueprint generation failed: {e}")
            raise  # Re-raise for service layer to handle
    
            raise  # Re-raise for service layer to handle

        """
        Create coexistence blueprint directly from requirements.
        
        Args:
            requirements: Blueprint requirements
            constraints: Implementation constraints
            user_context: User context data
            
        Returns:
            BlueprintResult with created blueprint and metadata
        """
        try:
            # Use adapter to create blueprint
            result = await self.coexistence_blueprint_adapter.create_coexistence_blueprint(
                requirements, constraints, user_context
            )
            
            if result.get("success"):
                blueprint_result = BlueprintResult(
                    success=True,
                    blueprint=result.get("blueprint", {}),
                    implementation_roadmap=result.get("implementation_plan", []),
                    success_metrics=result.get("success_metrics", []),
                    metadata=result.get("metadata", {}),
                    error=None
                )
                
                return blueprint_result
            else:
                return BlueprintResult(
                    success=False,
                    blueprint={},
                    implementation_roadmap=[],
                    success_metrics=[],
                    metadata={},
                    error=result.get("error", "Blueprint creation failed")
                )
                
        except Exception as e:
            self.logger.error(f"❌ Coexistence blueprint creation failed: {e}")
            raise  # Re-raise for service layer to handle

        """Check the health of the coexistence blueprint abstraction."""
        try:
            # Check adapter health
            adapter_health = await self.coexistence_blueprint_adapter.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "abstraction": "CoexistenceBlueprintAbstraction",
                "adapter_health": adapter_health,
                "capabilities": [
                    "blueprint_generation",
                    "roadmap_creation",
                    "metrics_definition"
                ]
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
