#!/usr/bin/env python3
"""
API Integration tests for Insights Solution Orchestrator

Tests API endpoints for data mapping operations.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.integration
@pytest.mark.insights
@pytest.mark.api_contract
@pytest.mark.slow
class TestInsightsSolutionOrchestratorAPI:
    """API integration tests for Insights Solution Orchestrator."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Mock platform gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Mock DI container."""
        return Mock()
    
    @pytest.fixture
    async def insights_solution_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create Insights Solution Orchestrator instance."""
        from backend.solution.services.insights_solution_orchestrator_service.insights_solution_orchestrator_service import InsightsSolutionOrchestratorService
        
        orchestrator = InsightsSolutionOrchestratorService(
            service_name="InsightsSolutionOrchestratorService",
            realm_name="solution",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock platform correlation services
        orchestrator.security_guard = AsyncMock()
        orchestrator.traffic_cop = AsyncMock()
        orchestrator.conductor = AsyncMock()
        orchestrator.post_office = AsyncMock()
        orchestrator.nurse = AsyncMock()
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_mapping_success(self, insights_solution_orchestrator):
        """Test successful mapping orchestration via API."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_data_mapping_workflow = AsyncMock(return_value={
            "success": True,
            "mapping_id": "mapping_123",
            "mapping_type": "unstructured_to_structured",
            "output_file_id": "output_file_123"
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        # Mock platform correlation
        insights_solution_orchestrator._orchestrate_platform_correlation = AsyncMock(return_value={
            "workflow_id": "workflow_123",
            "user_id": "test_user",
            "session_id": "session_123"
        })
        
        result = await insights_solution_orchestrator.orchestrate_insights_mapping(
            source_file_id="source_file_123",
            target_file_id="target_file_456",
            mapping_options={"mapping_type": "auto"},
            user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
        )
        
        assert result["success"] is True
        assert "mapping_id" in result
        assert "output_file_id" in result
    
    @pytest.mark.asyncio
    async def test_orchestrate_insights_mapping_platform_correlation(self, insights_solution_orchestrator):
        """Test that platform correlation is properly orchestrated."""
        # Mock Insights Journey Orchestrator
        mock_journey_orchestrator = AsyncMock()
        mock_journey_orchestrator.execute_data_mapping_workflow = AsyncMock(return_value={
            "success": True,
            "mapping_id": "mapping_123"
        })
        
        insights_solution_orchestrator._discover_insights_journey_orchestrator = AsyncMock(
            return_value=mock_journey_orchestrator
        )
        
        # Mock platform correlation services
        insights_solution_orchestrator.security_guard.validate_tenant_access = AsyncMock(return_value={"valid": True})
        insights_solution_orchestrator.traffic_cop.get_session_state = AsyncMock(return_value={"state": "active"})
        insights_solution_orchestrator.conductor.start_workflow = AsyncMock()
        insights_solution_orchestrator.conductor.complete_workflow = AsyncMock()
        
        result = await insights_solution_orchestrator.orchestrate_insights_mapping(
            source_file_id="source_file_123",
            target_file_id="target_file_456",
            user_context={"user_id": "test_user", "tenant_id": "test_tenant", "session_id": "session_123"}
        )
        
        # Verify platform correlation was called
        assert insights_solution_orchestrator.conductor.start_workflow.called
        assert insights_solution_orchestrator.conductor.complete_workflow.called
        assert result["success"] is True










