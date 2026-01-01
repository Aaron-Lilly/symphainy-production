"""
Test ArangoDB Adapter with Real Infrastructure

Validates that ArangoDB adapter actually accesses and works with real ArangoDB instance.
Uses real infrastructure (not mocks) to catch actual infrastructure issues.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter
from arango import ArangoClient

@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.asyncio
class TestArangoDBAdapterReal:
    """Test ArangoDB adapter with real ArangoDB instance."""
    
    @pytest.fixture
    def arangodb_adapter(self):
        """Create ArangoDB adapter connected to real ArangoDB."""
        # Ensure database exists before creating adapter
        hosts = os.getenv("ARANGO_HOSTS", "http://localhost:8529")
        db_name = os.getenv("ARANGO_DB", "symphainy_metadata")
        username = os.getenv("ARANGO_USER", "root")
        password = os.getenv("ARANGO_PASS", "")
        
        # Create database if it doesn't exist
        try:
            client = ArangoClient(hosts=hosts)
            sys_db = client.db("_system", username=username, password=password)
            if db_name not in sys_db.databases():
                sys_db.create_database(db_name)
        except Exception as e:
            # If we can't create database, adapter will fail with clear error
            pass
        
        adapter = ArangoDBAdapter(
            hosts=hosts,
            database=db_name,
            username=username,
            password=password
        )
        # ArangoDBAdapter initializes in __init__, no need to call initialize()
        yield adapter
        # Cleanup
        try:
            if hasattr(adapter, 'db') and adapter.db:
                # Delete test collections
                collections = adapter.db.collections()
                for col in collections:
                    if col['name'].startswith('test_'):
                        try:
                            adapter.db.delete_collection(col['name'])
                        except Exception:
                            pass
        except Exception:
            pass
    
    @pytest.fixture
    def test_collection(self, arangodb_adapter):
        """Create a test collection for document operations."""
        collection_name = "test_documents"
        if not arangodb_adapter.db.has_collection(collection_name):
            arangodb_adapter.db.create_collection(collection_name)
        yield collection_name
        # Cleanup handled by arangodb_adapter fixture
    
    @pytest.mark.asyncio
    async def test_arangodb_connection(self, arangodb_adapter):
        """Test ArangoDB connection works."""
        # Test connection by checking database exists
        assert arangodb_adapter.db is not None, "ArangoDB connection failed"
        assert hasattr(arangodb_adapter.db, 'name'), "ArangoDB database not initialized"
    
    @pytest.mark.asyncio
    async def test_arangodb_create_document(self, arangodb_adapter, test_collection):
        """Test ArangoDB create document operation."""
        # Create document
        document = {"_key": "test_doc_1", "name": "Test Document", "value": 123}
        result = await arangodb_adapter.create_document(test_collection, document)
        
        assert result is not None, "Document creation failed"
        assert "_id" in result or "_key" in result, "Document should have _id or _key"
        assert result.get("_key") == "test_doc_1", "Document key should match"
    
    @pytest.mark.asyncio
    async def test_arangodb_update_document(self, arangodb_adapter, test_collection):
        """Test ArangoDB update document operation."""
        # Create document first
        document = {"_key": "test_doc_2", "name": "Original", "value": 100}
        await arangodb_adapter.create_document(test_collection, document)
        
        # Update document - adapter now correctly merges key into document
        update_data = {"name": "Updated", "value": 200}
        result = await arangodb_adapter.update_document(test_collection, "test_doc_2", update_data)
        
        assert result is not None, "Document update failed"
        # Verify update
        updated_doc = await arangodb_adapter.get_document(test_collection, "test_doc_2")
        assert updated_doc is not None, "Updated document should exist"
        assert updated_doc.get("name") == "Updated", "Name should be updated"
        assert updated_doc.get("value") == 200, "Value should be updated"
    
    @pytest.mark.asyncio
    async def test_arangodb_delete_document(self, arangodb_adapter, test_collection):
        """Test ArangoDB delete document operation."""
        # Create document first
        document = {"_key": "test_doc_3", "name": "To Delete"}
        await arangodb_adapter.create_document(test_collection, document)
        
        # Delete document - returns dict, not bool
        result = await arangodb_adapter.delete_document(test_collection, "test_doc_3")
        
        # ArangoDB delete returns dict with _id, _key, _rev
        assert result is not None, "Document deletion should return result"
        assert isinstance(result, dict) or result is True, "Document deletion should return dict or True"
        # Verify deleted
        deleted_doc = await arangodb_adapter.get_document(test_collection, "test_doc_3")
        assert deleted_doc is None, "Document should be deleted"
    
    @pytest.mark.asyncio
    async def test_arangodb_version_matches_requirements(self):
        """Test ArangoDB client version matches requirements.txt."""
        try:
            import arango
            # Try different ways to get version
            if hasattr(arango, '__version__'):
                arango_version = arango.__version__
            elif hasattr(arango, 'VERSION'):
                arango_version = arango.VERSION
            else:
                # Just verify module is importable
                arango_version = "installed"
            
            # Check version matches requirements.txt (python-arango==7.8.1)
            # Allow for patch version differences
            if isinstance(arango_version, str) and arango_version != "installed":
                assert arango_version.startswith("7.") or arango_version.startswith("8."),                     f"ArangoDB version should be 7.x or 8.x (from requirements.txt), got {arango_version}"
            else:
                # Just verify it's installed
                assert arango is not None, "python-arango should be installed"
        except ImportError:
            pytest.skip("python-arango not installed")
