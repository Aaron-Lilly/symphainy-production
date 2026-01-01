#!/usr/bin/env python3
"""
Registry Initialization Tests

Tests to validate all 4 registries work correctly:
- SecurityRegistry
- FileManagementRegistry
- ContentMetadataRegistry
- ServiceDiscoveryRegistry
"""

import pytest
from foundations.public_works_foundation.infrastructure_registry.security_registry import SecurityRegistry
from foundations.public_works_foundation.infrastructure_registry.file_management_registry_gcs import FileManagementRegistry
from foundations.public_works_foundation.infrastructure_registry.content_metadata_registry import ContentMetadataRegistry
from foundations.public_works_foundation.infrastructure_registry.service_discovery_registry import ServiceDiscoveryRegistry


class TestRegistryInitialization:
    """Test registry initialization."""
    
    def test_security_registry_initializes(self):
        """Test that SecurityRegistry initializes successfully."""
        registry = SecurityRegistry()
        assert registry is not None
        assert hasattr(registry, '_abstractions')
        assert hasattr(registry, '_policy_engines')
        assert hasattr(registry, 'logger')
    
    def test_file_management_registry_initializes(self):
        """Test that FileManagementRegistry initializes successfully."""
        registry = FileManagementRegistry()
        assert registry is not None
        assert hasattr(registry, '_abstractions')
        assert hasattr(registry, 'logger')
    
    def test_content_metadata_registry_initializes(self):
        """Test that ContentMetadataRegistry initializes successfully."""
        registry = ContentMetadataRegistry()
        assert registry is not None
        assert hasattr(registry, '_abstractions')
        assert hasattr(registry, 'logger')
    
    def test_service_discovery_registry_initializes(self):
        """Test that ServiceDiscoveryRegistry initializes successfully."""
        registry = ServiceDiscoveryRegistry()
        assert registry is not None
        # ServiceDiscoveryRegistry uses 'abstraction' (singular) not '_abstractions' (plural)
        assert hasattr(registry, 'abstraction')
        assert hasattr(registry, 'logger')


class TestRegistryAbstractionRegistration:
    """Test registry abstraction registration."""
    
    @pytest.fixture
    def mock_abstraction(self):
        """Create a mock abstraction for testing."""
        class MockAbstraction:
            def __init__(self):
                self.name = "test_abstraction"
        return MockAbstraction()
    
    def test_security_registry_registers_abstractions(self, mock_abstraction):
        """Test that SecurityRegistry registers abstractions correctly."""
        registry = SecurityRegistry()
        registry.register_abstraction("test_auth", mock_abstraction)
        assert "test_auth" in registry._abstractions
        assert registry._abstractions["test_auth"] == mock_abstraction
    
    def test_file_management_registry_registers_abstraction(self, mock_abstraction):
        """Test that FileManagementRegistry registers abstractions correctly."""
        registry = FileManagementRegistry()
        registry.register_abstraction("test_file", mock_abstraction)
        assert "test_file" in registry._abstractions
        assert registry._abstractions["test_file"] == mock_abstraction
    
    def test_content_metadata_registry_registers_abstractions(self, mock_abstraction):
        """Test that ContentMetadataRegistry registers abstractions correctly."""
        registry = ContentMetadataRegistry()
        registry.register_abstraction("test_content", mock_abstraction)
        assert "test_content" in registry._abstractions
        assert registry._abstractions["test_content"] == mock_abstraction
    
    def test_service_discovery_registry_registers_abstraction(self, mock_abstraction):
        """Test that ServiceDiscoveryRegistry registers abstractions correctly."""
        registry = ServiceDiscoveryRegistry()
        registry.register_abstraction("test_service", mock_abstraction)
        # ServiceDiscoveryRegistry uses 'abstraction' (singular) not '_abstractions' (plural)
        assert registry.abstraction == mock_abstraction


class TestRegistryExposure:
    """Test registry abstraction exposure."""
    
    @pytest.fixture
    def mock_abstraction(self):
        """Create a mock abstraction for testing."""
        class MockAbstraction:
            def __init__(self):
                self.name = "test_abstraction"
        return MockAbstraction()
    
    def test_security_registry_exposes_abstractions(self, mock_abstraction):
        """Test that SecurityRegistry exposes abstractions correctly."""
        registry = SecurityRegistry()
        registry.register_abstraction("test_auth", mock_abstraction)
        
        # Test get_abstraction method
        if hasattr(registry, 'get_abstraction'):
            abstraction = registry.get_abstraction("test_auth")
            assert abstraction == mock_abstraction
        else:
            # Fallback: check direct access
            assert registry._abstractions["test_auth"] == mock_abstraction
    
    def test_file_management_registry_exposes_abstraction(self, mock_abstraction):
        """Test that FileManagementRegistry exposes abstractions correctly."""
        registry = FileManagementRegistry()
        registry.register_abstraction("test_file", mock_abstraction)
        
        if hasattr(registry, 'get_abstraction'):
            abstraction = registry.get_abstraction("test_file")
            assert abstraction == mock_abstraction
        else:
            assert registry._abstractions["test_file"] == mock_abstraction
    
    def test_content_metadata_registry_exposes_abstraction(self, mock_abstraction):
        """Test that ContentMetadataRegistry exposes abstractions correctly."""
        registry = ContentMetadataRegistry()
        registry.register_abstraction("test_content", mock_abstraction)
        
        if hasattr(registry, 'get_abstraction'):
            abstraction = registry.get_abstraction("test_content")
            assert abstraction == mock_abstraction
        else:
            assert registry._abstractions["test_content"] == mock_abstraction
    
    def test_service_discovery_registry_exposes_abstraction(self, mock_abstraction):
        """Test that ServiceDiscoveryRegistry exposes abstractions correctly."""
        registry = ServiceDiscoveryRegistry()
        registry.register_abstraction("test_service", mock_abstraction)
        
        # ServiceDiscoveryRegistry uses 'get_service_discovery()' method
        if hasattr(registry, 'get_service_discovery'):
            abstraction = registry.get_service_discovery()
            assert abstraction == mock_abstraction
        else:
            # Fallback: check direct access
            assert registry.abstraction == mock_abstraction
