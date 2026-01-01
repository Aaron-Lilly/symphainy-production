#!/usr/bin/env python3
"""
ContentInsightsAbstraction Tests

Tests for ContentInsightsAbstraction in isolation.
Verifies abstraction works correctly and realms can access it via Platform Gateway.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestContentInsightsAbstraction:
    """Test ContentInsightsAbstraction functionality."""
    
    @pytest.fixture
    def mock_arango_adapter(self):
        """Mock ArangoDB adapter."""
        adapter = MagicMock()
        adapter.create_content_insight = AsyncMock(return_value={"_key": "insight_123"})
        adapter.get_content_insights = AsyncMock(return_value=[{"insight_id": "insight_123"}])
        return adapter
    
    @pytest.fixture
    def mock_config_adapter(self):
        """Mock config adapter."""
        return MagicMock()
    
    @pytest.fixture
    def abstraction(self, mock_arango_adapter, mock_config_adapter):
        """Create ContentInsightsAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.content_insights_abstraction import ContentInsightsAbstraction
        
        abstraction = ContentInsightsAbstraction(
            arango_adapter=mock_arango_adapter,
            config_adapter=mock_config_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_arango_adapter, mock_config_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.content_insights_abstraction import ContentInsightsAbstraction
        
        abstraction = ContentInsightsAbstraction(
            arango_adapter=mock_arango_adapter,
            config_adapter=mock_config_adapter
        )
        assert abstraction.arango_adapter == mock_arango_adapter
        assert abstraction.config_adapter == mock_config_adapter
    
    @pytest.mark.asyncio
    async def test_generate_content_insights(self, abstraction, mock_arango_adapter):
        """Test abstraction can generate content insights."""
        # Mock the internal helper method
        abstraction._generate_insights_from_content = AsyncMock(return_value={
            "confidence_score": 0.8,
            "insights": ["insight1", "insight2"]
        })
        
        result = await abstraction.generate_content_insights("content_123")
        assert result is not None
        assert "confidence_score" in result
        mock_arango_adapter.create_content_insight.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_content_patterns(self, abstraction, mock_arango_adapter):
        """Test abstraction can analyze content patterns."""
        # Mock the internal helper method
        abstraction._analyze_patterns_in_content = AsyncMock(return_value={
            "confidence_score": 0.7,
            "patterns": ["pattern1"]
        })
        
        result = await abstraction.analyze_content_patterns("content_123")
        assert result is not None
        assert "confidence_score" in result
        mock_arango_adapter.get_content_insights.assert_called_once()

