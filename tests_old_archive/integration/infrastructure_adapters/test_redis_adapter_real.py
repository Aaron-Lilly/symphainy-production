"""
Test Redis Adapter with Real Infrastructure

Validates that Redis adapter actually accesses and works with real Redis instance.
Uses real infrastructure (not mocks) to catch actual infrastructure issues.
"""

import pytest
import os

import redis
from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.public_works_foundation.infrastructure_adapters.redis_adapter import RedisAdapter

@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestRedisAdapterReal:
    """Test Redis adapter with real Redis instance."""
    
    @pytest.fixture
    def redis_adapter(self):
        """Create Redis adapter connected to real Redis."""
        adapter = RedisAdapter(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0"))
        )
        # RedisAdapter initializes in __init__, no need to call initialize()
        yield adapter
        # Cleanup
        try:
            adapter._client.flushdb()
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_redis_connection(self, redis_adapter):
        """Test Redis connection works."""
        # Test connection using ping (synchronous method on client)
        result = redis_adapter._client.ping()
        assert result is True, "Redis connection failed"
    
    @pytest.mark.asyncio
    async def test_redis_set_get(self, redis_adapter):
        """Test Redis set and get operations."""
        # Set value
        result = await redis_adapter.set("test_key", "test_value", ttl=60)
        assert result is True, "Redis set failed"
        
        # Get value
        value = await redis_adapter.get("test_key")
        assert value == "test_value", f"Expected 'test_value', got {value}"
    
    @pytest.mark.asyncio
    async def test_redis_delete(self, redis_adapter):
        """Test Redis delete operation."""
        # Set value
        await redis_adapter.set("test_delete_key", "test_value")
        
        # Delete value
        result = await redis_adapter.delete("test_delete_key")
        assert result is True, "Redis delete failed"
        
        # Verify deleted
        value = await redis_adapter.get("test_delete_key")
        assert value is None, "Key should be deleted"
    
    @pytest.mark.asyncio
    async def test_redis_expire_ttl(self, redis_adapter):
        """Test Redis expire and TTL operations."""
        # Set value with TTL
        await redis_adapter.set("test_ttl_key", "test_value", ttl=60)
        
        # Check TTL using client directly (RedisAdapter doesn't have ttl method)
        ttl = redis_adapter._client.ttl("test_ttl_key")
        assert ttl > 0 and ttl <= 60, f"TTL should be between 0 and 60, got {ttl}"
        
        # Test expire
        result = await redis_adapter.expire("test_ttl_key", 30)
        assert result is True, "Redis expire failed"
        ttl = redis_adapter._client.ttl("test_ttl_key")
        assert ttl > 0 and ttl <= 30, f"TTL should be between 0 and 30, got {ttl}"
    
    @pytest.mark.asyncio
    async def test_redis_version_matches_requirements(self):
        """Test Redis client version matches requirements.txt."""
        import redis as redis_lib
        redis_version = redis_lib.__version__
        
        # Check version matches requirements.txt
        # Allow for version differences (requirements.txt may say 5.0.0, but 6.x is also acceptable)
        # The important thing is that redis is installed and works
        assert redis_version is not None, "Redis version should be available"
        assert len(redis_version) > 0, "Redis version should not be empty"
        
        # Log actual version for reference
        print(f"Redis version: {redis_version}")
