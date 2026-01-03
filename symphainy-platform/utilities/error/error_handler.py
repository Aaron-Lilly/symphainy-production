"""
Consolidated Error Handling Service for MCP Servers

This service provides a single, consistent error handling pattern across all
MCP servers in the SymphAIny platform, based on proven patterns from symphainy-mvp.

Updated to use OpenTelemetry-aware logging service for automatic trace correlation.
"""

import traceback
import sys
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
from pathlib import Path

# Import logging service for OpenTelemetry-aware logging
try:
    # Try relative import first (utilities/error -> utilities/logging)
    from ..logging.logging_service import get_logging_service
    _LOGGING_SERVICE_AVAILABLE = True
except ImportError:
    try:
        # Try absolute import
        from utilities.logging.logging_service import get_logging_service
        _LOGGING_SERVICE_AVAILABLE = True
    except ImportError:
        # Fallback to standard logging if logging service not available
        import logging
        _LOGGING_SERVICE_AVAILABLE = False

class SmartCityError(Exception):
    """Base error class for Smart City MCP Servers."""

    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.traceback = traceback.format_exc()

class ValidationError(SmartCityError):
    """Error raised when validation fails."""
    pass

class ConfigurationError(SmartCityError):
    """Error raised when configuration is invalid."""
    pass

class ServiceError(SmartCityError):
    """Error raised when a service operation fails."""
    pass

class IntegrationError(SmartCityError):
    """Error raised when integration between services fails."""
    pass

class MCPError(SmartCityError):
    """Error raised when MCP server operations fail."""
    pass

