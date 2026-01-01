"""
Journey Orchestration Hub Service
Central point for dynamic journey initiation and orchestration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from bases.realm_service_base import RealmServiceBase
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext

logger = logging.getLogger(__name__)


class JourneyIntent(Enum):
    """Journey intent enumeration for user-centric journeys."""
    MVP_JOURNEY = "mvp_journey"                    # MVP journey that produces POC Proposal + Roadmap
    POC_EXECUTION_JOURNEY = "poc_execution_journey" # Execute POC Proposal to validate coexistence
    ROADMAP_EXECUTION_JOURNEY = "roadmap_execution_journey" # Execute roadmap to deploy production
    CUSTOM_EXECUTION_JOURNEY = "custom_execution_journey" # Execute other specific implementations


class JourneyScope(Enum):
    """Journey scope enumeration reflecting progressive complexity."""
    QUICK_DEMO = "quick_demo"                       # Show capabilities quickly
    MVP_IMPLEMENTATION = "mvp_implementation"       # Basic MVP journey
    PROOF_OF_CONCEPT = "proof_of_concept"          # Validate specific concept
    PILOT_PROJECT = "pilot_project"                # Limited production pilot
    PRODUCTION_READY = "production_ready"          # Full production deployment
    ENTERPRISE_SCALE = "enterprise_scale"          # Enterprise-wide deployment
    STRATEGIC_ROADMAP = "strategic_roadmap"        # Long-term evolution plan


class JourneyInitiatorInterface:
    """Interface for journey initiators."""
    
    async def orchestrate_journey(self, solution_context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Orchestrate a journey based on solution context."""
        pass


