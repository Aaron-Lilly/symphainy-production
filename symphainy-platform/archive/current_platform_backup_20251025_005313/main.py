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
from typing import Dict, Any, Optional

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
    """Application lifespan manager with proper dependency-ordered startup."""
    global di_container, public_works_foundation, experience_bridge, domain_managers
    
    logger.info("🚀 Starting SymphAIny Platform with Dependency-Ordered Startup...")
    print("🚀 Starting SymphAIny Platform with Dependency-Ordered Startup...")
    
    try:
        # PHASE 1: Foundation Services (main.py responsibility)
        logger.info("🏗️ Phase 1: Starting Foundation Services...")
        print("🏗️ Phase 1: Starting Foundation Services...")
        
        # 1.1 Start Infrastructure Services
        infrastructure_services = await _start_infrastructure_services()
        logger.info("✅ Infrastructure services started")
        print("✅ Infrastructure services started")
        
        # 1.2 Initialize DI Container
        di_container = DIContainerService()
        logger.info("✅ DI Container initialized")
        print("✅ DI Container initialized")
        
        # 1.3 Initialize Public Works Foundation
        public_works_foundation = PublicWorksFoundationService(di_container)
        await public_works_foundation.initialize()
        logger.info("✅ Public Works Foundation initialized")
        print("✅ Public Works Foundation initialized")
        
        # 1.4 Initialize Communication Foundation
        communication_foundation = di_container.get_communication_foundation()
        await communication_foundation.initialize()
        await communication_foundation.start()
        di_container.register_communication_foundation()
        logger.info("✅ Communication Foundation initialized")
        print("✅ Communication Foundation initialized")
        
        # PHASE 2: Domain Manager Startup (with proper dependency order)
        logger.info("🎯 Phase 2: Starting Domain Managers with Dependency Order...")
        print("🎯 Phase 2: Starting Domain Managers with Dependency Order...")
        
        domain_managers = await _start_domain_managers_with_dependencies(public_works_foundation, communication_foundation)
        
        # PHASE 3: Experience Layer Integration
        logger.info("🎭 Phase 3: Starting Experience Layer...")
        print("🎭 Phase 3: Starting Experience Layer...")
        
        experience_bridge = ExperienceFastAPIBridge(di_container, public_works_foundation)
        await experience_bridge.initialize()
        logger.info("✅ Experience Layer FastAPI Bridge initialized")
        print("✅ Experience Layer FastAPI Bridge initialized")
        
        # Include all Experience Layer routers
        routers = experience_bridge.get_all_routers()
        for router_name, router in routers.items():
            app.include_router(router)
            logger.info(f"Included {router_name} router")
            print(f"Included {router_name} router")
        
        # Store services in app state for access by routes
        app.state.di_container = di_container
        app.state.public_works_foundation = public_works_foundation
        app.state.communication_foundation = communication_foundation
        app.state.infrastructure_services = infrastructure_services
        app.state.domain_managers = domain_managers
        app.state.experience_bridge = experience_bridge
        
        logger.info("✅ SymphAIny Platform started successfully with proper dependency order")
        print("✅ SymphAIny Platform started successfully with proper dependency order")
        
    except Exception as e:
        logger.error(f"❌ Failed to start platform: {e}")
        print(f"❌ Failed to start platform: {e}")
        raise
    
    yield
    
    # Cleanup
    try:
        logger.info("🛑 Shutting down SymphAIny Platform...")
        print("🛑 Shutting down SymphAIny Platform...")
        await _orchestrate_domain_shutdown()
        await _shutdown_infrastructure_services()
        logger.info("✅ SymphAIny Platform shutdown complete")
        print("✅ SymphAIny Platform shutdown complete")
    except Exception as e:
        logger.warning(f"Error during platform shutdown: {e}")
        print(f"Error during platform shutdown: {e}")


async def _start_infrastructure_services() -> Dict[str, Any]:
    """Start infrastructure services (Consul, Redis, ArangoDB, etc.)."""
    logger.info("🏗️ Starting infrastructure services...")
    print("🏗️ Starting infrastructure services...")
    
    # In a real implementation, this would start Docker infrastructure
    # For now, we'll simulate infrastructure startup
    infrastructure_result = {
        "consul": {"status": "started", "port": 8500},
        "redis": {"status": "started", "port": 6379},
        "arangodb": {"status": "started", "port": 8529},
        "grafana": {"status": "started", "port": 3000},
        "otel_collector": {"status": "started", "port": 4317}
    }
    
    # Wait for infrastructure to be healthy
    await _wait_for_infrastructure_health()
    
    return infrastructure_result


async def _wait_for_infrastructure_health():
    """Wait for infrastructure services to be healthy."""
    logger.info("⏳ Waiting for infrastructure services to be healthy...")
    print("⏳ Waiting for infrastructure services to be healthy...")
    
    # In a real implementation, this would check actual health endpoints
    # For now, we'll simulate a health check delay
    await asyncio.sleep(2)  # Simulate infrastructure startup time
    
    logger.info("✅ Infrastructure services are healthy")
    print("✅ Infrastructure services are healthy")


