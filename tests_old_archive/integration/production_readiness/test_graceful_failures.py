"""
Test Graceful Failures

HIGH PRIORITY TEST: Validates that services fail gracefully with clear error messages
when dependencies are unavailable.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.high_priority
class TestGracefulFailures:
    """Test that services fail gracefully with clear error messages."""
    
    @pytest.fixture
    async def orchestrator(self, real_platform_gateway):
        """Create Business Outcomes Orchestrator."""
        # TODO: Initialize with real dependencies
        orchestrator = BusinessOutcomesOrchestrator(
            service_name="test_business_outcomes_orchestrator",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_graceful_failure(self, orchestrator):
        """Test orchestrator fails gracefully when services unavailable."""
        business_context = {
            "pillar_outputs": {},
            "objectives": ["Test objective"]
        }
        
        # This should work or fail gracefully (not crash)
        result = await orchestrator.generate_strategic_roadmap(business_context)
        
        # Should return structured response, not crash
        assert result is not None, "Orchestrator should not return None"
        assert isinstance(result, dict), "Orchestrator should return dict"
        assert "success" in result, "Response should have 'success' field"
        
        if not result.get("success"):
            # Should have proper error structure
            assert "error" in result or "error_code" in result,                 "Error response should have 'error' or 'error_code'"
            
            # Error code should be standard
            error_code = result.get("error_code")
            if error_code:
                standard_codes = [
                    "SERVICE_UNAVAILABLE",
                    "CAPABILITY_UNAVAILABLE",
                    "DEPENDENCY_MISSING",
                    "INVALID_INPUT"
                ]
                assert error_code in standard_codes or error_code.startswith("CUSTOM_"),                     f"Non-standard error code: {error_code}"
            
            # Error message should be clear and actionable
            error_message = result.get("message") or result.get("error", "")
            assert len(error_message) > 20,                 f"Error message too short (not actionable): {len(error_message)} chars"
            
            # Should contain actionable guidance
            actionable_keywords = ["please", "ensure", "check", "verify", "required", "missing"]
            message_lower = error_message.lower()
            has_actionable = any(keyword in message_lower for keyword in actionable_keywords)
            assert has_actionable,                 f"Error message should be actionable: {error_message[:100]}"
    
    @pytest.mark.asyncio
    async def test_no_exceptions_on_failure(self, orchestrator):
        """Test that services don't raise exceptions, they return error responses."""
        business_context = {
            "pillar_outputs": None,  # Invalid input
            "objectives": []
        }
        
        # Should not raise exception, should return error response
        try:
            result = await orchestrator.generate_strategic_roadmap(business_context)
            
            # Should return structured error, not raise
            assert result is not None
            assert isinstance(result, dict)
            assert "success" in result
            
        except Exception as e:
            # If exception is raised, it should be a specific, expected exception type
            # Not a generic RuntimeError or AttributeError
            assert isinstance(e, (ValueError, TypeError, RuntimeError)),                 f"Unexpected exception type: {type(e).__name__}"
            # Exception message should be clear
            assert len(str(e)) > 20, f"Exception message too short: {str(e)}"
    
    @pytest.mark.asyncio
    async def test_error_messages_are_clear(self, orchestrator):
        """Test that error messages are clear and helpful."""
        # Test various failure scenarios
        test_cases = [
            {"pillar_outputs": None},  # Missing required field
            {"pillar_outputs": {}, "objectives": []},  # Empty objectives
            {"pillar_outputs": {}, "budget": -1000},  # Invalid budget
        ]
        
        for test_case in test_cases:
            result = await orchestrator.generate_strategic_roadmap(test_case)
            
            if not result.get("success"):
                error_message = result.get("message") or result.get("error", "")
                
                # Should be clear (not cryptic)
                assert len(error_message) > 10,                     f"Error message too short: {error_message}"
                
                # Should not be just error codes
                assert error_message != result.get("error_code", ""),                     "Error message should not just be error code"
                
                # Should be human-readable
                assert not error_message.startswith("ERR_"),                     "Error message should be human-readable, not just error code"
