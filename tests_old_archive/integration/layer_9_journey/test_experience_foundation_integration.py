#!/usr/bin/env python3
"""
Experience Foundation Integration Tests for Journey Realm

Tests Experience Foundation initialization and SDK capabilities to ensure
Journey realm services can properly use Experience Foundation.

Similar to Agentic Foundation tests in Business Enablement realm.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# EXPERIENCE FOUNDATION INITIALIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_experience_foundation_initialization(journey_infrastructure):
    """Test that Experience Foundation initializes correctly."""
    logger.info("🧪 Test: Experience Foundation initialization")
    
    infra = journey_infrastructure
    experience_foundation = infra.get("experience_foundation")
    
    assert experience_foundation is not None, "Experience Foundation should be initialized"
    assert experience_foundation.is_initialized, "Experience Foundation should be initialized"
    assert experience_foundation.service_name == "experience_foundation"
    
    logger.info("✅ Experience Foundation initialized correctly")


@pytest.mark.asyncio
async def test_experience_foundation_registered_in_di_container(journey_infrastructure):
    """Test that Experience Foundation is registered in DI container."""
    logger.info("🧪 Test: Experience Foundation DI container registration")
    
    infra = journey_infrastructure
    di_container = infra["di_container"]
    
    # Check service registry
    experience_foundation = di_container.service_registry.get("ExperienceFoundationService")
    assert experience_foundation is not None, "Experience Foundation should be in service registry"
    
    # Check foundation service access
    experience_foundation_via_get = di_container.get_foundation_service("ExperienceFoundationService")
    assert experience_foundation_via_get is not None, "Experience Foundation should be accessible via get_foundation_service"
    assert experience_foundation_via_get == experience_foundation, "Both access methods should return same instance"
    
    logger.info("✅ Experience Foundation registered in DI container correctly")


@pytest.mark.asyncio
async def test_experience_foundation_sdk_builders(journey_infrastructure):
    """Test that Experience Foundation provides SDK builders."""
    logger.info("🧪 Test: Experience Foundation SDK builders")
    
    infra = journey_infrastructure
    experience_foundation = infra["experience_foundation"]
    
    # Check SDK builders exist
    assert hasattr(experience_foundation, 'frontend_gateway_builder'), "Should have frontend_gateway_builder"
    assert hasattr(experience_foundation, 'session_manager_builder'), "Should have session_manager_builder"
    assert hasattr(experience_foundation, 'user_experience_builder'), "Should have user_experience_builder"
    
    # Check builders are classes (not instances)
    assert experience_foundation.frontend_gateway_builder is not None
    assert experience_foundation.session_manager_builder is not None
    assert experience_foundation.user_experience_builder is not None
    
    logger.info("✅ Experience Foundation SDK builders available")


@pytest.mark.asyncio
async def test_experience_foundation_get_sdk(journey_infrastructure):
    """Test that Experience Foundation get_experience_sdk method works."""
    logger.info("🧪 Test: Experience Foundation get_experience_sdk")
    
    infra = journey_infrastructure
    experience_foundation = infra["experience_foundation"]
    
    # Get SDK
    sdk = await experience_foundation.get_experience_sdk()
    
    assert isinstance(sdk, dict), "SDK should be a dictionary"
    assert "frontend_gateway_builder" in sdk, "SDK should include frontend_gateway_builder"
    assert "session_manager_builder" in sdk, "SDK should include session_manager_builder"
    assert "user_experience_builder" in sdk, "SDK should include user_experience_builder"
    
    logger.info("✅ Experience Foundation get_experience_sdk works correctly")


@pytest.mark.asyncio
async def test_experience_foundation_health_check(journey_infrastructure):
    """Test that Experience Foundation health check works."""
    logger.info("🧪 Test: Experience Foundation health check")
    
    infra = journey_infrastructure
    experience_foundation = infra["experience_foundation"]
    
    # Perform health check
    health = await experience_foundation.health_check()
    
    assert isinstance(health, dict), "Health check should return a dictionary"
    assert "status" in health, "Health check should include status"
    assert health["status"] in ["healthy", "unhealthy"], "Status should be healthy or unhealthy"
    assert health.get("status") == "healthy", "Experience Foundation should be healthy"
    
    logger.info(f"✅ Experience Foundation health check: {health.get('status')}")


@pytest.mark.asyncio
async def test_experience_foundation_service_capabilities(journey_infrastructure):
    """Test that Experience Foundation service capabilities method works."""
    logger.info("🧪 Test: Experience Foundation service capabilities")
    
    infra = journey_infrastructure
    experience_foundation = infra["experience_foundation"]
    
    # Get capabilities
    capabilities = await experience_foundation.get_service_capabilities()
    
    assert isinstance(capabilities, dict), "Capabilities should be a dictionary"
    assert "service_name" in capabilities, "Capabilities should include service_name"
    assert capabilities["service_name"] == "experience_foundation"
    assert "capabilities" in capabilities, "Capabilities should include capabilities list"
    assert "frontend_gateway" in capabilities["capabilities"], "Should include frontend_gateway capability"
    assert "session_manager" in capabilities["capabilities"], "Should include session_manager capability"
    assert "user_experience" in capabilities["capabilities"], "Should include user_experience capability"
    
    logger.info("✅ Experience Foundation service capabilities work correctly")

