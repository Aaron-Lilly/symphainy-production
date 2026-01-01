#!/usr/bin/env python3
"""
Config Validator Builder - SDK Builder for Config Validator

Creates Config Validator instances for validating tenant-specific configurations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class ConfigValidator:
    """
    Config Validator Instance - Validates tenant-specific configurations.
    
    Validates:
    - Schema validation for configs
    - Tenant isolation validation
    - Dependency validation (configs that reference other configs)
    - Business rule validation
    """
    
    def __init__(
        self,
        tenant_id: str,
        config: Dict[str, Any],
        di_container: Any
    ):
        """Initialize Config Validator instance."""
        self.tenant_id = tenant_id
        self.config = config
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigValidator initialization")
        self.logger = di_container.get_logger(f"ConfigValidator.{tenant_id}")
        
        # Validation schemas (can be loaded from config or defaults)
        self.validation_schemas: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """Initialize Config Validator."""
        try:
            self.logger.info(f"🔧 Initializing Config Validator for tenant: {self.tenant_id}")
            
            # Load validation schemas (if available)
            # For now, use default schemas
            self._load_default_schemas()
            
            self.logger.info(f"✅ Config Validator initialized for tenant: {self.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Config Validator initialization failed: {e}")
            raise
    
    def _load_default_schemas(self):
        """Load default validation schemas."""
        # Default schemas for common config types
        self.validation_schemas = {
            "domain_models": {
                "required_fields": ["name", "fields"],
                "field_types": ["string", "number", "boolean", "date", "object", "array"]
            },
            "workflows": {
                "required_fields": ["name", "steps"],
                "step_types": ["action", "decision", "parallel", "wait"]
            },
            "dashboards": {
                "required_fields": ["name", "widgets"],
                "widget_types": ["chart", "table", "metric", "text"]
            },
            "ingestion_endpoints": {
                "required_fields": ["name", "endpoint", "method"],
                "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"]
            },
            "user_management": {
                "required_fields": ["roles", "permissions"],
                "role_types": ["owner", "admin", "member", "viewer"]
            },
            "ai_agent_personas": {
                "required_fields": ["name", "capabilities"],
                "capability_types": ["analysis", "recommendation", "automation"]
            }
        }
    
    async def validate_config(
        self,
        config_type: str,
        config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate configuration.
        
        Args:
            config_type: Config type (e.g., "domain_models", "workflows")
            config: Configuration data to validate
            user_context: Optional user context for security validation
        
        Returns:
            Validation result with success, issues, and recommendations
        """
        try:
            self.logger.info(f"🔍 Validating config for tenant: {self.tenant_id}, type: {config_type}")
            
            issues = []
            recommendations = []
            
            # 1. Schema validation
            schema_validation = self._validate_schema(config_type, config)
            issues.extend(schema_validation.get("issues", []))
            recommendations.extend(schema_validation.get("recommendations", []))
            
            # 2. Tenant isolation validation
            tenant_validation = await self._validate_tenant_isolation(config, user_context)
            issues.extend(tenant_validation.get("issues", []))
            
            # 3. Dependency validation
            dependency_validation = await self._validate_dependencies(config_type, config)
            issues.extend(dependency_validation.get("issues", []))
            recommendations.extend(dependency_validation.get("recommendations", []))
            
            # 4. Business rule validation
            business_validation = await self._validate_business_rules(config_type, config)
            issues.extend(business_validation.get("issues", []))
            recommendations.extend(business_validation.get("recommendations", []))
            
            is_valid = len(issues) == 0
            
            result = {
                "success": is_valid,
                "is_valid": is_valid,
                "config_type": config_type,
                "tenant_id": self.tenant_id,
                "issues": issues,
                "recommendations": recommendations,
                "validated_at": datetime.utcnow().isoformat()
            }
            
            if is_valid:
                self.logger.info(f"✅ Config validation passed for {config_type}")
            else:
                self.logger.warning(f"⚠️ Config validation found {len(issues)} issues for {config_type}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Config validation failed: {e}")
            return {
                "success": False,
                "is_valid": False,
                "error": str(e),
                "config_type": config_type,
                "tenant_id": self.tenant_id
            }
    
    def _validate_schema(self, config_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate config against schema."""
        issues = []
        recommendations = []
        
        schema = self.validation_schemas.get(config_type, {})
        required_fields = schema.get("required_fields", [])
        
        # Check required fields
        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")
                recommendations.append(f"Add '{field}' field to config")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _validate_tenant_isolation(
        self,
        config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate tenant isolation."""
        issues = []
        
        # Check if config contains tenant_id and matches
        config_tenant_id = config.get("tenant_id")
        if config_tenant_id and config_tenant_id != self.tenant_id:
            issues.append(f"Tenant ID mismatch: config has {config_tenant_id}, expected {self.tenant_id}")
        
        # Check user context tenant matches
        if user_context:
            user_tenant_id = user_context.get("tenant_id")
            if user_tenant_id and user_tenant_id != self.tenant_id:
                issues.append(f"User tenant mismatch: user has {user_tenant_id}, expected {self.tenant_id}")
        
        return {
            "issues": issues
        }
    
    async def _validate_dependencies(
        self,
        config_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate config dependencies."""
        issues = []
        recommendations = []
        
        # Check for references to other configs
        # For example, workflows might reference domain_models
        if config_type == "workflows":
            # Check if referenced domain models exist
            steps = config.get("steps", [])
            for step in steps:
                if "domain_model" in step:
                    domain_model_name = step.get("domain_model")
                    # Would check if domain_model exists in tenant configs
                    # For now, just log
                    self.logger.debug(f"Workflow references domain model: {domain_model_name}")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _validate_business_rules(
        self,
        config_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate business rules."""
        issues = []
        recommendations = []
        
        # Business rule validations
        if config_type == "workflows":
            # Check workflow has at least one step
            steps = config.get("steps", [])
            if not steps:
                issues.append("Workflow must have at least one step")
                recommendations.append("Add at least one step to the workflow")
        
        elif config_type == "dashboards":
            # Check dashboard has at least one widget
            widgets = config.get("widgets", [])
            if not widgets:
                issues.append("Dashboard must have at least one widget")
                recommendations.append("Add at least one widget to the dashboard")
        
        elif config_type == "domain_models":
            # Check domain model has at least one field
            fields = config.get("fields", [])
            if not fields:
                issues.append("Domain model must have at least one field")
                recommendations.append("Add at least one field to the domain model")
        
        return {
            "issues": issues,
            "recommendations": recommendations
        }


class ConfigValidatorBuilder:
    """
    Config Validator Builder - SDK Builder for Config Validator
    
    Creates Config Validator instances for validating tenant-specific configurations.
    """
    
    def __init__(
        self,
        tenant_id: str,
        config: Dict[str, Any],
        di_container: Any
    ):
        """
        Initialize Config Validator Builder.
        
        Args:
            tenant_id: Tenant identifier
            config: Optional validator configuration
            di_container: DI Container
        """
        self.tenant_id = tenant_id
        self.config = config or {}
        self.di_container = di_container
        
        if not di_container:
            raise ValueError("DI Container is required for ConfigValidatorBuilder initialization")
        self.logger = di_container.get_logger(f"ConfigValidatorBuilder.{tenant_id}")
        
        # Validator instance (will be created in initialize)
        self.validator: Optional[ConfigValidator] = None
    
    async def initialize(self) -> bool:
        """
        Initialize Config Validator instance.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            self.logger.info(f"🔧 Initializing Config Validator for tenant: {self.tenant_id}")
            
            # Create ConfigValidator instance
            self.validator = ConfigValidator(
                tenant_id=self.tenant_id,
                config=self.config,
                di_container=self.di_container
            )
            
            # Initialize the validator
            success = await self.validator.initialize()
            
            if success:
                self.logger.info(f"✅ Config Validator initialized for tenant: {self.tenant_id}")
            else:
                self.logger.error(f"❌ Config Validator initialization failed for tenant: {self.tenant_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Config Validator Builder initialization failed: {e}")
            raise
    
    def get_validator(self) -> Optional[ConfigValidator]:
        """Get the initialized Config Validator instance."""
        return self.validator










