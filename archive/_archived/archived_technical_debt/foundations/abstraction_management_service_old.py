#!/usr/bin/env python3
"""
Abstraction Management Service

Handles service management and health monitoring for all abstractions.

WHAT (Service Role): I need to handle service management and health monitoring
HOW (Service Implementation): I provide management capabilities for all abstractions
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


class AbstractionManagementService(FoundationServiceBase):
    """
    Abstraction Management Service - Service management for all abstractions
    
    Provides management capabilities for role abstractions across all dimensions.
    
    WHAT (Service Role): I need to handle service management and health monitoring
    HOW (Service Implementation): I provide management capabilities for all abstractions
    """
    
    def __init__(self, validation_utility, serialization_utility, config_utility, health_utility, mcp_utilities, abstraction_creation_service, abstraction_access_service, abstraction_discovery_service):
        """Initialize Abstraction Management Service."""
        super().__init__("abstraction_management")
        
        # Store utilities
        self.validation_utility = validation_utility
        self.serialization_utility = serialization_utility
        self.config_utility = config_utility
        self.health_utility = health_utility
        self.mcp_utilities = mcp_utilities
        
        # Store other services
        self.abstraction_creation_service = abstraction_creation_service
        self.abstraction_access_service = abstraction_access_service
        self.abstraction_discovery_service = abstraction_discovery_service
        
        self.logger.info("🔧 Abstraction Management Service initialized")
    
    async def initialize(self):
        """Initialize the Abstraction Management Service."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Abstraction Management Service...")
            
            self.logger.info("✅ Abstraction Management Service initialized successfully")
            
        except Exception as e:
            self.error_handler.handle_error(e, context="abstraction_management_initialize")
            raise

    # ============================================================================
    # ABSTRACTION MANAGEMENT
    
    def get_management_status(self) -> Dict[str, Any]:
        """Get management service status."""
        try:
            return {
                "service": "abstraction_management",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services_managed": {
                    "abstraction_creation": self.abstraction_creation_service is not None,
                    "abstraction_access": self.abstraction_access_service is not None,
                    "abstraction_discovery": self.abstraction_discovery_service is not None
                },
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": "abstraction_management",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_all_services_health(self) -> Dict[str, Any]:
        """Get health status of all managed services."""
        try:
            health_status = {
                "abstraction_creation": self.abstraction_creation_service.get_creation_status() if self.abstraction_creation_service else {"status": "unavailable"},
                "abstraction_access": self.abstraction_access_service.get_access_status() if self.abstraction_access_service else {"status": "unavailable"},
                "abstraction_discovery": self.abstraction_discovery_service.get_discovery_status() if self.abstraction_discovery_service else {"status": "unavailable"}
            }
            
            return health_status
            
        except Exception as e:
            self.error_handler.handle_error(e, context="get_all_services_health")
            return {"error": str(e)}

    def get_abstraction_statistics(self) -> Dict[str, Any]:
        """Get statistics about all abstractions."""
        try:
            if not self.abstraction_creation_service:
                return {"error": "abstraction_creation_service not available"}
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            
            stats = {
                "total_dimensions": len(role_abstractions),
                "dimensions": {}
            }
            
            for dimension, roles in role_abstractions.items():
                total_abstractions = 0
                for role, abstractions in roles.items():
                    total_abstractions += len(abstractions)
                
                stats["dimensions"][dimension] = {
                    "total_roles": len(roles),
                    "total_abstractions": total_abstractions,
                    "roles": list(roles.keys())
                }
            
            return stats
            
        except Exception as e:
            self.error_handler.handle_error(e, context="get_abstraction_statistics")
            return {"error": str(e)}

    # ============================================================================
    # STATUS AND HEALTH
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            health_status = {
                "service": "abstraction_management",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services_managed": {
                    "abstraction_creation": self.abstraction_creation_service is not None,
                    "abstraction_access": self.abstraction_access_service is not None,
                    "abstraction_discovery": self.abstraction_discovery_service is not None
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "abstraction_management",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
