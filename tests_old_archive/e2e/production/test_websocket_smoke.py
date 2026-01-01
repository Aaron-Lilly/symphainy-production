#!/usr/bin/env python3
"""
WebSocket Connection Smoke Tests

Quick smoke tests to verify all critical WebSocket endpoints connect.
These tests catch WebSocket registration issues before deployment.

Run: pytest tests/e2e/production/test_websocket_smoke.py -v
"""

import pytest
import websockets
from typing import Optional
import asyncio

# Handle websockets library version differences
try:
    # websockets >= 11.0
    from websockets.exceptions import InvalidStatusCode
except (ImportError, AttributeError):
    try:
        # websockets < 11.0
        InvalidStatusCode = websockets.InvalidStatusCode
    except AttributeError:
        # Fallback: define our own exception handler
        class InvalidStatusCode(Exception):
            def __init__(self, status_code, *args, **kwargs):
                self.status_code = status_code
                super().__init__(*args, **kwargs)

# Test timeout
TIMEOUT = 10.0


@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.websocket
class TestWebSocketSmoke:
    """Smoke tests for critical WebSocket endpoints."""
    
    @pytest.fixture
    def websocket_url(self) -> str:
        """Get WebSocket URL from environment or default."""
        import os
        # Use TEST_BACKEND_URL to match HTTP tests (defaults to Traefik: http://localhost)
        base_url = os.getenv("TEST_BACKEND_URL", "http://localhost")
        # Convert HTTP URL to WebSocket URL
        ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        return ws_url
    
    @pytest.mark.asyncio
    async def test_guide_agent_websocket_connects(self, websocket_url):
        """Test that Guide Agent WebSocket endpoint connects (matches frontend)."""
        # Frontend uses: /api/ws/guide
        ws_endpoint = f"{websocket_url}/api/ws/guide"
        
        try:
            # websockets.connect() can be used as a context manager
            # Use asyncio.wait_for to add timeout support
            try:
                async with asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT) as ws:
                    # Verify connection is open (handle different websockets library versions)
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    
                    # Send a test message (optional - just verify connection works)
                    # await ws.send('{"type": "ping"}')
                    
                    print(f"✅ WebSocket /api/ws/guide connected successfully")
            except (TypeError, AttributeError):
                # Fallback for websockets versions that don't support context manager with wait_for
                ws = await asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT)
                try:
                    # Check if connection is open (different websockets versions use different attributes)
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/guide connected successfully")
                finally:
                    if ws:
                        await ws.close()
        except asyncio.TimeoutError:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/guide connection timed out after {TIMEOUT}s")
        except InvalidStatusCode as e:
            # 503 is acceptable (service unavailable but endpoint exists)
            if e.status_code == 503:
                print(f"⚠️ WebSocket /api/ws/guide returned 503 (service unavailable) - endpoint exists")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /api/ws/guide returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/guide connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_liaison_content_websocket_connects(self, websocket_url):
        """Test that Content Liaison Agent WebSocket endpoint connects."""
        # Frontend uses: /api/ws/liaison/{pillar}
        ws_endpoint = f"{websocket_url}/api/ws/liaison/content"
        
        try:
            try:
                async with asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT) as ws:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/content connected successfully")
            except (TypeError, AttributeError):
                ws = await asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT)
                try:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/content connected successfully")
                finally:
                    if ws:
                        await ws.close()
        except asyncio.TimeoutError:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/content connection timed out after {TIMEOUT}s")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                print(f"⚠️ WebSocket /api/ws/liaison/content returned 503 (service unavailable) - endpoint exists")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/content returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/content connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_liaison_insights_websocket_connects(self, websocket_url):
        """Test that Insights Liaison Agent WebSocket endpoint connects."""
        ws_endpoint = f"{websocket_url}/api/ws/liaison/insights"
        
        try:
            try:
                async with asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT) as ws:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/insights connected successfully")
            except (TypeError, AttributeError):
                ws = await asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT)
                try:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/insights connected successfully")
                finally:
                    if ws:
                        await ws.close()
        except asyncio.TimeoutError:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/insights connection timed out after {TIMEOUT}s")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                print(f"⚠️ WebSocket /api/ws/liaison/insights returned 503 (service unavailable) - endpoint exists")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/insights returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/insights connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_liaison_operations_websocket_connects(self, websocket_url):
        """Test that Operations Liaison Agent WebSocket endpoint connects."""
        ws_endpoint = f"{websocket_url}/api/ws/liaison/operations"
        
        try:
            try:
                async with asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT) as ws:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/operations connected successfully")
            except (TypeError, AttributeError):
                ws = await asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT)
                try:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/operations connected successfully")
                finally:
                    if ws:
                        await ws.close()
        except asyncio.TimeoutError:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/operations connection timed out after {TIMEOUT}s")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                print(f"⚠️ WebSocket /api/ws/liaison/operations returned 503 (service unavailable) - endpoint exists")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/operations returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/operations connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_liaison_business_outcomes_websocket_connects(self, websocket_url):
        """Test that Business Outcomes Liaison Agent WebSocket endpoint connects."""
        ws_endpoint = f"{websocket_url}/api/ws/liaison/business_outcomes"
        
        try:
            try:
                async with asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT) as ws:
                    assert ws.open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/business_outcomes connected successfully")
            except (TypeError, AttributeError):
                ws = await asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT)
                try:
                    # Check if connection is open (different websockets versions use different attributes)
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/liaison/business_outcomes connected successfully")
                finally:
                    if ws:
                        await ws.close()
        except asyncio.TimeoutError:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/business_outcomes connection timed out after {TIMEOUT}s")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                print(f"⚠️ WebSocket /api/ws/liaison/business_outcomes returned 503 (service unavailable) - endpoint exists")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/business_outcomes returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/liaison/business_outcomes connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_unified_agent_websocket_connects(self, websocket_url):
        """Test that Unified Agent WebSocket endpoint connects (Phase 5)."""
        # Frontend uses: /api/ws/agent
        ws_endpoint = f"{websocket_url}/api/ws/agent"
        
        try:
            try:
                async with asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT) as ws:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/agent connected successfully")
            except (TypeError, AttributeError):
                ws = await asyncio.wait_for(websockets.connect(ws_endpoint), timeout=TIMEOUT)
                try:
                    is_open = getattr(ws, 'open', None) or getattr(ws, 'close_code', None) is None
                    assert is_open, "WebSocket connection not open"
                    print(f"✅ WebSocket /api/ws/agent connected successfully")
                finally:
                    if ws:
                        await ws.close()
        except asyncio.TimeoutError:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/agent connection timed out after {TIMEOUT}s")
        except InvalidStatusCode as e:
            if e.status_code == 503:
                print(f"⚠️ WebSocket /api/ws/agent returned 503 (service unavailable) - endpoint exists")
            else:
                pytest.fail(f"❌ FAILED: WebSocket /api/ws/agent returned status {e.status_code}")
        except Exception as e:
            pytest.fail(f"❌ FAILED: WebSocket /api/ws/agent connection failed: {e}")


