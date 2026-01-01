#!/usr/bin/env python3
"""
Pattern Validation Service (Refactored)

Handles pattern validation and rule checking for architectural patterns
across the platform. Refactored into micro-modules for better maintainability.

WHAT (Service Role): I need to validate architectural patterns and enforce rules
HOW (Service Implementation): I coordinate micro-modules for pattern validation
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Direct library usage - no abstractions needed for standard libraries
import json
import re
import ast
import os
from pathlib import Path
from ..models import PatternDefinition
from utilities import TenantManagementUtility, UserContext

# Import micro-modules
from .micro_modules.pattern_initialization import PatternInitializationModule
from .micro_modules.pattern_validation_engine import PatternValidationEngineModule
from .micro_modules.pattern_management import PatternManagementModule
from .micro_modules.pattern_tenant_compliance import PatternTenantComplianceModule


class PatternValidationService(FoundationServiceBase):
    """
    Pattern Validation Service - Architectural pattern validation and rule enforcement
    
    Validates patterns against architectural rules and maintains pattern definitions
    for consistent platform architecture. Refactored into micro-modules.
    
    WHAT (Service Role): I need to validate architectural patterns and enforce rules
    HOW (Service Implementation): I coordinate micro-modules for pattern validation
    """
    
    def __init__(self, di_container):
        """Initialize Pattern Validation Service."""
        super().__init__("pattern_validation", di_container)
        
        # Initialize micro-modules
        self.pattern_initialization = PatternInitializationModule(self.logger)
        self.pattern_validation_engine = PatternValidationEngineModule(self.logger)
        self.pattern_management = PatternManagementModule(self.logger)
        self.pattern_tenant_compliance = PatternTenantComplianceModule(self.logger, self.authorization_guard)
        
        # Pattern registry
        self.pattern_registry: Dict[str, PatternDefinition] = {}
        
        self.logger.info("🔍 Pattern Validation Service initialized")
    
    async def initialize(self):
        """Initialize the Pattern Validation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("pattern_validation_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Pattern Validation Service...")
            
            # Initialize default patterns
            self.pattern_registry = self.pattern_initialization.initialize_default_patterns()
            
            self.logger.info("✅ Pattern Validation Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("pattern_validation_initialized", 1.0, {"service": "pattern_validation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("pattern_validation_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "pattern_validation_initialize")
            raise
    
    # ============================================================================
    # PATTERN VALIDATION
    
    async def validate_pattern(self, pattern: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate a pattern against architectural rules."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_pattern_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "pattern_validation", "read"):
                        await self.record_health_metric("validate_pattern_access_denied", 1.0, {"pattern_name": pattern.get("name", "unknown")})
                        await self.log_operation_with_telemetry("validate_pattern_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("validate_pattern_tenant_denied", 1.0, {"pattern_name": pattern.get("name", "unknown"), "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("validate_pattern_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = await self.pattern_validation_engine.validate_pattern(pattern, self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("validate_pattern_success", 1.0, {"pattern_name": pattern.get("name", "unknown")})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_pattern_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_pattern")
            raise
    
    # ============================================================================
    # PATTERN MANAGEMENT
    
    async def add_pattern(self, pattern: PatternDefinition) -> bool:
        """Add a new pattern to the registry."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("add_pattern_start", success=True)
            
            result = await self.pattern_management.add_pattern(pattern, self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("add_pattern_success", 1.0, {"pattern_name": pattern.pattern_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("add_pattern_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "add_pattern")
            raise
    
    async def remove_pattern(self, pattern_name: str) -> bool:
        """Remove a pattern from the registry."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("remove_pattern_start", success=True)
            
            result = await self.pattern_management.remove_pattern(pattern_name, self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("remove_pattern_success", 1.0, {"pattern_name": pattern_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("remove_pattern_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "remove_pattern")
            raise
    
    async def get_pattern(self, pattern_name: str, user_context: Dict[str, Any] = None) -> PatternDefinition:
        """Get a specific pattern from the registry."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_pattern_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, pattern_name, "read"):
                        await self.record_health_metric("get_pattern_access_denied", 1.0, {"pattern_name": pattern_name})
                        await self.log_operation_with_telemetry("get_pattern_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_pattern_tenant_denied", 1.0, {"pattern_name": pattern_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_pattern_complete", success=False)
                            return None
            
            result = await self.pattern_management.get_pattern(pattern_name, self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("get_pattern_success", 1.0, {"pattern_name": pattern_name, "found": result is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_pattern_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_pattern")
            raise
    
    async def list_patterns(self, pattern_type: str = None) -> List[PatternDefinition]:
        """List all patterns, optionally filtered by type."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_patterns_start", success=True)
            
            result = await self.pattern_management.list_patterns(pattern_type, self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("list_patterns_success", 1.0, {"pattern_type": pattern_type, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_patterns_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "list_patterns")
            raise
    
    async def get_pattern_status(self) -> Dict[str, Any]:
        """Get pattern registry status and statistics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_pattern_status_start", success=True)
            
            result = await self.pattern_management.get_pattern_status(self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("get_pattern_status_success", 1.0, {})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_pattern_status_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_pattern_status")
            raise
    
    # ============================================================================
    # TENANT COMPLIANCE
    
    async def check_tenant_compliance(self, tenant_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Check tenant compliance with architectural patterns."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("check_tenant_compliance_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    # Convert UserContext to dict for check_permissions
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": tenant_id,
                        "roles": getattr(user_context, "roles", []),
                        "permissions": getattr(user_context, "permissions", [])
                    }
                    if not await security.check_permissions(user_context_dict, tenant_id, "read"):
                        await self.record_health_metric("check_tenant_compliance_access_denied", 1.0, {"tenant_id": tenant_id})
                        await self.log_operation_with_telemetry("check_tenant_compliance_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            tenant = self.get_tenant()
            if tenant:
                if not await tenant.validate_tenant_access(tenant_id):
                    await self.record_health_metric("check_tenant_compliance_tenant_denied", 1.0, {"tenant_id": tenant_id})
                    await self.log_operation_with_telemetry("check_tenant_compliance_complete", success=False)
                    return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = await self.pattern_tenant_compliance.check_tenant_compliance(tenant_id, user_context, self.pattern_registry)
            
            # Record health metric
            await self.record_health_metric("check_tenant_compliance_success", 1.0, {"tenant_id": tenant_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("check_tenant_compliance_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "check_tenant_compliance")
            raise

    async def shutdown(self):
        """Shutdown the Pattern Validation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("pattern_validation_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Pattern Validation Service...")
            
            # Clear pattern registry
            self.pattern_registry.clear()
            
            self.logger.info("✅ Pattern Validation Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("pattern_validation_shutdown", 1.0, {"service": "pattern_validation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("pattern_validation_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "pattern_validation_shutdown")
            self.logger.error(f"❌ Error during Pattern Validation Service shutdown: {e}")
