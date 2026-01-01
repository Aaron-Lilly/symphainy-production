#!/usr/bin/env python3
"""
Layer 1: Configuration Foundation Tests

Tests the real EnvironmentLoader and configuration foundation
using actual implementations without mocking.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

from config.environment_loader import EnvironmentLoader
from config import Environment

class TestEnvironmentLoader:
    """Test real EnvironmentLoader with test configuration."""
    
    def test_environment_loader_initialization(self):
        """Test that EnvironmentLoader can be initialized with test config."""
        loader = EnvironmentLoader(Environment.TESTING)
        assert loader is not None, "EnvironmentLoader should initialize successfully"
    
    def test_environment_loader_config_loading(self):
        """Test that EnvironmentLoader loads test configuration correctly."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test that we can get configuration
        config = loader.get_all_config()
        assert config is not None, "Should be able to get all configuration"
        assert isinstance(config, dict), "Configuration should be a dictionary"
    
    def test_multi_tenant_configuration(self):
        """Test that multi-tenant configuration is loaded correctly."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test multi-tenant configuration
        multi_tenant_config = loader.get_multi_tenant_config()
        assert multi_tenant_config is not None, "Multi-tenant configuration should be available"
        assert isinstance(multi_tenant_config, dict), "Multi-tenant configuration should be a dictionary"
        
        # Test specific multi-tenant settings
        assert "enabled" in multi_tenant_config, "Multi-tenant config should have 'enabled' field"
        assert "default_tenant_type" in multi_tenant_config, "Multi-tenant config should have 'default_tenant_type' field"
        assert "max_tenants_per_user" in multi_tenant_config, "Multi-tenant config should have 'max_tenants_per_user' field"
    
    def test_tenant_configuration(self):
        """Test that tenant-specific configuration works."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test organization tenant config
        org_config = loader.get_tenant_config("organization")
        assert org_config is not None, "Organization tenant config should be available"
        assert "max_users" in org_config, "Tenant config should have 'max_users' field"
        assert "features" in org_config, "Tenant config should have 'features' field"
        assert "type" in org_config, "Tenant config should have 'type' field"
        
        # Test individual tenant config
        individual_config = loader.get_tenant_config("individual")
        assert individual_config is not None, "Individual tenant config should be available"
        assert individual_config["type"] == "individual", "Tenant type should match"
    
    def test_multi_tenant_enabled_check(self):
        """Test that multi-tenant enabled check works."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test multi-tenant enabled check
        is_enabled = loader.is_multi_tenant_enabled()
        assert isinstance(is_enabled, bool), "Multi-tenant enabled check should return boolean"
        assert is_enabled == True, "Multi-tenancy should be enabled in test config"
    
    def test_external_services_config(self):
        """Test that external services configuration is loaded."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test external services configuration
        external_config = loader.get_external_services_config()
        assert external_config is not None, "External services configuration should be available"
        assert isinstance(external_config, dict), "External services configuration should be a dictionary"
        
        # Test specific services
        assert "supabase" in external_config, "Supabase configuration should be available"
        assert "openai" in external_config, "OpenAI configuration should be available"
        assert "anthropic" in external_config, "Anthropic configuration should be available"
        
        # Test Supabase config
        supabase_config = external_config["supabase"]
        assert "url" in supabase_config, "Supabase config should have 'url' field"
        assert "key" in supabase_config, "Supabase config should have 'key' field"
        
        # Test OpenAI config
        openai_config = external_config["openai"]
        assert "api_key" in openai_config, "OpenAI config should have 'api_key' field"
        
        # Test Anthropic config
        anthropic_config = external_config["anthropic"]
        assert "api_key" in anthropic_config, "Anthropic config should have 'api_key' field"
    
    def test_database_config(self):
        """Test that database configuration is loaded."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test database configuration
        db_config = loader.get_database_config()
        assert db_config is not None, "Database configuration should be available"
        assert isinstance(db_config, dict), "Database configuration should be a dictionary"
        
        # Test specific database settings
        assert "url" in db_config, "Database config should have 'url' field"
        assert "pool_size" in db_config, "Database config should have 'pool_size' field"
        assert "max_overflow" in db_config, "Database config should have 'max_overflow' field"
    
    def test_redis_config(self):
        """Test that Redis configuration is loaded."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test Redis configuration
        redis_config = loader.get_redis_config()
        assert redis_config is not None, "Redis configuration should be available"
        assert isinstance(redis_config, dict), "Redis configuration should be a dictionary"
        
        # Test specific Redis settings
        assert "url" in redis_config, "Redis config should have 'url' field"
        assert "password" in redis_config, "Redis config should have 'password' field"
        assert "decode_responses" in redis_config, "Redis config should have 'decode_responses' field"
    
    def test_telemetry_config(self):
        """Test that telemetry configuration is loaded."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test telemetry configuration
        telemetry_config = loader.get_telemetry_config()
        assert telemetry_config is not None, "Telemetry configuration should be available"
        assert isinstance(telemetry_config, dict), "Telemetry configuration should be a dictionary"
        
        # Test specific telemetry settings
        assert "enabled" in telemetry_config, "Telemetry config should have 'enabled' field"
        assert "collection_interval" in telemetry_config, "Telemetry config should have 'collection_interval' field"
        assert "batch_size" in telemetry_config, "Telemetry config should have 'batch_size' field"
    
    def test_security_config(self):
        """Test that security configuration is loaded."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test security configuration
        security_config = loader.get_security_config()
        assert security_config is not None, "Security configuration should be available"
        assert isinstance(security_config, dict), "Security configuration should be a dictionary"
        
        # Test specific security settings
        assert "secret_key" in security_config, "Security config should have 'secret_key' field"
        assert "jwt_secret" in security_config, "Security config should have 'jwt_secret' field"
        assert "jwt_algorithm" in security_config, "Security config should have 'jwt_algorithm' field"
    
    def test_configuration_validation(self):
        """Test that configuration validation works."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test that all required configurations are available
        all_config = loader.get_all_config()
        
        # Test that key configuration sections exist
        assert "multi_tenant" in all_config, "All config should include multi_tenant section"
        assert "external_services" in all_config, "All config should include external_services section"
        assert "database" in all_config, "All config should include database section"
        assert "redis" in all_config, "All config should include redis section"
        assert "security" in all_config, "All config should include security section"
        assert "api" in all_config, "All config should include api section"
    
    def test_configuration_consistency(self):
        """Test that configuration is consistent across different access methods."""
        loader = EnvironmentLoader(Environment.TESTING)
        
        # Test that multi-tenant config is consistent
        multi_tenant_config = loader.get_multi_tenant_config()
        all_config = loader.get_all_config()
        
        assert multi_tenant_config == all_config["multi_tenant"], "Multi-tenant config should be consistent"
        
        # Test that tenant config is consistent
        org_config = loader.get_tenant_config("organization")
        multi_tenant_config = loader.get_multi_tenant_config()
        
        assert org_config["max_users"] == multi_tenant_config["tenant_limits"]["organization"], "Organization tenant config should be consistent"
        assert org_config["features"] == multi_tenant_config["tenant_features"]["organization"], "Organization tenant features should be consistent"
