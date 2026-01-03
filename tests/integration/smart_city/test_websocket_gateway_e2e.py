#!/usr/bin/env python3
"""
WebSocket Gateway E2E Tests

End-to-end tests that verify the complete WebSocket Gateway flow
works correctly with real infrastructure, simulating real browser usage.
"""

import pytest
import asyncio
import json
import uuid
from typing import List, Dict, Any

import websockets
from websockets.client import WebSocketClientProtocol

from config.test_config import TestConfig


@pytest.mark.e2e
@pytest.mark.websocket
class TestWebSocketGatewayE2E:
    """E2E tests for WebSocket Gateway simulating real browser usage."""
    
    @pytest.fixture
    def test_session_token(self):
        """Generate test session token."""
        return f"test_session_{uuid.uuid4().hex[:16]}"
    
    @pytest.fixture
    def websocket_url(self, test_session_token):
        """Get WebSocket URL."""
        backend_url = TestConfig.BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://")
        return f"{backend_url}/ws?session_token={test_session_token}"
    
    @pytest.mark.asyncio
    async def test_browser_like_connection_flow(self, websocket_url):
        """
        Test WebSocket connection flow as it would happen in a browser.
        
        Simulates:
        1. User opens page
        2. Frontend connects to /ws
        3. Receives welcome message
        4. Sends chat message
        5. Receives response (if agent is available)
        6. Closes connection
        """
        messages_received: List[Dict[str, Any]] = []
        
        async with websockets.connect(websocket_url) as websocket:
            # Step 1: Connection established
            assert websocket.open, "WebSocket connection not open"
            
            # Step 2: Receive welcome message
            welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            welcome_data = json.loads(welcome)
            messages_received.append(welcome_data)
            
            assert welcome_data["type"] == "system", "Expected system message"
            assert "connection_id" in welcome_data, "Missing connection_id"
            connection_id = welcome_data["connection_id"]
            
            # Step 3: Send chat message (as frontend would)
            chat_message = {
                "channel": "guide",
                "intent": "chat",
                "payload": {
                    "message": "Hello, I need help with my data analysis.",
                    "conversation_id": f"conv_{uuid.uuid4().hex[:8]}"
                }
            }
            await websocket.send(json.dumps(chat_message))
            
            # Step 4: Wait for response (may come from agent via Redis)
            # In real scenario, agent would process and respond
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                messages_received.append(response_data)
                
                # Response could be from agent or system
                assert response_data.get("type") in ["chat_response", "system", "error"], \
                    f"Unexpected response type: {response_data.get('type')}"
            except asyncio.TimeoutError:
                # No response is OK if agent is not subscribed
                pass
            
            # Step 5: Connection should still be open
            assert websocket.open, "Connection closed unexpectedly"
            
            # Step 6: Send another message
            follow_up = {
                "channel": "guide",
                "intent": "chat",
                "payload": {
                    "message": "Can you help me understand the data better?",
                    "conversation_id": f"conv_{uuid.uuid4().hex[:8]}"
                }
            }
            await websocket.send(json.dumps(follow_up))
            await asyncio.sleep(0.5)
            
            # Step 7: Verify connection still open
            assert websocket.open, "Connection closed after follow-up"
        
        # Verify we received at least the welcome message
        assert len(messages_received) >= 1, "No messages received"
        assert messages_received[0]["type"] == "system", "First message should be welcome"
    
    @pytest.mark.asyncio
    async def test_channel_switching(self, websocket_url):
        """
        Test switching between channels (as user would switch between guide and pillars).
        
        Simulates:
        1. Connect to guide channel
        2. Send message to guide
        3. Switch to pillar:content channel
        4. Send message to pillar
        5. Switch back to guide
        """
        async with websockets.connect(websocket_url) as websocket:
            # Receive welcome
            await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            # Step 1: Send to guide channel
            guide_message = {
                "channel": "guide",
                "intent": "chat",
                "payload": {"message": "Guide question"}
            }
            await websocket.send(json.dumps(guide_message))
            await asyncio.sleep(0.3)
            assert websocket.open, "Connection closed after guide message"
            
            # Step 2: Switch to pillar:content
            content_message = {
                "channel": "pillar:content",
                "intent": "query",
                "payload": {"message": "Content question"}
            }
            await websocket.send(json.dumps(content_message))
            await asyncio.sleep(0.3)
            assert websocket.open, "Connection closed after content message"
            
            # Step 3: Switch to pillar:insights
            insights_message = {
                "channel": "pillar:insights",
                "intent": "query",
                "payload": {"message": "Insights question"}
            }
            await websocket.send(json.dumps(insights_message))
            await asyncio.sleep(0.3)
            assert websocket.open, "Connection closed after insights message"
            
            # Step 4: Switch back to guide
            guide_message2 = {
                "channel": "guide",
                "intent": "chat",
                "payload": {"message": "Back to guide"}
            }
            await websocket.send(json.dumps(guide_message2))
            await asyncio.sleep(0.3)
            assert websocket.open, "Connection closed after switching back to guide"
    
    @pytest.mark.asyncio
    async def test_concurrent_connections(self, test_session_token):
        """
        Test multiple concurrent connections (simulating multiple browser tabs).
        
        Each connection should work independently.
        """
        backend_url = TestConfig.BACKEND_URL.replace("http://", "ws://")
        num_connections = 3
        
        async def connection_worker(conn_id: int):
            """Worker for a single connection."""
            ws_url = f"{backend_url}/ws?session_token={test_session_token}_{conn_id}"
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Receive welcome
                    welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    welcome_data = json.loads(welcome)
                    
                    # Send message
                    message = {
                        "channel": "guide",
                        "intent": "chat",
                        "payload": {"message": f"Message from connection {conn_id}"}
                    }
                    await websocket.send(json.dumps(message))
                    await asyncio.sleep(0.5)
                    
                    # Verify still open
                    assert websocket.open, f"Connection {conn_id} closed unexpectedly"
                    
                    return True
            except Exception as e:
                print(f"Connection {conn_id} error: {e}")
                return False
        
        # Create concurrent connections
        tasks = [connection_worker(i) for i in range(num_connections)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All connections should succeed
        successful = sum(1 for r in results if r is True)
        assert successful == num_connections, f"Only {successful}/{num_connections} connections succeeded"
    
    @pytest.mark.asyncio
    async def test_connection_recovery(self, websocket_url):
        """
        Test connection recovery after temporary network issues.
        
        Simulates:
        1. Connect
        2. Send messages
        3. Connection drops (simulated)
        4. Reconnect
        5. Continue sending messages
        """
        # First connection
        async with websockets.connect(websocket_url) as websocket1:
            await asyncio.wait_for(websocket1.recv(), timeout=5.0)
            
            message1 = {
                "channel": "guide",
                "intent": "chat",
                "payload": {"message": "First connection message"}
            }
            await websocket1.send(json.dumps(message1))
            await asyncio.sleep(0.5)
        
        # Wait a bit (simulating network issue)
        await asyncio.sleep(1.0)
        
        # Reconnect
        async with websockets.connect(websocket_url) as websocket2:
            await asyncio.wait_for(websocket2.recv(), timeout=5.0)
            
            message2 = {
                "channel": "guide",
                "intent": "chat",
                "payload": {"message": "Reconnected message"}
            }
            await websocket2.send(json.dumps(message2))
            await asyncio.sleep(0.5)
            
            assert websocket2.open, "Reconnection failed"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, websocket_url):
        """
        Test error handling for various error scenarios.
        
        Tests:
        1. Invalid JSON
        2. Missing required fields
        3. Invalid channel name
        4. Malformed message
        """
        async with websockets.connect(websocket_url) as websocket:
            # Receive welcome
            await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            # Test 1: Invalid JSON
            await websocket.send("not json")
            error1 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            error1_data = json.loads(error1)
            assert error1_data["type"] == "error", "Expected error for invalid JSON"
            
            # Test 2: Missing channel
            invalid_message = {
                "intent": "chat",
                "payload": {"message": "Missing channel"}
            }
            await websocket.send(json.dumps(invalid_message))
            # Should still work (defaults to guide channel)
            await asyncio.sleep(0.3)
            assert websocket.open, "Connection closed on missing channel"
            
            # Test 3: Invalid channel name
            invalid_channel = {
                "channel": "invalid:channel:name",
                "intent": "chat",
                "payload": {"message": "Invalid channel"}
            }
            await websocket.send(json.dumps(invalid_channel))
            # Should route to default or handle gracefully
            await asyncio.sleep(0.3)
            assert websocket.open, "Connection closed on invalid channel"
    
    @pytest.mark.asyncio
    async def test_heartbeat_handling(self, websocket_url):
        """
        Test heartbeat/ping handling (simulating browser keepalive).
        
        Connection should stay alive with periodic pings.
        """
        async with websockets.connect(websocket_url) as websocket:
            # Receive welcome
            await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            # Wait for heartbeat (sent every 30 seconds)
            # We'll wait a bit and verify connection is still alive
            await asyncio.sleep(35.0)
            
            # Connection should still be open
            assert websocket.open, "Connection closed (heartbeat may have failed)"
            
            # Try to send a message after heartbeat
            message = {
                "channel": "guide",
                "intent": "chat",
                "payload": {"message": "Message after heartbeat"}
            }
            await websocket.send(json.dumps(message))
            await asyncio.sleep(0.5)
            
            assert websocket.open, "Connection closed after heartbeat test"

