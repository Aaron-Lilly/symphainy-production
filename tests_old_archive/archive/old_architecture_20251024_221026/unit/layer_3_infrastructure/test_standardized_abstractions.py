#!/usr/bin/env python3
"""
Layer 2: Standardized Infrastructure Abstraction Tests

Tests infrastructure abstractions using standardized patterns while maintaining
abstraction-specific flexibility.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

# Import test base classes
from test_base import InfrastructureAbstractionTestBase, InfrastructureAbstractionFactory
from config.environment_loader import EnvironmentLoader
from config import Environment


class TestPostgreSQLAbstraction(InfrastructureAbstractionTestBase):
    """Test PostgreSQL abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create PostgreSQL abstraction instance."""
        return InfrastructureAbstractionFactory.create_postgresql_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "postgresql"
    
    def get_test_config(self) -> dict:
        """Get test configuration for PostgreSQL."""
        return {
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "user": "test_user",
            "password": "test_password",
            "pool_size": 5,
            "max_overflow": 10
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["connection", "database", "postgresql", "asyncpg", "connect", "refused"]
    
    @pytest.mark.asyncio
    async def test_postgresql_connection_string(self):
        """Test PostgreSQL connection string property."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'connection_string')
        assert abstraction.connection_string is not None
        assert "postgresql://" in abstraction.connection_string


