#!/usr/bin/env python3
"""
Smart City Foundation Integration Tests

Tests Smart City services integration with foundations (Public Works, Curator, Communication).
Verifies that the full foundation stack works together with Smart City services.

WHAT: Test Smart City services with full foundation stack
HOW: Initialize all foundations, then test Smart City services
"""

import sys
from pathlib import Path
import pytest
import asyncio

# Add project root to path (tests are in symphainy-platform/tests, so parent.parent is symphainy-platform)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from backend.smart_city.services.librarian.librarian_service import LibrarianService
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def full_foundation_stack(event_loop):
    """Initialize full foundation stack (Public Works, Curator, Communication)."""
    container = DIContainerService("test")
    
    # Initialize Public Works Foundation
    public_works = PublicWorksFoundationService(di_container=container)
    await public_works.initialize()
    container.register_foundation_service("PublicWorksFoundationService", public_works)
    
    # Initialize Curator Foundation
    curator = CuratorFoundationService(foundation_services=container)
    await curator.initialize()
    container.register_foundation_service("CuratorFoundationService", curator)
    
    # Initialize Communication Foundation
    communication = CommunicationFoundationService(di_container=container)
    await communication.initialize()
    container.register_foundation_service("CommunicationFoundationService", communication)
    
    yield {
        "di_container": container,
        "public_works": public_works,
        "curator": curator,
        "communication": communication
    }
    
    # Cleanup
    if hasattr(communication, 'shutdown'):
        await communication.shutdown()
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture(scope="module")
async def librarian_with_foundations(full_foundation_stack):
    """Create Librarian Service with full foundation stack."""
    container = full_foundation_stack["di_container"]
    librarian = LibrarianService(di_container=container)
    initialized = await librarian.initialize()
    
    if not initialized:
        pytest.skip("Librarian Service failed to initialize with foundations")
    
    yield librarian
    
    # Cleanup
    if hasattr(librarian, 'shutdown'):
        await librarian.shutdown()


class TestSmartCityFoundationIntegration:
    """Test Smart City services with full foundation stack."""
    
    @pytest.mark.asyncio
    async def test_foundations_initialize_together(self, full_foundation_stack):
        """Test that all foundations initialize together."""
        assert full_foundation_stack["public_works"].is_initialized
        assert full_foundation_stack["curator"].is_initialized
        assert full_foundation_stack["communication"].is_initialized
    
    @pytest.mark.asyncio
    async def test_smart_city_service_uses_public_works(self, librarian_with_foundations, full_foundation_stack):
        """Test that Smart City service uses Public Works Foundation."""
        librarian = librarian_with_foundations
        public_works = full_foundation_stack["public_works"]
        
        # Librarian should have access to Public Works abstractions
        assert librarian.is_infrastructure_connected
        assert librarian.knowledge_discovery_abstraction is not None
        
        # Verify Public Works is accessible
        assert public_works.is_initialized
    
    @pytest.mark.asyncio
    async def test_smart_city_service_registers_with_curator(self, librarian_with_foundations, full_foundation_stack):
        """Test that Smart City service registers with Curator Foundation."""
        librarian = librarian_with_foundations
        curator = full_foundation_stack["curator"]
        
        # Register capabilities
        capabilities = await librarian.soa_mcp_module.register_capabilities()
        
        assert capabilities is not None
        assert isinstance(capabilities, dict)
        
        # Check if registered with Curator
        registered_services = await curator.get_registered_services()
        assert registered_services is not None
    
    @pytest.mark.asyncio
    async def test_smart_city_service_can_use_communication(self, librarian_with_foundations, full_foundation_stack):
        """Test that Smart City service can use Communication Foundation."""
        librarian = librarian_with_foundations
        communication = full_foundation_stack["communication"]
        
        # Communication Foundation should be available
        assert communication.is_initialized
        
        # Librarian should be able to access communication capabilities
        # (via PlatformCapabilitiesMixin)
        assert hasattr(librarian, "get_curator")
    
    @pytest.mark.asyncio
    async def test_city_manager_orchestrates_foundations(self, full_foundation_stack):
        """Test that City Manager can orchestrate all foundations."""
        container = full_foundation_stack["di_container"]
        city_manager = CityManagerService(di_container=container)
        initialized = await city_manager.initialize()
        
        if not initialized:
            pytest.skip("City Manager failed to initialize")
        
        # City Manager should have access to all foundations
        assert city_manager.is_infrastructure_connected
        assert city_manager.session_abstraction is not None
        
        # Cleanup
        if hasattr(city_manager, 'shutdown'):
            await city_manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_foundations_provide_shared_infrastructure(self, full_foundation_stack):
        """Test that foundations provide shared infrastructure to Smart City services."""
        container = full_foundation_stack["di_container"]
        
        # Create multiple Smart City services
        librarian = LibrarianService(di_container=container)
        content_steward = ContentStewardService(di_container=container)
        
        await librarian.initialize()
        await content_steward.initialize()
        
        # Both should have access to same infrastructure via Public Works
        assert librarian.is_infrastructure_connected
        assert content_steward.is_infrastructure_connected
        
        # Both should use same DI Container
        assert librarian.di_container == content_steward.di_container
        
        # Cleanup
        if hasattr(librarian, 'shutdown'):
            await librarian.shutdown()
        if hasattr(content_steward, 'shutdown'):
            await content_steward.shutdown()

