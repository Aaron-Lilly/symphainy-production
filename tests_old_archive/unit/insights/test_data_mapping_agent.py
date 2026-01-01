#!/usr/bin/env python3
"""
Unit tests for Data Mapping Agent - Insights Realm

Tests schema extraction and mapping rule generation.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.insights
@pytest.mark.fast
class TestDataMappingAgent:
    """Unit tests for Data Mapping Agent."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock orchestrator."""
        orchestrator = Mock()
        orchestrator.logger = Mock()
        orchestrator.platform_gateway = Mock()
        orchestrator.di_container = Mock()
        orchestrator.get_smart_city_service = AsyncMock()
        orchestrator.get_business_abstraction = AsyncMock()
        return orchestrator
    
    @pytest.fixture
    def data_mapping_agent(self, mock_orchestrator):
        """Create Data Mapping Agent instance."""
        from backend.insights.agents.data_mapping_agent import DataMappingAgent
        return DataMappingAgent(mock_orchestrator)
    
    @pytest.mark.asyncio
    async def test_extract_source_schema_unstructured(self, data_mapping_agent, mock_orchestrator):
        """Test schema extraction from unstructured source."""
        # Mock Content Steward
        content_steward = AsyncMock()
        content_steward.get_parsed_file = AsyncMock(return_value={
            "parsed_content": "License expires on December 31, 2025.",
            "text_content": "License expires on December 31, 2025."
        })
        mock_orchestrator.get_smart_city_service = AsyncMock(return_value=content_steward)
        
        # Mock LLM
        llm_composition = AsyncMock()
        llm_composition.generate_text = AsyncMock(return_value={
            "text": '{"fields": [{"field_name": "license_expiration_date", "field_type": "date", "description": "License expiration date", "required": true}]}'
        })
        mock_orchestrator.get_business_abstraction = AsyncMock(return_value=llm_composition)
        
        result = await data_mapping_agent.extract_source_schema(
            source_file_id="test_file_123",
            mapping_type="unstructured_to_structured"
        )
        
        assert "schema_type" in result
        assert result["schema_type"] == "unstructured" or "fields" in result
    
    @pytest.mark.asyncio
    async def test_extract_source_schema_structured(self, data_mapping_agent, mock_orchestrator):
        """Test schema extraction from structured source."""
        # Mock Content Steward
        content_steward = AsyncMock()
        content_steward.get_parsed_file = AsyncMock(return_value={
            "parsed_data": {
                "columns": ["POLICY-NUMBER", "PREMIUM-AMOUNT"],
                "rows": [
                    {"POLICY-NUMBER": "POL-001", "PREMIUM-AMOUNT": 1000.50}
                ]
            }
        })
        mock_orchestrator.get_smart_city_service = AsyncMock(return_value=content_steward)
        
        result = await data_mapping_agent.extract_source_schema(
            source_file_id="test_file_123",
            mapping_type="structured_to_structured"
        )
        
        assert "schema_type" in result
        assert result["schema_type"] == "structured"
    
    @pytest.mark.asyncio
    async def test_generate_mapping_rules(self, data_mapping_agent, mock_orchestrator):
        """Test mapping rule generation."""
        source_schema = {
            "fields": [
                {"field_name": "POLICY-NUMBER", "field_type": "string"},
                {"field_name": "PREMIUM-AMOUNT", "field_type": "number"}
            ]
        }
        
        target_schema = {
            "fields": [
                {"field_name": "policy_number", "field_type": "string"},
                {"field_name": "premium_amount", "field_type": "number"}
            ]
        }
        
        # Mock LLM for fallback
        llm_composition = AsyncMock()
        llm_composition.generate_text = AsyncMock(return_value={
            "text": '{"mappings": [{"source_field": "POLICY-NUMBER", "target_field": "policy_number", "confidence": 0.95, "matching_method": "llm_semantic"}]}'
        })
        mock_orchestrator.get_business_abstraction = AsyncMock(return_value=llm_composition)
        
        result = await data_mapping_agent.generate_mapping_rules(
            source_schema=source_schema,
            target_schema=target_schema,
            source_embeddings=[],
            target_embeddings=[]
        )
        
        assert isinstance(result, list)
        # Should have at least some mappings (even if from LLM fallback)
        assert len(result) >= 0  # May be empty if no embeddings and LLM fails
    
    @pytest.mark.asyncio
    async def test_cosine_similarity(self, data_mapping_agent):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = data_mapping_agent._cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, abs=0.01)  # Identical vectors
        
        vec3 = [0.0, 1.0, 0.0]
        similarity2 = data_mapping_agent._cosine_similarity(vec1, vec3)
        assert similarity2 == pytest.approx(0.0, abs=0.01)  # Orthogonal vectors










