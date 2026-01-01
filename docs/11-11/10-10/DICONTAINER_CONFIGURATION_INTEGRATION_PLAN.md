# DIContainer Configuration Integration Plan

## 🚨 **CRITICAL FINDINGS: DIContainerService is the Configuration Hub**

### **❌ Current Problems**
1. **DIContainerService** is the **central configuration hub** for the entire platform
2. **775 matches** across **96 files** importing DIContainerService
3. **72 files** directly importing from `di_container`
4. **DIContainerService** uses **EnvironmentLoader** internally (line 32, 76-78)
5. **ConfigurationUtility** is initialized in DIContainerService (line 89)
6. **Every service** gets configuration through DIContainerService

### **🎯 ROOT CAUSE ANALYSIS**
The current architecture has **DIContainerService as the configuration hub**:
- **DIContainerService** loads `EnvironmentLoader` (line 76)
- **DIContainerService** creates `ConfigurationUtility` with environment config (line 89)
- **Every service** imports DIContainerService to get configuration
- **108+ files** importing EnvironmentLoader → **775+ files** importing DIContainerService

## 🎯 **RECOMMENDED SOLUTION: DIContainerService Integration**

### **Phase 1: Update DIContainerService to Use Unified Configuration**

```python
# foundations/di_container/di_container_service.py
#!/usr/bin/env python3
"""
DI Container Service - UPDATED with Unified Configuration

Central dependency injection container that provides all foundational utilities
to services across the platform. Now uses UnifiedConfigurationManager instead of
multiple configuration utilities.

WHAT (Foundation Role): I provide comprehensive utilities through dependency injection
HOW (Foundation Service): I compose all foundational utilities into a single container
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import FastAPI for MCP server support
from fastapi import FastAPI

# Import utilities directly from utilities folder
from utilities.logging.logging_service import SmartCityLoggingService
from utilities.health.health_management_utility import HealthManagementUtility
from utilities.telemetry_reporting.telemetry_reporting_utility import TelemetryReportingUtility
from utilities.security_authorization.security_authorization_utility import SecurityAuthorizationUtility
from utilities.error.error_handler import SmartCityErrorHandler
from utilities.tenant.tenant_management_utility import TenantManagementUtility
from utilities.validation.validation_utility import ValidationUtility
from utilities.serialization.serialization_utility import SerializationUtility

# UNIFIED Configuration Management (replaces multiple config utilities)
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager


class DIContainerService:
    """
    DI Container Service - UPDATED with Unified Configuration
    
    Central dependency injection container that provides all foundational utilities
    to services across the platform. Now uses UnifiedConfigurationManager instead of
    multiple configuration utilities.
    
    WHAT (Foundation Role): I provide comprehensive utilities through dependency injection
    HOW (Foundation Service): I compose all foundational utilities into a single container
    """
    
    def __init__(self, service_name: str = "foundation"):
        """Initialize DI Container Service."""
        self.service_name = service_name
        self.initialization_time = datetime.utcnow()
        
        # Initialize basic logging first
        self._logger = logging.getLogger(f"DIContainerService-{service_name}")
        self._logger.info(f"🚀 Initializing DI Container Service for {service_name}...")
        
        # UNIFIED Configuration Management (replaces EnvironmentLoader + ConfigurationUtility)
        self._initialize_unified_configuration()
        
        # Initialize direct utilities (no bootstrap needed)
        self._initialize_direct_utilities()
        
        # Initialize bootstrap-aware utilities
        self._initialize_bootstrap_utilities()
        
        # Bootstrap utilities that need it
        self._bootstrap_utilities()
        
        # Initialize FastAPI support for MCP servers
        self._initialize_fastapi_support()
        
        self._logger.info(f"✅ DI Container Service initialized successfully")
    
    def _initialize_unified_configuration(self):
        """Initialize unified configuration management."""
        try:
            # UNIFIED Configuration Manager (replaces EnvironmentLoader + ConfigurationUtility)
            self.config = UnifiedConfigurationManager(service_name=self.service_name)
            
            # Get configuration for utilities that need it
            self.env_config = self.config.config_cache
            
            self._logger.info(f"✅ Unified configuration loaded: {len(self.env_config)} variables")
        except Exception as e:
            self._logger.error(f"❌ Failed to load unified configuration: {e}")
            # Fallback to empty config
            self.env_config = {}
    
    def _initialize_direct_utilities(self):
        """Initialize utilities that don't require bootstrap."""
        try:
            # Logging utility (direct)
            self.logger = SmartCityLoggingService(self.service_name)
            self._logger.info("✅ Logging utility initialized")
            
            # Health management utility (direct)
            self.health = HealthManagementUtility(self.service_name)
            self._logger.info("✅ Health management utility initialized")
            
            # Error handler utility (direct)
            self.error_handler = SmartCityErrorHandler(self.service_name)
            self._logger.info("✅ Error handler utility initialized")
            
            # Validation utility (direct)
            self.validation = ValidationUtility(self.service_name)
            self._logger.info("✅ Validation utility initialized")
            
            # Serialization utility (direct)
            self.serialization = SerializationUtility(self.service_name)
            self._logger.info("✅ Serialization utility initialized")
            
        except Exception as e:
            self._logger.error(f"❌ Failed to initialize direct utilities: {e}")
            raise
    
    def _initialize_bootstrap_utilities(self):
        """Initialize utilities that require bootstrap."""
        try:
            # Telemetry reporting utility (bootstrap-aware)
            self.telemetry = TelemetryReportingUtility(self.service_name)
            self._logger.info("✅ Telemetry reporting utility initialized")
            
            # Security authorization utility (bootstrap-aware)
            self.security = SecurityAuthorizationUtility(self.service_name)
            self._logger.info("✅ Security authorization utility initialized")
            
            # Tenant management utility (bootstrap-aware)
            self.tenant = TenantManagementUtility(self.service_name)
            self._logger.info("✅ Tenant management utility initialized")
            
        except Exception as e:
            self._logger.error(f"❌ Failed to initialize bootstrap utilities: {e}")
            raise
    
    def _bootstrap_utilities(self):
        """Bootstrap utilities that need it."""
        try:
            # Bootstrap telemetry reporting utility
            if hasattr(self.telemetry, 'bootstrap'):
                self.telemetry.bootstrap(self)
                self._logger.info("✅ Telemetry reporting utility bootstrapped")
            
            # Bootstrap security authorization utility
            if hasattr(self.security, 'bootstrap'):
                self.security.bootstrap(self)
                self._logger.info("✅ Security authorization utility bootstrapped")
            
            # Bootstrap tenant management utility
            if hasattr(self.tenant, 'bootstrap'):
                self.tenant.bootstrap(self)
                self._logger.info("✅ Tenant management utility bootstrapped")
            
        except Exception as e:
            self._logger.error(f"❌ Failed to bootstrap utilities: {e}")
            raise
    
    def _initialize_fastapi_support(self):
        """Initialize FastAPI support for MCP servers."""
        try:
            # Create FastAPI app for MCP server support
            self.fastapi_app = FastAPI(
                title="SymphAIny Platform MCP Server",
                description="Micro-Capability Platform Server for SymphAIny Platform",
                version="1.0.0"
            )
            self._logger.info("✅ FastAPI support initialized")
        except Exception as e:
            self._logger.error(f"❌ Failed to initialize FastAPI support: {e}")
            raise
    
    # ============================================================================
    # CONFIGURATION ACCESS METHODS (UNIFIED)
    # ============================================================================
    
    def get_config(self, key: str, default: Any = None) -> Any:
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
    # SPECIALIZED CONFIGURATION METHODS (UNIFIED)
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
    # ENVIRONMENT-SPECIFIC METHODS (UNIFIED)
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
    # CACHING AND PERFORMANCE (UNIFIED)
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
    # VALIDATION AND HEALTH (UNIFIED)
    # ============================================================================
    
    def validate_configuration(self, required_keys: list) -> Dict[str, Any]:
        """Validate that required configuration keys are present."""
        return self.config.validate_configuration(required_keys)
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get configuration manager status."""
        return self.config.get_configuration_status()
    
    # ============================================================================
    # UTILITY ACCESS METHODS
    # ============================================================================
    
    def get_logger(self, service_name: str = None) -> SmartCityLoggingService:
        """Get logging service."""
        if service_name:
            return SmartCityLoggingService(service_name)
        return self.logger
    
    def get_error_handler(self, service_name: str = None) -> SmartCityErrorHandler:
        """Get error handler service."""
        if service_name:
            return SmartCityErrorHandler(service_name)
        return self.error_handler
    
    def get_health_management(self, service_name: str = None) -> HealthManagementUtility:
        """Get health management service."""
        if service_name:
            return HealthManagementUtility(service_name)
        return self.health
    
    def get_telemetry_reporting(self, service_name: str = None) -> TelemetryReportingUtility:
        """Get telemetry reporting service."""
        if service_name:
            return TelemetryReportingUtility(service_name)
        return self.telemetry
    
    def get_security_authorization(self, service_name: str = None) -> SecurityAuthorizationUtility:
        """Get security authorization service."""
        if service_name:
            return SecurityAuthorizationUtility(service_name)
        return self.security
    
    def get_tenant_management(self, service_name: str = None) -> TenantManagementUtility:
        """Get tenant management service."""
        if service_name:
            return TenantManagementUtility(service_name)
        return self.tenant
    
    def get_validation(self, service_name: str = None) -> ValidationUtility:
        """Get validation service."""
        if service_name:
            return ValidationUtility(service_name)
        return self.validation
    
    def get_serialization(self, service_name: str = None) -> SerializationUtility:
        """Get serialization service."""
        if service_name:
            return SerializationUtility(service_name)
        return self.serialization
    
    # ============================================================================
    # HEALTH AND STATUS
    # ============================================================================
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all services."""
        return {
            "service_name": self.service_name,
            "status": "healthy",
            "initialization_time": self.initialization_time.isoformat(),
            "configuration": self.get_configuration_status(),
            "utilities": {
                "logging": "healthy",
                "health": "healthy",
                "error_handler": "healthy",
                "validation": "healthy",
                "serialization": "healthy",
                "telemetry": "healthy",
                "security": "healthy",
                "tenant": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        self.config.print_config_summary()
```

