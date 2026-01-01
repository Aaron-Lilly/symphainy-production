#!/usr/bin/env python3
"""
Session API Router

Handles global session management.
Routes requests to Traffic Cop (Smart City) via City Manager.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/global", tags=["session"])

# Request/Response models
class SessionRequest(BaseModel):
    user_id: Optional[str] = None
    session_type: str = "mvp"
    context: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    session_token: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    orchestrator_states: Optional[Dict[str, str]] = None  # CHANGED: Orchestrator workflow states
    orchestrator_context: Optional[Dict[str, Any]] = None  # NEW: Orchestrator context
    conversations: Optional[Dict[str, Any]] = None  # NEW: Agent conversations
    error: Optional[str] = None


# Platform orchestrator reference (set by main.py)
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    logger.info("✅ Session router connected to platform orchestrator")


def get_initial_orchestrator_states() -> Dict[str, str]:
    """Get initial orchestrator states for workflow tracking."""
    return {
        "ContentAnalysisOrchestrator": "not_started",
        "InsightsOrchestrator": "not_started",
        "OperationsOrchestrator": "not_started",
        "BusinessOutcomesOrchestrator": "not_started"
    }


def get_city_manager():
    """Get City Manager from platform orchestrator."""
    if not _platform_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform not initialized"
        )
    return _platform_orchestrator.managers.get("city_manager")


async def get_traffic_cop():
    """Get Traffic Cop service via City Manager."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            logger.warning("City Manager not available")
            return None
        
        # Try to get Traffic Cop from DI container
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            traffic_cop = di_container.service_registry.get("TrafficCop")
            if traffic_cop:
                logger.info("✅ Retrieved Traffic Cop from DI container")
                return traffic_cop
        
        logger.warning("Traffic Cop not available, using mock session management")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Traffic Cop: {e}")
        return None


async def get_session_manager():
    """Get Session Manager service via Experience Manager."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            return None
        
        # Try to get Session Manager from Experience Manager hierarchy
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
        
        logger.warning("Session Manager not available")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Session Manager: {e}")
        return None


@router.post("/session", response_model=SessionResponse)
async def create_session(request: SessionRequest = None):
    """
    Create a new global session.
    
    For MVP: Creates mock session if Traffic Cop unavailable.
    Production: Uses Traffic Cop for session management.
    """
    try:
        if request is None:
            request = SessionRequest()
            
        logger.info(f"🎫 Creating session for user: {request.user_id or 'anonymous'}")
        
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
            
            return SessionResponse(
                success=True,
                session_id=session.get("session_id") or result.get("session_id"),
                session_token=result.get("session_token"),
                user_id=session.get("user_id") or result.get("user_id"),
                created_at=session.get("created_at") or result.get("created_at"),
                orchestrator_states=orchestrator_states,
                orchestrator_context=orchestrator_context,
                conversations=session.get("conversations", {})
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
            
            return SessionResponse(
                success=True,
                session_id=result.get("session_id"),
                session_token=result.get("session_token"),
                user_id=result.get("user_id"),
                created_at=result.get("created_at"),
                orchestrator_states=orchestrator_states,
                orchestrator_context=orchestrator_context,
                conversations=result.get("conversations", {})
            )
        
        # MVP Fallback: Mock session
        logger.warning("⚠️ Using mock session management for MVP")
        session_id = f"session_{uuid.uuid4().hex}"
        user_id = request.user_id or f"anon_{uuid.uuid4().hex[:8]}"
        
        return SessionResponse(
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
            conversations={}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session by ID.
    
    For MVP: Returns mock session data.
    Production: Retrieves from Traffic Cop.
    """
    try:
        logger.info(f"📋 Getting session: {session_id}")
        
        session_manager = await get_session_manager()
        if session_manager and hasattr(session_manager, 'get_session'):
            result = await session_manager.get_session(session_id)
            return result
        
        traffic_cop = await get_traffic_cop()
        if traffic_cop and hasattr(traffic_cop, 'get_session'):
            result = await traffic_cop.get_session(session_id)
            return result
        
        # MVP Fallback
        return {
            "success": True,
            "session_id": session_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Get session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def destroy_session(session_id: str):
    """
    Destroy a session.
    
    For MVP: Returns success.
    Production: Destroys via Traffic Cop.
    """
    try:
        logger.info(f"🗑️ Destroying session: {session_id}")
        
        session_manager = await get_session_manager()
        if session_manager and hasattr(session_manager, 'destroy_session'):
            await session_manager.destroy_session(session_id)
            return {"success": True, "message": "Session destroyed"}
        
        traffic_cop = await get_traffic_cop()
        if traffic_cop and hasattr(traffic_cop, 'destroy_session'):
            await traffic_cop.destroy_session(session_id)
            return {"success": True, "message": "Session destroyed"}
        
        # MVP Fallback
        return {"success": True, "message": "Session destroyed"}
        
    except Exception as e:
        logger.error(f"❌ Destroy session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to destroy session: {str(e)}"
        )


@router.get("/health")
async def session_health():
    """Session service health check."""
    session_manager = await get_session_manager()
    traffic_cop = await get_traffic_cop()
    
    return {
        "status": "healthy",
        "service": "session_management",
        "session_manager_available": session_manager is not None,
        "traffic_cop_available": traffic_cop is not None,
        "mode": "production" if (session_manager or traffic_cop) else "mock"
    }


