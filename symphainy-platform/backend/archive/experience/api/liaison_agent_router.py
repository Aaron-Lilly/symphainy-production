#!/usr/bin/env python3
"""
Liaison Agent API Router

Handles pillar-specific liaison agent operations (secondary chat panel).
Routes through Chat Service → Liaison Agents for domain-specific conversations.
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Create routers
router = APIRouter(prefix="/api/liaison", tags=["Liaison Agents"])
ws_router = APIRouter(tags=["Liaison Agent WebSocket"])

# Request/Response models
class LiaisonChatRequest(BaseModel):
    message: str
    pillar: str  # content, insights, operations, business_outcomes
    conversation_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"

# Platform orchestrator reference
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    logger.info("✅ Liaison Agent router connected to platform orchestrator")


def get_city_manager():
    """Get City Manager from platform orchestrator."""
    if not _platform_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform not initialized"
        )
    return _platform_orchestrator.managers.get("city_manager")


async def get_chat_service():
    """Get Chat Service from Experience Manager."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            logger.warning("City Manager not available")
            return None
        
        # Get Experience Manager
        experience_manager = city_manager.manager_hierarchy.get("experience_manager", {}).get("instance")
        if not experience_manager:
            logger.warning("Experience Manager not available")
            return None
        
        # Try to get Chat Service
        chat_service = getattr(experience_manager, 'chat_service', None)
        if chat_service:
            logger.info("✅ Retrieved Chat Service from Experience Manager")
            return chat_service
        
        # Fallback: Try DI container
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            chat_service = di_container.service_registry.get("ChatService")
            if chat_service:
                logger.info("✅ Retrieved Chat Service from DI container")
                return chat_service
        
        logger.warning("Chat Service not available")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Chat Service: {e}")
        return None


async def get_frontend_gateway():
    """Get Frontend Gateway Service."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            return None
        
        # Get Experience Manager
        experience_manager = city_manager.manager_hierarchy.get("experience_manager", {}).get("instance")
        if not experience_manager:
            return None
        
        # Try to get Frontend Gateway
        frontend_gateway = getattr(experience_manager, 'frontend_gateway', None)
        if frontend_gateway:
            logger.info("✅ Retrieved Frontend Gateway from Experience Manager")
            return frontend_gateway
        
        # Fallback: DI container
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            frontend_gateway = di_container.service_registry.get("FrontendGatewayService")
            if frontend_gateway:
                logger.info("✅ Retrieved Frontend Gateway from DI container")
                return frontend_gateway
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting Frontend Gateway: {e}")
        return None


async def get_session_manager():
    """Get Session Manager service."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            return None
        
        # Try to get Session Manager from Experience Manager
        experience_manager = city_manager.manager_hierarchy.get("experience_manager", {}).get("instance")
        if experience_manager:
            session_manager = getattr(experience_manager, 'session_manager', None)
            if session_manager:
                logger.info("✅ Retrieved Session Manager from Experience Manager")
                return session_manager
        
        # Fallback: Try DI container
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            session_manager = di_container.service_registry.get("SessionManager")
            if session_manager:
                logger.info("✅ Retrieved Session Manager from DI container")
                return session_manager
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting Session Manager: {e}")
        return None


async def get_session_id_from_conversation_id(conversation_id: Optional[str], pillar: str) -> Optional[str]:
    """
    Get session_id from conversation_id.
    
    If conversation_id is None, creates a new session.
    Maps conversation_id to session_id for liaison agents.
    """
    if not conversation_id:
        # Create new session
        session_manager = await get_session_manager()
        if session_manager:
            result = await session_manager.create_session(
                user_id="anonymous",
                context={}
            )
            if result.get("success"):
                return result.get("session", {}).get("session_id")
        return None
    
    # For now, extract session_id from conversation_id if it follows pattern conv_{pillar}_{session_id}
    # Otherwise, try to find session by conversation_id
    # TODO: Add proper conversation_id-to-session_id mapping
    session_manager = await get_session_manager()
    if session_manager:
        # Try pattern: conv_{pillar}_{session_id}
        if conversation_id.startswith(f"conv_{pillar}_"):
            potential_session_id = conversation_id.replace(f"conv_{pillar}_", "")
            result = await session_manager.get_session(potential_session_id)
            if result.get("success"):
                return potential_session_id
        
        # Try conversation_id as session_id
        result = await session_manager.get_session(conversation_id)
        if result.get("success"):
            return conversation_id
    
    # If not found, create new session
    if session_manager:
        result = await session_manager.create_session(
            user_id="anonymous",
            context={}
        )
        if result.get("success"):
            return result.get("session", {}).get("session_id")
    
    return None


