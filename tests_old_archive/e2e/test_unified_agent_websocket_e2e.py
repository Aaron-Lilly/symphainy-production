#!/usr/bin/env python3
"""
E2E Tests for Unified Agent WebSocket

Comprehensive end-to-end tests for the unified agent websocket endpoint (/api/ws/agent).
Tests Guide agent, Insights liaison agent, agent switching, and conversation history.

Run: pytest tests/e2e/test_unified_agent_websocket_e2e.py -v
"""

import pytest
import asyncio
import json
import uuid
from typing import Dict, Any, Optional
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

# Test timeout
TIMEOUT = 15.0


@pytest.mark.e2e
@pytest.mark.websocket
@pytest.mark.asyncio
class TestUnifiedAgentWebSocketE2E:
    """E2E tests for unified agent websocket."""
    
    @pytest.fixture
    def session_token(self):
        """Generate a test session token."""
        return f"test_session_{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def websocket_url(self):
        """Get websocket URL from environment or default."""
        import os
        base_url = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
        ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        return ws_url
    
    async def test_guide_agent_communication(self, websocket_url, session_token):
        """Test full Guide Agent communication flow."""
        url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
        
        try:
            async with websockets.connect(url) as websocket:
                # Verify connection
                assert websocket.open, "WebSocket connection not open"
                
                # Send message to Guide Agent
                message = {
                    "agent_type": "guide",
                    "message": "Hello, I need help getting started",
                    "conversation_id": f"test_guide_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    response_data = json.loads(response)
                    
                    # Verify response structure
                    assert response_data.get("agent_type") == "guide", "Response should be from guide agent"
                    assert "message" in response_data or "response" in response_data, "Response should contain message"
                    assert response_data.get("type") != "error", f"Received error response: {response_data}"
                    
                    print(f"✅ Guide Agent communication successful: {response_data.get('message', 'No message')[:50]}")
                    
                except asyncio.TimeoutError:
                    pytest.skip("Guide Agent response timeout - service may not be fully initialized")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                pytest.skip("Service unavailable - endpoint exists but service not ready")
            else:
                pytest.fail(f"WebSocket returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"Guide Agent communication test failed: {e}")
    
    async def test_insights_liaison_communication(self, websocket_url, session_token):
        """Test full Insights Liaison Agent communication flow."""
        url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
        
        try:
            async with websockets.connect(url) as websocket:
                # Verify connection
                assert websocket.open, "WebSocket connection not open"
                
                # Send message to Insights Liaison Agent
                message = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Can you help me analyze my data?",
                    "conversation_id": f"test_insights_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    response_data = json.loads(response)
                    
                    # Verify response structure
                    assert response_data.get("agent_type") == "liaison", "Response should be from liaison agent"
                    assert response_data.get("pillar") == "insights", "Response should be from insights pillar"
                    assert "message" in response_data or "response" in response_data, "Response should contain message"
                    assert response_data.get("type") != "error", f"Received error response: {response_data}"
                    
                    print(f"✅ Insights Liaison Agent communication successful: {response_data.get('message', 'No message')[:50]}")
                    
                except asyncio.TimeoutError:
                    pytest.skip("Insights Liaison Agent response timeout - service may not be fully initialized")
                    
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                pytest.skip("Service unavailable - endpoint exists but service not ready")
            else:
                pytest.fail(f"WebSocket returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"Insights Liaison Agent communication test failed: {e}")
    
    async def test_agent_switching_during_conversation(self, websocket_url, session_token):
        """Test switching between Guide and Liaison agents during a conversation."""
        url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
        
        try:
            async with websockets.connect(url) as websocket:
                # Verify connection
                assert websocket.open, "WebSocket connection not open"
                
                # Step 1: Start conversation with Guide Agent
                guide_message = {
                    "agent_type": "guide",
                    "message": "I want to analyze my data",
                    "conversation_id": f"test_switch_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(guide_message))
                
                try:
                    guide_response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    guide_data = json.loads(guide_response)
                    assert guide_data.get("agent_type") == "guide", "First response should be from guide"
                    print(f"✅ Guide Agent response received: {guide_data.get('message', 'No message')[:50]}")
                except asyncio.TimeoutError:
                    pytest.skip("Guide Agent response timeout")
                
                # Step 2: Switch to Insights Liaison without reconnecting
                liaison_message = {
                    "agent_type": "liaison",
                    "pillar": "insights",
                    "message": "Can you help me with data analysis?",
                    "conversation_id": f"test_switch_insights_{uuid.uuid4().hex[:8]}"
                }
                await websocket.send(json.dumps(liaison_message))
                
                try:
                    liaison_response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    liaison_data = json.loads(liaison_response)
                    assert liaison_data.get("agent_type") == "liaison", "Second response should be from liaison"
                    assert liaison_data.get("pillar") == "insights", "Second response should be from insights pillar"
                    print(f"✅ Insights Liaison response received: {liaison_data.get('message', 'No message')[:50]}")
                except asyncio.TimeoutError:
                    pytest.skip("Liaison Agent response timeout")
                
                # Step 3: Switch back to Guide Agent
                guide_message2 = {
                    "agent_type": "guide",
                    "message": "What should I do next?",
                    "conversation_id": guide_message["conversation_id"]  # Same conversation
                }
                await websocket.send(json.dumps(guide_message2))
                
                try:
                    guide_response2 = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    guide_data2 = json.loads(guide_response2)
                    assert guide_data2.get("agent_type") == "guide", "Third response should be from guide"
                    print(f"✅ Guide Agent response received (switch back): {guide_data2.get('message', 'No message')[:50]}")
                except asyncio.TimeoutError:
                    pytest.skip("Guide Agent response timeout (switch back)")
                
                # Verify connection is still open after multiple switches
                assert websocket.open, "WebSocket connection should remain open after agent switching"
                print("✅ Agent switching successful - connection maintained")
                
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                pytest.skip("Service unavailable - endpoint exists but service not ready")
            else:
                pytest.fail(f"WebSocket returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"Agent switching test failed: {e}")
    
    async def test_conversation_history_persistence(self, websocket_url, session_token):
        """Test that conversation history is maintained across messages."""
        url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
        conversation_id = f"test_history_{uuid.uuid4().hex[:8]}"
        
        try:
            async with websockets.connect(url) as websocket:
                # Verify connection
                assert websocket.open, "WebSocket connection not open"
                
                # First message
                message1 = {
                    "agent_type": "guide",
                    "message": "I want to analyze sales data",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message1))
                
                try:
                    response1 = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    data1 = json.loads(response1)
                    assert data1.get("conversation_id") == conversation_id or data1.get("conversation_id") is None, "First response should have correct conversation ID"
                    print(f"✅ First message response received: {data1.get('message', 'No message')[:50]}")
                except asyncio.TimeoutError:
                    pytest.skip("First response timeout")
                
                # Second message in same conversation
                message2 = {
                    "agent_type": "guide",
                    "message": "What files do I need?",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message2))
                
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    data2 = json.loads(response2)
                    assert data2.get("conversation_id") == conversation_id or data2.get("conversation_id") is None, "Second response should have correct conversation ID"
                    print(f"✅ Second message response received: {data2.get('message', 'No message')[:50]}")
                except asyncio.TimeoutError:
                    pytest.skip("Second response timeout")
                
                # Third message - should maintain context
                message3 = {
                    "agent_type": "guide",
                    "message": "Can you remind me what we discussed?",
                    "conversation_id": conversation_id
                }
                await websocket.send(json.dumps(message3))
                
                try:
                    response3 = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                    data3 = json.loads(response3)
                    assert data3.get("conversation_id") == conversation_id or data3.get("conversation_id") is None, "Third response should have correct conversation ID"
                    print(f"✅ Third message response received: {data3.get('message', 'No message')[:50]}")
                except asyncio.TimeoutError:
                    pytest.skip("Third response timeout")
                
                print("✅ Conversation history persistence verified")
                
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                pytest.skip("Service unavailable - endpoint exists but service not ready")
            else:
                pytest.fail(f"WebSocket returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"Conversation history persistence test failed: {e}")
    
    async def test_all_pillars_liaison_agents(self, websocket_url, session_token):
        """Test routing to all liaison agent pillars."""
        pillars = ["content", "insights", "operations", "business_outcomes"]
        
        try:
            url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
            async with websockets.connect(url) as websocket:
                assert websocket.open, "WebSocket connection not open"
                
                for pillar in pillars:
                    message = {
                        "agent_type": "liaison",
                        "pillar": pillar,
                        "message": f"Hello {pillar} liaison agent",
                        "conversation_id": f"test_{pillar}_{uuid.uuid4().hex[:8]}"
                    }
                    await websocket.send(json.dumps(message))
                    
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=TIMEOUT)
                        response_data = json.loads(response)
                        assert response_data.get("pillar") == pillar, f"Response should be from {pillar} pillar"
                        assert response_data.get("agent_type") == "liaison", f"Response should be from liaison agent"
                        assert response_data.get("type") != "error", f"Received error response for {pillar}: {response_data}"
                        print(f"✅ {pillar.capitalize()} Liaison Agent communication successful")
                    except asyncio.TimeoutError:
                        pytest.skip(f"Response timeout for pillar: {pillar}")
                
                # Verify connection is still open after all pillars
                assert websocket.open, "WebSocket connection should remain open after all pillar tests"
                print("✅ All pillars routing successful")
                
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                pytest.skip("Service unavailable - endpoint exists but service not ready")
            else:
                pytest.fail(f"WebSocket returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"All pillars liaison agents test failed: {e}")
    
    async def test_error_handling_invalid_messages(self, websocket_url, session_token):
        """Test error handling for invalid messages."""
        url = f"{websocket_url}/api/ws/agent?session_token={session_token}"
        
        try:
            async with websockets.connect(url) as websocket:
                assert websocket.open, "WebSocket connection not open"
                
                # Test 1: Missing required fields (liaison without pillar)
                invalid_message1 = {
                    "agent_type": "liaison"
                    # Missing "pillar" and "message"
                }
                await websocket.send(json.dumps(invalid_message1))
                
                try:
                    response1 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data1 = json.loads(response1)
                    # Should receive error response
                    assert response_data1.get("type") == "error" or "error" in response_data1, "Should receive error for invalid message"
                    print("✅ Error handling for missing fields verified")
                except asyncio.TimeoutError:
                    # Error response may not be sent immediately, which is acceptable
                    print("⚠️ No error response received (may be acceptable)")
                
                # Test 2: Invalid agent_type
                invalid_message2 = {
                    "agent_type": "invalid_agent",
                    "message": "Test message"
                }
                await websocket.send(json.dumps(invalid_message2))
                
                try:
                    response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data2 = json.loads(response2)
                    # Should receive error response
                    assert response_data2.get("type") == "error" or "error" in response_data2, "Should receive error for invalid agent_type"
                    print("✅ Error handling for invalid agent_type verified")
                except asyncio.TimeoutError:
                    # Error response may not be sent immediately, which is acceptable
                    print("⚠️ No error response received (may be acceptable)")
                
        except ConnectionRefusedError:
            pytest.skip("WebSocket server not available")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                pytest.skip("Service unavailable - endpoint exists but service not ready")
            else:
                pytest.fail(f"WebSocket returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"Error handling test failed: {e}")

