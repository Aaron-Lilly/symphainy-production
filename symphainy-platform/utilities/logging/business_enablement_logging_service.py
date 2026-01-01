#!/usr/bin/env python3
"""
Business Enablement Logging Service

Realm-specific logging service for Business Enablement services.
Handles logging for pillars and business logic services.

WHAT (Utility Role): I provide logging for Business Enablement realm
HOW (Utility Implementation): I handle business logic logging with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class BusinessEnablementLoggingService(RealmLoggingServiceBase):
    """
    Logging service for Business Enablement realm.
    
    Handles logging for:
    - Content Pillar Service
    - Operations Pillar Service
    - Insights Pillar Service
    - Delivery Manager Service
    - Experience Manager Service
    - Business Logic Services
    """
    
    def __init__(self, service_name: str = "business_enablement"):
        """Initialize Business Enablement logging service."""
        super().__init__("business_enablement", service_name)
        
        # Business Enablement-specific logging patterns
        self._initialize_business_enablement_patterns()
        
        self.logger.info(f"✅ Business Enablement logging service initialized for {service_name}")
    
    def _initialize_business_enablement_patterns(self):
        """Initialize Business Enablement-specific logging patterns."""
        # Override log categories with Business Enablement-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "content_pillar": LogCategory.BUSINESS,
            "operations_pillar": LogCategory.BUSINESS,
            "insights_pillar": LogCategory.BUSINESS,
            "delivery_manager": LogCategory.SYSTEM,
            "experience_manager": LogCategory.SYSTEM,
            "business_logic": LogCategory.BUSINESS,
            "pillar_coordination": LogCategory.SYSTEM,
            "api_gateway": LogCategory.SYSTEM,
            "frontend_integration": LogCategory.SYSTEM
        })
        
        # Add Business Enablement-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "content_operation", "file_id", "content_type", "content_id",
            "operations_operation", "workflow_id", "operation_type", "workflow_status",
            "insights_operation", "analysis_type", "data_source", "insights_id",
            "delivery_operation", "delivery_type", "target_realm", "delivery_status",
            "experience_operation", "ui_component", "user_action", "experience_status",
            "business_rule", "business_context", "validation_type", "business_status",
            "coordination_operation", "involved_pillars", "coordination_type", "coordination_status",
            "gateway_operation", "api_endpoint", "http_method", "gateway_status",
            "integration_operation", "frontend_component", "api_call", "integration_status"
        ])
    
    def log_content_pillar_operation(self, message: str, context: LogContext, content_operation: str = None, 
                                    file_id: str = None, content_type: str = None, content_id: str = None, 
                                    data: Dict[str, Any] = None):
        """Log Content Pillar operation-related message."""
        log_data = data or {}
        if content_operation:
            log_data["content_operation"] = content_operation
        if file_id:
            log_data["file_id"] = file_id
        if content_type:
            log_data["content_type"] = content_type
        if content_id:
            log_data["content_id"] = content_id
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_operations_pillar_operation(self, message: str, context: LogContext, operations_operation: str = None, 
                                       workflow_id: str = None, operation_type: str = None, workflow_status: str = None, 
                                       data: Dict[str, Any] = None):
        """Log Operations Pillar operation-related message."""
        log_data = data or {}
        if operations_operation:
            log_data["operations_operation"] = operations_operation
        if workflow_id:
            log_data["workflow_id"] = workflow_id
        if operation_type:
            log_data["operation_type"] = operation_type
        if workflow_status:
            log_data["workflow_status"] = workflow_status
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_insights_pillar_operation(self, message: str, context: LogContext, insights_operation: str = None, 
                                     analysis_type: str = None, data_source: str = None, insights_id: str = None, 
                                     data: Dict[str, Any] = None):
        """Log Insights Pillar operation-related message."""
        log_data = data or {}
        if insights_operation:
            log_data["insights_operation"] = insights_operation
        if analysis_type:
            log_data["analysis_type"] = analysis_type
        if data_source:
            log_data["data_source"] = data_source
        if insights_id:
            log_data["insights_id"] = insights_id
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_delivery_manager_operation(self, message: str, context: LogContext, delivery_operation: str = None, 
                                      delivery_type: str = None, target_realm: str = None, delivery_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log Delivery Manager operation-related message."""
        log_data = data or {}
        if delivery_operation:
            log_data["delivery_operation"] = delivery_operation
        if delivery_type:
            log_data["delivery_type"] = delivery_type
        if target_realm:
            log_data["target_realm"] = target_realm
        if delivery_status:
            log_data["delivery_status"] = delivery_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_experience_manager_operation(self, message: str, context: LogContext, experience_operation: str = None, 
                                        ui_component: str = None, user_action: str = None, experience_status: str = None, 
                                        data: Dict[str, Any] = None):
        """Log Experience Manager operation-related message."""
        log_data = data or {}
        if experience_operation:
            log_data["experience_operation"] = experience_operation
        if ui_component:
            log_data["ui_component"] = ui_component
        if user_action:
            log_data["user_action"] = user_action
        if experience_status:
            log_data["experience_status"] = experience_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_business_logic_operation(self, message: str, context: LogContext, business_rule: str = None, 
                                    business_context: str = None, validation_type: str = None, business_status: str = None, 
                                    data: Dict[str, Any] = None):
        """Log business logic operation-related message."""
        log_data = data or {}
        if business_rule:
            log_data["business_rule"] = business_rule
        if business_context:
            log_data["business_context"] = business_context
        if validation_type:
            log_data["validation_type"] = validation_type
        if business_status:
            log_data["business_status"] = business_status
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_pillar_coordination_operation(self, message: str, context: LogContext, coordination_operation: str = None, 
                                         involved_pillars: list = None, coordination_type: str = None, 
                                         coordination_status: str = None, data: Dict[str, Any] = None):
        """Log pillar coordination operation-related message."""
        log_data = data or {}
        if coordination_operation:
            log_data["coordination_operation"] = coordination_operation
        if involved_pillars:
            log_data["involved_pillars"] = involved_pillars
        if coordination_type:
            log_data["coordination_type"] = coordination_type
        if coordination_status:
            log_data["coordination_status"] = coordination_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_api_gateway_operation(self, message: str, context: LogContext, gateway_operation: str = None, 
                                 api_endpoint: str = None, http_method: str = None, gateway_status: str = None, 
                                 data: Dict[str, Any] = None):
        """Log API Gateway operation-related message."""
        log_data = data or {}
        if gateway_operation:
            log_data["gateway_operation"] = gateway_operation
        if api_endpoint:
            log_data["api_endpoint"] = api_endpoint
        if http_method:
            log_data["http_method"] = http_method
        if gateway_status:
            log_data["gateway_status"] = gateway_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_frontend_integration_operation(self, message: str, context: LogContext, integration_operation: str = None, 
                                          frontend_component: str = None, api_call: str = None, integration_status: str = None, 
                                          data: Dict[str, Any] = None):
        """Log frontend integration operation-related message."""
        log_data = data or {}
        if integration_operation:
            log_data["integration_operation"] = integration_operation
        if frontend_component:
            log_data["frontend_component"] = frontend_component
        if api_call:
            log_data["api_call"] = api_call
        if integration_status:
            log_data["integration_status"] = integration_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_business_enablement_startup(self, context: LogContext, service_name: str, startup_data: Dict[str, Any] = None):
        """Log Business Enablement service startup."""
        message = f"Business Enablement service {service_name} starting up"
        log_data = startup_data or {}
        log_data["service_name"] = service_name
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_business_enablement_shutdown(self, context: LogContext, service_name: str, shutdown_data: Dict[str, Any] = None):
        """Log Business Enablement service shutdown."""
        message = f"Business Enablement service {service_name} shutting down"
        log_data = shutdown_data or {}
        log_data["service_name"] = service_name
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_business_enablement_error(self, context: LogContext, service_name: str, error: Exception, 
                                     error_data: Dict[str, Any] = None):
        """Log Business Enablement service error."""
        message = f"Business Enablement service {service_name} error: {str(error)}"
        log_data = error_data or {}
        log_data["service_name"] = service_name
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "service_name": service_name
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def get_business_enablement_logging_summary(self) -> Dict[str, Any]:
        """Get Business Enablement-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add Business Enablement-specific metrics
        business_enablement_metrics = {
            "content_pillar_operation_logs": self._count_logs_by_field("content_operation"),
            "operations_pillar_operation_logs": self._count_logs_by_field("operations_operation"),
            "insights_pillar_operation_logs": self._count_logs_by_field("insights_operation"),
            "delivery_manager_operation_logs": self._count_logs_by_field("delivery_operation"),
            "experience_manager_operation_logs": self._count_logs_by_field("experience_operation"),
            "business_logic_operation_logs": self._count_logs_by_field("business_rule"),
            "pillar_coordination_operation_logs": self._count_logs_by_field("coordination_operation"),
            "api_gateway_operation_logs": self._count_logs_by_field("gateway_operation"),
            "frontend_integration_operation_logs": self._count_logs_by_field("integration_operation")
        }
        
        base_summary["business_enablement_metrics"] = business_enablement_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


