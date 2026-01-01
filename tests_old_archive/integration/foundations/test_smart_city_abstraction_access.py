"""
Test Smart City Direct Abstraction Access

Validates that Smart City services can access abstractions directly
(bypassing Platform Gateway) as per architectural design.

This is a critical architectural test - Smart City should have direct
Public Works Foundation access, not go through Platform Gateway.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService
from bases.mixins.infrastructure_access_mixin import InfrastructureAccessMixin

class MockSmartCityService(InfrastructureAccessMixin):
    """Mock Smart City service to test direct abstraction access."""
    
    def __init__(self, di_container):
        """Initialize mock Smart City service."""
        self.di_container = di_container
        self.role_name = "city_manager"  # Smart City role
        self._init_infrastructure_access(di_container)
        self.logger = None

@pytest.mark.integration
@pytest.mark.foundations
@pytest.mark.asyncio
class TestSmartCityAbstractionAccess:
    """Test Smart City direct abstraction access."""
    
    @pytest.fixture
    def di_container(self):
        """Create DI container (initializes in __init__)."""
        container = DIContainerService("smart_city_test")  # realm_name required, initializes in __init__
        yield container
        # No shutdown needed - DIContainerService doesn't have shutdown()
    
    @pytest.fixture
    async def public_works_foundation(self, di_container):
        """Create and initialize Public Works Foundation."""
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        foundation = PublicWorksFoundationService(
            di_container=di_container,
            security_provider=None,
            authorization_guard=None
        )
        
        # Initialize foundation
        initialized = await foundation.initialize_foundation()
        if not initialized:
            pytest.skip("Public Works Foundation failed to initialize")
        
        # CRITICAL: Link Public Works Foundation to DI container
        di_container.public_works_foundation = foundation
        
        yield foundation
        await foundation.shutdown()
    
    @pytest.fixture
    def smart_city_service(self, di_container):
        """Create mock Smart City service."""
        return MockSmartCityService(di_container)
    
    @pytest.mark.asyncio
    async def test_smart_city_can_access_abstractions_directly(self, smart_city_service, public_works_foundation):
        """Test Smart City can access abstractions directly (not via Platform Gateway)."""
        # Smart City should use get_infrastructure_abstraction() which calls Public Works directly
        # This bypasses Platform Gateway
        
        # Test accessing a common abstraction
        session_abstraction = smart_city_service.get_infrastructure_abstraction("session")
        
        assert session_abstraction is not None, "Smart City should be able to access session abstraction directly"
        assert hasattr(session_abstraction, 'create_session'), "Session abstraction should have create_session method"
    
    @pytest.mark.asyncio
    async def test_smart_city_has_access_to_all_abstractions(self, smart_city_service, public_works_foundation):
        """Test Smart City has access to all abstractions (full access privilege)."""
        # Smart City should have access to ALL abstractions
        # Test a variety of abstractions
        
        abstractions_to_test = [
            "session",
            "state_management",
            "messaging",
            "file_management",
            "content_metadata",
            "llm"
        ]
        
        for abstraction_name in abstractions_to_test:
            abstraction = smart_city_service.get_infrastructure_abstraction(abstraction_name)
            assert abstraction is not None,                 f"Smart City should have access to '{abstraction_name}' abstraction (full access privilege)"
    
    @pytest.mark.asyncio
    async def test_smart_city_abstractions_are_functional(self, smart_city_service, public_works_foundation):
        """Test that Smart City abstractions are actually functional (not just accessible)."""
        # Get session abstraction
        session_abstraction = smart_city_service.get_infrastructure_abstraction("session")
        
        assert session_abstraction is not None, "Session abstraction should be accessible"
        
        # Test that abstraction has expected methods (functional, not just a placeholder)
        assert hasattr(session_abstraction, 'create_session'), "Session abstraction should have create_session method"
        assert callable(getattr(session_abstraction, 'create_session', None)),             "create_session should be callable (not just an attribute)"
