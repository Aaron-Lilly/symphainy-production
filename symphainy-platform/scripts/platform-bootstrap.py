#!/usr/bin/env python3
"""
Platform Bootstrap - Layer 2
Pure platform initialization with DI Container and Public Works Foundation
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

class PlatformBootstrap:
    """Platform Bootstrap - Layer 2"""
    
    def __init__(self):
        self.di_container = None
        self.public_works_foundation = None
        self.infrastructure_foundation = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize platform foundation services."""
        logger.info("🏗️ Platform Bootstrap - Layer 2")
        logger.info("======================================")
        logger.info("Initializing platform foundation services")
        logger.info("")
        
        try:
            # Step 1: Initialize DI Container
            logger.info("📦 Step 1: Initializing DI Container...")
            from foundations.di_container.di_container_service import DIContainerService
            
            self.di_container = DIContainerService("platform_bootstrap")
            await self.di_container.initialize()
            logger.info("✅ DI Container initialized")
            
            # Step 2: Initialize Public Works Foundation
            logger.info("🏛️ Step 2: Initializing Public Works Foundation...")
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            
            self.public_works_foundation = PublicWorksFoundationService(self.di_container)
            await self.public_works_foundation.initialize()
            logger.info("✅ Public Works Foundation initialized")
            
            # Step 3: Initialize Infrastructure Foundation
            logger.info("🔧 Step 3: Initializing Infrastructure Foundation...")
            from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationService
            
            self.infrastructure_foundation = InfrastructureFoundationService(self.di_container)
            await self.infrastructure_foundation.initialize()
            logger.info("✅ Infrastructure Foundation initialized")
            
            # Step 4: Platform health check
            logger.info("🏥 Step 4: Platform health check...")
            await self._health_check()
            
            self.initialized = True
            logger.info("")
            logger.info("🎉 Platform Layer - Ready!")
            logger.info("==========================")
            logger.info("Platform foundation services are initialized and healthy")
            logger.info("")
            logger.info("📊 Platform Status:")
            logger.info("  - DI Container: ✅ Operational")
            logger.info("  - Public Works Foundation: ✅ Operational")
            logger.info("  - Infrastructure Foundation: ✅ Operational")
            logger.info("")
            logger.info("✅ Platform Layer Complete - Ready for Application Layer")
            
        except Exception as e:
            logger.error(f"❌ Platform bootstrap failed: {e}")
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
            
            logger.info("✅ Platform health check passed")
            
        except Exception as e:
            logger.error(f"❌ Platform health check failed: {e}")
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
    """Main function for platform bootstrap."""
    bootstrap = PlatformBootstrap()
    await bootstrap.initialize()
    
    # Keep running for application layer to connect
    logger.info("🔄 Platform bootstrap complete - waiting for application layer...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Platform bootstrap shutting down...")

if __name__ == "__main__":
    asyncio.run(main())




