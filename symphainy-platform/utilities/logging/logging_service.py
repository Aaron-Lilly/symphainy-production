"""
Updated Logging Service with OpenTelemetry Support

This is an updated version of logging_service.py that adds OpenTelemetry OTLP support
while maintaining 100% backward compatibility with existing code.

Best Practice: Uses both console/file logging AND OTLP export:
- Console/file: Immediate visibility, local debugging, human-readable
- OTLP: Centralized aggregation, trace correlation, production monitoring

Production Requirements:
- OTLP is REQUIRED in production (fails fast if not configured)
- Console/file logging is always enabled (both environments)

Development:
- OTLP is optional (warns but continues)
- Console/file logging always works

WHAT (Utility Role): I provide logging with automatic OpenTelemetry integration
HOW (Utility Implementation): I add OTLP handler when OpenTelemetry is configured, 
                              require it in production, make it optional in development
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime
from .trace_context_formatter import TraceContextFormatter


class SmartCityLoggingService:
    """
    Consolidated logging service with OpenTelemetry support.
    
    Automatically adds OTLP handler if OpenTelemetry is configured,
    maintains backward compatibility with existing code.
    """

    def __init__(self, service_name: str, log_level: str = "INFO", config_adapter=None):
        """
        Initialize the logging service.
        
        Args:
            service_name: Name of the service
            log_level: Logging level (default: INFO)
            config_adapter: Optional ConfigAdapter for reading configuration (preferred over os.getenv)
        """
        self.service_name = service_name
        self.config_adapter = config_adapter
        self.log_level = getattr(logging, log_level.upper())

        # Create logger
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(self.log_level)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup logging handlers with OpenTelemetry support."""
        # Console handler with trace context formatter (for debugging)
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

        # OTLP handler (optional - only if OpenTelemetry is configured)
        self._setup_otlp_handler()

    def _setup_otlp_handler(self):
        """
        Setup OTLP handler for automatic log aggregation.
        
        Best Practice: Always use both console/file AND OTLP export.
        - Console/file: For local development, debugging, immediate visibility
        - OTLP: For centralized aggregation, trace correlation, production monitoring
        
        Production: OTLP is REQUIRED (fails if not configured)
        Development: OTLP is optional (warns but continues)
        """
        try:
            # Check if OpenTelemetry logging instrumentation is available
            from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
            from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
            from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
            from opentelemetry._logs import get_logger_provider, set_logger_provider
            
            # Check if OTLP endpoint is configured
            # Use ConfigAdapter if available (preferred), otherwise fallback to os.getenv()
            if self.config_adapter:
                otlp_endpoint = self.config_adapter.get("OTEL_EXPORTER_OTLP_ENDPOINT") or self.config_adapter.get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")
                environment = self.config_adapter.get("ENVIRONMENT", "development")
                if isinstance(environment, str):
                    environment = environment.lower()
            else:
                otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")
                environment = os.getenv("ENVIRONMENT", "development").lower()
                if otlp_endpoint:
                    logging.getLogger(__name__).warning("⚠️ [LOGGING_SERVICE] Using os.getenv() - consider passing config_adapter for centralized configuration")
            
            is_production = environment in ["production", "prod"]
            
            if not otlp_endpoint:
                if is_production:
                    # Production requires OTLP - fail fast
                    raise RuntimeError(
                        "OTEL_EXPORTER_OTLP_ENDPOINT is required in production but not configured. "
                        "Set OTEL_EXPORTER_OTLP_ENDPOINT environment variable to enable log aggregation and trace correlation."
                    )
                else:
                    # Development: OTLP optional - warn but continue
                    logging.getLogger(__name__).warning(
                        f"⚠️ OTLP endpoint not configured for {self.service_name}. "
                        "Logs will only go to console/file (not to Loki). "
                        "Set OTEL_EXPORTER_OTLP_ENDPOINT to enable centralized log aggregation."
                    )
                    return
            
            # Get or create logger provider
            # Check if we have a real LoggerProvider (not NoOpLoggerProvider)
            logger_provider = get_logger_provider()
            if logger_provider is None or not hasattr(logger_provider, 'add_log_record_processor'):
                # Create new logger provider with resource
                from opentelemetry.sdk.resources import Resource
                resource = Resource.create({
                    "service.name": self.service_name,
                    "service.namespace": "symphainy-platform"
                })
                logger_provider = LoggerProvider(resource=resource)
                set_logger_provider(logger_provider)
            
            # Create OTLP log exporter
            log_exporter = OTLPLogExporter(
                endpoint=otlp_endpoint,
                insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"
            )
            
            # Add batch processor
            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(log_exporter)
            )
            
            # Create OTLP handler (no formatter needed - OpenTelemetry handles correlation)
            otlp_handler = LoggingHandler(logger_provider=logger_provider)
            otlp_handler.setLevel(self.log_level)
            
            # Add to logger
            self.logger.addHandler(otlp_handler)
            
            # Log success (but only once to avoid spam)
            if not hasattr(SmartCityLoggingService, '_otlp_handler_logged'):
                env_msg = "REQUIRED" if is_production else "enabled"
                logging.getLogger(__name__).info(
                    f"✅ OTLP handler {env_msg} for {self.service_name} → {otlp_endpoint}"
                )
                SmartCityLoggingService._otlp_handler_logged = True
                
        except ImportError:
            # OpenTelemetry logging instrumentation not installed
            environment = os.getenv("ENVIRONMENT", "development").lower()
            is_production = environment in ["production", "prod"]
            
            if is_production:
                # Production requires OpenTelemetry - fail fast
                raise RuntimeError(
                    "opentelemetry-instrumentation-logging is required in production but not installed. "
                    "Install with: pip install opentelemetry-instrumentation-logging"
                )
            else:
                # Development: OpenTelemetry optional - warn but continue
                logging.getLogger(__name__).warning(
                    f"⚠️ OpenTelemetry logging instrumentation not installed for {self.service_name}. "
                    "Install opentelemetry-instrumentation-logging to enable OTLP log export. "
                    "Falling back to console/file logging."
                )
        except RuntimeError:
            # Re-raise RuntimeErrors (production requirements)
            raise
        except Exception as e:
            # Any other error - check environment
            environment = os.getenv("ENVIRONMENT", "development").lower()
            is_production = environment in ["production", "prod"]
            
            if is_production:
                # Production: Fail fast on OTLP setup errors
                raise RuntimeError(
                    f"Failed to setup OTLP handler in production: {e}. "
                    "OTLP is required for log aggregation and trace correlation."
                ) from e
            else:
                # Development: Warn but continue
                logging.getLogger(__name__).warning(
                    f"⚠️ Failed to setup OTLP handler for {self.service_name}: {e}. "
                    "Falling back to console/file logging."
                )

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
        # Use exc_info=False to avoid LogRecord conflicts with TraceContextFormatter
        # OpenTelemetry OTLP handler will capture exception info automatically if needed
        exc_info = kwargs.pop('exc_info', False)
        self.logger.error(f"[{self.service_name}] {message}", extra=kwargs, exc_info=exc_info)

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
        # Use exc_info=False to avoid conflicts
        self.logger.error(f"Error with Context: {json.dumps(error_log)}", exc_info=False)

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

