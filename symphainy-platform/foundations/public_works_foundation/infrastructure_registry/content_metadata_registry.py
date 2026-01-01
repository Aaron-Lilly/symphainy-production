#!/usr/bin/env python3
"""
Content Metadata Registry - Infrastructure Registry (Exposure/Discovery Layer)

Registry for exposing and discovering content metadata infrastructure abstractions.
This is Layer 5 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I expose and manage content metadata infrastructure abstractions
HOW (Infrastructure Implementation): I provide discovery and health monitoring for registered abstractions

NOTE: This registry does NOT create adapters or abstractions.
      All creation happens in Public Works Foundation Service.
      This registry only holds references and provides discovery.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentMetadataRegistry:
    """
    Content Metadata infrastructure registry - exposure/discovery layer only.
    
    This registry holds references to abstractions created by Public Works Foundation Service.
    It provides discovery, health monitoring, and service registration capabilities.
    
    Does NOT create adapters or abstractions - that's Public Works Foundation's responsibility.
    """
    
    def __init__(self):
        """Initialize Content Metadata Registry (exposure only, no creation)."""
        self.logger = logging.getLogger(__name__)
        
        # Infrastructure abstractions (registered by Public Works Foundation)
        self._abstractions = {}
        
        # Composition services (registered by Public Works Foundation)
        self._composition_services = {}
        
        self.logger.info("✅ Content Metadata Registry initialized (exposure/discovery layer)")
    
    # ============================================================================
    # REGISTRATION METHODS (Called by Public Works Foundation)
    # ============================================================================
    
    def register_abstraction(self, name: str, abstraction: Any) -> None:
        """
        Register an abstraction (created by Public Works Foundation).
        
        Args:
            name: Abstraction name (e.g., "content_metadata", "content_schema", "content_insights")
            abstraction: Abstraction instance (already created with dependency injection)
        """
        if not abstraction:
            raise ValueError(f"Cannot register None for abstraction '{name}'")
        
        self._abstractions[name] = abstraction
        self.logger.info(f"✅ Registered '{name}' abstraction")
    
    def register_composition_service(self, name: str, composition_service: Any) -> None:
        """
        Register a composition service (created by Public Works Foundation).
        
        Args:
            name: Composition service name (e.g., "content_metadata", "content_analysis")
            composition_service: Composition service instance (already created)
        """
        if not composition_service:
            raise ValueError(f"Cannot register None for composition service '{name}'")
        
        self._composition_services[name] = composition_service
        self.logger.info(f"✅ Registered '{name}' composition service")
    
    # ============================================================================
    # DISCOVERY METHODS (Called by Platform Gateway, Services, etc.)
    # ============================================================================
    
    def get_abstraction(self, name: str) -> Any:
        """
        Get infrastructure abstraction by name (discovery method).
        
        Args:
            name: Abstraction name
            
        Returns:
            Abstraction instance
            
        Raises:
            ValueError: If abstraction not registered
        """
        if name not in self._abstractions:
            available = list(self._abstractions.keys())
            raise ValueError(
                f"Abstraction '{name}' not registered. "
                f"Available: {available}"
            )
        return self._abstractions[name]
    
    def get_content_metadata_abstraction(self) -> Optional[Any]:
        """
        Get content metadata abstraction (convenience method).
        
        Returns:
            ContentMetadataAbstraction instance or None if not registered
        """
        return self._abstractions.get("content_metadata")
    
    def get_content_schema_abstraction(self) -> Optional[Any]:
        """
        Get content schema abstraction (convenience method).
        
        Returns:
            ContentSchemaAbstraction instance or None if not registered
        """
        return self._abstractions.get("content_schema")
    
    def get_content_insights_abstraction(self) -> Optional[Any]:
        """
        Get content insights abstraction (convenience method).
        
        Returns:
            ContentInsightsAbstraction instance or None if not registered
        """
        return self._abstractions.get("content_insights")
    
    def get_content_metadata_composition(self) -> Optional[Any]:
        """
        Get content metadata composition service (convenience method).
        
        Returns:
            ContentMetadataCompositionService instance or None if not registered
        """
        return self._composition_services.get("content_metadata")
    
    def get_content_analysis_composition(self) -> Optional[Any]:
        """
        Get content analysis composition service (convenience method).
        
        Returns:
            ContentAnalysisCompositionService instance or None if not registered
        """
        return self._composition_services.get("content_analysis")
    
    def get_all_abstractions(self) -> Dict[str, Any]:
        """Get all registered abstractions."""
        return self._abstractions.copy()
    
    def get_all_composition_services(self) -> Dict[str, Any]:
        """Get all registered composition services."""
        return self._composition_services.copy()
    
    # ============================================================================
    # HEALTH MONITORING
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Aggregate health check for all registered abstractions.
        
        Returns:
            Dict containing health status for all abstractions
        """
        health = {
            "status": "healthy",
            "abstractions": {},
            "composition_services_count": len(self._composition_services)
        }
        
        for name, abstraction in self._abstractions.items():
            try:
                if hasattr(abstraction, 'health_check'):
                    abstraction_health = await abstraction.health_check()
                    health["abstractions"][name] = abstraction_health
                    
                    # Check if abstraction is unhealthy
                    if isinstance(abstraction_health, dict):
                        if abstraction_health.get("status") != "healthy":
                            health["status"] = "degraded"
                    elif not abstraction_health:
                        health["status"] = "degraded"
                else:
                    # No health check method - assume healthy
                    health["abstractions"][name] = {"status": "unknown"}
            except Exception as e:
                health["abstractions"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health["status"] = "unhealthy"
        
        return health
    
    # ============================================================================
    # STATUS METHODS
    # ============================================================================
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status information."""
        return {
            "abstractions_count": len(self._abstractions),
            "composition_services_count": len(self._composition_services),
            "abstractions": list(self._abstractions.keys()),
            "composition_services": list(self._composition_services.keys()),
                "capabilities": [
                    "content_metadata_management",
                    "content_schema_analysis",
                    "content_insights_generation",
                    "content_relationship_tracking",
                    "content_analysis_workflows",
                    "content_intelligence_reporting"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
    def is_ready(self) -> bool:
        """
        Check if registry is ready (has required abstractions).
        
        Returns:
            bool: True if all required abstractions are registered
        """
        required = ["content_metadata", "content_schema", "content_insights"]
        return all(name in self._abstractions for name in required)
    
    @property
    def is_initialized(self) -> bool:
        """Alias for is_ready() for backward compatibility."""
        return self.is_ready()
    
    def get_available_services(self) -> Dict[str, Any]:
        """Get list of available services."""
        return {
            "abstractions": list(self._abstractions.keys()),
            "composition_services": list(self._composition_services.keys())
        }
    
    def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (static list for documentation)."""
        return {
            "content_metadata": [
                "create_content_metadata",
                "get_content_metadata",
                "update_content_metadata",
                "delete_content_metadata",
                "search_content_metadata",
                "analyze_content_structure",
                "extract_content_schema",
                "generate_content_insights",
                "create_content_relationship",
                "get_content_relationships",
                "perform_content_analysis",
                "search_content_by_pattern"
            ],
            "content_schema": [
                "extract_content_schema",
                "analyze_schema_structure",
                "validate_schema_consistency",
                "search_schemas_by_pattern",
                "identify_schema_patterns",
                "compare_schema_structures",
                "create_schema_relationship",
                "get_schema_relationships",
                "generate_schema_insights",
                "analyze_schema_quality"
            ],
            "content_insights": [
                "generate_content_insights",
                "analyze_content_patterns",
                "extract_business_meaning",
                "store_content_insight",
                "get_content_insights",
                "update_content_insight",
                "search_insights_by_type",
                "search_insights_by_pattern",
                "find_related_insights",
                "analyze_insight_confidence",
                "validate_insight_accuracy",
                "generate_insight_recommendations",
                "aggregate_content_insights",
                "generate_insights_summary"
            ],
            "content_metadata_composition": [
                "process_hybrid_content",
                "extract_complete_content_analysis",
                "create_content_lineage_chain",
                "get_complete_content_lineage",
                "advanced_content_search",
                "generate_content_analytics"
            ],
            "content_analysis_composition": [
                "perform_deep_content_analysis",
                "analyze_content_relationships",
                "generate_content_intelligence_report",
                "perform_cross_content_analysis",
                "optimize_content_structure"
            ]
        }




