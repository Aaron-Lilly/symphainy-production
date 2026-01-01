# Utilities Integration & Optimization Plan

## 🚨 **CRITICAL FINDINGS: Configuration Utility Bloat**

### **❌ Current Problems**
1. **`ConfigurationUtility` (237 lines)** - Basic configuration access
2. **`EnvironmentLoader` (884 lines)** - MASSIVE configuration loader with 20+ specialized config methods
3. **`ConfigManager` (180 lines)** - Environment-specific configuration management
4. **`platform_env_file_for_cursor.md` (850+ lines)** - Monolithic configuration file
5. **108 files** importing `EnvironmentLoader` - Widespread dependency

### **🎯 ROOT CAUSE ANALYSIS**
The current architecture has **3 layers of configuration utilities** doing overlapping work:
- **Layer 1**: `ConfigurationUtility` - Basic get/set operations
- **Layer 2**: `EnvironmentLoader` - Specialized configuration methods (MASSIVE)
- **Layer 3**: `ConfigManager` - Environment detection and file loading

## 🎯 **RECOMMENDED SOLUTION: Unified Configuration Architecture**

### **Phase 1: Create Unified Configuration Manager**

```python
# utilities/configuration/unified_configuration_manager.py
#!/usr/bin/env python3
"""
Unified Configuration Manager - Single Source of Truth

Replaces ConfigurationUtility, EnvironmentLoader, and ConfigManager with a single,
layered configuration system that provides clean separation of concerns.

WHAT (Configuration Role): I provide unified configuration management with proper layering
HOW (Configuration Implementation): I use layered configuration with secrets separation
"""

import os
import yaml
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ConfigurationLayer:
    """Configuration layer definition."""
    name: str
    priority: int
    source: str
    description: str

class UnifiedConfigurationManager:
    """
    Unified Configuration Manager - Single Source of Truth
    
    Replaces all existing configuration utilities with a single, layered system.
    Provides clean separation of concerns and proper configuration hierarchy.
    """
    
    def __init__(self, environment: Environment = None, service_name: str = "unified_config"):
        """Initialize Unified Configuration Manager."""
        self.service_name = service_name
        self.environment = environment or self._detect_environment()
        self.config_root = Path("config")
        
        # Configuration layers (in priority order)
        self.layers = [
            ConfigurationLayer("environment_variables", 1, "os.environ", "Highest priority - runtime overrides"),
            ConfigurationLayer("secrets", 2, ".env.secrets", "Secrets and credentials"),
            ConfigurationLayer("environment_config", 3, f"config/{self.environment.value}.env", "Environment-specific settings"),
            ConfigurationLayer("business_logic", 4, "config/business-logic.yaml", "Business rules and governance"),
            ConfigurationLayer("infrastructure", 5, "config/infrastructure.yaml", "Infrastructure configuration"),
            ConfigurationLayer("defaults", 6, "built-in", "Default values and fallbacks")
        ]
        
        # Configuration cache
        self.config_cache: Dict[str, Any] = {}
        self.cache_enabled = True
        
        # Load configuration
        self._load_configuration()
        
        print(f"🔧 Unified Configuration Manager initialized for {self.environment.value}")
    
    def _detect_environment(self) -> Environment:
        """Detect current environment."""
        env_name = os.getenv("SYMPHAINY_ENV", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            print(f"⚠️ Unknown environment '{env_name}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_configuration(self):
        """Load configuration from all layers."""
        self.config_cache = {}
        
        # Load from each layer in priority order
        for layer in self.layers:
            try:
                layer_config = self._load_layer_config(layer)
                if layer_config:
                    self.config_cache.update(layer_config)
                    print(f"✅ Loaded {len(layer_config)} configs from {layer.name}")
            except Exception as e:
                print(f"⚠️ Failed to load {layer.name}: {e}")
        
        print(f"🔧 Total configuration keys loaded: {len(self.config_cache)}")
    
    def _load_layer_config(self, layer: ConfigurationLayer) -> Dict[str, Any]:
        """Load configuration from a specific layer."""
        if layer.name == "environment_variables":
            return dict(os.environ)
        
        elif layer.name == "secrets":
            return self._load_secrets_file()
        
        elif layer.name == "environment_config":
            return self._load_env_file(f"config/{self.environment.value}.env")
        
        elif layer.name == "business_logic":
            return self._load_yaml_file("config/business-logic.yaml")
        
        elif layer.name == "infrastructure":
            return self._load_yaml_file("config/infrastructure.yaml")
        
        elif layer.name == "defaults":
            return self._get_default_config()
        
        return {}
    
    def _load_secrets_file(self) -> Dict[str, Any]:
        """Load secrets from .env.secrets file."""
        secrets_file = Path(".env.secrets")
        if not secrets_file.exists():
            print("⚠️ No .env.secrets file found - using environment variables")
            return {}
        
        secrets = {}
        try:
            with open(secrets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip().strip('"').strip("'")
        except Exception as e:
            print(f"❌ Error loading secrets: {e}")
        
        return secrets
    
    def _load_env_file(self, file_path: str) -> Dict[str, Any]:
        """Load environment variables from file."""
        config = {}
        file_path = Path(file_path)
        
        if not file_path.exists():
            return config
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
        
        return config
    
    def _load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            # Environment
            "ENVIRONMENT": self.environment.value,
            "DEBUG": "true" if self.environment == Environment.DEVELOPMENT else "false",
            "LOG_LEVEL": "DEBUG" if self.environment == Environment.DEVELOPMENT else "INFO",
            
            # Database
            "DATABASE_URL": "postgresql://localhost:5432/symphainy_dev",
            "DATABASE_POOL_SIZE": "10",
            "DATABASE_MAX_OVERFLOW": "20",
            
            # Redis
            "REDIS_URL": "redis://localhost:6379/0",
            "REDIS_PASSWORD": "",
            
            # API
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
            "API_DEBUG": "true" if self.environment == Environment.DEVELOPMENT else "false",
            
            # Security
            "SECRET_KEY": "dev-secret-key-change-in-production",
            "JWT_SECRET": "dev-jwt-secret-change-in-production",
            
            # External Services
            "SUPABASE_URL": "",
            "SUPABASE_KEY": "",
            "OPENAI_API_KEY": "",
            
            # Monitoring
            "ENABLE_METRICS": "true",
            "METRICS_PORT": "9090"
        }
    
    # ============================================================================
    # CONFIGURATION ACCESS METHODS
    # ============================================================================
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        try:
            # Check cache first
            if self.cache_enabled and key in self.config_cache:
                return self.config_cache[key]
            
            # Get from environment variables (highest priority)
            value = os.getenv(key, default)
            
            # Cache the value
            if self.cache_enabled:
                self.config_cache[key] = value
            
            return value
            
        except Exception as e:
            print(f"❌ Failed to get configuration key '{key}': {e}")
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
            print(f"⚠️ Failed to convert config '{key}' to int: {value}")
            return default
    
    def get_float(self, key: str, default: float = None) -> float:
        """Get configuration value as float."""
        value = self.get(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            print(f"⚠️ Failed to convert config '{key}' to float: {value}")
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
            return default or []
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
    # SPECIALIZED CONFIGURATION METHODS
    # ============================================================================
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.get("DATABASE_URL", "postgresql://localhost:5432/symphainy_dev"),
            "pool_size": self.get_int("DATABASE_POOL_SIZE", 10),
            "max_overflow": self.get_int("DATABASE_MAX_OVERFLOW", 20),
            "echo": self.get_bool("API_DEBUG", False)
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return {
            "url": self.get("REDIS_URL", "redis://localhost:6379/0"),
            "password": self.get("REDIS_PASSWORD", ""),
            "decode_responses": True
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API server configuration."""
        return {
            "host": self.get("API_HOST", "0.0.0.0"),
            "port": self.get_int("API_PORT", 8000),
            "debug": self.get_bool("API_DEBUG", False),
            "reload": self.get_bool("API_RELOAD", False)
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "secret_key": self.get("SECRET_KEY"),
            "jwt_secret": self.get("JWT_SECRET"),
            "jwt_algorithm": self.get("JWT_ALGORITHM", "HS256"),
            "jwt_expiration": self.get_int("JWT_EXPIRATION", 3600)
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            "provider": self.get("LLM_DEFAULT_PROVIDER", "openai"),
            "model": self.get("LLM_MODEL_DEFAULT", "gpt-4o-mini"),
            "temperature": self.get_float("LLM_TEMPERATURE", 0.7),
            "max_tokens": self.get_int("LLM_MAX_TOKENS", 4000),
            "timeout": self.get_int("LLM_TIMEOUT", 30),
            "api_key": self.get("LLM_OPENAI_API_KEY") or self.get("OPENAI_API_KEY")
        }
    
    def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration."""
        return {
            "rate_limiting": {
                "enabled": self.get_bool("LLM_RATE_LIMIT_ENABLED", True),
                "requests_per_minute": self.get_int("LLM_RATE_LIMIT_REQUESTS_PER_MINUTE", 60),
                "requests_per_hour": self.get_int("LLM_RATE_LIMIT_REQUESTS_PER_HOUR", 1000),
                "tokens_per_minute": self.get_int("LLM_RATE_LIMIT_TOKENS_PER_MINUTE", 100000),
                "tokens_per_hour": self.get_int("LLM_RATE_LIMIT_TOKENS_PER_HOUR", 1000000)
            },
            "cost_management": {
                "enabled": self.get_bool("LLM_COST_TRACKING_ENABLED", True),
                "alert_threshold_usd": self.get_float("LLM_COST_ALERT_THRESHOLD_USD", 100.0),
                "budget_monthly_usd": self.get_float("LLM_BUDGET_MONTHLY_USD", 1000.0),
                "alert_percentage": self.get_int("LLM_BUDGET_ALERT_PERCENTAGE", 80)
            },
            "security": {
                "enabled": self.get_bool("LLM_SECURITY_ENABLED", True),
                "content_filtering": self.get_bool("LLM_CONTENT_FILTERING_ENABLED", True),
                "pii_detection": self.get_bool("LLM_PII_DETECTION_ENABLED", True),
                "audit_logging": self.get_bool("LLM_AUDIT_LOGGING_ENABLED", True),
                "response_validation": self.get_bool("LLM_RESPONSE_VALIDATION_ENABLED", True)
            },
            "monitoring": {
                "enabled": self.get_bool("LLM_MONITORING_ENABLED", True),
                "metrics_collection": self.get_bool("LLM_METRICS_COLLECTION_ENABLED", True),
                "response_time_threshold_ms": self.get_int("LLM_RESPONSE_TIME_THRESHOLD_MS", 2000),
                "error_rate_threshold_percent": self.get_float("LLM_ERROR_RATE_THRESHOLD_PERCENT", 5.0),
                "availability_threshold_percent": self.get_float("LLM_AVAILABILITY_THRESHOLD_PERCENT", 99.0)
            }
        }
    
    # ============================================================================
    # CACHING AND PERFORMANCE
    # ============================================================================
    
    def enable_cache(self):
        """Enable configuration caching."""
        self.cache_enabled = True
        print("✅ Configuration caching enabled")
    
    def disable_cache(self):
        """Disable configuration caching."""
        self.cache_enabled = False
        self.config_cache.clear()
        print("✅ Configuration caching disabled")
    
    def clear_cache(self):
        """Clear configuration cache."""
        self.config_cache.clear()
        print("✅ Configuration cache cleared")
    
    def refresh_config(self):
        """Refresh configuration from source."""
        self.clear_cache()
        self._load_configuration()
        print("✅ Configuration refreshed")
    
    # ============================================================================
    # VALIDATION AND HEALTH
    # ============================================================================
    
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
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration manager status."""
        return {
            "service_name": self.service_name,
            "environment": self.environment.value,
            "status": "active",
            "cache_enabled": self.cache_enabled,
            "cached_keys": len(self.config_cache),
            "layers_loaded": len([layer for layer in self.layers if layer.name in self.config_cache]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        print(f"\n🔧 Unified Configuration Summary")
        print(f"Environment: {self.environment.value}")
        print(f"Database: {self.get_database_config()['url']}")
        print(f"Redis: {self.get_redis_config()['url']}")
        print(f"API: {self.get_api_config()['host']}:{self.get_api_config()['port']}")
        print(f"Debug Mode: {self.get_api_config()['debug']}")
        print(f"Logging Level: {self.get('LOG_LEVEL', 'INFO')}")
        print(f"Total Config Keys: {len(self.config_cache)}")


# Create global configuration manager instance
unified_config = UnifiedConfigurationManager()
```

