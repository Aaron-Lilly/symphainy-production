#!/usr/bin/env python3
"""
TelemetryAbstraction Tests

Tests for TelemetryAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestTelemetryAbstraction:
    """Test TelemetryAbstraction functionality."""
    
    @pytest.fixture
    def mock_telemetry_adapter(self):
        """Mock telemetry adapter."""
        adapter = MagicMock()
        adapter.collect_metric = AsyncMock(return_value=True)
        adapter.collect_trace = AsyncMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def abstraction(self, mock_telemetry_adapter):
        """Create TelemetryAbstraction instance."""
        with patch('foundations.public_works_foundation.infrastructure_abstractions.telemetry_abstraction.TelemetryAdapter', return_value=mock_telemetry_adapter):
            from foundations.public_works_foundation.infrastructure_abstractions.telemetry_abstraction import TelemetryAbstraction
            
            abstraction = TelemetryAbstraction(
                adapter_type="opentelemetry",
                service_name="test_service"
            )
            abstraction.adapter = mock_telemetry_adapter
            return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_telemetry_adapter):
        """Test abstraction initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_abstractions.telemetry_abstraction.TelemetryAdapter', return_value=mock_telemetry_adapter):
            from foundations.public_works_foundation.infrastructure_abstractions.telemetry_abstraction import TelemetryAbstraction
            
            abstraction = TelemetryAbstraction(
                adapter_type="opentelemetry",
                service_name="test_service"
            )
            assert abstraction.adapter_type == "opentelemetry"
            assert abstraction.adapter is not None
    
    @pytest.mark.asyncio
    async def test_collect_metric(self, abstraction, mock_telemetry_adapter):
        """Test abstraction can collect a metric."""
        from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TelemetryData, TelemetryType, MetricType
        
        telemetry_data = TelemetryData(
            name="test_metric",
            type=TelemetryType.METRIC,
            value=100.0,
            metadata={"unit": "count"},
            timestamp=datetime.utcnow()
        )
        
        result = await abstraction.collect_metric(telemetry_data)
        assert result is True
        mock_telemetry_adapter.collect_metric.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_trace(self, abstraction, mock_telemetry_adapter):
        """Test abstraction can collect a trace."""
        from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TraceSpan
        
        trace_data = TraceSpan(
            name="test_trace",
            span_id="span_123",
            trace_id="trace_123"
        )
        
        result = await abstraction.collect_trace(trace_data)
        assert result is True
        mock_telemetry_adapter.collect_trace.assert_called_once()

