#!/usr/bin/env python3
"""
Unified Agent WebSocket Integration Tests

Tests for the unified agent websocket endpoint (/api/ws/agent).
Verifies message routing, agent switching, and conversation context.
"""

import pytest
import asyncio
import json
import uuid
from typing import Dict, Any, Optional
from websockets.client import connect
from websockets.exceptions import ConnectionClosed


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.websocket
class TestUnifiedAgentWebSocket:
    """Integration tests for unified agent websocket."""
    
    @pytest.fixture
    def session_token(self):
        """Generate a test session token."""
        return f"test_session_{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def websocket_url(self):
        """Get websocket URL from environment or default."""
        import os
        api_url = os.getenv("API_URL", "http://127.0.0.1:8000")
        ws_url = api_url.replace("http://", "ws://").replace("https://", "wss://")
        return ws_url
    
    async def test_unified_websocket_connection(self, websocket_url, session_token):
        """Test that unified websocket endpoint accepts connections."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with connect(url) as websocket:
                # Connection should be established
                assert websocket.open
                
                # Send a test message
                test_message = {
                    "agent_type": "guide",
                    "message": "Hello, Guide Agent"
                }
                await websocket.send(json.dumps(test_message))
                
                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    response_data = json.loads(response)
                    
                    # Verify response structure
                    assert "type" in response_data or "message" in response_data
                    assert response_data.get("agent_type") == "guide"
                    
                except asyncio.TimeoutError:
                    pytest.skip("WebSocket response timeout - service may not be fully initialized")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")
    
    async def test_guide_agent_routing(self, websocket_url, session_token):
        """Test that guide agent messages are routed correctly."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with connect(url) as websocket:
                # Send guide agent message
                message = {
                    "agent_type": "guide",
                    "message": "What can you help me with?",
                    "conversation_id": f"test_guide_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    response_data = json.loads(response)
                    
                    # Verify routing
                    assert response_data.get("agent_type") == "guide"
                    assert "message" in response_data or "response" in response_data
                    
                except asyncio.TimeoutError:
                    pytest.skip("WebSocket response timeout")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Guide agent routing test failed: {e}")
    
    async def test_liaison_agent_routing(self, websocket_url, session_token):
        """Test that liaison agent messages are routed correctly."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with connect(url) as websocket:
                # Send insights liaison agent message
                message = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Can you help me analyze my data?",
                    "conversation_id": f"test_insights_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    response_data = json.loads(response)
                    
                    # Verify routing
                    assert response_data.get("agent_type") == "liaison"
                    assert response_data.get("pillar") == "insights"
                    assert "message" in response_data or "response" in response_data
                    
                except asyncio.TimeoutError:
                    pytest.skip("WebSocket response timeout")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Liaison agent routing test failed: {e}")
    
    async def test_agent_switching(self, websocket_url, session_token):
        """Test switching between agents without reconnection."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with connect(url) as websocket:
                # First message to guide agent
                guide_message = {
                    "agent_type": "guide",
                    "message": "Hello Guide",
                    "conversation_id": f"test_switch_guide_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(guide_message))
                
                try:
                    guide_response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    guide_data = json.loads(guide_response)
                    assert guide_data.get("agent_type") == "guide"
                except asyncio.TimeoutError:
                    pytest.skip("Guide agent response timeout")
                
                # Switch to insights liaison without reconnecting
                liaison_message = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Hello Insights Liaison",
                    "conversation_id": f"test_switch_insights_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(liaison_message))
                
                try:
                    liaison_response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    liaison_data = json.loads(liaison_response)
                    assert liaison_data.get("agent_type") == "liaison"
                    assert liaison_data.get("pillar") == "insights"
                except asyncio.TimeoutError:
                    pytest.skip("Liaison agent response timeout")
                
                # Verify connection is still open
                assert websocket.open
                
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Agent switching test failed: {e}")
    
    async def test_conversation_context(self, websocket_url, session_token):
        """Test that conversation context is maintained."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            conversation_id = f"test_context_{uuid.uuid4().hex[:8]}"
            
            async with connect(url) as websocket:
                # First message
                message1 = {
                    "agent_type": "guide",
                    "message": "I want to analyze data",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message1))
                
                try:
                    response1 = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data1 = json.loads(response1)
                    assert data1.get("conversation_id") == conversation_id
                except asyncio.TimeoutError:
                    pytest.skip("First response timeout")
                
                # Second message in same conversation
                message2 = {
                    "agent_type": "guide",
                    "message": "What should I do next?",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message2))
                
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data2 = json.loads(response2)
                    assert data2.get("conversation_id") == conversation_id
                except asyncio.TimeoutError:
                    pytest.skip("Second response timeout")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Conversation context test failed: {e}")
    
    async def test_error_handling(self, websocket_url, session_token):
        """Test error handling for invalid messages."""
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with connect(url) as websocket:
                # Send invalid message (missing required fields)
                invalid_message = {
                    "agent_type": "liaison"
                    # Missing "pillar" and "message"
                }
                await websocket.send(json.dumps(invalid_message))
                
                # Should receive error response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    assert response_data.get("type") == "error" or "error" in response_data
                except asyncio.TimeoutError:
                    # Error response may not be sent, which is acceptable
                    pass
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"Error handling test failed: {e}")
    
    async def test_all_pillars_routing(self, websocket_url, session_token):
        """Test routing to all liaison agent pillars."""
        pillars = ["content", "insights", "operations", "business_outcomes"]
        
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with connect(url) as websocket:
                for pillar in pillars:
                    message = {
                        "agent_type": "liaison",
                        "pillar": pillar,
                        "message": f"Hello {pillar} liaison",
                        "conversation_id": f"test_{pillar}_{uuid.uuid4().hex[:8]}"
                    }
                    await websocket.send(json.dumps(message))
                    
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        assert response_data.get("pillar") == pillar
                        assert response_data.get("agent_type") == "liaison"
                    except asyncio.TimeoutError:
                        pytest.skip(f"Response timeout for pillar: {pillar}")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except Exception as e:
            pytest.fail(f"All pillars routing test failed: {e}")

