#!/usr/bin/env python3
"""
SupabaseMetadataAdapter Tests

Tests for SupabaseMetadataAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestSupabaseMetadataAdapter:
    """Test SupabaseMetadataAdapter functionality."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "meta_123", "key": "value"}]
        mock_table.insert.return_value.execute.return_value = mock_result
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_result
        mock_table.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        mock_client.table.return_value = mock_table
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_supabase_client):
        """Create SupabaseMetadataAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.supabase_metadata_adapter.create_client', return_value=mock_supabase_client):
            from foundations.public_works_foundation.infrastructure_adapters.supabase_metadata_adapter import SupabaseMetadataAdapter
            adapter = SupabaseMetadataAdapter(
                url="https://test.supabase.co",
                anon_key="test_anon_key",
                service_key="test_service_key"
            )
            adapter.service_client = mock_supabase_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_supabase_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.supabase_metadata_adapter.create_client', return_value=mock_supabase_client):
            from foundations.public_works_foundation.infrastructure_adapters.supabase_metadata_adapter import SupabaseMetadataAdapter
            adapter = SupabaseMetadataAdapter(
                url="https://test.supabase.co",
                anon_key="test_anon_key"
            )
            assert adapter.url == "https://test.supabase.co"
            assert adapter.service_client is not None
    
    @pytest.mark.asyncio
    async def test_create_metadata(self, adapter, mock_supabase_client):
        """Test adapter can create metadata."""
        result = await adapter.create_metadata("metadata_table", {"key": "value"})
        assert result["id"] == "meta_123"
        mock_supabase_client.table.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_metadata(self, adapter, mock_supabase_client):
        """Test adapter can retrieve metadata."""
        result = await adapter.get_metadata("metadata_table", "meta_123")
        assert result is not None
        assert result["id"] == "meta_123"
    
    @pytest.mark.asyncio
    async def test_update_metadata(self, adapter, mock_supabase_client):
        """Test adapter can update metadata."""
        result = await adapter.update_metadata("metadata_table", "meta_123", {"key": "updated"})
        assert result["id"] == "meta_123"
    
    @pytest.mark.asyncio
    async def test_delete_metadata(self, adapter, mock_supabase_client):
        """Test adapter can delete metadata."""
        result = await adapter.delete_metadata("metadata_table", "meta_123")
        assert result is True

