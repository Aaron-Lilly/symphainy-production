#!/usr/bin/env python3
"""
Experience Layer FastAPI Bridge

This module creates the bridge between the Experience Layer and FastAPI,
providing the API endpoints that the frontend expects while using the
proper architectural patterns.

WHAT (Bridge): I connect Experience Layer services to FastAPI routes
HOW (Implementation): I create FastAPI routers that delegate to Experience Layer services
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Body, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
import json
import uuid
from datetime import datetime
import base64

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from experience.roles.frontend_integration.frontend_integration_service import FrontendIntegrationService

logger = logging.getLogger(__name__)


class ExperienceFastAPIBridge:
    """
    Bridge between Experience Layer and FastAPI.
    
    This class creates FastAPI routers that delegate to Experience Layer services,
    maintaining the proper architectural separation while providing the API endpoints
    that the frontend expects.
    """
    
    def __init__(self, di_container: DIContainerService, public_works_foundation: PublicWorksFoundationService):
        """Initialize the FastAPI bridge with DI container and public works foundation."""
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.frontend_integration_service = None
        self.routers = {}
        
        logger.info("🌉 Experience Layer FastAPI Bridge initialized")
    
    async def initialize(self):
        """Initialize the bridge and create all routers."""
        try:
            logger.info("🚀 Initializing Experience Layer FastAPI Bridge...")
            
            # Initialize Frontend Integration Service
            self.frontend_integration_service = FrontendIntegrationService(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation
            )
            await self.frontend_integration_service.initialize()
            
            # Create all routers
            await self._create_routers()
            
            logger.info("✅ Experience Layer FastAPI Bridge initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Experience Layer FastAPI Bridge: {e}")
            raise
    
    async def _create_routers(self):
        """Create all FastAPI routers for different pillars."""
        
        # Content Pillar Router
        self.routers['content'] = await self._create_content_router()
        
        # Insights Pillar Router
        self.routers['insights'] = await self._create_insights_router()
        
        # Operations Pillar Router
        self.routers['operations'] = await self._create_operations_router()
        
        # Business Outcomes Pillar Router
        self.routers['business_outcomes'] = await self._create_business_outcomes_router()
        
        # Global Router
        self.routers['global'] = await self._create_global_router()
        
        # WebSocket Router
        self.routers['websocket'] = await self._create_websocket_router()
        
        logger.info(f"✅ Created {len(self.routers)} FastAPI routers")
    
    async def _create_content_router(self) -> APIRouter:
        """Create content pillar router."""
        router = APIRouter(prefix="/api/content", tags=["Content"])
        
        @router.get("/files")
        async def get_files(request: Request):
            """Get list of files."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/content/files",
                    method="GET",
                    user_context=user_context
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in get_files: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.post("/upload")
        async def upload_file(
            request: Request,
            file: UploadFile = File(None),
            file_data: Optional[str] = Form(None),
            user_id: Optional[str] = Form(None)
        ):
            """Upload a file (supports both multipart and JSON)."""
            try:
                # Handle multipart file upload
                if file:
                    file_content = await file.read()
                    file_b64 = base64.b64encode(file_content).decode('utf-8')
                    
                    upload_data = {
                        "filename": file.filename,
                        "content": file_b64,
                        "content_type": file.content_type,
                        "user_id": user_id or "anonymous"
                    }
                # Handle JSON body (for backward compatibility)
                elif file_data:
                    upload_data = json.loads(file_data) if isinstance(file_data, str) else file_data
                else:
                    # Try to get JSON from request body
                    try:
                        upload_data = await request.json()
                    except:
                        raise HTTPException(status_code=400, detail="No file or data provided")
                
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/content/upload-file",
                    method="POST",
                    user_context=user_context,
                    data=upload_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in upload_file: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.post("/parse")
        async def parse_file(request: Request, parse_data: Dict[str, Any] = Body(...)):
            """Parse a file."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/content/parse",
                    method="POST",
                    user_context=user_context,
                    data=parse_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in parse_file: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.post("/parse/{file_id}")
        async def parse_file_by_id(request: Request, file_id: str):
            """Parse a file by ID."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint=f"/api/content/parse/{file_id}",
                    method="POST",
                    user_context=user_context,
                    data={"file_id": file_id}
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in parse_file_by_id: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/health")
        async def health_check():
            """Content pillar health check."""
            return {"status": "healthy", "pillar": "content", "timestamp": datetime.utcnow().isoformat()}
        
        return router
    
    async def _create_insights_router(self) -> APIRouter:
        """Create insights pillar router."""
        router = APIRouter(prefix="/api/insights", tags=["Insights"])
        
        @router.post("/analyze")
        async def analyze_data(request: Request, analysis_data: Dict[str, Any] = Body(...)):
            """Analyze data."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/insights/analyze",
                    method="POST",
                    user_context=user_context,
                    data=analysis_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in analyze_data: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/insights")
        async def get_insights(request: Request):
            """Get insights."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/insights/insights",
                    method="GET",
                    user_context=user_context
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in get_insights: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/health")
        async def health_check():
            """Insights pillar health check."""
            return {"status": "healthy", "pillar": "insights", "timestamp": datetime.utcnow().isoformat()}
        
        return router
    
    async def _create_operations_router(self) -> APIRouter:
        """Create operations pillar router."""
        router = APIRouter(prefix="/api/operations", tags=["Operations"])
        
        @router.post("/sop-builder")
        async def create_sop(request: Request, sop_data: Dict[str, Any] = Body(...)):
            """Create SOP."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/operations/sop-builder",
                    method="POST",
                    user_context=user_context,
                    data=sop_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in create_sop: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.post("/workflow-builder")
        async def create_workflow(request: Request, workflow_data: Dict[str, Any] = Body(...)):
            """Create workflow."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/operations/workflow-builder",
                    method="POST",
                    user_context=user_context,
                    data=workflow_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in create_workflow: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/health")
        async def health_check():
            """Operations pillar health check."""
            return {"status": "healthy", "pillar": "operations", "timestamp": datetime.utcnow().isoformat()}
        
        return router
    
    async def _create_business_outcomes_router(self) -> APIRouter:
        """Create business outcomes pillar router."""
        router = APIRouter(prefix="/api/business-outcomes", tags=["Business Outcomes"])
        
        @router.post("/strategic-planning")
        async def create_strategic_plan(request: Request, plan_data: Dict[str, Any] = Body(...)):
            """Create strategic plan."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/business-outcomes/strategic-planning",
                    method="POST",
                    user_context=user_context,
                    data=plan_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in create_strategic_plan: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/metrics")
        async def get_metrics(request: Request):
            """Get business metrics."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/business-outcomes/metrics",
                    method="GET",
                    user_context=user_context
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in get_metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/health")
        async def health_check():
            """Business outcomes pillar health check."""
            return {"status": "healthy", "pillar": "business_outcomes", "timestamp": datetime.utcnow().isoformat()}
        
        return router
    
    async def _create_global_router(self) -> APIRouter:
        """Create global router for session management and other global operations."""
        router = APIRouter(prefix="/api/global", tags=["Global"])
        
        @router.post("/session")
        async def start_session(request: Request, session_data: Dict[str, Any] = Body(...)):
            """Start a global session."""
            try:
                user_context = await self._extract_user_context(request)
                result = await self.frontend_integration_service.route_api_request(
                    endpoint="/api/global/session",
                    method="POST",
                    user_context=user_context,
                    data=session_data
                )
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Error in start_session: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @router.get("/health")
        async def health_check():
            """Global services health check."""
            return {"status": "healthy", "service": "global", "timestamp": datetime.utcnow().isoformat()}
        
        return router
    
    async def _extract_user_context(self, request: Request) -> Dict[str, Any]:
        """Extract user context from request."""
        # For now, create a basic user context
        # In a real implementation, this would extract from JWT tokens, session data, etc.
        return {
            "user_id": "default_user",
            "tenant_id": "default_tenant",
            "session_id": "default_session",
            "permissions": ["read", "write"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _create_websocket_router(self) -> APIRouter:
        """Create WebSocket router for agent chat."""
        router = APIRouter()
        
        @router.websocket("/smart-chat")
        async def smart_chat_websocket(websocket: WebSocket):
            """Enhanced WebSocket with tenant-aware agent routing."""
            await websocket.accept()
            session_id = str(uuid.uuid4())
            
            try:
                logger.info(f"WebSocket connection established: {session_id}")
                
                while True:
                    # Receive message from client
                    data = await websocket.receive_text()
                    logger.info(f"Received message from {session_id}: {data[:100]}...")
                    
                    try:
                        # Parse the message with sophisticated agent routing support
                        message_data = json.loads(data)
                        user_message = message_data.get("message", data)
                        user_id = message_data.get("user_id", "default_user")
                        session_token = message_data.get("session_token", "")
                        
                        # Support both legacy and new agent routing patterns
                        agent_type = message_data.get("agent_type", message_data.get("agent", "guide"))
                        current_pillar = message_data.get("current_pillar", "")
                        file_context = message_data.get("file_context", {})
                        
                        # Map agent types to proper names
                        agent_mapping = {
                            "guide": "GuideAgent",
                            "content": "ContentAgent", 
                            "insights": "InsightsAgent",
                            "operations": "OperationsAgent",
                            "business-outcomes": "BusinessOutcomesAgent"
                        }
                        agent_name = agent_mapping.get(agent_type, "GuideAgent")
                        
                    except json.JSONDecodeError:
                        # Fallback: treat as plain text
                        user_message = data
                        user_id = "default_user"
                        session_token = ""
                        agent_type = "guide"
                        agent_name = "GuideAgent"
                        current_pillar = ""
                        file_context = {}
                    
                    # Create user context with agent routing information
                    user_context = {
                        "user_id": user_id,
                        "session_id": session_id,
                        "session_token": session_token,
                        "agent_type": agent_type,
                        "agent_name": agent_name,
                        "current_pillar": current_pillar,
                        "file_context": file_context,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Route the message through the Experience Layer with proper agent routing
                    try:
                        # Determine the appropriate endpoint based on agent type
                        if agent_type == "guide":
                            endpoint = "/api/guide-agent"
                        elif agent_type == "content":
                            endpoint = "/api/content-agent"
                        elif agent_type == "insights":
                            endpoint = "/api/insights-agent"
                        elif agent_type == "operations":
                            endpoint = "/api/operations-agent"
                        elif agent_type == "business-outcomes":
                            endpoint = "/api/business-outcomes-agent"
                        else:
                            endpoint = "/api/agent-chat"
                        
                        result = await self.frontend_integration_service.route_api_request(
                            endpoint=endpoint,
                            method="POST",
                            user_context=user_context,
                            data={
                                "message": user_message, 
                                "agent_type": agent_type,
                                "agent_name": agent_name,
                                "current_pillar": current_pillar,
                                "file_context": file_context
                            }
                        )
                        
                        # Send response back to client in the format expected by frontend
                        response = {
                            "success": True,
                            "content": result.get("data", {}).get("response", "Message processed successfully"),
                            "agent": agent_name,
                            "current_pillar": current_pillar or result.get("pillar", "unknown"),
                            "tenant_id": user_context.get("user_id", "default_tenant"),
                            "conversation_id": session_id,
                            "intent_type": agent_type,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        await websocket.send_text(json.dumps(response))
                        logger.info(f"Sent response to {session_id}")
                        
                    except Exception as e:
                        logger.error(f"Error processing message from {session_id}: {e}")
                        error_response = {
                            "success": False,
                            "error": str(e),
                            "session_id": session_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await websocket.send_text(json.dumps(error_response))
                        
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {session_id}")
            except Exception as e:
                logger.error(f"WebSocket error for {session_id}: {e}")
        
        @router.websocket("/ws/agent-chat")
        async def agent_chat_websocket(websocket: WebSocket):
            """Legacy WebSocket endpoint for backward compatibility."""
            await smart_chat_websocket(websocket)
        
        return router

    def get_all_routers(self) -> Dict[str, APIRouter]:
        """Get all created routers."""
        return self.routers
