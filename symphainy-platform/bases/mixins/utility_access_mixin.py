#!/usr/bin/env python3
"""
Utility Access Mixin

Focused mixin for utility access patterns - extracts utility getter functionality
from base classes into a reusable, testable component.

WHAT (Utility Access Role): I provide standardized access to all platform utilities
HOW (Utility Access Mixin): I centralize utility access patterns with error handling
"""

from typing import Dict, Any, Optional


class UtilityAccessMixin:
    """
    Mixin for standardized utility access patterns.
    
    Provides consistent access to all platform utilities through the DI Container
    with proper error handling and fallback mechanisms.
    """
    
    def _init_utility_access(self, di_container: Any):
        """Initialize utility access patterns."""
        if not di_container:
            raise ValueError(
                "DI Container is required for UtilityAccessMixin initialization. "
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
            logger_service = di_container.get_logger(f"{self.__class__.__name__}.utility_access")
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
        
        # Utility references (initialized lazily)
        self._utility_cache = {}
        
        self.logger.debug("Utility access mixin initialized")
    
    def get_utility(self, name: str) -> Any:
        """Get utility service by name with caching."""
        if name in self._utility_cache:
            return self._utility_cache[name]
        
        try:
            utility = self.di_container.get_utility(name)
            self._utility_cache[name] = utility
            return utility
        except Exception as e:
            self.logger.error(f"Failed to get utility '{name}': {e}")
            raise
    
    def get_config(self) -> Any:
        """Get configuration utility."""
        return self.get_utility("config")
    
    def get_health(self) -> Any:
        """Get health monitoring utility."""
        return self.get_utility("health")
    
    def get_telemetry(self) -> Any:
        """Get telemetry utility."""
        return self.get_utility("telemetry")
    
    def get_error_handler(self) -> Any:
        """Get error handling utility."""
        try:
            return self.get_utility("error_handler")
        except Exception:
            # Return a safe no-op handler if error handler isn't available
            # This can happen during early initialization
            return None
    
    def get_tenant(self) -> Any:
        """Get tenant management utility."""
        return self.get_utility("tenant")
    
    def get_validation(self) -> Any:
        """Get validation utility."""
        return self.get_utility("validation")
    
    def get_serialization(self) -> Any:
        """Get serialization utility."""
        return self.get_utility("serialization")
    
    def get_security(self) -> Any:
        """Get security utility."""
        return self.get_utility("security")
    
    def get_logger(self):
        """Get logger utility from DI Container."""
        try:
            logger_utility = self.get_utility("logger")
            if logger_utility:
                # Return the logger service (SmartCityLoggingService)
                return logger_utility
            # Fallback: use DI Container's get_logger method
            return self.di_container.get_logger(self.service_name if hasattr(self, 'service_name') else "unknown")
        except Exception as e:
            # If logger utility not available, use DI Container's get_logger
            if hasattr(self.di_container, 'get_logger'):
                return self.di_container.get_logger(self.service_name if hasattr(self, 'service_name') else "unknown")
            raise RuntimeError(
                f"Failed to get logger utility: {e}. "
                f"DI Container must initialize logging utility before services can use it."
            ) from e
    
    def clear_utility_cache(self):
        """Clear utility cache (useful for testing)."""
        self._utility_cache.clear()
        self.logger.debug("Utility cache cleared")

