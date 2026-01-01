#!/usr/bin/env python3
"""
Solution Error Handler

Realm-specific error handler for Solution realm services.
Handles solution orchestration and business outcome related errors.

WHAT (Utility Role): I handle solution realm specific errors
HOW (Utility Implementation): I provide solution-specific error handling patterns
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorSeverity, ErrorAction


class SolutionErrorHandler(RealmErrorHandlerBase):
    """
    Solution Error Handler
    
    Handles solution orchestration and business outcome related errors.
    Provides solution-specific error patterns and recovery suggestions.
    """
    
    def __init__(self, service_name: str = "solution"):
        """Initialize Solution error handler."""
        super().__init__("solution", service_name)
        
        # Solution-specific error patterns
        self.solution_error_patterns = self._initialize_solution_patterns()
        
        self.logger.info(f"✅ Solution error handler initialized for {service_name}")
    
    def _initialize_solution_patterns(self) -> Dict[str, Any]:
        """Initialize solution-specific error patterns."""
        return {
            "solution_errors": {
                "SOLUTION_ORCHESTRATION_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.RETRY_WITH_BACKOFF,
                    "user_message": "Solution orchestration failed - please try again"
                },
                "BUSINESS_OUTCOME_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Business outcome processing failed - please contact support"
                },
                "SOLUTION_CONTEXT_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.LOG_AND_CONTINUE,
                    "user_message": "Solution context issue - continuing with default context"
                },
                "SOLUTION_VALIDATION_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "Solution validation failed - please check your input"
                },
                "SOLUTION_ROUTING_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.FALLBACK,
                    "user_message": "Solution routing failed - using alternative path"
                },
                "SOLUTION_TIMEOUT_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "Solution timeout - please try again"
                },
                "SOLUTION_PERMISSION_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Solution access denied - please check your permissions"
                },
                "SOLUTION_INTEGRATION_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.FALLBACK,
                    "user_message": "Solution integration failed - using fallback method"
                },
                "SOLUTION_DATA_ERROR": {
                    "severity": ErrorSeverity.MEDIUM,
                    "action": ErrorAction.RETRY,
                    "user_message": "Solution data issue - please try again"
                },
                "SOLUTION_CONFIGURATION_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Solution configuration error - please contact support"
                },
                "SOLUTION_DEPENDENCY_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Solution dependency failed - please contact support"
                },
                "SOLUTION_SCALING_ERROR": {
                    "severity": ErrorSeverity.HIGH,
                    "action": ErrorAction.ESCALATE,
                    "user_message": "Solution scaling failed - please contact support"
                }
            },
            "recovery_strategies": {
                "SOLUTION_ORCHESTRATION_ERROR": [
                    "Check solution orchestration service health",
                    "Verify solution configuration",
                    "Retry with exponential backoff",
                    "Use alternative orchestration method"
                ],
                "BUSINESS_OUTCOME_ERROR": [
                    "Check business outcome service status",
                    "Verify business logic configuration",
                    "Escalate to business stakeholders",
                    "Use fallback business processes"
                ],
                "SOLUTION_CONTEXT_ERROR": [
                    "Check solution context service",
                    "Verify context data integrity",
                    "Use default context values",
                    "Reinitialize context if needed"
                ],
                "SOLUTION_VALIDATION_ERROR": [
                    "Check input validation rules",
                    "Verify data format requirements",
                    "Provide clear validation messages",
                    "Implement progressive validation"
                ],
                "SOLUTION_ROUTING_ERROR": [
                    "Check solution routing service",
                    "Verify routing configuration",
                    "Use alternative routing paths",
                    "Implement circuit breaker pattern"
                ],
                "SOLUTION_TIMEOUT_ERROR": [
                    "Increase timeout values",
                    "Implement retry logic",
                    "Use asynchronous processing",
                    "Optimize solution performance"
                ],
                "SOLUTION_PERMISSION_ERROR": [
                    "Check user permissions",
                    "Verify authorization policies",
                    "Refresh user context",
                    "Escalate to administrator"
                ],
                "SOLUTION_INTEGRATION_ERROR": [
                    "Check integration service health",
                    "Verify integration configuration",
                    "Use alternative integration methods",
                    "Implement integration fallbacks"
                ],
                "SOLUTION_DATA_ERROR": [
                    "Check data service availability",
                    "Verify data integrity",
                    "Use cached data if available",
                    "Implement data validation"
                ],
                "SOLUTION_CONFIGURATION_ERROR": [
                    "Check solution configuration",
                    "Verify configuration files",
                    "Reset to default configuration",
                    "Escalate to system administrator"
                ],
                "SOLUTION_DEPENDENCY_ERROR": [
                    "Check solution dependencies",
                    "Verify dependency service health",
                    "Use alternative dependencies",
                    "Escalate to dependency owners"
                ],
                "SOLUTION_SCALING_ERROR": [
                    "Check scaling configuration",
                    "Verify resource availability",
                    "Use alternative scaling methods",
                    "Escalate to infrastructure team"
                ]
            },
            "escalation_rules": {
                "BUSINESS_OUTCOME_ERROR": True,
                "SOLUTION_ORCHESTRATION_ERROR": True,
                "SOLUTION_ROUTING_ERROR": True,
                "SOLUTION_INTEGRATION_ERROR": True,
                "SOLUTION_CONFIGURATION_ERROR": True,
                "SOLUTION_DEPENDENCY_ERROR": True,
                "SOLUTION_SCALING_ERROR": True,
                "SOLUTION_CONTEXT_ERROR": False,
                "SOLUTION_VALIDATION_ERROR": False,
                "SOLUTION_TIMEOUT_ERROR": False,
                "SOLUTION_PERMISSION_ERROR": False,
                "SOLUTION_DATA_ERROR": False
            }
        }
    
    def _get_common_errors(self) -> Dict[str, Dict[str, Any]]:
        """Get common errors for Solution realm."""
        return self.solution_error_patterns["solution_errors"]
    
    def _get_recovery_strategies(self) -> Dict[str, List[str]]:
        """Get recovery strategies for Solution realm."""
        return self.solution_error_patterns["recovery_strategies"]
    
    def _get_escalation_rules(self) -> Dict[str, bool]:
        """Get escalation rules for Solution realm."""
        return self.solution_error_patterns["escalation_rules"]
    
    def _get_user_messages(self) -> Dict[str, str]:
        """Get user-friendly messages for Solution realm."""
        return {
            error_code: error_info["user_message"]
            for error_code, error_info in self.solution_error_patterns["solution_errors"].items()
        }
    
    def handle_solution_error(self, error: Exception, context: Any) -> Any:
        """Handle solution-specific errors with enhanced processing."""
        try:
            # Determine if this is a solution-specific error
            error_message = str(error).lower()
            
            if "orchestration" in error_message or "orchestrate" in error_message:
                error_code = "SOLUTION_ORCHESTRATION_ERROR"
            elif "business outcome" in error_message or "outcome" in error_message:
                error_code = "BUSINESS_OUTCOME_ERROR"
            elif "context" in error_message:
                error_code = "SOLUTION_CONTEXT_ERROR"
            elif "validation" in error_message or "validate" in error_message:
                error_code = "SOLUTION_VALIDATION_ERROR"
            elif "routing" in error_message or "route" in error_message:
                error_code = "SOLUTION_ROUTING_ERROR"
            elif "timeout" in error_message:
                error_code = "SOLUTION_TIMEOUT_ERROR"
            elif "permission" in error_message or "access" in error_message:
                error_code = "SOLUTION_PERMISSION_ERROR"
            elif "integration" in error_message:
                error_code = "SOLUTION_INTEGRATION_ERROR"
            elif "data" in error_message:
                error_code = "SOLUTION_DATA_ERROR"
            elif "configuration" in error_message or "config" in error_message:
                error_code = "SOLUTION_CONFIGURATION_ERROR"
            elif "dependency" in error_message:
                error_code = "SOLUTION_DEPENDENCY_ERROR"
            elif "scaling" in error_message or "scale" in error_message:
                error_code = "SOLUTION_SCALING_ERROR"
            else:
                # Use base error handling
                return super().handle_error(error, context)
            
            # Get solution-specific error pattern
            error_pattern = self.solution_error_patterns["solution_errors"].get(
                error_code,
                self.solution_error_patterns["solution_errors"]["SOLUTION_ORCHESTRATION_ERROR"]
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
                recovery_suggestions=self.solution_error_patterns["recovery_strategies"].get(
                    error_code,
                    ["Check solution configuration", "Contact support if problem persists"]
                ),
                user_message=error_pattern["user_message"],
                technical_details={
                    "solution_error": True,
                    "error_code": error_code,
                    "realm": "solution",
                    "service_name": self.service_name,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timestamp=datetime.utcnow().isoformat(),
                realm="solution",
                service_type="realm"
            )
            
            # Log solution-specific error
            self.logger.error(f"🎯 Solution Error: {error_code} - {str(error)}")
            
            return error_response
            
        except Exception as e:
            self.logger.error(f"❌ Solution error handler failed: {e}")
            # Fallback to base error handling
            return super().handle_error(error, context)
    
    def get_solution_error_statistics(self) -> Dict[str, Any]:
        """Get solution-specific error statistics."""
        base_stats = self.get_error_statistics()
        
        # Add solution-specific statistics
        solution_stats = {
            "solution_errors": {
                error_code: count
                for error_code, count in self.error_counts.items()
                if error_code in self.solution_error_patterns["solution_errors"]
            },
            "solution_error_rate": self._calculate_solution_error_rate(),
            "escalated_solution_errors": self._get_escalated_solution_errors()
        }
        
        return {**base_stats, **solution_stats}
    
    def _calculate_solution_error_rate(self) -> float:
        """Calculate solution error rate."""
        total_errors = sum(self.error_counts.values())
        solution_errors = sum(
            count for error_code, count in self.error_counts.items()
            if error_code in self.solution_error_patterns["solution_errors"]
        )
        
        if total_errors == 0:
            return 0.0
        
        return solution_errors / total_errors
    
    def _get_escalated_solution_errors(self) -> List[str]:
        """Get list of escalated solution errors."""
        escalated_errors = []
        for error_response in self.error_history:
            if (error_response.error_code in self.solution_error_patterns["solution_errors"] and
                self.solution_error_patterns["escalation_rules"].get(error_response.error_code, False)):
                escalated_errors.append(error_response.error_code)
        
        return escalated_errors







