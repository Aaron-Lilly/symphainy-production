#!/usr/bin/env python3
"""
MVP Solution Initiator Service - MVP-specific orchestration

Handles MVP solution orchestration, solution context propagation,
and business outcome coordination for top-down MVP execution.

WHAT (Solution Role): I orchestrate MVP-specific functionality
HOW (Service Implementation): I coordinate solution context and MVP journey orchestration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from bases.realm_service_base import RealmServiceBase
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService

logger = logging.getLogger(__name__)


class SolutionType(Enum):
    """MVP solution type enumeration."""
    AI_TESTING_CAPABILITY = "ai_testing_capability"
    LEGACY_DATA_CONSTRAINTS = "legacy_data_constraints"
    DATA_PIPELINES_ANALYTICS = "data_pipelines_analytics"
    CUSTOM_SOLUTION = "custom_solution"


class MVPScope(Enum):
    """MVP scope enumeration."""
    POC = "poc"
    PILOT = "pilot"
    PRODUCTION = "production"


@dataclass
class SolutionContext:
    """Solution context for MVP orchestration."""
    tenant_id: str
    user_id: str
    solution_type: SolutionType
    mvp_scope: MVPScope
    business_outcome: str
    requirements: Dict[str, Any]
    journey_steps: List[str]
    pillar_focus: Dict[str, str]  # Which pillars are relevant
    agentic_personas: Dict[str, str]  # Tailored agent personas
    ui_adaptations: Dict[str, Any]  # Frontend adaptations
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SolutionContext':
        """Create from dictionary."""
        return cls(**data)


class MVPSolutionInitiatorService(RealmServiceBase):
    """
    MVP Solution Initiator Service - MVP-specific orchestration
    
    Handles MVP solution orchestration, solution context propagation,
    and business outcome coordination for top-down MVP execution.
    """
    
    def __init__(self, 
                 di_container: DIContainerService,
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: CuratorFoundationService = None):
        """Initialize MVP Solution Initiator Service."""
        super().__init__(
            service_name="mvp_solution_initiator",
            di_container=di_container,
            realm_name="solution",
            service_type="solution_initiator"
        )
        
        # Store foundation services
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # MVP orchestration services
        self.user_solution_design_service = None
        self.journey_manager = None
        self.experience_manager = None
        self.delivery_manager = None
        self.city_manager = None
        
        # Solution context management
        self.active_solution_contexts = {}
        self.solution_templates = {}
        
        # Initialize MVP solution initiator
        self._initialize_mvp_solution_initiator()
    
    def _initialize_mvp_solution_initiator(self):
        """Initialize the MVP solution initiator."""
        self.logger.info("Initializing MVP Solution Initiator for MVP orchestration")
        
        # Initialize solution context management
        self._initialize_solution_context_management()
        
        # Initialize MVP orchestration services
        self._initialize_mvp_orchestration_services()
        
        self.logger.info("MVP Solution Initiator initialized successfully")
    
    def _initialize_solution_context_management(self):
        """Initialize solution context management system."""
        self.solution_context_management = {
            "active_contexts": {},
            "context_templates": {},
            "context_propagation": {},
            "context_analytics": {}
        }
    
    def _initialize_mvp_orchestration_services(self):
        """Initialize MVP orchestration services."""
        try:
            # Get realm managers from DI container
            self.journey_manager = self.di_container.get_service("JourneyManagerService")
            self.experience_manager = self.di_container.get_service("ExperienceManagerService")
            self.delivery_manager = self.di_container.get_service("DeliveryManagerService")
            self.city_manager = self.di_container.get_service("CityManagerService")
            
            # Get UserSolutionDesignService
            self.user_solution_design_service = self.di_container.get_service("UserSolutionDesignService")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize some MVP orchestration services: {e}")
    
    # ============================================================================
    # REALM SERVICE BASE ABSTRACT METHODS
    # ============================================================================
    
    async def initialize(self):
        """Initialize the MVP Solution Initiator Service."""
        try:
            self.logger.info("🎯 Initializing MVP Solution Initiator Service...")
            
            # Initialize MVP orchestration capabilities
            self.mvp_orchestration_enabled = True
            self.solution_context_propagation_enabled = True
            self.business_outcome_coordination_enabled = True
            self.top_down_execution_enabled = True
            
            # Initialize solution context management
            await self._initialize_solution_context_management()
            
            # Initialize MVP orchestration services
            await self._initialize_mvp_orchestration_services()
            
            self.logger.info("✅ MVP Solution Initiator Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MVP Solution Initiator Service: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the MVP Solution Initiator Service."""
        try:
            self.logger.info("🛑 Shutting down MVP Solution Initiator Service...")
            
            # Clear solution contexts
            self.active_solution_contexts.clear()
            self.solution_templates.clear()
            
            self.logger.info("✅ MVP Solution Initiator Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during MVP Solution Initiator Service shutdown: {e}")
    
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get MVP Solution Initiator capabilities for realm operations."""
        return {
            "service_name": self.service_name,
            "realm": "solution",
            "service_type": "mvp_solution_initiator",
            "capabilities": {
                "mvp_orchestration": {
                    "enabled": self.mvp_orchestration_enabled,
                    "active_contexts": len(self.active_solution_contexts),
                    "solution_templates": len(self.solution_templates)
                },
                "solution_context_propagation": {
                    "enabled": self.solution_context_propagation_enabled,
                    "propagation_methods": ["context_creation", "context_routing", "context_adaptation"]
                },
                "business_outcome_coordination": {
                    "enabled": self.business_outcome_coordination_enabled,
                    "coordination_methods": ["outcome_analysis", "journey_composition", "pillar_orchestration"]
                },
                "top_down_execution": {
                    "enabled": self.top_down_execution_enabled,
                    "execution_methods": ["solution_initiation", "realm_coordination", "mvp_delivery"]
                }
            },
            "enhanced_platform_capabilities": {
                "zero_trust_security": True,
                "multi_tenancy": True,
                "enhanced_logging": True,
                "enhanced_error_handling": True,
                "health_monitoring": True,
                "cross_realm_communication": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # MVP SOLUTION ORCHESTRATION
    # ============================================================================
    
    async def initiate_mvp_solution(self, user_context: Dict[str, Any], business_outcome: str) -> Dict[str, Any]:
        """Initiate MVP solution based on user context and business outcome."""
        try:
            self.logger.info(f"Initiating MVP solution for business outcome: {business_outcome}")
            
            # Step 1: Use UserSolutionDesignService to understand client needs
            solution_design = await self._analyze_solution_requirements(user_context, business_outcome)
            
            # Step 2: Create solution context
            solution_context = await self._create_solution_context(user_context, business_outcome, solution_design)
            
            # Step 3: Orchestrate MVP journey
            mvp_journey = await self._orchestrate_mvp_journey(solution_context)
            
            # Step 4: Coordinate realm managers
            realm_coordination = await self._coordinate_realm_managers(solution_context)
            
            return {
                "success": True,
                "solution_context": solution_context.to_dict(),
                "mvp_journey": mvp_journey,
                "realm_coordination": realm_coordination,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initiate MVP solution: {e}")
            return {
                "success": False,
                "error": str(e),
                "solution_context": None
            }
    
    def get_initiator_info(self) -> Dict[str, Any]:
        """Get information about this initiator - interface expected by Solution Orchestration Hub."""
        return {
            "type": "mvp",
            "name": "MVP Solution Initiator",
            "description": "MVP solution orchestration and business outcome coordination",
            "capabilities": [
                "solution_context_propagation",
                "mvp_journey_orchestration", 
                "business_outcome_coordination",
                "realm_manager_coordination"
            ],
            "supported_intents": ["mvp", "custom"],
            "supported_scopes": ["mvp_implementation"],
            "version": "1.0.0"
        }
    
    async def orchestrate_solution(self, intent: str, scope: str, user_context: Dict[str, Any], solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate solution - interface expected by Solution Orchestration Hub."""
        try:
            self.logger.info(f"Orchestrating MVP solution for intent: {intent}, scope: {scope}")
            
            # Convert user_context to the format expected by initiate_mvp_solution
            business_outcome = solution_context.get("business_outcome", "AI-enabled solution")
            
            # Use the existing initiate_mvp_solution method
            result = await self.initiate_mvp_solution(user_context, business_outcome)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate solution: {e}")
            return {
                "success": False,
                "error": str(e),
                "intent": intent,
                "scope": scope
            }
    
    async def orchestrate_mvp_solution(self, solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate MVP solution with existing solution context."""
        try:
            self.logger.info("Orchestrating MVP solution with existing context")
            
            # Convert dict to SolutionContext object
            if isinstance(solution_context, dict):
                context = SolutionContext.from_dict(solution_context)
            else:
                context = solution_context
            
            # Store active solution context
            self.active_solution_contexts[context.tenant_id] = context
            
            # Orchestrate MVP journey
            mvp_journey = await self._orchestrate_mvp_journey(context)
            
            # Coordinate realm managers
            realm_coordination = await self._coordinate_realm_managers(context)
            
            return {
                "success": True,
                "solution_context": context.to_dict(),
                "mvp_journey": mvp_journey,
                "realm_coordination": realm_coordination,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate MVP solution: {e}")
            return {
                "success": False,
                "error": str(e),
                "solution_context": solution_context
            }
    
    # ============================================================================
    # SOLUTION CONTEXT MANAGEMENT
    # ============================================================================
    
    async def _analyze_solution_requirements(self, user_context: Dict[str, Any], business_outcome: str) -> Dict[str, Any]:
        """Analyze solution requirements using UserSolutionDesignService."""
        try:
            if not self.user_solution_design_service:
                # Fallback analysis if service not available
                return await self._fallback_solution_analysis(user_context, business_outcome)
            
            # Use UserSolutionDesignService to analyze requirements
            analysis_result = await self.user_solution_design_service.analyze_business_outcome(
                user_context=user_context,
                business_outcome=business_outcome
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze solution requirements: {e}")
            return await self._fallback_solution_analysis(user_context, business_outcome)
    
    async def _fallback_solution_analysis(self, user_context: Dict[str, Any], business_outcome: str) -> Dict[str, Any]:
        """Fallback solution analysis when UserSolutionDesignService is not available."""
        # Simple pattern matching for common business outcomes
        business_outcome_lower = business_outcome.lower()
        
        if "testing" in business_outcome_lower or "test" in business_outcome_lower:
            solution_type = SolutionType.AI_TESTING_CAPABILITY
            requirements = {
                "testing_framework": "AI-enabled testing",
                "test_automation": True,
                "quality_assurance": True
            }
        elif "legacy" in business_outcome_lower or "data" in business_outcome_lower:
            solution_type = SolutionType.LEGACY_DATA_CONSTRAINTS
            requirements = {
                "data_migration": True,
                "legacy_integration": True,
                "data_transformation": True
            }
        elif "analytics" in business_outcome_lower or "pipeline" in business_outcome_lower:
            solution_type = SolutionType.DATA_PIPELINES_ANALYTICS
            requirements = {
                "data_pipelines": True,
                "analytics_platform": True,
                "data_visualization": True
            }
        else:
            solution_type = SolutionType.CUSTOM_SOLUTION
            requirements = {
                "custom_requirements": True,
                "flexible_solution": True
            }
        
        return {
            "solution_type": solution_type,
            "requirements": requirements,
            "mvp_scope": MVPScope.POC,
            "estimated_duration": "4-6 weeks",
            "complexity": "medium"
        }
    
    async def _create_solution_context(self, user_context: Dict[str, Any], business_outcome: str, solution_design: Dict[str, Any]) -> SolutionContext:
        """Create solution context from analysis results."""
        try:
            # Extract solution type
            solution_type = solution_design.get("solution_type", SolutionType.CUSTOM_SOLUTION)
            if isinstance(solution_type, str):
                solution_type = SolutionType(solution_type)
            
            # Determine MVP scope
            mvp_scope = MVPScope.POC  # Default to POC for MVP
            
            # Create journey steps based on solution type
            journey_steps = await self._create_journey_steps(solution_type, solution_design)
            
            # Determine pillar focus
            pillar_focus = await self._determine_pillar_focus(solution_type, solution_design)
            
            # Create agentic personas
            agentic_personas = await self._create_agentic_personas(solution_type, solution_design)
            
            # Create UI adaptations
            ui_adaptations = await self._create_ui_adaptations(solution_type, solution_design)
            
            # Create solution context
            solution_context = SolutionContext(
                tenant_id=getattr(user_context, "tenant_id", "default"),
                user_id=getattr(user_context, "user_id", "anonymous"),
                solution_type=solution_type,
                mvp_scope=mvp_scope,
                business_outcome=business_outcome,
                requirements=solution_design.get("requirements", {}),
                journey_steps=journey_steps,
                pillar_focus=pillar_focus,
                agentic_personas=agentic_personas,
                ui_adaptations=ui_adaptations,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return solution_context
            
        except Exception as e:
            self.logger.error(f"Failed to create solution context: {e}")
            raise
    
    async def _create_journey_steps(self, solution_type: SolutionType, solution_design: Dict[str, Any]) -> List[str]:
        """Create journey steps based on solution type."""
        base_steps = [
            "solution_initiation",
            "requirements_analysis",
            "solution_design",
            "implementation",
            "testing",
            "delivery"
        ]
        
        if solution_type == SolutionType.AI_TESTING_CAPABILITY:
            return [
                "solution_initiation",
                "testing_requirements_analysis",
                "ai_testing_framework_design",
                "test_automation_implementation",
                "quality_assurance_testing",
                "testing_capability_delivery"
            ]
        elif solution_type == SolutionType.LEGACY_DATA_CONSTRAINTS:
            return [
                "solution_initiation",
                "legacy_data_analysis",
                "data_migration_design",
                "legacy_integration_implementation",
                "data_validation_testing",
                "legacy_solution_delivery"
            ]
        elif solution_type == SolutionType.DATA_PIPELINES_ANALYTICS:
            return [
                "solution_initiation",
                "data_requirements_analysis",
                "pipeline_architecture_design",
                "analytics_platform_implementation",
                "data_visualization_testing",
                "analytics_solution_delivery"
            ]
        else:
            return base_steps
    
    async def _determine_pillar_focus(self, solution_type: SolutionType, solution_design: Dict[str, Any]) -> Dict[str, str]:
        """Determine which pillars are relevant for the solution."""
        pillar_focus = {
            "content": "data_management",
            "insights": "analytics",
            "operations": "workflow",
            "business_outcomes": "outcome_tracking"
        }
        
        if solution_type == SolutionType.AI_TESTING_CAPABILITY:
            pillar_focus.update({
                "content": "test_data_management",
                "insights": "testing_analytics",
                "operations": "testing_workflows",
                "business_outcomes": "quality_metrics"
            })
        elif solution_type == SolutionType.LEGACY_DATA_CONSTRAINTS:
            pillar_focus.update({
                "content": "legacy_data_processing",
                "insights": "data_quality_analytics",
                "operations": "migration_workflows",
                "business_outcomes": "migration_success"
            })
        elif solution_type == SolutionType.DATA_PIPELINES_ANALYTICS:
            pillar_focus.update({
                "content": "pipeline_data_management",
                "insights": "advanced_analytics",
                "operations": "pipeline_workflows",
                "business_outcomes": "analytics_insights"
            })
        
        return pillar_focus
    
    async def _create_agentic_personas(self, solution_type: SolutionType, solution_design: Dict[str, Any]) -> Dict[str, str]:
        """Create agentic personas tailored to the solution type."""
        base_personas = {
            "guide_agent": "general_advisor",
            "content_liaison": "content_specialist",
            "insights_liaison": "analytics_specialist",
            "operations_liaison": "workflow_specialist",
            "business_outcomes_liaison": "outcome_specialist"
        }
        
        if solution_type == SolutionType.AI_TESTING_CAPABILITY:
            base_personas.update({
                "guide_agent": "testing_advisor",
                "content_liaison": "test_data_specialist",
                "insights_liaison": "testing_analytics_specialist",
                "operations_liaison": "testing_workflow_specialist",
                "business_outcomes_liaison": "quality_metrics_specialist"
            })
        elif solution_type == SolutionType.LEGACY_DATA_CONSTRAINTS:
            base_personas.update({
                "guide_agent": "legacy_migration_advisor",
                "content_liaison": "legacy_data_specialist",
                "insights_liaison": "data_quality_specialist",
                "operations_liaison": "migration_workflow_specialist",
                "business_outcomes_liaison": "migration_success_specialist"
            })
        elif solution_type == SolutionType.DATA_PIPELINES_ANALYTICS:
            base_personas.update({
                "guide_agent": "analytics_advisor",
                "content_liaison": "pipeline_data_specialist",
                "insights_liaison": "advanced_analytics_specialist",
                "operations_liaison": "pipeline_workflow_specialist",
                "business_outcomes_liaison": "analytics_insights_specialist"
            })
        
        return base_personas
    
    async def _create_ui_adaptations(self, solution_type: SolutionType, solution_design: Dict[str, Any]) -> Dict[str, Any]:
        """Create UI adaptations for the solution type."""
        base_adaptations = {
            "theme": "default",
            "navigation": "standard",
            "dashboard": "general"
        }
        
        if solution_type == SolutionType.AI_TESTING_CAPABILITY:
            base_adaptations.update({
                "theme": "testing_focused",
                "navigation": "testing_workflow",
                "dashboard": "testing_metrics",
                "color_scheme": "blue_green",
                "icons": "testing_icons"
            })
        elif solution_type == SolutionType.LEGACY_DATA_CONSTRAINTS:
            base_adaptations.update({
                "theme": "migration_focused",
                "navigation": "migration_workflow",
                "dashboard": "migration_progress",
                "color_scheme": "orange_red",
                "icons": "migration_icons"
            })
        elif solution_type == SolutionType.DATA_PIPELINES_ANALYTICS:
            base_adaptations.update({
                "theme": "analytics_focused",
                "navigation": "analytics_workflow",
                "dashboard": "analytics_insights",
                "color_scheme": "purple_blue",
                "icons": "analytics_icons"
            })
        
        return base_adaptations
    
    # ============================================================================
    # MVP JOURNEY ORCHESTRATION
    # ============================================================================
    
    async def _orchestrate_mvp_journey(self, solution_context: SolutionContext) -> Dict[str, Any]:
        """Orchestrate MVP journey using JourneyManager."""
        try:
            if not self.journey_manager:
                return {
                    "success": False,
                    "error": "JourneyManager not available",
                    "mvp_journey": None
                }
            
            # Create journey orchestration request
            journey_request = {
                "solution_context": solution_context.to_dict(),
                "business_outcome": solution_context.business_outcome,
                "journey_steps": solution_context.journey_steps,
                "pillar_focus": solution_context.pillar_focus
            }
            
            # Delegate to JourneyManager
            journey_result = await self.journey_manager.orchestrate_mvp_journey(journey_request)
            
            return {
                "success": True,
                "mvp_journey": journey_result,
                "solution_context": solution_context.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate MVP journey: {e}")
            return {
                "success": False,
                "error": str(e),
                "mvp_journey": None
            }
    
    # ============================================================================
    # REALM MANAGER COORDINATION
    # ============================================================================
    
    async def _coordinate_realm_managers(self, solution_context: SolutionContext) -> Dict[str, Any]:
        """Coordinate realm managers with solution context."""
        try:
            coordination_results = {}
            
            # Coordinate Experience Manager
            if self.experience_manager:
                experience_result = await self._coordinate_experience_manager(solution_context)
                coordination_results["experience"] = experience_result
            
            # Coordinate Delivery Manager
            if self.delivery_manager:
                delivery_result = await self._coordinate_delivery_manager(solution_context)
                coordination_results["delivery"] = delivery_result
            
            # Coordinate City Manager
            if self.city_manager:
                city_result = await self._coordinate_city_manager(solution_context)
                coordination_results["city"] = city_result
            
            return {
                "success": True,
                "coordination_results": coordination_results,
                "realms_coordinated": len(coordination_results)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to coordinate realm managers: {e}")
            return {
                "success": False,
                "error": str(e),
                "coordination_results": {}
            }
    
    async def _coordinate_experience_manager(self, solution_context: SolutionContext) -> Dict[str, Any]:
        """Coordinate Experience Manager with solution context."""
        try:
            # Create experience adaptation request
            adaptation_request = {
                "solution_context": solution_context.to_dict(),
                "ui_adaptations": solution_context.ui_adaptations,
                "agentic_personas": solution_context.agentic_personas
            }
            
            # Delegate to Experience Manager
            if hasattr(self.experience_manager, 'adapt_for_solution_context'):
                return await self.experience_manager.adapt_for_solution_context(adaptation_request)
            else:
                return {
                    "success": True,
                    "message": "Experience Manager adaptation not yet implemented",
                    "adaptation_request": adaptation_request
                }
                
        except Exception as e:
            self.logger.error(f"Failed to coordinate Experience Manager: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _coordinate_delivery_manager(self, solution_context: SolutionContext) -> Dict[str, Any]:
        """Coordinate Delivery Manager with solution context."""
        try:
            # Create delivery orchestration request
            orchestration_request = {
                "solution_context": solution_context.to_dict(),
                "pillar_focus": solution_context.pillar_focus,
                "business_outcome": solution_context.business_outcome
            }
            
            # Delegate to Delivery Manager
            if hasattr(self.delivery_manager, 'orchestrate_for_solution_context'):
                return await self.delivery_manager.orchestrate_for_solution_context(orchestration_request)
            else:
                return {
                    "success": True,
                    "message": "Delivery Manager orchestration not yet implemented",
                    "orchestration_request": orchestration_request
                }
                
        except Exception as e:
            self.logger.error(f"Failed to coordinate Delivery Manager: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _coordinate_city_manager(self, solution_context: SolutionContext) -> Dict[str, Any]:
        """Coordinate City Manager with solution context."""
        try:
            # Create infrastructure support request
            infrastructure_request = {
                "solution_context": solution_context.to_dict(),
                "solution_type": solution_context.solution_type.value,
                "requirements": solution_context.requirements
            }
            
            # Delegate to City Manager
            if hasattr(self.city_manager, 'support_solution_context'):
                return await self.city_manager.support_solution_context(infrastructure_request)
            else:
                return {
                    "success": True,
                    "message": "City Manager support not yet implemented",
                    "infrastructure_request": infrastructure_request
                }
                
        except Exception as e:
            self.logger.error(f"Failed to coordinate City Manager: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Create service instance factory function
def create_mvp_solution_initiator_service(di_container: DIContainerService,
                                         public_works_foundation: PublicWorksFoundationService,
                                         curator_foundation: CuratorFoundationService = None) -> MVPSolutionInitiatorService:
    """Factory function to create MVPSolutionInitiatorService with proper DI."""
    return MVPSolutionInitiatorService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
mvp_solution_initiator_service = None  # Will be set by foundation services during initialization




