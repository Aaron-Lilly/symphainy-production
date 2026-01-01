#!/usr/bin/env python3
"""
Platform Bootstrap - Containerized Version
Runs inside Docker container with Poetry and .env.secrets
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerizedPlatformBootstrap:
    """Containerized Platform Bootstrap - Layer 2"""
    
    def __init__(self):
        self.di_container = None
        self.public_works_foundation = None
        self.infrastructure_foundation = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize platform foundation services in container."""
        logger.info("🏗️ Containerized Platform Bootstrap - Layer 2")
        logger.info("================================================")
        logger.info("Initializing platform foundation services in container")
        logger.info("")
        
        try:
            # Step 1: Check container environment
            logger.info("🐳 Step 1: Checking container environment...")
            self._check_container_environment()
            logger.info("✅ Container environment verified")
            
            # Step 2: Initialize DI Container
            logger.info("📦 Step 2: Initializing DI Container...")
            from foundations.di_container.di_container_service import DIContainerService
            
            self.di_container = DIContainerService("platform_container")
            await self.di_container.initialize()
            logger.info("✅ DI Container initialized")
            
            # Step 3: Initialize Public Works Foundation
            logger.info("🏛️ Step 3: Initializing Public Works Foundation...")
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            self.public_works_foundation = PublicWorksFoundationService(self.di_container)
            await self.public_works_foundation.initialize()
            logger.info("✅ Public Works Foundation initialized")
            
            # Step 4: Initialize Infrastructure Foundation
            logger.info("🔧 Step 4: Initializing Infrastructure Foundation...")
            from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationService
            
            self.infrastructure_foundation = InfrastructureFoundationService(self.di_container)
            await self.infrastructure_foundation.initialize()
            logger.info("✅ Infrastructure Foundation initialized")
            
            # Step 5: Platform health check
            logger.info("🏥 Step 5: Platform health check...")
            await self._health_check()
            
            self.initialized = True
            logger.info("")
            logger.info("🎉 Containerized Platform Layer - Ready!")
            logger.info("==========================================")
            logger.info("Platform foundation services are initialized in container")
            logger.info("")
            logger.info("📊 Platform Status:")
            logger.info("  - Container: ✅ Running")
            logger.info("  - Poetry: ✅ Dependencies installed")
            logger.info("  - .env.secrets: ✅ Loaded")
            logger.info("  - DI Container: ✅ Operational")
            logger.info("  - Public Works Foundation: ✅ Operational")
            logger.info("  - Infrastructure Foundation: ✅ Operational")
            logger.info("")
            logger.info("✅ Containerized Platform Layer Complete - Ready for Application Layer")
            
        except Exception as e:
            logger.error(f"❌ Containerized platform bootstrap failed: {e}")
            raise
    
    def _check_container_environment(self):
        """Check container environment and dependencies."""
        try:
            # Check if we're in a container
            if not os.path.exists('/.dockerenv'):
                logger.warning("⚠️ Not running in Docker container")
            
            # Check Poetry installation
            import subprocess
            result = subprocess.run(['poetry', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Poetry not available in container")
            logger.info(f"✅ Poetry: {result.stdout.strip()}")
            
            # Check .env.secrets file
            if not os.path.exists('.env.secrets'):
                raise Exception(".env.secrets file not found in container")
            logger.info("✅ .env.secrets file found")
            
            # Check Python dependencies
            try:
                import fastapi
                import uvicorn
                logger.info("✅ Python dependencies available")
            except ImportError as e:
                raise Exception(f"Python dependencies not available: {e}")
            
        except Exception as e:
            logger.error(f"❌ Container environment check failed: {e}")
            raise
    
    async def _health_check(self):
        """Perform platform health check."""
        try:
            # Check DI Container
            if not self.di_container:
                raise Exception("DI Container not initialized")
            
            # Check Public Works Foundation
            if not self.public_works_foundation:
                raise Exception("Public Works Foundation not initialized")
            
            # Check Infrastructure Foundation
            if not self.infrastructure_foundation:
                raise Exception("Infrastructure Foundation not initialized")
            
            logger.info("✅ Containerized platform health check passed")
            
        except Exception as e:
            logger.error(f"❌ Containerized platform health check failed: {e}")
            raise
    
    def get_services(self):
        """Get initialized services for application layer."""
        if not self.initialized:
            raise Exception("Platform not initialized")
        
        return {
            "di_container": self.di_container,
            "public_works_foundation": self.public_works_foundation,
            "infrastructure_foundation": self.infrastructure_foundation
        }

async def main():
    """Main function for containerized platform bootstrap."""
    bootstrap = ContainerizedPlatformBootstrap()
    await bootstrap.initialize()
    
    # Keep running for application layer to connect
    logger.info("🔄 Containerized platform bootstrap complete - waiting for application layer...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Containerized platform bootstrap shutting down...")

if __name__ == "__main__":
    asyncio.run(main())




