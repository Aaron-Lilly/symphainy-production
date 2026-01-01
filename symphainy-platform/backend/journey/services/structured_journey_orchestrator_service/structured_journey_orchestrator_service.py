#!/usr/bin/env python3
"""
Structured Journey Orchestrator Service

WHAT: Designs and executes structured, linear multi-step user journeys
HOW: Composes Experience services (FrontendGateway, UserExperience, SessionManager) into guided journey flows

This service provides STRUCTURED journey orchestration for linear, guided flows
(e.g., enterprise migrations, onboarding processes) by composing Experience service APIs
into multi-step user flows with milestone tracking and enforced progression.

Use this for: Guided workflows, enterprise solutions, structured processes
For free-form navigation, use SessionJourneyOrchestratorService instead.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class StructuredJourneyOrchestratorService(RealmServiceBase):
    """
    Structured Journey Orchestrator Service for Journey realm.
    
    Designs and executes STRUCTURED, LINEAR multi-step user journeys by composing 
    Experience services (FrontendGateway, UserExperience, SessionManager) into guided flows.
    
    Use for: Enterprise migrations, guided onboarding, structured workflows
    For free-form user navigation, use SessionJourneyOrchestratorService instead.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Journey Orchestrator Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.conductor = None
        self.librarian = None
        self.data_steward = None
        
        # Experience services (discovered via Curator)
        self.frontend_gateway = None
        self.user_experience = None
        self.session_manager = None
        
        # Journey Milestone Tracker (discovered via Curator)
        self.milestone_tracker = None
        
        # Journey templates and definitions
        self.journey_templates: Dict[str, Dict[str, Any]] = {}
        self.active_journeys: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """
        Initialize Structured Journey Orchestrator Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "structured_journey_orchestrator_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.conductor = await self.get_conductor_api()
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            
            # 2. Discover Experience services via Curator
            await self._discover_experience_services()
            
            # 3. Discover Journey services via Curator
            await self._discover_journey_services()
            
            # 4. Load journey templates
            await self._load_journey_templates()
            
            # 5. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "journey_orchestration",
                        "protocol": "StructuredJourneyOrchestratorProtocol",
                        "description": "Design and execute structured, linear multi-step user journeys",
                        "contracts": {
                            "soa_api": {
                                "api_name": "design_journey",
                                "endpoint": "/api/v1/journey/structured/design",
                                "method": "POST",
                                "handler": self.design_journey,
                                "metadata": {
                                    "description": "Design a journey from template or requirements",
                                    "parameters": ["journey_type", "requirements", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.design_structured",
                            "semantic_api": "/api/v1/journey/structured/design",
                            "user_journey": "design_structured_journey"
                        }
                    },
                    {
                        "name": "journey_design",
                        "protocol": "StructuredJourneyOrchestratorProtocol",
                        "description": "Get and customize journey templates",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_journey_template",
                                "endpoint": "/api/v1/journey/structured/template",
                                "method": "GET",
                                "handler": self.get_journey_template,
                                "metadata": {
                                    "description": "Get journey template",
                                    "parameters": ["template_name", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_template",
                            "semantic_api": "/api/v1/journey/structured/template",
                            "user_journey": "get_journey_template"
                        }
                    },
                    {
                        "name": "journey_execution",
                        "protocol": "StructuredJourneyOrchestratorProtocol",
                        "description": "Execute structured journeys with milestone tracking",
                        "contracts": {
                            "soa_api": {
                                "api_name": "execute_journey",
                                "endpoint": "/api/v1/journey/structured/execute",
                                "method": "POST",
                                "handler": self.execute_journey,
                                "metadata": {
                                    "description": "Execute a structured journey",
                                    "parameters": ["journey_id", "user_id", "context", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.execute_structured",
                            "semantic_api": "/api/v1/journey/structured/execute",
                            "user_journey": "execute_structured_journey"
                        }
                    },
                    {
                        "name": "milestone_management",
                        "protocol": "StructuredJourneyOrchestratorProtocol",
                        "description": "Manage journey milestones (advance, pause, resume, cancel)",
                        "contracts": {
                            "soa_api": {
                                "api_name": "advance_journey_step",
                                "endpoint": "/api/v1/journey/structured/advance",
                                "method": "POST",
                                "handler": self.advance_journey_step,
                                "metadata": {
                                    "description": "Advance to next journey step",
                                    "parameters": ["journey_id", "user_id", "step_result", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.advance_step",
                            "semantic_api": "/api/v1/journey/structured/advance",
                            "user_journey": "advance_journey_step"
                        }
                    }
                ],
                soa_apis=[
                    "design_journey", "get_journey_template", "customize_journey",
                    "execute_journey", "advance_journey_step", "get_journey_status",
                    "pause_journey", "resume_journey", "cancel_journey", "get_available_journey_types"
                ],
                mcp_tools=[]  # Journey services provide SOA APIs, not MCP tools
            )
            
            # Record health metric
            await self.record_health_metric(
                "structured_journey_orchestrator_initialized",
                1.0,
                {"service": self.service_name, "templates_loaded": len(self.journey_templates)}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "structured_journey_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Structured Journey Orchestrator Service initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "structured_journey_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "structured_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Structured Journey Orchestrator Service initialization failed: {e}")
            return False
    
    async def _discover_experience_services(self):
        """Discover Experience services via Curator."""
        try:
            curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
            
            if curator:
                # Try to discover each Experience service
                try:
                    self.frontend_gateway = await curator.discover_service_by_name("FrontendGatewayService")
                    self.logger.info("✅ Discovered FrontendGatewayService")
                except Exception:
                    self.logger.warning("⚠️ FrontendGatewayService not yet available")
                
                try:
                    self.user_experience = await curator.discover_service_by_name("UserExperienceService")
                    self.logger.info("✅ Discovered UserExperienceService")
                except Exception:
                    self.logger.warning("⚠️ UserExperienceService not yet available")
                
                try:
                    self.session_manager = await curator.discover_service_by_name("SessionManagerService")
                    self.logger.info("✅ Discovered SessionManagerService")
                except Exception:
                    self.logger.warning("⚠️ SessionManagerService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Experience service discovery failed: {e}")
    
    async def _discover_journey_services(self):
        """Discover other Journey services via Curator."""
        try:
            curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
            
            if curator:
                try:
                    self.milestone_tracker = await curator.discover_service_by_name("JourneyMilestoneTrackerService")
                    self.logger.info("✅ Discovered JourneyMilestoneTrackerService")
                except Exception:
                    self.logger.warning("⚠️ JourneyMilestoneTrackerService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Journey service discovery failed: {e}")
    
    async def _load_journey_templates(self):
        """Load journey templates (predefined journey structures)."""
        # Content Migration Journey Template
        self.journey_templates["content_migration"] = {
            "template_name": "Content Migration Journey",
            "description": "End-to-end content migration with analysis and validation",
            "milestones": [
                {
                    "milestone_id": "upload",
                    "milestone_name": "Upload Content",
                    "experience_api": "handle_document_analysis_request",
                    "required": True,
                    "next_steps": ["analyze"]
                },
                {
                    "milestone_id": "analyze",
                    "milestone_name": "Analyze Content",
                    "experience_api": "handle_insights_request",
                    "required": True,
                    "next_steps": ["transform", "validate"]
                },
                {
                    "milestone_id": "transform",
                    "milestone_name": "Transform Data",
                    "experience_api": "handle_data_operations_request",
                    "required": True,
                    "next_steps": ["validate"]
                },
                {
                    "milestone_id": "validate",
                    "milestone_name": "Validate Results",
                    "experience_api": "handle_document_analysis_request",
                    "required": True,
                    "completion": True
                }
            ]
        }
        
        # Insights Generation Journey Template
        self.journey_templates["insights_generation"] = {
            "template_name": "Insights Generation Journey",
            "description": "Generate insights from data with visualization",
            "milestones": [
                {
                    "milestone_id": "select_data",
                    "milestone_name": "Select Data Source",
                    "experience_api": "handle_document_analysis_request",
                    "required": True,
                    "next_steps": ["analyze"]
                },
                {
                    "milestone_id": "analyze",
                    "milestone_name": "Analyze Data",
                    "experience_api": "handle_insights_request",
                    "required": True,
                    "next_steps": ["visualize"]
                },
                {
                    "milestone_id": "visualize",
                    "milestone_name": "Create Visualizations",
                    "experience_api": "handle_insights_request",
                    "required": True,
                    "completion": True
                }
            ]
        }
        
        # Operations Optimization Journey Template
        self.journey_templates["operations_optimization"] = {
            "template_name": "Operations Optimization Journey",
            "description": "Optimize business operations with workflow analysis",
            "milestones": [
                {
                    "milestone_id": "map_process",
                    "milestone_name": "Map Current Process",
                    "experience_api": "handle_operations_request",
                    "required": True,
                    "next_steps": ["analyze"]
                },
                {
                    "milestone_id": "analyze",
                    "milestone_name": "Analyze Process",
                    "experience_api": "handle_insights_request",
                    "required": True,
                    "next_steps": ["optimize"]
                },
                {
                    "milestone_id": "optimize",
                    "milestone_name": "Generate Optimizations",
                    "experience_api": "handle_operations_request",
                    "required": True,
                    "completion": True
                }
            ]
        }
        
        # ⭐ Insurance Discovery Journey Template (NEW)
        try:
            from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_templates.solution_composer_templates import INSURANCE_DISCOVERY_JOURNEY
            # Convert to Structured Journey format
            self.journey_templates["insurance_discovery"] = {
                "template_name": INSURANCE_DISCOVERY_JOURNEY["name"],
                "description": INSURANCE_DISCOVERY_JOURNEY["description"],
                "milestones": [
                    {
                        "milestone_id": milestone["milestone_id"],
                        "milestone_name": milestone["name"],
                        "service": milestone.get("service"),
                        "operation": milestone.get("operation"),
                        "required": True,
                        "next_steps": milestone.get("next_milestones", [])
                    }
                    for milestone in INSURANCE_DISCOVERY_JOURNEY.get("milestones", [])
                ]
            }
            self.logger.info("✅ Loaded Insurance Discovery Journey template")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load Insurance Discovery Journey template: {e}")
        
        # ⭐ Insurance Validation Journey Template (NEW)
        try:
            from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_templates.solution_composer_templates import INSURANCE_VALIDATION_JOURNEY
            # Convert to Structured Journey format
            self.journey_templates["insurance_validation"] = {
                "template_name": INSURANCE_VALIDATION_JOURNEY["name"],
                "description": INSURANCE_VALIDATION_JOURNEY["description"],
                "milestones": [
                    {
                        "milestone_id": milestone["milestone_id"],
                        "milestone_name": milestone["name"],
                        "service": milestone.get("service"),
                        "operation": milestone.get("operation"),
                        "required": True,
                        "next_steps": milestone.get("next_milestones", [])
                    }
                    for milestone in INSURANCE_VALIDATION_JOURNEY.get("milestones", [])
                ]
            }
            self.logger.info("✅ Loaded Insurance Validation Journey template")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load Insurance Validation Journey template: {e}")
        
        self.logger.info(f"✅ Loaded {len(self.journey_templates)} journey templates")
    
    # ========================================================================
    # SOA APIs (Journey Design)
    # ========================================================================
    
    async def design_journey(
        self,
        journey_type: str,
        requirements: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design a journey from template or requirements (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_type: Type of journey (content_migration, insights_generation, etc.)
            requirements: Journey requirements and customizations
            user_context: User context for security and tenant validation
        
        Returns:
            Journey definition
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "design_journey_start",
            success=True,
            details={"journey_type": journey_type}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "design_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "design_journey",
                    details={"user_id": user_context.get("user_id"), "journey_type": journey_type}
                )
                await self.record_health_metric("design_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("design_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "design_journey",
                    details={"tenant_id": tenant_id, "journey_type": journey_type}
                )
                await self.record_health_metric("design_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("design_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get template if available
            if journey_type in self.journey_templates:
                template = self.journey_templates[journey_type]
            else:
                return {
                    "success": False,
                    "error": f"Journey type '{journey_type}' not found"
                }
            
            # Create journey from template
            journey_id = str(uuid.uuid4())
            journey = {
                "journey_id": journey_id,
                "journey_type": journey_type,
                "journey_name": template["template_name"],
                "description": template["description"],
                "milestones": template["milestones"],
                "requirements": requirements,
                "created_at": datetime.utcnow().isoformat(),
                "status": "designed"
            }
            
            # Store journey via Librarian
            await self.store_document(
                document_data=journey,
                metadata={
                    "type": "journey_definition",
                    "journey_id": journey_id,
                    "journey_type": journey_type
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("design_journey_success", 1.0, {"journey_id": journey_id, "journey_type": journey_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("design_journey_complete", success=True, details={"journey_id": journey_id, "journey_type": journey_type})
            
            self.logger.info(f"✅ Journey designed: {journey_id} ({journey_type})")
            
            return {
                "success": True,
                "journey": journey
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "design_journey", details={"journey_type": journey_type})
            
            # Record health metric (failure)
            await self.record_health_metric("design_journey_failed", 1.0, {"journey_type": journey_type, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("design_journey_complete", success=False, details={"journey_type": journey_type, "error": str(e)})
            
            self.logger.error(f"❌ Design journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_template(
        self,
        template_name: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get journey template (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            template_name: Name of template
            user_context: User context for security and tenant validation
        
        Returns:
            Journey template
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_template_start",
            success=True,
            details={"template_name": template_name}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_journey_template", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_template",
                    details={"user_id": user_context.get("user_id"), "template_name": template_name}
                )
                await self.record_health_metric("get_journey_template_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_journey_template_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_journey_template",
                    details={"tenant_id": tenant_id, "template_name": template_name}
                )
                await self.record_health_metric("get_journey_template_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_journey_template_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            if template_name in self.journey_templates:
                # Record health metric (success)
                await self.record_health_metric("get_journey_template_success", 1.0, {"template_name": template_name})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_journey_template_complete", success=True, details={"template_name": template_name})
                
                return {
                    "success": True,
                    "template": self.journey_templates[template_name]
                }
            
            # Record health metric (not found)
            await self.record_health_metric("get_journey_template_not_found", 1.0, {"template_name": template_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_journey_template_complete", success=False, details={"template_name": template_name, "error": "Template not found"})
            
            return {
                "success": False,
                "error": f"Template '{template_name}' not found"
            }
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_template", details={"template_name": template_name})
            
            # Record health metric (failure)
            await self.record_health_metric("get_journey_template_failed", 1.0, {"template_name": template_name, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_journey_template_complete", success=False, details={"template_name": template_name, "error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def customize_journey(
        self,
        journey_id: str,
        customizations: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Customize an existing journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            customizations: Customizations to apply
            user_context: User context for security and tenant validation
        
        Returns:
            Customized journey
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "customize_journey_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "customize_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "customize_journey",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("customize_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("customize_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "customize_journey",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("customize_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("customize_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get journey
            journey_doc = await self.retrieve_document(f"journey_{journey_id}")
            
            if not journey_doc or "document" not in journey_doc:
                return {
                    "success": False,
                    "error": "Journey not found"
                }
            
            journey = journey_doc["document"]
            
            # Apply customizations
            for key, value in customizations.items():
                if key in journey:
                    journey[key] = value
            
            # Update journey
            await self.store_document(
                document_data=journey,
                metadata={
                    "type": "journey_definition",
                    "journey_id": journey_id,
                    "customized_at": datetime.utcnow().isoformat()
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("customize_journey_success", 1.0, {"journey_id": journey_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("customize_journey_complete", success=True, details={"journey_id": journey_id})
            
            self.logger.info(f"✅ Journey customized: {journey_id}")
            
            return {
                "success": True,
                "journey": journey
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "customize_journey", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("customize_journey_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("customize_journey_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Customize journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Journey Execution)
    # ========================================================================
    
    async def execute_journey(
        self,
        journey_id: str,
        user_id: str,
        context: Dict[str, Any],
        client_id: Optional[str] = None,  # NEW - Week 6: Client-scoped execution
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a journey for a user (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        - Client-scoped execution validation (NEW - Week 6)
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            context: Execution context
            client_id: Client ID for client-scoped execution (optional, can be in context)
            user_context: User context for security and tenant validation
        
        Returns:
            Journey execution result
        """
        # Extract client_id from context if not provided
        if not client_id:
            client_id = context.get("client_id")
        
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "execute_journey_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "execute_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "execute_journey",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("execute_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("execute_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "execute_journey",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("execute_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("execute_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get journey definition
            journey_doc = await self.retrieve_document(f"journey_{journey_id}")
            
            if not journey_doc or "document" not in journey_doc:
                return {
                    "success": False,
                    "error": "Journey not found"
                }
            
            journey = journey_doc["document"]
            
            # NEW - Week 6: Client-scoped execution validation
            if client_id:
                journey_client_id = journey.get("client_id")
                if journey_client_id and journey_client_id != client_id:
                    result = {
                        "success": False,
                        "error": f"Journey client_id mismatch: expected {client_id}, got {journey_client_id}"
                    }
                    await self.log_operation_with_telemetry("execute_journey_complete", success=False, details={"error": result["error"]})
                    return result
                # Ensure client_id is in context for downstream operations
                context["client_id"] = client_id
            
            # Create session via SessionManager (Experience)
            if self.session_manager:
                session_result = await self.session_manager.create_session(user_id, {
                    "journey_id": journey_id,
                    "context": context
                })
                session_id = session_result.get("session", {}).get("session_id")
            else:
                session_id = None
            
            # Track journey start
            execution = {
                "journey_id": journey_id,
                "user_id": user_id,
                "client_id": client_id,  # NEW - Week 6: Store client_id in execution
                "session_id": session_id,
                "status": "in_progress",
                "started_at": datetime.utcnow().isoformat(),
                "current_milestone": journey["milestones"][0]["milestone_id"] if journey["milestones"] else None,
                "completed_milestones": [],
                "context": context
            }
            
            # Store in active journeys
            self.active_journeys[f"{journey_id}_{user_id}"] = execution
            
            # Track via Librarian
            await self.store_document(
                document_data=execution,
                metadata={
                    "type": "journey_execution",
                    "journey_id": journey_id,
                    "user_id": user_id
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("execute_journey_success", 1.0, {"journey_id": journey_id, "user_id": user_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("execute_journey_complete", success=True, details={"journey_id": journey_id, "user_id": user_id})
            
            self.logger.info(f"✅ Journey execution started: {journey_id} for user {user_id}")
            
            return {
                "success": True,
                "execution": execution,
                "next_milestone": journey["milestones"][0] if journey["milestones"] else None
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "execute_journey", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("execute_journey_failed", 1.0, {"journey_id": journey_id, "user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("execute_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Execute journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def advance_journey_step(
        self,
        journey_id: str,
        user_id: str,
        step_result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advance journey to next step (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            step_result: Result from current step
            user_context: User context for security and tenant validation
        
        Returns:
            Next step information
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "advance_journey_step_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "advance_journey_step", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "advance_journey_step",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("advance_journey_step_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("advance_journey_step_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "advance_journey_step",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("advance_journey_step_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("advance_journey_step_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get active journey
            key = f"{journey_id}_{user_id}"
            if key not in self.active_journeys:
                return {
                    "success": False,
                    "error": "Journey execution not found"
                }
            
            execution = self.active_journeys[key]
            
            # Get journey definition
            journey_doc = await self.retrieve_document(f"journey_{journey_id}")
            journey = journey_doc["document"]
            
            # Mark current milestone complete
            current_milestone_id = execution["current_milestone"]
            execution["completed_milestones"].append({
                "milestone_id": current_milestone_id,
                "completed_at": datetime.utcnow().isoformat(),
                "result": step_result
            })
            
            # Track milestone completion
            if self.milestone_tracker:
                await self.milestone_tracker.track_milestone_complete(
                    journey_id,
                    user_id,
                    current_milestone_id,
                    step_result,
                    user_context=user_context
                )
            
            # Find next milestone
            current_milestone = next((m for m in journey["milestones"] if m["milestone_id"] == current_milestone_id), None)
            
            if current_milestone and current_milestone.get("completion"):
                # Journey complete!
                execution["status"] = "completed"
                execution["completed_at"] = datetime.utcnow().isoformat()
                
                # Record health metric (success - journey completed)
                await self.record_health_metric("advance_journey_step_success", 1.0, {"journey_id": journey_id, "user_id": user_id, "status": "completed"})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("advance_journey_step_complete", success=True, details={"journey_id": journey_id, "user_id": user_id, "status": "completed"})
                
                self.logger.info(f"✅ Journey completed: {journey_id} for user {user_id}")
                
                return {
                    "success": True,
                    "status": "completed",
                    "execution": execution
                }
            
            # Get next steps
            next_steps = current_milestone.get("next_steps", []) if current_milestone else []
            if next_steps:
                next_milestone_id = next_steps[0]  # Take first next step
                next_milestone = next((m for m in journey["milestones"] if m["milestone_id"] == next_milestone_id), None)
                
                execution["current_milestone"] = next_milestone_id
                
                # Update session
                if self.session_manager and execution.get("session_id"):
                    await self.session_manager.update_session(
                        execution["session_id"],
                        {"current_milestone": next_milestone_id}
                    )
                
                # Record health metric (success - advanced to next step)
                await self.record_health_metric("advance_journey_step_success", 1.0, {"journey_id": journey_id, "user_id": user_id, "next_milestone": next_milestone_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("advance_journey_step_complete", success=True, details={"journey_id": journey_id, "user_id": user_id, "next_milestone": next_milestone_id})
                
                self.logger.info(f"✅ Journey advanced: {journey_id} to {next_milestone_id}")
                
                return {
                    "success": True,
                    "status": "in_progress",
                    "next_milestone": next_milestone,
                    "execution": execution
                }
            
            # No more steps - complete
            execution["status"] = "completed"
            execution["completed_at"] = datetime.utcnow().isoformat()
            
            # Record health metric (success)
            await self.record_health_metric("advance_journey_step_success", 1.0, {"journey_id": journey_id, "user_id": user_id, "status": "completed"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("advance_journey_step_complete", success=True, details={"journey_id": journey_id, "user_id": user_id, "status": "completed"})
            
            return {
                "success": True,
                "status": "completed",
                "execution": execution
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "advance_journey_step", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("advance_journey_step_failed", 1.0, {"journey_id": journey_id, "user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("advance_journey_step_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Advance journey step failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_status(
        self,
        journey_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get journey execution status (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Journey status
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_status_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_journey_status", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_status",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_journey_status_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_journey_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_journey_status",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_journey_status_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_journey_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            key = f"{journey_id}_{user_id}"
            
            if key in self.active_journeys:
                execution = self.active_journeys[key]
                
                # Get progress from milestone tracker
                if self.milestone_tracker:
                    progress = await self.milestone_tracker.get_journey_progress(
                        journey_id,
                        user_id,
                        user_context=user_context
                    )
                else:
                    progress = None
                
                # Record health metric (success)
                await self.record_health_metric("get_journey_status_success", 1.0, {"journey_id": journey_id, "user_id": user_id, "status": execution.get("status")})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_journey_status_complete", success=True, details={"journey_id": journey_id, "user_id": user_id})
                
                return {
                    "success": True,
                    "execution": execution,
                    "progress": progress
                }
            
            # Try to retrieve from storage
            results = await self.search_documents(
                "journey_execution",
                {"type": "journey_execution", "journey_id": journey_id, "user_id": user_id}
            )
            
            if results and len(results) > 0:
                execution = results[0].get("document") if isinstance(results[0], dict) else results[0]
                
                # Record health metric (success)
                await self.record_health_metric("get_journey_status_success", 1.0, {"journey_id": journey_id, "user_id": user_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_journey_status_complete", success=True, details={"journey_id": journey_id, "user_id": user_id})
                
                return {
                    "success": True,
                    "execution": execution
                }
            
            # Record health metric (not found)
            await self.record_health_metric("get_journey_status_not_found", 1.0, {"journey_id": journey_id, "user_id": user_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_journey_status_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": "Journey execution not found"})
            
            return {
                "success": False,
                "error": "Journey execution not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_status", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_journey_status_failed", 1.0, {"journey_id": journey_id, "user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_journey_status_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Get journey status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Journey Management)
    # ========================================================================
    
    async def pause_journey(
        self,
        journey_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pause journey execution (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Pause result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "pause_journey_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "pause_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "pause_journey",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("pause_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("pause_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "pause_journey",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("pause_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("pause_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            key = f"{journey_id}_{user_id}"
            if key in self.active_journeys:
                self.active_journeys[key]["status"] = "paused"
                self.active_journeys[key]["paused_at"] = datetime.utcnow().isoformat()
                
                # Record health metric (success)
                await self.record_health_metric("pause_journey_success", 1.0, {"journey_id": journey_id, "user_id": user_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("pause_journey_complete", success=True, details={"journey_id": journey_id, "user_id": user_id})
                
                self.logger.info(f"✅ Journey paused: {journey_id} for user {user_id}")
                
                return {
                    "success": True,
                    "status": "paused"
                }
            
            # Record health metric (not found)
            await self.record_health_metric("pause_journey_not_found", 1.0, {"journey_id": journey_id, "user_id": user_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("pause_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": "Journey execution not found"})
            
            return {
                "success": False,
                "error": "Journey execution not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "pause_journey", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("pause_journey_failed", 1.0, {"journey_id": journey_id, "user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("pause_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Pause journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def resume_journey(
        self,
        journey_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resume paused journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Resume result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "resume_journey_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "resume_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "resume_journey",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("resume_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("resume_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "resume_journey",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("resume_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("resume_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            key = f"{journey_id}_{user_id}"
            if key in self.active_journeys:
                self.active_journeys[key]["status"] = "in_progress"
                self.active_journeys[key]["resumed_at"] = datetime.utcnow().isoformat()
                
                # Record health metric (success)
                await self.record_health_metric("resume_journey_success", 1.0, {"journey_id": journey_id, "user_id": user_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("resume_journey_complete", success=True, details={"journey_id": journey_id, "user_id": user_id})
                
                self.logger.info(f"✅ Journey resumed: {journey_id} for user {user_id}")
                
                return {
                    "success": True,
                    "status": "in_progress"
                }
            
            # Record health metric (not found)
            await self.record_health_metric("resume_journey_not_found", 1.0, {"journey_id": journey_id, "user_id": user_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("resume_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": "Journey execution not found"})
            
            return {
                "success": False,
                "error": "Journey execution not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "resume_journey", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("resume_journey_failed", 1.0, {"journey_id": journey_id, "user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("resume_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Resume journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_journey(
        self,
        journey_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cancel journey execution (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Cancel result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "cancel_journey_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "cancel_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "cancel_journey",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("cancel_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("cancel_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "cancel_journey",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("cancel_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("cancel_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            key = f"{journey_id}_{user_id}"
            if key in self.active_journeys:
                self.active_journeys[key]["status"] = "cancelled"
                self.active_journeys[key]["cancelled_at"] = datetime.utcnow().isoformat()
                
                # Remove from active journeys
                del self.active_journeys[key]
                
                # Record health metric (success)
                await self.record_health_metric("cancel_journey_success", 1.0, {"journey_id": journey_id, "user_id": user_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("cancel_journey_complete", success=True, details={"journey_id": journey_id, "user_id": user_id})
                
                self.logger.info(f"✅ Journey cancelled: {journey_id} for user {user_id}")
                
                return {
                    "success": True,
                    "status": "cancelled"
                }
            
            # Record health metric (not found)
            await self.record_health_metric("cancel_journey_not_found", 1.0, {"journey_id": journey_id, "user_id": user_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("cancel_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": "Journey execution not found"})
            
            return {
                "success": False,
                "error": "Journey execution not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "cancel_journey", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("cancel_journey_failed", 1.0, {"journey_id": journey_id, "user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("cancel_journey_complete", success=False, details={"journey_id": journey_id, "user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Cancel journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_journey_types(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get available journey types (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            user_context: User context for security and tenant validation
        
        Returns:
            Available journey types
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_available_journey_types_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_available_journey_types", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_available_journey_types",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_available_journey_types_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_available_journey_types_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_available_journey_types",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("get_available_journey_types_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_available_journey_types_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            journey_types = list(self.journey_templates.keys())
            
            result = {
                "success": True,
                "journey_types": journey_types,
                "templates": {
                    name: {
                        "name": template["template_name"],
                        "description": template["description"],
                        "milestones_count": len(template["milestones"])
                    }
                    for name, template in self.journey_templates.items()
                }
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_available_journey_types_success", 1.0, {"journey_types_count": len(journey_types)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_available_journey_types_complete", success=True, details={"journey_types_count": len(journey_types)})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_available_journey_types")
            
            # Record health metric (failure)
            await self.record_health_metric("get_available_journey_types_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_available_journey_types_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # ARTIFACT STORAGE (Phase 1: Foundation)
    # ========================================================================
    
    async def create_journey_artifact(
        self,
        artifact_type: str,  # "workflow", "sop", "wave_definition", "coexistence_blueprint"
        artifact_data: Dict[str, Any],
        client_id: Optional[str] = None,
        status: str = "draft",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Journey artifact (not yet a journey).
        
        This is the foundation - artifacts are stored as journey-like structures
        but with status lifecycle.
        
        Args:
            artifact_type: Type of artifact (workflow, sop, wave_definition, coexistence_blueprint)
            artifact_data: Artifact data (same structure as journey data)
            client_id: Client ID for client-scoped artifacts (optional)
            status: Artifact status (draft, review, approved, implemented, active)
            user_context: User context for security and tenant validation
        
        Returns:
            Created artifact with artifact_id
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_journey_artifact_start",
            success=True,
            details={"artifact_type": artifact_type, "status": status}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "create_journey_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "create_journey_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("create_journey_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Generate artifact ID
            artifact_id = str(uuid.uuid4())
            
            # Create artifact structure
            artifact = {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id,
                "status": status,
                "data": artifact_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "version": 1,
                "user_id": user_context.get("user_id") if user_context else None,
                "tenant_id": user_context.get("tenant_id") if user_context else None,
                "journey_id": None  # Will be set when artifact becomes journey
            }
            
            # Store via Librarian (persistent storage)
            await self.store_document(
                document_data=artifact,
                metadata={
                    "type": "journey_artifact",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "client_id": client_id,
                    "status": status
                }
            )
            
            # Register with Curator for discovery
            curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
            if curator:
                try:
                    await curator.register_artifact(
                        artifact_id=artifact_id,
                        artifact_type="journey",
                        artifact_data=artifact,
                        client_id=client_id,
                        user_context=user_context
                    )
                    self.logger.info(f"✅ Journey artifact registered with Curator: {artifact_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to register artifact with Curator: {e}")
            
            result = {
                "success": True,
                "artifact": artifact
            }
            
            # Record health metric
            await self.record_health_metric("create_journey_artifact_success", 1.0, {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "create_journey_artifact_complete",
                success=True,
                details={"artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Journey artifact created: {artifact_id} ({artifact_type}, status: {status})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_journey_artifact", details={"artifact_type": artifact_type})
            
            # Record health metric (failure)
            await self.record_health_metric("create_journey_artifact_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "create_journey_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Create journey artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_artifact(
        self,
        artifact_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve Journey artifact.
        
        Args:
            artifact_id: Artifact ID
            user_context: User context for security and tenant validation
        
        Returns:
            Artifact data
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_artifact_start",
            success=True,
            details={"artifact_id": artifact_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_journey_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_journey_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Try to retrieve from Librarian
            artifact_doc = await self.retrieve_document(f"journey_artifact_{artifact_id}")
            
            if artifact_doc and "document" in artifact_doc:
                artifact = artifact_doc["document"]
                
                result = {
                    "success": True,
                    "artifact": artifact
                }
                
                # End telemetry tracking
                await self.log_operation_with_telemetry(
                    "get_journey_artifact_complete",
                    success=True,
                    details={"artifact_id": artifact_id}
                )
                
                return result
            
            # Try Curator as fallback
            curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
            if curator:
                try:
                    artifact = await curator.get_artifact(artifact_id, artifact_type="journey")
                    if artifact:
                        result = {
                            "success": True,
                            "artifact": artifact
                        }
                        await self.log_operation_with_telemetry("get_journey_artifact_complete", success=True)
                        return result
                except Exception as e:
                    self.logger.debug(f"Curator artifact retrieval failed: {e}")
            
            result = {
                "success": False,
                "error": "Artifact not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_journey_artifact_complete",
                success=False,
                details={"error": result["error"]}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_artifact", details={"artifact_id": artifact_id})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_journey_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get journey artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_journey_artifact_status(
        self,
        artifact_id: str,
        new_status: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update artifact status (part of lifecycle).
        
        Validates status transition and updates artifact.
        
        Args:
            artifact_id: Artifact ID
            new_status: New status (must be valid transition)
            user_context: User context for security and tenant validation
        
        Returns:
            Updated artifact
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "update_journey_artifact_status_start",
            success=True,
            details={"artifact_id": artifact_id, "new_status": new_status}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "update_journey_artifact_status", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "update_journey_artifact_status",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("update_journey_artifact_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get artifact
            artifact_result = await self.get_journey_artifact(artifact_id, user_context)
            if not artifact_result.get("success"):
                return artifact_result
            
            artifact = artifact_result["artifact"]
            current_status = artifact.get("status")
            
            # Validate status transition
            valid_transitions = {
                "draft": ["review", "cancelled"],
                "review": ["approved", "rejected", "draft"],
                "approved": ["implemented", "draft"],
                "implemented": ["active"],
                "active": ["paused", "completed"],
                "rejected": ["draft"],
                "cancelled": [],
                "paused": ["active", "cancelled"],
                "completed": []
            }
            
            if current_status not in valid_transitions:
                result = {
                    "success": False,
                    "error": f"Invalid current status: {current_status}"
                }
                await self.log_operation_with_telemetry("update_journey_artifact_status_complete", success=False)
                return result
            
            if new_status not in valid_transitions.get(current_status, []):
                result = {
                    "success": False,
                    "error": f"Invalid status transition: {current_status} → {new_status}"
                }
                await self.log_operation_with_telemetry("update_journey_artifact_status_complete", success=False)
                return result
            
            # Update artifact
            artifact["status"] = new_status
            artifact["updated_at"] = datetime.utcnow().isoformat()
            artifact["version"] = artifact.get("version", 1) + 1
            
            # Store updated artifact (latest version)
            await self.store_document(
                document_data=artifact,
                metadata={
                    "type": "journey_artifact",
                    "artifact_id": artifact_id,
                    "status": new_status,
                    "previous_status": current_status,
                    "version": artifact["version"],
                    "document_id": f"journey_artifact_{artifact_id}"  # Consistent document_id for latest
                }
            )
            
            # Also store versioned copy for history
            await self.store_document(
                document_data=artifact,
                metadata={
                    "type": "journey_artifact_version",
                    "artifact_id": artifact_id,
                    "version": artifact["version"],
                    "status": new_status,
                    "previous_status": current_status,
                    "document_id": f"journey_artifact_{artifact_id}_v{artifact['version']}"  # Versioned document_id
                }
            )
            
            # Update Curator registration
            curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
            if curator:
                try:
                    await curator.update_artifact(
                        artifact_id=artifact_id,
                        artifact_data=artifact,
                        user_context=user_context
                    )
                    self.logger.info(f"✅ Journey artifact updated in Curator: {artifact_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update artifact in Curator: {e}")
            
            result = {
                "success": True,
                "artifact": artifact,
                "status_transition": f"{current_status} → {new_status}"
            }
            
            # Record health metric
            await self.record_health_metric("update_journey_artifact_status_success", 1.0, {
                "artifact_id": artifact_id,
                "status_transition": f"{current_status} → {new_status}"
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "update_journey_artifact_status_complete",
                success=True,
                details={"artifact_id": artifact_id, "status_transition": f"{current_status} → {new_status}"}
            )
            
            self.logger.info(f"✅ Journey artifact status updated: {artifact_id} ({current_status} → {new_status})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "update_journey_artifact_status", details={"artifact_id": artifact_id})
            
            # Record health metric (failure)
            await self.record_health_metric("update_journey_artifact_status_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "update_journey_artifact_status_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Update journey artifact status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_artifact_version(
        self,
        artifact_id: str,
        version: int,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a specific version of a Journey artifact.
        
        Args:
            artifact_id: Artifact ID
            version: Version number to retrieve
            user_context: User context for security and tenant validation
        
        Returns:
            Artifact data for the specified version
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_artifact_version_start",
            success=True,
            details={"artifact_id": artifact_id, "version": version}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_journey_artifact_version", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_artifact_version",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_journey_artifact_version_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Try to retrieve versioned document from Content Steward
            versioned_doc = await self.retrieve_document(f"journey_artifact_{artifact_id}_v{version}")
            
            if versioned_doc and "document" in versioned_doc:
                artifact = versioned_doc["document"]
                
                result = {
                    "success": True,
                    "artifact": artifact,
                    "version": version
                }
                
                # End telemetry tracking
                await self.log_operation_with_telemetry(
                    "get_journey_artifact_version_complete",
                    success=True,
                    details={"artifact_id": artifact_id, "version": version}
                )
                
                return result
            
            # If versioned document not found, try to get current artifact and check version
            artifact_result = await self.get_journey_artifact(artifact_id, user_context)
            if artifact_result.get("success"):
                artifact = artifact_result["artifact"]
                if artifact.get("version") == version:
                    return artifact_result
                else:
                    return {
                        "success": False,
                        "error": f"Version {version} not found. Current version is {artifact.get('version')}"
                    }
            
            return {
                "success": False,
                "error": f"Artifact {artifact_id} version {version} not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_artifact_version", details={"artifact_id": artifact_id, "version": version})
            
            # Record health metric (failure)
            await self.record_health_metric("get_journey_artifact_version_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_journey_artifact_version_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get journey artifact version failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_artifact_versions(
        self,
        artifact_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all versions of a Journey artifact.
        
        Args:
            artifact_id: Artifact ID
            user_context: User context for security and tenant validation
        
        Returns:
            List of all versions with metadata
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_artifact_versions_start",
            success=True,
            details={"artifact_id": artifact_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_journey_artifact_versions", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_artifact_versions",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_journey_artifact_versions_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get current artifact to get version info
            artifact_result = await self.get_journey_artifact(artifact_id, user_context)
            if not artifact_result.get("success"):
                return artifact_result
            
            current_artifact = artifact_result["artifact"]
            current_version = current_artifact.get("version", 1)
            
            # Build version list (for now, we only have the current version)
            # In future, we can enhance this to query all versioned documents
            versions = [
                {
                    "version": current_version,
                    "status": current_artifact.get("status"),
                    "updated_at": current_artifact.get("updated_at"),
                    "created_at": current_artifact.get("created_at")
                }
            ]
            
            result = {
                "success": True,
                "artifact_id": artifact_id,
                "versions": versions,
                "current_version": current_version,
                "total_versions": len(versions)
            }
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "get_journey_artifact_versions_complete",
                success=True,
                details={"artifact_id": artifact_id, "total_versions": len(versions)}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_artifact_versions", details={"artifact_id": artifact_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_journey_artifact_versions_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_journey_artifact_versions_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get journey artifact versions failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "journey_templates": len(self.journey_templates),
            "active_journeys": len(self.active_journeys),
            "experience_services_available": {
                "frontend_gateway": self.frontend_gateway is not None,
                "user_experience": self.user_experience is not None,
                "session_manager": self.session_manager is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_journey_from_artifact(
        self,
        artifact_id: str,
        client_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create operational Journey from approved artifact.
        
        This is the bridge from MVP artifact to operational journey.
        
        Flow:
        1. Retrieve artifact (must be "approved")
        2. Validate artifact is approved and client_id matches
        3. Create Journey from artifact data
        4. Update artifact status to "implemented"
        5. Link artifact to journey
        
        Args:
            artifact_id: Artifact ID
            client_id: Client ID (must match artifact client_id)
            user_context: User context for security and tenant validation
        
        Returns:
            Journey creation result with journey_id and artifact_id
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_journey_from_artifact_start",
            success=True,
            details={"artifact_id": artifact_id, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "create_journey_from_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "create_journey_from_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("create_journey_from_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # 1. Get artifact
            artifact_result = await self.get_journey_artifact(artifact_id, user_context)
            if not artifact_result.get("success"):
                result = {
                    "success": False,
                    "error": artifact_result.get("error", "Failed to retrieve artifact")
                }
                await self.log_operation_with_telemetry("create_journey_from_artifact_complete", success=False)
                return result
            
            artifact = artifact_result["artifact"]
            
            # 2. Validate client_id
            artifact_client_id = artifact.get("client_id")
            if artifact_client_id != client_id:
                result = {
                    "success": False,
                    "error": f"Artifact client_id mismatch: expected {client_id}, got {artifact_client_id}"
                }
                await self.log_operation_with_telemetry("create_journey_from_artifact_complete", success=False)
                return result
            
            # 3. Validate status is "approved"
            artifact_status = artifact.get("status")
            if artifact_status != "approved":
                result = {
                    "success": False,
                    "error": f"Artifact must be 'approved' to implement. Current status: {artifact_status}"
                }
                await self.log_operation_with_telemetry("create_journey_from_artifact_complete", success=False)
                return result
            
            # 4. Create Journey from artifact data
            artifact_data = artifact.get("data", {})
            artifact_type = artifact.get("artifact_type")
            
            # Map artifact_type to journey_type
            # For MVP artifacts, we'll use the artifact_type as journey_type
            # or map to a known journey template
            journey_type = artifact_type  # Use artifact_type as journey_type
            
            # If artifact_type doesn't match a known template, use a generic template
            if journey_type not in self.journey_templates:
                # Use workflow as default template for MVP artifacts
                journey_type = "workflow"
                self.logger.info(f"⚠️ Artifact type '{artifact_type}' not found in templates, using 'workflow' template")
            
            # Create journey using design_journey
            # Extract requirements from artifact_data
            requirements = artifact_data.get("requirements", artifact_data)
            # Ensure client_id is in requirements for journey creation
            if "client_id" not in requirements:
                requirements["client_id"] = client_id
            
            journey_result = await self.design_journey(
                journey_type=journey_type,
                requirements=requirements,
                user_context=user_context
            )
            
            if not journey_result.get("success"):
                result = {
                    "success": False,
                    "error": journey_result.get("error", "Failed to create journey from artifact")
                }
                await self.log_operation_with_telemetry("create_journey_from_artifact_complete", success=False)
                return result
            
            journey = journey_result["journey"]
            journey_id = journey["journey_id"]
            
            # Ensure client_id is stored in journey
            journey["client_id"] = client_id
            
            # Update journey document with client_id
            await self.store_document(
                document_data=journey,
                metadata={
                    "type": "journey_definition",
                    "journey_id": journey_id,
                    "journey_type": journey_type,
                    "client_id": client_id
                }
            )
            
            # 5. Update artifact status to "implemented"
            status_result = await self.update_journey_artifact_status(
                artifact_id=artifact_id,
                new_status="implemented",
                user_context=user_context
            )
            
            if not status_result.get("success"):
                # Log warning but continue - journey is created
                self.logger.warning(f"⚠️ Failed to update artifact status to 'implemented': {status_result.get('error')}")
            
            # 6. Link artifact to journey
            # Get updated artifact
            updated_artifact_result = await self.get_journey_artifact(artifact_id, user_context)
            if updated_artifact_result.get("success"):
                updated_artifact = updated_artifact_result["artifact"]
                updated_artifact["journey_id"] = journey_id
                
                # Store updated artifact with journey_id link
                await self.store_document(
                    document_data=updated_artifact,
                    metadata={
                        "type": "journey_artifact",
                        "artifact_id": artifact_id,
                        "journey_id": journey_id,
                        "status": "implemented",
                        "document_id": f"journey_artifact_{artifact_id}"
                    }
                )
                
                # Update in Curator
                curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
                if curator:
                    try:
                        await curator.update_artifact(
                            artifact_id=artifact_id,
                            artifact_data=updated_artifact,
                            user_context=user_context
                        )
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to update artifact in Curator: {e}")
            
            result = {
                "success": True,
                "journey_id": journey_id,
                "artifact_id": artifact_id,
                "status": "implemented",
                "journey": journey
            }
            
            # Record health metric
            await self.record_health_metric("create_journey_from_artifact_success", 1.0, {
                "journey_id": journey_id,
                "artifact_id": artifact_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "create_journey_from_artifact_complete",
                success=True,
                details={"journey_id": journey_id, "artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Journey created from artifact: {journey_id} (artifact: {artifact_id})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_journey_from_artifact", details={"artifact_id": artifact_id})
            
            # Record health metric (failure)
            await self.record_health_metric("create_journey_from_artifact_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "create_journey_from_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Create journey from artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "journey_service",
            "realm": "journey",
            "layer": "journey_orchestration",
            "capabilities": ["journey_orchestration", "journey_design", "journey_execution", "milestone_management", "artifact_storage"],
            "soa_apis": [
                "design_journey", "get_journey_template", "customize_journey",
                "execute_journey", "advance_journey_step", "get_journey_status",
                "pause_journey", "resume_journey", "cancel_journey", "get_available_journey_types",
                "create_journey_artifact", "get_journey_artifact", "update_journey_artifact_status",
                "get_journey_artifact_version", "get_journey_artifact_versions",  # Week 2.2
                "create_journey_from_artifact"  # NEW - Week 5.2
            ],
            "mcp_tools": [],
            "composes": "experience_services",
            "journey_templates": list(self.journey_templates.keys())
        }

