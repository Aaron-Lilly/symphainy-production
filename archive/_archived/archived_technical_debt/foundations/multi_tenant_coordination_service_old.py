#!/usr/bin/env python3
"""
Multi-Tenant Coordination Service

Handles multi-tenant coordination and tenant management operations.

WHAT (Service Role): I need to handle multi-tenant coordination and tenant management
HOW (Service Implementation): I provide multi-tenant coordination capabilities
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


class MultiTenantCoordinationService(FoundationServiceBase):
    """
    Multi-Tenant Coordination Service - Multi-tenant coordination for all abstractions
    
    Provides multi-tenant coordination capabilities for role abstractions across all dimensions.
    
    WHAT (Service Role): I need to handle multi-tenant coordination and tenant management
    HOW (Service Implementation): I provide multi-tenant coordination capabilities
    """
    
    def __init__(self, validation_utility, serialization_utility, config_utility, health_utility, mcp_utilities):
        """Initialize Multi-Tenant Coordination Service."""
        super().__init__("multi_tenant_coordination")
        
        # Store utilities
        self.validation_utility = validation_utility
        self.serialization_utility = serialization_utility
        self.config_utility = config_utility
        self.health_utility = health_utility
        self.mcp_utilities = mcp_utilities
        
        # Security Guard client for multi-tenant operations
        self.security_guard_client = None
        
        self.logger.info("🏢 Multi-Tenant Coordination Service initialized")
    
    async def initialize(self):
        """Initialize the Multi-Tenant Coordination Service."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Multi-Tenant Coordination Service...")
            
            self.logger.info("✅ Multi-Tenant Coordination Service initialized successfully")
            
        except Exception as e:
            self.error_handler.handle_error(e, context="multi_tenant_coordination_initialize")
            raise

    # ============================================================================
    # MULTI-TENANT COORDINATION
    
    def set_security_guard_client(self, security_guard_client):
        """Set the Security Guard client for multi-tenant operations."""
        self.security_guard_client = security_guard_client
        self.logger.info("Security Guard client set for multi-tenant coordination")

    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information."""
        try:
            if self.security_guard_client:
                # Use Security Guard client if available
                return await self.security_guard_client.get_tenant_info(tenant_id)
            else:
                # Fallback to basic implementation
                return {
                    "tenant_id": tenant_id,
                    "name": f"Tenant {tenant_id}",
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.error_handler.handle_error(e, context="get_tenant_info")
            return {"error": str(e)}

    async def get_tenant_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant usage statistics."""
        try:
            if self.security_guard_client:
                # Use Security Guard client if available
                return await self.security_guard_client.get_tenant_usage_stats(tenant_id)
            else:
                # Fallback to basic implementation
                return {
                    "tenant_id": tenant_id,
                    "usage_stats": {
                        "active_users": 0,
                        "storage_used": 0,
                        "api_calls": 0
                    },
                    "last_updated": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.error_handler.handle_error(e, context="get_tenant_usage_stats")
            return {"error": str(e)}

    async def validate_tenant_access(self, tenant_id: str, user_id: str, resource: str) -> bool:
        """Validate tenant access for a user and resource."""
        try:
            if self.security_guard_client:
                # Use Security Guard client if available
                return await self.security_guard_client.validate_tenant_access(tenant_id, user_id, resource)
            else:
                # Fallback to basic validation
                return tenant_id and user_id and resource is not None
                
        except Exception as e:
            self.error_handler.handle_error(e, context="validate_tenant_access")
            return False

    # ============================================================================
    # STATUS AND HEALTH
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get coordination service status."""
        try:
            return {
                "service": "multi_tenant_coordination",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "security_guard_client_available": self.security_guard_client is not None,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": "multi_tenant_coordination",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            health_status = {
                "service": "multi_tenant_coordination",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "security_guard_client_available": self.security_guard_client is not None
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "multi_tenant_coordination",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }