#!/usr/bin/env python3
"""
Simplified DI Container Service

Simplified DI Container with single registry pattern and single service access pattern.
Maintains backward compatibility while reducing complexity.

WHAT (Infrastructure Kernel Role): I provide dependency injection and service management for all platform services
HOW (Infrastructure Kernel Implementation): I use a single registry pattern with simplified initialization
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import utilities
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
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService


class DIContainerService:
    """
    Simplified DI Container Service - Single Registry Pattern
    
    The DI Container is the infrastructure kernel that provides services to all other services.
    It does not inherit from FoundationServiceBase because it IS the foundation infrastructure.
    
    WHAT (Infrastructure Kernel Role): I provide dependency injection and service management for all platform services
    HOW (Infrastructure Kernel Implementation): I use a single registry pattern with simplified initialization
    """
    
    def __init__(self, realm_name: str, security_provider: Optional[Any] = None, 
                 authorization_guard: Optional[Any] = None):
        """Initialize Simplified DI Container Service."""
        self.realm_name = realm_name
        self.service_name = realm_name  # For backward compatibility
        self.initialization_time = datetime.utcnow()
        
        # Security components (optional)
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        
        # Single unified service registry (simplest possible)
        self.service_registry: Dict[str, Any] = {}
        
        # Initialize basic logging first
        self._logger = logging.getLogger(f"SimplifiedDIContainerService-{realm_name}")
        self._logger.info(f"🚀 Initializing Simplified DI Container Service for {realm_name}...")
        
        # Load environment configuration
        self._load_environment_configuration()
        
        # Initialize utilities
        self._initialize_utilities()
        
        # Initialize Manager Vision support (Public Works, Curator, Platform Gateway)
        self._initialize_manager_vision_support()
        
        self._logger.info(f"✅ Simplified DI Container Service initialized successfully")
    
    def _load_environment_configuration(self):
        """Load environment configuration using UnifiedConfigurationManager."""
        try:
            from utilities.path_utils import get_config_root
            config_root = get_config_root()
            self.config = UnifiedConfigurationManager(service_name=self.realm_name, config_root=str(config_root))
            self.env_config = self.config.config_cache
            self._logger.info(f"✅ Unified configuration loaded: {len(self.env_config)} variables")
        except Exception as e:
            self._logger.error(f"❌ Failed to load unified configuration: {e}")
            self.env_config = {}
    
    def _initialize_utilities(self):
        """Initialize utilities (simplest possible)."""
        try:
            # Direct utilities (no bootstrap needed)
            self.logger = SmartCityLoggingService(self.realm_name)
            self.health = HealthManagementUtility(self.realm_name)
            self.error_handler = SmartCityErrorHandler(self.realm_name)
            self.logging_service_factory = get_logging_service_factory()
            self.error_handler_factory = get_error_handler_factory()
            self.service_type_factory = get_service_type_factory()
            self.tenant = TenantManagementUtility(self.config)
            self.validation = ValidationUtility(self.realm_name)
            self.serialization = SerializationUtility(self.realm_name)
            
            # Bootstrap-aware utilities (bootstrap in initialize() if needed)
            self.telemetry = TelemetryReportingUtility(self.realm_name)
            self.security = SecurityAuthorizationUtility(self.realm_name)
            
            # Bootstrap utilities that need it
            self.telemetry.bootstrap(self)
            self.security.bootstrap(self)
            
            self._logger.info("✅ Utilities initialized")
        except Exception as e:
            self._logger.error(f"❌ Failed to initialize utilities: {e}")
            raise
    
    def _initialize_manager_vision_support(self):
        """Initialize Manager Vision support (Public Works, Curator, Platform Gateway)."""
        try:
            # Initialize Public Works Foundation
            self.public_works_foundation = PublicWorksFoundationService(di_container=self)
            self._logger.info("✅ Public Works Foundation instance created")
            
            # Initialize Curator Foundation
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            self.curator_foundation = CuratorFoundationService(
                foundation_services=self,
                public_works_foundation=self.public_works_foundation
            )
            self._logger.info("✅ Curator Foundation instance created")
            
            # Initialize Platform Infrastructure Gateway
            from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
            self.platform_gateway = PlatformInfrastructureGateway(
                public_works_foundation=self.public_works_foundation,
                di_container=self
            )
            self._logger.info("✅ Platform Infrastructure Gateway initialized")
            
            # Register Platform Gateway in service registry
            self.service_registry["PlatformInfrastructureGateway"] = self.platform_gateway
            
        except Exception as e:
            self._logger.error(f"❌ Failed to initialize Manager Vision support: {e}")
            raise
    
    # ============================================================================
    # SINGLE SERVICE ACCESS PATTERN (Simplified)
    # ============================================================================
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get service by name (single access pattern).
        
        This is the primary method for accessing services.
        All other get_* methods delegate to this.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance or None if not found
        """
        # Check service registry first
        service = self.service_registry.get(service_name)
        if service:
            return service
        
        # Check direct attributes (for backward compatibility)
        if service_name == "PublicWorksFoundationService" and hasattr(self, 'public_works_foundation'):
            return self.public_works_foundation
        
        if service_name == "CuratorFoundationService" or service_name == "curator_foundation":
            return self.curator_foundation
        
        if service_name == "PlatformInfrastructureGateway" or service_name == "PlatformGatewayFoundationService":
            return self.platform_gateway
        
        # Check for other foundation services (lazy initialization)
        if service_name == "EventBusFoundationService" or service_name == "event_bus_foundation":
            return self._get_event_bus_foundation()
        
        if service_name == "MessagingFoundationService" or service_name == "messaging_foundation":
            return self._get_messaging_foundation()
        
        if service_name == "WebSocketFoundationService" or service_name == "websocket_foundation":
            return self._get_websocket_foundation()
        
        return None
    
    def get_foundation_service(self, service_name: str) -> Optional[Any]:
        """
        Get foundation service by name (alias for get_service - backward compatibility).
        
        Args:
            service_name: Name of the foundation service to retrieve
            
        Returns:
            Foundation service instance or None if not found
        """
        return self.get_service(service_name)
    
    def register_service(self, service_name: str, service_instance: Any):
        """
        Register service in the unified registry.
        
        Args:
            service_name: Name of the service
            service_instance: Service instance to register
        """
        self.service_registry[service_name] = service_instance
        self._logger.info(f"✅ Registered service: {service_name}")
    
    # ============================================================================
    # BACKWARD COMPATIBILITY METHODS
    # ============================================================================
    
    def get_public_works_foundation(self) -> PublicWorksFoundationService:
        """Get the Public Works Foundation Service."""
        return self.public_works_foundation
    
    def get_platform_gateway(self):
        """Get the Platform Infrastructure Gateway."""
        return self.platform_gateway
    
    def get_curator_foundation(self):
        """Get the Curator Foundation Service."""
        return self.curator_foundation
    
    @property
    def curator(self):
        """Alias for curator_foundation (backward compatibility)."""
        return self.curator_foundation
    
    def _get_event_bus_foundation(self):
        """Get Event Bus Foundation Service (lazy initialization)."""
        if not hasattr(self, '_event_bus_foundation') or not self._event_bus_foundation:
            from foundations.public_works_foundation.foundation_services.event_bus_foundation_service import EventBusFoundationService
            self._event_bus_foundation = EventBusFoundationService(
                di_container=self,
                public_works_foundation=self.public_works_foundation
            )
        return self._event_bus_foundation
    
    def _get_messaging_foundation(self):
        """Get Messaging Foundation Service (lazy initialization)."""
        if not hasattr(self, '_messaging_foundation') or not self._messaging_foundation:
            from foundations.public_works_foundation.foundation_services.messaging_foundation_service import MessagingFoundationService
            self._messaging_foundation = MessagingFoundationService(
                di_container=self,
                public_works_foundation=self.public_works_foundation
            )
        return self._messaging_foundation
    
    def _get_websocket_foundation(self):
        """Get WebSocket Foundation Service (lazy initialization)."""
        if not hasattr(self, '_websocket_foundation') or not self._websocket_foundation:
            from foundations.public_works_foundation.foundation_services.websocket_foundation_service import WebSocketFoundationService
            self._websocket_foundation = WebSocketFoundationService(
                di_container=self,
                public_works_foundation=self.public_works_foundation
            )
        return self._websocket_foundation
    
    # ============================================================================
    # UTILITY ACCESS METHODS (Backward Compatibility)
    # ============================================================================
    
    def get_utility(self, utility_name: str) -> Any:
        """Get utility by name."""
        utility_map = {
            "logger": self.logger,
            "config": self.config,
            "health": self.health,
            "telemetry": self.telemetry,
            "security": self.security,
            "error_handler": self.error_handler,
            "tenant": self.tenant,
            "validation": self.validation,
            "serialization": self.serialization,
        }
        return utility_map.get(utility_name)
    
    def get_logger(self, service_name: str) -> SmartCityLoggingService:
        """Get a logger instance for a specific service."""
        return SmartCityLoggingService(service_name)
    
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
        """Get the error handler utility."""
        return self.error_handler
    
    def get_tenant(self) -> TenantManagementUtility:
        """Get the tenant management utility."""
        return self.tenant
    
    def get_validation(self) -> ValidationUtility:
        """Get the validation utility."""
        return self.validation
    
    def get_serialization(self) -> SerializationUtility:
        """Get the serialization utility."""
        return self.serialization
    
    # ============================================================================
    # CONFIGURATION METHODS (Backward Compatibility)
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
    
    def get_bool(self, key: str, default: bool = None) -> bool:
        """Get configuration value as boolean."""
        return self.config.get_bool(key, default)
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self.config.get_environment().value if hasattr(self.config, 'get_environment') else "development"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.config.is_development() if hasattr(self.config, 'is_development') else True
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.config.is_production() if hasattr(self.config, 'is_production') else False
    
    # ============================================================================
    # FASTAPI METHODS (for MCP Server support)
    # ============================================================================
    
    def create_fastapi_app(self, title: str = None, version: str = "1.0.0", 
                          description: str = None) -> Any:
        """
        Create a new FastAPI app for MCP servers.
        
        Args:
            title: App title (defaults to "{realm_name} MCP Server")
            version: App version (defaults to "1.0.0")
            description: App description (defaults to "MCP server for {realm_name} operations")
            
        Returns:
            FastAPI app instance
        """
        try:
            from fastapi import FastAPI
            
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
            self._logger.error(f"❌ Failed to create FastAPI app: {e}")
            raise
    
    def get_fastapi_default_config(self) -> Dict[str, Any]:
        """
        Get default FastAPI configuration for MCP servers.
        
        Returns:
            Dictionary with default FastAPI configuration
        """
        return {
            "title": f"{self.realm_name} MCP Server",
            "version": "1.0.0",
            "description": f"MCP server for {self.realm_name} operations",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }


# ============================================================================
# MODULE-LEVEL FUNCTIONS (for backward compatibility)
# ============================================================================

_di_container: Optional[DIContainerService] = None

def get_foundation_services(realm_name: str, security_provider: Optional[Any] = None, 
                          authorization_guard: Optional[Any] = None) -> DIContainerService:
    """Get or create the global DI Container instance."""
    global _di_container
    if _di_container is None:
        _di_container = DIContainerService(
            realm_name=realm_name,
            security_provider=security_provider,
            authorization_guard=authorization_guard
        )
    return _di_container

def create_foundation_services(realm_name: str, security_provider: Optional[Any] = None, 
                              authorization_guard: Optional[Any] = None) -> DIContainerService:
    """Create a new DI Container Service instance."""
    return DIContainerService(
        realm_name=realm_name,
        security_provider=security_provider,
        authorization_guard=authorization_guard
    )