class TestRedisAbstraction(InfrastructureAbstractionTestBase):
    """Test Redis abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create Redis abstraction instance."""
        return InfrastructureAbstractionFactory.create_redis_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "redis"
    
    def get_test_config(self) -> dict:
        """Get test configuration for Redis."""
        return {
            "host": "localhost",
            "port": 6379,
            "password": "",
            "database": 0,
            "pool_size": 5,
            "max_connections": 25,
            "socket_timeout": 5,
            "socket_connect_timeout": 5
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["connection", "redis", "connection", "infrastructure"]
    
    @pytest.mark.asyncio
    async def test_redis_connection_properties(self):
        """Test Redis connection properties."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'host')
        assert abstraction.host == "localhost"
        assert hasattr(abstraction, 'port')
        assert abstraction.port == 6379
        assert hasattr(abstraction, 'database')
        assert abstraction.database == 0


class TestFileStorageAbstraction(InfrastructureAbstractionTestBase):
    """Test File Storage abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create File Storage abstraction instance."""
        return InfrastructureAbstractionFactory.create_file_storage_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "file_storage"
    
    def get_test_config(self) -> dict:
        """Get test configuration for File Storage."""
        return {
            "storage_root": "/tmp/test_storage"
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["storage", "path", "directory", "file"]
    
    @pytest.mark.asyncio
    async def test_file_storage_storage_root(self):
        """Test File Storage storage root property."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'storage_root')
        assert abstraction.storage_root == Path("/tmp/test_storage")


class TestTelemetryAbstraction(InfrastructureAbstractionTestBase):
    """Test Telemetry abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create Telemetry abstraction instance."""
        return InfrastructureAbstractionFactory.create_telemetry_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "telemetry"
    
    def get_test_config(self) -> dict:
        """Get test configuration for Telemetry."""
        return {
            "service_name": "test_service",
            "service_version": "1.0.0",
            "endpoint": "http://localhost:4317"
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["telemetry", "opentelemetry", "tracing", "metrics"]
    
    @pytest.mark.asyncio
    async def test_telemetry_service_info(self):
        """Test Telemetry service information."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'service_name')
        assert abstraction.service_name == "test_service"
        assert hasattr(abstraction, 'service_version')
        assert abstraction.service_version == "1.0.0"


class TestSupabaseAuthAbstraction(InfrastructureAbstractionTestBase):
    """Test Supabase Auth abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create Supabase Auth abstraction instance."""
        return InfrastructureAbstractionFactory.create_supabase_auth_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "supabase_auth"
    
    def get_test_config(self) -> dict:
        """Get test configuration for Supabase Auth."""
        return {
            "url": "https://test.supabase.co",
            "key": "test_anon_key",
            "service_key": "test_service_key"
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["connection", "supabase", "auth", "client"]
    
    @pytest.mark.asyncio
    async def test_supabase_auth_config(self):
        """Test Supabase Auth configuration."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'supabase_url')
        assert abstraction.supabase_url == "https://test.supabase.co"
        assert hasattr(abstraction, 'supabase_anon_key')
        assert abstraction.supabase_anon_key == "test_anon_key"


class TestSupabaseMetadataAbstraction(InfrastructureAbstractionTestBase):
    """Test Supabase Metadata abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create Supabase Metadata abstraction instance."""
        return InfrastructureAbstractionFactory.create_supabase_metadata_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "supabase_metadata"
    
    def get_test_config(self) -> dict:
        """Get test configuration for Supabase Metadata."""
        return {
            "url": "https://test.supabase.co",
            "key": "test_anon_key",
            "multi_tenant_enabled": True
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["connection", "supabase", "metadata", "client"]
    
    @pytest.mark.asyncio
    async def test_supabase_metadata_multi_tenant(self):
        """Test Supabase Metadata multi-tenant configuration."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'multi_tenant_enabled')
        assert abstraction.multi_tenant_enabled is True
    
    @pytest.mark.asyncio
    async def test_supabase_metadata_connection_info(self):
        """Test Supabase Metadata connection info."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        assert hasattr(abstraction, 'get_connection_info')
        assert callable(abstraction.get_connection_info)
        
        connection_info = abstraction.get_connection_info()
        assert connection_info is not None
        assert isinstance(connection_info, dict)
        assert "supabase_url" in connection_info
        assert "multi_tenant_enabled" in connection_info
        assert connection_info["multi_tenant_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_supabase_metadata_tenant_methods(self):
        """Test Supabase Metadata tenant management methods."""
        config = self.get_test_config()
        abstraction = self.create_abstraction(**config)
        
        # Test tenant creation method
        assert hasattr(abstraction, 'create_tenant')
        assert callable(abstraction.create_tenant)
        
        # Test tenant retrieval method
        assert hasattr(abstraction, 'get_tenant')
        assert callable(abstraction.get_tenant)


class TestMeilisearchAbstraction(InfrastructureAbstractionTestBase):
    """Test Meilisearch abstraction using standardized patterns."""
    
    def create_abstraction(self, **kwargs):
        """Create Meilisearch abstraction instance."""
        return InfrastructureAbstractionFactory.create_meilisearch_abstraction(kwargs)
    
    def get_expected_abstraction_name(self) -> str:
        """Get expected abstraction name."""
        return "meilisearch"
    
    def get_test_config(self) -> dict:
        """Get test configuration for Meilisearch."""
        return {
            "url": "http://localhost:7700",
            "api_key": "test_key"
        }
    
    def get_expected_initialization_error_keywords(self) -> list:
        """Get expected initialization error keywords."""
        return ["connection", "meilisearch", "search", "client"]


# Configuration-based tests using real environment
class TestAbstractionConfigurationIntegration:
    """Test abstractions with real configuration from environment."""
    
    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)
    
    @pytest.mark.asyncio
    async def test_postgresql_with_real_config(self, env_loader):
        """Test PostgreSQL abstraction with real configuration."""
        db_config = env_loader.get_database_config()
        abstraction = InfrastructureAbstractionFactory.create_postgresql_abstraction(db_config)
        
        assert abstraction is not None
        assert abstraction.abstraction_name == "postgresql"
        assert hasattr(abstraction, 'connection_string')
    
    @pytest.mark.asyncio
    async def test_redis_with_real_config(self, env_loader):
        """Test Redis abstraction with real configuration."""
        redis_config = env_loader.get_redis_config()
        abstraction = InfrastructureAbstractionFactory.create_redis_abstraction(redis_config)
        
        assert abstraction is not None
        assert abstraction.abstraction_name == "redis"
        assert hasattr(abstraction, 'host')
    
    @pytest.mark.asyncio
    async def test_supabase_with_real_config(self, env_loader):
        """Test Supabase abstractions with real configuration."""
        external_config = env_loader.get_external_services_config()
        supabase_config = external_config["supabase"]
        
        # Test Supabase Auth
        auth_abstraction = InfrastructureAbstractionFactory.create_supabase_auth_abstraction(supabase_config)
        assert auth_abstraction is not None
        assert auth_abstraction.abstraction_name == "supabase_auth"
        
        # Test Supabase Metadata with multi-tenancy
        metadata_config = {**supabase_config, "multi_tenant_enabled": True}
        metadata_abstraction = InfrastructureAbstractionFactory.create_supabase_metadata_abstraction(metadata_config)
        assert metadata_abstraction is not None
        assert metadata_abstraction.abstraction_name == "supabase_metadata"
        assert metadata_abstraction.multi_tenant_enabled is True
    
    @pytest.mark.asyncio
    async def test_telemetry_with_real_config(self, env_loader):
        """Test Telemetry abstraction with real configuration."""
        telemetry_config = env_loader.get_telemetry_config()
        
        # Create telemetry abstraction with service info
        config = {
            "service_name": "test_service",
            "service_version": "1.0.0",
            "endpoint": telemetry_config.get("endpoint")
        }
        abstraction = InfrastructureAbstractionFactory.create_telemetry_abstraction(config)
        
        assert abstraction is not None
        assert abstraction.abstraction_name == "telemetry"
        assert abstraction.service_name == "test_service"
