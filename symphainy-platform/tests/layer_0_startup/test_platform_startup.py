#!/usr/bin/env python3
"""
Layer 0: Platform Startup Tests

Tests that validate the platform can actually start successfully.

WHAT: Validate platform startup
HOW: Test actual platform startup, verify all foundations initialize

This is the foundational layer - if the platform can't start, nothing else matters.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Import platform components
from main import PlatformOrchestrator, app_state


class TestPlatformStartup:
    """Test platform startup."""
    
    @pytest.fixture
    def platform_orchestrator(self):
        """Create Platform Orchestrator instance."""
        # PlatformOrchestrator only needs logging, which is already available
        return PlatformOrchestrator()
    
    @pytest.mark.asyncio
    async def test_platform_orchestrator_initializes(self, platform_orchestrator):
        """Test that Platform Orchestrator can be initialized."""
        assert platform_orchestrator is not None
        assert hasattr(platform_orchestrator, 'orchestrate_platform_startup')
        assert hasattr(platform_orchestrator, 'get_platform_status')
        assert hasattr(platform_orchestrator, 'startup_status')
        assert hasattr(platform_orchestrator, 'foundation_services')
    
    @pytest.mark.asyncio
    async def test_platform_startup_sequence_exists(self, platform_orchestrator):
        """Test that platform startup sequence methods exist."""
        assert hasattr(platform_orchestrator, '_initialize_foundation_infrastructure')
        assert hasattr(platform_orchestrator, '_initialize_smart_city_gateway')
        assert hasattr(platform_orchestrator, '_start_background_watchers')
        assert hasattr(platform_orchestrator, '_start_curator_autodiscovery')
    
    @pytest.mark.asyncio
    async def test_platform_startup_returns_success(self, platform_orchestrator):
        """Test that platform startup returns success result."""
        # Mock the initialization methods
        platform_orchestrator._initialize_foundation_infrastructure = AsyncMock()
        platform_orchestrator._initialize_smart_city_gateway = AsyncMock()
        platform_orchestrator._start_background_watchers = AsyncMock()
        platform_orchestrator._start_curator_autodiscovery = AsyncMock()
        
        # Set startup status
        platform_orchestrator.startup_status = {
            "foundation": "completed",
            "smart_city_gateway": "completed",
            "lazy_hydration": "ready"
        }
        platform_orchestrator.startup_sequence = [
            "foundation_infrastructure",
            "smart_city_gateway",
            "lazy_realm_hydration"
        ]
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        result = await platform_orchestrator.orchestrate_platform_startup()
        
        assert result is not None
        assert result.get('success') is True
        assert 'startup_sequence' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_platform_startup_initializes_foundations(self, platform_orchestrator):
        """Test that platform startup initializes foundations."""
        # Mock the initialization methods
        platform_orchestrator._initialize_foundation_infrastructure = AsyncMock()
        platform_orchestrator._initialize_smart_city_gateway = AsyncMock()
        platform_orchestrator._start_background_watchers = AsyncMock()
        platform_orchestrator._start_curator_autodiscovery = AsyncMock()
        
        # Set startup status
        platform_orchestrator.startup_status = {
            "foundation": "completed",
            "smart_city_gateway": "completed",
            "lazy_hydration": "ready"
        }
        platform_orchestrator.startup_sequence = []
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        await platform_orchestrator.orchestrate_platform_startup()
        
        # Verify initialization methods were called
        platform_orchestrator._initialize_foundation_infrastructure.assert_called_once()
        platform_orchestrator._initialize_smart_city_gateway.assert_called_once()
        platform_orchestrator._start_background_watchers.assert_called_once()
        platform_orchestrator._start_curator_autodiscovery.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_platform_startup_tracks_sequence(self, platform_orchestrator):
        """Test that platform startup tracks the startup sequence."""
        # Mock the initialization methods
        platform_orchestrator._initialize_foundation_infrastructure = AsyncMock()
        platform_orchestrator._initialize_smart_city_gateway = AsyncMock()
        platform_orchestrator._start_background_watchers = AsyncMock()
        platform_orchestrator._start_curator_autodiscovery = AsyncMock()
        
        # Set startup status
        platform_orchestrator.startup_status = {
            "foundation": "completed",
            "smart_city_gateway": "completed",
            "lazy_hydration": "ready"
        }
        platform_orchestrator.startup_sequence = []
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        result = await platform_orchestrator.orchestrate_platform_startup()
        
        assert 'startup_sequence' in result
        assert isinstance(result['startup_sequence'], list)
        assert len(result['startup_sequence']) > 0
    
    @pytest.mark.asyncio
    async def test_platform_startup_handles_errors(self, platform_orchestrator):
        """Test that platform startup handles errors gracefully."""
        # Mock the initialization methods to raise an error
        platform_orchestrator._initialize_foundation_infrastructure = AsyncMock(side_effect=Exception("Test error"))
        platform_orchestrator._initialize_smart_city_gateway = AsyncMock()
        platform_orchestrator._start_background_watchers = AsyncMock()
        platform_orchestrator._start_curator_autodiscovery = AsyncMock()
        
        platform_orchestrator.startup_status = {}
        platform_orchestrator.startup_sequence = []
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        # Should raise exception
        with pytest.raises(Exception):
            await platform_orchestrator.orchestrate_platform_startup()
    
    @pytest.mark.asyncio
    async def test_platform_status_endpoint_exists(self, platform_orchestrator):
        """Test that platform status endpoint method exists."""
        assert hasattr(platform_orchestrator, 'get_platform_status')
        assert callable(platform_orchestrator.get_platform_status)
    
    @pytest.mark.asyncio
    async def test_platform_status_returns_status(self, platform_orchestrator):
        """Test that platform status returns status information."""
        platform_orchestrator.startup_status = {
            "foundation": "completed",
            "smart_city_gateway": "completed"
        }
        platform_orchestrator.startup_sequence = ["foundation_infrastructure", "smart_city_gateway"]
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        status = await platform_orchestrator.get_platform_status()
        
        assert status is not None
        assert 'platform_status' in status
        assert 'startup_status' in status
        assert 'timestamp' in status
    
    @pytest.mark.asyncio
    async def test_platform_status_indicates_operational(self, platform_orchestrator):
        """Test that platform status indicates operational when ready."""
        platform_orchestrator.startup_status = {
            "foundation": "completed",
            "smart_city_gateway": "completed"
        }
        platform_orchestrator.startup_sequence = ["foundation_infrastructure", "smart_city_gateway"]
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        status = await platform_orchestrator.get_platform_status()
        
        assert status['platform_status'] == 'operational'
    
    @pytest.mark.asyncio
    async def test_platform_status_indicates_initializing(self, platform_orchestrator):
        """Test that platform status indicates initializing when not ready."""
        platform_orchestrator.startup_status = {
            "foundation": "in_progress",
            "smart_city_gateway": "pending"
        }
        platform_orchestrator.startup_sequence = []
        platform_orchestrator.managers = {}
        platform_orchestrator.foundation_services = {}
        platform_orchestrator.infrastructure_services = {}
        
        status = await platform_orchestrator.get_platform_status()
        
        assert status['platform_status'] == 'initializing'

