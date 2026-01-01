#!/usr/bin/env python3
"""
TempoAdapter Tests

Tests for TempoAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestTempoAdapter:
    """Test TempoAdapter functionality."""
    
    @pytest.fixture
    def mock_tempo_client(self):
        """Mock Tempo client."""
        mock_client = MagicMock()
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_tempo_client):
        """Create TempoAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.tempo_adapter.TempoClient', return_value=mock_tempo_client):
            from foundations.public_works_foundation.infrastructure_adapters.tempo_adapter import TempoAdapter
            adapter = TempoAdapter(
                tempo_url="http://localhost:3200"
            )
            adapter.client = mock_tempo_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_tempo_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.tempo_adapter.TempoClient', return_value=mock_tempo_client):
            from foundations.public_works_foundation.infrastructure_adapters.tempo_adapter import TempoAdapter
            adapter = TempoAdapter(
                tempo_url="http://localhost:3200"
            )
            assert adapter.tempo_url == "http://localhost:3200"
    
    @pytest.mark.asyncio
    async def test_start_trace(self, adapter):
        """Test adapter can start a trace."""
        trace_id = await adapter.start_trace("test_trace", {})
        assert trace_id is not None
        assert isinstance(trace_id, str)
    
    @pytest.mark.asyncio
    async def test_add_span(self, adapter):
        """Test adapter can add a span."""
        span_id = await adapter.add_span("trace_123", "test_span", {})
        assert span_id is not None
        assert isinstance(span_id, str)
    
    @pytest.mark.asyncio
    async def test_end_span(self, adapter):
        """Test adapter can end a span."""
        result = await adapter.end_span("span_123", "success")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_end_trace(self, adapter):
        """Test adapter can end a trace."""
        result = await adapter.end_trace("trace_123", "success")
        assert result is True

