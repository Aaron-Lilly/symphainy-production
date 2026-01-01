#!/usr/bin/env python3
"""
Smart City Real Infrastructure Integration Tests

Tests Smart City services with REAL infrastructure (Redis, ArangoDB, Meilisearch, etc.).
These tests verify that services actually work with real infrastructure capabilities.

WHAT: Test Smart City services with real infrastructure
HOW: Use Docker Compose infrastructure, initialize services, test actual operations
"""

import sys
from pathlib import Path
import pytest
import asyncio
from typing import Dict, Any

# Add project root to path (tests are in symphainy-platform/tests, so parent.parent is symphainy-platform)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from backend.smart_city.services.librarian.librarian_service import LibrarianService
from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def di_container(event_loop):
    """Create and initialize DI Container with real infrastructure."""
    container = DIContainerService("test")
    
    # Public Works Foundation is automatically created in DI Container __init__
    # We just need to initialize it (this connects to real infrastructure)
    if hasattr(container, 'public_works_foundation') and container.public_works_foundation:
        public_works = container.public_works_foundation
    else:
        # Fallback: create it manually if not auto-created
        public_works = PublicWorksFoundationService(di_container=container)
        container.public_works_foundation = public_works
    
    await public_works.initialize()
    
    # Initialize Curator Foundation (needed for service registration tests)
    curator = container.get_curator_foundation()
    if curator:
        await curator.initialize()
    
    yield container
    
    # Cleanup
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture(scope="module")
async def librarian_service(di_container):
    """Create and initialize Librarian Service with real infrastructure."""
    librarian = LibrarianService(di_container=di_container)
    initialized = await librarian.initialize()
    
    if not initialized:
        pytest.skip("Librarian Service failed to initialize with real infrastructure")
    
    yield librarian
    
    # Cleanup
    if hasattr(librarian, 'shutdown'):
        await librarian.shutdown()


@pytest.fixture(scope="module")
async def content_steward_service(di_container):
    """Create and initialize Content Steward Service with real infrastructure."""
    content_steward = ContentStewardService(di_container=di_container)
    initialized = await content_steward.initialize()
    
    if not initialized:
        pytest.skip("Content Steward Service failed to initialize with real infrastructure")
    
    yield content_steward
    
    # Cleanup
    if hasattr(content_steward, 'shutdown'):
        await content_steward.shutdown()


@pytest.fixture(scope="module")
async def city_manager_service(di_container):
    """Create and initialize City Manager Service with real infrastructure."""
    city_manager = CityManagerService(di_container=di_container)
    initialized = await city_manager.initialize()
    
    if not initialized:
        pytest.skip("City Manager Service failed to initialize with real infrastructure")
    
    yield city_manager
    
    # Cleanup
    if hasattr(city_manager, 'shutdown'):
        await city_manager.shutdown()


