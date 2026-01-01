#!/usr/bin/env python3
"""
AGUI Schema Registry - Agentic Realm Business Service

Manages dynamic AGUI output schemas for agents as a business service.
Handles schema registration, validation, and component type management.

WHAT (Agentic Role): I manage AGUI output schemas for agent communication
HOW (Business Service): I orchestrate schema management and validation
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AGUIComponent:
    """AGUI Component definition."""
    type: str
    title: str
    description: Optional[str] = None
    required: bool = True
    properties: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None


@dataclass
class AGUISchema:
    """AGUI Schema definition for an agent."""
    agent_name: str
    version: str
    description: str
    components: List[AGUIComponent]
    metadata: Optional[Dict[str, Any]] = None


class AGUISchemaRegistry:
    """
    AGUI Schema Registry - Agentic Realm Business Service
    
    Manages dynamic AGUI output schemas for agents.
    Handles schema registration, validation, and component type management.
    
    This is a BUSINESS SERVICE that orchestrates schema management and validation
    for agent-to-agent communication.
    """
    
    def __init__(self, config_path: str = None, di_container=None):
        """Initialize AGUI schema registry."""
        if not di_container:
            raise ValueError("DI Container is required for AGUISchemaRegistry initialization")
        
        self.di_container = di_container
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger("AGUISchemaRegistry")
        
        self.config_path = config_path or "agentic/agui_schemas.json"
        self.schemas = {}
        self.component_types = {}
        
        # Business metrics
        self.business_metrics = {
            "total_schemas_registered": 0,
            "total_components_defined": 0,
            "schema_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Load schemas from config
        self._load_schemas()
        
        # Initialize standard component types
        self._initialize_standard_components()
        
        self.logger.info("✅ AGUI Schema Registry (Business Service) initialized")
    
    def _load_schemas(self):
        """Load schemas from configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.schemas = config.get("schemas", {})
                    self.component_types = config.get("component_types", {})
                self.logger.info(f"✅ Loaded AGUI schemas from {self.config_path}")
            else:
                self.logger.info("ℹ️ No existing AGUI schemas found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load AGUI schemas: {e}")
            self.schemas = {}
            self.component_types = {}
    
    def _initialize_standard_components(self):
        """Initialize standard AGUI component types."""
        if not self.component_types:
            self.component_types = {
                "analysis_card": {
                    "description": "Display analysis results in a card format",
                    "required_properties": ["title", "metrics"],
                    "optional_properties": ["status", "visualizations", "actions"],
                    "example": {
                        "type": "analysis_card",
                        "title": "Data Analysis Results",
                        "metrics": {"accuracy": 0.95, "confidence": 0.87},
                        "status": "completed"
                    }
                },
                "data_table": {
                    "description": "Display tabular data with sorting and filtering",
                    "required_properties": ["columns", "data"],
                    "optional_properties": ["pagination", "sorting", "filtering"],
                    "example": {
                        "type": "data_table",
                        "columns": ["Name", "Value", "Status"],
                        "data": [["Item 1", "100", "Active"]]
                    }
                },
                "visualization": {
                    "description": "Display data visualizations and charts",
                    "required_properties": ["chart_type", "data"],
                    "optional_properties": ["options", "interactive"],
                    "example": {
                        "type": "visualization",
                        "chart_type": "line_chart",
                        "data": {"x": [1, 2, 3], "y": [10, 20, 30]}
                    }
                },
                "progress_indicator": {
                    "description": "Show progress and status information",
                    "required_properties": ["status", "progress"],
                    "optional_properties": ["message", "estimated_completion"],
                    "example": {
                        "type": "progress_indicator",
                        "status": "in_progress",
                        "progress": 75,
                        "message": "Processing data..."
                    }
                },
                "action_buttons": {
                    "description": "Provide interactive action buttons",
                    "required_properties": ["buttons"],
                    "optional_properties": ["alignment", "spacing"],
                    "example": {
                        "type": "action_buttons",
                        "buttons": [
                            {"label": "Save", "action": "save", "style": "primary"},
                            {"label": "Cancel", "action": "cancel", "style": "secondary"}
                        ]
                    }
                },
                "error_display": {
                    "description": "Display error messages and warnings",
                    "required_properties": ["error_type", "message"],
                    "optional_properties": ["title", "details", "actions"],
                    "example": {
                        "type": "error_display",
                        "error_type": "warning",
                        "title": "Validation Error",
                        "message": "Please check your input data"
                    }
                }
            }
            
            self.logger.info("✅ Standard AGUI component types initialized")
    
    async def register_agent_schema(self, agent_name: str, schema: AGUISchema, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register AGUI schema for an agent.
        
        Args:
            agent_name: Name of the agent
            schema: AGUI schema definition
            user_context: User context for security validation
            
        Returns:
            Dict containing registration result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_agent_schema_start", success=True, details={"agent_name": agent_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "write"):
                        await self.record_health_metric("register_agent_schema_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("register_agent_schema_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_schema_tenant_denied", 1.0, {"agent_name": agent_name})
                            await self.log_operation_with_telemetry("register_agent_schema_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.info(f"📝 Registering AGUI schema for agent: {agent_name}")
            
            # Validate schema
            validation_result = await self.validate_schema(schema)
            if not validation_result.get("valid", False):
                await self.record_health_metric("register_agent_schema_validation_failed", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("register_agent_schema_complete", success=False)
                return {
                    "success": False,
                    "error": "Schema validation failed",
                    "validation_errors": validation_result.get("errors", [])
                }
            
            # Store schema
            self.schemas[agent_name] = asdict(schema)
            
            # Update business metrics
            self.business_metrics["total_schemas_registered"] += 1
            self.business_metrics["total_components_defined"] += len(schema.components)
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            # Record success metric
            await self.record_health_metric("register_agent_schema_success", 1.0, {"agent_name": agent_name, "components_count": len(schema.components)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agent_schema_complete", success=True, details={"agent_name": agent_name})
            
            # Save to file
            await self._save_schemas()
            
            self.logger.info(f"✅ AGUI schema registered for agent: {agent_name}")
            return {
                "success": True,
                "agent_name": agent_name,
                "schema_version": schema.version,
                "components_count": len(schema.components),
                "message": f"Schema registered for {agent_name}"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_schema", details={"agent_name": agent_name})
            self.logger.error(f"❌ Failed to register schema for {agent_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_name": agent_name
            }
    
    async def get_agent_schema(self, agent_name: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get AGUI schema for an agent.
        
        Args:
            agent_name: Name of the agent
            user_context: User context for security validation
            
        Returns:
            Dict containing agent schema or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_schema_start", success=True, details={"agent_name": agent_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "read"):
                        await self.record_health_metric("get_agent_schema_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("get_agent_schema_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_schema_tenant_denied", 1.0, {"agent_name": agent_name})
                            await self.log_operation_with_telemetry("get_agent_schema_complete", success=False)
                            return None
            
            schema = self.schemas.get(agent_name)
            if schema:
                # Record success metric
                await self.record_health_metric("get_agent_schema_success", 1.0, {"agent_name": agent_name, "found": True})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_agent_schema_complete", success=True, details={"agent_name": agent_name})
                self.logger.debug(f"✅ Retrieved schema for agent: {agent_name}")
                return schema
            else:
                # Record not found metric
                await self.record_health_metric("get_agent_schema_not_found", 1.0, {"agent_name": agent_name})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_agent_schema_complete", success=True, details={"agent_name": agent_name, "found": False})
                self.logger.warning(f"⚠️ No schema found for agent: {agent_name}")
                return None
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_schema", details={"agent_name": agent_name})
            self.logger.error(f"❌ Failed to get schema for {agent_name}: {e}")
            return None
    
    async def validate_schema(self, schema: AGUISchema, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate AGUI schema.
        
        Args:
            schema: AGUI schema to validate
            user_context: User context for security validation
            
        Returns:
            Dict containing validation result
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_schema_start", success=True, details={"agent_name": schema.agent_name if schema else "unknown"})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "read"):
                        await self.record_health_metric("validate_schema_access_denied", 1.0, {"agent_name": schema.agent_name if schema else "unknown"})
                        await self.log_operation_with_telemetry("validate_schema_complete", success=False)
                        return {"valid": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("validate_schema_tenant_denied", 1.0, {"agent_name": schema.agent_name if schema else "unknown"})
                            await self.log_operation_with_telemetry("validate_schema_complete", success=False)
                            return {"valid": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"🔍 Validating schema for agent: {schema.agent_name}")
            
            errors = []
            
            # Validate agent name
            if not schema.agent_name or not isinstance(schema.agent_name, str):
                errors.append("Agent name is required and must be a string")
            
            # Validate version
            if not schema.version or not isinstance(schema.version, str):
                errors.append("Version is required and must be a string")
            
            # Validate description
            if not schema.description or not isinstance(schema.description, str):
                errors.append("Description is required and must be a string")
            
            # Validate components
            if not schema.components or not isinstance(schema.components, list):
                errors.append("Components are required and must be a list")
            else:
                for i, component in enumerate(schema.components):
                    component_errors = await self._validate_component(component, i)
                    errors.extend(component_errors)
            
            # Update business metrics
            self.business_metrics["schema_validations"] += 1
            if errors:
                self.business_metrics["failed_validations"] += 1
            else:
                self.business_metrics["successful_validations"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "agent_name": schema.agent_name,
                "components_count": len(schema.components) if schema.components else 0
            }
            
            # Record success metric
            await self.record_health_metric("validate_schema_success", 1.0, {"valid": result["valid"], "errors_count": len(errors)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_schema_complete", success=True, details={"valid": result["valid"]})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_schema", details={"agent_name": schema.agent_name if schema else "unknown"})
            self.logger.error(f"❌ Schema validation failed: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "agent_name": schema.agent_name if schema else "unknown"
            }
    
    async def _validate_component(self, component: AGUIComponent, index: int) -> List[str]:
        """Validate individual component."""
        errors = []
        
        # Validate component type
        if not component.type or not isinstance(component.type, str):
            errors.append(f"Component {index}: Type is required and must be a string")
        elif component.type not in self.component_types:
            errors.append(f"Component {index}: Unknown component type '{component.type}'")
        
        # Validate title
        if not component.title or not isinstance(component.title, str):
            errors.append(f"Component {index}: Title is required and must be a string")
        
        # Validate required property
        if not isinstance(component.required, bool):
            errors.append(f"Component {index}: Required must be a boolean")
        
        # Validate properties if provided
        if component.properties is not None and not isinstance(component.properties, dict):
            errors.append(f"Component {index}: Properties must be a dictionary")
        
        # Validate examples if provided
        if component.examples is not None and not isinstance(component.examples, list):
            errors.append(f"Component {index}: Examples must be a list")
        
        return errors
    
    async def get_component_type_info(self, component_type: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a component type.
        
        Args:
            component_type: Type of component
            user_context: User context for security validation
            
        Returns:
            Dict containing component type information or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_component_type_info_start", success=True, details={"component_type": component_type})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "read"):
                        await self.record_health_metric("get_component_type_info_access_denied", 1.0, {"component_type": component_type})
                        await self.log_operation_with_telemetry("get_component_type_info_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_component_type_info_tenant_denied", 1.0, {"component_type": component_type})
                            await self.log_operation_with_telemetry("get_component_type_info_complete", success=False)
                            return None
            
            info = self.component_types.get(component_type)
            if info:
                # Record success metric
                await self.record_health_metric("get_component_type_info_success", 1.0, {"component_type": component_type, "found": True})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_component_type_info_complete", success=True, details={"component_type": component_type})
                self.logger.debug(f"✅ Retrieved component type info: {component_type}")
                return info
            else:
                # Record not found metric
                await self.record_health_metric("get_component_type_info_not_found", 1.0, {"component_type": component_type})
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_component_type_info_complete", success=True, details={"component_type": component_type, "found": False})
                self.logger.warning(f"⚠️ Unknown component type: {component_type}")
                return None
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_component_type_info", details={"component_type": component_type})
            self.logger.error(f"❌ Failed to get component type info for {component_type}: {e}")
            return None
    
    async def list_agent_schemas(self, user_context: Dict[str, Any] = None) -> List[str]:
        """Get list of registered agent names."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_agent_schemas_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "read"):
                        await self.record_health_metric("list_agent_schemas_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("list_agent_schemas_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("list_agent_schemas_tenant_denied", 1.0, {})
                            await self.log_operation_with_telemetry("list_agent_schemas_complete", success=False)
                            return []
            
            result = list(self.schemas.keys())
            
            # Record success metric
            await self.record_health_metric("list_agent_schemas_success", 1.0, {"count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_agent_schemas_complete", success=True, details={"count": len(result)})
            
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "list_agent_schemas")
            return []
    
    async def list_component_types(self, user_context: Dict[str, Any] = None) -> List[str]:
        """Get list of available component types."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("list_component_types_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "read"):
                        await self.record_health_metric("list_component_types_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("list_component_types_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("list_component_types_tenant_denied", 1.0, {})
                            await self.log_operation_with_telemetry("list_component_types_complete", success=False)
                            return []
            
            result = list(self.component_types.keys())
            
            # Record success metric
            await self.record_health_metric("list_component_types_success", 1.0, {"count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("list_component_types_complete", success=True, details={"count": len(result)})
            
            return result
        except Exception as e:
            await self.handle_error_with_audit(e, "list_component_types")
            return []
    
    async def _save_schemas(self):
        """Save schemas to configuration file."""
        try:
            config = {
                "schemas": self.schemas,
                "component_types": self.component_types,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.debug(f"✅ Schemas saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save schemas: {e}")
            raise
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics for AGUI schema management."""
        return self.business_metrics.copy()
    
    def get_registry_health(self) -> Dict[str, Any]:
        """Get AGUI Schema Registry health status."""
        return {
            "service_name": "AGUISchemaRegistry",
            "service_type": "business_service",
            "realm": "agentic",
            "registered_agents": len(self.schemas),
            "available_component_types": len(self.component_types),
            "business_metrics": self.get_business_metrics(),
            "config_path": self.config_path,
            "status": "healthy"
        }
