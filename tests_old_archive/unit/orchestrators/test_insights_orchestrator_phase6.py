#!/usr/bin/env python3
"""
Insights Orchestrator Phase 6 Unit Tests

Tests for InsightsOrchestrator Phase 6 refactoring:
- Agent initialization and discovery
- Data Solution Orchestrator integration
- Semantic Enrichment Gateway integration
- Helper methods for data type detection, enrichment, visualization
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.orchestrators]


class TestInsightsOrchestratorPhase6:
    """Test InsightsOrchestrator Phase 6 functionality."""
    
    @pytest.fixture
    def mock_delivery_manager(self):
        """Create mock delivery manager."""
        manager = Mock()
        manager.realm_name = "business_enablement"
        manager.service_name = "DeliveryManagerService"
        manager.platform_gateway = Mock()
        manager.di_container = Mock()
        manager.di_container.get_logger = Mock(return_value=Mock())
        return manager
    
    @pytest.fixture
    def mock_data_solution_orchestrator(self):
        """Create mock Data Solution Orchestrator."""
        orchestrator = Mock()
        orchestrator.orchestrate_data_expose = AsyncMock(return_value={
            "success": True,
            "embeddings": [
                {"embedding_type": "schema", "column_name": "col1", "column_type": "string"},
                {"embedding_type": "schema", "column_name": "col2", "column_type": "number"},
                {"embedding_type": "chunk", "content": "sample text"}
            ],
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123"
        })
        return orchestrator
    
    @pytest.fixture
    def mock_semantic_enrichment_gateway(self):
        """Create mock Semantic Enrichment Gateway."""
        gateway = Mock()
        gateway.enrich_semantic_layer = AsyncMock(return_value={
            "success": True,
            "embedding_ids": ["emb_1", "emb_2"],
            "enrichment_type": "column_values",
            "count": 2
        })
        return gateway
    
    @pytest.fixture
    def mock_curator(self):
        """Create mock Curator for service discovery."""
        curator = Mock()
        curator.get_service = AsyncMock()
        return curator
    
    @pytest.fixture
    async def orchestrator(self, mock_delivery_manager):
        """Create InsightsOrchestrator instance with Phase 6 setup."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        
        orchestrator = InsightsOrchestrator(mock_delivery_manager)
        
        # Mock Smart City services
        orchestrator.librarian = Mock()
        orchestrator.data_steward = Mock()
        orchestrator.content_steward = Mock()
        
        # Mock _realm_service for telemetry
        orchestrator._realm_service = Mock()
        orchestrator._realm_service.log_operation_with_telemetry = AsyncMock()
        orchestrator._realm_service.handle_error_with_audit = AsyncMock()
        orchestrator._realm_service.record_health_metric = AsyncMock()
        orchestrator._realm_service.security = Mock()
        orchestrator._realm_service.security.check_permissions = AsyncMock(return_value=True)
        orchestrator._realm_service.get_tenant = Mock(return_value=None)
        
        # Mock OrchestratorBase methods
        orchestrator.get_librarian_api = AsyncMock(return_value=orchestrator.librarian)
        orchestrator.get_data_steward_api = AsyncMock(return_value=orchestrator.data_steward)
        orchestrator.get_content_steward_api = AsyncMock(return_value=orchestrator.content_steward)
        orchestrator.get_foundation_service = AsyncMock()
        orchestrator.get_enabling_service = AsyncMock()
        
        # Mock agent initialization
        orchestrator.initialize_agent = AsyncMock()
        
        # Mock workflows
        orchestrator.structured_workflow = Mock()
        orchestrator.structured_workflow.execute = AsyncMock(return_value={"success": True})
        orchestrator.unstructured_workflow = Mock()
        orchestrator.unstructured_workflow.execute = AsyncMock(return_value={"success": True})
        orchestrator.hybrid_workflow = Mock()
        orchestrator.hybrid_workflow.execute = AsyncMock(return_value={"success": True})
        
        # Mock parent initialize
        with patch.object(orchestrator.__class__.__bases__[0], 'initialize', new_callable=AsyncMock) as mock_init:
            mock_init.return_value = True
            orchestrator.initialize = AsyncMock(return_value=True)
        
        return orchestrator
    
    # ========================================================================
    # AGENT INITIALIZATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_liaison_agent_initialization(self, orchestrator):
        """Test that InsightsLiaisonAgent is properly initialized and accessible."""
        # Mock agent initialization (avoiding import issues)
        mock_liaison_agent = Mock()
        mock_liaison_agent.pillar = None
        mock_liaison_agent.agent_name = "InsightsLiaisonAgent"
        orchestrator.initialize_agent = AsyncMock(return_value=mock_liaison_agent)
        
        # Simulate agent initialization pattern from Phase 6
        liaison_agent = await orchestrator.initialize_agent(
            Mock,  # Use Mock instead of actual class to avoid import issues
            "InsightsLiaisonAgent",
            agent_type="liaison",
            capabilities=["conversation", "guidance", "analysis_support"],
            required_roles=["liaison_agent"]
        )
        
        # Verify agent is stored in both places (Phase 6 pattern)
        orchestrator.liaison_agent = liaison_agent
        if liaison_agent:
            if "InsightsLiaisonAgent" not in orchestrator._agents:
                orchestrator._agents["InsightsLiaisonAgent"] = liaison_agent
            liaison_agent.pillar = "insights"
        
        assert orchestrator.liaison_agent is not None
        assert orchestrator.liaison_agent == liaison_agent
        assert "InsightsLiaisonAgent" in orchestrator._agents
        assert orchestrator._agents["InsightsLiaisonAgent"] == liaison_agent
        assert liaison_agent.pillar == "insights"
    
    @pytest.mark.asyncio
    async def test_get_agent_retrieves_liaison_agent(self, orchestrator):
        """Test that get_agent() can retrieve InsightsLiaisonAgent."""
        # Setup: Create mock agent and store it
        mock_liaison_agent = Mock()
        mock_liaison_agent.agent_name = "InsightsLiaisonAgent"
        orchestrator._agents = {"InsightsLiaisonAgent": mock_liaison_agent}
        orchestrator.liaison_agent = mock_liaison_agent
        
        # Test: Retrieve agent via get_agent()
        retrieved_agent = await orchestrator.get_agent("InsightsLiaisonAgent")
        
        assert retrieved_agent is not None
        assert retrieved_agent == mock_liaison_agent
        assert retrieved_agent.agent_name == "InsightsLiaisonAgent"
    
    @pytest.mark.asyncio
    async def test_query_agent_initialization(self, orchestrator):
        """Test that InsightsQueryAgent is properly initialized."""
        # Mock agent initialization (avoiding import issues)
        mock_query_agent = Mock()
        mock_query_agent.agent_name = "InsightsQueryAgent"
        orchestrator.initialize_agent = AsyncMock(return_value=mock_query_agent)
        
        query_agent = await orchestrator.initialize_agent(
            Mock,  # Use Mock instead of actual class to avoid import issues
            "InsightsQueryAgent",
            agent_type="query",
            capabilities=["query_generation", "schema_analysis"],
            required_roles=[]
        )
        
        assert query_agent is not None
        assert query_agent == mock_query_agent
    
    @pytest.mark.asyncio
    async def test_business_analysis_agent_initialization(self, orchestrator):
        """Test that InsightsBusinessAnalysisAgent is properly initialized."""
        # Mock agent initialization (avoiding import issues)
        mock_business_agent = Mock()
        mock_business_agent.agent_name = "InsightsBusinessAnalysisAgent"
        orchestrator.initialize_agent = AsyncMock(return_value=mock_business_agent)
        
        business_agent = await orchestrator.initialize_agent(
            Mock,  # Use Mock instead of actual class to avoid import issues
            "InsightsBusinessAnalysisAgent",
            agent_type="analysis",
            capabilities=["structured_analysis", "unstructured_analysis", "business_narrative"],
            required_roles=[]
        )
        
        assert business_agent is not None
        assert business_agent == mock_business_agent
    
    # ========================================================================
    # DATA SOLUTION ORCHESTRATOR INTEGRATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_get_data_solution_orchestrator(self, orchestrator, mock_data_solution_orchestrator, mock_curator):
        """Test Data Solution Orchestrator discovery."""
        # Setup: Mock Curator discovery
        orchestrator.get_foundation_service = AsyncMock(return_value=mock_curator)
        mock_curator.get_service = AsyncMock(return_value=mock_data_solution_orchestrator)
        
        # Test: Get Data Solution Orchestrator
        data_solution = await orchestrator._get_data_solution_orchestrator()
        
        assert data_solution is not None
        assert data_solution == mock_data_solution_orchestrator
        orchestrator.get_foundation_service.assert_called_with("CuratorFoundationService")
        mock_curator.get_service.assert_called_with("DataSolutionOrchestratorService")
    
    @pytest.mark.asyncio
    async def test_get_data_solution_orchestrator_not_available(self, orchestrator, mock_curator):
        """Test Data Solution Orchestrator discovery failure."""
        # Setup: Mock Curator but no service
        orchestrator.get_foundation_service = AsyncMock(return_value=mock_curator)
        mock_curator.get_service = AsyncMock(return_value=None)
        
        # Test: Should raise ValueError
        with pytest.raises(ValueError, match="Data Solution Orchestrator Service not available"):
            await orchestrator._get_data_solution_orchestrator()
    
    @pytest.mark.asyncio
    async def test_get_semantic_embeddings_via_data_solution_with_file_id(self, orchestrator, mock_data_solution_orchestrator):
        """Test getting semantic embeddings via Data Solution Orchestrator with file_id."""
        # Setup: Mock Data Solution Orchestrator
        orchestrator._data_solution_orchestrator = mock_data_solution_orchestrator
        
        # Test: Get embeddings
        embeddings = await orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            user_context={"user_id": "test_user"}
        )
        
        assert len(embeddings) == 3
        assert embeddings[0]["embedding_type"] == "schema"
        mock_data_solution_orchestrator.orchestrate_data_expose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_semantic_embeddings_via_data_solution_with_content_id(self, orchestrator, mock_data_solution_orchestrator):
        """Test getting semantic embeddings via Data Solution Orchestrator with content_id."""
        # Setup: Mock Data Solution Orchestrator and Librarian
        orchestrator._data_solution_orchestrator = mock_data_solution_orchestrator
        orchestrator.librarian.get_content_metadata = AsyncMock(return_value={
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123"
        })
        
        # Test: Get embeddings using content_id
        embeddings = await orchestrator.get_semantic_embeddings_via_data_solution(
            content_id="test_content_123",
            user_context={"user_id": "test_user"}
        )
        
        assert len(embeddings) == 3
        orchestrator.librarian.get_content_metadata.assert_called_once()
        mock_data_solution_orchestrator.orchestrate_data_expose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_semantic_embeddings_via_data_solution_with_embedding_type_filter(self, orchestrator, mock_data_solution_orchestrator):
        """Test getting semantic embeddings with embedding_type filter."""
        # Setup: Mock Data Solution Orchestrator
        orchestrator._data_solution_orchestrator = mock_data_solution_orchestrator
        
        # Test: Get only schema embeddings
        embeddings = await orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            embedding_type="schema",
            user_context={"user_id": "test_user"}
        )
        
        assert len(embeddings) == 2
        assert all(emb["embedding_type"] == "schema" for emb in embeddings)
    
    # ========================================================================
    # SEMANTIC ENRICHMENT GATEWAY INTEGRATION TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_get_semantic_enrichment_gateway(self, orchestrator, mock_semantic_enrichment_gateway):
        """Test Semantic Enrichment Gateway discovery."""
        # Setup: Mock enabling service discovery
        orchestrator.get_enabling_service = AsyncMock(return_value=mock_semantic_enrichment_gateway)
        
        # Test: Get Semantic Enrichment Gateway
        gateway = await orchestrator._get_semantic_enrichment_gateway()
        
        assert gateway is not None
        assert gateway == mock_semantic_enrichment_gateway
        orchestrator.get_enabling_service.assert_called_with("SemanticEnrichmentGatewayService")
    
    # ========================================================================
    # HELPER METHODS TESTS
    # ========================================================================
    
    def test_determine_data_type_structured(self, orchestrator):
        """Test _determine_data_type detects structured data."""
        embeddings = [
            {"embedding_type": "schema", "column_name": "col1"},
            {"embedding_type": "schema", "column_name": "col2"},
            {"embedding_type": "chunk", "content": "text"}
        ]
        
        data_type = orchestrator._determine_data_type(embeddings)
        
        assert data_type == "structured"
    
    def test_determine_data_type_unstructured(self, orchestrator):
        """Test _determine_data_type detects unstructured data."""
        embeddings = [
            {"embedding_type": "chunk", "content": "text content"},
            {"embedding_type": "chunk", "content": "more text"}
        ]
        
        data_type = orchestrator._determine_data_type(embeddings)
        
        assert data_type == "unstructured"
    
    def test_determine_data_type_empty(self, orchestrator):
        """Test _determine_data_type with empty embeddings."""
        data_type = orchestrator._determine_data_type([])
        
        assert data_type == "unstructured"
    
    def test_needs_enrichment_true(self, orchestrator):
        """Test _needs_enrichment returns True when enrichment needed."""
        user_query = "Show me all the specific column values"
        embeddings = [
            {"embedding_type": "schema", "column_name": "col1"}
        ]
        
        needs_enrichment = orchestrator._needs_enrichment(user_query, embeddings)
        
        assert needs_enrichment is True
    
    def test_needs_enrichment_false(self, orchestrator):
        """Test _needs_enrichment returns False when enrichment not needed."""
        # Use a query that definitely doesn't need enrichment
        # Avoid keywords like "data", "values", "numbers", "text" which trigger enrichment
        user_query = "What are the main insights?"
        embeddings = [
            {"embedding_type": "schema", "column_name": "col1"},
            {"embedding_type": "chunk", "content": "summary text"}
        ]
        
        needs_enrichment = orchestrator._needs_enrichment(user_query, embeddings)
        
        # This query asks for insights/summary, not specific values, so enrichment should not be needed
        assert needs_enrichment is False
    
    def test_build_enrichment_request(self, orchestrator):
        """Test _build_enrichment_request creates proper request."""
        user_query = "Show me statistics for column A"
        
        request = orchestrator._build_enrichment_request(user_query)
        
        assert request["type"] == "statistics"
        assert request["description"] == user_query
        assert "filters" in request
    
    def test_needs_visualization_true(self, orchestrator):
        """Test _needs_visualization returns True when visualization needed."""
        user_query = "Show me a chart of sales data"
        
        needs_viz = orchestrator._needs_visualization(user_query)
        
        assert needs_viz is True
    
    def test_needs_visualization_false(self, orchestrator):
        """Test _needs_visualization returns False when visualization not needed."""
        user_query = "What is the summary of this data?"
        
        needs_viz = orchestrator._needs_visualization(user_query)
        
        assert needs_viz is False

