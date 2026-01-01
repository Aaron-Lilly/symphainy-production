#!/usr/bin/env python3
"""
RedisAdapter Tests

Tests for RedisAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestRedisAdapter:
    """Test RedisAdapter functionality."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client."""
        mock_client = MagicMock()
        mock_client.set = MagicMock(return_value=True)
        mock_client.setex = MagicMock(return_value=True)
        mock_client.get = MagicMock(return_value="test_value")
        mock_client.delete = MagicMock(return_value=1)
        mock_client.exists = MagicMock(return_value=1)
        mock_client.expire = MagicMock(return_value=True)
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_redis_client):
        """Create RedisAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.redis_adapter.redis.Redis', return_value=mock_redis_client):
            from foundations.public_works_foundation.infrastructure_adapters.redis_adapter import RedisAdapter
            adapter = RedisAdapter(
                host="localhost",
                port=6379,
                db=0
            )
            adapter.client = mock_redis_client
            adapter.redis_client = mock_redis_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_redis_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.redis_adapter.redis.Redis', return_value=mock_redis_client):
            from foundations.public_works_foundation.infrastructure_adapters.redis_adapter import RedisAdapter
            adapter = RedisAdapter(
                host="localhost",
                port=6379,
                db=0
            )
            assert adapter.host == "localhost"
            assert adapter.port == 6379
            assert adapter.db == 0
            assert adapter.client is not None
    
    @pytest.mark.asyncio
    async def test_set_operation(self, adapter, mock_redis_client):
        """Test adapter can set a value."""
        result = await adapter.set("test_key", "test_value")
        assert result is True
        mock_redis_client.set.assert_called_once_with("test_key", "test_value")
    
    @pytest.mark.asyncio
    async def test_set_with_ttl(self, adapter, mock_redis_client):
        """Test adapter can set a value with TTL."""
        result = await adapter.set("test_key", "test_value", ttl=3600)
        assert result is True
        mock_redis_client.setex.assert_called_once_with("test_key", 3600, "test_value")
    
    @pytest.mark.asyncio
    async def test_get_operation(self, adapter, mock_redis_client):
        """Test adapter can get a value."""
        result = await adapter.get("test_key")
        assert result == "test_value"
        mock_redis_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_delete_operation(self, adapter, mock_redis_client):
        """Test adapter can delete a key."""
        result = await adapter.delete("test_key")
        assert result is True
        mock_redis_client.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_exists_operation(self, adapter, mock_redis_client):
        """Test adapter can check if key exists."""
        result = await adapter.exists("test_key")
        assert result is True
        mock_redis_client.exists.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_expire_operation(self, adapter, mock_redis_client):
        """Test adapter can set expiration."""
        result = await adapter.expire("test_key", 3600)
        assert result is True
        mock_redis_client.expire.assert_called_once_with("test_key", 3600)

