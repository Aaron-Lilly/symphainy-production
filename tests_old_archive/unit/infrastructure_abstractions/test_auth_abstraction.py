#!/usr/bin/env python3
"""
AuthAbstraction Tests

Tests for AuthAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestAuthAbstraction:
    """Test AuthAbstraction functionality."""
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter."""
        adapter = MagicMock()
        adapter.sign_in_with_password = AsyncMock(return_value={
            "success": True,
            "user": {"id": "user_123", "user_metadata": {"tenant_id": "tenant_123"}},
            "session": {"access_token": "token_123"}
        })
        return adapter
    
    @pytest.fixture
    def mock_jwt_adapter(self):
        """Mock JWT adapter."""
        adapter = MagicMock()
        adapter.validate_token = MagicMock(return_value={
            "valid": True,
            "payload": {"user_id": "user_123", "tenant_id": "tenant_123"}
        })
        return adapter
    
    @pytest.fixture
    def abstraction(self, mock_supabase_adapter, mock_jwt_adapter):
        """Create AuthAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.auth_abstraction import AuthAbstraction
        
        abstraction = AuthAbstraction(
            supabase_adapter=mock_supabase_adapter,
            jwt_adapter=mock_jwt_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_supabase_adapter, mock_jwt_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.auth_abstraction import AuthAbstraction
        
        abstraction = AuthAbstraction(
            supabase_adapter=mock_supabase_adapter,
            jwt_adapter=mock_jwt_adapter
        )
        assert abstraction.supabase == mock_supabase_adapter
        assert abstraction.jwt == mock_jwt_adapter
    
    @pytest.mark.asyncio
    async def test_authenticate_user(self, abstraction, mock_supabase_adapter):
        """Test abstraction can authenticate a user."""
        context = await abstraction.authenticate_user({
            "email": "test@example.com",
            "password": "password123"
        })
        
        assert context is not None
        assert context.user_id == "user_123"
        mock_supabase_adapter.sign_in_with_password.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_token(self, abstraction, mock_jwt_adapter):
        """Test abstraction can validate a token."""
        context = await abstraction.validate_token("test_token")
        
        assert context is not None
        assert context.user_id == "user_123"
        mock_jwt_adapter.validate_token.assert_called_once()

