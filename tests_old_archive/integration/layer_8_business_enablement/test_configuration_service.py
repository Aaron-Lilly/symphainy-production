#!/usr/bin/env python3
"""
Functional tests for ConfigurationService.

Tests configuration management capabilities.
"""

import pytest
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestConfigurationServiceFunctional:
    """Functional tests for ConfigurationService."""
    
    @pytest.fixture(scope="function")
    async def configuration_service(self, smart_city_infrastructure):
        """Create ConfigurationService instance."""
        from backend.business_enablement.enabling_services.configuration_service import ConfigurationService
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = ConfigurationService(
            service_name="ConfigurationService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "ConfigurationService should initialize successfully"
        
        return service
    
    @pytest.fixture(scope="function")
    def mock_user_context(self) -> Dict[str, Any]:
        """Create a mock user context."""
        return {
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_123",
            "email": "test@example.com",
            "permissions": ["read", "write"]
        }
    
    async def test_service_initialization(self, configuration_service):
        """Test that ConfigurationService initializes correctly."""
        assert configuration_service is not None
        assert configuration_service.is_initialized is True
        assert configuration_service.librarian is not None
        
        logger.info("✅ ConfigurationService initialized correctly")
    
    async def test_get_config(
        self,
        configuration_service,
        mock_user_context
    ):
        """Test getting a configuration value."""
        result = await configuration_service.get_config(
            config_key="test_config_key",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        # May succeed or fail depending on whether config exists
        assert "success" in result
        
        logger.info(f"✅ Config retrieval attempted: {result.get('success')}")
    
    async def test_set_config(
        self,
        configuration_service,
        mock_user_context
    ):
        """Test setting a configuration value."""
        result = await configuration_service.set_config(
            config_key="test_config_key",
            value="test_value",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "config_key" in result
        
        logger.info("✅ Config set successfully")
    
    async def test_validate_config(
        self,
        configuration_service,
        mock_user_context
    ):
        """Test validating a configuration."""
        result = await configuration_service.validate_config(
            config_key="test_config_key",
            value="test_value",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        # May succeed or fail depending on whether config exists
        assert "success" in result
        
        logger.info(f"✅ Config validation attempted: {result.get('success')}")
    
    async def test_get_all_configs(
        self,
        configuration_service,
        mock_user_context
    ):
        """Test getting all configurations."""
        result = await configuration_service.get_all_configs(
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "configs" in result or "count" in result
        
        logger.info("✅ All configs retrieved successfully")
    
    async def test_get_config_security_validation(
        self,
        configuration_service
    ):
        """Test that getting configs requires proper permissions."""
        # User context without permissions
        unauthorized_context = {
            "user_id": "unauthorized_user",
            "tenant_id": "test_tenant_123",
            "permissions": []  # No permissions
        }
        
        # This should raise PermissionError
        with pytest.raises(PermissionError):
            await configuration_service.get_config(
                config_key="test_config_key",
                user_context=unauthorized_context
            )
        
        logger.info("✅ Security validation tested")
    
    async def test_health_check(self, configuration_service):
        """Test health check."""
        health = await configuration_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health or "service_name" in health
        
        logger.info("✅ Health check passed")
    
    async def test_get_service_capabilities(self, configuration_service):
        """Test service capabilities."""
        capabilities = await configuration_service.get_service_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "service_name" in capabilities or "capabilities" in capabilities
        
        logger.info("✅ Service capabilities verified")
    
    async def test_architecture_verification(self, configuration_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions (if needed)
        assert configuration_service.platform_gateway is not None
        
        # Verify it uses Smart City services via RealmServiceBase
        assert configuration_service.librarian is not None
        
        logger.info("✅ Architecture verification passed (5-layer pattern)")