### **Phase 2: Update Utilities Package**

```python
# utilities/__init__.py
"""
Platform-Specific Utilities Package - UPDATED

This package provides comprehensive utilities for all Smart City services in the SymphAIny platform:
- Error handling and management
- Health monitoring and metrics
- Logging and audit trails
- Validation and serialization
- UNIFIED Configuration management (replaces multiple config utilities)
- MCP tool management
- Security utilities

All Smart City services should import and use these utilities for consistent behavior.
"""

from .error import (
    SmartCityError,
    ValidationError,
    ConfigurationError,
    ServiceError,
    IntegrationError,
    MCPError,
    SmartCityErrorHandler,
    get_error_handler
)

from .health import (
    HealthManagementUtility,
    HealthStatus,
    ServiceStatus,
    HealthMetrics,
    HealthCheck,
    HealthReport
)

from .logging import (
    SmartCityLoggingService,
    get_logging_service,
    create_logging_service
)

# New descriptive utilities with bootstrap pattern
from .security_authorization import (
    SecurityAuthorizationUtility,
    UserContext,
    get_security_authorization_utility
)

from .telemetry_reporting import (
    TelemetryReportingUtility,
    get_telemetry_reporting_utility
)

# New platform-specific utilities
from .validation import (
    ValidationUtility,
    ValidationResult
)

from .serialization import (
    SerializationUtility
)

# UNIFIED Configuration Management (replaces multiple config utilities)
from .configuration import (
    UnifiedConfigurationManager,
    unified_config,
    get_configuration_manager
)

from .tenant import (
    TenantManagementUtility
)

__all__ = [
    # Error handling
    "SmartCityError",
    "ValidationError",
    "ConfigurationError", 
    "ServiceError",
    "IntegrationError",
    "MCPError",
    "SmartCityErrorHandler",
    "get_error_handler",
    
    # Health monitoring
    "HealthManagementUtility",
    "HealthStatus",
    "ServiceStatus",
    "HealthMetrics",
    "HealthCheck",
    "HealthReport",
    
    # Logging
    "SmartCityLoggingService",
    "get_logging_service",
    "create_logging_service",
    
    # New descriptive utilities with bootstrap pattern
    "SecurityAuthorizationUtility",
    "UserContext",
    "get_security_authorization_utility",
    "TelemetryReportingUtility",
    "get_telemetry_reporting_utility",
    
    # New platform-specific utilities
    "ValidationUtility",
    "ValidationResult",
    "SerializationUtility",
    
    # UNIFIED Configuration Management
    "UnifiedConfigurationManager",
    "unified_config",
    "get_configuration_manager",
    
    "TenantManagementUtility"
]
```

