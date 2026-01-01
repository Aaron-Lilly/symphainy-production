#!/usr/bin/env python3
"""
Smart City Realm Compliance Tests

Tests to validate that Smart City services follow architectural patterns:
- Uses DI Container correctly
- Uses Utilities correctly
- Uses Foundations correctly (direct Public Works and Communications access allowed)
- Follows SmartCityRoleBase patterns
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, MagicMock, patch
from foundations.di_container.di_container_service import DIContainerService
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
from backend.smart_city.services.librarian.librarian_service import LibrarianService
from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
from backend.smart_city.services.data_steward.data_steward_service import DataStewardService


class TestSmartCityCompliance:
    """Test Smart City services compliance with architectural patterns."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI Container for testing."""
        container = DIContainerService("test")
        # DI Container initializes utilities in __init__
        return container
    
    @pytest.fixture
    def city_manager(self, di_container):
        """Create a City Manager Service instance."""
        return CityManagerService(di_container=di_container)
    
    @pytest.fixture
    def librarian(self, di_container):
        """Create a Librarian Service instance."""
        return LibrarianService(di_container=di_container)
    
    @pytest.fixture
    def content_steward(self, di_container):
        """Create a Content Steward Service instance."""
        return ContentStewardService(di_container=di_container)
    
    def test_city_manager_uses_di_container(self, city_manager):
        """Test that City Manager uses DI Container correctly."""
        assert hasattr(city_manager, "di_container")
        assert city_manager.di_container is not None
    
    def test_city_manager_inherits_from_smart_city_role_base(self, city_manager):
        """Test that City Manager inherits from SmartCityRoleBase."""
        assert isinstance(city_manager, SmartCityRoleBase)
        assert hasattr(city_manager, "service_name")
        assert hasattr(city_manager, "role_name")
        assert city_manager.role_name == "city_manager"
    
    def test_city_manager_has_utility_access(self, city_manager):
        """Test that City Manager has utility access methods."""
        assert hasattr(city_manager, "get_logger")
        assert hasattr(city_manager, "get_utility")
        assert callable(city_manager.get_logger)
        assert callable(city_manager.get_utility)
    
    def test_city_manager_has_foundation_access(self, city_manager):
        """Test that City Manager has foundation access methods."""
        assert hasattr(city_manager, "get_infrastructure_abstraction")
        assert callable(city_manager.get_infrastructure_abstraction)
    
    def test_librarian_uses_di_container(self, librarian):
        """Test that Librarian uses DI Container correctly."""
        assert hasattr(librarian, "di_container")
        assert librarian.di_container is not None
    
    def test_librarian_inherits_from_smart_city_role_base(self, librarian):
        """Test that Librarian inherits from SmartCityRoleBase."""
        assert isinstance(librarian, SmartCityRoleBase)
        assert hasattr(librarian, "service_name")
        assert hasattr(librarian, "role_name")
        assert librarian.role_name == "librarian"
    
    def test_librarian_has_utility_access(self, librarian):
        """Test that Librarian has utility access methods."""
        assert hasattr(librarian, "get_logger")
        assert hasattr(librarian, "get_utility")
        assert callable(librarian.get_logger)
        assert callable(librarian.get_utility)
    
    def test_librarian_has_foundation_access(self, librarian):
        """Test that Librarian has foundation access methods."""
        assert hasattr(librarian, "get_infrastructure_abstraction")
        assert callable(librarian.get_infrastructure_abstraction)
    
    def test_content_steward_uses_di_container(self, content_steward):
        """Test that Content Steward uses DI Container correctly."""
        assert hasattr(content_steward, "di_container")
        assert content_steward.di_container is not None
    
    def test_content_steward_inherits_from_smart_city_role_base(self, content_steward):
        """Test that Content Steward inherits from SmartCityRoleBase."""
        assert isinstance(content_steward, SmartCityRoleBase)
        assert hasattr(content_steward, "service_name")
        assert hasattr(content_steward, "role_name")
        assert content_steward.role_name == "content_steward"
    
    def test_content_steward_has_utility_access(self, content_steward):
        """Test that Content Steward has utility access methods."""
        assert hasattr(content_steward, "get_logger")
        assert hasattr(content_steward, "get_utility")
        assert callable(content_steward.get_logger)
        assert callable(content_steward.get_utility)
    
    def test_content_steward_has_foundation_access(self, content_steward):
        """Test that Content Steward has foundation access methods."""
        assert hasattr(content_steward, "get_infrastructure_abstraction")
        assert callable(content_steward.get_infrastructure_abstraction)
    
    def test_smart_city_services_accept_di_container(self, di_container):
        """Test that all Smart City services accept di_container in constructor."""
        city_manager = CityManagerService(di_container=di_container)
        librarian = LibrarianService(di_container=di_container)
        content_steward = ContentStewardService(di_container=di_container)
        
        assert city_manager.di_container == di_container
        assert librarian.di_container == di_container
        assert content_steward.di_container == di_container
    
    def test_smart_city_services_comprehensive_compliance(self, city_manager, librarian, content_steward):
        """Comprehensive compliance test for all Smart City services."""
        services = [city_manager, librarian, content_steward]
        
        for service in services:
            # DI Container compliance
            assert hasattr(service, "di_container")
            assert service.di_container is not None
            
            # Base class compliance
            assert isinstance(service, SmartCityRoleBase)
            assert hasattr(service, "service_name")
            assert hasattr(service, "role_name")
            
            # Utility access compliance
            assert hasattr(service, "get_logger")
            assert hasattr(service, "get_utility")
            assert callable(service.get_logger)
            assert callable(service.get_utility)
            
            # Foundation access compliance
            assert hasattr(service, "get_infrastructure_abstraction")
            assert callable(service.get_infrastructure_abstraction)
    
    def test_smart_city_services_base_class_verification(self, city_manager, librarian, content_steward):
        """Verify that Smart City services properly inherit from SmartCityRoleBase."""
        services = [city_manager, librarian, content_steward]
        
        for service in services:
            # Verify inheritance
            assert isinstance(service, SmartCityRoleBase)
            
            # Verify base class attributes
            assert hasattr(service, "service_name")
            assert hasattr(service, "role_name")
            assert hasattr(service, "di_container")
            
            # Verify base class methods from SmartCityRoleBase
            assert hasattr(service, "get_logger")
            assert hasattr(service, "get_utility")
            assert hasattr(service, "get_infrastructure_abstraction")
            
            # Verify service_name and role_name are set correctly
            assert service.service_name is not None
            assert service.role_name is not None
            assert isinstance(service.service_name, str)
            assert isinstance(service.role_name, str)

