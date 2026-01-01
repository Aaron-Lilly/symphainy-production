#!/usr/bin/env python3
"""
SymphAIny Platform - Full Manager Orchestration
Complete startup orchestration with all realm managers and proper dependency management
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
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager, Environment
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
    with proper manager orchestration and dependency management.
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
            "managers": "pending",
            "services": "pending",
            "communication": "pending",
            "health_monitoring": "pending"
        }
    
    async def orchestrate_platform_startup(self) -> Dict[str, Any]:
        """Orchestrate the complete platform startup sequence."""
        self.logger.info("🚀 Starting SymphAIny Platform Orchestration")
        
        try:
            # Phase 1: Foundation Infrastructure (DI Container → Public Works → Curator → Communication → Agentic)
            await self._initialize_foundation_infrastructure()
            
            # Phase 2: Manager Orchestration (Smart City → Solution → Others)
            await self._orchestrate_managers()
            
            # Phase 4: Service Registration
            await self._register_realm_services()
            
            # Phase 5: Cross-realm Communication
            await self._setup_cross_realm_communication()
            
            # Phase 6: Health Monitoring
            await self._setup_health_monitoring()
            
            self.logger.info("🎉 Platform orchestration completed successfully!")
            return {
                "success": True,
                "startup_sequence": self.startup_sequence,
                "managers": list(self.managers.keys()),
                "foundation_services": list(self.foundation_services.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Platform orchestration failed: {e}")
            raise
    
    async def _initialize_foundation_infrastructure(self):
        """Initialize foundation infrastructure (DI Container, Public Works, Communication, Curator, Agentic)."""
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
            self.logger.info("✅ DI Container initialized")
            
            # Initialize Public Works Foundation
            public_works_foundation = PublicWorksFoundationService(di_container)
            await public_works_foundation.initialize()
            self.infrastructure_services["public_works_foundation"] = public_works_foundation
            self.logger.info("✅ Public Works Foundation initialized")
            
            # Initialize Curator Foundation
            curator_foundation = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=public_works_foundation
            )
            await curator_foundation.initialize()
            self.infrastructure_services["curator_foundation"] = curator_foundation
            self.logger.info("✅ Curator Foundation initialized")
            
            # Initialize Communication Foundation
            communication_foundation = CommunicationFoundationService(di_container, public_works_foundation)
            await communication_foundation.initialize()
            self.infrastructure_services["communication_foundation"] = communication_foundation
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
            self.logger.info("✅ Agentic Foundation initialized")
            
            self.startup_status["foundation_infrastructure"] = "completed"
            self.startup_sequence.append("foundation_infrastructure")
            
        except Exception as e:
            self.logger.error(f"❌ Foundation infrastructure initialization failed: {e}")
            raise
    
    
    async def _orchestrate_managers(self):
        """Orchestrate managers in solution-centric flow (Smart City → Solution → Others)."""
        self.logger.info("👥 Phase 2: Orchestrating Managers (Solution-Centric Flow)")
        
        try:
            # Get infrastructure services
            di_container = self.infrastructure_services["di_container"]
            public_works_foundation = self.infrastructure_services["public_works_foundation"]
            communication_foundation = self.infrastructure_services["communication_foundation"]
            curator_foundation = self.infrastructure_services["curator_foundation"]
            agentic_foundation = self.infrastructure_services["agentic_foundation"]
            
            # Solution-centric manager startup order
            # Smart City (City Manager) → calls Solution Manager to start solution-centric process
            manager_startup_order = [
                ("city_manager", "City Manager (Platform governance - starts solution-centric process)"),
                ("solution_manager", "Solution Manager (Strategic orchestration - called by City Manager)"),
                ("journey_manager", "Journey Manager (Journey orchestration - called by Solution Manager)"),
                ("experience_manager", "Experience Manager (Frontend gateway - called by Journey Manager)"),
                ("delivery_manager", "Delivery Manager (Business Enablement - called by Experience Manager)")
            ]
            
            for manager_name, description in manager_startup_order:
                await self._initialize_manager(manager_name, description, {
                    "di_container": di_container,
                    "public_works_foundation": public_works_foundation,
                    "communication_foundation": communication_foundation,
                    "curator_foundation": curator_foundation,
                    "agentic_foundation": agentic_foundation
                })
            
            self.startup_status["managers"] = "completed"
            self.startup_sequence.append("manager_orchestration")
            
        except Exception as e:
            self.logger.error(f"❌ Manager orchestration failed: {e}")
            raise
    
    async def _initialize_manager(self, manager_name: str, description: str, dependencies: Dict[str, Any]):
        """Initialize a specific manager with its dependencies."""
        try:
            self.logger.info(f"🎯 Initializing {description}")
            
            if manager_name == "solution_manager":
                from solution.services.solution_manager.solution_manager_service import SolutionManagerService
                manager = SolutionManagerService(
                    public_works_foundation=dependencies["public_works_foundation"],
                    di_container=dependencies["di_container"],
                    curator_foundation=dependencies["curator_foundation"]
                )
                
            elif manager_name == "journey_manager":
                from journey_solution.services.journey_manager.journey_manager_service import JourneyManagerService
                manager = JourneyManagerService(
                    public_works_foundation=dependencies["public_works_foundation"],
                    communication_foundation=dependencies["communication_foundation"]
                )
                
            elif manager_name == "experience_manager":
                from experience.roles.experience_manager.experience_manager_service import ExperienceManagerService
                manager = ExperienceManagerService(
                    public_works_foundation=dependencies["public_works_foundation"]
                )
                
            elif manager_name == "delivery_manager":
                from backend.business_enablement.services.delivery_manager.delivery_manager_service import DeliveryManagerService
                manager = DeliveryManagerService(
                    public_works_foundation=dependencies["public_works_foundation"],
                    communication_foundation=dependencies["communication_foundation"]
                )
                
            elif manager_name == "city_manager":
                from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
                manager = CityManagerService(
                    public_works_foundation=dependencies["public_works_foundation"],
                    di_container=dependencies["di_container"],
                    curator_foundation=dependencies["curator_foundation"]
                )
                
            else:
                raise ValueError(f"Unknown manager: {manager_name}")
            
            # Initialize the manager
            await manager.initialize()
            self.managers[manager_name] = manager
            
            # Register with DI container
            dependencies["di_container"].register_service(f"{manager_name}_service", manager)
            
            self.logger.info(f"✅ {description} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {description}: {e}")
            raise
    
    async def _register_realm_services(self):
        """Register all realm services with their managers."""
        self.logger.info("🔧 Phase 4: Registering Realm Services")
        
        try:
            # Each manager will register its realm services
            for manager_name, manager in self.managers.items():
                if hasattr(manager, 'register_realm_services'):
                    await manager.register_realm_services()
                    self.logger.info(f"✅ {manager_name} realm services registered")
            
            self.startup_status["services"] = "completed"
            self.startup_sequence.append("service_registration")
            
        except Exception as e:
            self.logger.error(f"❌ Service registration failed: {e}")
            raise
    
    async def _setup_cross_realm_communication(self):
        """Setup cross-realm communication and coordination."""
        self.logger.info("🌐 Phase 5: Setting up Cross-realm Communication")
        
        try:
            communication_foundation = self.infrastructure_services["communication_foundation"]
            
            # Setup manager coordination
            for manager_name, manager in self.managers.items():
                if hasattr(manager, 'setup_cross_realm_communication'):
                    await manager.setup_cross_realm_communication(communication_foundation)
                    self.logger.info(f"✅ {manager_name} cross-realm communication setup")
            
            self.startup_status["communication"] = "completed"
            self.startup_sequence.append("cross_realm_communication")
            
        except Exception as e:
            self.logger.error(f"❌ Cross-realm communication setup failed: {e}")
            raise
    
    async def _setup_health_monitoring(self):
        """Setup platform health monitoring."""
        self.logger.info("🏥 Phase 6: Setting up Health Monitoring")
        
        try:
            # Setup health monitoring for all managers
            for manager_name, manager in self.managers.items():
                if hasattr(manager, 'setup_health_monitoring'):
                    await manager.setup_health_monitoring()
                    self.logger.info(f"✅ {manager_name} health monitoring setup")
            
            self.startup_status["health_monitoring"] = "completed"
            self.startup_sequence.append("health_monitoring")
            
        except Exception as e:
            self.logger.error(f"❌ Health monitoring setup failed: {e}")
            raise
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status."""
        return {
            "platform_status": "operational" if all(status == "completed" for status in self.startup_status.values()) else "initializing",
            "startup_status": self.startup_status,
            "managers": {name: "healthy" for name in self.managers.keys()},
            "foundation_services": {name: "healthy" for name in self.foundation_services.keys()},
            "infrastructure_services": {name: "healthy" for name in self.infrastructure_services.keys()},
            "startup_sequence": self.startup_sequence,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global orchestrator instance
platform_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Platform lifespan with full manager orchestration."""
    global platform_orchestrator
    
    logger.info("🚀 Starting SymphAIny Platform (Full Manager Orchestration)")
    
    try:
        # Initialize platform orchestrator
        platform_orchestrator = PlatformOrchestrator()
        
        # Orchestrate complete platform startup
        startup_result = await platform_orchestrator.orchestrate_platform_startup()
        
        # Store in app state
        app_state["platform_orchestrator"] = platform_orchestrator
        app_state["startup_result"] = startup_result
        app_state["infrastructure_mode"] = "full_orchestration"
        
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
        # Shutdown managers in reverse order
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
    description="AI-Coexistence Platform with Full Manager Orchestration",
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
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()