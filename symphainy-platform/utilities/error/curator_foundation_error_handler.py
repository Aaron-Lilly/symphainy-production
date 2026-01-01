#!/usr/bin/env python3
"""
Curator Foundation Error Handler

Realm-specific error handler for Curator Foundation services.
Handles errors from service discovery, agent management, and capability registry services.

WHAT (Utility Role): I provide error handling for Curator Foundation realm
HOW (Utility Implementation): I handle service discovery and agent management errors with appropriate recovery strategies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorContext, ErrorResponse, ErrorSeverity, ErrorAction


class CuratorFoundationErrorHandler(RealmErrorHandlerBase):
    """
    Error handler for Curator Foundation realm.
    
    Handles errors from:
    - Service Discovery Service
    - Agent Capability Registry Service
    - Agent Specialization Management Service
    - Service Registration Services
    - Agent Management Services
    """
    
    def __init__(self, service_name: str = "curator_foundation"):
        """Initialize Curator Foundation error handler."""
        super().__init__("curator_foundation", service_name)
        
        # Curator Foundation-specific error patterns
        self._initialize_curator_foundation_patterns()
        
        self.logger.info(f"✅ Curator Foundation error handler initialized for {service_name}")
    
    def _initialize_curator_foundation_patterns(self):
        """Initialize Curator Foundation-specific error patterns."""
        # Override common errors with Curator Foundation-specific patterns
        self.realm_error_patterns["common_errors"].update({
            "SERVICE_DISCOVERY_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.ESCALATE,
                "user_message": "Service discovery error - system may be unstable"
            },
            "AGENT_REGISTRY_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Agent registry error - retrying"
            },
            "AGENT_SPECIALIZATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Agent specialization error - retrying"
            },
            "SERVICE_REGISTRATION_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Service registration error - retrying"
            },
            "AGENT_MANAGEMENT_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Agent management error - retrying"
            },
            "CAPABILITY_REGISTRATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Capability registration error - retrying"
            },
            "SERVICE_HEALTH_CHECK_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Service health check error - retrying"
            },
            "AGENT_HEALTH_CHECK_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Agent health check error - retrying"
            },
            "SERVICE_COMMUNICATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Service communication error - retrying"
            }
        })
        
        # Add Curator Foundation-specific recovery strategies
        self.realm_error_patterns["recovery_strategies"].update({
            "SERVICE_DISCOVERY_ERROR": [
                "Check service registry",
                "Verify service registrations",
                "Restart service discovery",
                "Use static service configuration"
            ],
            "AGENT_REGISTRY_ERROR": [
                "Check agent registry health",
                "Verify agent registrations",
                "Retry with exponential backoff",
                "Use cached agent information"
            ],
            "AGENT_SPECIALIZATION_ERROR": [
                "Check specialization configuration",
                "Verify agent capabilities",
                "Retry specialization",
                "Use default specialization"
            ],
            "SERVICE_REGISTRATION_ERROR": [
                "Check service configuration",
                "Verify service dependencies",
                "Retry with exponential backoff",
                "Use manual service registration"
            ],
            "AGENT_MANAGEMENT_ERROR": [
                "Check agent configuration",
                "Verify agent health",
                "Retry agent operations",
                "Use simplified agent management"
            ],
            "CAPABILITY_REGISTRATION_ERROR": [
                "Check capability configuration",
                "Verify capability definitions",
                "Retry registration",
                "Use manual capability registration"
            ],
            "SERVICE_HEALTH_CHECK_ERROR": [
                "Check service health endpoints",
                "Verify health check configuration",
                "Retry health checks",
                "Use basic health monitoring"
            ],
            "AGENT_HEALTH_CHECK_ERROR": [
                "Check agent health endpoints",
                "Verify agent configuration",
                "Retry health checks",
                "Use basic agent monitoring"
            ],
            "SERVICE_COMMUNICATION_ERROR": [
                "Check service connectivity",
                "Verify service endpoints",
                "Retry with backoff",
                "Use alternative communication"
            ]
        })
    
    def handle_service_discovery_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle service discovery errors."""
        # Add service discovery-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "service_discovery",
            "discovery_operation": getattr(error, 'discovery_operation', 'unknown'),
            "service_name": getattr(error, 'service_name', 'unknown'),
            "registry_type": getattr(error, 'registry_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_agent_registry_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle agent registry errors."""
        # Add agent registry-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "agent_registry",
            "registry_operation": getattr(error, 'registry_operation', 'unknown'),
            "agent_id": getattr(error, 'agent_id', 'unknown'),
            "capability_name": getattr(error, 'capability_name', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_agent_specialization_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle agent specialization errors."""
        # Add agent specialization-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "agent_specialization",
            "specialization_operation": getattr(error, 'specialization_operation', 'unknown'),
            "specialization_id": getattr(error, 'specialization_id', 'unknown'),
            "agent_id": getattr(error, 'agent_id', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_service_registration_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle service registration errors."""
        # Add service registration-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "service_registration",
            "registration_operation": getattr(error, 'registration_operation', 'unknown'),
            "service_name": getattr(error, 'service_name', 'unknown'),
            "service_type": getattr(error, 'service_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_agent_management_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle agent management errors."""
        # Add agent management-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "agent_management",
            "management_operation": getattr(error, 'management_operation', 'unknown'),
            "agent_id": getattr(error, 'agent_id', 'unknown'),
            "agent_type": getattr(error, 'agent_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_capability_registration_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle capability registration errors."""
        # Add capability registration-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "capability_registration",
            "registration_operation": getattr(error, 'registration_operation', 'unknown'),
            "capability_name": getattr(error, 'capability_name', 'unknown'),
            "agent_id": getattr(error, 'agent_id', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_service_health_check_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle service health check errors."""
        # Add service health check-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "service_health_check",
            "health_check_type": getattr(error, 'health_check_type', 'unknown'),
            "service_name": getattr(error, 'service_name', 'unknown'),
            "health_status": getattr(error, 'health_status', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_agent_health_check_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle agent health check errors."""
        # Add agent health check-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "agent_health_check",
            "health_check_type": getattr(error, 'health_check_type', 'unknown'),
            "agent_id": getattr(error, 'agent_id', 'unknown'),
            "health_status": getattr(error, 'health_status', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_service_communication_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle service communication errors."""
        # Add service communication-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "service_communication",
            "communication_type": getattr(error, 'communication_type', 'unknown'),
            "source_service": getattr(error, 'source_service', 'unknown'),
            "target_service": getattr(error, 'target_service', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def get_curator_foundation_error_summary(self) -> Dict[str, Any]:
        """Get Curator Foundation-specific error summary."""
        base_summary = self.get_error_statistics()
        
        # Add Curator Foundation-specific metrics
        curator_foundation_metrics = {
            "service_discovery_errors": self.error_counts.get("SERVICE_DISCOVERY_ERROR", 0),
            "agent_registry_errors": self.error_counts.get("AGENT_REGISTRY_ERROR", 0),
            "agent_specialization_errors": self.error_counts.get("AGENT_SPECIALIZATION_ERROR", 0),
            "service_registration_errors": self.error_counts.get("SERVICE_REGISTRATION_ERROR", 0),
            "agent_management_errors": self.error_counts.get("AGENT_MANAGEMENT_ERROR", 0),
            "capability_registration_errors": self.error_counts.get("CAPABILITY_REGISTRATION_ERROR", 0),
            "service_health_check_errors": self.error_counts.get("SERVICE_HEALTH_CHECK_ERROR", 0),
            "agent_health_check_errors": self.error_counts.get("AGENT_HEALTH_CHECK_ERROR", 0),
            "service_communication_errors": self.error_counts.get("SERVICE_COMMUNICATION_ERROR", 0)
        }
        
        base_summary["curator_foundation_metrics"] = curator_foundation_metrics
        return base_summary