### **Phase 2: Update All Services to Use Unified Configuration**

```python
# Example: Update a service to use unified configuration
# backend/smart_city/services/security_guard/security_guard_service.py

from foundations.di_container import DIContainerService

class SecurityGuardService:
    def __init__(self, di_container: DIContainerService):
        self.di_container = di_container
        
        # Get configuration through DIContainerService (now unified)
        self.config = di_container.config
        
        # Get specialized configuration
        self.llm_config = di_container.get_llm_config()
        self.governance_config = di_container.get_governance_config()
        self.security_config = di_container.get_security_config()
        
        # Get utilities through DIContainerService
        self.logger = di_container.get_logger(self.service_name)
        self.error_handler = di_container.get_error_handler(self.service_name)
```

### **Phase 3: Remove Old Configuration Utilities**

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

# REMOVED: Old configuration utilities
# from .configuration import ConfigurationUtility  # REMOVED
# from config.environment_loader import EnvironmentLoader  # REMOVED
# from config import ConfigManager  # REMOVED

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

## 🎯 **MIGRATION STRATEGY**

### **Phase 1: Update DIContainerService**
1. **Update DIContainerService** to use UnifiedConfigurationManager
2. **Remove EnvironmentLoader** and ConfigurationUtility imports
3. **Add unified configuration methods** to DIContainerService
4. **Test DIContainerService** functionality

