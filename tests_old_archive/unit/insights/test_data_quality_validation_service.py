#!/usr/bin/env python3
"""
Unit tests for Data Quality Validation Service - Insights Realm

Tests data quality validation and cleanup action generation.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.fast
class TestDataQualityValidationService:
    """Unit tests for Data Quality Validation Service."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def data_quality_service(self, mock_platform_gateway, mock_di_container):
        """Create Data Quality Validation Service instance."""
        from backend.insights.services.data_quality_validation_service.data_quality_validation_service import DataQualityValidationService
        
        service = DataQualityValidationService(
            service_name="DataQualityValidationService",
            realm_name="insights",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.data_steward = AsyncMock()
        service.content_steward = AsyncMock()
        service.nurse = AsyncMock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_validate_records_success(self, data_quality_service):
        """Test successful record validation."""
        records = [
            {
                "record_id": "record_1",
                "policy_number": "POL-001",
                "premium_amount": 1000.50,
                "issue_date": "2024-01-15"
            },
            {
                "record_id": "record_2",
                "policy_number": "POL-002",
                "premium_amount": 2000.00,
                "issue_date": "2024-02-20"
            }
        ]
        
        target_schema = {
            "fields": [
                {
                    "field_name": "policy_number",
                    "field_type": "string",
                    "required": True
                },
                {
                    "field_name": "premium_amount",
                    "field_type": "number",
                    "required": True
                },
                {
                    "field_name": "issue_date",
                    "field_type": "date",
                    "required": True
                }
            ]
        }
        
        mapping_rules = [
            {
                "source_field": "policy_number",
                "target_field": "policy_number"
            },
            {
                "source_field": "premium_amount",
                "target_field": "premium_amount"
            },
            {
                "source_field": "issue_date",
                "target_field": "issue_date"
            }
        ]
        
        result = await data_quality_service.validate_records(
            records=records,
            target_schema=target_schema,
            mapping_rules=mapping_rules
        )
        
        assert result["success"] is True
        assert "validation_results" in result
        assert "summary" in result
        assert result["summary"]["total_records"] == 2
    
    @pytest.mark.asyncio
    async def test_validate_records_missing_required(self, data_quality_service):
        """Test validation with missing required fields."""
        records = [
            {
                "record_id": "record_1",
                "policy_number": "",  # Missing required field
                "premium_amount": 1000.50
            }
        ]
        
        target_schema = {
            "fields": [
                {
                    "field_name": "policy_number",
                    "field_type": "string",
                    "required": True
                },
                {
                    "field_name": "premium_amount",
                    "field_type": "number",
                    "required": True
                }
            ]
        }
        
        mapping_rules = [
            {
                "source_field": "policy_number",
                "target_field": "policy_number"
            },
            {
                "source_field": "premium_amount",
                "target_field": "premium_amount"
            }
        ]
        
        result = await data_quality_service.validate_records(
            records=records,
            target_schema=target_schema,
            mapping_rules=mapping_rules
        )
        
        assert result["success"] is True
        assert result["summary"]["invalid_records"] > 0
        assert result["has_issues"] is True
    
    @pytest.mark.asyncio
    async def test_generate_cleanup_actions(self, data_quality_service):
        """Test cleanup action generation."""
        validation_results = {
            "validation_results": [
                {
                    "record_id": "record_1",
                    "is_valid": False,
                    "issues": [
                        {
                            "field": "policy_number",
                            "issue_type": "missing_required",
                            "severity": "error",
                            "message": "Required field missing",
                            "source_field": "policy_number",
                            "target_field": "policy_number"
                        }
                    ]
                }
            ],
            "summary": {
                "total_records": 1,
                "valid_records": 0,
                "invalid_records": 1,
                "overall_quality_score": 0.5
            }
        }
        
        result = await data_quality_service.generate_cleanup_actions(
            validation_results=validation_results,
            source_file_id="test_file_123"
        )
        
        assert result["success"] is True
        assert "cleanup_actions" in result
        assert len(result["cleanup_actions"]) > 0
        assert "summary" in result










