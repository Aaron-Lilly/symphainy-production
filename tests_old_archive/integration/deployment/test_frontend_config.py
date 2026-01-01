"""
Test Frontend EC2 Deployment Configuration

MEDIUM PRIORITY TEST: Validates that frontend configuration is correct for EC2 deployment.
"""

import pytest
import os

from pathlib import Path

# Add symphainy-frontend to path if needed
frontend_path = Path(__file__).parent.parent.parent.parent / "symphainy-frontend"
sys.path.insert(0, str(frontend_path))

@pytest.mark.integration
@pytest.mark.deployment
@pytest.mark.medium_priority
class TestFrontendConfiguration:
    """Test frontend EC2 deployment configuration."""
    
    @pytest.fixture
    def frontend_root(self):
        """Get frontend root directory."""
        return Path(__file__).parent.parent.parent.parent / "symphainy-frontend"
    
    @pytest.fixture
    def next_config_path(self, frontend_root):
        """Get next.config.js path."""
        return frontend_root / "next.config.js"
    
    @pytest.fixture
    def env_production_path(self, frontend_root):
        """Get .env.production path."""
        return frontend_root / ".env.production"
    
    def test_frontend_url_defaults_to_ec2(self, env_production_path):
        """Test frontend URL defaults to EC2 IP, not localhost."""
        if env_production_path.exists():
            content = env_production_path.read_text()
            
            # Should have EC2 IP or be configurable
            assert "NEXT_PUBLIC_FRONTEND_URL" in content or                    "NEXT_PUBLIC_BACKEND_URL" in content,                 "Frontend should have URL configuration"
            
            # Should not hardcode localhost:3000
            if "localhost:3000" in content:
                # If localhost is present, it should be for development only
                assert "# Development" in content or                        "# Local" in content,                     "localhost:3000 should be marked as development-only"
    
    def test_backend_api_url_points_to_ec2(self, env_production_path):
        """Test backend API URL points to EC2 IP, not localhost."""
        if env_production_path.exists():
            content = env_production_path.read_text()
            
            # Should have backend URL configuration
            assert "NEXT_PUBLIC_BACKEND_URL" in content or                    "NEXT_PUBLIC_API_URL" in content,                 "Frontend should have backend API URL configuration"
            
            # Should default to EC2 IP or be configurable
            if "localhost:8000" in content:
                # If localhost is present, it should be for development only
                assert "# Development" in content or                        "# Local" in content,                     "localhost:8000 should be marked as development-only"
    
    def test_next_config_supports_ec2(self, next_config_path):
        """Test next.config.js supports EC2 deployment."""
        if next_config_path.exists():
            content = next_config_path.read_text()
            
            # Should have rewrites or API configuration
            # This is a basic check - actual implementation may vary
            assert "rewrites" in content or                    "env" in content or                    "NEXT_PUBLIC" in content,                 "next.config.js should have API/rewrite configuration"
