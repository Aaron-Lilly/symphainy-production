#!/usr/bin/env python3
"""
Abstraction Access Service

Handles access to role abstractions with realm-based patterns for all dimensions.

WHAT (Service Role): I need to provide access to role abstractions with realm-based patterns
HOW (Service Implementation): I coordinate abstraction access across all dimensions
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


class AbstractionAccessService(FoundationServiceBase):
    """
    Abstraction Access Service - Role abstraction access for all dimensions
    
    Provides access to role abstractions with realm-based patterns that SOA teams
    can consume directly.
    
    WHAT (Service Role): I need to provide access to role abstractions with realm-based patterns
    HOW (Service Implementation): I coordinate abstraction access across all dimensions
    """
    
    def __init__(self, validation_utility, serialization_utility, config_utility, health_utility, mcp_utilities, abstraction_creation_service):
        """Initialize Abstraction Access Service."""
        super().__init__("abstraction_access")
        
        # Store utilities
        self.validation_utility = validation_utility
        self.serialization_utility = serialization_utility
        self.config_utility = config_utility
        self.health_utility = health_utility
        self.mcp_utilities = mcp_utilities
        self.abstraction_creation_service = abstraction_creation_service
        
        self.logger.info("🔍 Abstraction Access Service initialized")
    
    async def initialize(self):
        """Initialize the Abstraction Access Service."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Abstraction Access Service...")
            
            self.logger.info("✅ Abstraction Access Service initialized successfully")
            
        except Exception as e:
            self.error_handler.handle_error(e, context="abstraction_access_initialize")
            raise

    # ============================================================================
    # ABSTRACTION ACCESS
    
    def get_abstraction_for_role(self, dimension: str, role: str, abstraction_name: str) -> Optional[Any]:
        """Get a specific abstraction for a role."""
        try:
            if not self.abstraction_creation_service:
                return None
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            if dimension not in role_abstractions:
                return None
            
            if role not in role_abstractions[dimension]:
                return None
            
            return role_abstractions[dimension][role].get(abstraction_name)
            
        except Exception as e:
            self.error_handler.handle_error(e, context="get_abstraction_for_role")
            return None

    def get_all_abstractions_for_role(self, dimension: str, role: str) -> Dict[str, Any]:
        """Get all abstractions for a role."""
        try:
            if not self.abstraction_creation_service:
                return {}
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            if dimension not in role_abstractions:
                return {}
            
            if role not in role_abstractions[dimension]:
                return {}
            
            return role_abstractions[dimension][role].copy()
            
        except Exception as e:
            self.error_handler.handle_error(e, context="get_all_abstractions_for_role")
            return {}
    
    # ============================================================================
    # DIMENSION-SPECIFIC ABSTRACTION ACCESS METHODS
    # ============================================================================
    
    async def get_smart_city_abstractions(self, role: str) -> Dict[str, Any]:
        """Get Smart City abstractions for a role."""
        return self.get_all_abstractions_for_role("smart_city", role)
    
    async def get_agentic_abstractions(self, role: str = None) -> Dict[str, Any]:
        """Get agentic abstractions for a role or all agentic abstractions."""
        if role:
            return self.get_all_abstractions_for_role("agentic", role)
        else:
            # Return all agentic abstractions
            return {
                "orchestrator": self.get_all_abstractions_for_role("agentic", "orchestrator"),
                "coordinator": self.get_all_abstractions_for_role("agentic", "coordinator"),
                "executor": self.get_all_abstractions_for_role("agentic", "executor")
            }
    
    async def get_business_abstractions(self, pillar: str) -> Dict[str, Any]:
        """Get business abstractions for a pillar."""
        return self.get_all_abstractions_for_role("business_pillars", pillar)
    
    async def get_experience_abstractions(self, component: str) -> Dict[str, Any]:
        """Get experience abstractions for a component."""
        return self.get_all_abstractions_for_role("experience", component)
    
    async def get_orchestration_abstractions(self, role: str) -> Dict[str, Any]:
        """Get orchestration abstractions (alias for agentic abstractions)."""
        return await self.get_agentic_abstractions(role)
    
    async def get_role_abstraction(self, dimension: str, role: str, abstraction_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific role abstraction."""
        try:
            role_abstractions = self.get_all_abstractions_for_role(dimension, role)
            return role_abstractions.get(abstraction_name)
        except Exception as e:
            self.logger.error(f"Failed to get abstraction {abstraction_name} for role {role} in dimension {dimension}: {e}")
            return None

    def list_available_abstractions(self, dimension: str = None) -> Dict[str, Any]:
        """List all available abstractions, optionally filtered by dimension."""
        try:
            if not self.abstraction_creation_service:
                return {}
            
            role_abstractions = self.abstraction_creation_service.role_abstractions
            
            if dimension:
                return {dimension: role_abstractions.get(dimension, {})}
            else:
                return role_abstractions.copy()
                
        except Exception as e:
            self.error_handler.handle_error(e, context="list_available_abstractions")
            return {}

    # ============================================================================
    # STATUS AND HEALTH
    
    def get_access_status(self) -> Dict[str, Any]:
        """Get access service status."""
        try:
            return {
                "service": "abstraction_access",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "abstraction_creation_available": self.abstraction_creation_service is not None,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": "abstraction_access",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            health_status = {
                "service": "abstraction_access",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "abstraction_creation_available": self.abstraction_creation_service is not None
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "abstraction_access",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
