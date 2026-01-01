#!/usr/bin/env python3
"""
GCSFileAdapter Tests

Tests for GCSFileAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestGCSFileAdapter:
    """Test GCSFileAdapter functionality."""
    
    @pytest.fixture
    def mock_gcs_client(self):
        """Mock GCS client."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.upload_from_string = MagicMock()
        mock_blob.download_as_bytes = MagicMock(return_value=b"test content")
        mock_blob.exists = MagicMock(return_value=True)
        mock_blob.delete = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        return mock_client, mock_bucket, mock_blob
    
    @pytest.fixture
    def adapter(self, mock_gcs_client):
        """Create GCSFileAdapter instance."""
        mock_client, mock_bucket, mock_blob = mock_gcs_client
        with patch('foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter.storage.Client', return_value=mock_client):
            from foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter import GCSFileAdapter
            adapter = GCSFileAdapter(
                project_id="test-project",
                bucket_name="test-bucket"
            )
            adapter.client = mock_client
            adapter.bucket = mock_bucket
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_gcs_client):
        """Test adapter initializes correctly."""
        mock_client, mock_bucket, mock_blob = mock_gcs_client
        with patch('foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter.storage.Client', return_value=mock_client):
            from foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter import GCSFileAdapter
            adapter = GCSFileAdapter(
                project_id="test-project",
                bucket_name="test-bucket"
            )
            assert adapter.project_id == "test-project"
            assert adapter.bucket_name == "test-bucket"
            assert adapter.client is not None
    
    @pytest.mark.asyncio
    async def test_upload_file(self, adapter, mock_gcs_client):
        """Test adapter can upload a file."""
        mock_client, mock_bucket, mock_blob = mock_gcs_client
        result = await adapter.upload_file(
            blob_name="test/file.pdf",
            file_data=b"test content",
            content_type="application/pdf"
        )
        assert result is True
        mock_blob.upload_from_string.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_download_file(self, adapter, mock_gcs_client):
        """Test adapter can download a file."""
        mock_client, mock_bucket, mock_blob = mock_gcs_client
        result = await adapter.download_file("test/file.pdf")
        assert result == b"test content"
        mock_blob.download_as_bytes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_file_exists(self, adapter, mock_gcs_client):
        """Test adapter can check if file exists."""
        mock_client, mock_bucket, mock_blob = mock_gcs_client
        result = await adapter.file_exists("test/file.pdf")
        assert result is True
        mock_blob.exists.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_file(self, adapter, mock_gcs_client):
        """Test adapter can delete a file."""
        mock_client, mock_bucket, mock_blob = mock_gcs_client
        result = await adapter.delete_file("test/file.pdf")
        assert result is True
        mock_blob.delete.assert_called_once()

