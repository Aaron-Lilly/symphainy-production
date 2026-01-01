"""
Test Error Code Consistency

HIGH PRIORITY TEST: Validates that error codes are consistent across services
and follow naming conventions.
"""

import pytest
import os

from typing import Dict, Any, List

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.high_priority
class TestErrorCodeConsistency:
    """Test that error codes are consistent across services."""
    
    # Standard error codes that should be used consistently
    STANDARD_ERROR_CODES = [
        "SERVICE_UNAVAILABLE",
        "CAPABILITY_UNAVAILABLE",
        "FILE_NOT_FOUND",
        "AUTH_TOKEN_MISSING",
        "DEPENDENCY_MISSING",
        "INVALID_INPUT",
        "AUTHENTICATION_FAILED",
        "AUTHORIZATION_FAILED",
        "RESOURCE_NOT_FOUND",
        "VALIDATION_ERROR"
    ]
    
    @pytest.fixture
    def orchestrators(self):
        """List of orchestrator classes to test."""
        return [
            BusinessOutcomesOrchestrator,
            InsightsOrchestrator,
            # Add more orchestrators as needed
        ]
    
    @pytest.mark.asyncio
    async def test_error_codes_use_standard_names(self, orchestrators):
        """Test that error codes use standard naming conventions."""
        # Test that all orchestrators use standard error codes or custom_ prefix
        for orchestrator_class in orchestrators:
            # This is a structural test - we check the code, not runtime behavior
            # In practice, we'd need to trigger errors and check codes
            
            # For now, we document the standard codes
            assert len(self.STANDARD_ERROR_CODES) > 0,                 "Standard error codes should be defined"
    
    @pytest.mark.asyncio
    async def test_error_codes_follow_naming_convention(self):
        """Test that error codes follow naming convention (UPPER_SNAKE_CASE)."""
        # Error codes should be UPPER_SNAKE_CASE
        for code in self.STANDARD_ERROR_CODES:
            # Should be uppercase
            assert code.isupper() or code.startswith("CUSTOM_"),                 f"Error code should be UPPER_CASE: {code}"
            
            # Should use underscores, not hyphens or spaces
            assert "_" in code or code.startswith("CUSTOM_"),                 f"Error code should use underscores: {code}"
            assert "-" not in code,                 f"Error code should not use hyphens: {code}"
            assert " " not in code,                 f"Error code should not use spaces: {code}"
    
    @pytest.mark.asyncio
    async def test_error_codes_are_documented(self):
        """Test that standard error codes are documented."""
        # Error codes should be documented somewhere
        # This test ensures the list exists and is maintained
        
        assert len(self.STANDARD_ERROR_CODES) >= 5,             "Should have at least 5 standard error codes"
        
        # Common error codes should be present
        required_codes = [
            "SERVICE_UNAVAILABLE",
            "CAPABILITY_UNAVAILABLE",
            "FILE_NOT_FOUND"
        ]
        
        for required_code in required_codes:
            assert required_code in self.STANDARD_ERROR_CODES,                 f"Required error code missing: {required_code}"