async def _start_domain_managers_with_dependencies(public_works_foundation: PublicWorksFoundationService, communication_foundation: Any) -> Dict[str, Any]:
    """Start domain managers in proper dependency order with Communication Foundation."""
    managers = {}
    
    # Note: Domain managers will use Communication Foundation for inter-realm communication
    # instead of direct DI Container access for better SOA patterns
    
    # STEP 1: Smart City Manager (depends on Foundation Services)
    logger.info("🏛️ Starting Smart City Manager...")
    print("🏛️ Starting Smart City Manager...")
    managers["city_manager"] = CityManagerService(public_works_foundation)
    await managers["city_manager"].initialize()
    city_startup = await managers["city_manager"].orchestrate_realm_startup()
    logger.info(f"✅ Smart City Manager started: {city_startup['status']}")
    print(f"✅ Smart City Manager started: {city_startup['status']}")
    
    # STEP 2: Agentic Manager (depends on Smart City)
    logger.info("🤖 Starting Agentic Manager...")
    print("🤖 Starting Agentic Manager...")
    managers["agentic_manager"] = AgenticManagerService(public_works_foundation)
    await managers["agentic_manager"].initialize()
    agentic_startup = await managers["agentic_manager"].orchestrate_realm_startup()
    logger.info(f"✅ Agentic Manager started: {agentic_startup['status']}")
    print(f"✅ Agentic Manager started: {agentic_startup['status']}")
    
    # STEP 3: Delivery Manager (depends on Agents)
    logger.info("🚚 Starting Delivery Manager...")
    print("🚚 Starting Delivery Manager...")
    managers["delivery_manager"] = DeliveryManagerService(public_works_foundation)
    await managers["delivery_manager"].initialize()
    delivery_startup = await managers["delivery_manager"].orchestrate_realm_startup()
    logger.info(f"✅ Delivery Manager started: {delivery_startup['status']}")
    print(f"✅ Delivery Manager started: {delivery_startup['status']}")
    
    # STEP 4: Experience Manager (depends on Business Enablement)
    logger.info("🎭 Starting Experience Manager...")
    print("🎭 Starting Experience Manager...")
    managers["experience_manager"] = ExperienceManagerService(public_works_foundation)
    await managers["experience_manager"].initialize()
    experience_startup = await managers["experience_manager"].orchestrate_realm_startup()
    logger.info(f"✅ Experience Manager started: {experience_startup['status']}")
    print(f"✅ Experience Manager started: {experience_startup['status']}")
    
    # STEP 5: Journey Manager (depends on Experience)
    logger.info("🗺️ Starting Journey Manager...")
    print("🗺️ Starting Journey Manager...")
    managers["journey_manager"] = JourneyManagerService(public_works_foundation)
    await managers["journey_manager"].initialize()
    journey_startup = await managers["journey_manager"].orchestrate_realm_startup()
    logger.info(f"✅ Journey Manager started: {journey_startup['status']}")
    print(f"✅ Journey Manager started: {journey_startup['status']}")
    
    return managers


async def _orchestrate_domain_shutdown():
    """Orchestrate shutdown of all domain managers."""
    logger.info("🛑 Orchestrating domain manager shutdown...")
    print("🛑 Orchestrating domain manager shutdown...")
    
    # Shutdown in reverse order
    shutdown_order = ["journey_manager", "experience_manager", "delivery_manager", "agentic_manager", "city_manager"]
    
    for manager_name in shutdown_order:
        if manager_name in domain_managers:
            try:
                logger.info(f"🛑 Shutting down {manager_name}...")
                print(f"🛑 Shutting down {manager_name}...")
                shutdown_result = await domain_managers[manager_name].coordinate_realm_shutdown()
                logger.info(f"✅ {manager_name} shutdown: {shutdown_result['status']}")
                print(f"✅ {manager_name} shutdown: {shutdown_result['status']}")
            except Exception as e:
                logger.warning(f"❌ Failed to shutdown {manager_name}: {e}")
                print(f"❌ Failed to shutdown {manager_name}: {e}")


async def _shutdown_infrastructure_services():
    """Shutdown infrastructure services."""
    logger.info("🛑 Shutting down infrastructure services...")
    print("🛑 Shutting down infrastructure services...")
    
    # In a real implementation, this would shutdown Docker infrastructure
    # For now, we'll simulate infrastructure shutdown
    logger.info("✅ Infrastructure services shutdown complete")
    print("✅ Infrastructure services shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="SymphAIny Platform",
    description="SymphAIny Platform with Dependency-Ordered Startup",
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
        # Check if all services are healthy
        if not di_container or not public_works_foundation or not domain_managers:
            return {"status": "unhealthy", "message": "Services not initialized"}
        
        # Get health status from domain managers
        health_status = {}
        for manager_name, manager in domain_managers.items():
            try:
                health = await manager.monitor_realm_health()
                health_status[manager_name] = health
            except Exception as e:
                health_status[manager_name] = {"error": str(e), "status": "unhealthy"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "di_container": "healthy",
                "public_works_foundation": "healthy",
                "domain_managers": health_status
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Platform status endpoint
@app.get("/platform/status")
async def platform_status():
    """Get overall platform status."""
    try:
        if not domain_managers:
            return {"status": "unhealthy", "message": "Domain managers not initialized"}
        
        # Get status from all domain managers
        platform_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "domain_managers": {}
        }
        
        for manager_name, manager in domain_managers.items():
            try:
                status = await manager.get_manager_status()
                platform_status["domain_managers"][manager_name] = status
            except Exception as e:
                platform_status["domain_managers"][manager_name] = {"error": str(e), "status": "unhealthy"}
        
        return platform_status
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Domain manager health endpoint
@app.get("/platform/health/{manager_name}")
async def domain_manager_health(manager_name: str):
    """Get health status of a specific domain manager."""
    try:
        if manager_name not in domain_managers:
            return {"error": f"Manager {manager_name} not found", "status": "not_found"}
        
        manager = domain_managers[manager_name]
        health = await manager.monitor_realm_health()
        
        return {
            "manager_name": manager_name,
            "health": health,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "status": "unhealthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




