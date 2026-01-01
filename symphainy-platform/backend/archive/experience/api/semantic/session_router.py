#!/usr/bin/env python3
"""
Semantic Session Router

User-focused semantic API endpoints for session management.
Uses semantic naming that aligns with user journeys and mental models.

Endpoints:
- POST /api/session/create-user-session
- GET  /api/session/get-session-details/{session_id}
- GET  /api/session/get-session-state/{session_id}
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Create semantic router
router = APIRouter(prefix="/api/session", tags=["Session"])

# Import helpers from existing routers
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ..session_router import (
    set_platform_orchestrator as set_platform_orchestrator_base,
    get_session_manager,
    get_traffic_cop,
    get_initial_orchestrator_states
)

# Request/Response models
class CreateUserSessionRequest(BaseModel):
    """Request model for session creation."""
    user_id: Optional[str] = None
    session_type: str = "mvp"
    context: Optional[Dict[str, Any]] = None

class CreateUserSessionResponse(BaseModel):
    """Semantic response model for session creation."""
    success: bool
    session_id: Optional[str] = None
    session_token: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    orchestrator_states: Optional[Dict[str, str]] = None
    orchestrator_context: Optional[Dict[str, Any]] = None
    conversations: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class SessionDetailsResponse(BaseModel):
    """Semantic response model for session details."""
    success: bool
    session: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class SessionStateResponse(BaseModel):
    """Semantic response model for session state."""
    success: bool
    state: Optional[Dict[str, Any]] = None
    orchestrator_states: Optional[Dict[str, str]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# Platform orchestrator reference
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    set_platform_orchestrator_base(orchestrator)
    logger.info("✅ Semantic Session router connected to platform orchestrator")


@router.post("/create-user-session", response_model=CreateUserSessionResponse)
async def create_user_session(
    request: CreateUserSessionRequest
):
    """
    Create a new user session.
    
    This semantic endpoint creates a new session for a user. It provides a
    user-focused API that aligns with the user journey of starting a new
    session on the platform.
    
    Args:
        request: Session creation request
        
    Returns:
        CreateUserSessionResponse with session details
    """
    try:
        logger.info(f"🎫 Semantic create-user-session request for user: {request.user_id or 'anonymous'}")
        
        # Try Session Manager first (Experience realm)
        session_manager = await get_session_manager()
        if session_manager and hasattr(session_manager, 'create_session'):
            logger.info("Using Session Manager for session creation")
            result = await session_manager.create_session(
                user_id=request.user_id or f"anon_{uuid.uuid4().hex[:8]}",
                context=request.context or {}
            )
            
            # Get orchestrator states from session
            session = result.get("session", {})
            orchestrator_context = session.get("orchestrator_context", {})
            active_orchestrators = orchestrator_context.get("active_orchestrators", [])
            
            # Build orchestrator states dict
            orchestrator_states = {}
            for orch in active_orchestrators:
                orchestrator_states[orch.get("orchestrator_name")] = orch.get("status", "not_started")
            
            # If no orchestrators active, initialize defaults
            if not orchestrator_states:
                orchestrator_states = get_initial_orchestrator_states()
            
            return CreateUserSessionResponse(
                success=True,
                session_id=session.get("session_id") or result.get("session_id"),
                session_token=result.get("session_token"),
                user_id=session.get("user_id") or result.get("user_id"),
                created_at=session.get("created_at") or result.get("created_at"),
                orchestrator_states=orchestrator_states,
                orchestrator_context=orchestrator_context,
                conversations=session.get("conversations", {}),
                message="Session created successfully"
            )
        
        # Fallback to Traffic Cop
        traffic_cop = await get_traffic_cop()
        if traffic_cop and hasattr(traffic_cop, 'create_session'):
            logger.info("Using Traffic Cop for session creation")
            result = await traffic_cop.create_session({
                "user_id": request.user_id or f"anon_{uuid.uuid4().hex[:8]}",
                "session_type": request.session_type,
                "context": request.context or {}
            })
            
            # Get orchestrator states from result
            orchestrator_context = result.get("orchestrator_context", {})
            active_orchestrators = orchestrator_context.get("active_orchestrators", [])
            
            # Build orchestrator states dict
            orchestrator_states = {}
            for orch in active_orchestrators:
                orchestrator_states[orch.get("orchestrator_name")] = orch.get("status", "not_started")
            
            # If no orchestrators active, initialize defaults
            if not orchestrator_states:
                orchestrator_states = get_initial_orchestrator_states()
            
            return CreateUserSessionResponse(
                success=True,
                session_id=result.get("session_id"),
                session_token=result.get("session_token"),
                user_id=result.get("user_id"),
                created_at=result.get("created_at"),
                orchestrator_states=orchestrator_states,
                orchestrator_context=orchestrator_context,
                conversations=result.get("conversations", {}),
                message="Session created successfully"
            )
        
        # MVP Fallback: Mock session
        logger.warning("⚠️ Using mock session management for MVP")
        session_id = f"session_{uuid.uuid4().hex}"
        user_id = request.user_id or f"anon_{uuid.uuid4().hex[:8]}"
        
        return CreateUserSessionResponse(
            success=True,
            session_id=session_id,
            session_token=f"token_{session_id}",
            user_id=user_id,
            created_at=datetime.utcnow().isoformat(),
            orchestrator_states=get_initial_orchestrator_states(),
            orchestrator_context={
                "active_orchestrators": [],
                "enabling_services": {},
                "workflow_delegation_chain": []
            },
            conversations={},
            message="Session created (mock mode)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic create-user-session error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@router.get("/get-session-details/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(
    session_id: str
):
    """
    Get detailed information about a session.
    
    This semantic endpoint retrieves comprehensive session details including
    orchestrator context and conversations.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionDetailsResponse with session details
    """
    try:
        logger.info(f"📋 Semantic get-session-details request: {session_id}")
        
        session_manager = await get_session_manager()
        
        if session_manager:
            result = await session_manager.get_session(session_id)
            if result.get("success"):
                return SessionDetailsResponse(
                    success=True,
                    session=result.get("session"),
                    message="Session details retrieved successfully"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.get("error", "Session not found")
                )
        
        # Fallback
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic get-session-details error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session details: {str(e)}"
        )


@router.get("/get-session-state/{session_id}", response_model=SessionStateResponse)
async def get_session_state(
    session_id: str
):
    """
    Get the current state of a session.
    
    This semantic endpoint retrieves the workflow state and orchestrator states
    for a session, providing a user-focused view of session progress.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionStateResponse with session state
    """
    try:
        logger.info(f"📊 Semantic get-session-state request: {session_id}")
        
        session_manager = await get_session_manager()
        
        if session_manager:
            result = await session_manager.get_session(session_id)
            if result.get("success"):
                session = result.get("session", {})
                
                # Extract orchestrator states
                orchestrator_context = session.get("orchestrator_context", {})
                active_orchestrators = orchestrator_context.get("active_orchestrators", [])
                
                orchestrator_states = {}
                for orch in active_orchestrators:
                    orchestrator_states[orch.get("orchestrator_name")] = orch.get("status", "not_started")
                
                return SessionStateResponse(
                    success=True,
                    state=session.get("state", {}),
                    orchestrator_states=orchestrator_states,
                    message="Session state retrieved successfully"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.get("error", "Session not found")
                )
        
        # Fallback
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Semantic get-session-state error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session state: {str(e)}"
        )


@router.get("/health")
async def session_health():
    """Session health check."""
    return {
        "status": "healthy",
        "service": "session",
        "timestamp": datetime.utcnow().isoformat()
    }






