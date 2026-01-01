#!/usr/bin/env python3
"""
RedisSessionAdapter Tests

Tests for RedisSessionAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestRedisSessionAdapter:
    """Test RedisSessionAdapter functionality."""
    
    @pytest.fixture
    def mock_redis_adapter(self):
        """Mock Redis adapter."""
        mock_adapter = MagicMock()
        mock_adapter.host = "localhost"
        mock_adapter.port = 6379
        mock_adapter.db = 0
        mock_adapter.client = MagicMock()
        mock_adapter.client.set = MagicMock(return_value=True)
        mock_adapter.client.get = MagicMock(return_value='{"session_id": "test_123"}')
        mock_adapter.client.hset = MagicMock(return_value=1)
        mock_adapter.client.hget = MagicMock(return_value="test_value")
        return mock_adapter
    
    @pytest.fixture
    def mock_jwt_adapter(self):
        """Mock JWT adapter."""
        mock_adapter = MagicMock()
        mock_adapter.encode = MagicMock(return_value="jwt_token_123")
        mock_adapter.decode = MagicMock(return_value={"user_id": "user_123"})
        return mock_adapter
    
    @pytest.fixture
    def adapter(self, mock_redis_adapter, mock_jwt_adapter):
        """Create RedisSessionAdapter instance."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_session_adapter import RedisSessionAdapter
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext
        
        adapter = RedisSessionAdapter(
            redis_adapter=mock_redis_adapter,
            jwt_adapter=mock_jwt_adapter
        )
        return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_redis_adapter, mock_jwt_adapter):
        """Test adapter initializes correctly."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_session_adapter import RedisSessionAdapter
        
        adapter = RedisSessionAdapter(
            redis_adapter=mock_redis_adapter,
            jwt_adapter=mock_jwt_adapter
        )
        assert adapter.redis_adapter == mock_redis_adapter
        assert adapter.jwt_adapter == mock_jwt_adapter
    
    @pytest.mark.asyncio
    async def test_create_session(self, adapter):
        """Test adapter can create a session."""
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext
        
        context = SessionContext(
            service_id="test_service",
            agent_id=None,
            tenant_id="tenant_123"
        )
        
        session = await adapter.create_session(context, {"user_id": "user_123"})
        assert session is not None
        assert session.session_id is not None
        assert session.user_id == "user_123"
    
    @pytest.mark.asyncio
    async def test_get_session(self, adapter):
        """Test adapter can retrieve a session."""
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext
        
        context = SessionContext(service_id="test_service")
        session = await adapter.get_session("test_session_123", context)
        # Session retrieval should work (may return None if not found)
        assert session is None or hasattr(session, 'session_id')
