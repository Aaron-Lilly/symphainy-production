#!/usr/bin/env python3
"""
MVP Landing Page Service - Frontend integration for solution discovery

This service provides the landing page integration for solution discovery,
enabling users to submit their business outcomes and get routed to appropriate solution orchestration.

WHAT (Solution Role): I provide landing page integration for solution discovery
HOW (Service Implementation): I use SOA APIs, MCP tools, and liaison agents for solution discovery
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

# Import MCP server
from .mcp_server.mvp_landing_page_mcp_server import MVPLandingPageMCPServer

# Import agents
from .agents.solution_liaison_agent import SolutionLiaisonAgent


class MVPLandingPageService(RealmServiceBase):
    """
    MVP Landing Page Service - Frontend integration for solution discovery
    
    This service provides the landing page integration for solution discovery,
    enabling users to submit their business outcomes and get routed to appropriate solution orchestration.
    """
    
    def __init__(self, di_container: DIContainerService,
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: CuratorFoundationService = None):
        """Initialize MVP Landing Page Service."""
        super().__init__(
            realm_name="solution",
            service_name="mvp_landing_page",
            public_works_foundation=public_works_foundation,
            di_container=di_container,
            curator_foundation=curator_foundation
        )
        
        # Landing page capabilities
        self.landing_page_capabilities = [
            "business_outcome_collection",
            "user_context_analysis",
            "solution_intent_detection",
            "solution_orchestration_routing",
            "frontend_integration"
        ]
        
        # Initialize MCP server
        self.mcp_server = MVPLandingPageMCPServer(self.di_container)
        
        # Initialize agents
        self.liaison_agent = SolutionLiaisonAgent(self.di_container)
        
        # Landing page state
        self.landing_page_sessions = {}
        self.solution_requests = {}
        
        # Initialize MVP landing page service
        self._initialize_mvp_landing_page_service()
    
    def _initialize_mvp_landing_page_service(self):
        """Initialize the MVP landing page service."""
        self.logger.info("🎯 Initializing MVP Landing Page Service for solution discovery")
        
        # Initialize landing page capabilities
        self._initialize_landing_page_capabilities()
        
        # Initialize solution routing
        self._initialize_solution_routing()
        
        self.logger.info("✅ MVP Landing Page Service initialized successfully")
    
    def _initialize_landing_page_capabilities(self):
        """Initialize landing page capabilities."""
        self.landing_page_capabilities = {
            "business_outcome_collection": {
                "enabled": True,
                "methods": ["form_processing", "intent_analysis", "context_extraction"]
            },
            "solution_routing": {
                "enabled": True,
                "methods": ["intent_detection", "orchestration_routing", "context_propagation"]
            },
            "frontend_integration": {
                "enabled": True,
                "methods": ["api_endpoints", "websocket_support", "real_time_communication"]
            }
        }
    
    def _initialize_solution_routing(self):
        """Initialize solution routing capabilities."""
        self.solution_routing = {
            "target_services": [
                "SolutionOrchestrationHubService",
                "UserSolutionDesignService",
                "MVPSolutionInitiatorService"
            ],
            "routing_methods": [
                "intent_based_routing",
                "context_aware_routing",
                "fallback_routing"
            ]
        }
    
    async def initialize(self):
        """Initialize the MVP Landing Page Service."""
        await super().initialize()
        self.logger.info("🎯 MVP Landing Page Service initialized")
    
    async def shutdown(self):
        """Shutdown the MVP Landing Page Service."""
        self.logger.info("🛑 Shutting down MVP Landing Page Service")
        await super().shutdown()
    
    # ============================================================================
    # LANDING PAGE INTEGRATION METHODS
    # ============================================================================
    
    async def handle_landing_page_submission(self, landing_page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle landing page data submission and route to solution orchestration."""
        try:
            self.logger.info("🎯 Handling landing page submission")
            
            # Extract business outcome and user context
            business_outcome = landing_page_data.get("business_outcome", "")
            user_context_data = landing_page_data.get("user_context", {})
            user_context = UserContext(**user_context_data)
            
            # Create landing page session
            session_id = await self._create_landing_page_session(landing_page_data, user_context)
            
            # Analyze solution intent
            intent_analysis = await self._analyze_solution_intent(business_outcome, user_context)
            
            # Route to Solution Orchestration Hub
            solution_orchestration_hub = self.di_container.get_service("SolutionOrchestrationHubService")
            if not solution_orchestration_hub:
                return await self._handle_missing_orchestration_hub(business_outcome, user_context)
            
            # Route to solution orchestration
            orchestration_result = await solution_orchestration_hub.orchestrate_solution(
                user_input=business_outcome,
                user_context=user_context
            )
            
            # Store solution request
            await self._store_solution_request(session_id, orchestration_result)
            
            return {
                "success": True,
                "session_id": session_id,
                "intent_analysis": intent_analysis,
                "orchestration_result": orchestration_result,
                "next_steps": await self._generate_next_steps(orchestration_result),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to handle landing page submission: {e}")
            return {
                "success": False,
                "error": str(e),
                "landing_page_data": landing_page_data
            }
    
    async def _create_landing_page_session(self, landing_page_data: Dict[str, Any], user_context: UserContext) -> str:
        """Create a landing page session."""
        session_id = f"landing_page_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        self.landing_page_sessions[session_id] = {
            "landing_page_data": landing_page_data,
            "user_context": user_context,
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        return session_id
    
    async def _analyze_solution_intent(self, business_outcome: str, user_context: UserContext) -> Dict[str, Any]:
        """Analyze solution intent from business outcome."""
        business_outcome_lower = business_outcome.lower()
        
        # Solution intent patterns
        intent_patterns = {
            "mvp": {
                "keywords": ["mvp", "minimum viable product", "start with basic", "begin", "initial"],
                "confidence_threshold": 0.7
            },
            "poc": {
                "keywords": ["poc", "proof of concept", "validate", "test idea", "prototype"],
                "confidence_threshold": 0.7
            },
            "demo": {
                "keywords": ["demo", "demonstration", "example", "show", "preview"],
                "confidence_threshold": 0.7
            }
        }
        
        # Analyze intent
        intent_scores = {}
        for intent, pattern in intent_patterns.items():
            keyword_matches = sum(1 for keyword in pattern["keywords"] if keyword in business_outcome_lower)
            confidence = keyword_matches / len(pattern["keywords"])
            
            if confidence >= pattern["confidence_threshold"]:
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
                "intent": "mvp",  # Default to MVP for landing page
                "confidence": 0.5,
                "analysis_details": {}
            }
    
    async def _handle_missing_orchestration_hub(self, business_outcome: str, user_context: UserContext) -> Dict[str, Any]:
        """Handle case when Solution Orchestration Hub is not available."""
        return {
            "success": False,
            "error": "Solution Orchestration Hub not available",
            "message": "Solution orchestration service is not available. Please try again later.",
            "business_outcome": business_outcome,
            "fallback_suggestion": "Contact support for assistance with solution discovery"
        }
    
    async def _store_solution_request(self, session_id: str, orchestration_result: Dict[str, Any]) -> None:
        """Store solution request for tracking."""
        self.solution_requests[session_id] = {
            "orchestration_result": orchestration_result,
            "created_at": datetime.utcnow(),
            "status": "processed"
        }
    
    async def _generate_next_steps(self, orchestration_result: Dict[str, Any]) -> List[str]:
        """Generate next steps based on orchestration result."""
        if orchestration_result.get("success", False):
            return [
                "Solution orchestration completed successfully",
                "Proceed to journey orchestration",
                "Begin solution implementation",
                "Monitor progress and adjust as needed"
            ]
        else:
            return [
                "Review solution requirements",
                "Contact support for assistance",
                "Try alternative solution approaches",
                "Provide additional context if needed"
            ]
    
    # ============================================================================
    # SESSION MANAGEMENT
    # ============================================================================
    
    async def get_landing_page_session(self, session_id: str) -> Dict[str, Any]:
        """Get landing page session information."""
        if session_id in self.landing_page_sessions:
            session = self.landing_page_sessions[session_id]
            solution_request = self.solution_requests.get(session_id, {})
            
            return {
                "success": True,
                "session_id": session_id,
                "session_info": session,
                "solution_request": solution_request,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
    
    async def update_landing_page_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update landing page session."""
        if session_id in self.landing_page_sessions:
            self.landing_page_sessions[session_id].update(updates)
            self.landing_page_sessions[session_id]["updated_at"] = datetime.utcnow()
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session updated successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
    
    async def close_landing_page_session(self, session_id: str) -> Dict[str, Any]:
        """Close landing page session."""
        if session_id in self.landing_page_sessions:
            self.landing_page_sessions[session_id]["status"] = "closed"
            self.landing_page_sessions[session_id]["closed_at"] = datetime.utcnow()
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Session closed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
    
    # ============================================================================
    # AGENT INTEGRATION
    # ============================================================================
    
    async def handle_agent_request(self, agent_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent requests for solution discovery."""
        try:
            # Route to liaison agent
            return await self.liaison_agent.process_user_query(
                query=agent_request.get("query", ""),
                conversation_id=agent_request.get("conversation_id", ""),
                user_context=agent_request.get("user_context", UserContext())
            )
            
        except Exception as e:
            self.logger.error(f"Failed to handle agent request: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_request": agent_request
            }
    
    # ============================================================================
    # REALM CAPABILITIES
    # ============================================================================
    
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get MVP Landing Page Service capabilities for realm operations."""
        return {
            "service_name": self.service_name,
            "realm": "solution",
            "service_type": "mvp_landing_page",
            "capabilities": {
                "landing_page_integration": {
                    "enabled": True,
                    "methods": ["form_processing", "intent_analysis", "context_extraction"],
                    "supported_intents": ["mvp", "poc", "demo"]
                },
                "solution_routing": {
                    "enabled": True,
                    "target_services": self.solution_routing["target_services"],
                    "routing_methods": self.solution_routing["routing_methods"]
                },
                "agent_integration": {
                    "enabled": True,
                    "liaison_agent": self.liaison_agent is not None,
                    "mcp_server": self.mcp_server is not None
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


# Create service instance factory function
def create_mvp_landing_page_service(di_container: DIContainerService,
                                  public_works_foundation: PublicWorksFoundationService,
                                  curator_foundation: CuratorFoundationService = None) -> MVPLandingPageService:
    """Factory function to create MVPLandingPageService with proper DI."""
    return MVPLandingPageService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
mvp_landing_page_service = None  # Will be set by foundation services during initialization






