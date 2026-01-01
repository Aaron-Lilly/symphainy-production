"""
Test All Smart City Services Initialization - Layer 3

Validates that ALL Smart City services can be initialized and access abstractions.
This catches missing dependencies, configuration issues, and initialization problems at Layer 3.

Layer 3 tests ensure Smart City services are properly created and can access
abstractions from Layer 2 before we test their actual functionality in higher layers.
"""

import pytest
import os

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

from foundations.di_container.di_container_service import DIContainerService
from backend.smart_city.services import (
    CityManagerService,
    SecurityGuardService,
    TrafficCopService,
    NurseService,
    LibrarianService,
    ConductorService,
    PostOfficeService,
    ContentStewardService,
    DataStewardService
)

@pytest.mark.integration
@pytest.mark.infrastructure
class TestAllSmartCityServicesInitialization:
    """Test all Smart City services can be initialized."""
    
    @pytest.fixture
    def di_container(self):
        """Create DI container for Smart City services."""
        container = DIContainerService("smart_city")
        yield container
    
    def test_city_manager_service_initialized(self, di_container):
        """Test CityManagerService can be initialized."""
        service = CityManagerService(di_container=di_container)
        assert service is not None, "CityManagerService should be initialized"
        assert hasattr(service, 'di_container'), "CityManagerService should have di_container"
    
    def test_security_guard_service_initialized(self, di_container):
        """Test SecurityGuardService can be initialized."""
        service = SecurityGuardService(di_container=di_container)
        assert service is not None, "SecurityGuardService should be initialized"
        assert hasattr(service, 'di_container'), "SecurityGuardService should have di_container"
    
    def test_traffic_cop_service_initialized(self, di_container):
        """Test TrafficCopService can be initialized."""
        service = TrafficCopService(di_container=di_container)
        assert service is not None, "TrafficCopService should be initialized"
        assert hasattr(service, 'di_container'), "TrafficCopService should have di_container"
    
    def test_nurse_service_initialized(self, di_container):
        """Test NurseService can be initialized."""
        service = NurseService(di_container=di_container)
        assert service is not None, "NurseService should be initialized"
        assert hasattr(service, 'di_container'), "NurseService should have di_container"
    
    def test_librarian_service_initialized(self, di_container):
        """Test LibrarianService can be initialized."""
        service = LibrarianService(di_container=di_container)
        assert service is not None, "LibrarianService should be initialized"
        assert hasattr(service, 'di_container'), "LibrarianService should have di_container"
    
    def test_conductor_service_initialized(self, di_container):
        """Test ConductorService can be initialized."""
        service = ConductorService(di_container=di_container)
        assert service is not None, "ConductorService should be initialized"
        assert hasattr(service, 'di_container'), "ConductorService should have di_container"
    
    def test_post_office_service_initialized(self, di_container):
        """Test PostOfficeService can be initialized."""
        service = PostOfficeService(di_container=di_container)
        assert service is not None, "PostOfficeService should be initialized"
        assert hasattr(service, 'di_container'), "PostOfficeService should have di_container"
    
    def test_content_steward_service_initialized(self, di_container):
        """Test ContentStewardService can be initialized."""
        service = ContentStewardService(di_container=di_container)
        assert service is not None, "ContentStewardService should be initialized"
        assert hasattr(service, 'di_container'), "ContentStewardService should have di_container"
    
    def test_data_steward_service_initialized(self, di_container):
        """Test DataStewardService can be initialized."""
        service = DataStewardService(di_container=di_container)
        assert service is not None, "DataStewardService should be initialized"
        assert hasattr(service, 'di_container'), "DataStewardService should have di_container"
    
    def test_all_services_have_abstraction_access(self, di_container):
        """Test all services can access abstractions via SmartCityRoleBase methods."""
        services = [
            CityManagerService(di_container=di_container),
            SecurityGuardService(di_container=di_container),
            TrafficCopService(di_container=di_container),
            NurseService(di_container=di_container),
            LibrarianService(di_container=di_container),
            ConductorService(di_container=di_container),
            PostOfficeService(di_container=di_container),
            ContentStewardService(di_container=di_container),
            DataStewardService(di_container=di_container)
        ]
        
        for service in services:
            # All Smart City services use get_foundation_abstraction() and get_infrastructure_abstraction()
            assert hasattr(service, 'get_foundation_abstraction'), \
                f"{service.__class__.__name__} should have get_foundation_abstraction method"
            assert hasattr(service, 'get_infrastructure_abstraction'), \
                f"{service.__class__.__name__} should have get_infrastructure_abstraction method"
