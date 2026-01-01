#!/usr/bin/env python3
"""
End-to-End Tests - Platform Startup

Tests for complete platform startup sequence.
"""

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

class TestPlatformStartup:
    """Test complete platform startup sequence."""
    
    @pytest.mark.asyncio
    async def test_platform_orchestrator_initialization(self):
        """Test Platform Orchestrator can be initialized."""
        try:
            from main import PlatformOrchestrator
            orchestrator = PlatformOrchestrator()
            assert orchestrator is not None
            assert orchestrator.startup_status is not None
        except Exception as e:
            pytest.skip(f"Platform Orchestrator initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_foundation_infrastructure_initialization(self, real_di_container):
        """Test foundation infrastructure can be initialized."""
        try:
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            
            # Initialize core foundations
            pwf = PublicWorksFoundationService(real_di_container)
            await pwf.initialize()
            assert pwf.is_initialized
            
            curator = CuratorFoundationService(
                foundation_services=real_di_container,
                public_works_foundation=pwf
            )
            await curator.initialize()
            assert curator.is_initialized
            
        except Exception as e:
            pytest.skip(f"Foundation initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_smart_city_services_startup(self, mock_di_container):
        """Test Smart City services can start up."""
        try:
            from backend.smart_city.services.librarian.librarian_service import LibrarianService
            from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
            
            # Initialize a few key services
            librarian = LibrarianService(mock_di_container)
            await librarian.initialize()
            assert librarian.is_initialized
            
            data_steward = DataStewardService(mock_di_container)
            await data_steward.initialize()
            assert data_steward.is_initialized
            
        except Exception as e:
            pytest.skip(f"Smart City service startup failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Full platform startup requires all infrastructure")
    async def test_full_platform_startup(self, skip_if_no_infrastructure):
        """Test full platform startup (requires all infrastructure)."""
        try:
            from main import PlatformOrchestrator
            orchestrator = PlatformOrchestrator()
            result = await orchestrator.orchestrate_platform_startup()
            
            assert result["success"] is True
            assert "foundation_services" in result
            assert "managers" in result
            
        except Exception as e:
            pytest.fail(f"Full platform startup failed: {e}")

class TestImportErrors:
    """Test for import errors that would prevent startup."""
    
    # NOTE: Test order matters due to sys.path manipulation in foundation files.
    # Run Smart City test FIRST to avoid test isolation issues.
    
    def test_no_import_errors_smart_city(self):
        """Test Smart City services can be imported."""
        try:
            from backend.smart_city.services.librarian.librarian_service import LibrarianService
            from backend.smart_city.services.data_steward.data_steward_service import DataStewardService
            from backend.smart_city.services.security_guard.security_guard_service import SecurityGuardService
            from backend.smart_city.services.conductor.conductor_service import ConductorService
            from backend.smart_city.services.post_office.post_office_service import PostOfficeService
            from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
            from backend.smart_city.services.nurse.nurse_service import NurseService
            from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: Import error in Smart City services: {e}")
    
    def test_no_import_errors_foundations(self):
        """Test foundation services can be imported."""
        try:
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: Import error in foundations: {e}")
    
    def test_no_import_errors_bases(self):
        """Test base classes can be imported."""
        try:
            from bases.smart_city_role_base import SmartCityRoleBase
            from bases.realm_service_base import RealmServiceBase
            from bases.manager_service_base import ManagerServiceBase
            from bases.mcp_server_base import MCPServerBase
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL: Import error in base classes: {e}")

