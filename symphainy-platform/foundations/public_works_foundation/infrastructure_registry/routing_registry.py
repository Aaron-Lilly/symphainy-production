#!/usr/bin/env python3
"""
Routing Registry - Layer 5 of 5-Layer Architecture

This registry is the single point of exposure for routing infrastructure.
It builds and manages all infrastructure abstractions for routing operations.

WHAT (Infrastructure Role): I provide single point of exposure for routing infrastructure
HOW (Infrastructure Implementation): I build and manage all routing infrastructure layers
WHY: To enable swap-ability and consistent access patterns for reverse proxy capabilities
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

from foundations.public_works_foundation.infrastructure_abstractions.routing_abstraction import RoutingAbstraction


class RoutingRegistry:
    """
    Routing Registry.
    
    Single point of exposure for routing infrastructure.
    Exposure-only registry (following architectural pattern):
    - Public Works Foundation creates adapters and abstractions
    - This registry only registers and exposes them
    """

    def __init__(self, service_name: str = "routing_registry", di_container=None):
        """Initialize Routing Registry (exposure only)."""
        if not di_container:
            raise ValueError("DI Container is required for RoutingRegistry initialization")
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"RoutingRegistry-{service_name}")
        
        # Registered abstraction (created by Public Works Foundation)
        self.abstraction = None
        
        self.is_ready = False
        self.initialization_time = None
        
        self.logger.info(f"✅ Routing Registry '{service_name}' initialized (exposure only)")

    def register_abstraction(self, name: str, abstraction: RoutingAbstraction) -> bool:
        """
        Register a routing abstraction (created by Public Works Foundation).
        
        Args:
            name: Name for the abstraction (e.g., "routing")
            abstraction: RoutingAbstraction instance
        
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
            
            self.logger.info(f"✅ Registered routing abstraction '{name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register abstraction '{name}': {e}")
            return False

    def get_routing(self) -> Optional[RoutingAbstraction]:
        """
        Get the routing abstraction.
        
        Returns:
            RoutingAbstraction: The abstraction layer
        
        Raises:
            RuntimeError: If abstraction not registered
        """
        if not self.is_ready or not self.abstraction:
            raise RuntimeError("Routing abstraction not registered. Ensure Public Works Foundation has initialized and registered the abstraction.")
        
        return self.abstraction

    def get_status(self) -> Dict[str, Any]:
        """
        Get routing registry status.
        
        Returns:
            Dict: Status information
        """
        return {
            "service_name": self.service_name,
            "is_ready": self.is_ready,
            "initialization_time": self.initialization_time.isoformat() if self.initialization_time else None,
            "has_abstraction": self.abstraction is not None
        }