### **Phase 3: Create Configuration Factory**

```python
# utilities/configuration/__init__.py
"""
Unified Configuration Management

Replaces ConfigurationUtility, EnvironmentLoader, and ConfigManager with a single,
layered configuration system.

WHAT (Configuration Role): I provide unified configuration management with proper layering
HOW (Configuration Implementation): I use layered configuration with secrets separation
"""

from .unified_configuration_manager import (
    UnifiedConfigurationManager,
    unified_config,
    Environment
)

def get_configuration_manager(service_name: str = "unified_config") -> UnifiedConfigurationManager:
    """Get configuration manager instance."""
    return UnifiedConfigurationManager(service_name=service_name)

__all__ = [
    "UnifiedConfigurationManager",
    "unified_config",
    "get_configuration_manager",
    "Environment"
]
```

## 🎯 **MIGRATION STRATEGY**

### **Phase 1: Create Unified Configuration Manager**
1. **Create `utilities/configuration/unified_configuration_manager.py`**
2. **Create layered configuration files**
3. **Test basic functionality**

### **Phase 2: Update Utilities Package**
1. **Update `utilities/__init__.py`** to export unified configuration
2. **Create `utilities/configuration/__init__.py`**
3. **Test integration**

### **Phase 3: Gradual Migration**
1. **Update services to use `unified_config`** instead of `EnvironmentLoader`
2. **Remove old configuration utilities** (ConfigurationUtility, EnvironmentLoader, ConfigManager)
3. **Update all 108 files** that import EnvironmentLoader

