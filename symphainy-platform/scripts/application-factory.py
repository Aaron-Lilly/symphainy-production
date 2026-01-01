#!/usr/bin/env python3
"""
Application Factory - Layer 3
Pure application creation with FastAPI and Experience Layer
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any

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

class ApplicationFactory:
    """Application Factory - Layer 3"""
    
    def __init__(self, platform_services: Dict[str, Any]):
        self.platform_services = platform_services
        self.app = None
        self.experience_bridge = None
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application with platform services."""
        logger.info("🚀 Application Factory - Layer 3")
        logger.info("==================================")
        logger.info("Creating FastAPI application with platform services")
        logger.info("")
        
        try:
            # Step 1: Create FastAPI app
            logger.info("📱 Step 1: Creating FastAPI application...")
            self.app = FastAPI(
                title="SymphAIny Platform",
                description="AI-Powered Business Enablement Platform",
                version="1.0.0"
            )
            
            # Add CORS middleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # Store platform services in app state
            self.app.state.platform_services = self.platform_services
            logger.info("✅ FastAPI application created")
            
            # Step 2: Initialize Experience Layer
            logger.info("🌐 Step 2: Initializing Experience Layer...")
            from experience.fastapi_bridge import ExperienceFastAPIBridge
            
            self.experience_bridge = ExperienceFastAPIBridge(
                self.platform_services["di_container"],
                self.platform_services["public_works_foundation"]
            )
            
            # Initialize Experience Bridge
            asyncio.run(self.experience_bridge.initialize())
            logger.info("✅ Experience Layer initialized")
            
            # Step 3: Register routes
            logger.info("🔗 Step 3: Registering API routes...")
            self._register_routes()
            logger.info("✅ API routes registered")
            
            # Step 4: Application health check
            logger.info("🏥 Step 4: Application health check...")
            self._health_check()
            
            logger.info("")
            logger.info("🎉 Application Layer - Ready!")
            logger.info("=============================")
            logger.info("FastAPI application is created and ready")
            logger.info("")
            logger.info("📊 Application Status:")
            logger.info("  - FastAPI: ✅ Operational")
            logger.info("  - Experience Layer: ✅ Operational")
            logger.info("  - API Routes: ✅ Registered")
            logger.info("")
            logger.info("✅ Application Layer Complete - Ready for User Access")
            
            return self.app
            
        except Exception as e:
            logger.error(f"❌ Application factory failed: {e}")
            raise
    
    def _register_routes(self):
        """Register API routes from Experience Layer."""
        try:
            # Get routers from Experience Bridge
            routers = self.experience_bridge.get_all_routers()
            
            for router_name, router in routers.items():
                self.app.include_router(router)
                logger.info(f"✅ Registered {router_name} router")
            
            # Add health check route
            @self.app.get("/health")
            async def health():
                return {
                    "status": "healthy",
                    "platform": "SymphAIny",
                    "version": "1.0.0",
                    "layers": {
                        "infrastructure": "operational",
                        "platform": "operational",
                        "application": "operational"
                    }
                }
            
            # Add root route
            @self.app.get("/")
            async def root():
                return {
                    "message": "Welcome to SymphAIny Platform",
                    "version": "1.0.0",
                    "docs": "/docs",
                    "health": "/health"
                }
            
        except Exception as e:
            logger.error(f"❌ Route registration failed: {e}")
            raise
    
    def _health_check(self):
        """Perform application health check."""
        try:
            # Check FastAPI app
            if not self.app:
                raise Exception("FastAPI app not created")
            
            # Check Experience Bridge
            if not self.experience_bridge:
                raise Exception("Experience Bridge not initialized")
            
            logger.info("✅ Application health check passed")
            
        except Exception as e:
            logger.error(f"❌ Application health check failed: {e}")
            raise

def main():
    """Main function for application factory."""
    # This would typically receive platform services from platform bootstrap
    # For now, we'll create a minimal version
    
    logger.info("🚀 Application Factory - Layer 3")
    logger.info("==================================")
    logger.info("Creating FastAPI application")
    logger.info("")
    
    # Create minimal platform services for testing
    platform_services = {
        "di_container": None,  # Would be provided by platform bootstrap
        "public_works_foundation": None,  # Would be provided by platform bootstrap
        "infrastructure_foundation": None  # Would be provided by platform bootstrap
    }
    
    # Create application factory
    factory = ApplicationFactory(platform_services)
    
    # Create FastAPI app
    app = factory.create_app()
    
    # Start server
    logger.info("🌐 Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()




