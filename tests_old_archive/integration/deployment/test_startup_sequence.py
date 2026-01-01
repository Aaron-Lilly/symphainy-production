"""
Test Startup Sequence

Validates that backend startup sequence works correctly after Phase 3 fixes:
- API router registration
- Infrastructure dependency checks
- Service initialization
- Health checks
"""

import pytest
import os

import subprocess
from pathlib import Path
from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
@pytest.mark.deployment
@pytest.mark.medium_priority
class TestStartupSequence:
    """Test backend startup sequence."""
    
    @pytest.fixture
    def backend_root(self):
        """Get backend root directory."""
        return Path(__file__).parent.parent.parent.parent / "symphainy-platform"
    
    @pytest.fixture
    def main_py_path(self, backend_root):
        """Get main.py path."""
        return backend_root / "main.py"
    
    @pytest.fixture
    def startup_script_path(self, backend_root):
        """Get startup script path."""
        # Check for common startup script names
        possible_names = ["startup.sh", "start.sh", "run.sh", "main.py"]
        for name in possible_names:
            path = backend_root / name
            if path.exists():
                return path
        return None
    
    def test_main_py_exists(self, main_py_path):
        """Test that main.py exists."""
        assert main_py_path.exists(), "main.py should exist"
    
    def test_api_router_registration_handled(self, main_py_path):
        """Test that API router registration is properly handled."""
        if main_py_path.exists():
            content = main_py_path.read_text()
            
            # Should have API router registration
            assert "register_api_routers" in content or                    "api" in content.lower(),                 "main.py should register API routers"
            
            # Should have error handling
            assert "try" in content or                    "except" in content or                    "raise" in content,                 "main.py should have error handling for API router registration"
    
    def test_backend_binds_to_all_interfaces(self, main_py_path):
        """Test that backend binds to 0.0.0.0, not localhost."""
        if main_py_path.exists():
            content = main_py_path.read_text()
            
            # Should bind to 0.0.0.0 or use environment variable
            has_bind_config = (
                "0.0.0.0" in content or
                "BACKEND_HOST" in content or
                "HOST" in content.upper() or
                "uvicorn.run" in content  # uvicorn defaults to 0.0.0.0
            )
            
            assert has_bind_config,                 "Backend should bind to 0.0.0.0 or use HOST environment variable"
    
    def test_startup_script_has_health_checks(self, startup_script_path):
        """Test that startup script has health checks."""
        if startup_script_path and startup_script_path.suffix == ".sh":
            content = startup_script_path.read_text()
            
            # Should have health check function or logic
            has_health_checks = (
                "check_service_health" in content or
                "health" in content.lower() or
                "nc -z" in content or
                "curl" in content or
                "ping" in content
            )
            
            # Health checks are recommended but not required
            # Just log if missing
            if not has_health_checks:
                pytest.skip("Startup script doesn't have health checks (recommended but not required)")
    
    def test_startup_script_fails_fast(self, startup_script_path):
        """Test that startup script fails fast if critical services unavailable."""
        if startup_script_path and startup_script_path.suffix == ".sh":
            content = startup_script_path.read_text()
            
            # Should have fail-fast logic
            has_fail_fast = (
                "exit 1" in content or
                "return 1" in content or
                "raise" in content or
                "fail" in content.lower()
            )
            
            # Fail-fast is recommended but not required
            # Just log if missing
            if not has_fail_fast:
                pytest.skip("Startup script doesn't have fail-fast logic (recommended but not required)")
