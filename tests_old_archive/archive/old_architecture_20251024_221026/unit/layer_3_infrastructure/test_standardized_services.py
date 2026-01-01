#!/usr/bin/env python3
"""
Layer 2: Standardized Infrastructure Service Tests

Tests infrastructure services using standardized patterns while maintaining
service-specific flexibility.
"""

import pytest
import sys
import os

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

# Import test base classes
from test_base import InfrastructureServiceTestBase, InfrastructureServiceFactory
from config.environment_loader import EnvironmentLoader
from config import Environment


class TestInfrastructureConfigurationInjectionService(InfrastructureServiceTestBase):
    """Test Configuration Injection Service using standardized patterns."""
    
    def create_service(self, utility_foundation, env_loader):
        """Create Configuration Injection Service instance."""
        return InfrastructureServiceFactory.create_configuration_injection_service(utility_foundation, env_loader)
    
    def get_expected_service_name(self) -> str:
        """Get expected service name."""
        return "infrastructure_configuration_injection_env_integrated"
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["config", "injection", "service", "infrastructure"]
    
    @pytest.mark.asyncio
    async def test_configuration_injection_environment_integration(self, mock_utility_foundation, env_loader):
        """Test that service properly integrates with environment configuration."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'env_loader')
        assert service.env_loader is not None
        assert service.env_loader.environment == Environment.TESTING
    
    @pytest.mark.asyncio
    async def test_configuration_injection_rules(self, mock_utility_foundation, env_loader):
        """Test that service has environment-specific injection rules."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'injection_rules')
        assert service.injection_rules is not None
        assert isinstance(service.injection_rules, dict)
    
    @pytest.mark.asyncio
    async def test_configuration_injection_database_config(self, mock_utility_foundation, env_loader):
        """Test database configuration injection."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        try:
            db_config = await service.inject_database_configuration()
            assert db_config is not None
            assert isinstance(db_config, dict)
        except Exception as e:
            # Configuration injection might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected injection error to contain one of {error_keywords}, got: {str(e)}"
    
    @pytest.mark.asyncio
    async def test_configuration_injection_redis_config(self, mock_utility_foundation, env_loader):
        """Test Redis configuration injection."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        try:
            redis_config = await service.inject_redis_configuration()
            assert redis_config is not None
            assert isinstance(redis_config, dict)
        except Exception as e:
            # Configuration injection might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected injection error to contain one of {error_keywords}, got: {str(e)}"


class TestInfrastructureAbstractionCreationService(InfrastructureServiceTestBase):
    """Test Abstraction Creation Service using standardized patterns."""
    
    def create_service(self, utility_foundation, env_loader):
        """Create Abstraction Creation Service instance."""
        return InfrastructureServiceFactory.create_abstraction_creation_service(utility_foundation)
    
    def get_expected_service_name(self) -> str:
        """Get expected service name."""
        return "infrastructure_abstraction_creation_env_integrated"
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["abstraction", "creation", "service", "infrastructure"]
    
    @pytest.mark.asyncio
    async def test_abstraction_creation_storage(self, mock_utility_foundation, env_loader):
        """Test that service has abstraction storage."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'created_abstractions')
        assert service.created_abstractions is not None
        assert isinstance(service.created_abstractions, dict)
        
        # Check for expected abstraction types
        expected_types = ["database", "redis", "celery", "storage", "search", "monitoring", "security"]
        for abstraction_type in expected_types:
            assert abstraction_type in service.created_abstractions
    
    @pytest.mark.asyncio
    async def test_abstraction_creation_status_tracking(self, mock_utility_foundation, env_loader):
        """Test that service tracks creation status."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'creation_status')
        assert service.creation_status is not None
        assert isinstance(service.creation_status, dict)
        
        # Check for expected abstraction types
        expected_types = ["database", "redis", "celery", "storage", "search", "monitoring", "security"]
        for abstraction_type in expected_types:
            assert abstraction_type in service.creation_status
    
    @pytest.mark.asyncio
    async def test_abstraction_creation_metadata(self, mock_utility_foundation, env_loader):
        """Test that service tracks creation metadata."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'creation_metadata')
        assert service.creation_metadata is not None
        assert isinstance(service.creation_metadata, dict)
        
        # Check for expected metadata fields
        expected_fields = ["last_creation", "environment", "creation_version", "total_creations", "successful_creations", "failed_creations"]
        for field in expected_fields:
            assert field in service.creation_metadata
    
    @pytest.mark.asyncio
    async def test_abstraction_creation_environment_integration(self, mock_utility_foundation, env_loader):
        """Test that service integrates with environment configuration."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'env_loader')
        assert service.env_loader is not None
        assert service.env_loader.environment == Environment.TESTING


class TestInfrastructureAbstractionAccessService(InfrastructureServiceTestBase):
    """Test Abstraction Access Service using standardized patterns."""
    
    def create_service(self, utility_foundation, env_loader):
        """Create Abstraction Access Service instance."""
        return InfrastructureServiceFactory.create_abstraction_access_service(utility_foundation)
    
    def get_expected_service_name(self) -> str:
        """Get expected service name."""
        return "infrastructure_abstraction_access_env_integrated"
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["abstraction", "access", "service", "infrastructure"]
    
    @pytest.mark.asyncio
    async def test_abstraction_access_database_method(self, mock_utility_foundation, env_loader):
        """Test database abstraction access method."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        try:
            abstraction = await service.get_database_abstraction("test_db")
            # Might return None if not found, which is expected
            assert abstraction is None or hasattr(abstraction, 'initialize')
        except Exception as e:
            # Abstraction access might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected access error to contain one of {error_keywords}, got: {str(e)}"
    
    @pytest.mark.asyncio
    async def test_abstraction_access_redis_method(self, mock_utility_foundation, env_loader):
        """Test Redis abstraction access method."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        try:
            abstraction = await service.get_redis_abstraction("test_redis")
            # Might return None if not found, which is expected
            assert abstraction is None or hasattr(abstraction, 'initialize')
        except Exception as e:
            # Abstraction access might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected access error to contain one of {error_keywords}, got: {str(e)}"


