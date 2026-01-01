#!/usr/bin/env python3
"""
SymphAIny Platform - Modern Application Factory Pattern
Following modern DDD/SOA best practices for clean, maintainable startup
"""

import os
import sys
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state (minimal)
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management - minimal, focused, reliable."""
    logger.info("🚀 Starting SymphAIny Platform (Modern Pattern)")
    
    try:
        # 1. Initialize only essential services
        logger.info("📦 Initializing essential services...")
        
        # Database connection (if needed)
        # app_state["db"] = await get_database()
        
        # Redis connection (if needed)  
        # app_state["redis"] = await get_redis()
        
        # Configuration (minimal)
        app_state["config"] = {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "true").lower() == "true"
        }
        
        logger.info("✅ Essential services initialized")
        
        # 2. Register routes (modern pattern)
        logger.info("🔗 Registering API routes...")
        register_routes(app)
        logger.info("✅ API routes registered")
        
        logger.info("🎉 Platform startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Cleanup (minimal)
    logger.info("🛑 Shutting down platform...")
    # Add cleanup if needed

def create_app() -> FastAPI:
    """Modern application factory pattern."""
    
    # Create FastAPI app with minimal configuration
    app = FastAPI(
        title="SymphAIny Platform",
        description="AI-Powered Business Enablement Platform",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store app state
    app.state = app_state
    
    return app

def register_routes(app: FastAPI):
    """Register API routes - modern pattern."""
    
    # Health check
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "platform": "SymphAIny",
            "version": "1.0.0",
            "environment": app.state.get("config", {}).get("environment", "unknown")
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to SymphAIny Platform",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    # API routes (minimal for now)
    @app.get("/api/test")
    async def test():
        return {"message": "API is working", "status": "success"}
    
    # TODO: Add pillar routes here when ready
    # register_content_routes(app)
    # register_insights_routes(app)
    # register_operations_routes(app)
    # register_business_outcomes_routes(app)

def main():
    """Main entry point - modern pattern."""
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info(f"🔄 Auto-reload: {reload}")
    
    uvicorn.run(
        "modern_main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
