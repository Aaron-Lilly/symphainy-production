#!/usr/bin/env python3
"""
Public Works Foundation Service - Coordinator (DI-Based)

Role abstraction mapping service that coordinates 4 focused micro-services
for abstraction creation, access, discovery, and management using dependency injection.

WHAT (Foundation Role): I need to map infrastructure abstractions to role abstractions
HOW (Foundation Service): I coordinate specialized micro-services for comprehensive abstraction management
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Using absolute imports from project root
from foundations.di_container import DIContainerService
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Import micro-services
from .services import (
    AbstractionCreationService,
    AbstractionAccessService,
    AbstractionDiscoveryService,
    AbstractionManagementService,
    MultiTenantCoordinationService
)


class PublicWorksFoundationService:
    """
    Public Works Foundation Service - Role Abstraction Coordinator (DI-Based)
    
    Coordinates 4 specialized micro-services to provide comprehensive abstraction management:
    - AbstractionCreationService: Create role abstractions for all dimensions
    - AbstractionAccessService: Provide access to role abstractions with realm-based patterns
    - AbstractionDiscoveryService: Handle abstraction discovery and listing
    - AbstractionManagementService: Handle service management and health monitoring
    
    WHAT (Foundation Role): I need to map infrastructure abstractions to role abstractions
    HOW (Foundation Service): I coordinate specialized micro-services for comprehensive abstraction management
    """
    
    def __init__(self, foundation_services: DIContainerService, 
                 curator_foundation=None, infrastructure_foundation=None, 
                 env_loader=None, security_guard_client=None):
        """Initialize Public Works Foundation Service with dependency injection."""
        self.service_name = "public_works_foundation"
        self.foundation_services = foundation_services
        
        # Get utilities from foundation services
        self.logger = foundation_services.get_logger(self.service_name)
        self.config = foundation_services.get_config()
        self.health = foundation_services.get_health()
        self.telemetry = foundation_services.get_telemetry()
        self.security = foundation_services.get_security()
        
        # Initialize utilities for micro-services (legacy pattern - will be refactored in micro-services)
        from utilities import (
            ValidationUtility, SerializationUtility, MCPUtilities
        )
        
        self.validation_utility = ValidationUtility("public_works_foundation")
        self.serialization_utility = SerializationUtility("public_works_foundation")
        self.mcp_utilities = MCPUtilities("public_works_foundation")
        
        # Dependencies
        self.curator_foundation = curator_foundation
        self.infrastructure_foundation = infrastructure_foundation
        self.env_loader = env_loader
        self.security_guard_client = security_guard_client
        
        # Initialize micro-services (will be refactored to use DI in future phases)
        self.abstraction_creation = AbstractionCreationService(
            self.validation_utility, self.serialization_utility, self.config,
            self.health, self.mcp_utilities, infrastructure_foundation)
        self.abstraction_access = AbstractionAccessService(
            self.validation_utility, self.serialization_utility, self.config,
            self.health, self.mcp_utilities, self.abstraction_creation)
        self.abstraction_discovery = AbstractionDiscoveryService(
            self.validation_utility, self.serialization_utility, self.config,
            self.health, self.mcp_utilities, self.abstraction_creation)
        self.abstraction_management = AbstractionManagementService(
            self.validation_utility, self.serialization_utility, self.config,
            self.health, self.mcp_utilities, self.abstraction_creation, 
            self.abstraction_access, self.abstraction_discovery)
        
        # Initialize multi-tenant coordination service
        self.multi_tenant_coordination = MultiTenantCoordinationService(
            self.validation_utility, self.serialization_utility, self.config,
            self.health, self.mcp_utilities
        )
        
        self.logger.info("🏛️ Public Works Foundation Service initialized as Role Abstraction Coordinator with Multi-Tenant Coordination (DI-Based)")
    
    async def initialize(self):
        """Initialize the Public Works Foundation Service and all micro-services."""
        try:
            self.logger.info("🚀 Initializing Public Works Foundation Service...")
            
            # Initialize all micro-services
            await self.abstraction_creation.initialize()
            await self.abstraction_access.initialize()
            await self.abstraction_discovery.initialize()
            await self.abstraction_management.initialize()
            await self.multi_tenant_coordination.initialize()
            
            # Bootstrap utilities with Smart City clients if available
            if self.security_guard_client:
                self.security.bootstrap(self, self.security_guard_client)
                self.logger.info("✅ Security authorization utility enhanced with Security Guard client")
            
            self.logger.info("✅ Public Works Foundation Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Public Works Foundation Service: {e}")
            raise
    
    # ============================================================================
    # ABSTRACTION CREATION METHODS
    # ============================================================================
    
    async def create_abstraction(self, abstraction_type: str, abstraction_data: Dict[str, Any], 
                                user_context: UserContext = None) -> Dict[str, Any]:
        """Create a new abstraction."""
        try:
            self.logger.info(f"Creating {abstraction_type} abstraction...")
            
            # Validate user context
            if user_context:
                await self.security.audit_user_action(user_context, "create_abstraction", abstraction_type)
            
            # Create abstraction
            result = await self.abstraction_creation.create_abstraction(
                abstraction_type, abstraction_data, user_context
            )
            
            # Record telemetry
            await self.telemetry.record_metric("abstraction_created", 1, {
                "abstraction_type": abstraction_type,
                "user_id": user_context.user_id if user_context else "system"
            })
            
            self.logger.info(f"✅ {abstraction_type} abstraction created successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create {abstraction_type} abstraction: {e}")
            await self.telemetry.log_anomaly({
                "error": str(e),
                "abstraction_type": abstraction_type,
                "operation": "create_abstraction"
            })
            raise
    
    # ============================================================================
    # ABSTRACTION ACCESS METHODS
    # ============================================================================
    
    async def get_abstraction(self, abstraction_id: str, user_context: UserContext = None) -> Dict[str, Any]:
        """Get an abstraction by ID."""
        try:
            self.logger.info(f"Getting abstraction {abstraction_id}...")
            
            # Validate user context
            if user_context:
                await self.security.audit_user_action(user_context, "get_abstraction", abstraction_id)
            
            # Get abstraction
            result = await self.abstraction_access.get_abstraction(abstraction_id, user_context)
            
            # Record telemetry
            await self.telemetry.record_metric("abstraction_accessed", 1, {
                "abstraction_id": abstraction_id,
                "user_id": user_context.user_id if user_context else "system"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get abstraction {abstraction_id}: {e}")
            await self.telemetry.log_anomaly({
                "error": str(e),
                "abstraction_id": abstraction_id,
                "operation": "get_abstraction"
            })
            raise
    
    # ============================================================================
    # ABSTRACTION DISCOVERY METHODS
    # ============================================================================
    
    async def discover_abstractions(self, filters: Dict[str, Any] = None, 
                                   user_context: UserContext = None) -> List[Dict[str, Any]]:
        """Discover abstractions based on filters."""
        try:
            self.logger.info("Discovering abstractions...")
            
            # Validate user context
            if user_context:
                await self.security.audit_user_action(user_context, "discover_abstractions", "abstraction_registry")
            
            # Discover abstractions
            result = await self.abstraction_discovery.discover_abstractions(filters, user_context)
            
            # Record telemetry
            await self.telemetry.record_metric("abstractions_discovered", len(result), {
                "filter_count": len(filters) if filters else 0,
                "user_id": user_context.user_id if user_context else "system"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to discover abstractions: {e}")
            await self.telemetry.log_anomaly({
                "error": str(e),
                "operation": "discover_abstractions"
            })
            raise
    
    # ============================================================================
    # ABSTRACTION MANAGEMENT METHODS
    # ============================================================================
    
    async def manage_abstraction(self, abstraction_id: str, action: str, 
                                action_data: Dict[str, Any] = None, 
                                user_context: UserContext = None) -> Dict[str, Any]:
        """Manage an abstraction (update, delete, etc.)."""
        try:
            self.logger.info(f"Managing abstraction {abstraction_id} with action {action}...")
            
            # Validate user context
            if user_context:
                await self.security.audit_user_action(user_context, f"manage_abstraction_{action}", abstraction_id)
            
            # Manage abstraction
            result = await self.abstraction_management.manage_abstraction(
                abstraction_id, action, action_data, user_context
            )
            
            # Record telemetry
            await self.telemetry.record_metric("abstraction_managed", 1, {
                "abstraction_id": abstraction_id,
                "action": action,
                "user_id": user_context.user_id if user_context else "system"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to manage abstraction {abstraction_id}: {e}")
            await self.telemetry.log_anomaly({
                "error": str(e),
                "abstraction_id": abstraction_id,
                "action": action,
                "operation": "manage_abstraction"
            })
            raise
    
    # ============================================================================
    # MULTI-TENANT COORDINATION METHODS
    # ============================================================================
    
    async def coordinate_tenant_abstractions(self, tenant_id: str, 
                                           user_context: UserContext = None) -> Dict[str, Any]:
        """Coordinate abstractions for a specific tenant."""
        try:
            self.logger.info(f"Coordinating abstractions for tenant {tenant_id}...")
            
            # Validate user context
            if user_context:
                await self.security.audit_user_action(user_context, "coordinate_tenant_abstractions", tenant_id)
            
            # Coordinate tenant abstractions
            result = await self.multi_tenant_coordination.coordinate_tenant_abstractions(
                tenant_id, user_context
            )
            
            # Record telemetry
            await self.telemetry.record_metric("tenant_abstractions_coordinated", 1, {
                "tenant_id": tenant_id,
                "user_id": user_context.user_id if user_context else "system"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate abstractions for tenant {tenant_id}: {e}")
            await self.telemetry.log_anomaly({
                "error": str(e),
                "tenant_id": tenant_id,
                "operation": "coordinate_tenant_abstractions"
            })
            raise
    
    # ============================================================================
    # HEALTH AND STATUS METHODS
    # ============================================================================
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get the health status of the Public Works Foundation Service."""
        try:
            # Get health from foundation services
            foundation_health = await self.foundation_services.get_container_health()
            
            # Get health from micro-services
            micro_services_health = {
                "abstraction_creation": await self.abstraction_creation.get_service_health(),
                "abstraction_access": await self.abstraction_access.get_service_health(),
                "abstraction_discovery": await self.abstraction_discovery.get_service_health(),
                "abstraction_management": await self.abstraction_management.get_service_health(),
                "multi_tenant_coordination": await self.multi_tenant_coordination.get_service_health()
            }
            
            return {
                "service": self.service_name,
                "status": "healthy",
                "foundation_services": foundation_health,
                "micro_services": micro_services_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the Public Works Foundation Service."""
        return {
            "service": self.service_name,
            "service_type": "PublicWorksFoundationService",
            "architecture": "DI-Based",
            "foundation_services_available": True,
            "micro_services_count": 5,
            "multi_tenant_enabled": True,
            "timestamp": datetime.utcnow().isoformat()
        }

