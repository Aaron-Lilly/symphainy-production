#!/usr/bin/env python3
"""
Smart City Realm Outputs Tests

Tests to validate that Smart City services expose their outputs correctly:
- SOA APIs are registered and accessible
- MCP Tools are registered and accessible
- Service methods are callable
- Infrastructure abstractions are accessible
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, MagicMock, patch
from foundations.di_container.di_container_service import DIContainerService
from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
from backend.smart_city.services.librarian.librarian_service import LibrarianService
from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService


class TestSmartCityOutputs:
    """Test Smart City services outputs accessibility."""
    
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
    
    def test_city_manager_has_soa_apis(self, city_manager):
        """Test that City Manager has SOA APIs structure."""
        assert hasattr(city_manager, "soa_apis")
        assert isinstance(city_manager.soa_apis, dict)
    
    def test_city_manager_has_mcp_tools(self, city_manager):
        """Test that City Manager has MCP Tools structure."""
        assert hasattr(city_manager, "mcp_tools")
        assert isinstance(city_manager.mcp_tools, dict)
    
    def test_city_manager_has_orchestration_methods(self, city_manager):
        """Test that City Manager has orchestration methods."""
        # Check for key orchestration methods
        assert hasattr(city_manager, "initialize")
        assert callable(city_manager.initialize)
    
    def test_librarian_has_soa_apis(self, librarian):
        """Test that Librarian has SOA APIs structure."""
        assert hasattr(librarian, "soa_apis")
        assert isinstance(librarian.soa_apis, dict)
    
    def test_librarian_has_mcp_tools(self, librarian):
        """Test that Librarian has MCP Tools structure."""
        assert hasattr(librarian, "mcp_tools")
        assert isinstance(librarian.mcp_tools, dict)
    
    def test_librarian_has_knowledge_methods(self, librarian):
        """Test that Librarian has knowledge management methods."""
        # Check for key knowledge management methods
        assert hasattr(librarian, "initialize")
        assert callable(librarian.initialize)
    
    def test_content_steward_has_soa_apis(self, content_steward):
        """Test that Content Steward has SOA APIs structure."""
        assert hasattr(content_steward, "soa_apis")
        assert isinstance(content_steward.soa_apis, dict)
    
    def test_content_steward_has_mcp_tools(self, content_steward):
        """Test that Content Steward has MCP Tools structure."""
        assert hasattr(content_steward, "mcp_tools")
        assert isinstance(content_steward.mcp_tools, dict)
    
    def test_content_steward_has_content_methods(self, content_steward):
        """Test that Content Steward has content processing methods."""
        # Check for key content processing methods
        assert hasattr(content_steward, "initialize")
        assert callable(content_steward.initialize)
    
    def test_smart_city_services_have_infrastructure_access(self, city_manager, librarian, content_steward):
        """Test that Smart City services have infrastructure access methods."""
        services = [city_manager, librarian, content_steward]
        
        for service in services:
            # All Smart City services should have infrastructure access
            assert hasattr(service, "get_infrastructure_abstraction")
            assert callable(service.get_infrastructure_abstraction)
    
    def test_smart_city_services_have_utility_access(self, city_manager, librarian, content_steward):
        """Test that Smart City services have utility access methods."""
        services = [city_manager, librarian, content_steward]
        
        for service in services:
            # All Smart City services should have utility access
            assert hasattr(service, "get_logger")
            assert hasattr(service, "get_utility")
            assert callable(service.get_logger)
            assert callable(service.get_utility)
    
    def test_smart_city_services_have_micro_modules(self, city_manager, librarian, content_steward):
        """Test that Smart City services have micro-modules initialized."""
        services = [city_manager, librarian, content_steward]
        
        for service in services:
            # All Smart City services should have micro-modules
            assert hasattr(service, "initialization_module")
            assert hasattr(service, "soa_mcp_module")
            assert hasattr(service, "utilities_module")

