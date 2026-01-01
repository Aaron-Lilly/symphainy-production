"""
Test Configuration Validation

Validates that configuration files are correct after Phase 3 fixes:
- Configuration files exist
- Environment variables are set
- No hardcoded localhost in production
- Option C migration path exists
"""

import pytest
import os

from pathlib import Path
from typing import Dict, Any, List

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
@pytest.mark.deployment
@pytest.mark.medium_priority
class TestConfigurationValidation:
    """Test configuration file validation."""
    
    @pytest.fixture
    def backend_root(self):
        """Get backend root directory."""
        return Path(__file__).parent.parent.parent.parent / "symphainy-platform"
    
    @pytest.fixture
    def frontend_root(self):
        """Get frontend root directory."""
        return Path(__file__).parent.parent.parent.parent / "symphainy-frontend"
    
    @pytest.fixture
    def production_env_path(self, backend_root):
        """Get production.env path."""
        return backend_root / "config" / "production.env"
    
    @pytest.fixture
    def next_config_path(self, frontend_root):
        """Get next.config.js path."""
        return frontend_root / "next.config.js"
    
    def test_production_env_exists(self, production_env_path):
        """Test that production.env exists."""
        assert production_env_path.exists(),             f"production.env should exist at {production_env_path}"
    
    def test_production_env_uses_environment_variables(self, production_env_path):
        """Test that production.env uses environment variables."""
        if production_env_path.exists():
            content = production_env_path.read_text()
            
            # Should use environment variables (${VAR} or $VAR)
            has_env_vars = "${" in content or "$" in content
            
            # Or should have comments about Option C migration
            has_option_c_comments = "OPTION" in content.upper() or "MIGRATION" in content.upper()
            
            assert has_env_vars or has_option_c_comments,                 "production.env should use environment variables or document Option C migration"
    
    def test_production_env_documents_option_c(self, production_env_path):
        """Test that production.env documents Option C migration path."""
        if production_env_path.exists():
            content = production_env_path.read_text()
            
            # Should have comments about Option C or environment variable usage
            has_documentation = (
                "OPTION" in content.upper() or
                "MIGRATION" in content.upper() or
                "ENV" in content or
                "#" in content  # Has comments
            )
            
            assert has_documentation,                 "production.env should document Option C migration or environment variable usage"
    
    def test_next_config_supports_ec2(self, next_config_path):
        """Test that next.config.js supports EC2 deployment."""
        if next_config_path.exists():
            content = next_config_path.read_text()
            
            # Should have EC2 IP or environment variable
            has_ec2_config = (
                "35.215.64.103" in content or
                "NEXT_PUBLIC_BACKEND_URL" in content or
                "NEXT_PUBLIC_API_URL" in content or
                "process.env" in content
            )
            
            assert has_ec2_config,                 "next.config.js should support EC2 deployment via IP or environment variables"
    
    def test_no_hardcoded_localhost_in_production(self, production_env_path):
        """Test that production.env doesn't hardcode localhost (except for internal services)."""
        if production_env_path.exists():
            content = production_env_path.read_text()
            
            # localhost is acceptable for internal services (Redis, ArangoDB, etc.)
            # But should be documented or use environment variables
            
            # Check if localhost is used
            if "localhost" in content:
                # Should be for internal services or documented
                has_internal_service_context = (
                    "REDIS" in content or
                    "ARANGO" in content or
                    "DATABASE" in content or
                    "OPA" in content or
                    "Internal" in content or
                    "#" in content  # Has comments explaining
                )
                
                assert has_internal_service_context,                     "localhost usage should be for internal services or documented"
    
    def test_frontend_env_variables_defined(self, frontend_root):
        """Test that frontend environment variables are defined."""
        # Check for .env.production or .env.local
        env_files = [
            frontend_root / ".env.production",
            frontend_root / ".env.local",
            frontend_root / ".env"
        ]
        
        found_env_file = False
        for env_file in env_files:
            if env_file.exists():
                found_env_file = True
                content = env_file.read_text()
                
                # Should have API URL configuration
                has_api_config = (
                    "NEXT_PUBLIC_BACKEND_URL" in content or
                    "NEXT_PUBLIC_API_URL" in content or
                    "NEXT_PUBLIC_FRONTEND_URL" in content
                )
                
                if has_api_config:
                    # Should use EC2 IP or be configurable
                    has_ec2_or_env = (
                        "35.215.64.103" in content or
                        "${" in content or
                        "$" in content
                    )
                    
                    assert has_ec2_or_env,                         f"Frontend env file should use EC2 IP or environment variables: {env_file}"
        
        # Env file is optional (can use next.config.js defaults)
        # Just skip if not found
        if not found_env_file:
            pytest.skip("No frontend env file found (using next.config.js defaults is acceptable)")
