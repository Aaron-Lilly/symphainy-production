#!/usr/bin/env python3
"""
RealmContext - Unified Dependency Injection for Realm Services

Provides unified dependency injection from Platform Gateway to all realm managers.
Based on CIO's architectural guidance for explicit access patterns.

WHAT (Context Role): I provide unified dependency injection for realm services
HOW (Context Implementation): I inject Platform Gateway, Curator Foundation, and DI Container utilities
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass

if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
    from platform.infrastructure.platform_gateway import PlatformInfrastructureGateway


@dataclass
class RealmContext:
    """
    RealmContext - Unified dependency injection for realm services.
    
    Provides access to Platform Gateway (validated abstraction access), Curator Foundation
    (service discovery), and DI Container utilities for realm services. This is the single 
    context object that gets injected from Platform Gateway to all realm managers.
    
    Key Changes (CIO's Plan):
    - Added realm_name for identification
    - Replaced city_services with platform_gateway (explicit validation)
    - Removed communication (realms use Smart City SOA APIs instead)
    - Kept curator for service discovery
    """
    
    # Core Context
    tenant: str
    realm_name: str  # NEW: Identifies which realm this context belongs to
    logger: logging.Logger
    
    # Platform Services (Injected from Platform Gateway)
    platform_gateway: 'PlatformInfrastructureGateway'  # NEW: Validated abstraction access
    curator: 'CuratorFoundationService'  # Service discovery
    di_container: 'DIContainerService'  # Utilities
    
    # Context Metadata
    created_at: datetime
    context_id: str
    
    def __init__(self, 
                 tenant: str,
                 realm_name: str,  # NEW: Required parameter
                 platform_gateway: 'PlatformInfrastructureGateway',  # NEW: Replaces city_services
                 curator: 'CuratorFoundationService',
                 logger: logging.Logger,
                 di_container: 'DIContainerService',
                 context_id: Optional[str] = None):
        """Initialize RealmContext with platform services."""
        self.tenant = tenant
        self.realm_name = realm_name  # NEW: Store realm name
        self.platform_gateway = platform_gateway  # NEW: Platform Gateway
        self.curator = curator
        self.logger = logger
        self.di_container = di_container
        self.created_at = datetime.utcnow()
        self.context_id = context_id or f"realm_context_{realm_name}_{tenant}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"✅ RealmContext '{self.context_id}' created for realm '{realm_name}' tenant '{tenant}'")
    
    @classmethod
    def create(cls, di_container: 'DIContainerService', realm_name: str, tenant: str = "default") -> 'RealmContext':
        """
        Create RealmContext from DI Container.
        
        This is the factory method that creates a RealmContext by getting all
        required services from the DI Container. This is called by the Platform
        Gateway when injecting context into realm managers.
        
        Args:
            di_container: DI Container service
            realm_name: Name of the realm (required for validation)
            tenant: Tenant identifier
        """
        try:
            # Get logger first
            logger = di_container.get_logger(f"RealmContext-{realm_name}-{tenant}")
            
            # Get Platform Infrastructure Gateway (NEW: replaces SmartCityFoundationGateway)
            platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            if not platform_gateway:
                raise ValueError("PlatformInfrastructureGateway not found in DI Container")
            
            # Get Curator Foundation (for service discovery)
            curator = di_container.get_foundation_service("CuratorFoundationService")
            if not curator:
                raise ValueError("CuratorFoundationService not found in DI Container")
            
            # Create context
            context = cls(
                tenant=tenant,
                realm_name=realm_name,  # NEW: Pass realm name
                platform_gateway=platform_gateway,  # NEW: Use Platform Gateway
                curator=curator,
                logger=logger,
                di_container=di_container
            )
            
            logger.info(f"✅ RealmContext created successfully for realm '{realm_name}' tenant '{tenant}'")
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to create RealmContext: {e}")
            raise
    
    # ============================================================================
    # VALIDATED ABSTRACTION ACCESS METHODS (NEW - Core Functionality)
    # ============================================================================
    
    def get_abstraction(self, abstraction_name: str) -> Any:
        """
        Get infrastructure abstraction with realm validation.
        
        Args:
            abstraction_name: Name of the abstraction to access
            
        Returns:
            Infrastructure abstraction instance
            
        Raises:
            ValueError: If realm doesn't have access to abstraction
        """
        return self.platform_gateway.get_abstraction(self.realm_name, abstraction_name)
    
    def get_all_abstractions(self) -> Dict[str, Any]:
        """
        Bulk load all abstractions allowed for this realm.
        
        Returns:
            Dictionary mapping abstraction names to instances
        """
        return self.platform_gateway.get_all_realm_abstractions(self.realm_name)
    
    def validate_abstraction_access(self, abstraction_name: str) -> bool:
        """
        Validate if realm has access to abstraction (non-throwing).
        
        Args:
            abstraction_name: Name of the abstraction to access
            
        Returns:
            True if realm has access, False otherwise
        """
        return self.platform_gateway.validate_realm_access(self.realm_name, abstraction_name)
    
    def get_realm_capabilities(self) -> Dict[str, Any]:
        """
        Get metadata about realm's allowed abstractions.
        
        Returns:
            Realm capability information
        """
        capability = self.platform_gateway.get_realm_capabilities(self.realm_name)
        if capability:
            return {
                "realm_name": capability.realm_name,
                "abstractions": capability.abstractions,
                "description": capability.description,
                "byoi_support": capability.byoi_support
            }
        return {"error": f"Realm '{self.realm_name}' not found"}
    
    # ============================================================================
    # SMART CITY SOA API ACCESS METHODS (NEW - Core Functionality)
    # ============================================================================
    
    async def get_smart_city_api(self, service_name: str) -> Any:
        """
        Get Smart City SOA API via Curator discovery.
        
        Args:
            service_name: Name of the Smart City service (e.g., "PostOffice", "TrafficCop")
            
        Returns:
            Smart City service instance
            
        Raises:
            ValueError: If service not found
        """
        try:
            # Discover Smart City service via Curator
            service_info = await self.curator.discover_service(service_name)
            if not service_info:
                raise ValueError(f"Smart City service '{service_name}' not found")
            
            # Get service instance (this would be implemented based on Curator's service registry)
            service_instance = await self.curator.get_service_instance(service_name)
            self.logger.debug(f"✅ Retrieved Smart City SOA API: {service_name}")
            return service_instance
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get Smart City SOA API '{service_name}': {e}")
            raise
    
    async def get_post_office_api(self) -> Any:
        """Convenience method to get Post Office SOA API."""
        return await self.get_smart_city_api("PostOffice")
    
    async def get_traffic_cop_api(self) -> Any:
        """Convenience method to get Traffic Cop SOA API."""
        return await self.get_smart_city_api("TrafficCop")
    
    async def get_conductor_api(self) -> Any:
        """Convenience method to get Conductor SOA API."""
        return await self.get_smart_city_api("Conductor")
    
    async def get_librarian_api(self) -> Any:
        """Convenience method to get Librarian SOA API."""
        return await self.get_smart_city_api("Librarian")
    
    async def get_security_guard_api(self) -> Any:
        """Convenience method to get Security Guard SOA API."""
        return await self.get_smart_city_api("SecurityGuard")
    
    # ============================================================================
    # COMMUNICATION METHODS (UPDATED - Use Smart City SOA APIs)
    # ============================================================================
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send message via Post Office SOA API (orchestrated communication).
        
        Args:
            message: Message to send
            
        Returns:
            Result of message sending
        """
        try:
            post_office = await self.get_post_office_api()
            result = await post_office.send_message(message)
            self.logger.info(f"✅ Message sent via Post Office SOA API")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to send message via Post Office: {e}")
            return {"success": False, "error": str(e)}
    
    async def route_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route event via Post Office SOA API (orchestrated communication).
        
        Args:
            event: Event to route
            
        Returns:
            Result of event routing
        """
        try:
            post_office = await self.get_post_office_api()
            result = await post_office.route_event(event)
            self.logger.info(f"✅ Event routed via Post Office SOA API")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to route event via Post Office: {e}")
            return {"success": False, "error": str(e)}
    
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request via Traffic Cop SOA API (orchestrated routing).
        
        Args:
            request: Request to route
            
        Returns:
            Result of request routing
        """
        try:
            traffic_cop = await self.get_traffic_cop_api()
            result = await traffic_cop.route_request(request)
            self.logger.info(f"✅ Request routed via Traffic Cop SOA API")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to route request via Traffic Cop: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start workflow via Conductor SOA API (orchestrated workflows).
        
        Args:
            workflow: Workflow to start
            
        Returns:
            Result of workflow start
        """
        try:
            conductor = await self.get_conductor_api()
            result = await conductor.start_workflow(workflow)
            self.logger.info(f"✅ Workflow started via Conductor SOA API")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to start workflow via Conductor: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # UTILITY ACCESS METHODS (Unchanged)
    # ============================================================================
    
    def get_logger(self, service_name: str) -> logging.Logger:
        """Get logger utility from DI Container."""
        return self.di_container.get_logger(service_name)
    
    def get_config(self) -> Any:
        """Get configuration utility from DI Container."""
        return self.di_container.get_config()
    
    def get_health(self) -> Any:
        """Get health management utility from DI Container."""
        return self.di_container.get_health()
    
    def get_telemetry(self) -> Any:
        """Get telemetry reporting utility from DI Container."""
        return self.di_container.get_telemetry()
    
    def get_security(self) -> Any:
        """Get security authorization utility from DI Container."""
        return self.di_container.get_security()
    
    def get_error_handler(self) -> Any:
        """Get error handler utility from DI Container."""
        return self.di_container.get_error_handler()
    
    def get_tenant_utility(self) -> Any:
        """Get tenant management utility from DI Container."""
        return self.di_container.get_tenant()
    
    def get_validation(self) -> Any:
        """Get validation utility from DI Container."""
        return self.di_container.get_validation()
    
    def get_serialization(self) -> Any:
        """Get serialization utility from DI Container."""
        return self.di_container.get_serialization()
    
    # ============================================================================
    # SERVICE DISCOVERY METHODS (Unchanged)
    # ============================================================================
    
    async def discover_services(self, service_type: str) -> Dict[str, Any]:
        """Discover services via Curator Foundation."""
        try:
            result = await self.curator.discover_services(service_type)
            self.logger.info(f"✅ Discovered {len(result.get('services', []))} services of type '{service_type}'")
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to discover services: {e}")
            return {"services": [], "error": str(e)}
    
    async def register_service(self, service: Any, capability: Dict[str, Any]) -> bool:
        """Register service capability with Curator Foundation."""
        try:
            result = await self.curator.register_service(service, capability)
            self.logger.info(f"✅ Registered service capability: {capability.get('service_name', 'unknown')}")
            return result.get("success", False)
        except Exception as e:
            self.logger.error(f"❌ Failed to register service: {e}")
            return False
    
    # ============================================================================
    # CONTEXT INFORMATION METHODS (Updated)
    # ============================================================================
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get context information for debugging and monitoring."""
        return {
            "context_id": self.context_id,
            "tenant": self.tenant,
            "realm_name": self.realm_name,  # NEW: Include realm name
            "created_at": self.created_at.isoformat(),
            "services_available": {
                "platform_gateway": self.platform_gateway is not None,  # NEW: Platform Gateway
                "curator": self.curator is not None,
                "di_container": self.di_container is not None
            },
            "realm_capabilities": self.get_realm_capabilities(),  # NEW: Realm capabilities
            "utilities_available": [
                "logger", "config", "health", "telemetry",
                "security", "error_handler", "tenant", 
                "validation", "serialization"
            ]
        }
    
    def validate_context(self) -> bool:
        """Validate that all required services are available."""
        try:
            required_services = [
                self.platform_gateway,  # NEW: Platform Gateway
                self.curator,
                self.di_container
            ]
            
            for service in required_services:
                if service is None:
                    self.logger.error("❌ Required service is None in RealmContext")
                    return False
            
            # Validate realm name is provided
            if not self.realm_name:
                self.logger.error("❌ Realm name is required in RealmContext")
                return False
            
            self.logger.info("✅ RealmContext validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ RealmContext validation failed: {e}")
            return False
    
    # ============================================================================
    # MONITORING AND HEALTH METHODS (NEW)
    # ============================================================================
    
    def get_access_metrics(self) -> Dict[str, Any]:
        """Get Platform Gateway access metrics for monitoring."""
        return self.platform_gateway.get_access_metrics()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on RealmContext and Platform Gateway."""
        try:
            # Check Platform Gateway health
            gateway_health = self.platform_gateway.health_check()
            
            # Check context validation
            context_valid = self.validate_context()
            
            return {
                "status": "healthy" if gateway_health["status"] == "healthy" and context_valid else "unhealthy",
                "realm_name": self.realm_name,
                "tenant": self.tenant,
                "context_valid": context_valid,
                "platform_gateway": gateway_health,
                "access_metrics": self.get_access_metrics()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "realm_name": self.realm_name,
                "tenant": self.tenant
            }