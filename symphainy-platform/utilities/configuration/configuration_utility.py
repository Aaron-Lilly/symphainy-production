#!/usr/bin/env python3
"""
Configuration Utility

Simple, reliable configuration utility for platform services.
Provides configuration access, validation, and management without unnecessary complexity.

WHAT (Utility Role): I provide configuration access and management for platform services
HOW (Utility Implementation): I use environment variables and configuration files directly
"""

import logging
import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from config.environment_loader import EnvironmentLoader

logger = logging.getLogger(__name__)


class ConfigurationUtility:
    """
    Simple Configuration Utility
    
    Provides reliable configuration access and management for platform services:
    - Configuration loading and validation
    - Environment-specific configuration management
    - Multi-tenant configuration access
    - Configuration caching and updates
    """
    
    def __init__(self, service_name: str, env_config: Optional[Dict[str, Any]] = None):
        """Initialize configuration utility."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"ConfigurationUtility-{service_name}")
        
        # Environment loader for configuration access
        self.env_loader = EnvironmentLoader()
        
        # Configuration cache
        self.config_cache: Dict[str, Any] = {}
        self.cache_enabled = True
        
        # Inject environment variables if provided
        if env_config:
            self._inject_environment_variables(env_config)
        
        self.logger.info(f"Configuration utility initialized for {service_name}")
    
    def _inject_environment_variables(self, env_config: Dict[str, Any]):
        """Inject environment variables into the configuration cache."""
        try:
            for key, value in env_config.items():
                self.config_cache[key] = value
            
            self.logger.info(f"Injected {len(env_config)} environment variables into configuration cache")
        except Exception as e:
            self.logger.error(f"Failed to inject environment variables: {e}")
    
    # ============================================================================
    # BASIC CONFIGURATION ACCESS
    # ============================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        try:
            # Check cache first
            if self.cache_enabled and key in self.config_cache:
                return self.config_cache[key]
            
            # Get from environment variables
            value = os.getenv(key, default)
            
            # Cache the value
            if self.cache_enabled:
                self.config_cache[key] = value
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get configuration key '{key}': {e}")
            return default
    
    # ============================================================================
    # TYPED CONFIGURATION ACCESS
    # ============================================================================
    
    def get_string(self, key: str, default: str = None) -> str:
        """Get configuration value as string."""
        value = self.get(key, default)
        return str(value) if value is not None else default
    
    def get_int(self, key: str, default: int = None) -> int:
        """Get configuration value as integer."""
        value = self.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            self.logger.warning(f"Failed to convert config '{key}' to int: {value}")
            return default
    
    def get_float(self, key: str, default: float = None) -> float:
        """Get configuration value as float."""
        value = self.get(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            self.logger.warning(f"Failed to convert config '{key}' to float: {value}")
            return default
    
    def get_bool(self, key: str, default: bool = None) -> bool:
        """Get configuration value as boolean."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value) if value is not None else default
    
    def get_list(self, key: str, default: List[str] = None, separator: str = ',') -> List[str]:
        """Get configuration value as list."""
        value = self.get(key, default)
        if value is None:
            return default
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        return default or []
    
    def get_dict(self, key: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get configuration value as dictionary."""
        value = self.get(key, default)
        if isinstance(value, dict):
            return value
        return default or {}
    
    # ============================================================================
    # ENVIRONMENT-SPECIFIC CONFIGURATION
    # ============================================================================
    
    def get_environment(self) -> str:
        """Get current environment."""
        return self.get_string("ENVIRONMENT", "development")
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        env = self.get_environment()
        return env.lower() == "development"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        env = self.get_environment()
        return env.lower() == "production"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        env = self.get_environment()
        return env.lower() == "testing"
    
    # ============================================================================
    # MULTI-TENANT CONFIGURATION
    # ============================================================================
    
    def get_multi_tenant_config(self) -> Dict[str, Any]:
        """Get multi-tenant configuration."""
        return {
            "enabled": self.get_bool("MULTI_TENANT_ENABLED", False),
            "default_tenant_type": self.get_string("DEFAULT_TENANT_TYPE", "individual"),
            "max_tenants_per_user": self.get_int("MAX_TENANTS_PER_USER", 5),
            "tenant_isolation_strict": self.get_bool("TENANT_ISOLATION_STRICT", True),
            "rls_enabled": self.get_bool("RLS_ENABLED", True)
        }
    
    def is_multi_tenant_enabled(self) -> bool:
        """Check if multi-tenancy is enabled."""
        return self.env_loader.is_multi_tenant_enabled()
    
    # ============================================================================
    # CACHING AND PERFORMANCE
    # ============================================================================
    
    def enable_cache(self):
        """Enable configuration caching."""
        self.cache_enabled = True
        self.logger.info("Configuration caching enabled")
    
    def disable_cache(self):
        """Disable configuration caching."""
        self.cache_enabled = False
        self.config_cache.clear()
        self.logger.info("Configuration caching disabled")
    
    def clear_cache(self):
        """Clear configuration cache."""
        self.config_cache.clear()
        self.logger.info("Configuration cache cleared")
    
    def refresh_config(self):
        """Refresh configuration from source."""
        self.clear_cache()
        self.logger.info("Configuration refreshed")
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration utility status."""
        return {
            "service_name": self.service_name,
            "status": "active",
            "cache_enabled": self.cache_enabled,
            "cached_keys": len(self.config_cache),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def validate_configuration(self, required_keys: List[str]) -> Dict[str, Any]:
        """Validate that required configuration keys are present."""
        missing = []
        present = []
        
        for key in required_keys:
            value = self.get(key)
            if value is not None:
                present.append(key)
            else:
                missing.append(key)
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "present": present,
            "total_required": len(required_keys)
        }
