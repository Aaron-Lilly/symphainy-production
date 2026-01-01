#!/usr/bin/env python3
"""
Test Utilities

Utility functions for SymphAIny platform testing.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json

class TestUtilities:
    """Test utility functions."""
    
    @staticmethod
    def create_solution_context(business_outcome: str, client_context: str) -> Dict[str, Any]:
        """Create solution context for testing."""
        return {
            "business_outcome": business_outcome,
            "solution_type": "mvp",
            "client_context": client_context,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_user_context(tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Create user context for testing."""
        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "role": "executive",
            "permissions": ["read", "write", "execute"]
        }
    
    @staticmethod
    def create_mock_response(success: bool = True, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create mock response for testing."""
        return {
            "success": success,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def wait_for_async_operation(operation, timeout: float = 30.0) -> Any:
        """Wait for async operation to complete."""
        try:
            return await asyncio.wait_for(operation, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
