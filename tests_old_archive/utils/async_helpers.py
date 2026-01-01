#!/usr/bin/env python3
"""
Async Test Helpers

Provides utilities for async testing patterns.
"""

import asyncio
from typing import Any, Callable, List, Optional
from functools import wraps


def async_timeout(timeout: float = 5.0):
    """
    Decorator to add timeout to async test functions.
    
    Args:
        timeout: Timeout in seconds
    
    Example:
        @async_timeout(10.0)
        async def test_something():
            await long_running_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=timeout
            )
        return wrapper
    return decorator


async def gather_with_errors(*coros):
    """
    Run coroutines in parallel and collect results/errors.
    
    Args:
        *coros: Coroutines to run
    
    Returns:
        Tuple of (results, errors)
    """
    results = []
    errors = []
    
    async def run_with_catch(coro):
        try:
            result = await coro
            results.append(result)
        except Exception as e:
            errors.append(e)
            results.append(None)
    
    await asyncio.gather(*[run_with_catch(coro) for coro in coros])
    
    return results, errors


async def retry_async_operation(
    operation: Callable,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry an async operation with exponential backoff.
    
    Args:
        operation: Async operation to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
        exceptions: Exceptions to catch and retry
    
    Returns:
        Operation result
    
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                raise last_exception
    
    raise last_exception


async def wait_for_service_ready(
    check_function: Callable,
    timeout: float = 30.0,
    interval: float = 0.5
) -> bool:
    """
    Wait for a service to become ready.
    
    Args:
        check_function: Async function that returns True when ready
        timeout: Maximum time to wait
        interval: Check interval
    
    Returns:
        True when service is ready
    
    Raises:
        TimeoutError if service doesn't become ready
    """
    start_time = asyncio.get_event_loop().time()
    
    while True:
        try:
            if await check_function():
                return True
        except Exception:
            pass  # Ignore errors during readiness check
        
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            raise TimeoutError(f"Service not ready after {timeout}s")
        
        await asyncio.sleep(interval)


class AsyncContextManager:
    """Helper for async context management in tests."""
    
    def __init__(self, setup_func: Callable, teardown_func: Callable):
        """
        Initialize async context manager.
        
        Args:
            setup_func: Async setup function
            teardown_func: Async teardown function
        """
        self.setup_func = setup_func
        self.teardown_func = teardown_func
        self.setup_result = None
    
    async def __aenter__(self):
        """Enter async context."""
        self.setup_result = await self.setup_func()
        return self.setup_result
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.teardown_func()


def create_async_context(setup_func: Callable, teardown_func: Callable):
    """
    Create an async context manager for test setup/teardown.
    
    Args:
        setup_func: Async setup function
        teardown_func: Async teardown function
    
    Returns:
        AsyncContextManager instance
    
    Example:
        async with create_async_context(setup_service, cleanup_service):
            # Test code here
            pass
    """
    return AsyncContextManager(setup_func, teardown_func)



