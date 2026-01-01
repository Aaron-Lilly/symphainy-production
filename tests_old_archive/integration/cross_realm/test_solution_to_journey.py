#!/usr/bin/env python3
"""
Sample Integration Test - Cross-Realm Communication

This is a sample integration test demonstrating cross-realm communication.
"""

import pytest
from solution.services.solution_orchestration_hub.solution_orchestration_hub_service import SolutionOrchestrationHubService
from journey_solution.services.journey_orchestration_hub.journey_orchestration_hub_service import JourneyOrchestrationHubService

class TestSolutionToJourneyCommunication:
    """Test solution to journey realm communication."""
    
    async def test_solution_context_propagation(self, solution_orchestration_hub, journey_orchestration_hub):
        """Test solution context propagation to journey realm."""
        solution_context = {
            "business_outcome": "Create insurance MVP solution",
            "solution_type": "mvp",
            "client_context": "insurance_client"
        }
        
        # Test solution orchestration
        solution_result = await solution_orchestration_hub.orchestrate_solution(solution_context)
        assert solution_result["success"] is True
        
        # Test journey orchestration with solution context
        journey_result = await journey_orchestration_hub.orchestrate_journey(solution_context)
        assert journey_result["success"] is True
        assert journey_result["client_context"] == "insurance_client"
