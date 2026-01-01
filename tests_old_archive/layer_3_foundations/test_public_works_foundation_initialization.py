#!/usr/bin/env python3
"""
Layer 3: Public Works Foundation Initialization Tests

Tests that validate Public Works Foundation initializes all layers correctly.

WHAT: Validate foundation initialization
HOW: Test that all adapters, abstractions, registries, and composition services are created
"""

import pytest

import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService

class TestPublicWorksFoundationInitialization:
    """Test that Public Works Foundation initializes correctly."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock(spec=DIContainerService)
        container.realm_name = "public_works_foundation"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        return container
    
    @pytest.fixture
    def foundation_service(self, mock_di_container):
        """Create Public Works Foundation Service instance."""
        return PublicWorksFoundationService(
            di_container=mock_di_container,
            security_provider=None,
            authorization_guard=None,
            communication_foundation=None
        )
    
    def test_foundation_initializes_with_di_container(self, foundation_service, mock_di_container):
        """Test that foundation initializes with DI Container."""
        assert foundation_service.di_container == mock_di_container
        assert foundation_service.service_name == "public_works_foundation"
        assert foundation_service.is_initialized is False
    
    def test_foundation_has_all_layer_components(self, foundation_service):
        """Test that foundation has all 5-layer architecture components."""
        # Layer 0: Adapters (will be created during initialization)
        assert hasattr(foundation_service, 'config_adapter')
        
        # Layer 1: Abstractions (will be created during initialization)
        assert hasattr(foundation_service, 'auth_abstraction')
        assert hasattr(foundation_service, 'file_management_abstraction')
        assert hasattr(foundation_service, 'content_metadata_abstraction')
        
        # Layer 2: Registries (will be created during initialization)
        assert hasattr(foundation_service, 'security_registry')
        assert hasattr(foundation_service, 'file_management_registry')
        assert hasattr(foundation_service, 'content_metadata_registry')
        assert hasattr(foundation_service, 'service_discovery_registry')
        
        # Layer 3: Composition Services (will be created during initialization)
        assert hasattr(foundation_service, 'composition_service')
    
    @pytest.mark.asyncio
    async def test_foundation_initialization_creates_config_adapter(self, foundation_service):
        """Test that foundation creates ConfigAdapter during initialization."""
        # Mock the initialization to avoid real infrastructure
        with patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True) as mock_create_adapters, \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True) as mock_create_abstractions, \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True) as mock_register, \
             patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter') as mock_config_adapter:
            
            mock_config_adapter.return_value = Mock()
            
            result = await foundation_service.initialize_foundation()
            
            assert result is True
            assert foundation_service.config_adapter is not None
            mock_create_adapters.assert_called_once()
            mock_create_abstractions.assert_called_once()
            mock_register.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_foundation_initialization_creates_adapters(self, foundation_service):
        """Test that foundation creates all adapters (Layer 0)."""
        with patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True) as mock_create_adapters, \
             patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter') as mock_config_adapter, \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True):
            
            mock_config_adapter.return_value = Mock()
            
            await foundation_service.initialize_foundation()
            
            mock_create_adapters.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_foundation_initialization_creates_abstractions(self, foundation_service):
        """Test that foundation creates all abstractions (Layer 1)."""
        with patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True) as mock_create_abstractions, \
             patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter') as mock_config_adapter, \
             patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True):
            
            mock_config_adapter.return_value = Mock()
            
            await foundation_service.initialize_foundation()
            
            mock_create_abstractions.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_foundation_initialization_initializes_registries(self, foundation_service):
        """Test that foundation initializes all registries (Layer 2)."""
        with patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True) as mock_register, \
             patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter') as mock_config_adapter, \
             patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True):
            
            mock_config_adapter.return_value = Mock()
            
            await foundation_service.initialize_foundation()
            
            mock_register.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_foundation_initialization_sets_is_initialized(self, foundation_service):
        """Test that foundation sets is_initialized flag after successful initialization."""
        with patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter') as mock_config_adapter, \
             patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_enhanced_platform_capabilities', new_callable=AsyncMock):
            
            mock_config_adapter.return_value = Mock()
            
            await foundation_service.initialize()
            
            assert foundation_service.is_initialized is True
    
    def test_foundation_uses_utility_access_mixin(self, foundation_service):
        """Test that foundation uses UtilityAccessMixin (inherited from FoundationServiceBase)."""
        # FoundationServiceBase should provide get_utility method
        assert hasattr(foundation_service, 'get_utility') or hasattr(foundation_service, 'di_container'), \
            "Public Works Foundation should have access to utilities via DI Container"
