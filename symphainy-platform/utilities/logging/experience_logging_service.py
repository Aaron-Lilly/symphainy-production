#!/usr/bin/env python3
"""
Experience Logging Service

Realm-specific logging service for Experience services.
Handles logging for frontend integration and user experience services.

WHAT (Utility Role): I provide logging for Experience realm
HOW (Utility Implementation): I handle frontend and user experience logging with appropriate patterns
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_logging_service_base import RealmLoggingServiceBase, LogContext, LogLevel, LogCategory


class ExperienceLoggingService(RealmLoggingServiceBase):
    """
    Logging service for Experience realm.
    
    Handles logging for:
    - Frontend Integration Service
    - UI Component Services
    - User Experience Services
    - API Integration Services
    - Frontend State Management
    """
    
    def __init__(self, service_name: str = "experience"):
        """Initialize Experience logging service."""
        super().__init__("experience", service_name)
        
        # Experience-specific logging patterns
        self._initialize_experience_patterns()
        
        self.logger.info(f"✅ Experience logging service initialized for {service_name}")
    
    def _initialize_experience_patterns(self):
        """Initialize Experience-specific logging patterns."""
        # Override log categories with Experience-specific patterns
        self.realm_logging_patterns["log_categories"].update({
            "frontend_integration": LogCategory.SYSTEM,
            "ui_component": LogCategory.SYSTEM,
            "user_experience": LogCategory.BUSINESS,
            "api_integration": LogCategory.SYSTEM,
            "state_management": LogCategory.SYSTEM,
            "frontend_routing": LogCategory.SYSTEM,
            "user_interaction": LogCategory.BUSINESS,
            "frontend_rendering": LogCategory.SYSTEM,
            "real_time_update": LogCategory.SYSTEM
        })
        
        # Add Experience-specific structured fields
        self.realm_logging_patterns["structured_fields"].extend([
            "integration_type", "api_endpoint", "http_method", "integration_status",
            "component_name", "component_type", "component_props", "component_status",
            "experience_type", "user_action", "experience_context", "experience_status",
            "api_service", "api_operation", "request_data", "api_status",
            "state_key", "state_operation", "state_value", "state_status",
            "route_path", "routing_operation", "route_params", "routing_status",
            "interaction_type", "interaction_element", "user_input", "interaction_status",
            "rendering_type", "rendering_component", "rendering_data", "rendering_status",
            "update_type", "update_source", "update_data", "update_status"
        ])
    
    def log_frontend_integration_operation(self, message: str, context: LogContext, integration_type: str = None, 
                                          api_endpoint: str = None, http_method: str = None, integration_status: str = None, 
                                          data: Dict[str, Any] = None):
        """Log frontend integration operation-related message."""
        log_data = data or {}
        if integration_type:
            log_data["integration_type"] = integration_type
        if api_endpoint:
            log_data["api_endpoint"] = api_endpoint
        if http_method:
            log_data["http_method"] = http_method
        if integration_status:
            log_data["integration_status"] = integration_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_ui_component_operation(self, message: str, context: LogContext, component_name: str = None, 
                                  component_type: str = None, component_props: dict = None, component_status: str = None, 
                                  data: Dict[str, Any] = None):
        """Log UI component operation-related message."""
        log_data = data or {}
        if component_name:
            log_data["component_name"] = component_name
        if component_type:
            log_data["component_type"] = component_type
        if component_props:
            log_data["component_props"] = component_props
        if component_status:
            log_data["component_status"] = component_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_user_experience_operation(self, message: str, context: LogContext, experience_type: str = None, 
                                     user_action: str = None, experience_context: str = None, experience_status: str = None, 
                                     data: Dict[str, Any] = None):
        """Log user experience operation-related message."""
        log_data = data or {}
        if experience_type:
            log_data["experience_type"] = experience_type
        if user_action:
            log_data["user_action"] = user_action
        if experience_context:
            log_data["experience_context"] = experience_context
        if experience_status:
            log_data["experience_status"] = experience_status
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_api_integration_operation(self, message: str, context: LogContext, api_service: str = None, 
                                     api_operation: str = None, request_data: dict = None, api_status: str = None, 
                                     data: Dict[str, Any] = None):
        """Log API integration operation-related message."""
        log_data = data or {}
        if api_service:
            log_data["api_service"] = api_service
        if api_operation:
            log_data["api_operation"] = api_operation
        if request_data:
            log_data["request_data"] = request_data
        if api_status:
            log_data["api_status"] = api_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_state_management_operation(self, message: str, context: LogContext, state_key: str = None, 
                                      state_operation: str = None, state_value: Any = None, state_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log state management operation-related message."""
        log_data = data or {}
        if state_key:
            log_data["state_key"] = state_key
        if state_operation:
            log_data["state_operation"] = state_operation
        if state_value is not None:
            log_data["state_value"] = str(state_value)
        if state_status:
            log_data["state_status"] = state_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_frontend_routing_operation(self, message: str, context: LogContext, route_path: str = None, 
                                      routing_operation: str = None, route_params: dict = None, routing_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log frontend routing operation-related message."""
        log_data = data or {}
        if route_path:
            log_data["route_path"] = route_path
        if routing_operation:
            log_data["routing_operation"] = routing_operation
        if route_params:
            log_data["route_params"] = route_params
        if routing_status:
            log_data["routing_status"] = routing_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_user_interaction_operation(self, message: str, context: LogContext, interaction_type: str = None, 
                                      interaction_element: str = None, user_input: str = None, interaction_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log user interaction operation-related message."""
        log_data = data or {}
        if interaction_type:
            log_data["interaction_type"] = interaction_type
        if interaction_element:
            log_data["interaction_element"] = interaction_element
        if user_input:
            log_data["user_input"] = user_input
        if interaction_status:
            log_data["interaction_status"] = interaction_status
        
        return self.log(LogLevel.INFO, LogCategory.BUSINESS, message, context, log_data)
    
    def log_frontend_rendering_operation(self, message: str, context: LogContext, rendering_type: str = None, 
                                        rendering_component: str = None, rendering_data: dict = None, rendering_status: str = None, 
                                        data: Dict[str, Any] = None):
        """Log frontend rendering operation-related message."""
        log_data = data or {}
        if rendering_type:
            log_data["rendering_type"] = rendering_type
        if rendering_component:
            log_data["rendering_component"] = rendering_component
        if rendering_data:
            log_data["rendering_data"] = rendering_data
        if rendering_status:
            log_data["rendering_status"] = rendering_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_real_time_update_operation(self, message: str, context: LogContext, update_type: str = None, 
                                      update_source: str = None, update_data: dict = None, update_status: str = None, 
                                      data: Dict[str, Any] = None):
        """Log real-time update operation-related message."""
        log_data = data or {}
        if update_type:
            log_data["update_type"] = update_type
        if update_source:
            log_data["update_source"] = update_source
        if update_data:
            log_data["update_data"] = update_data
        if update_status:
            log_data["update_status"] = update_status
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_experience_startup(self, context: LogContext, service_name: str, startup_data: Dict[str, Any] = None):
        """Log Experience service startup."""
        message = f"Experience service {service_name} starting up"
        log_data = startup_data or {}
        log_data["service_name"] = service_name
        log_data["startup_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_experience_shutdown(self, context: LogContext, service_name: str, shutdown_data: Dict[str, Any] = None):
        """Log Experience service shutdown."""
        message = f"Experience service {service_name} shutting down"
        log_data = shutdown_data or {}
        log_data["service_name"] = service_name
        log_data["shutdown_timestamp"] = datetime.utcnow().isoformat()
        
        return self.log(LogLevel.INFO, LogCategory.SYSTEM, message, context, log_data)
    
    def log_experience_error(self, context: LogContext, service_name: str, error: Exception, 
                            error_data: Dict[str, Any] = None):
        """Log Experience service error."""
        message = f"Experience service {service_name} error: {str(error)}"
        log_data = error_data or {}
        log_data["service_name"] = service_name
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)
        
        error_details = {
            "traceback": str(error),
            "service_name": service_name
        }
        
        return self.log(LogLevel.ERROR, LogCategory.ERROR, message, context, log_data, error_details)
    
    def get_experience_logging_summary(self) -> Dict[str, Any]:
        """Get Experience-specific logging summary."""
        base_summary = self.get_log_statistics()
        
        # Add Experience-specific metrics
        experience_metrics = {
            "frontend_integration_operation_logs": self._count_logs_by_field("integration_type"),
            "ui_component_operation_logs": self._count_logs_by_field("component_name"),
            "user_experience_operation_logs": self._count_logs_by_field("experience_type"),
            "api_integration_operation_logs": self._count_logs_by_field("api_service"),
            "state_management_operation_logs": self._count_logs_by_field("state_key"),
            "frontend_routing_operation_logs": self._count_logs_by_field("route_path"),
            "user_interaction_operation_logs": self._count_logs_by_field("interaction_type"),
            "frontend_rendering_operation_logs": self._count_logs_by_field("rendering_type"),
            "real_time_update_operation_logs": self._count_logs_by_field("update_type")
        }
        
        base_summary["experience_metrics"] = experience_metrics
        return base_summary
    
    def _count_logs_by_field(self, field_name: str) -> int:
        """Count logs that contain a specific field."""
        count = 0
        for log_entry in self.log_entries:
            if field_name in log_entry.data:
                count += 1
        return count


