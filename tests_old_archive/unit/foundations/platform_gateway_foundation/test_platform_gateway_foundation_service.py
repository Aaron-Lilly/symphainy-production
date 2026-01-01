#!/usr/bin/env python3
"""
PlatformGatewayFoundationService Tests

Tests for PlatformGatewayFoundationService in isolation.
Verifies foundation service works correctly and provides Platform Gateway access.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestPlatformGatewayFoundationService:
    """Test PlatformGatewayFoundationService functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        container = MagicMock()
        container.service_registry = {}
        return container
    
    @pytest.fixture
    def mock_public_works_foundation(self):
        """Mock Public Works Foundation."""
        foundation = MagicMock()
        foundation.get_abstraction = MagicMock(return_value=MagicMock())
        return foundation
    
    @pytest.fixture
    def service(self, mock_di_container, mock_public_works_foundation):
        """Create PlatformGatewayFoundationService instance."""
        from foundations.platform_gateway_foundation.platform_gateway_foundation_service import PlatformGatewayFoundationService
        
        service = PlatformGatewayFoundationService(
            di_container=mock_di_container,
            public_works_foundation=mock_public_works_foundation
        )
        return service
    
    @pytest.mark.asyncio
    async def test_service_initializes(self, service, mock_public_works_foundation):
        """Test service initializes correctly."""
        result = await service.initialize()
        assert result is True
        assert service.is_initialized is True
        assert service.platform_gateway is not None
    
    @pytest.mark.asyncio
    async def test_get_platform_gateway(self, service):
        """Test service can return Platform Gateway."""
        await service.initialize()
        gateway = service.get_platform_gateway()
        assert gateway is not None
    
    @pytest.mark.asyncio
    async def test_get_abstraction(self, service, mock_public_works_foundation):
        """Test service can get abstraction via Platform Gateway."""
        await service.initialize()
        
        # Mock the platform gateway's get_abstraction
        service.platform_gateway.get_abstraction = MagicMock(return_value=MagicMock())
        
        abstraction = service.get_abstraction("business_enablement", "file_management")
        assert abstraction is not None
        service.platform_gateway.get_abstraction.assert_called_once_with("business_enablement", "file_management")
    
    @pytest.mark.asyncio
    async def test_get_realm_abstractions(self, service):
        """Test service can get realm abstractions."""
        await service.initialize()
        
        abstractions = service.get_realm_abstractions("business_enablement")
        assert isinstance(abstractions, list)
        assert len(abstractions) > 0
    
    @pytest.mark.asyncio
    async def test_validate_realm_access(self, service):
        """Test service can validate realm access."""
        await service.initialize()
        
        # business_enablement should have access to file_management
        result = service.validate_realm_access("business_enablement", "file_management")
        assert result is True
        
        # business_enablement should NOT have access to session (not in its list)
        result = service.validate_realm_access("business_enablement", "session")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_shutdown(self, service):
        """Test service can shutdown."""
        await service.initialize()
        result = await service.shutdown()
        assert result is True
        assert service.is_initialized is False

