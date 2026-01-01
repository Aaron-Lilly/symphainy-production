#!/usr/bin/env python3
"""
Data Analyzer Service Functionality Tests

Tests Data Analyzer Service core functionality:
- Data analysis (descriptive, predictive, diagnostic)
- Pattern detection
- Statistical analysis
- Entity extraction

Uses mock AI responses and test datasets.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

from tests.fixtures.test_datasets import get_sample_json_data

@pytest.mark.business_enablement
@pytest.mark.functional
class TestDataAnalyzerServiceFunctionality:
    """Test Data Analyzer Service functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_librarian(self):
        """Create mock Librarian API."""
        mock_api = Mock()
        mock_api.get_knowledge = AsyncMock(return_value={"data": get_sample_json_data()})
        return mock_api
    
    @pytest.fixture
    async def data_analyzer_service(self, mock_di_container, mock_platform_gateway, mock_librarian):
        """Create Data Analyzer Service instance."""
        # project_root is set at module level and already added to sys.path
        # Just ensure it's still there (pytest might reset sys.path)
        from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
        
        service = DataAnalyzerService(
            service_name="DataAnalyzerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City APIs - need to mock methods used by RealmServiceBase
        mock_librarian.get_knowledge = AsyncMock(return_value={"data": get_sample_json_data()})
        mock_data_steward = Mock()
        mock_data_steward.validate_data_quality = AsyncMock(return_value=True)
        mock_data_steward.track_data_lineage = AsyncMock(return_value=True)
        
        service.librarian = mock_librarian
        service.data_steward = mock_data_steward
        service.content_steward = Mock()
        service.analytics = Mock()
        
        # Mock RealmServiceBase methods
        service.retrieve_document = AsyncMock(return_value={"data": get_sample_json_data(), "metadata": {}})
        service.store_document = AsyncMock(return_value={"document_id": "test_doc_001"})
        service.validate_data_quality = AsyncMock(return_value=True)
        service.track_data_lineage = AsyncMock(return_value=True)
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_analyze_data(self, data_analyzer_service):
        """Test data analysis functionality."""
        data_id = "test_data_001"
        
        result = await data_analyzer_service.analyze_data(
            data_id=data_id,
            analysis_type="descriptive"
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "analysis" in result
    
    @pytest.mark.asyncio
    async def test_analyze_structure(self, data_analyzer_service):
        """Test data structure analysis."""
        data_id = "test_data_001"
        
        result = await data_analyzer_service.analyze_structure(data_id)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_detect_patterns(self, data_analyzer_service):
        """Test pattern detection."""
        data_id = "test_data_001"
        
        result = await data_analyzer_service.detect_patterns(
            data_id=data_id,
            pattern_type="trend"
        )
        
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, data_analyzer_service):
        """Test statistical analysis."""
        data_id = "test_data_001"
        
        result = await data_analyzer_service.get_statistics(data_id)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_extract_entities(self, data_analyzer_service):
        """Test entity extraction."""
        data_id = "test_data_001"
        
        result = await data_analyzer_service.extract_entities(data_id)
        
        assert result is not None
        assert isinstance(result, dict)