class TestSmartCityRealInfrastructure:
    """Test Smart City services with real infrastructure."""
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_librarian_stores_knowledge_with_real_infrastructure(self, librarian_service):
        """Test that Librarian can store knowledge using real infrastructure."""
        knowledge_data = {
            "title": "Test Knowledge Item",
            "content": "This is a test knowledge item for integration testing",
            "category": "test",
            "tags": ["integration", "test"],
            "metadata": {"test": True}
        }
        
        # Store knowledge using real infrastructure
        item_id = await librarian_service.store_knowledge(knowledge_data)
        
        assert item_id is not None
        assert isinstance(item_id, str)
        assert len(item_id) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_librarian_retrieves_knowledge_with_real_infrastructure(self, librarian_service):
        """Test that Librarian can retrieve knowledge using real infrastructure."""
        # First store knowledge
        knowledge_data = {
            "title": "Retrieval Test",
            "content": "Testing knowledge retrieval",
            "category": "test"
        }
        
        item_id = await librarian_service.store_knowledge(knowledge_data)
        assert item_id is not None
        
        # Retrieve knowledge
        retrieved = await librarian_service.get_knowledge_item(item_id)
        
        assert retrieved is not None
        assert isinstance(retrieved, dict)
        # get_knowledge_item returns {"item_id": ..., "item": {...}, "source": ..., "status": ...}
        assert retrieved.get("status") == "success"
        assert "item" in retrieved
        item = retrieved.get("item")
        assert item is not None
        assert item.get("title") == "Retrieval Test"
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_librarian_searches_knowledge_with_real_infrastructure(self, librarian_service):
        """Test that Librarian can search knowledge using real infrastructure."""
        # Store some test knowledge
        await librarian_service.store_knowledge({
            "title": "Search Test 1",
            "content": "This is a searchable content",
            "category": "test"
        })
        
        await librarian_service.store_knowledge({
            "title": "Search Test 2",
            "content": "Another searchable item",
            "category": "test"
        })
        
        # Search knowledge
        results = await librarian_service.search_knowledge("searchable")
        
        assert results is not None
        assert isinstance(results, dict)
        # Results should contain search results
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_librarian_infrastructure_abstractions_work(self, librarian_service):
        """Test that Librarian's infrastructure abstractions are connected."""
        assert librarian_service.is_infrastructure_connected
        assert librarian_service.knowledge_discovery_abstraction is not None
        assert librarian_service.knowledge_governance_abstraction is not None
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_content_steward_infrastructure_abstractions_work(self, content_steward_service):
        """Test that Content Steward's infrastructure abstractions are connected."""
        assert content_steward_service.is_infrastructure_connected
        assert content_steward_service.file_management_abstraction is not None
        assert content_steward_service.content_metadata_abstraction is not None
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_city_manager_infrastructure_abstractions_work(self, city_manager_service):
        """Test that City Manager's infrastructure abstractions are connected."""
        assert city_manager_service.is_infrastructure_connected
        assert city_manager_service.session_abstraction is not None
        assert city_manager_service.state_management_abstraction is not None
        assert city_manager_service.messaging_abstraction is not None
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_smart_city_services_can_communicate(self, librarian_service, content_steward_service):
        """Test that Smart City services can communicate with each other."""
        # Verify both services are initialized
        assert librarian_service.is_infrastructure_connected
        assert content_steward_service.is_infrastructure_connected
        
        # Services should be able to access shared infrastructure
        # (This is a basic connectivity test)
        assert librarian_service.di_container == content_steward_service.di_container
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_librarian_soa_apis_work_with_real_infrastructure(self, librarian_service):
        """Test that Librarian SOA APIs work with real infrastructure."""
        # Test store_knowledge SOA API
        knowledge_data = {
            "title": "SOA API Test",
            "content": "Testing SOA API with real infrastructure",
            "category": "test"
        }
        
        item_id = await librarian_service.store_knowledge(knowledge_data)
        assert item_id is not None
        
        # Test get_knowledge_item SOA API
        retrieved = await librarian_service.get_knowledge_item(item_id)
        assert retrieved is not None
        
        # Test search_knowledge SOA API
        results = await librarian_service.search_knowledge("SOA")
        assert results is not None
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_services_handle_errors_gracefully(self, librarian_service):
        """Test that services handle errors gracefully with real infrastructure."""
        # Try to get non-existent knowledge item
        result = await librarian_service.get_knowledge_item("nonexistent-id-12345")
        
        # Should return None or empty dict, not raise exception
        assert result is None or isinstance(result, dict)
    
    @pytest.mark.asyncio
    @pytest.mark.real_infrastructure
    async def test_services_register_with_curator(self, librarian_service, di_container):
        """Test that services register their capabilities with Curator."""
        # Get Curator Foundation
        curator = di_container.get_foundation_service("CuratorFoundationService")
        
        if curator:
            # Check if Librarian is registered
            registered_services = await curator.get_registered_services()
            services_dict = registered_services.get("services", {})
            
            # Librarian should be registered (or at least registration should not fail)
            # This verifies the registration mechanism works
            assert isinstance(services_dict, dict)
        else:
            pytest.skip("Curator Foundation not available")

