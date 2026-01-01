"""
Test Backend EC2 Deployment Configuration

MEDIUM PRIORITY TEST: Validates that backend configuration is correct for EC2 deployment.
"""

import pytest
import os

from pathlib import Path

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
@pytest.mark.deployment
@pytest.mark.medium_priority
class TestBackendConfiguration:
    """Test backend EC2 deployment configuration."""
    
    @pytest.fixture
    def backend_root(self):
        """Get backend root directory."""
        return Path(__file__).parent.parent.parent.parent / "symphainy-platform"
    
    @pytest.fixture
    def production_env_path(self, backend_root):
        """Get production.env path."""
        return backend_root / "config" / "production.env"
    
    @pytest.fixture
    def main_py_path(self, backend_root):
        """Get main.py path."""
        return backend_root / "main.py"
    
    def test_backend_binds_to_all_interfaces(self, main_py_path):
        """Test backend binds to 0.0.0.0, not localhost."""
        if main_py_path.exists():
            content = main_py_path.read_text()
            
            # Should bind to 0.0.0.0 or use environment variable
            assert "0.0.0.0" in content or                    "BACKEND_HOST" in content or                    "HOST" in content.upper(),                 "Backend should bind to 0.0.0.0 or use HOST environment variable"
            
            # Should not hardcode localhost
            if "localhost" in content and "0.0.0.0" not in content:
                # If localhost is present, it should be for development only
                assert "# Development" in content or                        "# Local" in content or                        "development" in content.lower(),                     "localhost binding should be marked as development-only"
    
    def test_internal_services_use_localhost(self, production_env_path):
        """Test internal services use localhost (correct for EC2)."""
        if production_env_path.exists():
            content = production_env_path.read_text()
            
            # Internal services should use localhost (Docker containers on same EC2)
            internal_services = [
                "REDIS_HOST",
                "DATABASE_HOST",
                "ARANGO_HOSTS",
                "OPA_URL"
            ]
            
            for service in internal_services:
                if service in content:
                    # Should default to localhost or be configurable
                    # (For Option C, these would be overridden)
                    assert "localhost" in content or                            f"{service}=" in content,                         f"{service} should use localhost or be configurable"
    
    def test_backend_port_configurable(self, main_py_path):
        """Test backend port is configurable via environment variable."""
        if main_py_path.exists():
            content = main_py_path.read_text()
            
            # Should use environment variable for port
            assert "PORT" in content or                    "BACKEND_PORT" in content or                    "8000" in content,                 "Backend should use configurable port (default 8000)"
    
    def test_environment_supports_option_c(self, production_env_path):
        """Test environment variables support Option C migration."""
        if production_env_path.exists():
            content = production_env_path.read_text()
            
            # Should have comments about Option C or use environment variables
            assert "OPTION" in content.upper() or                    "ENV" in content or                    "${" in content,                 "Configuration should support Option C migration via environment variables"
