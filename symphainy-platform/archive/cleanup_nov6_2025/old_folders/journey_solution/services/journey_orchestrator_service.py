#!/usr/bin/env python3
"""
Journey Orchestrator Service - The Heart of the Journey/Solution Dimension

This service orchestrates business outcome journeys across all platform dimensions,
giving purpose to the dormant cross-dimensional managers.

WHAT (Journey/Solution Role): I orchestrate business outcome journeys across all dimensions
HOW (Service Implementation): I coordinate City Manager, Delivery Manager, and Experience Manager
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from bases.realm_service_base import RealmServiceBase
from utilities import UserContext


class JourneyOrchestratorService(RealmServiceBase):
    """
    Journey Orchestrator Service - The orchestration hub for business outcome journeys
    
    This service gives purpose to the dormant cross-dimensional managers by orchestrating
    business outcome journeys across all platform dimensions.
    """

    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: Optional[CuratorFoundationService] = None):
        """Initialize Journey Orchestrator Service."""
        super().__init__(
            realm_name="journey",
            service_name="journey_orchestrator",
            public_works_foundation=public_works_foundation,
            di_container=di_container,
            curator_foundation=curator_foundation
        )
        
        # Inject all cross-dimensional managers (they finally have purpose!)
        self.city_manager = None  # Will be injected
        self.delivery_manager = None  # Will be injected
        self.experience_manager = None  # Will be injected
        
        # Journey/Solution services
        self.solution_architect = None  # Will be injected
        self.business_outcome_analyzer = None  # Will be injected
        
        # Journey Manager Factory
        self.journey_manager_factory = None  # Will be injected
        
        # Journey management
        self.active_journeys: Dict[str, Dict[str, Any]] = {}
        self.journey_templates: Dict[str, Dict[str, Any]] = {}
        self.business_outcome_catalog: Dict[str, Dict[str, Any]] = {}
        
        print(f"🎯 Journey Orchestrator Service initialized - The orchestration hub!")

    async def initialize(self):
        """Initialize the Journey Orchestrator Service."""
        try:
            print("🎯 Initializing Journey Orchestrator Service...")
            
            # Inject cross-dimensional managers
            await self._inject_cross_dimensional_managers()
            
            # Initialize Journey/Solution services
            await self._initialize_journey_solution_services()
            
            # Initialize business outcome catalog
            await self._initialize_business_outcome_catalog()
            
            # Initialize journey templates
            await self._initialize_journey_templates()
            
            print("✅ Journey Orchestrator Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Journey Orchestrator Service: {e}")
            raise

    async def _inject_cross_dimensional_managers(self):
        """Inject cross-dimensional managers - they finally have purpose!"""
        try:
            # City Manager - now has purpose: orchestrate Smart City for business outcomes
            self.city_manager = self.di_container.get_foundation_service("CityManagerService")
            print("✅ City Manager injected - now has business outcome purpose!")
            
            # Delivery Manager - now has purpose: orchestrate Business Enablement for business outcomes
            self.delivery_manager = self.di_container.get_foundation_service("DeliveryManagerService")
            print("✅ Delivery Manager injected - now has business outcome purpose!")
            
            # Experience Manager - now has purpose: orchestrate Experience for business outcomes
            self.experience_manager = self.di_container.get_foundation_service("ExperienceManagerService")
            print("✅ Experience Manager injected - now has business outcome purpose!")
            
        except Exception as e:
            print(f"⚠️ Some cross-dimensional managers not available: {e}")

    async def _initialize_journey_solution_services(self):
        """Initialize Journey/Solution services."""
        try:
            # Solution Architect - architects solutions by composing platform capabilities
            from .solution_architect_service import SolutionArchitectService
            self.solution_architect = SolutionArchitectService(self.di_container)
            await self.solution_architect.initialize()
            print("✅ Solution Architect Service initialized")
            
            # Business Outcome Analyzer - analyzes business outcomes and determines required capabilities
            from .business_outcome_analyzer_service import BusinessOutcomeAnalyzerService
            self.business_outcome_analyzer = BusinessOutcomeAnalyzerService(self.di_container)
            await self.business_outcome_analyzer.initialize()
            print("✅ Business Outcome Analyzer Service initialized")
            
            # Journey Manager Factory - manages journey managers for different use cases
            from .journey_manager_factory import JourneyManagerFactory
            self.journey_manager_factory = JourneyManagerFactory(self.di_container, self.public_works_foundation)
            await self.journey_manager_factory.initialize()
            print("✅ Journey Manager Factory initialized")
            
        except Exception as e:
            print(f"⚠️ Some Journey/Solution services not available: {e}")

    async def _initialize_business_outcome_catalog(self):
        """Initialize business outcome catalog."""
        self.business_outcome_catalog = {
            "data_analysis": {
                "name": "Data Analysis & Insights",
                "description": "Analyze data to generate business insights",
                "use_cases": ["mvp", "autonomous_vehicle", "insurance_ai"],
                "required_dimensions": ["smart_city", "business_enablement", "experience"],
                "required_capabilities": ["data_processing", "insights_generation", "visualization"]
            },
            "process_optimization": {
                "name": "Process Optimization",
                "description": "Optimize business processes and workflows",
                "use_cases": ["mvp", "autonomous_vehicle", "insurance_ai"],
                "required_dimensions": ["smart_city", "business_enablement", "experience"],
                "required_capabilities": ["workflow_analysis", "process_optimization", "automation"]
            },
            "strategic_planning": {
                "name": "Strategic Planning",
                "description": "Create strategic plans and roadmaps",
                "use_cases": ["mvp", "autonomous_vehicle", "insurance_ai"],
                "required_dimensions": ["smart_city", "business_enablement", "experience"],
                "required_capabilities": ["roadmap_generation", "strategic_analysis", "planning"]
            },
            "content_management": {
                "name": "Content Management",
                "description": "Manage and organize content and documents",
                "use_cases": ["mvp", "autonomous_vehicle", "insurance_ai"],
                "required_dimensions": ["smart_city", "business_enablement", "experience"],
                "required_capabilities": ["content_processing", "document_management", "organization"]
            }
        }
        print("✅ Business outcome catalog initialized")

    async def _initialize_journey_templates(self):
        """Initialize journey templates for different business outcomes."""
        self.journey_templates = {
            "data_analysis": {
                "name": "Data Analysis Journey",
                "stages": [
                    "data_collection",
                    "data_processing", 
                    "analysis_execution",
                    "insights_generation",
                    "visualization_creation",
                    "report_delivery"
                ],
                "estimated_duration": "2-4 hours",
                "complexity": "medium"
            },
            "process_optimization": {
                "name": "Process Optimization Journey", 
                "stages": [
                    "process_analysis",
                    "bottleneck_identification",
                    "optimization_design",
                    "implementation_planning",
                    "change_management",
                    "results_measurement"
                ],
                "estimated_duration": "1-2 days",
                "complexity": "high"
            }
        }
        print("✅ Journey templates initialized")

    # ============================================================================
    # CORE JOURNEY ORCHESTRATION METHODS
    # ============================================================================

    async def create_business_outcome_journey(self, business_outcome: str, use_case: str, user_context: UserContext):
        """
        Create a complete business outcome journey across all dimensions.
        
        This is where the cross-dimensional managers finally have purpose!
        """
        try:
            print(f"🎯 Creating business outcome journey: {business_outcome} for use case: {use_case}")
            
            # 1. Analyze business outcome requirements
            outcome_analysis = await self.business_outcome_analyzer.analyze_business_outcome(
                business_outcome, use_case, user_context
            )
            
            # 2. Architect solution using all platform capabilities
            solution_architecture = await self.solution_architect.architect_solution(
                outcome_analysis
            )
            
            # 3. Orchestrate cross-dimensional execution
            journey_result = await self._orchestrate_cross_dimensional_journey(
                business_outcome, use_case, solution_architecture, user_context
            )
            
            # 4. Create journey record
            journey_id = await self._create_journey_record(
                business_outcome, use_case, journey_result, user_context
            )
            
            return {
                "journey_id": journey_id,
                "business_outcome": business_outcome,
                "use_case": use_case,
                "outcome_analysis": outcome_analysis,
                "solution_architecture": solution_architecture,
                "journey_result": journey_result,
                "status": "created",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Business outcome journey creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "journey_id": None
            }

    async def _orchestrate_cross_dimensional_journey(self, business_outcome: str, use_case: str, 
                                                   solution_architecture: Dict[str, Any], user_context: UserContext):
        """
        Orchestrate the cross-dimensional journey - this is where the managers get purpose!
        """
        try:
            print("🎯 Orchestrating cross-dimensional journey...")
            
            # City Manager: "I need to coordinate Smart City + other dimensions for this outcome"
            city_coordination = None
            if self.city_manager:
                city_coordination = await self.city_manager.orchestrate_for_business_outcome(
                    business_outcome, use_case, user_context
                )
                print("✅ City Manager orchestrated Smart City for business outcome")
            
            # Delivery Manager: "I need to coordinate Business Enablement + other dimensions"
            business_coordination = None
            if self.delivery_manager:
                business_coordination = await self.delivery_manager.orchestrate_for_business_outcome(
                    business_outcome, use_case, user_context
                )
                print("✅ Delivery Manager orchestrated Business Enablement for business outcome")
            
            # Experience Manager: "I need to coordinate Experience + other dimensions"
            experience_coordination = None
            if self.experience_manager:
                experience_coordination = await self.experience_manager.orchestrate_for_business_outcome(
                    business_outcome, use_case, user_context
                )
                print("✅ Experience Manager orchestrated Experience for business outcome")
            
            # Journey/Solution Dimension coordinates the cross-dimensional orchestration
            orchestration_result = {
                "business_outcome": business_outcome,
                "use_case": use_case,
                "city_coordination": city_coordination,
                "business_coordination": business_coordination,
                "experience_coordination": experience_coordination,
                "solution_architecture": solution_architecture,
                "orchestration_status": "completed",
                "orchestrated_at": datetime.utcnow().isoformat()
            }
            
            print("✅ Cross-dimensional orchestration completed")
            return orchestration_result
            
        except Exception as e:
            print(f"❌ Cross-dimensional orchestration failed: {e}")
            return {
                "orchestration_status": "failed",
                "error": str(e)
            }

    async def _create_journey_record(self, business_outcome: str, use_case: str, 
                                   journey_result: Dict[str, Any], user_context: UserContext):
        """Create a journey record for tracking."""
        journey_id = f"journey_{int(datetime.utcnow().timestamp())}"
        
        journey_record = {
            "journey_id": journey_id,
            "business_outcome": business_outcome,
            "use_case": use_case,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "journey_result": journey_result,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.active_journeys[journey_id] = journey_record
        print(f"✅ Journey record created: {journey_id}")
        
        return journey_id

    # ============================================================================
    # INTELLIGENT BUSINESS OUTCOME ROUTING
    # ============================================================================

    async def route_business_outcome_intelligently(self, business_outcome: str, use_case: str, user_context: UserContext):
        """
        Route business outcome intelligently using the appropriate journey manager.
        """
        try:
            print(f"🎯 Intelligently routing business outcome: {business_outcome} for use case: {use_case}")
            
            # Get appropriate journey manager for use case
            if self.journey_manager_factory:
                journey_manager_result = await self.journey_manager_factory.create_journey_manager(use_case, user_context)
                
                if journey_manager_result.get("success", True):  # Default to True if no success field
                    journey_manager = journey_manager_result["journey_manager"]
                    
                    # Use journey manager to analyze and route business outcome
                    routing_result = await journey_manager.analyze_business_outcome_and_route(
                        business_outcome, user_context
                    )
                    
                    return {
                        "business_outcome": business_outcome,
                        "use_case": use_case,
                        "routing_result": routing_result,
                        "journey_manager_type": journey_manager_result["manager_type"],
                        "routed_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to create journey manager",
                        "business_outcome": business_outcome,
                        "use_case": use_case
                    }
            else:
                # Fallback to basic business outcome analysis
                return await self._fallback_business_outcome_routing(business_outcome, use_case, user_context)
                
        except Exception as e:
            print(f"❌ Intelligent business outcome routing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "business_outcome": business_outcome,
                "use_case": use_case
            }

    async def _fallback_business_outcome_routing(self, business_outcome: str, use_case: str, user_context: UserContext):
        """Fallback business outcome routing when journey manager factory is not available."""
        return {
            "business_outcome": business_outcome,
            "use_case": use_case,
            "routing_result": {
                "routing": "content_pillar -> insights_pillar",
                "reason": "Fallback routing - journey manager factory not available",
                "action": "Direct to content pillar for data upload and analysis"
            },
            "journey_manager_type": "fallback",
            "routed_at": datetime.utcnow().isoformat()
        }

    async def process_user_response_for_routing(self, business_outcome: str, use_case: str, user_response: str, user_context: UserContext):
        """
        Process user response for intelligent routing.
        """
        try:
            print(f"🎯 Processing user response for routing: {business_outcome}")
            
            # Get appropriate journey manager for use case
            if self.journey_manager_factory:
                journey_manager_info = await self.journey_manager_factory.get_journey_manager_for_use_case(use_case)
                
                if journey_manager_info["available"]:
                    journey_manager = journey_manager_info["manager_instance"]
                    
                    # Process user response using journey manager
                    response_result = await journey_manager.process_user_response(
                        business_outcome, user_response, user_context
                    )
                    
                    return {
                        "business_outcome": business_outcome,
                        "use_case": use_case,
                        "user_response": user_response,
                        "response_result": response_result,
                        "journey_manager_type": journey_manager_info["manager_type"],
                        "processed_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Journey manager not available for use case: {use_case}",
                        "business_outcome": business_outcome,
                        "use_case": use_case
                    }
            else:
                return {
                    "success": False,
                    "error": "Journey manager factory not available",
                    "business_outcome": business_outcome,
                    "use_case": use_case
                }
                
        except Exception as e:
            print(f"❌ User response processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "business_outcome": business_outcome,
                "use_case": use_case
            }

    # ============================================================================
    # BUSINESS OUTCOME MANAGEMENT
    # ============================================================================

    async def get_available_business_outcomes(self, tenant_id: str, user_id: str):
        """Get available business outcomes for a user."""
        try:
            # Filter business outcomes by tenant and user context
            available_outcomes = []
            
            for outcome_id, outcome_data in self.business_outcome_catalog.items():
                # Check if outcome is available for the tenant
                if self._is_outcome_available_for_tenant(outcome_id, tenant_id):
                    available_outcomes.append({
                        "outcome_id": outcome_id,
                        "name": outcome_data["name"],
                        "description": outcome_data["description"],
                        "use_cases": outcome_data["use_cases"],
                        "complexity": outcome_data.get("complexity", "medium")
                    })
            
            return {
                "success": True,
                "available_outcomes": available_outcomes,
                "total_count": len(available_outcomes)
            }
            
        except Exception as e:
            print(f"❌ Failed to get available business outcomes: {e}")
            return {
                "success": False,
                "error": str(e),
                "available_outcomes": []
            }

    def _is_outcome_available_for_tenant(self, outcome_id: str, tenant_id: str) -> bool:
        """Check if a business outcome is available for a tenant."""
        # For now, all outcomes are available to all tenants
        # In the future, this could be tenant-specific
        return True

    async def get_journey_status(self, journey_id: str):
        """Get the status of a specific journey."""
        if journey_id in self.active_journeys:
            return {
                "success": True,
                "journey": self.active_journeys[journey_id]
            }
        else:
            return {
                "success": False,
                "error": "Journey not found"
            }

    async def get_active_journeys(self, user_context: UserContext):
        """Get all active journeys for a user."""
        try:
            user_journeys = [
                journey for journey in self.active_journeys.values()
                if journey["user_id"] == user_context.user_id and journey["tenant_id"] == user_context.tenant_id
            ]
            
            return {
                "success": True,
                "active_journeys": user_journeys,
                "total_count": len(user_journeys)
            }
            
        except Exception as e:
            print(f"❌ Failed to get active journeys: {e}")
            return {
                "success": False,
                "error": str(e),
                "active_journeys": []
            }

    # ============================================================================
    # HEALTH AND CAPABILITIES
    # ============================================================================

    async def health_check(self):
        """Get health status of the Journey Orchestrator Service."""
        try:
            health_status = {
                "service_name": "JourneyOrchestratorService",
                "status": "healthy",
                "active_journeys_count": len(self.active_journeys),
                "business_outcomes_catalog_size": len(self.business_outcome_catalog),
                "journey_templates_count": len(self.journey_templates),
                "cross_dimensional_managers": {
                    "city_manager": self.city_manager is not None,
                    "delivery_manager": self.delivery_manager is not None,
                    "experience_manager": self.experience_manager is not None
                },
                "journey_solution_services": {
                    "solution_architect": self.solution_architect is not None,
                    "business_outcome_analyzer": self.business_outcome_analyzer is not None
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "JourneyOrchestratorService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_capabilities(self):
        """Get capabilities of the Journey Orchestrator Service."""
        return {
            "service_name": "JourneyOrchestratorService",
            "capabilities": [
                "business_outcome_journey_creation",
                "cross_dimensional_orchestration",
                "journey_management",
                "business_outcome_catalog_management",
                "solution_architecture",
                "journey_tracking",
                "multi_tenant_journey_support"
            ],
            "business_outcomes_supported": list(self.business_outcome_catalog.keys()),
            "journey_templates_available": list(self.journey_templates.keys()),
            "cross_dimensional_coordination": True
        }
    
    # ============================================================================
    # REALM SERVICE BASE ABSTRACT METHODS
    # ============================================================================
    
    async def initialize(self):
        """Initialize the Journey Orchestrator Service."""
        try:
            self.logger.info("🗺️ Initializing Journey Orchestrator Service...")
            
            # Initialize orchestration capabilities
            self.orchestration_enabled = True
            self.cross_dimensional_coordination_enabled = True
            self.business_outcome_management_enabled = True
            
            # Initialize journey management
            self.journey_management_enabled = True
            self.journey_tracking_enabled = True
            self.solution_architecture_enabled = True
            
            # Initialize business outcome catalog
            await self._initialize_business_outcome_catalog()
            
            # Initialize journey templates
            await self._initialize_journey_templates()
            
            self.logger.info("✅ Journey Orchestrator Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Journey Orchestrator Service: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the Journey Orchestrator Service."""
        try:
            self.logger.info("🛑 Shutting down Journey Orchestrator Service...")
            
            # Clean up active journeys
            for journey_id in list(self.active_journeys.keys()):
                await self._cleanup_journey(journey_id)
            
            # Clear registries
            self.active_journeys.clear()
            self.business_outcome_catalog.clear()
            self.journey_templates.clear()
            
            self.logger.info("✅ Journey Orchestrator Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during Journey Orchestrator Service shutdown: {e}")
    
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get Journey Orchestrator capabilities for realm operations."""
        return {
            "service_name": self.service_name,
            "realm": "journey",
            "service_type": "orchestrator",
            "capabilities": {
                "orchestration": {
                    "enabled": self.orchestration_enabled,
                    "active_journeys": len(self.active_journeys),
                    "business_outcomes": len(self.business_outcome_catalog)
                },
                "cross_dimensional_coordination": {
                    "enabled": self.cross_dimensional_coordination_enabled,
                    "coordination_methods": ["service_discovery", "health_monitoring", "dashboard_aggregation"]
                },
                "business_outcome_management": {
                    "enabled": self.business_outcome_management_enabled,
                    "outcome_types": list(self.business_outcome_catalog.keys())
                },
                "journey_management": {
                    "enabled": self.journey_management_enabled,
                    "tracking_enabled": self.journey_tracking_enabled,
                    "templates_available": len(self.journey_templates)
                },
                "solution_architecture": {
                    "enabled": self.solution_architecture_enabled,
                    "architecture_methods": ["solution_design", "component_coordination", "integration_planning"]
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
    
    async def _cleanup_journey(self, journey_id: str):
        """Clean up a specific journey."""
        try:
            if journey_id in self.active_journeys:
                journey = self.active_journeys[journey_id]
                journey["status"] = "cleaned_up"
                journey["cleanup_timestamp"] = datetime.utcnow().isoformat()
                del self.active_journeys[journey_id]
        except Exception as e:
            self.logger.warning(f"Failed to cleanup journey {journey_id}: {e}")


# Create service instance factory function
def create_journey_orchestrator_service(di_container: DIContainerService,
                                       public_works_foundation: PublicWorksFoundationService,
                                       curator_foundation: Optional[CuratorFoundationService] = None) -> JourneyOrchestratorService:
    """Factory function to create JourneyOrchestratorService with proper DI."""
    return JourneyOrchestratorService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
journey_orchestrator_service = None  # Will be set by foundation services during initialization
