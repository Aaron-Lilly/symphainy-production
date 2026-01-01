#!/usr/bin/env python3
"""
Unit Tests - DI Container Service

Tests for the DI Container (foundation for all services).
"""

import pytest
from unittest.mock import Mock, MagicMock

pytestmark = [pytest.mark.unit, pytest.mark.foundations, pytest.mark.fast]

class TestDIContainerService:
    """Test DI Container Service functionality."""
    
    @pytest.mark.asyncio
    async def test_di_container_initialization(self, real_di_container):
        """Test DI container can be initialized."""
        assert real_di_container is not None
        assert real_di_container.service_name == "test_service"
    
    def test_di_container_provides_logger(self, real_di_container):
        """Test DI container provides logger."""
        logger = real_di_container.get_logger("test_component")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
    
    def test_di_container_provides_config(self, real_di_container):
        """Test DI container provides configuration."""
        config = real_di_container.get_config()
        assert config is not None
        assert hasattr(config, 'get')
    
    def test_di_container_provides_health(self, real_di_container):
        """Test DI container provides health service."""
        health = real_di_container.get_health()
        assert health is not None
        assert hasattr(health, 'record_request')
        assert hasattr(health, 'record_operation')
    
    def test_di_container_provides_telemetry(self, real_di_container):
        """Test DI container provides telemetry service."""
        telemetry = real_di_container.get_telemetry()
        assert telemetry is not None
        assert hasattr(telemetry, 'record_metric')
    
    def test_di_container_provides_security(self, real_di_container):
        """Test DI container provides security service."""
        security = real_di_container.get_security()
        assert security is not None
        assert hasattr(security, 'validate_user_permission')
    
    def test_di_container_provides_error_handler(self, real_di_container):
        """Test DI container provides error handler."""
        error_handler = real_di_container.get_error_handler()
        assert error_handler is not None
        assert hasattr(error_handler, 'handle_error')
    
    def test_di_container_provides_tenant(self, real_di_container):
        """Test DI container provides tenant service."""
        tenant = real_di_container.get_tenant()
        assert tenant is not None
        assert hasattr(tenant, 'get_tenant_config')
        assert hasattr(tenant, 'validate_tenant_type')
    
    def test_di_container_lazy_loading(self, real_di_container):
        """Test DI container lazy loads utilities."""
        # First access should initialize
        logger1 = real_di_container.get_logger("test1")
        logger2 = real_di_container.get_logger("test2")
        
        # Both should be valid loggers
        assert logger1 is not None
        assert logger2 is not None

class TestMockDIContainer:
    """Test mock DI container for unit testing."""
    
    def test_mock_container_has_logger(self, mock_di_container):
        """Test mock container provides logger."""
        assert mock_di_container.logger is not None
        assert hasattr(mock_di_container.logger, 'info')
    
    def test_mock_container_has_config(self, mock_di_container):
        """Test mock container provides config."""
        assert mock_di_container.config is not None
        config_value = mock_di_container.config.get("test_key")
        assert config_value == "test_value"
    
    def test_mock_container_has_all_utilities(self, mock_di_container):
        """Test mock container provides all utilities."""
        assert mock_di_container.health is not None
        assert mock_di_container.telemetry is not None
        assert mock_di_container.security is not None
        assert mock_di_container.error_handler is not None
        assert mock_di_container.tenant is not None
        assert mock_di_container.validation is not None
        assert mock_di_container.serialization is not None

