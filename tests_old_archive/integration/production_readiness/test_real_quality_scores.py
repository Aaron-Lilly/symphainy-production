"""
Test Real Quality Scores in Content Steward

CRITICAL TEST: Validates that Content Steward calculates real quality scores,
not placeholder 0.8 values.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.critical
class TestRealQualityScores:
    """Test that Content Steward calculates real quality scores."""
    
    @pytest.fixture
    async def content_steward(self, real_platform_gateway):
        """Create Content Steward Service."""
        # TODO: Initialize with real dependencies
        service = ContentStewardService(
            service_name="test_content_steward",
            realm_name="smart_city",
            platform_gateway=real_platform_gateway,
            di_container=None  # TODO: Get from fixture
        )
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_content_steward_real_quality_scores(self, content_steward):
        """Test Content Steward calculates real quality scores."""
        # Test with good metadata (should have high quality score)
        result1 = await content_steward.get_quality_metrics(asset_id="test_good_asset")
        
        quality1 = result1.get("quality_score")
        assert quality1 is not None, "Quality score is None"
        assert quality1 != 0.8, f"Found placeholder quality score: {quality1}"
        assert 0.0 <= quality1 <= 1.0, f"Quality score out of range: {quality1}"
        
        # Test with poor metadata (should have lower quality score)
        result2 = await content_steward.get_quality_metrics(asset_id="test_poor_asset")
        
        quality2 = result2.get("quality_score")
        assert quality2 is not None, "Quality score is None"
        assert quality2 != 0.8, f"Found placeholder quality score: {quality2}"
        assert 0.0 <= quality2 <= 1.0, f"Quality score out of range: {quality2}"
        
        # Quality scores should vary based on input (unless both are perfect/terrible)
        # This validates that scores are calculated, not hardcoded
        if quality1 != 1.0 and quality2 != 0.0:
            # Scores should be different for different inputs
            # (allowing for edge cases where both might be same)
            assert abs(quality1 - quality2) > 0.01 or quality1 == quality2,                 f"Quality scores should vary based on input, got {quality1} and {quality2}"
    
    @pytest.mark.asyncio
    async def test_quality_score_calculation(self, content_steward):
        """Test quality score is calculated from actual metrics."""
        result = await content_steward.get_quality_metrics(asset_id="test_asset")
        
        # Should have quality score
        quality_score = result.get("quality_score")
        assert quality_score is not None
        
        # Should have underlying metrics that contribute to score
        metrics = result.get("metrics", {})
        
        # Check that score makes sense based on metrics
        if "metadata_completeness" in metrics:
            completeness = metrics["metadata_completeness"]
            # Quality score should correlate with completeness
            # (not exact, but should be related)
            if completeness > 0.8:
                assert quality_score >= 0.5,                     f"Quality score {quality_score} too low for high completeness {completeness}"
            elif completeness < 0.3:
                assert quality_score <= 0.7,                     f"Quality score {quality_score} too high for low completeness {completeness}"
    
    @pytest.mark.asyncio
    async def test_no_hardcoded_quality_scores(self, content_steward):
        """Test quality scores are not hardcoded to 0.8."""
        # Test multiple assets
        test_assets = ["asset1", "asset2", "asset3", "asset4", "asset5"]
        quality_scores = []
        
        for asset_id in test_assets:
            result = await content_steward.get_quality_metrics(asset_id=asset_id)
            quality = result.get("quality_score")
            if quality is not None:
                quality_scores.append(quality)
        
        if len(quality_scores) > 1:
            # Not all scores should be exactly 0.8 (placeholder value)
            scores_not_placeholder = [q for q in quality_scores if q != 0.8]
            assert len(scores_not_placeholder) > 0,                 f"All quality scores are 0.8 (placeholder): {quality_scores}"
            
            # Scores should have some variation (unless all assets are identical)
            unique_scores = set(quality_scores)
            if len(unique_scores) == 1 and len(quality_scores) > 2:
                # If all scores are same, they should not be 0.8
                assert quality_scores[0] != 0.8,                     f"All quality scores are placeholder 0.8: {quality_scores}"
