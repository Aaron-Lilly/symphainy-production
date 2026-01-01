"""
Error Handling Utilities for MCP Servers

This module provides comprehensive error handling capabilities for all MCP servers
in the SymphAIny platform, based on the proven patterns from symphainy-mvp.
"""

from .error_handler import (
    SmartCityError,
    ValidationError,
    ConfigurationError,
    ServiceError,
    IntegrationError,
    MCPError,
    SmartCityErrorHandler,
    get_error_handler
)

__all__ = [
    "SmartCityError",
    "ValidationError", 
    "ConfigurationError",
    "ServiceError",
    "IntegrationError",
    "MCPError",
    "SmartCityErrorHandler",
    "get_error_handler"
]







