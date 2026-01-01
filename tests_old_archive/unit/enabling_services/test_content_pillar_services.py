#!/usr/bin/env python3
"""
Unit Tests for Content Pillar Enabling Services

Smoke tests for Content Pillar enabling services including:
- FileParserService
- DataAnalyzerService  
- MetricsCalculatorService
- ValidationEngineService
- TransformationEngineService
- SchemaMapperService
- DataCompositorService
"""

import pytest

import os
from unittest.mock import Mock, AsyncMock

from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
from backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service import MetricsCalculatorService
from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
from backend.business_enablement.enabling_services.transformation_engine_service.transformation_engine_service import TransformationEngineService
from backend.business_enablement.enabling_services.schema_mapper_service.schema_mapper_service import SchemaMapperService
from backend.business_enablement.enabling_services.data_compositor_service.data_compositor_service import DataCompositorService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

class TestContentPillarServices:
    """Smoke tests for Content Pillar enabling services."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        return container
    
    async def test_file_parser_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test FileParserService initializes correctly."""
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "FileParserService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'parse_file')
    
    async def test_data_analyzer_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test DataAnalyzerService initializes correctly."""
        service = DataAnalyzerService(
            service_name="DataAnalyzerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "DataAnalyzerService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'analyze_data')
    
    async def test_metrics_calculator_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test MetricsCalculatorService initializes correctly."""
        service = MetricsCalculatorService(
            service_name="MetricsCalculatorService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "MetricsCalculatorService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully
    
    async def test_validation_engine_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test ValidationEngineService initializes correctly."""
        service = ValidationEngineService(
            service_name="ValidationEngineService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "ValidationEngineService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully
    
    async def test_transformation_engine_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test TransformationEngineService initializes correctly."""
        service = TransformationEngineService(
            service_name="TransformationEngineService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "TransformationEngineService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully
    
    async def test_schema_mapper_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test SchemaMapperService initializes correctly."""
        service = SchemaMapperService(
            service_name="SchemaMapperService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "SchemaMapperService"
        assert service.realm_name == "business_enablement"
        assert hasattr(service, 'map_schema')
    
    async def test_data_compositor_service_initialization(self, mock_platform_gateway, mock_di_container):
        """Test DataCompositorService initializes correctly."""
        service = DataCompositorService(
            service_name="DataCompositorService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        assert service.service_name == "DataCompositorService"
        assert service.realm_name == "business_enablement"
        # Service initialized successfully

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

