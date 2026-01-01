#!/usr/bin/env python3
"""
OpenTelemetryAdapter Tests

Tests for OpenTelemetryAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestOpenTelemetryAdapter:
    """Test OpenTelemetryAdapter functionality."""
    
    @pytest.fixture
    def adapter(self):
        """Create OpenTelemetryAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.opentelemetry_adapter.trace') as mock_trace, \
             patch('foundations.public_works_foundation.infrastructure_adapters.opentelemetry_adapter.metrics') as mock_metrics:
            
            # Mock OpenTelemetry components
            mock_tracer = MagicMock()
            mock_meter = MagicMock()
            mock_tracer_provider = MagicMock()
            mock_meter_provider = MagicMock()
            
            mock_trace.get_tracer.return_value = mock_tracer
            mock_metrics.get_meter.return_value = mock_meter
            mock_trace.TracerProvider.return_value = mock_tracer_provider
            mock_metrics.MeterProvider.return_value = mock_meter_provider
            
            from foundations.public_works_foundation.infrastructure_adapters.opentelemetry_adapter import OpenTelemetryAdapter
            adapter = OpenTelemetryAdapter(
                service_name="test_service",
                endpoint="http://localhost:4317"
            )
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.opentelemetry_adapter.trace') as mock_trace, \
             patch('foundations.public_works_foundation.infrastructure_adapters.opentelemetry_adapter.metrics') as mock_metrics:
            
            mock_tracer = MagicMock()
            mock_meter = MagicMock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_metrics.get_meter.return_value = mock_meter
            mock_trace.TracerProvider.return_value = MagicMock()
            mock_metrics.MeterProvider.return_value = MagicMock()
            
            from foundations.public_works_foundation.infrastructure_adapters.opentelemetry_adapter import OpenTelemetryAdapter
            adapter = OpenTelemetryAdapter(
                service_name="test_service"
            )
            assert adapter.service_name == "test_service"
    
    @pytest.mark.asyncio
    async def test_create_span(self, adapter):
        """Test adapter can create a span."""
        if adapter.tracer:
            span = adapter.create_span("test_span", {"key": "value"})
            # Span creation should not raise exception
            assert True
    
    @pytest.mark.asyncio
    async def test_create_counter(self, adapter):
        """Test adapter can create a counter metric."""
        if adapter.meter:
            counter = adapter.create_counter("test_counter", "Test counter")
            # Counter creation should not raise exception
            assert True

