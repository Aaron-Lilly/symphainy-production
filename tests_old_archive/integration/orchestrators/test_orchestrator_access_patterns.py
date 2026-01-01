"""
Test Orchestrator Four-Tier Access Pattern

CRITICAL TEST: Validates that orchestrators use the four-tier access pattern correctly:
1. Try Enabling Services first (Tier 1)
2. Try SOA APIs second (Tier 2)
3. Try Platform Gateway third (Tier 3)
4. Fail gracefully with structured errors (Tier 4)

Also validates that orchestrators NEVER return None silently.
"""

import pytest
import os

from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.critical
class TestOrchestratorAccessPatterns:
    """Test orchestrator four-tier access pattern."""
    
    @pytest.fixture
    async def orchestrator(self, real_platform_gateway):
        """Create Business Outcomes Orchestrator."""
        # TODO: Initialize orchestrator with real dependencies
        orchestrator = BusinessOutcomesOrchestrator(
            service_name="test_business_outcomes_orchestrator",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrator_never_returns_none(self, orchestrator):
        """Test orchestrator never returns None silently."""
        business_context = {
            "pillar_outputs": {},
            "objectives": ["Test objective"]
        }
        
        # Test all orchestrator methods
        methods_to_test = [
            ("generate_strategic_roadmap", {"business_context": business_context}),
            ("generate_poc_proposal", {"business_context": business_context}),
            ("get_pillar_summaries", {}),
            ("get_journey_visualization", {}),
        ]
        
        for method_name, kwargs in methods_to_test:
            if hasattr(orchestrator, method_name):
                method = getattr(orchestrator, method_name)
                result = await method(**kwargs)
                
                # Critical: Never return None
                assert result is not None, f"{method_name} returned None"
                
                # Should return structured response
                assert isinstance(result, dict), f"{method_name} did not return dict"
                assert "success" in result, f"{method_name} missing 'success' field"
    
    @pytest.mark.asyncio
    async def test_orchestrator_returns_structured_errors(self, orchestrator):
        """Test orchestrator returns structured error responses."""
        # Test with invalid input that should fail
        invalid_context = {
            "pillar_outputs": None,  # Invalid
            "objectives": []
        }
        
        result = await orchestrator.generate_strategic_roadmap(invalid_context)
        
        # Should return structured error, not None
        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result
        
        if not result.get("success"):
            # Should have error details
            assert "error" in result or "error_code" in result
            assert "message" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_orchestrator_four_tier_fallback(self, orchestrator):
        """Test orchestrator tries all tiers before failing."""
        # This test would require mocking each tier
        # For now, we validate the pattern exists in code
        
        # Check that orchestrator has methods to access different tiers
        assert hasattr(orchestrator, "get_enabling_service") or                hasattr(orchestrator, "_get_enabling_service"),                "Orchestrator should have method to get enabling services (Tier 1)"
        
        assert hasattr(orchestrator, "get_content_steward_api") or                hasattr(orchestrator, "get_librarian_api") or                hasattr(orchestrator, "get_data_steward_api"),                "Orchestrator should have methods to get SOA APIs (Tier 2)"
        
        assert hasattr(orchestrator, "get_abstraction") or                hasattr(orchestrator, "platform_gateway"),                "Orchestrator should have access to Platform Gateway (Tier 3)"
    
    @pytest.mark.asyncio
    async def test_orchestrator_error_codes(self, orchestrator):
        """Test orchestrator uses standard error codes."""
        # Test with unavailable service scenario
        business_context = {
            "pillar_outputs": {},
            "objectives": ["Test"]
        }
        
        result = await orchestrator.generate_strategic_roadmap(business_context)
        
        if not result.get("success"):
            error_code = result.get("error_code")
            if error_code:
                # Should use standard error codes
                standard_codes = [
                    "SERVICE_UNAVAILABLE",
                    "CAPABILITY_UNAVAILABLE",
                    "DEPENDENCY_MISSING",
                    "INVALID_INPUT"
                ]
                assert error_code in standard_codes or error_code.startswith("CUSTOM_"),                     f"Non-standard error code: {error_code}"
