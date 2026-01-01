#!/usr/bin/env python3
"""
Layer 0: Poetry Dependencies & Environment Tests

Tests the real Poetry dependencies and environment configuration
using actual implementations without mocking.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../symphainy-source/symphainy-platform'))

class TestPoetryDependencies:
    """Test Poetry dependencies and environment setup."""
    
    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and is readable."""
        pyproject_path = Path(__file__).parent / "../../../symphainy-source/symphainy-platform/pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml should exist"
        
        # Test that we can read the file
        content = pyproject_path.read_text()
        assert "symphainy" in content, "pyproject.toml should contain project name"
        assert "[tool.poetry]" in content, "pyproject.toml should contain poetry configuration"
    
    def test_multi_tenant_dependencies(self):
        """Test that multi-tenant dependencies are included."""
        pyproject_path = Path(__file__).parent / "../../../symphainy-source/symphainy-platform/pyproject.toml"
        content = pyproject_path.read_text()
        
        # Check for multi-tenant specific dependencies
        assert "redis" in content, "Redis should be included for tenant caching"
        assert "supabase" in content, "Supabase should be included for multi-tenancy"
        assert "cryptography" in content, "Cryptography should be included for security"
        assert "PyJWT" in content, "PyJWT should be included for JWT handling"
    
    def test_development_dependencies(self):
        """Test that development dependencies are included."""
        pyproject_path = Path(__file__).parent / "../../../symphainy-source/symphainy-platform/pyproject.toml"
        content = pyproject_path.read_text()
        
        # Check for testing dependencies
        assert "pytest" in content, "pytest should be included for testing"
        assert "pytest-asyncio" in content, "pytest-asyncio should be included for async testing"
        assert "pytest-cov" in content, "pytest-cov should be included for coverage"
    
    def test_environment_variables_accessible(self):
        """Test that environment variables are accessible."""
        # Test that we can access environment variables
        assert "PATH" in os.environ, "PATH environment variable should be accessible"
        
        # Test that we can set and get environment variables
        test_var = "SYMPHAINY_TEST_VAR"
        test_value = "test_value_123"
        
        os.environ[test_var] = test_value
        assert os.environ[test_var] == test_value, "Should be able to set and get environment variables"
        
        # Cleanup
        del os.environ[test_var]
    
    def test_python_path_setup(self):
        """Test that Python path is set up correctly for imports."""
        # Test that we can import from the platform
        try:
            from config.environment_loader import EnvironmentLoader
            assert EnvironmentLoader is not None, "Should be able to import EnvironmentLoader"
        except ImportError as e:
            pytest.fail(f"Should be able to import from platform: {e}")
    
    def test_configuration_files_exist(self):
        """Test that configuration files exist."""
        config_dir = Path(__file__).parent / "../../../symphainy-source/symphainy-platform/config"
        
        # Test that config directory exists
        assert config_dir.exists(), "Config directory should exist"
        
        # Test that key config files exist
        test_env_path = config_dir / "test.env"
        development_env_path = config_dir / "development.env"
        
        assert test_env_path.exists(), "test.env should exist"
        assert development_env_path.exists(), "development.env should exist"
    
    def test_configuration_files_readable(self):
        """Test that configuration files are readable."""
        config_dir = Path(__file__).parent / "../../../symphainy-source/symphainy-platform/config"
        test_env_path = config_dir / "test.env"
        
        # Test that we can read the test configuration
        content = test_env_path.read_text()
        assert "MULTI_TENANT_ENABLED" in content, "test.env should contain multi-tenant configuration"
        assert "SUPABASE_URL" in content, "test.env should contain Supabase configuration"
        assert "REDIS_URL" in content, "test.env should contain Redis configuration"
    
    def test_platform_structure_exists(self):
        """Test that platform directory structure exists."""
        platform_dir = Path(__file__).parent / "../../../symphainy-source/symphainy-platform"
        
        # Test that key directories exist
        assert (platform_dir / "config").exists(), "config directory should exist"
        assert (platform_dir / "foundations").exists(), "foundations directory should exist"
        assert (platform_dir / "backend").exists(), "backend directory should exist"
        
        # Test that key foundation directories exist
        foundations_dir = platform_dir / "foundations"
        assert (foundations_dir / "configuration_foundation").exists(), "configuration_foundation should exist"
        assert (foundations_dir / "infrastructure_foundation").exists(), "infrastructure_foundation should exist"
        assert (foundations_dir / "utility_foundation").exists(), "utility_foundation should exist"
        assert (foundations_dir / "public_works_foundation").exists(), "public_works_foundation should exist"
        assert (foundations_dir / "curator_foundation").exists(), "curator_foundation should exist"
    
    def test_smart_city_structure_exists(self):
        """Test that smart city directory structure exists."""
        backend_dir = Path(__file__).parent / "../../../symphainy-source/symphainy-platform/backend"
        
        # Test that smart city directories exist
        assert (backend_dir / "smart_city").exists(), "smart_city directory should exist"
        
        smart_city_dir = backend_dir / "smart_city"
        assert (smart_city_dir / "protocols").exists(), "smart_city/protocols should exist"
        assert (smart_city_dir / "interfaces").exists(), "smart_city/interfaces should exist"
        assert (smart_city_dir / "services").exists(), "smart_city/services should exist"
    
    def test_multi_tenant_files_exist(self):
        """Test that multi-tenant implementation files exist."""
        platform_dir = Path(__file__).parent / "../../../symphainy-source/symphainy-platform"
        
        # Test that multi-tenant files exist
        tenant_utility_path = platform_dir / "foundations/utility_foundation/utilities/tenant/tenant_management_utility.py"
        assert tenant_utility_path.exists(), "tenant_management_utility.py should exist"
        
        multi_tenant_protocol_path = platform_dir / "backend/smart_city/protocols/multi_tenant_protocol.py"
        assert multi_tenant_protocol_path.exists(), "multi_tenant_protocol.py should exist"
        
        multi_tenant_interface_path = platform_dir / "backend/smart_city/interfaces/multi_tenant_interface.py"
        assert multi_tenant_interface_path.exists(), "multi_tenant_interface.py should exist"
        
        security_guard_path = platform_dir / "backend/smart_city/services/security_guard/security_guard_service.py"
        assert security_guard_path.exists(), "security_guard_service.py should exist"
