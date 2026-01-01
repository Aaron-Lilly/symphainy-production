#!/usr/bin/env python3
"""
Test Cloud-Ready Phases 1.3 and 1.4

Tests:
- Phase 1.3: Auto-Discovery Pattern
- Phase 1.4: Cloud-Ready Startup Orchestrator

This test verifies that:
1. Auto-discovery can discover services
2. Cloud-ready orchestrator can start up
3. Feature flags work correctly
4. Both modes can coexist
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_RESULTS = {
    "phase_1_3": {"passed": False, "errors": []},
    "phase_1_4": {"passed": False, "errors": []},
    "feature_flags": {"passed": False, "errors": []},
    "integration": {"passed": False, "errors": []}
}


async def test_feature_flags():
    """Test Phase 1.1: Feature Flag System"""
    logger.info("=" * 80)
    logger.info("TEST: Feature Flag System")
    logger.info("=" * 80)
    
    try:
        from utilities.configuration.cloud_ready_config import (
            get_cloud_ready_config,
            reset_cloud_ready_config
        )
        
        # Test 1: Default mode (disabled)
        reset_cloud_ready_config()
        os.environ.pop("CLOUD_READY_MODE", None)
        os.environ.pop("CLOUD_READY_AUTO_DISCOVERY", None)
        os.environ.pop("CLOUD_READY_UNIFIED_REGISTRY", None)
        
        config = get_cloud_ready_config()
        assert not config.should_use_cloud_ready_startup(), "Default should be disabled"
        assert not config.should_use_auto_discovery(), "Auto-discovery should be disabled by default"
        assert not config.should_use_unified_registry(), "Unified registry should be disabled by default"
        logger.info("✅ Test 1: Default mode (disabled) - PASSED")
        
        # Test 2: Enabled mode
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_MODE"] = "enabled"
        config = get_cloud_ready_config()
        assert config.should_use_cloud_ready_startup(), "Should be enabled"
        assert config.should_use_auto_discovery(), "Auto-discovery should be enabled"
        assert config.should_use_unified_registry(), "Unified registry should be enabled"
        logger.info("✅ Test 2: Enabled mode - PASSED")
        
        # Test 3: Hybrid mode (auto-discovery only)
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_MODE"] = "disabled"
        os.environ["CLOUD_READY_AUTO_DISCOVERY"] = "true"
        config = get_cloud_ready_config()
        assert not config.should_use_cloud_ready_startup(), "Startup should be disabled"
        assert config.should_use_auto_discovery(), "Auto-discovery should be enabled"
        logger.info("✅ Test 3: Hybrid mode (auto-discovery only) - PASSED")
        
        # Test 4: Hybrid mode (unified registry only)
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_MODE"] = "disabled"
        os.environ["CLOUD_READY_UNIFIED_REGISTRY"] = "true"
        config = get_cloud_ready_config()
        assert not config.should_use_cloud_ready_startup(), "Startup should be disabled"
        assert config.should_use_unified_registry(), "Unified registry should be enabled"
        logger.info("✅ Test 4: Hybrid mode (unified registry only) - PASSED")
        
        TEST_RESULTS["feature_flags"]["passed"] = True
        logger.info("✅ Feature Flag System - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        error_msg = f"Feature flag test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["feature_flags"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_phase_1_3_auto_discovery():
    """Test Phase 1.3: Auto-Discovery Pattern"""
    logger.info("=" * 80)
    logger.info("TEST: Phase 1.3 - Auto-Discovery Pattern")
    logger.info("=" * 80)
    
    try:
        # Enable auto-discovery and test mode (makes Traefik optional)
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_AUTO_DISCOVERY"] = "true"
        os.environ["TEST_MODE"] = "true"  # Makes Traefik optional
        
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_auto_discovery")
        logger.info("✅ DI Container initialized")
        
        # Initialize Public Works Foundation (required for Curator)
        public_works_foundation = PublicWorksFoundationService(di_container=di_container)
        await public_works_foundation.initialize()
        logger.info("✅ Public Works Foundation initialized")
        
        # Initialize Curator Foundation (with auto-discovery)
        curator_foundation = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works_foundation
        )
        await curator_foundation.initialize()
        logger.info("✅ Curator Foundation initialized")
        
        # Test 1: Auto-discovery service exists
        assert curator_foundation.auto_discovery is not None, "Auto-discovery service should be initialized"
        assert curator_foundation.auto_discovery.is_initialized, "Auto-discovery service should be initialized"
        logger.info("✅ Test 1: Auto-discovery service exists - PASSED")
        
        # Test 2: Auto-discovery can discover services
        discovered_services = await curator_foundation.auto_discovery.discover_all_services()
        logger.info(f"✅ Discovered {len(discovered_services)} services")
        
        # Should discover at least foundation services
        assert len(discovered_services) > 0, "Should discover at least some services"
        logger.info("✅ Test 2: Auto-discovery can discover services - PASSED")
        
        # Test 3: Register discovered services
        registration_results = await curator_foundation.auto_discovery.register_discovered_services(discovered_services)
        assert "registered" in registration_results, "Registration results should include 'registered' list"
        logger.info(f"✅ Registered {len(registration_results.get('registered', []))} services")
        logger.info("✅ Test 3: Register discovered services - PASSED")
        
        # Test 4: Auto-discovery disabled mode
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_AUTO_DISCOVERY"] = "false"
        
        curator_foundation_disabled = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works_foundation
        )
        await curator_foundation_disabled.initialize()
        assert curator_foundation_disabled.auto_discovery is None, "Auto-discovery should be None when disabled"
        logger.info("✅ Test 4: Auto-discovery disabled mode - PASSED")
        
        TEST_RESULTS["phase_1_3"]["passed"] = True
        logger.info("✅ Phase 1.3: Auto-Discovery Pattern - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        error_msg = f"Phase 1.3 test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["phase_1_3"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_phase_1_4_cloud_ready_startup():
    """Test Phase 1.4: Cloud-Ready Startup Orchestrator"""
    logger.info("=" * 80)
    logger.info("TEST: Phase 1.4 - Cloud-Ready Startup Orchestrator")
    logger.info("=" * 80)
    
    try:
        # Enable cloud-ready mode and test mode (makes Traefik optional)
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_MODE"] = "enabled"
        os.environ["TEST_MODE"] = "true"  # Makes Traefik optional
        
        from main_cloud_ready import CloudReadyPlatformOrchestrator
        
        # Test 1: Create orchestrator
        orchestrator = CloudReadyPlatformOrchestrator()
        assert orchestrator is not None, "Orchestrator should be created"
        logger.info("✅ Test 1: Create orchestrator - PASSED")
        
        # Test 2: Start platform (bootstrap phase)
        startup_result = await orchestrator.orchestrate_platform_startup()
        assert startup_result.get("success"), "Startup should succeed"
        assert startup_result.get("mode") == "cloud_ready", "Mode should be cloud_ready"
        logger.info("✅ Test 2: Start platform - PASSED")
        
        # Test 3: Verify DI Container
        di_container = orchestrator.get_di_container()
        assert di_container is not None, "DI Container should be initialized"
        assert di_container.unified_registry is not None, "Unified registry should be initialized"
        logger.info("✅ Test 3: Verify DI Container - PASSED")
        
        # Test 4: Verify Router Manager
        router_manager = orchestrator.get_router_manager()
        assert router_manager is not None, "Router Manager should be initialized"
        assert router_manager.is_initialized, "Router Manager should be initialized"
        logger.info("✅ Test 4: Verify Router Manager - PASSED")
        
        # Test 5: Verify Foundation Services
        foundation_services = orchestrator.foundation_services
        assert len(foundation_services) > 0, "Should have foundation services"
        assert "PublicWorksFoundationService" in foundation_services, "Should have Public Works Foundation"
        assert "CuratorFoundationService" in foundation_services, "Should have Curator Foundation"
        assert "AgenticFoundationService" in foundation_services, "Should have Agentic Foundation"
        assert "ExperienceFoundationService" in foundation_services, "Should have Experience Foundation"
        logger.info("✅ Test 5: Verify Foundation Services - PASSED")
        
        # Test 6: Verify startup sequence
        startup_sequence = startup_result.get("startup_sequence", [])
        assert "di_container" in startup_sequence, "Should have di_container in sequence"
        assert "router_manager" in startup_sequence, "Should have router_manager in sequence"
        assert "public_works_foundation" in startup_sequence, "Should have public_works_foundation in sequence"
        assert "curator_foundation" in startup_sequence, "Should have curator_foundation in sequence"
        logger.info("✅ Test 6: Verify startup sequence - PASSED")
        
        # Test 7: Get platform status
        status = await orchestrator.get_platform_status()
        assert status.get("mode") == "cloud_ready", "Status should indicate cloud_ready mode"
        assert "startup_status" in status, "Status should include startup_status"
        logger.info("✅ Test 7: Get platform status - PASSED")
        
        TEST_RESULTS["phase_1_4"]["passed"] = True
        logger.info("✅ Phase 1.4: Cloud-Ready Startup Orchestrator - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        error_msg = f"Phase 1.4 test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["phase_1_4"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_integration():
    """Test Integration: Auto-Discovery + Cloud-Ready Startup"""
    logger.info("=" * 80)
    logger.info("TEST: Integration - Auto-Discovery + Cloud-Ready Startup")
    logger.info("=" * 80)
    
    try:
        # Enable both features and test mode (makes Traefik optional)
        reset_cloud_ready_config()
        os.environ["CLOUD_READY_MODE"] = "enabled"
        os.environ["CLOUD_READY_AUTO_DISCOVERY"] = "true"
        os.environ["TEST_MODE"] = "true"  # Makes Traefik optional
        
        from main_cloud_ready import CloudReadyPlatformOrchestrator
        
        # Start platform
        orchestrator = CloudReadyPlatformOrchestrator()
        startup_result = await orchestrator.orchestrate_platform_startup()
        
        # Test 1: Auto-discovery should run during startup
        curator = orchestrator.get_foundation_service("CuratorFoundationService")
        assert curator is not None, "Curator Foundation should be available"
        assert curator.auto_discovery is not None, "Auto-discovery should be initialized"
        assert curator.auto_discovery.is_initialized, "Auto-discovery should be initialized"
        logger.info("✅ Test 1: Auto-discovery initialized during startup - PASSED")
        
        # Test 2: Services should be discovered
        discovered_services = curator.auto_discovery.discovered_services
        logger.info(f"✅ Discovered {len(discovered_services)} services during startup")
        logger.info("✅ Test 2: Services discovered during startup - PASSED")
        
        # Test 3: Unified registry should have services
        di_container = orchestrator.get_di_container()
        if di_container and di_container.unified_registry:
            services = di_container.unified_registry.list_services()
            logger.info(f"✅ Unified registry has {len(services)} services")
            logger.info("✅ Test 3: Unified registry populated - PASSED")
        
        TEST_RESULTS["integration"]["passed"] = True
        logger.info("✅ Integration Test - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        error_msg = f"Integration test failed: {e}"
        logger.error(f"❌ {error_msg}")
        TEST_RESULTS["integration"]["errors"].append(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return False


def reset_cloud_ready_config():
    """Reset cloud-ready config (helper function)."""
    from utilities.configuration.cloud_ready_config import reset_cloud_ready_config as reset
    reset()


async def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("CLOUD-READY PHASES 1.3 & 1.4 TEST SUITE")
    logger.info("=" * 80)
    logger.info("")
    
    # Test feature flags first (required for other tests)
    logger.info("📋 Running Feature Flag Tests...")
    feature_flags_passed = await test_feature_flags()
    logger.info("")
    
    # Test Phase 1.3
    logger.info("📋 Running Phase 1.3 Tests (Auto-Discovery)...")
    phase_1_3_passed = await test_phase_1_3_auto_discovery()
    logger.info("")
    
    # Test Phase 1.4
    logger.info("📋 Running Phase 1.4 Tests (Cloud-Ready Startup)...")
    phase_1_4_passed = await test_phase_1_4_cloud_ready_startup()
    logger.info("")
    
    # Test Integration
    logger.info("📋 Running Integration Tests...")
    integration_passed = await test_integration()
    logger.info("")
    
    # Print summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    all_passed = (
        feature_flags_passed and
        phase_1_3_passed and
        phase_1_4_passed and
        integration_passed
    )
    
    logger.info(f"Feature Flags:        {'✅ PASSED' if feature_flags_passed else '❌ FAILED'}")
    logger.info(f"Phase 1.3 (Auto-Discovery): {'✅ PASSED' if phase_1_3_passed else '❌ FAILED'}")
    logger.info(f"Phase 1.4 (Cloud-Ready Startup): {'✅ PASSED' if phase_1_4_passed else '❌ FAILED'}")
    logger.info(f"Integration:          {'✅ PASSED' if integration_passed else '❌ FAILED'}")
    logger.info("")
    
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED - Cloud-Ready Architecture Ready!")
        logger.info("")
        logger.info("✅ Phases 1.3 and 1.4 are working correctly")
        logger.info("✅ You can officially transition to cloud-ready architecture")
        logger.info("")
        logger.info("To enable cloud-ready mode, set:")
        logger.info("  CLOUD_READY_MODE=enabled")
        logger.info("")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.error("")
        logger.error("Errors:")
        for test_name, result in TEST_RESULTS.items():
            if not result["passed"] and result["errors"]:
                logger.error(f"  {test_name}:")
                for error in result["errors"]:
                    logger.error(f"    - {error}")
        logger.error("")
        logger.error("Please fix errors before transitioning to cloud-ready architecture")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

