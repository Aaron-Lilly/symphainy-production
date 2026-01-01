#!/usr/bin/env python3
"""
Service Type Factory

Factory for creating service type-specific error handlers and logging services.
Provides centralized creation and management of service type-specific utilities.

WHAT (Utility Role): I provide centralized service type-specific utility creation and management
HOW (Utility Implementation): I create service type-specific error handlers and logging services with proper configuration
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .error.service_type_error_handler import ServiceTypeErrorHandler, ServiceType as ErrorServiceType
from .logging.service_type_logging_service import ServiceTypeLoggingService, ServiceType as LoggingServiceType
from .error.error_handler_factory import get_error_handler_factory
from .logging.logging_service_factory import get_logging_service_factory


class ServiceTypeFactory:
    """
    Factory for creating service type-specific utilities.
    
    Provides centralized creation and management of service type-specific error handlers and logging services.
    """
    
    def __init__(self):
        """Initialize service type factory."""
        self.logger = logging.getLogger("ServiceTypeFactory")
        
        # Get factories
        self.error_handler_factory = get_error_handler_factory()
        self.logging_service_factory = get_logging_service_factory()
        
        # Cache of created service type utilities
        self.service_type_cache: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("✅ Service Type Factory initialized")
    
    def create_service_type_utilities(self, realm: str, service_name: str, service_type: str) -> Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]:
        """
        Create service type-specific error handler and logging service.
        
        Args:
            realm: The realm name
            service_name: The service name
            service_type: The service type (service, agent, mcp_server, foundation_service)
            
        Returns:
            Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]: The created utilities
            
        Raises:
            ValueError: If service type is not supported
        """
        try:
            # Validate service type
            if service_type not in ["service", "agent", "mcp_server", "foundation_service"]:
                raise ValueError(f"Unsupported service type: {service_type}. Supported types: service, agent, mcp_server, foundation_service")
            
            # Check cache first
            cache_key = f"{realm}:{service_name}:{service_type}"
            if cache_key in self.service_type_cache:
                self.logger.debug(f"✅ Returning cached service type utilities for {cache_key}")
                cached = self.service_type_cache[cache_key]
                return cached["error_handler"], cached["logging_service"]
            
            # Create realm-specific error handler and logging service
            realm_error_handler = self.error_handler_factory.get_error_handler(realm, service_name)
            realm_logging_service = self.logging_service_factory.get_logging_service(realm, service_name)
            
            # Create service type-specific utilities
            error_handler = ServiceTypeErrorHandler(realm_error_handler)
            logging_service = ServiceTypeLoggingService(realm_logging_service)
            
            # Cache the utilities
            self.service_type_cache[cache_key] = {
                "error_handler": error_handler,
                "logging_service": logging_service,
                "realm": realm,
                "service_name": service_name,
                "service_type": service_type,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Created service type utilities for {cache_key}")
            return error_handler, logging_service
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create service type utilities for {realm}:{service_name}:{service_type}: {e}")
            raise
    
    def get_service_type_utilities(self, realm: str, service_name: str, service_type: str) -> Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]:
        """
        Get service type-specific utilities (create if not exists).
        
        Args:
            realm: The realm name
            service_name: The service name
            service_type: The service type
            
        Returns:
            Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]: The utilities
        """
        return self.create_service_type_utilities(realm, service_name, service_type)
    
    def get_all_service_type_utilities(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all cached service type utilities.
        
        Returns:
            Dict[str, Dict[str, Any]]: All cached utilities
        """
        return self.service_type_cache.copy()
    
    def clear_cache(self):
        """Clear the service type utilities cache."""
        self.service_type_cache.clear()
        self.logger.info("✅ Service type utilities cache cleared")
    
    def get_supported_service_types(self) -> list:
        """
        Get list of supported service types.
        
        Returns:
            list: List of supported service type names
        """
        return ["service", "agent", "mcp_server", "foundation_service"]
    
    def get_factory_status(self) -> Dict[str, Any]:
        """
        Get factory status and statistics.
        
        Returns:
            Dict[str, Any]: Factory status information
        """
        return {
            "supported_service_types": self.get_supported_service_types(),
            "cached_utilities": len(self.service_type_cache),
            "cache_keys": list(self.service_type_cache.keys()),
            "factory_initialized": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_service_type_statistics(self, service_type: str) -> Dict[str, Any]:
        """
        Get statistics for a specific service type.
        
        Args:
            service_type: The service type
            
        Returns:
            Dict[str, Any]: Service type statistics
        """
        if service_type not in self.get_supported_service_types():
            raise ValueError(f"Unsupported service type: {service_type}")
        
        # Count utilities by service type
        service_type_count = 0
        realms = set()
        services = set()
        
        for cache_key, cached_data in self.service_type_cache.items():
            if cached_data["service_type"] == service_type:
                service_type_count += 1
                realms.add(cached_data["realm"])
                services.add(cached_data["service_name"])
        
        return {
            "service_type": service_type,
            "total_utilities": service_type_count,
            "realms": list(realms),
            "services": list(services),
            "timestamp": datetime.utcnow().isoformat()
        }


# Global factory instance
_service_type_factory = None

def get_service_type_factory() -> ServiceTypeFactory:
    """
    Get the global service type factory instance.
    
    Returns:
        ServiceTypeFactory: The global factory instance
    """
    global _service_type_factory
    if _service_type_factory is None:
        _service_type_factory = ServiceTypeFactory()
    return _service_type_factory

def create_service_type_utilities(realm: str, service_name: str, service_type: str) -> Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]:
    """
    Create service type-specific utilities using the global factory.
    
    Args:
        realm: The realm name
        service_name: The service name
        service_type: The service type
        
    Returns:
        Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]: The created utilities
    """
    factory = get_service_type_factory()
    return factory.create_service_type_utilities(realm, service_name, service_type)

def get_service_type_utilities(realm: str, service_name: str, service_type: str) -> Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]:
    """
    Get service type-specific utilities using the global factory.
    
    Args:
        realm: The realm name
        service_name: The service name
        service_type: The service type
        
    Returns:
        Tuple[ServiceTypeErrorHandler, ServiceTypeLoggingService]: The utilities
    """
    factory = get_service_type_factory()
    return factory.get_service_type_utilities(realm, service_name, service_type)


