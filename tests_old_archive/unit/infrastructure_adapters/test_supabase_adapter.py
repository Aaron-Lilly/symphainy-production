#!/usr/bin/env python3
"""
SupabaseAdapter Tests

Tests for SupabaseAdapter (auth/authz) in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestSupabaseAdapter:
    """Test SupabaseAdapter functionality."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client."""
        mock_client = MagicMock()
        mock_auth = MagicMock()
        mock_user = MagicMock()
        mock_session = MagicMock()
        mock_session.access_token = "test_token"
        mock_session.refresh_token = "refresh_token"
        mock_session.expires_in = 3600
        mock_session.expires_at = 1234567890
        mock_user.__dict__ = {"id": "user_123", "email": "test@example.com"}
        mock_session.__dict__ = {"access_token": "test_token"}
        
        mock_response = MagicMock()
        mock_response.user = mock_user
        mock_response.session = mock_session
        mock_auth.sign_in_with_password = MagicMock(return_value=mock_response)
        mock_auth.sign_up = MagicMock(return_value=mock_response)
        mock_auth.sign_out = MagicMock(return_value=None)
        mock_client.auth = mock_auth
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_supabase_client):
        """Create SupabaseAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.supabase_adapter.create_client', return_value=mock_supabase_client):
            from foundations.public_works_foundation.infrastructure_adapters.supabase_adapter import SupabaseAdapter
            adapter = SupabaseAdapter(
                url="https://test.supabase.co",
                anon_key="test_anon_key",
                service_key="test_service_key"
            )
            adapter.anon_client = mock_supabase_client
            adapter.service_client = mock_supabase_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_supabase_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.supabase_adapter.create_client', return_value=mock_supabase_client):
            from foundations.public_works_foundation.infrastructure_adapters.supabase_adapter import SupabaseAdapter
            adapter = SupabaseAdapter(
                url="https://test.supabase.co",
                anon_key="test_anon_key"
            )
            assert adapter.url == "https://test.supabase.co"
            assert adapter.anon_key == "test_anon_key"
            assert adapter.anon_client is not None
    
    @pytest.mark.asyncio
    async def test_sign_in_with_password(self, adapter, mock_supabase_client):
        """Test adapter can sign in with password."""
        result = await adapter.sign_in_with_password("test@example.com", "password123")
        assert result["success"] is True
        assert "access_token" in result
        mock_supabase_client.auth.sign_in_with_password.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sign_up_with_password(self, adapter, mock_supabase_client):
        """Test adapter can sign up with password."""
        result = await adapter.sign_up_with_password("test@example.com", "password123")
        assert result["success"] is True
        assert "access_token" in result
        mock_supabase_client.auth.sign_up.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sign_out(self, adapter, mock_supabase_client):
        """Test adapter can sign out."""
        result = await adapter.sign_out("test_token")
        assert result["success"] is True
        mock_supabase_client.auth.sign_out.assert_called_once()

