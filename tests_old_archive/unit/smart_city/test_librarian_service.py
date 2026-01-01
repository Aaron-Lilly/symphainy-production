#!/usr/bin/env python3
"""
Unit Tests - Librarian Service

Tests for Librarian Service (Smart City role).
"""

import pytest
from unittest.mock import Mock, AsyncMock

pytestmark = [pytest.mark.unit, pytest.mark.smart_city]

class TestLibrarianService:
    """Test Librarian Service functionality."""
    
    @pytest.mark.asyncio
    async def test_librarian_initialization(self, librarian_service):
        """Test Librarian Service can be initialized."""
        assert librarian_service is not None
        assert librarian_service.service_name == "LibrarianService"
        assert librarian_service.role_name == "librarian"
        assert librarian_service.is_initialized
    
    @pytest.mark.asyncio
    async def test_librarian_uses_smart_city_role_base(self, librarian_service):
        """Test Librarian uses SmartCityRoleBase."""
        from bases.smart_city_role_base import SmartCityRoleBase
        assert isinstance(librarian_service, SmartCityRoleBase)
    
    @pytest.mark.asyncio
    async def test_librarian_has_soa_apis(self, librarian_service):
        """Test Librarian exposes SOA APIs."""
        assert hasattr(librarian_service, 'soa_apis')
        assert isinstance(librarian_service.soa_apis, dict)
    
    @pytest.mark.asyncio
    async def test_librarian_has_mcp_tools(self, librarian_service):
        """Test Librarian exposes MCP tools."""
        assert hasattr(librarian_service, 'mcp_tools')
        assert isinstance(librarian_service.mcp_tools, dict)
    
    @pytest.mark.asyncio
    async def test_librarian_has_knowledge_management(self, librarian_service):
        """Test Librarian has knowledge management methods."""
        assert hasattr(librarian_service, 'store_knowledge')
        assert hasattr(librarian_service, 'get_knowledge_item')
        assert hasattr(librarian_service, 'search_knowledge')
    
    @pytest.mark.asyncio
    async def test_librarian_store_knowledge(self, librarian_service, sample_knowledge_item):
        """Test Librarian can store knowledge."""
        try:
            result = await librarian_service.store_knowledge(sample_knowledge_item)
            assert result is not None
        except NotImplementedError:
            pytest.skip("store_knowledge not fully implemented yet")
    
    @pytest.mark.asyncio
    async def test_librarian_search(self, librarian_service):
        """Test Librarian search functionality."""
        try:
            result = await librarian_service.search_knowledge("test query")
            assert result is not None
        except NotImplementedError:
            pytest.skip("search_knowledge not fully implemented yet")
    
    @pytest.mark.asyncio
    async def test_librarian_shutdown(self, librarian_service):
        """Test Librarian can shutdown gracefully."""
        result = await librarian_service.shutdown()
        assert result is True

class TestLibrarianServiceProtocol:
    """Test Librarian Service implements protocol correctly."""
    
    @pytest.mark.asyncio
    async def test_librarian_implements_protocol(self, librarian_service):
        """Test Librarian implements LibrarianServiceProtocol."""
        from backend.smart_city.protocols.librarian_service_protocol import LibrarianServiceProtocol
        assert isinstance(librarian_service, LibrarianServiceProtocol)
    
    @pytest.mark.asyncio
    async def test_librarian_has_required_methods(self, librarian_service):
        """Test Librarian has all required protocol methods."""
        required_methods = [
            'initialize',
            'shutdown',
            'store_knowledge',
            'get_knowledge_item',
            'search_knowledge'
        ]
        
        for method in required_methods:
            assert hasattr(librarian_service, method), f"Missing method: {method}"

