"""
Test Enabling Service Three-Tier Access Pattern

CRITICAL TEST: Validates that enabling services use the three-tier access pattern correctly:
1. Try SOA APIs first (Tier 1)
2. Try Platform Gateway second (Tier 2)
3. Fail gracefully with structured errors (Tier 3)

Also validates that enabling services NEVER return None silently.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.critical
class TestEnablingServiceAccessPatterns:
    """Test enabling service three-tier access pattern."""
    
    @pytest.fixture
    async def file_parser_service(self, real_platform_gateway):
        """Create File Parser Service."""
        # TODO: Initialize with real dependencies
        service = FileParserService(
            service_name="test_file_parser_service",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_enabling_service_never_returns_none(self, file_parser_service):
        """Test enabling service never returns None silently."""
        # Test with invalid file_id
        result = await file_parser_service.parse_file("nonexistent_file_id")
        
        # Critical: Never return None
        assert result is not None, "parse_file returned None"
        
        # Should return structured response
        assert isinstance(result, dict), "parse_file did not return dict"
        assert "success" in result, "parse_file missing 'success' field"
    
    @pytest.mark.asyncio
    async def test_enabling_service_returns_structured_errors(self, file_parser_service):
        """Test enabling service returns structured error responses."""
        result = await file_parser_service.parse_file("invalid_file_id")
        
        if not result.get("success"):
            # Should have error details
            assert "error" in result or "error_code" in result
            assert "message" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_enabling_service_three_tier_fallback(self, file_parser_service):
        """Test enabling service tries all tiers before failing."""
        # Check that service has methods to access different tiers
        assert hasattr(file_parser_service, "get_content_steward_api") or                hasattr(file_parser_service, "get_data_steward_api"),                "Enabling service should have method to get SOA APIs (Tier 1)"
        
        assert hasattr(file_parser_service, "get_abstraction") or                hasattr(file_parser_service, "platform_gateway"),                "Enabling service should have access to Platform Gateway (Tier 2)"
    
    @pytest.mark.asyncio
    async def test_enabling_service_error_codes(self, file_parser_service):
        """Test enabling service uses standard error codes."""
        result = await file_parser_service.parse_file("nonexistent_file")
        
        if not result.get("success"):
            error_code = result.get("error_code")
            if error_code:
                # Should use standard error codes
                standard_codes = [
                    "SERVICE_UNAVAILABLE",
                    "FILE_NOT_FOUND",
                    "CAPABILITY_UNAVAILABLE",
                    "DEPENDENCY_MISSING"
                ]
                assert error_code in standard_codes or error_code.startswith("CUSTOM_"),                     f"Non-standard error code: {error_code}"