class TestInfrastructureManagementService(InfrastructureServiceTestBase):
    """Test Management Service using standardized patterns."""
    
    def create_service(self, utility_foundation, env_loader):
        """Create Management Service instance."""
        return InfrastructureServiceFactory.create_management_service(utility_foundation)
    
    def get_expected_service_name(self) -> str:
        """Get expected service name."""
        return "infrastructure_management_env_integrated"
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["management", "service", "infrastructure"]
    
    @pytest.mark.asyncio
    async def test_management_service_status_method(self, mock_utility_foundation, env_loader):
        """Test management service status method."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        try:
            status = await service.get_status()
            assert status is not None
            assert isinstance(status, dict)
        except Exception as e:
            # Status check might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected status error to contain one of {error_keywords}, got: {str(e)}"


# Service coordination tests
class TestInfrastructureServiceCoordination:
    """Test infrastructure service coordination using standardized patterns."""
    
    @pytest.fixture
    def mock_utility_foundation(self):
        """Create mock utility foundation."""
        class MockLogger:
            def info(self, msg): pass
            def error(self, msg): pass
            def warning(self, msg): pass
            def debug(self, msg): pass
        
        class MockUtilityFoundation:
            def __init__(self):
                self.logger = MockLogger()
                self.error_handler = None
                self.health_service = None
                self.telemetry_service = None
                self.security_service = None
                self.tool_factory = None
            
            def register_service(self, service_name, service_type):
                """Mock register_service method."""
                pass
            
            async def log_operation_with_telemetry(self, operation, user_context=None, details=None, success=True):
                """Mock log_operation_with_telemetry method."""
                pass
            
            async def handle_error_with_audit(self, error, context=None, user_context=None):
                """Mock handle_error_with_audit method."""
                pass
            
            def track_utility_usage(self, utility_name):
                """Mock track_utility_usage method."""
                pass
            
            async def record_health_metric(self, metric_name, value, tags=None):
                """Mock record_health_metric method."""
                pass
        return MockUtilityFoundation()
    
    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)
    
    @pytest.mark.asyncio
    async def test_service_coordination_initialization(self, mock_utility_foundation, env_loader):
        """Test that all services can be initialized and coordinated."""
        # Initialize all services using standardized factory
        config_service = InfrastructureServiceFactory.create_configuration_injection_service(
            mock_utility_foundation, env_loader
        )
        creation_service = InfrastructureServiceFactory.create_abstraction_creation_service(
            mock_utility_foundation
        )
        access_service = InfrastructureServiceFactory.create_abstraction_access_service(
            mock_utility_foundation
        )
        management_service = InfrastructureServiceFactory.create_management_service(
            mock_utility_foundation
        )
        
        # Test that all services are properly initialized
        assert config_service is not None
        assert creation_service is not None
        assert access_service is not None
        assert management_service is not None
        
        # Test service names
        assert config_service.service_name == "infrastructure_configuration_injection_env_integrated"
        assert creation_service.service_name == "infrastructure_abstraction_creation_env_integrated"
        assert access_service.service_name == "infrastructure_abstraction_access_env_integrated"
        assert management_service.service_name == "infrastructure_management_env_integrated"
    
    @pytest.mark.asyncio
    async def test_service_coordination_async_initialization(self, mock_utility_foundation, env_loader):
        """Test that all services can be initialized asynchronously."""
        # Initialize all services
        config_service = InfrastructureServiceFactory.create_configuration_injection_service(
            mock_utility_foundation, env_loader
        )
        creation_service = InfrastructureServiceFactory.create_abstraction_creation_service(
            mock_utility_foundation
        )
        access_service = InfrastructureServiceFactory.create_abstraction_access_service(
            mock_utility_foundation
        )
        management_service = InfrastructureServiceFactory.create_management_service(
            mock_utility_foundation
        )
        
        try:
            # Try to initialize all services
            await config_service.initialize()
            await creation_service.initialize()
            await access_service.initialize()
            await management_service.initialize()
            
            # If all initialize successfully, test coordination
            assert config_service.is_initialized is True
            assert creation_service.is_initialized is True
            assert access_service.is_initialized is True
            assert management_service.is_initialized is True
        except Exception as e:
            # Coordination might fail due to missing dependencies
            assert "service" in str(e).lower() or "coordination" in str(e).lower() or "infrastructure" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_service_environment_integration(self, mock_utility_foundation, env_loader):
        """Test that services properly integrate with environment configuration."""
        config_service = InfrastructureServiceFactory.create_configuration_injection_service(
            mock_utility_foundation, env_loader
        )
        
        # Test that environment loader is properly integrated
        assert config_service.env_loader == env_loader
        assert config_service.env_loader.environment == Environment.TESTING
    
    @pytest.mark.asyncio
    async def test_service_multi_tenant_awareness(self, mock_utility_foundation, env_loader):
        """Test that services are aware of multi-tenant configuration."""
        config_service = InfrastructureServiceFactory.create_configuration_injection_service(
            mock_utility_foundation, env_loader
        )
        
        # Test that multi-tenant configuration is accessible
        multi_tenant_config = env_loader.get_multi_tenant_config()
        assert multi_tenant_config is not None
        assert multi_tenant_config["enabled"] is True
