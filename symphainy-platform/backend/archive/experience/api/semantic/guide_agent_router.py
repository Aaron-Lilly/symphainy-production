#!/usr/bin/env python3
"""
Semantic Guide Agent Router

User-focused semantic API endpoints for Guide Agent operations.
Uses semantic naming that aligns with user journeys and mental models.

Endpoints:
- POST /api/guide-agent/analyze-user-intent
- POST /api/guide-agent/get-journey-guidance
- GET  /api/guide-agent/get-conversation-history/{session_id}
"""

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create semantic router
router = APIRouter(prefix="/api/guide-agent", tags=["Guide Agent"])

# Import helpers from existing routers
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ..guide_agent_router import (
    set_platform_orchestrator as set_platform_orchestrator_base,
    get_guide_agent,
    get_session_id_from_token,
    get_session_manager
)

# Request/Response models
class AnalyzeUserIntentRequest(BaseModel):
    """Request model for user intent analysis."""
    message: str
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AnalyzeUserIntentResponse(BaseModel):
    """Semantic response model for user intent analysis."""
    success: bool
    intent_analysis: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class GetJourneyGuidanceRequest(BaseModel):
    """Request model for journey guidance."""
    user_goal: str
    current_pillar: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class GetJourneyGuidanceResponse(BaseModel):
    """Semantic response model for journey guidance."""
    success: bool
    guidance: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class ConversationHistoryResponse(BaseModel):
    """Semantic response model for conversation history."""
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
    logger.info("✅ Semantic Guide Agent router connected to platform orchestrator")


@router.post("/analyze-user-intent", response_model=AnalyzeUserIntentResponse)
async def analyze_user_intent(
    request: AnalyzeUserIntentRequest,
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """
    Analyze user intent and provide personalized recommendations.
    
    This semantic endpoint analyzes user messages to understand intent and
    provide guidance on which pillar to use. It provides a user-focused API
    that aligns with the user journey of getting started.
    
    Args:
        request: Intent analysis request
        session_token: Session token from header (optional, also in request)
        
    Returns:
        AnalyzeUserIntentResponse with intent analysis and recommendations
    """
    try:
        logger.info(f"🤖 Semantic analyze-user-intent request: {request.message[:100]}...")
        
        # Use session_token from header if not in request
        effective_token = session_token or request.session_token
        
        # Get session_id from session_token
        session_id = await get_session_id_from_token(effective_token)
        if not session_id:
            logger.warning("⚠️ Could not get session_id, creating new session")
            session_id = "default"
        
        # Get session manager for conversation tracking
        session_manager = await get_session_manager()
        
        # Add user message to conversation if session manager available
        if session_manager:
            await session_manager.add_conversation_message(
                session_id=session_id,
                agent_type="guide_agent",
                role="user",
                content=request.message
            )
        
        guide_agent = await get_guide_agent()
        
        if guide_agent and hasattr(guide_agent, 'provide_guidance'):
            # Use real Guide Agent (new pattern)
            logger.info("Using real Guide Agent for intent analysis")
            user_context = {
                "user_id": request.user_id
            }
            if request.context:
                user_context.update(request.context)
            
            result = await guide_agent.provide_guidance({
                "message": request.message,
                "session_id": session_id,
                "user_id": request.user_id,
                "user_context": user_context
            })
            
            # Extract guidance text
            guidance_text = result.get("guidance", "") if isinstance(result, dict) else str(result)
            
            # Add assistant response to conversation if session manager available
            orchestrator_context = None
            if isinstance(result, dict) and result.get("workflow_id"):
                orchestrator_context = {
                    "orchestrator": result.get("orchestrator"),
                    "workflow_id": result.get("workflow_id"),
                    "status": result.get("status", "active")
                }
            
            if session_manager:
                await session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type="guide_agent",
                    role="assistant",
                    content=guidance_text,
                    orchestrator_context=orchestrator_context
                )
            
            # Build intent analysis from result
            intent_analysis = {
                "primary_intent": result.get("intent", "user_guidance") if isinstance(result, dict) else "user_guidance",
                "confidence": result.get("confidence", 0.8) if isinstance(result, dict) else 0.8,
                "recommended_pillar": result.get("recommended_pillar") if isinstance(result, dict) else None,
                "recommended_actions": result.get("recommended_actions", []) if isinstance(result, dict) else []
            }
            
            return AnalyzeUserIntentResponse(
                success=True,
                intent_analysis=intent_analysis,
                session_id=session_id,
                timestamp=datetime.utcnow().isoformat(),
                message="Intent analyzed successfully"
            )
        else:
            # Fallback
            logger.warning("⚠️ Guide Agent not available, using mock analysis")
            return AnalyzeUserIntentResponse(
                success=True,
                intent_analysis={
                    "primary_intent": "user_guidance",
                    "confidence": 0.8,
                    "recommended_pillar": None,
                    "recommended_actions": []
                },
                session_id=session_id,
                timestamp=datetime.utcnow().isoformat(),
                message="Intent analyzed (mock mode)"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic analyze-user-intent error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent analysis failed: {str(e)}"
        )


