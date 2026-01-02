"""
API Layer for SymphAIny Platform

This module provides FastAPI routers that connect the frontend to the backend services.
All routes go through the appropriate managers and orchestrators.
"""

from fastapi import FastAPI
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import routers
from .universal_pillar_router import router as universal_pillar_router, set_frontend_gateway
from .auth_router import router as auth_router, set_city_manager
from backend.business_enablement.services.client_collaboration_service.api import router as client_collaboration_router, set_client_collaboration_service


async def register_api_routers(app: FastAPI, platform_orchestrator) -> None:
    """
    Register API routers with FastAPI app.
    
    This function:
    1. Retrieves FrontendGatewayService from Curator Foundation (must already exist in experience realm)
    2. Connects FrontendGatewayService to universal pillar router
    3. Sets City Manager in auth router (for Security Guard discovery)
    4. Registers all routers with FastAPI app
    
    Args:
        app: FastAPI application instance
        platform_orchestrator: PlatformOrchestrator instance
    """
    try:
        logger.info("🔌 Registering API routers...")
        
        # Get Experience Foundation to retrieve FrontendGatewayService via SDK
        # Foundation Services don't register with Curator (since Curator is itself a foundation),
        # so we access strategic services via Foundation SDK methods instead.
        experience_foundation = platform_orchestrator.foundation_services.get("ExperienceFoundationService")
        if not experience_foundation:
            raise RuntimeError("ExperienceFoundationService not found in platform orchestrator")
        
        # Retrieve FrontendGatewayService via Experience Foundation SDK
        # This is the strategic service that routes all API requests
        frontend_gateway = await experience_foundation.get_platform_frontend_gateway()
        if not frontend_gateway:
            raise RuntimeError(
                "FrontendGatewayService not available via Experience Foundation SDK. "
                "It should be created during Experience Foundation initialization."
            )
        
        # Set frontend gateway in universal router
        set_frontend_gateway(frontend_gateway)
        logger.info("✅ FrontendGatewayService connected to universal router")
        
        # Set City Manager in auth router
        # Auth router needs City Manager to discover Security Guard (fallback if Curator unavailable)
        try:
            city_manager = platform_orchestrator.managers.get("city_manager")
            if city_manager:
                set_city_manager(city_manager)
                logger.info("✅ City Manager set in auth router")
            else:
                logger.warning("⚠️ City Manager not available - auth router will use Curator for Security Guard discovery")
        except Exception as e:
            logger.warning(f"⚠️ Failed to set City Manager in auth router: {e}")
            # Don't fail startup - auth router can still discover Security Guard via Curator
        
        # Register auth router (must be before universal router to avoid conflicts)
        app.include_router(auth_router)
        logger.info("✅ Auth router registered with FastAPI app")
        
        # Register universal router with FastAPI app
        app.include_router(universal_pillar_router)
        logger.info("✅ Universal pillar router registered with FastAPI app")
        
        # Register WebSocket Gateway router (NEW - Post Office Gateway)
        try:
            from backend.api.websocket_gateway_router import router as websocket_gateway_router, set_websocket_gateway_service
            from backend.smart_city.services.post_office.websocket_gateway_service import WebSocketGatewayService
            
            # Discover Post Office service via Curator
            curator = platform_orchestrator.foundation_services.get("CuratorFoundationService")
            post_office_service = None
            
            if curator:
                try:
                    post_office_service = await curator.discover_service_by_name("PostOfficeService")
                    if post_office_service:
                        logger.info("✅ Discovered PostOfficeService via Curator")
                except Exception as e:
                    logger.warning(f"⚠️ PostOfficeService not available via Curator: {e}")
            
            # Fallback: Try to get from City Manager
            if not post_office_service:
                try:
                    city_manager = platform_orchestrator.managers.get("city_manager")
                    if city_manager and hasattr(city_manager, 'get_smart_city_service'):
                        post_office_service = await city_manager.get_smart_city_service("PostOfficeService")
                        if post_office_service:
                            logger.info("✅ Retrieved PostOfficeService via City Manager")
                except Exception as e:
                    logger.warning(f"⚠️ PostOfficeService not available via City Manager: {e}")
            
            # Create WebSocket Gateway Service
            if post_office_service:
                websocket_gateway_service = WebSocketGatewayService(
                    di_container=platform_orchestrator.di_container,
                    post_office_service=post_office_service
                )
                
                # Initialize the gateway service
                initialized = await websocket_gateway_service.initialize()
                if initialized:
                    # Set in router
                    set_websocket_gateway_service(websocket_gateway_service)
                    
                    # Register router
                    app.include_router(websocket_gateway_router)
                    logger.info("✅ WebSocket Gateway router registered with FastAPI app")
                else:
                    logger.warning("⚠️ WebSocket Gateway Service not ready - router not registered")
            else:
                logger.warning("⚠️ PostOfficeService not available - WebSocket Gateway router not registered")
                
        except ImportError as e:
            logger.error(f"❌ Failed to import WebSocket Gateway router: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't fail startup - WebSocket is important but not critical for basic functionality
            logger.warning("⚠️ Continuing without WebSocket Gateway router")
        except Exception as e:
            logger.error(f"❌ Failed to register WebSocket Gateway router: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't fail startup - WebSocket is important but not critical for basic functionality
            logger.warning("⚠️ Continuing without WebSocket Gateway router")
        
        # Register Client Collaboration router (NEW - Week 4)
        try:
            # Discover ClientCollaborationService via Curator
            curator = platform_orchestrator.foundation_services.get("CuratorFoundationService")
            if curator:
                client_collaboration_service = await curator.discover_service_by_name("ClientCollaborationService")
                if client_collaboration_service:
                    set_client_collaboration_service(client_collaboration_service)
                    app.include_router(client_collaboration_router)
                    logger.info("✅ Client Collaboration router registered with FastAPI app")
                else:
                    logger.warning("⚠️ ClientCollaborationService not available - router not registered")
            else:
                logger.warning("⚠️ Curator not available - Client Collaboration router not registered")
        except Exception as e:
            logger.warning(f"⚠️ Failed to register Client Collaboration router: {e}")
            # Don't fail startup - client collaboration is optional for MVP
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
        
        logger.info("🎉 API routers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register API routers: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise RuntimeError(f"API router registration failed: {e}") from e
