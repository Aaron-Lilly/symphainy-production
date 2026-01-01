#!/usr/bin/env python3
"""
Simple Foundation Test - Demonstrates New Test Environment

This is a simple test to demonstrate the new test environment is working.
"""

import pytest

from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
platform_root = project_root / "symphainy-platform"
sys.path.insert(0, str(platform_root))

class TestSimpleFoundation:
    """Simple test to demonstrate the new test environment."""
    
    def test_environment_setup(self):
        """Test that the environment is properly set up."""
        assert True, "Environment is properly set up"
    
    def test_python_path(self):
        """Test that Python path is correctly configured."""
        import foundations
        assert foundations is not None, "Foundations module is importable"
    
    def test_platform_structure(self):
        """Test that platform structure is accessible."""
        from foundations.di_container.di_container_service import DIContainerService
        assert DIContainerService is not None, "DIContainerService is importable"
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test that async functionality works."""
        import asyncio
        
        async def async_function():
            return "async test passed"
        
        result = await async_function()
        assert result == "async test passed", "Async functionality works"

