#!/usr/bin/env python3
"""
SymphAIny Platform - Updated Startup Orchestration
Aligned with latest architectural patterns:
- ManagerServiceBase with di_container only
- Platform Gateway for realm abstraction access
- Smart City services via SmartCityRoleBase
- Curator-based service discovery
"""

import os
import sys
import logging
import argparse
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment secrets
load_dotenv('.env.secrets')

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Load configuration first
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
config_manager = UnifiedConfigurationManager(service_name="platform_orchestrated", config_root=project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Global state
app_state = {}


class PlatformOrchestrator:
    """
    Platform Orchestrator - Manages the complete startup sequence
    aligned with latest architectural patterns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.startup_sequence = []
        self.managers = {}
        self.foundation_services = {}
        self.infrastructure_services = {}
        self.startup_status = {
            "infrastructure": "pending",
            "foundation": "pending", 
            "platform_gateway": "pending",
            "smart_city": "pending",
            "managers": "pending",
            "realm_services": "pending",
            "health_monitoring": "pending"
        }
    
    async def orchestrate_platform_startup(self) -> Dict[str, Any]:
        """Orchestrate the complete platform startup sequence."""
        self.logger.info("🚀 Starting SymphAIny Platform Orchestration (Updated Architecture)")
        
        try:
            # Phase 1: Foundation Infrastructure
            await self._initialize_foundation_infrastructure()
            
            # Phase 2: Platform Gateway (NEW - Required for realm services)
            await self._initialize_platform_gateway()
            
            # Phase 3: Smart City Services (City Manager)
            await self._initialize_smart_city_services()
            
            # Phase 4: Manager Hierarchy (via City Manager)
            await self._orchestrate_managers()
            
            # Phase 5: Realm Services (Business Enablement, Experience, Journey, Solution)
            await self._initialize_realm_services()
            
            # Phase 6: Health Monitoring
            await self._setup_health_monitoring()
            
            self.logger.info("🎉 Platform orchestration completed successfully!")
            return {
                "success": True,
                "startup_sequence": self.startup_sequence,
                "managers": list(self.managers.keys()),
                "foundation_services": list(self.foundation_services.keys()),
                "infrastructure_services": list(self.infrastructure_services.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Platform orchestration failed: {e}")
            raise
    
    async def _initialize_foundation_infrastructure(self):
        """Initialize foundation infrastructure (DI Container, Public Works, Curator, Communication, Agentic)."""
        self.logger.info("🔧 Phase 1: Initializing Foundation Infrastructure")
        
        try:
            # Import all foundation services
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            
            # Initialize DI Container (Core infrastructure)
            di_container = DIContainerService("platform_orchestrated")
            self.infrastructure_services["di_container"] = di_container
            self.foundation_services["DIContainerService"] = di_container
            self.logger.info("✅ DI Container initialized")
            
            # Initialize Public Works Foundation
            public_works_foundation = PublicWorksFoundationService(di_container)
            await public_works_foundation.initialize()
            self.infrastructure_services["public_works_foundation"] = public_works_foundation
            self.foundation_services["PublicWorksFoundationService"] = public_works_foundation
            self.logger.info("✅ Public Works Foundation initialized")
            
            # Initialize Curator Foundation
            curator_foundation = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=public_works_foundation
            )
            await curator_foundation.initialize()
            self.infrastructure_services["curator_foundation"] = curator_foundation
            self.foundation_services["CuratorFoundationService"] = curator_foundation
            # Register in DI Container
            di_container.foundation_services["CuratorFoundationService"] = curator_foundation
            self.logger.info("✅ Curator Foundation initialized")
            
            # Initialize Communication Foundation
            communication_foundation = CommunicationFoundationService(di_container, public_works_foundation)
            await communication_foundation.initialize()
            self.infrastructure_services["communication_foundation"] = communication_foundation
            self.foundation_services["CommunicationFoundationService"] = communication_foundation
            self.logger.info("✅ Communication Foundation initialized")
            
            # Initialize Agentic Foundation
            agentic_foundation = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                communication_foundation=communication_foundation,
                curator_foundation=curator_foundation
            )
            await agentic_foundation.initialize()
            self.infrastructure_services["agentic_foundation"] = agentic_foundation
            self.foundation_services["AgenticFoundationService"] = agentic_foundation
            self.logger.info("✅ Agentic Foundation initialized")
            
            self.startup_status["foundation"] = "completed"
            self.startup_sequence.append("foundation_infrastructure")
            
        except Exception as e:
            self.logger.error(f"❌ Foundation infrastructure initialization failed: {e}")
            raise
    
    async def _initialize_platform_gateway(self):
        """Initialize Platform Gateway (NEW - Required for realm abstraction access)."""
        self.logger.info("🚪 Phase 2: Initializing Platform Gateway")
        
        try:
            public_works_foundation = self.infrastructure_services["public_works_foundation"]
            di_container = self.infrastructure_services["di_container"]
            
            # Import Platform Gateway
            try:
                from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
            except ImportError:
                from platform.infrastructure.platform_gateway import PlatformInfrastructureGateway
            
            # Create Platform Gateway
            platform_gateway = PlatformInfrastructureGateway(public_works_foundation)
            
            # Store in DI Container (for manager discovery)
            di_container.foundation_services["PlatformInfrastructureGateway"] = platform_gateway
            self.infrastructure_services["platform_gateway"] = platform_gateway
            self.foundation_services["PlatformInfrastructureGateway"] = platform_gateway
            
            self.logger.info("✅ Platform Gateway initialized")
            self.startup_status["platform_gateway"] = "completed"
            self.startup_sequence.append("platform_gateway")
            
        except Exception as e:
            self.logger.error(f"❌ Platform Gateway initialization failed: {e}")
            raise
    
    async def _initialize_smart_city_services(self):
        """Initialize Smart City services (starting with City Manager)."""
        self.logger.info("🏙️ Phase 3: Initializing Smart City Services")
        
        try:
            di_container = self.infrastructure_services["di_container"]
            
            # Initialize City Manager (uses SmartCityRoleBase, only needs di_container)
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            
            city_manager = CityManagerService(di_container=di_container)
            await city_manager.initialize()
            
            self.managers["city_manager"] = city_manager
            self.foundation_services["CityManagerService"] = city_manager
            
            # Register City Manager in DI Container
            di_container.foundation_services["CityManagerService"] = city_manager
            
            self.logger.info("✅ City Manager initialized")
            self.startup_status["smart_city"] = "completed"
            self.startup_sequence.append("smart_city_services")
            
        except Exception as e:
            self.logger.error(f"❌ Smart City services initialization failed: {e}")
            raise
    
    async def _orchestrate_managers(self):
        """Orchestrate managers via City Manager's bootstrap_manager_hierarchy."""
        self.logger.info("👥 Phase 4: Orchestrating Manager Hierarchy (via City Manager)")
        
        try:
            city_manager = self.managers["city_manager"]
            di_container = self.infrastructure_services["di_container"]
            
            # City Manager orchestrates manager hierarchy via bootstrap_manager_hierarchy()
            bootstrap_result = await city_manager.bootstrap_manager_hierarchy()
            
            if not bootstrap_result.get("success"):
                raise Exception(f"Manager hierarchy bootstrap failed: {bootstrap_result.get('error')}")
            
            # Get initialized managers from City Manager's manager_hierarchy
            for manager_name, manager_info in city_manager.manager_hierarchy.items():
                if manager_info.get("status") == "initialized":
                    manager_instance = manager_info.get("instance")
                    if manager_instance:
                        self.managers[manager_name] = manager_instance
                        self.logger.info(f"✅ {manager_name} initialized via City Manager")
            
            # Also register managers directly if they exist in DI Container
            manager_names = [
                "SolutionManagerService",
                "JourneyManagerService", 
                "ExperienceManagerService",
                "DeliveryManagerService"
            ]
            
            for manager_name in manager_names:
                manager = di_container.get_foundation_service(manager_name)
                if manager:
                    key = manager_name.lower().replace("service", "")
                    if key not in self.managers:
                        self.managers[key] = manager
                        self.logger.info(f"✅ {manager_name} registered")
            
            self.startup_status["managers"] = "completed"
            self.startup_sequence.append("manager_orchestration")
            
        except Exception as e:
            self.logger.error(f"❌ Manager orchestration failed: {e}")
            raise
    
    async def _initialize_realm_services(self):
        """Initialize realm services (Business Enablement, Experience, Journey, Solution)."""
        self.logger.info("🌐 Phase 5: Initializing Realm Services")
        
        try:
            di_container = self.infrastructure_services["di_container"]
            platform_gateway = self.infrastructure_services["platform_gateway"]
            
            # 1. Business Enablement - Business Orchestrator
            try:
                from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
                
                business_orchestrator = BusinessOrchestratorService(
                    service_name="BusinessOrchestratorService",
                    realm_name="business_enablement",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                await business_orchestrator.initialize()
                
                self.managers["business_orchestrator"] = business_orchestrator
                self.logger.info("✅ Business Orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Business Orchestrator initialization skipped: {e}")
            
            # 2. Experience Realm Services
            try:
                from backend.experience.services.session_manager_service.session_manager_service import SessionManagerService
                from backend.experience.services.user_experience_service.user_experience_service import UserExperienceService
                from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
                
                # Session Manager
                session_manager = SessionManagerService(
                    service_name="SessionManagerService",
                    realm_name="experience",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                await session_manager.initialize()
                self.logger.info("✅ Session Manager Service initialized")
                
                # User Experience Service
                user_experience = UserExperienceService(
                    service_name="UserExperienceService",
                    realm_name="experience",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                await user_experience.initialize()
                self.logger.info("✅ User Experience Service initialized")
                
                # Frontend Gateway Service
                frontend_gateway = FrontendGatewayService(
                    service_name="FrontendGatewayService",
                    realm_name="experience",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                await frontend_gateway.initialize()
                self.logger.info("✅ Frontend Gateway Service initialized")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Experience realm services initialization skipped: {e}")
            
            # 3. Journey Realm Services
            try:
                from backend.journey.services.mvp_journey_orchestrator_service.mvp_journey_orchestrator_service import MVPJourneyOrchestratorService
                
                mvp_journey_orchestrator = MVPJourneyOrchestratorService(
                    service_name="MVPJourneyOrchestratorService",
                    realm_name="journey",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                await mvp_journey_orchestrator.initialize()
                self.logger.info("✅ MVP Journey Orchestrator initialized")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Journey realm services initialization skipped: {e}")
            
            # 4. Solution Realm Services
            try:
                from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
                
                solution_composer = SolutionComposerService(
                    service_name="SolutionComposerService",
                    realm_name="solution",
                    platform_gateway=platform_gateway,
                    di_container=di_container
                )
                await solution_composer.initialize()
                self.logger.info("✅ Solution Composer Service initialized")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Solution realm services initialization skipped: {e}")
            
            self.startup_status["realm_services"] = "completed"
            self.startup_sequence.append("realm_services")
            
        except Exception as e:
            self.logger.error(f"❌ Realm services initialization failed: {e}")
            raise
    
    async def _setup_health_monitoring(self):
        """Setup platform health monitoring."""
        self.logger.info("🏥 Phase 6: Setting up Health Monitoring")
        
        try:
            # Health monitoring is handled by individual services
            # Platform Gateway tracks access metrics
            # Curator tracks service health
            # Each service has its own health_check() method
            
            self.startup_status["health_monitoring"] = "completed"
            self.startup_sequence.append("health_monitoring")
            self.logger.info("✅ Health monitoring setup complete")
            
        except Exception as e:
            self.logger.error(f"❌ Health monitoring setup failed: {e}")
            raise
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status."""
        return {
            "platform_status": "operational" if all(
                status == "completed" for status in self.startup_status.values()
            ) else "initializing",
            "startup_status": self.startup_status,
            "managers": {name: "healthy" if hasattr(mgr, "is_initialized") and mgr.is_initialized else "unhealthy" 
                        for name, mgr in self.managers.items()},
            "foundation_services": {name: "healthy" for name in self.foundation_services.keys()},
            "infrastructure_services": {name: "healthy" for name in self.infrastructure_services.keys()},
            "startup_sequence": self.startup_sequence,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global orchestrator instance
platform_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Platform lifespan with updated architecture."""
    global platform_orchestrator
    
    logger.info("🚀 Starting SymphAIny Platform (Updated Architecture)")
    
    try:
        # Initialize platform orchestrator
        platform_orchestrator = PlatformOrchestrator()
        
        # Orchestrate complete platform startup
        startup_result = await platform_orchestrator.orchestrate_platform_startup()
        
        # Store in app state
        app_state["platform_orchestrator"] = platform_orchestrator
        app_state["startup_result"] = startup_result
        app_state["infrastructure_mode"] = "updated_architecture"
        
        # Setup FastAPI routes
        await setup_platform_routes(app)
        
        logger.info("🎉 SymphAIny Platform fully orchestrated and operational!")
        
    except Exception as e:
        logger.error(f"❌ Platform startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down platform...")
    if platform_orchestrator:
        # Shutdown in reverse order
        for manager_name in reversed(list(platform_orchestrator.managers.keys())):
            try:
                manager = platform_orchestrator.managers[manager_name]
                if hasattr(manager, 'shutdown'):
                    await manager.shutdown()
                logger.info(f"✅ {manager_name} shutdown complete")
            except Exception as e:
                logger.error(f"❌ {manager_name} shutdown failed: {e}")

async def setup_platform_routes(app: FastAPI):
    """Setup FastAPI routes for the platform."""
    
    @app.get("/health")
    async def health():
        """Platform health endpoint."""
        if platform_orchestrator:
            return await platform_orchestrator.get_platform_status()
        return {"status": "unhealthy", "error": "Platform not initialized"}
    
    @app.get("/platform/status")
    async def platform_status():
        """Detailed platform status."""
        if platform_orchestrator:
            return await platform_orchestrator.get_platform_status()
        return {"error": "Platform not initialized"}
    
    @app.get("/managers")
    async def list_managers():
        """List all active managers."""
        if platform_orchestrator:
            return {
                "managers": list(platform_orchestrator.managers.keys()),
                "status": "operational"
            }
        return {"error": "Platform not initialized"}
    
    @app.get("/foundation/services")
    async def list_foundation_services():
        """List all foundation services."""
        if platform_orchestrator:
            return {
                "foundation_services": list(platform_orchestrator.foundation_services.keys()),
                "infrastructure_services": list(platform_orchestrator.infrastructure_services.keys()),
                "status": "operational"
            }
        return {"error": "Platform not initialized"}

# Create FastAPI app
app = FastAPI(
    title="SymphAIny Platform",
    description="AI-Coexistence Platform with Updated Architecture",
    version="2.1.0",
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

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SymphAIny Platform Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")
    
    args = parser.parse_args()
    
    logger.info(f"🌐 Starting SymphAIny Platform on {args.host}:{args.port}")
    logger.info(f"🔄 Auto-reload: {args.reload}")
    logger.info(f"📊 Log level: {args.log_level}")
    
    uvicorn.run(
        "main_updated:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()



