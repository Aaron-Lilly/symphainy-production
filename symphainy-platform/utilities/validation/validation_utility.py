"""
Validation Utility

Platform-specific validation utility for Smart City services.
Handles common validation patterns used across the platform.

WHAT (Utility Role): I provide standardized validation for platform operations
HOW (Utility Implementation): I validate inputs, business rules, and data integrity
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class ValidationUtility:
    """
    Platform-specific validation utility for Smart City services.
    
    Provides common validation patterns used across the platform including:
    - Input parameter validation
    - Business rule validation
    - Multi-tenant context validation
    - Connection health validation
    - Data existence validation
    """
    
    def __init__(self, service_name: str):
        """Initialize validation utility."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"ValidationUtility-{service_name}")
        
        self.logger.info(f"Validation utility initialized for {service_name}")
    
    # ============================================================================
    # INPUT VALIDATION
    # ============================================================================
    
    def validate_required_params(self, params: Dict[str, Any], required_keys: List[str]) -> ValidationResult:
        """Validate that required parameters are present and not None."""
        result = ValidationResult(True)
        
        for key in required_keys:
            if key not in params:
                result.add_error(f"Missing required parameter: {key}")
            elif params[key] is None:
                result.add_error(f"Required parameter cannot be None: {key}")
            elif isinstance(params[key], str) and not params[key].strip():
                result.add_error(f"Required parameter cannot be empty: {key}")
        
        return result
    
    def validate_param_types(self, params: Dict[str, Any], type_map: Dict[str, type]) -> ValidationResult:
        """Validate parameter types."""
        result = ValidationResult(True)
        
        for key, expected_type in type_map.items():
            if key in params and params[key] is not None:
                if not isinstance(params[key], expected_type):
                    result.add_error(f"Parameter '{key}' must be of type {expected_type.__name__}, got {type(params[key]).__name__}")
        
        return result
    
    def validate_enum_value(self, value: Any, enum_class: type, param_name: str) -> ValidationResult:
        """Validate that a value is a valid enum value."""
        result = ValidationResult(True)
        
        if value is None:
            result.add_error(f"Parameter '{param_name}' cannot be None")
        elif hasattr(enum_class, '__iter__') and not isinstance(enum_class, type):
            # Handle list of valid values
            if value not in enum_class:
                result.add_error(f"Parameter '{param_name}' must be one of {enum_class}, got '{value}'")
        elif not isinstance(value, enum_class):
            # Try to match by value for enum classes
            valid_values = [e.value for e in enum_class]
            if value not in valid_values:
                result.add_error(f"Parameter '{param_name}' must be one of {valid_values}, got '{value}'")
        
        return result
    
    # ============================================================================
    # BUSINESS RULE VALIDATION
    # ============================================================================
    
    def validate_tenant_access(self, tenant_id: Optional[str], user_context: Dict[str, Any]) -> ValidationResult:
        """Validate tenant access for multi-tenant operations."""
        result = ValidationResult(True)
        
        if not tenant_id:
            result.add_error("Tenant ID is required for multi-tenant operations")
            return result
        
        if not user_context:
            result.add_error("User context is required for tenant validation")
            return result
        
        user_tenant_id = user_context.get("tenant_id")
        if user_tenant_id and user_tenant_id != tenant_id:
            result.add_error(f"User tenant '{user_tenant_id}' does not match requested tenant '{tenant_id}'")
        
        return result
    
    def validate_permissions(self, user_context: Dict[str, Any], required_permissions: List[str]) -> ValidationResult:
        """Validate user permissions."""
        result = ValidationResult(True)
        
        if not user_context:
            result.add_error("User context is required for permission validation")
            return result
        
        user_permissions = user_context.get("permissions", [])
        for permission in required_permissions:
            if permission not in user_permissions:
                result.add_error(f"User lacks required permission: {permission}")
        
        return result
    
    def validate_business_rule(self, rule_name: str, data: Dict[str, Any], rule_func: callable) -> ValidationResult:
        """Validate a custom business rule."""
        result = ValidationResult(True)
        
        try:
            rule_result = rule_func(data)
            if not rule_result:
                result.add_error(f"Business rule validation failed: {rule_name}")
        except Exception as e:
            result.add_error(f"Business rule validation error for '{rule_name}': {str(e)}")
        
        return result
    
    # ============================================================================
    # DATA VALIDATION
    # ============================================================================
    
    def validate_data_exists(self, data: Any, data_name: str) -> ValidationResult:
        """Validate that data exists (not None, not empty)."""
        result = ValidationResult(True)
        
        if data is None:
            result.add_error(f"{data_name} is required but was None")
        elif isinstance(data, (list, dict, str)) and not data:
            result.add_error(f"{data_name} is required but was empty")
        
        return result
    
    def validate_success_response(self, response: Dict[str, Any], operation_name: str) -> ValidationResult:
        """Validate that a service response indicates success."""
        result = ValidationResult(True)
        
        if not response:
            result.add_error(f"{operation_name} returned no response")
        elif not response.get("success", False):
            error_msg = response.get("error", "Unknown error")
            result.add_error(f"{operation_name} failed: {error_msg}")
        
        return result
    
    def validate_connection_result(self, connection_result: Any, service_name: str) -> ValidationResult:
        """Validate connection result for infrastructure services."""
        result = ValidationResult(True)
        
        if not connection_result:
            result.add_error(f"Connection to {service_name} failed")
        elif isinstance(connection_result, dict) and not connection_result.get("success", True):
            error_msg = connection_result.get("error", "Unknown connection error")
            result.add_error(f"Connection to {service_name} failed: {error_msg}")
        
        return result
    
    # ============================================================================
    # COMPOSITE VALIDATION
    # ============================================================================
    
    def validate_service_operation(self, 
                                 params: Dict[str, Any], 
                                 required_params: List[str],
                                 user_context: Optional[Dict[str, Any]] = None,
                                 required_permissions: List[str] = None,
                                 tenant_id: Optional[str] = None) -> ValidationResult:
        """Comprehensive validation for service operations."""
        result = ValidationResult(True)
        
        # Validate required parameters
        param_result = self.validate_required_params(params, required_params)
        if not param_result.is_valid:
            result.errors.extend(param_result.errors)
            result.is_valid = False
        
        # Validate user context if provided
        if user_context:
            if tenant_id:
                tenant_result = self.validate_tenant_access(tenant_id, user_context)
                if not tenant_result.is_valid:
                    result.errors.extend(tenant_result.errors)
                    result.is_valid = False
            
            if required_permissions:
                perm_result = self.validate_permissions(user_context, required_permissions)
                if not perm_result.is_valid:
                    result.errors.extend(perm_result.errors)
                    result.is_valid = False
        
        return result
    
    def validate_mcp_tool_execution(self, 
                                  tool_name: str,
                                  parameters: Dict[str, Any],
                                  user_context: Optional[Dict[str, Any]] = None,
                                  requires_tenant: bool = True) -> ValidationResult:
        """Validate MCP tool execution parameters."""
        result = ValidationResult(True)
        
        # Validate tool name
        if not tool_name or not isinstance(tool_name, str):
            result.add_error("Tool name is required and must be a string")
        
        # Validate parameters
        if not isinstance(parameters, dict):
            result.add_error("Parameters must be a dictionary")
        
        # Validate tenant context if required
        if requires_tenant and user_context:
            tenant_id = user_context.get("tenant_id")
            if not tenant_id:
                result.add_error("Tenant ID is required for this tool")
        
        return result
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def log_validation_result(self, result: ValidationResult, operation: str):
        """Log validation result."""
        if result.is_valid:
            if result.warnings:
                self.logger.warning(f"Validation passed for {operation} with {len(result.warnings)} warnings: {result.warnings}")
            else:
                self.logger.debug(f"Validation passed for {operation}")
        else:
            self.logger.error(f"Validation failed for {operation}: {result.errors}")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation utility status."""
        return {
            "service_name": self.service_name,
            "utility_type": "validation",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }

