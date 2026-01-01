#!/usr/bin/env python3
"""
Realm Service Base - Unified Base for All Realm Services

This base class provides everything realm services need to operate (except managers, agents, MCP servers).
Built on top of RealmBase with Communication Foundation integration.

WHAT (Realm Service Role): I provide everything realm services need to operate
HOW (Realm Service Implementation): I inherit from RealmBase and add realm service-specific capabilities
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

# Import RealmBase
from bases.realm_base import RealmBase

# Import DI Container (using TYPE_CHECKING to avoid circular import)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService


class RealmServiceBase(RealmBase):
    """
    Realm Service Base - Unified Base for All Realm Services
    
    This base class provides everything realm services need to operate (except managers, agents, MCP servers).
    Built on top of RealmBase with Communication Foundation integration.
    
    WHAT (Realm Service Role): I provide everything realm services need to operate
    HOW (Realm Service Implementation): I inherit from RealmBase and add realm service-specific capabilities
    """
    
    def __init__(self, service_name: str, di_container: "DIContainerService",
                 realm_name: str, service_type: str,
                 security_provider=None, authorization_guard=None,
                 communication_foundation: Optional["CommunicationFoundationService"] = None):
        """Initialize RealmServiceBase with enhanced capabilities."""
        # Initialize RealmBase
        super().__init__(
            service_name=service_name,
            di_container=di_container,
            realm_name=realm_name,
            service_type=service_type,
            security_provider=security_provider,
            authorization_guard=authorization_guard,
            communication_foundation=communication_foundation
        )
        
        # Realm service-specific properties
        self.service_capabilities = []
        self.business_operations = {}
        self.realm_integrations = {}
        
        # Initialize realm service-specific capabilities
        self._initialize_realm_service_capabilities()
        
        self.logger.info(f"🌐 RealmServiceBase '{service_name}' initialized for realm '{realm_name}' with enhanced capabilities")
    
    def _initialize_realm_service_capabilities(self):
        """Initialize realm service-specific capabilities."""
        # Business operations
        self._initialize_business_operations()
        
        # Realm integrations
        self._initialize_realm_integrations()
        
        # Service-specific utilities
        self._initialize_service_utilities()
    
    def _initialize_business_operations(self):
        """Initialize business operations for this realm service."""
        # This will be implemented by concrete realm services
        pass
    
    def _initialize_realm_integrations(self):
        """Initialize realm integrations for this realm service."""
        # This will be implemented by concrete realm services
        pass
    
    def _initialize_service_utilities(self):
        """Initialize service-specific utilities."""
        # This will be implemented by concrete realm services
        pass
    
    # ============================================================================
    # BUSINESS OPERATIONS
    # ============================================================================
    
    async def execute_business_operation(self, operation_name: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a business operation."""
        try:
            self.logger.info(f"🏢 Executing business operation: {operation_name}")
            
            # Execute business operation
            operation_result = await self._execute_business_operation(operation_name, operation_data)
            
            self.logger.info(f"✅ Business operation '{operation_name}' executed successfully")
            return {
                "success": True,
                "operation_name": operation_name,
                "operation_result": operation_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute business operation '{operation_name}': {e}")
            return {
                "success": False,
                "operation_name": operation_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_business_operation(self, operation_name: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute business operation (to be implemented by concrete services)."""
        # This will be implemented by concrete realm services
        return {
            "operation_name": operation_name,
            "status": "executed",
            "realm": self.realm_name,
            "service": self.service_name
        }
    
    # ============================================================================
    # REALM INTEGRATIONS
    # ============================================================================
    
    async def integrate_with_realm(self, target_realm: str, integration_request: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with another realm."""
        try:
            self.logger.info(f"🔗 Integrating with realm: {target_realm}")
            
            # Use Communication Foundation for inter-realm communication
            if self.communication_foundation:
                integration_result = await self.communication_foundation.communicate_with_realm(
                    source_realm=self.realm_name,
                    target_realm=target_realm,
                    integration_request=integration_request
                )
                
                self.logger.info(f"✅ Integration with realm '{target_realm}' successful")
                return integration_result
            else:
                self.logger.warning("⚠️ Communication Foundation not available")
                return {"error": "Communication Foundation not available"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to integrate with realm '{target_realm}': {e}")
            return {"error": str(e)}
    
    async def coordinate_with_service(self, target_service: str, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with another service."""
        try:
            self.logger.info(f"🤝 Coordinating with service: {target_service}")
            
            # Use Communication Foundation for service coordination
            if self.communication_foundation:
                coordination_result = await self.communication_foundation.coordinate_with_service(
                    source_service=self.service_name,
                    target_service=target_service,
                    coordination_request=coordination_request
                )
                
                self.logger.info(f"✅ Coordination with service '{target_service}' successful")
                return coordination_result
            else:
                self.logger.warning("⚠️ Communication Foundation not available")
                return {"error": "Communication Foundation not available"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate with service '{target_service}': {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # SERVICE CAPABILITIES
    # ============================================================================
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities."""
        return {
            "service_name": self.service_name,
            "realm": self.realm_name,
            "service_type": self.service_type,
            "capabilities": self.service_capabilities,
            "business_operations": list(self.business_operations.keys()),
            "realm_integrations": list(self.realm_integrations.keys()),
            "soa_endpoints": len(self.soa_endpoints),
            "communication_foundation_available": self.communication_foundation is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            # Get base health from RealmBase
            base_health = await super().get_health_with_realm_context()
            
            # Add realm service-specific health
            service_health = {
                "service_type": self.service_type,
                "business_operations_count": len(self.business_operations),
                "realm_integrations_count": len(self.realm_integrations),
                "service_capabilities_count": len(self.service_capabilities),
                "status": "healthy"
            }
            
            return {**base_health, **service_health}
            
        except Exception as e:
            return {
                "service_name": self.service_name,
                "realm": self.realm_name,
                "service_type": self.service_type,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # ABSTRACT METHODS (to be implemented by concrete realm services)
    # ============================================================================
    
    @abstractmethod
    async def initialize(self):
        """Initialize the realm service."""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Shutdown the realm service."""
        pass
    
    @abstractmethod
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get realm-specific capabilities for this service."""
        pass
