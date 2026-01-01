"""
Unit tests for LiaisonDomainAgent

Tests the SDK-first, domain-configurable liaison agent pattern.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from backend.business_enablement.agents.liaison_domain_agent import LiaisonDomainAgent
from backend.business_enablement.agents.mvp_liaison_agents import MVPLiaisonAgents

class TestLiaisonDomainAgent:
    """Test suite for LiaisonDomainAgent."""
    
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
    def content_domain_config(self):
        """Create test domain configuration for content management."""
        return {
            "capabilities": ["file_upload", "file_parsing", "content_validation"],
            "orchestrator": "ContentAnalysisOrchestrator",
            "mcp_tools": ["upload_file", "parse_file"],
            "description": "Manage file uploads and content processing"
        }
    
    def test_liaison_agent_initialization(self, mock_services, content_domain_config):
        """Test Liaison Agent initialization."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        assert agent is not None
        assert agent.domain_name == "content_management"
        assert agent.domain_config == content_domain_config
        assert agent.orchestrator is None  # Not initialized yet
        assert agent.orchestrator_name == "ContentAnalysisOrchestrator"
    
    @pytest.mark.asyncio
    async def test_initialize_discovers_orchestrator(self, mock_services, content_domain_config):
        """Test initialization discovers orchestrator."""
        mock_orchestrator = MagicMock()
        mock_services['curator_foundation'].get_service = AsyncMock(return_value=mock_orchestrator)
        
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        await agent.initialize()
        
        assert agent.orchestrator == mock_orchestrator
        mock_services['curator_foundation'].get_service.assert_called_once_with("ContentAnalysisOrchestrator")
    
    @pytest.mark.asyncio
    async def test_handle_user_request_simple_intent(self, mock_services, content_domain_config):
        """Test handling user request with simple intent."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        request = {
            "message": "Can you help me validate a file?",
            "user_context": {}
        }
        
        result = await agent.handle_user_request(request)
        
        assert result is not None
        assert 'success' in result
        assert 'response' in result
    
    @pytest.mark.asyncio
    async def test_handle_user_request_with_orchestrator_delegation(self, mock_services, content_domain_config):
        """Test handling request that requires orchestrator delegation."""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "results": "Processed by orchestrator"
        })
        
        mock_services['curator_foundation'].get_service = AsyncMock(return_value=mock_orchestrator)
        
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        await agent.initialize()
        
        request = {
            "message": "I need to upload and parse multiple files",
            "user_context": {},
            "parameters": {}
        }
        
        result = await agent.handle_user_request(request)
        
        assert result is not None
        # Note: Actual delegation depends on intent analysis
    
    @pytest.mark.asyncio
    async def test_analyze_intent_upload_action(self, mock_services, content_domain_config):
        """Test intent analysis for upload action."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        request = {
            "message": "I want to upload a document",
            "user_context": {}
        }
        
        result = await agent.analyze_intent(request)
        
        assert result is not None
        assert 'intent' in result
        assert 'action' in result
        assert 'confidence' in result
        assert result['intent'] == "upload"
    
    @pytest.mark.asyncio
    async def test_analyze_intent_parse_action(self, mock_services, content_domain_config):
        """Test intent analysis for parse action."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        request = {
            "message": "Can you parse this CSV file?",
            "user_context": {}
        }
        
        result = await agent.analyze_intent(request)
        
        assert result is not None
        assert result['intent'] == "parse"
    
    @pytest.mark.asyncio
    async def test_add_and_get_user_session(self, mock_services, content_domain_config):
        """Test adding and retrieving user session."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        session_data = {
            "context": {"file_count": 5}
        }
        
        await agent.add_user_session("test_user", session_data)
        
        session = await agent.get_user_session("test_user")
        
        assert session is not None
        assert session['domain'] == "content_management"
        assert "test_user" in agent.active_sessions
    
    def test_get_agent_capabilities(self, mock_services, content_domain_config):
        """Test getting agent capabilities."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        capabilities = agent.get_agent_capabilities()
        
        assert "file_upload" in capabilities
        assert "file_parsing" in capabilities
        assert "content_validation" in capabilities
    
    def test_get_agent_description(self, mock_services, content_domain_config):
        """Test getting agent description."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        description = agent.get_agent_description()
        
        assert "Content Management" in description
        assert "content_management" in description.lower()
    
    @pytest.mark.asyncio
    async def test_process_request(self, mock_services, content_domain_config):
        """Test process_request method (AgentBase interface)."""
        agent = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config=content_domain_config,
            **mock_services
        )
        
        request = {
            "message": "Help me upload a file",
            "user_context": {}
        }
        
        result = await agent.process_request(request)
        
        assert result is not None
        assert 'success' in result

