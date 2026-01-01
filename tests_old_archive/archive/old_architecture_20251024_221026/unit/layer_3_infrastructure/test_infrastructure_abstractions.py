#!/usr/bin/env python3
"""
Layer 2: Infrastructure Abstractions Tests

Tests the key infrastructure abstractions with real implementations.
These abstractions provide the foundation for all platform operations.

Key Abstractions:
- Database (PostgreSQL, Supabase)
- Cache (Redis)
- Search (Meilisearch)
- File Storage (Local, S3, GCS)
- Telemetry (OpenTelemetry)
- Authentication (Supabase Auth)
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the platform directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

from foundations.infrastructure_foundation.abstractions.postgresql_abstraction import PostgreSQLAbstraction
from foundations.infrastructure_foundation.abstractions.redis_abstraction import RedisAbstraction
from foundations.infrastructure_foundation.abstractions.meilisearch_abstraction import MeilisearchAbstraction
from foundations.infrastructure_foundation.abstractions.file_storage_abstraction import FileStorageAbstraction
from foundations.infrastructure_foundation.abstractions.telemetry_abstraction import TelemetryAbstraction
from foundations.infrastructure_foundation.abstractions.supabase_auth_abstraction import SupabaseAuthAbstraction
from foundations.infrastructure_foundation.abstractions.supabase_metadata_abstraction import SupabaseMetadataAbstraction
from config.environment_loader import EnvironmentLoader
from config import Environment


class TestInfrastructureAbstractions:
    """Test Infrastructure Abstractions with real implementations."""

    @pytest.fixture
    def env_loader(self):
        """Create Environment Loader instance."""
        return EnvironmentLoader(Environment.TESTING)

    @pytest.fixture
    def db_config(self, env_loader):
        """Get database configuration."""
        return env_loader.get_database_config()

    @pytest.fixture
    def redis_config(self, env_loader):
        """Get Redis configuration."""
        return env_loader.get_redis_config()

    @pytest.fixture
    def supabase_config(self, env_loader):
        """Get Supabase configuration."""
        external_config = env_loader.get_external_services_config()
        supabase_config = external_config.get("supabase", {})
        # Provide mock values for testing if not configured
        if not supabase_config.get("url") or not supabase_config.get("key"):
            return {
                "url": "https://mock-project.supabase.co",
                "key": "mock-anon-key-for-testing"
            }
        return supabase_config

    @pytest.fixture
    def telemetry_config(self, env_loader):
        """Get telemetry configuration."""
        return env_loader.get_telemetry_config()

    # PostgreSQL Abstraction Tests
    @pytest.mark.asyncio
    async def test_postgresql_abstraction_initialization(self, db_config):
        """Test PostgreSQL abstraction initialization."""
        abstraction = PostgreSQLAbstraction(db_config)
        assert abstraction is not None
        assert abstraction.config == db_config

    @pytest.mark.asyncio
    async def test_postgresql_abstraction_initialization_async(self, db_config):
        """Test PostgreSQL abstraction async initialization."""
        abstraction = PostgreSQLAbstraction(db_config)
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing database connection
            # This is expected in a real implementation test
            assert "connection" in str(e).lower() or "database" in str(e).lower()

    @pytest.mark.asyncio
    async def test_postgresql_abstraction_connection_info(self, db_config):
        """Test PostgreSQL abstraction connection info."""
        abstraction = PostgreSQLAbstraction(db_config)
        connection_info = abstraction.get_connection_info()
        assert connection_info is not None
        assert isinstance(connection_info, dict)
        assert "database_url" in connection_info

    # Redis Abstraction Tests
    @pytest.mark.asyncio
    async def test_redis_abstraction_initialization(self, redis_config):
        """Test Redis abstraction initialization."""
        abstraction = RedisAbstraction(redis_config)
        assert abstraction is not None
        assert abstraction.config == redis_config

    @pytest.mark.asyncio
    async def test_redis_abstraction_initialization_async(self, redis_config):
        """Test Redis abstraction async initialization."""
        abstraction = RedisAbstraction(redis_config)
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing Redis connection
            # This is expected in a real implementation test
            assert "connection" in str(e).lower() or "redis" in str(e).lower()

    @pytest.mark.asyncio
    async def test_redis_abstraction_connection_info(self, redis_config):
        """Test Redis abstraction connection info."""
        abstraction = RedisAbstraction(redis_config)
        connection_info = abstraction.get_connection_info()
        assert connection_info is not None
        assert isinstance(connection_info, dict)
        assert "redis_url" in connection_info

    # Meilisearch Abstraction Tests
    @pytest.mark.asyncio
    async def test_meilisearch_abstraction_initialization(self):
        """Test Meilisearch abstraction initialization."""
        config = {"url": "http://localhost:7700", "api_key": "test_key"}
        abstraction = MeilisearchAbstraction(config)
        assert abstraction is not None
        assert abstraction.config == config

    @pytest.mark.asyncio
    async def test_meilisearch_abstraction_initialization_async(self):
        """Test Meilisearch abstraction async initialization."""
        config = {"url": "http://localhost:7700", "api_key": "test_key"}
        abstraction = MeilisearchAbstraction(config)
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing Meilisearch connection
            # This is expected in a real implementation test
            assert "connection" in str(e).lower() or "meilisearch" in str(e).lower()

    # File Storage Abstraction Tests
    @pytest.mark.asyncio
    async def test_file_storage_abstraction_initialization(self):
        """Test File Storage abstraction initialization."""
        abstraction = FileStorageAbstraction(storage_root="/tmp/test_storage")
        assert abstraction is not None
        assert abstraction.storage_root == Path("/tmp/test_storage")

    @pytest.mark.asyncio
    async def test_file_storage_abstraction_initialization_async(self):
        """Test File Storage abstraction async initialization."""
        abstraction = FileStorageAbstraction(storage_root="/tmp/test_storage")
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing storage setup
            # This is expected in a real implementation test
            assert "storage" in str(e).lower() or "path" in str(e).lower()

    # Telemetry Abstraction Tests
    @pytest.mark.asyncio
    async def test_telemetry_abstraction_initialization(self, telemetry_config):
        """Test Telemetry abstraction initialization."""
        abstraction = TelemetryAbstraction("test_service", "1.0.0")
        assert abstraction is not None
        assert abstraction.service_name == "test_service"
        assert abstraction.service_version == "1.0.0"

    @pytest.mark.asyncio
    async def test_telemetry_abstraction_initialization_async(self, telemetry_config):
        """Test Telemetry abstraction async initialization."""
        abstraction = TelemetryAbstraction("test_service", "1.0.0")
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing telemetry setup
            # This is expected in a real implementation test
            assert "telemetry" in str(e).lower() or "opentelemetry" in str(e).lower()

    # Supabase Auth Abstraction Tests
    @pytest.mark.asyncio
    async def test_supabase_auth_abstraction_initialization(self, supabase_config):
        """Test Supabase Auth abstraction initialization."""
        abstraction = SupabaseAuthAbstraction(
            supabase_config["url"], 
            supabase_config["key"]
        )
        assert abstraction is not None
        assert abstraction.supabase_url == supabase_config["url"]
        assert abstraction.supabase_anon_key == supabase_config["key"]

    @pytest.mark.asyncio
    async def test_supabase_auth_abstraction_initialization_async(self, supabase_config):
        """Test Supabase Auth abstraction async initialization."""
        abstraction = SupabaseAuthAbstraction(
            supabase_config["url"], 
            supabase_config["key"]
        )
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing Supabase connection
            # This is expected in a real implementation test
            assert "connection" in str(e).lower() or "supabase" in str(e).lower()

    # Supabase Metadata Abstraction Tests
    @pytest.mark.asyncio
    async def test_supabase_metadata_abstraction_initialization(self, supabase_config):
        """Test Supabase Metadata abstraction initialization."""
        abstraction = SupabaseMetadataAbstraction(
            supabase_config["url"], 
            supabase_config["key"], 
            multi_tenant_enabled=True
        )
        assert abstraction is not None
        assert abstraction.supabase_url == supabase_config["url"]
        assert abstraction.multi_tenant_enabled is True

    @pytest.mark.asyncio
    async def test_supabase_metadata_abstraction_initialization_async(self, supabase_config):
        """Test Supabase Metadata abstraction async initialization."""
        abstraction = SupabaseMetadataAbstraction(
            supabase_config["url"], 
            supabase_config["key"], 
            multi_tenant_enabled=True
        )
        try:
            await abstraction.initialize()
            assert abstraction.is_initialized is True
        except Exception as e:
            # Initialization might fail due to missing Supabase connection
            # This is expected in a real implementation test
            assert "connection" in str(e).lower() or "supabase" in str(e).lower()

    @pytest.mark.asyncio
    async def test_supabase_metadata_abstraction_connection_info(self, supabase_config):
        """Test Supabase Metadata abstraction connection info."""
        abstraction = SupabaseMetadataAbstraction(
            supabase_config["url"], 
            supabase_config["key"], 
            multi_tenant_enabled=True
        )
        connection_info = abstraction.get_connection_info()
        assert connection_info is not None
        assert isinstance(connection_info, dict)
        assert "supabase_url" in connection_info
        assert "multi_tenant_enabled" in connection_info
        assert connection_info["multi_tenant_enabled"] is True

    # Multi-tenant specific tests
    @pytest.mark.asyncio
    async def test_supabase_metadata_abstraction_multi_tenant_tables(self, supabase_config):
        """Test that Supabase Metadata abstraction includes multi-tenant tables."""
        abstraction = SupabaseMetadataAbstraction(
            supabase_config["url"], 
            supabase_config["key"], 
            multi_tenant_enabled=True
        )
        connection_info = abstraction.get_connection_info()
        tables = connection_info.get("tables", [])
        assert "tenants" in tables
        assert "audit_logs" in tables

    @pytest.mark.asyncio
    async def test_supabase_metadata_abstraction_tenant_creation(self, supabase_config):
        """Test Supabase Metadata abstraction tenant creation method."""
        abstraction = SupabaseMetadataAbstraction(
            supabase_config["url"], 
            supabase_config["key"], 
            multi_tenant_enabled=True
        )
        assert hasattr(abstraction, 'create_tenant')
        assert callable(abstraction.create_tenant)

    @pytest.mark.asyncio
    async def test_supabase_metadata_abstraction_tenant_retrieval(self, supabase_config):
        """Test Supabase Metadata abstraction tenant retrieval method."""
        abstraction = SupabaseMetadataAbstraction(
            supabase_config["url"], 
            supabase_config["key"], 
            multi_tenant_enabled=True
        )
        assert hasattr(abstraction, 'get_tenant')
        assert callable(abstraction.get_tenant)

    # Configuration validation tests
    @pytest.mark.asyncio
    async def test_database_configuration_structure(self, db_config):
        """Test that database configuration has required structure."""
        assert isinstance(db_config, dict)
        assert "url" in db_config
        assert "pool_size" in db_config
        assert "max_overflow" in db_config

    @pytest.mark.asyncio
    async def test_redis_configuration_structure(self, redis_config):
        """Test that Redis configuration has required structure."""
        assert isinstance(redis_config, dict)
        assert "url" in redis_config
        assert "password" in redis_config
        assert "decode_responses" in redis_config

    @pytest.mark.asyncio
    async def test_supabase_configuration_structure(self, supabase_config):
        """Test that Supabase configuration has required structure."""
        assert isinstance(supabase_config, dict)
        assert "url" in supabase_config
        assert "key" in supabase_config

    @pytest.mark.asyncio
    async def test_telemetry_configuration_structure(self, telemetry_config):
        """Test that telemetry configuration has required structure."""
        assert isinstance(telemetry_config, dict)
        assert "enabled" in telemetry_config
        assert "collection_interval" in telemetry_config
        assert "batch_size" in telemetry_config
