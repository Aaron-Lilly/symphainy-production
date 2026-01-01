#!/usr/bin/env python3
"""
ArangoDBAdapter Tests

Tests for ArangoDBAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestArangoDBAdapter:
    """Test ArangoDBAdapter functionality."""
    
    @pytest.fixture
    def mock_arango_client(self):
        """Mock ArangoDB client."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.insert = MagicMock(return_value={"_key": "doc_123", "_id": "collection/doc_123"})
        mock_collection.get = MagicMock(return_value={"_key": "doc_123", "data": "test"})
        mock_collection.update = MagicMock(return_value={"_key": "doc_123"})
        mock_collection.delete = MagicMock(return_value=True)
        mock_db.collection.return_value = mock_collection
        mock_client.db.return_value = mock_db
        return mock_client, mock_db, mock_collection
    
    @pytest.fixture
    def adapter(self, mock_arango_client):
        """Create ArangoDBAdapter instance."""
        mock_client, mock_db, mock_collection = mock_arango_client
        with patch('foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter.ArangoClient', return_value=mock_client):
            from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter
            adapter = ArangoDBAdapter(
                hosts="http://localhost:8529",
                database="test_db",
                username="test_user",
                password="test_pass"
            )
            adapter.client = mock_client
            adapter.db = mock_db
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_arango_client):
        """Test adapter initializes correctly."""
        mock_client, mock_db, mock_collection = mock_arango_client
        with patch('foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter.ArangoClient', return_value=mock_client):
            from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter
            adapter = ArangoDBAdapter(
                hosts="http://localhost:8529",
                database="test_db",
                username="test_user",
                password="test_pass"
            )
            assert adapter.database == "test_db"
            assert adapter.db is not None
    
    @pytest.mark.asyncio
    async def test_create_document(self, adapter, mock_arango_client):
        """Test adapter can create a document."""
        mock_client, mock_db, mock_collection = mock_arango_client
        result = await adapter.create_document("test_collection", {"key": "value"})
        assert result["_key"] == "doc_123"
        mock_collection.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_document(self, adapter, mock_arango_client):
        """Test adapter can retrieve a document."""
        mock_client, mock_db, mock_collection = mock_arango_client
        result = await adapter.get_document("test_collection", "doc_123")
        assert result is not None
        assert result["_key"] == "doc_123"
        mock_collection.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_document(self, adapter, mock_arango_client):
        """Test adapter can update a document."""
        mock_client, mock_db, mock_collection = mock_arango_client
        result = await adapter.update_document("test_collection", "doc_123", {"key": "updated"})
        assert result["_key"] == "doc_123"
        mock_collection.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_document(self, adapter, mock_arango_client):
        """Test adapter can delete a document."""
        mock_client, mock_db, mock_collection = mock_arango_client
        result = await adapter.delete_document("test_collection", "doc_123")
        assert result is True
        mock_collection.delete.assert_called_once()

