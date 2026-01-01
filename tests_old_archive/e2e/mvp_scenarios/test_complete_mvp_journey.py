#!/usr/bin/env python3
"""
Sample E2E Test - Complete MVP Journey

This is a sample E2E test demonstrating the complete MVP journey.
"""

import pytest
from tests.utils.helpers.test_utilities import TestUtilities

class TestCompleteMVPJourney:
    """Test complete MVP journey from solution to business outcomes."""
    
    async def test_insurance_client_mvp_journey(self, 
                                               solution_orchestration_hub,
                                               journey_orchestration_hub,
                                               experience_manager,
                                               delivery_manager,
                                               insurance_client_data):
        """Test complete insurance client MVP journey."""
        # 1. Solution orchestration
        solution_context = TestUtilities.create_solution_context(
            "Create insurance MVP solution",
            "insurance_client"
        )
        
        solution_result = await solution_orchestration_hub.orchestrate_solution(solution_context)
        assert solution_result["success"] is True
        
        # 2. Journey orchestration
        journey_result = await journey_orchestration_hub.orchestrate_journey(solution_context)
        assert journey_result["success"] is True
        
        # 3. Experience orchestration
        experience_result = await experience_manager.orchestrate_mvp_experience(solution_context)
        assert experience_result["success"] is True
        
        # 4. Business Enablement orchestration
        business_result = await delivery_manager.orchestrate_mvp_business_enablement(solution_context)
        assert business_result["success"] is True
        
        # 5. Validate pillar flow
        assert "pillar_flow_result" in business_result
        assert business_result["pillar_flow_result"]["pillar_flow_completed"] is True
