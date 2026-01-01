#!/usr/bin/env python3
"""
Path Utilities - Absolute Path Management

Provides utilities for consistent absolute path handling across the platform.
All paths are resolved to absolute paths to avoid confusion and path calculation errors.

WHAT (Utility Role): I provide consistent absolute path resolution
HOW (Utility Implementation): I use Path.resolve() to ensure all paths are absolute
"""

from pathlib import Path
from typing import Optional
import os

# Cache for project root to avoid repeated calculations
_PROJECT_ROOT_CACHE: Optional[Path] = None

def get_project_root() -> Path:
    """
    Get the absolute path to the symphainy-platform project root.
    
    This function finds the project root by looking for the 'foundations' directory,
    which is a core platform directory that should always exist at the project root.
    
    Returns:
        Path: Absolute path to the symphainy-platform directory
        
    Raises:
        RuntimeError: If project root cannot be determined
    """
    global _PROJECT_ROOT_CACHE
    
    if _PROJECT_ROOT_CACHE is not None:
        return _PROJECT_ROOT_CACHE
    
    # Strategy 1: Check if we're in the project root (has 'foundations' directory)
    current = Path.cwd().resolve()
    if (current / "foundations").exists() and (current / "main.py").exists():
        _PROJECT_ROOT_CACHE = current
        return _PROJECT_ROOT_CACHE
    
    # Strategy 2: Walk up from current file location
    # This file is at: symphainy-platform/utilities/path_utils.py
    # Project root is: symphainy-platform/
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent  # utilities -> symphainy-platform
    
    if (project_root / "foundations").exists() and (project_root / "main.py").exists():
        _PROJECT_ROOT_CACHE = project_root
        return _PROJECT_ROOT_CACHE
    
    # Strategy 3: Check environment variable
    env_root = os.getenv("SYMPHAINY_PLATFORM_ROOT")
    if env_root:
        project_root = Path(env_root).resolve()
        if (project_root / "foundations").exists():
            _PROJECT_ROOT_CACHE = project_root
            return _PROJECT_ROOT_CACHE
    
    # Strategy 4: BREAKING - Hard-coded paths removed
    # ❌ REMOVED: Path("/home/founders/demoversion/symphainy_source/symphainy-platform")
    # Only use environment variable or current working directory
    # common_paths = [
    #     Path("/home/founders/demoversion/symphainy_source/symphainy-platform"),  # ❌ REMOVED
    #     Path.home() / "symphainy-platform",
    # ]
    
    # Only try user home directory (no hard-coded paths)
    home_path = Path.home() / "symphainy-platform"
    if home_path.exists() and (home_path / "foundations").exists():
        _PROJECT_ROOT_CACHE = home_path.resolve()
        return _PROJECT_ROOT_CACHE
    
    raise RuntimeError(
        "Could not determine project root. "
        "Please ensure you're running from the symphainy-platform directory, "
        "or set SYMPHAINY_PLATFORM_ROOT environment variable. "
        "Hard-coded paths have been removed for Option C compatibility."
    )


def get_config_root() -> Path:
    """
    Get the absolute path to the config root directory.
    
    Config root is the same as project root for this platform.
    
    Returns:
        Path: Absolute path to the config root (project root)
    """
    return get_project_root()


def resolve_path(path: str | Path) -> Path:
    """
    Resolve a path to an absolute path.
    
    Args:
        path: Relative or absolute path string or Path object
        
    Returns:
        Path: Absolute resolved path
    """
    return Path(path).resolve()


def get_config_file_path(filename: str) -> Path:
    """
    Get absolute path to a config file.
    
    Args:
        filename: Name of config file (e.g., ".env.secrets", "config/development.env")
        
    Returns:
        Path: Absolute path to the config file
    """
    config_root = get_config_root()
    return (config_root / filename).resolve()


def ensure_absolute_path(path: str | Path, base: Optional[Path] = None) -> Path:
    """
    Ensure a path is absolute, resolving relative to base if provided.
    
    Args:
        path: Path to resolve
        base: Base directory for relative paths (defaults to project root)
        
    Returns:
        Path: Absolute resolved path
    """
    path_obj = Path(path)
    
    if path_obj.is_absolute():
        return path_obj.resolve()
    
    if base is None:
        base = get_project_root()
    
    return (base / path_obj).resolve()

