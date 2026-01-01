#!/usr/bin/env python3
"""
Error Handler Factory

Factory for creating realm-specific error handlers with real working implementations.
Provides centralized error handler creation and management.

WHAT (Utility Role): I provide centralized error handler creation and management
HOW (Utility Implementation): I create realm-specific error handlers with proper configuration
"""

import logging
from typing import Dict, Any, Optional, Type
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase
from .utility_foundation_error_handler import UtilityFoundationErrorHandler
from .public_works_foundation_error_handler import PublicWorksFoundationErrorHandler
from .smart_city_error_handler import SmartCityErrorHandler
from .business_enablement_error_handler import BusinessEnablementErrorHandler
from .experience_error_handler import ExperienceErrorHandler
from .curator_foundation_error_handler import CuratorFoundationErrorHandler
from .agentic_foundation_error_handler import AgenticFoundationErrorHandler
from .communication_foundation_error_handler import CommunicationFoundationErrorHandler
from .journey_error_handler import JourneyErrorHandler
from .solution_error_handler import SolutionErrorHandler


class ErrorHandlerFactory:
    """
    Factory for creating realm-specific error handlers.
    
    Provides centralized creation and management of error handlers for all realms.
    """
    
    def __init__(self):
        """Initialize error handler factory."""
        self.logger = logging.getLogger("ErrorHandlerFactory")
        
        # Registry of available error handlers
        self.error_handler_registry: Dict[str, Type[RealmErrorHandlerBase]] = {
            "utility_foundation": UtilityFoundationErrorHandler,
            "public_works_foundation": PublicWorksFoundationErrorHandler,
            "smart_city": SmartCityErrorHandler,
            "business_enablement": BusinessEnablementErrorHandler,
            "experience": ExperienceErrorHandler,
            "curator_foundation": CuratorFoundationErrorHandler,
            "agentic_foundation": AgenticFoundationErrorHandler,
            "communication_foundation": CommunicationFoundationErrorHandler,
            "journey": JourneyErrorHandler,
            "solution": SolutionErrorHandler
        }
        
        # Cache of created error handlers
        self.error_handler_cache: Dict[str, RealmErrorHandlerBase] = {}
        
        self.logger.info("✅ Error Handler Factory initialized")
    
    def create_error_handler(self, realm: str, service_name: str = None) -> RealmErrorHandlerBase:
        """
        Create a realm-specific error handler.
        
        Args:
            realm: The realm name
            service_name: Optional service name (defaults to realm name)
            
        Returns:
            RealmErrorHandlerBase: The created error handler
            
        Raises:
            ValueError: If realm is not supported
        """
        try:
            # Check if realm is supported
            if realm not in self.error_handler_registry:
                raise ValueError(f"Unsupported realm: {realm}. Supported realms: {list(self.error_handler_registry.keys())}")
            
            # Use service name or default to realm name
            if service_name is None:
                service_name = realm
            
            # Check cache first
            cache_key = f"{realm}:{service_name}"
            if cache_key in self.error_handler_cache:
                self.logger.debug(f"✅ Returning cached error handler for {cache_key}")
                return self.error_handler_cache[cache_key]
            
            # Create new error handler
            error_handler_class = self.error_handler_registry[realm]
            error_handler = error_handler_class(service_name=service_name)
            
            # Cache the error handler
            self.error_handler_cache[cache_key] = error_handler
            
            self.logger.info(f"✅ Created error handler for {realm} realm: {service_name}")
            return error_handler
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create error handler for {realm}: {e}")
            raise
    
    def get_error_handler(self, realm: str, service_name: str = None) -> RealmErrorHandlerBase:
        """
        Get an error handler (create if not exists).
        
        Args:
            realm: The realm name
            service_name: Optional service name
            
        Returns:
            RealmErrorHandlerBase: The error handler
        """
        return self.create_error_handler(realm, service_name)
    
    def get_all_error_handlers(self) -> Dict[str, RealmErrorHandlerBase]:
        """
        Get all cached error handlers.
        
        Returns:
            Dict[str, RealmErrorHandlerBase]: All cached error handlers
        """
        return self.error_handler_cache.copy()
    
    def clear_cache(self):
        """Clear the error handler cache."""
        self.error_handler_cache.clear()
        self.logger.info("✅ Error handler cache cleared")
    
    def get_supported_realms(self) -> list:
        """
        Get list of supported realms.
        
        Returns:
            list: List of supported realm names
        """
        return list(self.error_handler_registry.keys())
    
    def register_error_handler(self, realm: str, error_handler_class: Type[RealmErrorHandlerBase]):
        """
        Register a new error handler class for a realm.
        
        Args:
            realm: The realm name
            error_handler_class: The error handler class
        """
        if not issubclass(error_handler_class, RealmErrorHandlerBase):
            raise ValueError("Error handler class must inherit from RealmErrorHandlerBase")
        
        self.error_handler_registry[realm] = error_handler_class
        self.logger.info(f"✅ Registered error handler for realm: {realm}")
    
    def get_factory_status(self) -> Dict[str, Any]:
        """
        Get factory status and statistics.
        
        Returns:
            Dict[str, Any]: Factory status information
        """
        return {
            "supported_realms": self.get_supported_realms(),
            "cached_handlers": len(self.error_handler_cache),
            "cache_keys": list(self.error_handler_cache.keys()),
            "factory_initialized": True,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global factory instance
_error_handler_factory = None

def get_error_handler_factory() -> ErrorHandlerFactory:
    """
    Get the global error handler factory instance.
    
    Returns:
        ErrorHandlerFactory: The global factory instance
    """
    global _error_handler_factory
    if _error_handler_factory is None:
        _error_handler_factory = ErrorHandlerFactory()
    return _error_handler_factory

def create_error_handler(realm: str, service_name: str = None) -> RealmErrorHandlerBase:
    """
    Create a realm-specific error handler using the global factory.
    
    Args:
        realm: The realm name
        service_name: Optional service name
        
    Returns:
        RealmErrorHandlerBase: The created error handler
    """
    factory = get_error_handler_factory()
    return factory.create_error_handler(realm, service_name)

def get_error_handler(realm: str, service_name: str = None) -> RealmErrorHandlerBase:
    """
    Get a realm-specific error handler using the global factory.
    
    Args:
        realm: The realm name
        service_name: Optional service name
        
    Returns:
        RealmErrorHandlerBase: The error handler
    """
    factory = get_error_handler_factory()
    return factory.get_error_handler(realm, service_name)


