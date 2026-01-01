#!/usr/bin/env python3
"""
KnowledgeDiscoveryAbstraction Tests

Tests for KnowledgeDiscoveryAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestKnowledgeDiscoveryAbstraction:
    """Test KnowledgeDiscoveryAbstraction functionality."""
    
    @pytest.fixture
    def mock_meilisearch_adapter(self):
        """Mock Meilisearch adapter."""
        adapter = MagicMock()
        adapter.search = AsyncMock(return_value={"hits": [{"id": "doc_123"}]})
        adapter.create_index = AsyncMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def mock_redis_graph_adapter(self):
        """Mock Redis Graph adapter."""
        adapter = MagicMock()
        adapter.query_graph = AsyncMock(return_value={"results": []})
        return adapter
    
    @pytest.fixture
    def mock_arango_adapter(self):
        """Mock ArangoDB adapter."""
        adapter = MagicMock()
        adapter.get_document = AsyncMock(return_value={"_key": "doc_123"})
        return adapter
    
    @pytest.fixture
    def abstraction(self, mock_meilisearch_adapter, mock_redis_graph_adapter, mock_arango_adapter):
        """Create KnowledgeDiscoveryAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.knowledge_discovery_abstraction import KnowledgeDiscoveryAbstraction
        
        abstraction = KnowledgeDiscoveryAbstraction(
            meilisearch_adapter=mock_meilisearch_adapter,
            redis_graph_adapter=mock_redis_graph_adapter,
            arango_adapter=mock_arango_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_meilisearch_adapter, mock_redis_graph_adapter, mock_arango_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.knowledge_discovery_abstraction import KnowledgeDiscoveryAbstraction
        
        abstraction = KnowledgeDiscoveryAbstraction(
            meilisearch_adapter=mock_meilisearch_adapter,
            redis_graph_adapter=mock_redis_graph_adapter,
            arango_adapter=mock_arango_adapter
        )
        assert abstraction.meilisearch_adapter == mock_meilisearch_adapter
        assert abstraction.redis_graph_adapter == mock_redis_graph_adapter
        assert abstraction.arango_adapter == mock_arango_adapter
    
    @pytest.mark.asyncio
    async def test_search_knowledge(self, abstraction, mock_meilisearch_adapter):
        """Test abstraction can search knowledge."""
        from foundations.public_works_foundation.abstraction_contracts.knowledge_discovery_protocol import SearchMode, DiscoveryScope
        
        result = await abstraction.search_knowledge(
            query="test query",
            search_mode=SearchMode.HYBRID,
            scope=DiscoveryScope.GLOBAL
        )
        
        assert result is not None
        assert "hits" in result or "results" in result
        # Should use Meilisearch for primary search
        mock_meilisearch_adapter.search.assert_called()

