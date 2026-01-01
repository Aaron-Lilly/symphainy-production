#!/usr/bin/env python3
"""
Content Analysis Orchestrator Functionality Tests

Tests Content Analysis Orchestrator core functionality:
- Content analysis coordination
- Agent routing
- Workflow management
- Multi-agent coordination

Uses mock AI responses.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

    # Fallback: calculate from this file's location
from tests.fixtures.ai_mock_responses import get_content_analysis_response, get_liaison_agent_response
from tests.fixtures.test_datasets import get_sample_document

@pytest.mark.business_enablement
@pytest.mark.functional
class TestContentAnalysisOrchestratorFunctionality:
    """Test Content Analysis Orchestrator functionality."""
    
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
    def mock_content_processing_agent(self):
        """Create mock Content Processing Agent."""
        agent = Mock()
        agent.process_content = AsyncMock(return_value={
            "status": "success",
            "result": {"analysis": "content analyzed"}
        })
        return agent
    
    @pytest.fixture
    def mock_content_liaison_agent(self):
        """Create mock Content Liaison Agent."""
        agent = Mock()
        agent.route_request = AsyncMock(return_value={
            "status": "success",
            "routed_to": "content_processing_agent"
        })
        return agent
    
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
    async def content_analysis_orchestrator(self, mock_delivery_manager, mock_content_processing_agent, mock_content_liaison_agent):
        """Create Content Analysis Orchestrator instance."""

        # Ensure correct path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../symphainy-platform')))
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(
            delivery_manager=mock_delivery_manager
        )
        
        # Mock agents
        orchestrator.content_processing_agent = mock_content_processing_agent
        orchestrator.content_liaison_agent = mock_content_liaison_agent
        
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_analyze_content(self, content_analysis_orchestrator, mock_content_processing_agent):
        """Test content analysis coordination."""
        content_data = get_sample_document("text")
        
        result = await content_analysis_orchestrator.analyze_content(
            content=content_data,
            options={"analysis_type": "full"}
        )
        
        assert result is not None
        assert isinstance(result, dict)
        # Should have analysis result structure
        assert "status" in result or "analysis" in result
    
    @pytest.mark.asyncio
    async def test_coordinate_agents(self, content_analysis_orchestrator, mock_content_liaison_agent):
        """Test agent coordination."""
        request = {
            "type": "content_analysis",
            "data": get_sample_document("text")
        }
        
        result = await content_analysis_orchestrator.coordinate_agents(request)
        
        assert result is not None
        assert isinstance(result, dict)
        # Should indicate successful coordination
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_agent_routing(self, content_analysis_orchestrator, mock_content_liaison_agent):
        """Test that orchestrator routes requests to correct agents."""
        user_message = "Analyze this document for key insights"
        
        # Mock liaison agent response
        mock_response = get_liaison_agent_response(user_message, {})
        mock_content_liaison_agent.route_request.return_value = mock_response
        
        result = await content_analysis_orchestrator.coordinate_agents({
            "user_message": user_message,
            "type": "content_analysis"
        })
        
        assert result is not None
        # Should route to appropriate agent
        assert mock_content_liaison_agent.route_request.called

