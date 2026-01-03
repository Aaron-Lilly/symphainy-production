#!/usr/bin/env python3
"""
WebSocket Gateway Router - Single WebSocket Endpoint

Provides the single authoritative WebSocket ingress point for the platform.
All WebSocket connections go through Post Office Gateway.

WHAT: Real-time WebSocket communication endpoint
HOW: FastAPI WebSocket endpoint that delegates to Post Office WebSocket Gateway Service
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global reference to WebSocket Gateway Service (set during registration)
_websocket_gateway_service = None


def set_websocket_gateway_service(service):
    """Set WebSocket Gateway Service reference."""
    global _websocket_gateway_service
    _websocket_gateway_service = service
    logger.info("✅ WebSocket Gateway Service set in router")


def get_websocket_gateway_service():
    """Get WebSocket Gateway Service reference."""
    if _websocket_gateway_service is None:
        raise RuntimeError(
            "WebSocket Gateway Service not initialized. "
            "Call set_websocket_gateway_service() during API router registration."
        )
    return _websocket_gateway_service


router = APIRouter(tags=["WebSocket Gateway"])


@router.websocket("/ws")
async def websocket_gateway(
    websocket: WebSocket,
    session_token: Optional[str] = Query(None, description="Session token for authentication")
):
    """
    Single WebSocket ingress point for the platform.
    
    All WebSocket connections go through this endpoint, which delegates to
    Post Office WebSocket Gateway Service.
    
    Message Format:
    {
        "channel": "guide" | "pillar:content" | "pillar:insights" | "pillar:operations" | "pillar:business_outcomes",
        "intent": "chat" | "query" | "command",
        "payload": {
            "message": "user message",
            "conversation_id": "optional",
            "metadata": {}
        }
    }
    
    Response Format:
    {
        "type": "response" | "error" | "system",
        "message": "response message",
        "agent_type": "guide" | "liaison",
        "pillar": "pillar name" (if liaison),
        "conversation_id": "conversation ID",
        "data": {...},  # Optional data
        "timestamp": "ISO timestamp"
    }
    """
    try:
        # Get WebSocket Gateway Service
        gateway_service = get_websocket_gateway_service()
        
        # Delegate to gateway service
        await gateway_service.handle_connection(websocket, session_token)
        
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
        
    except Exception as e:
        logger.error(f"❌ Error in WebSocket gateway endpoint: {e}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass


@router.get("/health/websocket-gateway")
async def websocket_gateway_health():
    """Health check endpoint for WebSocket Gateway."""
    try:
        gateway_service = get_websocket_gateway_service()
        
        is_ready = await gateway_service.is_ready()
        connection_stats = await gateway_service.get_connection_count()
        
        from datetime import datetime
        uptime_seconds = 0
        if hasattr(gateway_service, 'started_at') and gateway_service.started_at:
            uptime_seconds = (datetime.utcnow() - gateway_service.started_at).total_seconds()
        
        return {
            "status": "ready" if is_ready else "not_ready",
            "instance_id": gateway_service.instance_id,
            "connections": connection_stats,
            "uptime_seconds": uptime_seconds
        }
        
    except Exception as e:
        logger.error(f"❌ Error in WebSocket gateway health check: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/test/websocket-gateway/connection/{connection_id}")
async def test_get_connection(connection_id: str):
    """
    Test-only endpoint to get connection info from backend's gateway registry.
    
    This allows tests to query the backend container's connection registry
    without creating a separate service instance.
    """
    try:
        gateway_service = get_websocket_gateway_service()
        
        if not gateway_service.connection_registry:
            return {
                "success": False,
                "error": "Connection registry not available"
            }
        
        conn = await gateway_service.connection_registry.get_connection(connection_id)
        
        if conn is None:
            return {
                "success": False,
                "error": "Connection not found",
                "connection_id": connection_id
            }
        
        return {
            "success": True,
            "connection": conn
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting connection {connection_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/test/websocket-gateway/channel/{channel}/connections")
async def test_get_connections_by_channel(channel: str):
    """
    Test-only endpoint to get connections for a channel from backend's gateway registry.
    """
    try:
        gateway_service = get_websocket_gateway_service()
        
        if not gateway_service.connection_registry:
            return {
                "success": False,
                "error": "Connection registry not available"
            }
        
        connections = await gateway_service.connection_registry.get_connections_by_channel(channel)
        
        return {
            "success": True,
            "channel": channel,
            "connections": connections
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting connections for channel {channel}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/test/websocket-gateway/connection-count")
async def test_get_connection_count():
    """
    Test-only endpoint to get connection count statistics from backend's gateway.
    """
    try:
        gateway_service = get_websocket_gateway_service()
        
        stats = await gateway_service.get_connection_count()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting connection count: {e}")
        return {
            "success": False,
            "error": str(e)
        }

