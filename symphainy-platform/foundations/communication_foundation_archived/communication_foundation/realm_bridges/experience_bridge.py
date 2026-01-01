#!/usr/bin/env python3
"""
Experience Foundation Bridge - Experience Foundation API Integration within Communication Foundation

Provides Experience Foundation API endpoints through the unified Communication Foundation.
Experience Foundation provides SDK builders for realms to create experience components.

WHAT (Foundation Bridge): I provide Experience Foundation API endpoints through Communication Foundation
HOW (Bridge Implementation): I use Experience Foundation SDK to create components and expose APIs

Note: Experience Foundation is accessed directly by realms via SDK (similar to Agentic Foundation).
This bridge provides optional API endpoints for created experience components.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import uuid

logger = logging.getLogger(__name__)


class ExperienceFoundationBridge:
    """
    Experience Foundation Bridge - Experience Foundation API Integration within Communication Foundation
    
    Provides Experience Foundation API endpoints through the unified Communication Foundation.
    Uses Experience Foundation SDK to create and manage experience components.
    
    WHAT (Foundation Bridge): I provide Experience Foundation API endpoints through Communication Foundation
    HOW (Bridge Implementation): I use Experience Foundation SDK to create components and expose APIs
    
    Note: Realms typically access Experience Foundation directly via SDK. This bridge provides
    optional API endpoints for managing experience components.
    """
    
    def __init__(self, di_container, public_works_foundation, curator_foundation):
        """Initialize Experience Foundation Bridge."""
        self.logger = logging.getLogger("ExperienceFoundationBridge")
        
        # Dependencies
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Experience Foundation (will be initialized)
        self.experience_foundation = None
        
        # Created experience components (tracked for API access)
        self.created_gateways: Dict[str, Any] = {}
        self.created_session_managers: Dict[str, Any] = {}
        self.created_user_experiences: Dict[str, Any] = {}
        
        # Router
        self.router = APIRouter(prefix="/api/v1/experience", tags=["experience"])
        
        self.logger.info("🏗️ Experience Foundation Bridge initialized")
    
    async def initialize(self):
        """Initialize Experience Foundation Bridge and create router."""
        try:
            self.logger.info("🚀 Initializing Experience Foundation Bridge...")
            
            # Get Experience Foundation from DI container
            await self._initialize_experience_foundation()
            
            # Create Experience API router
            await self._create_experience_router()
            
            self.logger.info("✅ Experience Foundation Bridge initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Experience Foundation Bridge: {e}", exc_info=True)
            raise
    
    async def get_router(self, user_context: Dict[str, Any] = None) -> APIRouter:
        """Get the Experience Foundation router."""
        try:
            # Note: Realm bridges don't have utility access yet
            # Security/tenant validation would be added when DI Container utilities are available
            return self.router
        except Exception as e:
            self.logger.error(f"❌ Failed to get router: {e}", exc_info=True)
            raise
    
    # PRIVATE METHODS
    
    async def _initialize_experience_foundation(self):
        """Initialize Experience Foundation."""
        self.logger.info("🔧 Initializing Experience Foundation...")
        
        try:
            # Get Experience Foundation from DI container (direct access pattern)
            self.experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")
            
            if not self.experience_foundation:
                # Try alternative access method
                self.experience_foundation = self.di_container.service_registry.get("ExperienceFoundationService")
            
            if not self.experience_foundation:
                self.logger.warning("⚠️ Experience Foundation not available - bridge will have limited functionality")
                return
            
            # Ensure Experience Foundation is initialized
            if not self.experience_foundation.is_initialized:
                await self.experience_foundation.initialize()
            
            self.logger.info("✅ Experience Foundation initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Experience Foundation: {e}")
            raise
    
    async def _create_experience_router(self):
        """Create Experience Foundation FastAPI router with all endpoints."""
        self.logger.info("🔧 Creating Experience Foundation router...")
        
        # Dependency injection functions
        def get_experience_foundation():
            """Get Experience Foundation instance."""
            if not self.experience_foundation:
                raise HTTPException(status_code=503, detail="Experience Foundation not available")
            return self.experience_foundation
        
        # ============================================================================
        # EXPERIENCE FOUNDATION ENDPOINTS
        # ============================================================================
        
        @self.router.get("/foundation/health")
        async def get_experience_foundation_health(
            experience_foundation = Depends(get_experience_foundation)
        ) -> Dict[str, Any]:
            """Get Experience Foundation health status."""
            try:
                health_status = await experience_foundation.health_check()
                return health_status
            except Exception as e:
                self.logger.error(f"Failed to get Experience Foundation health: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/foundation/capabilities")
        async def get_experience_foundation_capabilities(
            experience_foundation = Depends(get_experience_foundation)
        ) -> Dict[str, Any]:
            """Get Experience Foundation capabilities."""
            try:
                capabilities = await experience_foundation.get_service_capabilities()
                return capabilities
            except Exception as e:
                self.logger.error(f"Failed to get Experience Foundation capabilities: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # EXPERIENCE COMPONENT CREATION ENDPOINTS (SDK Access)
        # ============================================================================
        
        @self.router.post("/gateway/create")
        async def create_frontend_gateway(
            request_data: Dict[str, Any] = Body(...),
            experience_foundation = Depends(get_experience_foundation)
        ) -> Dict[str, Any]:
            """Create a frontend gateway using Experience Foundation SDK."""
            try:
                realm_name = request_data.get("realm_name", "default")
                config = request_data.get("config", {})
                
                gateway = await experience_foundation.create_frontend_gateway(
                    realm_name=realm_name,
                    config=config
                )
                
                # Track created gateway
                gateway_key = f"{realm_name}_gateway"
                self.created_gateways[gateway_key] = gateway
                
                return {
                    "success": True,
                    "gateway_key": gateway_key,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to create frontend gateway: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/session/create")
        async def create_session_manager(
            request_data: Dict[str, Any] = Body(...),
            experience_foundation = Depends(get_experience_foundation)
        ) -> Dict[str, Any]:
            """Create a session manager using Experience Foundation SDK."""
            try:
                realm_name = request_data.get("realm_name", "default")
                config = request_data.get("config", {})
                
                session_manager = await experience_foundation.create_session_manager(
                    realm_name=realm_name,
                    config=config
                )
                
                # Track created session manager
                manager_key = f"{realm_name}_session_manager"
                self.created_session_managers[manager_key] = session_manager
                
                return {
                    "success": True,
                    "session_manager_key": manager_key,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to create session manager: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/user-experience/create")
        async def create_user_experience(
            request_data: Dict[str, Any] = Body(...),
            experience_foundation = Depends(get_experience_foundation)
        ) -> Dict[str, Any]:
            """Create a user experience service using Experience Foundation SDK."""
            try:
                realm_name = request_data.get("realm_name", "default")
                config = request_data.get("config", {})
                
                user_experience = await experience_foundation.create_user_experience(
                    realm_name=realm_name,
                    config=config
                )
                
                # Track created user experience
                ux_key = f"{realm_name}_user_experience"
                self.created_user_experiences[ux_key] = user_experience
                
                return {
                    "success": True,
                    "user_experience_key": ux_key,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to create user experience: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        self.logger.info("✅ Experience Foundation router created with all endpoints")
    
    async def shutdown(self):
        """Shutdown Experience Foundation Bridge."""
        try:
            self.logger.info("🛑 Shutting down Experience Foundation Bridge...")
            
            # Note: Experience Foundation manages lifecycle of created components
            # Individual components should be shut down by their creating realms
            
            self.logger.info("✅ Experience Foundation Bridge shutdown completed")
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Experience Foundation Bridge: {e}", exc_info=True)
            raise






