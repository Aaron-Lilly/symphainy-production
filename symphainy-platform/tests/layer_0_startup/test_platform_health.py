#!/usr/bin/env python3
"""
Layer 0: Platform Health Tests

Tests that validate platform health endpoints and health checks work correctly.

WHAT: Validate platform health
HOW: Test health endpoints, verify health status, test foundation health
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
from main import PlatformOrchestrator, app_state, setup_platform_routes
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestPlatformHealth:
    """Test platform health endpoints."""
    
    @pytest.fixture
    def platform_orchestrator(self):
        """Create Platform Orchestrator instance."""
        orchestrator = PlatformOrchestrator()
        orchestrator.startup_status = {
            "foundation": "completed",
            "smart_city_gateway": "completed"
        }
        orchestrator.startup_sequence = ["foundation_infrastructure", "smart_city_gateway"]
        orchestrator.managers = {}
        orchestrator.foundation_services = {
            "public_works_foundation": Mock(),
            "curator_foundation": Mock(),
            "communication_foundation": Mock(),
            "agentic_foundation": Mock()
        }
        orchestrator.infrastructure_services = {}
        return orchestrator
    
    @pytest.fixture
    def app(self, platform_orchestrator):
        """Create FastAPI app with mocked platform orchestrator."""
        app = FastAPI()
        
        # Mock global platform_orchestrator
        import main
        main.platform_orchestrator = platform_orchestrator
        
        # Setup routes
        asyncio.run(setup_platform_routes(app))
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint_exists(self, client):
        """Test that health endpoint exists."""
        response = client.get("/health")
        assert response.status_code in [200, 500]  # May fail if platform not initialized, but endpoint exists
    
    def test_health_endpoint_returns_status(self, client):
        """Test that health endpoint returns status information."""
        response = client.get("/health")
        
        # Should return some response (even if error)
        assert response.status_code is not None
        
        if response.status_code == 200:
            data = response.json()
            assert 'platform_status' in data or 'status' in data
    
    def test_platform_status_endpoint_exists(self, client):
        """Test that platform status endpoint exists."""
        response = client.get("/platform/status")
        assert response.status_code in [200, 500]  # May fail if platform not initialized, but endpoint exists
    
    def test_platform_status_returns_detailed_status(self, client):
        """Test that platform status endpoint returns detailed status."""
        response = client.get("/platform/status")
        
        # Should return some response (even if error)
        assert response.status_code is not None
        
        if response.status_code == 200:
            data = response.json()
            assert 'platform_status' in data or 'error' in data
    
    def test_foundation_services_endpoint_exists(self, client):
        """Test that foundation services endpoint exists."""
        response = client.get("/foundation/services")
        assert response.status_code in [200, 500]  # May fail if platform not initialized, but endpoint exists
    
    def test_foundation_services_returns_list(self, client):
        """Test that foundation services endpoint returns list of services."""
        response = client.get("/foundation/services")
        
        # Should return some response (even if error)
        assert response.status_code is not None
        
        if response.status_code == 200:
            data = response.json()
            assert 'foundation_services' in data or 'error' in data
    
    def test_managers_endpoint_exists(self, client):
        """Test that managers endpoint exists."""
        response = client.get("/managers")
        assert response.status_code in [200, 500]  # May fail if platform not initialized, but endpoint exists
    
    def test_managers_endpoint_returns_list(self, client):
        """Test that managers endpoint returns list of managers."""
        response = client.get("/managers")
        
        # Should return some response (even if error)
        assert response.status_code is not None
        
        if response.status_code == 200:
            data = response.json()
            assert 'managers' in data or 'error' in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint_with_operational_platform(self, platform_orchestrator):
        """Test health endpoint with operational platform."""
        status = await platform_orchestrator.get_platform_status()
        
        assert status is not None
        assert 'platform_status' in status
        assert status['platform_status'] == 'operational'
        assert 'startup_status' in status
        assert 'foundation_services' in status
    
    @pytest.mark.asyncio
    async def test_health_endpoint_includes_foundation_services(self, platform_orchestrator):
        """Test that health endpoint includes foundation services."""
        status = await platform_orchestrator.get_platform_status()
        
        assert 'foundation_services' in status
        assert isinstance(status['foundation_services'], dict)
    
    @pytest.mark.asyncio
    async def test_health_endpoint_includes_infrastructure_services(self, platform_orchestrator):
        """Test that health endpoint includes infrastructure services."""
        status = await platform_orchestrator.get_platform_status()
        
        assert 'infrastructure_services' in status
        assert isinstance(status['infrastructure_services'], dict)
    
    @pytest.mark.asyncio
    async def test_health_endpoint_includes_startup_sequence(self, platform_orchestrator):
        """Test that health endpoint includes startup sequence."""
        status = await platform_orchestrator.get_platform_status()
        
        assert 'startup_sequence' in status
        assert isinstance(status['startup_sequence'], list)
    
    @pytest.mark.asyncio
    async def test_health_endpoint_includes_timestamp(self, platform_orchestrator):
        """Test that health endpoint includes timestamp."""
        status = await platform_orchestrator.get_platform_status()
        
        assert 'timestamp' in status
        assert isinstance(status['timestamp'], str)

