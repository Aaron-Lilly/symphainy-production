#!/usr/bin/env python3
"""
Utility Foundation Logging Service

Realm-specific logging service for Utility Foundation services.
Handles logging for configuration, logging, DI container, and other utility services.

WHAT (Utility Role): I provide logging for Utility Foundation realm
HOW (Utility Implementation): I handle infrastructure and utility-specific logging with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class UtilityFoundationLoggingService(RealmLoggingServiceBase):
    """
    Logging service for Utility Foundation realm.
    
    Handles logging for:
    - Configuration management
    - Logging services
    - DI container operations
    - Health monitoring
    - Telemetry reporting
    - Security authorization
    - Tenant management
    - Validation services
    - Serialization services
    """
    
    def __init__(self, service_name: str = "utility_foundation"):
        """Initialize Utility Foundation logging service."""
        super().__init__("utility_foundation", service_name)
        
        # Utility-specific logging patterns
        self._initialize_utility_patterns()
        
        self.logger.info(f"✅ Utility Foundation logging service initialized for {service_name}")
    
    def _initialize_utility_patterns(self):
        """Initialize utility-specific logging patterns."""
        # Override log categories with utility-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "configuration": LogCategory.SYSTEM,
            "di_container": LogCategory.SYSTEM,
            "logging": LogCategory.SYSTEM,
            "health": LogCategory.PERFORMANCE,
            "telemetry": LogCategory.PERFORMANCE,
            "security": LogCategory.SECURITY,
            "tenant": LogCategory.BUSINESS,
            "validation": LogCategory.SYSTEM,
            "serialization": LogCategory.SYSTEM
        })
        
        # Add utility-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "config_key", "config_value", "di_service", "di_operation",
            "log_level", "log_handler", "health_status", "health_metric",
            "telemetry_metric", "telemetry_value", "security_operation",
            "tenant_id", "validation_rule", "serialization_format"
        ])
    
    def log_configuration(self, message: str, context: LogContext, config_key: str = None, 
                         config_value: Any = None, data: Dict[str, Any] = None):
        """Log configuration-related message."""
        log_data = data or {}
        if config_key:
            log_data["config_key"] = config_key
        if config_value is not None:
            log_data["config_value"] = str(config_value)
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_di_container(self, message: str, context: LogContext, di_service: str = None, 
                        di_operation: str = None, data: Dict[str, Any] = None):
        """Log DI container-related message."""
        log_data = data or {}
        if di_service:
            log_data["di_service"] = di_service
        if di_operation:
            log_data["di_operation"] = di_operation
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_logging_system(self, message: str, context: LogContext, log_level: str = None, 
                          log_handler: str = None, data: Dict[str, Any] = None):
        """Log logging system-related message."""
        log_data = data or {}
        if log_level:
            log_data["log_level"] = log_level
        if log_handler:
            log_data["log_handler"] = log_handler
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_health_monitoring(self, message: str, context: LogContext, health_status: str = None, 
                             health_metric: str = None, data: Dict[str, Any] = None):
        """Log health monitoring-related message."""
        log_data = data or {}
        if health_status:
            log_data["health_status"] = health_status
        if health_metric:
            log_data["health_metric"] = health_metric
        
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, log_data)
    
    def log_telemetry(self, message: str, context: LogContext, telemetry_metric: str = None, 
                     telemetry_value: Any = None, data: Dict[str, Any] = None):
        """Log telemetry-related message."""
        log_data = data or {}
        if telemetry_metric:
            log_data["telemetry_metric"] = telemetry_metric
        if telemetry_value is not None:
            log_data["telemetry_value"] = telemetry_value
        
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, log_data)
    
    def log_security_operation(self, message: str, context: LogContext, security_operation: str = None, 
                              data: Dict[str, Any] = None):
        """Log security operation-related message."""
        log_data = data or {}
        if security_operation:
            log_data["security_operation"] = security_operation
        
        return self.log(LogLevel.INFO, LogCategory.SECURITY, message, context, log_data)
    
    def log_tenant_operation(self, message: str, context: LogContext, tenant_id: str = None, 
                            data: Dict[str, Any] = None):
        """Log tenant operation-related message."""
        log_data = data or {}
        if tenant_id:
            log_data["tenant_id"] = tenant_id
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_validation(self, message: str, context: LogContext, validation_rule: str = None, 
                      data: Dict[str, Any] = None):
        """Log validation-related message."""
        log_data = data or {}
        if validation_rule:
            log_data["validation_rule"] = validation_rule
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_serialization(self, message: str, context: LogContext, serialization_format: str = None, 
                         data: Dict[str, Any] = None):
        """Log serialization-related message."""
        log_data = data or {}
        if serialization_format:
            log_data["serialization_format"] = serialization_format
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_utility_startup(self, context: LogContext, utility_name: str, startup_data: Dict[str, Any] = None):
        """Log utility startup."""
        message = f"Utility {utility_name} starting up"
        log_data = startup_data or {}
        log_data["utility_name"] = utility_name
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_utility_shutdown(self, context: LogContext, utility_name: str, shutdown_data: Dict[str, Any] = None):
        """Log utility shutdown."""
        message = f"Utility {utility_name} shutting down"
        log_data = shutdown_data or {}
        log_data["utility_name"] = utility_name
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_utility_error(self, context: LogContext, utility_name: str, error: Exception, 
                         error_data: Dict[str, Any] = None):
        """Log utility error."""
        message = f"Utility {utility_name} error: {str(error)}"
        log_data = error_data or {}
        log_data["utility_name"] = utility_name
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "utility_name": utility_name
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def get_utility_logging_summary(self) -> Dict[str, Any]:
        """Get utility-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add utility-specific metrics
        utility_metrics = {
            "configuration_logs": self._count_logs_by_field("config_key"),
            "di_container_logs": self._count_logs_by_field("di_service"),
            "logging_system_logs": self._count_logs_by_field("log_handler"),
            "health_monitoring_logs": self._count_logs_by_field("health_metric"),
            "telemetry_logs": self._count_logs_by_field("telemetry_metric"),
            "security_operation_logs": self._count_logs_by_field("security_operation"),
            "tenant_operation_logs": self._count_logs_by_field("tenant_id"),
            "validation_logs": self._count_logs_by_field("validation_rule"),
            "serialization_logs": self._count_logs_by_field("serialization_format")
        }
        
        base_summary["utility_metrics"] = utility_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


