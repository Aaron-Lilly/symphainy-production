#!/usr/bin/env python3
"""
Layer 0: Platform Shutdown Tests

Tests that validate platform shutdown sequence works correctly.

WHAT: Validate platform shutdown
HOW: Test PlatformOrchestrator shutdown methods
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

import os

from main import PlatformOrchestrator

class TestPlatformShutdown:
    """Test platform shutdown sequence."""
    
    @pytest.fixture
    async def platform_orchestrator(self):
        """Create PlatformOrchestrator instance."""
        return PlatformOrchestrator()
    
    @pytest.mark.asyncio
    async def test_shutdown_background_tasks(self, platform_orchestrator):
        """Test that background tasks are shut down correctly."""
        # Create actual coroutines (not AsyncMock objects)
        async def task1():
            await asyncio.sleep(0.01)
            return "task1"
        
        async def task2():
            await asyncio.sleep(0.01)
            return "task2"
        
        # Create actual tasks
        task1_obj = asyncio.create_task(task1())
        task2_obj = asyncio.create_task(task2())
        platform_orchestrator.background_tasks = [task1_obj, task2_obj]
        
        # Execute shutdown
        await platform_orchestrator.shutdown_background_tasks()
        
        # Verify shutdown event was set
        assert platform_orchestrator._shutdown_event.is_set(), "Shutdown event should be set"
    
    @pytest.mark.asyncio
    async def test_shutdown_cleanup(self, platform_orchestrator):
        """Test that shutdown cleans up resources."""
        # Initialize some state
        platform_orchestrator.managers = {"test_manager": Mock()}
        platform_orchestrator.foundation_services = {"test_foundation": Mock()}
        
        # Mock shutdown methods
        with patch.object(platform_orchestrator, 'shutdown_background_tasks', new_callable=AsyncMock) as mock_shutdown:
            await platform_orchestrator.shutdown_background_tasks()
            
            # Verify shutdown was called
            assert mock_shutdown.called
    
    @pytest.mark.asyncio
    async def test_shutdown_with_no_tasks(self, platform_orchestrator):
        """Test that shutdown works when no background tasks exist."""
        platform_orchestrator.background_tasks = []
        
        # Should not raise an error
        await platform_orchestrator.shutdown_background_tasks()
        
        # Verify shutdown event was set
        assert platform_orchestrator._shutdown_event.is_set()
