#!/usr/bin/env python3
"""
Journey Error Handler

Realm-specific error handler for Journey realm services.
Handles journey orchestration and user experience related errors.

WHAT (Utility Role): I handle journey realm specific errors
HOW (Utility Implementation): I provide journey-specific error handling patterns
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorSeverity, ErrorAction


class JourneyErrorHandler(RealmErrorHandlerBase):
    """
    Journey Error Handler
    
    Handles journey orchestration and user experience related errors.
    Provides journey-specific error patterns and recovery suggestions.
    """
    
    def __init__(self, service_name: str = "journey"):
        """Initialize Journey error handler."""
        super().__init__("journey", service_name)
        
        # Journey-specific error patterns
        self.journey_error_patterns = self._initialize_journey_patterns()
        
        self.logger.info(f"✅ Journey error handler initialized for {service_name}")
    
    def _initialize_journey_patterns(self) -> Dict[str, Any]:
        """Initialize journey-specific error patterns."""
        return {
            "journey_errors": {
                "JOURNEY_ORCHESTRATION_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.RETRY_WITH_BACKOFF,
                    "user_message": "Journey orchestration failed - please try again"
                },
                "USER_EXPERIENCE_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "User experience temporarily unavailable - please try again"
                },
                "JOURNEY_CONTEXT_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.LOG_AND_CONTINUE,
                    "user_message": "Journey context issue - continuing with default context"
                },
                "JOURNEY_STATE_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Journey state corrupted - please contact support"
                },
                "JOURNEY_ROUTING_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.FALLBACK,
                    "user_message": "Journey routing failed - using alternative path"
                },
                "JOURNEY_VALIDATION_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "Journey validation failed - please check your input"
                },
                "JOURNEY_TIMEOUT_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "Journey timeout - please try again"
                },
                "JOURNEY_PERMISSION_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Journey access denied - please check your permissions"
                },
                "JOURNEY_INTEGRATION_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.FALLBACK,
                    "user_message": "Journey integration failed - using fallback method"
                },
                "JOURNEY_DATA_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "Journey data issue - please try again"
                }
            },
            "recovery_strategies": {
                "JOURNEY_ORCHESTRATION_ERROR": [
                    "Check journey orchestration service health",
                    "Verify journey configuration",
                    "Retry with exponential backoff",
                    "Use alternative orchestration method"
                ],
                "USER_EXPERIENCE_ERROR": [
                    "Check user experience service status",
                    "Verify UX configuration",
                    "Implement fallback UX",
                    "Use cached experience data"
                ],
                "JOURNEY_CONTEXT_ERROR": [
                    "Check journey context service",
                    "Verify context data integrity",
                    "Use default context values",
                    "Reinitialize context if needed"
                ],
                "JOURNEY_STATE_ERROR": [
                    "Check journey state service",
                    "Verify state data integrity",
                    "Reset journey state if possible",
                    "Escalate to administrator"
                ],
                "JOURNEY_ROUTING_ERROR": [
                    "Check journey routing service",
                    "Verify routing configuration",
                    "Use alternative routing paths",
                    "Implement circuit breaker pattern"
                ],
                "JOURNEY_VALIDATION_ERROR": [
                    "Check input validation rules",
                    "Verify data format requirements",
                    "Provide clear validation messages",
                    "Implement progressive validation"
                ],
                "JOURNEY_TIMEOUT_ERROR": [
                    "Increase timeout values",
                    "Implement retry logic",
                    "Use asynchronous processing",
                    "Optimize journey performance"
                ],
                "JOURNEY_PERMISSION_ERROR": [
                    "Check user permissions",
                    "Verify authorization policies",
                    "Refresh user context",
                    "Escalate to administrator"
                ],
                "JOURNEY_INTEGRATION_ERROR": [
                    "Check integration service health",
                    "Verify integration configuration",
                    "Use alternative integration methods",
                    "Implement integration fallbacks"
                ],
                "JOURNEY_DATA_ERROR": [
                    "Check data service availability",
                    "Verify data integrity",
                    "Use cached data if available",
                    "Implement data validation"
                ]
            },
            "escalation_rules": {
                "JOURNEY_STATE_ERROR": True,
                "JOURNEY_ORCHESTRATION_ERROR": True,
                "JOURNEY_ROUTING_ERROR": True,
                "JOURNEY_INTEGRATION_ERROR": True,
                "USER_EXPERIENCE_ERROR": False,
                "JOURNEY_CONTEXT_ERROR": False,
                "JOURNEY_VALIDATION_ERROR": False,
                "JOURNEY_TIMEOUT_ERROR": False,
                "JOURNEY_PERMISSION_ERROR": False,
                "JOURNEY_DATA_ERROR": False
            }
        }
    
    def _get_common_errors(self) -> Dict[str, Dict[str, Any]]:
        """Get common errors for Journey realm."""
        return self.journey_error_patterns["journey_errors"]
    
    def _get_recovery_strategies(self) -> Dict[str, List[str]]:
        """Get recovery strategies for Journey realm."""
        return self.journey_error_patterns["recovery_strategies"]
    
    def _get_escalation_rules(self) -> Dict[str, bool]:
        """Get escalation rules for Journey realm."""
        return self.journey_error_patterns["escalation_rules"]
    
    def _get_user_messages(self) -> Dict[str, str]:
        """Get user-friendly messages for Journey realm."""
        return {
            error_code: error_info["user_message"]
            for error_code, error_info in self.journey_error_patterns["journey_errors"].items()
        }
    
    def handle_journey_error(self, error: Exception, context: Any) -> Any:
        """Handle journey-specific errors with enhanced processing."""
        try:
            # Determine if this is a journey-specific error
            error_message = str(error).lower()
            
            if "orchestration" in error_message or "orchestrate" in error_message:
                error_code = "JOURNEY_ORCHESTRATION_ERROR"
            elif "user experience" in error_message or "ux" in error_message:
                error_code = "USER_EXPERIENCE_ERROR"
            elif "context" in error_message:
                error_code = "JOURNEY_CONTEXT_ERROR"
            elif "state" in error_message:
                error_code = "JOURNEY_STATE_ERROR"
            elif "routing" in error_message or "route" in error_message:
                error_code = "JOURNEY_ROUTING_ERROR"
            elif "validation" in error_message or "validate" in error_message:
                error_code = "JOURNEY_VALIDATION_ERROR"
            elif "timeout" in error_message:
                error_code = "JOURNEY_TIMEOUT_ERROR"
            elif "permission" in error_message or "access" in error_message:
                error_code = "JOURNEY_PERMISSION_ERROR"
            elif "integration" in error_message:
                error_code = "JOURNEY_INTEGRATION_ERROR"
            elif "data" in error_message:
                error_code = "JOURNEY_DATA_ERROR"
            else:
                # Use base error handling
                return super().handle_error(error, context)
            
            # Get journey-specific error pattern
            error_pattern = self.journey_error_patterns["journey_errors"].get(
                error_code,
                self.journey_error_patterns["journey_errors"]["JOURNEY_ORCHESTRATION_ERROR"]
            )
            
            # Create enhanced error response
            from .realm_error_handler_base import ErrorResponse, ErrorContext
            
            error_response = ErrorResponse(
                success=False,
                error_code=error_code,
                error_message=str(error),
                error_type=type(error).__name__,
                severity=error_pattern["severity"],
                action=error_pattern["action"],
                recovery_suggestions=self.journey_error_patterns["recovery_strategies"].get(
                    error_code,
                    ["Check journey configuration", "Contact support if problem persists"]
                ),
                user_message=error_pattern["user_message"],
                technical_details={
                    "journey_error": True,
                    "error_code": error_code,
                    "realm": "journey",
                    "service_name": self.service_name,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timestamp=datetime.utcnow().isoformat(),
                realm="journey",
                service_type="realm"
            )
            
            # Log journey-specific error
            self.logger.error(f"🛤️ Journey Error: {error_code} - {str(error)}")
            
            return error_response
            
        except Exception as e:
            self.logger.error(f"❌ Journey error handler failed: {e}")
            # Fallback to base error handling
            return super().handle_error(error, context)
    
    def get_journey_error_statistics(self) -> Dict[str, Any]:
        """Get journey-specific error statistics."""
        base_stats = self.get_error_statistics()
        
        # Add journey-specific statistics
        journey_stats = {
            "journey_errors": {
                error_code: count
                for error_code, count in self.error_counts.items()
                if error_code in self.journey_error_patterns["journey_errors"]
            },
            "journey_error_rate": self._calculate_journey_error_rate(),
            "escalated_journey_errors": self._get_escalated_journey_errors()
        }
        
        return {**base_stats, **journey_stats}
    
    def _calculate_journey_error_rate(self) -> float:
        """Calculate journey error rate."""
        total_errors = sum(self.error_counts.values())
        journey_errors = sum(
            count for error_code, count in self.error_counts.items()
            if error_code in self.journey_error_patterns["journey_errors"]
        )
        
        if total_errors == 0:
            return 0.0
        
        return journey_errors / total_errors
    
    def _get_escalated_journey_errors(self) -> List[str]:
        """Get list of escalated journey errors."""
        escalated_errors = []
        for error_response in self.error_history:
            if (error_response.error_code in self.journey_error_patterns["journey_errors"] and
                self.journey_error_patterns["escalation_rules"].get(error_response.error_code, False)):
                escalated_errors.append(error_response.error_code)
        
        return escalated_errors







