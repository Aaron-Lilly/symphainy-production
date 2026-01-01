#!/usr/bin/env python3
"""
Realm-Specific Logging Service Base

Base class for realm-specific logging services with real working implementations.
Provides common functionality and patterns for all realm logging services.

WHAT (Utility Role): I provide the foundation for realm-specific logging
HOW (Utility Implementation): I implement common logging patterns with realm-specific customization
"""

import logging
import json
import traceback
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
from pathlib import Path


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Log category enumeration."""
    SYSTEM = "system"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"
    ERROR = "error"
    DEBUG = "debug"


@dataclass
class LogContext:
    """Enhanced log context with realm-specific information."""
    realm: str
    service_type: str
    service_name: str
    operation: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}
        if not self.correlation_id:
            self.correlation_id = str(uuid.uuid4())


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: LogLevel
    category: LogCategory
    message: str
    context: LogContext
    data: Dict[str, Any] = None
    error_details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.error_details is None:
            self.error_details = {}


class RealmLoggingServiceBase:
    """
    Base class for realm-specific logging services.
    
    Provides common logging functionality with realm-specific customization.
    All realm logging services inherit from this base class.
    """
    
    def __init__(self, realm_name: str, service_name: str = None):
        """Initialize realm logging service."""
        self.realm_name = realm_name
        self.service_name = service_name or f"{realm_name}_service"
        
        # Create logger
        self.logger = logging.getLogger(f"RealmLogging-{realm_name}-{self.service_name}")
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        # Log storage
        self.log_entries: List[LogEntry] = []
        self.max_log_entries = 10000
        
        # Realm-specific logging patterns
        self.realm_logging_patterns = self._initialize_realm_patterns()
        
        self.logger.info(f"✅ Realm logging service initialized for {realm_name}: {self.service_name}")
    
    def _setup_handlers(self):
        """Setup logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"{self.realm_name}_{self.service_name}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _initialize_realm_patterns(self) -> Dict[str, Any]:
        """Initialize realm-specific logging patterns."""
        return {
            "log_categories": self._get_log_categories(),
            "log_levels": self._get_log_levels(),
            "structured_fields": self._get_structured_fields(),
            "performance_metrics": self._get_performance_metrics()
        }
    
    def _get_log_categories(self) -> Dict[str, LogCategory]:
        """Get log categories for this realm."""
        return {
            "system": LogCategory.SYSTEM,
            "business": LogCategory.BUSINESS,
            "security": LogCategory.SECURITY,
            "performance": LogCategory.PERFORMANCE,
            "audit": LogCategory.AUDIT,
            "error": LogCategory.ERROR,
            "debug": LogCategory.DEBUG
        }
    
    def _get_log_levels(self) -> Dict[str, LogLevel]:
        """Get log levels for this realm."""
        return {
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL
        }
    
    def _get_structured_fields(self) -> List[str]:
        """Get structured fields for this realm."""
        return [
            "realm", "service_type", "service_name", "operation",
            "user_id", "tenant_id", "request_id", "correlation_id",
            "session_id", "timestamp", "level", "category"
        ]
    
    def _get_performance_metrics(self) -> List[str]:
        """Get performance metrics for this realm."""
        return [
            "response_time", "memory_usage", "cpu_usage", "request_count",
            "error_count", "success_rate", "throughput"
        ]
    
    def log(self, level: LogLevel, category: LogCategory, message: str, 
            context: LogContext, data: Dict[str, Any] = None, 
            error_details: Dict[str, Any] = None) -> LogEntry:
        """Log a message with realm-specific processing."""
        try:
            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.utcnow().isoformat(),
                level=level,
                category=category,
                message=message,
                context=context,
                data=data or {},
                error_details=error_details or {}
            )
            
            # Store log entry
            self._store_log_entry(log_entry)
            
            # Log with appropriate level
            self._log_with_level(log_entry)
            
            return log_entry
            
        except Exception as e:
            # Fallback logging
            self.logger.error(f"❌ Logging failed: {e}")
            return self._create_fallback_log_entry(level, message, context)
    
    def _store_log_entry(self, log_entry: LogEntry):
        """Store log entry in memory."""
        self.log_entries.append(log_entry)
        
        # Maintain log entry limit
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]
    
    def _log_with_level(self, log_entry: LogEntry):
        """Log with appropriate level and structured data."""
        # Create structured log data
        log_data = {
            "realm": log_entry.context.realm,
            "service_type": log_entry.context.service_type,
            "service_name": log_entry.context.service_name,
            "operation": log_entry.context.operation,
            "user_id": log_entry.context.user_id,
            "tenant_id": log_entry.context.tenant_id,
            "request_id": log_entry.context.request_id,
            "correlation_id": log_entry.context.correlation_id,
            "session_id": log_entry.context.session_id,
            "category": log_entry.category.value,
            "data": log_entry.data,
            "error_details": log_entry.error_details
        }
        
        # Log with appropriate level
        if log_entry.level == LogLevel.DEBUG:
            self.logger.debug(f"🔍 {log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.INFO:
            self.logger.info(f"ℹ️ {log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.WARNING:
            self.logger.warning(f"⚠️ {log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.ERROR:
            self.logger.error(f"❌ {log_entry.message}", extra=log_data)
        elif log_entry.level == LogLevel.CRITICAL:
            self.logger.critical(f"🚨 {log_entry.message}", extra=log_data)
    
    def _create_fallback_log_entry(self, level: LogLevel, message: str, context: LogContext) -> LogEntry:
        """Create fallback log entry when logging fails."""
        return LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            category=LogCategory.ERROR,
            message=f"Logging failed: {message}",
            context=context,
            data={"fallback": True},
            error_details={"fallback_reason": "Logging system failed"}
        )
    
    # CONVENIENCE METHODS
    
    def log_debug(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log debug message."""
        return self.log(LogLevel.DEBUG, LogCategory.DEBUG, message, context, data)
    
    def log_info(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log info message."""
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, data)
    
    def log_warning(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log warning message."""
        return self.log(LogLevel.WARNING, LogCategory.SYSTEM, message, context, data)
    
    def log_error(self, message: str, context: LogContext, data: Dict[str, Any] = None, 
                  error_details: Dict[str, Any] = None):
        """Log error message."""
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, data, error_details)
    
    def log_critical(self, message: str, context: LogContext, data: Dict[str, Any] = None, 
                     error_details: Dict[str, Any] = None):
        """Log critical message."""
        return self.log(LogLevel.CRITICAL, LogCategory.ERROR, message, context, data, error_details)
    
    def log_business(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log business message."""
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, data)
    
    def log_security(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log security message."""
        return self.log(LogLevel.INFO, LogCategory.SECURITY, message, context, data)
    
    def log_performance(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log performance message."""
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, data)
    
    def log_audit(self, message: str, context: LogContext, data: Dict[str, Any] = None):
        """Log audit message."""
        return self.log(LogLevel.INFO, LogCategory.AUDIT, message, context, data)
    
    # STATISTICS AND MONITORING
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics for this realm."""
        if not self.log_entries:
            return {
                "realm": self.realm_name,
                "service_name": self.service_name,
                "total_logs": 0,
                "logs_by_level": {},
                "logs_by_category": {},
                "recent_logs": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Calculate statistics
        logs_by_level = {}
        logs_by_category = {}
        
        for log_entry in self.log_entries:
            level = log_entry.level.value
            category = log_entry.category.value
            
            logs_by_level[level] = logs_by_level.get(level, 0) + 1
            logs_by_category[category] = logs_by_category.get(category, 0) + 1
        
        return {
            "realm": self.realm_name,
            "service_name": self.service_name,
            "total_logs": len(self.log_entries),
            "logs_by_level": logs_by_level,
            "logs_by_category": logs_by_category,
            "recent_logs": [asdict(log_entry) for log_entry in self.log_entries[-10:]],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def clear_log_entries(self):
        """Clear log entries (useful for testing)."""
        self.log_entries.clear()
        self.logger.info(f"✅ Log entries cleared for {self.realm_name}: {self.service_name}")
    
    def export_logs(self, format: str = "json") -> Union[str, List[Dict[str, Any]]]:
        """Export logs in specified format."""
        if format == "json":
            return json.dumps([asdict(log_entry) for log_entry in self.log_entries], indent=2)
        elif format == "dict":
            return [asdict(log_entry) for log_entry in self.log_entries]
        else:
            raise ValueError(f"Unsupported export format: {format}")


