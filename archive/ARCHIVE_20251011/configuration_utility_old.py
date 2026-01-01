"""
Configuration Utility

Platform-specific configuration utility for Smart City services.
Refactored from Configuration Foundation Layer to be a self-contained utility.

WHAT (Utility Role): I provide standardized configuration access for platform operations
HOW (Utility Implementation): I load, validate, and provide configuration values
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from enum import Enum

from config import ConfigManager, Environment


class ConfigurationUtility:
    """
    Platform-specific configuration utility for Smart City services.
    
    Refactored from Configuration Foundation Layer to be a self-contained utility.
    Provides configuration access patterns used across the platform including:
    - Environment-specific configuration loading
    - Configuration validation
    - Multi-tenant configuration access
    - Service-specific configuration
    - Configuration caching and updates
    """
    
    def __init__(self, service_name: str, environment: Optional[Environment] = None):
        """Initialize configuration utility."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"ConfigurationUtility-{service_name}")
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(environment)
        self.environment = self.config_manager.get_environment()
        
        # Configuration cache
        self.config_cache: Dict[str, Any] = {}
        self.cache_enabled = True
        
        # Validate configuration
        self._validate_config()
        
        self.logger.info(f"Configuration utility initialized for {service_name} in {self.environment.value} environment")
    
    # ============================================================================
    # BASIC CONFIGURATION ACCESS
    # ============================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        if self.cache_enabled and key in self.config_cache:
            return self.config_cache[key]
        
        value = self.config_manager.get(key, default)
        
        if self.cache_enabled:
            self.config_cache[key] = value
        
        return value
    
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
    
    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.environment
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        return {
            "environment": self.environment.value,
            "is_development": self.is_development(),
            "is_production": self.is_production(),
            "is_testing": self.is_testing(),
            "config_file": self.config_manager.get_config_file_path()
        }
    
    # ============================================================================
    # SERVICE-SPECIFIC CONFIGURATION
    # ============================================================================
    
    def get_service_config(self, service_name: str = None) -> Dict[str, Any]:
        """Get service-specific configuration."""
        service = service_name or self.service_name
        service_prefix = f"{service.upper()}_"
        
        service_config = {}
        for key, value in self.config_manager.get_all().items():
            if key.startswith(service_prefix):
                config_key = key[len(service_prefix):].lower()
                service_config[config_key] = value
        
        return service_config
    
    def get_service_setting(self, setting: str, service_name: str = None, default: Any = None) -> Any:
        """Get a specific service setting."""
        service = service_name or self.service_name
        key = f"{service.upper()}_{setting.upper()}"
        return self.get(key, default)
    
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
    
    def get_tenant_config(self, tenant_type: str) -> Dict[str, Any]:
        """Get configuration for specific tenant type."""
        prefix = f"TENANT_{tenant_type.upper()}_"
        config = {}
        
        for key, value in self.config_manager.get_all().items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        
        return config
    
    def is_multi_tenant_enabled(self) -> bool:
        """Check if multi-tenancy is enabled."""
        return self.get_bool("MULTI_TENANT_ENABLED", False)
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.get_string("DATABASE_URL"),
            "host": self.get_string("DB_HOST", "localhost"),
            "port": self.get_int("DB_PORT", 5432),
            "name": self.get_string("DB_NAME"),
            "user": self.get_string("DB_USER"),
            "password": self.get_string("DB_PASSWORD"),
            "ssl_mode": self.get_string("DB_SSL_MODE", "prefer"),
            "pool_size": self.get_int("DB_POOL_SIZE", 10),
            "max_overflow": self.get_int("DB_MAX_OVERFLOW", 20)
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return {
            "url": self.get_string("REDIS_URL"),
            "host": self.get_string("REDIS_HOST", "localhost"),
            "port": self.get_int("REDIS_PORT", 6379),
            "password": self.get_string("REDIS_PASSWORD"),
            "db": self.get_int("REDIS_DB", 0),
            "ssl": self.get_bool("REDIS_SSL", False)
        }
    
    def get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase configuration."""
        return {
            "url": self.get_string("SUPABASE_URL"),
            "key": self.get_string("SUPABASE_ANON_KEY"),
            "service_key": self.get_string("SUPABASE_SERVICE_ROLE_KEY"),
            "bucket": self.get_string("SUPABASE_BUCKET", "default")
        }
    
    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "jwt_secret": self.get_string("JWT_SECRET"),
            "jwt_expiry": self.get_int("JWT_EXPIRY", 3600),
            "bcrypt_rounds": self.get_int("BCRYPT_ROUNDS", 12),
            "session_timeout": self.get_int("SESSION_TIMEOUT", 1800),
            "max_login_attempts": self.get_int("MAX_LOGIN_ATTEMPTS", 5),
            "lockout_duration": self.get_int("LOCKOUT_DURATION", 900)
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration."""
        return {
            "origins": self.get_list("CORS_ORIGINS", ["http://localhost:3000"]),
            "methods": self.get_list("CORS_METHODS", ["GET", "POST", "PUT", "DELETE"]),
            "headers": self.get_list("CORS_HEADERS", ["*"]),
            "credentials": self.get_bool("CORS_CREDENTIALS", True)
        }
    
    # ============================================================================
    # CACHING AND PERFORMANCE
    # ============================================================================
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get caching configuration."""
        return {
            "enabled": self.get_bool("CACHE_ENABLED", True),
            "default_ttl": self.get_int("CACHE_DEFAULT_TTL", 300),
            "max_size": self.get_int("CACHE_MAX_SIZE", 1000),
            "user_context_ttl": self.get_int("USER_CONTEXT_CACHE_TTL", 1800),
            "tenant_cache_ttl": self.get_int("TENANT_CACHE_TTL", 3600)
        }
    
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
        self.config_manager.reload()
        self._validate_config()
        self.logger.info("Configuration refreshed")
    
    # ============================================================================
    # VALIDATION
    # ============================================================================
    
    def _validate_config(self):
        """Validate configuration for current environment."""
        required_keys = self._get_required_keys()
        missing_keys = []
        
        for key in required_keys:
            if not self.config_manager.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            self.logger.warning(f"Missing required configuration keys: {', '.join(missing_keys)}")
            if self.is_production():
                raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    def _get_required_keys(self) -> List[str]:
        """Get list of required configuration keys."""
        base_keys = [
            "DATABASE_URL",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY"
        ]
        
        if self.is_production():
            base_keys.extend([
                "JWT_SECRET",
                "SUPABASE_SERVICE_ROLE_KEY"
            ])
        
        return base_keys
    
    def validate_required_config(self, keys: List[str]) -> Dict[str, Any]:
        """Validate that required configuration keys are present."""
        missing = []
        present = []
        
        for key in keys:
            if self.get(key):
                present.append(key)
            else:
                missing.append(key)
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "present": present,
            "total_required": len(keys)
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config_manager.get_all()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration utility status summary."""
        return {
            "service_name": self.service_name,
            "utility_type": "configuration",
            "status": "operational",
            "environment": self.environment.value,
            "cache_enabled": self.cache_enabled,
            "cached_keys": len(self.config_cache),
            "timestamp": self.config_manager.get_timestamp()
        }

