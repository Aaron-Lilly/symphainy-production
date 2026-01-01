#!/usr/bin/env python3
"""
Unified Configuration Manager

Centralized configuration management with layered architecture:
- Layer 1: Secrets Management (.env.secrets)
- Layer 2: Environment-Specific Configuration (config/{env}.env)
- Layer 3: Business Logic Configuration (config/business-logic.yaml)
- Layer 4: Infrastructure Configuration (config/infrastructure.yaml)
- Layer 5: Default Configuration (built-in defaults)

WHAT (Configuration Role): I provide unified configuration management with layered architecture
HOW (Configuration Implementation): I load configuration from multiple layers with proper precedence
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from enum import Enum
from datetime import datetime
import json

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigurationLayer(Enum):
    """Configuration layers in order of precedence."""
    SECRETS = "secrets"
    ENVIRONMENT = "environment"
    BUSINESS_LOGIC = "business_logic"
    INFRASTRUCTURE = "infrastructure"
    DEFAULTS = "defaults"

class UnifiedConfigurationManager:
    """
    Unified Configuration Manager
    
    Provides centralized configuration management with layered architecture.
    Replaces ConfigurationUtility, EnvironmentLoader, and ConfigManager.
    """
    
    def __init__(self, service_name: str = "unified_config", 
                 environment: Optional[Environment] = None,
                 config_root: Optional[str] = None):
        """Initialize Unified Configuration Manager."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"UnifiedConfigurationManager-{service_name}")
        self.config_root = Path(config_root) if config_root else Path.cwd()
        
        # Configuration cache
        self.config_cache: Dict[str, Any] = {}
        self.cache_enabled = True
        self.last_loaded = None
        
        # Environment detection
        self.environment = environment or self._detect_environment()
        
        # Layer configuration
        self.layers = {
            ConfigurationLayer.SECRETS: self._load_secrets_config,
            ConfigurationLayer.ENVIRONMENT: self._load_environment_config,
            ConfigurationLayer.BUSINESS_LOGIC: self._load_business_logic_config,
            ConfigurationLayer.INFRASTRUCTURE: self._load_infrastructure_config,
            ConfigurationLayer.DEFAULTS: self._load_defaults_config
        }
        
        # Load configuration
        self._load_all_configuration()
        
        self.logger.info(f"✅ Unified Configuration Manager initialized for {service_name}")
        self.logger.info(f"📁 Config root: {self.config_root}")
        self.logger.info(f"🌍 Environment: {self.environment.value}")
        self.logger.info(f"📊 Loaded {len(self.config_cache)} configuration values")
    
    def _detect_environment(self) -> Environment:
        """Detect current environment from environment variables."""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        
        if env_str in ["dev", "development"]:
            return Environment.DEVELOPMENT
        elif env_str in ["staging", "stage"]:
            return Environment.STAGING
        elif env_str in ["prod", "production"]:
            return Environment.PRODUCTION
        elif env_str in ["test", "testing"]:
            return Environment.TESTING
        else:
            self.logger.warning(f"⚠️ Unknown environment '{env_str}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_all_configuration(self):
        """Load configuration from all layers in order of precedence."""
        try:
            self.logger.info("🔄 Loading configuration from all layers...")
            
            # Start with empty configuration
            self.config_cache = {}
            
            # Load from each layer (later layers override earlier ones)
            for layer in ConfigurationLayer:
                try:
                    layer_config = self.layers[layer]()
                    if layer_config:
                        self.config_cache.update(layer_config)
                        self.logger.info(f"✅ Loaded {len(layer_config)} values from {layer.value} layer")
                    else:
                        self.logger.info(f"ℹ️ No configuration found in {layer.value} layer")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to load {layer.value} layer: {e}")
            
            self.last_loaded = datetime.utcnow()
            self.logger.info(f"✅ Configuration loaded successfully: {len(self.config_cache)} total values")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def _load_secrets_config(self) -> Dict[str, Any]:
        """Load secrets configuration from .env.secrets file."""
        secrets_file = self.config_root / ".env.secrets"
        
        if not secrets_file.exists():
            self.logger.info("ℹ️ No secrets file found, skipping secrets layer")
            return {}
        
        try:
            secrets = {}
            with open(secrets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip()
            
            self.logger.info(f"✅ Loaded {len(secrets)} secrets from {secrets_file}")
            return secrets
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load secrets from {secrets_file}: {e}")
            return {}
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration from config/{env}.env file."""
        env_file = self.config_root / "config" / f"{self.environment.value}.env"
        
        if not env_file.exists():
            self.logger.info(f"ℹ️ No environment config file found: {env_file}")
            return {}
        
        try:
            env_config = {}
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_config[key.strip()] = value.strip()
            
            self.logger.info(f"✅ Loaded {len(env_config)} values from {env_file}")
            return env_config
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load environment config from {env_file}: {e}")
            return {}
    
    def _load_business_logic_config(self) -> Dict[str, Any]:
        """Load business logic configuration from config/business-logic.yaml file."""
        business_logic_file = self.config_root / "config" / "business-logic.yaml"
        
        if not business_logic_file.exists():
            self.logger.info(f"ℹ️ No business logic config file found: {business_logic_file}")
            return {}
        
        try:
            with open(business_logic_file, 'r') as f:
                business_config = yaml.safe_load(f) or {}
            
            self.logger.info(f"✅ Loaded business logic config from {business_logic_file}")
            return business_config
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load business logic config from {business_logic_file}: {e}")
            return {}
    
    def _load_infrastructure_config(self) -> Dict[str, Any]:
        """Load infrastructure configuration from config/infrastructure.yaml file."""
        infrastructure_file = self.config_root / "config" / "infrastructure.yaml"
        
        if not infrastructure_file.exists():
            self.logger.info(f"ℹ️ No infrastructure config file found: {infrastructure_file}")
            return {}
        
        try:
            with open(infrastructure_file, 'r') as f:
                infrastructure_config = yaml.safe_load(f) or {}
            
            self.logger.info(f"✅ Loaded infrastructure config from {infrastructure_file}")
            return infrastructure_config
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load infrastructure config from {infrastructure_file}: {e}")
            return {}
    
    def _load_defaults_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            # Environment
            "ENVIRONMENT": self.environment.value,
            
            # Database defaults
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "symphainy_platform",
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "",
            
            # Redis defaults
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_DB": "0",
            "REDIS_PASSWORD": "",
            
            # API defaults
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
            "API_DEBUG": "true" if self.environment == Environment.DEVELOPMENT else "false",
            
            # Security defaults
            "SECRET_KEY": "your-secret-key-here",
            "JWT_SECRET": "your-jwt-secret-here",
            "JWT_EXPIRATION": "3600",
            
            # LLM defaults
            "LLM_PROVIDER_DEFAULT": "openai",
            "LLM_MODEL_DEFAULT": "gpt-3.5-turbo",
            "LLM_MAX_TOKENS": "1000",
            "LLM_TEMPERATURE": "0.7",
            
            # Multi-tenancy defaults
            "MULTI_TENANT_ENABLED": "false",
            "DEFAULT_TENANT_TYPE": "individual",
            "MAX_TENANTS_PER_USER": "5",
            "TENANT_ISOLATION_STRICT": "true",
            "RLS_ENABLED": "true",
            
            # Logging defaults
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            
            # Health monitoring defaults
            "HEALTH_CHECK_INTERVAL": "30",
            "HEALTH_CHECK_TIMEOUT": "5",
            "HEALTH_CHECK_RETRIES": "3"
        }
    
    # ============================================================================
    # CONFIGURATION ACCESS METHODS
    # ============================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        if self.cache_enabled and key in self.config_cache:
            return self.config_cache[key]
        
        # Try environment variable as fallback
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        
        return default
    
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
            self.logger.warning(f"⚠️ Invalid integer value for {key}: {value}")
            return default
    
    def get_float(self, key: str, default: float = None) -> float:
        """Get configuration value as float."""
        value = self.get(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            self.logger.warning(f"⚠️ Invalid float value for {key}: {value}")
            return default
    
    def get_bool(self, key: str, default: bool = None) -> bool:
        """Get configuration value as boolean."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return default
    
    def get_list(self, key: str, default: list = None, separator: str = ',') -> list:
        """Get configuration value as list."""
        value = self.get(key, default)
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        return default or []
    
    def get_dict(self, key: str, default: dict = None) -> dict:
        """Get configuration value as dictionary."""
        value = self.get(key, default)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                self.logger.warning(f"⚠️ Invalid JSON value for {key}: {value}")
                return default
        return default or {}
    
    # ============================================================================
    # SPECIALIZED CONFIGURATION METHODS
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "host": self.get_string("DATABASE_HOST"),
            "port": self.get_int("DATABASE_PORT"),
            "name": self.get_string("DATABASE_NAME"),
            "user": self.get_string("DATABASE_USER"),
            "password": self.get_string("DATABASE_PASSWORD"),
            "url": self.get_string("DATABASE_URL"),
            "pool_size": self.get_int("DATABASE_POOL_SIZE", 10),
            "max_overflow": self.get_int("DATABASE_MAX_OVERFLOW", 20),
            "pool_timeout": self.get_int("DATABASE_POOL_TIMEOUT", 30),
            "pool_recycle": self.get_int("DATABASE_POOL_RECYCLE", 3600)
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return {
            "host": self.get_string("REDIS_HOST"),
            "port": self.get_int("REDIS_PORT"),
            "db": self.get_int("REDIS_DB"),
            "password": self.get_string("REDIS_PASSWORD"),
            "url": self.get_string("REDIS_URL"),
            "max_connections": self.get_int("REDIS_MAX_CONNECTIONS", 10),
            "socket_timeout": self.get_int("REDIS_SOCKET_TIMEOUT", 5),
            "socket_connect_timeout": self.get_int("REDIS_SOCKET_CONNECT_TIMEOUT", 5)
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API server configuration."""
        return {
            "host": self.get_string("API_HOST"),
            "port": self.get_int("API_PORT"),
            "debug": self.get_bool("API_DEBUG"),
            "reload": self.get_bool("API_RELOAD"),
            "workers": self.get_int("API_WORKERS", 1),
            "timeout": self.get_int("API_TIMEOUT", 30),
            "cors_origins": self.get_list("API_CORS_ORIGINS"),
            "cors_methods": self.get_list("API_CORS_METHODS"),
            "cors_headers": self.get_list("API_CORS_HEADERS")
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "secret_key": self.get_string("SECRET_KEY"),
            "jwt_secret": self.get_string("JWT_SECRET"),
            "jwt_expiration": self.get_int("JWT_EXPIRATION"),
            "jwt_algorithm": self.get_string("JWT_ALGORITHM", "HS256"),
            "password_min_length": self.get_int("PASSWORD_MIN_LENGTH", 8),
            "password_require_uppercase": self.get_bool("PASSWORD_REQUIRE_UPPERCASE", True),
            "password_require_lowercase": self.get_bool("PASSWORD_REQUIRE_LOWERCASE", True),
            "password_require_numbers": self.get_bool("PASSWORD_REQUIRE_NUMBERS", True),
            "password_require_symbols": self.get_bool("PASSWORD_REQUIRE_SYMBOLS", True)
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            "provider_default": self.get_string("LLM_PROVIDER_DEFAULT"),
            "model_default": self.get_string("LLM_MODEL_DEFAULT"),
            "max_tokens": self.get_int("LLM_MAX_TOKENS"),
            "temperature": self.get_float("LLM_TEMPERATURE"),
            "top_p": self.get_float("LLM_TOP_P", 1.0),
            "frequency_penalty": self.get_float("LLM_FREQUENCY_PENALTY", 0.0),
            "presence_penalty": self.get_float("LLM_PRESENCE_PENALTY", 0.0),
            "timeout": self.get_int("LLM_TIMEOUT", 60),
            "retry_attempts": self.get_int("LLM_RETRY_ATTEMPTS", 3),
            "retry_delay": self.get_int("LLM_RETRY_DELAY", 1)
        }
    
    def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration."""
        return {
            "rate_limiting_enabled": self.get_bool("RATE_LIMITING_ENABLED", True),
            "rate_limit_requests": self.get_int("RATE_LIMIT_REQUESTS", 100),
            "rate_limit_window": self.get_int("RATE_LIMIT_WINDOW", 3600),
            "cost_management_enabled": self.get_bool("COST_MANAGEMENT_ENABLED", True),
            "max_daily_cost": self.get_float("MAX_DAILY_COST", 100.0),
            "audit_logging_enabled": self.get_bool("AUDIT_LOGGING_ENABLED", True),
            "audit_retention_days": self.get_int("AUDIT_RETENTION_DAYS", 90)
        }
    
    # ============================================================================
    # ENVIRONMENT-SPECIFIC METHODS
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
    
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == Environment.STAGING
    
    # ============================================================================
    # CACHING AND PERFORMANCE
    # ============================================================================
    
    def enable_cache(self):
        """Enable configuration caching."""
        self.cache_enabled = True
        self.logger.info("✅ Configuration caching enabled")
    
    def disable_cache(self):
        """Disable configuration caching."""
        self.cache_enabled = False
        self.logger.info("✅ Configuration caching disabled")
    
    def clear_cache(self):
        """Clear configuration cache."""
        self.config_cache.clear()
        self.logger.info("✅ Configuration cache cleared")
    
    def refresh_config(self):
        """Refresh configuration from source."""
        self.logger.info("🔄 Refreshing configuration from source...")
        self._load_all_configuration()
        self.logger.info("✅ Configuration refreshed successfully")
    
    # ============================================================================
    # VALIDATION AND HEALTH
    # ============================================================================
    
    def validate_configuration(self, required_keys: List[str]) -> Dict[str, Any]:
        """Validate that required configuration keys are present."""
        missing_keys = []
        invalid_keys = []
        
        for key in required_keys:
            if key not in self.config_cache:
                missing_keys.append(key)
            elif not self.config_cache[key]:
                invalid_keys.append(key)
        
        return {
            "valid": len(missing_keys) == 0 and len(invalid_keys) == 0,
            "missing_keys": missing_keys,
            "invalid_keys": invalid_keys,
            "total_required": len(required_keys),
            "valid_count": len(required_keys) - len(missing_keys) - len(invalid_keys)
        }
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration manager status."""
        return {
            "service_name": self.service_name,
            "environment": self.environment.value,
            "config_root": str(self.config_root),
            "cache_enabled": self.cache_enabled,
            "total_config_values": len(self.config_cache),
            "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None,
            "layers_loaded": len([layer for layer in ConfigurationLayer if self.layers[layer]()])
        }
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        print(f"\n🔧 Configuration Summary for {self.service_name}")
        print(f"🌍 Environment: {self.environment.value}")
        print(f"📁 Config Root: {self.config_root}")
        print(f"📊 Total Values: {len(self.config_cache)}")
        print(f"💾 Cache Enabled: {self.cache_enabled}")
        print(f"⏰ Last Loaded: {self.last_loaded}")
        
        # Print configuration by layer
        print(f"\n📋 Configuration by Layer:")
        for layer in ConfigurationLayer:
            layer_config = self.layers[layer]()
            print(f"  {layer.value}: {len(layer_config)} values")
        
        # Print some key configuration values
        print(f"\n🔑 Key Configuration Values:")
        key_configs = [
            "ENVIRONMENT", "DATABASE_HOST", "REDIS_HOST", "API_HOST", "API_PORT",
            "LLM_PROVIDER_DEFAULT", "MULTI_TENANT_ENABLED", "LOG_LEVEL"
        ]
        
        for key in key_configs:
            value = self.get(key, "NOT_SET")
            print(f"  {key}: {value}")
        
        print(f"\n✅ Configuration Summary Complete\n")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_configuration_manager(service_name: str = "unified_config", 
                            environment: Optional[Environment] = None,
                            config_root: Optional[str] = None) -> UnifiedConfigurationManager:
    """Get a Unified Configuration Manager instance."""
    return UnifiedConfigurationManager(service_name, environment, config_root)

# Global instance for backward compatibility
unified_config = UnifiedConfigurationManager()
