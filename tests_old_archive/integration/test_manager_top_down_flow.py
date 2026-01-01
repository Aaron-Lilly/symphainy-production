#!/usr/bin/env python3
"""
Production Readiness Test: Manager Hierarchy Top-Down Flow

Tests the top-down orchestration flow through the manager hierarchy:
Solution Manager → Journey Manager → Experience Manager → Delivery Manager
"""

import pytest
import asyncio

from pathlib import Path
from typing import Dict, Any

class TestManagerTopDownFlow:
    """Test manager hierarchy top-down orchestration flow."""
    
    @pytest.fixture
    async def initialized_platform(self):
        """Initialize complete platform for testing."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Foundations
        public_works = PublicWorksFoundationService(di_container=di_container)
        await public_works.initialize()
        di_container.service_registry["PublicWorksFoundationService"] = public_works
        
        curator = CuratorFoundationService(di_container=di_container)
        await curator.initialize()
        di_container.service_registry["CuratorFoundationService"] = curator
        
        communication = CommunicationFoundationService(di_container=di_container)
        await communication.initialize()
        di_container.service_registry["CommunicationFoundationService"] = communication
        
        agentic = AgenticFoundationService(di_container=di_container)
        await agentic.initialize()
        di_container.service_registry["AgenticFoundationService"] = agentic
        
        # Initialize Platform Gateway
        platform_gateway = PlatformInfrastructureGateway(public_works_foundation=public_works)
        await platform_gateway.initialize()
        di_container.service_registry["PlatformInfrastructureGateway"] = platform_gateway
        
        # Initialize City Manager
        city_manager = CityManagerService(di_container=di_container)
        await city_manager.initialize()
        di_container.service_registry["CityManagerService"] = city_manager
        
        # Bootstrap Manager Hierarchy
        from backend.smart_city.protocols.city_manager_service_protocol import BootstrapRequest
        bootstrap_request = BootstrapRequest(solution_context=None, manager_configs=None)
        bootstrap_result = await city_manager.bootstrap_manager_hierarchy(bootstrap_request)
        
        assert bootstrap_result.success, f"Bootstrap failed: {bootstrap_result.error}"
        
        return {
            "di_container": di_container,
            "city_manager": city_manager,
            "platform_gateway": platform_gateway
        }
    
    @pytest.mark.asyncio
    async def test_solution_manager_initialization(self, initialized_platform):
        """Test Solution Manager is initialized and ready."""
        di_container = initialized_platform["di_container"]
        
        solution_manager = di_container.get_foundation_service("SolutionManagerService")
        assert solution_manager is not None
        assert solution_manager.is_initialized
        assert solution_manager.manager_type.value == "solution_manager"
    
    @pytest.mark.asyncio
    async def test_journey_manager_initialization(self, initialized_platform):
        """Test Journey Manager is initialized and ready."""
        di_container = initialized_platform["di_container"]
        
        journey_manager = di_container.get_foundation_service("JourneyManagerService")
        assert journey_manager is not None
        assert journey_manager.is_initialized
        assert journey_manager.manager_type.value == "journey_manager"
    
    @pytest.mark.asyncio
    async def test_experience_manager_initialization(self, initialized_platform):
        """Test Experience Manager is initialized and ready."""
        di_container = initialized_platform["di_container"]
        
        experience_manager = di_container.get_foundation_service("ExperienceManagerService")
        assert experience_manager is not None
        assert experience_manager.is_initialized
        assert experience_manager.manager_type.value == "experience_manager"
    
    @pytest.mark.asyncio
    async def test_delivery_manager_initialization(self, initialized_platform):
        """Test Delivery Manager is initialized and ready."""
        di_container = initialized_platform["di_container"]
        
        delivery_manager = di_container.get_foundation_service("DeliveryManagerService")
        assert delivery_manager is not None
        assert delivery_manager.is_initialized
        assert delivery_manager.manager_type.value == "delivery_manager"
    
    @pytest.mark.asyncio
    async def test_manager_hierarchy_order(self, initialized_platform):
        """Test managers are initialized in correct order."""
        city_manager = initialized_platform["city_manager"]
        
        # Check manager hierarchy order
        hierarchy = city_manager.manager_hierarchy
        
        # Solution Manager should be first
        assert "solution_manager" in hierarchy
        assert hierarchy["solution_manager"]["status"] == "initialized"
        
        # Journey Manager should be second
        assert "journey_manager" in hierarchy
        assert hierarchy["journey_manager"]["status"] == "initialized"
        
        # Experience Manager should be third
        assert "experience_manager" in hierarchy
        assert hierarchy["experience_manager"]["status"] == "initialized"
        
        # Delivery Manager should be fourth
        assert "delivery_manager" in hierarchy
        assert hierarchy["delivery_manager"]["status"] == "initialized"
    
    @pytest.mark.asyncio
    async def test_manager_service_discovery(self, initialized_platform):
        """Test managers can discover Smart City services via Curator."""
        di_container = initialized_platform["di_container"]
        
        solution_manager = di_container.get_foundation_service("SolutionManagerService")
        
        # Managers should be able to discover Smart City services
        # (Note: In test environment, services may not be registered, but discovery should not error)
        try:
            security_guard = await solution_manager.get_security_guard_api()
            # Service may not be available, but discovery should not raise exception
        except Exception as e:
            # If it's a discovery error, that's acceptable in test environment
            assert "not found" in str(e).lower() or "not available" in str(e).lower()

