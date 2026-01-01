#!/usr/bin/env python3
"""
Abstraction Discovery Service

Handles abstraction discovery and listing for all dimensions.

WHAT (Service Role): I need to handle abstraction discovery and listing
HOW (Service Implementation): I provide discovery capabilities for all abstractions
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Import utilities directly
from utilities import (
    ValidationUtility, SerializationUtility, ConfigurationUtility,
    HealthManagementUtility
)


class AbstractionDiscoveryService(FoundationServiceBase):
    """
    Abstraction Discovery Service - Abstraction discovery for all dimensions
    
    Provides discovery capabilities for role abstractions across all dimensions.
    
    WHAT (Service Role): I need to handle abstraction discovery and listing
    HOW (Service Implementation): I provide discovery capabilities for all abstractions
    """
    
    def __init__(self, validation_utility, serialization_utility, config_utility, health_utility, mcp_utilities, abstraction_creation_service):
        """Initialize Abstraction Discovery Service."""
        super().__init__("abstraction_discovery")
        
        # Store utilities
        self.validation_utility = validation_utility
        self.serialization_utility = serialization_utility
        self.config_utility = config_utility
        self.health_utility = health_utility
        self.mcp_utilities = mcp_utilities
        self.abstraction_creation_service = abstraction_creation_service
        
        self.logger.info("🔍 Abstraction Discovery Service initialized")
    
    async def initialize(self):
        """Initialize the Abstraction Discovery Service."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Abstraction Discovery Service...")
            
            self.logger.info("✅ Abstraction Discovery Service initialized successfully")
            
        except Exception as e:
            self.error_handler.handle_error(e, context="abstraction_discovery_initialize")
            raise

    # ============================================================================
    # ABSTRACTION DISCOVERY
    
    def discover_abstractions_by_dimension(self, dimension: str) -> List[str]:
        """Discover all abstractions for a specific dimension."""
        try:
            if not self.abstraction_creation_service:
                return []
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            if dimension not in role_abstractions:
                return []
            
            abstractions = set()
            for role, role_abstractions_dict in role_abstractions[dimension].items():
                abstractions.update(role_abstractions_dict.keys())
            
            return list(abstractions)
            
        except Exception as e:
            self.error_handler.handle_error(e, context="discover_abstractions_by_dimension")
            return []

    def discover_abstractions_by_role(self, dimension: str, role: str) -> List[str]:
        """Discover all abstractions for a specific role."""
        try:
            if not self.abstraction_creation_service:
                return []
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            if dimension not in role_abstractions:
                return []
            
            if role not in role_abstractions[dimension]:
                return []
            
            return list(role_abstractions[dimension][role].keys())
            
        except Exception as e:
            self.error_handler.handle_error(e, context="discover_abstractions_by_role")
            return []

    def discover_all_dimensions(self) -> List[str]:
        """Discover all available dimensions."""
        try:
            if not self.abstraction_creation_service:
                return []
            
            return list(self.abstraction_creation_service.role_abstractions.keys())
            
        except Exception as e:
            self.error_handler.handle_error(e, context="discover_all_dimensions")
            return []

    def discover_all_roles(self, dimension: str = None) -> Dict[str, List[str]]:
        """Discover all roles, optionally filtered by dimension."""
        try:
            if not self.abstraction_creation_service:
                return {}
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            
            if dimension:
                return {dimension: list(role_abstractions.get(dimension, {}).keys())}
            else:
                result = {}
                for dim, roles in role_abstractions.items():
                    result[dim] = list(roles.keys())
                return result
                
        except Exception as e:
            self.error_handler.handle_error(e, context="discover_all_roles")
            return {}

    # ============================================================================
    # STATUS AND HEALTH
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Get discovery service status."""
        try:
            return {
                "service": "abstraction_discovery",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "abstraction_creation_available": self.abstraction_creation_service is not None,
                "dimensions_available": len(self.discover_all_dimensions()),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": "abstraction_discovery",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            health_status = {
                "service": "abstraction_discovery",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "abstraction_creation_available": self.abstraction_creation_service is not None,
                "dimensions_available": len(self.discover_all_dimensions())
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "abstraction_discovery",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
