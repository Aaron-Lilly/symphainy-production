#!/usr/bin/env python3
"""
Public Works Foundation Initialization Tests

Tests to verify foundation structure and initialization methods exist.
Following structure-first approach - verify components exist before full functionality testing.
"""

import pytest
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService


class TestPublicWorksFoundationInitialization:
    """Test Public Works Foundation initialization structure."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI Container for testing."""
        return DIContainerService("test")
    
    @pytest.fixture
    def foundation_service(self, di_container):
        """Create a Public Works Foundation Service instance."""
        return PublicWorksFoundationService(di_container=di_container)
    
    def test_foundation_initializes_with_di_container(self, foundation_service, di_container):
        """Test that foundation initializes with DI Container."""
        assert foundation_service.di_container is not None
        assert foundation_service.di_container == di_container
        assert foundation_service.service_name == "public_works_foundation"
    
    def test_foundation_has_all_layer_components(self, foundation_service):
        """Test that foundation has all 5-layer architecture components."""
        # Layer 0: Adapters (config_adapter)
        assert hasattr(foundation_service, 'config_adapter')
        
        # Layer 1: Abstractions
        assert hasattr(foundation_service, 'auth_abstraction')
        assert hasattr(foundation_service, 'authorization_abstraction')
        assert hasattr(foundation_service, 'session_abstraction')
        assert hasattr(foundation_service, 'tenant_abstraction')
        
        # Layer 2: Registries
        assert hasattr(foundation_service, 'security_registry')
        assert hasattr(foundation_service, 'file_management_registry')
        assert hasattr(foundation_service, 'content_metadata_registry')
        assert hasattr(foundation_service, 'service_discovery_registry')
        
        # Layer 3: Composition Services
        assert hasattr(foundation_service, 'composition_service')
    
    def test_foundation_initialization_creates_config_adapter(self, foundation_service):
        """Test that foundation has method to create config adapter."""
        assert hasattr(foundation_service, 'initialize_foundation')
        assert callable(foundation_service.initialize_foundation)
    
    def test_foundation_initialization_creates_adapters(self, foundation_service):
        """Test that foundation has method to create adapters."""
        # Check for adapter creation method (internal method)
        assert hasattr(foundation_service, '_create_all_adapters')
        assert callable(foundation_service._create_all_adapters)
    
    def test_foundation_initialization_creates_abstractions(self, foundation_service):
        """Test that foundation has method to create abstractions."""
        # Check for abstraction creation method (internal method)
        assert hasattr(foundation_service, '_create_all_abstractions')
        assert callable(foundation_service._create_all_abstractions)
    
    def test_foundation_initialization_initializes_registries(self, foundation_service):
        """Test that foundation has method to initialize registries."""
        # Check for registry initialization method (internal method)
        assert hasattr(foundation_service, '_initialize_and_register_abstractions')
        assert callable(foundation_service._initialize_and_register_abstractions)
    
    def test_foundation_initialization_sets_is_initialized(self, foundation_service):
        """Test that foundation has is_initialized flag."""
        assert hasattr(foundation_service, 'is_initialized')
        # Initially should be False
        assert foundation_service.is_initialized is False
    
    def test_foundation_uses_utility_access_mixin(self, foundation_service):
        """Test that foundation uses utility access mixin."""
        assert hasattr(foundation_service, 'get_logger')
        assert hasattr(foundation_service, 'get_utility')
        assert callable(foundation_service.get_logger)
        assert callable(foundation_service.get_utility)
