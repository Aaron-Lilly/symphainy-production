#!/usr/bin/env python3
"""
FileManagementAbstraction Tests

Tests for FileManagementAbstraction (GCS) in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestFileManagementAbstraction:
    """Test FileManagementAbstraction functionality."""
    
    @pytest.fixture
    def mock_gcs_adapter(self):
        """Mock GCS adapter."""
        adapter = MagicMock()
        adapter.upload_file = AsyncMock(return_value=True)
        adapter.download_file = AsyncMock(return_value=b"test content")
        adapter.file_exists = AsyncMock(return_value=True)
        adapter.delete_file = AsyncMock(return_value=True)
        adapter.list_files = AsyncMock(return_value=[{"uuid": "file_123", "ui_name": "test.pdf"}])
        adapter.bucket_name = "test-bucket"
        return adapter
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter."""
        adapter = MagicMock()
        adapter.create_file = AsyncMock(return_value={"uuid": "file_123"})
        adapter.get_file = AsyncMock(return_value={"uuid": "file_123", "ui_name": "test.pdf", "service_context": {"gcs_blob_name": "files/file_123"}})
        adapter.update_file = AsyncMock(return_value={"uuid": "file_123"})
        adapter.delete_file = AsyncMock(return_value=True)
        adapter.list_files = AsyncMock(return_value=[{"uuid": "file_123", "ui_name": "test.pdf"}])
        return adapter
    
    @pytest.fixture
    def mock_config_adapter(self):
        """Mock config adapter."""
        return MagicMock()
    
    @pytest.fixture
    def abstraction(self, mock_gcs_adapter, mock_supabase_adapter, mock_config_adapter):
        """Create FileManagementAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction_gcs import FileManagementAbstraction
        
        abstraction = FileManagementAbstraction(
            gcs_adapter=mock_gcs_adapter,
            supabase_adapter=mock_supabase_adapter,
            config_adapter=mock_config_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_gcs_adapter, mock_supabase_adapter, mock_config_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction_gcs import FileManagementAbstraction
        
        abstraction = FileManagementAbstraction(
            gcs_adapter=mock_gcs_adapter,
            supabase_adapter=mock_supabase_adapter,
            config_adapter=mock_config_adapter
        )
        assert abstraction.gcs_adapter == mock_gcs_adapter
        assert abstraction.supabase_adapter == mock_supabase_adapter
    
    @pytest.mark.asyncio
    async def test_create_file(self, abstraction, mock_gcs_adapter, mock_supabase_adapter):
        """Test abstraction can create a file."""
        result = await abstraction.create_file({
            "user_id": "user_123",
            "ui_name": "test.pdf",
            "file_type": "application/pdf",
            "file_content": b"test content"
        })
        
        assert result is not None
        assert "uuid" in result or "file_id" in result
        mock_gcs_adapter.upload_file.assert_called_once()
        mock_supabase_adapter.create_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_file(self, abstraction, mock_gcs_adapter, mock_supabase_adapter):
        """Test abstraction can retrieve a file."""
        result = await abstraction.get_file("file_123")
        
        assert result is not None
        mock_supabase_adapter.get_file.assert_called_once()
        mock_gcs_adapter.download_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_files(self, abstraction, mock_supabase_adapter):
        """Test abstraction can list files."""
        result = await abstraction.list_files("user_123")
        
        assert isinstance(result, list) or isinstance(result, dict)
        # Should call Supabase to list metadata

