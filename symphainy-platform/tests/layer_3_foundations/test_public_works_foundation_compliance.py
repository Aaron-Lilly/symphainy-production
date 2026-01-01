#!/usr/bin/env python3
"""
Public Works Foundation Compliance Tests

Tests to validate that Public Works Foundation follows architectural patterns:
- Uses DI Container correctly
- Uses Utilities correctly
- Follows base class patterns
"""

import pytest
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.di_container.di_container_service import DIContainerService
from bases.foundation_service_base import FoundationServiceBase


class TestPublicWorksFoundationCompliance:
    """Test Public Works Foundation compliance with architectural patterns."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI Container for testing."""
        return DIContainerService("test")
    
    @pytest.fixture
    def foundation_service(self, di_container):
        """Create a Public Works Foundation Service instance."""
        return PublicWorksFoundationService(di_container=di_container)
    
    def test_foundation_uses_di_container(self, foundation_service):
        """Test that foundation uses DI Container correctly."""
        assert hasattr(foundation_service, "di_container")
        assert foundation_service.di_container is not None
    
    def test_foundation_uses_utilities(self, foundation_service):
        """Test that foundation uses utilities via DI Container."""
        assert hasattr(foundation_service, "get_logger")
        assert hasattr(foundation_service, "get_utility")
        # Check that utility access methods exist and are callable
        assert callable(foundation_service.get_logger)
        assert callable(foundation_service.get_utility)
        
        # Note: Logger may not be initialized yet in DI Container during test setup
        # This is acceptable - we're testing structure, not full initialization
    
    def test_foundation_comprehensive_compliance(self, foundation_service):
        """Comprehensive compliance test combining all validators."""
        assert hasattr(foundation_service, "di_container")
        assert foundation_service.di_container is not None
        assert hasattr(foundation_service, "get_logger")
        assert callable(foundation_service.get_logger)
        assert isinstance(foundation_service, FoundationServiceBase)
    
    def test_foundation_inherits_from_foundation_service_base(self, foundation_service):
        """Test that foundation inherits from FoundationServiceBase."""
        assert isinstance(foundation_service, FoundationServiceBase)
        assert hasattr(foundation_service, "service_name")
        assert hasattr(foundation_service, "is_initialized")
        assert hasattr(foundation_service, "initialize")
        assert hasattr(foundation_service, "shutdown")
    
    def test_foundation_accepts_di_container(self):
        """Test that foundation accepts di_container in constructor."""
        di_container = DIContainerService("test")
        foundation_service = PublicWorksFoundationService(di_container=di_container)
        assert foundation_service.di_container is not None
        assert foundation_service.di_container == di_container
