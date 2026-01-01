#!/usr/bin/env python3
"""
Business Enablement Error Handler

Realm-specific error handler for Business Enablement services.
Handles errors from pillars and business logic services.

WHAT (Utility Role): I provide error handling for Business Enablement realm
HOW (Utility Implementation): I handle business logic errors with appropriate recovery strategies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorContext, ErrorResponse, ErrorSeverity, ErrorAction


class BusinessEnablementErrorHandler(RealmErrorHandlerBase):
    """
    Error handler for Business Enablement realm.
    
    Handles errors from:
    - Content Pillar Service
    - Operations Pillar Service
    - Insights Pillar Service
    - Delivery Manager Service
    - Experience Manager Service
    - Business Logic Services
    """
    
    def __init__(self, service_name: str = "business_enablement"):
        """Initialize Business Enablement error handler."""
        super().__init__("business_enablement", service_name)
        
        # Business Enablement-specific error patterns
        self._initialize_business_enablement_patterns()
        
        self.logger.info(f"✅ Business Enablement error handler initialized for {service_name}")
    
    def _initialize_business_enablement_patterns(self):
        """Initialize Business Enablement-specific error patterns."""
        # Override common errors with Business Enablement-specific patterns
        self.realm_error_patterns["common_errors"].update({
            "CONTENT_PILLAR_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Content processing error - retrying"
            },
            "OPERATIONS_PILLAR_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Operations processing error - retrying"
            },
            "INSIGHTS_PILLAR_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.FALLBACK,
                "user_message": "Insights processing error - using fallback"
            },
            "DELIVERY_MANAGER_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Delivery coordination error - retrying"
            },
            "EXPERIENCE_MANAGER_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Experience management error - retrying"
            },
            "BUSINESS_LOGIC_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Business logic error - retrying"
            },
            "PILLAR_COORDINATION_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.ESCALATE,
                "user_message": "Pillar coordination error - escalating"
            },
            "API_GATEWAY_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "API gateway error - retrying"
            },
            "FRONTEND_INTEGRATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Frontend integration error - retrying"
            }
        })
        
        # Add Business Enablement-specific recovery strategies
        self.realm_error_patterns["recovery_strategies"].update({
            "CONTENT_PILLAR_ERROR": [
                "Check content service health",
                "Verify content processing pipeline",
                "Retry with exponential backoff",
                "Use content processing fallback"
            ],
            "OPERATIONS_PILLAR_ERROR": [
                "Check operations service health",
                "Verify operations pipeline",
                "Retry with exponential backoff",
                "Use operations fallback"
            ],
            "INSIGHTS_PILLAR_ERROR": [
                "Check insights service health",
                "Verify analytics pipeline",
                "Use cached insights",
                "Use simplified analytics"
            ],
            "DELIVERY_MANAGER_ERROR": [
                "Check delivery coordination",
                "Verify cross-realm communication",
                "Retry with exponential backoff",
                "Use simplified delivery"
            ],
            "EXPERIENCE_MANAGER_ERROR": [
                "Check experience management",
                "Verify UI state management",
                "Retry experience operations",
                "Use basic experience mode"
            ],
            "BUSINESS_LOGIC_ERROR": [
                "Check business rules",
                "Verify business context",
                "Retry business operation",
                "Use simplified business logic"
            ],
            "PILLAR_COORDINATION_ERROR": [
                "Check pillar communication",
                "Verify pillar health",
                "Escalate to pillar administrators",
                "Use emergency coordination mode"
            ],
            "API_GATEWAY_ERROR": [
                "Check API gateway health",
                "Verify routing configuration",
                "Retry with backoff",
                "Use direct service communication"
            ],
            "FRONTEND_INTEGRATION_ERROR": [
                "Check frontend connectivity",
                "Verify API endpoints",
                "Retry integration",
                "Use offline mode"
            ]
        })
    
    def handle_content_pillar_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Content Pillar Service errors."""
        # Add Content Pillar-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "content_pillar",
            "content_operation": getattr(error, 'content_operation', 'unknown'),
            "file_id": getattr(error, 'file_id', 'unknown'),
            "content_type": getattr(error, 'content_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_operations_pillar_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Operations Pillar Service errors."""
        # Add Operations Pillar-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "operations_pillar",
            "operations_operation": getattr(error, 'operations_operation', 'unknown'),
            "workflow_id": getattr(error, 'workflow_id', 'unknown'),
            "operation_type": getattr(error, 'operation_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_insights_pillar_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Insights Pillar Service errors."""
        # Add Insights Pillar-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "insights_pillar",
            "insights_operation": getattr(error, 'insights_operation', 'unknown'),
            "analysis_type": getattr(error, 'analysis_type', 'unknown'),
            "data_source": getattr(error, 'data_source', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_delivery_manager_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Delivery Manager Service errors."""
        # Add Delivery Manager-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "delivery_manager",
            "delivery_operation": getattr(error, 'delivery_operation', 'unknown'),
            "delivery_type": getattr(error, 'delivery_type', 'unknown'),
            "target_realm": getattr(error, 'target_realm', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_experience_manager_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Experience Manager Service errors."""
        # Add Experience Manager-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "experience_manager",
            "experience_operation": getattr(error, 'experience_operation', 'unknown'),
            "ui_component": getattr(error, 'ui_component', 'unknown'),
            "user_action": getattr(error, 'user_action', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_business_logic_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle business logic errors."""
        # Add business logic-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "business_logic",
            "business_rule": getattr(error, 'business_rule', 'unknown'),
            "business_context": getattr(error, 'business_context', 'unknown'),
            "validation_type": getattr(error, 'validation_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_pillar_coordination_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle pillar coordination errors."""
        # Add pillar coordination-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "pillar_coordination",
            "coordination_operation": getattr(error, 'coordination_operation', 'unknown'),
            "involved_pillars": getattr(error, 'involved_pillars', []),
            "coordination_type": getattr(error, 'coordination_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_api_gateway_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle API Gateway errors."""
        # Add API Gateway-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "api_gateway",
            "gateway_operation": getattr(error, 'gateway_operation', 'unknown'),
            "api_endpoint": getattr(error, 'api_endpoint', 'unknown'),
            "http_method": getattr(error, 'http_method', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_frontend_integration_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle frontend integration errors."""
        # Add frontend integration-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "frontend_integration",
            "integration_operation": getattr(error, 'integration_operation', 'unknown'),
            "frontend_component": getattr(error, 'frontend_component', 'unknown'),
            "api_call": getattr(error, 'api_call', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def get_business_enablement_error_summary(self) -> Dict[str, Any]:
        """Get Business Enablement-specific error summary."""
        base_summary = self.get_error_statistics()
        
        # Add Business Enablement-specific metrics
        business_enablement_metrics = {
            "content_pillar_errors": self.error_counts.get("CONTENT_PILLAR_ERROR", 0),
            "operations_pillar_errors": self.error_counts.get("OPERATIONS_PILLAR_ERROR", 0),
            "insights_pillar_errors": self.error_counts.get("INSIGHTS_PILLAR_ERROR", 0),
            "delivery_manager_errors": self.error_counts.get("DELIVERY_MANAGER_ERROR", 0),
            "experience_manager_errors": self.error_counts.get("EXPERIENCE_MANAGER_ERROR", 0),
            "business_logic_errors": self.error_counts.get("BUSINESS_LOGIC_ERROR", 0),
            "pillar_coordination_errors": self.error_counts.get("PILLAR_COORDINATION_ERROR", 0),
            "api_gateway_errors": self.error_counts.get("API_GATEWAY_ERROR", 0),
            "frontend_integration_errors": self.error_counts.get("FRONTEND_INTEGRATION_ERROR", 0)
        }
        
        base_summary["business_enablement_metrics"] = business_enablement_metrics
        return base_summary


