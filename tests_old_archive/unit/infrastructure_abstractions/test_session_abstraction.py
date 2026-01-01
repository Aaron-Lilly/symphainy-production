#!/usr/bin/env python3
"""
SessionAbstraction Tests

Tests for SessionAbstraction in isolation.
Verifies abstraction works correctly with dependency injection.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestSessionAbstraction:
    """Test SessionAbstraction functionality."""
    
    @pytest.fixture
    def mock_session_adapter(self):
        """Mock session adapter implementing SessionProtocol."""
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import Session, SessionContext, SessionStatus, SessionType
        
        adapter = AsyncMock()
        adapter.create_session = AsyncMock(return_value=Session(
            session_id="session_123",
            user_id="user_123",
            agent_id=None,
            session_type=SessionType.USER,
            status=SessionStatus.ACTIVE
        ))
        adapter.get_session = AsyncMock(return_value=Session(
            session_id="session_123",
            user_id="user_123",
            agent_id=None,
            session_type=SessionType.USER,
            status=SessionStatus.ACTIVE
        ))
        adapter.update_session = AsyncMock(return_value=True)
        adapter.delete_session = AsyncMock(return_value=True)
        adapter.validate_session = AsyncMock(return_value=True)
        adapter.refresh_session = AsyncMock(return_value=Session(
            session_id="session_123",
            user_id="user_123",
            status=SessionStatus.ACTIVE
        ))
        adapter.revoke_session = AsyncMock(return_value=True)
        adapter.list_sessions = AsyncMock(return_value=[])
        adapter.create_session_token = AsyncMock(return_value=MagicMock())
        adapter.validate_session_token = AsyncMock(return_value=Session(
            session_id="session_123",
            user_id="user_123",
            status=SessionStatus.ACTIVE
        ))
        adapter.revoke_session_token = AsyncMock(return_value=True)
        adapter.get_session_analytics = AsyncMock(return_value=MagicMock())
        adapter.update_session_analytics = AsyncMock(return_value=True)
        adapter.health_check = AsyncMock(return_value={"status": "healthy"})
        adapter.adapter_type = "redis"  # For logging
        return adapter
    
    @pytest.fixture
    def abstraction(self, mock_session_adapter):
        """Create SessionAbstraction instance with dependency injection."""
        from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction
        
        return SessionAbstraction(
            session_adapter=mock_session_adapter
        )
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_session_adapter):
        """Test abstraction initializes correctly with dependency injection."""
        from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction
        
        abstraction = SessionAbstraction(
            session_adapter=mock_session_adapter
        )
        assert abstraction.adapter == mock_session_adapter
        assert abstraction.adapter_type == "redis"
    
    @pytest.mark.asyncio
    async def test_requires_session_adapter(self):
        """Test abstraction requires session adapter via dependency injection."""
        from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction
        
        with pytest.raises(ValueError, match="requires session_adapter"):
            SessionAbstraction(session_adapter=None)
    
    @pytest.mark.asyncio
    async def test_create_session(self, abstraction, mock_session_adapter):
        """Test abstraction can create a session."""
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionContext
        
        context = SessionContext(
            service_id="service_123",
            agent_id=None,
            tenant_id="tenant_123"
        )
        
        session = await abstraction.create_session(context, {"user_id": "user_123"})
        assert session is not None
        assert session.session_id == "session_123"
        mock_session_adapter.create_session.assert_called_once()
