"""
Platform-Specific Utilities Package

This package provides comprehensive utilities for all Smart City services in the SymphAIny platform:
- Error handling and management
- Health monitoring and metrics
- Logging and audit trails
- Validation and serialization
- Configuration management
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

# Legacy utilities (archived - imports removed)
# from .telemetry import TelemetryService, get_telemetry_service
# from .security.security_service import SecurityService, get_security_service

# New platform-specific utilities
from .validation import (
    ValidationUtility,
    ValidationResult
)

from .serialization import (
    SerializationUtility
)

from .configuration import (
    ConfigurationUtility
)

from .tenant import (
    TenantManagementUtility
)

# MCP functionality moved to bases/mcp_server_base.py
# from .mcp import (
#     MCPUtilities,
#     MCPToolDefinition,
#     MCPExecutionResult
# )

# from .mcp_base import MCPBaseServer  # Removed - using clean version from protocols

# Archived base classes (removed from active codebase)
# from .dimension_manager_base import DimensionManagerBase  # Archived
# from .broker_base import BrokerBase  # Not used in active code - only examples

# Tool factory moved to agentic dimension
# from .tool_factory import (
#     ToolFactoryService,
#     ToolDiscoveryEngine,
#     ToolExecutionEngine,
#     ToolAnalyticsEngine,
#     ToolNotFoundError,
#     ToolNotPublicError,
#     ServiceNotAvailableError,
#     ToolExecutionError,
#     get_tool_factory
# )

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
    
    # Legacy utilities (archived - removed from exports)
    # "TelemetryService",
    # "get_telemetry_service", 
    # "SecurityService",
    # "get_security_service",
    
    # New platform-specific utilities
    "ValidationUtility",
    "ValidationResult",
    "SerializationUtility",
    "ConfigurationUtility",
    "TenantManagementUtility",
    # MCP functionality moved to bases/mcp_server_base.py
    # "MCPUtilities",
    # "MCPToolDefinition", 
    # "MCPExecutionResult",
    
    # Tool Factory (moved to agentic dimension)
    # "ToolFactoryService",
    # "ToolDiscoveryEngine",
    # "ToolExecutionEngine",
    # "ToolAnalyticsEngine",
    # "ToolNotFoundError",
    # "ToolNotPublicError",
    # "ServiceNotAvailableError",
    # "ToolExecutionError",
    # "get_tool_factory",
    
    # Base MCP Servers
    # "MCPBaseServer",  # Removed - using clean version from protocols
    
    # Archived base classes (removed from active codebase)
    # "DimensionManagerBase",  # Archived
    # "BrokerBase"  # Not used in active code - only examples
]
