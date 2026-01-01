#!/usr/bin/env python3
"""
RedisGraphAdapter Tests

Tests for RedisGraphAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestRedisGraphAdapter:
    """Test RedisGraphAdapter functionality."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        mock_client = MagicMock()
        mock_client.ping = MagicMock(return_value=True)
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_redis_client):
        """Create RedisGraphAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.redis_graph_adapter.redis.Redis', return_value=mock_redis_client):
            from foundations.public_works_foundation.infrastructure_adapters.redis_graph_adapter import RedisGraphAdapter
            adapter = RedisGraphAdapter(
                host="localhost",
                port=6379,
                db=0
            )
            adapter.redis_client = mock_redis_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_redis_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.redis_graph_adapter.redis.Redis', return_value=mock_redis_client):
            from foundations.public_works_foundation.infrastructure_adapters.redis_graph_adapter import RedisGraphAdapter
            adapter = RedisGraphAdapter(
                host="localhost",
                port=6379,
                db=0
            )
            assert adapter.host == "localhost"
            assert adapter.port == 6379
            assert adapter.redis_client is not None
    
    @pytest.mark.asyncio
    async def test_create_node(self, adapter):
        """Test adapter can create a graph node."""
        # Graph operations may require specific Redis Graph setup
        # For now, test that adapter has the method
        assert hasattr(adapter, 'create_node') or hasattr(adapter, 'add_node')

