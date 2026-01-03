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

