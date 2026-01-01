#!/usr/bin/env python3
"""
Layer 2: Infrastructure Foundation Test Base

Standardized testing patterns and utilities for infrastructure abstractions.
Provides consistent interfaces while maintaining abstraction flexibility.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Type, Union
from abc import ABC, abstractmethod

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

from config.environment_loader import EnvironmentLoader
from config import Environment


class InfrastructureAbstractionTestBase(ABC):
    """
    Base class for infrastructure abstraction tests.
    
    Provides standardized testing patterns while allowing abstraction-specific
    configuration and validation.
    """
    
    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)
    
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
    
    @abstractmethod
    def create_abstraction(self, **kwargs) -> Any:
        """Create the specific abstraction instance for testing."""
        pass
    
    @abstractmethod
    def get_expected_abstraction_name(self) -> str:
        """Get the expected abstraction name."""
        pass
    
    @abstractmethod
    def get_test_config(self) -> Dict[str, Any]:
        """Get test configuration for the abstraction."""
        pass
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get keywords that should appear in expected initialization errors."""
        return ["connection", "infrastructure", "config"]
    
    def get_expected_health_check_error_keywords(self) -> list:
        """Get keywords that should appear in expected health check errors."""
        return ["health", "check", "connection", "infrastructure"]
    
    # Standardized test methods
    @pytest.mark.asyncio
    async def test_abstraction_initialization(self):
        """Test that abstraction initializes correctly."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert abstraction is not None
        assert hasattr(abstraction, 'abstraction_type')
        assert abstraction.abstraction_type == self.get_expected_abstraction_name()
        assert hasattr(abstraction, 'is_connected')
        assert hasattr(abstraction, 'created_at')
    
    @pytest.mark.asyncio
    async def test_abstraction_async_initialization(self):
        """Test that abstraction initializes asynchronously."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        try:
            await abstraction.connect()
            assert abstraction.is_connected is True
        except Exception as e:
            # Connection might fail due to missing infrastructure
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected connection error to contain one of {error_keywords}, got: {str(e)}"
    
    @pytest.mark.asyncio
    async def test_abstraction_status_check(self):
        """Test that status check method exists and can be called."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'get_status')
        assert callable(abstraction.get_status)
        
        try:
            status = abstraction.get_status()
            assert status is not None
            assert isinstance(status, dict)
        except Exception as e:
            # Status check might fail due to missing infrastructure
            error_keywords = self.get_expected_health_check_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected status check error to contain one of {error_keywords}, got: {str(e)}"
    
    @pytest.mark.asyncio
    async def test_abstraction_status_info(self):
        """Test that abstraction status info method works."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'get_status')
        assert callable(abstraction.get_status)
        
        status = abstraction.get_status()
        assert status is not None
        assert isinstance(status, dict)
        assert "type" in status
        assert status["type"] == self.get_expected_abstraction_name()
    
    @pytest.mark.asyncio
    async def test_abstraction_config(self):
        """Test that abstraction configuration is accessible."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'config')
        assert isinstance(abstraction.config, dict)
    
    @pytest.mark.asyncio
    async def test_abstraction_creation_time(self):
        """Test that abstraction creation time is accessible."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'created_at')
        assert abstraction.created_at is not None


