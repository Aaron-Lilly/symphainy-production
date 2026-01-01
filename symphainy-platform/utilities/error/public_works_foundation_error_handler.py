#!/usr/bin/env python3
"""
Public Works Foundation Error Handler

Realm-specific error handler for Public Works Foundation services.
Handles errors from infrastructure abstractions, adapters, and composition services.

WHAT (Utility Role): I provide error handling for Public Works Foundation realm
HOW (Utility Implementation): I handle infrastructure abstraction errors with appropriate recovery strategies
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .realm_error_handler_base import RealmErrorHandlerBase, ErrorContext, ErrorResponse, ErrorSeverity, ErrorAction


class PublicWorksFoundationErrorHandler(RealmErrorHandlerBase):
    """
    Error handler for Public Works Foundation realm.
    
    Handles errors from:
    - Infrastructure adapters (ArangoDB, Supabase, GCS, etc.)
    - Abstraction contracts and protocols
    - Infrastructure abstractions
    - Composition services
    - Infrastructure registry
    - Public Works Foundation Service
    """
    
    def __init__(self, service_name: str = "public_works_foundation"):
        """Initialize Public Works Foundation error handler."""
        super().__init__("public_works_foundation", service_name)
        
        # Public Works-specific error patterns
        self._initialize_public_works_patterns()
        
        self.logger.info(f"✅ Public Works Foundation error handler initialized for {service_name}")
    
    def _initialize_public_works_patterns(self):
        """Initialize Public Works-specific error patterns."""
        # Override common errors with Public Works-specific patterns
        self.realm_error_patterns["common_errors"].update({
            "ADAPTER_CONNECTION_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Infrastructure adapter connection failed - retrying"
            },
            "ADAPTER_OPERATION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Infrastructure operation failed - retrying"
            },
            "ABSTRACTION_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.FALLBACK,
                "user_message": "Infrastructure abstraction failed - using fallback"
            },
            "COMPOSITION_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Service composition failed - retrying"
            },
            "REGISTRY_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.ESCALATE,
                "user_message": "Service registry error - system may be unstable"
            },
            "ARANGO_DB_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "ArangoDB operation failed - retrying"
            },
            "SUPABASE_ERROR": {
                "severity": ErrorSeverity.HIGH,
                "action": ErrorAction.RETRY_WITH_BACKOFF,
                "user_message": "Supabase operation failed - retrying"
            },
            "GCS_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Google Cloud Storage operation failed - retrying"
            },
            "PROTOCOL_ERROR": {
                "severity": ErrorSeverity.MEDIUM,
                "action": ErrorAction.RETRY,
                "user_message": "Protocol implementation error - retrying"
            }
        })
        
        # Add Public Works-specific recovery strategies
        self.realm_error_patterns["recovery_strategies"].update({
            "ADAPTER_CONNECTION_ERROR": [
                "Check adapter configuration",
                "Verify network connectivity",
                "Retry with exponential backoff",
                "Use alternative adapter if available"
            ],
            "ADAPTER_OPERATION_ERROR": [
                "Check operation parameters",
                "Verify data format",
                "Retry the operation",
                "Use alternative operation method"
            ],
            "ABSTRACTION_ERROR": [
                "Check abstraction implementation",
                "Verify underlying adapter",
                "Use fallback abstraction",
                "Contact system administrator"
            ],
            "COMPOSITION_ERROR": [
                "Check service dependencies",
                "Verify composition logic",
                "Retry composition",
                "Use simplified composition"
            ],
            "REGISTRY_ERROR": [
                "Check registry configuration",
                "Verify service registrations",
                "Restart registry service",
                "Contact system administrator"
            ],
            "ARANGO_DB_ERROR": [
                "Check ArangoDB connection",
                "Verify database configuration",
                "Retry with backoff",
                "Use alternative database"
            ],
            "SUPABASE_ERROR": [
                "Check Supabase connection",
                "Verify API credentials",
                "Retry with backoff",
                "Use alternative storage"
            ],
            "GCS_ERROR": [
                "Check GCS credentials",
                "Verify bucket permissions",
                "Retry operation",
                "Use alternative storage"
            ],
            "PROTOCOL_ERROR": [
                "Check protocol implementation",
                "Verify interface compliance",
                "Retry operation",
                "Use alternative protocol"
            ]
        })
    
    def handle_adapter_error(self, error: Exception, context: ErrorContext, adapter_type: str) -> ErrorResponse:
        """Handle adapter-specific errors."""
        # Add adapter-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "adapter",
            "adapter_type": adapter_type,
            "adapter_operation": getattr(error, 'operation', 'unknown'),
            "adapter_endpoint": getattr(error, 'endpoint', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_abstraction_error(self, error: Exception, context: ErrorContext, abstraction_type: str) -> ErrorResponse:
        """Handle abstraction-specific errors."""
        # Add abstraction-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "abstraction",
            "abstraction_type": abstraction_type,
            "abstraction_operation": getattr(error, 'operation', 'unknown'),
            "underlying_adapter": getattr(error, 'underlying_adapter', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_composition_error(self, error: Exception, context: ErrorContext, composition_type: str) -> ErrorResponse:
        """Handle composition-specific errors."""
        # Add composition-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "composition",
            "composition_type": composition_type,
            "composition_operation": getattr(error, 'operation', 'unknown'),
            "involved_services": getattr(error, 'involved_services', [])
        })
        
        return self.handle_error(error, context)
    
    def handle_registry_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle registry-specific errors."""
        # Add registry-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "registry",
            "registry_operation": getattr(error, 'operation', 'unknown'),
            "service_name": getattr(error, 'service_name', 'unknown'),
            "registry_type": getattr(error, 'registry_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_arango_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle ArangoDB-specific errors."""
        # Add ArangoDB-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "arango_db",
            "database_name": getattr(error, 'database_name', 'unknown'),
            "collection_name": getattr(error, 'collection_name', 'unknown'),
            "query_type": getattr(error, 'query_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_supabase_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Supabase-specific errors."""
        # Add Supabase-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "supabase",
            "table_name": getattr(error, 'table_name', 'unknown'),
            "operation_type": getattr(error, 'operation_type', 'unknown'),
            "api_endpoint": getattr(error, 'api_endpoint', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_gcs_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle Google Cloud Storage-specific errors."""
        # Add GCS-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "gcs",
            "bucket_name": getattr(error, 'bucket_name', 'unknown'),
            "object_name": getattr(error, 'object_name', 'unknown'),
            "operation_type": getattr(error, 'operation_type', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def handle_protocol_error(self, error: Exception, context: ErrorContext, protocol_type: str) -> ErrorResponse:
        """Handle protocol-specific errors."""
        # Add protocol-specific context
        context.additional_context = context.additional_context or {}
        context.additional_context.update({
            "error_category": "protocol",
            "protocol_type": protocol_type,
            "protocol_operation": getattr(error, 'operation', 'unknown'),
            "interface_name": getattr(error, 'interface_name', 'unknown')
        })
        
        return self.handle_error(error, context)
    
    def get_public_works_error_summary(self) -> Dict[str, Any]:
        """Get Public Works-specific error summary."""
        base_summary = self.get_error_statistics()
        
        # Add Public Works-specific metrics
        public_works_metrics = {
            "adapter_errors": sum([
                self.error_counts.get("ADAPTER_CONNECTION_ERROR", 0),
                self.error_counts.get("ADAPTER_OPERATION_ERROR", 0)
            ]),
            "abstraction_errors": self.error_counts.get("ABSTRACTION_ERROR", 0),
            "composition_errors": self.error_counts.get("COMPOSITION_ERROR", 0),
            "registry_errors": self.error_counts.get("REGISTRY_ERROR", 0),
            "arango_errors": self.error_counts.get("ARANGO_DB_ERROR", 0),
            "supabase_errors": self.error_counts.get("SUPABASE_ERROR", 0),
            "gcs_errors": self.error_counts.get("GCS_ERROR", 0),
            "protocol_errors": self.error_counts.get("PROTOCOL_ERROR", 0)
        }
        
        base_summary["public_works_metrics"] = public_works_metrics
        return base_summary


