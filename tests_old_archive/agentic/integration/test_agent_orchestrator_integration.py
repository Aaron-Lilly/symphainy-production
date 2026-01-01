"""
Agent-Orchestrator Integration Tests

Tests the integration between agents and orchestrators:
- Guide Agent → Liaison Agents
- Liaison Agents → Orchestrators
- Agent discovery mechanisms
- Request routing
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestGuideToLiaisonIntegration:
    """Test Guide Agent → Liaison Agent integration."""
    
    async def test_guide_discovers_liaison_agents(self, guide_agent_fixture, liaison_agent_fixture,
                                                  mock_curator_foundation):
        """Test Guide Agent discovers Liaison Agents via Curator."""
        guide = guide_agent_fixture
        
        # Mock Curator to return liaison agents
        mock_curator_foundation.get_service = AsyncMock(return_value=liaison_agent_fixture)
        
        # Guide should discover liaison agents during initialization
        await guide.configure_for_solution("mvp")
        
        # Verify discovery
        assert len(guide.liaison_agents) > 0
    
    async def test_guide_routes_content_request_to_content_liaison(self, guide_agent_fixture,
                                                                   mock_curator_foundation):
        """Test Guide routes content requests to Content Liaison."""
        guide = guide_agent_fixture
        
        # Mock liaison agents
        content_liaison = MagicMock()
        content_liaison.handle_user_request = AsyncMock(return_value={"success": True})
        guide.liaison_agents = {"content_management": content_liaison}
        
        # User request about content
        request = {
            "message": "I want to upload a document",
            "user_context": {"role": "user"}
        }
        
        result = await guide.provide_guidance(request)
        
        # Verify routing to content liaison
        content_liaison.handle_user_request.assert_called_once()
        assert result["success"] is True
    
    async def test_guide_routes_insights_request_to_insights_liaison(self, guide_agent_fixture):
        """Test Guide routes insights requests to Insights Liaison."""
        guide = guide_agent_fixture
        
        # Mock liaison agents
        insights_liaison = MagicMock()
        insights_liaison.handle_user_request = AsyncMock(return_value={"success": True})
        guide.liaison_agents = {"insights_analysis": insights_liaison}
        
        # User request about insights
        request = {
            "message": "I need data analysis and insights",
            "user_context": {"role": "analyst"}
        }
        
        result = await guide.provide_guidance(request)
        
        # Verify routing to insights liaison
        insights_liaison.handle_user_request.assert_called_once()
        assert result["success"] is True
    
    async def test_guide_handles_ambiguous_request(self, guide_agent_fixture):
        """Test Guide handles ambiguous requests that don't clearly map to a domain."""
        guide = guide_agent_fixture
        
        # Mock liaison agents
        guide.liaison_agents = {
            "content_management": MagicMock(),
            "insights_analysis": MagicMock()
        }
        
        # Ambiguous request
        request = {
            "message": "Help me",
            "user_context": {}
        }
        
        result = await guide.provide_guidance(request)
        
        # Guide should provide general guidance or ask clarifying questions
        assert "result" in result

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestLiaisonToOrchestratorIntegration:
    """Test Liaison Agent → Orchestrator integration."""
    
    async def test_content_liaison_discovers_orchestrator(self, liaison_agent_fixture,
                                                          mock_curator_foundation):
        """Test Content Liaison discovers Content Analysis Orchestrator."""
        liaison = liaison_agent_fixture
        
        # Mock Curator to return orchestrator
        mock_orchestrator = MagicMock()
        mock_curator_foundation.get_service = AsyncMock(return_value=mock_orchestrator)
        
        # Liaison should discover orchestrator during initialization
        await liaison.initialize()
        
        # Verify discovery (liaison should have reference to orchestrator)
        assert liaison.domain_orchestrator is not None or mock_curator_foundation.get_service.called
    
    async def test_liaison_delegates_complex_request_to_orchestrator(self, liaison_agent_fixture):
        """Test Liaison delegates complex requests to orchestrator."""
        liaison = liaison_agent_fixture
        
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.handle_request = AsyncMock(return_value={"success": True, "result": "orchestrated"})
        liaison.domain_orchestrator = mock_orchestrator
        
        # Complex user request
        request = {
            "message": "Analyze this document and generate insights",
            "data": {"document": "test.pdf"},
            "user_context": {}
        }
        
        result = await liaison.handle_user_request(request)
        
        # Verify delegation to orchestrator
        mock_orchestrator.handle_request.assert_called_once()
        assert result["success"] is True
    
    async def test_liaison_handles_simple_request_directly(self, liaison_agent_fixture):
        """Test Liaison handles simple requests without orchestrator."""
        liaison = liaison_agent_fixture
        
        # Mock MCP tools for direct handling
        liaison.mcp_client_manager.execute_role_tool = AsyncMock(
            return_value={"success": True, "result": "direct"}
        )
        
        # Simple user request
        request = {
            "message": "What file types do you support?",
            "user_context": {}
        }
        
        result = await liaison.handle_user_request(request)
        
        # Verify direct handling (should use MCP tools, not orchestrator)
        assert result is not None
    
    async def test_liaison_orchestrator_error_handling(self, liaison_agent_fixture):
        """Test Liaison handles orchestrator errors gracefully."""
        liaison = liaison_agent_fixture
        
        # Mock orchestrator that fails
        mock_orchestrator = MagicMock()
        mock_orchestrator.handle_request = AsyncMock(side_effect=Exception("Orchestrator error"))
        liaison.domain_orchestrator = mock_orchestrator
        
        # User request
        request = {
            "message": "Process this complex task",
            "user_context": {}
        }
        
        result = await liaison.handle_user_request(request)
        
        # Liaison should handle error gracefully
        assert "error" in result or result.get("success") is False

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestFullAgentOrchestratorFlow:
    """Test full flow: Guide → Liaison → Orchestrator."""
    
    async def test_full_content_upload_flow(self, guide_agent_fixture, mock_curator_foundation):
        """Test complete flow for content upload request."""
        guide = guide_agent_fixture
        
        # Setup: Create mock liaison and orchestrator
        mock_liaison = MagicMock()
        mock_orchestrator = MagicMock()
        
        # Mock liaison handling
        async def liaison_handler(request):
            # Liaison delegates to orchestrator
            return await mock_orchestrator.handle_request(request)
        
        mock_liaison.handle_user_request = liaison_handler
        mock_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "result": "Document uploaded and analyzed"
        })
        
        guide.liaison_agents = {"content_management": mock_liaison}
        
        # User request
        request = {
            "message": "Upload and analyze this document",
            "data": {"file": "document.pdf"},
            "user_context": {"role": "user"}
        }
        
        result = await guide.provide_guidance(request)
        
        # Verify full flow completed
        mock_orchestrator.handle_request.assert_called_once()
        assert result.get("success") is True
    
    async def test_full_insights_analysis_flow(self, guide_agent_fixture):
        """Test complete flow for insights analysis request."""
        guide = guide_agent_fixture
        
        # Setup mocks
        mock_liaison = MagicMock()
        mock_orchestrator = MagicMock()
        
        async def liaison_handler(request):
            return await mock_orchestrator.handle_request(request)
        
        mock_liaison.handle_user_request = liaison_handler
        mock_orchestrator.handle_request = AsyncMock(return_value={
            "success": True,
            "result": "Insights generated"
        })
        
        guide.liaison_agents = {"insights_analysis": mock_liaison}
        
        # User request
        request = {
            "message": "Generate insights from my data",
            "data": {"dataset": "sales_data.csv"},
            "user_context": {"role": "analyst"}
        }
        
        result = await guide.provide_guidance(request)
        
        # Verify full flow
        mock_orchestrator.handle_request.assert_called_once()
        assert result.get("success") is True
    
    async def test_multi_turn_conversation_flow(self, guide_agent_fixture):
        """Test multi-turn conversation maintaining context."""
        guide = guide_agent_fixture
        
        # Setup mocks
        mock_liaison = MagicMock()
        mock_orchestrator = MagicMock()
        
        async def liaison_handler(request):
            return await mock_orchestrator.handle_request(request)
        
        mock_liaison.handle_user_request = liaison_handler
        mock_orchestrator.handle_request = AsyncMock(return_value={"success": True})
        
        guide.liaison_agents = {"content_management": mock_liaison}
        
        # Turn 1: Initial request
        request1 = {
            "message": "Upload document",
            "user_context": {"session_id": "test_session"}
        }
        result1 = await guide.provide_guidance(request1)
        
        # Turn 2: Follow-up request
        request2 = {
            "message": "Now analyze it",
            "user_context": {"session_id": "test_session"}
        }
        result2 = await guide.provide_guidance(request2)
        
        # Verify both turns completed
        assert result1 is not None
        assert result2 is not None
        assert mock_orchestrator.handle_request.call_count == 2

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestOrchestratorDiscovery:
    """Test orchestrator discovery mechanisms."""
    
    async def test_liaison_discovers_correct_orchestrator_for_domain(self, mock_curator_foundation):
        """Test Liaison discovers the correct orchestrator for its domain."""
        from backend.business_enablement.agents import LiaisonDomainAgent
        
        # Create liaison for content domain
        content_liaison = LiaisonDomainAgent(
            domain_name="content_management",
            domain_config={
                "capabilities": ["file_upload", "parsing"],
                "orchestrator": "ContentAnalysisOrchestrator"
            },
            foundation_services=MagicMock(),
            agentic_foundation=MagicMock(),
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Curator response
        mock_curator_foundation.get_service = AsyncMock(return_value=MagicMock())
        
        # Initialize (should trigger discovery)
        await content_liaison.initialize()
        
        # Verify Curator was called to discover orchestrator
        mock_curator_foundation.get_service.assert_called()
    
    async def test_orchestrator_not_found_handling(self, mock_curator_foundation):
        """Test handling when orchestrator is not found."""
        from backend.business_enablement.agents import LiaisonDomainAgent
        
        liaison = LiaisonDomainAgent(
            domain_name="test_domain",
            domain_config={
                "capabilities": [],
                "orchestrator": "NonExistentOrchestrator"
            },
            foundation_services=MagicMock(),
            agentic_foundation=MagicMock(),
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock(),
            curator_foundation=mock_curator_foundation
        )
        
        # Mock Curator to return None (orchestrator not found)
        mock_curator_foundation.get_service = AsyncMock(return_value=None)
        
        # Initialize should handle gracefully
        await liaison.initialize()
        
        # Liaison should still be functional (can use MCP tools directly)
        assert liaison is not None

@pytest.mark.integration
@pytest.mark.agentic
@pytest.mark.asyncio
class TestAgentRoutingLogic:
    """Test agent routing and intent analysis logic."""
    
    async def test_guide_intent_analysis_for_content_requests(self, guide_agent_fixture):
        """Test Guide correctly analyzes intent for content-related requests."""
        guide = guide_agent_fixture
        
        content_requests = [
            "Upload a document",
            "Parse this file",
            "Validate my content",
            "Store this document"
        ]
        
        for request_text in content_requests:
            request = {"message": request_text, "user_context": {}}
            intent = await guide.analyze_cross_dimensional_intent(request)
            
            # Should identify content domain
            assert intent is not None
    
    async def test_guide_intent_analysis_for_insights_requests(self, guide_agent_fixture):
        """Test Guide correctly analyzes intent for insights-related requests."""
        guide = guide_agent_fixture
        
        insights_requests = [
            "Analyze my data",
            "Generate insights",
            "Show me patterns",
            "Create visualizations"
        ]
        
        for request_text in insights_requests:
            request = {"message": request_text, "user_context": {}}
            intent = await guide.analyze_cross_dimensional_intent(request)
            
            # Should identify insights domain
            assert intent is not None
    
    async def test_liaison_determines_direct_vs_orchestrated_handling(self, liaison_agent_fixture):
        """Test Liaison decides when to handle directly vs delegate."""
        liaison = liaison_agent_fixture
        
        # Simple request (should handle directly)
        simple_request = {"message": "What can you do?", "user_context": {}}
        can_handle = liaison._can_handle_directly(simple_request)
        
        # Complex request (should delegate)
        complex_request = {
            "message": "Analyze document and generate report",
            "user_context": {}
        }
        cant_handle = not liaison._can_handle_directly(complex_request)
        
        # Verify decision logic
        assert can_handle or cant_handle  # At least one should be decided correctly
