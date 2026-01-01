#!/usr/bin/env python3
"""
Layer 10 Solution Realm - Test Configuration and Fixtures

Provides shared fixtures for Layer 10 tests, including:
- solution_infrastructure: Comprehensive Solution infrastructure fixture with Journey Foundation
- Reuses journey_infrastructure from Layer 9 (which includes Experience Foundation)
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add symphainy-platform to path for imports (set early for module-level imports)
project_root = Path(__file__).parent.parent.parent.parent.parent
symphainy_platform = project_root / "symphainy-platform"
if str(symphainy_platform) not in sys.path:
    sys.path.insert(0, str(symphainy_platform))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import journey_infrastructure and its dependencies from Layer 9
# Solution realm composes Journey services, so we need Journey infrastructure
# We need to import the full dependency chain
from tests.integration.layer_9_journey.conftest import journey_infrastructure
# Also import smart_city_infrastructure to ensure the dependency chain works
from tests.integration.layer_8_business_enablement.conftest import smart_city_infrastructure


@pytest.fixture(scope="function")
# Timeout handled by pytest-timeout plugin
async def solution_infrastructure(journey_infrastructure):
    """
    Comprehensive Solution infrastructure fixture with Journey Foundation.
    
    Initializes:
    - All Journey infrastructure (from journey_infrastructure fixture)
      - Smart City infrastructure
      - Agentic Foundation
      - Experience Foundation
      - Journey services (MVP, Session, Structured orchestrators)
    
    CRITICAL: This fixture has a 240-second timeout to prevent SSH session crashes.
    If infrastructure is unavailable, tests will fail fast rather than hanging.
    
    Returns:
        Dictionary with:
        - di_container: DIContainerService
        - public_works_foundation: PublicWorksFoundationService
        - curator: CuratorFoundationService
        - platform_gateway: PlatformInfrastructureGateway
        - smart_city_services: Dict of initialized Smart City services
        - agentic_foundation: AgenticFoundationService
        - experience_foundation: ExperienceFoundationService
        - journey_infrastructure: All Journey infrastructure
    """
    # Reuse journey_infrastructure (which includes everything we need)
    # Solution services compose Journey services, so we need Journey infrastructure
    infra = journey_infrastructure
    
    # Return comprehensive infrastructure
    return {
        **infra,  # Include all Journey infrastructure (which includes Smart City, Experience, etc.)
    }

