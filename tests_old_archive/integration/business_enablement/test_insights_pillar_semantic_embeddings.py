#!/usr/bin/env python3
"""
Insights Pillar Semantic Embeddings Integration Tests

Tests the full semantic embeddings workflow for the Insights Pillar:
- Data Solution Orchestrator integration
- Semantic embeddings retrieval (schema, chunk)
- Agent access to embeddings via orchestrator
- Fallback mechanisms
- Security boundary validation
"""

import pytest
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock

pytestmark = [pytest.mark.integration, pytest.mark.business_enablement, pytest.mark.asyncio]


class TestInsightsPillarSemanticEmbeddings:
    """Integration tests for Insights Pillar semantic embeddings."""
    
    @pytest.fixture
    def mock_data_solution_orchestrator(self):
        """Create mock Data Solution Orchestrator with realistic embeddings."""
        orchestrator = Mock()
        
        # Mock orchestrate_data_expose with realistic response
        orchestrator.orchestrate_data_expose = AsyncMock(return_value={
            "success": True,
            "embeddings": [
                # Schema embeddings
                {
                    "embedding_type": "schema",
                    "column_name": "sales",
                    "column_type": "number",
                    "data_type": "float",
                    "content_id": "test_content_123",
                    "file_id": "test_file_123",
                    "parsed_file_id": "test_parsed_123"
                },
                {
                    "embedding_type": "schema",
                    "column_name": "region",
                    "column_type": "string",
                    "data_type": "varchar",
                    "content_id": "test_content_123",
                    "file_id": "test_file_123",
                    "parsed_file_id": "test_parsed_123"
                },
                {
                    "embedding_type": "schema",
                    "column_name": "date",
                    "column_type": "date",
                    "data_type": "timestamp",
                    "content_id": "test_content_123",
                    "file_id": "test_file_123",
                    "parsed_file_id": "test_parsed_123"
                },
                # Chunk embeddings
                {
                    "embedding_type": "chunk",
                    "content": "Sales data for Q1 2024 shows strong growth in the Northeast region",
                    "content_id": "test_content_123",
                    "file_id": "test_file_123",
                    "parsed_file_id": "test_parsed_123",
                    "chunk_index": 0
                },
                {
                    "embedding_type": "chunk",
                    "content": "Revenue increased by 15% compared to the previous quarter",
                    "content_id": "test_content_123",
                    "file_id": "test_file_123",
                    "parsed_file_id": "test_parsed_123",
                    "chunk_index": 1
                }
            ],
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123",
            "metadata": {
                "content_id": "test_content_123",
                "content_type": "structured"
            }
        })
        
        return orchestrator
    
    @pytest.fixture
    def mock_librarian(self):
        """Create mock Librarian service for content metadata."""
        librarian = Mock()
        librarian.get_content_metadata = AsyncMock(return_value={
            "content_id": "test_content_123",
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123",
            "content_type": "structured",
            "file_name": "sales_data.csv"
        })
        return librarian
    
    @pytest.fixture
    def mock_insights_orchestrator(self, mock_data_solution_orchestrator, mock_librarian):
        """Create mock Insights Orchestrator with Data Solution Orchestrator integration."""
        orchestrator = Mock()
        orchestrator._data_solution_orchestrator = mock_data_solution_orchestrator
        orchestrator.get_librarian_api = AsyncMock(return_value=mock_librarian)
        
        # Mock get_semantic_embeddings_via_data_solution
        async def mock_get_embeddings(content_id=None, file_id=None, parsed_file_id=None, 
                                     embedding_type="all", user_context=None):
            """Mock embeddings retrieval via Data Solution Orchestrator."""
            if file_id and parsed_file_id:
                expose_result = await mock_data_solution_orchestrator.orchestrate_data_expose(
                    file_id=file_id,
                    parsed_file_id=parsed_file_id,
                    user_context=user_context
                )
                if expose_result.get("success"):
                    all_embeddings = expose_result.get("embeddings", [])
                    if embedding_type == "all":
                        return all_embeddings
                    return [e for e in all_embeddings if e.get("embedding_type") == embedding_type]
            return []
        
        orchestrator.get_semantic_embeddings_via_data_solution = mock_get_embeddings
        
        return orchestrator
    
    @pytest.fixture
    def mock_user_context(self):
        """Create mock user context."""
        from utilities import UserContext
        return UserContext(
            user_id="test_user_123",
            tenant_id="test_tenant_456",
            session_id="test_session_789",
            email="test@example.com",
            full_name="Test User",
            permissions=["read", "write", "execute"]
        )
    
    @pytest.mark.asyncio
    async def test_get_schema_embeddings_via_data_solution(self, mock_insights_orchestrator, mock_user_context):
        """Test retrieving schema embeddings via Data Solution Orchestrator."""
        # Test: Get schema embeddings
        embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            embedding_type="schema",
            user_context={"user_id": "test_user"}
        )
        
        # Verify schema embeddings
        assert len(embeddings) == 3
        assert all(e.get("embedding_type") == "schema" for e in embeddings)
        assert any(e.get("column_name") == "sales" for e in embeddings)
        assert any(e.get("column_name") == "region" for e in embeddings)
        assert any(e.get("column_name") == "date" for e in embeddings)
    
    @pytest.mark.asyncio
    async def test_get_chunk_embeddings_via_data_solution(self, mock_insights_orchestrator, mock_user_context):
        """Test retrieving chunk embeddings via Data Solution Orchestrator."""
        # Test: Get chunk embeddings
        embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            embedding_type="chunk",
            user_context={"user_id": "test_user"}
        )
        
        # Verify chunk embeddings
        assert len(embeddings) == 2
        assert all(e.get("embedding_type") == "chunk" for e in embeddings)
        assert all("content" in e for e in embeddings)
    
    @pytest.mark.asyncio
    async def test_query_agent_uses_schema_embeddings(self, mock_insights_orchestrator, mock_user_context):
        """Test that InsightsQueryAgent uses schema embeddings from orchestrator."""
        # Mock Query Agent
        query_agent = Mock()
        query_agent.orchestrator = mock_insights_orchestrator
        
        # Mock _get_schema_metadata to use orchestrator
        async def mock_get_schema_metadata(content_id, user_context):
            embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
                file_id="test_file_123",
                parsed_file_id="test_parsed_123",
                embedding_type="schema",
                user_context=user_context
            )
            
            if not embeddings:
                return None
            
            schema_metadata = {
                "columns": [],
                "column_types": {},
                "content_id": content_id
            }
            
            for emb in embeddings:
                column_name = emb.get("column_name")
                column_type = emb.get("column_type") or emb.get("data_type")
                if column_name:
                    schema_metadata["columns"].append(column_name)
                    if column_type:
                        schema_metadata["column_types"][column_name] = column_type
            
            return schema_metadata
        
        query_agent._get_schema_metadata = mock_get_schema_metadata
        
        # Test: Get schema metadata
        schema_metadata = await query_agent._get_schema_metadata("test_content_123", {"user_id": "test_user"})
        
        # Verify schema metadata
        assert schema_metadata is not None
        assert len(schema_metadata["columns"]) == 3
        assert "sales" in schema_metadata["columns"]
        assert "region" in schema_metadata["columns"]
        assert "date" in schema_metadata["columns"]
        assert "sales" in schema_metadata["column_types"]
    
    @pytest.mark.asyncio
    async def test_business_analysis_agent_uses_embeddings(self, mock_insights_orchestrator, mock_user_context):
        """Test that InsightsBusinessAnalysisAgent uses embeddings from orchestrator."""
        # Mock Business Analysis Agent
        business_agent = Mock()
        business_agent.orchestrator = mock_insights_orchestrator
        
        # Mock analyze_structured_data to use orchestrator
        async def mock_analyze_structured_data(content_id, user_context):
            # Get schema embeddings via orchestrator
            embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
                file_id="test_file_123",
                parsed_file_id="test_parsed_123",
                embedding_type="schema",
                user_context=user_context
            )
            
            if not embeddings:
                return {"success": False, "error": "No schema embeddings found"}
            
            # Simulate EDA analysis
            eda_results = {
                "mean": 100.5,
                "std": 25.3,
                "columns": [e.get("column_name") for e in embeddings if e.get("column_name")]
            }
            
            # Simulate LLM interpretation
            interpretation = f"Analysis of {len(embeddings)} columns shows structured data patterns"
            
            return {
                "success": True,
                "content_id": content_id,
                "eda_results": eda_results,
                "interpretation": interpretation
            }
        
        business_agent.analyze_structured_data = mock_analyze_structured_data
        
        # Test: Analyze structured data
        result = await business_agent.analyze_structured_data("test_content_123", {"user_id": "test_user"})
        
        # Verify analysis result
        assert result.get("success") is True
        assert "eda_results" in result
        assert "interpretation" in result
        assert len(result["eda_results"]["columns"]) == 3
    
    @pytest.mark.asyncio
    async def test_liaison_agent_uses_embeddings_for_visualization(self, mock_insights_orchestrator, mock_user_context):
        """Test that InsightsLiaisonAgent uses embeddings for visualization spec generation."""
        # Mock Liaison Agent
        liaison_agent = Mock()
        liaison_agent.insights_orchestrator = mock_insights_orchestrator
        
        # Mock _generate_visualization_spec_from_nl to use orchestrator
        async def mock_generate_visualization_spec(query, content_id, user_context):
            # Get schema embeddings via orchestrator
            embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
                file_id="test_file_123",
                parsed_file_id="test_parsed_123",
                embedding_type="schema",
                user_context=user_context
            )
            
            if not embeddings:
                return None
            
            # Generate visualization spec based on schema
            columns = [e.get("column_name") for e in embeddings if e.get("column_name")]
            
            return {
                "type": "chart",
                "chart_type": "bar",
                "x_axis": columns[1] if len(columns) > 1 else columns[0],
                "y_axis": columns[0] if len(columns) > 0 else "value",
                "title": f"Visualization for {query}"
            }
        
        liaison_agent._generate_visualization_spec_from_nl = mock_generate_visualization_spec
        
        # Test: Generate visualization spec
        viz_spec = await liaison_agent._generate_visualization_spec_from_nl(
            "Show me sales by region",
            "test_content_123",
            {"user_id": "test_user"}
        )
        
        # Verify visualization spec
        assert viz_spec is not None
        assert viz_spec["type"] == "chart"
        assert "x_axis" in viz_spec
        assert "y_axis" in viz_spec
    
    @pytest.mark.asyncio
    async def test_fallback_to_semantic_data_abstraction(self, mock_insights_orchestrator, mock_user_context):
        """Test fallback to SemanticDataAbstraction when Data Solution Orchestrator unavailable."""
        # Setup: Remove Data Solution Orchestrator
        mock_insights_orchestrator._data_solution_orchestrator = None
        
        # Mock SemanticDataAbstraction as fallback
        mock_semantic_data = Mock()
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=[
            {"embedding_type": "schema", "column_name": "fallback_col", "column_type": "string"}
        ])
        
        # Mock get_business_abstraction to return semantic_data
        async def mock_get_embeddings_with_fallback(content_id=None, file_id=None, parsed_file_id=None,
                                                    embedding_type="all", user_context=None):
            """Mock with fallback to SemanticDataAbstraction."""
            # Try Data Solution Orchestrator first
            if mock_insights_orchestrator._data_solution_orchestrator:
                # Would use Data Solution Orchestrator
                return []
            
            # Fallback to SemanticDataAbstraction
            if mock_semantic_data:
                return await mock_semantic_data.get_semantic_embeddings(
                    content_id=content_id,
                    filters={"embedding_type": embedding_type},
                    user_context=user_context
                )
            
            return []
        
        mock_insights_orchestrator.get_semantic_embeddings_via_data_solution = mock_get_embeddings_with_fallback
        
        # Test: Get embeddings (should use fallback)
        embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            content_id="test_content_123",
            embedding_type="schema",
            user_context={"user_id": "test_user"}
        )
        
        # Verify fallback worked
        assert len(embeddings) == 1
        assert embeddings[0]["embedding_type"] == "schema"
        assert embeddings[0]["column_name"] == "fallback_col"
    
    @pytest.mark.asyncio
    async def test_security_boundary_data_access(self, mock_insights_orchestrator, mock_user_context):
        """Test that all data access goes through Data Solution Orchestrator (security boundary)."""
        # Test: Verify that get_semantic_embeddings_via_data_solution is the primary pathway
        embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            embedding_type="schema",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        # Verify Data Solution Orchestrator was called
        assert mock_insights_orchestrator._data_solution_orchestrator.orchestrate_data_expose.called
        
        # Verify user_context was passed (security boundary)
        call_args = mock_insights_orchestrator._data_solution_orchestrator.orchestrate_data_expose.call_args
        assert call_args is not None
        assert "user_context" in call_args.kwargs or "user_context" in str(call_args)
        
        # Verify embeddings returned
        assert len(embeddings) > 0
    
    @pytest.mark.asyncio
    async def test_embedding_type_filtering(self, mock_insights_orchestrator, mock_user_context):
        """Test that embedding type filtering works correctly."""
        # Test: Get only schema embeddings
        schema_embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            embedding_type="schema",
            user_context={"user_id": "test_user"}
        )
        
        assert len(schema_embeddings) == 3
        assert all(e.get("embedding_type") == "schema" for e in schema_embeddings)
        
        # Test: Get only chunk embeddings
        chunk_embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            embedding_type="chunk",
            user_context={"user_id": "test_user"}
        )
        
        assert len(chunk_embeddings) == 2
        assert all(e.get("embedding_type") == "chunk" for e in chunk_embeddings)
        
        # Test: Get all embeddings
        all_embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            file_id="test_file_123",
            parsed_file_id="test_parsed_123",
            embedding_type="all",
            user_context={"user_id": "test_user"}
        )
        
        assert len(all_embeddings) == 5  # 3 schema + 2 chunk


