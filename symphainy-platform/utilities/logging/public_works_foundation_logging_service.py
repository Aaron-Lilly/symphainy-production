#!/usr/bin/env python3
"""
Public Works Foundation Logging Service

Realm-specific logging service for Public Works Foundation services.
Handles logging for infrastructure abstractions, adapters, and composition services.

WHAT (Utility Role): I provide logging for Public Works Foundation realm
HOW (Utility Implementation): I handle infrastructure abstraction logging with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class PublicWorksFoundationLoggingService(RealmLoggingServiceBase):
    """
    Logging service for Public Works Foundation realm.
    
    Handles logging for:
    - Infrastructure adapters (ArangoDB, Supabase, GCS, etc.)
    - Abstraction contracts and protocols
    - Infrastructure abstractions
    - Composition services
    - Infrastructure registry
    - Public Works Foundation Service
    """
    
    def __init__(self, service_name: str = "public_works_foundation"):
        """Initialize Public Works Foundation logging service."""
        super().__init__("public_works_foundation", service_name)
        
        # Public Works-specific logging patterns
        self._initialize_public_works_patterns()
        
        self.logger.info(f"✅ Public Works Foundation logging service initialized for {service_name}")
    
    def _initialize_public_works_patterns(self):
        """Initialize Public Works-specific logging patterns."""
        # Override log categories with Public Works-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "adapter": LogCategory.SYSTEM,
            "abstraction": LogCategory.SYSTEM,
            "composition": LogCategory.SYSTEM,
            "registry": LogCategory.SYSTEM,
            "infrastructure": LogCategory.SYSTEM,
            "database": LogCategory.SYSTEM,
            "storage": LogCategory.SYSTEM,
            "protocol": LogCategory.SYSTEM
        })
        
        # Add Public Works-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "adapter_type", "adapter_operation", "adapter_endpoint",
            "abstraction_type", "abstraction_operation", "underlying_adapter",
            "composition_type", "composition_operation", "involved_services",
            "registry_operation", "service_name", "registry_type",
            "database_name", "collection_name", "query_type",
            "storage_bucket", "object_name", "operation_type",
            "protocol_type", "protocol_operation", "interface_name"
        ])
    
    def log_adapter_operation(self, message: str, context: LogContext, adapter_type: str = None, 
                             adapter_operation: str = None, adapter_endpoint: str = None, 
                             data: Dict[str, Any] = None):
        """Log adapter operation-related message."""
        log_data = data or {}
        if adapter_type:
            log_data["adapter_type"] = adapter_type
        if adapter_operation:
            log_data["adapter_operation"] = adapter_operation
        if adapter_endpoint:
            log_data["adapter_endpoint"] = adapter_endpoint
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_abstraction_operation(self, message: str, context: LogContext, abstraction_type: str = None, 
                                 abstraction_operation: str = None, underlying_adapter: str = None, 
                                 data: Dict[str, Any] = None):
        """Log abstraction operation-related message."""
        log_data = data or {}
        if abstraction_type:
            log_data["abstraction_type"] = abstraction_type
        if abstraction_operation:
            log_data["abstraction_operation"] = abstraction_operation
        if underlying_adapter:
            log_data["underlying_adapter"] = underlying_adapter
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_composition_operation(self, message: str, context: LogContext, composition_type: str = None, 
                                 composition_operation: str = None, involved_services: list = None, 
                                 data: Dict[str, Any] = None):
        """Log composition operation-related message."""
        log_data = data or {}
        if composition_type:
            log_data["composition_type"] = composition_type
        if composition_operation:
            log_data["composition_operation"] = composition_operation
        if involved_services:
            log_data["involved_services"] = involved_services
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_registry_operation(self, message: str, context: LogContext, registry_operation: str = None, 
                              service_name: str = None, registry_type: str = None, 
                              data: Dict[str, Any] = None):
        """Log registry operation-related message."""
        log_data = data or {}
        if registry_operation:
            log_data["registry_operation"] = registry_operation
        if service_name:
            log_data["service_name"] = service_name
        if registry_type:
            log_data["registry_type"] = registry_type
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_database_operation(self, message: str, context: LogContext, database_name: str = None, 
                              collection_name: str = None, query_type: str = None, 
                              data: Dict[str, Any] = None):
        """Log database operation-related message."""
        log_data = data or {}
        if database_name:
            log_data["database_name"] = database_name
        if collection_name:
            log_data["collection_name"] = collection_name
        if query_type:
            log_data["query_type"] = query_type
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_storage_operation(self, message: str, context: LogContext, storage_bucket: str = None, 
                             object_name: str = None, operation_type: str = None, 
                             data: Dict[str, Any] = None):
        """Log storage operation-related message."""
        log_data = data or {}
        if storage_bucket:
            log_data["storage_bucket"] = storage_bucket
        if object_name:
            log_data["object_name"] = object_name
        if operation_type:
            log_data["operation_type"] = operation_type
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_protocol_operation(self, message: str, context: LogContext, protocol_type: str = None, 
                              protocol_operation: str = None, interface_name: str = None, 
                              data: Dict[str, Any] = None):
        """Log protocol operation-related message."""
        log_data = data or {}
        if protocol_type:
            log_data["protocol_type"] = protocol_type
        if protocol_operation:
            log_data["protocol_operation"] = protocol_operation
        if interface_name:
            log_data["interface_name"] = interface_name
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_infrastructure_startup(self, context: LogContext, infrastructure_type: str, 
                                  startup_data: Dict[str, Any] = None):
        """Log infrastructure startup."""
        message = f"Infrastructure {infrastructure_type} starting up"
        log_data = startup_data or {}
        log_data["infrastructure_type"] = infrastructure_type
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_infrastructure_shutdown(self, context: LogContext, infrastructure_type: str, 
                                   shutdown_data: Dict[str, Any] = None):
        """Log infrastructure shutdown."""
        message = f"Infrastructure {infrastructure_type} shutting down"
        log_data = shutdown_data or {}
        log_data["infrastructure_type"] = infrastructure_type
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_infrastructure_error(self, context: LogContext, infrastructure_type: str, error: Exception, 
                                error_data: Dict[str, Any] = None):
        """Log infrastructure error."""
        message = f"Infrastructure {infrastructure_type} error: {str(error)}"
        log_data = error_data or {}
        log_data["infrastructure_type"] = infrastructure_type
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "infrastructure_type": infrastructure_type
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def log_performance_metric(self, context: LogContext, metric_name: str, metric_value: Any, 
                              metric_unit: str = None, data: Dict[str, Any] = None):
        """Log performance metric."""
        message = f"Performance metric: {metric_name} = {metric_value}"
        log_data = data or {}
        log_data["metric_name"] = metric_name
        log_data["metric_value"] = metric_value
        if metric_unit:
            log_data["metric_unit"] = metric_unit
        log_data["metric_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, log_data)
    
    def get_public_works_logging_summary(self) -> Dict[str, Any]:
        """Get Public Works-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add Public Works-specific metrics
        public_works_metrics = {
            "adapter_operation_logs": self._count_logs_by_field("adapter_type"),
            "abstraction_operation_logs": self._count_logs_by_field("abstraction_type"),
            "composition_operation_logs": self._count_logs_by_field("composition_type"),
            "registry_operation_logs": self._count_logs_by_field("registry_operation"),
            "database_operation_logs": self._count_logs_by_field("database_name"),
            "storage_operation_logs": self._count_logs_by_field("storage_bucket"),
            "protocol_operation_logs": self._count_logs_by_field("protocol_type"),
            "performance_metric_logs": self._count_logs_by_field("metric_name")
        }
        
        base_summary["public_works_metrics"] = public_works_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


