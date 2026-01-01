#!/usr/bin/env python3
"""
Production Configuration Validation Tests

Validates that production configuration files exist and have required variables.
Catches missing configuration before deployment.

Run: pytest tests/config/test_production_config_validation.py -v
"""

import pytest
import os
from pathlib import Path
from typing import Dict, Set
import re


@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    # Tests run from tests/ directory, so go up one level
    return Path(__file__).parent.parent.parent


@pytest.fixture
def platform_root(project_root) -> Path:
    """Get symphainy-platform root directory."""
    return project_root / "symphainy-platform"


def parse_env_file(file_path: Path) -> Dict[str, str]:
    """
    Parse .env file and return dict of key-value pairs.
    Handles comments, empty lines, and variable substitution syntax.
    """
    config = {}
    if not file_path.exists():
        return config
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Handle variable substitution syntax like ${VAR:-default}
            # For validation, we just check the key exists, not the resolved value
            if '=' in line:
                # Split on first = only
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove variable substitution syntax for validation
                # ${VAR:-default} -> just check VAR exists
                if value.startswith('${') and ':-' in value:
                    # Extract the variable name
                    match = re.match(r'\$\{([^:]+)', value)
                    if match:
                        # The key itself is what we're checking
                        config[key] = value  # Keep original for reference
                    else:
                        config[key] = value
                else:
                    config[key] = value
    
    return config


class TestProductionConfigValidation:
    """Tests for production configuration validation."""
    
    def test_production_env_file_exists(self, platform_root):
        """Test that production.env file exists."""
        config_file = platform_root / "config" / "production.env"
        assert config_file.exists(), \
            f"❌ Production config file missing: {config_file}\n" \
            f"   Expected location: symphainy-platform/config/production.env"
    
    def test_production_env_example_exists(self, platform_root):
        """Test that production.env.example template exists."""
        example_file = platform_root / "config" / "production.env.example"
        assert example_file.exists(), \
            f"❌ Production config example missing: {example_file}\n" \
            f"   This template should exist for deployment reference"
    
    def test_production_config_has_required_vars(self, platform_root):
        """Test that production config has all required environment variables."""
        config_file = platform_root / "config" / "production.env"
        
        if not config_file.exists():
            pytest.skip("Production config file not found (may be in .gitignore)")
        
        config = parse_env_file(config_file)
        
        # Required variables for production (from PLATFORM_STARTUP.md)
        required_vars = {
            "ENVIRONMENT",  # Must be set to "production"
            "API_HOST",     # API server host
            "API_PORT",     # API server port
            "DATABASE_HOST",  # Database connection
            "REDIS_HOST",   # Redis connection
            "ARANGO_URL",   # ArangoDB connection
            "CONSUL_HOST",  # Consul service discovery
        }
        
        # Check required vars exist
        missing = required_vars - set(config.keys())
        assert not missing, \
            f"❌ Missing required config vars in production.env: {missing}\n" \
            f"   These variables are required for the platform to start"
        
        print(f"✅ All required config variables present: {required_vars}")
    
    def test_production_config_critical_vars_not_empty(self, platform_root):
        """Test that critical config vars are not empty."""
        config_file = platform_root / "config" / "production.env"
        
        if not config_file.exists():
            pytest.skip("Production config file not found")
        
        config = parse_env_file(config_file)
        
        # Critical vars that must have non-empty values
        critical_vars = {
            "ENVIRONMENT": "production",  # Must be exactly "production"
            "API_PORT": None,  # Must be a number, but can be from ${VAR:-default}
        }
        
        # Check ENVIRONMENT is set to production
        if "ENVIRONMENT" in config:
            env_value = config["ENVIRONMENT"]
            # Handle variable substitution
            if env_value.startswith("${"):
                # Variable substitution - check if it resolves
                pass  # Can't validate substituted values without runtime
            else:
                assert env_value.lower() == "production", \
                    f"❌ ENVIRONMENT must be 'production', got: {env_value}"
        
        # Check API_PORT exists (can be from ${VAR:-default})
        assert "API_PORT" in config, \
            "❌ API_PORT must be defined in production config"
        
        print(f"✅ Critical config variables validated")
    
    def test_production_config_has_database_config(self, platform_root):
        """Test that production config has database configuration."""
        config_file = platform_root / "config" / "production.env"
        
        if not config_file.exists():
            pytest.skip("Production config file not found")
        
        config = parse_env_file(config_file)
        
        # Database config vars
        db_vars = {
            "DATABASE_HOST",
            "DATABASE_PORT",
            "DATABASE_NAME",
        }
        
        missing = db_vars - set(config.keys())
        assert not missing, \
            f"❌ Missing database config vars: {missing}\n" \
            f"   Database configuration is required for production"
        
        print(f"✅ Database configuration present")
    
    def test_production_config_has_redis_config(self, platform_root):
        """Test that production config has Redis configuration."""
        config_file = platform_root / "config" / "production.env"
        
        if not config_file.exists():
            pytest.skip("Production config file not found")
        
        config = parse_env_file(config_file)
        
        # Redis config vars
        redis_vars = {
            "REDIS_HOST",
            "REDIS_PORT",
        }
        
        missing = redis_vars - set(config.keys())
        assert not missing, \
            f"❌ Missing Redis config vars: {missing}\n" \
            f"   Redis configuration is required for production"
        
        print(f"✅ Redis configuration present")
    
    def test_production_config_has_api_config(self, platform_root):
        """Test that production config has API server configuration."""
        config_file = platform_root / "config" / "production.env"
        
        if not config_file.exists():
            pytest.skip("Production config file not found")
        
        config = parse_env_file(config_file)
        
        # API config vars
        api_vars = {
            "API_HOST",
            "API_PORT",
            "API_CORS_ORIGINS",
        }
        
        missing = api_vars - set(config.keys())
        assert not missing, \
            f"❌ Missing API config vars: {missing}\n" \
            f"   API server configuration is required for production"
        
        print(f"✅ API server configuration present")
    
    def test_secrets_template_exists(self, platform_root):
        """Test that secrets template exists (for deployment reference)."""
        # Check for secrets.example or .env.secrets.example
        possible_templates = [
            platform_root / "config" / "secrets.example",
            platform_root / ".env.secrets.example",
            platform_root / "config" / ".env.secrets.example",
        ]
        
        template_exists = any(template.exists() for template in possible_templates)
        
        assert template_exists, \
            f"❌ Secrets template not found. Expected one of:\n" \
            f"   - {possible_templates[0]}\n" \
            f"   - {possible_templates[1]}\n" \
            f"   - {possible_templates[2]}\n" \
            f"   This template is needed for deployment documentation"
        
        # Find which one exists
        existing_template = next((t for t in possible_templates if t.exists()), None)
        print(f"✅ Secrets template found: {existing_template}")
    
    def test_production_config_no_debug_mode(self, platform_root):
        """Test that production config has debug mode disabled."""
        config_file = platform_root / "config" / "production.env"
        
        if not config_file.exists():
            pytest.skip("Production config file not found")
        
        config = parse_env_file(config_file)
        
        # Check debug-related settings are disabled
        debug_vars = {
            "API_DEBUG": "false",
            "DEBUG_MODE": "false",
            "VERBOSE_LOGGING": "false",
            "HOT_RELOAD": "false",
        }
        
        for var, expected_value in debug_vars.items():
            if var in config:
                value = config[var].lower()
                # Handle variable substitution
                if not value.startswith("${"):
                    assert value == expected_value.lower(), \
                        f"❌ {var} should be '{expected_value}' in production, got: {config[var]}"
        
        print(f"✅ Production debug settings validated (debug mode disabled)")




