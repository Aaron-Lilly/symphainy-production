#!/usr/bin/env python3
"""
Solution Orchestration Hub Service - Extensible solution orchestration

This service serves as the central hub for solution orchestration, dynamically discovering
and routing to appropriate solution initiators based on user intent and context.

WHAT (Solution Role): I orchestrate solutions dynamically based on user intent
HOW (Service Implementation): I use intent analysis, dynamic routing, and solution initiator discovery
"""

import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from bases.realm_service_base import RealmServiceBase
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext

logger = logging.getLogger(__name__)


class SolutionIntent(Enum):
    """Solution intent enumeration for user-centric solutions."""
    MVP = "mvp"                    # Start with basic MVP solution
    POC = "poc"                    # Validate idea with proof of concept
    ROADMAP = "roadmap"            # Strategic roadmap for evolution
    PRODUCTION = "production"      # Scale to production/enterprise
    INTEGRATION = "integration"    # Integrate with existing systems
    DEMO = "demo"                  # See demonstration or example
    CUSTOM = "custom"              # Custom solution request


class SolutionScope(Enum):
    """Solution scope enumeration reflecting progressive complexity."""
    QUICK_DEMO = "quick_demo"                    # Show capabilities quickly
    MVP_IMPLEMENTATION = "mvp_implementation"    # Basic MVP solution
    PROOF_OF_CONCEPT = "proof_of_concept"       # Validate specific concept
    PILOT_PROJECT = "pilot_project"             # Limited production pilot
    PRODUCTION_READY = "production_ready"       # Full production deployment
    ENTERPRISE_SCALE = "enterprise_scale"       # Enterprise-wide deployment
    STRATEGIC_ROADMAP = "strategic_roadmap"     # Long-term evolution plan


