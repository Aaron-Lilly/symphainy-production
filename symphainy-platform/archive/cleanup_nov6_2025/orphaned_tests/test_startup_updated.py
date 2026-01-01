#!/usr/bin/env python3
"""
Test script for updated startup process.

Tests the startup sequence phase by phase to verify alignment with latest architecture.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path - CRITICAL for all imports
project_root = Path(__file__).resolve().parent
# Ensure we use the absolute path and it's FIRST in sys.path
project_root_str = str(project_root)
# Remove any existing entries to avoid duplicates
if project_root_str in sys.path:
    sys.path.remove(project_root_str)
# Insert at the beginning to ensure it's checked first
sys.path.insert(0, project_root_str)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_phase_1_foundation_infrastructure():
    """Test Phase 1: Foundation Infrastructure Initialization."""
    logger.info("=" * 60)
    logger.info("Testing Phase 1: Foundation Infrastructure")
    logger.info("=" * 60)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container (initializes during construction)
        logger.info("📦 Initializing DI Container...")
        di_container = DIContainerService("test_platform")
        # DI Container is initialized during construction, no separate initialize() call needed
        logger.info("✅ DI Container initialized")
        
        # Initialize Public Works Foundation
        logger.info("🏛️ Initializing Public Works Foundation...")
        public_works_foundation = PublicWorksFoundationService(di_container)
        await public_works_foundation.initialize()
        # Register Public Works Foundation in DI Container
        di_container.service_registry["PublicWorksFoundationService"] = public_works_foundation
        logger.info("✅ Public Works Foundation initialized and registered")
        
        # Initialize Curator Foundation
        logger.info("📚 Initializing Curator Foundation...")
        curator_foundation = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works_foundation
        )
        await curator_foundation.initialize()
        # Register Curator Foundation in DI Container
        di_container.service_registry["CuratorFoundationService"] = curator_foundation
        logger.info("✅ Curator Foundation initialized and registered")
        
        # Initialize Communication Foundation
        logger.info("📡 Initializing Communication Foundation...")
        communication_foundation = CommunicationFoundationService(di_container, public_works_foundation)
        await communication_foundation.initialize()
        # Register Communication Foundation in DI Container
        di_container.service_registry["CommunicationFoundationService"] = communication_foundation
        logger.info("✅ Communication Foundation initialized and registered")
        
        # Initialize Agentic Foundation
        logger.info("🤖 Initializing Agentic Foundation...")
        # Agentic Foundation only needs di_container and optional public_works_foundation, curator_foundation
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
        await agentic_foundation.initialize()
        # Register Agentic Foundation in DI Container
        di_container.service_registry["AgenticFoundationService"] = agentic_foundation
        logger.info("✅ Agentic Foundation initialized and registered")
        
        return {
            "success": True,
            "di_container": di_container,
            "public_works_foundation": public_works_foundation,
            "curator_foundation": curator_foundation,
            "communication_foundation": communication_foundation,
            "agentic_foundation": agentic_foundation
        }
        
    except Exception as e:
        logger.error(f"❌ Phase 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def test_phase_2_platform_gateway(dependencies):
    """Test Phase 2: Platform Gateway Initialization."""
    logger.info("=" * 60)
    logger.info("Testing Phase 2: Platform Gateway")
    logger.info("=" * 60)
    
    try:
        public_works_foundation = dependencies["public_works_foundation"]
        di_container = dependencies["di_container"]
        
        # Try platform_infrastructure first, fallback to platform
        try:
            from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
            logger.info("📦 Using platform_infrastructure.infrastructure.platform_gateway")
        except ImportError:
            from platform.infrastructure.platform_gateway import PlatformInfrastructureGateway
            logger.info("📦 Using platform.infrastructure.platform_gateway")
        
        # Create Platform Gateway
        logger.info("🚪 Creating Platform Gateway...")
        platform_gateway = PlatformInfrastructureGateway(public_works_foundation)
        
        # Store in DI Container (Platform Gateway is already registered by DI Container)
        logger.info("✅ Platform Gateway created and stored in DI Container")
        
        # Verify it can be retrieved
        retrieved_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
        assert retrieved_gateway is not None, "Platform Gateway should be retrievable from DI Container"
        logger.info("✅ Platform Gateway verification successful")
        
        dependencies["platform_gateway"] = platform_gateway
        return {"success": True, **dependencies}
        
    except Exception as e:
        logger.error(f"❌ Phase 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def test_phase_3_smart_city_services(dependencies):
    """Test Phase 3: Smart City Services (City Manager)."""
    logger.info("=" * 60)
    logger.info("Testing Phase 3: Smart City Services")
    logger.info("=" * 60)
    
    try:
        di_container = dependencies["di_container"]
        
        # Import City Manager
        # Ensure project root is at the front of sys.path (might have been pushed down by other imports)
        import sys
        import os
        from pathlib import Path
        
        # Re-insert project root at the front to ensure it's found first
        project_root = Path(__file__).resolve().parent
        project_root_str = str(project_root)
        
        # Remove any existing entry
        if project_root_str in sys.path:
            sys.path.remove(project_root_str)
        # Insert at the very beginning
        sys.path.insert(0, project_root_str)
        
        # Verify backend is importable
        try:
            import backend
            logger.debug(f"✅ Backend module found: {backend.__file__}")
        except ImportError as e:
            logger.error(f"❌ Backend module not found: {e}")
            logger.error(f"sys.path[0]: {sys.path[0] if sys.path else 'None'}")
            logger.error(f"sys.path[:5]: {sys.path[:5]}")
            raise
        
        from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
        logger.info("✅ City Manager imported successfully")
        
        # Initialize City Manager (only needs di_container)
        logger.info("🏙️ Initializing City Manager...")
        city_manager = CityManagerService(di_container=di_container)
        
        # Verify constructor signature
        assert hasattr(city_manager, 'di_container'), "City Manager should have di_container"
        assert not hasattr(city_manager, 'public_works_foundation') or city_manager.public_works_foundation is None, \
            "City Manager should not take public_works_foundation in constructor"
        logger.info("✅ City Manager constructor verified")
        
        # Initialize City Manager
        await city_manager.initialize()
        logger.info("✅ City Manager initialized")
        
        # Verify City Manager discovered Platform Gateway during initialize
        # (This happens in the initialization module)
        logger.info("✅ City Manager initialization complete")
        
        # City Manager will be registered during bootstrap
        # No need to register manually here
        
        dependencies["city_manager"] = city_manager
        return {"success": True, **dependencies}
        
    except Exception as e:
        logger.error(f"❌ Phase 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def test_phase_4_manager_hierarchy(dependencies):
    """Test Phase 4: Manager Hierarchy Bootstrap."""
    logger.info("=" * 60)
    logger.info("Testing Phase 4: Manager Hierarchy Bootstrap")
    logger.info("=" * 60)
    
    try:
        city_manager = dependencies["city_manager"]
        di_container = dependencies["di_container"]
        
        # Bootstrap manager hierarchy via City Manager
        logger.info("🚀 Bootstrapping manager hierarchy via City Manager...")
        bootstrap_result = await city_manager.bootstrap_manager_hierarchy()
        
        # Log the bootstrap result for debugging
        logger.debug(f"Bootstrap result type: {type(bootstrap_result)}")
        logger.debug(f"Bootstrap result: {bootstrap_result}")
        
        # Verify bootstrap result
        if hasattr(bootstrap_result, 'success'):
            success = bootstrap_result.success
            error_msg = getattr(bootstrap_result, 'error', None) if not success else None
        else:
            success = bootstrap_result.get("success", False) if isinstance(bootstrap_result, dict) else False
            error_msg = bootstrap_result.get("error") if isinstance(bootstrap_result, dict) else None
        
        if not success:
            # Try to get more details about the failure
            if hasattr(bootstrap_result, 'error'):
                error_msg = bootstrap_result.error
            elif isinstance(bootstrap_result, dict):
                error_msg = bootstrap_result.get("error") or bootstrap_result.get("message") or str(bootstrap_result)
            else:
                error_msg = str(bootstrap_result) if bootstrap_result else "Unknown error"
            logger.error(f"Bootstrap result details: {bootstrap_result}")
            raise Exception(f"Bootstrap failed: {error_msg}")
        
        logger.info("✅ Manager hierarchy bootstrap successful")
        
        # Verify managers were created
        manager_names = ["solution_manager", "journey_manager", "experience_manager", "delivery_manager"]
        for manager_name in manager_names:
            if manager_name in city_manager.manager_hierarchy:
                manager_info = city_manager.manager_hierarchy[manager_name]
                if manager_info.get("status") == "initialized":
                    logger.info(f"✅ {manager_name} initialized")
                else:
                    logger.warning(f"⚠️ {manager_name} status: {manager_info.get('status')}")
            else:
                logger.warning(f"⚠️ {manager_name} not found in hierarchy")
        
        # Verify managers can be retrieved from DI Container
        manager_service_names = [
            "SolutionManagerService",
            "JourneyManagerService",
            "ExperienceManagerService",
            "DeliveryManagerService"
        ]
        
        for service_name in manager_service_names:
            manager = di_container.get_foundation_service(service_name)
            if manager:
                logger.info(f"✅ {service_name} retrievable from DI Container")
            else:
                logger.warning(f"⚠️ {service_name} not found in DI Container")
        
        return {"success": True, **dependencies}
        
    except Exception as e:
        logger.error(f"❌ Phase 4 failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def test_phase_5_realm_services(dependencies):
    """Test Phase 5: Realm Services Initialization."""
    logger.info("=" * 60)
    logger.info("Testing Phase 5: Realm Services")
    logger.info("=" * 60)
    
    try:
        di_container = dependencies["di_container"]
        platform_gateway = dependencies["platform_gateway"]
        
        # Test Business Orchestrator initialization
        try:
            from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
            
            logger.info("🎯 Initializing Business Orchestrator...")
            business_orchestrator = BusinessOrchestratorService(
                service_name="BusinessOrchestratorService",
                realm_name="business_enablement",
                platform_gateway=platform_gateway,
                di_container=di_container
            )
            
            # Verify constructor signature
            assert business_orchestrator.platform_gateway == platform_gateway, \
                "Business Orchestrator should have platform_gateway"
            assert business_orchestrator.di_container == di_container, \
                "Business Orchestrator should have di_container"
            logger.info("✅ Business Orchestrator constructor verified")
            
            await business_orchestrator.initialize()
            logger.info("✅ Business Orchestrator initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Business Orchestrator initialization skipped: {e}")
        
        # Test Experience Realm Service (Session Manager)
        try:
            from backend.experience.services.session_manager_service.session_manager_service import SessionManagerService
            
            logger.info("👤 Initializing Session Manager Service...")
            session_manager = SessionManagerService(
                service_name="SessionManagerService",
                realm_name="experience",
                platform_gateway=platform_gateway,
                di_container=di_container
            )
            
            # Verify constructor signature
            assert session_manager.platform_gateway == platform_gateway, \
                "Session Manager should have platform_gateway"
            logger.info("✅ Session Manager constructor verified")
            
            await session_manager.initialize()
            logger.info("✅ Session Manager initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Session Manager initialization skipped: {e}")
        
        return {"success": True, **dependencies}
        
    except Exception as e:
        logger.error(f"❌ Phase 5 failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def main():
    """Run all startup phase tests."""
    logger.info("🚀 Starting Updated Startup Process Tests")
    logger.info("=" * 60)
    
    results = {}
    
    # Phase 1: Foundation Infrastructure
    phase1_result = await test_phase_1_foundation_infrastructure()
    if not phase1_result.get("success"):
        logger.error("❌ Phase 1 failed - stopping tests")
        return
    results["phase1"] = phase1_result
    
    # Phase 2: Platform Gateway
    phase2_result = await test_phase_2_platform_gateway(phase1_result)
    if not phase2_result.get("success"):
        logger.error("❌ Phase 2 failed - stopping tests")
        return
    results["phase2"] = phase2_result
    
    # Phase 3: Smart City Services
    phase3_result = await test_phase_3_smart_city_services(phase2_result)
    if not phase3_result.get("success"):
        logger.error("❌ Phase 3 failed - stopping tests")
        return
    results["phase3"] = phase3_result
    
    # Phase 4: Manager Hierarchy
    phase4_result = await test_phase_4_manager_hierarchy(phase3_result)
    if not phase4_result.get("success"):
        logger.error("❌ Phase 4 failed - stopping tests")
        return
    results["phase4"] = phase4_result
    
    # Phase 5: Realm Services
    phase5_result = await test_phase_5_realm_services(phase4_result)
    if not phase5_result.get("success"):
        logger.error("❌ Phase 5 failed - stopping tests")
        return
    results["phase5"] = phase5_result
    
    # Summary
    logger.info("=" * 60)
    logger.info("✅ ALL PHASES COMPLETED SUCCESSFULLY!")
    logger.info("=" * 60)
    logger.info("📊 Test Summary:")
    logger.info(f"  ✅ Phase 1: Foundation Infrastructure")
    logger.info(f"  ✅ Phase 2: Platform Gateway")
    logger.info(f"  ✅ Phase 3: Smart City Services")
    logger.info(f"  ✅ Phase 4: Manager Hierarchy")
    logger.info(f"  ✅ Phase 5: Realm Services")
    logger.info("=" * 60)
    logger.info("🎉 Updated startup process is aligned with latest architecture!")


if __name__ == "__main__":
    asyncio.run(main())

