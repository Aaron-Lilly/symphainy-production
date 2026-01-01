#!/usr/bin/env python3
"""
Layer 9 Journey Realm - Test Configuration and Fixtures

Provides shared fixtures for Layer 9 tests, including:
- journey_infrastructure: Comprehensive Journey infrastructure fixture with Experience Foundation
- smart_city_infrastructure: Comprehensive Smart City infrastructure fixture (reused from Business Enablement)
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from tests.utils.safe_docker import check_container_status, check_container_health

# Add symphainy-platform to path for imports (set early for module-level imports)
project_root = Path(__file__).parent.parent.parent.parent.parent
symphainy_platform = project_root / "symphainy-platform"
if str(symphainy_platform) not in sys.path:
    sys.path.insert(0, str(symphainy_platform))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import SmartCityServiceManager from Business Enablement conftest
# We'll reuse the same infrastructure setup pattern
from tests.integration.layer_8_business_enablement.conftest import SmartCityServiceManager, smart_city_infrastructure


@pytest.fixture(scope="function")
# Timeout handled by pytest-timeout plugin
async def journey_infrastructure(smart_city_infrastructure):
    """
    Comprehensive Journey infrastructure fixture with Experience Foundation.
    
    Initializes:
    - All Smart City infrastructure (from smart_city_infrastructure fixture)
    - Agentic Foundation (for agent capabilities if needed)
    - Experience Foundation (CRITICAL for Journey realm)
    
    CRITICAL: This fixture has a 240-second timeout to prevent SSH session crashes.
    If infrastructure is unavailable, tests will fail fast rather than hanging.
    
    Returns:
        Dictionary with:
        - di_container: DIContainerService
        - public_works_foundation: PublicWorksFoundationService
        - curator: CuratorFoundationService
        - platform_gateway: PlatformInfrastructureGateway
        - smart_city_services: Dict of initialized Smart City services
        - agentic_foundation: AgenticFoundationService (if needed)
        - experience_foundation: ExperienceFoundationService (CRITICAL)
    """
    infra = smart_city_infrastructure
    di_container = infra["di_container"]
    pwf = infra["public_works_foundation"]
    curator = infra["curator"]
    
    # Initialize Agentic Foundation (Journey services may use agents)
    from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
    
    agentic_foundation = AgenticFoundationService(
        di_container=di_container,
        public_works_foundation=pwf,
        curator_foundation=curator
    )
    
    try:
        agentic_result = await asyncio.wait_for(
            agentic_foundation.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Agentic Foundation initialization timed out after 30 seconds")
    
    if not agentic_result:
        pytest.fail("Agentic Foundation initialization failed")
    
    # CRITICAL: Register in DI container so Journey services can access it
    di_container.service_registry["AgenticFoundationService"] = agentic_foundation
    
    # Initialize Experience Foundation (CRITICAL for Journey realm)
    from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService
    
    experience_foundation = ExperienceFoundationService(
        di_container=di_container,
        public_works_foundation=pwf,
        curator_foundation=curator
    )
    
    try:
        experience_result = await asyncio.wait_for(
            experience_foundation.initialize(),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        pytest.fail("Experience Foundation initialization timed out after 30 seconds")
    
    if not experience_result:
        pytest.fail("Experience Foundation initialization failed")
    
    # CRITICAL: Register in DI container so Journey services can access it
    di_container.service_registry["ExperienceFoundationService"] = experience_foundation
    
    # Return comprehensive infrastructure
    return {
        **infra,  # Include all Smart City infrastructure
        "agentic_foundation": agentic_foundation,
        "experience_foundation": experience_foundation
    }

