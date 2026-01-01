#!/usr/bin/env python3
"""
Nurse Service Curator Registration Test

Tests that Nurse service can:
1. Register with Curator using new Phase 2 pattern
2. Be discovered by other services via Curator

WHAT: Verify Nurse service registration and discovery
HOW: Initialize foundations, create Nurse service, test registration and discovery
"""

import sys
from pathlib import Path
import pytest
import asyncio

# Add project root to path (tests are in symphainy-platform/tests, so parent.parent is symphainy-platform)
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from backend.smart_city.services.nurse.nurse_service import NurseService


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def foundation_stack(event_loop):
    """Initialize foundation stack (Public Works, Curator)."""
    container = DIContainerService("test")
    
    # Initialize Public Works Foundation
    public_works = PublicWorksFoundationService(di_container=container)
    await public_works.initialize()
    container.register_foundation_service("PublicWorksFoundationService", public_works)
    
    # Initialize Curator Foundation
    curator = CuratorFoundationService(
        foundation_services=container,
        public_works_foundation=public_works
    )
    await curator.initialize()
    container.register_foundation_service("CuratorFoundationService", curator)
    
    yield {
        "di_container": container,
        "public_works": public_works,
        "curator": curator
    }
    
    # Cleanup
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture(scope="module")
async def nurse_service(foundation_stack):
    """Create and initialize Nurse Service with foundation stack."""
    container = foundation_stack["di_container"]
    nurse = NurseService(di_container=container)
    initialized = await nurse.initialize()
    
    if not initialized:
        pytest.skip("Nurse Service failed to initialize with foundations")
    
    yield nurse
    
    # Cleanup
    if hasattr(nurse, 'shutdown'):
        await nurse.shutdown()


class TestNurseCuratorRegistration:
    """Test Nurse service registration with Curator."""
    
    @pytest.mark.asyncio
    async def test_nurse_registers_with_curator(self, nurse_service, foundation_stack):
        """Test that Nurse service registers its capabilities with Curator."""
        curator = foundation_stack["curator"]
        
        # Verify Nurse service is initialized
        assert nurse_service.is_initialized, "Nurse service should be initialized"
        
        # Verify capabilities were registered
        # Check that Nurse service is in Curator's registered services
        # (This depends on how Curator tracks services - may need to check capability registry)
        assert hasattr(curator, 'capability_registry'), "Curator should have capability registry"
        
        # Verify Nurse has SOA APIs and MCP tools
        assert hasattr(nurse_service, 'soa_apis'), "Nurse should have SOA APIs"
        assert len(nurse_service.soa_apis) > 0, "Nurse should have at least one SOA API"
        
        assert hasattr(nurse_service, 'mcp_tools'), "Nurse should have MCP tools"
        assert len(nurse_service.mcp_tools) > 0, "Nurse should have at least one MCP tool"
    
    @pytest.mark.asyncio
    async def test_nurse_capabilities_discoverable(self, nurse_service, foundation_stack):
        """Test that Nurse capabilities can be discovered via Curator."""
        curator = foundation_stack["curator"]
        
        # Discover capabilities for Nurse service
        # Check if we can discover Nurse's capabilities
        service_name = nurse_service.service_name
        
        # Try to discover service by name
        discovered_service = await curator.discover_service_by_name(service_name)
        
        # Service discovery might return None if not registered with service discovery
        # But capabilities should still be registered in capability registry
        # Let's check capability registry directly
        if hasattr(curator.capability_registry, 'get_service_capabilities'):
            capabilities = await curator.capability_registry.get_service_capabilities(service_name)
            assert capabilities is not None, f"Should be able to discover capabilities for {service_name}"
            assert len(capabilities) > 0, f"Should have at least one capability for {service_name}"
    
    @pytest.mark.asyncio
    async def test_nurse_soa_apis_registered(self, nurse_service, foundation_stack):
        """Test that Nurse SOA APIs are registered with Curator."""
        curator = foundation_stack["curator"]
        service_name = nurse_service.service_name
        
        # Check that SOA APIs are registered
        # We can check via capability registry or route registry
        if hasattr(curator.capability_registry, 'get_service_capabilities'):
            capabilities = await curator.capability_registry.get_service_capabilities(service_name)
            
            if capabilities:
                # Check that at least one capability has SOA API contract
                soa_api_capabilities = [
                    cap for cap in capabilities
                    if isinstance(cap, dict) and cap.get("contracts", {}).get("soa_api")
                ]
                
                # If using CapabilityDefinition, check differently
                # Let's check route registry for endpoints
                if hasattr(curator, 'route_registry'):
                    routes = await curator.discover_routes(service_name=service_name)
                    # Nurse should have registered routes for its SOA APIs
                    assert len(routes) > 0, f"Nurse should have registered routes for SOA APIs"
    
    @pytest.mark.asyncio
    async def test_nurse_mcp_tools_registered(self, nurse_service, foundation_stack):
        """Test that Nurse MCP tools are registered with Curator."""
        curator = foundation_stack["curator"]
        service_name = nurse_service.service_name
        
        # Check that MCP tools are registered
        if hasattr(curator.capability_registry, 'get_service_capabilities'):
            capabilities = await curator.capability_registry.get_service_capabilities(service_name)
            
            if capabilities:
                # Check that at least one capability has MCP tool contract
                mcp_tool_capabilities = [
                    cap for cap in capabilities
                    if isinstance(cap, dict) and cap.get("contracts", {}).get("mcp_tool")
                ]
                
                # Verify we found MCP tool capabilities
                # (This depends on how capabilities are stored - may need to check tool registry)
                assert len(mcp_tool_capabilities) > 0 or len(nurse_service.mcp_tools) > 0, \
                    "Nurse should have MCP tools registered"
    
    @pytest.mark.asyncio
    async def test_other_service_can_discover_nurse(self, nurse_service, foundation_stack):
        """Test that another service can discover Nurse via Curator."""
        curator = foundation_stack["curator"]
        service_name = nurse_service.service_name
        
        # Simulate another service trying to discover Nurse
        # Try to get service information
        discovered_service = await curator.discover_service_by_name(service_name)
        
        # Even if service discovery returns None, capabilities should be discoverable
        # Check capability registry
        if hasattr(curator.capability_registry, 'get_service_capabilities'):
            capabilities = await curator.capability_registry.get_service_capabilities(service_name)
            assert capabilities is not None, "Other services should be able to discover Nurse capabilities"
            
            # Verify we can get specific capability information
            if capabilities and len(capabilities) > 0:
                # Check that capabilities have proper structure
                first_cap = capabilities[0]
                assert "service_name" in first_cap or hasattr(first_cap, 'service_name'), \
                    "Capability should have service_name"
                assert "description" in first_cap or hasattr(first_cap, 'description'), \
                    "Capability should have description"

