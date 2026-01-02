#!/usr/bin/env python3
"""
WebSocket Router for Agent Chat

Provides WebSocket endpoints for Guide Agent and Liaison Agents (per pillar).
Uses the new architecture: Agentic Foundation SDK + Smart City SOA APIs.

WHAT: Real-time chat communication for Guide and Liaison agents
HOW: FastAPI WebSocket endpoints that compose SDKs + SOA APIs
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Dict, Any, Optional
import logging
import sys
import os
import uuid
import time
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Import WebSocket routing helper
from utilities.api_routing.websocket_routing_helper import WebSocketRoutingHelper

logger = logging.getLogger(__name__)

# Connection tracking (in-memory, can be moved to Redis for multi-instance)
_connection_tracking = {
    "user_connections": defaultdict(int),  # session_id -> connection_count
    "global_connections": 0,
    "message_rates": defaultdict(list),  # session_id -> [timestamps]
    "last_cleanup": time.time()
}

router = APIRouter(tags=["WebSocket Chat"])

# Pillar-to-Orchestrator Mapping
PILLAR_TO_ORCHESTRATOR_MAP = {
    "content": {
        "orchestrator_key": "content_analysis",  # Key in DeliveryManager.mvp_pillar_orchestrators
        "orchestrator_name": "ContentAnalysisOrchestrator",
        "liaison_agent_name": "ContentLiaisonAgent"
    },
    "insights": {
        "orchestrator_key": "insights",
        "orchestrator_name": "InsightsOrchestrator",
        "liaison_agent_name": "InsightsLiaisonAgent"
    },
    "operations": {
        "orchestrator_key": "operations",
        "orchestrator_name": "OperationsOrchestrator",
        "liaison_agent_name": "OperationsLiaisonAgent"
    },
    "business_outcomes": {
        "orchestrator_key": "business_outcomes",
        "orchestrator_name": "BusinessOutcomesOrchestrator",
        "liaison_agent_name": "BusinessOutcomesLiaisonAgent"
    }
}


# Global reference to platform orchestrator (set during router registration)
_platform_orchestrator = None

def set_platform_orchestrator(platform_orchestrator: Any):
    """Set platform orchestrator reference (called during router registration)."""
    global _platform_orchestrator
    _platform_orchestrator = platform_orchestrator

# Helper functions to get services
async def get_platform_orchestrator() -> Optional[Any]:
    """Get Platform Orchestrator from global reference."""
    return _platform_orchestrator


async def get_traffic_cop_service() -> Optional[Any]:
    """Get Traffic Cop service via Curator."""
    try:
        platform_orchestrator = await get_platform_orchestrator()
        if not platform_orchestrator:
            logger.warning("⚠️ Platform Orchestrator not available")
            return None
        
        # Get di_container from PlatformOrchestrator's infrastructure_services
        di_container = platform_orchestrator.infrastructure_services.get("di_container")
        if not di_container:
            logger.warning("⚠️ DI Container not available in Platform Orchestrator")
            return None
        
        # Get Traffic Cop via Curator's registered_services
        curator = di_container.get_curator_foundation()
        if curator and hasattr(curator, 'registered_services'):
            # Check for service name variants
            service_variants = ["TrafficCop", "TrafficCopService", "traffic_cop"]
            for variant in service_variants:
                service_registration = curator.registered_services.get(variant)
                if service_registration:
                    traffic_cop = service_registration.get("service_instance")
                    if traffic_cop:
                        logger.debug(f"✅ Found Traffic Cop via Curator: {variant}")
                        return traffic_cop
        
        logger.warning("⚠️ Traffic Cop not found in Curator")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get Traffic Cop service: {e}")
        return None


async def get_delivery_manager() -> Optional[Any]:
    """Get Delivery Manager via Platform Orchestrator."""
    try:
        platform_orchestrator = await get_platform_orchestrator()
        if not platform_orchestrator:
            logger.warning("⚠️ Platform Orchestrator not available")
            return None
        
        # Get Delivery Manager via Platform Orchestrator
        delivery_manager = await platform_orchestrator.get_manager("delivery_manager")
        return delivery_manager
    except Exception as e:
        logger.error(f"❌ Failed to get Delivery Manager: {e}")
        return None


async def get_guide_agent() -> Optional[Any]:
    """Get Guide Agent via Journey Manager or Delivery Manager."""
    try:
        platform_orchestrator = await get_platform_orchestrator()
        if not platform_orchestrator:
            logger.warning("⚠️ Platform Orchestrator not available")
            return None
        
        # Try Journey Manager first
        journey_manager = await platform_orchestrator.get_manager("journey_manager")
        if journey_manager and hasattr(journey_manager, 'guide_agent'):
            return journey_manager.guide_agent
        
        # Try Delivery Manager
        delivery_manager = await get_delivery_manager()
        if delivery_manager and hasattr(delivery_manager, 'guide_agent'):
            return delivery_manager.guide_agent
        
        # Try Agentic Foundation
        agentic_foundation = platform_orchestrator.di_container.get_foundation_service("AgenticFoundationService")
        if agentic_foundation:
            # Try to get via Curator's agent registry
            curator = platform_orchestrator.di_container.get_curator_foundation()
            if curator and hasattr(curator, 'agent_capability_registry'):
                try:
                    guide_agent = await curator.agent_capability_registry.get_agent("GuideCrossDomainAgent")
                    if guide_agent:
                        return guide_agent
                except Exception as e:
                    logger.debug(f"Could not get Guide Agent via Curator agent registry: {e}")
        
        logger.warning("⚠️ Guide Agent not found")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get Guide Agent: {e}")
        return None


async def get_session_manager_service() -> Optional[Any]:
    """Get SessionManagerService via Curator."""
    try:
        platform_orchestrator = await get_platform_orchestrator()
        if not platform_orchestrator:
            logger.warning("⚠️ Platform Orchestrator not available")
            return None
        
        curator = platform_orchestrator.di_container.get_curator_foundation()
        if curator and hasattr(curator, 'registered_services'):
            # Check for service name variants
            service_variants = ["SessionManagerService", "SessionManager", "session_manager"]
            for variant in service_variants:
                service_registration = curator.registered_services.get(variant)
                if service_registration:
                    session_manager = service_registration.get("service_instance")
                    if session_manager:
                        return session_manager
        
        logger.warning("⚠️ SessionManagerService not found")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get SessionManagerService: {e}")
        return None


async def get_experience_foundation() -> Optional[Any]:
    """Get Experience Foundation Service."""
    try:
        platform_orchestrator = await get_platform_orchestrator()
        if not platform_orchestrator:
            logger.warning("⚠️ Platform Orchestrator not available")
            return None
        
        experience_foundation = platform_orchestrator.foundation_services.get("ExperienceFoundationService")
        if experience_foundation:
            return experience_foundation
        
        logger.warning("⚠️ Experience Foundation not found")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get Experience Foundation: {e}")
        return None


async def get_agentic_foundation() -> Optional[Any]:
    """Get Agentic Foundation Service."""
    try:
        platform_orchestrator = await get_platform_orchestrator()
        if not platform_orchestrator:
            logger.warning("⚠️ Platform Orchestrator not available")
            return None
        
        agentic_foundation = platform_orchestrator.di_container.get_foundation_service("AgenticFoundationService")
        return agentic_foundation
    except Exception as e:
        logger.error(f"❌ Failed to get Agentic Foundation: {e}")
        return None


@router.websocket("/api/ws/guide")
async def guide_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """
    Guide Agent WebSocket endpoint.
    
    ⚠️ DEPRECATED: This endpoint is deprecated and will be removed in a future release.
    Please migrate to the unified endpoint: /api/ws/agent
    
    Migration:
    - Use /api/ws/agent with message format: {"agent_type": "guide", "message": "..."}
    - The unified endpoint supports all agents (Guide + Liaison) via message routing
    - Benefits: Single connection, better resource efficiency, agent switching without reconnection
    
    Provides real-time chat communication with the Guide Agent.
    Uses Agentic Foundation WebSocket SDK + Smart City SOA APIs.
    """
    await websocket.accept()
    logger.warning("⚠️ DEPRECATED: /api/ws/guide endpoint is deprecated. Please migrate to /api/ws/agent")
    logger.info(f"🔌 Guide Agent WebSocket connection accepted (session_token: {session_token})")
    
    traffic_cop = None
    guide_agent = None
    websocket_sdk = None
    connection_id = None
    
    try:
        # 1. Validate session via Traffic Cop SOA API
        traffic_cop = await get_traffic_cop_service()
        if not traffic_cop:
            await websocket.close(code=4001, reason="Traffic Cop service not available")
            return
        
        session_response = None
        if hasattr(traffic_cop, 'call_soa_api'):
            try:
                session_response = await traffic_cop.call_soa_api("session_management", {
                    "action": "get_or_create",
                    "session_token": session_token or "anonymous"
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to get session via Traffic Cop: {e}")
        
        session = session_response.get("session") if session_response and isinstance(session_response, dict) else {}
        session_id = session.get("session_id") if session else None
        
        # 2. Get Guide Agent
        guide_agent = await get_guide_agent()
        if not guide_agent:
            await websocket.close(code=4002, reason="Guide Agent not available")
            return
        
        # 3. Connect Guide Agent WebSocket (via Agentic Foundation SDK)
        agentic_foundation = await get_agentic_foundation()
        if not agentic_foundation:
            await websocket.close(code=4003, reason="Agentic Foundation not available")
            return
        
        websocket_sdk = await agentic_foundation.create_agent_websocket_sdk()
        if not websocket_sdk:
            await websocket.close(code=4004, reason="Failed to create WebSocket SDK")
            return
        
        connection_id = await websocket_sdk.connect_guide_agent(session_token or "anonymous")
        if not connection_id:
            await websocket.close(code=4005, reason="Failed to connect Guide Agent WebSocket")
            return
        
        logger.info(f"✅ Guide Agent WebSocket connected: {connection_id}")
        
        # 4. Link WebSocket to Traffic Cop session
        if session_id and hasattr(traffic_cop, 'call_soa_api'):
            try:
                await traffic_cop.call_soa_api("websocket_session", {
                    "action": "link",
                    "websocket_id": connection_id,
                    "session_id": session_id,
                    "agent_type": "guide"
                })
                logger.info(f"✅ WebSocket {connection_id} linked to session {session_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to link WebSocket to session: {e}")
        
        # 5. Message loop
        try:
            while True:
                message_data = await websocket.receive_json()
                user_message = message_data.get("message", "")
                
                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message is required"
                    })
                    continue
                
                # Route to Guide Agent (which handles via its composed capabilities)
                response = await guide_agent.handle_user_message(
                    user_message,
                    session_token or "anonymous"
                )
                
                # Send response via WebSocket
                await websocket.send_json(response)
                
        except WebSocketDisconnect:
            logger.info(f"🔌 Guide Agent WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"❌ Error in Guide Agent WebSocket message loop: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Internal error: {str(e)}"
                })
            except:
                pass  # WebSocket may already be closed
    except Exception as e:
        logger.error(f"❌ Guide Agent WebSocket setup failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            await websocket.close(code=4006, reason=f"Setup failed: {str(e)}")
        except:
            pass
    finally:
        # Cleanup
        if connection_id and websocket_sdk:
            try:
                await websocket_sdk.disconnect_agent(connection_id)
            except Exception as e:
                logger.warning(f"⚠️ Failed to disconnect WebSocket: {e}")
        
        if connection_id and traffic_cop and hasattr(traffic_cop, 'call_soa_api'):
            try:
                await traffic_cop.call_soa_api("websocket_session", {
                    "action": "unlink",
                    "websocket_id": connection_id
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to unlink WebSocket from session: {e}")


@router.websocket("/api/ws/liaison/{pillar}")
async def liaison_agent_websocket(
    websocket: WebSocket,
    pillar: str,
    session_token: str = Query(None)
):
    """
    Liaison Agent WebSocket endpoint (per pillar).
    
    ⚠️ DEPRECATED: This endpoint is deprecated and will be removed in a future release.
    Please migrate to the unified endpoint: /api/ws/agent
    
    Migration:
    - Use /api/ws/agent with message format: {"agent_type": "liaison", "pillar": "content|insights|operations|business_outcomes", "message": "..."}
    - The unified endpoint supports all agents (Guide + Liaison) via message routing
    - Benefits: Single connection, better resource efficiency, agent switching without reconnection
    
    Args:
        pillar: Frontend pillar name (content, insights, operations, business_outcomes)
        session_token: User session token
    
    Architecture:
    - Frontend pillar → Backend orchestrator → Liaison agent
    - All liaison agents are in business_enablement realm
    - Each orchestrator has its own liaison_agent property
    - Conversation history persists in SessionManagerService (survives pillar switches)
    """
    await websocket.accept()
    logger.warning(f"⚠️ DEPRECATED: /api/ws/liaison/{pillar} endpoint is deprecated. Please migrate to /api/ws/agent")
    logger.info(f"🔌 Liaison Agent WebSocket connection accepted (pillar: {pillar}, session_token: {session_token})")
    
    traffic_cop = None
    liaison_agent = None
    websocket_sdk = None
    connection_id = None
    session_manager = None
    
    try:
        # 1. Validate pillar name
        if pillar not in PILLAR_TO_ORCHESTRATOR_MAP:
            await websocket.close(code=4004, reason=f"Invalid pillar: {pillar}")
            return
        
        pillar_config = PILLAR_TO_ORCHESTRATOR_MAP[pillar]
        
        # 2. Get SessionManagerService for conversation history persistence
        session_manager = await get_session_manager_service()
        if not session_manager:
            logger.warning("⚠️ SessionManagerService not available - conversation history will not persist")
        
        # 3. Get or create session (via SessionManagerService)
        session_id = None
        if session_manager:
            try:
                session_result = await session_manager.get_or_create_session(
                    user_id=session_token or "anonymous",
                    context={"pillar": pillar}
                )
                if session_result.get("success"):
                    session_id = session_result.get("session", {}).get("session_id")
            except Exception as e:
                logger.warning(f"⚠️ Failed to get/create session: {e}")
        
        # 4. Map pillar to agent_type for conversation history
        agent_type_map = {
            "content": "content_liaison",
            "insights": "insights_liaison",
            "operations": "operations_liaison",
            "business_outcomes": "business_outcomes_liaison"
        }
        agent_type = agent_type_map[pillar]
        
        # 5. Restore conversation history from SessionManagerService
        if session_manager and session_id:
            try:
                conversation_history = await session_manager.get_conversation_history(
                    session_id=session_id,
                    agent_type=agent_type
                )
                
                # Send conversation history to frontend (so UI can restore chat)
                if conversation_history.get("success") and conversation_history.get("messages"):
                    await websocket.send_json({
                        "type": "conversation_restored",
                        "agent_type": agent_type,
                        "pillar": pillar,
                        "messages": conversation_history["messages"],
                        "message_count": len(conversation_history["messages"])
                    })
                    logger.info(f"✅ Restored {len(conversation_history['messages'])} messages for {agent_type}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to restore conversation history: {e}")
        
        # 6. Validate session via Traffic Cop SOA API (for session linking)
        traffic_cop = await get_traffic_cop_service()
        if not traffic_cop:
            await websocket.close(code=4001, reason="Traffic Cop service not available")
            return
        
        traffic_cop_session = None
        if hasattr(traffic_cop, 'call_soa_api'):
            try:
                traffic_cop_session_response = await traffic_cop.call_soa_api("session_management", {
                    "action": "get_or_create",
                    "session_token": session_token or "anonymous"
                })
                if traffic_cop_session_response and isinstance(traffic_cop_session_response, dict):
                    traffic_cop_session = traffic_cop_session_response.get("session") or traffic_cop_session_response
            except Exception as e:
                logger.warning(f"⚠️ Failed to get Traffic Cop session: {e}")
        
        # 7. Get orchestrator from Delivery Manager
        delivery_manager = await get_delivery_manager()
        if not delivery_manager:
            await websocket.close(code=4005, reason="Delivery Manager not available")
            return
        
        if not hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
            await websocket.close(code=4006, reason="Delivery Manager MVP orchestrators not initialized")
            return
        
        orchestrator = delivery_manager.mvp_pillar_orchestrators.get(pillar_config["orchestrator_key"])
        if not orchestrator:
            await websocket.close(code=4007, reason=f"Orchestrator not available: {pillar_config['orchestrator_name']}")
            return
        
        # 8. Get liaison agent from orchestrator
        liaison_agent = orchestrator.liaison_agent
        if not liaison_agent:
            await websocket.close(code=4008, reason=f"Liaison agent not available: {pillar_config['liaison_agent_name']}")
            return
        
        logger.info(f"✅ Found {pillar_config['liaison_agent_name']} for pillar {pillar}")
        
        # 9. Connect Liaison Agent WebSocket (via Agentic Foundation SDK)
        agentic_foundation = await get_agentic_foundation()
        if not agentic_foundation:
            await websocket.close(code=4003, reason="Agentic Foundation not available")
            return
        
        websocket_sdk = await agentic_foundation.create_agent_websocket_sdk()
        if not websocket_sdk:
            await websocket.close(code=4004, reason="Failed to create WebSocket SDK")
            return
        
        connection_id = await websocket_sdk.connect_liaison_agent(
            pillar=pillar,
            session_token=session_token or "anonymous"
        )
        if not connection_id:
            await websocket.close(code=4009, reason="Failed to connect Liaison Agent WebSocket")
            return
        
        logger.info(f"✅ Liaison Agent WebSocket connected: {connection_id} (pillar: {pillar})")
        
        # 10. Link WebSocket to Traffic Cop session
        if traffic_cop_session and hasattr(traffic_cop, 'call_soa_api'):
            try:
                traffic_cop_session_id = traffic_cop_session.get("session_id") if isinstance(traffic_cop_session, dict) else None
                if traffic_cop_session_id:
                    await traffic_cop.call_soa_api("websocket_session", {
                        "action": "link",
                        "websocket_id": connection_id,
                        "session_id": traffic_cop_session_id,
                        "agent_type": "liaison",
                        "pillar": pillar
                    })
                    logger.info(f"✅ WebSocket {connection_id} linked to session {traffic_cop_session_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to link WebSocket to session: {e}")
        
        # 11. Message loop (with conversation history persistence)
        try:
            while True:
                message_data = await websocket.receive_json()
                user_message = message_data.get("message", "")
                
                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message is required"
                    })
                    continue
                
                # Store user message in conversation history
                if session_manager and session_id:
                    try:
                        await session_manager.add_conversation_message(
                            session_id=session_id,
                            agent_type=agent_type,
                            role="user",
                            content=user_message,
                            orchestrator_context={"pillar": pillar}
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to store user message: {e}")
                
                # Route to Liaison Agent (which handles via its orchestrator)
                response = await liaison_agent.handle_user_message(
                    user_message,
                    session_token or "anonymous",
                    pillar=pillar
                )
                
                # Store agent response in conversation history
                if session_manager and session_id:
                    try:
                        await session_manager.add_conversation_message(
                            session_id=session_id,
                            agent_type=agent_type,
                            role="assistant",
                            content=response.get("message", ""),
                            orchestrator_context={"pillar": pillar}
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to store agent response: {e}")
                
                # Send response via WebSocket
                await websocket.send_json(response)
                
        except WebSocketDisconnect:
            logger.info(f"🔌 Liaison Agent WebSocket disconnected: {connection_id} (pillar: {pillar})")
        except Exception as e:
            logger.error(f"❌ Error in Liaison Agent WebSocket message loop: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Internal error: {str(e)}"
                })
            except:
                pass  # WebSocket may already be closed
    except Exception as e:
        logger.error(f"❌ Liaison Agent WebSocket setup failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            await websocket.close(code=4010, reason=f"Setup failed: {str(e)}")
        except:
            pass
    finally:
        # Cleanup
        if connection_id and websocket_sdk:
            try:
                await websocket_sdk.disconnect_agent(connection_id)
            except Exception as e:
                logger.warning(f"⚠️ Failed to disconnect WebSocket: {e}")
        
        if connection_id and traffic_cop and hasattr(traffic_cop, 'call_soa_api'):
            try:
                await traffic_cop.call_soa_api("websocket_session", {
                    "action": "unlink",
                    "websocket_id": connection_id
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to unlink WebSocket from session: {e}")



@router.websocket("/api/ws/agent")
async def unified_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """
    Unified Agent WebSocket endpoint.
    
    Handles all agent communications (Guide + Liaison) via message routing.
    Single connection per user, routes messages to appropriate agent.
    
    Uses Experience Foundation UnifiedAgentWebSocketSDK.
    
    Security Features:
    - Origin validation (security in depth)
    - Connection limits (per-user and global)
    - Rate limiting (per-session message limits)
    - Session token validation
    
    Message Format:
    {
        "agent_type": "guide" | "liaison",
        "pillar": "content" | "insights" | "operations" | "business_outcomes" (required if liaison),
        "message": "user message",
        "conversation_id": "optional conversation ID"
    }
    
    Response Format:
    {
        "type": "response" | "error",
        "message": "agent response",
        "agent_type": "guide" | "liaison",
        "pillar": "pillar name" (if liaison),
        "conversation_id": "conversation ID",
        "data": {...},  # Optional data (AGUI components, etc.)
        "visualization": {...}  # Optional visualization component
    }
    """
    # ✅ STANDARD WEBSOCKET PATTERN: Accept quickly, validate minimally, enter message loop immediately
    # Heavy setup (service lookups, SDK initialization) happens lazily when first message arrives
    
    # 1. Accept connection immediately (required by FastAPI/Starlette)
    try:
        await websocket.accept()
        logger.debug(f"🔌 WebSocket connection accepted (session_token: {session_token})")
    except Exception as e:
        logger.error(f"❌ Failed to accept websocket connection: {e}")
        return
    
    # 2. Minimal validation (fast checks only)
    origin = websocket.headers.get("origin")
    if not WebSocketRoutingHelper.validate_origin(origin):
        logger.warning(f"🚫 WebSocket connection rejected: invalid origin '{origin}' (session_token: {session_token})")
        try:
            await websocket.close(code=4003, reason="Origin not allowed")
        except:
            pass
        return
    
    # Connection limits check
    connection_limits = WebSocketRoutingHelper.get_connection_limits()
    session_id_key = session_token or "anonymous"
    
    if _connection_tracking["user_connections"][session_id_key] >= connection_limits["max_per_user"]:
        logger.warning(f"🚫 WebSocket connection rejected: user connection limit exceeded (session_token: {session_token})")
        try:
            await websocket.close(code=4004, reason="Connection limit exceeded")
        except:
            pass
        return
    
    if _connection_tracking["global_connections"] >= connection_limits["max_global"]:
        logger.warning(f"🚫 WebSocket connection rejected: global connection limit exceeded")
        try:
            await websocket.close(code=4005, reason="Server at capacity")
        except:
            pass
        return
    
    # Increment connection counts
    _connection_tracking["user_connections"][session_id_key] += 1
    _connection_tracking["global_connections"] += 1
    
    connection_start_time = time.time()
    logger.info(f"🔌 Unified Agent WebSocket connection accepted (session_token: {session_token}, origin: {origin}, global_connections: {_connection_tracking['global_connections']})")
    
    # 3. Generate connection ID (fast, no I/O)
    connection_id = f"unified_agent_{session_id_key}_{uuid.uuid4().hex[:8]}"
    
    # 4. Send welcome message immediately (keeps connection alive)
    try:
        welcome_message = {
            "type": "system",
            "message": "Connected to Unified Agent WebSocket. Ready to receive messages.",
            "agent_type": "guide",
            "connection_id": connection_id
        }
        await websocket.send_json(welcome_message)
        logger.info(f"✅ [WEBSOCKET] Welcome message sent (connection_id: {connection_id})")
    except Exception as welcome_error:
        logger.warning(f"⚠️ [WEBSOCKET] Failed to send welcome message: {welcome_error}")
        # Continue anyway - connection might still be usable
    
    # 5. Initialize services lazily (will be set up when first message arrives)
    unified_sdk = None
    traffic_cop = None
    session_id = session_id_key  # Use session_token as fallback initially
    auth_context = None
    setup_complete = False
    heartbeat_task = None  # Background heartbeat task for keepalive (initialized in try block)
    
    # Phase 1: Security Hardening - Rate Limiting Helper (defined at function scope)
    def check_rate_limit(session_key: str) -> bool:
        """Check if message is within rate limits."""
        rate_limits = WebSocketRoutingHelper.get_rate_limits()
        current_time = time.time()
        
        # Clean old timestamps (older than 1 minute)
        message_timestamps = _connection_tracking["message_rates"][session_key]
        message_timestamps[:] = [ts for ts in message_timestamps if current_time - ts < 60]
        
        # Check per-second limit
        recent_second = [ts for ts in message_timestamps if current_time - ts < 1]
        if len(recent_second) >= rate_limits["max_per_second"]:
            logger.warning(f"🚫 Rate limit exceeded: {len(recent_second)} messages in last second (session_token: {session_token})")
            return False
        
        # Check per-minute limit
        if len(message_timestamps) >= rate_limits["max_per_minute"]:
            logger.warning(f"🚫 Rate limit exceeded: {len(message_timestamps)} messages in last minute (session_token: {session_token})")
            return False
        
        # Record message timestamp
        message_timestamps.append(current_time)
        return True
    
    async def ensure_setup_complete():
        """Lazy initialization of services - called when first message arrives."""
        nonlocal unified_sdk, traffic_cop, session_id, auth_context, setup_complete
        
        if setup_complete:
            return
        
        setup_start = time.time()
        logger.debug(f"🔧 [WEBSOCKET] Starting lazy setup (connection_id: {connection_id})")
        
        try:
            # Get Unified Agent WebSocket SDK (required for message handling)
            experience_foundation = await get_experience_foundation()
            if not experience_foundation:
                raise Exception("Experience Foundation not available")
            
            unified_sdk = await experience_foundation.get_unified_agent_websocket_sdk()
            if not unified_sdk:
                raise Exception("Unified Agent WebSocket SDK not available")
            
            # Optional: Get Traffic Cop for session management
            try:
                traffic_cop = await get_traffic_cop_service()
                if traffic_cop and hasattr(traffic_cop, 'call_soa_api'):
                    session_response = await traffic_cop.call_soa_api("session_management", {
                        "action": "get_or_create",
                        "session_token": session_token or "anonymous"
                    })
                    if session_response and isinstance(session_response, dict):
                        session = session_response.get("session", {})
                        session_id = session.get("session_id", session_id)
                        
                        # Link WebSocket to session
                        await traffic_cop.call_soa_api("websocket_session", {
                            "action": "link",
                            "websocket_id": connection_id,
                            "session_id": session_id
                        })
            except Exception as e:
                logger.debug(f"⚠️ [WEBSOCKET] Traffic Cop setup failed (non-critical): {e}")
            
            # Optional: Validate JWT token
            if session_token and session_token != "anonymous" and len(session_token) > 50:
                try:
                    platform_orchestrator = await get_platform_orchestrator()
                    if platform_orchestrator:
                        public_works = platform_orchestrator.foundation_services.get("PublicWorksFoundationService")
                        if public_works and hasattr(public_works, 'auth_abstraction'):
                            auth_abstraction = public_works.auth_abstraction
                            if auth_abstraction:
                                auth_context = await auth_abstraction.validate_token(session_token)
                                logger.debug(f"✅ [WEBSOCKET] JWT token validated for user: {auth_context.user_id}")
                except Exception as e:
                    logger.debug(f"⚠️ [WEBSOCKET] Token validation failed (non-critical): {e}")
            
            setup_complete = True
            setup_time = time.time() - setup_start
            logger.info(f"✅ [WEBSOCKET] Lazy setup completed in {setup_time:.3f}s (connection_id: {connection_id})")
            
        except Exception as e:
            logger.error(f"❌ [WEBSOCKET] Lazy setup failed: {e}", exc_info=True)
            # Don't close connection - allow retry on next message
            raise
    
    # 6. Background heartbeat task for keepalive during idle periods
    # ✅ PATTERN: Keep connection alive while user interacts with other page elements
    # Wrap main logic in try block for error handling
    try:
        heartbeat_interval = 30  # Send heartbeat every 30 seconds
        last_heartbeat_time = time.time()
        
        async def heartbeat_loop():
            """Background task that sends periodic heartbeat messages to keep connection alive."""
            nonlocal last_heartbeat_time
            try:
                while True:
                    await asyncio.sleep(heartbeat_interval)
                    
                    # Check if connection is still alive
                    if websocket.client_state.name != "CONNECTED":
                        logger.debug(f"🔌 [WEBSOCKET] Connection closed, stopping heartbeat (connection_id: {connection_id})")
                        break
                    
                    try:
                        # Send heartbeat ping
                        heartbeat_message = {
                            "type": "heartbeat",
                            "action": "ping",
                            "timestamp": time.time(),
                            "connection_id": connection_id
                        }
                        await websocket.send_json(heartbeat_message)
                        last_heartbeat_time = time.time()
                        logger.debug(f"💓 [WEBSOCKET] Heartbeat ping sent (connection_id: {connection_id})")
                    except Exception as heartbeat_error:
                        # Connection likely closed
                        logger.debug(f"🔌 [WEBSOCKET] Heartbeat failed, connection closed: {heartbeat_error}")
                        break
            except asyncio.CancelledError:
                logger.debug(f"💓 [WEBSOCKET] Heartbeat task cancelled (connection_id: {connection_id})")
            except Exception as e:
                logger.warning(f"⚠️ [WEBSOCKET] Heartbeat task error: {e}")
        
        # Start heartbeat task (assign to outer scope variable)
        heartbeat_task = asyncio.create_task(heartbeat_loop())
        logger.debug(f"💓 [WEBSOCKET] Heartbeat task started (connection_id: {connection_id}, interval: {heartbeat_interval}s)")
        
        # 7. Message loop - enters immediately, setup happens lazily
        # ✅ PATTERN: Connection "waits in background" - message loop handles both:
        #   - Regular chat messages (guide/liaison agents)
        #   - Heartbeat pong responses (keepalive)
        try:
            while True:
                # ✅ CRITICAL: Enter message loop immediately - setup happens lazily on first message
                # This allows connection to "wait in background" during idle periods
                message_data = await websocket.receive_json()
                
                # Handle heartbeat pong responses (keepalive)
                if message_data.get("type") == "heartbeat" and message_data.get("action") == "pong":
                    # Client responded to heartbeat - connection is alive
                    last_heartbeat_time = time.time()
                    logger.debug(f"💓 [WEBSOCKET] Heartbeat pong received (connection_id: {connection_id})")
                    continue  # Skip to next message - no agent processing needed
                
                # Regular message handling (guide/liaison agents)
                
                # Ensure services are initialized (lazy setup on first message)
                if not setup_complete:
                    try:
                        await ensure_setup_complete()
                    except Exception as setup_error:
                        # If setup fails, send error and continue (allow retry)
                        try:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Service initialization failed: {str(setup_error)}. Please try again.",
                                "agent_type": message_data.get("agent_type", "unknown")
                            })
                        except:
                            pass
                        # Continue to next message - setup might succeed on retry
                        continue
                
                # Verify unified_sdk is available (required for message handling)
                if not unified_sdk:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Service not available. Please reconnect.",
                            "agent_type": message_data.get("agent_type", "unknown")
                        })
                    except:
                        pass
                    continue
                
                # Phase 1: Security Hardening - Rate Limiting
                if not check_rate_limit(session_id_key):
                    # Phase 3: Observability - Record rate limit metric
                    try:
                        platform_orchestrator = await get_platform_orchestrator()
                        if platform_orchestrator:
                            public_works = platform_orchestrator.foundation_services.get("PublicWorksFoundationService")
                            if public_works and hasattr(public_works, 'telemetry_foundation'):
                                telemetry = public_works.telemetry_foundation
                                if telemetry:
                                    await telemetry.record_health_metric(
                                        "websocket.rate_limit.exceeded",
                                        1.0,
                                        {
                                            "session_token": session_token or "anonymous",
                                            "connection_id": connection_id
                                        }
                                    )
                    except Exception as metric_error:
                        logger.debug(f"Could not record rate limit metric: {metric_error}")
                    
                    # Rate limit exceeded - send error and close
                    error_response = {
                        "type": "error",
                        "message": "Rate limit exceeded. Please slow down your requests.",
                        "agent_type": message_data.get("agent_type", "unknown"),
                        "conversation_id": message_data.get("conversation_id")
                    }
                    try:
                        await websocket.send_json(error_response)
                        await websocket.close(code=4029, reason="Rate limit exceeded")
                    except:
                        pass
                    break
                
                # Phase 3: Observability - Record message metric
                try:
                    platform_orchestrator = await get_platform_orchestrator()
                    if platform_orchestrator:
                        public_works = platform_orchestrator.foundation_services.get("PublicWorksFoundationService")
                        if public_works and hasattr(public_works, 'telemetry_foundation'):
                            telemetry = public_works.telemetry_foundation
                            if telemetry:
                                await telemetry.record_health_metric(
                                    "websocket.message.received",
                                    1.0,
                                    {
                                        "agent_type": message_data.get("agent_type", "unknown"),
                                        "pillar": message_data.get("pillar", "none"),
                                        "connection_id": connection_id
                                    }
                                )
                except Exception as metric_error:
                    logger.debug(f"Could not record message metric: {metric_error}")
                
                # Handle agent message via Unified SDK
                response = await unified_sdk.handle_agent_message(
                    websocket=websocket,
                    message=message_data,
                    session_token=session_token or "anonymous",
                    connection_id=connection_id
                )
                
                # Send response via WebSocket
                await websocket.send_json(response)
                
        except WebSocketDisconnect as disconnect:
            connection_duration = time.time() - connection_start_time
            logger.info(f"🔌 [WEBSOCKET] Unified Agent WebSocket disconnected normally: {connection_id} (duration: {connection_duration:.3f}s, code: {getattr(disconnect, 'code', 'unknown')})")
        except Exception as e:
            connection_duration = time.time() - connection_start_time
            logger.error(f"❌ [WEBSOCKET] Error in Unified Agent WebSocket message loop after {connection_duration:.3f}s: {e}")
            logger.error(f"❌ [WEBSOCKET] Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ [WEBSOCKET] Traceback: {traceback.format_exc()}")
            # Check if this is a connection closure error
            if "connection closed" in str(e).lower() or "websocket" in str(e).lower():
                logger.warning(f"⚠️ [WEBSOCKET] Connection appears to have been closed by client or network (connection_id: {connection_id})")
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Internal error: {str(e)}",
                    "agent_type": message_data.get("agent_type", "unknown") if 'message_data' in locals() else "unknown"
                })
            except Exception as send_error:
                logger.error(f"❌ [WEBSOCKET] Failed to send error message: {send_error}")
                # WebSocket may already be closed
        
        except Exception as e:
            connection_duration = time.time() - connection_start_time
        logger.error(f"❌ [WEBSOCKET] Unified Agent WebSocket error after {connection_duration:.3f}s: {e}")
        logger.error(f"❌ [WEBSOCKET] Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ [WEBSOCKET] Traceback: {traceback.format_exc()}")
        try:
            await websocket.close(code=4006, reason=f"Error: {str(e)}")
        except Exception as close_error:
            logger.error(f"❌ [WEBSOCKET] Failed to close websocket: {close_error}")
    finally:
        # Stop heartbeat task
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.debug(f"💓 [WEBSOCKET] Heartbeat task stopped (connection_id: {connection_id})")
        
        # Phase 1: Security Hardening - Cleanup Connection Tracking
        _connection_tracking["user_connections"][session_id_key] = max(0, _connection_tracking["user_connections"][session_id_key] - 1)
        _connection_tracking["global_connections"] = max(0, _connection_tracking["global_connections"] - 1)
        
        # Cleanup old rate limit data (older than 5 minutes)
        current_time = time.time()
        if current_time - _connection_tracking["last_cleanup"] > 300:  # 5 minutes
            for session_key in list(_connection_tracking["message_rates"].keys()):
                timestamps = _connection_tracking["message_rates"][session_key]
                _connection_tracking["message_rates"][session_key] = [ts for ts in timestamps if current_time - ts < 300]
                # Remove empty entries
                if not _connection_tracking["message_rates"][session_key]:
                    del _connection_tracking["message_rates"][session_key]
            _connection_tracking["last_cleanup"] = current_time
        
        # Cleanup
        if connection_id and unified_sdk:
            try:
                await unified_sdk.close_connection(connection_id)
            except Exception as e:
                logger.warning(f"⚠️ Failed to close connection: {e}")
        
        if connection_id and traffic_cop and hasattr(traffic_cop, 'call_soa_api'):
            try:
                await traffic_cop.call_soa_api("websocket_session", {
                    "action": "unlink",
                    "websocket_id": connection_id
                })
            except Exception as e:
                logger.warning(f"⚠️ Failed to unlink WebSocket from session: {e}")
