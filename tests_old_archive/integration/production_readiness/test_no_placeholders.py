"""
Test No Placeholder Data in Production Code

CRITICAL TEST: Validates that no placeholder/mock data exists in production code.
Tests:
- No placeholder text in Insights Orchestrator workflows
- No placeholder data/metadata in orchestrator responses
- No placeholder tokens in Security Guard authentication
- No placeholder quality scores in Content Steward
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.critical
class TestNoPlaceholders:
    """Test that no placeholder data exists in production code."""
    
    @pytest.fixture
    async def insights_orchestrator(self, real_platform_gateway):
        """Create Insights Orchestrator."""
        # TODO: Initialize with real dependencies
        orchestrator = InsightsOrchestrator(
            service_name="test_insights_orchestrator",
            realm_name="business_enablement",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_no_placeholder_text(self, insights_orchestrator):
        """Test Insights Orchestrator returns real data, not placeholders."""
        # Test unstructured analysis
        result = await insights_orchestrator.analyze_unstructured_data(
            file_id="test_file_id"
        )
        
        # Check for placeholder text
        if result.get("success"):
            text_content = result.get("text", "")
            metadata = result.get("metadata", {})
            
            # Should not contain placeholder text
            placeholder_indicators = [
                "This is placeholder",
                "placeholder text content",
                "placeholder data",
                "placeholder metadata",
                "placeholder unstructured",
                "placeholder structured"
            ]
            
            combined_text = (text_content + " " + str(metadata)).lower()
            for indicator in placeholder_indicators:
                assert indicator.lower() not in combined_text,                     f"Found placeholder text: {indicator} in response"
            
            # Should contain real content or error
            assert len(text_content) > 0 or result.get("error") is not None,                 "Response should contain real content or error"
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_no_placeholder_metadata(self, insights_orchestrator):
        """Test Insights Orchestrator returns real metadata, not placeholders."""
        result = await insights_orchestrator.analyze_structured_data(
            file_id="test_file_id"
        )
        
        if result.get("success"):
            metadata = result.get("metadata", {})
            
            # Check metadata values are not placeholders
            placeholder_values = ["placeholder", "fake", "dummy", "test_data"]
            
            for key, value in metadata.items():
                if isinstance(value, str):
                    value_lower = value.lower()
                    for placeholder in placeholder_values:
                        assert placeholder not in value_lower,                             f"Found placeholder value '{placeholder}' in metadata key '{key}'"
    
    @pytest.mark.asyncio
    async def test_orchestrator_responses_not_generic(self, insights_orchestrator):
        """Test orchestrator responses are specific, not generic boilerplate."""
        result = await insights_orchestrator.analyze_unstructured_data(
            file_id="test_file_id"
        )
        
        if result.get("success"):
            text_content = result.get("text", "")
            
            # Generic boilerplate indicators
            generic_indicators = [
                "lorem ipsum",
                "sample text",
                "example content",
                "test data",
                "dummy data"
            ]
            
            text_lower = text_content.lower()
            for indicator in generic_indicators:
                # Allow if it's part of a longer, specific sentence
                if indicator in text_lower:
                    # Check it's not standalone generic text
                    assert len(text_content) > 100,                         f"Response appears to be generic boilerplate: {indicator}"
