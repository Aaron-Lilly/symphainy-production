"""
Test Librarian Service - Smart City Role for Knowledge Management

Tests the Librarian service which handles knowledge discovery, metadata extraction,
semantic search, and knowledge analytics.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any

from backend.smart_city.services.librarian.librarian_service import LibrarianService
from foundations.utility_foundation.utilities.security.security_service import UserContext
from tests.unit.layer_7_smart_city_roles.test_base import SmartCityRolesTestBase


class TestLibrarianService(SmartCityRolesTestBase):
    """Test Librarian Service implementation."""
    
    @pytest.mark.asyncio
    async def test_librarian_service_initialization(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian service initialization."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test basic initialization
        self.assert_service_initialization(service, [
            'public_works_foundation', 'env_loader', 'config', 'api_config', 'feature_flags',
            'knowledge_management', 'search_engine', 'metadata_extraction',
            'knowledge_analytics', 'knowledge_recommendations'
        ])
        
        assert service.public_works_foundation == mock_public_works_foundation
        assert service.env_loader is not None
        assert service.config is not None
    
    @pytest.mark.asyncio
    async def test_librarian_service_initialization_async(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian service async initialization."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test async initialization
        await service.initialize()
        
        # Verify initialization completed
        assert hasattr(service, 'logger')
        assert service.logger is not None
    
    @pytest.mark.asyncio
    async def test_librarian_knowledge_management(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian knowledge management operations."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test basic initialization without calling initialize() to avoid infrastructure dependencies
        assert service.knowledge_management is not None
        assert service.search_engine is not None
        assert service.metadata_extraction is not None
        assert service.knowledge_analytics is not None
        assert service.knowledge_recommendations is not None
        
        # Test that service has the expected methods
        assert hasattr(service, 'search_knowledge')
        assert hasattr(service, 'index_knowledge')
        assert hasattr(service, 'get_knowledge_asset')
        assert hasattr(service, 'update_knowledge_asset')
        assert hasattr(service, 'delete_knowledge_asset')
    
    @pytest.mark.asyncio
    async def test_librarian_search_operations(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian search operations."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test that service has search capabilities
        assert hasattr(service, 'search_knowledge')
        assert hasattr(service, 'get_recommendations')
        
        # Test that search engine module is properly initialized
        assert service.search_engine is not None
        assert hasattr(service.search_engine, 'search')
        assert hasattr(service.search_engine, 'update_search_index')
    
    @pytest.mark.asyncio
    async def test_librarian_metadata_extraction(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian metadata extraction operations."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test that service has metadata extraction capabilities
        assert hasattr(service, 'extract_metadata')
        assert hasattr(service, 'assess_quality')
        
        # Test that metadata extraction module is properly initialized
        assert service.metadata_extraction is not None
        assert hasattr(service.metadata_extraction, 'extract_metadata')
        assert hasattr(service.metadata_extraction, 'get_status')
    
    @pytest.mark.asyncio
    async def test_librarian_knowledge_analytics(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian knowledge analytics."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test that service has analytics capabilities
        assert hasattr(service, 'assess_quality')
        assert hasattr(service, 'get_recommendations')
        
        # Test that analytics modules are properly initialized
        assert service.knowledge_analytics is not None
        assert service.knowledge_recommendations is not None
        assert hasattr(service.knowledge_analytics, 'get_asset_analytics')
        assert hasattr(service.knowledge_recommendations, 'get_content_recommendations')
    
    @pytest.mark.asyncio
    async def test_librarian_health_check(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian health check (inherited from SOAServiceBase)."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test health check (inherited from SOAServiceBase)
        health_result = await service.get_service_health()
        self.assert_health_check(health_result)
        
        # Verify service name
        assert health_result["service"] == "LibrarianService"
    
    @pytest.mark.asyncio
    async def test_librarian_error_handling(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Librarian error handling."""
        service = LibrarianService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test that service has proper error handling capabilities
        assert hasattr(service, 'get_knowledge_asset')
        assert hasattr(service, 'search_knowledge')
        
        # Test that error handling is properly set up through the foundation
        assert service.utility_foundation is not None
        assert hasattr(service.utility_foundation, 'error_handler')
