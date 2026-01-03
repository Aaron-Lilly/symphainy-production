"""
Pytest plugin to ensure Python path is set before test collection.

This plugin runs very early in pytest's lifecycle to ensure the symphainy-platform
directory is in sys.path before any test files are imported.

This is a fallback for pytest.ini's pythonpath setting, which may not work
reliably depending on where pytest is run from.
"""
import sys
from pathlib import Path

def pytest_configure(config):
    """
    Configure pytest - ensure Python path is set before test collection.
    
    This hook runs early enough that it can set up sys.path before pytest
    starts importing test files.
    """
    # Get the tests directory (where pytest.ini is located)
    # config.rootdir is the directory containing pytest.ini (resolved to absolute path)
    tests_dir = Path(config.rootdir)
    platform_dir = tests_dir.parent / "symphainy-platform"
    
    if platform_dir.exists():
        platform_dir_str = str(platform_dir.resolve())
        if platform_dir_str not in sys.path:
            sys.path.insert(0, platform_dir_str)

