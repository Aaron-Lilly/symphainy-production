#!/usr/bin/env python3
"""
Business Outcome Analyzer Service - Analyzes business outcomes and determines required capabilities

This service analyzes business outcomes and determines what platform capabilities are needed
to achieve them.

WHAT (Journey/Solution Role): I analyze business outcomes and determine required capabilities
HOW (Service Implementation): I use AI and pattern matching to analyze user intent and map to outcomes
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
import re

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container import DIContainerService
from utilities import UserContext


class BusinessOutcomeAnalyzerService:
    """
    Business Outcome Analyzer Service - Analyzes business outcomes and determines required capabilities
    
    This service analyzes user input and business outcomes to determine what platform capabilities
    are needed to achieve the desired business outcome.
    """

    def __init__(self, di_container: DIContainerService):
        """Initialize Business Outcome Analyzer Service."""
        self.di_container = di_container
        
        # Business outcome patterns and keywords
        self.outcome_patterns = {
            "data_analysis": {
                "keywords": ["analyze", "data", "insights", "analytics", "report", "dashboard", "visualization"],
                "patterns": [
                    r"analyze.*data",
                    r"generate.*insights",
                    r"create.*report",
                    r"build.*dashboard",
                    r"visualize.*data"
                ],
                "capabilities": ["data_processing", "insights_generation", "visualization", "reporting"]
            },
            "process_optimization": {
                "keywords": ["optimize", "process", "workflow", "efficiency", "streamline", "improve"],
                "patterns": [
                    r"optimize.*process",
                    r"improve.*workflow",
                    r"streamline.*operations",
                    r"increase.*efficiency"
                ],
                "capabilities": ["workflow_analysis", "process_optimization", "automation", "efficiency_measurement"]
            },
            "strategic_planning": {
                "keywords": ["plan", "strategy", "roadmap", "goals", "objectives", "vision"],
                "patterns": [
                    r"create.*strategy",
                    r"develop.*roadmap",
                    r"plan.*goals",
                    r"strategic.*planning"
                ],
                "capabilities": ["roadmap_generation", "strategic_analysis", "planning", "goal_setting"]
            },
            "content_management": {
                "keywords": ["content", "document", "organize", "manage", "catalog", "library"],
                "patterns": [
                    r"manage.*content",
                    r"organize.*documents",
                    r"catalog.*information"
                ],
                "capabilities": ["content_processing", "document_management", "organization", "cataloging"]
            }
        }
        
        # Use case patterns
        self.use_case_patterns = {
            "mvp": {
                "keywords": ["mvp", "demo", "prototype", "basic", "simple"],
                "capabilities": ["basic_analysis", "simple_reporting", "standard_workflows"]
            },
            "autonomous_vehicle": {
                "keywords": ["vehicle", "autonomous", "testing", "safety", "simulation"],
                "capabilities": ["test_planning", "safety_analysis", "simulation", "coverage_analysis"]
            },
            "insurance_ai": {
                "keywords": ["insurance", "claims", "risk", "fraud", "underwriting"],
                "capabilities": ["fraud_detection", "risk_assessment", "claims_processing", "underwriting"]
            }
        }
        
        print(f"🔍 Business Outcome Analyzer Service initialized")

    async def initialize(self):
        """Initialize the Business Outcome Analyzer Service."""
        try:
            print("🔍 Initializing Business Outcome Analyzer Service...")
            
            # Initialize pattern matching
            await self._initialize_pattern_matching()
            
            # Initialize capability mapping
            await self._initialize_capability_mapping()
            
            print("✅ Business Outcome Analyzer Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Business Outcome Analyzer Service: {e}")
            raise

    async def _initialize_pattern_matching(self):
        """Initialize pattern matching for business outcomes."""
        # Compile regex patterns for better performance
        for outcome_id, outcome_data in self.outcome_patterns.items():
            compiled_patterns = []
            for pattern in outcome_data["patterns"]:
                compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            outcome_data["compiled_patterns"] = compiled_patterns
        
        print("✅ Pattern matching initialized")

    async def _initialize_capability_mapping(self):
        """Initialize capability mapping for different outcomes."""
        self.capability_mapping = {
            "data_processing": {
                "required_services": ["data_steward", "librarian"],
                "required_pillars": ["content_pillar", "insights_pillar"],
                "required_dimensions": ["smart_city", "business_enablement"]
            },
            "insights_generation": {
                "required_services": ["data_steward", "librarian"],
                "required_pillars": ["insights_pillar"],
                "required_dimensions": ["business_enablement"]
            },
            "visualization": {
                "required_services": ["librarian"],
                "required_pillars": ["insights_pillar"],
                "required_dimensions": ["business_enablement", "experience"]
            },
            "workflow_analysis": {
                "required_services": ["traffic_cop", "data_steward"],
                "required_pillars": ["operations_pillar"],
                "required_dimensions": ["smart_city", "business_enablement"]
            },
            "process_optimization": {
                "required_services": ["traffic_cop", "data_steward"],
                "required_pillars": ["operations_pillar"],
                "required_dimensions": ["business_enablement"]
            }
        }
        print("✅ Capability mapping initialized")

    # ============================================================================
    # BUSINESS OUTCOME ANALYSIS METHODS
    # ============================================================================

    async def analyze_business_outcome(self, business_outcome: str, use_case: str, user_context: UserContext):
        """
        Analyze a business outcome and determine required capabilities.
        """
        try:
            print(f"🔍 Analyzing business outcome: {business_outcome} for use case: {use_case}")
            
            # 1. Analyze business outcome requirements
            outcome_requirements = await self._analyze_outcome_requirements(business_outcome, use_case)
            
            # 2. Determine required capabilities
            required_capabilities = await self._determine_required_capabilities(outcome_requirements)
            
            # 3. Map capabilities to platform dimensions
            dimension_mapping = await self._map_capabilities_to_dimensions(required_capabilities)
            
            # 4. Create implementation plan
            implementation_plan = await self._create_implementation_plan(
                business_outcome, use_case, required_capabilities, dimension_mapping
            )
            
            return {
                "business_outcome": business_outcome,
                "use_case": use_case,
                "outcome_requirements": outcome_requirements,
                "required_capabilities": required_capabilities,
                "dimension_mapping": dimension_mapping,
                "implementation_plan": implementation_plan,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Business outcome analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "business_outcome": business_outcome,
                "use_case": use_case
            }

    async def analyze_user_input(self, user_input: str, user_context: UserContext):
        """
        Analyze user input to determine business outcome and use case.
        """
        try:
            print(f"🔍 Analyzing user input: {user_input}")
            
            # 1. Extract business outcome from user input
            business_outcome = await self._extract_business_outcome(user_input)
            
            # 2. Extract use case from user input
            use_case = await self._extract_use_case(user_input)
            
            # 3. Analyze requirements
            requirements = await self._analyze_requirements_from_input(user_input, business_outcome, use_case)
            
            return {
                "user_input": user_input,
                "business_outcome": business_outcome,
                "use_case": use_case,
                "requirements": requirements,
                "confidence_score": await self._calculate_confidence_score(user_input, business_outcome, use_case)
            }
            
        except Exception as e:
            print(f"❌ User input analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input
            }

    # ============================================================================
    # ANALYSIS HELPER METHODS
    # ============================================================================

    async def _analyze_outcome_requirements(self, business_outcome: str, use_case: str):
        """Analyze requirements for a specific business outcome."""
        requirements = {
            "outcome_type": business_outcome,
            "use_case": use_case,
            "complexity": "medium",
            "estimated_duration": "2-4 hours",
            "required_data_sources": [],
            "required_processing_steps": [],
            "expected_outputs": []
        }
        
        # Map business outcome to specific requirements
        if business_outcome in self.outcome_patterns:
            outcome_data = self.outcome_patterns[business_outcome]
            requirements["required_capabilities"] = outcome_data["capabilities"]
            requirements["keywords"] = outcome_data["keywords"]
        
        # Map use case to specific requirements
        if use_case in self.use_case_patterns:
            use_case_data = self.use_case_patterns[use_case]
            requirements["use_case_capabilities"] = use_case_data["capabilities"]
            requirements["use_case_keywords"] = use_case_data["keywords"]
        
        return requirements

    async def _determine_required_capabilities(self, outcome_requirements: Dict[str, Any]):
        """Determine required capabilities based on outcome requirements."""
        required_capabilities = []
        
        # Get capabilities from outcome requirements
        if "required_capabilities" in outcome_requirements:
            required_capabilities.extend(outcome_requirements["required_capabilities"])
        
        # Get capabilities from use case
        if "use_case_capabilities" in outcome_requirements:
            required_capabilities.extend(outcome_requirements["use_case_capabilities"])
        
        # Remove duplicates
        required_capabilities = list(set(required_capabilities))
        
        return required_capabilities

    async def _map_capabilities_to_dimensions(self, required_capabilities: List[str]):
        """Map required capabilities to platform dimensions."""
        dimension_mapping = {
            "smart_city": {
                "required_services": [],
                "required_capabilities": []
            },
            "business_enablement": {
                "required_pillars": [],
                "required_capabilities": []
            },
            "experience": {
                "required_services": [],
                "required_capabilities": []
            }
        }
        
        # Map each capability to dimensions
        for capability in required_capabilities:
            if capability in self.capability_mapping:
                capability_data = self.capability_mapping[capability]
                
                # Map to smart city services
                if "required_services" in capability_data:
                    for service in capability_data["required_services"]:
                        if service not in dimension_mapping["smart_city"]["required_services"]:
                            dimension_mapping["smart_city"]["required_services"].append(service)
                
                # Map to business enablement pillars
                if "required_pillars" in capability_data:
                    for pillar in capability_data["required_pillars"]:
                        if pillar not in dimension_mapping["business_enablement"]["required_pillars"]:
                            dimension_mapping["business_enablement"]["required_pillars"].append(pillar)
                
                # Map to experience services
                if "required_dimensions" in capability_data:
                    for dimension in capability_data["required_dimensions"]:
                        if dimension in dimension_mapping:
                            if capability not in dimension_mapping[dimension]["required_capabilities"]:
                                dimension_mapping[dimension]["required_capabilities"].append(capability)
        
        return dimension_mapping

    async def _create_implementation_plan(self, business_outcome: str, use_case: str, 
                                        required_capabilities: List[str], dimension_mapping: Dict[str, Any]):
        """Create implementation plan for the business outcome."""
        implementation_plan = {
            "business_outcome": business_outcome,
            "use_case": use_case,
            "required_capabilities": required_capabilities,
            "dimension_mapping": dimension_mapping,
            "implementation_steps": [
                {
                    "step": 1,
                    "name": "Initialize Journey",
                    "description": "Create business outcome journey and initialize cross-dimensional coordination",
                    "estimated_duration": "5-10 minutes"
                },
                {
                    "step": 2,
                    "name": "Smart City Coordination",
                    "description": "Coordinate Smart City services for data and infrastructure support",
                    "estimated_duration": "10-15 minutes"
                },
                {
                    "step": 3,
                    "name": "Business Enablement Execution",
                    "description": "Execute business enablement pillars for core functionality",
                    "estimated_duration": "30-60 minutes"
                },
                {
                    "step": 4,
                    "name": "Experience Orchestration",
                    "description": "Orchestrate user experience and frontend integration",
                    "estimated_duration": "15-30 minutes"
                },
                {
                    "step": 5,
                    "name": "Results Delivery",
                    "description": "Deliver business outcome results and insights",
                    "estimated_duration": "10-20 minutes"
                }
            ],
            "total_estimated_duration": "1-2 hours",
            "complexity": "medium"
        }
        
        return implementation_plan

    async def _extract_business_outcome(self, user_input: str):
        """Extract business outcome from user input."""
        user_input_lower = user_input.lower()
        
        # Check against outcome patterns
        for outcome_id, outcome_data in self.outcome_patterns.items():
            # Check keywords
            for keyword in outcome_data["keywords"]:
                if keyword in user_input_lower:
                    return outcome_id
            
            # Check patterns
            for pattern in outcome_data["compiled_patterns"]:
                if pattern.search(user_input):
                    return outcome_id
        
        # Default to data analysis if no specific pattern matches
        return "data_analysis"

    async def _extract_use_case(self, user_input: str):
        """Extract use case from user input."""
        user_input_lower = user_input.lower()
        
        # Check against use case patterns
        for use_case_id, use_case_data in self.use_case_patterns.items():
            for keyword in use_case_data["keywords"]:
                if keyword in user_input_lower:
                    return use_case_id
        
        # Default to MVP if no specific pattern matches
        return "mvp"

    async def _analyze_requirements_from_input(self, user_input: str, business_outcome: str, use_case: str):
        """Analyze requirements from user input."""
        requirements = {
            "user_input": user_input,
            "business_outcome": business_outcome,
            "use_case": use_case,
            "extracted_keywords": [],
            "confidence_indicators": []
        }
        
        # Extract keywords from user input
        words = user_input.lower().split()
        for word in words:
            if len(word) > 3:  # Only consider meaningful words
                requirements["extracted_keywords"].append(word)
        
        # Add confidence indicators
        if business_outcome in self.outcome_patterns:
            outcome_data = self.outcome_patterns[business_outcome]
            keyword_matches = sum(1 for keyword in outcome_data["keywords"] if keyword in user_input.lower())
            requirements["confidence_indicators"].append(f"Keyword matches: {keyword_matches}")
        
        return requirements

    async def _calculate_confidence_score(self, user_input: str, business_outcome: str, use_case: str):
        """Calculate confidence score for the analysis."""
        confidence_score = 0.5  # Base confidence
        
        # Increase confidence based on keyword matches
        if business_outcome in self.outcome_patterns:
            outcome_data = self.outcome_patterns[business_outcome]
            keyword_matches = sum(1 for keyword in outcome_data["keywords"] if keyword in user_input.lower())
            confidence_score += min(keyword_matches * 0.1, 0.3)
        
        # Increase confidence based on use case matches
        if use_case in self.use_case_patterns:
            use_case_data = self.use_case_patterns[use_case]
            keyword_matches = sum(1 for keyword in use_case_data["keywords"] if keyword in user_input.lower())
            confidence_score += min(keyword_matches * 0.1, 0.2)
        
        return min(confidence_score, 1.0)

    # ============================================================================
    # HEALTH AND CAPABILITIES
    # ============================================================================

    async def health_check(self):
        """Get health status of the Business Outcome Analyzer Service."""
        try:
            health_status = {
                "service_name": "BusinessOutcomeAnalyzerService",
                "status": "healthy",
                "outcome_patterns_count": len(self.outcome_patterns),
                "use_case_patterns_count": len(self.use_case_patterns),
                "capability_mapping_count": len(self.capability_mapping),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service_name": "BusinessOutcomeAnalyzerService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_capabilities(self):
        """Get capabilities of the Business Outcome Analyzer Service."""
        return {
            "service_name": "BusinessOutcomeAnalyzerService",
            "capabilities": [
                "business_outcome_analysis",
                "user_input_analysis",
                "capability_determination",
                "dimension_mapping",
                "implementation_planning",
                "pattern_matching",
                "confidence_scoring"
            ],
            "supported_outcomes": list(self.outcome_patterns.keys()),
            "supported_use_cases": list(self.use_case_patterns.keys()),
            "pattern_matching_enabled": True
        }


# Create service instance factory function
def create_business_outcome_analyzer_service(di_container: DIContainerService) -> BusinessOutcomeAnalyzerService:
    """Factory function to create BusinessOutcomeAnalyzerService with proper DI."""
    return BusinessOutcomeAnalyzerService(di_container)


# Create default service instance (will be properly initialized by foundation services)
business_outcome_analyzer_service = None  # Will be set by foundation services during initialization
