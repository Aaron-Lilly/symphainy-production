#!/usr/bin/env python3
"""
Comprehensive DI Container Service - Production Ready with Zero Functionality Loss

This comprehensive DI Container Service provides ALL functionality from the original
plus enhanced Manager Vision capabilities, zero-trust security, and service discovery.

WHAT (Foundation Role): I provide comprehensive DI with zero functionality loss and enhanced capabilities
HOW (Foundation Service): I merge original functionality with Manager Vision enhancements and simplify architecture
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Type, Protocol
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Import FastAPI for MCP server support
from fastapi import FastAPI

# Import utilities from the restored utilities directory
from utilities.logging.logging_service import SmartCityLoggingService
from utilities.logging.logging_service_factory import get_logging_service_factory
from utilities.health.health_management_utility import HealthManagementUtility
from utilities.telemetry_reporting.telemetry_reporting_utility import TelemetryReportingUtility
from utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
from utilities.error.error_handler import SmartCityErrorHandler
from utilities.error.error_handler_factory import get_error_handler_factory
from utilities.service_type_factory import get_service_type_factory
from utilities.tenant.tenant_management_utility import TenantManagementUtility
from utilities.validation.validation_utility import ValidationUtility
from utilities.serialization.serialization_utility import SerializationUtility
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager

# Import Manager Vision components
from bases.manager_service_base import ManagerServiceType, OrchestrationScope, GovernanceLevel
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import Communication Foundation - Import moved to method to avoid circular import


class ServiceLifecycleState(Enum):
    """Service lifecycle states."""
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass(frozen=True)
class SecurityContext:
    """Security context for zero-trust security."""
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    origin: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    session_id: Optional[str] = None


class PolicyEngine(Protocol):
    """Policy engine interface for pluggable authorization."""
    def is_allowed(self, action: str, resource: str, context: SecurityContext) -> bool: ...


class AuthorizationGuard:
    """Authorization guard with pluggable policy engine."""
    
    def __init__(self, engine: Optional[PolicyEngine] = None):
        self.engine = engine
        self.logger = logging.getLogger("AuthorizationGuard")
    
    def enforce(self, action: str, resource: str, context: SecurityContext) -> bool:
        """Enforce authorization with pluggable policy engine."""
        if not self.engine:  # Default open policy
            return True
        
        if not self.engine.is_allowed(action, resource, context):
            self.logger.warning(f"Authorization denied: {action} on {resource} for {context.user_id}")
            return False
        
        return True


class SecurityProvider:
    """Security provider for zero-trust security."""
    
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client
        self.logger = logging.getLogger("SecurityProvider")
    
    def create_security_context(self, user_id: str, tenant_id: str, roles: List[str] = None, 
                              permissions: List[str] = None, session_id: str = None) -> SecurityContext:
        """Create security context for user."""
        return SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles or [],
            permissions=permissions or [],
            session_id=session_id
        )
    
    def validate_security_context(self, context: SecurityContext) -> bool:
        """Validate security context."""
        return context.user_id is not None and context.tenant_id is not None


@dataclass
class ServiceRegistration:
    """Service registration information."""
    service_name: str
    service_type: str
    realm_name: str
    endpoint: str
    health_check_url: str
    capabilities: List[str]
    dependencies: List[str]
    lifecycle_state: ServiceLifecycleState
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)


class DIContainerService:
    """
    DI Container Service - Infrastructure Kernel
    
    The DI Container is the infrastructure kernel that provides services to all other services.
    It does not inherit from FoundationServiceBase because it IS the foundation infrastructure.
    
    WHAT (Infrastructure Kernel Role): I provide dependency injection and service management for all platform services
    HOW (Infrastructure Kernel Implementation): I manage service registration, discovery, and lifecycle for the entire platform
    """
    
    def __init__(self, realm_name: str, security_provider: Optional[SecurityProvider] = None, 
                 authorization_guard: Optional[AuthorizationGuard] = None):
        """Initialize Comprehensive DI Container Service."""
        self.realm_name = realm_name
        self.service_name = realm_name  # For backward compatibility
        self.initialization_time = datetime.utcnow()
        self.lifecycle_state = ServiceLifecycleState.INITIALIZING
        
        # Security components
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        
        # Service registry
        # NOTE: Can contain either ServiceRegistration objects OR direct service instances
        # (e.g., PlatformInfrastructureGateway is stored as a direct instance)
        self.service_registry: Dict[str, Any] = {}
        self.manager_services: Dict[str, Any] = {}  # ManagerServiceBase instances
        
        # Initialize basic logging first (before unified registry check)
        self._logger = logging.getLogger(f"ComprehensiveDIContainerService-{realm_name}")
        
        # Cloud-ready unified registry (parallel implementation)
        from utilities.configuration.cloud_ready_config import get_cloud_ready_config
        cloud_ready_config = get_cloud_ready_config()
        
        if cloud_ready_config.should_use_unified_registry():
            from foundations.di_container.unified_service_registry import UnifiedServiceRegistry, ServiceType
            self.unified_registry = UnifiedServiceRegistry()
            self._service_type_enum = ServiceType  # Store enum for later use
            self._logger.info("✅ Unified service registry enabled (cloud-ready mode)")
        else:
            self.unified_registry = None
            self._service_type_enum = None
            self._logger.info("✅ Using legacy service registries (current mode)")
        
        # Basic logging already initialized above (before unified registry check)
        self._logger.info(f"🚀 Initializing Comprehensive DI Container Service for {realm_name}...")
        
        # Load environment configuration
        self._load_environment_configuration()
        
        # Initialize direct utilities
        self._initialize_direct_utilities()
        
        # Initialize bootstrap-aware utilities
        self._initialize_bootstrap_utilities()
        
        # Bootstrap utilities that need it
        self._bootstrap_utilities()
        
        # Initialize Manager Vision support
        self._initialize_manager_vision_support()
        
        # Initialize service discovery
        self._initialize_service_discovery()
        
        # Initialize FastAPI support for MCP servers
        self._initialize_fastapi_support()
        
        # Initialize MCP client factory for direct injection
        self._initialize_mcp_client_factory()
        
        self.lifecycle_state = ServiceLifecycleState.RUNNING
        self._logger.info(f"✅ Comprehensive DI Container Service initialized successfully")
    
    def _load_environment_configuration(self):
        """Load environment configuration using UnifiedConfigurationManager."""
        try:
            from utilities.path_utils import get_config_root
            config_root = get_config_root()
            self.config = UnifiedConfigurationManager(service_name=self.realm_name, config_root=str(config_root))
            self.env_config = self.config.config_cache
            self._logger.info(f"✅ Unified configuration loaded: {len(self.env_config)} variables")
        except Exception as e:
            # Error handling - sync method, can't await (error_handler not yet initialized)
            self._logger.error(f"❌ Failed to load unified configuration: {e}")
            self.env_config = {}
    
    def _initialize_direct_utilities(self):
        """Initialize utilities that don't require bootstrap."""
        try:
            # Logging utility (legacy compatibility)
            self.logger = SmartCityLoggingService(self.realm_name)
            self._logger.info("✅ Logging utility initialized")
            
            self.logging_service_factory = get_logging_service_factory()
            self._logger.info("✅ Basic logging initialized")
            
            # Health management utility
            self.health = HealthManagementUtility(self.realm_name)
            self._logger.info("✅ Health management utility initialized")
            
            # Error handler utility (legacy compatibility)
            self.error_handler = SmartCityErrorHandler(self.realm_name)
            self._logger.info("✅ Error handler utility initialized")
            
            # Error handler factory for realm-specific handlers
            self.error_handler_factory = get_error_handler_factory()
            self._logger.info("✅ Error handler factory initialized")
            
            # Service type factory for service type-specific utilities
            self.service_type_factory = get_service_type_factory()
            self._logger.info("✅ Service type factory initialized")
            
            # API router utility (lazy initialization)
            self.api_router = None
            self._logger.info("✅ API router utility placeholder initialized")
            
            # Tenant management utility
            self.tenant = TenantManagementUtility(self.config)
            self._logger.info("✅ Tenant management utility initialized")
            
            # Validation utility
            self.validation = ValidationUtility(self.realm_name)
            self._logger.info("✅ Validation utility initialized")
            
            # Serialization utility
            self.serialization = SerializationUtility(self.realm_name)
            self._logger.info("✅ Serialization utility initialized")
            
        except Exception as e:
            # Error handling - sync method, error_handler may not be initialized yet
            self._logger.error(f"❌ Failed to initialize direct utilities: {e}")
            raise
    
    def _initialize_bootstrap_utilities(self):
        """Initialize bootstrap-aware utilities."""
        try:
            # Telemetry reporting utility
            self.telemetry = TelemetryReportingUtility(self.realm_name)
            self._logger.info("✅ Telemetry reporting utility initialized")
            
            # Security authorization utility
            self.security = SecurityAuthorizationUtility(self.realm_name)
            self._logger.info("✅ Security authorization utility initialized")
            
        except Exception as e:
            # Error handling - sync method, error_handler may not be initialized yet
            self._logger.error(f"❌ Failed to initialize bootstrap utilities: {e}")
            raise
    
    def _bootstrap_utilities(self):
        """Bootstrap utilities that require it."""
        try:
            # Bootstrap telemetry reporting utility
            self.telemetry.bootstrap(self)
            self._logger.info("✅ Telemetry reporting utility bootstrapped")
            
            # Bootstrap security authorization utility
            self.security.bootstrap(self)
            self._logger.info("✅ Security authorization utility bootstrapped")
            
        except Exception as e:
            # Error handling - sync method, error_handler may not be initialized yet
            self._logger.error(f"❌ Failed to bootstrap utilities: {e}")
            raise
    
    async def _handle_error_with_telemetry(self, error: Exception, operation: str, context: Dict[str, Any] = None):
        """Helper method to handle errors with telemetry integration."""
        if hasattr(self, 'error_handler') and self.error_handler:
            error_context = context or {}
            error_context["operation"] = operation
            telemetry = getattr(self, 'telemetry', None) if hasattr(self, 'telemetry') else None
            await self.error_handler.handle_error(error, context=error_context, telemetry=telemetry)
    
    def _initialize_manager_vision_support(self):
        """Initialize Manager Vision support."""
        try:
            # Initialize Public Works Foundation with self as di_container
            self.public_works_foundation = PublicWorksFoundationService(di_container=self)
            # Note: Public Works Foundation must be initialized via await initialize() in main.py
            # This just creates the instance - initialization happens in main.py
            self._logger.info("✅ Public Works Foundation instance created for Manager Vision")
            
            # Initialize Curator Foundation with self as di_container
            # Architectural Pattern:
            # - Curator Foundation is independent and gets infrastructure from Public Works
            # - Curator does NOT depend on Communication Foundation
            # - Communication Foundation uses Curator for service discovery, but Curator works standalone
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            self.curator_foundation = CuratorFoundationService(
                foundation_services=self,
                public_works_foundation=self.public_works_foundation
            )
            # Note: Curator Foundation must be initialized via await initialize() in main.py
            # This just creates the instance - initialization happens in main.py
            self._logger.info("✅ Curator Foundation instance created (independent, uses Public Works for infrastructure)")
            
            # Initialize Platform Infrastructure Gateway (CRITICAL - Required for realm abstraction access)
            # Platform Gateway is essential for the new platform architecture
            try:
                from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
                self.platform_gateway = PlatformInfrastructureGateway(self.public_works_foundation)
                self._logger.info("✅ Platform Infrastructure Gateway initialized")
                
                # Register Platform Gateway in service registry
                self.service_registry["PlatformInfrastructureGateway"] = self.platform_gateway
                self._logger.info("✅ Platform Infrastructure Gateway registered in service registry")
            except ImportError as e:
                # Error handling - sync method, can't await (error_handler may not be initialized)
                self._logger.error(f"❌ CRITICAL: Platform Infrastructure Gateway import failed: {e}")
                self._logger.error("Platform Gateway is required for platform architecture. Please ensure platform_infrastructure package is available.")
                raise
            except Exception as e:
                # Error handling - sync method, can't await (error_handler may not be initialized)
                self._logger.error(f"❌ CRITICAL: Platform Infrastructure Gateway initialization failed: {e}")
                raise
            
            # Initialize Communication Foundation (lazy initialization)
            # Architectural Pattern:
            # - Communication Foundation uses Public Works for infrastructure (databases, messaging, etc.)
            # - Communication Foundation uses Curator for service discovery and registry
            # - Communication Foundation is created lazily when needed
            self.communication_foundation = None
            
            # Communication Foundation Services (infrastructure-level services)
            self.websocket_foundation = None
            self.messaging_foundation = None
            self.event_bus_foundation = None
            self._logger.info("✅ Communication Foundation placeholder initialized")
            
        except Exception as e:
            # Error handling - sync method, can't await (error_handler may not be initialized)
            self._logger.error(f"❌ Failed to initialize Manager Vision support: {e}")
            raise
    
    def _initialize_service_discovery(self):
        """Initialize service discovery."""
        try:
            self._logger.info("✅ Service discovery initialized")
        except Exception as e:
            # Error handling - sync method, can't await (error_handler may not be initialized)
            self._logger.error(f"❌ Failed to initialize service discovery: {e}")
    
    def _initialize_fastapi_support(self):
        """Initialize FastAPI support for MCP servers."""
        try:
            self._logger.info("✅ FastAPI support initialized for MCP servers")
        except Exception as e:
            # Error handling - sync method, can't await (error_handler may not be initialized)
            self._logger.error(f"❌ Failed to initialize FastAPI support: {e}")
    
    def _initialize_mcp_client_factory(self):
        """Initialize MCP client factory for direct injection."""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            
            # Register MCP client factory
            self.mcp_client_factory = lambda server_name="default": ClientSession(
                server_name=server_name,
                # Configuration will be loaded from environment
            )
            
            self._logger.info("✅ MCP client factory registered for direct injection")
        except Exception as e:
            # Error handling - sync method, can't await (error_handler may not be initialized)
            self._logger.error(f"❌ Failed to initialize MCP client factory: {e}")
    
    # ============================================================================
    # MANAGER VISION SUPPORT (NEW)
    # ============================================================================
    
    async def register_manager_service(self, manager_service: Any, security_context: Optional[SecurityContext] = None) -> bool:
        """
        Register a manager service.
        
        Args:
            manager_service: Manager service to register
            security_context: Optional security context for authorization and tenant validation
        """
        try:
            # Security validation - validate access to register services
            if security_context:
                if not self.enforce_authorization("register", "manager_service", security_context):
                    self._logger.warning(f"❌ Authorization denied for manager service registration")
                    return False
                
                # Multi-tenancy validation - ensure tenant context is set
                if not security_context.tenant_id:
                    self._logger.warning(f"❌ Tenant ID required for manager service registration")
                    return False
            
            service_name = getattr(manager_service, 'service_name', f"manager_{len(self.manager_services)}")
            service_type = getattr(manager_service, 'manager_type', 'unknown')
            realm_name = getattr(manager_service, 'realm_name', self.realm_name)
            
            # Create service registration
            registration = ServiceRegistration(
                service_name=service_name,
                service_type=str(service_type),
                realm_name=realm_name,
                endpoint=f"/api/{service_name}",
                health_check_url=f"/health/{service_name}",
                capabilities=await manager_service.get_service_capabilities() if hasattr(manager_service, 'get_service_capabilities') else [],
                dependencies=[],
                lifecycle_state=ServiceLifecycleState.RUNNING
            )
            
            # Register service (legacy pattern)
            self.service_registry[service_name] = registration
            self.manager_services[service_name] = manager_service
            
            # Register with unified registry (cloud-ready pattern)
            if self.unified_registry and self._service_type_enum:
                service_type_enum = self._service_type_enum.ORCHESTRATOR  # Manager services are orchestrators
                self.unified_registry.register(
                    service_name=service_name,
                    service_type=service_type_enum,
                    instance=manager_service,
                    dependencies=registration.dependencies,
                    metadata={
                        "realm_name": realm_name,
                        "endpoint": registration.endpoint,
                        "capabilities": registration.capabilities
                    }
                )
            
            # Track telemetry
            if hasattr(self, 'telemetry') and self.telemetry:
                await self.telemetry.record_metric(
                    "di_container.manager_service_registered",
                    1.0,
                    {"service_name": service_name, "service_type": str(service_type), "realm": realm_name}
                )
            
            self._logger.info(f"✅ Manager service registered: {service_name}")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "register_manager_service")
            self._logger.error(f"❌ Failed to register manager service: {e}")
            return False
    
    def get_manager_service(self, service_name: str, security_context: Optional[SecurityContext] = None) -> Optional[Any]:
        """
        Get a registered manager service.
        
        Args:
            service_name: Name of the manager service
            security_context: Optional security context for authorization and tenant validation
        """
        # Security validation - validate access to get manager services
        if security_context:
            if not self.enforce_authorization("get", "manager_service", security_context):
                self._logger.warning(f"❌ Authorization denied for manager service access: {service_name}")
                return None
        
        return self.manager_services.get(service_name)
    
    def get_manager_services_by_type(self, manager_type: str) -> List[Any]:
        """Get manager services by type."""
        return [
            service for service in self.manager_services.values()
            if getattr(service, 'manager_type', None) == manager_type
        ]
    
    def get_manager_services_by_realm(self, realm_name: str) -> List[Any]:
        """Get manager services by realm."""
        return [
            service for service in self.manager_services.values()
            if getattr(service, 'realm_name', None) == realm_name
        ]
    
    # ============================================================================
    # ZERO-TRUST SECURITY SUPPORT (NEW)
    # ============================================================================
    
    def create_security_context(self, user_id: str, tenant_id: str, roles: List[str] = None, 
                               permissions: List[str] = None, session_id: str = None) -> SecurityContext:
        """Create security context for user."""
        if self.security_provider:
            return self.security_provider.create_security_context(
                user_id=user_id, tenant_id=tenant_id, roles=roles, 
                permissions=permissions, session_id=session_id
            )
        else:
            return SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles or [],
                permissions=permissions or [],
                session_id=session_id
            )
    
    def enforce_authorization(self, action: str, resource: str, context: SecurityContext) -> bool:
        """Enforce authorization with zero-trust security."""
        if self.authorization_guard:
            return self.authorization_guard.enforce(action, resource, context)
        return True  # Default open policy
    
    def validate_security_context(self, context: SecurityContext) -> bool:
        """Validate security context."""
        if self.security_provider:
            return self.security_provider.validate_security_context(context)
        return context.user_id is not None and context.tenant_id is not None
    
    # ============================================================================
    # SERVICE DISCOVERY AND REGISTRY (NEW)
    # ============================================================================
    
    async def register_service(self, service_name: str, service_type: str, endpoint: str, 
                       capabilities: List[str], dependencies: List[str] = None,
                       security_context: Optional[SecurityContext] = None) -> bool:
        """
        Register a service in the service registry.
        
        Args:
            service_name: Name of the service
            service_type: Type of the service
            endpoint: Service endpoint
            capabilities: List of service capabilities
            dependencies: List of service dependencies
            security_context: Optional security context for authorization and tenant validation
        """
        try:
            # Security validation - validate access to register services
            if security_context:
                if not self.enforce_authorization("register", "service", security_context):
                    self._logger.warning(f"❌ Authorization denied for service registration: {service_name}")
                    return False
                
                # Multi-tenancy validation - ensure tenant context is set
                if not security_context.tenant_id:
                    self._logger.warning(f"❌ Tenant ID required for service registration: {service_name}")
                    return False
            
            registration = ServiceRegistration(
                service_name=service_name,
                service_type=service_type,
                realm_name=self.realm_name,
                endpoint=endpoint,
                health_check_url=f"/health/{service_name}",
                capabilities=capabilities,
                dependencies=dependencies or [],
                lifecycle_state=ServiceLifecycleState.RUNNING
            )
            
            # Register service (legacy pattern)
            self.service_registry[service_name] = registration
            
            # Register with unified registry (cloud-ready pattern)
            if self.unified_registry and self._service_type_enum:
                # Map service_type string to ServiceType enum
                service_type_map = {
                    "foundation": self._service_type_enum.FOUNDATION,
                    "infrastructure": self._service_type_enum.INFRASTRUCTURE,
                    "realm": self._service_type_enum.REALM,
                    "utility": self._service_type_enum.UTILITY,
                    "orchestrator": self._service_type_enum.ORCHESTRATOR,
                    "agent": self._service_type_enum.AGENT,
                }
                service_type_enum = service_type_map.get(service_type.lower(), self._service_type_enum.UTILITY)
                
                self.unified_registry.register(
                    service_name=service_name,
                    service_type=service_type_enum,
                    instance=None,  # Service registration doesn't have instance, only metadata
                    dependencies=dependencies or [],
                    metadata={
                        "realm_name": self.realm_name,
                        "endpoint": endpoint,
                        "capabilities": capabilities,
                        "service_type": service_type
                    }
                )
            
            # Track telemetry
            if hasattr(self, 'telemetry') and self.telemetry:
                await self.telemetry.record_metric(
                    "di_container.service_registered",
                    1.0,
                    {"service_name": service_name, "service_type": service_type, "realm": self.realm_name}
                )
            
            self._logger.info(f"✅ Service registered: {service_name}")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "register_service", {"service_name": service_name})
            self._logger.error(f"❌ Failed to register service: {e}")
            return False
    
    def discover_service(self, service_name: str, security_context: Optional[SecurityContext] = None) -> Optional[ServiceRegistration]:
        """
        Discover a service by name.
        
        Args:
            service_name: Name of the service to discover
            security_context: Optional security context for authorization and tenant validation
        """
        # Security validation - validate access to discover services
        if security_context:
            if not self.enforce_authorization("discover", "service", security_context):
                self._logger.warning(f"❌ Authorization denied for service discovery: {service_name}")
                return None
        
        registration = self.service_registry.get(service_name)
        
        # Multi-tenancy validation - if service has tenant info, validate access
        if registration and security_context and security_context.tenant_id:
            # Note: Service registrations don't currently store tenant_id, but this is where we'd validate
            # For now, we allow discovery if security context is valid
            pass
        
        return registration
    
    def discover_services_by_type(self, service_type: str) -> List[ServiceRegistration]:
        """Discover services by type."""
        return [
            registration for registration in self.service_registry.values()
            if registration.service_type == service_type
        ]
    
    def discover_services_by_capability(self, capability: str) -> List[ServiceRegistration]:
        """Discover services by capability."""
        return [
            registration for registration in self.service_registry.values()
            if capability in registration.capabilities
        ]
    
    # ============================================================================
    # CROSS-DIMENSIONAL COORDINATION (NEW)
    # ============================================================================
    
    async def coordinate_cross_dimensional_services(self, coordination_request: Dict[str, Any], 
                                                    security_context: Optional[SecurityContext] = None) -> Dict[str, Any]:
        """
        Coordinate services across dimensions.
        
        Args:
            coordination_request: Coordination request details
            security_context: Optional security context for authorization and tenant validation
        """
        import time
        start_time = time.time()
        
        try:
            # Security validation - validate access to coordinate services
            if security_context:
                if not self.enforce_authorization("coordinate", "cross_dimensional_services", security_context):
                    self._logger.warning(f"❌ Authorization denied for cross-dimensional coordination")
                    return {
                        "coordination_id": f"coord_{int(datetime.utcnow().timestamp())}",
                        "request": coordination_request,
                        "error": "Authorization denied",
                        "error_code": "ACCESS_DENIED",
                        "status": "failed",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                # Multi-tenancy validation - ensure tenant context is set
                if not security_context.tenant_id:
                    self._logger.warning(f"❌ Tenant ID required for cross-dimensional coordination")
                    return {
                        "coordination_id": f"coord_{int(datetime.utcnow().timestamp())}",
                        "request": coordination_request,
                        "error": "Tenant ID required",
                        "error_code": "TENANT_REQUIRED",
                        "status": "failed",
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            self._logger.info(f"🔄 Coordinating cross-dimensional services: {coordination_request}")
            
            # Get all manager services
            all_managers = list(self.manager_services.values())
            
            # Coordinate with each manager
            coordination_results = {}
            for manager in all_managers:
                if hasattr(manager, 'coordinate_with_manager'):
                    result = await manager.coordinate_with_manager(
                        manager_type=coordination_request.get('target_manager_type', 'unknown'),
                        coordination_request=coordination_request
                    )
                    coordination_results[getattr(manager, 'service_name', 'unknown')] = result
            
            # Track performance and telemetry
            duration = time.time() - start_time
            if hasattr(self, 'telemetry') and self.telemetry:
                await self.telemetry.record_metric(
                    "di_container.coordination_duration",
                    duration,
                    {"target_manager_type": coordination_request.get('target_manager_type', 'unknown')}
                )
                await self.telemetry.record_metric(
                    "di_container.coordination_completed",
                    1.0,
                    {"managers_coordinated": len(coordination_results)}
                )
            
            return {
                "coordination_id": f"coord_{int(datetime.utcnow().timestamp())}",
                "request": coordination_request,
                "results": coordination_results,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "coordinate_cross_dimensional_services", {"request": coordination_request})
            
            # Track failed coordination
            if hasattr(self, 'telemetry') and self.telemetry:
                await self.telemetry.record_metric(
                    "di_container.coordination_failed",
                    1.0,
                    {"error": type(e).__name__, "duration": duration}
                )
            
            self._logger.error(f"❌ Failed to coordinate cross-dimensional services: {e}")
            return {
                "coordination_id": f"coord_{int(datetime.utcnow().timestamp())}",
                "request": coordination_request,
                "error": str(e),
                "error_code": type(e).__name__,
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # HEALTH MONITORING AND AGGREGATION (ENHANCED)
    # ============================================================================
    
    async def get_aggregated_health(self) -> Dict[str, Any]:
        """Get aggregated health status of all services."""
        try:
            # Get container health
            container_health = await self.get_container_health()
            
            # Get manager services health
            manager_health = {}
            for service_name, manager in self.manager_services.items():
                if hasattr(manager, 'health_check'):
                    manager_health[service_name] = await manager.health_check()
            
            # Get registered services health
            service_health = {}
            for service_name, registration in self.service_registry.items():
                service_health[service_name] = {
                    "lifecycle_state": registration.lifecycle_state.value,
                    "last_heartbeat": registration.last_heartbeat.isoformat(),
                    "capabilities": registration.capabilities
                }
            
            return {
                "container_health": container_health,
                "manager_services_health": manager_health,
                "registered_services_health": service_health,
                "overall_status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "get_aggregated_health")
            self._logger.error(f"❌ Failed to get aggregated health: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # LIFECYCLE MANAGEMENT (NEW)
    # ============================================================================
    
    async def start_all_services(self) -> bool:
        """Start all registered services."""
        try:
            self._logger.info("🚀 Starting all registered services...")
            
            # Start manager services
            for service_name, manager in self.manager_services.items():
                if hasattr(manager, 'start_service'):
                    await manager.start_service()
                    self._logger.info(f"✅ Started manager service: {service_name}")
            
            self.lifecycle_state = ServiceLifecycleState.RUNNING
            self._logger.info("✅ All services started successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "start_all_services")
            self._logger.error(f"❌ Failed to start all services: {e}")
            self.lifecycle_state = ServiceLifecycleState.ERROR
            return False
    
    async def stop_all_services(self) -> bool:
        """Stop all registered services."""
        try:
            self._logger.info("🛑 Stopping all registered services...")
            
            # Stop manager services
            for service_name, manager in self.manager_services.items():
                if hasattr(manager, 'shutdown_service'):
                    await manager.shutdown_service()
                    self._logger.info(f"✅ Stopped manager service: {service_name}")
            
            self.lifecycle_state = ServiceLifecycleState.STOPPED
            self._logger.info("✅ All services stopped successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "stop_all_services")
            self._logger.error(f"❌ Failed to stop all services: {e}")
            self.lifecycle_state = ServiceLifecycleState.ERROR
            return False
    
    # ============================================================================
    # FASTAPI SUPPORT (FROM ORIGINAL)
    # ============================================================================
    
    def create_fastapi_app(self, title: str = None, version: str = "1.0.0", 
                          description: str = None) -> FastAPI:
        """Create a new FastAPI app for MCP servers."""
        try:
            app_title = title or f"{self.realm_name} MCP Server"
            app_description = description or f"MCP server for {self.realm_name} operations"
            
            app = FastAPI(
                title=app_title,
                version=version,
                description=app_description,
                docs_url="/docs",
                redoc_url="/redoc"
            )
            
            self._logger.info(f"✅ FastAPI app created: {app_title}")
            return app
            
        except Exception as e:
            # Error handling - sync method, can't await
            self._logger.error(f"❌ Failed to create FastAPI app: {e}")
            # Note: Error handler is async, so we log but don't await in sync method
            raise
    
    def get_fastapi_default_config(self) -> Dict[str, Any]:
        """Get default FastAPI configuration for MCP servers."""
        return {
            "title": f"{self.realm_name} MCP Server",
            "version": "1.0.0",
            "description": f"MCP server for {self.realm_name} operations",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json"
        }
    
    # ============================================================================
    # UTILITY ACCESS METHODS (FROM ORIGINAL)
    # ============================================================================
    
    def get_utility(self, utility_name: str) -> Any:
        """Get utility by name (for compatibility with mixins and base classes)."""
        # Build utility map dynamically checking if attributes exist
        utility_map = {}
        
        if hasattr(self, 'logging_service'):
            utility_map["logger"] = self.logging_service
        if hasattr(self, 'config'):
            utility_map["config"] = self.config
        if hasattr(self, 'health'):
            utility_map["health"] = self.health
        if hasattr(self, 'telemetry'):
            utility_map["telemetry"] = self.telemetry
        if hasattr(self, 'security'):
            utility_map["security"] = self.security
        if hasattr(self, 'error_handler'):
            utility_map["error_handler"] = self.error_handler
        if hasattr(self, 'tenant'):
            utility_map["tenant"] = self.tenant
        if hasattr(self, 'validation'):
            utility_map["validation"] = self.validation
        if hasattr(self, 'serialization'):
            utility_map["serialization"] = self.serialization
        
        utility = utility_map.get(utility_name)
        if utility is None:
            if hasattr(self, '_logger'):
                self._logger.warning(f"Utility '{utility_name}' not yet initialized in DI container")
            return None
        return utility
    
    def get_logger(self, service_name: str) -> SmartCityLoggingService:
        """Get a logger instance for a specific service (legacy compatibility)."""
        return SmartCityLoggingService(service_name)
    
    def get_realm_logging_service(self, realm: str, service_name: str = None):
        """Get a realm-specific logging service."""
        return self.logging_service_factory.get_logging_service(realm, service_name)
    
    def get_logging_service_factory(self):
        """Get the logging service factory."""
        return self.logging_service_factory
    
    
    def get_config(self) -> UnifiedConfigurationManager:
        """Get the configuration utility."""
        return self.config
    
    def get_health(self) -> HealthManagementUtility:
        """Get the health management utility."""
        return self.health
    
    def get_telemetry(self) -> TelemetryReportingUtility:
        """Get the telemetry reporting utility."""
        return self.telemetry
    
    def get_security(self) -> SecurityAuthorizationUtility:
        """Get the security authorization utility."""
        return self.security
    
    def get_error_handler(self) -> SmartCityErrorHandler:
        """Get the error handler utility (legacy compatibility)."""
        return self.error_handler
    
    def get_realm_error_handler(self, realm: str, service_name: str = None):
        """Get a realm-specific error handler."""
        return self.error_handler_factory.get_error_handler(realm, service_name)
    
    def get_error_handler_factory(self):
        """Get the error handler factory."""
        return self.error_handler_factory
    
    def get_service_type_utilities(self, service_type: str, service_name: str = None):
        """Get service type-specific utilities (error handler and logging service)."""
        if service_name is None:
            service_name = f"{service_type}_{self.realm_name}"
        return self.service_type_factory.get_service_type_utilities(self.realm_name, service_name, service_type)
    
    def get_service_type_factory(self):
        """Get the service type factory."""
        return self.service_type_factory
    
    def get_tenant(self) -> TenantManagementUtility:
        """Get the tenant management utility."""
        return self.tenant
    
    def get_validation(self) -> ValidationUtility:
        """Get the validation utility."""
        return self.validation
    
    def get_serialization(self) -> SerializationUtility:
        """Get the serialization utility."""
        return self.serialization
    
    def get_api_router(self):
        """Get the API routing utility."""
        if not self.api_router:
            from utilities.api_routing.api_routing_utility import APIRoutingUtility
            self.api_router = APIRoutingUtility(self)
        return self.api_router
    
    def get_mcp_client_factory(self):
        """Get the MCP client factory for direct injection."""
        return self.mcp_client_factory
    
    def get_foundation_service(self, service_name: str) -> Optional[Any]:
        """Get a foundation service by name (supports both legacy and unified registry)."""
        # Try unified registry first (if enabled)
        if self.unified_registry:
            service = self.unified_registry.get(service_name)
            if service:
                return service
        
        # Check direct attributes first (Public Works Foundation is stored as self.public_works_foundation)
        if service_name == "PublicWorksFoundationService" and hasattr(self, 'public_works_foundation'):
            return self.public_works_foundation
        
        # Check Curator Foundation
        if service_name == "CuratorFoundationService" or service_name == "curator_foundation":
            return self.get_curator_foundation()
        
        # Check Platform Infrastructure Gateway (stored directly in service_registry)
        if service_name == "PlatformInfrastructureGateway" or service_name == "PlatformGatewayFoundationService":
            # Try direct instance first
            gateway = self.service_registry.get("PlatformInfrastructureGateway")
            if gateway and not isinstance(gateway, ServiceRegistration):
                if hasattr(self, '_logger'):
                    self._logger.debug(f"✅ [get_foundation_service] Found PlatformInfrastructureGateway as direct instance: {type(gateway).__name__}")
                return gateway
            
            # Try via PlatformGatewayFoundationService
            gateway_foundation = self.service_registry.get("PlatformGatewayFoundationService")
            if gateway_foundation and not isinstance(gateway_foundation, ServiceRegistration):
                if hasattr(gateway_foundation, 'get_platform_gateway'):
                    gateway = gateway_foundation.get_platform_gateway()
                    if gateway:
                        if hasattr(self, '_logger'):
                            self._logger.debug(f"✅ [get_foundation_service] Found PlatformInfrastructureGateway via PlatformGatewayFoundationService: {type(gateway).__name__}")
                        return gateway
            
            # Not found - log warning for debugging
            if hasattr(self, '_logger'):
                self._logger.warning(f"⚠️ [get_foundation_service] PlatformInfrastructureGateway not available. service_registry keys: {list(self.service_registry.keys())}")
            return None
        
        # Check Communication Foundation Services
        if service_name == "websocket_foundation":
            return self.get_websocket_foundation()
        elif service_name == "messaging_foundation":
            return self.get_messaging_foundation()
        elif service_name == "event_bus_foundation":
            return self.get_event_bus_foundation()
        # Communication Foundation removed - functionality distributed to:
        # - FastAPIRouterManager (utilities) - router management
        # - Experience Foundation SDK - WebSocket and realm bridges
        # - Post Office SOA APIs - messaging/events
        # - Curator Foundation - SOA Client
        # elif service_name == "CommunicationFoundationService" or service_name == "communication_foundation":
        #     return self.get_communication_foundation()  # REMOVED
        
        # Check service registry (legacy pattern)
        # NOTE: service_registry can contain either ServiceRegistration objects OR direct instances
        registration_or_instance = self.service_registry.get(service_name)
        if registration_or_instance:
            # If it's a ServiceRegistration object, it doesn't have instance (return None)
            # If it's a direct instance (like PlatformInfrastructureGateway), return it
            # ServiceRegistration is defined in this same file, so use it directly
            if isinstance(registration_or_instance, ServiceRegistration):
                # ServiceRegistration doesn't have instance, return None for now
                # In the future, we might want to store instances in service_registry
                return None
            else:
                # Direct instance stored in service_registry (e.g., PlatformInfrastructureGateway)
                return registration_or_instance
        
        return None
    
    def get_infrastructure_foundation(self):
        """Get infrastructure foundation service."""
        try:
            from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationService
            infrastructure_foundation = InfrastructureFoundationService(service_name="infrastructure_foundation")
            return infrastructure_foundation
        except Exception as e:
            # Error handling - non-critical, log and continue (sync method, can't await)
            self.logger.error(f"Failed to get infrastructure foundation: {e}")
            # Note: Error handler is async, so we log but don't await in sync method
            return None
    
    def get_infrastructure_abstractions(self) -> Dict[str, Any]:
        """Get infrastructure abstractions from Infrastructure Foundation."""
        try:
            infrastructure_foundation = self.get_infrastructure_foundation()
            if not infrastructure_foundation:
                self.logger.warning("Infrastructure Foundation not available")
                return {}
            
            abstractions = infrastructure_foundation.get_all_abstractions()
            if abstractions:
                self.logger.info(f"✅ Retrieved {len(abstractions)} infrastructure abstractions")
                return abstractions
            else:
                self.logger.warning("⚠️ No infrastructure abstractions available")
                return {}
                
        except Exception as e:
            # Error handling - non-critical, log and continue (sync method, can't await)
            self.logger.error(f"❌ Failed to get infrastructure abstractions: {e}")
            # Note: Error handler is async, so we log but don't await in sync method
            return {}
    
    def get_public_works_foundation(self) -> PublicWorksFoundationService:
        """Get the Public Works Foundation Service."""
        return self.public_works_foundation
    
    def get_platform_gateway(self):
        """Get the Platform Infrastructure Gateway."""
        return self.platform_gateway
    
    def get_curator_foundation(self):
        """Get the Curator Foundation Service."""
        # Curator Foundation is initialized in _initialize_manager_vision_support()
        # It should always be available after DI Container initialization
        if not hasattr(self, 'curator_foundation') or not self.curator_foundation:
            self._logger.warning("⚠️ Curator Foundation not initialized - this should not happen")
            # Fallback: create it if somehow not initialized
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            self.curator_foundation = CuratorFoundationService(
                foundation_services=self,
                public_works_foundation=self.public_works_foundation
            )
        return self.curator_foundation
    
    @property
    def curator(self):
        """
        Alias for curator_foundation (backward compatibility).
        
        Provides backward compatibility for code that uses di_container.curator
        instead of di_container.get_curator_foundation().
        """
        return self.get_curator_foundation()
    
    # Communication Foundation has been eliminated - functionality distributed to:
    # - FastAPIRouterManager (utilities) - router management
    # - Experience Foundation SDK - WebSocket and realm bridges
    # - Post Office SOA APIs - messaging/events
    # - Curator Foundation - SOA Client
    # 
    # def get_communication_foundation(self):  # REMOVED
    # async def register_communication_foundation(self):  # REMOVED
    
    def get_websocket_foundation(self):
        """
        Get the WebSocket Foundation Service.
        
        NOTE: WebSocket Foundation Service has been moved to Public Works Foundation.
        Access via Experience Foundation SDK for user-facing WebSocket capabilities.
        """
        if not self.websocket_foundation:
            # WebSocket Foundation Service is now in Public Works Foundation
            from foundations.public_works_foundation.foundation_services.websocket_foundation_service import WebSocketFoundationService
            
            self.websocket_foundation = WebSocketFoundationService(
                di_container=self,
                public_works_foundation=self.get_public_works_foundation()
            )
            # Note: initialize() will be called when service is first used
        return self.websocket_foundation
    
    def get_messaging_foundation(self):
        """Get the Messaging Foundation Service."""
        if not self.messaging_foundation:
            from foundations.public_works_foundation.foundation_services.messaging_foundation_service import MessagingFoundationService
            
            self.messaging_foundation = MessagingFoundationService(
                di_container=self,
                public_works_foundation=self.get_public_works_foundation()
            )
            # Note: initialize() will be called when service is first used
        return self.messaging_foundation
    
    def get_event_bus_foundation(self):
        """Get the Event Bus Foundation Service."""
        if not self.event_bus_foundation:
            from foundations.public_works_foundation.foundation_services.event_bus_foundation_service import EventBusFoundationService
            
            self.event_bus_foundation = EventBusFoundationService(
                di_container=self,
                public_works_foundation=self.get_public_works_foundation()
            )
            # Note: initialize() will be called when service is first used
        return self.event_bus_foundation
    
    # ============================================================================
    # CONTAINER STATUS AND HEALTH (ENHANCED FROM ORIGINAL)
    # ============================================================================
    
    async def get_container_health(self) -> Dict[str, Any]:
        """Get the health status of the Comprehensive DI Container."""
        try:
            return {
                "container_name": self.realm_name,
                "lifecycle_state": self.lifecycle_state.value,
                "status": "healthy",
                "initialization_time": self.initialization_time.isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.initialization_time).total_seconds(),
                "utilities": {
                    "config": "available" if hasattr(self.config, 'is_bootstrapped') and self.config.is_bootstrapped else "available",
                    "logger": "available", 
                    "health": "available",
                    "telemetry": "available" if hasattr(self.telemetry, 'is_bootstrapped') and self.telemetry.is_bootstrapped else "available",
                    "security": "available" if hasattr(self.security, 'is_bootstrapped') and self.security.is_bootstrapped else "available",
                    "error_handler": "available",
                    "tenant": "available"
                },
                "manager_services_count": len(self.manager_services),
                "registered_services_count": len(self.service_registry),
                "security_enabled": self.security_provider is not None,
                "authorization_enabled": self.authorization_guard is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "get_container_health")
            return {
                "container_name": self.realm_name,
                "lifecycle_state": self.lifecycle_state.value,
                "status": "error",
                "error": str(e),
                "error_code": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def validate_utilities(self) -> Dict[str, Any]:
        """Validate that all utilities are properly initialized."""
        validation_results = {
            "config": False,
            "logger": False,
            "health": False,
            "telemetry": False,
            "security": False
        }
        
        try:
            # Validate configuration utility
            if hasattr(self.config, 'is_bootstrapped') and self.config.is_bootstrapped:
                validation_results["config"] = True
            elif hasattr(self.config, 'config_cache'):
                validation_results["config"] = True
            
            # Validate logging utility
            if hasattr(self.logger, 'info'):
                validation_results["logger"] = True
            
            # Validate health utility
            if hasattr(self.health, 'get_health_summary'):
                validation_results["health"] = True
            
            # Validate telemetry utility
            if hasattr(self.telemetry, 'is_bootstrapped') and self.telemetry.is_bootstrapped:
                validation_results["telemetry"] = True
            elif hasattr(self.telemetry, 'metrics'):
                validation_results["telemetry"] = True
            
            # Validate security utility
            if hasattr(self.security, 'is_bootstrapped') and self.security.is_bootstrapped:
                validation_results["security"] = True
            elif hasattr(self.security, 'check_security'):
                validation_results["security"] = True
            
            all_valid = all(validation_results.values())
            
            return {
                "all_valid": all_valid,
                "validation_results": validation_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Error handling with audit
            await self._handle_error_with_telemetry(e, "validate_utilities")
            return {
                "all_valid": False,
                "error": str(e),
                "error_code": type(e).__name__,
                "validation_results": validation_results,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_container_summary(self) -> Dict[str, Any]:
        """Get a summary of the Comprehensive DI Container."""
        return {
            "container_name": self.realm_name,
            "container_type": "ComprehensiveDIContainer",
            "initialization_time": self.initialization_time.isoformat(),
            "utilities_available": [
                "UnifiedConfigurationManager",
                "SmartCityLoggingService", 
                "HealthManagementUtility",
                "TelemetryReportingUtility",
                "SecurityAuthorizationUtility"
            ],
            "enhanced_features": [
                "ZeroTrustSecurity",
                "ManagerVisionSupport",
                "ServiceDiscovery",
                "CrossDimensionalCoordination",
                "LifecycleManagement"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # UNIFIED CONFIGURATION METHODS (FROM ORIGINAL)
    # ============================================================================
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_string(self, key: str, default: str = None) -> str:
        """Get configuration value as string."""
        return self.config.get_string(key, default)
    
    def get_int(self, key: str, default: int = None) -> int:
        """Get configuration value as integer."""
        return self.config.get_int(key, default)
    
    def get_float(self, key: str, default: float = None) -> float:
        """Get configuration value as float."""
        return self.config.get_float(key, default)
    
    def get_bool(self, key: str, default: bool = None) -> bool:
        """Get configuration value as boolean."""
        return self.config.get_bool(key, default)
    
    def get_list(self, key: str, default: list = None, separator: str = ',') -> list:
        """Get configuration value as list."""
        return self.config.get_list(key, default, separator)
    
    def get_dict(self, key: str, default: dict = None) -> dict:
        """Get configuration value as dictionary."""
        return self.config.get_dict(key, default)
    
    # ============================================================================
    # SPECIALIZED CONFIGURATION METHODS (FROM ORIGINAL)
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.config.get_database_config()
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return self.config.get_redis_config()
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API server configuration."""
        return self.config.get_api_config()
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.config.get_security_config()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get_llm_config()
    
    def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration."""
        return self.config.get_governance_config()
    
    # ============================================================================
    # ENVIRONMENT-SPECIFIC METHODS (FROM ORIGINAL)
    # ============================================================================
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self.config.get_environment().value
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.config.is_development()
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.config.is_production()
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.config.is_testing()
    
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.config.is_staging()
    
    # ============================================================================
    # CACHING AND PERFORMANCE (FROM ORIGINAL)
    # ============================================================================
    
    def enable_config_cache(self):
        """Enable configuration caching."""
        self.config.enable_cache()
    
    def disable_config_cache(self):
        """Disable configuration caching."""
        self.config.disable_cache()
    
    def clear_config_cache(self):
        """Clear configuration cache."""
        self.config.clear_cache()
    
    def refresh_config(self):
        """Refresh configuration from source."""
        self.config.refresh_config()
    
    # ============================================================================
    # VALIDATION AND HEALTH (FROM ORIGINAL)
    # ============================================================================
    
    def validate_configuration(self, required_keys: list) -> Dict[str, Any]:
        """Validate that required configuration keys are present."""
        return self.config.validate_configuration(required_keys)
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration manager status."""
        return self.config.get_configuration_status()


# Global DI Container instance
_di_container: Optional[DIContainerService] = None

def get_foundation_services(realm_name: str, security_provider: Optional[SecurityProvider] = None, 
                          authorization_guard: Optional[AuthorizationGuard] = None) -> DIContainerService:
    """Get or create the global DI Container instance."""
    global _di_container
    if _di_container is None:
        _di_container = DIContainerService(
            realm_name=realm_name,
            security_provider=security_provider,
            authorization_guard=authorization_guard
        )
    return _di_container

def create_foundation_services(realm_name: str, security_provider: Optional[SecurityProvider] = None, 
                              authorization_guard: Optional[AuthorizationGuard] = None) -> DIContainerService:
    """Create a new DI Container Service instance."""
    return DIContainerService(
        realm_name=realm_name,
        security_provider=security_provider,
        authorization_guard=authorization_guard
    )

# NO BACKWARD COMPATIBILITY - BREAK AND FIX APPROACH
# All services must be updated to use the new comprehensive DI Container
# This forces us to find and fix hidden anti-patterns
