"""
AGUI Schema Registry

Manages dynamic AGUI output schemas for agents.
Requires agents to define their output schemas as part of their implementation.
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin

# Using absolute imports from project root


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
    
    @property
    def schema_name(self) -> str:
        """Return schema_name (alias for agent_name for Curator compatibility)."""
        return self.agent_name


class AGUISchemaRegistry(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Registry for managing AGUI output schemas for agents.
    
    Provides:
    - Schema registration and validation
    - Component type management
    - Schema versioning
    - Agent-specific schema lookup
    """
    
    def __init__(self, config_path: str = None, di_container=None):
        """Initialize AGUI schema registry."""
        if not di_container:
            raise ValueError("DI Container is required for AGUISchemaRegistry initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.di_container = di_container
        self.service_name = "agui_schema_registry"
        
        self.config_path = config_path or "agentic/agui_schemas.json"
        self.schemas = {}
        self.component_types = {}
        
        # Load schemas from config
        self._load_schemas()
        
        # Initialize standard component types
        self._initialize_standard_components()
        
        self.logger.info("AGUI Schema Registry initialized")
    
    def _load_schemas(self):
        """Load schemas from configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.schemas = config.get("schemas", {})
                    self.component_types = config.get("component_types", {})
                self.logger.info(f"Loaded AGUI schemas from {self.config_path}")
            else:
                self.logger.info("No existing AGUI schemas found, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Failed to load AGUI schemas: {e}")
            self.schemas = {}
            self.component_types = {}
    
    def _initialize_standard_components(self):
        """Initialize standard AGUI component types."""
        if not self.component_types:
            self.component_types = {
                "info_card": {
                    "description": "Display informational content in a card format",
                    "required_properties": ["title", "content"],
                    "optional_properties": ["status", "icon", "actions"],
                    "example": {
                        "type": "info_card",
                        "title": "Analysis Complete",
                        "content": "Data analysis has been completed successfully",
                        "status": "success"
                    }
                },
                "analysis_card": {
                    "description": "Display analysis results with data and visualizations",
                    "required_properties": ["title", "data"],
                    "optional_properties": ["status", "visualization", "insights", "actions"],
                    "example": {
                        "type": "analysis_card",
                        "title": "Sales Analysis",
                        "data": {"revenue": 100000, "growth": 15.5},
                        "status": "completed"
                    }
                },
                "workflow_card": {
                    "description": "Display workflow status and progress",
                    "required_properties": ["title", "workflow_id"],
                    "optional_properties": ["status", "progress", "steps", "actions"],
                    "example": {
                        "type": "workflow_card",
                        "title": "Data Processing Workflow",
                        "workflow_id": "wf_123",
                        "status": "running",
                        "progress": 75
                    }
                },
                "status_card": {
                    "description": "Display system or component status",
                    "required_properties": ["title", "status"],
                    "optional_properties": ["details", "metrics", "health_score"],
                    "example": {
                        "type": "status_card",
                        "title": "System Health",
                        "status": "healthy",
                        "health_score": 95
                    }
                },
                "message_card": {
                    "description": "Display messages and communications",
                    "required_properties": ["title", "message"],
                    "optional_properties": ["sender", "recipient", "timestamp", "priority"],
                    "example": {
                        "type": "message_card",
                        "title": "Notification",
                        "message": "Analysis completed successfully",
                        "sender": "DataAnalyst",
                        "timestamp": "2024-12-30T10:00:00Z"
                    }
                },
                "chart_card": {
                    "description": "Display charts and visualizations",
                    "required_properties": ["title", "chart_type", "data"],
                    "optional_properties": ["options", "interactions", "export"],
                    "example": {
                        "type": "chart_card",
                        "title": "Revenue Trend",
                        "chart_type": "line",
                        "data": {"labels": ["Jan", "Feb", "Mar"], "values": [100, 120, 110]}
                    }
                },
                "table_card": {
                    "description": "Display tabular data",
                    "required_properties": ["title", "columns", "rows"],
                    "optional_properties": ["pagination", "sorting", "filtering", "actions"],
                    "example": {
                        "type": "table_card",
                        "title": "Customer Data",
                        "columns": ["Name", "Email", "Status"],
                        "rows": [["John Doe", "john@example.com", "Active"]]
                    }
                },
                "form_card": {
                    "description": "Display forms for user input",
                    "required_properties": ["title", "fields"],
                    "optional_properties": ["validation", "submit_action", "cancel_action"],
                    "example": {
                        "type": "form_card",
                        "title": "Analysis Parameters",
                        "fields": [
                            {"name": "date_range", "type": "date_range", "required": True},
                            {"name": "metrics", "type": "multi_select", "options": ["revenue", "profit"]}
                        ]
                    }
                },
                "alert_card": {
                    "description": "Display alerts and notifications",
                    "required_properties": ["title", "message", "alert_type"],
                    "optional_properties": ["dismissible", "actions", "expiry"],
                    "example": {
                        "type": "alert_card",
                        "title": "Data Quality Issue",
                        "message": "Missing data detected in customer records",
                        "alert_type": "warning"
                    }
                },
                "generic_output": {
                    "description": "Generic output for unknown or custom content",
                    "required_properties": ["title", "content"],
                    "optional_properties": ["format", "metadata"],
                    "example": {
                        "type": "generic_output",
                        "title": "Custom Output",
                        "content": "Custom content here",
                        "format": "text"
                    }
                }
            }
    
    async def register_agent_schema(self, agent_name: str, schema: AGUISchema, user_context: Dict[str, Any] = None) -> bool:
        """
        Register an AGUI schema for an agent.
        
        Args:
            agent_name: Name of the agent
            schema: AGUI schema definition
            user_context: User context for security and tenant validation
            
        Returns:
            True if registered successfully, False otherwise
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
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_schema_tenant_denied", 1.0, {"agent_name": agent_name})
                            await self.log_operation_with_telemetry("register_agent_schema_complete", success=False)
                            return False
            
            # Validate schema
            validation_result = await self.validate_schema(schema)
            if not validation_result["valid"]:
                await self.record_health_metric("register_agent_schema_validation_failed", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("register_agent_schema_complete", success=False)
                self.logger.error(f"Schema validation failed for {agent_name}: {validation_result['errors']}")
                return False
            
            # Register schema
            self.schemas[agent_name] = asdict(schema)
            
            # Save to file
            self._save_schemas()
            
            # Record success metric
            await self.record_health_metric("register_agent_schema_success", 1.0, {"agent_name": agent_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agent_schema_complete", success=True, details={"agent_name": agent_name})
            
            self.logger.info(f"Registered AGUI schema for agent: {agent_name}")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_schema", details={"agent_name": agent_name})
            self.logger.error(f"Failed to register schema for {agent_name}: {e}")
            return False
    
    def get_agent_schema(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get AGUI schema for an agent."""
        return self.schemas.get(agent_name)
    
    async def validate_schema(self, schema: AGUISchema) -> Dict[str, Any]:
        """
        Validate an AGUI schema.
        
        Args:
            schema: AGUI schema to validate
            
        Returns:
            Validation result with details
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_schema_start", success=True, details={"agent_name": schema.agent_name})
            
            errors = []
            
            # Check required fields
            if not schema.agent_name:
                errors.append("Agent name is required")
            if not schema.version:
                errors.append("Version is required")
            if not schema.description:
                errors.append("Description is required")
            if not schema.components:
                errors.append("At least one component is required")
            
            # Validate components
            for i, component in enumerate(schema.components):
                component_errors = self._validate_component(component, i)
                errors.extend(component_errors)
            
            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "schema": asdict(schema) if len(errors) == 0 else None
            }
            
            # Record success metric
            await self.record_health_metric("validate_schema_success", 1.0, {"valid": result["valid"], "errors_count": len(errors)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_schema_complete", success=True, details={"valid": result["valid"]})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_schema", details={"agent_name": schema.agent_name if schema else "unknown"})
            return {
                "valid": False,
                "error": f"Validation failed: {e}"
            }
    
    def _validate_component(self, component: AGUIComponent, index: int) -> List[str]:
        """Validate a single AGUI component."""
        errors = []
        
        # Check required fields
        if not component.type:
            errors.append(f"Component {index}: Type is required")
        if not component.title:
            errors.append(f"Component {index}: Title is required")
        
        # Check if component type is known
        if component.type and component.type not in self.component_types:
            errors.append(f"Component {index}: Unknown component type '{component.type}'")
        
        # Validate component properties against type definition
        if component.type in self.component_types:
            type_def = self.component_types[component.type]
            required_props = type_def.get("required_properties", [])
            
            # Check required properties - they can be direct attributes or in properties dict
            for prop in required_props:
                if not hasattr(component, prop) and (not component.properties or prop not in component.properties):
                    errors.append(f"Component {index}: Missing required property '{prop}' for type '{component.type}'")
        
        return errors
    
    def get_component_types(self) -> Dict[str, Any]:
        """Get available component types."""
        return self.component_types
    
    async def register_component_type(self, type_name: str, type_definition: Dict[str, Any], user_context: Dict[str, Any] = None) -> bool:
        """Register a new component type."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_component_type_start", success=True, details={"type_name": type_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "write"):
                        await self.record_health_metric("register_component_type_access_denied", 1.0, {"type_name": type_name})
                        await self.log_operation_with_telemetry("register_component_type_complete", success=False)
                        return False
            
            self.component_types[type_name] = type_definition
            self._save_schemas()
            
            # Record success metric
            await self.record_health_metric("register_component_type_success", 1.0, {"type_name": type_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_component_type_complete", success=True, details={"type_name": type_name})
            
            self.logger.info(f"Registered component type: {type_name}")
            return True
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_component_type", details={"type_name": type_name})
            self.logger.error(f"Failed to register component type {type_name}: {e}")
            return False
    
    async def generate_schema_template(self, agent_name: str, capabilities: List[str], user_context: Dict[str, Any] = None) -> AGUISchema:
        """
        Generate a schema template for an agent based on its capabilities.
        
        Args:
            agent_name: Name of the agent
            capabilities: List of agent capabilities
            user_context: User context for security and tenant validation
            
        Returns:
            Generated schema template
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_schema_template_start", success=True, details={"agent_name": agent_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_schema", "read"):
                        await self.record_health_metric("generate_schema_template_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("generate_schema_template_complete", success=False)
                        raise PermissionError("Access denied")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("generate_schema_template_tenant_denied", 1.0, {"agent_name": agent_name})
                            await self.log_operation_with_telemetry("generate_schema_template_complete", success=False)
                            raise PermissionError("Tenant access denied")
            
            components = []
            
            # Add components based on capabilities
            if "data_analysis" in capabilities:
                components.append(AGUIComponent(
                type="analysis_card",
                title="Analysis Results",
                description="Display analysis results and insights",
                required=True,
                properties={
                    "data": {"type": "object", "description": "Analysis data"},
                    "insights": {"type": "array", "description": "Key insights"}
                }
            ))
            
            if "workflow" in capabilities:
                components.append(AGUIComponent(
                    type="workflow_card",
                    title="Workflow Status",
                    description="Display workflow execution status",
                    required=True,
                    properties={
                        "workflow_id": {"type": "string", "description": "Workflow identifier"},
                        "status": {"type": "string", "description": "Current status"}
                    }
                ))
            
            if "monitoring" in capabilities:
                components.append(AGUIComponent(
                    type="status_card",
                    title="System Status",
                    description="Display system health and status",
                    required=True,
                    properties={
                        "status": {"type": "string", "description": "System status"},
                        "health_score": {"type": "number", "description": "Health score"}
                    }
                ))
            
            # Always include a message card for communications
            components.append(AGUIComponent(
                type="message_card",
                title="Agent Communication",
                description="Display agent messages and notifications",
                required=True,
                properties={
                    "message": {"type": "string", "description": "Message content"},
                    "priority": {"type": "string", "description": "Message priority"}
                }
            ))
            
            result = AGUISchema(
                agent_name=agent_name,
                version="1.0",
                description=f"AGUI schema for {agent_name}",
                components=components,
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "capabilities": capabilities
                }
            )
            
            # Record success metric
            await self.record_health_metric("generate_schema_template_success", 1.0, {"agent_name": agent_name, "components_count": len(components)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_schema_template_complete", success=True, 
                                                   details={"agent_name": agent_name, "components_count": len(components)})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_schema_template", details={"agent_name": agent_name})
            self.logger.error(f"Failed to generate schema template for {agent_name}: {e}")
            raise
    
    def _save_schemas(self):
        """Save schemas to configuration file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = {
                "schemas": self.schemas,
                "component_types": self.component_types,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"AGUI schemas saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save AGUI schemas: {e}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        try:
            total_schemas = len(self.schemas)
            total_component_types = len(self.component_types)
            
            # Count components by type
            component_counts = {}
            for schema in self.schemas.values():
                for component in schema.get("components", []):
                    comp_type = component.get("type", "unknown")
                    component_counts[comp_type] = component_counts.get(comp_type, 0) + 1
            
            return {
                "total_schemas": total_schemas,
                "total_component_types": total_component_types,
                "component_counts": component_counts,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}


# Global AGUI schema registry instance (lazy initialization)
_agui_schema_registry: Optional[AGUISchemaRegistry] = None


def get_agui_schema_registry(di_container=None) -> Optional[AGUISchemaRegistry]:
    """
    Get the global AGUI schema registry instance.
    
    Note: This is a legacy function. The registry should be obtained from
    AgenticFoundationService instead. This function is kept for backward compatibility.
    
    Args:
        di_container: DI Container (required for first call)
    
    Returns:
        AGUISchemaRegistry instance or None if di_container not provided
    """
    global _agui_schema_registry
    
    if _agui_schema_registry is None:
        if not di_container:
            # Return None instead of raising - let the caller handle it
            return None
        _agui_schema_registry = AGUISchemaRegistry(di_container=di_container)
    
    return _agui_schema_registry

