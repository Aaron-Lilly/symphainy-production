#!/usr/bin/env python3
"""Quick websocket connection test"""
import asyncio
import websockets
import json

async def test_websocket():
    import os
    backend_url = os.getenv("TEST_BACKEND_URL", "http://35.215.64.103")
    ws_url = backend_url.replace("http://", "ws://").replace("https://", "wss://")
    url = f"{ws_url}/api/ws/agent?session_token=test123"
    
    try:
        # Connect to websocket
        # Note: websockets library doesn't support extra_headers directly
        # We'll need to configure CORS_ORIGINS or set ENVIRONMENT=development for testing
        async with websockets.connect(url) as ws:
            print("✅ Connected to unified websocket!")
            
            # Send a test message to Insights Liaison Agent
            message = {
                "agent_type": "liaison",
                "pillar": "insights",
                "message": "Can you help me analyze my data?",
                "conversation_id": "test_conv_123"
            }
            await ws.send(json.dumps(message))
            print(f"✅ Sent message: {message}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                response_data = json.loads(response)
                print(f"✅ Received response: {json.dumps(response_data, indent=2)}")
                return True
            except asyncio.TimeoutError:
                print("⚠️ No response received within 10 seconds")
                return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    exit(0 if result else 1)

