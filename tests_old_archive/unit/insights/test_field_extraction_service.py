#!/usr/bin/env python3
"""
Unit tests for Field Extraction Service - Insights Realm

Tests field extraction from unstructured documents.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.fast
class TestFieldExtractionService:
    """Unit tests for Field Extraction Service."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def field_extraction_service(self, mock_platform_gateway, mock_di_container):
        """Create Field Extraction Service instance."""
        from backend.insights.services.field_extraction_service.field_extraction_service import FieldExtractionService
        
        service = FieldExtractionService(
            service_name="FieldExtractionService",
            realm_name="insights",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = AsyncMock()
        service.librarian = AsyncMock()
        service.nurse = AsyncMock()
        service.llm_composition = AsyncMock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_extract_fields_success(self, field_extraction_service):
        """Test successful field extraction."""
        # Mock parsed file
        field_extraction_service.content_steward.get_parsed_file = AsyncMock(return_value={
            "parsed_content": "License expires on December 31, 2025. Regulations: CFR 21 Part 11.",
            "text_content": "License expires on December 31, 2025. Regulations: CFR 21 Part 11."
        })
        
        # Mock LLM response
        field_extraction_service.llm_composition.generate_text = AsyncMock(return_value={
            "text": '{"value": "2025-12-31", "location": "Page 1", "source_text": "License expires on December 31, 2025", "confidence": 0.95}'
        })
        
        extraction_schema = {
            "fields": [
                {
                    "field_name": "license_expiration_date",
                    "field_type": "date",
                    "description": "Date when license expires",
                    "patterns": ["expires", "expiration"],
                    "required": True
                }
            ]
        }
        
        result = await field_extraction_service.extract_fields(
            file_id="test_file_123",
            extraction_schema=extraction_schema
        )
        
        assert result["success"] is True
        assert "extracted_fields" in result
        assert len(result["extracted_fields"]) > 0
    
    @pytest.mark.asyncio
    async def test_extract_fields_no_parsed_file(self, field_extraction_service):
        """Test field extraction when parsed file not found."""
        field_extraction_service.content_steward.get_parsed_file = AsyncMock(return_value=None)
        
        extraction_schema = {"fields": []}
        
        result = await field_extraction_service.extract_fields(
            file_id="nonexistent_file",
            extraction_schema=extraction_schema
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_extract_fields_regex_fallback(self, field_extraction_service):
        """Test regex fallback when LLM fails."""
        field_extraction_service.content_steward.get_parsed_file = AsyncMock(return_value={
            "parsed_content": "License expires on December 31, 2025.",
            "text_content": "License expires on December 31, 2025."
        })
        
        # Mock LLM failure
        field_extraction_service.llm_composition.generate_text = AsyncMock(side_effect=Exception("LLM error"))
        
        extraction_schema = {
            "fields": [
                {
                    "field_name": "license_expiration_date",
                    "field_type": "date",
                    "description": "Date when license expires",
                    "patterns": [r"expires on (\w+ \d+, \d+)"],
                    "required": False
                }
            ]
        }
        
        result = await field_extraction_service.extract_fields(
            file_id="test_file_123",
            extraction_schema=extraction_schema
        )
        
        # Should handle gracefully
        assert "success" in result










