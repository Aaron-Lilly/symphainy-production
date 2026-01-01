"""
MVP Journey Initiator Service
Orchestrates MVP journeys that produce POC Proposals and Roadmaps
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from bases.realm_service_base import RealmServiceBase
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext

logger = logging.getLogger(__name__)


class MVPJourneyInitiatorService(RealmServiceBase):
    """
    MVP Journey Initiator Service - Orchestrates MVP journeys that produce POC Proposals and Roadmaps.
    
    This service orchestrates the complete MVP journey across all 4 pillars, producing:
    1. POC Proposal - To validate the coexistence model
    2. Roadmap - To deploy full production platform
    
    Context examples:
    - Insurance Client → Insurance-specific MVP journey
    - Autonomous Vehicle Testing → AV testing-specific MVP journey
    - Carbon Credits Trader → Carbon trading-specific MVP journey
    - Data Integration Platform → Legacy modernization-specific MVP journey
    """

    def __init__(self,
                 di_container: DIContainerService,
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: CuratorFoundationService = None):
        super().__init__(
            realm_name="journey",
            service_name="mvp_journey_initiator",
            public_works_foundation=public_works_foundation,
            di_container=di_container,
            curator_foundation=curator_foundation
        )
        
        # MVP journey orchestration services
        self.journey_manager = None
        self.experience_manager = None
        self.delivery_manager = None
        self.city_manager = None
        
        # MVP journey context
        self.active_mvp_journeys = {}
        self.journey_templates = {}
        
        # Initialize MVP journey initiator
        self._initialize_mvp_journey_initiator()

    def _initialize_mvp_journey_initiator(self):
        """Initialize the MVP journey initiator."""
        logger.info("🚀 Initializing MVP Journey Initiator for MVP journeys that produce POC Proposals and Roadmaps")
        self._initialize_journey_templates()
        logger.info("✅ MVP Journey Initiator initialized successfully")

    def _initialize_journey_templates(self):
        """Initialize MVP journey templates for different client contexts."""
        self.journey_templates = {
            "insurance_client": {
                "name": "Insurance Client MVP Journey",
                "description": "MVP journey for insurance client coexistence platform",
                "pillar_focus": {
                    "content": "insurance_data_management",
                    "insights": "insurance_analytics",
                    "operations": "insurance_workflows",
                    "business_outcomes": "insurance_outcomes"
                },
                "agent_personas": {
                    "content_liaison": "insurance_data_specialist",
                    "insights_liaison": "insurance_analytics_specialist",
                    "operations_liaison": "insurance_workflow_specialist",
                    "business_outcomes_liaison": "insurance_outcomes_specialist"
                },
                "ui_adaptations": {
                    "theme": "insurance_focused",
                    "color_scheme": "blue_white",
                    "icons": "insurance_icons"
                }
            },
            "autonomous_vehicle_testing": {
                "name": "Autonomous Vehicle Testing MVP Journey",
                "description": "MVP journey for AV testing coexistence platform",
                "pillar_focus": {
                    "content": "av_test_data_management",
                    "insights": "av_testing_analytics",
                    "operations": "av_testing_workflows",
                    "business_outcomes": "av_testing_outcomes"
                },
                "agent_personas": {
                    "content_liaison": "av_test_data_specialist",
                    "insights_liaison": "av_testing_analytics_specialist",
                    "operations_liaison": "av_testing_workflow_specialist",
                    "business_outcomes_liaison": "av_testing_outcomes_specialist"
                },
                "ui_adaptations": {
                    "theme": "av_testing_focused",
                    "color_scheme": "green_blue",
                    "icons": "av_testing_icons"
                }
            },
            "carbon_credits_trader": {
                "name": "Carbon Credits Trader MVP Journey",
                "description": "MVP journey for carbon trading coexistence platform",
                "pillar_focus": {
                    "content": "carbon_trading_data_management",
                    "insights": "carbon_trading_analytics",
                    "operations": "carbon_trading_workflows",
                    "business_outcomes": "carbon_trading_outcomes"
                },
                "agent_personas": {
                    "content_liaison": "carbon_trading_data_specialist",
                    "insights_liaison": "carbon_trading_analytics_specialist",
                    "operations_liaison": "carbon_trading_workflow_specialist",
                    "business_outcomes_liaison": "carbon_trading_outcomes_specialist"
                },
                "ui_adaptations": {
                    "theme": "carbon_trading_focused",
                    "color_scheme": "green_purple",
                    "icons": "carbon_trading_icons"
                }
            },
            "data_integration_platform": {
                "name": "Data Integration Platform MVP Journey",
                "description": "MVP journey for legacy modernization coexistence platform",
                "pillar_focus": {
                    "content": "legacy_data_management",
                    "insights": "legacy_modernization_analytics",
                    "operations": "legacy_modernization_workflows",
                    "business_outcomes": "legacy_modernization_outcomes"
                },
                "agent_personas": {
                    "content_liaison": "legacy_data_specialist",
                    "insights_liaison": "legacy_modernization_analytics_specialist",
                    "operations_liaison": "legacy_modernization_workflow_specialist",
                    "business_outcomes_liaison": "legacy_modernization_outcomes_specialist"
                },
                "ui_adaptations": {
                    "theme": "legacy_modernization_focused",
                    "color_scheme": "orange_red",
                    "icons": "legacy_modernization_icons"
                }
            }
        }
        logger.info(f"✅ Loaded {len(self.journey_templates)} MVP journey templates for different client contexts.")

    async def orchestrate_mvp_journey(self, journey_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate MVP journey that produces POC Proposal and Roadmap.
        This is the main entry point for MVP journeys.
        """
        try:
            logger.info("🎯 Orchestrating MVP journey that will produce POC Proposal and Roadmap")
            
            # Extract journey context
            solution_context = journey_request.get("solution_context", {})
            user_context = journey_request.get("user_context", {})
            intent_analysis = journey_request.get("intent_analysis", {})
            
            # Determine client context for journey customization
            client_context = self._determine_client_context(solution_context)
            
            # Create MVP journey orchestration
            mvp_journey = await self._create_mvp_journey_orchestration(
                solution_context, user_context, client_context
            )
            
            # Orchestrate across all 4 pillars to produce POC Proposal and Roadmap
            pillar_orchestration = await self._orchestrate_mvp_pillars(
                solution_context, user_context, client_context
            )
            
            # Generate POC Proposal and Roadmap
            poc_proposal = await self._generate_poc_proposal(solution_context, pillar_orchestration)
            roadmap = await self._generate_roadmap(solution_context, pillar_orchestration)
            
            return {
                "success": True,
                "mvp_journey": mvp_journey,
                "pillar_orchestration": pillar_orchestration,
                "poc_proposal": poc_proposal,
                "roadmap": roadmap,
                "client_context": client_context,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to orchestrate MVP journey: {e}")
            return {
                "success": False,
                "error": str(e),
                "mvp_journey": None
            }

    def _determine_client_context(self, solution_context: Dict[str, Any]) -> str:
        """Determine client context for journey customization."""
        business_outcome = solution_context.get("business_outcome", "").lower()
        solution_type = solution_context.get("solution_type", "custom")
        
        if "insurance" in business_outcome or "insurance" in solution_type:
            return "insurance_client"
        elif "autonomous" in business_outcome or "vehicle" in business_outcome or "testing" in business_outcome:
            return "autonomous_vehicle_testing"
        elif "carbon" in business_outcome or "credit" in business_outcome or "trading" in business_outcome:
            return "carbon_credits_trader"
        elif "legacy" in business_outcome or "integration" in business_outcome or "modernization" in business_outcome:
            return "data_integration_platform"
        else:
            return "custom_client"

    async def _create_mvp_journey_orchestration(self, solution_context: Dict[str, Any], 
                                            user_context: UserContext, client_context: str) -> Dict[str, Any]:
        """Create MVP journey orchestration structure."""
        journey_template = self.journey_templates.get(client_context, {})
        
        return {
            "journey_id": f"mvp_{int(datetime.utcnow().timestamp())}",
            "business_outcome": solution_context.get("business_outcome", ""),
            "solution_context": solution_context,
            "user_context": user_context,
            "client_context": client_context,
            "journey_template": journey_template,
            "pillar_sequence": [
                "content_pillar",
                "insights_pillar", 
                "operations_pillar",
                "business_outcomes_pillar"
            ],
            "current_pillar": "content_pillar",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }

    async def _orchestrate_mvp_pillars(self, solution_context: Dict[str, Any], 
                                       user_context: UserContext, client_context: str) -> Dict[str, Any]:
        """Orchestrate MVP journey across all 4 pillars with client-specific adaptations."""
        journey_template = self.journey_templates.get(client_context, {})
        pillar_focus = journey_template.get("pillar_focus", {})
        agent_personas = journey_template.get("agent_personas", {})
        ui_adaptations = journey_template.get("ui_adaptations", {})
        
        pillar_results = {}
        
        # Content Pillar Orchestration
        content_result = await self._orchestrate_content_pillar(
            solution_context, pillar_focus.get("content", "data_management"), 
            agent_personas, ui_adaptations
        )
        pillar_results["content_pillar"] = content_result
        
        # Insights Pillar Orchestration  
        insights_result = await self._orchestrate_insights_pillar(
            solution_context, pillar_focus.get("insights", "analytics"),
            agent_personas, ui_adaptations
        )
        pillar_results["insights_pillar"] = insights_result
        
        # Operations Pillar Orchestration
        operations_result = await self._orchestrate_operations_pillar(
            solution_context, pillar_focus.get("operations", "workflow"),
            agent_personas, ui_adaptations
        )
        pillar_results["operations_pillar"] = operations_result
        
        # Business Outcomes Pillar Orchestration
        business_outcomes_result = await self._orchestrate_business_outcomes_pillar(
            solution_context, pillar_focus.get("business_outcomes", "outcome_tracking"),
            agent_personas, ui_adaptations
        )
        pillar_results["business_outcomes_pillar"] = business_outcomes_result
        
        return {
            "success": True,
            "pillar_results": pillar_results,
            "client_context": client_context,
            "orchestration_complete": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _orchestrate_content_pillar(self, solution_context: Dict[str, Any], 
                                        content_focus: str, agent_personas: Dict[str, str], 
                                        ui_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate Content Pillar for MVP journey with client-specific adaptations."""
        return {
            "pillar": "content",
            "focus": content_focus,
            "capabilities": [
                "file_upload_support",
                "multi_format_parsing", 
                "data_preview",
                "content_liaison_agent"
            ],
            "client_adaptations": {
                "agent_personas": {
                    "content_liaison": agent_personas.get("content_liaison", "content_specialist")
                },
                "ui_adaptations": {
                    "theme": ui_adaptations.get("theme", "default"),
                    "color_scheme": ui_adaptations.get("color_scheme", "blue"),
                    "icons": ui_adaptations.get("icons", "default_icons")
                }
            },
            "status": "ready"
        }

    async def _orchestrate_insights_pillar(self, solution_context: Dict[str, Any], 
                                         insights_focus: str, agent_personas: Dict[str, str], 
                                         ui_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate Insights Pillar for MVP journey with client-specific adaptations."""
        return {
            "pillar": "insights",
            "focus": insights_focus,
            "capabilities": [
                "file_selection_prompt",
                "business_analysis",
                "data_visualization",
                "insights_liaison_agent"
            ],
            "client_adaptations": {
                "agent_personas": {
                    "insights_liaison": agent_personas.get("insights_liaison", "analytics_specialist")
                },
                "ui_adaptations": {
                    "theme": ui_adaptations.get("theme", "default"),
                    "color_scheme": ui_adaptations.get("color_scheme", "green"),
                    "icons": ui_adaptations.get("icons", "default_icons")
                }
            },
            "status": "ready"
        }

    async def _orchestrate_operations_pillar(self, solution_context: Dict[str, Any], 
                                           operations_focus: str, agent_personas: Dict[str, str], 
                                           ui_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate Operations Pillar for MVP journey with client-specific adaptations."""
        return {
            "pillar": "operations",
            "focus": operations_focus,
            "capabilities": [
                "file_selection_or_upload",
                "workflow_generation",
                "sop_creation",
                "coexistence_blueprint",
                "operations_liaison_agent"
            ],
            "client_adaptations": {
                "agent_personas": {
                    "operations_liaison": agent_personas.get("operations_liaison", "workflow_specialist")
                },
                "ui_adaptations": {
                    "theme": ui_adaptations.get("theme", "default"),
                    "color_scheme": ui_adaptations.get("color_scheme", "orange"),
                    "icons": ui_adaptations.get("icons", "default_icons")
                }
            },
            "status": "ready"
        }

    async def _orchestrate_business_outcomes_pillar(self, solution_context: Dict[str, Any], 
                                                  business_outcomes_focus: str, agent_personas: Dict[str, str], 
                                                  ui_adaptations: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate Business Outcomes Pillar for MVP journey with client-specific adaptations."""
        return {
            "pillar": "business_outcomes",
            "focus": business_outcomes_focus,
            "capabilities": [
                "summary_aggregation",
                "additional_context_collection",
                "roadmap_generation",
                "poc_proposal",
                "business_outcomes_liaison_agent"
            ],
            "client_adaptations": {
                "agent_personas": {
                    "business_outcomes_liaison": agent_personas.get("business_outcomes_liaison", "outcome_specialist")
                },
                "ui_adaptations": {
                    "theme": ui_adaptations.get("theme", "default"),
                    "color_scheme": ui_adaptations.get("color_scheme", "purple"),
                    "icons": ui_adaptations.get("icons", "default_icons")
                }
            },
            "status": "ready"
        }

    async def _generate_poc_proposal(self, solution_context: Dict[str, Any], 
                                   pillar_orchestration: Dict[str, Any]) -> Dict[str, Any]:
        """Generate POC Proposal based on MVP journey results."""
        return {
            "poc_proposal": {
                "title": f"POC Proposal for {solution_context.get('business_outcome', 'Solution')}",
                "description": "Proof of concept to validate coexistence model",
                "objectives": [
                    "Validate coexistence model",
                    "Demonstrate platform capabilities",
                    "Test integration points",
                    "Prove business value"
                ],
                "deliverables": [
                    "Working prototype",
                    "Integration validation",
                    "Performance metrics",
                    "Business case validation"
                ],
                "timeline": "4-6 weeks",
                "success_criteria": [
                    "Coexistence model validated",
                    "Integration points working",
                    "Performance targets met",
                    "Business value demonstrated"
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
        }

    async def _generate_roadmap(self, solution_context: Dict[str, Any], 
                              pillar_orchestration: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Roadmap based on MVP journey results."""
        return {
            "roadmap": {
                "title": f"Production Roadmap for {solution_context.get('business_outcome', 'Solution')}",
                "description": "Strategic roadmap to deploy full production platform",
                "phases": [
                    {
                        "phase": "Phase 1: Foundation",
                        "duration": "8-12 weeks",
                        "deliverables": [
                            "Core platform deployment",
                            "Basic integration capabilities",
                            "Initial user training"
                        ]
                    },
                    {
                        "phase": "Phase 2: Enhancement",
                        "duration": "12-16 weeks",
                        "deliverables": [
                            "Advanced features deployment",
                            "Full integration capabilities",
                            "Comprehensive user training"
                        ]
                    },
                    {
                        "phase": "Phase 3: Optimization",
                        "duration": "16-20 weeks",
                        "deliverables": [
                            "Performance optimization",
                            "Advanced analytics",
                            "Full production deployment"
                        ]
                    }
                ],
                "milestones": [
                    "Platform foundation complete",
                    "Integration validation complete",
                    "User training complete",
                    "Production deployment complete"
                ],
                "generated_at": datetime.utcnow().isoformat()
            }
        }

    async def initialize(self):
        """Initialize the MVP Journey Initiator Service."""
        await super().initialize()
        logger.info("🚀 MVP Journey Initiator Service initialized.")
        await self._inject_dependencies()

    async def _inject_dependencies(self):
        """Inject required dependencies."""
        try:
            self.journey_manager = self.di_container.get_service("JourneyManagerService")
            logger.info("✅ JourneyManagerService injected.")
            self.experience_manager = self.di_container.get_service("ExperienceManagerService")
            logger.info("✅ ExperienceManagerService injected.")
            self.delivery_manager = self.di_container.get_service("DeliveryManagerService")
            logger.info("✅ DeliveryManagerService injected.")
            self.city_manager = self.di_container.get_service("CityManagerService")
            logger.info("✅ CityManagerService injected.")
        except Exception as e:
            logger.warning(f"⚠️ Some dependencies for MVPJourneyInitiatorService not available: {e}")

    async def shutdown(self):
        """Shutdown the MVP Journey Initiator Service."""
        logger.info("🛑 Shutting down MVP Journey Initiator Service...")
        self.active_mvp_journeys.clear()
        self.journey_templates.clear()
        logger.info("✅ MVP Journey Initiator Service shutdown complete.")
        await super().shutdown()

    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get MVP Journey Initiator Service capabilities for realm operations."""
        base_capabilities = await super().get_realm_capabilities()
        mvp_capabilities = {
            "service_name": self.service_name,
            "realm": "journey",
            "service_type": "mvp_journey_initiator",
            "capabilities": {
                "mvp_journey_orchestration": {
                    "enabled": True,
                    "supported_client_contexts": list(self.journey_templates.keys()),
                    "journey_outputs": ["poc_proposal", "roadmap"]
                },
                "pillar_orchestration": {
                    "enabled": True,
                    "supported_pillars": ["content", "insights", "operations", "business_outcomes"]
                },
                "client_adaptation": {
                    "enabled": True,
                    "adaptation_types": ["agent_personas", "ui_adaptations", "pillar_focus"]
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
        return {**base_capabilities, **mvp_capabilities}


# Factory function
def create_mvp_journey_initiator_service(
    di_container: DIContainerService,
    public_works_foundation: PublicWorksFoundationService,
    curator_foundation: CuratorFoundationService = None
) -> MVPJourneyInitiatorService:
    """Factory function to create MVPJourneyInitiatorService with proper DI."""
    return MVPJourneyInitiatorService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Default service instance
mvp_journey_initiator_service = None