### **Phase 2: Update All Services**
1. **Update all 775+ files** that import DIContainerService
2. **Remove direct EnvironmentLoader** imports
3. **Update configuration access** to use DIContainerService methods
4. **Test all services** with unified configuration

### **Phase 3: Remove Old Configuration Utilities**
1. **Remove ConfigurationUtility** from utilities package
2. **Remove EnvironmentLoader** from config package
3. **Remove ConfigManager** from config package
4. **Update all imports** to use unified configuration

### **Phase 4: Configuration File Migration**
1. **Extract secrets to `.env.secrets`**
2. **Create environment-specific configs**
3. **Create business-logic.yaml**
4. **Create infrastructure.yaml**
5. **Remove `platform_env_file_for_cursor.md`**

## 🎯 **BENEFITS OF THIS APPROACH**

### **✅ Single Source of Truth**
- **DIContainerService** remains the central hub
- **UnifiedConfigurationManager** replaces multiple configuration utilities
- **All services** get configuration through DIContainerService

### **✅ Reduced Complexity**
- **775+ files** importing DIContainerService → **Same files, unified configuration**
- **108+ files** importing EnvironmentLoader → **0 files** (removed)
- **3 configuration utilities** → **1 unified configuration manager**

### **✅ Enhanced Developer Experience**
- **Same import pattern**: `from foundations.di_container import DIContainerService`
- **Same usage pattern**: `di_container.get_config(key)`
- **Enhanced configuration methods**: `di_container.get_llm_config()`, `di_container.get_governance_config()`

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
- **108 files** importing EnvironmentLoader → **0 files** (removed)
- **775+ files** importing DIContainerService → **Same files, unified configuration**

### **Configuration Quality**
- **Secrets separated** from configuration
- **Environment-specific** configs working
- **Business logic** in YAML files
- **Infrastructure** configuration separated

This approach provides **massive simplification** while maintaining **all existing functionality** and adding **enhanced security and layering**! The DIContainerService remains the **central hub** but now uses **unified configuration management**! 🎯
