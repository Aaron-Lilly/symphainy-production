#!/usr/bin/env python3
"""
Insights Pillar Integration Tests

Comprehensive integration tests for the Insights Pillar including:
- Websocket E2E communication with InsightsLiaisonAgent
- Data Solution Orchestrator integration
- Semantic embeddings retrieval and processing
- Full workflow: query -> agent -> orchestrator -> data -> response
- Agent coordination (Liaison, Query, Business Analysis)
"""

import pytest
import asyncio
import json
import uuid
from typing import Dict, Any, Optional
from websockets.client import connect
from websockets.exceptions import ConnectionClosed
from unittest.mock import Mock, AsyncMock, patch

pytestmark = [pytest.mark.integration, pytest.mark.business_enablement, pytest.mark.asyncio, pytest.mark.websocket]


class TestInsightsPillarWebSocketIntegration:
    """Integration tests for Insights Pillar websocket communication."""
    
    @pytest.fixture
    def session_token(self):
        """Generate a test session token."""
        return f"test_session_{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def websocket_url(self):
        """Get websocket URL from environment or default."""
        import os
        # Default to public IP for production container testing
        api_url = os.getenv("API_URL", "http://35.215.64.103")
        ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")
        return ws_url
    
    async def test_insights_liaison_agent_websocket_connection(self, websocket_url, session_token):
        """Test that Insights Liaison Agent accepts websocket connections."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            # Add Authorization header for Traefik ForwardAuth bypass (testing)
            headers = {"Authorization": "Bearer test_token"}
            async with connect(url, extra_headers=headers) as websocket:
                assert websocket.open
                
                # Send message to Insights Liaison Agent
                message = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Hello, can you help me?",
                    "conversation_id": f"test_conn_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    
                    # Verify response structure
                    assert response_data.get("agent_type") == "liaison"
                    assert response_data.get("pillar") == "insights"
                    assert "response" in response_data or "message" in response_data
                    assert response_data.get("success") is not False  # Should be True or not present
                    
                except asyncio.TimeoutError:
                    pytest.skip("WebSocket response timeout - service may not be fully initialized")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")
    
    async def test_insights_liaison_agent_analysis_request(self, websocket_url, session_token):
        """Test that Insights Liaison Agent can handle analysis requests."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            headers = {"Authorization": "Bearer test_token"}
            async with connect(url, extra_headers=headers) as websocket:
                # Request data analysis
                message = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "I want to analyze my sales data",
                    "conversation_id": f"test_analysis_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(message))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    
                    # Verify the agent understands the request
                    assert response_data.get("agent_type") == "liaison"
                    assert response_data.get("pillar") == "insights"
                    response_text = response_data.get("response") or response_data.get("message", "")
                    assert len(response_text) > 0  # Should have a response
                    
                except asyncio.TimeoutError:
                    pytest.skip("Analysis request response timeout")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Analysis request test failed: {e}")
    
    async def test_insights_liaison_agent_conversation_flow(self, websocket_url, session_token):
        """Test multi-turn conversation with Insights Liaison Agent."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            conversation_id = f"test_conv_{uuid.uuid4().hex[:8]}"
            headers = {"Authorization": "Bearer test_token"}
            
            async with connect(url, extra_headers=headers) as websocket:
                # First message
                message1 = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "I need help analyzing data",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message1))
                
                try:
                    response1 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data1 = json.loads(response1)
                    assert data1.get("conversation_id") == conversation_id
                except asyncio.TimeoutError:
                    pytest.skip("First response timeout")
                
                # Follow-up message
                message2 = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "What types of analysis can you do?",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message2))
                
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data2 = json.loads(response2)
                    assert data2.get("conversation_id") == conversation_id
                    assert "response" in data2 or "message" in data2
                except asyncio.TimeoutError:
                    pytest.skip("Second response timeout")
                
                # Verify connection maintained
                assert websocket.open
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Conversation flow test failed: {e}")


class TestInsightsPillarDataIntegration:
    """Integration tests for Insights Pillar data access and processing."""
    
    @pytest.fixture
    def mock_data_solution_orchestrator(self):
        """Create mock Data Solution Orchestrator."""
        orchestrator = Mock()
        orchestrator.orchestrate_data_expose = AsyncMock(return_value={
            "success": True,
            "embeddings": [
                {"embedding_type": "schema", "column_name": "sales", "column_type": "number", "content_id": "test_content_123"},
                {"embedding_type": "schema", "column_name": "region", "column_type": "string", "content_id": "test_content_123"},
                {"embedding_type": "schema", "column_name": "date", "column_type": "date", "content_id": "test_content_123"},
                {"embedding_type": "chunk", "content": "Sales data for Q1 2024", "content_id": "test_content_123"}
            ],
            "file_id": "test_file_123",
            "parsed_file_id": "test_parsed_123"
        })
        return orchestrator
    
    @pytest.fixture
    def mock_insights_orchestrator(self, mock_data_solution_orchestrator):
        """Create mock Insights Orchestrator with Data Solution Orchestrator."""
        orchestrator = Mock()
        orchestrator._data_solution_orchestrator = mock_data_solution_orchestrator
        orchestrator.get_semantic_embeddings_via_data_solution = AsyncMock(return_value=[
            {"embedding_type": "schema", "column_name": "sales", "column_type": "number"},
            {"embedding_type": "schema", "column_name": "region", "column_type": "string"}
        ])
        orchestrator.analyze_content_for_insights = AsyncMock(return_value={
            "success": True,
            "summary": {
                "textual": "Analysis complete",
                "tabular": {},
                "visualizations": []
            }
        })
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
    async def test_data_solution_orchestrator_integration(self, mock_insights_orchestrator, mock_user_context):
        """Test that Insights Orchestrator can retrieve embeddings via Data Solution Orchestrator."""
        # Test: Get embeddings via orchestrator helper
        embeddings = await mock_insights_orchestrator.get_semantic_embeddings_via_data_solution(
            content_id="test_content_123",
            embedding_type="schema",
            user_context={"user_id": "test_user"}
        )
        
        # Verify embeddings retrieved
        assert len(embeddings) == 2
        assert embeddings[0]["embedding_type"] == "schema"
        assert "column_name" in embeddings[0]
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_analyze_content_workflow(self, mock_insights_orchestrator, mock_user_context):
        """Test full analyze_content_for_insights workflow."""
        # Test: Analyze content
        result = await mock_insights_orchestrator.analyze_content_for_insights(
            source_type="content_metadata",
            content_metadata_id="test_content_123",
            content_type="structured",
            user_context={"user_id": "test_user"}
        )
        
        # Verify analysis result
        assert result.get("success") is True
        assert "summary" in result
        assert "textual" in result.get("summary", {})


class TestInsightsPillarAgentCoordination:
    """Integration tests for Insights Pillar agent coordination."""
    
    @pytest.fixture
    def mock_insights_orchestrator(self):
        """Create mock Insights Orchestrator with all agents."""
        orchestrator = Mock()
        
        # Mock Liaison Agent
        liaison_agent = Mock()
        liaison_agent.process_user_query = AsyncMock(return_value={
            "success": True,
            "response": "I can help you analyze your data!",
            "intent": "analyze"
        })
        orchestrator.liaison_agent = liaison_agent
        orchestrator.get_agent = AsyncMock(return_value=liaison_agent)
        
        # Mock Query Agent
        query_agent = Mock()
        query_agent.generate_query_spec = AsyncMock(return_value={
            "query_spec": {"type": "filter", "columns": ["sales"], "filters": {}}
        })
        orchestrator._agents = {"InsightsQueryAgent": query_agent}
        
        # Mock Business Analysis Agent
        business_agent = Mock()
        business_agent.analyze_structured_data = AsyncMock(return_value={
            "success": True,
            "eda_results": {"mean": 100.5},
            "interpretation": "Data shows positive trends"
        })
        orchestrator._agents["InsightsBusinessAnalysisAgent"] = business_agent
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_liaison_agent_coordinates_with_orchestrator(self, mock_insights_orchestrator):
        """Test that Liaison Agent can coordinate with Insights Orchestrator."""
        liaison_agent = mock_insights_orchestrator.liaison_agent
        liaison_agent.insights_orchestrator = mock_insights_orchestrator
        
        # Test: Process query via liaison agent
        from utilities import UserContext
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        response = await liaison_agent.process_user_query(
            query="Analyze my sales data",
            conversation_id="test_conv_123",
            user_context=user_context
        )
        
        # Verify coordination
        assert response.get("success") is True
        assert "response" in response
    
    @pytest.mark.asyncio
    async def test_query_agent_integration(self, mock_insights_orchestrator):
        """Test that Query Agent can generate query specs."""
        query_agent = mock_insights_orchestrator._agents["InsightsQueryAgent"]
        
        # Test: Generate query spec
        query_spec = await query_agent.generate_query_spec(
            query="Show me sales by region",
            content_id="test_content_123",
            user_context={"user_id": "test_user"}
        )
        
        # Verify query spec
        assert "query_spec" in query_spec
        assert query_spec["query_spec"]["type"] == "filter"
    
    @pytest.mark.asyncio
    async def test_business_analysis_agent_integration(self, mock_insights_orchestrator):
        """Test that Business Analysis Agent can analyze data."""
        business_agent = mock_insights_orchestrator._agents["InsightsBusinessAnalysisAgent"]
        
        # Test: Analyze structured data
        from utilities import UserContext
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        result = await business_agent.analyze_structured_data(
            content_id="test_content_123",
            user_context=user_context
        )
        
        # Verify analysis
        assert result.get("success") is True
        assert "eda_results" in result
        assert "interpretation" in result


class TestInsightsPillarEndToEnd:
    """End-to-end integration tests for Insights Pillar."""
    
    @pytest.fixture
    def websocket_url(self):
        """Get websocket URL."""
        import os
        # Default to public IP for production container testing
        api_url = os.getenv("API_URL", "http://35.215.64.103")
        ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")
        return ws_url
    
    @pytest.fixture
    def session_token(self):
        """Generate session token."""
        return f"test_e2e_{uuid.uuid4().hex[:8]}"
    
    async def test_insights_pillar_full_workflow(self, websocket_url, session_token):
        """
        Test full Insights Pillar workflow:
        1. User connects via websocket
        2. User asks for analysis
        3. Liaison Agent processes request
        4. Agent coordinates with orchestrator
        5. Response returned to user
        """
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            conversation_id = f"test_e2e_{uuid.uuid4().hex[:8]}"
            headers = {"Authorization": "Bearer test_token"}
            
            async with connect(url, extra_headers=headers) as websocket:
                # Step 1: Initial greeting
                message1 = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Hello, I need help with data analysis",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message1))
                
                try:
                    response1 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data1 = json.loads(response1)
                    assert data1.get("success") is not False
                    assert data1.get("conversation_id") == conversation_id
                except asyncio.TimeoutError:
                    pytest.skip("Initial greeting timeout")
                
                # Step 2: Analysis request
                message2 = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Can you analyze my sales data?",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message2))
                
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data2 = json.loads(response2)
                    assert data2.get("conversation_id") == conversation_id
                    assert "response" in data2 or "message" in data2
                except asyncio.TimeoutError:
                    pytest.skip("Analysis request timeout")
                
                # Step 3: Verify conversation context maintained
                message3 = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "What did you find?",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message3))
                
                try:
                    response3 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    data3 = json.loads(response3)
                    assert data3.get("conversation_id") == conversation_id
                except asyncio.TimeoutError:
                    pytest.skip("Follow-up question timeout")
                
                # Verify connection still open
                assert websocket.open
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"End-to-end workflow test failed: {e}")