@router.post("/get-journey-guidance", response_model=GetJourneyGuidanceResponse)
async def get_journey_guidance(
    request: GetJourneyGuidanceRequest
):
    """
    Get journey guidance from Guide Agent.
    
    This semantic endpoint provides guidance on the user's journey through
    the platform, suggesting next steps and recommended pillars.
    
    Args:
        request: Journey guidance request
        
    Returns:
        GetJourneyGuidanceResponse with guidance
    """
    try:
        logger.info(f"🗺️ Semantic get-journey-guidance request")
        
        guide_agent = await get_guide_agent()
        
        if guide_agent and hasattr(guide_agent, 'provide_guidance'):
            result = await guide_agent.provide_guidance({
                "message": f"I want to {request.user_goal}",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "user_context": {
                    "current_pillar": request.current_pillar
                }
            })
            
            guidance = {
                "next_steps": result.get("next_steps", []) if isinstance(result, dict) else [],
                "recommended_pillar": result.get("recommended_pillar") if isinstance(result, dict) else None,
                "suggested_actions": result.get("recommended_actions", []) if isinstance(result, dict) else []
            }
            
            return GetJourneyGuidanceResponse(
                success=True,
                guidance=guidance,
                message="Journey guidance retrieved successfully"
            )
        else:
            # Fallback
            return GetJourneyGuidanceResponse(
                success=True,
                guidance={
                    "next_steps": [],
                    "recommended_pillar": None,
                    "suggested_actions": []
                },
                message="Journey guidance retrieved (mock mode)"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic get-journey-guidance error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get journey guidance: {str(e)}"
        )


@router.get("/get-conversation-history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history_from_guide_agent(
    session_id: str
):
    """
    Get conversation history from Guide Agent.
    
    This semantic endpoint retrieves the conversation history between the
    user and the Guide Agent for a given session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        ConversationHistoryResponse with conversation history
    """
    try:
        logger.info(f"📜 Semantic get-conversation-history request: {session_id}")
        
        session_manager = await get_session_manager()
        
        if session_manager:
            session_result = await session_manager.get_session(session_id)
            if session_result.get("success"):
                session = session_result.get("session", {})
                conversations = session.get("conversations", {})
                guide_conversation = conversations.get("guide_agent", {})
                
                return ConversationHistoryResponse(
                    success=True,
                    conversation={
                        "messages": guide_conversation.get("messages", []),
                        "orchestrator_context": guide_conversation.get("orchestrator_context", {})
                    },
                    message="Conversation history retrieved successfully"
                )
        
        # Fallback
        return ConversationHistoryResponse(
            success=True,
            conversation={
                "messages": [],
                "orchestrator_context": {}
            },
            message="Conversation history retrieved (empty)"
        )
        
    except Exception as e:
        logger.error(f"❌ Semantic get-conversation-history error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@router.get("/health")
async def guide_agent_health():
    """Guide Agent health check."""
    return {
        "status": "healthy",
        "agent": "guide_agent",
        "timestamp": datetime.utcnow().isoformat()
    }

