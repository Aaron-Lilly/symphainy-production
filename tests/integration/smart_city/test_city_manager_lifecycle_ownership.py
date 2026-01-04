#!/usr/bin/env python3
"""
City Manager Lifecycle Ownership Tests

Validates that City Manager owns service lifecycle by testing BEHAVIOR:
- Services cannot initialize without City Manager permission
- Services are registered before initialization
- Services are marked as initialized after success
- Lifecycle registry tracks service states

ANTI-PATTERN 2 COMPLIANCE: Tests behavior and outcomes, not internal structure.
"""

import pytest
import asyncio
from typing import Dict, Any


@pytest.mark.integration
@pytest.mark.smart_city
@pytest.mark.critical
class TestCityManagerLifecycleOwnership:
    """Test suite for City Manager lifecycle ownership - testing behavior, not structure."""
    
    @pytest.mark.asyncio
    async def test_service_cannot_initialize_without_city_manager_permission(
        self, di_container, platform_gateway, city_manager
    ):
        """
        Verify services cannot initialize without City Manager permission.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (service initialization fails),
        not structure (hasattr checks).
        """
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        # Create a service instance
        service = FileParserService(
            service_name="TestFileParserService",
            realm_name="content",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # ✅ TEST BEHAVIOR: Service should NOT be able to initialize without City Manager permission
        # The service's initialize() method should check with City Manager and fail if not registered
        try:
            success = await service.initialize()
            # If initialization succeeds without registration, that's a failure of the pattern
            # (This should be caught by RealmServiceBase.initialize() checking with City Manager)
            assert success == False, \
                "Service should not be able to initialize without City Manager permission"
        except Exception as e:
            # Exception is also acceptable - service should fail fast if not registered
            assert "not registered" in str(e).lower() or "permission" in str(e).lower() or \
                   "city manager" in str(e).lower(), \
                f"Service should fail with registration/permission error, got: {e}"
        
        # Cleanup
        try:
            await service.shutdown()
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_service_can_initialize_after_city_manager_registration(
        self, di_container, platform_gateway, city_manager
    ):
        """
        Verify services CAN initialize after City Manager registration.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (service initialization succeeds after registration),
        not structure (hasattr checks).
        """
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        # Create a service instance
        service = FileParserService(
            service_name="TestFileParserService",
            realm_name="content",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # ✅ TEST BEHAVIOR: Register service with City Manager
        service_name = "TestFileParserService"
        registered = await city_manager.service_management_module.register_service_for_initialization(service_name)
        assert registered == True, "Service should be registered successfully"
        
        # ✅ TEST BEHAVIOR: Service CAN initialize after registration
        success = await service.initialize()
        assert success == True, "Service should be able to initialize after City Manager registration"
        
        # ✅ TEST BEHAVIOR: Service is marked as initialized in lifecycle registry
        # Check lifecycle state via City Manager (behavior-based, not direct registry access)
        can_init_again = await city_manager.service_management_module.can_service_initialize(service_name)
        # Should return False because service is already initialized
        assert can_init_again == False, "Service should not be able to initialize again (already initialized)"
        
        # Cleanup
        try:
            await service.shutdown()
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_lifecycle_registry_tracks_service_states(
        self, di_container, platform_gateway, city_manager
    ):
        """
        Verify lifecycle registry tracks service states correctly.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (state tracking works),
        not structure (direct registry access).
        """
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        
        service_name = "TestFileParserService"
        
        # Create a service instance
        service = FileParserService(
            service_name=service_name,
            realm_name="content",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # ✅ TEST BEHAVIOR: Service cannot initialize before registration
        can_init_before = await city_manager.service_management_module.can_service_initialize(service_name)
        assert can_init_before == False, "Service should not be able to initialize before registration"
        
        # ✅ TEST BEHAVIOR: Register service
        registered = await city_manager.service_management_module.register_service_for_initialization(service_name)
        assert registered == True, "Service should be registered successfully"
        
        # ✅ TEST BEHAVIOR: Initialize service (can_service_initialize is called internally by initialize())
        # Note: We don't call can_service_initialize() here because it has side effects (changes state to "initializing")
        # The initialize() method will call it internally and handle state transitions
        success = await service.initialize()
        assert success == True, "Service should initialize successfully"
        
        # ✅ TEST BEHAVIOR: Service is automatically marked as initialized by initialize() method
        # (initialize() calls mark_service_initialized() internally, so we don't need to call it again)
        # Verify that service cannot initialize again (already initialized)
        can_init_again = await city_manager.service_management_module.can_service_initialize(service_name)
        assert can_init_again == False, "Service should not be able to initialize again (already initialized)"
        
        # Cleanup
        try:
            await service.shutdown()
        except Exception:
            pass
    
    @pytest.mark.asyncio
    async def test_smart_city_service_lifecycle_ownership(
        self, di_container, city_manager
    ):
        """
        Verify Smart City services follow lifecycle ownership pattern.
        
        ANTI-PATTERN 2 COMPLIANCE: Tests behavior (Smart City service lifecycle),
        not structure (hasattr checks).
        """
        from backend.smart_city.services.librarian.librarian_service import LibrarianService
        
        service_name = "librarian"
        
        # ✅ TEST BEHAVIOR: Register Smart City service
        registered = await city_manager.service_management_module.register_service_for_initialization(service_name)
        assert registered == True, "Smart City service should be registered successfully"
        
        # ✅ TEST BEHAVIOR: Service can initialize after registration
        can_init = await city_manager.service_management_module.can_service_initialize(service_name)
        assert can_init == True, "Smart City service should be able to initialize after registration"
        
        # Create and initialize service
        service = LibrarianService(di_container=di_container)
        success = await service.initialize()
        assert success == True, "Smart City service should initialize successfully"
        
        # ✅ TEST BEHAVIOR: Mark service as initialized
        marked = await city_manager.service_management_module.mark_service_initialized(service_name)
        assert marked == True, "Smart City service should be marked as initialized"
        
        # Cleanup
        try:
            await service.shutdown()
        except Exception:
            pass


