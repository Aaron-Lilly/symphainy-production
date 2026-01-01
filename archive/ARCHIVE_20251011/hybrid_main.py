#!/usr/bin/env python3
"""
SymphAIny Platform - Hybrid Main
Uses our infrastructure foundation but with simplified dependency management
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Global state
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hybrid lifespan - tries infrastructure foundation, falls back to minimal."""
    logger.info("🚀 Starting SymphAIny Platform (Hybrid Approach)")
    
    try:
        # Try to use our infrastructure foundation
        logger.info("🔧 Attempting to initialize infrastructure foundation...")
        
        try:
            # Import our infrastructure components
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from experience.fastapi_bridge import ExperienceFastAPIBridge
            
            # Initialize DI Container
            di_container = DIContainerService("platform_hybrid")
            logger.info("✅ DI Container initialized")
            
            # Initialize Public Works Foundation
            public_works_foundation = PublicWorksFoundationService(di_container)
            logger.info("✅ Public Works Foundation initialized")
            
            # Initialize Experience Bridge
            experience_bridge = ExperienceFastAPIBridge(di_container, public_works_foundation)
            await experience_bridge.initialize()
            logger.info("✅ Experience Bridge initialized")
            
            # Store in app state
            app_state["di_container"] = di_container
            app_state["public_works_foundation"] = public_works_foundation
            app_state["experience_bridge"] = experience_bridge
            app_state["infrastructure_mode"] = "full"
            
            # Register routes from experience bridge
            routers = experience_bridge.get_all_routers()
            for router_name, router in routers.items():
                app.include_router(router)
                logger.info(f"✅ Registered {router_name} router")
            
            logger.info("🎉 Full infrastructure foundation loaded successfully!")
            
        except Exception as e:
            logger.warning(f"⚠️ Infrastructure foundation failed: {e}")
            logger.info("🔄 Falling back to minimal mode...")
            
            # Fallback to minimal mode
            app_state["infrastructure_mode"] = "minimal"
            app_state["config"] = {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "debug": os.getenv("DEBUG", "true").lower() == "true"
            }
            
            # Register minimal routes
            register_minimal_routes(app)
            logger.info("✅ Minimal mode initialized")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down platform...")

def register_minimal_routes(app: FastAPI):
    """Register minimal routes for fallback mode."""
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "platform": "SymphAIny",
            "version": "1.0.0",
            "mode": app_state.get("infrastructure_mode", "unknown")
        }
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to SymphAIny Platform",
            "version": "1.0.0",
            "mode": app_state.get("infrastructure_mode", "unknown"),
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/api/test")
    async def test():
        return {
            "message": "API is working",
            "status": "success",
            "mode": app_state.get("infrastructure_mode", "unknown")
        }

# Create FastAPI app
app = FastAPI(
    title="SymphAIny Platform",
    description="AI-Powered Business Enablement Platform",
    version="1.0.0",
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

# Store app state
app.state = app_state

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SymphAIny Platform Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")
    
    args = parser.parse_args()
    
    logger.info(f"🌐 Starting server on {args.host}:{args.port}")
    logger.info(f"🔄 Auto-reload: {args.reload}")
    
    uvicorn.run(
        "hybrid_main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
