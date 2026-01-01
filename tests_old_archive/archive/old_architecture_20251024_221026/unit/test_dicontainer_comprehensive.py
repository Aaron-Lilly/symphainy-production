#!/usr/bin/env python3
"""
Comprehensive Unit Tests: DIContainer Service

Tests the DIContainerService with comprehensive coverage based on infrastructure testing learnings.
This test suite ensures we catch all the types of issues we discovered in infrastructure testing.

WHAT (Test Role): I validate the DI container with comprehensive coverage
HOW (Test Implementation): I test initialization, dependency injection, error handling, and integration scenarios

Key Learnings from Infrastructure Testing:
1. Test actual service connections, not just abstractions
2. Test error handling and failure scenarios
3. Test configuration loading and environment variables
4. Test dependency chains and startup order
5. Test port/connection issues and resource conflicts
"""

import pytest
import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../symphainy-platform'))

from foundations.di_container.di_container_service import DIContainerService


class TestDIContainerServiceComprehensive:
    """Comprehensive test suite for DIContainerService based on infrastructure testing learnings."""
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock environment files
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("""
# Test environment variables
SERVICE_NAME=test_service
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL=30
TELEMETRY_ENABLED=true
SECURITY_ENABLED=true
TENANT_MODE=multi
VALIDATION_STRICT=true
SERIALIZATION_FORMAT=json
""")
            yield temp_dir
    
    @pytest.fixture
    def di_container(self, mock_environment):
        """Create a DI container for testing with mock environment."""
        with patch.dict(os.environ, {
            'SERVICE_NAME': 'test_service',
            'LOG_LEVEL': 'INFO',
            'HEALTH_CHECK_INTERVAL': '30',
            'TELEMETRY_ENABLED': 'true',
            'SECURITY_ENABLED': 'true',
            'TENANT_MODE': 'multi',
            'VALIDATION_STRICT': 'true',
            'SERIALIZATION_FORMAT': 'json'
        }):
            return DIContainerService("test_service")
    
    def test_di_container_initialization_success(self, di_container):
        """Test DI container initializes correctly with all utilities."""
        assert di_container is not None
        assert di_container.service_name == "test_service"
        assert isinstance(di_container.initialization_time, datetime)
        
        # Test all utility access methods exist
        assert hasattr(di_container, 'get_logger')
        assert hasattr(di_container, 'get_config')
        assert hasattr(di_container, 'get_health')
        assert hasattr(di_container, 'get_telemetry')
        assert hasattr(di_container, 'get_security')
        assert hasattr(di_container, 'get_error_handler')
        assert hasattr(di_container, 'get_tenant')
        assert hasattr(di_container, 'get_validation')
        assert hasattr(di_container, 'get_serialization')
    
    def test_di_container_initialization_with_different_service_names(self):
        """Test DI container initialization with different service names."""
        service_names = ["test_service", "business_service", "smart_city_service", "foundation"]
        
        for service_name in service_names:
            container = DIContainerService(service_name)
            assert container.service_name == service_name
            assert container is not None
    
    def test_configuration_loading_success(self, di_container):
        """Test configuration loading works correctly."""
        config = di_container.get_config()
        assert config is not None
        assert hasattr(config, 'config_cache')
        assert isinstance(config.config_cache, dict)
        
        # Test configuration access methods
        assert hasattr(config, 'get')
        assert hasattr(config, 'get_string')
        assert hasattr(config, 'get_int')
        assert hasattr(config, 'get_bool')
    
    def test_configuration_loading_failure_handling(self):
        """Test configuration loading failure is handled gracefully."""
        with patch('utilities.configuration.unified_configuration_manager.UnifiedConfigurationManager') as mock_config:
            mock_config.side_effect = Exception("Configuration loading failed")
            
            # Should not raise exception, should fallback to empty config
            container = DIContainerService("test_service")
            assert container.env_config == {}
    
    def test_logger_utility_access(self, di_container):
        """Test logger utility access and functionality."""
        logger = di_container.get_logger("test_logger")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')
        
        # Test logger can be called without errors
        logger.info("Test log message")
        logger.error("Test error message")
        logger.warning("Test warning message")
        logger.debug("Test debug message")
    
    def test_health_utility_access(self, di_container):
        """Test health utility access and functionality."""
        health = di_container.get_health()
        assert health is not None
        assert hasattr(health, 'get_status')
        assert hasattr(health, 'set_status')
        assert hasattr(health, 'register_health_check')
        
        # Test health utility methods
        status = health.get_status()
        assert isinstance(status, dict)
        
        health.set_status("test_component", "healthy")
        assert health.get_status()["test_component"] == "healthy"
    
    def test_telemetry_utility_access(self, di_container):
        """Test telemetry utility access and functionality."""
        telemetry = di_container.get_telemetry()
        assert telemetry is not None
        assert hasattr(telemetry, 'record_metric')
        assert hasattr(telemetry, 'bootstrap')
        assert hasattr(telemetry, 'is_bootstrapped')
        
        # Test telemetry methods
        assert telemetry.is_bootstrapped() is False
        telemetry.bootstrap()
        assert telemetry.is_bootstrapped() is True
        
        # Test metric recording
        telemetry.record_metric("test_metric", 42, {"tag": "value"})
    
    def test_security_utility_access(self, di_container):
        """Test security utility access and functionality."""
        security = di_container.get_security()
        assert security is not None
        assert hasattr(security, 'bootstrap')
        assert hasattr(security, 'is_bootstrapped')
        assert hasattr(security, 'service_name')
        
        # Test security methods
        assert security.service_name == "test_service"
        assert security.is_bootstrapped() is False
        security.bootstrap()
        assert security.is_bootstrapped() is True
    
    def test_error_handler_utility_access(self, di_container):
        """Test error handler utility access and functionality."""
        error_handler = di_container.get_error_handler()
        assert error_handler is not None
        assert hasattr(error_handler, 'handle_error')
        assert hasattr(error_handler, 'log_error')
        
        # Test error handling
        try:
            raise ValueError("Test error")
        except Exception as e:
            error_handler.handle_error(e, "test_context")
    
    def test_tenant_utility_access(self, di_container):
        """Test tenant utility access and functionality."""
        tenant = di_container.get_tenant()
        assert tenant is not None
        assert hasattr(tenant, 'get_current_tenant')
        assert hasattr(tenant, 'set_tenant')
        
        # Test tenant methods
        current_tenant = tenant.get_current_tenant()
        assert current_tenant is not None
    
    def test_validation_utility_access(self, di_container):
        """Test validation utility access and functionality."""
        validation = di_container.get_validation()
        assert validation is not None
        assert hasattr(validation, 'validate')
        assert hasattr(validation, 'validate_schema')
        
        # Test validation methods
        result = validation.validate("test_data", "string")
        assert result is True
    
    def test_serialization_utility_access(self, di_container):
        """Test serialization utility access and functionality."""
        serialization = di_container.get_serialization()
        assert serialization is not None
        assert hasattr(serialization, 'serialize')
        assert hasattr(serialization, 'deserialize')
        
        # Test serialization methods
        test_data = {"key": "value", "number": 42}
        serialized = serialization.serialize(test_data)
        assert isinstance(serialized, str)
        
        deserialized = serialization.deserialize(serialized)
        assert deserialized == test_data
    
    def test_fastapi_app_creation(self, di_container):
        """Test FastAPI app creation and configuration."""
        app = di_container.create_fastapi_app("test_app")
        assert app is not None
        assert hasattr(app, 'get')
        assert hasattr(app, 'post')
        assert hasattr(app, 'put')
        assert hasattr(app, 'delete')
        
        # Test app configuration
        assert app.title == "test_app MCP Server"
        assert app.version == "1.0.0"
        assert "/docs" in str(app.docs_url)
        assert "/redoc" in str(app.redoc_url)
    
    def test_fastapi_app_creation_with_custom_config(self, di_container):
        """Test FastAPI app creation with custom configuration."""
        custom_config = {
            "title": "Custom Test App",
            "version": "2.0.0",
            "description": "Custom test application"
        }
        
        app = di_container.create_fastapi_app("test_app", custom_config)
        assert app.title == "Custom Test App"
        assert app.version == "2.0.0"
        assert app.description == "Custom test application"
    
    def test_utility_dependency_injection(self, di_container):
        """Test that utilities are properly injected and can access each other."""
        # Test that utilities can access the DI container
        logger = di_container.get_logger("test")
        health = di_container.get_health()
        telemetry = di_container.get_telemetry()
        
        # Test that utilities are properly initialized
        assert logger is not None
        assert health is not None
        assert telemetry is not None
        
        # Test that utilities can work together
        health.set_status("test_component", "healthy")
        telemetry.record_metric("health_check", 1, {"component": "test_component"})
    
    def test_bootstrap_sequence(self, di_container):
        """Test that bootstrap sequence works correctly."""
        # Test that bootstrap-aware utilities are properly initialized
        telemetry = di_container.get_telemetry()
        security = di_container.get_security()
        
        # Test initial state
        assert telemetry.is_bootstrapped() is False
        assert security.is_bootstrapped() is False
        
        # Test bootstrap
        telemetry.bootstrap()
        security.bootstrap()
        
        assert telemetry.is_bootstrapped() is True
        assert security.is_bootstrapped() is True
    
    def test_error_handling_during_initialization(self):
        """Test error handling during initialization."""
        with patch('utilities.logging.logging_service.SmartCityLoggingService') as mock_logger:
            mock_logger.side_effect = Exception("Logger initialization failed")
            
            # Should raise exception during initialization
            with pytest.raises(Exception):
                DIContainerService("test_service")
    
    def test_partial_initialization_failure(self):
        """Test handling of partial initialization failures."""
        with patch('utilities.health.health_management_utility.HealthManagementUtility') as mock_health:
            mock_health.side_effect = Exception("Health utility initialization failed")
            
            # Should raise exception during initialization
            with pytest.raises(Exception):
                DIContainerService("test_service")
    
    def test_environment_variable_handling(self, mock_environment):
        """Test environment variable handling and configuration."""
        with patch.dict(os.environ, {
            'SERVICE_NAME': 'test_service',
            'LOG_LEVEL': 'DEBUG',
            'HEALTH_CHECK_INTERVAL': '60',
            'TELEMETRY_ENABLED': 'false',
            'SECURITY_ENABLED': 'false'
        }):
            container = DIContainerService("test_service")
            config = container.get_config()
            
            # Test that environment variables are loaded
            assert config.get_string('SERVICE_NAME') == 'test_service'
            assert config.get_string('LOG_LEVEL') == 'DEBUG'
            assert config.get_int('HEALTH_CHECK_INTERVAL') == 60
            assert config.get_bool('TELEMETRY_ENABLED') is False
            assert config.get_bool('SECURITY_ENABLED') is False
    
    def test_configuration_fallback_behavior(self):
        """Test configuration fallback behavior when environment variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            container = DIContainerService("test_service")
            config = container.get_config()
            
            # Test fallback values
            assert config.get_string('SERVICE_NAME', 'default') == 'default'
            assert config.get_int('HEALTH_CHECK_INTERVAL', 30) == 30
            assert config.get_bool('TELEMETRY_ENABLED', True) is True
    
    def test_multiple_container_instances(self):
        """Test that multiple container instances work independently."""
        container1 = DIContainerService("service1")
        container2 = DIContainerService("service2")
        
        assert container1.service_name == "service1"
        assert container2.service_name == "service2"
        assert container1 is not container2
        
        # Test that utilities are independent
        logger1 = container1.get_logger("test")
        logger2 = container2.get_logger("test")
        assert logger1 is not logger2
    
    def test_utility_lifecycle_management(self, di_container):
        """Test utility lifecycle management."""
        # Test that utilities are properly initialized
        logger = di_container.get_logger("test")
        health = di_container.get_health()
        
        # Test that utilities can be accessed multiple times
        logger2 = di_container.get_logger("test")
        health2 = di_container.get_health()
        
        # Should return the same instances
        assert logger is logger2
        assert health is health2
    
    def test_integration_with_foundation_services(self, di_container):
        """Test integration with foundation services."""
        # Test that DI container can be used by foundation services
        from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationService
        
        # This should work without errors
        foundation_service = InfrastructureFoundationService(di_container)
        assert foundation_service is not None
    
    def test_async_utility_access(self, di_container):
        """Test async utility access patterns."""
        async def test_async_operations():
            logger = di_container.get_logger("async_test")
            health = di_container.get_health()
            telemetry = di_container.get_telemetry()
            
            # Test async operations
            logger.info("Async test message")
            health.set_status("async_component", "healthy")
            telemetry.record_metric("async_metric", 1)
            
            return True
        
        # Run async test
        result = asyncio.run(test_async_operations())
        assert result is True
    
    def test_resource_cleanup(self, di_container):
        """Test resource cleanup and memory management."""
        # Test that utilities can be properly cleaned up
        logger = di_container.get_logger("cleanup_test")
        health = di_container.get_health()
        
        # Test cleanup operations
        health.set_status("cleanup_component", "healthy")
        logger.info("Cleanup test message")
        
        # Test that resources are properly managed
        assert logger is not None
        assert health is not None
    
    def test_concurrent_access(self, di_container):
        """Test concurrent access to utilities."""
        import threading
        import time
        
        results = []
        
        def worker(worker_id):
            logger = di_container.get_logger(f"worker_{worker_id}")
            health = di_container.get_health()
            
            # Test concurrent operations
            logger.info(f"Worker {worker_id} message")
            health.set_status(f"worker_{worker_id}", "healthy")
            
            results.append(f"worker_{worker_id}_completed")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Test that all workers completed
        assert len(results) == 5
        for i in range(5):
            assert f"worker_{i}_completed" in results
    
    def test_error_recovery(self, di_container):
        """Test error recovery and resilience."""
        # Test that utilities can recover from errors
        logger = di_container.get_logger("error_recovery_test")
        health = di_container.get_health()
        
        # Test error handling
        try:
            raise ValueError("Test error for recovery")
        except Exception as e:
            error_handler = di_container.get_error_handler()
            error_handler.handle_error(e, "error_recovery_test")
        
        # Test that system continues to work after error
        health.set_status("error_recovery", "healthy")
        logger.info("System recovered from error")
        
        assert health.get_status()["error_recovery"] == "healthy"


class TestDIContainerServiceIntegration:
    """Integration tests for DIContainerService with other platform components."""
    
    def test_integration_with_business_services(self):
        """Test integration with business services."""
        container = DIContainerService("business_test")
        
        # Test that business services can use the DI container
        from backend.business_enablement.protocols.business_service_base import BusinessServiceBase
        
        # This should work without errors
        business_service = BusinessServiceBase(container)
        assert business_service is not None
    
    def test_integration_with_smart_city_services(self):
        """Test integration with smart city services."""
        container = DIContainerService("smart_city_test")
        
        # Test that smart city services can use the DI container
        from backend.smart_city.protocols.smart_city_service_base import SmartCityServiceBase
        
        # This should work without errors
        smart_city_service = SmartCityServiceBase(container)
        assert smart_city_service is not None
    
    def test_integration_with_mcp_servers(self):
        """Test integration with MCP servers."""
        container = DIContainerService("mcp_test")
        
        # Test FastAPI app creation for MCP servers
        app = container.create_fastapi_app("mcp_test_server")
        assert app is not None
        
        # Test that MCP servers can use the DI container
        from foundations.mcp_server.mcp_server_service import MCPServerService
        
        # This should work without errors
        mcp_server = MCPServerService(container)
        assert mcp_server is not None


class TestDIContainerServicePerformance:
    """Performance tests for DIContainerService."""
    
    def test_initialization_performance(self):
        """Test initialization performance."""
        import time
        
        start_time = time.time()
        container = DIContainerService("performance_test")
        end_time = time.time()
        
        # Initialization should be fast (less than 1 second)
        assert (end_time - start_time) < 1.0
        assert container is not None
    
    def test_utility_access_performance(self):
        """Test utility access performance."""
        container = DIContainerService("performance_test")
        
        import time
        
        # Test multiple utility accesses
        start_time = time.time()
        for i in range(100):
            logger = container.get_logger(f"test_{i}")
            health = container.get_health()
            telemetry = container.get_telemetry()
        end_time = time.time()
        
        # Utility access should be fast (less than 0.1 seconds for 100 accesses)
        assert (end_time - start_time) < 0.1
    
    def test_memory_usage(self):
        """Test memory usage of DI container."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        container = DIContainerService("memory_test")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024  # 10MB





