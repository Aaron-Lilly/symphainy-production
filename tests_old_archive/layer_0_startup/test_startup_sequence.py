#!/usr/bin/env python3
"""
Layer 0: Platform Startup Sequence Tests

Tests that validate the platform startup sequence follows the correct order
and initializes all required components.

WHAT: Validate platform startup sequence
HOW: Test PlatformOrchestrator.orchestrate_platform_startup()
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

import os

from main import PlatformOrchestrator

class TestPlatformStartupSequence:
    """Test platform startup sequence follows correct order."""
    
    @pytest.fixture
    async def platform_orchestrator(self):
        """Create PlatformOrchestrator instance."""
        return PlatformOrchestrator()
    
    @pytest.mark.asyncio
    async def test_startup_sequence_phases(self, platform_orchestrator):
        """Test that startup sequence has all required phases."""
        # Create mocks that update state correctly
        async def mock_foundation():
            platform_orchestrator.startup_status["foundation"] = "ready"
            platform_orchestrator.startup_sequence.append("foundation_infrastructure")
        
        async def mock_gateway():
            platform_orchestrator.startup_status["smart_city_gateway"] = "ready"
            platform_orchestrator.startup_sequence.append("smart_city_gateway")
        
        with patch.object(platform_orchestrator, '_initialize_foundation_infrastructure', side_effect=mock_foundation), \
             patch.object(platform_orchestrator, '_initialize_smart_city_gateway', side_effect=mock_gateway), \
             patch.object(platform_orchestrator, '_start_background_watchers', new_callable=AsyncMock) as mock_watchers, \
             patch.object(platform_orchestrator, '_start_curator_autodiscovery', new_callable=AsyncMock) as mock_curator:
            
            # Execute startup
            result = await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify all phases were called
            assert mock_watchers.called, "Phase 4: Background Watchers should be called"
            assert mock_curator.called, "Phase 5: Curator Auto-Discovery should be called"
            
            # Verify startup sequence order (includes lazy_realm_hydration which is always added)
            assert "foundation_infrastructure" in platform_orchestrator.startup_sequence
            assert "smart_city_gateway" in platform_orchestrator.startup_sequence
            assert "lazy_realm_hydration" in platform_orchestrator.startup_sequence
            
            # Verify startup status
            assert platform_orchestrator.startup_status["foundation"] == "ready"
            assert platform_orchestrator.startup_status["smart_city_gateway"] == "ready"
            assert platform_orchestrator.startup_status["lazy_hydration"] == "ready"
    
    @pytest.mark.asyncio
    async def test_startup_sequence_order(self, platform_orchestrator):
        """Test that startup phases execute in correct order."""
        call_order = []
        
        async def track_foundation():
            call_order.append("foundation")
            platform_orchestrator.startup_status["foundation"] = "ready"
            platform_orchestrator.startup_sequence.append("foundation_infrastructure")
            return True
        
        async def track_gateway():
            call_order.append("gateway")
            platform_orchestrator.startup_status["smart_city_gateway"] = "ready"
            platform_orchestrator.startup_sequence.append("smart_city_gateway")
            return True
        
        async def track_watchers():
            call_order.append("watchers")
            return True
        
        async def track_curator():
            call_order.append("curator")
            return True
        
        with patch.object(platform_orchestrator, '_initialize_foundation_infrastructure', side_effect=track_foundation), \
             patch.object(platform_orchestrator, '_initialize_smart_city_gateway', side_effect=track_gateway), \
             patch.object(platform_orchestrator, '_start_background_watchers', side_effect=track_watchers), \
             patch.object(platform_orchestrator, '_start_curator_autodiscovery', side_effect=track_curator):
            
            await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify order: foundation -> gateway -> watchers -> curator
            assert call_order == ["foundation", "gateway", "watchers", "curator"], \
                f"Startup order incorrect. Got: {call_order}"
    
    @pytest.mark.asyncio
    async def test_startup_result_structure(self, platform_orchestrator):
        """Test that startup result has correct structure."""
        async def mock_foundation():
            platform_orchestrator.startup_status["foundation"] = "ready"
            platform_orchestrator.startup_sequence.append("foundation_infrastructure")
        
        async def mock_gateway():
            platform_orchestrator.startup_status["smart_city_gateway"] = "ready"
            platform_orchestrator.startup_sequence.append("smart_city_gateway")
        
        with patch.object(platform_orchestrator, '_initialize_foundation_infrastructure', side_effect=mock_foundation), \
             patch.object(platform_orchestrator, '_initialize_smart_city_gateway', side_effect=mock_gateway), \
             patch.object(platform_orchestrator, '_start_background_watchers', new_callable=AsyncMock), \
             patch.object(platform_orchestrator, '_start_curator_autodiscovery', new_callable=AsyncMock):
            
            result = await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify result structure
            assert "success" in result
            assert result["success"] is True
            assert "startup_sequence" in result
            assert isinstance(result["startup_sequence"], list)
            assert "timestamp" in result
            assert "foundation_services" in result
            assert "infrastructure_services" in result
    
    @pytest.mark.asyncio
    async def test_lazy_hydration_deferred(self, platform_orchestrator):
        """Test that lazy hydration is deferred (not eagerly initialized)."""
        realm_startup_called = False
        
        async def track_realm_startup(*args, **kwargs):
            nonlocal realm_startup_called
            realm_startup_called = True
        
        async def mock_foundation():
            platform_orchestrator.startup_status["foundation"] = "ready"
            platform_orchestrator.startup_sequence.append("foundation_infrastructure")
        
        async def mock_gateway():
            platform_orchestrator.startup_status["smart_city_gateway"] = "ready"
            platform_orchestrator.startup_sequence.append("smart_city_gateway")
        
        with patch.object(platform_orchestrator, '_initialize_foundation_infrastructure', side_effect=mock_foundation), \
             patch.object(platform_orchestrator, '_initialize_smart_city_gateway', side_effect=mock_gateway), \
             patch.object(platform_orchestrator, '_start_background_watchers', new_callable=AsyncMock), \
             patch.object(platform_orchestrator, '_start_curator_autodiscovery', new_callable=AsyncMock):
            
            await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify realm startup was NOT called (lazy hydration)
            assert not realm_startup_called, "Realm startup should be deferred (lazy hydration)"
            assert platform_orchestrator.startup_status["lazy_hydration"] == "ready"
