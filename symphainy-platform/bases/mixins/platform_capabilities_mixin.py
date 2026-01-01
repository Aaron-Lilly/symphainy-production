#!/usr/bin/env python3
"""
Platform Capabilities Mixin

Focused mixin for platform capabilities - extracts SOA communication and service
discovery functionality from base classes into a reusable, testable component.

WHAT (Platform Capabilities Role): I provide SOA communication and service discovery patterns
HOW (Platform Capabilities Mixin): I centralize platform orchestration and service coordination
"""

from typing import Dict, Any, Optional


class PlatformCapabilitiesMixin:
    """
    Mixin for platform capabilities and service orchestration patterns.
    
    Provides consistent SOA communication, service discovery, and capability
    registry access across all services with proper error handling.
    """
    
    def _init_platform_capabilities(self, di_container: Any):
        """Initialize platform capabilities patterns."""
        if not di_container:
            raise ValueError(
                "DI Container is required for PlatformCapabilitiesMixin initialization. "
                "Services must be created with a valid DI Container instance."
            )
        
        self.di_container = di_container
        
        # Get logger from DI Container (should be available - DI Container initializes logging in __init__)
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError(
                f"DI Container does not have get_logger method. "
                f"This indicates a platform initialization failure or incorrect DI Container instance."
            )
        
        try:
            # Use DI Container's get_logger method to create logger for this mixin
            logger_service = di_container.get_logger(f"{self.__class__.__name__}.platform_capabilities")
            if not logger_service:
                raise RuntimeError(
                    f"DI Container.get_logger() returned None. "
                    f"Logging service should be available - this indicates a platform initialization failure."
                )
            # SmartCityLoggingService has .logger attribute and methods like .info(), .error(), etc.
            self.logger = logger_service
        except Exception as e:
            raise RuntimeError(
                f"Failed to get logger from DI Container: {e}. "
                f"DI Container must initialize logging utility before services can use it. "
                f"This indicates a platform initialization failure."
            ) from e
        
        # Platform capabilities (initialized when available)
        self.soa_client = None
        self.service_discovery = None
        self.capability_registry = None
        self._curator = None  # Curator Foundation for Smart City service discovery
        self._smart_city_services = {}  # Cache for discovered Smart City services
        self._enabling_services = {}  # Cache for discovered Business Enablement enabling services
        
        self.logger.debug("Platform capabilities mixin initialized")
    
    def get_soa_client(self) -> Optional[Any]:
        """Get SOA client for service communication."""
        if not self.soa_client:
            try:
                # Try to get SOA client from DI container
                self.soa_client = self.di_container.get_utility("soa_client")
            except Exception as e:
                self.logger.debug(f"SOA client not available: {e}")
        
        return self.soa_client
    
    def get_service_discovery(self) -> Optional[Any]:
        """Get service discovery for service location."""
        if not self.service_discovery:
            try:
                # Try to get service discovery from DI container
                self.service_discovery = self.di_container.get_utility("service_discovery")
            except Exception as e:
                self.logger.debug(f"Service discovery not available: {e}")
        
        return self.service_discovery
    
    def get_capability_registry(self) -> Optional[Any]:
        """Get capability registry for service capabilities."""
        if not self.capability_registry:
            try:
                # Try to get capability registry from DI container
                self.capability_registry = self.di_container.get_utility("capability_registry")
            except Exception as e:
                self.logger.debug(f"Capability registry not available: {e}")
        
        return self.capability_registry
    
    def get_curator(self) -> Optional[Any]:
        """Get Curator Foundation for Smart City service discovery."""
        if not self._curator:
            try:
                # Get Curator Foundation from DI container
                self._curator = self.di_container.get_foundation_service("CuratorFoundationService")
                if self._curator:
                    self.logger.debug("✅ Curator Foundation available for Smart City discovery")
            except Exception as e:
                self.logger.debug(f"Curator Foundation not available: {e}")
        
        return self._curator
    
    async def get_smart_city_api(self, service_name: str) -> Optional[Any]:
        """
        Get Smart City SOA API via Curator discovery with lazy initialization.
        
        Args:
            service_name: Name of Smart City service (e.g., "SecurityGuard", "TrafficCop", "Conductor", "PostOffice", "Librarian")
            
        Returns:
            Smart City service instance or None if not found
        """
        try:
            # Check cache first
            if service_name in self._smart_city_services:
                return self._smart_city_services[service_name]
            
            # Get Curator Foundation
            curator = self.get_curator()
            if not curator:
                self.logger.warning(f"⚠️ Curator not available - cannot discover {service_name}")
                return None
            
            # Check if service is registered with Curator
            # Curator stores services in registered_services dict with service_name as key
            # Also check for service_name + "Service" pattern (e.g., "ContentStewardService")
            service_name_variants = [service_name, f"{service_name}Service", service_name.lower()]
            
            # Map Curator service name to City Manager service_name
            service_name_mapping = {
                "TrafficCop": "traffic_cop",
                "SecurityGuard": "security_guard",
                "Nurse": "nurse",
                "Librarian": "librarian",
                "DataSteward": "data_steward",
                "ContentSteward": "content_steward",
                "PostOffice": "post_office",
                "Conductor": "conductor",
            }
            
            # Check Curator's registered_services dict directly
            service_found = False
            service_instance = None
            
            for variant in service_name_variants:
                service_registration = curator.registered_services.get(variant)
                if service_registration:
                    service_instance = service_registration.get("service_instance")
                    if service_instance:
                        service_found = True
                        break
            
            # If service not found, try lazy initialization via City Manager
            if not service_found:
                self.logger.info(f"🔄 Smart City service '{service_name}' not in Curator - attempting lazy initialization")
                
                # Get City Manager (avoid recursion by checking if it's CityManager itself)
                if service_name == "CityManager":
                    # CityManager should be EAGER and already registered
                    self.logger.warning(f"⚠️ CityManager not found in Curator - it should be EAGER")
                    return None
                
                # Get City Manager from DI container or Curator (avoid recursion)
                city_manager = None
                try:
                    # Try to get from DI container first (CityManager is EAGER)
                    city_manager = self.di_container.get_foundation_service("CityManagerService")
                    if not city_manager:
                        # Try Curator (but avoid recursion)
                        city_manager_registration = curator.registered_services.get("CityManager")
                        if city_manager_registration:
                            city_manager = city_manager_registration.get("service_instance")
                except Exception as e:
                    self.logger.debug(f"Could not get CityManager: {e}")
                
                if not city_manager:
                    self.logger.warning(f"⚠️ City Manager not available - cannot lazy-initialize {service_name}")
                    return None
                
                # Map service name to City Manager service_name
                city_manager_service_name = service_name_mapping.get(service_name)
                if not city_manager_service_name:
                    self.logger.warning(f"⚠️ Unknown Smart City service: {service_name}")
                    return None
                
                # Lazy initialize via City Manager's orchestrate_realm_startup
                if hasattr(city_manager, 'realm_orchestration_module'):
                    result = await city_manager.realm_orchestration_module.orchestrate_realm_startup(
                        services=[city_manager_service_name]
                    )
                    
                    if result.get("success"):
                        # Service should now be in Curator registry - try again
                        for variant in service_name_variants:
                            service_registration = curator.registered_services.get(variant)
                            if service_registration:
                                service_instance = service_registration.get("service_instance")
                                if service_instance:
                                    service_found = True
                                    break
                    else:
                        error_msg = result.get("error", "Unknown error")
                        self.logger.warning(f"⚠️ Failed to lazy-initialize {service_name}: {error_msg}")
                        return None
                else:
                    self.logger.warning(f"⚠️ City Manager does not have realm_orchestration_module")
                    return None
            
            # Return service instance if found
            if service_found and service_instance:
                # Cache for performance
                self._smart_city_services[service_name] = service_instance
                self.logger.debug(f"✅ Discovered Smart City service: {service_name}")
                return service_instance
            else:
                self.logger.warning(f"⚠️ Service '{service_name}' not found in Curator registered_services (checked variants: {service_name_variants})")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get Smart City API '{service_name}': {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def get_enabling_service(self, service_name: str) -> Optional[Any]:
        """
        Get Business Enablement enabling service via Curator discovery.
        
        Similar to get_smart_city_api(), but for business_enablement realm services.
        Enabling services are shared services that provide atomic capabilities
        (e.g., file_parser_service, data_analyzer_service, semantic_enrichment_gateway).
        
        Args:
            service_name: Name of enabling service (e.g., "file_parser_service", "data_analyzer_service")
            
        Returns:
            Enabling service instance or None if not found
        """
        try:
            # Check cache first
            if service_name in self._enabling_services:
                return self._enabling_services[service_name]
            
            # Get Curator Foundation
            curator = self.get_curator()
            if not curator:
                self.logger.warning(f"⚠️ Curator not available - cannot discover {service_name}")
                return None
            
            # Service name variants (enabling services use snake_case with _service suffix)
            service_name_variants = [
                service_name,
                f"{service_name}Service",
                service_name.replace("_service", "").replace("_", "").title() + "Service",
                service_name.replace("_", "").title() + "Service"
            ]
            
            # Check Curator's registered_services dict directly
            service_found = False
            service_instance = None
            
            for variant in service_name_variants:
                service_registration = curator.registered_services.get(variant)
                if service_registration:
                    # Check if service is from business_enablement realm
                    service_realm = service_registration.get("realm_name", "")
                    if service_realm == "business_enablement":
                        service_instance = service_registration.get("service_instance")
                        if service_instance:
                            service_found = True
                            break
            
            # Return service instance if found
            if service_found and service_instance:
                # Cache for performance
                self._enabling_services[service_name] = service_instance
                self.logger.debug(f"✅ Discovered enabling service: {service_name}")
                return service_instance
            else:
                self.logger.debug(f"⚠️ Enabling service '{service_name}' not found in Curator (checked variants: {service_name_variants})")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get enabling service '{service_name}': {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def discover_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Discover service using service discovery."""
        try:
            service_discovery = self.get_service_discovery()
            if service_discovery:
                return await service_discovery.discover_service(service_name)
            else:
                self.logger.warning(f"Service discovery not available for {service_name}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to discover service {service_name}: {e}")
            return None
    
    async def register_capability(self, capability_name: str, capability_data: Dict[str, Any]) -> bool:
        """Register service capability."""
        try:
            capability_registry = self.get_capability_registry()
            if capability_registry:
                return await capability_registry.register_capability(capability_name, capability_data)
            else:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"Capability registry not available for {capability_name}")
                return False
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Failed to register capability {capability_name}: {e}")
            return False
    
    async def get_capability(self, capability_name: str) -> Optional[Dict[str, Any]]:
        """Get service capability."""
        try:
            capability_registry = self.get_capability_registry()
            if capability_registry:
                return await capability_registry.get_capability(capability_name)
            else:
                self.logger.warning(f"Capability registry not available for {capability_name}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get capability {capability_name}: {e}")
            return None
    
    async def send_soa_message(self, service_name: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message via SOA client."""
        try:
            soa_client = self.get_soa_client()
            if soa_client:
                return await soa_client.send_message(service_name, message)
            else:
                self.logger.warning(f"SOA client not available for {service_name}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to send SOA message to {service_name}: {e}")
            return None
    
    async def orchestrate_services(self, orchestration_request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate multiple services for complex workflows."""
        try:
            # This would be implemented by specific services that need orchestration
            # The mixin provides the foundation for service coordination
            self.logger.info(f"Orchestrating services: {orchestration_request}")
            
            # Placeholder for orchestration logic
            return {
                "status": "orchestration_started",
                "request": orchestration_request,
                "timestamp": "2024-10-28T00:00:00Z"
            }
            
        except Exception as e:
            self.logger.error(f"Service orchestration failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def is_platform_capability_available(self, capability: str) -> bool:
        """Check if specific platform capability is available."""
        capabilities = {
            "soa_client": self.get_soa_client() is not None,
            "service_discovery": self.get_service_discovery() is not None,
            "capability_registry": self.get_capability_registry() is not None,
            "curator": self.get_curator() is not None
        }
        
        return capabilities.get(capability, False)

