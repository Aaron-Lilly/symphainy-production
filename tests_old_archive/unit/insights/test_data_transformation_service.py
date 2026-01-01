#!/usr/bin/env python3
"""
Unit tests for Data Transformation Service - Insights Realm

Tests data transformation and output file generation.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.fast
class TestDataTransformationService:
    """Unit tests for Data Transformation Service."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def data_transformation_service(self, mock_platform_gateway, mock_di_container):
        """Create Data Transformation Service instance."""
        from backend.insights.services.data_transformation_service.data_transformation_service import DataTransformationService
        
        service = DataTransformationService(
            service_name="DataTransformationService",
            realm_name="insights",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = AsyncMock()
        service.file_management = AsyncMock()
        service.nurse = AsyncMock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_transform_data_structured_records(self, data_transformation_service):
        """Test transformation of structured records."""
        source_data = {
            "records": [
                {
                    "record_id": "record_1",
                    "POLICY-NUMBER": "POL-001",
                    "PREMIUM-AMOUNT": "1000.50",
                    "ISSUE-DATE": "2024-01-15"
                }
            ]
        }
        
        mapping_rules = [
            {
                "source_field": "POLICY-NUMBER",
                "target_field": "policy_number",
                "confidence": 0.95
            },
            {
                "source_field": "PREMIUM-AMOUNT",
                "target_field": "premium_amount",
                "confidence": 0.90,
                "transformation": "to_number"
            },
            {
                "source_field": "ISSUE-DATE",
                "target_field": "issue_date",
                "confidence": 0.95
            }
        ]
        
        target_schema = {
            "fields": [
                {"field_name": "policy_number", "field_type": "string"},
                {"field_name": "premium_amount", "field_type": "number"},
                {"field_name": "issue_date", "field_type": "date"}
            ]
        }
        
        # Mock file management
        data_transformation_service.file_management.upload_file = AsyncMock(return_value={
            "success": True,
            "file_id": "output_file_123"
        })
        
        result = await data_transformation_service.transform_data(
            source_data=source_data,
            mapping_rules=mapping_rules,
            target_schema=target_schema,
            output_format="json"
        )
        
        assert result["success"] is True
        assert "transformed_data" in result
        assert "output_file_id" in result
    
    @pytest.mark.asyncio
    async def test_transform_data_unstructured_fields(self, data_transformation_service):
        """Test transformation of unstructured extracted fields."""
        source_data = {
            "extracted_fields": {
                "license_expiration_date": {
                    "value": "2025-12-31",
                    "citation": "Page 1",
                    "confidence": 0.95
                }
            }
        }
        
        mapping_rules = [
            {
                "source_field": "license_expiration_date",
                "target_field": "expiration_date",
                "confidence": 0.95
            }
        ]
        
        target_schema = {
            "fields": [
                {"field_name": "expiration_date", "field_type": "date"}
            ]
        }
        
        # Mock file management
        data_transformation_service.file_management.upload_file = AsyncMock(return_value={
            "success": True,
            "file_id": "output_file_123"
        })
        
        result = await data_transformation_service.transform_data(
            source_data=source_data,
            mapping_rules=mapping_rules,
            target_schema=target_schema,
            output_format="json"
        )
        
        assert result["success"] is True
        assert "transformed_data" in result
        assert "citations" in result["transformed_data"]
    
    @pytest.mark.asyncio
    async def test_apply_transformation_date_format(self, data_transformation_service):
        """Test date format transformation."""
        result = data_transformation_service._apply_transformation("2024-01-15", "date_format")
        assert result == "2024-01-15"  # Already in correct format
    
    @pytest.mark.asyncio
    async def test_apply_transformation_to_number(self, data_transformation_service):
        """Test number transformation."""
        result = data_transformation_service._apply_transformation("1,000.50", "to_number")
        assert isinstance(result, (int, float))
        assert result == 1000.50










