#!/usr/bin/env python3
"""
Semantic Liaison Agents Router

User-focused semantic API endpoints for Liaison Agent operations.
Uses semantic naming that aligns with user journeys and mental models.

Endpoints:
- POST /api/liaison-agents/send-message-to-pillar-agent
- GET  /api/liaison-agents/get-pillar-conversation-history/{session_id}/{pillar}
"""

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create semantic router
router = APIRouter(prefix="/api/liaison-agents", tags=["Liaison Agents"])

# Import helpers from existing routers
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ..liaison_agent_router import (
    set_platform_orchestrator as set_platform_orchestrator_base,
    get_session_id_from_conversation_id,
    get_session_manager
)
from ..liaison_agent_router import get_chat_service

# Request/Response models
class SendMessageToPillarAgentRequest(BaseModel):
    """Request model for sending message to pillar agent."""
    message: str
    pillar: str  # content, insights, operations, business_outcomes
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_token: Optional[str] = None

class SendMessageToPillarAgentResponse(BaseModel):
    """Semantic response model for pillar agent message."""
    success: bool
    response: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    pillar: Optional[str] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class PillarConversationHistoryResponse(BaseModel):
    """Semantic response model for pillar conversation history."""
    success: bool
    conversation: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# Platform orchestrator reference
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    set_platform_orchestrator_base(orchestrator)
    logger.info("✅ Semantic Liaison Agents router connected to platform orchestrator")


@router.post("/send-message-to-pillar-agent", response_model=SendMessageToPillarAgentResponse)
async def send_message_to_pillar_agent(
    request: SendMessageToPillarAgentRequest,
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """
    Send a message to a pillar-specific liaison agent.
    
    This semantic endpoint sends messages to pillar-specific agents (Content,
    Insights, Operations, Business Outcomes). It provides a user-focused API
    that aligns with the user journey of interacting with domain experts.
    
    Args:
        request: Message request with pillar and message
        session_token: Session token from header (optional, also in request)
        
    Returns:
        SendMessageToPillarAgentResponse with agent response
    """
    try:
        logger.info(f"💬 Semantic send-message-to-pillar-agent request: {request.pillar} - {request.message[:100]}...")
        
        # Use session_token from header if not in request
        effective_token = session_token or request.session_token
        
        # Get session_id from conversation_id or session_token
        session_id = request.session_id
        if not session_id:
            if request.conversation_id:
                session_id = await get_session_id_from_conversation_id(request.conversation_id, request.pillar)
            elif effective_token:
                from ..guide_agent_router import get_session_id_from_token
                session_id = await get_session_id_from_token(effective_token)
        
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
        
        # Get chat service
        chat_service = await get_chat_service()
        if chat_service and hasattr(chat_service, 'send_message_to_liaison'):
            logger.info("Using Chat Service for liaison message")
            result = await chat_service.send_message_to_liaison(
                message=request.message,
                pillar=request.pillar,
                session_id=session_id,
                user_id=request.user_id or "anonymous"
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
            
            return SendMessageToPillarAgentResponse(
                success=True,
                response=result if isinstance(result, dict) else {"message": str(result)},
                session_id=session_id,
                pillar=request.pillar,
                timestamp=datetime.utcnow().isoformat(),
                message="Message sent successfully"
            )
        else:
            # Fallback
            logger.warning("⚠️ Chat Service not available, using mock response")
            return SendMessageToPillarAgentResponse(
                success=True,
                response={"message": "Mock response from liaison agent"},
                session_id=session_id,
                pillar=request.pillar,
                timestamp=datetime.utcnow().isoformat(),
                message="Message sent (mock mode)"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic send-message-to-pillar-agent error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/get-pillar-conversation-history/{session_id}/{pillar}", response_model=PillarConversationHistoryResponse)
async def get_pillar_conversation_history(
    session_id: str,
    pillar: str
):
    """
    Get conversation history for a pillar-specific liaison agent.
    
    This semantic endpoint retrieves the conversation history between the
    user and a specific pillar's liaison agent for a given session.
    
    Args:
        session_id: Session identifier
        pillar: Pillar name (content, insights, operations, business_outcomes)
        
    Returns:
        PillarConversationHistoryResponse with conversation history
    """
    try:
        logger.info(f"📜 Semantic get-pillar-conversation-history request: {session_id}/{pillar}")
        
        session_manager = await get_session_manager()
        
        if session_manager:
            session_result = await session_manager.get_session(session_id)
            if session_result.get("success"):
                session = session_result.get("session", {})
                conversations = session.get("conversations", {})
                
                # Map pillar to agent_type
                agent_type_map = {
                    "content": "content_liaison",
                    "insights": "insights_liaison",
                    "operations": "operations_liaison",
                    "business_outcomes": "business_outcomes_liaison"
                }
                agent_type = agent_type_map.get(pillar, f"{pillar}_liaison")
                pillar_conversation = conversations.get(agent_type, {})
                
                return PillarConversationHistoryResponse(
                    success=True,
                    conversation={
                        "messages": pillar_conversation.get("messages", []),
                        "orchestrator_context": pillar_conversation.get("orchestrator_context", {})
                    },
                    message="Conversation history retrieved successfully"
                )
        
        # Fallback
        return PillarConversationHistoryResponse(
            success=True,
            conversation={
                "messages": [],
                "orchestrator_context": {}
            },
            message="Conversation history retrieved (empty)"
        )
        
    except Exception as e:
        logger.error(f"❌ Semantic get-pillar-conversation-history error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.get("/health")
async def liaison_agents_health():
    """Liaison Agents health check."""
    return {
        "status": "healthy",
        "agents": "liaison_agents",
        "timestamp": datetime.utcnow().isoformat()
    }

