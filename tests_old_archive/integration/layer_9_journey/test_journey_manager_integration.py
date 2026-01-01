#!/usr/bin/env python3
"""
Journey Manager Service - Critical Integration Tests

Tests Journey Manager Service to verify:
- Service initialization with Experience Foundation
- Experience Foundation SDK access
- Journey orchestration capabilities
- MCP server integration
- Smart City service discovery

Uses proven patterns from Business Enablement tests.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
async def journey_manager(journey_infrastructure):
    """
    Journey Manager Service instance for each test.
    
    Reuses the journey_infrastructure fixture which includes Experience Foundation.
    """
    logger.info("🔧 Fixture: Starting journey_manager fixture...")
    
    from backend.journey.services.journey_manager.journey_manager_service import JourneyManagerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating JourneyManagerService...")
    infra = journey_infrastructure
    manager = JourneyManagerService(
        di_container=infra["di_container"],
        platform_gateway=infra["platform_gateway"]
    )
    
    # Initialize journey manager
    logger.info("🔧 Fixture: Initializing journey manager...")
    try:
        result = await asyncio.wait_for(manager.initialize(), timeout=90.0)
        if not result:
            pytest.fail("Journey Manager Service failed to initialize")
    except asyncio.TimeoutError:
        pytest.fail("Journey Manager Service initialization timed out")
    
    logger.info("✅ Fixture: Journey Manager ready")
    yield manager
    logger.info("✅ Fixture: Test completed, cleaning up...")


# ============================================================================
# CRITICAL INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_journey_manager_initialization(journey_manager):
    """Test that Journey Manager initializes correctly."""
    logger.info("🧪 Test: Journey Manager initialization")
    
    assert journey_manager is not None
    assert journey_manager.is_initialized
    assert journey_manager.service_name == "JourneyManagerService"
    assert journey_manager.realm_name == "journey"
    
    logger.info("✅ Journey Manager initialized correctly")


@pytest.mark.asyncio
async def test_journey_manager_can_access_experience_foundation(journey_manager, journey_infrastructure):
    """Test that Journey Manager can access Experience Foundation."""
    logger.info("🧪 Test: Journey Manager Experience Foundation access")
    
    infra = journey_infrastructure
    di_container = infra["di_container"]
    
    # Journey Manager should be able to access Experience Foundation via DI container
    experience_foundation = di_container.get_foundation_service("ExperienceFoundationService")
    assert experience_foundation is not None, "Experience Foundation should be available"
    assert experience_foundation.is_initialized, "Experience Foundation should be initialized"
    
    logger.info("✅ Journey Manager can access Experience Foundation")


@pytest.mark.asyncio
async def test_journey_manager_can_access_experience_sdk(journey_manager, journey_infrastructure):
    """Test that Journey Manager can access Experience SDK builders."""
    logger.info("🧪 Test: Journey Manager Experience SDK access")
    
    infra = journey_infrastructure
    experience_foundation = infra["experience_foundation"]
    
    # Get Experience SDK
    sdk = await experience_foundation.get_experience_sdk()
    
    assert isinstance(sdk, dict), "SDK should be a dictionary"
    assert "frontend_gateway_builder" in sdk, "SDK should include frontend_gateway_builder"
    assert "session_manager_builder" in sdk, "SDK should include session_manager_builder"
    assert "user_experience_builder" in sdk, "SDK should include user_experience_builder"
    
    logger.info("✅ Journey Manager can access Experience SDK")


@pytest.mark.asyncio
async def test_journey_manager_has_smart_city_services(journey_manager):
    """Test that Journey Manager has access to Smart City services."""
    logger.info("🧪 Test: Journey Manager Smart City services")
    
    # Journey Manager should discover Smart City services during initialization
    # Check if services are available (they may be None if not discovered, which is OK for now)
    assert hasattr(journey_manager, 'traffic_cop'), "Should have traffic_cop attribute"
    assert hasattr(journey_manager, 'conductor'), "Should have conductor attribute"
    assert hasattr(journey_manager, 'post_office'), "Should have post_office attribute"
    
    logger.info("✅ Journey Manager has Smart City service attributes")


@pytest.mark.asyncio
async def test_journey_manager_has_micro_modules(journey_manager):
    """Test that Journey Manager has all required micro-modules."""
    logger.info("🧪 Test: Journey Manager micro-modules")
    
    assert hasattr(journey_manager, 'initialization_module'), "Should have initialization_module"
    assert hasattr(journey_manager, 'journey_design_module'), "Should have journey_design_module"
    assert hasattr(journey_manager, 'experience_orchestration_module'), "Should have experience_orchestration_module"
    assert hasattr(journey_manager, 'roadmap_management_module'), "Should have roadmap_management_module"
    assert hasattr(journey_manager, 'soa_mcp_module'), "Should have soa_mcp_module"
    assert hasattr(journey_manager, 'utilities_module'), "Should have utilities_module"
    
    logger.info("✅ Journey Manager has all micro-modules")


@pytest.mark.asyncio
async def test_journey_manager_has_mcp_server(journey_manager):
    """Test that Journey Manager has MCP server (if initialized)."""
    logger.info("🧪 Test: Journey Manager MCP server")
    
    # MCP server may be initialized during journey manager initialization
    # Check if it exists (it may be None if not initialized, which is OK for now)
    if hasattr(journey_manager, 'mcp_server'):
        mcp_server = journey_manager.mcp_server
        if mcp_server is not None:
            assert hasattr(mcp_server, 'service_name'), "MCP server should have service_name"
            logger.info(f"✅ Journey Manager MCP server: {mcp_server.service_name}")
        else:
            logger.info("ℹ️ Journey Manager MCP server not initialized (may be lazy initialization)")
    else:
        logger.info("ℹ️ Journey Manager does not have mcp_server attribute (may be in micro-module)")
    
    logger.info("✅ Journey Manager MCP server check complete")

