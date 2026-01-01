#!/usr/bin/env python3
"""
RedisEventBusAdapter Tests

Tests for RedisEventBusAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestRedisEventBusAdapter:
    """Test RedisEventBusAdapter functionality."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock async Redis client."""
        mock_client = MagicMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_client.xadd = AsyncMock(return_value="1234567890-0")
        mock_client.xread = AsyncMock(return_value=[])
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_redis_client):
        """Create RedisEventBusAdapter instance."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_event_bus_adapter import RedisEventBusAdapter
        
        adapter = RedisEventBusAdapter(
            redis_client=mock_redis_client,
            service_name="test_service"
        )
        return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_redis_client):
        """Test adapter initializes correctly."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_event_bus_adapter import RedisEventBusAdapter
        
        adapter = RedisEventBusAdapter(
            redis_client=mock_redis_client,
            service_name="test_service"
        )
        assert adapter.redis_client == mock_redis_client
        assert adapter.service_name == "test_service"
    
    @pytest.mark.asyncio
    async def test_connect(self, adapter, mock_redis_client):
        """Test adapter can connect."""
        result = await adapter.connect()
        assert result is True
        assert adapter.is_connected is True
        mock_redis_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_publish_event(self, adapter, mock_redis_client):
        """Test adapter can publish an event."""
        from foundations.public_works_foundation.abstraction_contracts.event_management_protocol import EventPriority
        
        event_context = await adapter.publish_event(
            event_type="test_event",
            source="test_source",
            target="test_target",
            event_data={"key": "value"},
            priority=EventPriority.NORMAL
        )
        
        assert event_context is not None
        assert event_context.event_type == "test_event"

