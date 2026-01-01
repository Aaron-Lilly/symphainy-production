#!/usr/bin/env python3
"""
Trace Context Formatter for Logging

Automatically injects OpenTelemetry trace_id into all log records.
This enables log-to-trace correlation without modifying individual log calls.

WHAT (Utility Role): I provide trace context injection for logging
HOW (Utility Implementation): I extract trace_id from OpenTelemetry context and add it to log records
"""

import logging
from typing import Optional


class TraceContextFormatter(logging.Formatter):
    """
    Custom formatter that automatically injects trace_id from OpenTelemetry context.
    
    This formatter extracts the current trace_id from OpenTelemetry's context
    and adds it to every log record, enabling automatic log-to-trace correlation.
    """
    
    def __init__(self, fmt=None, datefmt=None, include_trace_id=True):
        """
        Initialize trace context formatter.
        
        Args:
            fmt: Format string (defaults to standard format with trace_id)
            datefmt: Date format string
            include_trace_id: Whether to include trace_id in formatted output
        """
        # Default format includes trace_id
        if fmt is None:
            fmt = '%(asctime)s - %(name)s - %(levelname)s - [trace_id=%(trace_id)s] - %(message)s'
        
        super().__init__(fmt, datefmt)
        self.include_trace_id = include_trace_id
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with trace_id, request_id, and user_id injection.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Extract trace_id from OpenTelemetry context
        trace_id = self._get_trace_id()
        
        # Extract request_id and user_id from record.extra (if available from middleware)
        request_id = getattr(record, 'request_id', None) or (getattr(record, 'extra', {}).get('request_id') if hasattr(record, 'extra') else None)
        user_id = getattr(record, 'user_id', None) or (getattr(record, 'extra', {}).get('user_id') if hasattr(record, 'extra') else None)
        
        # Try to get from contextvars if available (for async context)
        if not request_id or not user_id:
            try:
                import contextvars
                request_id_var = contextvars.ContextVar('request_id', default=None)
                user_id_var = contextvars.ContextVar('user_id', default=None)
                request_id = request_id or request_id_var.get()
                user_id = user_id or user_id_var.get()
            except Exception:
                pass  # contextvars not available or not set
        
        # Add to record (for formatter string substitution)
        # CRITICAL: Check if exc_info is already set or being processed before modifying record
        # exc_info is a protected attribute that cannot be overwritten once set
        has_exc_info = (
            hasattr(record, 'exc_info') and record.exc_info is not None
        ) or (
            hasattr(record, 'exc_text') and record.exc_text is not None
        )
        
        # Only modify record if exc_info is not present
        if not has_exc_info:
            try:
                if not hasattr(record, 'trace_id'):
                    setattr(record, 'trace_id', trace_id if trace_id else "no-trace")
                if not hasattr(record, 'request_id'):
                    setattr(record, 'request_id', request_id if request_id else "no-request")
                if not hasattr(record, 'user_id'):
                    setattr(record, 'user_id', user_id if user_id else "no-user")
            except (AttributeError, TypeError, ValueError):
                # If we can't set attributes (e.g., exc_info is protected), skip and continue
                # This can happen if the record is being processed by multiple formatters
                pass
        else:
            # If exc_info is present, use a safer approach: store values in a way that won't conflict
            # We'll format the message manually to include trace context
            try:
                # Store in a non-conflicting way (use a prefix in the message or format manually)
                # For now, we'll just skip setting attributes and format manually if needed
                pass
            except Exception:
                pass
        
        # Format using parent formatter
        # If exc_info is present, we need to be extra careful
        has_exc_info = (
            hasattr(record, 'exc_info') and record.exc_info is not None
        ) or (
            hasattr(record, 'exc_text') and record.exc_text is not None
        )
        
        if has_exc_info:
            # When exc_info is present, format manually to avoid conflicts
            try:
                from datetime import datetime
                asctime = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
                trace_str = f"[trace_id={trace_id if trace_id else 'no-trace'} request_id={request_id if request_id else 'no-request'} user_id={user_id if user_id else 'no-user'}]"
                message = record.getMessage()
                
                # Format exception info if present
                if hasattr(record, 'exc_info') and record.exc_info:
                    import traceback
                    exc_text = ''.join(traceback.format_exception(*record.exc_info))
                    return f"{asctime} - {record.name} - {record.levelname} - {trace_str} - {message}\n{exc_text}"
                else:
                    return f"{asctime} - {record.name} - {record.levelname} - {trace_str} - {message}"
            except Exception:
                # Last resort: return minimal message
                return f"{record.name} - {record.levelname} - {record.getMessage()}"
        else:
            # Normal formatting when no exc_info
            try:
                return super().format(record)
            except (AttributeError, ValueError) as e:
                # If formatting fails (e.g., due to exc_info conflict), return a simple formatted message
                try:
                    from datetime import datetime
                    asctime = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
                    trace_str = f"[trace_id={trace_id if trace_id else 'no-trace'} request_id={request_id if request_id else 'no-request'} user_id={user_id if user_id else 'no-user'}]"
                    return f"{asctime} - {record.name} - {record.levelname} - {trace_str} - {record.getMessage()}"
                except Exception:
                    # Last resort: return minimal message
                    return f"{record.name} - {record.levelname} - {record.getMessage()}"
    
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

