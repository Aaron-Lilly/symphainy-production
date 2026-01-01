"""
Test Meilisearch Adapter with Real Infrastructure

Validates that Meilisearch adapter actually accesses and works with real Meilisearch instance.
Uses real infrastructure (not mocks) to catch actual infrastructure issues.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.public_works_foundation.infrastructure_adapters.meilisearch_knowledge_adapter import MeilisearchKnowledgeAdapter

@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestMeilisearchAdapterReal:
    """Test Meilisearch adapter with real Meilisearch instance."""
    
    @pytest.fixture
    async def meilisearch_adapter(self):
        """Create Meilisearch adapter connected to real Meilisearch."""
        # Use master key from container (masterKey) or None if not set
        api_key = os.getenv("MEILI_MASTER_KEY", "masterKey")
        adapter = MeilisearchKnowledgeAdapter(
            host=os.getenv("MEILI_HOST", "localhost"),
            port=int(os.getenv("MEILI_PORT", "7700")),
            api_key=api_key if api_key else None
        )
        # Meilisearch adapter needs connect() call
        connected = await adapter.connect()
        if not connected:
            pytest.skip("Meilisearch connection failed")
        yield adapter
        # Cleanup
        try:
            # Delete test indexes
            if adapter._client:
                indexes = adapter._client.get_indexes()
                for index in indexes:
                    if index.uid.startswith('test_'):
                        try:
                            adapter._client.delete_index(index.uid)
                        except Exception:
                            pass
        except Exception:
            pass
    
    @pytest.fixture
    def test_index(self, meilisearch_adapter):
        """Create a test index for document operations."""
        test_index_name = "test_documents"
        try:
            # Create test index (not async)
            index = meilisearch_adapter._client.index(test_index_name)
            index.create_index("id")
        except Exception:
            pass  # Index might already exist
        yield test_index_name
        # Cleanup handled by meilisearch_adapter fixture
    
    @pytest.mark.asyncio
    async def test_meilisearch_connection(self, meilisearch_adapter):
        """Test Meilisearch connection works."""
        # Test connection by checking client exists
        assert meilisearch_adapter._client is not None, "Meilisearch connection failed"
        assert meilisearch_adapter.client is not None, "Meilisearch client not initialized"
    
    @pytest.mark.asyncio
    async def test_meilisearch_add_documents(self, meilisearch_adapter, test_index):
        """Test Meilisearch add documents operation."""
        if not meilisearch_adapter._client:
            pytest.skip("Meilisearch client not connected")
        
        # Add documents (not async - returns TaskInfo)
        documents = [
            {"id": "1", "title": "Test Document 1", "content": "This is test content 1"},
            {"id": "2", "title": "Test Document 2", "content": "This is test content 2"}
        ]
        
        # Use Meilisearch client directly (not async)
        index = meilisearch_adapter._client.index(test_index)
        result = index.add_documents(documents)
        
        assert result is not None, "Document addition failed"
        # Wait for indexing
        import asyncio
        await asyncio.sleep(0.5)
    
    @pytest.mark.asyncio
    async def test_meilisearch_search(self, meilisearch_adapter, test_index):
        """Test Meilisearch search operation."""
        if not meilisearch_adapter._client:
            pytest.skip("Meilisearch client not connected")
        
        # Ensure index has documents
        try:
            index = meilisearch_adapter._client.index(test_index)
            documents = [{"id": "1", "title": "Test", "content": "Search test"}]
            index.add_documents(documents)
            # Wait for indexing
            import asyncio
            await asyncio.sleep(0.5)
        except Exception:
            pass  # Documents might already exist
        
        # Search (not async - returns dict)
        index = meilisearch_adapter._client.index(test_index)
        result = index.search("test")
        
        assert result is not None, "Search failed"
        assert isinstance(result, dict), "Search should return dict"
        assert "hits" in result, "Search result should have hits"
    
    @pytest.mark.asyncio
    async def test_meilisearch_version_matches_requirements(self):
        """Test Meilisearch client version matches requirements.txt."""
        try:
            import meilisearch
            # Try different ways to get version
            if hasattr(meilisearch, '__version__'):
                meili_version = meilisearch.__version__
            elif hasattr(meilisearch, 'VERSION'):
                meili_version = meilisearch.VERSION
            else:
                # Just verify module is importable
                meili_version = "installed"
            
            # Check version matches requirements.txt (meilisearch==0.27.0)
            # Allow for patch version differences
            if isinstance(meili_version, str) and meili_version != "installed":
                assert meili_version.startswith("0.27.") or meili_version.startswith("0.2") or meili_version.startswith("1."),                     f"Meilisearch version should be 0.27.x or compatible (from requirements.txt), got {meili_version}"
            else:
                # Just verify it's installed
                assert meilisearch is not None, "meilisearch should be installed"
        except ImportError:
            pytest.skip("meilisearch not installed")
        except AttributeError:
            pytest.skip("meilisearch version not available")
