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
        # Architecture: PostOfficeService is a Smart City role, lifecycle-managed by City Manager
        # Nothing bypasses Smart City - use City Manager exclusively
        try:
            from backend.api.websocket_gateway_router import router as websocket_gateway_router, set_websocket_gateway_service
            
            # Get City Manager (must be available - it's initialized before API router registration)
            city_manager = platform_orchestrator.managers.get("city_manager")
            if not city_manager:
                logger.error("❌ City Manager not available - cannot register WebSocket Gateway router")
                logger.error("   City Manager must be initialized before API router registration")
                raise RuntimeError("City Manager not available - platform startup failure")
            
            # Get PostOfficeService via City Manager (proper authority)
            # City Manager knows if PostOfficeService is already active or will activate it if needed
            post_office_service = None
            
            # Check if PostOfficeService is already active
            if "post_office" in city_manager.smart_city_services:
                service_info = city_manager.smart_city_services["post_office"]
                if service_info.get("status") == "active" and service_info.get("instance"):
                    post_office_service = service_info["instance"]
                    logger.info("✅ PostOfficeService already active (retrieved from City Manager)")
            
            # If not active, request activation via City Manager
            if not post_office_service:
                logger.info("🔧 Requesting PostOfficeService activation via City Manager...")
                try:
                    # Pass list directly as request parameter (City Manager handles both protocol objects and lists)
                    activation_result = await city_manager.orchestrate_realm_startup(["post_office"])
                    # RealmStartupResponse is a dataclass, access attributes directly
                    if activation_result and activation_result.success:
                        # Get the service instance after activation
                        if "post_office" in city_manager.smart_city_services:
                            service_info = city_manager.smart_city_services["post_office"]
                            post_office_service = service_info.get("instance")
                            if post_office_service:
                                logger.info("✅ PostOfficeService activated and retrieved via City Manager")
                    else:
                        error_msg = activation_result.error if activation_result and hasattr(activation_result, 'error') else "Unknown error"
                        if not activation_result:
                            error_msg = "Activation returned no result"
                        logger.error(f"❌ Failed to activate PostOfficeService: {error_msg}")
                except Exception as e:
                    logger.error(f"❌ Failed to activate PostOfficeService via City Manager: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # Use existing WebSocketGatewayService instance from PostOfficeService
            # PostOfficeService.initialize() already creates and initializes WebSocketGatewayService
            if post_office_service:
                if hasattr(post_office_service, 'websocket_gateway_service') and post_office_service.websocket_gateway_service:
                    websocket_gateway_service = post_office_service.websocket_gateway_service
                    
                    # Set in router (needed for health/test endpoints even if not fully ready)
                    set_websocket_gateway_service(websocket_gateway_service)
                    
                    # Register router
                    # WebSocket endpoint is at /ws (no prefix), health/test endpoints need /api prefix
                    # Keep original router for WebSocket endpoint
                    app.include_router(websocket_gateway_router)
                    
                    # Create separate router for health/test HTTP endpoints with /api prefix
                    # These endpoints should be available even if gateway isn't fully ready
                    from fastapi import APIRouter
                    api_router = APIRouter(prefix="/api")
                    
                    # Import the endpoint functions
                    from backend.api.websocket_gateway_router import (
                        websocket_gateway_health,
                        test_get_connection,
                        test_get_connections_by_channel,
                        test_get_connection_count
                    )
                    
                    # Register endpoints using router decorators
                    @api_router.get("/health/websocket-gateway")
                    async def health_endpoint():
                        return await websocket_gateway_health()
                    
                    @api_router.get("/test/websocket-gateway/connection/{connection_id}")
                    async def test_connection_endpoint(connection_id: str):
                        return await test_get_connection(connection_id)
                    
                    @api_router.get("/test/websocket-gateway/channel/{channel}/connections")
                    async def test_channel_endpoint(channel: str):
                        return await test_get_connections_by_channel(channel)
                    
                    @api_router.get("/test/websocket-gateway/connection-count")
                    async def test_count_endpoint():
                        return await test_get_connection_count()
                    
                    app.include_router(api_router)
                    
                    # Check readiness for logging
                    is_ready = await websocket_gateway_service.is_ready()
                    if is_ready:
                        logger.info("✅ WebSocket Gateway router registered (WebSocket at /ws, health/test at /api) - Gateway ready")
                    else:
                        logger.info("✅ WebSocket Gateway router registered (WebSocket at /ws, health/test at /api) - Gateway not fully ready yet")
                else:
                    logger.warning("⚠️ PostOfficeService does not have WebSocketGatewayService - router not registered")
                    logger.warning("   PostOfficeService may not be fully initialized")
            else:
                logger.error("❌ PostOfficeService not available - WebSocket Gateway router not registered")
                logger.error("   This indicates a Smart City realm startup failure")
                
        except ImportError as e:
            logger.error(f"❌ Failed to import WebSocket Gateway router: {e}")
            import traceback
            logger.error(traceback.format_exc())
                
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
