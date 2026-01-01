"""
Unit tests for GuideCrossDomainAgent

Tests the SDK-first, domain-configurable guide agent pattern.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from backend.business_enablement.agents.guide_cross_domain_agent import GuideCrossDomainAgent
from backend.business_enablement.agents.mvp_guide_agent import MVPGuideAgent

class TestGuideCrossDomainAgent:
    """Test suite for GuideCrossDomainAgent."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        return {
            'foundation_services': MagicMock(),
            'agentic_foundation': MagicMock(),
            'mcp_client_manager': MagicMock(),
            'policy_integration': MagicMock(),
            'tool_composition': MagicMock(),
            'agui_formatter': MagicMock(),
            'curator_foundation': MagicMock(),
            'metadata_foundation': MagicMock()
        }
    
    @pytest.fixture
    def solution_config(self):
        """Create test solution configuration."""
        return {
            "name": "Test Solution",
            "description": "Test solution for unit testing",
            "domains": ["test_domain_1", "test_domain_2"],
            "version": "1.0.0"
        }
    
    def test_guide_agent_initialization(self, mock_services, solution_config):
        """Test Guide Agent initialization."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        assert agent is not None
        assert agent.solution_config == solution_config
        assert agent.liaison_agents == {}
        assert agent.configured_domains == []
        assert agent.solution_type is None
    
    @pytest.mark.asyncio
    async def test_configure_for_mvp_solution(self, mock_services, solution_config):
        """Test configuring Guide Agent for MVP solution."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        result = await agent.configure_for_solution("mvp")
        
        assert result['success'] is True
        assert result['solution_type'] == "mvp"
        assert len(result['domains_configured']) == 4
        assert "content_management" in result['domains_configured']
        assert "insights_analysis" in result['domains_configured']
        assert "operations_management" in result['domains_configured']
        assert "business_outcomes" in result['domains_configured']
    
    @pytest.mark.asyncio
    async def test_configure_for_data_mash_solution(self, mock_services, solution_config):
        """Test configuring Guide Agent for Data Mash solution."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        result = await agent.configure_for_solution("data_mash")
        
        assert result['success'] is True
        assert result['solution_type'] == "data_mash"
        assert len(result['domains_configured']) == 4
        assert "metadata_extraction" in result['domains_configured']
        assert "schema_alignment" in result['domains_configured']
    
    @pytest.mark.asyncio
    async def test_configure_for_unknown_solution_raises_error(self, mock_services, solution_config):
        """Test that configuring for unknown solution raises error."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        with pytest.raises(ValueError, match="Unknown solution type"):
            await agent.configure_for_solution("unknown_solution")
    
    @pytest.mark.asyncio
    async def test_analyze_cross_dimensional_intent_content(self, mock_services, solution_config):
        """Test intent analysis for content-related request."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        await agent.configure_for_solution("mvp")
        
        request = {
            "message": "I want to upload a PDF document",
            "user_context": {}
        }
        
        result = await agent.analyze_cross_dimensional_intent(request)
        
        assert result['success'] is True
        assert result['target_domain'] == "content_management"
        assert result['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_cross_dimensional_intent_insights(self, mock_services, solution_config):
        """Test intent analysis for insights-related request."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        await agent.configure_for_solution("mvp")
        
        request = {
            "message": "Show me data analysis and trends",
            "user_context": {}
        }
        
        result = await agent.analyze_cross_dimensional_intent(request)
        
        assert result['success'] is True
        assert result['target_domain'] == "insights_analysis"
        assert result['confidence'] > 0
    
    @pytest.mark.asyncio
    async def test_provide_guidance_with_liaison_routing(self, mock_services, solution_config):
        """Test guidance provision with liaison agent routing."""
        # Mock liaison agent
        mock_liaison = AsyncMock()
        mock_liaison.handle_user_request = AsyncMock(return_value={
            "success": True,
            "response": "Handled by liaison"
        })
        
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        await agent.configure_for_solution("mvp")
        
        # Inject mock liaison agent
        agent.liaison_agents['content_management'] = mock_liaison
        
        request = {
            "message": "Upload a file",
            "user_context": {}
        }
        
        result = await agent.provide_guidance(request)
        
        assert result['success'] is True
        assert result['response_type'] == "liaison_routed"
        assert result['domain'] == "content_management"
        mock_liaison.handle_user_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_provide_general_guidance(self, mock_services, solution_config):
        """Test general guidance when no specific domain detected."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        await agent.configure_for_solution("mvp")
        
        request = {
            "message": "Hello, can you help me?",
            "user_context": {}
        }
        
        result = await agent.provide_guidance(request)
        
        assert result['success'] is True
        assert result['response_type'] == "general_guidance"
        assert 'guidance' in result
        assert 'available_domains' in result
    
    @pytest.mark.asyncio
    async def test_track_user_journey(self, mock_services, solution_config):
        """Test user journey tracking."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        journey_data = {
            "domains_visited": ["content_management"],
            "current_domain": "content_management",
            "user_context": {"user_id": "test_user"}
        }
        
        await agent.track_user_journey("test_user", journey_data)
        
        journey = await agent.get_user_journey("test_user")
        
        assert journey is not None
        assert journey['current_domain'] == "content_management"
        assert "test_user" in agent.active_journeys
    
    def test_get_agent_capabilities(self, mock_services, solution_config):
        """Test getting agent capabilities."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        capabilities = agent.get_agent_capabilities()
        
        assert "cross_domain_intent_analysis" in capabilities
        assert "liaison_agent_routing" in capabilities
        assert "user_journey_tracking" in capabilities
    
    def test_get_agent_description(self, mock_services, solution_config):
        """Test getting agent description."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        description = agent.get_agent_description()
        
        assert "GuideCrossDomainAgent" in description
        assert "cross-domain" in description.lower()
    
    @pytest.mark.asyncio
    async def test_process_request(self, mock_services, solution_config):
        """Test process_request method (AgentBase interface)."""
        agent = GuideCrossDomainAgent(
            solution_config=solution_config,
            **mock_services
        )
        
        await agent.configure_for_solution("mvp")
        
        request = {
            "message": "Help me",
            "user_context": {}
        }
        
        result = await agent.process_request(request)
        
        assert result is not None
        assert 'success' in result

class TestMVPGuideAgent:
    """Test suite for MVP Guide Agent factory."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        return {
            'foundation_services': MagicMock(),
            'agentic_foundation': MagicMock(),
            'mcp_client_manager': MagicMock(),
            'policy_integration': MagicMock(),
            'tool_composition': MagicMock(),
            'agui_formatter': MagicMock(),
            'curator_foundation': MagicMock(),
            'metadata_foundation': MagicMock()
        }
    
    @pytest.mark.asyncio
    async def test_create_mvp_guide_agent(self, mock_services):
        """Test creating MVP Guide Agent via factory."""
        agent = await MVPGuideAgent.create(**mock_services)
        
        assert agent is not None
        assert isinstance(agent, GuideCrossDomainAgent)
        assert agent.solution_type == "mvp"
        assert len(agent.configured_domains) == 4
    
    def test_get_mvp_config(self):
        """Test getting MVP configuration."""
        config = MVPGuideAgent.get_mvp_config()
        
        assert config['name'] == "MVP"
        assert len(config['domains']) == 4
        assert "content_management" in config['domains']

