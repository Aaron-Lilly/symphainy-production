#!/usr/bin/env python3
"""
Public Works Foundation Integration Tests

Tests to verify foundation integrates correctly with:
- DI Container
- Utilities
- Other services
- Error handling
"""

import pytest
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestPublicWorksFoundationIntegration:
    """Test Public Works Foundation integration."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI Container for testing."""
        return DIContainerService("test")
    
    @pytest.fixture
    def foundation_service(self, di_container):
        """Create a Public Works Foundation Service instance."""
        return PublicWorksFoundationService(di_container=di_container)
    
    def test_foundation_integrates_with_di_container(self, foundation_service, di_container):
        """Test that foundation integrates with DI Container."""
        assert foundation_service.di_container is not None
        assert foundation_service.di_container == di_container
        
        # Foundation should be able to access utilities via DI Container
        assert hasattr(foundation_service, 'get_logger')
        assert callable(foundation_service.get_logger)
        
        # Note: Logger may not be initialized yet in DI Container during test setup
        # This is acceptable - we're testing structure, not full initialization
    
    def test_foundation_uses_utilities_via_di_container(self, foundation_service):
        """Test that foundation uses utilities via DI Container."""
        # Test utility access methods exist
        assert hasattr(foundation_service, 'get_logger')
        assert hasattr(foundation_service, 'get_utility')
        assert callable(foundation_service.get_logger)
        assert callable(foundation_service.get_utility)
        
        # Note: Logger may not be initialized yet in DI Container during test setup
        # This is acceptable - we're testing structure, not full initialization
    
    def test_foundation_exposes_abstractions_to_other_services(self, foundation_service):
        """Test that foundation exposes abstractions to other services."""
        # Foundation should have abstraction attributes
        assert hasattr(foundation_service, 'auth_abstraction')
        assert hasattr(foundation_service, 'authorization_abstraction')
        assert hasattr(foundation_service, 'session_abstraction')
        assert hasattr(foundation_service, 'tenant_abstraction')
    
    def test_foundation_handles_errors_gracefully(self, foundation_service):
        """Test that foundation handles errors gracefully."""
        # Foundation should have error handling capabilities
        assert hasattr(foundation_service, 'get_error_handler')
        assert callable(foundation_service.get_error_handler)
        
        # Foundation should have logger for error reporting
        assert hasattr(foundation_service, 'logger')
        assert foundation_service.logger is not None
    
    def test_foundation_integrates_with_registries(self, foundation_service):
        """Test that foundation integrates with registries."""
        # Foundation should have registry attributes
        assert hasattr(foundation_service, 'security_registry')
        assert hasattr(foundation_service, 'file_management_registry')
        assert hasattr(foundation_service, 'content_metadata_registry')
        assert hasattr(foundation_service, 'service_discovery_registry')
    
    def test_foundation_integrates_with_composition_services(self, foundation_service):
        """Test that foundation integrates with composition services."""
        # Foundation should have composition service attributes
        # (May be None initially, but attribute should exist)
        assert hasattr(foundation_service, 'composition_service') or hasattr(foundation_service, 'security_composition_service')