@router.post("/chat")
async def liaison_chat(request: LiaisonChatRequest):
    """
    Send message to pillar-specific liaison agent.
    
    This is for the secondary chat panel where users interact with
    pillar-specific liaison agents (Content, Insights, Operations, Business Outcomes).
    """
    try:
        logger.info(f"💬 Liaison chat request: {request.pillar} - {request.message[:100]}...")
        
        # Get session_id from conversation_id
        session_id = await get_session_id_from_conversation_id(request.conversation_id, request.pillar)
        if not session_id:
            logger.warning("⚠️ Could not get session_id, creating new session")
            session_id = "default"
        
        # Generate conversation ID for response (based on session_id)
        conversation_id = request.conversation_id or f"conv_{request.pillar}_{session_id}"
        
        # Get session manager for conversation tracking
        session_manager = await get_session_manager()
        
        # Map pillar to agent_type
        agent_type_map = {
            "content": "content_liaison",
            "insights": "insights_liaison",
            "operations": "operations_liaison",
            "business_outcomes": "business_outcomes_liaison"
        }
        agent_type = agent_type_map.get(request.pillar, f"{request.pillar}_liaison")
        
        # Add user message to conversation
        if session_manager:
            await session_manager.add_conversation_message(
                session_id=session_id,
                agent_type=agent_type,
                role="user",
                content=request.message
            )
        
        # Try Frontend Gateway first (preferred path)
        frontend_gateway = await get_frontend_gateway()
        if frontend_gateway and hasattr(frontend_gateway, 'handle_liaison_chat_request'):
            logger.info("Using Frontend Gateway for liaison chat")
            result = await frontend_gateway.handle_liaison_chat_request(
                message=request.message,
                pillar=request.pillar,
                conversation_id=conversation_id,  # Pass conversation_id (not session_id)
                user_id=request.user_id
            )
            
            # Add assistant response to conversation
            if session_manager and isinstance(result, dict):
                orchestrator_context = None
                if result.get("workflow_id"):
                    orchestrator_context = {
                        "orchestrator": result.get("orchestrator"),
                        "workflow_id": result.get("workflow_id"),
                        "status": result.get("status", "active")
                    }
                
                await session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type=agent_type,
                    role="assistant",
                    content=result.get("message", "") if isinstance(result, dict) else str(result),
                    orchestrator_context=orchestrator_context
                )
            
            return {
                "success": True,
                "response": result,
                "conversation_id": conversation_id,
                "session_id": session_id,  # Return session_id
                "pillar": request.pillar,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Fallback: Chat Service directly
        chat_service = await get_chat_service()
        if chat_service and hasattr(chat_service, 'send_message_to_liaison'):
            logger.info("Using Chat Service directly for liaison chat")
            result = await chat_service.send_message_to_liaison(
                message=request.message,
                pillar=request.pillar,
                session_id=session_id,  # Pass session_id
                user_id=request.user_id
            )
            
            # Add assistant response to conversation
            if session_manager and isinstance(result, dict):
                orchestrator_context = None
                if result.get("workflow_id"):
                    orchestrator_context = {
                        "orchestrator": result.get("orchestrator"),
                        "workflow_id": result.get("workflow_id"),
                        "status": result.get("status", "active")
                    }
                
                await session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type=agent_type,
                    role="assistant",
                    content=result.get("message", "") if isinstance(result, dict) else str(result),
                    orchestrator_context=orchestrator_context
                )
            
            return {
                "success": True,
                "response": result,
                "conversation_id": conversation_id,
                "session_id": session_id,  # Return session_id
                "pillar": request.pillar,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Smart fallback: Domain-specific mock responses
        logger.warning(f"⚠️ Liaison services not available, using smart fallback for {request.pillar}")
        
        pillar_contexts = {
            "content": {
                "greeting": "I'm your Content Liaison Agent. I can help you with file uploads, parsing, and content management.",
                "capabilities": ["Upload files", "Parse documents", "Extract metadata", "Validate content"]
            },
            "insights": {
                "greeting": "I'm your Insights Liaison Agent. I can help you analyze data and generate insights.",
                "capabilities": ["Analyze data", "Detect patterns", "Create visualizations", "Generate reports"]
            },
            "operations": {
                "greeting": "I'm your Operations Liaison Agent. I can help you create workflows and SOPs.",
                "capabilities": ["Create workflows", "Generate SOPs", "Document processes", "Check compliance"]
            },
            "business_outcomes": {
                "greeting": "I'm your Business Outcomes Liaison Agent. I can help you with strategic planning and ROI analysis.",
                "capabilities": ["Calculate metrics", "Generate forecasts", "Analyze ROI", "Create roadmaps"]
            }
        }
        
        context = pillar_contexts.get(request.pillar, {
            "greeting": f"I'm the {request.pillar} Liaison Agent",
            "capabilities": ["General assistance"]
        })
        
        # Smart response based on keywords
        message_lower = request.message.lower()
        response_text = context["greeting"]
        
        if any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
            response_text = f"{context['greeting']}\n\nI can help you with:\n" + "\n".join([f"• {cap}" for cap in context["capabilities"]])
        elif "how" in message_lower:
            response_text = f"Let me guide you through {request.pillar} operations. {context['greeting']}"
        
        return {
            "success": True,
            "response": {
                "success": True,
                "message": response_text,
                "agent": f"{request.pillar}_liaison",
                "capabilities": context["capabilities"]
            },
            "conversation_id": conversation_id,
            "pillar": request.pillar,
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "fallback"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Liaison chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Liaison chat failed: {str(e)}"
        )


@ws_router.websocket("/liaison/{pillar}")
async def liaison_websocket(
    websocket: WebSocket,
    pillar: str,
    conversation_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time liaison agent chat.
    
    Supports pillar-specific conversations:
    - /liaison/content
    - /liaison/insights
    - /liaison/operations
    - /liaison/business_outcomes
    """
    await websocket.accept()
    
    # Get session_id from conversation_id
    session_id = await get_session_id_from_conversation_id(conversation_id, pillar)
    if not session_id:
        logger.warning("⚠️ Could not get session_id, creating new session")
        session_id = "default"
    
    # Generate conversation ID for response
    conv_id = conversation_id or f"conv_{pillar}_{session_id}"
    
    logger.info(f"🔌 Liaison WebSocket connected - pillar: {pillar}, session: {session_id}, conversation: {conv_id}")
    
    # Get session manager
    session_manager = await get_session_manager()
    
    # Map pillar to agent_type
    agent_type_map = {
        "content": "content_liaison",
        "insights": "insights_liaison",
        "operations": "operations_liaison",
        "business_outcomes": "business_outcomes_liaison"
    }
    agent_type = agent_type_map.get(pillar, f"{pillar}_liaison")
    
    try:
        chat_service = await get_chat_service()
        
        # Send welcome message
        pillar_names = {
            "content": "Content",
            "insights": "Insights",
            "operations": "Operations",
            "business_outcomes": "Business Outcomes"
        }
        pillar_name = pillar_names.get(pillar, pillar.title())
        
        welcome_message = f"Welcome! I'm your {pillar_name} Liaison Agent. How can I assist you today?"
        
        # Add welcome message to conversation
        if session_manager:
            await session_manager.add_conversation_message(
                session_id=session_id,
                agent_type=agent_type,
                role="assistant",
                content=welcome_message
            )
        
        await websocket.send_json({
            "type": "welcome",
            "data": {
                "message": welcome_message,
                "pillar": pillar,
                "conversation_id": conv_id,
                "session_id": session_id
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse message
                message_data = json.loads(data)
                user_message = message_data.get("message", data)
                user_id = message_data.get("user_id", "anonymous")
                
                logger.info(f"💬 Liaison message from {user_id} ({pillar}): {user_message[:100]}...")
                
                # Add user message to conversation
                if session_manager:
                    await session_manager.add_conversation_message(
                        session_id=session_id,
                        agent_type=agent_type,
                        role="user",
                        content=user_message
                    )
                
                # Process via Chat Service
                if chat_service and hasattr(chat_service, 'send_message_to_liaison'):
                    response = await chat_service.send_message_to_liaison(
                        message=user_message,
                        pillar=pillar,
                        session_id=session_id,  # Pass session_id
                        user_id=user_id
                    )
                else:
                    # Fallback response
                    response = {
                        "success": True,
                        "message": f"I received your message about: '{user_message}'. The {pillar_name} Liaison service will be fully operational soon!",
                        "agent": f"{pillar}_liaison"
                    }
                
                # Add assistant response to conversation
                if session_manager:
                    orchestrator_context = None
                    if isinstance(response, dict) and response.get("workflow_id"):
                        orchestrator_context = {
                            "orchestrator": response.get("orchestrator"),
                            "workflow_id": response.get("workflow_id"),
                            "status": response.get("status", "active")
                        }
                    
                    await session_manager.add_conversation_message(
                        session_id=session_id,
                        agent_type=agent_type,
                        role="assistant",
                        content=response.get("message", "") if isinstance(response, dict) else str(response),
                        orchestrator_context=orchestrator_context
                    )
                
                # Send response
                await websocket.send_json({
                    "type": "agent_response",
                    "data": response,
                    "pillar": pillar,
                    "conversation_id": conv_id,
                    "session_id": session_id,  # Include session_id
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except json.JSONDecodeError:
                # Handle plain text messages
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format. Please send JSON.",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"❌ Error processing WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"🔌 Liaison WebSocket disconnected - pillar: {pillar}")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass


@router.get("/health")
async def liaison_health():
    """Liaison Agent health check."""
    chat_service = await get_chat_service()
    frontend_gateway = await get_frontend_gateway()
    
    return {
        "status": "healthy",
        "service": "liaison_agents",
        "chat_service_available": chat_service is not None,
        "frontend_gateway_available": frontend_gateway is not None,
        "pillars": ["content", "insights", "operations", "business_outcomes"],
        "websocket_available": True,
        "mode": "production" if chat_service else "fallback"
    }


