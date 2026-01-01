#!/usr/bin/env python3
"""
Logging Service Factory

Factory for creating realm-specific logging services with real working implementations.
Provides centralized logging service creation and management.

WHAT (Utility Role): I provide centralized logging service creation and management
HOW (Utility Implementation): I create realm-specific logging services with proper configuration
"""

import logging
from typing import Dict, Any, Optional, Type
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase
from .utility_foundation_logging_service import UtilityFoundationLoggingService
from .public_works_foundation_logging_service import PublicWorksFoundationLoggingService
from .smart_city_logging_service import SmartCityLoggingService
from .business_enablement_logging_service import BusinessEnablementLoggingService
from .experience_logging_service import ExperienceLoggingService
from .curator_foundation_logging_service import CuratorFoundationLoggingService
from .agentic_foundation_logging_service import AgenticFoundationLoggingService


class LoggingServiceFactory:
    """
    Factory for creating realm-specific logging services.
    
    Provides centralized creation and management of logging services for all realms.
    """
    
    def __init__(self):
        """Initialize logging service factory."""
        self.logger = logging.getLogger("LoggingServiceFactory")
        
        # Registry of available logging services
        self.logging_service_registry: Dict[str, Type[RealmLoggingServiceBase]] = {
            "utility_foundation": UtilityFoundationLoggingService,
            "public_works_foundation": PublicWorksFoundationLoggingService,
            "smart_city": SmartCityLoggingService,
            "business_enablement": BusinessEnablementLoggingService,
            "experience": ExperienceLoggingService,
            "curator_foundation": CuratorFoundationLoggingService,
            "agentic_foundation": AgenticFoundationLoggingService
        }
        
        # Cache of created logging services
        self.logging_service_cache: Dict[str, RealmLoggingServiceBase] = {}
        
        self.logger.info("✅ Logging Service Factory initialized")
    
    def create_logging_service(self, realm: str, service_name: str = None) -> RealmLoggingServiceBase:
        """
        Create a realm-specific logging service.
        
        Args:
            realm: The realm name
            service_name: Optional service name (defaults to realm name)
            
        Returns:
            RealmLoggingServiceBase: The created logging service
            
        Raises:
            ValueError: If realm is not supported
        """
        try:
            # Check if realm is supported
            if realm not in self.logging_service_registry:
                raise ValueError(f"Unsupported realm: {realm}. Supported realms: {list(self.logging_service_registry.keys())}")
            
            # Use service name or default to realm name
            if service_name is None:
                service_name = realm
            
            # Check cache first
            cache_key = f"{realm}:{service_name}"
            if cache_key in self.logging_service_cache:
                self.logger.debug(f"✅ Returning cached logging service for {cache_key}")
                return self.logging_service_cache[cache_key]
            
            # Create new logging service
            logging_service_class = self.logging_service_registry[realm]
            logging_service = logging_service_class(service_name)
            
            # Cache the logging service
            self.logging_service_cache[cache_key] = logging_service
            
            self.logger.info(f"✅ Created logging service for {realm} realm: {service_name}")
            return logging_service
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create logging service for {realm}: {e}")
            raise
    
    def get_logging_service(self, realm: str, service_name: str = None) -> RealmLoggingServiceBase:
        """
        Get a logging service (create if not exists).
        
        Args:
            realm: The realm name
            service_name: Optional service name
            
        Returns:
            RealmLoggingServiceBase: The logging service
        """
        return self.create_logging_service(realm, service_name)
    
    def get_all_logging_services(self) -> Dict[str, RealmLoggingServiceBase]:
        """
        Get all cached logging services.
        
        Returns:
            Dict[str, RealmLoggingServiceBase]: All cached logging services
        """
        return self.logging_service_cache.copy()
    
    def clear_cache(self):
        """Clear the logging service cache."""
        self.logging_service_cache.clear()
        self.logger.info("✅ Logging service cache cleared")
    
    def get_supported_realms(self) -> list:
        """
        Get list of supported realms.
        
        Returns:
            list: List of supported realm names
        """
        return list(self.logging_service_registry.keys())
    
    def register_logging_service(self, realm: str, logging_service_class: Type[RealmLoggingServiceBase]):
        """
        Register a new logging service class for a realm.
        
        Args:
            realm: The realm name
            logging_service_class: The logging service class
        """
        if not issubclass(logging_service_class, RealmLoggingServiceBase):
            raise ValueError("Logging service class must inherit from RealmLoggingServiceBase")
        
        self.logging_service_registry[realm] = logging_service_class
        self.logger.info(f"✅ Registered logging service for realm: {realm}")
    
    def get_factory_status(self) -> Dict[str, Any]:
        """
        Get factory status and statistics.
        
        Returns:
            Dict[str, Any]: Factory status information
        """
        return {
            "supported_realms": self.get_supported_realms(),
            "cached_services": len(self.logging_service_cache),
            "cache_keys": list(self.logging_service_cache.keys()),
            "factory_initialized": True,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global factory instance
_logging_service_factory = None

def get_logging_service_factory() -> LoggingServiceFactory:
    """
    Get the global logging service factory instance.
    
    Returns:
        LoggingServiceFactory: The global factory instance
    """
    global _logging_service_factory
    if _logging_service_factory is None:
        _logging_service_factory = LoggingServiceFactory()
    return _logging_service_factory

def create_logging_service(realm: str, service_name: str = None) -> RealmLoggingServiceBase:
    """
    Create a realm-specific logging service using the global factory.
    
    Args:
        realm: The realm name
        service_name: Optional service name
        
    Returns:
        RealmLoggingServiceBase: The created logging service
    """
    factory = get_logging_service_factory()
    return factory.create_logging_service(realm, service_name)

def get_logging_service(realm: str, service_name: str = None) -> RealmLoggingServiceBase:
    """
    Get a realm-specific logging service using the global factory.
    
    Args:
        realm: The realm name
        service_name: Optional service name
        
    Returns:
        RealmLoggingServiceBase: The logging service
    """
    factory = get_logging_service_factory()
    return factory.get_logging_service(realm, service_name)


