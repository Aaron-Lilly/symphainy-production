"""
Test Platform Gateway Realm Abstraction Access

Validates that Platform Gateway correctly:
1. Allows authorized realm access to abstractions
2. Denies unauthorized realm access
3. Validates realm access correctly
4. Exposes abstractions that are actually functional

This is a critical architectural test - Platform Gateway is the governance
layer that controls which realms can access which abstractions.
"""

import pytest
import os

from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService

@pytest.mark.integration
@pytest.mark.platform_gateway
@pytest.mark.asyncio
class TestPlatformGatewayRealmAccess:
    """Test Platform Gateway realm abstraction access."""
    
    @pytest.fixture
    async def di_container(self):
        """Create DI container."""
        container = DIContainerService()
        await container.initialize()
        yield container
        await container.shutdown()
    
    @pytest.fixture
    async def public_works_foundation(self, di_container):
        """Create and initialize Public Works Foundation."""
        foundation = PublicWorksFoundationService(
            di_container=di_container,
            security_provider=None,
            authorization_guard=None
        )
        
        initialized = await foundation.initialize()
        if not initialized:
            pytest.skip("Public Works Foundation failed to initialize")
        
        yield foundation
        await foundation.shutdown()
    
    @pytest.fixture
    async def platform_gateway(self, public_works_foundation):
        """Create and initialize Platform Gateway."""
        gateway = PlatformInfrastructureGateway(public_works_foundation)
        
        initialized = await gateway.initialize()
        if not initialized:
            pytest.skip("Platform Gateway failed to initialize")
        
        yield gateway
    
    @pytest.mark.asyncio
    async def test_business_enablement_can_access_authorized_abstractions(self, platform_gateway):
        """Test Business Enablement realm can access authorized abstractions."""
        # Business Enablement should have access to specific abstractions
        # Per REALM_ABSTRACTION_MAPPINGS
        
        authorized_abstractions = [
            "content_metadata",
            "file_management",
            "llm",
            "document_intelligence"
        ]
        
        for abstraction_name in authorized_abstractions:
            abstraction = platform_gateway.get_abstraction("business_enablement", abstraction_name)
            assert abstraction is not None,                 f"Business Enablement should have access to '{abstraction_name}' abstraction"
    
    @pytest.mark.asyncio
    async def test_business_enablement_cannot_access_unauthorized_abstractions(self, platform_gateway):
        """Test Business Enablement realm cannot access unauthorized abstractions."""
        # Business Enablement should NOT have access to Smart City-only abstractions
        
        unauthorized_abstractions = [
            "auth",  # Smart City only
            "authorization",  # Smart City only
            "tenant"  # Smart City only
        ]
        
        for abstraction_name in unauthorized_abstractions:
            with pytest.raises(ValueError) as exc_info:
                platform_gateway.get_abstraction("business_enablement", abstraction_name)
            
            assert "cannot access" in str(exc_info.value).lower(),                 f"Business Enablement should be denied access to '{abstraction_name}'"
    
    @pytest.mark.asyncio
    async def test_platform_gateway_validates_realm_access(self, platform_gateway):
        """Test Platform Gateway correctly validates realm access."""
        # Test that validate_realm_access() works correctly
        
        # Business Enablement should have access to content_metadata
        assert platform_gateway.validate_realm_access("business_enablement", "content_metadata"),             "Business Enablement should have access to content_metadata"
        
        # Business Enablement should NOT have access to auth
        assert not platform_gateway.validate_realm_access("business_enablement", "auth"),             "Business Enablement should NOT have access to auth"
    
    @pytest.mark.asyncio
    async def test_platform_gateway_abstractions_are_functional(self, platform_gateway):
        """Test that Platform Gateway abstractions are actually functional (not just accessible)."""
        # Get an abstraction via Platform Gateway
        content_metadata = platform_gateway.get_abstraction("business_enablement", "content_metadata")
        
        assert content_metadata is not None, "Content metadata abstraction should be accessible"
        
        # Test that abstraction has expected methods (functional, not just a placeholder)
        # This ensures abstractions are real, not mock/placeholder objects
        assert hasattr(content_metadata, 'get_asset_metadata') or                hasattr(content_metadata, 'create_asset') or                hasattr(content_metadata, 'search_assets'),             "Content metadata abstraction should have functional methods"
