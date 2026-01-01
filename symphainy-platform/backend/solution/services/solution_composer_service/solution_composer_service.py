#!/usr/bin/env python3
"""
Solution Composer Service

WHAT: Designs and executes complete, multi-journey solutions
HOW: Composes Journey services (Structured, Session, MVP orchestrators) into multi-phase solutions

This service provides solution composition by orchestrating multiple journeys
across solution phases (Discovery, Migration, Validation, etc.) to deliver
complete end-to-end solutions.

Use this to: Compose journeys into solutions, execute multi-phase solutions, track solution progress
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SolutionComposerService(RealmServiceBase):
    """
    Solution Composer Service for Solution realm.
    
    Designs and executes complete, multi-journey solutions by composing
    Journey services (Structured, Session, MVP orchestrators) into phases.
    
    Provides end-to-end solution orchestration for complex, multi-phase use cases.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Solution Composer Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.conductor = None
        self.librarian = None
        self.data_steward = None
        
        # Journey services (discovered via Curator)
        self.structured_journey_orchestrator = None
        self.session_journey_orchestrator = None
        self.mvp_journey_orchestrator = None
        self.journey_analytics = None
        
        # Solution templates and active solutions
        self.solution_templates: Dict[str, Dict[str, Any]] = {}
        self.active_solutions: Dict[str, Dict[str, Any]] = {}
        
        # Specialist agents (lazy initialization)
        self._coexistence_strategy_agent = None
    
    async def initialize(self) -> bool:
        """
        Initialize Solution Composer Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "solution_composer_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.conductor = await self.get_conductor_api()
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            
            # 2. Discover Journey services via Curator
            await self._discover_journey_services()
            
            # 3. Load solution templates
            await self._load_solution_templates()
            
            # 4. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "solution_composition",
                        "protocol": "SolutionComposerProtocol",
                        "description": "Design and execute complete multi-journey solutions",
                        "contracts": {
                            "soa_api": {
                                "api_name": "design_solution",
                                "endpoint": "/api/v1/solution/composer/design",
                                "method": "POST",
                                "handler": self.design_solution,
                                "metadata": {
                                    "description": "Design a solution from template",
                                    "parameters": ["solution_type", "requirements", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.design",
                            "semantic_api": "/api/v1/solution/composer/design",
                            "user_journey": "design_solution"
                        }
                    },
                    {
                        "name": "solution_design",
                        "protocol": "SolutionComposerProtocol",
                        "description": "Get solution templates and customize solutions",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_solution_template",
                                "endpoint": "/api/v1/solution/composer/template",
                                "method": "GET",
                                "handler": self.get_solution_template,
                                "metadata": {
                                    "description": "Get solution template definition",
                                    "parameters": ["template_name", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.get_template",
                            "semantic_api": "/api/v1/solution/composer/template",
                            "user_journey": "get_solution_template"
                        }
                    },
                    {
                        "name": "solution_execution",
                        "protocol": "SolutionComposerProtocol",
                        "description": "Deploy and execute solution phases",
                        "contracts": {
                            "soa_api": {
                                "api_name": "deploy_solution",
                                "endpoint": "/api/v1/solution/composer/deploy",
                                "method": "POST",
                                "handler": self.deploy_solution,
                                "metadata": {
                                    "description": "Deploy a solution for a user",
                                    "parameters": ["solution_id", "user_id", "context", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.deploy",
                            "semantic_api": "/api/v1/solution/composer/deploy",
                            "user_journey": "deploy_solution"
                        }
                    },
                    {
                        "name": "multi_phase_orchestration",
                        "protocol": "SolutionComposerProtocol",
                        "description": "Execute solution phases and manage solution lifecycle",
                        "contracts": {
                            "soa_api": {
                                "api_name": "execute_solution_phase",
                                "endpoint": "/api/v1/solution/composer/execute-phase",
                                "method": "POST",
                                "handler": self.execute_solution_phase,
                                "metadata": {
                                    "description": "Execute a specific solution phase",
                                    "parameters": ["solution_id", "phase_id", "user_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.execute_phase",
                            "semantic_api": "/api/v1/solution/composer/execute-phase",
                            "user_journey": "execute_solution_phase"
                        }
                    }
                ],
                soa_apis=[
                    "design_solution", "get_solution_template", "customize_solution",
                    "deploy_solution", "execute_solution_phase", "get_solution_status",
                    "pause_solution", "resume_solution", "cancel_solution", "get_available_solution_types"
                ],
                mcp_tools=[]  # Solution services provide SOA APIs, not MCP tools
            )
            
            # Record health metric
            await self.record_health_metric(
                "solution_composer_initialized",
                1.0,
                {"service": self.service_name, "templates": len(self.solution_templates)}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "solution_composer_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Solution Composer Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "solution_composer_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "solution_composer_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Solution Composer Service initialization failed: {e}")
            return False
    
    async def _discover_journey_services(self):
        """Discover Journey services via Curator."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            
            if curator:
                try:
                    self.structured_journey_orchestrator = await curator.get_service("StructuredJourneyOrchestratorService")
                    self.logger.info("✅ Discovered StructuredJourneyOrchestratorService")
                except Exception:
                    self.logger.warning("⚠️ StructuredJourneyOrchestratorService not yet available")
                
                try:
                    self.session_journey_orchestrator = await curator.get_service("SessionJourneyOrchestratorService")
                    self.logger.info("✅ Discovered SessionJourneyOrchestratorService")
                except Exception:
                    self.logger.warning("⚠️ SessionJourneyOrchestratorService not yet available")
                
                try:
                    self.mvp_journey_orchestrator = await curator.get_service("MVPJourneyOrchestratorService")
                    self.logger.info("✅ Discovered MVPJourneyOrchestratorService")
                except Exception:
                    self.logger.warning("⚠️ MVPJourneyOrchestratorService not yet available")
                
                try:
                    self.journey_analytics = await curator.get_service("JourneyAnalyticsService")
                    self.logger.info("✅ Discovered JourneyAnalyticsService")
                except Exception:
                    self.logger.warning("⚠️ JourneyAnalyticsService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Journey service discovery failed: {e}")
    
    async def _load_solution_templates(self):
        """Load solution templates (predefined solution structures)."""
        # Enterprise Migration Solution Template
        self.solution_templates["enterprise_migration"] = {
            "template_name": "Enterprise Migration Solution",
            "description": "Complete enterprise content migration with discovery, migration, and validation",
            "phases": [
                {
                    "phase_id": "discovery",
                    "phase_name": "Discovery & Assessment",
                    "journey_type": "structured",
                    "journey_template": "content_discovery",
                    "required": True,
                    "estimated_duration_hours": 40,
                    "next_phases": ["migration"]
                },
                {
                    "phase_id": "migration",
                    "phase_name": "Content Migration",
                    "journey_type": "structured",
                    "journey_template": "content_migration",
                    "required": True,
                    "estimated_duration_hours": 120,
                    "next_phases": ["validation"]
                },
                {
                    "phase_id": "validation",
                    "phase_name": "Quality Validation",
                    "journey_type": "structured",
                    "journey_template": "quality_validation",
                    "required": True,
                    "estimated_duration_hours": 24,
                    "completion": True
                }
            ]
        }
        
        # MVP Solution Template
        self.solution_templates["mvp_solution"] = {
            "template_name": "MVP Solution",
            "description": "MVP solution with free-form navigation across 4 pillars",
            "phases": [
                {
                    "phase_id": "mvp_journey",
                    "phase_name": "MVP User Journey",
                    "journey_type": "mvp",
                    "journey_template": "mvp",  # Uses MVPJourneyOrchestratorService
                    "required": True,
                    "completion": True
                }
            ]
        }
        
        # Data Analytics Solution Template
        self.solution_templates["data_analytics"] = {
            "template_name": "Data Analytics Solution",
            "description": "End-to-end data analytics with insights generation and visualization",
            "phases": [
                {
                    "phase_id": "data_preparation",
                    "phase_name": "Data Preparation",
                    "journey_type": "structured",
                    "journey_template": "content_migration",
                    "required": True,
                    "next_phases": ["analysis"]
                },
                {
                    "phase_id": "analysis",
                    "phase_name": "Data Analysis",
                    "journey_type": "structured",
                    "journey_template": "insights_generation",
                    "required": True,
                    "next_phases": ["optimization"]
                },
                {
                    "phase_id": "optimization",
                    "phase_name": "Process Optimization",
                    "journey_type": "structured",
                    "journey_template": "operations_optimization",
                    "required": True,
                    "completion": True
                }
            ]
        }
        
        # ⭐ Insurance Migration Solution Template (NEW)
        try:
            from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_templates.solution_composer_templates import INSURANCE_MIGRATION_SOLUTION
            self.solution_templates["insurance_migration"] = INSURANCE_MIGRATION_SOLUTION
            self.logger.info("✅ Loaded Insurance Migration Solution template")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load Insurance Migration Solution template: {e}")
        
            self.logger.info(f"✅ Loaded {len(self.solution_templates)} solution templates")
    
    async def _get_coexistence_strategy_agent(self):
        """Lazy initialization of Coexistence Strategy Specialist Agent."""
        if self._coexistence_strategy_agent is None:
            try:
                # Get Agentic Foundation Service
                agentic_foundation = self.di_container.get_foundation_service("AgenticFoundationService")
                if agentic_foundation:
                    from backend.business_enablement.agents.specialists.coexistence_strategy_specialist import CoexistenceStrategySpecialist
                    
                    self._coexistence_strategy_agent = await agentic_foundation.create_agent(
                        agent_class=CoexistenceStrategySpecialist,
                        agent_name="CoexistenceStrategySpecialist",
                        agent_type="specialist",
                        realm_name=self.realm_name,
                        di_container=self.di_container,
                        orchestrator=None  # Service, not orchestrator
                    )
                    
                    if self._coexistence_strategy_agent:
                        self.logger.debug("✅ Coexistence Strategy Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Coexistence Strategy Specialist Agent not available: {e}")
        
        return self._coexistence_strategy_agent
    
    # ========================================================================
    # SOA APIs (Solution Design)
    # ========================================================================
    
    async def design_solution(
        self,
        solution_type: str,
        requirements: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design a solution from template (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            solution_type: Type of solution (enterprise_migration, mvp_solution, etc.)
            requirements: Solution requirements and customizations
            user_context: User context for security and tenant validation
        
        Returns:
            Solution definition
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "design_solution_start",
            success=True,
            details={"solution_type": solution_type}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "design_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "design_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("design_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("design_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Check if tenant management is configured (multi-tenancy enabled)
                # If not configured, allow access by default (open by default)
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "design_solution",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("design_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("design_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get template
            if solution_type not in self.solution_templates:
                result = {
                    "success": False,
                    "error": f"Solution type '{solution_type}' not found"
                }
                await self.log_operation_with_telemetry("design_solution_complete", success=False, details={"error": result["error"]})
                return result
            
            template = self.solution_templates[solution_type]
            
            # Get Coexistence Strategy Agent for insurance migration solutions
            coexistence_strategy = None
            if solution_type == "insurance_migration":
                coexistence_agent = await self._get_coexistence_strategy_agent()
                if coexistence_agent:
                    try:
                        # Get current state and target state from requirements
                        current_state = requirements.get("current_state", {})
                        target_state = requirements.get("target_state", {})
                        
                        if current_state or target_state:
                            strategy_result = await coexistence_agent.plan_coexistence_strategy(
                                current_state=current_state,
                                target_state=target_state,
                                constraints=requirements.get("constraints"),
                                user_context=user_context
                            )
                            
                            if strategy_result.get("success"):
                                coexistence_strategy = strategy_result.get("recommended_strategy", {})
                                self.logger.info(f"✅ Coexistence strategy planned: {coexistence_strategy.get('strategy', 'N/A')}")
                    except Exception as e:
                        self.logger.debug(f"Coexistence strategy planning not available: {e}")
            
            # Create solution from template
            solution_id = str(uuid.uuid4())
            solution = {
                "solution_id": solution_id,
                "solution_type": solution_type,
                "solution_name": template["template_name"],
                "description": template["description"],
                "phases": template["phases"],
                "requirements": requirements,
                "coexistence_strategy": coexistence_strategy,  # Add AI-generated strategy
                "created_at": datetime.utcnow().isoformat(),
                "status": "designed",
                "user_id": user_context.get("user_id") if user_context else None,
                "tenant_id": user_context.get("tenant_id") if user_context else None
            }
            
            # Store solution via Librarian
            await self.store_document(
                document_data=solution,
                metadata={
                    "type": "solution_definition",
                    "solution_id": solution_id,
                    "solution_type": solution_type
                }
            )
            
            result = {
                "success": True,
                "solution": solution
            }
            
            # Record health metric (success)
            await self.record_health_metric("design_solution_success", 1.0, {"solution_id": solution_id, "solution_type": solution_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("design_solution_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution designed: {solution_id} ({solution_type})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "design_solution", details={"solution_type": solution_type})
            
            # Record health metric (failure)
            await self.record_health_metric("design_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("design_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Design solution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_template(
        self,
        template_name: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get solution template (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            template_name: Name of template
            user_context: User context for security and tenant validation
        
        Returns:
            Solution template
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_template_start",
            success=True,
            details={"template_name": template_name}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_template", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_template",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_template_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_template_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_solution_template",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_solution_template_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_solution_template_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if template_name in self.solution_templates:
                result = {
                    "success": True,
                    "template": self.solution_templates[template_name]
                }
                
                # Record health metric (success)
                await self.record_health_metric("get_solution_template_success", 1.0, {"template_name": template_name})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_solution_template_complete", success=True, details={"template_name": template_name})
                
                return result
            
            result = {
                "success": False,
                "error": f"Template '{template_name}' not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_template_complete", success=False, details={"error": result["error"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_template", details={"template_name": template_name})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_template_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_template_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def customize_solution(
        self,
        solution_id: str,
        customizations: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Customize an existing solution (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            solution_id: Solution ID
            customizations: Customizations to apply
            user_context: User context for security and tenant validation
        
        Returns:
            Customized solution
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "customize_solution_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "customize_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "customize_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("customize_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("customize_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "customize_solution",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("customize_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("customize_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get solution
            solution_doc = await self.retrieve_document(f"solution_{solution_id}")
            
            if not solution_doc or "document" not in solution_doc:
                result = {
                    "success": False,
                    "error": "Solution not found"
                }
                await self.log_operation_with_telemetry("customize_solution_complete", success=False, details={"error": result["error"]})
                return result
            
            solution = solution_doc["document"]
            
            # Apply customizations
            for key, value in customizations.items():
                if key in solution:
                    solution[key] = value
            
            # Update solution
            await self.store_document(
                document_data=solution,
                metadata={
                    "type": "solution_definition",
                    "solution_id": solution_id,
                    "customized_at": datetime.utcnow().isoformat()
                }
            )
            
            result = {
                "success": True,
                "solution": solution
            }
            
            # Record health metric (success)
            await self.record_health_metric("customize_solution_success", 1.0, {"solution_id": solution_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("customize_solution_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution customized: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "customize_solution", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("customize_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("customize_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Customize solution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Solution Execution)
    # ========================================================================
    
    async def deploy_solution(
        self,
        solution_id: str,
        user_id: str,
        context: Dict[str, Any],
        client_id: Optional[str] = None,  # NEW - Week 6: Client-scoped execution
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deploy a solution for a user (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        - Client-scoped execution validation (NEW - Week 6)
        
        Args:
            solution_id: Solution ID
            user_id: User ID
            context: Deployment context
            client_id: Client ID for client-scoped execution (optional, can be in context)
            user_context: User context for security and tenant validation
        
        Returns:
            Solution deployment result
        """
        # Extract client_id from context if not provided
        if not client_id:
            client_id = context.get("client_id")
        
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "deploy_solution_start",
            success=True,
            details={"solution_id": solution_id, "user_id": user_id, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "deploy_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "deploy_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("deploy_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("deploy_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "deploy_solution",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("deploy_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("deploy_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get solution definition
            solution_doc = await self.retrieve_document(f"solution_{solution_id}")
            
            if not solution_doc or "document" not in solution_doc:
                result = {
                    "success": False,
                    "error": "Solution not found"
                }
                await self.log_operation_with_telemetry("deploy_solution_complete", success=False, details={"error": result["error"]})
                return result
            
            solution = solution_doc["document"]
            
            # NEW - Week 6: Client-scoped execution validation
            if client_id:
                solution_client_id = solution.get("client_id")
                if solution_client_id and solution_client_id != client_id:
                    result = {
                        "success": False,
                        "error": f"Solution client_id mismatch: expected {client_id}, got {solution_client_id}"
                    }
                    await self.log_operation_with_telemetry("deploy_solution_complete", success=False, details={"error": result["error"]})
                    return result
                # Ensure client_id is in context for downstream operations
                context["client_id"] = client_id
            
            # Initialize solution deployment
            deployment = {
                "solution_id": solution_id,
                "user_id": user_id,
                "client_id": client_id,  # NEW - Week 6: Store client_id in deployment
                "status": "deploying",
                "started_at": datetime.utcnow().isoformat(),
                "current_phase": solution["phases"][0]["phase_id"] if solution["phases"] else None,
                "completed_phases": [],
                "phase_results": {},
                "context": context,
                "tenant_id": user_context.get("tenant_id") if user_context else None
            }
            
            # Store in active solutions
            self.active_solutions[f"{solution_id}_{user_id}"] = deployment
            
            # Store via Librarian
            await self.store_document(
                document_data=deployment,
                metadata={
                    "type": "solution_deployment",
                    "solution_id": solution_id,
                    "user_id": user_id
                }
            )
            
            result = {
                "success": True,
                "deployment": deployment,
                "next_phase": solution["phases"][0] if solution["phases"] else None
            }
            
            # Record health metric (success)
            await self.record_health_metric("deploy_solution_success", 1.0, {"solution_id": solution_id, "user_id": user_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("deploy_solution_complete", success=True, details={"solution_id": solution_id, "user_id": user_id})
            
            self.logger.info(f"✅ Solution deployment started: {solution_id} for user {user_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "deploy_solution", details={"solution_id": solution_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("deploy_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("deploy_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Deploy solution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_solution_phase(
        self,
        solution_id: str,
        phase_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific solution phase (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            solution_id: Solution ID
            phase_id: Phase ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Phase execution result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "execute_solution_phase_start",
            success=True,
            details={"solution_id": solution_id, "phase_id": phase_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "execute_solution_phase", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "execute_solution_phase",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("execute_solution_phase_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("execute_solution_phase_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "execute_solution_phase",
                    details={"tenant_id": tenant_id}
                )
                            await self.record_health_metric("execute_solution_phase_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("execute_solution_phase_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get solution
            solution_doc = await self.retrieve_document(f"solution_{solution_id}")
            solution = solution_doc["document"]
            
            # Get deployment
            key = f"{solution_id}_{user_id}"
            if key not in self.active_solutions:
                return {
                    "success": False,
                    "error": "Deployment not found"
                }
            
            deployment = self.active_solutions[key]
            
            # Find phase
            phase = next((p for p in solution["phases"] if p["phase_id"] == phase_id), None)
            if not phase:
                return {
                    "success": False,
                    "error": f"Phase '{phase_id}' not found"
                }
            
            # Get appropriate journey orchestrator
            orchestrator = None
            if phase["journey_type"] == "structured":
                orchestrator = self.structured_journey_orchestrator
            elif phase["journey_type"] == "session":
                orchestrator = self.session_journey_orchestrator
            elif phase["journey_type"] == "mvp":
                orchestrator = self.mvp_journey_orchestrator
            
            if not orchestrator:
                return {
                    "success": False,
                    "error": f"Orchestrator for journey type '{phase['journey_type']}' not available"
                }
            
            # Execute phase journey
            if phase["journey_type"] == "mvp":
                # MVP uses different API
                journey_result = await orchestrator.start_mvp_journey(
                    user_id=user_id,
                    initial_pillar="content"
                )
            else:
                # Structured/Session use standard API
                journey_design = await orchestrator.design_journey(
                    phase.get("journey_template", "default"),
                    deployment["context"]
                )
                
                journey_result = await orchestrator.execute_journey(
                    journey_design["journey"]["journey_id"],
                    user_id,
                    deployment["context"]
                )
            
            # Track phase completion
            deployment["completed_phases"].append(phase_id)
            deployment["phase_results"][phase_id] = journey_result
            
            # Check if phase completes solution
            if phase.get("completion"):
                deployment["status"] = "completed"
                deployment["completed_at"] = datetime.utcnow().isoformat()
            else:
                # Move to next phase
                next_phases = phase.get("next_phases", [])
                if next_phases:
                    deployment["current_phase"] = next_phases[0]
            
            # Update cache
            self.active_solutions[key] = deployment
            
            # Persist
            await self.store_document(
                document_data=deployment,
                metadata={
                    "type": "solution_deployment",
                    "solution_id": solution_id,
                    "user_id": user_id,
                    "phase_id": phase_id,
                    "status": deployment["status"]
                }
            )
            
            result = {
                "success": True,
                "phase_result": journey_result,
                "deployment": deployment
            }
            
            # Record health metric (success)
            await self.record_health_metric("execute_solution_phase_success", 1.0, {"solution_id": solution_id, "phase_id": phase_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("execute_solution_phase_complete", success=True, details={"solution_id": solution_id, "phase_id": phase_id})
            
            self.logger.info(f"✅ Phase executed: {phase_id} for solution {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "execute_solution_phase", details={"solution_id": solution_id, "phase_id": phase_id})
            
            # Record health metric (failure)
            await self.record_health_metric("execute_solution_phase_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("execute_solution_phase_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Execute solution phase failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_status(
        self,
        solution_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get solution deployment status (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            solution_id: Solution ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Solution status
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_status_start",
            success=True,
            details={"solution_id": solution_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_status", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_status",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_status_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_solution_status",
                    details={"tenant_id": tenant_id}
                )
                            await self.record_health_metric("get_solution_status_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_solution_status_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            key = f"{solution_id}_{user_id}"
            
            if key in self.active_solutions:
                deployment = self.active_solutions[key]
                
                result = {
                    "success": True,
                    "deployment": deployment
                }
                
                # Record health metric (success)
                await self.record_health_metric("get_solution_status_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_solution_status_complete", success=True, details={"solution_id": solution_id})
                
                return result
            
            # Try to retrieve from storage
            results = await self.search_documents(
                "solution_deployment",
                {"type": "solution_deployment", "solution_id": solution_id, "user_id": user_id}
            )
            
            if results and len(results) > 0:
                deployment = results[0].get("document") if isinstance(results[0], dict) else results[0]
                
                result = {
                    "success": True,
                    "deployment": deployment
                }
                
                # Record health metric (success)
                await self.record_health_metric("get_solution_status_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_solution_status_complete", success=True, details={"solution_id": solution_id})
                
                return result
            
            result = {
                "success": False,
                "error": "Deployment not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_status_complete", success=False, details={"error": result["error"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_status", details={"solution_id": solution_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_status_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_status_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get solution status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Solution Management)
    # ========================================================================
    
    async def pause_solution(
        self,
        solution_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pause solution deployment (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "pause_solution_start",
            success=True,
            details={"solution_id": solution_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "pause_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "pause_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("pause_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("pause_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "pause_solution",
                    details={"tenant_id": tenant_id}
                )
                            await self.record_health_metric("pause_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("pause_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            key = f"{solution_id}_{user_id}"
            if key in self.active_solutions:
                self.active_solutions[key]["status"] = "paused"
                self.active_solutions[key]["paused_at"] = datetime.utcnow().isoformat()
                
                result = {
                    "success": True,
                    "status": "paused"
                }
                
                # Record health metric (success)
                await self.record_health_metric("pause_solution_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("pause_solution_complete", success=True, details={"solution_id": solution_id})
                
                self.logger.info(f"✅ Solution paused: {solution_id}")
                
                return result
            
            result = {
                "success": False,
                "error": "Deployment not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("pause_solution_complete", success=False, details={"error": result["error"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "pause_solution", details={"solution_id": solution_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("pause_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("pause_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Pause solution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def resume_solution(
        self,
        solution_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resume paused solution (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "resume_solution_start",
            success=True,
            details={"solution_id": solution_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "resume_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "resume_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("resume_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("resume_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "resume_solution",
                    details={"tenant_id": tenant_id}
                )
                            await self.record_health_metric("resume_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("resume_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            key = f"{solution_id}_{user_id}"
            if key in self.active_solutions:
                self.active_solutions[key]["status"] = "deploying"
                self.active_solutions[key]["resumed_at"] = datetime.utcnow().isoformat()
                
                result = {
                    "success": True,
                    "status": "deploying"
                }
                
                # Record health metric (success)
                await self.record_health_metric("resume_solution_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("resume_solution_complete", success=True, details={"solution_id": solution_id})
                
                self.logger.info(f"✅ Solution resumed: {solution_id}")
                
                return result
            
            result = {
                "success": False,
                "error": "Deployment not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("resume_solution_complete", success=False, details={"error": result["error"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "resume_solution", details={"solution_id": solution_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("resume_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("resume_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Resume solution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_solution(
        self,
        solution_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cancel solution deployment (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "cancel_solution_start",
            success=True,
            details={"solution_id": solution_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "cancel_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "cancel_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("cancel_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("cancel_solution_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "cancel_solution",
                    details={"tenant_id": tenant_id}
                )
                            await self.record_health_metric("cancel_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("cancel_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            key = f"{solution_id}_{user_id}"
            if key in self.active_solutions:
                self.active_solutions[key]["status"] = "cancelled"
                self.active_solutions[key]["cancelled_at"] = datetime.utcnow().isoformat()
                
                # Remove from active solutions
                del self.active_solutions[key]
                
                result = {
                    "success": True,
                    "status": "cancelled"
                }
                
                # Record health metric (success)
                await self.record_health_metric("cancel_solution_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("cancel_solution_complete", success=True, details={"solution_id": solution_id})
                
                self.logger.info(f"✅ Solution cancelled: {solution_id}")
                
                return result
            
            result = {
                "success": False,
                "error": "Deployment not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("cancel_solution_complete", success=False, details={"error": result["error"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "cancel_solution", details={"solution_id": solution_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("cancel_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("cancel_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Cancel solution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_solution_types(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get available solution types (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_available_solution_types_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_available_solution_types", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_available_solution_types",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_available_solution_types_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_available_solution_types_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Check if tenant management is configured (multi-tenancy enabled)
                # If not configured, allow access by default (open by default)
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_available_solution_types",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_available_solution_types_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_available_solution_types_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            result = {
                "success": True,
                "solution_types": list(self.solution_templates.keys()),
                "templates": {
                    name: {
                        "name": template["template_name"],
                        "description": template["description"],
                        "phases_count": len(template["phases"])
                    }
                    for name, template in self.solution_templates.items()
                }
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_available_solution_types_success", 1.0, {"count": len(self.solution_templates)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_available_solution_types_complete", success=True, details={"count": len(self.solution_templates)})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_available_solution_types")
            
            # Record health metric (failure)
            await self.record_health_metric("get_available_solution_types_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_available_solution_types_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # ARTIFACT STORAGE (Phase 1: Foundation)
    # ========================================================================
    
    async def create_solution_artifact(
        self,
        artifact_type: str,  # "migration_plan", "roadmap", "poc_proposal"
        artifact_data: Dict[str, Any],
        client_id: Optional[str] = None,
        status: str = "draft",  # draft → review → approved → implemented
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Solution artifact (not yet a solution).
        
        This is the foundation - artifacts are stored as solution-like structures
        but with status lifecycle.
        
        Args:
            artifact_type: Type of artifact (migration_plan, roadmap, poc_proposal)
            artifact_data: Artifact data (same structure as solution data)
            client_id: Client ID for client-scoped artifacts (optional)
            status: Artifact status (draft, review, approved, implemented, active)
            user_context: User context for security and tenant validation
        
        Returns:
            Created artifact with artifact_id
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_solution_artifact_start",
            success=True,
            details={"artifact_type": artifact_type, "status": status}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "create_solution_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "create_solution_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("create_solution_artifact_complete", success=False)
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
                "solution_id": None  # Will be set when artifact becomes solution
            }
            
            # Store via Librarian (persistent storage)
            await self.store_document(
                document_data=artifact,
                metadata={
                    "type": "solution_artifact",
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
                        artifact_type="solution",
                        artifact_data=artifact,
                        client_id=client_id,
                        user_context=user_context
                    )
                    self.logger.info(f"✅ Solution artifact registered with Curator: {artifact_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to register artifact with Curator: {e}")
            
            result = {
                "success": True,
                "artifact": artifact
            }
            
            # Record health metric
            await self.record_health_metric("create_solution_artifact_success", 1.0, {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "create_solution_artifact_complete",
                success=True,
                details={"artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Solution artifact created: {artifact_id} ({artifact_type}, status: {status})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_solution_artifact", details={"artifact_type": artifact_type})
            
            # Record health metric (failure)
            await self.record_health_metric("create_solution_artifact_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "create_solution_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Create solution artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_artifact(
        self,
        artifact_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve Solution artifact.
        
        Args:
            artifact_id: Artifact ID
            user_context: User context for security and tenant validation
        
        Returns:
            Artifact data
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_artifact_start",
            success=True,
            details={"artifact_id": artifact_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_solution_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Try to retrieve from Librarian
            artifact_doc = await self.retrieve_document(f"solution_artifact_{artifact_id}")
            
            if artifact_doc and "document" in artifact_doc:
                artifact = artifact_doc["document"]
                
                result = {
                    "success": True,
                    "artifact": artifact
                }
                
                # End telemetry tracking
                await self.log_operation_with_telemetry(
                    "get_solution_artifact_complete",
                    success=True,
                    details={"artifact_id": artifact_id}
                )
                
                return result
            
            # Try Curator as fallback
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    artifact = await curator.get_artifact(artifact_id, artifact_type="solution")
                    if artifact:
                        result = {
                            "success": True,
                            "artifact": artifact
                        }
                        await self.log_operation_with_telemetry("get_solution_artifact_complete", success=True)
                        return result
                except Exception as e:
                    self.logger.debug(f"Curator artifact retrieval failed: {e}")
            
            result = {
                "success": False,
                "error": "Artifact not found"
            }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_solution_artifact_complete",
                success=False,
                details={"error": result["error"]}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_artifact", details={"artifact_id": artifact_id})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_solution_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get solution artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_solution_artifact_status(
        self,
        artifact_id: str,
        new_status: str,  # draft → review → approved → implemented
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
            "update_solution_artifact_status_start",
            success=True,
            details={"artifact_id": artifact_id, "new_status": new_status}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "update_solution_artifact_status", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "update_solution_artifact_status",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("update_solution_artifact_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get artifact
            artifact_result = await self.get_solution_artifact(artifact_id, user_context)
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
                await self.log_operation_with_telemetry("update_solution_artifact_status_complete", success=False)
                return result
            
            if new_status not in valid_transitions.get(current_status, []):
                result = {
                    "success": False,
                    "error": f"Invalid status transition: {current_status} → {new_status}"
                }
                await self.log_operation_with_telemetry("update_solution_artifact_status_complete", success=False)
                return result
            
            # Update artifact
            artifact["status"] = new_status
            artifact["updated_at"] = datetime.utcnow().isoformat()
            artifact["version"] = artifact.get("version", 1) + 1
            
            # Store updated artifact (latest version)
            await self.store_document(
                document_data=artifact,
                metadata={
                    "type": "solution_artifact",
                    "artifact_id": artifact_id,
                    "status": new_status,
                    "previous_status": current_status,
                    "version": artifact["version"],
                    "document_id": f"solution_artifact_{artifact_id}"  # Consistent document_id for latest
                }
            )
            
            # Also store versioned copy for history
            await self.store_document(
                document_data=artifact,
                metadata={
                    "type": "solution_artifact_version",
                    "artifact_id": artifact_id,
                    "version": artifact["version"],
                    "status": new_status,
                    "previous_status": current_status,
                    "document_id": f"solution_artifact_{artifact_id}_v{artifact['version']}"  # Versioned document_id
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
                    self.logger.info(f"✅ Solution artifact updated in Curator: {artifact_id}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to update artifact in Curator: {e}")
            
            result = {
                "success": True,
                "artifact": artifact,
                "status_transition": f"{current_status} → {new_status}"
            }
            
            # Record health metric
            await self.record_health_metric("update_solution_artifact_status_success", 1.0, {
                "artifact_id": artifact_id,
                "status_transition": f"{current_status} → {new_status}"
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "update_solution_artifact_status_complete",
                success=True,
                details={"artifact_id": artifact_id, "status_transition": f"{current_status} → {new_status}"}
            )
            
            self.logger.info(f"✅ Solution artifact status updated: {artifact_id} ({current_status} → {new_status})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "update_solution_artifact_status", details={"artifact_id": artifact_id})
            
            # Record health metric (failure)
            await self.record_health_metric("update_solution_artifact_status_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "update_solution_artifact_status_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Update solution artifact status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_artifact_version(
        self,
        artifact_id: str,
        version: int,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a specific version of a Solution artifact.
        
        Args:
            artifact_id: Artifact ID
            version: Version number to retrieve
            user_context: User context for security and tenant validation
        
        Returns:
            Artifact data for the specified version
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_artifact_version_start",
            success=True,
            details={"artifact_id": artifact_id, "version": version}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_artifact_version", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_artifact_version",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_solution_artifact_version_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Try to retrieve versioned document from Content Steward
            # Note: Content Steward uses UUIDs, so we search by metadata
            versioned_doc = await self.retrieve_document(f"solution_artifact_{artifact_id}_v{version}")
            
            if versioned_doc and "document" in versioned_doc:
                artifact = versioned_doc["document"]
                
                result = {
                    "success": True,
                    "artifact": artifact,
                    "version": version
                }
                
                # End telemetry tracking
                await self.log_operation_with_telemetry(
                    "get_solution_artifact_version_complete",
                    success=True,
                    details={"artifact_id": artifact_id, "version": version}
                )
                
                return result
            
            # If versioned document not found, try to get current artifact and check version
            artifact_result = await self.get_solution_artifact(artifact_id, user_context)
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
            await self.handle_error_with_audit(e, "get_solution_artifact_version", details={"artifact_id": artifact_id, "version": version})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_artifact_version_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_solution_artifact_version_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get solution artifact version failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_artifact_versions(
        self,
        artifact_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all versions of a Solution artifact.
        
        Args:
            artifact_id: Artifact ID
            user_context: User context for security and tenant validation
        
        Returns:
            List of all versions with metadata
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_artifact_versions_start",
            success=True,
            details={"artifact_id": artifact_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_artifact_versions", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_artifact_versions",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_solution_artifact_versions_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get current artifact to get version info
            artifact_result = await self.get_solution_artifact(artifact_id, user_context)
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
                "get_solution_artifact_versions_complete",
                success=True,
                details={"artifact_id": artifact_id, "total_versions": len(versions)}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_artifact_versions", details={"artifact_id": artifact_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_artifact_versions_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_solution_artifact_versions_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get solution artifact versions failed: {e}")
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
            "solution_templates": len(self.solution_templates),
            "active_solutions": len(self.active_solutions),
            "journey_orchestrators_available": {
                "structured": self.structured_journey_orchestrator is not None,
                "session": self.session_journey_orchestrator is not None,
                "mvp": self.mvp_journey_orchestrator is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_solution_from_artifact(
        self,
        artifact_id: str,
        client_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create operational Solution from approved artifact.
        
        This is the bridge from MVP artifact to operational solution.
        
        Flow:
        1. Retrieve artifact (must be "approved")
        2. Validate artifact is approved and client_id matches
        3. Create Solution from artifact data
        4. Update artifact status to "implemented"
        5. Link artifact to solution
        
        Args:
            artifact_id: Artifact ID
            client_id: Client ID (must match artifact client_id)
            user_context: User context for security and tenant validation
        
        Returns:
            Solution creation result with solution_id and artifact_id
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_solution_from_artifact_start",
            success=True,
            details={"artifact_id": artifact_id, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "create_solution_from_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "create_solution_from_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("create_solution_from_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # 1. Get artifact
            artifact_result = await self.get_solution_artifact(artifact_id, user_context)
            if not artifact_result.get("success"):
                result = {
                    "success": False,
                    "error": artifact_result.get("error", "Failed to retrieve artifact")
                }
                await self.log_operation_with_telemetry("create_solution_from_artifact_complete", success=False)
                return result
            
            artifact = artifact_result["artifact"]
            
            # 2. Validate client_id
            artifact_client_id = artifact.get("client_id")
            if artifact_client_id != client_id:
                result = {
                    "success": False,
                    "error": f"Artifact client_id mismatch: expected {client_id}, got {artifact_client_id}"
                }
                await self.log_operation_with_telemetry("create_solution_from_artifact_complete", success=False)
                return result
            
            # 3. Validate status is "approved"
            artifact_status = artifact.get("status")
            if artifact_status != "approved":
                result = {
                    "success": False,
                    "error": f"Artifact must be 'approved' to implement. Current status: {artifact_status}"
                }
                await self.log_operation_with_telemetry("create_solution_from_artifact_complete", success=False)
                return result
            
            # 4. Create Solution from artifact data
            artifact_data = artifact.get("data", {})
            artifact_type = artifact.get("artifact_type")
            
            # Map artifact_type to solution_type
            # For MVP artifacts, we'll use the artifact_type as solution_type
            # or map to a known solution template
            solution_type = artifact_type  # Use artifact_type as solution_type
            
            # If artifact_type doesn't match a known template, use a generic template
            if solution_type not in self.solution_templates:
                # Use mvp_solution as default template for MVP artifacts
                solution_type = "mvp_solution"
                self.logger.info(f"⚠️ Artifact type '{artifact_type}' not found in templates, using 'mvp_solution' template")
            
            # Create solution using design_solution
            # Extract requirements from artifact_data
            requirements = artifact_data.get("requirements", artifact_data)
            # Ensure client_id is in requirements for solution creation
            if "client_id" not in requirements:
                requirements["client_id"] = client_id
            
            solution_result = await self.design_solution(
                solution_type=solution_type,
                requirements=requirements,
                user_context=user_context
            )
            
            if not solution_result.get("success"):
                result = {
                    "success": False,
                    "error": solution_result.get("error", "Failed to create solution from artifact")
                }
                await self.log_operation_with_telemetry("create_solution_from_artifact_complete", success=False)
                return result
            
            solution = solution_result["solution"]
            solution_id = solution["solution_id"]
            
            # Ensure client_id is stored in solution
            solution["client_id"] = client_id
            
            # Update solution document with client_id
            await self.store_document(
                document_data=solution,
                metadata={
                    "type": "solution_definition",
                    "solution_id": solution_id,
                    "solution_type": solution_type,
                    "client_id": client_id
                }
            )
            
            # 5. Update artifact status to "implemented"
            status_result = await self.update_solution_artifact_status(
                artifact_id=artifact_id,
                new_status="implemented",
                user_context=user_context
            )
            
            if not status_result.get("success"):
                # Log warning but continue - solution is created
                self.logger.warning(f"⚠️ Failed to update artifact status to 'implemented': {status_result.get('error')}")
            
            # 6. Link artifact to solution
            # Get updated artifact
            updated_artifact_result = await self.get_solution_artifact(artifact_id, user_context)
            if updated_artifact_result.get("success"):
                updated_artifact = updated_artifact_result["artifact"]
                updated_artifact["solution_id"] = solution_id
                
                # Store updated artifact with solution_id link
                await self.store_document(
                    document_data=updated_artifact,
                    metadata={
                        "type": "solution_artifact",
                        "artifact_id": artifact_id,
                        "solution_id": solution_id,
                        "status": "implemented",
                        "document_id": f"solution_artifact_{artifact_id}"
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
                "solution_id": solution_id,
                "artifact_id": artifact_id,
                "status": "implemented",
                "solution": solution
            }
            
            # Record health metric
            await self.record_health_metric("create_solution_from_artifact_success", 1.0, {
                "solution_id": solution_id,
                "artifact_id": artifact_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "create_solution_from_artifact_complete",
                success=True,
                details={"solution_id": solution_id, "artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Solution created from artifact: {solution_id} (artifact: {artifact_id})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_solution_from_artifact", details={"artifact_id": artifact_id})
            
            # Record health metric (failure)
            await self.record_health_metric("create_solution_from_artifact_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "create_solution_from_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Create solution from artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "solution_service",
            "realm": "solution",
            "layer": "solution_composition",
            "capabilities": ["solution_composition", "solution_design", "solution_execution", "multi_phase_orchestration", "artifact_storage"],
            "soa_apis": [
                "design_solution", "get_solution_template", "customize_solution",
                "deploy_solution", "execute_solution_phase", "get_solution_status",
                "pause_solution", "resume_solution", "cancel_solution", "get_available_solution_types",
                "create_solution_artifact", "get_solution_artifact", "update_solution_artifact_status",
                "get_solution_artifact_version", "get_solution_artifact_versions",  # Week 2.2
                "create_solution_from_artifact"  # NEW - Week 5.1
            ],
            "mcp_tools": [],
            "composes": "journey_services",
            "solution_templates": list(self.solution_templates.keys())
        }








