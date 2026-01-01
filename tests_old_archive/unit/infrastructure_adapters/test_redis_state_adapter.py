#!/usr/bin/env python3
"""
RedisStateAdapter Tests

Tests for RedisStateAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestRedisStateAdapter:
    """Test RedisStateAdapter functionality."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        mock_client = MagicMock()
        mock_client.set = MagicMock(return_value=True)
        mock_client.get = MagicMock(return_value="test_value")
        mock_client.delete = MagicMock(return_value=1)
        mock_client.hset = MagicMock(return_value=1)
        mock_client.hget = MagicMock(return_value="hash_value")
        mock_client.hgetall = MagicMock(return_value={"field1": "value1"})
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_redis_client):
        """Create RedisStateAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.redis_state_adapter.redis.Redis', return_value=mock_redis_client):
            from foundations.public_works_foundation.infrastructure_adapters.redis_state_adapter import RedisStateAdapter
            adapter = RedisStateAdapter(
                host="localhost",
                port=6379,
                db=0
            )
            adapter.client = mock_redis_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_redis_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.redis_state_adapter.redis.Redis', return_value=mock_redis_client):
            from foundations.public_works_foundation.infrastructure_adapters.redis_state_adapter import RedisStateAdapter
            adapter = RedisStateAdapter(
                host="localhost",
                port=6379,
                db=0
            )
            assert adapter.client is not None
    
    @pytest.mark.asyncio
    async def test_set_string(self, adapter, mock_redis_client):
        """Test adapter can set a string value."""
        result = await adapter.set_string("test_key", "test_value")
        assert result is True
        mock_redis_client.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_string(self, adapter, mock_redis_client):
        """Test adapter can get a string value."""
        result = await adapter.get_string("test_key")
        assert result == "test_value"
        mock_redis_client.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_hash(self, adapter, mock_redis_client):
        """Test adapter can set a hash field."""
        result = await adapter.set_hash("test_hash", "field1", "value1")
        assert result is True
        mock_redis_client.hset.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_hash(self, adapter, mock_redis_client):
        """Test adapter can get a hash field."""
        result = await adapter.get_hash("test_hash", "field1")
        assert result == "hash_value"
        mock_redis_client.hget.assert_called_once()