class SmartCityErrorHandler:
    """
    Consolidated error handler for MCP servers.
    
    Uses OpenTelemetry-aware logging service for automatic trace correlation.
    Falls back to standard logging if logging service not available.
    """

    def __init__(self, service_name: str):
        """Initialize the error handler."""
        self.service_name = service_name
        self.error_handlers: Dict[str, Callable] = {}
        self.error_log: list = []

        # Initialize logging (OpenTelemetry-aware if available)
        # Use lazy initialization to avoid requiring ConfigAdapter at module import time
        try:
            if _LOGGING_SERVICE_AVAILABLE:
                self.logger = get_logging_service(service_name)
            else:
                # Fallback to standard logging
                self.logger = logging.getLogger(f"ErrorHandler-{service_name}")
        except (ValueError, Exception) as e:
            # If logging service requires ConfigAdapter and it's not available yet, use standard logging
            if not _LOGGING_SERVICE_AVAILABLE:
                import logging
            self.logger = logging.getLogger(f"ErrorHandler-{service_name}")
            self.logger.warning(f"Using standard logging fallback (ConfigAdapter not available): {e}")

        # Register default error handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default error handlers."""
        self.register_error_handler(ValidationError, self._handle_validation_error)
        self.register_error_handler(ConfigurationError, self._handle_configuration_error)
        self.register_error_handler(ServiceError, self._handle_service_error)
        self.register_error_handler(IntegrationError, self._handle_integration_error)
        self.register_error_handler(MCPError, self._handle_mcp_error)
        self.register_error_handler(Exception, self._handle_generic_error)

    def register_error_handler(self, error_type: type, handler: Callable):
        """Register a custom error handler."""
        self.error_handlers[error_type.__name__] = handler

    async def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                          telemetry: Optional[Any] = None) -> Dict[str, Any]:
        """
        Handle an error using registered handlers with telemetry integration.
        
        Args:
            error: The exception to handle
            context: Optional context dictionary with operation details
            telemetry: Optional telemetry utility for error tracking
        
        Returns:
            Dictionary with error information and handler result
        """
        # Extract trace_id from OpenTelemetry context (if available)
        trace_id = None
        try:
            from opentelemetry import trace
            current_span = trace.get_current_span()
            if current_span and hasattr(current_span, 'get_span_context'):
                span_context = current_span.get_span_context()
                if span_context and span_context.is_valid:
                    trace_id = format(span_context.trace_id, '032x')
        except Exception:
            # OpenTelemetry not available or error - continue without trace_id
            pass

        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc(),
            "trace_id": trace_id  # Include trace_id for correlation
        }

        # Log the error (with trace_id if available)
        self.error_log.append(error_info)
        
        # Log error using logging service (includes trace_id automatically)
        if _LOGGING_SERVICE_AVAILABLE and hasattr(self.logger, 'error'):
            # Use logging service's error method (includes trace correlation)
            self.logger.error(
                f"Error in {self.service_name}: {str(error)}",
                error_type=type(error).__name__,
                error_code=getattr(error, 'error_code', 'UNKNOWN_ERROR'),
                context=context or {}
            )
        else:
            # Fallback to standard logging
            self.logger.error(f"Error in {self.service_name}: {str(error)}", exc_info=True)

        # Record platform error event if telemetry available (reports to Nurse Service)
        if telemetry:
            try:
                operation = context.get("operation", "unknown") if context else "unknown"
                await telemetry.record_platform_error_event("error_occurred", {
                    "operation": operation,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "service": self.service_name,
                    "error_code": getattr(error, 'error_code', 'UNKNOWN_ERROR')
                })
            except Exception as telemetry_error:
                # Don't fail error handling if telemetry fails
                # Log telemetry failure but continue with error handling
                pass

        # Find and execute appropriate handler
        error_type_name = type(error).__name__
        if error_type_name in self.error_handlers:
            handler_result = self.error_handlers[error_type_name](error, context)
            error_info["handler_result"] = handler_result
        else:
            # Use generic handler
            handler_result = self._handle_generic_error(error, context)
            error_info["handler_result"] = handler_result

        return error_info

    def _handle_validation_error(self, error: ValidationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors."""
        return {
            "action": "retry_with_correction",
            "severity": "warning",
            "user_message": f"Validation failed: {error.message}",
            "suggestions": ["Check input data", "Verify format requirements"],
            "error_code": error.error_code
        }

    def _handle_configuration_error(self, error: ConfigurationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration errors."""
        return {
            "action": "check_configuration",
            "severity": "error",
            "user_message": f"Configuration error: {error.message}",
            "suggestions": ["Verify environment variables", "Check configuration files"],
            "error_code": error.error_code
        }

    def _handle_service_error(self, error: ServiceError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle service errors."""
        return {
            "action": "retry_operation",
            "severity": "error",
            "user_message": f"Service error: {error.message}",
            "suggestions": ["Retry the operation", "Check service status"],
            "error_code": error.error_code
        }

    def _handle_integration_error(self, error: IntegrationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle integration errors."""
        return {
            "action": "check_connectivity",
            "severity": "error",
            "user_message": f"Integration error: {error.message}",
            "suggestions": ["Check network connectivity", "Verify service endpoints"],
            "error_code": error.error_code
        }

    def _handle_mcp_error(self, error: MCPError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP server errors."""
        return {
            "action": "check_mcp_server",
            "severity": "error",
            "user_message": f"MCP server error: {error.message}",
            "suggestions": ["Check MCP server status", "Verify MCP server configuration"],
            "error_code": error.error_code
        }

    def _handle_generic_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic errors."""
        return {
            "action": "log_and_continue",
            "severity": "error",
            "user_message": f"An unexpected error occurred: {str(error)}",
            "suggestions": ["Check logs for details", "Contact support if problem persists"],
            "error_code": "UNKNOWN_ERROR"
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all handled errors."""
        if not self.error_log:
            return {"total_errors": 0, "errors": []}

        error_counts = {}
        for error_info in self.error_log:
            error_type = error_info["error_type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        return {
            "total_errors": len(self.error_log),
            "error_counts": error_counts,
            "recent_errors": self.error_log[-5:],  # Last 5 errors
            "service": self.service_name
        }

    def clear_error_log(self):
        """Clear the error log."""
        self.error_log.clear()

    def handle_service_error(self, error: Exception, service_name: str, context: Dict[str, Any]):
        """Handle service errors with backward compatibility."""
        return self.handle_error(error, context)

# Global error handler factory
def get_error_handler(service_name: str, config=None) -> SmartCityErrorHandler:
    """Get an error handler for the specified service with optional configuration injection."""
    return SmartCityErrorHandler(service_name)

# Default error handler (lazy initialization to avoid requiring ConfigAdapter at module import time)
# DO NOT initialize at module import time - causes startup failures
_default_error_handler = None

def get_default_error_handler() -> SmartCityErrorHandler:
    """Get the default error handler (lazy initialization)."""
    global _default_error_handler
    if _default_error_handler is None:
        _default_error_handler = get_error_handler("mcp_platform")
    return _default_error_handler

# For backward compatibility, create a lazy wrapper
class _LazyDefaultErrorHandler:
    """Lazy wrapper for default error handler to avoid module import initialization."""
    def __call__(self):
        return get_default_error_handler()
    def __getattr__(self, name):
        return getattr(get_default_error_handler(), name)

default_error_handler = _LazyDefaultErrorHandler()












