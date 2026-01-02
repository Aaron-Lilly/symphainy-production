"""
Common test helpers and utilities.

Provides reusable test patterns and helper functions for all test categories.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Callable, Awaitable
from pathlib import Path
import json


def assert_dict_contains(expected: Dict[str, Any], actual: Dict[str, Any], path: str = ""):
    """
    Assert that actual dict contains all keys and values from expected dict.
    
    Args:
        expected: Dictionary with expected keys/values
        actual: Dictionary to check
        path: Current path in nested dict (for error messages)
    """
    for key, expected_value in expected.items():
        full_path = f"{path}.{key}" if path else key
        
        assert key in actual, f"Missing key: {full_path}"
        
        if isinstance(expected_value, dict):
            assert isinstance(actual[key], dict), f"Expected dict at {full_path}, got {type(actual[key])}"
            assert_dict_contains(expected_value, actual[key], full_path)
        else:
            assert actual[key] == expected_value, f"Mismatch at {full_path}: expected {expected_value}, got {actual[key]}"


def assert_no_placeholders(data: Any, path: str = ""):
    """
    Assert that data contains no placeholder values.
    
    Args:
        data: Data to check (dict, list, str, etc.)
        path: Current path in nested structure (for error messages)
    """
    placeholder_keywords = ["placeholder", "todo", "fixme", "xxx", "tbd", "mock", "stub"]
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_path = f"{path}.{key}" if path else key
            assert_no_placeholders(value, full_path)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            full_path = f"{path}[{i}]" if path else f"[{i}]"
            assert_no_placeholders(item, full_path)
    elif isinstance(data, str):
        data_lower = data.lower()
        for keyword in placeholder_keywords:
            assert keyword not in data_lower, f"Found placeholder keyword '{keyword}' at {path}: {data[:100]}"


async def wait_for_condition(
    condition: Callable[[], Awaitable[bool] | bool],
    timeout: float = 5.0,
    interval: float = 0.1,
    error_message: Optional[str] = None,
) -> bool:
    """
    Wait for a condition to become true.
    
    Args:
        condition: Function that returns True when condition is met
        timeout: Maximum time to wait (seconds)
        interval: Check interval (seconds)
        error_message: Custom error message if timeout
    
    Returns:
        True if condition met, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if asyncio.iscoroutinefunction(condition):
            result = await condition()
        else:
            result = condition()
        
        if result:
            return True
        
        await asyncio.sleep(interval)
    
    if error_message:
        raise TimeoutError(error_message)
    return False


def load_test_data(filename: str) -> Dict[str, Any]:
    """
    Load test data from JSON file.
    
    Args:
        filename: Name of test data file (in tests/data/)
    
    Returns:
        Loaded test data
    """
    data_path = Path(__file__).parent.parent / "data" / filename
    if not data_path.exists():
        raise FileNotFoundError(f"Test data file not found: {data_path}")
    
    with open(data_path, "r") as f:
        return json.load(f)


def create_test_file(filename: str, content: bytes, directory: Optional[Path] = None) -> Path:
    """
    Create a temporary test file.
    
    Args:
        filename: Name of file to create
        content: File content
        directory: Directory to create file in (default: tests/tmp/)
    
    Returns:
        Path to created file
    """
    if directory is None:
        directory = Path(__file__).parent.parent / "tmp"
    
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path


def cleanup_test_file(file_path: Path):
    """Remove a test file."""
    if file_path.exists():
        file_path.unlink()


class TestTimer:
    """Context manager for timing test execution."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time




