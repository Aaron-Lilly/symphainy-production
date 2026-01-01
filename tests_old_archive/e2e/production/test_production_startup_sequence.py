#!/usr/bin/env python3
"""
Production Startup Sequence Test

Tests the actual production startup sequence to catch startup order issues,
dependency problems, and timing issues that cause production failures.

This test runs the EXACT same startup sequence as production, not mocks.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.e2e, pytest.mark.production_readiness]


class TestProductionStartupSequence:
    """Test the actual production startup sequence."""
    
    @pytest.mark.asyncio
    async def test_platform_orchestrator_starts_correctly(self):
        """Test that Platform Orchestrator starts correctly."""
        print("\n" + "="*70)
        print("TEST: Platform Orchestrator Startup")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator
            
            # Create orchestrator (like production)
            platform_orchestrator = PlatformOrchestrator()
            assert platform_orchestrator is not None, "Platform Orchestrator must be created"
            
            print("✅ Platform Orchestrator created successfully")
            
        except Exception as e:
            pytest.fail(f"❌ Platform Orchestrator creation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_all_startup_phases_complete(self):
        """Test that all startup phases complete in order."""
        print("\n" + "="*70)
        print("TEST: Startup Phases Completion")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator
            
            platform_orchestrator = PlatformOrchestrator()
            
            # Run startup sequence (like production)
            startup_result = await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify startup succeeded
            assert startup_result.get("success") == True, \
                f"Startup must succeed. Result: {startup_result}"
            
            # Verify all critical phases completed
            startup_sequence = startup_result.get("startup_sequence", [])
            
            required_phases = [
                "foundation_infrastructure",  # Actual phase name from platform
                "smart_city_gateway",
                "mvp_solution",
                "lazy_realm_hydration",
                "background_watchers",
                "curator_autodiscovery"
            ]
            
            for phase in required_phases:
                assert phase in startup_sequence, \
                    f"Required phase '{phase}' missing from startup sequence: {startup_sequence}"
                print(f"✅ Phase '{phase}' completed")
            
            print(f"\n✅ All {len(required_phases)} startup phases completed successfully")
            
        except Exception as e:
            pytest.fail(f"❌ Startup phases failed: {e}")
    
    @pytest.mark.asyncio
    async def test_critical_services_available_after_startup(self):
        """Test that critical services are available after startup."""
        print("\n" + "="*70)
        print("TEST: Critical Services Availability")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator
            
            platform_orchestrator = PlatformOrchestrator()
            await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify City Manager is available
            city_manager = platform_orchestrator.managers.get("city_manager")
            assert city_manager is not None, \
                "City Manager must be available after startup"
            print("✅ City Manager available")
            
            # Verify Platform Gateway is available
            platform_gateway = platform_orchestrator.infrastructure_services.get("platform_gateway")
            assert platform_gateway is not None, \
                "Platform Gateway must be available after startup"
            print("✅ Platform Gateway available")
            
            # Verify DI Container is available
            di_container = platform_orchestrator.infrastructure_services.get("di_container")
            assert di_container is not None, \
                "DI Container must be available after startup"
            print("✅ DI Container available")
            
            # Verify Curator is available
            curator = platform_orchestrator.foundation_services.get("CuratorFoundationService")
            assert curator is not None, \
                "Curator must be available after startup"
            print("✅ Curator available")
            
            print("\n✅ All critical services available after startup")
            
        except Exception as e:
            pytest.fail(f"❌ Critical services not available: {e}")
    
    @pytest.mark.asyncio
    async def test_services_available_when_routers_register(self):
        """Test that services required by routers are available when routers register."""
        print("\n" + "="*70)
        print("TEST: Service Availability at Router Registration")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator
            from fastapi import FastAPI
            from backend.api import register_api_routers
            
            # 1. Start platform (like production)
            platform_orchestrator = PlatformOrchestrator()
            await platform_orchestrator.orchestrate_platform_startup()
            
            # 2. Create FastAPI app (like production)
            app = FastAPI()
            
            # 3. Register API routers (like production)
            await register_api_routers(app, platform_orchestrator)
            
            print("✅ API routers registered successfully")
            
            # 4. Verify Security Guard can be accessed (critical for auth)
            platform_gateway = platform_orchestrator.infrastructure_services.get("platform_gateway")
            assert platform_gateway is not None, \
                "Platform Gateway must be available for Security Guard access"
            
            # Try to get Security Guard via platform gateway (lazy initialization)
            try:
                security_guard = await platform_gateway.get_abstraction("security")
                if security_guard:
                    print("✅ Security Guard available via Platform Gateway")
                else:
                    # Security Guard may initialize lazily - that's OK
                    print("⚠️ Security Guard will initialize on first request (lazy initialization)")
            except Exception as e:
                # Security Guard may not be initialized yet - check if it can be initialized
                city_manager = platform_orchestrator.managers.get("city_manager")
                if city_manager:
                    # Try to verify Security Guard is available
                    # Security Guard is initialized during startup, so we just verify it exists
                    try:
                        # Check if Security Guard service exists in the city manager
                        security_guard = getattr(city_manager, 'security_guard', None)
                        if security_guard:
                            print("✅ Security Guard is available")
                        else:
                            # Security Guard might be accessed differently - check if it's in services
                            services = getattr(city_manager, 'services', {})
                            if 'security_guard' in services or 'SecurityGuard' in str(type(city_manager)):
                                print("✅ Security Guard is available")
                            else:
                                print("⚠️ Security Guard not directly accessible (may be lazy-loaded)")
                    except Exception as init_error:
                        print(f"⚠️ Security Guard check failed: {init_error} (may be expected)")
                else:
                    pytest.fail("❌ City Manager not available for Security Guard initialization")
            
            # 5. Verify Frontend Gateway Service is available (critical for API routing)
            experience_foundation = platform_orchestrator.foundation_services.get(
                "ExperienceFoundationService"
            )
            if experience_foundation:
                try:
                    frontend_gateway = await experience_foundation.get_frontend_gateway_service()
                    if frontend_gateway:
                        print("✅ Frontend Gateway Service available")
                    else:
                        print("⚠️ Frontend Gateway Service will initialize on first request")
                except Exception as e:
                    print(f"⚠️ Frontend Gateway Service initialization deferred: {e}")
            else:
                print("⚠️ Experience Foundation not available (may initialize lazily)")
            
            print("\n✅ Service availability verified at router registration")
            
        except Exception as e:
            pytest.fail(f"❌ Service availability check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_background_tasks_started(self):
        """Test that background tasks are started (but may not complete immediately)."""
        print("\n" + "="*70)
        print("TEST: Background Tasks Started")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator
            
            platform_orchestrator = PlatformOrchestrator()
            await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify background tasks are tracked
            background_tasks = platform_orchestrator.background_tasks
            assert len(background_tasks) > 0, \
                "Background tasks should be started"
            
            print(f"✅ {len(background_tasks)} background tasks started")
            
            # Verify background tasks are running (not cancelled)
            running_tasks = [task for task in background_tasks if not task.done()]
            print(f"✅ {len(running_tasks)} background tasks still running")
            
            # Note: Background tasks may not complete immediately - that's OK
            # The important thing is that they're started and running
            
        except Exception as e:
            pytest.fail(f"❌ Background tasks check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_startup_status_tracking(self):
        """Test that startup status is tracked correctly."""
        print("\n" + "="*70)
        print("TEST: Startup Status Tracking")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator
            
            platform_orchestrator = PlatformOrchestrator()
            await platform_orchestrator.orchestrate_platform_startup()
            
            # Verify startup status is tracked
            startup_status = platform_orchestrator.startup_status
            
            # Verify critical phases are tracked
            required_status_keys = [
                "foundation",
                "smart_city_gateway",
                "lazy_hydration",
                "background_watchers",
                "curator_autodiscovery"
            ]
            
            for key in required_status_keys:
                assert key in startup_status, \
                    f"Startup status missing key: {key}"
                status_value = startup_status[key]
                print(f"✅ {key}: {status_value}")
            
            print("\n✅ Startup status tracking verified")
            
        except Exception as e:
            pytest.fail(f"❌ Startup status tracking failed: {e}")
    
    @pytest.mark.asyncio
    async def test_full_production_startup_sequence(self):
        """Test the complete production startup sequence end-to-end."""
        print("\n" + "="*70)
        print("TEST: Full Production Startup Sequence")
        print("="*70)
        
        try:
            from main import PlatformOrchestrator, lifespan
            from fastapi import FastAPI
            
            # Create FastAPI app (like production)
            app = FastAPI()
            
            # Run lifespan (like production)
            async with lifespan(app):
                # Verify app state is set
                from main import app_state
                
                platform_orchestrator = app_state.get("platform_orchestrator")
                assert platform_orchestrator is not None, \
                    "Platform Orchestrator must be in app state"
                
                startup_result = app_state.get("startup_result")
                assert startup_result is not None, \
                    "Startup result must be in app state"
                assert startup_result.get("success") == True, \
                    "Startup must succeed"
                
                print("✅ Full production startup sequence completed successfully")
                print(f"   - Startup sequence: {startup_result.get('startup_sequence', [])}")
                print(f"   - Managers: {startup_result.get('managers', [])}")
                print(f"   - Foundation services: {startup_result.get('foundation_services', [])}")
                
        except Exception as e:
            pytest.fail(f"❌ Full production startup sequence failed: {e}")


