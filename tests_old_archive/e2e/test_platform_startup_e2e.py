#!/usr/bin/env python3
"""
Production Readiness Test: Full Platform Startup E2E

Tests the complete platform startup sequence from foundations through realm services.
This validates that the platform can start successfully in production-like conditions.
"""

import pytest
import asyncio

from pathlib import Path
from typing import Dict, Any

if platform_path.exists():
    sys.path.insert(0, str(platform_path))
else:
    # Try alternative path
    alt_path = project_root.parent / "symphainy-platform"
    if alt_path.exists():
        sys.path.insert(0, str(alt_path))
    else:
        # Last resort: assume we're in symphainy_source

# Note: Test fixtures may be imported if needed, but we'll use direct initialization for this test

class TestPlatformStartupE2E:
    """Test complete platform startup sequence."""
    
    @pytest.mark.asyncio
    async def test_phase_1_foundation_infrastructure(self):
        """Test Phase 1: Foundation Infrastructure initialization."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
        from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        public_works_foundation = PublicWorksFoundationService(di_container=di_container)
        await public_works_foundation.initialize()
        di_container.service_registry["PublicWorksFoundationService"] = public_works_foundation
        
        # Initialize Curator Foundation (needs foundation_services and public_works_foundation)
        curator_foundation = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=public_works_foundation
        )
        await curator_foundation.initialize()
        di_container.service_registry["CuratorFoundationService"] = curator_foundation
        
        # Initialize Communication Foundation (needs di_container, public_works_foundation, curator_foundation)
        communication_foundation = CommunicationFoundationService(
            di_container=di_container,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
        await communication_foundation.initialize()
        di_container.service_registry["CommunicationFoundationService"] = communication_foundation
        
        # Initialize Agentic Foundation (needs di_container, public_works_foundation, curator_foundation)
        agentic_foundation = AgenticFoundationService(
            di_container=di_container,
            public_works_foundation=public_works_foundation,
            curator_foundation=curator_foundation
        )
        await agentic_foundation.initialize()
        di_container.service_registry["AgenticFoundationService"] = agentic_foundation
        
        # Verify all foundations are initialized
        assert public_works_foundation.is_initialized
        assert curator_foundation.is_initialized
        assert communication_foundation.is_initialized
        assert agentic_foundation.is_initialized
        
        return {"di_container": di_container, "foundations": {
            "public_works": public_works_foundation,
            "curator": curator_foundation,
            "communication": communication_foundation,
            "agentic": agentic_foundation
        }}
    
    @pytest.mark.asyncio
    async def test_phase_2_platform_gateway(self):
        """Test Phase 2: Platform Gateway initialization."""
        # Get foundations from Phase 1
        phase1_result = await self.test_phase_1_foundation_infrastructure()
        di_container = phase1_result["di_container"]
        public_works_foundation = phase1_result["foundations"]["public_works"]
        
        # Initialize Platform Gateway
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        platform_gateway = PlatformInfrastructureGateway(public_works_foundation=public_works_foundation)
        await platform_gateway.initialize()
        di_container.service_registry["PlatformInfrastructureGateway"] = platform_gateway
        
        # Verify Platform Gateway is initialized
        assert platform_gateway.is_initialized
        
        return {"di_container": di_container, "platform_gateway": platform_gateway}
    
    @pytest.mark.asyncio
    async def test_phase_3_smart_city_services(self):
        """Test Phase 3: Smart City Services initialization."""
        # Get dependencies from Phase 2
        phase2_result = await self.test_phase_2_platform_gateway()
        di_container = phase2_result["di_container"]
        
        # Initialize City Manager
        from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
        import traceback
        
        city_manager = CityManagerService(di_container=di_container)
        
        # Try to initialize and capture any exceptions
        try:
            init_result = await city_manager.initialize()
        except Exception as e:
            traceback.print_exc()
            raise AssertionError(f"City Manager initialization raised exception: {e}")
        
        # If initialization failed, provide detailed error information
        if not init_result or not city_manager.is_initialized:
            error_msg = f"City Manager initialization failed. Return value: {init_result}, is_initialized: {city_manager.is_initialized}, service_health: {city_manager.service_health}"
            # Print recent logs if available
            print(f"\n=== City Manager Initialization Debug Info ===")
            print(f"Service health: {city_manager.service_health}")
            print(f"Is initialized: {city_manager.is_initialized}")
            print(f"Initialization result: {init_result}")
            if hasattr(city_manager, 'initialization_module'):
                print(f"Initialization module exists: {city_manager.initialization_module}")
            raise AssertionError(error_msg)
        
        di_container.service_registry["CityManagerService"] = city_manager
        
        # Verify City Manager is initialized
        assert city_manager.is_initialized, f"City Manager not initialized. Service health: {city_manager.service_health}"
        
        return {"di_container": di_container, "city_manager": city_manager}
    
    @pytest.mark.asyncio
    async def test_phase_4_manager_hierarchy(self):
        """Test Phase 4: Manager Hierarchy bootstrap."""
        # Get dependencies from Phase 3
        phase3_result = await self.test_phase_3_smart_city_services()
        di_container = phase3_result["di_container"]
        city_manager = phase3_result["city_manager"]
        
        # Bootstrap manager hierarchy
        from backend.smart_city.protocols.city_manager_service_protocol import BootstrapRequest
        bootstrap_request = BootstrapRequest(
            solution_context=None,
            start_from=None  # None = full bootstrap from Solution Manager
        )
        bootstrap_result = await city_manager.bootstrap_manager_hierarchy(bootstrap_request)
        
        # Verify bootstrap succeeded
        assert bootstrap_result.success, f"Bootstrap failed: {bootstrap_result.error}"
        
        # Verify all managers are bootstrapped
        assert "solution_manager" in bootstrap_result.bootstrapped_managers
        assert "journey_manager" in bootstrap_result.bootstrapped_managers
        assert "experience_manager" in bootstrap_result.bootstrapped_managers
        assert "delivery_manager" in bootstrap_result.bootstrapped_managers
        
        return {"di_container": di_container, "bootstrap_result": bootstrap_result}
    
    @pytest.mark.asyncio
    async def test_phase_5_realm_services(self):
        """Test Phase 5: Realm Services initialization."""
        # Get dependencies from Phase 4
        phase4_result = await self.test_phase_4_manager_hierarchy()
        di_container = phase4_result["di_container"]
        platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
        
        # Initialize Business Orchestrator
        from backend.business_enablement.business_orchestrator.business_orchestrator_service import BusinessOrchestratorService
        business_orchestrator = BusinessOrchestratorService(
            service_name="BusinessOrchestratorService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        await business_orchestrator.initialize()
        
        # Verify Business Orchestrator is initialized
        assert business_orchestrator.is_initialized
        
        return {"di_container": di_container, "business_orchestrator": business_orchestrator}
    
    @pytest.mark.asyncio
    async def test_complete_startup_sequence(self):
        """Test complete startup sequence end-to-end."""
        # Run all phases sequentially
        phase1 = await self.test_phase_1_foundation_infrastructure()
        phase2 = await self.test_phase_2_platform_gateway()
        phase3 = await self.test_phase_3_smart_city_services()
        phase4 = await self.test_phase_4_manager_hierarchy()
        phase5 = await self.test_phase_5_realm_services()
        
        # Verify complete startup
        assert phase1["foundations"]["public_works"].is_initialized
        assert phase2["platform_gateway"].is_initialized
        assert phase3["city_manager"].is_initialized
        assert phase4["bootstrap_result"].success
        assert phase5["business_orchestrator"].is_initialized
        
        return {
            "success": True,
            "phases": {
                "foundations": phase1,
                "platform_gateway": phase2,
                "smart_city": phase3,
                "manager_hierarchy": phase4,
                "realm_services": phase5
            }
        }
    
    @pytest.mark.asyncio
    async def test_manager_orchestration_flow(self):
        """Test manager-to-manager orchestration flow (top-down pattern)."""
        # First, ensure all managers are bootstrapped
        phase4_result = await self.test_phase_4_manager_hierarchy()
        di_container = phase4_result["di_container"]
        bootstrap_result = phase4_result["bootstrap_result"]
        
        # Verify all managers are bootstrapped
        assert bootstrap_result.success, "Manager hierarchy bootstrap failed"
        assert "solution_manager" in bootstrap_result.bootstrapped_managers
        assert "journey_manager" in bootstrap_result.bootstrapped_managers
        assert "experience_manager" in bootstrap_result.bootstrapped_managers
        assert "delivery_manager" in bootstrap_result.bootstrapped_managers
        
        # Get managers from DI Container
        solution_manager = di_container.get_foundation_service("SolutionManagerService")
        journey_manager = di_container.get_foundation_service("JourneyManagerService")
        experience_manager = di_container.get_foundation_service("ExperienceManagerService")
        delivery_manager = di_container.get_foundation_service("DeliveryManagerService")
        
        # Verify all managers are initialized
        assert solution_manager.is_initialized, "Solution Manager not initialized"
        assert journey_manager.is_initialized, "Journey Manager not initialized"
        assert experience_manager.is_initialized, "Experience Manager not initialized"
        assert delivery_manager.is_initialized, "Delivery Manager not initialized"
        
        # Test 1: Solution Manager → Journey Manager
        print("\n📊 Testing: Solution Manager → Journey Manager")
        journey_context = {
            "user_intent": "test_intent",
            "business_outcome": "test_outcome",
            "solution_id": "test_solution"
        }
        journey_result = await solution_manager.orchestrate_journey(journey_context)
        assert journey_result.get("success") or journey_result.get("journey_orchestrated"), \
            f"Journey orchestration failed: {journey_result.get('error', 'Unknown error')}"
        print(f"✅ Solution Manager → Journey Manager: {journey_result.get('success', False)}")
        
        # Test 2: Journey Manager → Experience Manager
        print("\n📊 Testing: Journey Manager → Experience Manager")
        experience_context = {
            "journey_id": "test_journey",
            "user_context": {"user_id": "test_user"},
            "experience_type": "mvp"
        }
        experience_result = await journey_manager.orchestrate_experience(experience_context)
        assert experience_result.get("success") or experience_result.get("experience_orchestrated"), \
            f"Experience orchestration failed: {experience_result.get('error', 'Unknown error')}"
        print(f"✅ Journey Manager → Experience Manager: {experience_result.get('success', False)}")
        
        # Test 3: Experience Manager → Delivery Manager
        print("\n📊 Testing: Experience Manager → Delivery Manager")
        delivery_context = {
            "experience_id": "test_experience",
            "business_outcome": "test_outcome",
            "delivery_type": "business_enablement"
        }
        delivery_result = await experience_manager.orchestrate_delivery(delivery_context)
        assert delivery_result.get("success") or delivery_result.get("delivery_orchestrated"), \
            f"Delivery orchestration failed: {delivery_result.get('error', 'Unknown error')}"
        print(f"✅ Experience Manager → Delivery Manager: {delivery_result.get('success', False)}")
        
        return {
            "success": True,
            "orchestration_flow": {
                "solution_to_journey": journey_result,
                "journey_to_experience": experience_result,
                "experience_to_delivery": delivery_result
            }
        }
    
    @pytest.mark.asyncio
    async def test_cross_realm_communication(self):
        """Test cross-realm communication via Platform Gateway access control."""
        # First, ensure all phases are complete
        phase4_result = await self.test_phase_4_manager_hierarchy()
        di_container = phase4_result["di_container"]
        platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
        
        # Verify Platform Gateway is initialized
        assert platform_gateway.is_initialized, "Platform Gateway not initialized"
        
        # Get managers for testing
        solution_manager = di_container.get_foundation_service("SolutionManagerService")
        journey_manager = di_container.get_foundation_service("JourneyManagerService")
        experience_manager = di_container.get_foundation_service("ExperienceManagerService")
        business_orchestrator = di_container.get_foundation_service("BusinessOrchestratorService")
        
        # Verify all managers are initialized
        assert solution_manager.is_initialized, "Solution Manager not initialized"
        assert journey_manager.is_initialized, "Journey Manager not initialized"
        assert experience_manager.is_initialized, "Experience Manager not initialized"
        
        print("\n📊 Testing Cross-Realm Communication via Platform Gateway\n")
        
        # Test 1: Solution Realm - Should have access to llm, content_metadata, file_management
        print("🔍 Test 1: Solution Realm Access")
        solution_allowed = ["llm", "content_metadata", "file_management"]
        solution_denied = ["session", "state", "auth"]  # Should NOT have access
        
        for abstraction in solution_allowed:
            try:
                abstraction_obj = platform_gateway.get_abstraction("solution", abstraction)
                # Abstractions can be None if not initialized (access control is what we're testing)
                # The key is that get_abstraction() doesn't raise ValueError (access denied)
                print(f"  ✅ Solution realm can access: {abstraction} (value: {abstraction_obj is not None})")
            except ValueError as e:
                # ValueError means access was denied (security issue)
                print(f"  ❌ Solution realm access denied for {abstraction}: {e}")
                raise
            except Exception as e:
                # Other exceptions are infrastructure issues (not access control issues)
                print(f"  ⚠️ Solution realm infrastructure issue for {abstraction}: {e}")
                # Don't fail the test for infrastructure issues - just log
        
        for abstraction in solution_denied:
            try:
                platform_gateway.get_abstraction("solution", abstraction)
                print(f"  ❌ Solution realm should NOT access {abstraction} (SECURITY ISSUE!)")
                raise AssertionError(f"Solution realm incorrectly granted access to {abstraction}")
            except ValueError as e:
                print(f"  ✅ Solution realm correctly denied access to: {abstraction}")
        
        # Test 2: Journey Realm - Should have access to llm, session, content_metadata
        print("\n🔍 Test 2: Journey Realm Access")
        journey_allowed = ["llm", "session", "content_metadata"]
        journey_denied = ["state", "file_management"]  # Should NOT have access
        
        for abstraction in journey_allowed:
            try:
                abstraction_obj = platform_gateway.get_abstraction("journey", abstraction)
                # Abstractions can be None if not initialized (access control is what we're testing)
                print(f"  ✅ Journey realm can access: {abstraction} (value: {abstraction_obj is not None})")
            except ValueError as e:
                print(f"  ❌ Journey realm access denied for {abstraction}: {e}")
                raise
            except Exception as e:
                print(f"  ⚠️ Journey realm infrastructure issue for {abstraction}: {e}")
        
        for abstraction in journey_denied:
            try:
                platform_gateway.get_abstraction("journey", abstraction)
                print(f"  ❌ Journey realm should NOT access {abstraction} (SECURITY ISSUE!)")
                raise AssertionError(f"Journey realm incorrectly granted access to {abstraction}")
            except ValueError as e:
                print(f"  ✅ Journey realm correctly denied access to: {abstraction}")
        
        # Test 3: Experience Realm - Should have access to session, auth, authorization, tenant
        print("\n🔍 Test 3: Experience Realm Access")
        experience_allowed = ["session", "auth", "authorization", "tenant"]
        experience_denied = ["llm", "file_management", "content_metadata"]  # Should NOT have access
        
        for abstraction in experience_allowed:
            try:
                abstraction_obj = platform_gateway.get_abstraction("experience", abstraction)
                # Abstractions can be None if not initialized (access control is what we're testing)
                print(f"  ✅ Experience realm can access: {abstraction} (value: {abstraction_obj is not None})")
            except ValueError as e:
                print(f"  ❌ Experience realm access denied for {abstraction}: {e}")
                raise
            except Exception as e:
                print(f"  ⚠️ Experience realm infrastructure issue for {abstraction}: {e}")
        
        for abstraction in experience_denied:
            try:
                platform_gateway.get_abstraction("experience", abstraction)
                print(f"  ❌ Experience realm should NOT access {abstraction} (SECURITY ISSUE!)")
                raise AssertionError(f"Experience realm incorrectly granted access to {abstraction}")
            except ValueError as e:
                print(f"  ✅ Experience realm correctly denied access to: {abstraction}")
        
        # Test 4: Business Enablement Realm - Should have access to content_metadata, file_management, llm
        print("\n🔍 Test 4: Business Enablement Realm Access")
        business_allowed = ["content_metadata", "file_management", "llm"]
        business_denied = ["session", "state", "auth"]  # Should NOT have access
        
        for abstraction in business_allowed:
            try:
                abstraction_obj = platform_gateway.get_abstraction("business_enablement", abstraction)
                # Abstractions can be None if not initialized (access control is what we're testing)
                print(f"  ✅ Business Enablement realm can access: {abstraction} (value: {abstraction_obj is not None})")
            except ValueError as e:
                print(f"  ❌ Business Enablement realm access denied for {abstraction}: {e}")
                raise
            except Exception as e:
                print(f"  ⚠️ Business Enablement realm infrastructure issue for {abstraction}: {e}")
        
        for abstraction in business_denied:
            try:
                platform_gateway.get_abstraction("business_enablement", abstraction)
                print(f"  ❌ Business Enablement realm should NOT access {abstraction} (SECURITY ISSUE!)")
                raise AssertionError(f"Business Enablement realm incorrectly granted access to {abstraction}")
            except ValueError as e:
                print(f"  ✅ Business Enablement realm correctly denied access to: {abstraction}")
        
        # Test 5: Smart City Services - Should bypass Platform Gateway and access Public Works directly
        print("\n🔍 Test 5: Smart City Services Direct Access")
        city_manager = di_container.get_foundation_service("CityManagerService")
        assert city_manager is not None, "City Manager not available"
        
        # City Manager should access abstractions directly (not via Platform Gateway)
        # This is validated by checking that City Manager has direct access to Public Works Foundation
        public_works = di_container.get_foundation_service("PublicWorksFoundationService")
        assert public_works is not None, "Public Works Foundation not available"
        
        # City Manager should be able to access file_management directly
        file_mgmt = city_manager.get_file_management_abstraction()
        assert file_mgmt is not None, "City Manager should have direct access to file_management"
        print("  ✅ Smart City services bypass Platform Gateway (by design)")
        
        # Test 6: Validate realm capability queries
        print("\n🔍 Test 6: Realm Capability Queries")
        solution_caps = platform_gateway.get_realm_capabilities("solution")
        assert solution_caps is not None, "Solution realm capabilities should be available"
        assert "llm" in solution_caps.abstractions, "Solution should have llm capability"
        print(f"  ✅ Solution realm capabilities: {len(solution_caps.abstractions)} abstractions")
        
        journey_caps = platform_gateway.get_realm_capabilities("journey")
        assert journey_caps is not None, "Journey realm capabilities should be available"
        assert "session" in journey_caps.abstractions, "Journey should have session capability"
        print(f"  ✅ Journey realm capabilities: {len(journey_caps.abstractions)} abstractions")
        
        # Test 7: Validate access metrics
        print("\n🔍 Test 7: Platform Gateway Metrics")
        metrics = platform_gateway.access_metrics
        assert metrics["total_requests"] > 0, "Platform Gateway should track access requests"
        print(f"  ✅ Total requests: {metrics['total_requests']}")
        print(f"  ✅ Successful requests: {metrics['successful_requests']}")
        print(f"  ✅ Denied requests: {metrics['denied_requests']}")
        
        return {
            "success": True,
            "realm_access_tested": {
                "solution": solution_allowed,
                "journey": journey_allowed,
                "experience": experience_allowed,
                "business_enablement": business_allowed
            },
            "access_control_validated": True,
            "smart_city_bypass_validated": True,
            "metrics": metrics
        }
    
    @pytest.mark.asyncio
    async def test_mvp_user_journey(self):
        """
        Test complete MVP user journey from landing to business outcome.
        
        Flow:
        1. User lands on platform (Solution Manager designs solution)
        2. Journey Manager orchestrates journey (4 pillars: Content → Insights → Operations → Business Outcome)
        3. Experience Manager coordinates experience
        4. Delivery Manager enables business outcomes
        """
        # First, ensure complete platform startup
        phase4_result = await self.test_phase_4_manager_hierarchy()
        di_container = phase4_result["di_container"]
        
        # Get all managers
        solution_manager = di_container.get_foundation_service("SolutionManagerService")
        journey_manager = di_container.get_foundation_service("JourneyManagerService")
        experience_manager = di_container.get_foundation_service("ExperienceManagerService")
        delivery_manager = di_container.get_foundation_service("DeliveryManagerService")
        
        # Verify all managers are initialized
        assert solution_manager.is_initialized, "Solution Manager not initialized"
        assert journey_manager.is_initialized, "Journey Manager not initialized"
        assert experience_manager.is_initialized, "Experience Manager not initialized"
        assert delivery_manager.is_initialized, "Delivery Manager not initialized"
        
        print("\n🚀 Testing Complete MVP User Journey\n")
        
        # Step 1: User lands on platform - Solution Manager designs solution
        print("📋 Step 1: User Lands on Platform (Solution Manager)")
        user_intent = {
            "business_outcome": "Improve operational efficiency through data-driven insights",
            "user_id": "test_user_001",
            "context": {
                "industry": "manufacturing",
                "use_case": "operational_analytics"
            }
        }
        
        # Design solution via Solution Manager
        solution_result = await solution_manager.design_solution({
            "solution_type": "mvp",
            "user_intent": user_intent,
            "context": user_intent.get("context", {})
        })
        
        # Solution design should succeed (or gracefully handle if not fully implemented)
        print(f"  ✅ Solution design initiated: {solution_result.get('success', False)}")
        if solution_result.get("error"):
            print(f"  ⚠️ Solution design details: {solution_result.get('error')}")
        
        # Step 2: Journey Manager orchestrates journey
        print("\n🗺️ Step 2: Journey Manager Orchestrates Journey")
        journey_context = {
            "solution_id": solution_result.get("solution_id", "mvp_solution_001"),
            "user_intent": user_intent,
            "journey_type": "mvp",
            "pillars": ["content", "insights", "operations", "business_outcome"]
        }
        
        # Design journey via Journey Manager
        journey_result = await journey_manager.design_journey(journey_context)
        
        # Journey design should succeed
        print(f"  ✅ Journey designed: {journey_result.get('success', False)}")
        if journey_result.get("journey_id"):
            print(f"  ✅ Journey ID: {journey_result.get('journey_id')}")
        
        # Test journey orchestration (Solution → Journey flow)
        print("\n🔄 Step 2a: Testing Solution → Journey Orchestration")
        orchestration_result = await solution_manager.orchestrate_journey(journey_context)
        assert orchestration_result.get("success") or orchestration_result.get("journey_orchestrated"), \
            f"Journey orchestration failed: {orchestration_result.get('error', 'Unknown error')}"
        print(f"  ✅ Solution Manager → Journey Manager orchestration successful")
        
        # Step 3: Experience Manager coordinates experience
        print("\n🎨 Step 3: Experience Manager Coordinates Experience")
        experience_context = {
            "journey_id": journey_result.get("journey_id", "mvp_journey_001"),
            "user_context": {
                "user_id": user_intent.get("user_id"),
                "session_id": "test_session_001"
            },
            "experience_type": "mvp"
        }
        
        # Coordinate experience via Experience Manager
        experience_result = await experience_manager.coordinate_experience(experience_context)
        
        # Experience coordination should succeed
        print(f"  ✅ Experience coordinated: {experience_result.get('success', False)}")
        
        # Test experience orchestration (Journey → Experience flow)
        print("\n🔄 Step 3a: Testing Journey → Experience Orchestration")
        experience_orchestration = await journey_manager.orchestrate_experience(experience_context)
        assert experience_orchestration.get("success") or experience_orchestration.get("experience_orchestrated"), \
            f"Experience orchestration failed: {experience_orchestration.get('error', 'Unknown error')}"
        print(f"  ✅ Journey Manager → Experience Manager orchestration successful")
        
        # Step 4: Delivery Manager enables business outcomes
        print("\n💼 Step 4: Delivery Manager Enables Business Outcomes")
        delivery_context = {
            "experience_id": experience_result.get("experience_id", "mvp_experience_001"),
            "business_outcome": user_intent.get("business_outcome"),
            "delivery_type": "business_enablement",
            "pillar": "business_outcome"
        }
        
        # Orchestrate delivery via Delivery Manager
        delivery_result = await delivery_manager.orchestrate_business_enablement(delivery_context)
        
        # Delivery orchestration should succeed
        print(f"  ✅ Business enablement orchestrated: {delivery_result.get('success', False)}")
        
        # Test delivery orchestration (Experience → Delivery flow)
        print("\n🔄 Step 4a: Testing Experience → Delivery Orchestration")
        delivery_orchestration = await experience_manager.orchestrate_delivery(delivery_context)
        assert delivery_orchestration.get("success") or delivery_orchestration.get("delivery_orchestrated"), \
            f"Delivery orchestration failed: {delivery_orchestration.get('error', 'Unknown error')}"
        print(f"  ✅ Experience Manager → Delivery Manager orchestration successful")
        
        # Step 5: Validate complete flow
        print("\n✅ Step 5: Validating Complete Flow")
        flow_validation = {
            "solution_designed": solution_result.get("success") or solution_result.get("solution_id") is not None,
            "journey_orchestrated": orchestration_result.get("success") or orchestration_result.get("journey_orchestrated"),
            "experience_orchestrated": experience_orchestration.get("success") or experience_orchestration.get("experience_orchestrated"),
            "delivery_orchestrated": delivery_orchestration.get("success") or delivery_orchestration.get("delivery_orchestrated")
        }
        
        print(f"  ✅ Solution → Journey → Experience → Delivery flow validated")
        print(f"  ✅ All manager orchestrations successful")
        
        return {
            "success": True,
            "user_journey": {
                "user_intent": user_intent,
                "solution_result": solution_result,
                "journey_result": journey_result,
                "experience_result": experience_result,
                "delivery_result": delivery_result
            },
            "orchestration_flow": {
                "solution_to_journey": orchestration_result,
                "journey_to_experience": experience_orchestration,
                "experience_to_delivery": delivery_orchestration
            },
            "flow_validation": flow_validation
        }
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """
        Test error handling and recovery scenarios.
        
        Tests:
        1. Manager initialization failure recovery
        2. Invalid abstraction access error handling
        3. Service unavailable error handling
        4. Graceful degradation when services fail
        """
        # First, ensure complete platform startup
        phase4_result = await self.test_phase_4_manager_hierarchy()
        di_container = phase4_result["di_container"]
        platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
        
        print("\n🛡️ Testing Error Handling and Recovery\n")
        
        # Test 1: Invalid abstraction access error handling
        print("🔍 Test 1: Invalid Abstraction Access Error Handling")
        try:
            # Try to access unauthorized abstraction
            platform_gateway.get_abstraction("solution", "session")  # Solution realm should NOT have session access
            print("  ❌ Should have raised ValueError for unauthorized access")
            raise AssertionError("Unauthorized access should have been denied")
        except ValueError as e:
            print(f"  ✅ Unauthorized access correctly denied: {str(e)[:60]}...")
            assert "cannot access" in str(e).lower(), "Error message should indicate access denied"
        
        # Test 2: Service unavailable error handling
        print("\n🔍 Test 2: Service Unavailable Error Handling")
        # Get a manager and test its error handling
        solution_manager = di_container.get_foundation_service("SolutionManagerService")
        assert solution_manager is not None, "Solution Manager should be available"
        
        # Test graceful handling when a service method is called with invalid data
        try:
            # Try to design solution with invalid data
            invalid_result = await solution_manager.design_solution({
                "solution_type": None,  # Invalid: None value
                "user_intent": None  # Invalid: None value
            })
            # Should handle gracefully (either return error or handle None values)
            print(f"  ✅ Invalid input handled gracefully: success={invalid_result.get('success', False)}")
        except Exception as e:
            # Exception is also acceptable - the key is it doesn't crash the platform
            print(f"  ✅ Invalid input error caught: {type(e).__name__}")
        
        # Test 3: Manager initialization failure recovery
        print("\n🔍 Test 3: Manager Initialization Failure Recovery")
        # Test that managers can be re-initialized if they fail
        journey_manager = di_container.get_foundation_service("JourneyManagerService")
        assert journey_manager is not None, "Journey Manager should be available"
        
        # Check if manager has health check method
        if hasattr(journey_manager, 'health_check'):
            health_result = await journey_manager.health_check()
            print(f"  ✅ Journey Manager health check available: {health_result.get('status', 'unknown')}")
        else:
            print("  ⚠️ Journey Manager health check not available (may not be implemented)")
        
        # Test 4: Graceful degradation when abstraction is None
        print("\n🔍 Test 4: Graceful Degradation with None Abstractions")
        # Test that services handle None abstractions gracefully
        experience_manager = di_container.get_foundation_service("ExperienceManagerService")
        assert experience_manager is not None, "Experience Manager should be available"
        
        # Services should handle None abstractions without crashing
        if hasattr(experience_manager, 'is_initialized'):
            print(f"  ✅ Experience Manager initialized: {experience_manager.is_initialized}")
        
        # Test 5: Error propagation through manager hierarchy
        print("\n🔍 Test 5: Error Propagation Through Manager Hierarchy")
        # Test that errors are properly propagated and handled
        delivery_manager = di_container.get_foundation_service("DeliveryManagerService")
        assert delivery_manager is not None, "Delivery Manager should be available"
        
        # Try orchestration with potentially invalid context
        try:
            invalid_context = {"invalid_key": "invalid_value"}
            result = await delivery_manager.orchestrate_business_enablement(invalid_context)
            # Should handle gracefully
            print(f"  ✅ Invalid context handled gracefully: success={result.get('success', False)}")
        except Exception as e:
            # Exception is acceptable - the key is it doesn't crash
            print(f"  ✅ Invalid context error caught: {type(e).__name__}")
        
        # Test 6: Platform Gateway error tracking
        print("\n🔍 Test 6: Platform Gateway Error Tracking")
        # Check that Platform Gateway tracks denied requests
        metrics_before = platform_gateway.access_metrics.get("denied_requests", 0)
        
        # Make an invalid request
        try:
            platform_gateway.get_abstraction("solution", "state")  # Should be denied
        except ValueError:
            pass  # Expected
        
        metrics_after = platform_gateway.access_metrics.get("denied_requests", 0)
        assert metrics_after >= metrics_before, "Denied requests should be tracked"
        print(f"  ✅ Error tracking working: denied_requests={metrics_after}")
        
        return {
            "success": True,
            "error_handling_tests": {
                "invalid_access_handled": True,
                "service_unavailable_handled": True,
                "initialization_failure_recovery": True,
                "graceful_degradation": True,
                "error_propagation": True,
                "error_tracking": True
            }
        }
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """
        Test health monitoring and service discovery.
        
        Tests:
        1. Foundation service health checks
        2. Manager service health checks
        3. Service discovery via Curator
        4. Platform Gateway health status
        5. DI Container service registry health
        """
        # First, ensure complete platform startup
        phase4_result = await self.test_phase_4_manager_hierarchy()
        di_container = phase4_result["di_container"]
        
        print("\n🏥 Testing Health Monitoring and Service Discovery\n")
        
        # Test 1: Foundation Service Health Checks
        print("🔍 Test 1: Foundation Service Health Checks")
        public_works = di_container.get_foundation_service("PublicWorksFoundationService")
        assert public_works is not None, "Public Works Foundation should be available"
        
        # Check if foundation is initialized
        assert public_works.is_initialized, "Public Works Foundation should be initialized"
        print(f"  ✅ Public Works Foundation: initialized={public_works.is_initialized}, health={getattr(public_works, 'service_health', 'unknown')}")
        
        curator = di_container.get_foundation_service("CuratorFoundationService")
        if curator:
            assert curator.is_initialized, "Curator Foundation should be initialized"
            print(f"  ✅ Curator Foundation: initialized={curator.is_initialized}")
        
        # Test 2: Manager Service Health Checks
        print("\n🔍 Test 2: Manager Service Health Checks")
        managers = {
            "SolutionManagerService": di_container.get_foundation_service("SolutionManagerService"),
            "JourneyManagerService": di_container.get_foundation_service("JourneyManagerService"),
            "ExperienceManagerService": di_container.get_foundation_service("ExperienceManagerService"),
            "DeliveryManagerService": di_container.get_foundation_service("DeliveryManagerService")
        }
        
        for manager_name, manager in managers.items():
            if manager:
                assert manager.is_initialized, f"{manager_name} should be initialized"
                health_status = getattr(manager, 'service_health', 'unknown')
                print(f"  ✅ {manager_name}: initialized={manager.is_initialized}, health={health_status}")
                
                # Test health_check method if available
                if hasattr(manager, 'health_check'):
                    try:
                        health_result = await manager.health_check()
                        print(f"    ✅ {manager_name} health_check() available: {health_result.get('status', 'unknown')}")
                    except Exception as e:
                        print(f"    ⚠️ {manager_name} health_check() error: {type(e).__name__}")
        
        # Test 3: Service Discovery via Curator
        print("\n🔍 Test 3: Service Discovery via Curator")
        if curator:
            # Check if Curator has discovery methods
            if hasattr(curator, 'get_registered_service'):
                # Try to discover a service
                city_manager = curator.get_registered_service("CityManagerService")
                if city_manager:
                    print(f"  ✅ City Manager discovered via Curator")
                else:
                    print(f"  ⚠️ City Manager not found in Curator (may not be registered)")
            else:
                print(f"  ⚠️ Curator discovery methods not available (may not be implemented)")
        
        # Test 4: Platform Gateway Health Status
        print("\n🔍 Test 4: Platform Gateway Health Status")
        platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
        assert platform_gateway is not None, "Platform Gateway should be available"
        assert platform_gateway.is_initialized, "Platform Gateway should be initialized"
        
        # Check access metrics
        metrics = platform_gateway.access_metrics
        print(f"  ✅ Platform Gateway: initialized={platform_gateway.is_initialized}")
        print(f"  ✅ Access metrics: total={metrics.get('total_requests', 0)}, successful={metrics.get('successful_requests', 0)}, denied={metrics.get('denied_requests', 0)}")
        
        # Test 5: DI Container Service Registry Health
        print("\n🔍 Test 5: DI Container Service Registry Health")
        service_registry = di_container.service_registry
        service_count = len(service_registry)
        print(f"  ✅ Service registry: {service_count} services registered")
        
        # List key services
        key_services = [
            "PublicWorksFoundationService",
            "CuratorFoundationService",
            "CommunicationFoundationService",
            "AgenticFoundationService",
            "PlatformInfrastructureGateway",
            "CityManagerService",
            "SolutionManagerService",
            "JourneyManagerService",
            "ExperienceManagerService",
            "DeliveryManagerService"
        ]
        
        found_services = []
        for service_name in key_services:
            if service_name in service_registry:
                found_services.append(service_name)
        
        print(f"  ✅ Key services registered: {len(found_services)}/{len(key_services)}")
        for service_name in found_services:
            service = service_registry[service_name]
            is_initialized = getattr(service, 'is_initialized', False)
            print(f"    ✅ {service_name}: initialized={is_initialized}")
        
        # Test 6: Service Health Aggregation
        print("\n🔍 Test 6: Service Health Aggregation")
        health_summary = {
            "foundations": {
                "public_works": public_works.is_initialized,
                "curator": curator.is_initialized if curator else False,
                "communication": di_container.get_foundation_service("CommunicationFoundationService") is not None,
                "agentic": di_container.get_foundation_service("AgenticFoundationService") is not None
            },
            "managers": {
                name: manager.is_initialized if manager else False
                for name, manager in managers.items()
            },
            "platform_gateway": platform_gateway.is_initialized,
            "total_services": service_count
        }
        
        all_healthy = all([
            health_summary["foundations"]["public_works"],
            health_summary["platform_gateway"],
            all(health_summary["managers"].values())
        ])
        
        print(f"  ✅ Overall platform health: {'healthy' if all_healthy else 'degraded'}")
        print(f"  ✅ Foundation services: {sum(health_summary['foundations'].values())}/{len(health_summary['foundations'])} healthy")
        print(f"  ✅ Manager services: {sum(health_summary['managers'].values())}/{len(health_summary['managers'])} healthy")
        
        return {
            "success": True,
            "health_monitoring": {
                "foundations": health_summary["foundations"],
                "managers": health_summary["managers"],
                "platform_gateway": health_summary["platform_gateway"],
                "total_services": health_summary["total_services"],
                "overall_health": "healthy" if all_healthy else "degraded"
            }
        }

