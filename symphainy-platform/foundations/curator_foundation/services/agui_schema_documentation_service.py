#!/usr/bin/env python3
"""
AGUI Schema Documentation Service

Provides AGUI schema documentation generation for the Curator Foundation.
Integrates with AGUI Schema Registry to generate comprehensive documentation for agent UI schemas.

WHAT (Curator Role): I provide AGUI schema documentation generation
HOW (AGUI Schema Documentation Service): I integrate with AGUI Schema Registry and generate comprehensive documentation
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase


@dataclass
class AGUISchemaDocumentation:
    """AGUI schema documentation definition."""
    agent_name: str
    schema_version: str
    documentation_type: str  # api, user_guide, developer_guide, reference
    title: str
    description: str
    components: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    generated_at: str
    generated_by: str


@dataclass
class AGUIDocumentationReport:
    """AGUI documentation report for Curator."""
    total_agents: int
    documented_agents: int
    undocumented_agents: int
    documentation_coverage: float
    documentation_types: Dict[str, int]
    last_updated: str
    quality_score: float


class AGUISchemaDocumentationService(FoundationServiceBase):
    """
    AGUI Schema Documentation Service for Curator Foundation.
    
    Provides AGUI schema documentation generation.
    Integrates with AGUI Schema Registry to generate comprehensive documentation for agent UI schemas.
    
    Features:
    - Automatic documentation generation from AGUI schemas
    - Multiple documentation formats (API, User Guide, Developer Guide, Reference)
    - Component documentation with examples
    - Schema validation and quality assessment
    - Integration with AGUI Schema Registry
    - Documentation versioning and updates
    - Cross-agent documentation analysis
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize AGUI Schema Documentation Service."""
        super().__init__("agui_schema_documentation", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Documentation storage
        self.agent_documentation: Dict[str, List[AGUISchemaDocumentation]] = {}  # agent_name -> docs
        self.documentation_index: Dict[str, str] = {}  # doc_id -> agent_name
        self.documentation_quality: Dict[str, Dict[str, Any]] = {}  # agent_name -> quality metrics
        
        # Integration points
        self.agui_schema_registry = None
        
        # Documentation templates
        self.documentation_templates = {
            "api": self._create_api_documentation_template(),
            "user_guide": self._create_user_guide_template(),
            "developer_guide": self._create_developer_guide_template(),
            "reference": self._create_reference_template()
        }
        
        self.logger.info("AGUI Schema Documentation Service initialized")
    
    async def initialize(self):
        """Initialize the AGUI Schema Documentation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agui_schema_documentation_initialize_start", success=True)
            
            self.logger.info("🚀 Initializing AGUI Schema Documentation Service...")
            
            # Load existing documentation from storage
            await self._load_documentation_from_storage()
            
            # Initialize integration points
            await self._initialize_integrations()
            
            # Generate documentation for existing schemas
            await self._generate_documentation_for_existing_schemas()
            
            self.logger.info("✅ AGUI Schema Documentation Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("agui_schema_documentation_initialized", 1.0, {"service": "agui_schema_documentation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agui_schema_documentation_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agui_schema_documentation_initialize")
            self.logger.error(f"❌ Failed to initialize AGUI Schema Documentation Service: {e}")
            raise
    
    async def _initialize_integrations(self):
        """Initialize integrations with other registries."""
        try:
            # Import and initialize AGUI Schema Registry
            from foundations.agentic_foundation.agui_schema_registry import AGUISchemaRegistry
            self.agui_schema_registry = AGUISchemaRegistry()
            
            self.logger.info("✅ AGUI schema registry integration initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to initialize AGUI schema registry integration: {e}")
    
    async def _load_documentation_from_storage(self):
        """Load existing documentation from persistent storage."""
        try:
            # In a real implementation, this would load from a database
            # For now, we'll start with an empty registry
            self.logger.info("📚 Loaded documentation from storage")
            
        except Exception as e:
            self.logger.error(f"Failed to load documentation from storage: {e}")
            await self.handle_error_with_audit(e, "load_documentation_from_storage_failed")
    
    async def _generate_documentation_for_existing_schemas(self):
        """Generate documentation for existing AGUI schemas."""
        try:
            if not self.agui_schema_registry:
                return
            
            # Get all registered schemas
            all_schemas = self.agui_schema_registry.get_all_schemas()
            
            for agent_name, schema in all_schemas.items():
                # Generate documentation for each type
                for doc_type in self.documentation_templates.keys():
                    await self.generate_agent_documentation(agent_name, doc_type)
            
            self.logger.info(f"📖 Generated documentation for {len(all_schemas)} existing schemas")
            
        except Exception as e:
            self.logger.error(f"Failed to generate documentation for existing schemas: {e}")
            await self.handle_error_with_audit(e, "generate_documentation_for_existing_schemas_failed")
    
    def _create_api_documentation_template(self) -> Dict[str, Any]:
        """Create API documentation template."""
        return {
            "title_template": "{agent_name} API Documentation",
            "description_template": "API documentation for {agent_name} agent components and interactions.",
            "sections": [
                "overview",
                "components",
                "interactions",
                "examples",
                "error_handling"
            ],
            "component_template": {
                "name": "{component_name}",
                "type": "{component_type}",
                "description": "{component_description}",
                "properties": "{component_properties}",
                "examples": "{component_examples}"
            }
        }
    
    def _create_user_guide_template(self) -> Dict[str, Any]:
        """Create user guide template."""
        return {
            "title_template": "{agent_name} User Guide",
            "description_template": "User guide for interacting with {agent_name} agent.",
            "sections": [
                "getting_started",
                "basic_usage",
                "advanced_features",
                "troubleshooting",
                "faq"
            ],
            "component_template": {
                "name": "{component_name}",
                "purpose": "{component_description}",
                "how_to_use": "{usage_instructions}",
                "examples": "{component_examples}"
            }
        }
    
    def _create_developer_guide_template(self) -> Dict[str, Any]:
        """Create developer guide template."""
        return {
            "title_template": "{agent_name} Developer Guide",
            "description_template": "Developer guide for integrating with {agent_name} agent.",
            "sections": [
                "integration_overview",
                "component_specifications",
                "implementation_examples",
                "best_practices",
                "testing"
            ],
            "component_template": {
                "name": "{component_name}",
                "specification": "{component_spec}",
                "implementation": "{implementation_notes}",
                "testing": "{testing_guidelines}"
            }
        }
    
    def _create_reference_template(self) -> Dict[str, Any]:
        """Create reference documentation template."""
        return {
            "title_template": "{agent_name} Reference",
            "description_template": "Complete reference for {agent_name} agent components.",
            "sections": [
                "component_reference",
                "property_reference",
                "example_reference",
                "schema_reference"
            ],
            "component_template": {
                "name": "{component_name}",
                "full_specification": "{full_spec}",
                "all_properties": "{all_properties}",
                "validation_rules": "{validation_rules}"
            }
        }
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    async def generate_agent_documentation(self, agent_name: str, documentation_type: str, user_context: Dict[str, Any] = None) -> Optional[AGUISchemaDocumentation]:
        """
        Generate documentation for an agent's AGUI schema.
        
        Args:
            agent_name: Name of the agent
            documentation_type: Type of documentation (api, user_guide, developer_guide, reference)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            AGUISchemaDocumentation or None if generation failed
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_agent_documentation_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_name, "write"):
                        await self.record_health_metric("generate_agent_documentation_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("generate_agent_documentation_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("generate_agent_documentation_tenant_denied", 1.0, {"agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("generate_agent_documentation_complete", success=False)
                            return None
            
            if not self.agui_schema_registry:
                self.logger.error("AGUI Schema Registry not available")
                await self.record_health_metric("generate_agent_documentation_error", 1.0, {"agent_name": agent_name, "error": "registry_not_available"})
                await self.log_operation_with_telemetry("generate_agent_documentation_complete", success=False)
                return None
            
            # Get agent schema
            schema = self.agui_schema_registry.get_agent_schema(agent_name)
            if not schema:
                self.logger.warning(f"No AGUI schema found for agent {agent_name}")
                await self.record_health_metric("generate_agent_documentation_error", 1.0, {"agent_name": agent_name, "error": "schema_not_found"})
                await self.log_operation_with_telemetry("generate_agent_documentation_complete", success=False)
                return None
            
            # Get documentation template
            if documentation_type not in self.documentation_templates:
                self.logger.error(f"Unknown documentation type: {documentation_type}")
                await self.record_health_metric("generate_agent_documentation_error", 1.0, {"agent_name": agent_name, "error": "unknown_type"})
                await self.log_operation_with_telemetry("generate_agent_documentation_complete", success=False)
                return None
            
            template = self.documentation_templates[documentation_type]
            
            # Generate documentation
            documentation = await self._generate_documentation_from_schema(
                agent_name, schema, documentation_type, template
            )
            
            # Store documentation
            if agent_name not in self.agent_documentation:
                self.agent_documentation[agent_name] = []
            
            # Remove existing documentation of this type
            self.agent_documentation[agent_name] = [
                doc for doc in self.agent_documentation[agent_name] 
                if doc.documentation_type != documentation_type
            ]
            
            # Add new documentation
            self.agent_documentation[agent_name].append(documentation)
            
            # Update documentation index
            doc_id = f"{agent_name}_{documentation_type}"
            self.documentation_index[doc_id] = agent_name
            
            # Assess documentation quality
            await self._assess_documentation_quality(agent_name, documentation)
            
            self.logger.info(f"✅ Generated {documentation_type} documentation for agent {agent_name}")
            
            # Record health metric
            await self.record_health_metric("generate_agent_documentation_success", 1.0, {"agent_name": agent_name, "documentation_type": documentation_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_agent_documentation_complete", success=True)
            
            return documentation
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "generate_agent_documentation")
            self.logger.error(f"❌ Failed to generate documentation for agent {agent_name}: {e}")
            return None
    
    async def _generate_documentation_from_schema(self, agent_name: str, schema: Any, 
                                                documentation_type: str, template: Dict[str, Any]) -> AGUISchemaDocumentation:
        """Generate documentation from AGUI schema using template."""
        try:
            # Extract schema information
            schema_version = getattr(schema, 'version', '1.0.0')
            schema_description = getattr(schema, 'description', f'AGUI schema for {agent_name}')
            schema_components = getattr(schema, 'components', [])
            schema_metadata = getattr(schema, 'metadata', {})
            
            # Generate title and description
            title = template["title_template"].format(agent_name=agent_name)
            description = template["description_template"].format(agent_name=agent_name)
            
            # Generate component documentation
            documented_components = []
            for component in schema_components:
                component_doc = await self._document_component(component, template["component_template"])
                documented_components.append(component_doc)
            
            # Generate examples
            examples = await self._generate_examples(schema_components, documentation_type)
            
            # Create documentation metadata
            doc_metadata = {
                "schema_version": schema_version,
                "documentation_type": documentation_type,
                "template_version": "1.0.0",
                "generation_method": "automatic",
                "component_count": len(schema_components),
                "example_count": len(examples)
            }
            
            return AGUISchemaDocumentation(
                agent_name=agent_name,
                schema_version=schema_version,
                documentation_type=documentation_type,
                title=title,
                description=description,
                components=documented_components,
                examples=examples,
                metadata=doc_metadata,
                generated_at=datetime.now().isoformat(),
                generated_by="agui_schema_documentation_service"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate documentation from schema: {e}")
            await self.handle_error_with_audit(e, f"generate_documentation_from_schema_failed_{agent_name}")
            raise
    
    async def _document_component(self, component: Any, template: Dict[str, Any]) -> Dict[str, Any]:
        """Document a single component using template."""
        try:
            # Extract component information
            component_name = getattr(component, 'type', 'unknown')
            component_description = getattr(component, 'description', 'No description available')
            component_properties = getattr(component, 'properties', {})
            component_examples = getattr(component, 'examples', [])
            
            # Generate component documentation based on template
            component_doc = {}
            for key, value in template.items():
                if isinstance(value, str):
                    # Replace placeholders
                    component_doc[key] = value.format(
                        component_name=component_name,
                        component_type=component_name,
                        component_description=component_description,
                        component_properties=component_properties,
                        component_examples=component_examples,
                        usage_instructions=self._generate_usage_instructions(component),
                        component_spec=self._generate_component_spec(component),
                        implementation_notes=self._generate_implementation_notes(component),
                        testing_guidelines=self._generate_testing_guidelines(component),
                        full_spec=self._generate_full_spec(component),
                        all_properties=component_properties,
                        validation_rules=self._generate_validation_rules(component)
                    )
                else:
                    component_doc[key] = value
            
            return component_doc
            
        except Exception as e:
            self.logger.error(f"Failed to document component: {e}")
            return {"error": f"Failed to document component: {e}"}
    
    def _generate_usage_instructions(self, component: Any) -> str:
        """Generate usage instructions for a component."""
        component_type = getattr(component, 'type', 'unknown')
        
        instructions_map = {
            "analysis_card": "Use this component to display analysis results with metrics and visualizations.",
            "data_table": "Use this component to display tabular data with sorting and filtering capabilities.",
            "visualization": "Use this component to display charts and graphs for data visualization.",
            "progress_indicator": "Use this component to show progress of long-running operations.",
            "action_buttons": "Use this component to provide user actions and interactions.",
            "error_display": "Use this component to display error messages and recovery options."
        }
        
        return instructions_map.get(component_type, f"Use this {component_type} component as needed.")
    
    def _generate_component_spec(self, component: Any) -> Dict[str, Any]:
        """Generate component specification."""
        return {
            "type": getattr(component, 'type', 'unknown'),
            "required": getattr(component, 'required', True),
            "properties": getattr(component, 'properties', {}),
            "validation": getattr(component, 'validation', {})
        }
    
    def _generate_implementation_notes(self, component: Any) -> str:
        """Generate implementation notes for a component."""
        component_type = getattr(component, 'type', 'unknown')
        
        notes_map = {
            "analysis_card": "Ensure metrics are properly formatted and visualizations are responsive.",
            "data_table": "Implement proper pagination and sorting for large datasets.",
            "visualization": "Use appropriate chart types based on data characteristics.",
            "progress_indicator": "Provide clear status messages and estimated completion times.",
            "action_buttons": "Ensure buttons are accessible and have proper loading states.",
            "error_display": "Include actionable error messages and recovery options."
        }
        
        return notes_map.get(component_type, f"Follow standard implementation practices for {component_type} components.")
    
    def _generate_testing_guidelines(self, component: Any) -> str:
        """Generate testing guidelines for a component."""
        component_type = getattr(component, 'type', 'unknown')
        
        guidelines_map = {
            "analysis_card": "Test with various metric values and visualization data.",
            "data_table": "Test sorting, filtering, and pagination functionality.",
            "visualization": "Test with different data sets and chart configurations.",
            "progress_indicator": "Test progress updates and completion states.",
            "action_buttons": "Test button interactions and loading states.",
            "error_display": "Test error message display and recovery actions."
        }
        
        return guidelines_map.get(component_type, f"Test {component_type} component functionality thoroughly.")
    
    def _generate_full_spec(self, component: Any) -> Dict[str, Any]:
        """Generate full component specification."""
        return {
            "type": getattr(component, 'type', 'unknown'),
            "title": getattr(component, 'title', ''),
            "description": getattr(component, 'description', ''),
            "required": getattr(component, 'required', True),
            "properties": getattr(component, 'properties', {}),
            "examples": getattr(component, 'examples', []),
            "validation": getattr(component, 'validation', {}),
            "metadata": getattr(component, 'metadata', {})
        }
    
    def _generate_validation_rules(self, component: Any) -> Dict[str, Any]:
        """Generate validation rules for a component."""
        return getattr(component, 'validation', {})
    
    async def _generate_examples(self, components: List[Any], documentation_type: str) -> List[Dict[str, Any]]:
        """Generate examples for documentation."""
        try:
            examples = []
            
            for component in components:
                component_examples = getattr(component, 'examples', [])
                if component_examples:
                    for example in component_examples:
                        examples.append({
                            "component_type": getattr(component, 'type', 'unknown'),
                            "example": example,
                            "description": f"Example usage of {getattr(component, 'type', 'unknown')} component"
                        })
            
            return examples
            
        except Exception as e:
            self.logger.error(f"Failed to generate examples: {e}")
            return []
    
    async def _assess_documentation_quality(self, agent_name: str, documentation: AGUISchemaDocumentation):
        """Assess documentation quality."""
        try:
            quality_score = 0.0
            quality_metrics = {}
            
            # Check completeness
            completeness_score = 0.0
            if documentation.title:
                completeness_score += 0.2
            if documentation.description:
                completeness_score += 0.2
            if documentation.components:
                completeness_score += 0.3
            if documentation.examples:
                completeness_score += 0.3
            
            quality_metrics["completeness"] = completeness_score
            quality_score += completeness_score * 0.4
            
            # Check component documentation quality
            component_quality = 0.0
            if documentation.components:
                for component in documentation.components:
                    if "description" in component and component["description"]:
                        component_quality += 1.0
                    if "examples" in component and component["examples"]:
                        component_quality += 1.0
                
                component_quality = component_quality / (len(documentation.components) * 2)
            
            quality_metrics["component_quality"] = component_quality
            quality_score += component_quality * 0.3
            
            # Check example quality
            example_quality = 0.0
            if documentation.examples:
                example_quality = min(1.0, len(documentation.examples) / 3.0)  # 3 examples = perfect score
            
            quality_metrics["example_quality"] = example_quality
            quality_score += example_quality * 0.3
            
            # Store quality assessment
            self.documentation_quality[agent_name] = {
                "overall_score": quality_score,
                "metrics": quality_metrics,
                "last_assessed": datetime.now().isoformat(),
                "documentation_type": documentation.documentation_type
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assess documentation quality for {agent_name}: {e}")
            await self.handle_error_with_audit(e, f"assess_documentation_quality_failed_{agent_name}")
    
    async def get_agent_documentation(self, agent_name: str, documentation_type: str = None, user_context: Dict[str, Any] = None) -> List[AGUISchemaDocumentation]:
        """
        Get documentation for an agent.
        
        Args:
            agent_name: Name of the agent
            documentation_type: Optional specific documentation type
            user_context: Optional user context for security and tenant validation
            
        Returns:
            List of AGUISchemaDocumentation
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_documentation_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_name, "read"):
                        await self.record_health_metric("get_agent_documentation_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("get_agent_documentation_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_documentation_tenant_denied", 1.0, {"agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_documentation_complete", success=False)
                            return []
            
            if agent_name not in self.agent_documentation:
                await self.record_health_metric("get_agent_documentation_not_found", 1.0, {"agent_name": agent_name})
                await self.log_operation_with_telemetry("get_agent_documentation_complete", success=True)
                return []
            
            docs = self.agent_documentation[agent_name]
            
            if documentation_type:
                docs = [doc for doc in docs if doc.documentation_type == documentation_type]
            
            # Record health metric
            await self.record_health_metric("get_agent_documentation_success", 1.0, {"agent_name": agent_name, "documentation_type": documentation_type, "count": len(docs)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_documentation_complete", success=True)
            
            return docs
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_documentation")
            self.logger.error(f"Failed to get documentation for agent {agent_name}: {e}")
            return []
    
    async def get_documentation_report(self, user_context: Dict[str, Any] = None) -> AGUIDocumentationReport:
        """Get comprehensive documentation report."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_documentation_report_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_documentation", "read"):
                        await self.record_health_metric("get_documentation_report_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_documentation_report_complete", success=False)
                        # Return empty report on access denied
                        from ..models import AGUIDocumentationReport
                        return AGUIDocumentationReport(
                            total_agents=0,
                            documented_agents=0,
                            undocumented_agents=0,
                            documentation_coverage=0.0,
                            documentation_types={},
                            quality_score=0.0
                        )
            
            # Tenant validation (multi-tenant support)
            agent_documentation_to_analyze = self.agent_documentation
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_documentation_report_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_documentation_report_complete", success=False)
                            # Return empty report on tenant denied
                            from ..models import AGUIDocumentationReport
                            return AGUIDocumentationReport(
                                total_agents=0,
                                documented_agents=0,
                                undocumented_agents=0,
                                documentation_coverage=0.0,
                                documentation_types={},
                                quality_score=0.0
                            )
                        # Filter by tenant if tenant_id is in agent metadata (would need to be stored)
                        # For now, we'll analyze all agents but this could be enhanced
            
            total_agents = len(agent_documentation_to_analyze)
            documented_agents = len([agent for agent, docs in agent_documentation_to_analyze.items() if docs])
            undocumented_agents = total_agents - documented_agents
            
            documentation_coverage = (documented_agents / total_agents * 100) if total_agents > 0 else 0.0
            
            # Count documentation types
            documentation_types = {}
            for docs in agent_documentation_to_analyze.values():
                for doc in docs:
                    doc_type = doc.documentation_type
                    documentation_types[doc_type] = documentation_types.get(doc_type, 0) + 1
            
            # Calculate overall quality score
            quality_scores = [metrics["overall_score"] for agent_name, metrics in self.documentation_quality.items() if agent_name in agent_documentation_to_analyze]
            quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
            result = AGUIDocumentationReport(
                total_agents=total_agents,
                documented_agents=documented_agents,
                undocumented_agents=undocumented_agents,
                documentation_coverage=documentation_coverage,
                documentation_types=documentation_types,
                last_updated=datetime.now().isoformat(),
                quality_score=quality_score
            )
            
            # Record health metric
            await self.record_health_metric("get_documentation_report_success", 1.0, {"total_agents": total_agents, "documented_agents": documented_agents})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_documentation_report_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_documentation_report")
            self.logger.error(f"Failed to generate documentation report: {e}")
            return AGUIDocumentationReport(
                total_agents=0,
                documented_agents=0,
                undocumented_agents=0,
                documentation_coverage=0.0,
                documentation_types={},
                last_updated=datetime.now().isoformat(),
                quality_score=0.0
            )
    
    async def get_documentation_quality_report(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get documentation quality report."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_documentation_quality_report_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_documentation", "read"):
                        await self.record_health_metric("get_documentation_quality_report_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_documentation_quality_report_complete", success=False)
                        return {"error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            documentation_quality_to_analyze = self.documentation_quality
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_documentation_quality_report_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_documentation_quality_report_complete", success=False)
                            return {"error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
                        # Filter by tenant if tenant_id is in agent metadata (would need to be stored)
                        # For now, we'll analyze all agents but this could be enhanced
            
            if not documentation_quality_to_analyze:
                await self.record_health_metric("get_documentation_quality_report_no_data", 1.0, {})
                await self.log_operation_with_telemetry("get_documentation_quality_report_complete", success=True)
                return {"message": "No documentation quality data available"}
            
            # Calculate aggregate quality metrics
            overall_scores = [metrics["overall_score"] for metrics in documentation_quality_to_analyze.values()]
            completeness_scores = [metrics["metrics"]["completeness"] for metrics in documentation_quality_to_analyze.values()]
            component_quality_scores = [metrics["metrics"]["component_quality"] for metrics in documentation_quality_to_analyze.values()]
            example_quality_scores = [metrics["metrics"]["example_quality"] for metrics in documentation_quality_to_analyze.values()]
            
            result = {
                "total_agents_assessed": len(documentation_quality_to_analyze),
                "average_overall_score": sum(overall_scores) / len(overall_scores),
                "average_completeness": sum(completeness_scores) / len(completeness_scores),
                "average_component_quality": sum(component_quality_scores) / len(component_quality_scores),
                "average_example_quality": sum(example_quality_scores) / len(example_quality_scores),
                "quality_distribution": {
                    "excellent": len([s for s in overall_scores if s >= 0.9]),
                    "good": len([s for s in overall_scores if 0.7 <= s < 0.9]),
                    "fair": len([s for s in overall_scores if 0.5 <= s < 0.7]),
                    "poor": len([s for s in overall_scores if s < 0.5])
                },
                "top_performing_agents": self._get_top_performing_agents(),
                "agents_needing_improvement": self._get_agents_needing_improvement(),
                "generated_at": datetime.now().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("get_documentation_quality_report_success", 1.0, {"total_agents_assessed": len(self.documentation_quality)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_documentation_quality_report_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_documentation_quality_report")
            self.logger.error(f"Failed to generate documentation quality report: {e}")
            return {"error": str(e), "error_code": type(e).__name__}
    
    def _get_top_performing_agents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing agents by documentation quality."""
        try:
            performance_data = []
            
            for agent_name, metrics in self.documentation_quality.items():
                performance_data.append({
                    "agent_name": agent_name,
                    "overall_score": metrics["overall_score"],
                    "completeness": metrics["metrics"]["completeness"],
                    "component_quality": metrics["metrics"]["component_quality"],
                    "example_quality": metrics["metrics"]["example_quality"]
                })
            
            # Sort by overall score
            performance_data.sort(key=lambda x: x["overall_score"], reverse=True)
            
            return performance_data[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get top performing agents: {e}")
            return []
    
    def _get_agents_needing_improvement(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get agents needing documentation improvement."""
        try:
            improvement_data = []
            
            for agent_name, metrics in self.documentation_quality.items():
                if metrics["overall_score"] < 0.7:  # Below good threshold
                    improvement_data.append({
                        "agent_name": agent_name,
                        "overall_score": metrics["overall_score"],
                        "completeness": metrics["metrics"]["completeness"],
                        "component_quality": metrics["metrics"]["component_quality"],
                        "example_quality": metrics["metrics"]["example_quality"],
                        "improvement_areas": self._identify_improvement_areas(metrics["metrics"])
                    })
            
            # Sort by overall score (lowest first)
            improvement_data.sort(key=lambda x: x["overall_score"])
            
            return improvement_data[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get agents needing improvement: {e}")
            return []
    
    def _identify_improvement_areas(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement."""
        improvement_areas = []
        
        if metrics["completeness"] < 0.8:
            improvement_areas.append("completeness")
        if metrics["component_quality"] < 0.7:
            improvement_areas.append("component_documentation")
        if metrics["example_quality"] < 0.7:
            improvement_areas.append("examples")
        
        return improvement_areas
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agui_schema_documentation_cleanup_start", success=True)
            
            self.agent_documentation.clear()
            self.documentation_index.clear()
            self.documentation_quality.clear()
            
            self.logger.info("AGUI Schema Documentation Service cleaned up")
            
            # Record health metric
            await self.record_health_metric("agui_schema_documentation_cleanup", 1.0, {"service": "agui_schema_documentation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agui_schema_documentation_cleanup_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agui_schema_documentation_cleanup")
            self.logger.error(f"Error during cleanup: {e}")

    async def shutdown(self):
        """Shutdown the AGUI Schema Documentation Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agui_schema_documentation_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down AGUI Schema Documentation Service...")
            
            # Clear documentation cache
            self.schema_documentation.clear()
            
            self.logger.info("✅ AGUI Schema Documentation Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("agui_schema_documentation_shutdown", 1.0, {"service": "agui_schema_documentation"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agui_schema_documentation_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agui_schema_documentation_shutdown")
            self.logger.error(f"❌ Error during AGUI Schema Documentation Service shutdown: {e}")





