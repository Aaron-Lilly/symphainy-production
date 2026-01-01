#!/usr/bin/env python3
"""
Business Outcomes Orchestrator Functionality Tests

Tests Business Outcomes Orchestrator core functionality:
- Business outcomes analysis coordination
- Agent routing
- Metrics calculation

Uses mock AI responses.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

    # Fallback: calculate from this file's location
from tests.fixtures.ai_mock_responses import get_business_outcomes_analysis_response
from tests.fixtures.test_datasets import get_sample_json_data

@pytest.mark.business_enablement
@pytest.mark.functional
class TestBusinessOutcomesOrchestratorFunctionality:
    """Test Business Outcomes Orchestrator functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_delivery_manager(self, mock_di_container, mock_platform_gateway):
        """Create mock Delivery Manager."""
        manager = Mock()
        manager.realm_name = "business_enablement"
        manager.platform_gateway = mock_platform_gateway
        manager.di_container = mock_di_container
        manager.logger = Mock()
        return manager
    
    @pytest.fixture
    def mock_business_outcomes_specialist_agent(self):
        """Create mock Business Outcomes Specialist Agent."""
        agent = Mock()
        agent.analyze_outcomes = AsyncMock(return_value={
            "status": "success",
            "outcomes": []
        })
        return agent
    
    @pytest.fixture
    async def business_outcomes_orchestrator(self, mock_delivery_manager, mock_business_outcomes_specialist_agent):

        # Ensure correct path
        """Create Business Outcomes Orchestrator instance."""

        # Ensure correct path
        # Ensure path is set - convert to absolute for comparison
        # Path is already set at module level, but ensure it's in sys.path
        # project_root is already absolute, just ensure it's added
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        orchestrator = BusinessOutcomesOrchestrator(
            delivery_manager=mock_delivery_manager
        )
        
        # Mock agents
        orchestrator.business_outcomes_specialist_agent = mock_business_outcomes_specialist_agent
        orchestrator.business_outcomes_liaison_agent = Mock()
        
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_analyze_outcomes(self, business_outcomes_orchestrator, mock_business_outcomes_specialist_agent):
        """Test business outcomes analysis coordination."""
        data = get_sample_json_data()
        
        result = await business_outcomes_orchestrator.analyze_outcomes(
            data=data,
            options={"metrics": ["revenue", "satisfaction"]}
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "status" in result or "outcomes" in result
    
    @pytest.mark.asyncio
    async def test_coordinate_agents(self, business_outcomes_orchestrator):
        """Test agent coordination."""
        request = {
            "type": "business_outcomes",
            "data": get_sample_json_data()
        }
        
        result = await business_outcomes_orchestrator.coordinate_agents(request)
        
        assert result is not None
        assert isinstance(result, dict)

