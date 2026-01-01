#!/usr/bin/env python3
"""
MeilisearchKnowledgeAdapter Tests

Tests for MeilisearchKnowledgeAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestMeilisearchKnowledgeAdapter:
    """Test MeilisearchKnowledgeAdapter functionality."""
    
    @pytest.fixture
    def mock_meilisearch_client(self):
        """Mock Meilisearch client."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_index.create_index = AsyncMock(return_value=True)
        mock_index.add_documents = AsyncMock(return_value={"taskUid": "task_123"})
        mock_index.search = AsyncMock(return_value={"hits": [{"id": "doc_123"}]})
        mock_client.index.return_value = mock_index
        return mock_client, mock_index
    
    @pytest.fixture
    def adapter(self, mock_meilisearch_client):
        """Create MeilisearchKnowledgeAdapter instance."""
        mock_client, mock_index = mock_meilisearch_client
        with patch('foundations.public_works_foundation.infrastructure_adapters.meilisearch_knowledge_adapter.meilisearch.Client', return_value=mock_client):
            from foundations.public_works_foundation.infrastructure_adapters.meilisearch_knowledge_adapter import MeilisearchKnowledgeAdapter
            adapter = MeilisearchKnowledgeAdapter(
                host="localhost",
                port=7700
            )
            adapter.client = mock_client
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_meilisearch_client):
        """Test adapter initializes correctly."""
        mock_client, mock_index = mock_meilisearch_client
        with patch('foundations.public_works_foundation.infrastructure_adapters.meilisearch_knowledge_adapter.meilisearch.Client', return_value=mock_client):
            from foundations.public_works_foundation.infrastructure_adapters.meilisearch_knowledge_adapter import MeilisearchKnowledgeAdapter
            adapter = MeilisearchKnowledgeAdapter(
                host="localhost",
                port=7700
            )
            assert adapter.host == "localhost"
            assert adapter.port == 7700
            assert adapter.client is not None
    
    @pytest.mark.asyncio
    async def test_connect(self, adapter, mock_meilisearch_client):
        """Test adapter can connect."""
        mock_client, mock_index = mock_meilisearch_client
        result = await adapter.connect()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_create_index(self, adapter, mock_meilisearch_client):
        """Test adapter can create an index."""
        mock_client, mock_index = mock_meilisearch_client
        result = await adapter.create_index("test_index", "id")
        assert result is True
        mock_index.create_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search(self, adapter, mock_meilisearch_client):
        """Test adapter can search."""
        mock_client, mock_index = mock_meilisearch_client
        result = await adapter.search("test_index", "query")
        assert result is not None
        assert "hits" in result or isinstance(result, list)

