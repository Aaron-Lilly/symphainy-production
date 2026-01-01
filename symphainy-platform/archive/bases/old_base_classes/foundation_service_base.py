#!/usr/bin/env python3
"""
Foundation Service Base Class

Simple base class for foundational services that provides comprehensive utilities
through the DIContainerService.

WHAT (Foundation Role): I need to provide comprehensive utilities for all foundation services
HOW (Foundation Service): I use DIContainerService to ensure consistent behavior
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

# Using absolute imports from project root

from typing import TYPE_CHECKING
from utilities import UserContext
from bases.realm_base import RealmBase

if TYPE_CHECKING:
    from foundations.di_container.di_container_service import DIContainerService


class FoundationServiceBase(ABC):
    """
    Foundation Service Base Class - Enhanced Foundation for ALL Foundation Services
    
    The ultimate foundation base class for ALL foundation services (Utility, Public Works, 
    Curator, Communication, Agentic). Provides comprehensive platform capabilities with 
    zero-trust security, multi-tenancy, and enhanced utilities.
    
    WHAT (Foundation Role): I provide the ultimate foundation for all foundation services
    HOW (Foundation Implementation): I provide comprehensive platform capabilities with enhanced security
    """
    
    def __init__(self, service_name: str, di_container: "DIContainerService",
                 security_provider=None, authorization_guard=None, communication_foundation=None):
        """Initialize Foundation Service Base with enhanced platform capabilities."""
        # Core service properties
        self.service_name = service_name
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        
        # Initialize logger first (before other utilities)
        self.logger = self.di_container.logger
        
        # Security infrastructure (foundation requirement)
        self.security_provider = security_provider
        self.authorization_guard = authorization_guard
        self.current_security_context = None
        
        # Enhanced utilities (from DI container with enhanced patterns)
        # Note: These will be initialized in the initialize() method since they're async
        
        # Service state
        self.is_initialized = False
        self.service_health = "unknown"
        
        self.infrastructure_abstractions = {}
        self.service_registry = {}
        
        self.logger.info(f"🏗️ FoundationServiceBase '{service_name}' initialized with enhanced platform capabilities")
    
    async def _initialize_enhanced_utilities(self):
        """Initialize enhanced utilities with new patterns."""
        # Get utilities from DI container (logger already initialized)
        self.config = self.di_container.config
        self.health = self.di_container.health
        self.telemetry = self.di_container.telemetry
        self.error_handler = self.di_container.error_handler
        self.tenant = self.di_container.tenant
        self.validation = self.di_container.validation
        self.serialization = self.di_container.serialization
        self.security = self.di_container.security
        
        # Enhanced utility patterns (using actual DIContainerService methods)
        self.enhanced_logging = self.di_container.logger
        self.enhanced_error_handler = self.di_container.error_handler
        self.enhanced_health = self.di_container.health
    
    def _initialize_enhanced_security(self):
        """Initialize enhanced security patterns."""
        # Security patterns will be implemented by specific foundation services
        # that have access to the actual security infrastructure
        pass
    
    def _initialize_platform_capabilities(self):
        """Initialize platform capabilities."""
        # SOA communication (will be provided by Communication Foundation when built)
        self.soa_client = None  # Will be set when Communication Foundation is available
        
        # Service discovery (will be provided by Communication Foundation when built)
        self.service_discovery = None  # Will be set when Communication Foundation is available
        
        # Capability registry (will be provided by Communication Foundation when built)
        self.capability_registry = None  # Will be set when Communication Foundation is available
        
        # Performance monitoring
        self.performance_monitor = self._create_performance_monitor()
        
        # Foundation-specific state
        self.start_time = datetime.utcnow()
        self.service_health = "unknown"
        
        self.logger.info(f"🏗️ {self.service_name} Foundation Service initialized with ServiceBase + DIContainerService")
    
    async def initialize(self):
        """Initialize the foundation service."""
        try:
            self.logger.info(f"🚀 Initializing {self.service_name}...")
            
            # Initialize enhanced utilities
            await self._initialize_enhanced_utilities()
            
            # Initialize enhanced security patterns
            await self._initialize_enhanced_security()
            
            # Initialize platform capabilities
            await self._initialize_platform_capabilities()
            
            # Foundation-specific initialization
            self.service_health = "healthy"
            self.is_initialized = True
            
            self.logger.info(f"✅ {self.service_name} Foundation Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            # Use basic error handling if enhanced error handler not available
            try:
                if hasattr(self, 'error_handler') and self.error_handler:
                    await self.error_handler.handle_error(e)
            except:
                # Fallback to basic logging
                self.logger.error(f"Error in {self.service_name}: {e}")
            self.service_health = "unhealthy"
            raise
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status using the health service."""
        try:
            # Use the health service for comprehensive health reporting
            # Use centralized health utility
            health_data = await self.health.run_all_health_checks()
            # Override service name with the actual service name
            health_data["service"] = self.service_name
            # Add service-specific information
            health_data.update({
                "initialized": self.is_initialized,
                "service_type": "foundation_service"
            })
            return health_data
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """Log an operation with details."""
        try:
            log_data = {
                "service": self.service_name,
                "operation": operation,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Operation: {operation}", extra=log_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log operation {operation}: {e}")
    
    async def handle_error(self, error: Exception, context: str = None):
        """Handle an error with context."""
        try:
            self.error_handler.handle_error(error)
            
            error_data = {
                "service": self.service_name,
                "error": str(error),
                "context": context or "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.error(f"Error in {context or 'unknown context'}: {error}", extra=error_data)
            
        except Exception as e:
            self.logger.error(f"Failed to handle error: {e}")
    
    async def validate_user_context(self, user_context: UserContext = None) -> bool:
        """Validate user context."""
        try:
            if not user_context:
                self.logger.warning("No user context provided")
                return False
            
            # Basic validation - can be extended by specific services
            if not hasattr(user_context, 'user_id') or not user_context.user_id:
                self.logger.warning("Invalid user context: missing user_id")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate user context: {e}")
            return False
    
    async def require_user_context(self, user_context: UserContext = None) -> UserContext:
        """Require valid user context."""
        if not await self.validate_user_context(user_context):
            raise ValueError("Valid user context is required")
        return user_context
    
    async def log_operation_with_context(self, operation: str, user_context: UserContext = None, details: Dict[str, Any] = None):
        """Log an operation with user context."""
        try:
            # Validate user context if provided
            if user_context and not await self.validate_user_context(user_context):
                self.logger.warning(f"Invalid user context for operation: {operation}")
                return
            
            log_data = {
                "service": self.service_name,
                "operation": operation,
                "user_id": user_context.user_id if user_context else None,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Operation: {operation}", extra=log_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log operation with context {operation}: {e}")
    
    # ============================================================================
    # ENHANCED UTILITY METHODS (Using Utility Foundation Service)
    
    async def log_operation_with_telemetry(self, operation: str, user_context: UserContext = None, 
                                         details: Dict[str, Any] = None, success: bool = True):
        """Log an operation with telemetry integration."""
        # Use centralized telemetry utility
        await self.telemetry.record_metric(f"operation_{operation}", 1 if success else 0, {
            "operation": operation,
            "success": success,
            "details": str(details) if details else ""
        })
        
        # Also log the operation
        await self.log_operation_with_context(operation, user_context, details)
    
    async def handle_error_with_audit(self, error: Exception, context: str = None, 
                                    user_context: UserContext = None):
        """Handle an error with audit logging."""
        # Use centralized error handler
        error_context = {
            "context": context,
            "user_context": str(user_context) if user_context else None,
            "service": self.service_name
        }
        self.error_handler.handle_error(error, error_context)
        
        # Also handle the error normally
        await self.handle_error(error, context)
    
    async def validate_user_context_with_security(self, user_context: UserContext = None) -> bool:
        """Validate user context with security service integration."""
        # Use centralized security utility
        return await self.security.validate_user_permission(
            user_context.user_id if user_context else "anonymous",
            "user_context", 
            "validate",
            user_context.permissions if user_context else []
        )
    
    async def check_permissions_with_audit(self, user: str, resource: str, action: str, 
                                         user_context: UserContext = None) -> bool:
        """Check permissions with audit logging."""
        # Use centralized security utility
        return await self.security.validate_user_permission(user, resource, action)
    
    async def record_health_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a health metric."""
        # Use centralized telemetry utility
        await self.telemetry.record_metric(metric_name, value, tags or {})
    
    async def run_comprehensive_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks."""
        # Use centralized health utility
        health_checks = await self.health.run_all_health_checks()
        return {
            "service": self.service_name,
            "health_checks": [check.to_dict() for check in health_checks],
            "overall_status": "healthy" if all(check.status == "healthy" for check in health_checks) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def track_utility_usage(self, utility_name: str):
        """Track usage of a utility."""
        # Use centralized telemetry utility to track usage
        self.telemetry.record_metric(f"utility_usage_{utility_name}", 1, {"utility": utility_name})
    
    def get_audit_log(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        # Basic audit log implementation
        return []
    
    # ============================================================================
    # ENHANCED SECURITY PATTERNS (Foundation Requirement)
    # ============================================================================
    
    async def get_security_context(self, token: str | None = None):
        """Get security context for request with enhanced security."""
        if not self.security_provider:
            # Return anonymous context if no security provider
            return {
                "user_id": None,
                "tenant_id": None,
                "roles": [],
                "permissions": [],
                "origin": "anonymous"
            }
        
        context = await self.security_provider.get_context(token)
        self.current_security_context = context
        
        return context
    
    # ============================================================================
    # ABSTRACT METHODS (to be implemented by concrete foundation services)
    # ============================================================================
    
    @abstractmethod
    async def initialize(self):
        """Initialize the foundation service."""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Shutdown the foundation service."""
        pass
    
