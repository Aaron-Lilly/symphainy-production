#!/usr/bin/env python3
"""
Layer 3: Public Works Foundation Lifecycle Tests

Tests that validate Public Works Foundation lifecycle (initialize, shutdown).

WHAT: Validate foundation lifecycle
HOW: Test initialize and shutdown methods
"""

import pytest

import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService

class TestPublicWorksFoundationLifecycle:
    """Test that Public Works Foundation lifecycle works correctly."""
    
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
    
    @pytest.mark.asyncio
    async def test_foundation_initializes_successfully(self, foundation_service):
        """Test that foundation initializes successfully."""
        mock_config = Mock()
        mock_config.set_env_from_file = Mock()
        
        with patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter', return_value=mock_config), \
             patch('utilities.path_utils.get_config_file_path', return_value=Path('/nonexistent')), \
             patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_enhanced_platform_capabilities', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, 'log_operation_with_telemetry', new_callable=AsyncMock):
            
            result = await foundation_service.initialize()
            
            assert result is True
            assert foundation_service.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_foundation_shutdown_successfully(self, foundation_service):
        """Test that foundation shuts down successfully."""
        # First initialize
        mock_config = Mock()
        mock_config.set_env_from_file = Mock()
        
        with patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter', return_value=mock_config), \
             patch('utilities.path_utils.get_config_file_path', return_value=Path('/nonexistent')), \
             patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_enhanced_platform_capabilities', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, 'log_operation_with_telemetry', new_callable=AsyncMock), \
             patch.object(foundation_service, 'shutdown_foundation', new_callable=AsyncMock, return_value=True):
            
            await foundation_service.initialize()
            
            # Now shutdown
            result = await foundation_service.shutdown()
            
            assert result is True
            assert foundation_service.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_foundation_can_reinitialize_after_shutdown(self, foundation_service):
        """Test that foundation can re-initialize after shutdown."""
        mock_config = Mock()
        mock_config.set_env_from_file = Mock()
        
        with patch('foundations.public_works_foundation.public_works_foundation_service.ConfigAdapter', return_value=mock_config), \
             patch('utilities.path_utils.get_config_file_path', return_value=Path('/nonexistent')), \
             patch.object(foundation_service, '_create_all_adapters', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_create_all_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_and_register_abstractions', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, '_initialize_enhanced_platform_capabilities', new_callable=AsyncMock, return_value=True), \
             patch.object(foundation_service, 'log_operation_with_telemetry', new_callable=AsyncMock), \
             patch.object(foundation_service, 'shutdown_foundation', new_callable=AsyncMock, return_value=True):
            
            # Initialize
            await foundation_service.initialize()
            assert foundation_service.is_initialized is True
            
            # Shutdown
            await foundation_service.shutdown()
            assert foundation_service.is_initialized is False
            
            # Re-initialize
            await foundation_service.initialize()
            assert foundation_service.is_initialized is True
