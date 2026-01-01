#!/usr/bin/env python3
"""
Business Outcome Landing Page Service - Creates the business outcome-driven landing page

This service creates the landing page that prompts users for business outcomes after login,
integrating with Guide Agent and Experience Manager for a complete business outcome-driven experience.

WHAT (Journey/Solution Role): I create the business outcome landing page and backend enablement
HOW (Service Implementation): I integrate Guide Agent, Experience Manager, and Frontend Integration
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container import DIContainerService
from utilities import UserContext


class BusinessOutcomeLandingPageService:
    """
    Business Outcome Landing Page Service - Creates business outcome-driven landing page
    
    This service creates the landing page that prompts users for business outcomes after login,
    providing a complete business outcome-driven user experience.
    """

    def __init__(self, di_container: DIContainerService):
        """Initialize Business Outcome Landing Page Service."""
        self.di_container = di_container
        
        # Guide Agent integration
        self.guide_agent = None  # Will be injected
        
        # Experience Manager integration
        self.experience_manager = None  # Will be injected
        
        # Frontend Integration
        self.frontend_integration = None  # Will be injected
        
        # Journey Orchestrator
        self.journey_orchestrator = None  # Will be injected
        
        # Business outcome templates
        self.business_outcome_templates = {
            "data_analysis": {
                "name": "Data Analysis & Insights",
                "description": "Analyze your data to generate actionable business insights",
                "icon": "📊",
                "examples": [
                    "Analyze customer data for insights",
                    "Generate sales performance reports",
                    "Create data visualizations"
                ],
                "guide_agent_prompt": "I can help you analyze your data and generate insights. What data would you like to analyze?"
            },
            "process_optimization": {
                "name": "Process Optimization",
                "description": "Optimize your business processes and workflows for better efficiency",
                "icon": "⚡",
                "examples": [
                    "Optimize workflow processes",
                    "Improve operational efficiency",
                    "Streamline business operations"
                ],
                "guide_agent_prompt": "I can help you optimize your processes. What workflow would you like to improve?"
            },
            "strategic_planning": {
                "name": "Strategic Planning",
                "description": "Create strategic plans and roadmaps for your business goals",
                "icon": "🎯",
                "examples": [
                    "Create strategic roadmaps",
                    "Plan business objectives",
                    "Develop growth strategies"
                ],
                "guide_agent_prompt": "I can help you create strategic plans. What business goals would you like to plan for?"
            },
            "content_management": {
                "name": "Content Management",
                "description": "Organize and manage your content and documents effectively",
                "icon": "📁",
                "examples": [
                    "Organize document library",
                    "Manage content workflows",
                    "Create content catalogs"
                ],
                "guide_agent_prompt": "I can help you manage your content. What content would you like to organize?"
            }
        }
        
        print(f"🏠 Business Outcome Landing Page Service initialized")

    async def initialize(self):
        """Initialize the Business Outcome Landing Page Service."""
        try:
            print("🏠 Initializing Business Outcome Landing Page Service...")
            
            # Inject dependencies
            await self._inject_dependencies()
            
            # Initialize landing page templates
            await self._initialize_landing_page_templates()
            
            print("✅ Business Outcome Landing Page Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Business Outcome Landing Page Service: {e}")
            raise

    async def _inject_dependencies(self):
        """Inject required dependencies."""
        try:
            # Guide Agent for business outcome collection
            self.guide_agent = self.di_container.get_service("GuideAgent")
            print("✅ Guide Agent injected")
            
            # Experience Manager for user experience orchestration
            self.experience_manager = self.di_container.get_service("ExperienceManagerService")
            print("✅ Experience Manager injected")
            
            # Frontend Integration for UI components
            self.frontend_integration = self.di_container.get_service("FrontendIntegrationService")
            print("✅ Frontend Integration injected")
            
            # Journey Orchestrator for business outcome journeys
            self.journey_orchestrator = self.di_container.get_service("JourneyOrchestratorService")
            print("✅ Journey Orchestrator injected")
            
        except Exception as e:
            print(f"⚠️ Some dependencies not available: {e}")

    async def _initialize_landing_page_templates(self):
        """Initialize landing page templates."""
        # Add metadata to templates
        for template_id, template in self.business_outcome_templates.items():
            template["id"] = template_id
            template["created_at"] = datetime.utcnow().isoformat()
            template["version"] = "1.0.0"
        
        print("✅ Landing page templates initialized")

    # ============================================================================
    # LANDING PAGE CREATION METHODS
    # ============================================================================

    async def render_landing_page(self, user_context: UserContext):
        """
        Render the business outcome landing page for a user.
        """
        try:
            print(f"🏠 Rendering business outcome landing page for user: {user_context.user_id}")
            
            # Get available business outcomes for the user
            available_outcomes = await self._get_available_business_outcomes(user_context)
            
            # Create landing page content
            landing_page_content = {
                "title": "What business outcome would you like to achieve?",
                "subtitle": "Tell our Guide Agent what you'd like to accomplish",
                "welcome_message": f"Welcome back, {user_context.user_id}! Let's achieve your business goals together.",
                "available_outcomes": available_outcomes,
                "guide_agent_prompt": "I'm here to help you achieve your business goals. What would you like to accomplish?",
                "use_cases": [
                    "Data Analysis & Insights",
                    "Process Optimization", 
                    "Strategic Planning",
                    "Content Management",
                    "Custom Business Outcome"
                ],
                "landing_page_metadata": {
                    "user_id": user_context.user_id,
                    "tenant_id": user_context.tenant_id,
                    "rendered_at": datetime.utcnow().isoformat(),
                    "version": "1.0.0"
                }
            }
            
            return landing_page_content
            
        except Exception as e:
            print(f"❌ Landing page rendering failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "landing_page_content": None
            }

    async def _get_available_business_outcomes(self, user_context: UserContext):
        """Get available business outcomes for the user."""
        try:
            # Get business outcomes from Journey Orchestrator
            if self.journey_orchestrator:
                outcomes_result = await self.journey_orchestrator.get_available_business_outcomes(
                    user_context.tenant_id, user_context.user_id
                )
                
                if outcomes_result.get("success"):
                    return outcomes_result["available_outcomes"]
            
            # Fallback to default outcomes
            return [
                {
                    "outcome_id": outcome_id,
                    "name": template["name"],
                    "description": template["description"],
                    "icon": template["icon"],
                    "examples": template["examples"]
                }
                for outcome_id, template in self.business_outcome_templates.items()
            ]
            
        except Exception as e:
            print(f"⚠️ Failed to get available business outcomes: {e}")
            return []

    # ============================================================================
    # GUIDE AGENT INTEGRATION
    # ============================================================================

    async def collect_business_outcome(self, user_input: str, user_context: UserContext):
        """
        Collect business outcome from user input using Guide Agent.
        """
        try:
            print(f"🤖 Collecting business outcome from user input: {user_input}")
            
            # Use Guide Agent to analyze user input
            if self.guide_agent:
                guide_analysis = await self.guide_agent.analyze_business_outcome_input(
                    user_input, user_context
                )
            else:
                # Fallback analysis
                guide_analysis = await self._fallback_business_outcome_analysis(user_input, user_context)
            
            # Create business outcome journey
            journey_result = await self._create_business_outcome_journey(
                guide_analysis, user_context
            )
            
            return {
                "user_input": user_input,
                "business_outcome": guide_analysis.get("business_outcome"),
                "use_case": guide_analysis.get("use_case"),
                "confidence_score": guide_analysis.get("confidence_score", 0.8),
                "guide_agent_recommendations": guide_analysis.get("recommendations", []),
                "journey_result": journey_result,
                "collection_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Business outcome collection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input
            }

    async def _fallback_business_outcome_analysis(self, user_input: str, user_context: UserContext):
        """Fallback business outcome analysis when Guide Agent is not available."""
        user_input_lower = user_input.lower()
        
        # Simple keyword matching
        for outcome_id, template in self.business_outcome_templates.items():
            for keyword in template["examples"]:
                if any(word in user_input_lower for word in keyword.lower().split()):
                    return {
                        "business_outcome": outcome_id,
                        "use_case": "mvp",
                        "confidence_score": 0.7,
                        "recommendations": [f"Based on your input, I recommend {template['name']}"]
                    }
        
        # Default to data analysis
        return {
            "business_outcome": "data_analysis",
            "use_case": "mvp",
            "confidence_score": 0.5,
            "recommendations": ["I'll help you with data analysis. Please provide more details about what you'd like to analyze."]
        }

    async def _create_business_outcome_journey(self, guide_analysis: Dict[str, Any], user_context: UserContext):
        """Create business outcome journey using Journey Orchestrator."""
        try:
            if self.journey_orchestrator:
                journey_result = await self.journey_orchestrator.create_business_outcome_journey(
                    business_outcome=guide_analysis.get("business_outcome"),
                    use_case=guide_analysis.get("use_case"),
                    user_context=user_context
                )
                return journey_result
            else:
                return {
                    "success": False,
                    "error": "Journey Orchestrator not available"
                }
                
        except Exception as e:
            print(f"❌ Business outcome journey creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ============================================================================
    # EXPERIENCE MANAGER INTEGRATION
    # ============================================================================

    async def enable_business_outcome_experience(self, business_outcome: str, use_case: str, user_context: UserContext):
        """
        Enable business outcome-driven user experience using Experience Manager.
        """
        try:
            print(f"🎭 Enabling business outcome experience: {business_outcome}")
            
            # Create business outcome user journey
            user_journey = await self._create_business_outcome_user_journey(
                business_outcome, use_case, user_context
            )
            
            # Orchestrate cross-dimensional experience
            experience_orchestration = await self._orchestrate_business_outcome_experience(
                business_outcome, use_case, user_context
            )
            
            # Create frontend integration
            frontend_integration = await self._create_frontend_integration(
                user_journey, experience_orchestration
            )
            
            return {
                "user_journey": user_journey,
                "experience_orchestration": experience_orchestration,
                "frontend_integration": frontend_integration,
                "enabled_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Business outcome experience enablement failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_business_outcome_user_journey(self, business_outcome: str, use_case: str, user_context: UserContext):
        """Create business outcome user journey."""
        journey_id = f"business_outcome_{int(datetime.utcnow().timestamp())}"
        
        user_journey = {
            "journey_id": journey_id,
            "business_outcome": business_outcome,
            "use_case": use_case,
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "stages": [
                "business_outcome_identification",
                "solution_architecture",
                "cross_dimensional_orchestration",
                "execution",
                "results_delivery"
            ],
            "current_stage": "business_outcome_identification"
        }
        
        return user_journey

    async def _orchestrate_business_outcome_experience(self, business_outcome: str, use_case: str, user_context: UserContext):
        """Orchestrate business outcome experience using Experience Manager."""
        try:
            if self.experience_manager:
                orchestration_result = await self.experience_manager.orchestrate_for_business_outcome(
                    business_outcome, use_case, user_context
                )
                return orchestration_result
            else:
                return {
                    "orchestration_status": "fallback",
                    "message": "Experience Manager not available, using fallback orchestration"
                }
                
        except Exception as e:
            print(f"⚠️ Experience orchestration failed: {e}")
            return {
                "orchestration_status": "failed",
                "error": str(e)
            }

    async def _create_frontend_integration(self, user_journey: Dict[str, Any], experience_orchestration: Dict[str, Any]):
        """Create frontend integration for business outcome experience."""
        try:
            if self.frontend_integration:
                frontend_request = {
                    "journey_id": user_journey["journey_id"],
                    "business_outcome": user_journey["business_outcome"],
                    "use_case": user_journey["use_case"],
                    "orchestration_result": experience_orchestration
                }
                
                frontend_result = await self.frontend_integration.integrate_business_outcome_experience(
                    frontend_request
                )
                return frontend_result
            else:
                return {
                    "integration_status": "fallback",
                    "message": "Frontend Integration not available, using fallback integration"
                }
                
        except Exception as e:
            print(f"⚠️ Frontend integration failed: {e}")
            return {
                "integration_status": "failed",
                "error": str(e)
            }

    # ============================================================================
    # FRONTEND INTEGRATION METHODS
    # ============================================================================

    async def create_business_outcome_components(self, frontend_request: Dict[str, Any]):
        """Create frontend components for business outcome experience."""
        components = {
            "business_outcome_dashboard": {
                "type": "dashboard",
                "title": f"Business Outcome: {frontend_request['business_outcome']}",
                "use_case": frontend_request["use_case"],
                "journey_id": frontend_request["journey_id"],
                "status": "active"
            },
            "journey_progress": {
                "type": "progress_tracker",
                "journey_id": frontend_request["journey_id"],
                "stages": frontend_request["orchestration_result"].get("stages", []),
                "current_stage": "business_outcome_identification"
            },
            "cross_dimensional_status": {
                "type": "status_panel",
                "dimensions": frontend_request["orchestration_result"].get("dimensions", {}),
                "coordination_status": "active"
            },
            "guide_agent_chat": {
                "type": "chat_interface",
                "title": "Guide Agent",
                "prompt": "I'm here to help you achieve your business goals. What would you like to accomplish?",
                "enabled": True
            }
        }
        
        return components

    # ============================================================================
    # HEALTH AND CAPABILITIES
    # ============================================================================

    async def health_check(self):
        """Get health status of the Business Outcome Landing Page Service."""
        try:
            health_status = {
                "service_name": "BusinessOutcomeLandingPageService",
                "status": "healthy",
                "business_outcome_templates_count": len(self.business_outcome_templates),
                "dependencies": {
                    "guide_agent": self.guide_agent is not None,
                    "experience_manager": self.experience_manager is not None,
                    "frontend_integration": self.frontend_integration is not None,
                    "journey_orchestrator": self.journey_orchestrator is not None
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "BusinessOutcomeLandingPageService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_capabilities(self):
        """Get capabilities of the Business Outcome Landing Page Service."""
        return {
            "service_name": "BusinessOutcomeLandingPageService",
            "capabilities": [
                "landing_page_rendering",
                "business_outcome_collection",
                "guide_agent_integration",
                "experience_manager_integration",
                "frontend_integration",
                "journey_creation",
                "user_experience_orchestration"
            ],
            "business_outcome_templates": list(self.business_outcome_templates.keys()),
            "integration_enabled": True,
            "landing_page_version": "1.0.0"
        }


# Create service instance factory function
def create_business_outcome_landing_page_service(di_container: DIContainerService) -> BusinessOutcomeLandingPageService:
    """Factory function to create BusinessOutcomeLandingPageService with proper DI."""
    return BusinessOutcomeLandingPageService(di_container)


# Create default service instance (will be properly initialized by foundation services)
business_outcome_landing_page_service = None  # Will be set by foundation services during initialization
