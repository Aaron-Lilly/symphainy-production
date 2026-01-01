#!/usr/bin/env python3
"""
Utility Foundation Error Handler

Realm-specific error handler for Utility Foundation services.
Handles errors from configuration, logging, DI container, and other utility services.

WHAT (Utility Role): I provide error handling for Utility Foundation realm
HOW (Utility Implementation): I handle infrastructure and utility-specific errors with appropriate recovery strategies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorContext, ErrorResponse, ErrorSeverity, ErrorAction


class UtilityFoundationErrorHandler(RealmErrorHandlerBase):
    """
    Error handler for Utility Foundation realm.
    
    Handles errors from:
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
        """Initialize Utility Foundation error handler."""
        super().__init__("utility_foundation", service_name)
        
        # Utility-specific error patterns
        self._initialize_utility_patterns()
        
        self.logger.info(f"✅ Utility Foundation error handler initialized for {service_name}")
    
    def _initialize_utility_patterns(self):
        """Initialize utility-specific error patterns."""
        # Override common errors with utility-specific patterns
        self.realm_error_patterns["common_errors"].update({
            "CONFIGURATION_LOAD_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.ESCALATE,
                "user_message": "Configuration loading failed - system may be unstable"
            },
            "DI_CONTAINER_ERROR": {
                "severity": ErrorSeverity.CRITICAL,
                "action": ErrorAction.ESCALATE,
                "user_message": "Dependency injection failed - system unavailable"
            },
            "LOGGING_INITIALIZATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.FALLBACK,
                "user_message": "Logging initialization failed - using fallback logging"
            },
            "HEALTH_CHECK_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Health check failed - retrying"
            },
            "TELEMETRY_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.LOG_AND_CONTINUE,
                "user_message": "Telemetry reporting failed - continuing operation"
            },
            "SECURITY_CONTEXT_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.ESCALATE,
                "user_message": "Security context error - access denied"
            },
            "TENANT_VALIDATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Tenant validation failed - please check tenant ID"
            },
            "SERIALIZATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Data serialization failed - retrying with different format"
            }
        })
        
        # Add utility-specific recovery strategies
        self.realm_error_patterns["recovery_strategies"].update({
            "CONFIGURATION_LOAD_ERROR": [
                "Check configuration file syntax",
                "Verify environment variables",
                "Restart configuration service",
                "Contact system administrator"
            ],
            "DI_CONTAINER_ERROR": [
                "Check service dependencies",
                "Verify service registration",
                "Restart DI container",
                "Contact system administrator"
            ],
            "LOGGING_INITIALIZATION_ERROR": [
                "Check log directory permissions",
                "Verify logging configuration",
                "Use console logging fallback",
                "Contact system administrator"
            ],
            "HEALTH_CHECK_ERROR": [
                "Retry health check",
                "Check service dependencies",
                "Verify health check configuration",
                "Contact system administrator"
            ],
            "TELEMETRY_ERROR": [
                "Check telemetry service connectivity",
                "Verify telemetry configuration",
                "Use local metrics storage",
                "Continue without telemetry"
            ],
            "SECURITY_CONTEXT_ERROR": [
                "Check user authentication",
                "Verify security configuration",
                "Refresh security tokens",
                "Contact security administrator"
            ],
            "TENANT_VALIDATION_ERROR": [
                "Verify tenant ID format",
                "Check tenant configuration",
                "Refresh tenant context",
                "Contact tenant administrator"
            ],
            "SERIALIZATION_ERROR": [
                "Check data format",
                "Verify serialization configuration",
                "Try alternative serialization method",
                "Contact system administrator"
            ]
        })
    
    def handle_configuration_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle configuration-specific errors."""
        # Add configuration-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "configuration",
            "configuration_file": getattr(error, 'config_file', 'unknown'),
            "configuration_key": getattr(error, 'config_key', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_di_container_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle DI container-specific errors."""
        # Add DI container-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "di_container",
            "service_name": getattr(error, 'service_name', 'unknown'),
            "dependency_type": getattr(error, 'dependency_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_logging_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle logging-specific errors."""
        # Add logging-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "logging",
            "log_level": getattr(error, 'log_level', 'unknown'),
            "log_handler": getattr(error, 'log_handler', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_health_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle health monitoring-specific errors."""
        # Add health-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "health_monitoring",
            "health_check_type": getattr(error, 'health_check_type', 'unknown'),
            "service_status": getattr(error, 'service_status', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_telemetry_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle telemetry-specific errors."""
        # Add telemetry-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "telemetry",
            "metric_name": getattr(error, 'metric_name', 'unknown'),
            "telemetry_endpoint": getattr(error, 'telemetry_endpoint', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_security_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle security-specific errors."""
        # Add security-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "security",
            "security_operation": getattr(error, 'security_operation', 'unknown'),
            "user_context": getattr(error, 'user_context', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_tenant_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle tenant-specific errors."""
        # Add tenant-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "tenant",
            "tenant_id": getattr(error, 'tenant_id', 'unknown'),
            "tenant_operation": getattr(error, 'tenant_operation', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_validation_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle validation-specific errors."""
        # Add validation-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "validation",
            "validation_rule": getattr(error, 'validation_rule', 'unknown'),
            "input_data": getattr(error, 'input_data', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_serialization_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle serialization-specific errors."""
        # Add serialization-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "serialization",
            "serialization_format": getattr(error, 'serialization_format', 'unknown'),
            "data_type": getattr(error, 'data_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def get_utility_error_summary(self) -> Dict[str, Any]:
        """Get utility-specific error summary."""
        base_summary = self.get_error_statistics()
        
        # Add utility-specific metrics
        utility_metrics = {
            "configuration_errors": self.error_counts.get("CONFIGURATION_LOAD_ERROR", 0),
            "di_container_errors": self.error_counts.get("DI_CONTAINER_ERROR", 0),
            "logging_errors": self.error_counts.get("LOGGING_INITIALIZATION_ERROR", 0),
            "health_errors": self.error_counts.get("HEALTH_CHECK_ERROR", 0),
            "telemetry_errors": self.error_counts.get("TELEMETRY_ERROR", 0),
            "security_errors": self.error_counts.get("SECURITY_CONTEXT_ERROR", 0),
            "tenant_errors": self.error_counts.get("TENANT_VALIDATION_ERROR", 0),
            "validation_errors": self.error_counts.get("VALIDATION_ERROR", 0),
            "serialization_errors": self.error_counts.get("SERIALIZATION_ERROR", 0)
        }
        
        base_summary["utility_metrics"] = utility_metrics
        return base_summary


