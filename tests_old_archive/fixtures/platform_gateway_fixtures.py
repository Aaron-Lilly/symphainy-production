#!/usr/bin/env python3
"""
Platform Gateway Test Fixtures

Provides fixtures for testing Platform Gateway and realm access control.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, Optional


@pytest.fixture
def mock_platform_gateway():
    """Create a mock Platform Gateway for testing."""
    mock_gateway = MagicMock()
    
    # Realm abstraction mappings
    mock_gateway.REALM_ABSTRACTION_MAPPINGS = {
        "smart_city": {
            "abstractions": [
                "session", "state", "auth", "authorization", "tenant",
                "file_management", "content_metadata", "content_schema",
                "content_insights", "llm", "mcp", "policy", "messaging",
                "event_management", "api_gateway", "websocket", "event_bus"
            ],
            "description": "Smart City - First-class citizen with full access",
            "byoi_support": True
        },
        "business_enablement": {
            "abstractions": [
                "content_metadata", "content_schema", "content_insights",
                "file_management", "llm"
            ],
            "description": "Business workflow capabilities",
            "byoi_support": False
        },
        "experience": {
            "abstractions": [
                "session", "auth", "authorization", "tenant"
            ],
            "description": "User interaction capabilities",
            "byoi_support": False
        },
        "solution": {
            "abstractions": [
                "llm", "content_metadata", "file_management"
            ],
            "description": "Solution design capabilities",
            "byoi_support": False
        },
        "journey": {
            "abstractions": [
                "llm", "session", "content_metadata"
            ],
            "description": "Journey orchestration capabilities",
            "byoi_support": False
        }
    }
    
    # Mock abstractions
    mock_abstractions = {}
    for realm, config in mock_gateway.REALM_ABSTRACTION_MAPPINGS.items():
        for abstraction_name in config["abstractions"]:
            if abstraction_name not in mock_abstractions:
                mock_abstractions[abstraction_name] = MagicMock()
    
    # Methods
    def get_abstraction(realm_name: str, abstraction_name: str):
        """Get abstraction with realm validation."""
        realm_config = mock_gateway.REALM_ABSTRACTION_MAPPINGS.get(realm_name, {})
        allowed = realm_config.get("abstractions", [])
        
        if abstraction_name not in allowed:
            raise ValueError(
                f"Realm '{realm_name}' cannot access '{abstraction_name}'. "
                f"Allowed: {allowed}"
            )
        
        return mock_abstractions.get(abstraction_name, MagicMock())
    
    mock_gateway.get_abstraction = MagicMock(side_effect=get_abstraction)
    mock_gateway.validate_access = MagicMock(return_value=True)
    mock_gateway.get_realm_abstractions = MagicMock(
        side_effect=lambda realm_name: {
            name: mock_abstractions.get(name)
            for name in mock_gateway.REALM_ABSTRACTION_MAPPINGS.get(realm_name, {}).get("abstractions", [])
        }
    )
    
    return mock_gateway


@pytest.fixture
async def real_platform_gateway(real_public_works_foundation):
    """Create a real Platform Gateway for integration tests."""
    try:
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        gateway = PlatformInfrastructureGateway(real_public_works_foundation)
        return gateway
    except ImportError:
        # Try alternative import path
        try:
            from platform.infrastructure.platform_gateway import PlatformInfrastructureGateway
            gateway = PlatformInfrastructureGateway(real_public_works_foundation)
            return gateway
        except Exception as e:
            pytest.skip(f"Could not create real Platform Gateway: {e}")



