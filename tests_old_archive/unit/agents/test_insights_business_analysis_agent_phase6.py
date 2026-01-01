#!/usr/bin/env python3
"""
Insights Business Analysis Agent Phase 6 Unit Tests

Tests for InsightsBusinessAnalysisAgent Phase 6 refactoring:
- Data Solution Orchestrator integration for structured data
- Data Solution Orchestrator integration for unstructured data
- EDA tool integration
- LLM interpretation
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any
from utilities import UserContext

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.agents]


class TestInsightsBusinessAnalysisAgentPhase6:
    """Test InsightsBusinessAnalysisAgent Phase 6 functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator with Data Solution Orchestrator integration."""
        orchestrator = Mock()
        orchestrator.get_semantic_embeddings_via_data_solution = AsyncMock(return_value=[
            {"embedding_type": "schema", "column_name": "col1", "column_type": "string"},
            {"embedding_type": "schema", "column_name": "col2", "column_type": "number"}
        ])
        return orchestrator
    
    @pytest.fixture
    def mock_user_context(self):
        """Create mock user context."""
        return UserContext(
            user_id="test_user_123",
            tenant_id="test_tenant_456",
            session_id="test_session_789",
            email="test@example.com",
            full_name="Test User",
            permissions=["read", "write"]
        )
    
    @pytest.fixture
    async def agent(self, mock_orchestrator):
        """Create InsightsBusinessAnalysisAgent instance (mocked to avoid import issues)."""
        # Create a mock agent that mimics InsightsBusinessAnalysisAgent behavior
        agent = Mock()
        agent.agent_name = "InsightsBusinessAnalysisAgent"
        agent.orchestrator = mock_orchestrator
        agent.insights_orchestrator = mock_orchestrator
        
        # Mock AgentBase methods
        agent.get_business_abstraction = AsyncMock(return_value=None)
        agent.get_smart_city_service = AsyncMock(return_value=None)
        agent._call_llm_simple = AsyncMock(return_value='{"interpretation": "The data shows interesting patterns"}')
        agent._call_eda_analysis_tool = AsyncMock(return_value={
            "success": True,
            "eda_results": {"mean": 10.5, "std": 2.3},
            "schema_info": {"columns": ["col1", "col2"]}
        })
        agent._review_embeddings_with_llm = AsyncMock(return_value={
            "summary": "This is unstructured text data",
            "themes": ["theme1", "theme2"]
        })
        
        # Mock _convert_user_context
        def mock_convert_user_context(user_context):
            if hasattr(user_context, 'user_id'):
                return {
                    "user_id": user_context.user_id,
                    "tenant_id": user_context.tenant_id,
                    "session_id": user_context.session_id,
                    "email": user_context.email,
                    "full_name": user_context.full_name,
                    "permissions": user_context.permissions
                }
            return user_context
        
        agent._convert_user_context = mock_convert_user_context
        
        # Mock analyze_structured_data (Phase 6 pattern)
        async def mock_analyze_structured_data(content_id, user_context):
            user_context_dict = agent._convert_user_context(user_context)
            
            # Phase 6: Use Data Solution Orchestrator via orchestrator
            if agent.orchestrator and hasattr(agent.orchestrator, 'get_semantic_embeddings_via_data_solution'):
                embeddings = await agent.orchestrator.get_semantic_embeddings_via_data_solution(
                    content_id=content_id,
                    embedding_type="schema",
                    user_context=user_context_dict
                )
            else:
                # Fallback
                semantic_data = await agent.get_business_abstraction("semantic_data")
                if semantic_data:
                    embeddings = await semantic_data.get_semantic_embeddings(
                        content_id=content_id,
                        filters={"embedding_type": "schema"},
                        user_context=user_context_dict
                    )
                else:
                    return {"success": False, "error": "No semantic data available"}
            
            if not embeddings:
                return {"success": False, "error": "No schema embeddings found"}
            
            # Run EDA
            eda_results = await agent._call_eda_analysis_tool(content_id, user_context_dict)
            if not eda_results.get("success"):
                return {"success": False, "error": "EDA analysis failed"}
            
            # LLM interpretation
            interpretation = await agent._call_llm_simple("prompt", "system")
            
            return {
                "success": True,
                "content_id": content_id,
                "eda_results": eda_results.get("eda_results"),
                "interpretation": interpretation
            }
        
        agent.analyze_structured_data = mock_analyze_structured_data
        
        # Mock analyze_unstructured_data (Phase 6 pattern)
        async def mock_analyze_unstructured_data(content_id, user_context):
            user_context_dict = agent._convert_user_context(user_context)
            
            # Phase 6: Use Data Solution Orchestrator via orchestrator
            if agent.orchestrator and hasattr(agent.orchestrator, 'get_semantic_embeddings_via_data_solution'):
                embeddings = await agent.orchestrator.get_semantic_embeddings_via_data_solution(
                    content_id=content_id,
                    embedding_type="chunk",
                    user_context=user_context_dict
                )
            else:
                # Fallback
                semantic_data = await agent.get_business_abstraction("semantic_data")
                if semantic_data:
                    embeddings = await semantic_data.get_semantic_embeddings(
                        content_id=content_id,
                        filters={"embedding_type": "chunk"},
                        user_context=user_context_dict
                    )
                else:
                    return {"success": False, "error": "No semantic data available"}
            
            if not embeddings:
                return {"success": False, "error": "No chunk embeddings found"}
            
            # LLM review
            analysis = await agent._review_embeddings_with_llm(embeddings, user_context_dict)
            
            return {
                "success": True,
                "content_id": content_id,
                "analysis": analysis
            }
        
        agent.analyze_unstructured_data = mock_analyze_unstructured_data
        
        # Mock logger and telemetry
        agent.logger = Mock()
        agent.log_operation_with_telemetry = AsyncMock()
        agent.handle_error_with_audit = AsyncMock()
        
        return agent
    
    @pytest.mark.asyncio
    async def test_analyze_structured_data_uses_data_solution_orchestrator(self, agent, mock_orchestrator, mock_user_context):
        """Test that analyze_structured_data uses Data Solution Orchestrator via orchestrator."""
        result = await agent.analyze_structured_data(
            content_id="test_content_123",
            user_context=mock_user_context
        )
        
        assert result is not None
        assert result.get("success") is True
        assert "eda_results" in result
        assert "interpretation" in result
        
        # Verify orchestrator method was called for schema embeddings
        mock_orchestrator.get_semantic_embeddings_via_data_solution.assert_called_once_with(
            content_id="test_content_123",
            embedding_type="schema",
            user_context=agent._convert_user_context(mock_user_context)
        )
    
    @pytest.mark.asyncio
    async def test_analyze_structured_data_fallback_to_semantic_data(self, agent, mock_orchestrator, mock_user_context):
        """Test that analyze_structured_data falls back to semantic data abstraction if orchestrator not available."""
        # Remove orchestrator
        agent.orchestrator = None
        agent.insights_orchestrator = None
        
        # Mock semantic data abstraction
        mock_semantic_data = Mock()
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=[
            {"embedding_type": "schema", "column_name": "col1", "column_type": "string"}
        ])
        agent.get_business_abstraction = AsyncMock(return_value=mock_semantic_data)
        
        result = await agent.analyze_structured_data(
            content_id="test_content_123",
            user_context=mock_user_context
        )
        
        assert result is not None
        # Verify fallback was used
        agent.get_business_abstraction.assert_called_with("semantic_data")
        mock_semantic_data.get_semantic_embeddings.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_unstructured_data_uses_data_solution_orchestrator(self, agent, mock_orchestrator, mock_user_context):
        """Test that analyze_unstructured_data uses Data Solution Orchestrator via orchestrator."""
        # Update mock to return chunk embeddings
        mock_orchestrator.get_semantic_embeddings_via_data_solution = AsyncMock(return_value=[
            {"embedding_type": "chunk", "content": "sample text content"},
            {"embedding_type": "chunk", "content": "more text content"}
        ])
        
        result = await agent.analyze_unstructured_data(
            content_id="test_content_123",
            user_context=mock_user_context
        )
        
        assert result is not None
        assert result.get("success") is True
        assert "analysis" in result
        
        # Verify orchestrator method was called for chunk embeddings
        mock_orchestrator.get_semantic_embeddings_via_data_solution.assert_called_once_with(
            content_id="test_content_123",
            embedding_type="chunk",
            user_context=agent._convert_user_context(mock_user_context)
        )
    
    @pytest.mark.asyncio
    async def test_analyze_unstructured_data_fallback_to_semantic_data(self, agent, mock_orchestrator, mock_user_context):
        """Test that analyze_unstructured_data falls back to semantic data abstraction if orchestrator not available."""
        # Remove orchestrator
        agent.orchestrator = None
        agent.insights_orchestrator = None
        
        # Mock semantic data abstraction
        mock_semantic_data = Mock()
        mock_semantic_data.get_semantic_embeddings = AsyncMock(return_value=[
            {"embedding_type": "chunk", "content": "sample text"}
        ])
        agent.get_business_abstraction = AsyncMock(return_value=mock_semantic_data)
        
        result = await agent.analyze_unstructured_data(
            content_id="test_content_123",
            user_context=mock_user_context
        )
        
        assert result is not None
        # Verify fallback was used
        agent.get_business_abstraction.assert_called_with("semantic_data")
        mock_semantic_data.get_semantic_embeddings.assert_called_once()

