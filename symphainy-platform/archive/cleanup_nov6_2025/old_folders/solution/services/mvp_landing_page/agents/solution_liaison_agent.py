#!/usr/bin/env python3
"""
Solution Liaison Agent

Liaison agent for the MVP Landing Page Service following Smart City patterns.
Handles user interaction and provides guidance for solution discovery.

WHAT (Solution Role): I provide user guidance for solution discovery
HOW (Smart City Role): I use liaison agent patterns for user interaction
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import UserContext
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase


class SolutionLiaisonAgent(AgentBase):
    """
    Solution Liaison Agent
    
    Liaison agent that handles user interaction and provides guidance for solution discovery.
    Provides conversational interface for solution discovery operations.
    """
    
    def __init__(self, di_container=None):
        """Initialize the Solution Liaison Agent."""
        super().__init__(
            agent_name="SolutionLiaisonAgent",
            agent_type="liaison",
            business_domain="solution_discovery",
            di_container=di_container
        )
        
        self.di_container = di_container
        self.service_name = "SolutionLiaisonAgent"
        
        # Agent capabilities
        self.capabilities = [
            "solution_discovery_guidance",
            "business_outcome_analysis",
            "solution_intent_detection",
            "orchestration_routing",
            "user_context_analysis"
        ]
        
        # Conversation context
        self.conversation_contexts: Dict[str, Dict[str, Any]] = {}
        
        # Initialize logger
        self.logger = logging.getLogger(self.service_name)
        
        self.logger.info(f"🤖 {self.service_name} initialized - Solution Liaison Agent")
    
    async def process_user_query(self, query: str, conversation_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Process user query for solution discovery guidance."""
        try:
            self.logger.info(f"🎯 Processing user query: {query}")
            
            # Analyze query intent
            intent_analysis = await self._analyze_query_intent(query, user_context)
            
            # Generate response based on intent
            response = await self._generate_response(intent_analysis, query, user_context)
            
            # Update conversation context
            await self._update_conversation_context(conversation_id, query, response, user_context)
            
            return {
                "success": True,
                "query": query,
                "intent_analysis": intent_analysis,
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process user query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _analyze_query_intent(self, query: str, user_context: UserContext) -> Dict[str, Any]:
        """Analyze query intent for solution discovery."""
        query_lower = query.lower()
        
        # Intent patterns
        intent_patterns = {
            "solution_discovery": {
                "keywords": ["solution", "help", "need", "want", "looking for", "business outcome"],
                "patterns": [r"need.*solution", r"looking.*for", r"want.*help", r"business.*outcome"]
            },
            "mvp_guidance": {
                "keywords": ["mvp", "minimum viable", "start", "begin", "initial"],
                "patterns": [r"mvp", r"minimum.*viable", r"start.*with", r"begin.*solution"]
            },
            "poc_guidance": {
                "keywords": ["poc", "proof of concept", "validate", "test", "prototype"],
                "patterns": [r"poc", r"proof.*concept", r"validate.*idea", r"test.*concept"]
            },
            "demo_guidance": {
                "keywords": ["demo", "demonstration", "example", "show", "preview"],
                "patterns": [r"demo", r"demonstration", r"show.*example", r"preview"]
            },
            "general_help": {
                "keywords": ["help", "how", "what", "explain", "guide"],
                "patterns": [r"help.*me", r"how.*to", r"what.*is", r"explain.*to"]
            }
        }
        
        # Analyze intent
        intent_scores = {}
        for intent, pattern in intent_patterns.items():
            keyword_matches = sum(1 for keyword in pattern["keywords"] if keyword in query_lower)
            pattern_matches = sum(1 for pattern_regex in pattern["patterns"] 
                                if any(keyword in query_lower for keyword in pattern["keywords"]))
            
            confidence = (keyword_matches + pattern_matches) / (len(pattern["keywords"]) + len(pattern["patterns"]))
            if confidence > 0:
                intent_scores[intent] = confidence
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return {
                "intent": best_intent[0],
                "confidence": best_intent[1],
                "analysis_details": intent_scores
            }
        else:
            return {
                "intent": "general_help",
                "confidence": 0.5,
                "analysis_details": {}
            }
    
    async def _generate_response(self, intent_analysis: Dict[str, Any], query: str, user_context: UserContext) -> Dict[str, Any]:
        """Generate response based on intent analysis."""
        intent = intent_analysis.get("intent", "general_help")
        
        if intent == "solution_discovery":
            return await self._generate_solution_discovery_response(query, user_context)
        elif intent == "mvp_guidance":
            return await self._generate_mvp_guidance_response(query, user_context)
        elif intent == "poc_guidance":
            return await self._generate_poc_guidance_response(query, user_context)
        elif intent == "demo_guidance":
            return await self._generate_demo_guidance_response(query, user_context)
        else:
            return await self._generate_general_help_response(query, user_context)
    
    async def _generate_solution_discovery_response(self, query: str, user_context: UserContext) -> Dict[str, Any]:
        """Generate response for solution discovery."""
        return {
            "message": "I can help you discover the right solution for your business needs. Let me guide you through the process.",
            "suggestions": [
                "Tell me about your business outcome or problem you're trying to solve",
                "Describe what you want to achieve with your solution",
                "Let me know if you're looking for an MVP, POC, or demonstration",
                "Share any specific requirements or constraints you have"
            ],
            "next_steps": [
                "Provide your business outcome description",
                "I'll analyze your requirements",
                "I'll recommend the appropriate solution type",
                "I'll guide you through the solution discovery process"
            ],
            "capabilities": [
                "Business outcome analysis",
                "Solution type recommendation",
                "Requirements gathering",
                "Solution orchestration guidance"
            ]
        }
    
    async def _generate_mvp_guidance_response(self, query: str, user_context: UserContext) -> Dict[str, Any]:
        """Generate response for MVP guidance."""
        return {
            "message": "Great! You're looking for an MVP (Minimum Viable Product) solution. This is perfect for getting started with a basic implementation.",
            "mvp_guidance": [
                "MVP solutions are ideal for validating your business concept",
                "They provide core functionality without complex features",
                "Perfect for testing market demand and user feedback",
                "Can be built and deployed quickly (2-4 weeks typically)"
            ],
            "next_steps": [
                "Describe your business outcome in detail",
                "I'll analyze your requirements for MVP scope",
                "I'll recommend the appropriate MVP approach",
                "I'll guide you through the MVP development process"
            ],
            "mvp_benefits": [
                "Fast time to market",
                "Lower development costs",
                "Early user feedback",
                "Foundation for future expansion"
            ]
        }
    
    async def _generate_poc_guidance_response(self, query: str, user_context: UserContext) -> Dict[str, Any]:
        """Generate response for POC guidance."""
        return {
            "message": "Excellent! You're looking for a POC (Proof of Concept) solution. This is perfect for validating specific ideas or technologies.",
            "poc_guidance": [
                "POC solutions are ideal for testing specific concepts",
                "They validate technical feasibility and business value",
                "Perfect for stakeholder buy-in and decision making",
                "Can be built and tested quickly (4-8 weeks typically)"
            ],
            "next_steps": [
                "Describe the specific concept you want to validate",
                "I'll analyze your POC requirements",
                "I'll recommend the appropriate POC approach",
                "I'll guide you through the POC development process"
            ],
            "poc_benefits": [
                "Concept validation",
                "Technical feasibility proof",
                "Stakeholder confidence",
                "Risk mitigation"
            ]
        }
    
    async def _generate_demo_guidance_response(self, query: str, user_context: UserContext) -> Dict[str, Any]:
        """Generate response for demo guidance."""
        return {
            "message": "Perfect! You're looking for a demonstration solution. This is ideal for showing capabilities and generating interest.",
            "demo_guidance": [
                "Demo solutions are perfect for showcasing capabilities",
                "They demonstrate value without full implementation",
                "Ideal for presentations and stakeholder engagement",
                "Can be built quickly (1-2 weeks typically)"
            ],
            "next_steps": [
                "Describe what you want to demonstrate",
                "I'll analyze your demo requirements",
                "I'll recommend the appropriate demo approach",
                "I'll guide you through the demo development process"
            ],
            "demo_benefits": [
                "Quick capability showcase",
                "Stakeholder engagement",
                "Interest generation",
                "Concept validation"
            ]
        }
    
    async def _generate_general_help_response(self, query: str, user_context: UserContext) -> Dict[str, Any]:
        """Generate response for general help."""
        return {
            "message": "I'm here to help you discover the right solution for your business needs. Let me explain how I can assist you.",
            "how_i_can_help": [
                "Analyze your business outcome and requirements",
                "Recommend the appropriate solution type (MVP, POC, Demo)",
                "Guide you through the solution discovery process",
                "Connect you with the right solution orchestration"
            ],
            "solution_types": [
                "MVP (Minimum Viable Product) - Basic implementation for validation",
                "POC (Proof of Concept) - Specific concept validation",
                "Demo - Capability demonstration and showcase"
            ],
            "getting_started": [
                "Tell me about your business outcome or problem",
                "Describe what you want to achieve",
                "Let me know your preferred solution type",
                "I'll guide you through the process"
            ]
        }
    
    async def _update_conversation_context(self, conversation_id: str, query: str, response: Dict[str, Any], user_context: UserContext) -> None:
        """Update conversation context."""
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = {
                "queries": [],
                "responses": [],
                "user_context": user_context,
                "created_at": datetime.utcnow()
            }
        
        self.conversation_contexts[conversation_id]["queries"].append(query)
        self.conversation_contexts[conversation_id]["responses"].append(response)
        self.conversation_contexts[conversation_id]["updated_at"] = datetime.utcnow()
    
    async def get_conversation_history(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation history."""
        if conversation_id in self.conversation_contexts:
            return {
                "success": True,
                "conversation_id": conversation_id,
                "conversation_context": self.conversation_contexts[conversation_id],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Conversation not found",
                "conversation_id": conversation_id
            }
    
    async def clear_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Clear conversation context."""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
            return {
                "success": True,
                "message": "Conversation cleared successfully",
                "conversation_id": conversation_id
            }
        else:
            return {
                "success": False,
                "error": "Conversation not found",
                "conversation_id": conversation_id
            }
    
    async def get_agent_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return self.capabilities
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Solution Liaison Agent - Provides conversational interface and user guidance for solution discovery operations"
