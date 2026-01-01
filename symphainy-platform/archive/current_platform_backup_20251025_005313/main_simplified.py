"""
SymphAIny Platform - Simplified Main Application
Following best practices for startup orchestration
"""

import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime

# Add the platform directory to Python path for consistent imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instances
di_container: Optional[Any] = None
public_works_foundation: Optional[Any] = None
experience_bridge: Optional[Any] = None
domain_managers: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with proper dependency-ordered startup."""
    global di_container, public_works_foundation, experience_bridge, domain_managers
    
    logger.info("🚀 Starting SymphAIny Platform...")
    
    try:
        # PHASE 1: Foundation Services
        logger.info("🏗️ Phase 1: Starting Foundation Services...")
        
        # Initialize DI Container
        di_container = await _initialize_di_container()
        logger.info("✅ DI Container initialized")
        
        # Initialize Public Works Foundation
        public_works_foundation = await _initialize_public_works_foundation(di_container)
        logger.info("✅ Public Works Foundation initialized")
        
        # PHASE 2: Experience Layer
        logger.info("🎭 Phase 2: Starting Experience Layer...")
        
        experience_bridge = await _initialize_experience_bridge(di_container, public_works_foundation)
        logger.info("✅ Experience Layer initialized")
        
        # Include routers
        routers = experience_bridge.get_all_routers() if experience_bridge else {}
        for router_name, router in routers.items():
            app.include_router(router)
            logger.info(f"Included {router_name} router")
        
        # Store services in app state
        app.state.di_container = di_container
        app.state.public_works_foundation = public_works_foundation
        app.state.experience_bridge = experience_bridge
        app.state.domain_managers = domain_managers
        
        logger.info("✅ SymphAIny Platform started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start platform: {e}")
        raise
    
    yield
    
    # Cleanup
    try:
        logger.info("🛑 Shutting down SymphAIny Platform...")
        if experience_bridge:
            await experience_bridge.shutdown()
        if public_works_foundation:
            await public_works_foundation.shutdown()
        if di_container:
            await di_container.shutdown()
        logger.info("✅ SymphAIny Platform shutdown complete")
    except Exception as e:
        logger.warning(f"Error during platform shutdown: {e}")


async def _initialize_di_container():
    """Initialize DI Container with error handling."""
    try:
        from foundations.di_container.di_container_service import DIContainerService
        container = DIContainerService()
        await container.initialize()
        return container
    except Exception as e:
        logger.error(f"Failed to initialize DI Container: {e}")
        return None


async def _initialize_public_works_foundation(di_container):
    """Initialize Public Works Foundation with error handling."""
    try:
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        foundation = PublicWorksFoundationService(di_container)
        await foundation.initialize()
        return foundation
    except Exception as e:
        logger.error(f"Failed to initialize Public Works Foundation: {e}")
        return None


async def _initialize_experience_bridge(di_container, public_works_foundation):
    """Initialize Experience Bridge with error handling."""
    try:
        from experience.fastapi_bridge import ExperienceFastAPIBridge
        bridge = ExperienceFastAPIBridge(di_container, public_works_foundation)
        await bridge.initialize()
        return bridge
    except Exception as e:
        logger.error(f"Failed to initialize Experience Bridge: {e}")
        return None


# Create FastAPI application
app = FastAPI(
    title="SymphAIny Platform",
    description="SymphAIny Platform with Simplified Startup",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if not di_container or not public_works_foundation:
            return {"status": "unhealthy", "message": "Services not initialized"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "di_container": "healthy" if di_container else "unhealthy",
                "public_works_foundation": "healthy" if public_works_foundation else "unhealthy",
                "experience_bridge": "healthy" if experience_bridge else "unhealthy"
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SymphAIny Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
