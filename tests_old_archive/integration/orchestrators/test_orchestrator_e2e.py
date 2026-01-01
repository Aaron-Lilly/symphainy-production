#!/usr/bin/env python3
"""
End-to-End Orchestrator Integration Tests

Tests orchestrators with real enabling services and Smart City services.
"""

import pytest
from typing import Dict, Any

@pytest.mark.integration
@pytest.mark.orchestrators
@pytest.mark.e2e
class TestOrchestratorE2E:
    """End-to-end tests for orchestrators."""
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_e2e(self, real_business_orchestrator):
        """Test Insights Orchestrator end-to-end."""
        if "insights" not in real_business_orchestrator.mvp_orchestrators:
            pytest.skip("Insights Orchestrator not available")
        
        orchestrator = real_business_orchestrator.mvp_orchestrators["insights"]
        
        # Test calculate_metrics
        result = await orchestrator.calculate_metrics(
            resource_id="test_resource",
            options={"analysis_type": "descriptive", "metric_name": "test_kpi"}
        )
        
        assert result.get("status") == "success", "Calculate metrics should succeed"
        assert "data" in result, "Result should contain data"
    
    @pytest.mark.asyncio
    async def test_operations_orchestrator_e2e(self, real_business_orchestrator):
        """Test Operations Orchestrator end-to-end."""
        if "operations" not in real_business_orchestrator.mvp_orchestrators:
            pytest.skip("Operations Orchestrator not available")
        
        orchestrator = real_business_orchestrator.mvp_orchestrators["operations"]
        
        # Test optimize_process
        result = await orchestrator.optimize_process(
            resource_id="test_resource",
            options={"workflow_definition": {"steps": []}}
        )
        
        assert result.get("status") == "success", "Optimize process should succeed"
    
    @pytest.mark.asyncio
    async def test_business_outcomes_orchestrator_e2e(self, real_business_orchestrator):
        """Test Business Outcomes Orchestrator end-to-end."""
        if "business_outcomes" not in real_business_orchestrator.mvp_orchestrators:
            pytest.skip("Business Outcomes Orchestrator not available")
        
        orchestrator = real_business_orchestrator.mvp_orchestrators["business_outcomes"]
        
        # Test track_outcomes
        result = await orchestrator.track_outcomes(
            resource_id="test_resource",
            options={"metric_name": "outcome_kpi"}
        )
        
        assert result.get("status") == "success", "Track outcomes should succeed"
    
    @pytest.mark.asyncio
    async def test_data_operations_orchestrator_e2e(self, real_business_orchestrator):
        """Test Data Operations Orchestrator end-to-end."""
        if "data_operations" not in real_business_orchestrator.mvp_orchestrators:
            pytest.skip("Data Operations Orchestrator not available")
        
        orchestrator = real_business_orchestrator.mvp_orchestrators["data_operations"]
        
        # Test transform_data
        result = await orchestrator.transform_data(
            resource_id="test_resource",
            options={"transformation_rules": {}}
        )
        
        assert result.get("status") == "success", "Transform data should succeed"
    
    @pytest.mark.asyncio
    async def test_business_orchestrator_routing(self, real_business_orchestrator):
        """Test Business Orchestrator routing to orchestrators."""
        # Test routing to Insights Orchestrator
        result = await real_business_orchestrator.execute_use_case(
            use_case="insights",
            request={
                "action": "calculate_metrics",
                "params": {
                    "resource_id": "test_resource",
                    "options": {}
                }
            }
        )
        
        assert result.get("status") == "success", "Routing should succeed"
    
    @pytest.mark.asyncio
    async def test_orchestrator_service_discovery(self, real_business_orchestrator):
        """Test orchestrator service discovery via Curator."""
        # Verify orchestrators are registered
        assert len(real_business_orchestrator.mvp_orchestrators) > 0, "Orchestrators should be discovered"
        
        # Verify each orchestrator is initialized
        for name, orchestrator in real_business_orchestrator.mvp_orchestrators.items():
            assert orchestrator.is_initialized, f"{name} orchestrator should be initialized"
    
    @pytest.mark.asyncio
    async def test_orchestrator_smart_city_integration(self, real_business_orchestrator):
        """Test orchestrator integration with Smart City services."""
        if "insights" not in real_business_orchestrator.mvp_orchestrators:
            pytest.skip("Insights Orchestrator not available")
        
        orchestrator = real_business_orchestrator.mvp_orchestrators["insights"]
        
        # Verify Smart City services are accessible
        librarian = await orchestrator.get_librarian_api()
        data_steward = await orchestrator.get_data_steward_api()
        
        assert librarian is not None, "Librarian should be accessible"
        assert data_steward is not None, "Data Steward should be accessible"