### **Phase 4: Configuration File Migration**
1. **Extract secrets to `.env.secrets`**
2. **Create environment-specific configs**
3. **Create business-logic.yaml**
4. **Create infrastructure.yaml**
5. **Remove `platform_env_file_for_cursor.md`**

## 🎯 **BENEFITS OF THIS APPROACH**

### **✅ Single Source of Truth**
- **One configuration manager** instead of three
- **Layered configuration** with proper priority
- **Clean separation** of secrets, environment, business logic, and infrastructure

### **✅ Reduced Complexity**
- **884 lines** of EnvironmentLoader → **~400 lines** of UnifiedConfigurationManager
- **108 files** importing EnvironmentLoader → **1 import** for unified_config
- **3 configuration utilities** → **1 unified configuration manager**

### **✅ Enhanced Developer Experience**
- **Single import**: `from utilities import unified_config`
- **Consistent interface** across all configuration needs
- **Proper layering** with clear priority hierarchy

### **✅ Better Security**
- **Secrets separation** - never committed to version control
- **Environment-specific** configuration
- **Validation** and error reporting

## 📊 **SUCCESS METRICS**

### **Code Reduction**
- **ConfigurationUtility**: 237 lines → **REMOVED**
- **EnvironmentLoader**: 884 lines → **REMOVED**
- **ConfigManager**: 180 lines → **REMOVED**
- **UnifiedConfigurationManager**: ~400 lines → **NEW**

### **Import Reduction**
- **108 files** importing EnvironmentLoader → **1 import** for unified_config
- **Multiple configuration utilities** → **Single unified configuration**

### **Configuration Quality**
- **Secrets separated** from configuration
- **Environment-specific** configs working
- **Business logic** in YAML files
- **Infrastructure** configuration separated

This approach provides **massive simplification** while maintaining **all existing functionality** and adding **enhanced security and layering**! 🎯
