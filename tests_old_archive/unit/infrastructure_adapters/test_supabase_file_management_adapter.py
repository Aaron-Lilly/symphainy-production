#!/usr/bin/env python3
"""
SupabaseFileManagementAdapter Tests

Tests for SupabaseFileManagementAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestSupabaseFileManagementAdapter:
    """Test SupabaseFileManagementAdapter functionality."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        return mock_client
    
    @pytest.fixture
    def adapter(self, mock_supabase_client):
        """Create SupabaseFileManagementAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter.create_client', return_value=mock_supabase_client):
            from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
            adapter = SupabaseFileManagementAdapter(
                url="https://test.supabase.co",
                service_key="test_key"
            )
            adapter.client = mock_supabase_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_supabase_client):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter.create_client', return_value=mock_supabase_client):
            from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
            adapter = SupabaseFileManagementAdapter(
                url="https://test.supabase.co",
                service_key="test_key"
            )
            assert adapter.url == "https://test.supabase.co"
            assert adapter.service_key == "test_key"
            assert adapter.client is not None
    
    @pytest.mark.asyncio
    async def test_adapter_connects(self, adapter, mock_supabase_client):
        """Test adapter can connect."""
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"uuid": "test-uuid"}]
        mock_table.select.return_value.limit.return_value.execute.return_value = mock_result
        mock_supabase_client.table.return_value = mock_table
        
        result = await adapter.connect()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_create_file(self, adapter, mock_supabase_client):
        """Test adapter can create a file."""
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"uuid": "test-uuid", "filename": "test.pdf"}]
        mock_table.insert.return_value.execute.return_value = mock_result
        mock_supabase_client.table.return_value = mock_table
        
        file_data = {"filename": "test.pdf", "user_id": "user_123"}
        result = await adapter.create_file(file_data)
        
        assert result["uuid"] == "test-uuid"
        assert result["filename"] == "test.pdf"
        mock_table.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_file(self, adapter, mock_supabase_client):
        """Test adapter can retrieve a file."""
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"uuid": "test-uuid", "filename": "test.pdf"}]
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase_client.table.return_value = mock_table
        
        result = await adapter.get_file("test-uuid")
        
        assert result is not None
        assert result["uuid"] == "test-uuid"
        assert result["filename"] == "test.pdf"
    
    @pytest.mark.asyncio
    async def test_update_file(self, adapter, mock_supabase_client):
        """Test adapter can update a file."""
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"uuid": "test-uuid", "filename": "updated.pdf"}]
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase_client.table.return_value = mock_table
        
        updates = {"filename": "updated.pdf"}
        result = await adapter.update_file("test-uuid", updates)
        
        assert result["uuid"] == "test-uuid"
        assert result["filename"] == "updated.pdf"
        mock_table.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_file(self, adapter, mock_supabase_client):
        """Test adapter can delete a file (soft delete)."""
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"uuid": "test-uuid", "deleted": True}]
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase_client.table.return_value = mock_table
        
        result = await adapter.delete_file("test-uuid")
        
        assert result is True
        mock_table.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_files(self, adapter, mock_supabase_client):
        """Test adapter can list files."""
        mock_table = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [
            {"uuid": "file1", "filename": "test1.pdf"},
            {"uuid": "file2", "filename": "test2.pdf"}
        ]
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase_client.table.return_value = mock_table
        
        result = await adapter.list_files("user_123")
        
        assert len(result) == 2
        assert result[0]["uuid"] == "file1"
        assert result[1]["uuid"] == "file2"

