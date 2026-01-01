#!/usr/bin/env python3
"""
Main API Module

Registers all API routers with the FastAPI application.
This is the central integration point for the new MVP API architecture.
"""

from fastapi import FastAPI
import logging
import asyncio

logger = logging.getLogger(__name__)

# Import all routers
from . import auth_router
from . import session_router
from . import guide_agent_router
from . import liaison_agent_router
from . import mvp_content_router
from . import mvp_insights_router
from . import mvp_operations_router
from . import mvp_business_outcomes_router
from . import universal_pillar_router  # NEW: Universal router for all pillars (replaces old pillar routers!)
from .semantic import (
    # content_pillar_router as semantic_content_router,  # ARCHIVED: Now uses universal_pillar_router
    # insights_pillar_router as semantic_insights_router,  # ARCHIVED: Now uses universal_pillar_router
    # operations_pillar_router as semantic_operations_router,  # ARCHIVED: Now uses universal_pillar_router
    business_outcomes_pillar_router as semantic_business_outcomes_router,
    guide_agent_router as semantic_guide_agent_router,
    liaison_agents_router as semantic_liaison_agents_router,
    session_router as semantic_session_router
)


async def register_api_routers(app: FastAPI, platform_orchestrator):
    """
    Register all API routers with the FastAPI app.
    
    Args:
        app: FastAPI application instance
        platform_orchestrator: Platform orchestrator instance for service access
    """
    logger.info("🔌 Registering MVP API routers...")
    
    # Set platform orchestrator reference in all routers
    auth_router.set_platform_orchestrator(platform_orchestrator)
    session_router.set_platform_orchestrator(platform_orchestrator)
    guide_agent_router.set_platform_orchestrator(platform_orchestrator)
    liaison_agent_router.set_platform_orchestrator(platform_orchestrator)
    mvp_content_router.set_platform_orchestrator(platform_orchestrator)
    # semantic_content_router.set_platform_orchestrator(platform_orchestrator)  # ARCHIVED
    # semantic_insights_router.set_platform_orchestrator(platform_orchestrator)  # ARCHIVED
    # semantic_operations_router.set_platform_orchestrator(platform_orchestrator)  # ARCHIVED
    semantic_business_outcomes_router.set_platform_orchestrator(platform_orchestrator)
    semantic_guide_agent_router.set_platform_orchestrator(platform_orchestrator)
    semantic_liaison_agents_router.set_platform_orchestrator(platform_orchestrator)
    semantic_session_router.set_platform_orchestrator(platform_orchestrator)
    # Note: Content, Insights & Operations now use universal_pillar_router + FrontendGatewayService
    
    # Register routers
    app.include_router(auth_router.router)
    logger.info("  ✅ Auth router registered: /api/auth/*")
    
    app.include_router(session_router.router)
    logger.info("  ✅ Session router registered: /api/global/session")
    
    app.include_router(guide_agent_router.router)
    logger.info("  ✅ Guide Agent router registered: /api/global/agent/*")
    
    app.include_router(guide_agent_router.ws_router)
    logger.info("  ✅ Guide Agent WebSocket registered: /guide-agent")
    
    app.include_router(liaison_agent_router.router)
    logger.info("  ✅ Liaison Agent router registered: /api/liaison/*")
    
    app.include_router(liaison_agent_router.ws_router)
    logger.info("  ✅ Liaison Agent WebSocket registered: /liaison/{pillar}")
    
    app.include_router(mvp_content_router.router)
    logger.info("  ✅ Content pillar router registered: /api/mvp/content/*")
    
    app.include_router(mvp_insights_router.router)
    logger.info("  ✅ Insights pillar router registered: /api/mvp/insights/*")
    
    app.include_router(mvp_operations_router.router)
    logger.info("  ✅ Operations pillar router registered: /api/mvp/operations/*")
    
    app.include_router(mvp_business_outcomes_router.router)
    logger.info("  ✅ Business Outcomes router registered: /api/mvp/business-outcomes/*")
    
    # Register semantic routers
    # app.include_router(semantic_content_router.router)  # ARCHIVED: Now uses universal_pillar_router
    # logger.info("  ✅ Semantic Content Pillar router registered: /api/content-pillar/*")
    
    # app.include_router(semantic_insights_router.router)  # ARCHIVED: Now uses universal_pillar_router
    # logger.info("  ✅ Semantic Insights Pillar router registered: /api/insights-pillar/*")
    
    # app.include_router(semantic_operations_router.router)  # ARCHIVED: Now uses universal_pillar_router
    # logger.info("  ✅ Semantic Operations Pillar router registered: /api/operations-pillar/*")
    
    app.include_router(semantic_business_outcomes_router.router)
    logger.info("  ✅ Semantic Business Outcomes Pillar router registered: /api/business-outcomes-pillar/*")
    
    app.include_router(semantic_guide_agent_router.router)
    logger.info("  ✅ Semantic Guide Agent router registered: /api/guide-agent/*")
    
    app.include_router(semantic_liaison_agents_router.router)
    logger.info("  ✅ Semantic Liaison Agents router registered: /api/liaison-agents/*")
    
    app.include_router(semantic_session_router.router)
    logger.info("  ✅ Semantic Session router registered: /api/session/*")
    
    # Verify Delivery Manager MVP orchestrators are initialized (proper pattern)
    # This ensures MVP orchestrators are ready before Frontend Gateway tries to discover them
    try:
        di_container = platform_orchestrator.infrastructure_services.get('di_container')
        
        if di_container:
            logger.info("  🔧 Verifying Delivery Manager MVP orchestrators...")
            try:
                # Get Delivery Manager from DI container
                delivery_manager = di_container.service_registry.get("DeliveryManagerService")
                
                if delivery_manager and hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                    logger.info("  ✅ Delivery Manager found - checking MVP orchestrators...")
                    
                    # Wait for MVP orchestrators to be initialized
                    logger.info("  ⏳ Waiting for Delivery Manager MVP orchestrators...")
                    max_wait = 10  # Maximum 10 seconds
                    wait_interval = 0.1  # Check every 0.1 seconds
                    waited = 0
                    
                    while waited < max_wait:
                        orchestrator_count = sum(1 for v in delivery_manager.mvp_pillar_orchestrators.values() if v is not None)
                        if orchestrator_count > 0:
                            logger.info(f"  ✅ Delivery Manager has {orchestrator_count} MVP orchestrators initialized")
                            logger.info(f"     Available orchestrators: {list(delivery_manager.mvp_pillar_orchestrators.keys())}")
                            break
                        await asyncio.sleep(wait_interval)
                        waited += wait_interval
                    
                    if waited >= max_wait:
                        logger.warning("  ⚠️  Delivery Manager MVP orchestrators not initialized within timeout")
                        logger.warning("     Frontend Gateway may not be able to discover orchestrators")
                    else:
                        logger.info("  ✅ Delivery Manager MVP orchestrators ready")
                else:
                    logger.warning("  ⚠️ Delivery Manager not available or missing mvp_pillar_orchestrators")
                    logger.warning("     Frontend Gateway will attempt to discover orchestrators on-demand")
                    
            except Exception as e:
                logger.error(f"  ❌ Failed to verify Delivery Manager MVP orchestrators: {e}")
                import traceback
                logger.error(f"     Traceback: {traceback.format_exc()}")
        else:
            logger.warning("  ⚠️ DI Container not available - skipping Delivery Manager verification")
    except Exception as e:
        logger.error(f"  ❌  Delivery Manager verification failed: {e}")
        import traceback
        logger.error(f"     Traceback: {traceback.format_exc()}")
    
    # Register universal pillar router (NEW - handles all 4 pillars)
    # This router provides /api/{pillar}/{path} endpoints for Content, Insights, Operations, Business Outcomes
    try:
        # Get DI container and platform gateway from infrastructure_services
        di_container = platform_orchestrator.infrastructure_services.get('di_container')
        platform_gateway = platform_orchestrator.infrastructure_services.get('platform_gateway')
        
        if di_container and platform_gateway:
            # Check if FrontendGatewayService already exists
            frontend_gateway = di_container.service_registry.get("FrontendGatewayService")
            
            # If not, create and initialize it
            if not frontend_gateway:
                logger.info("  🔧 Initializing FrontendGatewayService...")
                from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
                
                frontend_gateway = FrontendGatewayService(
                    service_name="FrontendGatewayService",
                    realm_name="experience",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                
                # Initialize the service
                await frontend_gateway.initialize()
                
                # Register in DI container's service_registry (direct access)
                di_container.service_registry["FrontendGatewayService"] = frontend_gateway
                logger.info("  ✅ FrontendGatewayService initialized and registered")
            
            if frontend_gateway:
                universal_pillar_router.set_frontend_gateway(frontend_gateway)
                app.include_router(universal_pillar_router.router)
                logger.info("  ✅ Universal Pillar router registered: /api/{pillar}/* (ALL 4 pillars!)")
                logger.info("     • /api/content/*")
                logger.info("     • /api/insights/*")
                logger.info("     • /api/operations/*")
                logger.info("     • /api/business-outcomes/*")
            else:
                logger.warning("  ⚠️  FrontendGatewayService initialization failed")
        else:
            logger.warning("  ⚠️  DI container or platform gateway not available, skipping universal router")
    except Exception as e:
        logger.error(f"  ❌  Could not register universal router: {e}")
        import traceback
        logger.error(f"  Traceback: {traceback.format_exc()}")
    
    logger.info("✅ All MVP API routers registered successfully!")
    
    # Log available endpoints summary
    logger.info("📋 Available API endpoints:")
    logger.info("  Auth:")
    logger.info("    POST /api/auth/register")
    logger.info("    POST /api/auth/login")
    logger.info("    POST /api/auth/logout")
    logger.info("  Session:")
    logger.info("    POST /api/global/session")
    logger.info("    GET  /api/global/session/{session_id}")
    logger.info("  Guide Agent:")
    logger.info("    POST /api/global/agent/analyze")
    logger.info("    WS   /guide-agent (WebSocket)")
    logger.info("  Liaison Agents:")
    logger.info("    POST /api/liaison/chat")
    logger.info("    WS   /liaison/{pillar} (WebSocket)")
    logger.info("  Content Pillar:")
    logger.info("    POST /api/mvp/content/upload")
    logger.info("    GET  /api/mvp/content/files")
    logger.info("    POST /api/mvp/content/parse/{file_id}")
    logger.info("  Insights Pillar:")
    logger.info("    POST /api/mvp/insights/analyze")
    logger.info("  Operations Pillar:")
    logger.info("    POST /api/mvp/operations/sop/create")
    logger.info("    POST /api/mvp/operations/workflow/create")
    logger.info("  Business Outcomes Pillar:")
    logger.info("    POST /api/mvp/business-outcomes/roadmap/create")
    logger.info("    POST /api/mvp/business-outcomes/poc-proposal/create")


def get_api_summary():
    """Return summary of all registered API endpoints."""
    return {
        "auth": {
            "base_path": "/api/auth",
            "endpoints": ["register", "login", "logout", "health"]
        },
        "session": {
            "base_path": "/api/global",
            "endpoints": ["session", "session/{session_id}", "health"]
        },
        "guide_agent": {
            "base_path": "/api/global/agent",
            "endpoints": ["analyze", "health"],
            "websocket": "/guide-agent"
        },
        "liaison_agents": {
            "base_path": "/api/liaison",
            "endpoints": ["chat", "health"],
            "websockets": {
                "content": "/liaison/content",
                "insights": "/liaison/insights",
                "operations": "/liaison/operations",
                "business_outcomes": "/liaison/business_outcomes"
            }
        },
        "content": {
            "base_path": "/api/mvp/content",
            "endpoints": ["upload", "files", "parse/{file_id}", "health"]
        },
        "insights": {
            "base_path": "/api/mvp/insights",
            "endpoints": ["analyze", "health"]
        },
        "operations": {
            "base_path": "/api/mvp/operations",
            "endpoints": ["sop/create", "workflow/create", "health"]
        },
        "business_outcomes": {
            "base_path": "/api/mvp/business-outcomes",
            "endpoints": ["roadmap/create", "poc-proposal/create", "health"]
        }
    }

