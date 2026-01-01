#!/usr/bin/env python3
"""
Experience Error Handler

Realm-specific error handler for Experience services.
Handles errors from frontend integration and user experience services.

WHAT (Utility Role): I provide error handling for Experience realm
HOW (Utility Implementation): I handle frontend and user experience errors with appropriate recovery strategies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorContext, ErrorResponse, ErrorSeverity, ErrorAction


class ExperienceErrorHandler(RealmErrorHandlerBase):
    """
    Error handler for Experience realm.
    
    Handles errors from:
    - Frontend Integration Service
    - UI Component Services
    - User Experience Services
    - API Integration Services
    - Frontend State Management
    """
    
    def __init__(self, service_name: str = "experience"):
        """Initialize Experience error handler."""
        super().__init__("experience", service_name)
        
        # Experience-specific error patterns
        self._initialize_experience_patterns()
        
        self.logger.info(f"✅ Experience error handler initialized for {service_name}")
    
    def _initialize_experience_patterns(self):
        """Initialize Experience-specific error patterns."""
        # Override common errors with Experience-specific patterns
        self.realm_error_patterns["common_errors"].update({
            "FRONTEND_INTEGRATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Frontend integration error - retrying"
            },
            "UI_COMPONENT_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.FALLBACK,
                "user_message": "UI component error - using fallback"
            },
            "USER_EXPERIENCE_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "User experience error - retrying"
            },
            "API_INTEGRATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "API integration error - retrying"
            },
            "STATE_MANAGEMENT_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.RETRY,
                "user_message": "State management error - retrying"
            },
            "FRONTEND_ROUTING_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.FALLBACK,
                "user_message": "Frontend routing error - using fallback"
            },
            "USER_INTERACTION_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.RETRY,
                "user_message": "User interaction error - retrying"
            },
            "FRONTEND_RENDERING_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.FALLBACK,
                "user_message": "Frontend rendering error - using fallback"
            },
            "REAL_TIME_UPDATE_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.LOG_AND_CONTINUE,
                "user_message": "Real-time update error - continuing"
            }
        })
        
        # Add Experience-specific recovery strategies
        self.realm_error_patterns["recovery_strategies"].update({
            "FRONTEND_INTEGRATION_ERROR": [
                "Check frontend-backend connectivity",
                "Verify API endpoints",
                "Retry integration",
                "Use offline mode"
            ],
            "UI_COMPONENT_ERROR": [
                "Check component configuration",
                "Verify component dependencies",
                "Use fallback component",
                "Reload component"
            ],
            "USER_EXPERIENCE_ERROR": [
                "Check user context",
                "Verify user permissions",
                "Retry user operation",
                "Use simplified experience"
            ],
            "API_INTEGRATION_ERROR": [
                "Check API connectivity",
                "Verify API credentials",
                "Retry with backoff",
                "Use cached data"
            ],
            "STATE_MANAGEMENT_ERROR": [
                "Check state configuration",
                "Verify state transitions",
                "Reset state",
                "Use default state"
            ],
            "FRONTEND_ROUTING_ERROR": [
                "Check routing configuration",
                "Verify route definitions",
                "Use fallback route",
                "Redirect to home"
            ],
            "USER_INTERACTION_ERROR": [
                "Check user input",
                "Verify interaction rules",
                "Retry interaction",
                "Show error message"
            ],
            "FRONTEND_RENDERING_ERROR": [
                "Check rendering configuration",
                "Verify component props",
                "Use fallback rendering",
                "Reload page"
            ],
            "REAL_TIME_UPDATE_ERROR": [
                "Check WebSocket connection",
                "Verify real-time configuration",
                "Continue without updates",
                "Use polling fallback"
            ]
        })
    
    def handle_frontend_integration_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle frontend integration errors."""
        # Add frontend integration-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "frontend_integration",
            "integration_type": getattr(error, 'integration_type', 'unknown'),
            "api_endpoint": getattr(error, 'api_endpoint', 'unknown'),
            "http_method": getattr(error, 'http_method', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_ui_component_error(self, error: Exception, context: ErrorContext, component_name: str) -> ErrorResponse:
        """Handle UI component errors."""
        # Add UI component-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "ui_component",
            "component_name": component_name,
            "component_type": getattr(error, 'component_type', 'unknown'),
            "component_props": getattr(error, 'component_props', {})
        })
        
        return self.handle_error(error, context)
    
    def handle_user_experience_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle user experience errors."""
        # Add user experience-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "user_experience",
            "experience_type": getattr(error, 'experience_type', 'unknown'),
            "user_action": getattr(error, 'user_action', 'unknown'),
            "experience_context": getattr(error, 'experience_context', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_api_integration_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle API integration errors."""
        # Add API integration-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "api_integration",
            "api_service": getattr(error, 'api_service', 'unknown'),
            "api_operation": getattr(error, 'api_operation', 'unknown'),
            "request_data": getattr(error, 'request_data', {})
        })
        
        return self.handle_error(error, context)
    
    def handle_state_management_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle state management errors."""
        # Add state management-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "state_management",
            "state_key": getattr(error, 'state_key', 'unknown'),
            "state_operation": getattr(error, 'state_operation', 'unknown'),
            "state_value": getattr(error, 'state_value', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_frontend_routing_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle frontend routing errors."""
        # Add frontend routing-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "frontend_routing",
            "route_path": getattr(error, 'route_path', 'unknown'),
            "routing_operation": getattr(error, 'routing_operation', 'unknown'),
            "route_params": getattr(error, 'route_params', {})
        })
        
        return self.handle_error(error, context)
    
    def handle_user_interaction_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle user interaction errors."""
        # Add user interaction-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "user_interaction",
            "interaction_type": getattr(error, 'interaction_type', 'unknown'),
            "interaction_element": getattr(error, 'interaction_element', 'unknown'),
            "user_input": getattr(error, 'user_input', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_frontend_rendering_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle frontend rendering errors."""
        # Add frontend rendering-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "frontend_rendering",
            "rendering_type": getattr(error, 'rendering_type', 'unknown'),
            "rendering_component": getattr(error, 'rendering_component', 'unknown'),
            "rendering_data": getattr(error, 'rendering_data', {})
        })
        
        return self.handle_error(error, context)
    
    def handle_real_time_update_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle real-time update errors."""
        # Add real-time update-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "real_time_update",
            "update_type": getattr(error, 'update_type', 'unknown'),
            "update_source": getattr(error, 'update_source', 'unknown'),
            "update_data": getattr(error, 'update_data', {})
        })
        
        return self.handle_error(error, context)
    
    def get_experience_error_summary(self) -> Dict[str, Any]:
        """Get Experience-specific error summary."""
        base_summary = self.get_error_statistics()
        
        # Add Experience-specific metrics
        experience_metrics = {
            "frontend_integration_errors": self.error_counts.get("FRONTEND_INTEGRATION_ERROR", 0),
            "ui_component_errors": self.error_counts.get("UI_COMPONENT_ERROR", 0),
            "user_experience_errors": self.error_counts.get("USER_EXPERIENCE_ERROR", 0),
            "api_integration_errors": self.error_counts.get("API_INTEGRATION_ERROR", 0),
            "state_management_errors": self.error_counts.get("STATE_MANAGEMENT_ERROR", 0),
            "frontend_routing_errors": self.error_counts.get("FRONTEND_ROUTING_ERROR", 0),
            "user_interaction_errors": self.error_counts.get("USER_INTERACTION_ERROR", 0),
            "frontend_rendering_errors": self.error_counts.get("FRONTEND_RENDERING_ERROR", 0),
            "real_time_update_errors": self.error_counts.get("REAL_TIME_UPDATE_ERROR", 0)
        }
        
        base_summary["experience_metrics"] = experience_metrics
        return base_summary


