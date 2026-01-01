#!/usr/bin/env python3
"""
Journey Realm Bridge - Journey API Integration within Communication Foundation

Provides Journey realm API endpoints through the unified Communication Foundation,
exposing Guide Agent and journey orchestration endpoints for external consumption.

WHAT (Realm Bridge): I provide Journey realm API endpoints through Communication Foundation
HOW (Bridge Implementation): I create Journey FastAPI router and register with Communication Foundation
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)


class JourneyRealmBridge:
    """
    Journey Realm Bridge - Journey API Integration within Communication Foundation
    
    Provides Journey realm API endpoints through the unified Communication Foundation,
    consolidating all Journey communication infrastructure in one place.
    
    WHAT (Realm Bridge): I provide Journey realm API endpoints through Communication Foundation
    HOW (Bridge Implementation): I create Journey FastAPI router and register with Communication Foundation
    """
    
    def __init__(self, di_container, public_works_foundation, curator_foundation):
        """Initialize Journey Realm Bridge."""
        self.logger = logging.getLogger("JourneyRealmBridge")
        
        # Dependencies
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Journey services (will be initialized)
        self.journey_manager = None
        self.mvp_journey_orchestrator = None
        self.session_manager = None
        
        # Session mapping cache (user_id -> session_id) for quick lookup
        # This is a temporary cache - in production, SessionManagerService should provide this
        self.user_session_cache: Dict[str, str] = {}
        
        # Router
        self.router = APIRouter(prefix="/api/v1/journey", tags=["journey"])
        
        self.logger.info("🏗️ Journey Realm Bridge initialized")
    
    async def initialize(self):
        """Initialize Journey Realm Bridge and create router."""
        try:
            self.logger.info("🚀 Initializing Journey Realm Bridge...")
            
            # Initialize Journey services
            await self._initialize_journey_services()
            
            # Create Journey API router
            await self._create_journey_router()
            
            self.logger.info("✅ Journey Realm Bridge initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Journey Realm Bridge: {e}", exc_info=True)
            raise
    
    async def get_router(self, user_context: Dict[str, Any] = None) -> APIRouter:
        """Get the Journey realm router."""
        try:
            # Note: Realm bridges don't have utility access yet
            # Security/tenant validation would be added when DI Container utilities are available
            return self.router
        except Exception as e:
            self.logger.error(f"❌ Failed to get router: {e}", exc_info=True)
            raise
    
    async def shutdown(self):
        """Shutdown Journey Realm Bridge."""
        try:
            self.logger.info("🛑 Shutting down Journey Realm Bridge...")
            # No cleanup needed for services (they're managed by DI Container)
            self.logger.info("✅ Journey Realm Bridge shutdown completed")
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Journey Realm Bridge: {e}", exc_info=True)
            raise
    
    # PRIVATE METHODS
    
    async def _initialize_journey_services(self):
        """Initialize Journey services from DI Container."""
        self.logger.info("🔧 Initializing Journey services...")
        
        try:
            # Get Journey Manager from DI Container
            self.journey_manager = self.di_container.service_registry.get("JourneyManagerService")
            if self.journey_manager:
                self.logger.info("✅ Journey Manager service found")
            else:
                self.logger.warning("⚠️ Journey Manager not available")
            
            # Get MVP Journey Orchestrator via Curator (it's registered with Curator)
            # If not found, lazy-initialize it (pattern for non-Smart City realms)
            self.mvp_journey_orchestrator = None
            if self.curator_foundation:
                try:
                    # Use discover_service_by_name (correct Curator method)
                    if hasattr(self.curator_foundation, 'discover_service_by_name'):
                        self.mvp_journey_orchestrator = await self.curator_foundation.discover_service_by_name("MVPJourneyOrchestratorService")
                    elif hasattr(self.curator_foundation, 'get_service'):
                        self.mvp_journey_orchestrator = await self.curator_foundation.get_service("MVPJourneyOrchestratorService")
                    else:
                        # Try direct service registry access
                        if hasattr(self.curator_foundation, 'service_registry'):
                            self.mvp_journey_orchestrator = self.curator_foundation.service_registry.get("MVPJourneyOrchestratorService")
                except Exception as e:
                    self.logger.debug(f"⚠️ Service discovery failed for MVP Journey Orchestrator: {e}")
                    # Continue to lazy initialization
                    self.mvp_journey_orchestrator = None
            
            # If not found via discovery, lazy-initialize it
            # This follows the pattern for non-Smart City realms (like SolutionRealmBridge)
            if not self.mvp_journey_orchestrator:
                self.logger.info("🔄 MVP Journey Orchestrator not found - lazy-initializing...")
                try:
                    from backend.journey.services.mvp_journey_orchestrator_service.mvp_journey_orchestrator_service import MVPJourneyOrchestratorService
                    
                    # Get platform gateway from DI container
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                    if not platform_gateway:
                        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                    
                    # Create and initialize MVP Journey Orchestrator
                    self.mvp_journey_orchestrator = MVPJourneyOrchestratorService(
                        service_name="MVPJourneyOrchestratorService",
                        realm_name="journey",
                        platform_gateway=platform_gateway,
                        di_container=self.di_container
                    )
                    await self.mvp_journey_orchestrator.initialize()
                    self.logger.info("✅ MVP Journey Orchestrator lazy-initialized successfully")
                except Exception as init_error:
                    self.logger.warning(f"⚠️ Failed to lazy-initialize MVP Journey Orchestrator: {init_error}")
                    import traceback
                    self.logger.debug(f"Traceback: {traceback.format_exc()}")
                    self.mvp_journey_orchestrator = None
            else:
                self.logger.info("✅ MVP Journey Orchestrator service found via discovery")
            
            # Get Session Manager Service from Experience Foundation (via DI Container or Curator)
            # If not found, lazy-initialize it (pattern for non-Smart City realms)
            self.session_manager = None
            try:
                # Try DI Container first
                self.session_manager = self.di_container.service_registry.get("SessionManagerService")
                if not self.session_manager and self.curator_foundation:
                    # Try Curator with correct method
                    if hasattr(self.curator_foundation, 'discover_service_by_name'):
                        self.session_manager = await self.curator_foundation.discover_service_by_name("SessionManagerService")
                    elif hasattr(self.curator_foundation, 'get_service'):
                        self.session_manager = await self.curator_foundation.get_service("SessionManagerService")
                    else:
                        # Try direct service registry access
                        if hasattr(self.curator_foundation, 'service_registry'):
                            self.session_manager = self.curator_foundation.service_registry.get("SessionManagerService")
            except Exception as e:
                self.logger.debug(f"⚠️ Service discovery failed for Session Manager: {e}")
                # Continue to lazy initialization
                self.session_manager = None
            
            # If not found via discovery, lazy-initialize it
            # This follows the pattern for non-Smart City realms (like SolutionRealmBridge)
            if not self.session_manager:
                self.logger.info("🔄 Session Manager not found - lazy-initializing...")
                try:
                    # Get Experience Foundation from DI container
                    experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")
                    if not experience_foundation:
                        experience_foundation = self.di_container.service_registry.get("ExperienceFoundationService")
                    
                    if experience_foundation:
                        # Use Experience Foundation SDK to create Session Manager
                        self.session_manager = await experience_foundation.create_session_manager(
                            realm_name="journey",
                            config={"session_ttl": 3600}
                        )
                        self.logger.info("✅ Session Manager lazy-initialized successfully via Experience Foundation SDK")
                    else:
                        # Fallback: Create SessionManagerService directly (if Experience Foundation not available)
                        from foundations.experience_foundation.services.session_manager_service.session_manager_service import SessionManagerService
                        
                        # Get platform gateway from DI container
                        platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                        if not platform_gateway:
                            platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                        
                        # Create and initialize Session Manager directly
                        self.session_manager = SessionManagerService(
                            service_name="SessionManagerService",
                            realm_name="experience",
                            platform_gateway=platform_gateway,
                            di_container=self.di_container
                        )
                        await self.session_manager.initialize()
                        self.logger.info("✅ Session Manager lazy-initialized successfully (direct creation)")
                except Exception as init_error:
                    self.logger.warning(f"⚠️ Failed to lazy-initialize Session Manager: {init_error}")
                    import traceback
                    self.logger.debug(f"Traceback: {traceback.format_exc()}")
                    self.session_manager = None
            else:
                self.logger.info("✅ Session Manager service found via discovery")
            
            self.logger.info("✅ Journey services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Journey services: {e}")
            raise
    
    async def _create_journey_router(self):
        """Create Journey realm FastAPI router with all endpoints."""
        self.logger.info("🔧 Creating Journey realm router...")
        
        # Dependency injection functions
        def get_journey_manager():
            """Get Journey Manager Service instance."""
            if not self.journey_manager:
                raise HTTPException(status_code=503, detail="Journey Manager not available")
            return self.journey_manager
        
        def get_mvp_journey_orchestrator():
            """Get MVP Journey Orchestrator instance."""
            if not self.mvp_journey_orchestrator:
                raise HTTPException(status_code=503, detail="MVP Journey Orchestrator not available")
            return self.mvp_journey_orchestrator
        
        def get_session_manager():
            """Get Session Manager Service instance."""
            if not self.session_manager:
                raise HTTPException(status_code=503, detail="Session Manager not available")
            return self.session_manager
        
        # Helper function to get or create session for user
        async def get_or_create_user_session(user_id: str, session_id: Optional[str] = None) -> str:
            """
            Get existing session for user or create a new one.
            
            Args:
                user_id: User ID
                session_id: Optional session ID (if provided, validates and returns it)
            
            Returns:
                session_id
            """
            if not self.session_manager:
                raise HTTPException(status_code=503, detail="Session Manager not available")
            
            # If session_id provided, validate it exists and belongs to user
            if session_id:
                session_result = await self.session_manager.get_session(session_id)
                if session_result.get("success"):
                    session = session_result.get("session", {})
                    if session.get("user_id") == user_id:
                        # Update cache
                        self.user_session_cache[user_id] = session_id
                        return session_id
                    else:
                        raise HTTPException(
                            status_code=403,
                            detail="Session does not belong to this user"
                        )
                else:
                    # Session not found, will create new one below
                    self.logger.warning(f"Session {session_id} not found, creating new session")
            
            # Check cache for existing session
            if user_id in self.user_session_cache:
                cached_session_id = self.user_session_cache[user_id]
                # Validate cached session still exists
                session_result = await self.session_manager.get_session(cached_session_id)
                if session_result.get("success"):
                    session = session_result.get("session", {})
                    # Check if session is expired
                    from datetime import datetime
                    expires_at = datetime.fromisoformat(session.get("expires_at", "1970-01-01T00:00:00"))
                    if datetime.utcnow() < expires_at:
                        return cached_session_id
                    else:
                        # Session expired, remove from cache
                        del self.user_session_cache[user_id]
            
            # Create new session for user
            session_result = await self.session_manager.create_session(
                user_id=user_id,
                context={"journey_type": "mvp", "created_via": "journey_bridge"}
            )
            
            if session_result.get("success"):
                new_session_id = session_result["session"]["session_id"]
                # Update cache
                self.user_session_cache[user_id] = new_session_id
                self.logger.info(f"✅ Created session {new_session_id} for user {user_id}")
                return new_session_id
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create session: {session_result.get('error', 'Unknown error')}"
                )
        
        # ============================================================================
        # GUIDE AGENT ENDPOINTS
        # ============================================================================
        
        @self.router.get("/guide-agent/get-journey-guidance")
        async def get_journey_guidance_get(
            user_id: str = "default_user",
            session_id: Optional[str] = None,
            current_pillar: Optional[str] = None,
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Get journey guidance (recommended next pillar) for Guide Agent (GET)."""
            try:
                # Get or create session for user
                resolved_session_id = await get_or_create_user_session(user_id, session_id)
                
                # Get recommended next pillar
                result = await mvp_orchestrator.get_recommended_next_pillar(
                    session_id=resolved_session_id
                )
                return result
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get journey guidance: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/guide-agent/get-journey-guidance")
        async def get_journey_guidance_post(
            request_data: Dict[str, Any],
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Get journey guidance (recommended next pillar) for Guide Agent (POST)."""
            try:
                user_id = request_data.get("user_id", "default_user")
                session_id = request_data.get("session_id")
                current_pillar = request_data.get("current_step")  # Map current_step to current_pillar
                
                # Get or create session for user
                resolved_session_id = await get_or_create_user_session(user_id, session_id)
                
                # Get recommended next pillar
                result = await mvp_orchestrator.get_recommended_next_pillar(
                    session_id=resolved_session_id
                )
                
                # Transform result to match frontend expectations
                if result.get("success"):
                    return {
                        "success": True,
                        "guidance": {
                            "recommended_pillar": result.get("recommended_pillar"),
                            "pillar_info": result.get("pillar_info")
                        },
                        "next_steps": [result.get("pillar_info", {}).get("area_name", "Continue journey")] if result.get("recommended_pillar") else [],
                        "session_id": resolved_session_id,
                        "message": result.get("message", "Journey guidance retrieved")
                    }
                else:
                    return result
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get journey guidance: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/guide-agent/analyze-user-intent")
        async def analyze_user_intent(
            request_data: Dict[str, Any],
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Analyze user intent for Guide Agent using declarative GuideCrossDomainAgent."""
            try:
                user_id = request_data.get("user_id", "default_user")
                message = request_data.get("message", "")
                session_id = request_data.get("session_id")
                
                # Get or create session for user
                resolved_session_id = await get_or_create_user_session(user_id, session_id)
                
                # Use declarative Guide Agent for real LLM-powered intent analysis
                if mvp_orchestrator.guide_agent:
                    agent_response = await mvp_orchestrator.guide_agent.handle_user_request({
                        "message": message,
                        "user_context": {
                            "user_id": user_id,
                            "session_id": resolved_session_id
                        },
                        "session_id": resolved_session_id
                    })
                    
                    return {
                        "success": True,
                        "intent_analysis": {
                            "intent": agent_response.get("intent", "general"),
                            "confidence": 0.9,  # LLM-powered analysis
                            "entities": []
                        },
                        "guidance": agent_response.get("message", ""),
                        "suggested_routes": agent_response.get("suggested_routes", []),
                        "session_id": resolved_session_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Intent analyzed successfully using Guide Agent"
                    }
                else:
                    # Fallback if guide agent not initialized
                    self.logger.warning("⚠️ Guide Agent not available, using fallback intent analysis")
                    return {
                        "success": True,
                        "intent_analysis": {
                            "intent": "journey_navigation",
                            "confidence": 0.5,
                            "entities": []
                        },
                        "session_id": resolved_session_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Intent analyzed (fallback mode)"
                    }
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to analyze user intent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/guide-agent/get-conversation-history/{session_id}")
        async def get_conversation_history(
            session_id: str,
            user_id: str = "default_user",
            session_manager = Depends(get_session_manager)
        ) -> Dict[str, Any]:
            """Get conversation history for Guide Agent."""
            try:
                # Get session from Session Manager
                session_result = await session_manager.get_session(session_id)
                
                if not session_result.get("success"):
                    raise HTTPException(status_code=404, detail="Session not found")
                
                session = session_result.get("session", {})
                
                # Extract conversation history from session
                conversations = session.get("conversations", {})
                guide_agent_conversation = conversations.get("guide_agent", {})
                messages = guide_agent_conversation.get("messages", [])
                
                return {
                    "success": True,
                    "conversation_history": messages,
                    "session_id": session_id,
                    "message": "Conversation history retrieved"
                }
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get conversation history: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/guide-agent/get-mvp-progress")
        async def get_mvp_progress(
            user_id: str = "default_user",
            session_id: Optional[str] = None,
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Get MVP journey progress for Guide Agent."""
            try:
                # Get or create session for user
                resolved_session_id = await get_or_create_user_session(user_id, session_id)
                
                result = await mvp_orchestrator.get_mvp_progress(session_id=resolved_session_id)
                return result
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get MVP progress: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/guide-agent/check-mvp-completion")
        async def check_mvp_completion(
            user_id: str = "default_user",
            session_id: Optional[str] = None,
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Check if MVP journey is complete for Guide Agent."""
            try:
                # Get or create session for user
                resolved_session_id = await get_or_create_user_session(user_id, session_id)
                
                result = await mvp_orchestrator.check_mvp_completion(session_id=resolved_session_id)
                return result
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to check MVP completion: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # JOURNEY ORCHESTRATION ENDPOINTS
        # ============================================================================
        
        @self.router.post("/start-mvp-journey")
        async def start_mvp_journey(
            request_data: Dict[str, Any],
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Start an MVP journey."""
            try:
                user_id = request_data.get("user_id", "default_user")
                initial_pillar = request_data.get("initial_pillar", "content")
                
                result = await mvp_orchestrator.start_mvp_journey(
                    user_id=user_id,
                    initial_pillar=initial_pillar
                )
                
                # If journey started successfully, extract session_id and cache it
                if result.get("success") and "session" in result:
                    session = result.get("session", {})
                    session_id = session.get("session_id")
                    if session_id:
                        self.user_session_cache[user_id] = session_id
                        self.logger.info(f"✅ Cached session {session_id} for user {user_id}")
                
                return result
            except Exception as e:
                self.logger.error(f"Failed to start MVP journey: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/navigate-to-pillar")
        async def navigate_to_pillar(
            request_data: Dict[str, Any],
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Navigate to a specific pillar in the MVP journey."""
            try:
                user_id = request_data.get("user_id", "default_user")
                pillar_id = request_data.get("pillar_id")
                
                result = await mvp_orchestrator.navigate_to_pillar(
                    user_id=user_id,
                    pillar_id=pillar_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to navigate to pillar: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/get-pillar-state/{pillar_id}")
        async def get_pillar_state(
            pillar_id: str,
            user_id: str = "default_user",
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Get the current state of a specific pillar."""
            try:
                result = await mvp_orchestrator.get_pillar_state(
                    user_id=user_id,
                    pillar_id=pillar_id
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get pillar state: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/update-pillar-progress")
        async def update_pillar_progress(
            request_data: Dict[str, Any],
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Update progress for a specific pillar."""
            try:
                user_id = request_data.get("user_id", "default_user")
                pillar_id = request_data.get("pillar_id")
                progress_data = request_data.get("progress_data", {})
                
                result = await mvp_orchestrator.update_pillar_progress(
                    user_id=user_id,
                    pillar_id=pillar_id,
                    progress_data=progress_data
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to update pillar progress: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/end-mvp-journey")
        async def end_mvp_journey(
            request_data: Dict[str, Any],
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """End an MVP journey."""
            try:
                user_id = request_data.get("user_id", "default_user")
                
                result = await mvp_orchestrator.end_mvp_journey(user_id=user_id)
                return result
            except Exception as e:
                self.logger.error(f"Failed to end MVP journey: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # JOURNEY MANAGER ENDPOINTS
        # ============================================================================
        
        @self.router.post("/design-journey")
        async def design_journey(
            request_data: Dict[str, Any],
            journey_manager = Depends(get_journey_manager)
        ) -> Dict[str, Any]:
            """Design a journey based on requirements."""
            try:
                journey_request = request_data.get("journey_request", {})
                
                result = await journey_manager.design_journey(journey_request)
                return result
            except Exception as e:
                self.logger.error(f"Failed to design journey: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/execute-journey")
        async def execute_journey(
            request_data: Dict[str, Any],
            journey_manager = Depends(get_journey_manager)
        ) -> Dict[str, Any]:
            """Execute a designed journey."""
            try:
                journey_id = request_data.get("journey_id")
                user_context = request_data.get("user_context", {})
                
                result = await journey_manager.execute_journey(
                    journey_id=journey_id,
                    user_context=user_context
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to execute journey: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/get-journey-status/{journey_id}")
        async def get_journey_status(
            journey_id: str,
            user_id: str = "default_user",
            journey_manager = Depends(get_journey_manager)
        ) -> Dict[str, Any]:
            """Get the current status of an executing journey."""
            try:
                user_context = {"user_id": user_id}
                result = await journey_manager.get_journey_status(
                    journey_id=journey_id,
                    user_context=user_context
                )
                return result
            except Exception as e:
                self.logger.error(f"Failed to get journey status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # LEGACY ENDPOINT MAPPINGS (for frontend compatibility)
        # ============================================================================
        # These endpoints map to the old guide-agent endpoint names that the frontend uses
        
        @self.router.get("/guide-agent/get-journey-guidance")
        async def get_journey_guidance_legacy(
            user_id: str = "default_user",
            current_pillar: Optional[str] = None,
            mvp_orchestrator = Depends(get_mvp_journey_orchestrator)
        ) -> Dict[str, Any]:
            """Legacy endpoint: Get journey guidance."""
            return await get_journey_guidance(user_id, current_pillar, mvp_orchestrator)
        
        self.logger.info("✅ Journey realm router created")