class SolutionInitiatorInterface(ABC):
    """Interface for solution initiators."""
    
    @abstractmethod
    async def can_handle_intent(self, intent: SolutionIntent, scope: SolutionScope, user_context: UserContext) -> bool:
        """Check if this initiator can handle the given intent and scope."""
        pass
    
    @abstractmethod
    async def get_confidence_score(self, intent: SolutionIntent, scope: SolutionScope, user_context: UserContext) -> float:
        """Get confidence score for handling this intent and scope."""
        pass
    
    @abstractmethod
    async def orchestrate_solution(self, intent: SolutionIntent, scope: SolutionScope, user_context: UserContext, solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the solution based on intent and scope."""
        pass
    
    @abstractmethod
    def get_initiator_info(self) -> Dict[str, Any]:
        """Get information about this initiator."""
        pass


class SolutionOrchestrationHubService(RealmServiceBase):
    """
    Solution Orchestration Hub Service - Extensible solution orchestration
    
    This service serves as the central hub for solution orchestration, dynamically discovering
    and routing to appropriate solution initiators based on user intent and context.
    """
    
    def __init__(self, di_container: DIContainerService,
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: CuratorFoundationService = None):
        """Initialize Solution Orchestration Hub Service."""
        super().__init__(
            service_name="solution_orchestration_hub",
            di_container=di_container,
            realm_name="solution",
            service_type="orchestration_hub"
        )
        
        # Store foundation services
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Solution orchestration capabilities
        self.solution_initiators = {}
        self.intent_patterns = {}
        self.solution_contexts = {}
        
        # Initialize solution orchestration hub
        self._initialize_solution_orchestration_hub()
    
    def _initialize_solution_orchestration_hub(self):
        """Initialize the solution orchestration hub."""
        self.logger.info("🎯 Initializing Solution Orchestration Hub for dynamic solution orchestration")
        
        # Initialize intent patterns
        self._initialize_intent_patterns()
        
        # Initialize solution initiator discovery
        self._initialize_solution_initiator_discovery()
        
        self.logger.info("✅ Solution Orchestration Hub initialized successfully")
    
    def _initialize_intent_patterns(self):
        """Initialize intent analysis patterns for user-centric solutions."""
        self.intent_patterns = {
            "mvp": {
                "keywords": ["mvp", "minimum viable product", "quick start", "get started", "begin", "start", "launch"],
                "patterns": [r"mvp", r"minimum.*viable", r"quick.*start", r"get.*started", r"begin.*with", r"start.*building"],
                "confidence_threshold": 0.8,
                "description": "User wants to start with a basic MVP solution"
            },
            "poc": {
                "keywords": ["poc", "proof of concept", "demonstrate", "show", "validate", "test", "try"],
                "patterns": [r"poc", r"proof.*concept", r"demonstrate", r"show.*me", r"validate.*idea", r"test.*solution"],
                "confidence_threshold": 0.8,
                "description": "User wants to validate an idea with a proof of concept"
            },
            "roadmap": {
                "keywords": ["roadmap", "plan", "strategy", "future", "long term", "evolve", "expand", "grow"],
                "patterns": [r"roadmap", r"plan", r"strategy", r"future.*plan", r"how.*to.*evolve", r"next.*steps"],
                "confidence_threshold": 0.8,
                "description": "User wants a strategic roadmap for solution evolution"
            },
            "production": {
                "keywords": ["production", "enterprise", "scale", "deploy", "rollout", "full", "complete"],
                "patterns": [r"production", r"enterprise", r"scale.*up", r"full.*deployment", r"complete.*solution"],
                "confidence_threshold": 0.8,
                "description": "User wants to scale to production/enterprise solution"
            },
            "integration": {
                "keywords": ["integrate", "connect", "combine", "merge", "unify", "consolidate"],
                "patterns": [r"integrate", r"connect.*systems", r"combine.*solutions", r"unify.*platform"],
                "confidence_threshold": 0.8,
                "description": "User wants to integrate with existing systems"
            },
            "demo": {
                "keywords": ["demo", "show", "example", "sample", "preview", "see"],
                "patterns": [r"demo", r"show.*me", r"example", r"sample", r"preview.*of"],
                "confidence_threshold": 0.8,
                "description": "User wants to see a demonstration or example"
            }
        }
    
    def _initialize_solution_initiator_discovery(self):
        """Initialize solution initiator discovery."""
        # This will be populated dynamically by discovered initiators
        self.solution_initiators = {}
        
        # Register known initiators
        self._register_known_initiators()
    
    def _register_known_initiators(self):
        """Register known solution initiators for user-centric solutions."""
        try:
            # MVP Solution Initiator - Primary user-centric solution
            from ..mvp_solution_initiator.mvp_solution_initiator_service import MVPSolutionInitiatorService
            self._register_initiator("mvp", MVPSolutionInitiatorService)
            
            # Future: POC Solution Initiator
            # Future: Roadmap Solution Initiator
            # Future: Production Solution Initiator
            # Future: Integration Solution Initiator
            
        except ImportError as e:
            self.logger.warning(f"Some solution initiators not available: {e}")
    
    def _register_initiator(self, initiator_type: str, initiator_class: Type[SolutionInitiatorInterface]):
        """Register a solution initiator."""
        self.solution_initiators[initiator_type] = {
            "class": initiator_class,
            "instance": None,
            "capabilities": {}
        }
        self.logger.info(f"Registered solution initiator: {initiator_type}")
    
    # ============================================================================
    # REALM SERVICE BASE ABSTRACT METHODS
    # ============================================================================
    
    async def initialize(self):
        """Initialize the Solution Orchestration Hub Service."""
        try:
            self.logger.info("🎯 Initializing Solution Orchestration Hub Service...")
            
            # Initialize solution orchestration capabilities
            self.solution_orchestration_enabled = True
            self.intent_analysis_enabled = True
            self.dynamic_routing_enabled = True
            
            # Initialize solution initiators
            await self._initialize_solution_initiators()
            
            self.logger.info("✅ Solution Orchestration Hub Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Solution Orchestration Hub Service: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the Solution Orchestration Hub Service."""
        try:
            self.logger.info("🛑 Shutting down Solution Orchestration Hub Service...")
            
            # Clear solution data
            self.solution_initiators.clear()
            self.intent_patterns.clear()
            self.solution_contexts.clear()
            
            self.logger.info("✅ Solution Orchestration Hub Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during Solution Orchestration Hub Service shutdown: {e}")
    
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get Solution Orchestration Hub Service capabilities for realm operations."""
        return {
            "service_name": self.service_name,
            "realm": "solution",
            "service_type": "solution_orchestration_hub",
            "capabilities": {
                "solution_orchestration": {
                    "enabled": self.solution_orchestration_enabled,
                    "initiators_count": len(self.solution_initiators),
                    "orchestration_methods": ["intent_analysis", "dynamic_routing", "solution_coordination"]
                },
                "intent_analysis": {
                    "enabled": self.intent_analysis_enabled,
                    "patterns_count": len(self.intent_patterns),
                    "analysis_methods": ["pattern_matching", "keyword_analysis", "context_analysis"]
                },
                "dynamic_routing": {
                    "enabled": self.dynamic_routing_enabled,
                    "routing_methods": ["initiator_discovery", "confidence_scoring", "capability_matching"]
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
    # SOLUTION ORCHESTRATION METHODS
    # ============================================================================
    
    async def orchestrate_solution(self, user_input: str, user_context: UserContext) -> Dict[str, Any]:
        """Orchestrate solution based on user input and context."""
        try:
            self.logger.info(f"🎯 Orchestrating solution for user input: {user_input}")
            
            # Analyze user intent
            intent_analysis = await self._analyze_user_intent(user_input, user_context)
            
            # Determine solution scope
            solution_scope = await self._determine_solution_scope(intent_analysis, user_context)
            
            # Find appropriate solution initiator
            solution_initiator = await self._find_solution_initiator(intent_analysis, solution_scope, user_context)
            
            if not solution_initiator:
                return {
                    "success": False,
                    "error": "No suitable solution initiator found",
                    "intent_analysis": intent_analysis,
                    "solution_scope": solution_scope
                }
            
            # Create solution context
            solution_context = await self._create_solution_context(intent_analysis, solution_scope, user_context)
            
            # Orchestrate solution using the selected initiator
            orchestration_result = await self._orchestrate_with_initiator(
                solution_initiator, intent_analysis, solution_scope, user_context, solution_context
            )
            
            return {
                "success": True,
                "intent_analysis": intent_analysis,
                "solution_scope": solution_scope,
                "solution_initiator": solution_initiator["type"],
                "orchestration_result": orchestration_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate solution: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input
            }
    
    async def _analyze_user_intent(self, user_input: str, user_context: UserContext) -> Dict[str, Any]:
        """Analyze user intent from input."""
        user_input_lower = user_input.lower()
        intent_scores = {}
        
        for intent_name, intent_data in self.intent_patterns.items():
            confidence_score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in intent_data["keywords"] 
                                if keyword in user_input_lower)
            keyword_score = keyword_matches / len(intent_data["keywords"]) if intent_data["keywords"] else 0
            
            # Pattern matching
            pattern_matches = 0
            for pattern in intent_data["patterns"]:
                import re
                if re.search(pattern, user_input_lower):
                    pattern_matches += 1
            pattern_score = pattern_matches / len(intent_data["patterns"]) if intent_data["patterns"] else 0
            
            # Calculate overall confidence
            confidence_score = (keyword_score * 0.6) + (pattern_score * 0.4)
            
            if confidence_score >= intent_data["confidence_threshold"]:
                intent_scores[intent_name] = confidence_score
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return {
                "intent": best_intent[0],
                "confidence_score": best_intent[1],
                "all_scores": intent_scores
            }
        else:
            return {
                "intent": "custom",
                "confidence_score": 0.5,
                "all_scores": {}
            }
    
    async def _determine_solution_scope(self, intent_analysis: Dict[str, Any], user_context: UserContext) -> SolutionScope:
        """Determine solution scope based on intent and context, reflecting progressive complexity."""
        intent = intent_analysis.get("intent", "custom")
        confidence = intent_analysis.get("confidence_score", 0.5)
        
        # Progressive complexity mapping
        if intent == "mvp":
            return SolutionScope.MVP_IMPLEMENTATION
        elif intent == "poc":
            return SolutionScope.PROOF_OF_CONCEPT
        elif intent == "roadmap":
            return SolutionScope.STRATEGIC_ROADMAP
        elif intent == "production":
            return SolutionScope.PRODUCTION_READY if confidence > 0.8 else SolutionScope.PILOT_PROJECT
        elif intent == "integration":
            return SolutionScope.ENTERPRISE_SCALE if confidence > 0.8 else SolutionScope.PRODUCTION_READY
        elif intent == "demo":
            return SolutionScope.QUICK_DEMO
        else:
            # Default to MVP for custom intents
            return SolutionScope.MVP_IMPLEMENTATION
    
    async def _find_solution_initiator(self, intent_analysis: Dict[str, Any], solution_scope: SolutionScope, user_context: UserContext) -> Optional[Dict[str, Any]]:
        """Find the most appropriate solution initiator."""
        intent = intent_analysis.get("intent", "custom")
        
        # Direct mapping for known intents
        if intent in self.solution_initiators:
            initiator_info = self.solution_initiators[intent]
            return {
                "type": intent,
                "class": initiator_info["class"],
                "instance": initiator_info["instance"],
                "confidence": 1.0
            }
        
        # Fallback to MVP initiator for custom intents
        if "mvp" in self.solution_initiators:
            initiator_info = self.solution_initiators["mvp"]
            return {
                "type": "mvp",
                "class": initiator_info["class"],
                "instance": initiator_info["instance"],
                "confidence": 0.7
            }
        
        return None
    
    async def _create_solution_context(self, intent_analysis: Dict[str, Any], solution_scope: SolutionScope, user_context: UserContext) -> Dict[str, Any]:
        """Create solution context for orchestration."""
        return {
            "intent": intent_analysis.get("intent", "custom"),
            "confidence_score": intent_analysis.get("confidence_score", 0.5),
            "solution_scope": solution_scope.value,
            "user_context": {
                "user_id": user_context.user_id,
                "tenant_id": user_context.tenant_id,
                "session_id": user_context.session_id
            },
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _orchestrate_with_initiator(self, solution_initiator: Dict[str, Any], intent_analysis: Dict[str, Any], 
                                        solution_scope: SolutionScope, user_context: UserContext, solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate solution using the selected initiator."""
        try:
            # Get or create initiator instance
            if not solution_initiator["instance"]:
                solution_initiator["instance"] = solution_initiator["class"](
                    di_container=self.di_container,
                    public_works_foundation=self.public_works_foundation,
                    curator_foundation=self.curator_foundation
                )
            
            # Convert intent to SolutionIntent enum
            intent_enum = SolutionIntent(intent_analysis.get("intent", "custom"))
            
            # Orchestrate using the initiator
            result = await solution_initiator["instance"].orchestrate_solution(
                intent=intent_enum,
                scope=solution_scope,
                user_context=user_context,
                solution_context=solution_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate with initiator: {e}")
            return {
                "success": False,
                "error": str(e),
                "initiator_type": solution_initiator["type"]
            }
    
    async def _initialize_solution_initiators(self):
        """Initialize solution initiators."""
        for initiator_type, initiator_info in self.solution_initiators.items():
            try:
                # Initialize the initiator
                initiator_instance = initiator_info["class"](
                    di_container=self.di_container,
                    public_works_foundation=self.public_works_foundation,
                    curator_foundation=self.curator_foundation
                )
                
                # Store the instance
                initiator_info["instance"] = initiator_instance
                
                # Get initiator capabilities
                initiator_info["capabilities"] = initiator_instance.get_initiator_info()
                
                self.logger.info(f"Initialized solution initiator: {initiator_type}")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize solution initiator {initiator_type}: {e}")
    
    # ============================================================================
    # SOLUTION INITIATOR MANAGEMENT
    # ============================================================================
    
    async def register_solution_initiator(self, initiator_type: str, initiator_class: Type[SolutionInitiatorInterface]):
        """Register a new solution initiator dynamically."""
        self._register_initiator(initiator_type, initiator_class)
        await self._initialize_solution_initiators()
    
    async def get_available_initiators(self) -> Dict[str, Any]:
        """Get information about available solution initiators."""
        return {
            initiator_type: {
                "type": initiator_type,
                "capabilities": initiator_info["capabilities"],
                "available": initiator_info["instance"] is not None
            }
            for initiator_type, initiator_info in self.solution_initiators.items()
        }
    
    async def get_initiator_capabilities(self, initiator_type: str) -> Dict[str, Any]:
        """Get capabilities of a specific solution initiator."""
        if initiator_type in self.solution_initiators:
            return self.solution_initiators[initiator_type]["capabilities"]
        else:
            return {"error": f"Solution initiator {initiator_type} not found"}


# Create service instance factory function
def create_solution_orchestration_hub_service(di_container: DIContainerService,
                                            public_works_foundation: PublicWorksFoundationService,
                                            curator_foundation: CuratorFoundationService = None) -> SolutionOrchestrationHubService:
    """Factory function to create SolutionOrchestrationHubService with proper DI."""
    return SolutionOrchestrationHubService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
solution_orchestration_hub_service = None  # Will be set by foundation services during initialization
