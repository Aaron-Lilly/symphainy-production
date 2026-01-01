#!/usr/bin/env python3
"""
CacheAbstraction Tests

Tests for CacheAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestCacheAbstraction:
    """Test CacheAbstraction functionality."""
    
    @pytest.fixture
    def mock_cache_adapter(self):
        """Mock cache adapter."""
        adapter = MagicMock()
        adapter.get = AsyncMock(return_value={"key": "value"})
        adapter.set = AsyncMock(return_value=True)
        adapter.delete = AsyncMock(return_value=True)
        adapter.storage_type = "redis"
        return adapter
    
    @pytest.fixture
    def mock_config_adapter(self):
        """Mock config adapter."""
        return MagicMock()
    
    @pytest.fixture
    def abstraction(self, mock_cache_adapter, mock_config_adapter):
        """Create CacheAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.cache_abstraction import CacheAbstraction
        
        abstraction = CacheAbstraction(
            cache_adapter=mock_cache_adapter,
            config_adapter=mock_config_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_cache_adapter, mock_config_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.cache_abstraction import CacheAbstraction
        
        abstraction = CacheAbstraction(
            cache_adapter=mock_cache_adapter,
            config_adapter=mock_config_adapter
        )
        assert abstraction.cache_adapter == mock_cache_adapter
        assert abstraction.config == mock_config_adapter
    
    @pytest.mark.asyncio
    async def test_get(self, abstraction, mock_cache_adapter):
        """Test abstraction can get from cache."""
        result = await abstraction.get("test_key")
        assert result is not None
        assert result["key"] == "value"
        mock_cache_adapter.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set(self, abstraction, mock_cache_adapter):
        """Test abstraction can set in cache."""
        result = await abstraction.set("test_key", {"key": "value"}, ttl=3600)
        assert result is True
        mock_cache_adapter.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete(self, abstraction, mock_cache_adapter):
        """Test abstraction can delete from cache."""
        result = await abstraction.delete("test_key")
        assert result is True
        mock_cache_adapter.delete.assert_called_once()

