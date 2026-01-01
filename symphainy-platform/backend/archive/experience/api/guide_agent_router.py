#!/usr/bin/env python3
"""
Guide Agent API Router

Handles Guide Agent operations (recommendations, analysis, chat).
Routes through Guide Agent service for AI-powered assistance.
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Create routers
router = APIRouter(prefix="/api/global", tags=["Guide Agent"])
ws_router = APIRouter(tags=["Guide Agent WebSocket"])

# Request/Response models
class AgentAnalyzeRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    session_token: Optional[str] = None
    user_id: Optional[str] = "anonymous"

# Platform orchestrator reference
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    """Set the platform orchestrator reference."""
    global _platform_orchestrator
    _platform_orchestrator = orchestrator
    logger.info("✅ Guide Agent router connected to platform orchestrator")


def get_city_manager():
    """Get City Manager from platform orchestrator."""
    if not _platform_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Platform not initialized"
        )
    return _platform_orchestrator.managers.get("city_manager")


async def get_guide_agent():
    """Get Guide Agent service."""
    try:
        city_manager = get_city_manager()
        if not city_manager:
            logger.warning("City Manager not available")
            return None
        
        # Try to get Guide Agent from DI container
        di_container = _platform_orchestrator.infrastructure_services.get("di_container")
        if di_container:
            guide_agent = di_container.service_registry.get("GuideAgent")
            if guide_agent:
                logger.info("✅ Retrieved Guide Agent from DI container")
                return guide_agent
        
        # Try to get from Experience Manager
        experience_manager = city_manager.manager_hierarchy.get("experience_manager", {}).get("instance")
        if experience_manager:
            guide_agent = getattr(experience_manager, 'guide_agent', None)
            if guide_agent:
                logger.info("✅ Retrieved Guide Agent from Experience Manager")
                return guide_agent
        
        logger.warning("Guide Agent not available")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Guide Agent: {e}")
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


async def get_session_id_from_token(session_token: Optional[str]) -> Optional[str]:
    """
    Get session_id from session_token.
    
    If session_token is None, creates a new session.
    If session_token is provided, validates and returns session_id.
    """
    if not session_token:
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
    
    # Try to find session by token
    # For now, assume session_token == session_id (we'll improve this later)
    # TODO: Add proper token-to-session-id mapping
    session_manager = await get_session_manager()
    if session_manager:
        # Try to get session - if it exists, return session_id
        result = await session_manager.get_session(session_token)
        if result.get("success"):
            return session_token
    
    # If not found, create new session
    if session_manager:
        result = await session_manager.create_session(
            user_id="anonymous",
            context={}
        )
        if result.get("success"):
            return result.get("session", {}).get("session_id")
    
    return None


@router.post("/agent/analyze")
async def analyze_with_agent(request: AgentAnalyzeRequest):
    """
    Analyze user request and provide personalized recommendations.
    
    This is the endpoint called from the landing page "Get personalized recommendations" button.
    """
    try:
        logger.info(f"🤖 Guide Agent analysis request: {request.message[:100]}...")
        
        # Get session_id from session_token
        session_id = await get_session_id_from_token(request.session_token)
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
            logger.info("Using real Guide Agent for analysis")
            result = await guide_agent.provide_guidance({
                "message": request.message,
                "session_id": session_id,  # Pass session_id
                "user_id": request.user_id,
                "user_context": {
                    "user_id": request.user_id,
                    **request.context
                }
            })
            
            # Extract guidance text
            guidance_text = result.get("guidance", "") if isinstance(result, dict) else str(result)
            
            # Add assistant response to conversation if session manager available
            orchestrator_context = None
            if result.get("workflow_id"):
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
            
            return {
                "success": True,
                "analysis": result,
                "session_id": session_id,  # Return session_id
                "timestamp": datetime.utcnow().isoformat()
            }
        elif guide_agent and hasattr(guide_agent, 'analyze_global_request'):
            # Legacy pattern (backward compatibility)
            logger.info("Using legacy Guide Agent for analysis")
            result = await guide_agent.analyze_global_request({
                "message": request.message,
                "context": {
                    "user_id": request.user_id,
                    "session_id": session_id,
                    **request.context
                }
            })
            
            # Add assistant response to conversation
            if session_manager:
                guidance_text = result.get("guidance", "") if isinstance(result, dict) else str(result)
                await session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type="guide_agent",
                    role="assistant",
                    content=guidance_text
                )
            
            return {
                "success": True,
                "analysis": result,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # MVP Fallback: Smart recommendations based on keywords
        logger.warning("⚠️ Guide Agent not available, using smart fallback")
        message_lower = request.message.lower()
        
        recommendations = []
        recommended_pillar = None
        
        # Keyword-based intent detection
        if any(word in message_lower for word in ["upload", "file", "document", "content"]):
            recommended_pillar = "content"
            recommendations.append({
                "type": "navigation",
                "pillar": "content",
                "action": "upload_file",
                "message": "Navigate to Content Pillar to upload and manage your files"
            })
        elif any(word in message_lower for word in ["analyze", "insight", "data", "report", "visualization"]):
            recommended_pillar = "insights"
            recommendations.append({
                "type": "navigation",
                "pillar": "insights",
                "action": "analyze_data",
                "message": "Navigate to Insights Pillar to analyze your data and generate reports"
            })
        elif any(word in message_lower for word in ["workflow", "process", "sop", "procedure", "operations"]):
            recommended_pillar = "operations"
            recommendations.append({
                "type": "navigation",
                "pillar": "operations",
                "action": "create_workflow",
                "message": "Navigate to Operations Pillar to create workflows and SOPs"
            })
        elif any(word in message_lower for word in ["roadmap", "strategy", "poc", "proposal", "business", "outcome"]):
            recommended_pillar = "business_outcomes"
            recommendations.append({
                "type": "navigation",
                "pillar": "business_outcomes",
                "action": "create_roadmap",
                "message": "Navigate to Business Outcomes Pillar to generate strategic roadmaps"
            })
        else:
            # Generic guidance
            recommendations = [
                {
                    "type": "guidance",
                    "message": "I can help you with:",
                    "options": [
                        "Upload and manage files (Content Pillar)",
                        "Analyze data and generate insights (Insights Pillar)",
                        "Create workflows and SOPs (Operations Pillar)",
                        "Generate strategic roadmaps (Business Outcomes Pillar)"
                    ]
                }
            ]
        
        return {
            "success": True,
            "analysis": {
                "intent": "user_guidance",
                "recommended_pillar": recommended_pillar,
                "recommendations": recommendations,
                "confidence": 0.8
            },
            "message": "Based on your request, here are my recommendations",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Guide Agent analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@ws_router.websocket("/guide-agent")
async def guide_agent_websocket(
    websocket: WebSocket,
    session_token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time Guide Agent chat.
    
    Provides conversational AI guidance and recommendations.
    """
    await websocket.accept()
    logger.info(f"🔌 Guide Agent WebSocket connected - session: {session_token}")
    
    try:
        guide_agent = await get_guide_agent()
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse message
                message_data = json.loads(data)
                user_message = message_data.get("message", data)
                user_id = message_data.get("user_id", "anonymous")
                
                logger.info(f"💬 Guide Agent message from {user_id}: {user_message[:100]}...")
                
                # Get session_id from session_token
                session_id = await get_session_id_from_token(session_token)
                if not session_id:
                    session_id = "default"
                
                # Get session manager for conversation tracking
                session_manager = await get_session_manager()
                
                # Add user message to conversation
                if session_manager:
                    await session_manager.add_conversation_message(
                        session_id=session_id,
                        agent_type="guide_agent",
                        role="user",
                        content=user_message
                    )
                
                # Process via Guide Agent
                if guide_agent and hasattr(guide_agent, 'provide_guidance'):
                    # New pattern
                    result = await guide_agent.provide_guidance({
                        "message": user_message,
                        "session_id": session_id,
                        "user_id": user_id,
                        "user_context": {}
                    })
                    guidance_text = result.get("guidance", "") if isinstance(result, dict) else str(result)
                    response = {
                        "success": True,
                        "message": guidance_text,
                        "type": "agent_response"
                    }
                elif guide_agent and hasattr(guide_agent, 'process_user_message'):
                    # Legacy pattern
                    response = await guide_agent.process_user_message({
                        "message": user_message,
                        "user_id": user_id,
                        "session_id": session_id
                    })
                else:
                    # Fallback response
                    response = {
                        "success": True,
                        "message": f"I received your message: '{user_message}'. The Guide Agent service will be fully operational soon!",
                        "type": "acknowledgment"
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
                        agent_type="guide_agent",
                        role="assistant",
                        content=response.get("message", "") if isinstance(response, dict) else str(response),
                        orchestrator_context=orchestrator_context
                    )
                
                # Send response
                await websocket.send_json({
                    "type": "agent_response",
                    "data": response,
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
        logger.info("🔌 Guide Agent WebSocket disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass


@router.get("/agent/health")
async def agent_health():
    """Guide Agent health check."""
    guide_agent = await get_guide_agent()
    
    return {
        "status": "healthy",
        "service": "guide_agent",
        "guide_agent_available": guide_agent is not None,
        "websocket_available": True,
        "mode": "production" if guide_agent else "fallback"
    }


