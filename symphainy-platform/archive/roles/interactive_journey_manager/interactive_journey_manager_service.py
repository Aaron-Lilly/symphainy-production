#!/usr/bin/env python3
"""
Interactive Journey Manager Service - Truly interactive journey management for any business outcome

This service provides truly interactive journey management that can handle any business outcome
dynamically, using AI-powered analysis and conversational discovery.

WHAT (Journey/Solution Role): I manage journeys interactively for any business outcome
HOW (Service Implementation): I use AI-powered dynamic analysis and conversational discovery
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
from utilities import UserContext


class InteractiveJourneyManagerService:
    """
    Interactive Journey Manager Service - Truly interactive journey management
    
    This service provides truly interactive journey management that can handle any business outcome
    dynamically, using AI-powered analysis and conversational discovery.
    """

    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize Interactive Journey Manager Service."""
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Dynamic Business Outcome Analyzer
        self.dynamic_analyzer = None  # Will be injected
        
        # Active conversations
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        
        # Journey templates for different scenarios
        self.journey_templates = {
            "ai_engine": {
                "name": "AI Engine Development Journey",
                "stages": ["data_collection", "model_training", "evaluation", "deployment"],
                "estimated_duration": "2-4 weeks",
                "complexity": "high"
            },
            "autonomous_testing": {
                "name": "Autonomous Testing Platform Journey",
                "stages": ["test_planning", "safety_analysis", "simulation", "coverage_analysis"],
                "estimated_duration": "1-2 weeks",
                "complexity": "high"
            },
            "insurance_platform": {
                "name": "Insurance AI Platform Journey",
                "stages": ["data_integration", "fraud_detection", "risk_assessment", "claims_processing"],
                "estimated_duration": "1-3 weeks",
                "complexity": "medium"
            },
            "collections_optimization": {
                "name": "Collections Optimization Journey",
                "stages": ["payment_analysis", "recovery_strategies", "workflow_optimization", "results_measurement"],
                "estimated_duration": "1-2 weeks",
                "complexity": "medium"
            }
        }
        
        print(f"🗣️ Interactive Journey Manager Service initialized")

    async def initialize(self):
        """Initialize the Interactive Journey Manager Service."""
        try:
            print("🗣️ Initializing Interactive Journey Manager Service...")
            
            # Inject Dynamic Business Outcome Analyzer
            await self._inject_dynamic_analyzer()
            
            # Initialize conversation management
            await self._initialize_conversation_management()
            
            # Initialize journey templates
            await self._initialize_journey_templates()
            
            print("✅ Interactive Journey Manager Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Interactive Journey Manager Service: {e}")
            raise

    async def _inject_dynamic_analyzer(self):
        """Inject Dynamic Business Outcome Analyzer."""
        try:
            from ...services.dynamic_business_outcome_analyzer import DynamicBusinessOutcomeAnalyzer
            self.dynamic_analyzer = DynamicBusinessOutcomeAnalyzer(self.di_container)
            await self.dynamic_analyzer.initialize()
            print("✅ Dynamic Business Outcome Analyzer injected")
            
        except Exception as e:
            print(f"⚠️ Dynamic Business Outcome Analyzer not available: {e}")

    async def _initialize_conversation_management(self):
        """Initialize conversation management capabilities."""
        self.conversation_capabilities = {
            "multi_turn_conversations": True,
            "context_preservation": True,
            "progressive_discovery": True,
            "adaptive_questioning": True,
            "intelligent_routing": True
        }
        print("✅ Conversation management initialized")

    async def _initialize_journey_templates(self):
        """Initialize journey templates for different scenarios."""
        # Add metadata to templates
        for template_id, template in self.journey_templates.items():
            template["id"] = template_id
            template["created_at"] = datetime.utcnow().isoformat()
            template["version"] = "1.0.0"
        
        print("✅ Journey templates initialized")

    # ============================================================================
    # INTERACTIVE JOURNEY MANAGEMENT
    # ============================================================================

    async def start_interactive_journey(self, business_outcome: str, user_context: UserContext):
        """
        Start an interactive journey for any business outcome.
        """
        try:
            print(f"🗣️ Starting interactive journey for: {business_outcome}")
            
            # Create conversation session
            conversation_id = await self._create_conversation_session(business_outcome, user_context)
            
            # Get initial analysis from dynamic analyzer
            if self.dynamic_analyzer:
                initial_analysis = await self.dynamic_analyzer.analyze_business_outcome_dynamically(
                    business_outcome, user_context
                )
            else:
                initial_analysis = await self._fallback_analysis(business_outcome)
            
            # Create interactive journey
            interactive_journey = await self._create_interactive_journey(
                business_outcome, conversation_id, initial_analysis, user_context
            )
            
            return {
                "conversation_id": conversation_id,
                "business_outcome": business_outcome,
                "initial_analysis": initial_analysis,
                "interactive_journey": interactive_journey,
                "started_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Interactive journey start failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "business_outcome": business_outcome
            }

    async def _create_conversation_session(self, business_outcome: str, user_context: UserContext):
        """Create a new conversation session."""
        conversation_id = f"conversation_{int(datetime.utcnow().timestamp())}"
        
        conversation_session = {
            "conversation_id": conversation_id,
            "business_outcome": business_outcome,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "responses": [],
            "context": {
                "data_availability": "unknown",
                "technical_context": "unknown",
                "business_context": "unknown",
                "discovery_stage": 1
            },
            "routing_decision": None,
            "recommendations": None
        }
        
        self.active_conversations[conversation_id] = conversation_session
        print(f"✅ Conversation session created: {conversation_id}")
        
        return conversation_id

    async def _fallback_analysis(self, business_outcome: str):
        """Fallback analysis when dynamic analyzer is not available."""
        return {
            "business_outcome": business_outcome,
            "domain_analysis": {
                "primary_domain": "general",
                "matched_domains": ["general"],
                "confidence_scores": {"general": 0.5},
                "suggested_data_types": ["general_data"],
                "suggested_capabilities": ["data_analysis", "insights_generation"],
                "analysis_confidence": 0.5
            },
            "dynamic_questions": [
                {
                    "question": f"What data do you currently have available for {business_outcome}?",
                    "type": "data_availability",
                    "priority": "high"
                }
            ],
            "discovery_flow": {
                "business_outcome": business_outcome,
                "primary_domain": "general",
                "discovery_stages": [
                    {
                        "stage": 1,
                        "name": "Data Availability Discovery",
                        "description": "Discover what data you have available",
                        "expected_duration": "2-3 minutes"
                    }
                ],
                "total_estimated_duration": "5-10 minutes"
            },
            "initial_routing": {
                "routing": "content_pillar -> insights_pillar",
                "reason": "General business outcome - start with data analysis",
                "action": "Upload your data and we'll help you achieve your goals"
            }
        }

    async def _create_interactive_journey(self, business_outcome: str, conversation_id: str, 
                                        initial_analysis: Dict[str, Any], user_context: UserContext):
        """Create an interactive journey based on initial analysis."""
        journey_id = f"interactive_journey_{int(datetime.utcnow().timestamp())}"
        
        interactive_journey = {
            "journey_id": journey_id,
            "conversation_id": conversation_id,
            "business_outcome": business_outcome,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "initial_analysis": initial_analysis,
            "current_stage": "discovery",
            "stages": [
                "discovery",
                "data_analysis", 
                "solution_architecture",
                "implementation",
                "results_delivery"
            ],
            "routing_decision": None,
            "recommendations": None
        }
        
        return interactive_journey

    # ============================================================================
    # CONVERSATIONAL INTERACTION
    # ============================================================================

    async def process_conversational_response(self, conversation_id: str, user_response: str, user_context: UserContext):
        """
        Process a conversational response and provide intelligent next steps.
        """
        try:
            print(f"🗣️ Processing conversational response: {user_response}")
            
            # Get conversation session
            if conversation_id not in self.active_conversations:
                return {
                    "success": False,
                    "error": "Conversation session not found",
                    "conversation_id": conversation_id
                }
            
            conversation_session = self.active_conversations[conversation_id]
            business_outcome = conversation_session["business_outcome"]
            
            # Process response using dynamic analyzer
            if self.dynamic_analyzer:
                response_result = await self.dynamic_analyzer.process_user_response_dynamically(
                    business_outcome, user_response, conversation_session["context"], user_context
                )
            else:
                response_result = await self._fallback_response_processing(
                    business_outcome, user_response, conversation_session["context"]
                )
            
            # Update conversation session
            await self._update_conversation_session(conversation_id, user_response, response_result)
            
            # Generate next steps
            next_steps = await self._generate_next_steps(conversation_id, response_result)
            
            return {
                "conversation_id": conversation_id,
                "user_response": user_response,
                "response_result": response_result,
                "next_steps": next_steps,
                "conversation_updated": True,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Conversational response processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }

    async def _fallback_response_processing(self, business_outcome: str, user_response: str, 
                                          conversation_context: Dict[str, Any]):
        """Fallback response processing when dynamic analyzer is not available."""
        user_response_lower = user_response.lower()
        
        # Simple response analysis
        has_data = any(word in user_response_lower for word in ["yes", "have", "data", "files", "documents"])
        no_data = any(word in user_response_lower for word in ["no", "don't", "nothing", "none"])
        
        response_analysis = {
            "has_data": has_data,
            "no_data": no_data,
            "confidence": 0.7 if (has_data or no_data) else 0.5,
            "response_type": "positive" if has_data else "negative" if no_data else "unclear"
        }
        
        # Update context
        if has_data:
            conversation_context["data_availability"] = "high"
        elif no_data:
            conversation_context["data_availability"] = "none"
        
        return {
            "business_outcome": business_outcome,
            "user_response": user_response,
            "response_analysis": response_analysis,
            "updated_context": conversation_context,
            "next_questions": [
                {
                    "question": "What specific types of data do you have?",
                    "type": "data_types",
                    "priority": "high"
                }
            ] if has_data else [
                {
                    "question": "Would you like to start by creating processes and data collection from scratch?",
                    "type": "process_creation",
                    "priority": "high"
                }
            ],
            "routing_decision": {
                "routing": "content_pillar -> insights_pillar" if has_data else "operations_pillar -> sop_builder_wizard",
                "reason": "You have data available" if has_data else "Let's build from scratch",
                "action": "Upload your data" if has_data else "Start the SOP Builder Wizard"
            },
            "recommendations": {
                "action": "Upload your data and we'll generate insights" if has_data else "Let's create your processes from scratch",
                "next_steps": ["Upload data", "Organize content", "Generate insights"] if has_data else ["Start SOP Builder", "Define processes", "Create workflows"]
            }
        }

    async def _update_conversation_session(self, conversation_id: str, user_response: str, response_result: Dict[str, Any]):
        """Update conversation session with response result."""
        conversation_session = self.active_conversations[conversation_id]
        
        # Add response to conversation
        conversation_session["responses"].append({
            "response": user_response,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": response_result.get("response_analysis", {})
        })
        
        # Update context
        if "updated_context" in response_result:
            conversation_session["context"].update(response_result["updated_context"])
        
        # Update routing decision
        if "routing_decision" in response_result:
            conversation_session["routing_decision"] = response_result["routing_decision"]
        
        # Update recommendations
        if "recommendations" in response_result:
            conversation_session["recommendations"] = response_result["recommendations"]
        
        print(f"✅ Conversation session updated: {conversation_id}")

    async def _generate_next_steps(self, conversation_id: str, response_result: Dict[str, Any]):
        """Generate next steps based on response result."""
        next_steps = {
            "conversation_id": conversation_id,
            "next_questions": response_result.get("next_questions", []),
            "routing_decision": response_result.get("routing_decision", {}),
            "recommendations": response_result.get("recommendations", {}),
            "conversation_stage": "discovery",
            "estimated_completion": "5-10 minutes"
        }
        
        # Determine if conversation is ready for routing
        if response_result.get("routing_decision"):
            next_steps["conversation_stage"] = "routing_ready"
            next_steps["ready_for_journey"] = True
        else:
            next_steps["conversation_stage"] = "discovery"
            next_steps["ready_for_journey"] = False
        
        return next_steps

    # ============================================================================
    # JOURNEY EXECUTION
    # ============================================================================

    async def execute_journey_from_conversation(self, conversation_id: str, user_context: UserContext):
        """
        Execute a journey based on conversation results.
        """
        try:
            print(f"🗣️ Executing journey from conversation: {conversation_id}")
            
            if conversation_id not in self.active_conversations:
                return {
                    "success": False,
                    "error": "Conversation session not found"
                }
            
            conversation_session = self.active_conversations[conversation_id]
            business_outcome = conversation_session["business_outcome"]
            routing_decision = conversation_session.get("routing_decision")
            
            if not routing_decision:
                return {
                    "success": False,
                    "error": "No routing decision available yet"
                }
            
            # Create journey based on routing decision
            journey = await self._create_journey_from_routing(
                business_outcome, routing_decision, user_context
            )
            
            # Update conversation status
            conversation_session["status"] = "journey_created"
            conversation_session["journey_id"] = journey["journey_id"]
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "journey": journey,
                "routing_decision": routing_decision,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Journey execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }

    async def _create_journey_from_routing(self, business_outcome: str, routing_decision: Dict[str, Any], user_context: UserContext):
        """Create a journey based on routing decision."""
        journey_id = f"executed_journey_{int(datetime.utcnow().timestamp())}"
        
        journey = {
            "journey_id": journey_id,
            "business_outcome": business_outcome,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "routing": routing_decision["routing"],
            "reason": routing_decision["reason"],
            "action": routing_decision["action"],
            "stages": self._get_journey_stages(routing_decision["routing"]),
            "current_stage": "initialization"
        }
        
        return journey

    def _get_journey_stages(self, routing: str):
        """Get journey stages based on routing."""
        if "content_pillar" in routing and "insights_pillar" in routing:
            return ["data_upload", "data_organization", "analysis_execution", "insights_generation", "results_delivery"]
        elif "operations_pillar" in routing:
            return ["process_analysis", "workflow_optimization", "implementation", "measurement"]
        elif "sop_builder_wizard" in routing:
            return ["process_definition", "workflow_creation", "documentation", "implementation"]
        elif "ai_platform" in routing:
            return ["data_preparation", "model_training", "evaluation", "deployment", "monitoring"]
        else:
            return ["initialization", "execution", "completion"]

    # ============================================================================
    # HEALTH AND CAPABILITIES
    # ============================================================================

    async def health_check(self):
        """Get health status of the Interactive Journey Manager Service."""
        try:
            health_status = {
                "service_name": "InteractiveJourneyManagerService",
                "status": "healthy",
                "active_conversations_count": len(self.active_conversations),
                "journey_templates_count": len(self.journey_templates),
                "dynamic_analyzer_available": self.dynamic_analyzer is not None,
                "conversation_capabilities": self.conversation_capabilities,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "InteractiveJourneyManagerService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_capabilities(self):
        """Get capabilities of the Interactive Journey Manager Service."""
        return {
            "service_name": "InteractiveJourneyManagerService",
            "capabilities": [
                "interactive_journey_management",
                "conversational_discovery",
                "dynamic_business_outcome_analysis",
                "ai_powered_routing",
                "multi_turn_conversations",
                "context_preservation",
                "progressive_discovery",
                "adaptive_questioning"
            ],
            "journey_templates": list(self.journey_templates.keys()),
            "conversation_capabilities": self.conversation_capabilities,
            "interactive": True,
            "ai_powered": True
        }


# Create service instance factory function
def create_interactive_journey_manager_service(di_container: DIContainerService,
                                              public_works_foundation: PublicWorksFoundationService) -> InteractiveJourneyManagerService:
    """Factory function to create InteractiveJourneyManagerService with proper DI."""
    return InteractiveJourneyManagerService(
        di_container=di_container,
        public_works_foundation=public_works_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
interactive_journey_manager_service = None  # Will be set by foundation services during initialization