class InfrastructureServiceTestBase(ABC):
    """
    Base class for infrastructure service tests.
    
    Provides standardized testing patterns for infrastructure services.
    """
    
    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)
    
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
    
    @abstractmethod
    def create_service(self, utility_foundation, env_loader) -> Any:
        """Create the specific service instance for testing."""
        pass
    
    @abstractmethod
    def get_expected_service_name(self) -> str:
        """Get the expected service name."""
        pass
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get keywords that should appear in expected initialization errors."""
        return ["service", "config", "infrastructure"]
    
    # Standardized test methods
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_utility_foundation, env_loader):
        """Test that service initializes correctly."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert service is not None
        assert hasattr(service, 'service_name')
        assert service.service_name == self.get_expected_service_name()
        assert hasattr(service, 'is_initialized')
        assert hasattr(service, 'logger')
    
    @pytest.mark.asyncio
    async def test_service_async_initialization(self, mock_utility_foundation, env_loader):
        """Test that service initializes asynchronously."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        try:
            await service.initialize()
            assert service.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected initialization error to contain one of {error_keywords}, got: {str(e)}"
    
    @pytest.mark.asyncio
    async def test_service_health_check(self, mock_utility_foundation, env_loader):
        """Test that health check method exists and can be called."""
        service = self.create_service(mock_utility_foundation, env_loader)
        
        assert hasattr(service, 'health_check')
        assert callable(service.health_check)
        
        try:
            health_status = await service.health_check()
            assert health_status is not None
            assert isinstance(health_status, dict)
            assert "service" in health_status
        except Exception as e:
            # Health check might fail due to missing dependencies
            error_keywords = self.get_expected_initialization_error_keywords()
            assert any(keyword in str(e).lower() for keyword in error_keywords), \
                f"Expected health check error to contain one of {error_keywords}, got: {str(e)}"


class InfrastructureAbstractionFactory:
    """
    Factory for creating infrastructure abstractions with standardized patterns.
    
    Provides consistent creation mechanisms while maintaining abstraction flexibility.
    """
    
    @staticmethod
    def create_postgresql_abstraction(config: Dict[str, Any]):
        """Create PostgreSQL abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.postgresql_abstraction import PostgreSQLAbstraction
        
        # Extract parameters from config or use defaults
        host = config.get("host", "localhost")
        port = config.get("port", 5432)
        database = config.get("database", "test")
        user = config.get("user", "test")
        password = config.get("password", "test")
        pool_size = config.get("pool_size", 10)
        max_overflow = config.get("max_overflow", 20)
        
        return PostgreSQLAbstraction(
            host=host, port=port, database=database, user=user, password=password,
            pool_size=pool_size, max_overflow=max_overflow
        )
    
    @staticmethod
    def create_redis_abstraction(config: Dict[str, Any]):
        """Create Redis abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.redis_abstraction import RedisAbstraction
        
        # Extract parameters from config or use defaults
        host = config.get("host", "localhost")
        port = config.get("port", 6379)
        password = config.get("password", "")
        database = config.get("database", 0)
        pool_size = config.get("pool_size", 10)
        max_connections = config.get("max_connections", 50)
        socket_timeout = config.get("socket_timeout", 5)
        socket_connect_timeout = config.get("socket_connect_timeout", 5)
        
        return RedisAbstraction(
            host=host, port=port, password=password, database=database,
            pool_size=pool_size, max_connections=max_connections,
            socket_timeout=socket_timeout, socket_connect_timeout=socket_connect_timeout
        )
    
    @staticmethod
    def create_file_storage_abstraction(config: Dict[str, Any]):
        """Create File Storage abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.file_storage_abstraction import FileStorageAbstraction
        
        storage_root = config.get("storage_root", "/tmp/test_storage")
        return FileStorageAbstraction(storage_root=storage_root)
    
    @staticmethod
    def create_telemetry_abstraction(config: Dict[str, Any]):
        """Create Telemetry abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.telemetry_abstraction import TelemetryAbstraction
        
        service_name = config.get("service_name", "test_service")
        service_version = config.get("service_version", "1.0.0")
        endpoint = config.get("endpoint")
        
        return TelemetryAbstraction(
            service_name=service_name, 
            service_version=service_version, 
            endpoint=endpoint
        )
    
    @staticmethod
    def create_supabase_auth_abstraction(config: Dict[str, Any]):
        """Create Supabase Auth abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.supabase_auth_abstraction import SupabaseAuthAbstraction
        
        supabase_url = config.get("url", "https://test.supabase.co")
        supabase_key = config.get("key", "test_key")
        supabase_service_key = config.get("service_key")
        
        return SupabaseAuthAbstraction(
            supabase_url=supabase_url,
            supabase_anon_key=supabase_key,
            supabase_service_key=supabase_service_key
        )
    
    @staticmethod
    def create_supabase_metadata_abstraction(config: Dict[str, Any]):
        """Create Supabase Metadata abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.supabase_metadata_abstraction import SupabaseMetadataAbstraction
        
        supabase_url = config.get("url", "https://test.supabase.co")
        supabase_key = config.get("key", "test_key")
        multi_tenant_enabled = config.get("multi_tenant_enabled", True)
        
        return SupabaseMetadataAbstraction(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            multi_tenant_enabled=multi_tenant_enabled
        )
    
    @staticmethod
    def create_meilisearch_abstraction(config: Dict[str, Any]):
        """Create Meilisearch abstraction with standardized parameters."""
        from foundations.infrastructure_foundation.abstractions.meilisearch_abstraction import MeilisearchAbstraction
        
        url = config.get("url", "http://localhost:7700")
        api_key = config.get("api_key", "test_key")
        
        return MeilisearchAbstraction({"url": url, "api_key": api_key})


class InfrastructureServiceFactory:
    """
    Factory for creating infrastructure services with standardized patterns.
    """
    
    @staticmethod
    def create_configuration_injection_service(utility_foundation, env_loader):
        """Create Configuration Injection Service."""
        from foundations.infrastructure_foundation.services.infrastructure_configuration_injection_service import InfrastructureConfigurationInjectionService
        
        return InfrastructureConfigurationInjectionService(
            utility_foundation=utility_foundation,
            environment=Environment.TESTING
        )
    
    @staticmethod
    def create_abstraction_creation_service(utility_foundation):
        """Create Abstraction Creation Service."""
        from foundations.infrastructure_foundation.services.infrastructure_abstraction_creation_service import InfrastructureAbstractionCreationService
        
        return InfrastructureAbstractionCreationService(
            utility_foundation=utility_foundation
        )
    
    @staticmethod
    def create_abstraction_access_service(utility_foundation):
        """Create Abstraction Access Service."""
        from foundations.infrastructure_foundation.services.infrastructure_abstraction_access_service import InfrastructureAbstractionAccessService
        
        return InfrastructureAbstractionAccessService(
            utility_foundation=utility_foundation
        )
    
    @staticmethod
    def create_management_service(utility_foundation):
        """Create Management Service."""
        from foundations.infrastructure_foundation.services.infrastructure_management_service import InfrastructureManagementService
        
        return InfrastructureManagementService(
            utility_foundation=utility_foundation
        )
