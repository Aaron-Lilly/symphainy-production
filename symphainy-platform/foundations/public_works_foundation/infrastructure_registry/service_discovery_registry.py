#!/usr/bin/env python3
"""
Service Discovery Registry - Layer 5 of 5-Layer Architecture

This registry is the single point of exposure for service discovery infrastructure.
It builds and manages all infrastructure abstractions for service registration and discovery.

WHAT (Infrastructure Role): I provide single point of exposure for service discovery infrastructure
HOW (Infrastructure Implementation): I build and manage all service discovery infrastructure layers
WHY: To enable swap-ability and consistent access patterns for service mesh capabilities
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

from foundations.public_works_foundation.infrastructure_abstractions.service_discovery_abstraction import ServiceDiscoveryAbstraction


class ServiceDiscoveryRegistry:
    """
    Service Discovery Registry.
    
    Single point of exposure for service discovery infrastructure.
    Exposure-only registry (following architectural pattern):
    - Public Works Foundation creates adapters and abstractions
    - This registry only registers and exposes them
    """

    def __init__(self, service_name: str = "service_discovery_registry", di_container=None):
        """Initialize Service Discovery Registry (exposure only)."""
        if not di_container:
            raise ValueError("DI Container is required for ServiceDiscoveryRegistry initialization")
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"ServiceDiscoveryRegistry-{service_name}")
        
        # Registered abstraction (created by Public Works Foundation)
        self.abstraction = None
        
        self.is_ready = False
        self.initialization_time = None
        
        self.logger.info(f"✅ Service Discovery Registry '{service_name}' initialized (exposure only)")

    def register_abstraction(self, name: str, abstraction: ServiceDiscoveryAbstraction) -> bool:
        """
        Register a service discovery abstraction (created by Public Works Foundation).
        
        Args:
            name: Name for the abstraction (e.g., "service_discovery")
            abstraction: ServiceDiscoveryAbstraction instance
        
        Returns:
            bool: True if registered successfully
        """
        try:
            if not abstraction:
                self.logger.error(f"❌ Cannot register None abstraction for '{name}'")
                return False
            
            self.abstraction = abstraction
            self.is_ready = True
            self.initialization_time = datetime.utcnow()
            
            self.logger.info(f"✅ Registered service discovery abstraction '{name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register abstraction '{name}': {e}")
            return False

    def get_service_discovery(self) -> Optional[ServiceDiscoveryAbstraction]:
        """
        Get the service discovery abstraction.
        
        Returns:
            ServiceDiscoveryAbstraction: The abstraction layer
        
        Raises:
            RuntimeError: If abstraction not registered
        """
        if not self.is_ready or not self.abstraction:
            raise RuntimeError("Service discovery abstraction not registered. Ensure Public Works Foundation has initialized and registered the abstraction.")
        
        return self.abstraction

    def get_status(self) -> Dict[str, Any]:
        """
        Get service discovery registry status.
        
        Returns:
            Dict: Status information
        """
        return {
            "service_name": self.service_name,
            "is_ready": self.is_ready,
            "initialization_time": self.initialization_time.isoformat() if self.initialization_time else None,
            "abstraction_available": self.abstraction is not None
        }

    async def cleanup(self):
        """Cleanup service discovery registry."""
        try:
            self.logger.info("🧹 Cleaning up service discovery registry...")
            
            self.abstraction = None
            self.is_ready = False
            
            self.logger.info("✅ Service discovery registry cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")

