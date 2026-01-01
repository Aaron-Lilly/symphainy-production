#!/usr/bin/env python3
"""
Integration tests for Data Mapping Workflow - Insights Realm

Tests end-to-end data mapping workflows for both use cases.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.integration
@pytest.mark.insights
@pytest.mark.slow
class TestDataMappingWorkflow:
    """Integration tests for Data Mapping Workflow."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def mock_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create mock Insights Journey Orchestrator."""
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        
        orchestrator = InsightsJourneyOrchestrator(
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        orchestrator.get_smart_city_service = AsyncMock(return_value=AsyncMock())
        orchestrator.get_infrastructure_abstraction = AsyncMock(return_value=None)
        orchestrator.get_business_abstraction = AsyncMock(return_value=None)
        
        return orchestrator
    
    @pytest.fixture
    async def data_mapping_workflow(self, mock_orchestrator):
        """Create Data Mapping Workflow instance."""
        from backend.journey.orchestrators.insights_journey_orchestrator.workflows.data_mapping_workflow import DataMappingWorkflow
        
        workflow = DataMappingWorkflow(mock_orchestrator)
        return workflow
    
    @pytest.mark.asyncio
    async def test_unstructured_to_structured_workflow(self, data_mapping_workflow, mock_orchestrator):
        """Test unstructured→structured mapping workflow."""
        # Mock Content Steward
        content_steward = AsyncMock()
        content_steward.get_file = AsyncMock(return_value={"file_type": "pdf"})
        content_steward.get_parsed_file = AsyncMock(return_value={
            "parsed_content": "License expires on December 31, 2025. Regulations: CFR 21 Part 11.",
            "text_content": "License expires on December 31, 2025. Regulations: CFR 21 Part 11."
        })
        mock_orchestrator.get_smart_city_service = AsyncMock(return_value=content_steward)
        
        # Mock Field Extraction Service
        field_extraction_service = AsyncMock()
        field_extraction_service.extract_fields = AsyncMock(return_value={
            "success": True,
            "extracted_fields": {
                "license_expiration_date": {
                    "value": "2025-12-31",
                    "citation": "Page 1",
                    "confidence": 0.95,
                    "source_text": "License expires on December 31, 2025"
                }
            }
        })
        mock_orchestrator._get_field_extraction_service = AsyncMock(return_value=field_extraction_service)
        
        # Mock Data Transformation Service
        data_transformation_service = AsyncMock()
        data_transformation_service.transform_data = AsyncMock(return_value={
            "success": True,
            "transformed_data": {"record": {"expiration_date": "2025-12-31"}},
            "output_file_id": "output_file_123"
        })
        mock_orchestrator._get_data_transformation_service = AsyncMock(return_value=data_transformation_service)
        
        # Mock Data Mapping Agent
        with patch('backend.journey.orchestrators.insights_journey_orchestrator.workflows.data_mapping_workflow.DataMappingAgent') as MockAgent:
            mock_agent = Mock()
            mock_agent.extract_source_schema = AsyncMock(return_value={
                "schema_type": "unstructured",
                "fields": [{"field_name": "license_expiration_date", "field_type": "date"}]
            })
            mock_agent.extract_target_schema = AsyncMock(return_value={
                "schema_type": "structured",
                "fields": [{"field_name": "expiration_date", "field_type": "date"}]
            })
            mock_agent.generate_mapping_rules = AsyncMock(return_value=[
                {"source_field": "license_expiration_date", "target_field": "expiration_date", "confidence": 0.95}
            ])
            MockAgent.return_value = mock_agent
            
            result = await data_mapping_workflow.execute(
                source_file_id="source_file_123",
                target_file_id="target_file_456"
            )
        
        assert result["success"] is True
        assert result["mapping_type"] == "unstructured_to_structured"
        assert "output_file_id" in result
    
    @pytest.mark.asyncio
    async def test_structured_to_structured_workflow(self, data_mapping_workflow, mock_orchestrator):
        """Test structured→structured mapping workflow."""
        # Mock Content Steward
        content_steward = AsyncMock()
        content_steward.get_file = AsyncMock(return_value={"file_type": "jsonl"})
        content_steward.get_parsed_file = AsyncMock(return_value={
            "parsed_data": {
                "columns": ["POLICY-NUMBER", "PREMIUM-AMOUNT", "ISSUE-DATE"],
                "rows": [
                    {"POLICY-NUMBER": "POL-001", "PREMIUM-AMOUNT": 1000.50, "ISSUE-DATE": "2024-01-15"},
                    {"POLICY-NUMBER": "POL-002", "PREMIUM-AMOUNT": 2000.00, "ISSUE-DATE": "2024-02-20"}
                ]
            }
        })
        mock_orchestrator.get_smart_city_service = AsyncMock(return_value=content_steward)
        
        # Mock Data Quality Validation Service
        data_quality_service = AsyncMock()
        data_quality_service.validate_records = AsyncMock(return_value={
            "success": True,
            "validation_results": [
                {"record_id": "record_1", "is_valid": True, "quality_score": 1.0, "issues": []}
            ],
            "summary": {
                "total_records": 2,
                "valid_records": 2,
                "invalid_records": 0,
                "overall_quality_score": 1.0
            },
            "has_issues": False
        })
        mock_orchestrator._get_data_quality_validation_service = AsyncMock(return_value=data_quality_service)
        
        # Mock Data Transformation Service
        data_transformation_service = AsyncMock()
        data_transformation_service.transform_data = AsyncMock(return_value={
            "success": True,
            "transformed_data": {"records": []},
            "output_file_id": "output_file_123"
        })
        mock_orchestrator._get_data_transformation_service = AsyncMock(return_value=data_transformation_service)
        
        # Mock Data Mapping Agent
        with patch('backend.journey.orchestrators.insights_journey_orchestrator.workflows.data_mapping_workflow.DataMappingAgent') as MockAgent:
            mock_agent = Mock()
            mock_agent.extract_source_schema = AsyncMock(return_value={
                "schema_type": "structured",
                "fields": [
                    {"field_name": "POLICY-NUMBER", "field_type": "string"},
                    {"field_name": "PREMIUM-AMOUNT", "field_type": "number"}
                ]
            })
            mock_agent.extract_target_schema = AsyncMock(return_value={
                "schema_type": "structured",
                "fields": [
                    {"field_name": "policy_number", "field_type": "string", "required": True},
                    {"field_name": "premium_amount", "field_type": "number", "required": True}
                ]
            })
            mock_agent.generate_mapping_rules = AsyncMock(return_value=[
                {"source_field": "POLICY-NUMBER", "target_field": "policy_number", "confidence": 0.95},
                {"source_field": "PREMIUM-AMOUNT", "target_field": "premium_amount", "confidence": 0.90}
            ])
            MockAgent.return_value = mock_agent
            
            result = await data_mapping_workflow.execute(
                source_file_id="source_file_123",
                target_file_id="target_file_456"
            )
        
        assert result["success"] is True
        assert result["mapping_type"] == "structured_to_structured"
        assert "data_quality" in result