class JourneyOrchestrationHubService(RealmServiceBase):
    """
    Journey Orchestration Hub Service - Central point for dynamic journey initiation.
    
    This service analyzes solution context and dynamically routes journey requests
    to the appropriate Journey Initiator (e.g., MVP, POC, Roadmap, Production).
    It uses a plugin-based architecture for extensibility.
    """

    def __init__(self,
                 di_container: DIContainerService,
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: CuratorFoundationService = None):
        super().__init__(
            realm_name="journey",
            service_name="journey_orchestration_hub",
            public_works_foundation=public_works_foundation,
            di_container=di_container,
            curator_foundation=curator_foundation
        )
        
        # Journey orchestration services
        self.journey_initiators: Dict[JourneyIntent, Any] = {}
        self.intent_patterns: Dict[JourneyIntent, List[str]] = self._load_intent_patterns()
        
        # Initialize journey orchestration hub
        self._initialize_journey_orchestration_hub()

    def _initialize_journey_orchestration_hub(self):
        """Initialize the journey orchestration hub."""
        logger.info("🎯 Initializing Journey Orchestration Hub...")
        
        # Initialize journey initiator discovery
        self._initialize_journey_initiator_discovery()
        
        logger.info("✅ Journey Orchestration Hub initialized successfully")
    
    def _load_intent_patterns(self) -> Dict[JourneyIntent, List[str]]:
        """Load configurable intent patterns for journey orchestration."""
        return {
            JourneyIntent.MVP_JOURNEY: [
                "mvp", "minimum viable product", "create", "build", "design", "plan", "start"
            ],
            JourneyIntent.POC_EXECUTION_JOURNEY: [
                "execute poc", "run poc", "implement poc", "validate", "test", "demonstrate", "prove"
            ],
            JourneyIntent.ROADMAP_EXECUTION_JOURNEY: [
                "execute roadmap", "implement roadmap", "deploy", "production", "implement", "rollout"
            ],
            JourneyIntent.CUSTOM_EXECUTION_JOURNEY: [
                "execute", "implement", "deploy", "run", "custom", "specific"
            ]
        }
    
    def _initialize_journey_initiator_discovery(self):
        """Initialize journey initiator discovery."""
        self.journey_initiators = {}
        
        # Register known initiators
        self._register_known_initiators()
    
    def _register_known_initiators(self):
        """Register known journey initiators for user-centric journeys."""
        try:
            # MVP Journey Initiator - Primary user-centric journey
            from .mvp_journey_initiator.mvp_journey_initiator_service import MVPJourneyInitiatorService
            self._register_initiator("mvp", MVPJourneyInitiatorService)
            
            # Future: POC Journey Initiator
            # Future: Roadmap Journey Initiator
            # Future: Production Journey Initiator
            # Future: Integration Journey Initiator
            
        except ImportError as e:
            logger.warning(f"Some journey initiators not available: {e}")
    
    def _register_initiator(self, initiator_type: str, initiator_class: type):
        """Register a journey initiator."""
        self.journey_initiators[initiator_type] = {
            "class": initiator_class,
            "type": initiator_type,
            "registered_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Registered journey initiator: {initiator_type}")

    async def analyze_journey_intent(self, solution_context: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """
        Analyzes solution context and user input to determine the primary journey intent.
        Returns the most likely intent and associated data.
        """
        user_input_lower = user_input.lower()
        best_intent = JourneyIntent.CUSTOM_JOURNEY
        max_confidence = 0.0

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    # Simple keyword match for now, can be enhanced with NLP/LLM
                    confidence = 0.7 if intent_type != JourneyIntent.CUSTOM_JOURNEY else 0.5
                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_intent = intent_type
                    break  # Found a match for this intent type

        # Further refine based on solution context
        solution_type = solution_context.get("solution_type", "custom")
        journey_scope = self._determine_journey_scope(solution_context, best_intent)

        return {
            "intent": best_intent.value,
            "confidence_score": max_confidence,
            "solution_type": solution_type,
            "journey_scope": journey_scope.value,
            "raw_input": user_input
        }

    def _determine_journey_scope(self, solution_context: Dict[str, Any], intent: JourneyIntent) -> JourneyScope:
        """Determine journey scope based on solution context and intent."""
        solution_type = solution_context.get("solution_type", "custom")
        
        if intent == JourneyIntent.MVP_JOURNEY:
            return JourneyScope.MVP_IMPLEMENTATION  # MVP journey produces POC Proposal + Roadmap
        elif intent == JourneyIntent.POC_EXECUTION_JOURNEY:
            return JourneyScope.PROOF_OF_CONCEPT  # Execute POC Proposal to validate coexistence
        elif intent == JourneyIntent.ROADMAP_EXECUTION_JOURNEY:
            return JourneyScope.PRODUCTION_READY  # Execute roadmap to deploy production
        elif intent == JourneyIntent.CUSTOM_EXECUTION_JOURNEY:
            return JourneyScope.ENTERPRISE_SCALE  # Execute custom implementations
        else:
            return JourneyScope.MVP_IMPLEMENTATION  # Default scope

    async def orchestrate_journey(self, solution_context: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Orchestrates a journey based on solution context by analyzing intent and routing
        to the appropriate journey initiator.
        """
        logger.info(f"🎯 Orchestrating journey for solution: {solution_context.get('business_outcome', 'Unknown')}")

        # 1. Analyze journey intent from solution context
        intent_analysis = await self.analyze_journey_intent(solution_context, solution_context.get("business_outcome", ""))
        intent = intent_analysis["intent"]
        journey_scope = intent_analysis["journey_scope"]

        logger.info(f"Detected journey intent: {intent} with scope {journey_scope}")

        # 2. Route to appropriate initiator
        initiator = self.journey_initiators.get(intent)

        if initiator:
            logger.info(f"Routing to {initiator['class'].__name__} for intent {intent}")
            
            # Create journey orchestration request
            journey_request = {
                "solution_context": solution_context,
                "user_context": user_context,
                "intent_analysis": intent_analysis,
                "journey_scope": journey_scope
            }
            
            # Delegate to appropriate journey initiator
            if intent == "mvp_journey":
                from .mvp_journey_initiator.mvp_journey_initiator_service import MVPJourneyInitiatorService
                mvp_initiator = MVPJourneyInitiatorService(
                    di_container=self.di_container,
                    public_works_foundation=self.public_works_foundation,
                    curator_foundation=self.curator_foundation
                )
                return await mvp_initiator.orchestrate_mvp_journey(journey_request)
            else:
                # Generic call for other initiators (if they have a common method)
                return {
                    "success": True,
                    "message": f"Routed to {initiator['class'].__name__} for {intent}. Further implementation needed.",
                    "intent_analysis": intent_analysis
                }
        else:
            logger.warning(f"No initiator registered for journey intent: {intent}. Falling back to custom handling.")
            return {
                "success": False,
                "error": f"No initiator found for journey intent: {intent}",
                "intent_analysis": intent_analysis
            }

    async def initialize(self):
        """Initialize the Journey Orchestration Hub Service."""
        await super().initialize()
        logger.info("🎯 Journey Orchestration Hub Service initialized.")
        # Re-register initiators after DI container is fully populated
        self._register_known_initiators()

    async def shutdown(self):
        """Shutdown the Journey Orchestration Hub Service."""
        logger.info("🛑 Shutting down Journey Orchestration Hub Service...")
        self.journey_initiators.clear()
        logger.info("✅ Journey Orchestration Hub Service shutdown complete.")
        await super().shutdown()

    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get Journey Orchestration Hub Service capabilities for realm operations."""
        base_capabilities = await super().get_realm_capabilities()
        hub_capabilities = {
            "service_name": self.service_name,
            "realm": "journey",
            "service_type": "journey_orchestration_hub",
            "capabilities": {
                "intent_analysis": {
                    "enabled": True,
                    "supported_intents": [it.value for it in JourneyIntent],
                    "patterns_count": sum(len(p) for p in self.intent_patterns.values())
                },
                "dynamic_routing": {
                    "enabled": True,
                    "registered_initiators": [i["class"].__name__ for i in self.journey_initiators.values()]
                },
                "extensibility": {
                    "enabled": True,
                    "architecture": "plugin-based"
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
        return {**base_capabilities, **hub_capabilities}


# Factory function
def create_journey_orchestration_hub_service(
    di_container: DIContainerService,
    public_works_foundation: PublicWorksFoundationService,
    curator_foundation: CuratorFoundationService = None
) -> JourneyOrchestrationHubService:
    """Factory function to create JourneyOrchestrationHubService with proper DI."""
    return JourneyOrchestrationHubService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Default service instance
journey_orchestration_hub_service = None
