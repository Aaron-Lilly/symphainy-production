#!/usr/bin/env python3
"""
Smart City Logging Service

Enhanced realm-specific logging service for Smart City services.
Handles logging for core Smart City services with city-specific context and patterns.

WHAT (Utility Role): I provide logging for Smart City realm
HOW (Utility Implementation): I handle core service logging with city-specific context and patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class SmartCityLoggingService(RealmLoggingServiceBase):
    """
    Enhanced logging service for Smart City realm.
    
    Handles logging for:
    - Data Steward Service
    - Content Steward Service
    - Librarian Service
    - Conductor Service
    - Nurse Service
    - Traffic Cop Service
    - Security Guard Service
    - MCP Servers
    """
    
    def __init__(self, service_name: str = "smart_city"):
        """Initialize Smart City logging service."""
        super().__init__("smart_city", service_name)
        
        # Smart City-specific logging patterns
        self._initialize_smart_city_patterns()
        
        self.logger.info(f"✅ Smart City logging service initialized for {service_name}")
    
    def _initialize_smart_city_patterns(self):
        """Initialize Smart City-specific logging patterns."""
        # Override log categories with Smart City-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "data_steward": LogCategory.BUSINESS,
            "content_steward": LogCategory.BUSINESS,
            "librarian": LogCategory.BUSINESS,
            "conductor": LogCategory.SYSTEM,
            "nurse": LogCategory.PERFORMANCE,
            "traffic_cop": LogCategory.SYSTEM,
            "security_guard": LogCategory.SECURITY,
            "mcp_server": LogCategory.SYSTEM,
            "service_discovery": LogCategory.SYSTEM,
            "service_communication": LogCategory.SYSTEM
        })
        
        # Add Smart City-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "data_operation", "data_source", "data_type", "data_id",
            "content_operation", "content_type", "content_id", "file_id",
            "knowledge_operation", "knowledge_type", "query_type", "search_query",
            "orchestration_operation", "workflow_type", "involved_services",
            "health_operation", "monitoring_type", "service_name", "health_status",
            "traffic_operation", "traffic_rule", "request_type", "traffic_status",
            "security_operation", "security_policy", "user_context", "security_status",
            "tool_name", "tool_operation", "tool_context", "mcp_server_name",
            "discovery_operation", "service_name", "registry_type", "discovery_status",
            "communication_type", "source_service", "target_service", "communication_status"
        ])
    
    def log_data_steward_operation(self, message: str, context: LogContext, data_operation: str = None, 
                                  data_source: str = None, data_type: str = None, data_id: str = None, 
                                  data: Dict[str, Any] = None):
        """Log Data Steward operation-related message."""
        log_data = data or {}
        if data_operation:
            log_data["data_operation"] = data_operation
        if data_source:
            log_data["data_source"] = data_source
        if data_type:
            log_data["data_type"] = data_type
        if data_id:
            log_data["data_id"] = data_id
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_content_steward_operation(self, message: str, context: LogContext, content_operation: str = None, 
                                     content_type: str = None, content_id: str = None, file_id: str = None, 
                                     data: Dict[str, Any] = None):
        """Log Content Steward operation-related message."""
        log_data = data or {}
        if content_operation:
            log_data["content_operation"] = content_operation
        if content_type:
            log_data["content_type"] = content_type
        if content_id:
            log_data["content_id"] = content_id
        if file_id:
            log_data["file_id"] = file_id
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_librarian_operation(self, message: str, context: LogContext, knowledge_operation: str = None, 
                               knowledge_type: str = None, query_type: str = None, search_query: str = None, 
                               data: Dict[str, Any] = None):
        """Log Librarian operation-related message."""
        log_data = data or {}
        if knowledge_operation:
            log_data["knowledge_operation"] = knowledge_operation
        if knowledge_type:
            log_data["knowledge_type"] = knowledge_type
        if query_type:
            log_data["query_type"] = query_type
        if search_query:
            log_data["search_query"] = search_query
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_conductor_operation(self, message: str, context: LogContext, orchestration_operation: str = None, 
                               workflow_type: str = None, involved_services: list = None, 
                               data: Dict[str, Any] = None):
        """Log Conductor operation-related message."""
        log_data = data or {}
        if orchestration_operation:
            log_data["orchestration_operation"] = orchestration_operation
        if workflow_type:
            log_data["workflow_type"] = workflow_type
        if involved_services:
            log_data["involved_services"] = involved_services
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_nurse_operation(self, message: str, context: LogContext, health_operation: str = None, 
                           monitoring_type: str = None, service_name: str = None, health_status: str = None, 
                           data: Dict[str, Any] = None):
        """Log Nurse operation-related message."""
        log_data = data or {}
        if health_operation:
            log_data["health_operation"] = health_operation
        if monitoring_type:
            log_data["monitoring_type"] = monitoring_type
        if service_name:
            log_data["service_name"] = service_name
        if health_status:
            log_data["health_status"] = health_status
        
        return self.log(LogLevel.INFO, LogCategory.PERFORMANCE, message, context, log_data)
    
    def log_traffic_cop_operation(self, message: str, context: LogContext, traffic_operation: str = None, 
                                 traffic_rule: str = None, request_type: str = None, traffic_status: str = None, 
                                 data: Dict[str, Any] = None):
        """Log Traffic Cop operation-related message."""
        log_data = data or {}
        if traffic_operation:
            log_data["traffic_operation"] = traffic_operation
        if traffic_rule:
            log_data["traffic_rule"] = traffic_rule
        if request_type:
            log_data["request_type"] = request_type
        if traffic_status:
            log_data["traffic_status"] = traffic_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_security_guard_operation(self, message: str, context: LogContext, security_operation: str = None, 
                                    security_policy: str = None, user_context: str = None, security_status: str = None, 
                                    data: Dict[str, Any] = None):
        """Log Security Guard operation-related message."""
        log_data = data or {}
        if security_operation:
            log_data["security_operation"] = security_operation
        if security_policy:
            log_data["security_policy"] = security_policy
        if user_context:
            log_data["user_context"] = user_context
        if security_status:
            log_data["security_status"] = security_status
        
        return self.log(LogLevel.INFO, LogCategory.SECURITY, message, context, log_data)
    
    def log_mcp_server_operation(self, message: str, context: LogContext, tool_name: str = None, 
                                tool_operation: str = None, tool_context: str = None, mcp_server_name: str = None, 
                                data: Dict[str, Any] = None):
        """Log MCP Server operation-related message."""
        log_data = data or {}
        if tool_name:
            log_data["tool_name"] = tool_name
        if tool_operation:
            log_data["tool_operation"] = tool_operation
        if tool_context:
            log_data["tool_context"] = tool_context
        if mcp_server_name:
            log_data["mcp_server_name"] = mcp_server_name
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_service_discovery_operation(self, message: str, context: LogContext, discovery_operation: str = None, 
                                       service_name: str = None, registry_type: str = None, discovery_status: str = None, 
                                       data: Dict[str, Any] = None):
        """Log service discovery operation-related message."""
        log_data = data or {}
        if discovery_operation:
            log_data["discovery_operation"] = discovery_operation
        if service_name:
            log_data["service_name"] = service_name
        if registry_type:
            log_data["registry_type"] = registry_type
        if discovery_status:
            log_data["discovery_status"] = discovery_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_service_communication_operation(self, message: str, context: LogContext, communication_type: str = None, 
                                           source_service: str = None, target_service: str = None, 
                                           communication_status: str = None, data: Dict[str, Any] = None):
        """Log service communication operation-related message."""
        log_data = data or {}
        if communication_type:
            log_data["communication_type"] = communication_type
        if source_service:
            log_data["source_service"] = source_service
        if target_service:
            log_data["target_service"] = target_service
        if communication_status:
            log_data["communication_status"] = communication_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_smart_city_startup(self, context: LogContext, service_name: str, startup_data: Dict[str, Any] = None):
        """Log Smart City service startup."""
        message = f"Smart City service {service_name} starting up"
        log_data = startup_data or {}
        log_data["service_name"] = service_name
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_smart_city_shutdown(self, context: LogContext, service_name: str, shutdown_data: Dict[str, Any] = None):
        """Log Smart City service shutdown."""
        message = f"Smart City service {service_name} shutting down"
        log_data = shutdown_data or {}
        log_data["service_name"] = service_name
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_smart_city_error(self, context: LogContext, service_name: str, error: Exception, 
                            error_data: Dict[str, Any] = None):
        """Log Smart City service error."""
        message = f"Smart City service {service_name} error: {str(error)}"
        log_data = error_data or {}
        log_data["service_name"] = service_name
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "service_name": service_name
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def get_smart_city_logging_summary(self) -> Dict[str, Any]:
        """Get Smart City-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add Smart City-specific metrics
        smart_city_metrics = {
            "data_steward_operation_logs": self._count_logs_by_field("data_operation"),
            "content_steward_operation_logs": self._count_logs_by_field("content_operation"),
            "librarian_operation_logs": self._count_logs_by_field("knowledge_operation"),
            "conductor_operation_logs": self._count_logs_by_field("orchestration_operation"),
            "nurse_operation_logs": self._count_logs_by_field("health_operation"),
            "traffic_cop_operation_logs": self._count_logs_by_field("traffic_operation"),
            "security_guard_operation_logs": self._count_logs_by_field("security_operation"),
            "mcp_server_operation_logs": self._count_logs_by_field("tool_name"),
            "service_discovery_operation_logs": self._count_logs_by_field("discovery_operation"),
            "service_communication_operation_logs": self._count_logs_by_field("communication_type")
        }
        
        base_summary["smart_city_metrics"] = smart_city_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


