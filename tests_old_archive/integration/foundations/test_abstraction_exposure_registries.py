"""
Test Abstraction Exposure via Registries - Layer 2

Validates that abstractions are properly registered and exposed via registries.
Tests both direct registry access and Platform Gateway access patterns.
"""

import pytest
import os

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

@pytest.mark.integration
@pytest.mark.infrastructure
class TestAbstractionExposureViaRegistries:
    """Test abstractions are exposed via registries."""
    
    @pytest.fixture
    async def public_works_foundation(self):
        """Create and initialize Public Works Foundation."""
        from foundations.di_container.di_container_service import DIContainerService
        di_container = DIContainerService("smart_city")
        foundation = PublicWorksFoundationService(di_container=di_container)
        await foundation.initialize_foundation()
        yield foundation
        # Cleanup
        try:
            await foundation.shutdown()
        except Exception:
            pass
    
    def test_security_registry_initialized(self, public_works_foundation):
        """Test SecurityRegistry is initialized."""
        assert public_works_foundation.security_registry is not None, "SecurityRegistry should be initialized"
    
    def test_security_registry_exposes_auth(self, public_works_foundation):
        """Test SecurityRegistry exposes auth abstraction."""
        auth = public_works_foundation.security_registry.get_abstraction("auth")
        assert auth is not None, "SecurityRegistry should expose auth abstraction"
        assert auth == public_works_foundation.auth_abstraction, "Registry should return same instance"
    
    def test_security_registry_exposes_session(self, public_works_foundation):
        """Test SecurityRegistry exposes session abstraction."""
        session = public_works_foundation.security_registry.get_abstraction("session")
        assert session is not None, "SecurityRegistry should expose session abstraction"
        assert session == public_works_foundation.session_abstraction, "Registry should return same instance"
    
    def test_security_registry_exposes_authorization(self, public_works_foundation):
        """Test SecurityRegistry exposes authorization abstraction."""
        authz = public_works_foundation.security_registry.get_abstraction("authorization")
        assert authz is not None, "SecurityRegistry should expose authorization abstraction"
        assert authz == public_works_foundation.authorization_abstraction, "Registry should return same instance"
    
    def test_security_registry_exposes_tenant(self, public_works_foundation):
        """Test SecurityRegistry exposes tenant abstraction."""
        tenant = public_works_foundation.security_registry.get_abstraction("tenant")
        assert tenant is not None, "SecurityRegistry should expose tenant abstraction"
        assert tenant == public_works_foundation.tenant_abstraction, "Registry should return same instance"
    
    def test_file_management_registry_initialized(self, public_works_foundation):
        """Test FileManagementRegistry is initialized (REQUIRED)."""
        assert public_works_foundation.file_management_registry is not None, "FileManagementRegistry should be initialized (REQUIRED)"
    
    def test_file_management_registry_exposes_abstraction(self, public_works_foundation):
        """Test FileManagementRegistry exposes file_management abstraction."""
        file_mgmt = public_works_foundation.file_management_registry.get_abstraction("file_management")
        assert file_mgmt is not None, "FileManagementRegistry should expose file_management abstraction"
        assert file_mgmt == public_works_foundation.file_management_abstraction, "Registry should return same instance"
    
    def test_content_metadata_registry_initialized(self, public_works_foundation):
        """Test ContentMetadataRegistry is initialized."""
        assert public_works_foundation.content_metadata_registry is not None, "ContentMetadataRegistry should be initialized"
    
    def test_content_metadata_registry_exposes_abstractions(self, public_works_foundation):
        """Test ContentMetadataRegistry exposes all content abstractions."""
        content_metadata = public_works_foundation.content_metadata_registry.get_abstraction("content_metadata")
        assert content_metadata is not None, "ContentMetadataRegistry should expose content_metadata abstraction"
        assert content_metadata == public_works_foundation.content_metadata_abstraction, "Registry should return same instance"
        
        content_schema = public_works_foundation.content_metadata_registry.get_abstraction("content_schema")
        assert content_schema is not None, "ContentMetadataRegistry should expose content_schema abstraction"
        assert content_schema == public_works_foundation.content_schema_abstraction, "Registry should return same instance"
        
        content_insights = public_works_foundation.content_metadata_registry.get_abstraction("content_insights")
        assert content_insights is not None, "ContentMetadataRegistry should expose content_insights abstraction"
        assert content_insights == public_works_foundation.content_insights_abstraction, "Registry should return same instance"
    
    def test_service_discovery_registry_initialized(self, public_works_foundation):
        """Test ServiceDiscoveryRegistry is initialized."""
        assert public_works_foundation.service_discovery_registry is not None, "ServiceDiscoveryRegistry should be initialized"
    
    def test_service_discovery_registry_exposes_abstraction(self, public_works_foundation):
        """Test ServiceDiscoveryRegistry exposes service_discovery abstraction."""
        service_discovery = public_works_foundation.service_discovery_registry.get_service_discovery()
        assert service_discovery is not None, "ServiceDiscoveryRegistry should expose service_discovery abstraction"
        assert service_discovery == public_works_foundation.service_discovery_abstraction, "Registry should return same instance"