class TestMVPLiaisonAgents:
    """Test suite for MVP Liaison Agents factory."""
    
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
    async def test_create_all_mvp_liaison_agents(self, mock_services):
        """Test creating all MVP liaison agents via factory."""
        mock_services['curator_foundation'].get_service = AsyncMock(return_value=None)
        
        agents = await MVPLiaisonAgents.create_all(**mock_services)
        
        assert agents is not None
        assert len(agents) == 4
        assert "content_management" in agents
        assert "insights_analysis" in agents
        assert "operations_management" in agents
        assert "business_outcomes" in agents
        
        # Verify each agent is correct type
        for domain, agent in agents.items():
            assert isinstance(agent, LiaisonDomainAgent)
            assert agent.domain_name == domain
    
    @pytest.mark.asyncio
    async def test_create_single_mvp_liaison_agent(self, mock_services):
        """Test creating single MVP liaison agent via factory."""
        mock_services['curator_foundation'].get_service = AsyncMock(return_value=None)
        
        agent = await MVPLiaisonAgents.create_single(
            domain_name="content_management",
            **mock_services
        )
        
        assert agent is not None
        assert isinstance(agent, LiaisonDomainAgent)
        assert agent.domain_name == "content_management"
    
    @pytest.mark.asyncio
    async def test_create_single_unknown_domain_raises_error(self, mock_services):
        """Test creating single agent with unknown domain raises error."""
        with pytest.raises(ValueError, match="Unknown MVP domain"):
            await MVPLiaisonAgents.create_single(
                domain_name="unknown_domain",
                **mock_services
            )
    
    def test_get_domain_config(self):
        """Test getting domain configuration."""
        config = MVPLiaisonAgents.get_domain_config("content_management")
        
        assert config is not None
        assert "capabilities" in config
        assert "orchestrator" in config
        assert config['orchestrator'] == "ContentAnalysisOrchestrator"
    
    def test_get_all_domains(self):
        """Test getting all MVP domains."""
        domains = MVPLiaisonAgents.get_all_domains()
        
        assert len(domains) == 4
        assert "content_management" in domains
        assert "insights_analysis" in domains
        assert "operations_management" in domains
        assert "business_outcomes" in domains
    
    def test_get_all_configs(self):
        """Test getting all domain configurations."""
        configs = MVPLiaisonAgents.get_all_configs()
        
        assert len(configs) == 4
        assert "content_management" in configs
        assert "capabilities" in configs["content_management"]

class TestDomainConfigurability:
    """Test suite for domain configurability (extensibility tests)."""
    
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
    
    def test_create_data_mash_liaison_agent(self, mock_services):
        """Test creating liaison agent for Data Mash domain (future use case)."""
        # Demonstrates extensibility - same agent type, different domain!
        data_mash_config = {
            "capabilities": ["metadata_extraction", "schema_detection", "lineage_tracking"],
            "orchestrator": "MetadataExtractionService",
            "mcp_tools": ["extract_metadata", "detect_schema"],
            "description": "Extract metadata and track data lineage"
        }
        
        agent = LiaisonDomainAgent(
            domain_name="metadata_extraction",
            domain_config=data_mash_config,
            **mock_services
        )
        
        assert agent is not None
        assert agent.domain_name == "metadata_extraction"
        assert "metadata_extraction" in agent.get_agent_capabilities()
    
    def test_create_apg_liaison_agent(self, mock_services):
        """Test creating liaison agent for APG domain (future use case)."""
        # Demonstrates extensibility - same agent type, different domain!
        apg_config = {
            "capabilities": ["test_coordination", "vehicle_management", "scenario_execution"],
            "orchestrator": "TestOrchestrationService",
            "mcp_tools": ["coordinate_test", "manage_vehicle"],
            "description": "Coordinate autonomous vehicle testing"
        }
        
        agent = LiaisonDomainAgent(
            domain_name="test_orchestration",
            domain_config=apg_config,
            **mock_services
        )
        
        assert agent is not None
        assert agent.domain_name == "test_orchestration"
        assert "test_coordination" in agent.get_agent_capabilities()

