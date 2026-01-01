#!/usr/bin/env python3
"""
Liaison Agent Unit Tests

Tests for all 4 Liaison Agents (Content, Insights, Operations, Business Outcomes).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from utilities import UserContext

@pytest.mark.unit
@pytest.mark.agentic
class TestLiaisonAgentsUnit:
    """Unit tests for Liaison Agents."""
    
    # ========================================================================
    # CONTENT LIAISON AGENT TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_content_liaison_initialization(self, mock_di_container):
        """Test Content Liaison Agent initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        
        liaison = ContentLiaisonAgent(di_container=mock_di_container)
        
        assert liaison.agent_name == "ContentLiaisonAgent"
        assert liaison.business_domain == "content_management"
        assert liaison.content_orchestrator is None  # Not initialized yet
    
    @pytest.mark.asyncio
    async def test_content_liaison_discovers_orchestrator(self, mock_di_container, mock_curator):
        """Test Content Liaison discovers ContentAnalysisOrchestrator."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        
        mock_orch = MagicMock()
        mock_curator.get_service = AsyncMock(return_value=mock_orch)
        mock_di_container.curator = mock_curator
        
        liaison = ContentLiaisonAgent(di_container=mock_di_container)
        await liaison.initialize()
        
        assert liaison.content_orchestrator is not None
        assert liaison.content_orchestrator == mock_orch
        assert liaison.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_content_liaison_processes_user_query(self, mock_di_container):
        """Test Content Liaison can process user queries."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        
        liaison = ContentLiaisonAgent(di_container=mock_di_container)
        liaison.content_orchestrator = MagicMock()
        liaison.is_initialized = True
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await liaison.process_user_query(
            query="Help me analyze a document",
            conversation_id="conv_789",
            user_context=user_context
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["agent"] == "content_liaison"
        assert result["conversation_id"] == "conv_789"
    
    # ========================================================================
    # INSIGHTS LIAISON AGENT TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_insights_liaison_initialization(self, mock_di_container):
        """Test Insights Liaison Agent initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.agents import InsightsLiaisonAgent
        
        liaison = InsightsLiaisonAgent(di_container=mock_di_container)
        
        assert liaison.agent_name == "InsightsLiaisonAgent"
        assert liaison.business_domain == "insights_analysis"
        assert liaison.insights_orchestrator is None
    
    @pytest.mark.asyncio
    async def test_insights_liaison_processes_user_query(self, mock_di_container):
        """Test Insights Liaison can process user queries."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.agents import InsightsLiaisonAgent
        
        liaison = InsightsLiaisonAgent(di_container=mock_di_container)
        liaison.insights_orchestrator = MagicMock()
        liaison.is_initialized = True
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await liaison.process_user_query(
            query="Show me insights from my data",
            conversation_id="conv_789",
            user_context=user_context
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["agent"] == "insights_liaison"
    
    # ========================================================================
    # OPERATIONS LIAISON AGENT TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_operations_liaison_initialization(self, mock_di_container):
        """Test Operations Liaison Agent initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.agents import OperationsLiaisonAgent
        
        liaison = OperationsLiaisonAgent(di_container=mock_di_container)
        
        assert liaison.agent_name == "OperationsLiaisonAgent"
        assert liaison.business_domain == "operations_management"
        assert liaison.operations_orchestrator is None
    
    @pytest.mark.asyncio
    async def test_operations_liaison_processes_user_query(self, mock_di_container):
        """Test Operations Liaison can process user queries."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.agents import OperationsLiaisonAgent
        
        liaison = OperationsLiaisonAgent(di_container=mock_di_container)
        liaison.operations_orchestrator = MagicMock()
        liaison.is_initialized = True
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await liaison.process_user_query(
            query="Help me create an SOP",
            conversation_id="conv_789",
            user_context=user_context
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["agent"] == "operations_liaison"
    
    # ========================================================================
    # BUSINESS OUTCOMES LIAISON AGENT TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_business_outcomes_liaison_initialization(self, mock_di_container):
        """Test Business Outcomes Liaison Agent initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.agents import BusinessOutcomesLiaisonAgent
        
        liaison = BusinessOutcomesLiaisonAgent(di_container=mock_di_container)
        
        assert liaison.agent_name == "BusinessOutcomesLiaisonAgent"
        assert liaison.business_domain == "business_outcomes_management"
        assert liaison.business_outcomes_orchestrator is None
    
    @pytest.mark.asyncio
    async def test_business_outcomes_liaison_processes_user_query(self, mock_di_container):
        """Test Business Outcomes Liaison can process user queries."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.agents import BusinessOutcomesLiaisonAgent
        
        liaison = BusinessOutcomesLiaisonAgent(di_container=mock_di_container)
        liaison.business_outcomes_orchestrator = MagicMock()
        liaison.is_initialized = True
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await liaison.process_user_query(
            query="Calculate ROI for my project",
            conversation_id="conv_789",
            user_context=user_context
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["agent"] == "business_outcomes_liaison"
    
    # ========================================================================
    # CROSS-LIAISON TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_all_liaisons_have_consistent_interface(self, mock_di_container):
        """Test all liaison agents have consistent process_user_query interface."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.agents import InsightsLiaisonAgent
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.agents import OperationsLiaisonAgent
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.agents import BusinessOutcomesLiaisonAgent
        
        liaisons = [
            ContentLiaisonAgent(di_container=mock_di_container),
            InsightsLiaisonAgent(di_container=mock_di_container),
            OperationsLiaisonAgent(di_container=mock_di_container),
            BusinessOutcomesLiaisonAgent(di_container=mock_di_container)
        ]
        
        # All should have process_user_query method
        for liaison in liaisons:
            assert hasattr(liaison, 'process_user_query')
            assert callable(liaison.process_user_query)
    
    @pytest.mark.asyncio
    async def test_liaison_agents_handle_different_query_types(self, mock_di_container):
        """Test liaison agents provide contextual responses."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.agents import ContentLiaisonAgent
        
        liaison = ContentLiaisonAgent(di_container=mock_di_container)
        liaison.content_orchestrator = MagicMock()
        liaison.is_initialized = True
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        # Test different query types
        queries = [
            "upload a document",
            "analyze content",
            "parse a file",
            "help me"
        ]
        
        for query in queries:
            result = await liaison.process_user_query(
                query=query,
                conversation_id="conv_test",
                user_context=user_context
            )
            
            assert result["success"] is True
            assert "response" in result
            assert len(result["response"]) > 0

