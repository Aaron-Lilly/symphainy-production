#!/usr/bin/env python3
"""
MVP Journey Manager Service - Handles MVP-specific journey flows

This service handles MVP-specific journey flows and provides intelligent routing
based on business outcomes and data requirements.

WHAT (Journey/Solution Role): I handle MVP-specific journey flows and intelligent routing
HOW (Service Implementation): I analyze business outcomes and route users to appropriate platform capabilities
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


class MVPJourneyManagerService:
    """
    MVP Journey Manager Service - Handles MVP-specific journey flows and intelligent routing
    
    This service provides intelligent routing based on business outcomes and data requirements,
    guiding users to the most appropriate platform capabilities for their specific needs.
    """

    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize MVP Journey Manager Service."""
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Business outcome routing patterns
        self.business_outcome_routing = {
            "call_center_transformation": {
                "name": "Call Center Transformation",
                "data_requirements": [
                    {
                        "type": "volumetric_data",
                        "description": "Call volume, duration, and performance metrics",
                        "sources": ["CRM", "phone_systems", "performance_dashboards"],
                        "routing": "content_pillar"
                    },
                    {
                        "type": "process_documentation", 
                        "description": "SOPs, scripts, and process flows",
                        "sources": ["documentation", "training_materials", "process_maps"],
                        "routing": "content_pillar -> operations_pillar"
                    },
                    {
                        "type": "none_available",
                        "description": "No existing data or documentation",
                        "sources": [],
                        "routing": "operations_pillar -> sop_builder_wizard"
                    }
                ]
            },
            "data_analysis": {
                "name": "Data Analysis & Insights",
                "data_requirements": [
                    {
                        "type": "structured_data",
                        "description": "Databases, spreadsheets, CSV files",
                        "sources": ["databases", "excel_files", "csv_files"],
                        "routing": "content_pillar -> insights_pillar"
                    },
                    {
                        "type": "unstructured_data",
                        "description": "Documents, emails, text files",
                        "sources": ["documents", "emails", "text_files"],
                        "routing": "content_pillar -> insights_pillar"
                    }
                ]
            },
            "process_optimization": {
                "name": "Process Optimization",
                "data_requirements": [
                    {
                        "type": "process_data",
                        "description": "Workflow data, task completion times, bottlenecks",
                        "sources": ["workflow_systems", "task_tracking", "performance_metrics"],
                        "routing": "content_pillar -> operations_pillar"
                    },
                    {
                        "type": "documentation",
                        "description": "Process documentation and procedures",
                        "sources": ["sops", "procedures", "training_materials"],
                        "routing": "content_pillar -> operations_pillar"
                    }
                ]
            }
        }
        
        # Data requirement questions
        self.data_requirement_questions = {
            "volumetric_data": [
                "Do you have call volume data from your phone system?",
                "Do you have performance metrics from your CRM?",
                "Do you have dashboards showing call center KPIs?"
            ],
            "process_documentation": [
                "Do you have written procedures or SOPs for your call center?",
                "Do you have training materials or scripts?",
                "Do you have process flow diagrams or documentation?"
            ],
            "structured_data": [
                "Do you have data in databases or spreadsheets?",
                "Do you have CSV files with your data?",
                "Do you have Excel files with structured data?"
            ],
            "unstructured_data": [
                "Do you have documents or text files to analyze?",
                "Do you have emails or communications to analyze?",
                "Do you have reports or written materials?"
            ]
        }
        
        # Routing recommendations
        self.routing_recommendations = {
            "content_pillar": {
                "name": "Content Pillar",
                "description": "Upload and organize your data and documents",
                "action": "Upload your data to get started with analysis",
                "next_steps": ["Upload data", "Organize content", "Prepare for analysis"]
            },
            "content_pillar -> operations_pillar": {
                "name": "Content + Operations Pillar",
                "description": "Upload documentation and optimize processes",
                "action": "Upload your process documentation and we'll help optimize your workflows",
                "next_steps": ["Upload documentation", "Process analysis", "Workflow optimization"]
            },
            "operations_pillar -> sop_builder_wizard": {
                "name": "SOP Builder Wizard",
                "description": "Create standard operating procedures from scratch",
                "action": "Let's build your processes step by step using our SOP Builder Wizard",
                "next_steps": ["Start SOP Builder", "Define processes", "Create documentation"]
            },
            "content_pillar -> insights_pillar": {
                "name": "Content + Insights Pillar", 
                "description": "Upload data and generate insights",
                "action": "Upload your data and we'll generate actionable insights",
                "next_steps": ["Upload data", "Data analysis", "Insights generation"]
            }
        }
        
        print(f"🎯 MVP Journey Manager Service initialized")

    async def initialize(self):
        """Initialize the MVP Journey Manager Service."""
        try:
            print("🎯 Initializing MVP Journey Manager Service...")
            
            # Initialize routing patterns
            await self._initialize_routing_patterns()
            
            # Initialize data requirement analysis
            await self._initialize_data_requirement_analysis()
            
            print("✅ MVP Journey Manager Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize MVP Journey Manager Service: {e}")
            raise

    async def _initialize_routing_patterns(self):
        """Initialize routing patterns for different business outcomes."""
        # Add metadata to routing patterns
        for outcome_id, outcome_data in self.business_outcome_routing.items():
            outcome_data["id"] = outcome_id
            outcome_data["created_at"] = datetime.utcnow().isoformat()
            outcome_data["version"] = "1.0.0"
        
        print("✅ Routing patterns initialized")

    async def _initialize_data_requirement_analysis(self):
        """Initialize data requirement analysis capabilities."""
        self.analysis_capabilities = {
            "data_type_detection": True,
            "routing_recommendation": True,
            "user_guidance": True,
            "progressive_discovery": True
        }
        print("✅ Data requirement analysis initialized")

    # ============================================================================
    # BUSINESS OUTCOME ROUTING METHODS
    # ============================================================================

    async def analyze_business_outcome_and_route(self, business_outcome: str, user_context: UserContext):
        """
        Analyze business outcome and provide intelligent routing recommendations.
        """
        try:
            print(f"🎯 Analyzing business outcome and routing: {business_outcome}")
            
            # 1. Analyze business outcome requirements
            outcome_analysis = await self._analyze_business_outcome_requirements(business_outcome)
            
            # 2. Determine data requirements
            data_requirements = await self._determine_data_requirements(outcome_analysis)
            
            # 3. Generate routing questions
            routing_questions = await self._generate_routing_questions(data_requirements)
            
            # 4. Create routing recommendations
            routing_recommendations = await self._create_routing_recommendations(
                business_outcome, data_requirements
            )
            
            return {
                "business_outcome": business_outcome,
                "outcome_analysis": outcome_analysis,
                "data_requirements": data_requirements,
                "routing_questions": routing_questions,
                "routing_recommendations": routing_recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Business outcome routing analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "business_outcome": business_outcome
            }

    async def _analyze_business_outcome_requirements(self, business_outcome: str):
        """Analyze requirements for a specific business outcome."""
        if business_outcome in self.business_outcome_routing:
            outcome_data = self.business_outcome_routing[business_outcome]
            return {
                "outcome_id": business_outcome,
                "name": outcome_data["name"],
                "data_requirements": outcome_data["data_requirements"],
                "complexity": "medium",
                "estimated_duration": "1-3 hours"
            }
        else:
            # Default analysis for unknown business outcomes
            return {
                "outcome_id": business_outcome,
                "name": f"Custom Business Outcome: {business_outcome}",
                "data_requirements": [
                    {
                        "type": "general_data",
                        "description": "Any relevant data for your business outcome",
                        "sources": ["various"],
                        "routing": "content_pillar -> insights_pillar"
                    }
                ],
                "complexity": "unknown",
                "estimated_duration": "variable"
            }

    async def _determine_data_requirements(self, outcome_analysis: Dict[str, Any]):
        """Determine data requirements based on business outcome analysis."""
        data_requirements = outcome_analysis.get("data_requirements", [])
        
        # Add analysis metadata
        for requirement in data_requirements:
            requirement["analysis_metadata"] = {
                "analyzed_at": datetime.utcnow().isoformat(),
                "priority": "high" if requirement["type"] != "none_available" else "low",
                "routing_confidence": 0.8
            }
        
        return data_requirements

    async def _generate_routing_questions(self, data_requirements: List[Dict[str, Any]]):
        """Generate routing questions based on data requirements."""
        routing_questions = []
        
        for requirement in data_requirements:
            requirement_type = requirement["type"]
            
            if requirement_type in self.data_requirement_questions:
                questions = self.data_requirement_questions[requirement_type]
                routing_questions.append({
                    "requirement_type": requirement_type,
                    "description": requirement["description"],
                    "questions": questions,
                    "routing": requirement["routing"]
                })
        
        return routing_questions

    async def _create_routing_recommendations(self, business_outcome: str, data_requirements: List[Dict[str, Any]]):
        """Create routing recommendations based on data requirements."""
        recommendations = []
        
        for requirement in data_requirements:
            routing = requirement["routing"]
            
            if routing in self.routing_recommendations:
                recommendation = self.routing_recommendations[routing].copy()
                recommendation["requirement_type"] = requirement["type"]
                recommendation["data_sources"] = requirement["sources"]
                recommendations.append(recommendation)
        
        return recommendations

    # ============================================================================
    # INTERACTIVE ROUTING METHODS
    # ============================================================================

    async def process_user_response(self, business_outcome: str, user_response: str, user_context: UserContext):
        """
        Process user response to routing questions and provide next steps.
        """
        try:
            print(f"🎯 Processing user response for business outcome: {business_outcome}")
            
            # 1. Analyze user response
            response_analysis = await self._analyze_user_response(user_response)
            
            # 2. Determine routing based on response
            routing_decision = await self._determine_routing_decision(
                business_outcome, response_analysis
            )
            
            # 3. Generate next steps
            next_steps = await self._generate_next_steps(routing_decision)
            
            # 4. Create user journey
            user_journey = await self._create_user_journey(
                business_outcome, routing_decision, user_context
            )
            
            return {
                "business_outcome": business_outcome,
                "user_response": user_response,
                "response_analysis": response_analysis,
                "routing_decision": routing_decision,
                "next_steps": next_steps,
                "user_journey": user_journey,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ User response processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_response": user_response
            }

    async def _analyze_user_response(self, user_response: str):
        """Analyze user response to determine data availability."""
        user_response_lower = user_response.lower()
        
        # Check for positive indicators
        positive_indicators = ["yes", "have", "available", "got", "yes we", "we have", "we do"]
        negative_indicators = ["no", "don't", "don't have", "no we", "we don't", "not available"]
        
        has_data = any(indicator in user_response_lower for indicator in positive_indicators)
        no_data = any(indicator in user_response_lower for indicator in negative_indicators)
        
        return {
            "has_data": has_data,
            "no_data": no_data,
            "confidence": 0.8 if (has_data or no_data) else 0.5,
            "response_type": "positive" if has_data else "negative" if no_data else "unclear"
        }

    async def _determine_routing_decision(self, business_outcome: str, response_analysis: Dict[str, Any]):
        """Determine routing decision based on business outcome and response."""
        if business_outcome == "call_center_transformation":
            if response_analysis["has_data"]:
                return {
                    "routing": "content_pillar",
                    "reason": "User has data available for analysis",
                    "action": "Direct to content pillar to upload and analyze data"
                }
            elif response_analysis["no_data"]:
                return {
                    "routing": "operations_pillar -> sop_builder_wizard",
                    "reason": "No data available, suggest SOP Builder Wizard",
                    "action": "Direct to SOP Builder Wizard to create processes from scratch"
                }
            else:
                return {
                    "routing": "content_pillar",
                    "reason": "Unclear response, default to content pillar",
                    "action": "Ask for clarification and suggest content upload"
                }
        else:
            # Default routing for other business outcomes
            return {
                "routing": "content_pillar -> insights_pillar",
                "reason": "Default routing for business outcome",
                "action": "Direct to content pillar for data upload and analysis"
            }

    async def _generate_next_steps(self, routing_decision: Dict[str, Any]):
        """Generate next steps based on routing decision."""
        routing = routing_decision["routing"]
        
        if routing in self.routing_recommendations:
            recommendation = self.routing_recommendations[routing]
            return {
                "routing": routing,
                "name": recommendation["name"],
                "description": recommendation["description"],
                "action": recommendation["action"],
                "next_steps": recommendation["next_steps"],
                "estimated_duration": "30-60 minutes"
            }
        else:
            return {
                "routing": routing,
                "name": "Custom Routing",
                "description": "Custom routing for your business outcome",
                "action": "Follow the recommended path for your business outcome",
                "next_steps": ["Start your journey", "Follow recommendations", "Achieve your outcome"],
                "estimated_duration": "Variable"
            }

    async def _create_user_journey(self, business_outcome: str, routing_decision: Dict[str, Any], user_context: UserContext):
        """Create user journey based on routing decision."""
        journey_id = f"mvp_journey_{int(datetime.utcnow().timestamp())}"
        
        user_journey = {
            "journey_id": journey_id,
            "business_outcome": business_outcome,
            "routing": routing_decision["routing"],
            "user_id": user_context.user_id,
            "tenant_id": user_context.tenant_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "stages": [
                "business_outcome_identification",
                "data_requirements_analysis",
                "routing_decision",
                "journey_execution",
                "outcome_achievement"
            ],
            "current_stage": "routing_decision",
            "routing_metadata": routing_decision
        }
        
        return user_journey

    # ============================================================================
    # JOURNEY MANAGEMENT METHODS
    # ============================================================================

    async def get_routing_questions(self, business_outcome: str):
        """Get routing questions for a specific business outcome."""
        if business_outcome in self.business_outcome_routing:
            outcome_data = self.business_outcome_routing[business_outcome]
            questions = []
            
            for requirement in outcome_data["data_requirements"]:
                requirement_type = requirement["type"]
                if requirement_type in self.data_requirement_questions:
                    questions.extend(self.data_requirement_questions[requirement_type])
            
            return {
                "business_outcome": business_outcome,
                "questions": questions,
                "total_questions": len(questions)
            }
        else:
            return {
                "business_outcome": business_outcome,
                "questions": ["What data do you have available for this business outcome?"],
                "total_questions": 1
            }

    async def get_routing_recommendations(self, business_outcome: str):
        """Get routing recommendations for a specific business outcome."""
        if business_outcome in self.business_outcome_routing:
            outcome_data = self.business_outcome_routing[business_outcome]
            recommendations = []
            
            for requirement in outcome_data["data_requirements"]:
                routing = requirement["routing"]
                if routing in self.routing_recommendations:
                    recommendation = self.routing_recommendations[routing].copy()
                    recommendation["requirement_type"] = requirement["type"]
                    recommendations.append(recommendation)
            
            return {
                "business_outcome": business_outcome,
                "recommendations": recommendations,
                "total_recommendations": len(recommendations)
            }
        else:
            return {
                "business_outcome": business_outcome,
                "recommendations": [],
                "total_recommendations": 0
            }

    # ============================================================================
    # HEALTH AND CAPABILITIES
    # ============================================================================

    async def health_check(self):
        """Get health status of the MVP Journey Manager Service."""
        try:
            health_status = {
                "service_name": "MVPJourneyManagerService",
                "status": "healthy",
                "business_outcome_routing_count": len(self.business_outcome_routing),
                "data_requirement_questions_count": sum(len(questions) for questions in self.data_requirement_questions.values()),
                "routing_recommendations_count": len(self.routing_recommendations),
                "analysis_capabilities": self.analysis_capabilities,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "MVPJourneyManagerService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_capabilities(self):
        """Get capabilities of the MVP Journey Manager Service."""
        return {
            "service_name": "MVPJourneyManagerService",
            "capabilities": [
                "business_outcome_routing",
                "data_requirements_analysis",
                "intelligent_routing",
                "user_guidance",
                "journey_creation",
                "progressive_discovery",
                "routing_questions_generation"
            ],
            "supported_business_outcomes": list(self.business_outcome_routing.keys()),
            "routing_patterns": len(self.business_outcome_routing),
            "intelligent_routing_enabled": True
        }


# Create service instance factory function
def create_mvp_journey_manager_service(di_container: DIContainerService,
                                      public_works_foundation: PublicWorksFoundationService) -> MVPJourneyManagerService:
    """Factory function to create MVPJourneyManagerService with proper DI."""
    return MVPJourneyManagerService(
        di_container=di_container,
        public_works_foundation=public_works_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
mvp_journey_manager_service = None  # Will be set by foundation services during initialization
