#!/usr/bin/env python3
"""
Realm-Specific Error Handler Base

Base class for realm-specific error handlers with real working implementations.
Provides common functionality and patterns for all realm error handlers.

WHAT (Utility Role): I provide the foundation for realm-specific error handling
HOW (Utility Implementation): I implement common error handling patterns with realm-specific customization
"""

import traceback
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json

from .error_handler import SmartCityError, ValidationError, ConfigurationError, ServiceError, IntegrationError, MCPError


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorAction(Enum):
    """Recommended actions for error recovery."""
    RETRY = "retry"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    LOG_AND_CONTINUE = "log_and_continue"
    TERMINATE = "terminate"


@dataclass
class ErrorContext:
    """Enhanced error context with realm-specific information."""
    realm: str
    service_type: str
    service_name: str
    operation: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    additional_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}


@dataclass
class ErrorResponse:
    """Standardized error response structure."""
    success: bool = False
    error_code: str = "UNKNOWN_ERROR"
    error_message: str = "An error occurred"
    error_type: str = "UnknownError"
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    action: ErrorAction = ErrorAction.LOG_AND_CONTINUE
    recovery_suggestions: List[str] = None
    user_message: str = ""
    technical_details: Dict[str, Any] = None
    request_id: Optional[str] = None
    timestamp: str = ""
    realm: str = ""
    service_type: str = ""
    
    def __post_init__(self):
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []
        if self.technical_details is None:
            self.technical_details = {}
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class RealmErrorHandlerBase:
    """
    Base class for realm-specific error handlers.
    
    Provides common error handling functionality with realm-specific customization.
    All realm error handlers inherit from this base class.
    """
    
    def __init__(self, realm_name: str, service_name: str = None):
        """Initialize realm error handler."""
        self.realm_name = realm_name
        self.service_name = service_name or f"{realm_name}_service"
        self.logger = logging.getLogger(f"RealmErrorHandler-{realm_name}")
        
        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.error_history: List[ErrorResponse] = []
        self.max_history_size = 1000
        
        # Realm-specific error patterns
        self.realm_error_patterns = self._initialize_realm_patterns()
        
        self.logger.info(f"✅ Realm error handler initialized for {realm_name}")
    
    def _initialize_realm_patterns(self) -> Dict[str, Any]:
        """Initialize realm-specific error patterns."""
        return {
            "common_errors": self._get_common_errors(),
            "recovery_strategies": self._get_recovery_strategies(),
            "escalation_rules": self._get_escalation_rules(),
            "user_messages": self._get_user_messages()
        }
    
    def _get_common_errors(self) -> Dict[str, Dict[str, Any]]:
        """Get common errors for this realm."""
        return {
            "VALIDATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Please check your input and try again"
            },
            "CONFIGURATION_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.ESCALATE,
                "user_message": "System configuration issue - please contact support"
            },
            "SERVICE_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Service temporarily unavailable - please try again"
            },
            "INTEGRATION_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.FALLBACK,
                "user_message": "Integration issue - using fallback method"
            },
            "AUTHORIZATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.ESCALATE,
                "user_message": "Access denied - please check your permissions"
            },
            "RATE_LIMIT_ERROR": {
                "severity": ErrorSeverity.LOW,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Rate limit exceeded - please wait and try again"
            }
        }
    
    def _get_recovery_strategies(self) -> Dict[str, List[str]]:
        """Get recovery strategies for this realm."""
        return {
            "VALIDATION_ERROR": [
                "Validate input data format",
                "Check required fields",
                "Verify data types"
            ],
            "CONFIGURATION_ERROR": [
                "Check environment variables",
                "Verify configuration files",
                "Contact system administrator"
            ],
            "SERVICE_ERROR": [
                "Retry the operation",
                "Check service health",
                "Use fallback service if available"
            ],
            "INTEGRATION_ERROR": [
                "Check network connectivity",
                "Verify service endpoints",
                "Use alternative integration method"
            ],
            "AUTHORIZATION_ERROR": [
                "Check user permissions",
                "Verify authentication token",
                "Contact administrator for access"
            ],
            "RATE_LIMIT_ERROR": [
                "Wait before retrying",
                "Reduce request frequency",
                "Contact administrator for limit increase"
            ]
        }
    
    def _get_escalation_rules(self) -> Dict[str, bool]:
        """Get escalation rules for this realm."""
        return {
            "CRITICAL": True,
            "HIGH": True,
            "MEDIUM": False,
            "LOW": False
        }
    
    def _get_user_messages(self) -> Dict[str, str]:
        """Get user-friendly messages for this realm."""
        return {
            "VALIDATION_ERROR": "Please check your input and try again",
            "CONFIGURATION_ERROR": "System configuration issue - please contact support",
            "SERVICE_ERROR": "Service temporarily unavailable - please try again",
            "INTEGRATION_ERROR": "Integration issue - using fallback method",
            "AUTHORIZATION_ERROR": "Access denied - please check your permissions",
            "RATE_LIMIT_ERROR": "Rate limit exceeded - please wait and try again"
        }
    
    def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle an error with realm-specific processing."""
        try:
            # Create error response
            error_response = self._create_error_response(error, context)
            
            # Update error tracking
            self._update_error_tracking(error_response)
            
            # Log the error
            self._log_error(error, context, error_response)
            
            # Check for escalation
            if self._should_escalate(error_response):
                self._escalate_error(error_response, context)
            
            return error_response
            
        except Exception as e:
            # Fallback error handling
            self.logger.error(f"❌ Error handler failed: {e}")
            return self._create_fallback_error_response(error, context)
    
    def _create_error_response(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Create error response with realm-specific processing."""
        # Determine error type and code
        error_type = type(error).__name__
        error_code = self._get_error_code(error, context)
        
        # Get realm-specific error pattern
        error_pattern = self.realm_error_patterns["common_errors"].get(
            error_code, 
            self.realm_error_patterns["common_errors"]["SERVICE_ERROR"]
        )
        
        # Create error response
        error_response = ErrorResponse(
            success=False,
            error_code=error_code,
            error_message=str(error),
            error_type=error_type,
            severity=error_pattern["severity"],
            action=error_pattern["action"],
            recovery_suggestions=self.realm_error_patterns["recovery_strategies"].get(
                error_code, 
                ["Check logs for details", "Contact support if problem persists"]
            ),
            user_message=error_pattern["user_message"],
            technical_details=self._get_technical_details(error, context),
            request_id=context.request_id,
            timestamp=datetime.utcnow().isoformat(),
            realm=context.realm,
            service_type=context.service_type
        )
        
        return error_response
    
    def _get_error_code(self, error: Exception, context: ErrorContext) -> str:
        """Get error code based on error type and context."""
        if isinstance(error, ValidationError):
            return "VALIDATION_ERROR"
        elif isinstance(error, ConfigurationError):
            return "CONFIGURATION_ERROR"
        elif isinstance(error, ServiceError):
            return "SERVICE_ERROR"
        elif isinstance(error, IntegrationError):
            return "INTEGRATION_ERROR"
        elif isinstance(error, MCPError):
            return "MCP_ERROR"
        elif "permission" in str(error).lower() or "authorization" in str(error).lower():
            return "AUTHORIZATION_ERROR"
        elif "rate limit" in str(error).lower() or "throttle" in str(error).lower():
            return "RATE_LIMIT_ERROR"
        else:
            return "UNKNOWN_ERROR"
    
    def _get_technical_details(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Get technical details for error response."""
        return {
            "traceback": traceback.format_exc(),
            "error_class": type(error).__name__,
            "error_module": getattr(error, '__module__', 'unknown'),
            "context": {
                "realm": context.realm,
                "service_type": context.service_type,
                "service_name": context.service_name,
                "operation": context.operation,
                "user_id": context.user_id,
                "tenant_id": context.tenant_id,
                "request_id": context.request_id,
                "correlation_id": context.correlation_id
            },
            "additional_context": context.additional_context or {}
        }
    
    def _update_error_tracking(self, error_response: ErrorResponse):
        """Update error tracking statistics."""
        # Update error counts
        error_code = error_response.error_code
        self.error_counts[error_code] = self.error_counts.get(error_code, 0) + 1
        
        # Add to error history
        self.error_history.append(error_response)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _log_error(self, error: Exception, context: ErrorContext, error_response: ErrorResponse):
        """Log error with appropriate level and context."""
        log_data = {
            "error_code": error_response.error_code,
            "error_type": error_response.error_type,
            "severity": error_response.severity.value,
            "action": error_response.action.value,
            "realm": context.realm,
            "service_type": context.service_type,
            "service_name": context.service_name,
            "operation": context.operation,
            "user_id": context.user_id,
            "tenant_id": context.tenant_id,
            "request_id": context.request_id,
            "correlation_id": context.correlation_id,
            "error_message": str(error),
            "recovery_suggestions": error_response.recovery_suggestions
        }
        
        # Log with appropriate level based on severity
        if error_response.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"🚨 CRITICAL ERROR: {error_response.error_code}", extra=log_data)
        elif error_response.severity == ErrorSeverity.HIGH:
            self.logger.error(f"❌ HIGH SEVERITY ERROR: {error_response.error_code}", extra=log_data)
        elif error_response.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"⚠️ MEDIUM SEVERITY ERROR: {error_response.error_code}", extra=log_data)
        else:
            self.logger.info(f"ℹ️ LOW SEVERITY ERROR: {error_response.error_code}", extra=log_data)
    
    def _should_escalate(self, error_response: ErrorResponse) -> bool:
        """Check if error should be escalated."""
        escalation_rules = self.realm_error_patterns["escalation_rules"]
        return escalation_rules.get(error_response.severity.value, False)
    
    def _escalate_error(self, error_response: ErrorResponse, context: ErrorContext):
        """Escalate error to appropriate level."""
        escalation_data = {
            "error_response": error_response,
            "context": context,
            "escalation_timestamp": datetime.utcnow().isoformat(),
            "realm": self.realm_name
        }
        
        self.logger.critical(f"🚨 ERROR ESCALATION: {error_response.error_code}", extra=escalation_data)
        
        # TODO: Implement actual escalation (email, Slack, PagerDuty, etc.)
        # This would integrate with your existing monitoring and alerting systems
    
    def _create_fallback_error_response(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Create fallback error response when error handler fails."""
        return ErrorResponse(
            success=False,
            error_code="ERROR_HANDLER_FAILED",
            error_message="Error handler failed to process error",
            error_type="ErrorHandlerError",
            severity=ErrorSeverity.CRITICAL,
            action=ErrorAction.ESCALATE,
            recovery_suggestions=["Contact system administrator immediately"],
            user_message="System error - please contact support",
            technical_details={
                "original_error": str(error),
                "original_error_type": type(error).__name__,
                "fallback_reason": "Error handler failed"
            },
            request_id=context.request_id,
            timestamp=datetime.utcnow().isoformat(),
            realm=context.realm,
            service_type=context.service_type
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for this realm."""
        return {
            "realm": self.realm_name,
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-10:],  # Last 10 errors
            "error_rate_by_severity": self._calculate_error_rate_by_severity(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_error_rate_by_severity(self) -> Dict[str, int]:
        """Calculate error rate by severity level."""
        severity_counts = {}
        for error_response in self.error_history:
            severity = error_response.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts
    
    def clear_error_history(self):
        """Clear error history (useful for testing)."""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info(f"✅ Error history cleared for {self.realm_name}")


