#!/usr/bin/env python3
"""
ExportFormatter Functionality Tests

Tests ExportFormatter core functionality.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock

    # Fallback: calculate from this file's location
@pytest.mark.business_enablement
@pytest.mark.functional
class TestExportFormatterServiceFunctionality:
    """Test ExportFormatter functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    async def export_formatter_service(self, mock_di_container, mock_platform_gateway):

        # Ensure correct path

        # Ensure correct path
        # Ensure path is set - convert to absolute for comparison
        # Path is already set at module level, but ensure it's in sys.path
        # project_root is already absolute, just ensure it's added
        from backend.business_enablement.enabling_services.export_formatter_service.export_formatter_service import ExportFormatterService
        
        service = ExportFormatterService(
            service_name="ExportFormatterService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        service.librarian = Mock()
        service.data_steward = Mock()
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_service_operation(self, export_formatter_service):
        """Test service core operation."""
        # TODO: Add specific test based on service capabilities
        assert export_formatter_service is not None
        assert hasattr(export_formatter_service, 'di_container')
