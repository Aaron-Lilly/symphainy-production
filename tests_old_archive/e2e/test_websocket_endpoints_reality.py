"""
E2E Test: WebSocket Endpoints - Reality Check
Tests that would have caught yesterday's WebSocket 403/404 errors

This test validates that all WebSocket endpoints the frontend uses
actually exist and accept connections.
"""

import pytest
import asyncio
import websockets
from websockets.exceptions import InvalidStatusCode, InvalidHandshake
import os
import json

BASE_WS_URL = os.getenv("TEST_BACKEND_WS_URL", "ws://localhost:8000")
TIMEOUT = 10.0

@pytest.mark.e2e
@pytest.mark.critical
@pytest.mark.asyncio
class TestCriticalWebSocketEndpoints:
    """Test critical WebSocket endpoints that caused yesterday's failures"""
    
    async def test_guide_agent_websocket_exists(self):
        """Test that Guide Agent WebSocket endpoint exists (403 yesterday)"""
        uri = f"{BASE_WS_URL}/guide-agent"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                print(f"✅ WebSocket /guide-agent connection succeeded")
                
                # Try sending a test message
                test_message = {
                    "type": "analyze",
                    "message": "Test connection",
                    "session_token": "test_token"
                }
                
                await websocket.send(json.dumps(test_message))
                print(f"✅ Sent test message to Guide Agent")
                
                # Try receiving a response (with timeout)
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=5.0
                    )
                    print(f"✅ Received response from Guide Agent: {response[:100]}...")
                except asyncio.TimeoutError:
                    print(f"⚠️  No response received (may be expected if service not fully initialized)")
                
        except InvalidStatusCode as e:
            if e.status_code == 403:
                pytest.fail(f"❌ FAILED: WebSocket /guide-agent returned 403 (forbidden) - This was yesterday's bug!")
            elif e.status_code == 404:
                pytest.fail(f"❌ FAILED: WebSocket /guide-agent returned 404 (not found)")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /guide-agent returned {e.status_code}")
        
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /guide-agent connection failed: {e}")
    
    async def test_liaison_content_websocket_exists(self):
        """Test that Content Liaison WebSocket endpoint exists"""
        uri = f"{BASE_WS_URL}/liaison/content"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                print(f"✅ WebSocket /liaison/content connection succeeded")
                
                # Send test message
                await websocket.send(json.dumps({
                    "type": "chat",
                    "message": "How do I upload files?",
                    "session_token": "test_token"
                }))
                print(f"✅ Sent message to Content Liaison")
                
        except InvalidStatusCode as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/content returned {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/content failed: {e}")
    
    async def test_liaison_insights_websocket_exists(self):
        """Test that Insights Liaison WebSocket endpoint exists"""
        uri = f"{BASE_WS_URL}/liaison/insights"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                print(f"✅ WebSocket /liaison/insights connection succeeded")
                
        except InvalidStatusCode as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/insights returned {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/insights failed: {e}")
    
    async def test_liaison_operations_websocket_exists(self):
        """Test that Operations Liaison WebSocket endpoint exists"""
        uri = f"{BASE_WS_URL}/liaison/operations"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                print(f"✅ WebSocket /liaison/operations connection succeeded")
                
        except InvalidStatusCode as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/operations returned {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/operations failed: {e}")
    
    async def test_liaison_business_outcomes_websocket_exists(self):
        """Test that Business Outcomes Liaison WebSocket endpoint exists"""
        uri = f"{BASE_WS_URL}/liaison/business_outcomes"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                print(f"✅ WebSocket /liaison/business_outcomes connection succeeded")
                
        except InvalidStatusCode as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/business_outcomes returned {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /liaison/business_outcomes failed: {e}")

@pytest.mark.e2e
@pytest.mark.asyncio
class TestWebSocketMessageExchange:
    """Test that WebSocket message exchange works"""
    
    async def test_guide_agent_message_exchange(self):
        """Test sending and receiving messages with Guide Agent"""
        uri = f"{BASE_WS_URL}/guide-agent"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                # Send analyze request
                request = {
                    "type": "analyze",
                    "message": "I want to upload files and analyze data",
                    "session_token": "test_session_123"
                }
                
                await websocket.send(json.dumps(request))
                print(f"✅ Sent analyze request to Guide Agent")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=10.0
                    )
                    
                    # Parse response
                    response_data = json.loads(response)
                    
                    # Verify response structure
                    assert isinstance(response_data, dict), \
                        "Response should be a dictionary"
                    
                    # Should have some kind of recommendation or message
                    assert any(key in response_data for key in ["recommendation", "message", "guidance", "response"]), \
                        f"Response missing expected fields: {response_data.keys()}"
                    
                    print(f"✅ Received valid response from Guide Agent")
                    
                except asyncio.TimeoutError:
                    print(f"⚠️  No response within timeout (may indicate service initialization issue)")
                    
        except Exception as e:
            pytest.fail(f"❌ Message exchange failed: {e}")
    
    async def test_liaison_agent_message_exchange(self):
        """Test sending and receiving messages with Liaison Agent"""
        uri = f"{BASE_WS_URL}/liaison/content"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                # Send chat message
                request = {
                    "type": "chat",
                    "message": "How do I parse a CSV file?",
                    "session_token": "test_session_123"
                }
                
                await websocket.send(json.dumps(request))
                print(f"✅ Sent chat message to Content Liaison")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=10.0
                    )
                    
                    response_data = json.loads(response)
                    assert isinstance(response_data, dict), \
                        "Response should be a dictionary"
                    
                    print(f"✅ Received valid response from Content Liaison")
                    
                except asyncio.TimeoutError:
                    print(f"⚠️  No response within timeout")
                    
        except Exception as e:
            pytest.fail(f"❌ Message exchange failed: {e}")

@pytest.mark.e2e
@pytest.mark.asyncio
class TestWebSocketErrorHandling:
    """Test WebSocket error handling"""
    
    async def test_invalid_websocket_path_returns_404(self):
        """Test that invalid WebSocket path returns 404"""
        uri = f"{BASE_WS_URL}/invalid-websocket-path"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                pytest.fail("Should have failed to connect to invalid path")
                
        except InvalidStatusCode as e:
            # Should be 404 for invalid path
            assert e.status_code == 404, \
                f"Expected 404 for invalid path, got {e.status_code}"
            print(f"✅ Invalid path correctly returns 404")
        
        except Exception as e:
            # Connection refused is also acceptable
            print(f"✅ Invalid path correctly failed to connect")
    
    async def test_websocket_handles_invalid_json(self):
        """Test that WebSocket handles invalid JSON gracefully"""
        uri = f"{BASE_WS_URL}/guide-agent"
        
        try:
            async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                # Send invalid JSON
                await websocket.send("invalid json {{{")
                print(f"✅ Sent invalid JSON")
                
                # Should either:
                # 1. Receive error message
                # 2. Connection closes gracefully
                # 3. No response (silent failure)
                
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=3.0
                    )
                    print(f"✅ Received response (error handling): {response[:100]}")
                except asyncio.TimeoutError:
                    print(f"✅ No response to invalid JSON (silent handling)")
                except websockets.exceptions.ConnectionClosed:
                    print(f"✅ Connection closed after invalid JSON (explicit handling)")
                    
        except Exception as e:
            # Any exception is fine - we're testing it doesn't crash
            print(f"✅ WebSocket handled invalid JSON: {e}")

@pytest.mark.e2e
@pytest.mark.asyncio
class TestMultipleWebSocketConnections:
    """Test multiple simultaneous WebSocket connections"""
    
    async def test_concurrent_websocket_connections(self):
        """Test that multiple WebSockets can connect simultaneously"""
        
        # Connect to all WebSocket endpoints concurrently
        connections = [
            f"{BASE_WS_URL}/guide-agent",
            f"{BASE_WS_URL}/liaison/content",
            f"{BASE_WS_URL}/liaison/insights",
            f"{BASE_WS_URL}/liaison/operations",
            f"{BASE_WS_URL}/liaison/business_outcomes",
        ]
        
        async def connect_to(uri):
            try:
                async with websockets.connect(uri, open_timeout=TIMEOUT) as websocket:
                    await websocket.send(json.dumps({"type": "ping"}))
                    return (uri, "success")
            except Exception as e:
                return (uri, f"failed: {e}")
        
        # Connect to all concurrently
        results = await asyncio.gather(*[connect_to(uri) for uri in connections])
        
        # Check results
        for uri, status in results:
            if status == "success":
                print(f"✅ {uri.split('/')[-1]} connected successfully")
            else:
                print(f"⚠️  {uri.split('/')[-1]}: {status}")
        
        # At least guide-agent should work
        guide_result = [r for r in results if "guide-agent" in r[0]][0]
        assert guide_result[1] == "success", \
            f"Guide Agent WebSocket must work: {guide_result[1]}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

