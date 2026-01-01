#!/usr/bin/env python3
"""
File Management Registry - Infrastructure Registry (Exposure/Discovery Layer)

Registry for exposing and discovering file management infrastructure abstractions.
This is Layer 5 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I expose and manage file management infrastructure abstractions
HOW (Infrastructure Implementation): I provide discovery and health monitoring for registered abstractions

NOTE: This registry does NOT create adapters or abstractions.
      All creation happens in Public Works Foundation Service.
      This registry only holds references and provides discovery.
"""

import logging
from typing import Dict, Any, Optional

from ..composition_services.file_management_composition_service import FileManagementCompositionService

logger = logging.getLogger(__name__)

class FileManagementRegistry:
    """
    File Management infrastructure registry - exposure/discovery layer only.
    
    This registry holds references to abstractions created by Public Works Foundation Service.
    It provides discovery, health monitoring, and service registration capabilities.
    
    Does NOT create adapters or abstractions - that's Public Works Foundation's responsibility.
    """
    
    def __init__(self):
        """Initialize File Management Registry (exposure only, no creation)."""
        self.logger = logging.getLogger(__name__)
        
        # Infrastructure abstractions (registered by Public Works Foundation)
        self._abstractions = {}
        
        # Composition services (registered by Public Works Foundation)
        self._composition_services = {}
        
        self.logger.info("✅ File Management Registry initialized (exposure/discovery layer)")
    
    # ============================================================================
    # REGISTRATION METHODS (Called by Public Works Foundation)
    # ============================================================================
    
    def register_abstraction(self, name: str, abstraction: Any) -> None:
        """
        Register an abstraction (created by Public Works Foundation).
        
        Args:
            name: Abstraction name (e.g., "file_management")
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
            name: Composition service name (e.g., "file_management")
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
    
    async def get_file_management_abstraction(self) -> Optional[Any]:
        """
        Get file management abstraction (convenience method).
        
        Returns:
            FileManagementAbstraction instance or None if not registered
        """
        return self._abstractions.get("file_management")
    
    def get_file_management_composition(self) -> Optional[Any]:
        """
        Get file management composition service.
        
        Returns:
            FileManagementCompositionService instance or None if not registered
        """
        return self._composition_services.get("file_management")
    
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
            "composition_services": list(self._composition_services.keys())
        }
    
    def is_ready(self) -> bool:
        """
        Check if registry is ready (has required abstractions).
        
        Returns:
            bool: True if file_management abstraction is registered
        """
        return "file_management" in self._abstractions
    
    @property
    def is_initialized(self) -> bool:
        """Alias for is_ready() for backward compatibility."""
        return self.is_ready()
