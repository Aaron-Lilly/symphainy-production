#!/usr/bin/env python3
"""
ContentSchemaAbstraction Tests

Tests for ContentSchemaAbstraction in isolation.
Verifies abstraction works correctly and realms can access it via Platform Gateway.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestContentSchemaAbstraction:
    """Test ContentSchemaAbstraction functionality."""
    
    @pytest.fixture
    def mock_arango_adapter(self):
        """Mock ArangoDB adapter."""
        adapter = MagicMock()
        adapter.create_content_schema = AsyncMock(return_value={"_key": "schema_123"})
        adapter.get_content_schema = AsyncMock(return_value={"schema_id": "schema_123"})
        return adapter
    
    @pytest.fixture
    def mock_config_adapter(self):
        """Mock config adapter."""
        return MagicMock()
    
    @pytest.fixture
    def abstraction(self, mock_arango_adapter, mock_config_adapter):
        """Create ContentSchemaAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.content_schema_abstraction import ContentSchemaAbstraction
        
        abstraction = ContentSchemaAbstraction(
            arango_adapter=mock_arango_adapter,
            config_adapter=mock_config_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_arango_adapter, mock_config_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.content_schema_abstraction import ContentSchemaAbstraction
        
        abstraction = ContentSchemaAbstraction(
            arango_adapter=mock_arango_adapter,
            config_adapter=mock_config_adapter
        )
        assert abstraction.arango_adapter == mock_arango_adapter
        assert abstraction.config_adapter == mock_config_adapter
    
    @pytest.mark.asyncio
    async def test_extract_content_schema(self, abstraction, mock_arango_adapter):
        """Test abstraction can extract content schema."""
        # Mock the internal helper method
        abstraction._extract_schema_from_content = AsyncMock(return_value={
            "schema_type": "json",
            "fields": ["field1", "field2"]
        })
        
        result = await abstraction.extract_content_schema("content_123")
        assert result is not None
        assert "schema_type" in result
        mock_arango_adapter.create_content_schema.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_schema_structure(self, abstraction):
        """Test abstraction can analyze schema structure."""
        # Mock the internal helper methods
        abstraction._analyze_schema_patterns = AsyncMock(return_value={"pattern": "structured"})
        abstraction._identify_schema_relationships = AsyncMock(return_value={"relationships": []})
        abstraction._generate_schema_insights = AsyncMock(return_value={"insights": []})
        
        result = await abstraction.analyze_schema_structure({"schema_type": "json"})
        assert result is not None
        assert "structure_analysis" in result

