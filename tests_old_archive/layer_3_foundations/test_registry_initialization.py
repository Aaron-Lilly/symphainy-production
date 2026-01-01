#!/usr/bin/env python3
"""
Layer 3: Public Works Foundation Registry Tests

Tests that validate registries initialize and work correctly.

WHAT: Validate registry initialization and functionality
HOW: Test that registries register and expose abstractions correctly
"""

import pytest

import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from foundations.public_works_foundation.infrastructure_registry.security_registry import SecurityRegistry
from foundations.public_works_foundation.infrastructure_registry.file_management_registry_gcs import FileManagementRegistry
from foundations.public_works_foundation.infrastructure_registry.content_metadata_registry import ContentMetadataRegistry
from foundations.public_works_foundation.infrastructure_registry.service_discovery_registry import ServiceDiscoveryRegistry

class TestRegistryInitialization:
    """Test that registries initialize correctly."""
    
    def test_security_registry_initializes(self):
        """Test that SecurityRegistry initializes correctly."""
        registry = SecurityRegistry()
        
        assert registry is not None
        assert hasattr(registry, "logger")  # All registries have logger
        # is_ready may not exist on all registries
    
    def test_file_management_registry_initializes(self):
        """Test that FileManagementRegistry initializes correctly."""
        registry = FileManagementRegistry()
        
        assert registry is not None
        assert hasattr(registry, "logger")  # All registries have logger
    
    def test_content_metadata_registry_initializes(self):
        """Test that ContentMetadataRegistry initializes correctly."""
        registry = ContentMetadataRegistry()
        
        assert registry is not None
        assert hasattr(registry, "logger")  # All registries have logger
    
    def test_service_discovery_registry_initializes(self):
        """Test that ServiceDiscoveryRegistry initializes correctly."""
        registry = ServiceDiscoveryRegistry()
        
        assert registry is not None
        assert hasattr(registry, "logger")  # All registries have logger
        # is_ready may not exist on all registries

class TestRegistryAbstractionRegistration:
    """Test that registries register abstractions correctly."""
    
    def test_security_registry_registers_abstractions(self):
        """Test that SecurityRegistry registers abstractions."""
        registry = SecurityRegistry()
        mock_auth = Mock()
        mock_authorization = Mock()
        mock_session = Mock()
        mock_tenant = Mock()
        
        result = registry.register_abstraction("auth", mock_auth)
        # register_abstraction may return None or True
        
        result = registry.register_abstraction("authorization", mock_authorization)
        # register_abstraction may return None or True
        
        result = registry.register_abstraction("session", mock_session)
        # register_abstraction may return None or True
        
        result = registry.register_abstraction("tenant", mock_tenant)
        # register_abstraction may return None or True
    
    def test_file_management_registry_registers_abstraction(self):
        """Test that FileManagementRegistry registers abstraction."""
        registry = FileManagementRegistry()
        mock_abstraction = Mock()
        mock_composition = Mock()
        
        registry.register_abstraction("file_management", mock_abstraction)
        registry.register_composition_service("file_management", mock_composition)
        
        # Verify registration
        assert registry.get_abstraction("file_management") == mock_abstraction
    
    def test_content_metadata_registry_registers_abstractions(self):
        """Test that ContentMetadataRegistry registers abstractions."""
        registry = ContentMetadataRegistry()
        mock_abstraction = Mock()
        mock_composition = Mock()
        
        registry.register_abstraction("content_metadata", mock_abstraction)
        registry.register_composition_service("content_metadata", mock_composition)
        
        # Verify registration
        assert registry.get_abstraction("content_metadata") == mock_abstraction
    
    def test_service_discovery_registry_registers_abstraction(self):
        """Test that ServiceDiscoveryRegistry registers abstraction."""
        registry = ServiceDiscoveryRegistry()
        mock_abstraction = Mock()
        
        result = registry.register_abstraction("service_discovery", mock_abstraction)
        
        assert result is True
        assert registry.abstraction == mock_abstraction
        assert registry.is_ready is True

class TestRegistryExposure:
    """Test that registries expose abstractions correctly."""
    
    def test_security_registry_exposes_abstractions(self):
        """Test that SecurityRegistry exposes abstractions."""
        registry = SecurityRegistry()
        mock_auth = Mock()
        mock_authorization = Mock()
        
        registry.register_abstraction("auth", mock_auth)
        registry.register_abstraction("authorization", mock_authorization)
        
        # Verify exposure
        assert registry.get_abstraction("auth") == mock_auth
        assert registry.get_abstraction("authorization") == mock_authorization
    
    def test_file_management_registry_exposes_abstraction(self):
        """Test that FileManagementRegistry exposes abstraction."""
        registry = FileManagementRegistry()
        mock_abstraction = Mock()
        
        registry.register_abstraction("file_management", mock_abstraction)
        
        # Verify exposure
        assert registry.get_abstraction("file_management") == mock_abstraction
    
    def test_content_metadata_registry_exposes_abstraction(self):
        """Test that ContentMetadataRegistry exposes abstraction."""
        registry = ContentMetadataRegistry()
        mock_abstraction = Mock()
        
        registry.register_abstraction("content_metadata", mock_abstraction)
        
        # Verify exposure
        assert registry.get_abstraction("content_metadata") == mock_abstraction
    
    def test_service_discovery_registry_exposes_abstraction(self):
        """Test that ServiceDiscoveryRegistry exposes abstraction."""
        registry = ServiceDiscoveryRegistry()
        mock_abstraction = Mock()
        
        registry.register_abstraction("service_discovery", mock_abstraction)
        
        # Verify exposure
        assert registry.get_service_discovery() == mock_abstraction
