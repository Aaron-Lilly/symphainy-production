"""
Consolidated Logging Service for MCP Servers

This service provides a single, consistent logging pattern across all
MCP servers in the SymphAIny platform, based on proven patterns from symphainy-mvp.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime
from .trace_context_formatter import TraceContextFormatter

class SmartCityLoggingService:
    """Consolidated logging service for MCP servers."""

    def __init__(self, service_name: str, log_level: str = "INFO"):
        """Initialize the logging service."""
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())

        # Create logger
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(self.log_level)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers with trace context formatter."""
        # Console handler with trace context formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_formatter = TraceContextFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [trace_id=%(trace_id)s request_id=%(request_id)s user_id=%(user_id)s] - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler with trace context formatter
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.service_name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_formatter = TraceContextFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [trace_id=%(trace_id)s request_id=%(request_id)s user_id=%(user_id)s] - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def info(self, message: str, **kwargs):
        """Log info message with trace context."""
        # Ensure trace_id is in extra if not already provided
        if 'trace_id' not in kwargs:
            trace_id = self._get_trace_id()
            if trace_id:
                kwargs['trace_id'] = trace_id
        self.logger.info(f"[{self.service_name}] {message}", extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with trace context."""
        if 'trace_id' not in kwargs:
            trace_id = self._get_trace_id()
            if trace_id:
                kwargs['trace_id'] = trace_id
        self.logger.warning(f"[{self.service_name}] {message}", extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with trace context."""
        if 'trace_id' not in kwargs:
            trace_id = self._get_trace_id()
            if trace_id:
                kwargs['trace_id'] = trace_id
        self.logger.error(f"[{self.service_name}] {message}", extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with trace context."""
        if 'trace_id' not in kwargs:
            trace_id = self._get_trace_id()
            if trace_id:
                kwargs['trace_id'] = trace_id
        self.logger.debug(f"[{self.service_name}] {message}", extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with trace context."""
        if 'trace_id' not in kwargs:
            trace_id = self._get_trace_id()
            if trace_id:
                kwargs['trace_id'] = trace_id
        self.logger.critical(f"[{self.service_name}] {message}", extra=kwargs)
    
    def _get_trace_id(self) -> Optional[str]:
        """
        Extract trace_id from OpenTelemetry context.
        
        Returns:
            Trace ID as hex string, or None if no active trace
        """
        try:
            from opentelemetry import trace
            
            # Get current span from context
            current_span = trace.get_current_span()
            
            if current_span and hasattr(current_span, 'get_span_context'):
                span_context = current_span.get_span_context()
                
                if span_context and span_context.is_valid:
                    # Convert trace_id to hex string (OpenTelemetry uses 128-bit IDs)
                    trace_id = format(span_context.trace_id, '032x')
                    return trace_id
            
            return None
            
        except ImportError:
            # OpenTelemetry not installed - return None
            return None
        except Exception:
            # Any other error - return None (fail gracefully)
            return None

    def log_service_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log a structured service event."""
        event_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "event_data": event_data
        }
        self.logger.info(f"Service Event: {json.dumps(event_log)}")

    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log an error with additional context."""
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.logger.error(f"Error with Context: {json.dumps(error_log)}")

    def log_function_call(self, function_name: str, args: Dict[str, Any], result: Any = None):
        """Standardized function call logging."""
        self.info(f"Function called: {function_name}", args=args, result=result)

    def log_mcp_tool_call(self, tool_name: str, input_data: Dict[str, Any], result: Any = None):
        """Log MCP tool calls."""
        tool_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "tool_name": tool_name,
            "input_data": input_data,
            "result": result
        }
        self.logger.info(f"MCP Tool Call: {json.dumps(tool_log)}")

    def log_mcp_server_event(self, event_type: str, server_name: str, event_data: Dict[str, Any]):
        """Log MCP server events."""
        server_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "mcp_server": server_name,
            "event_type": event_type,
            "event_data": event_data
        }
        self.logger.info(f"MCP Server Event: {json.dumps(server_log)}")

# Global logging service factory
def get_logging_service(service_name: str, log_level: str = "INFO", config=None) -> SmartCityLoggingService:
    """Get a logging service instance with optional configuration injection."""
    if config and hasattr(config, 'log_level'):
        log_level = config.log_level
    return SmartCityLoggingService(service_name, log_level)

# Factory function for infrastructure service compatibility
def create_logging_service(service_name: str, log_level: str = "INFO") -> SmartCityLoggingService:
    """Create a logging service instance (alias for compatibility)."""
    return SmartCityLoggingService(service_name, log_level)












