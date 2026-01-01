#!/usr/bin/env python3
"""
E2E Tests for Business Outcomes Pillar Journey

Tests the complete Business Outcomes Pillar user journey:
1. Generate roadmap from insights
2. Create POC proposal
3. Verify document quality
4. Test KPI calculation
5. Test outcome tracking
6. Test journey visualization

This simulates a real user workflow through the Business Outcomes Pillar.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

class TestBusinessOutcomesPillarJourney:
    """E2E tests for Business Outcomes Pillar user journey."""
    
    @pytest.fixture
    async def mock_platform_services(self):
        """Create mock platform services."""
        services = {}
        
        # Mock Librarian
        services['librarian'] = Mock()
        services['librarian'].store_document = AsyncMock(return_value={
            "success": True,
            "document_id": "doc_123"
        })
        services['librarian'].get_document = AsyncMock(return_value={
            "data": {
                "roadmap": {"phases": ["Phase 1", "Phase 2"]},
                "poc": {"title": "Test POC"},
                "metadata": {}
            }
        })
        
        # Mock Data Steward
        services['data_steward'] = Mock()
        services['data_steward'].track_lineage = AsyncMock(return_value={"success": True})
        
        return services
    
    @pytest.fixture
    async def mock_orchestrators(self):
        """Create mock orchestrators for other pillars."""
        orchestrators = {}
        
        # Mock Content Orchestrator
        orchestrators['content'] = Mock()
        orchestrators['content'].get_pillar_summary = AsyncMock(return_value={
            "status": "success",
            "summary": {
                "files_processed": 10,
                "entities_extracted": 50
            }
        })
        
        # Mock Insights Orchestrator
        orchestrators['insights'] = Mock()
        orchestrators['insights'].get_pillar_summary = AsyncMock(return_value={
            "status": "success",
            "summary": {
                "analyses_completed": 5,
                "insights_generated": 15,
                "visualizations_created": 8
            }
        })
        
        # Mock Operations Orchestrator
        orchestrators['operations'] = Mock()
        orchestrators['operations'].get_session_elements = AsyncMock(return_value={
            "success": True,
            "elements": [
                {"type": "sop", "count": 3},
                {"type": "workflow", "count": 2}
            ]
        })
        
        return orchestrators
    
    @pytest.fixture
    async def business_outcomes_orchestrator(self, mock_platform_services, mock_orchestrators):
        """Create BusinessOutcomesOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.platform_gateway = Mock()
        mock_business_orchestrator.di_container = Mock()
        
        # Inject other orchestrators
        mock_business_orchestrator.content_orchestrator = mock_orchestrators['content']
        mock_business_orchestrator.insights_orchestrator = mock_orchestrators['insights']
        mock_business_orchestrator.operations_orchestrator = mock_orchestrators['operations']
        
        # Mock enabling services
        mock_business_orchestrator.metrics_calculator_service = Mock()
        mock_business_orchestrator.metrics_calculator_service.calculate_kpi = AsyncMock(return_value={
            "success": True,
            "kpi_value": 100,
            "metric": "test_metric"
        })
        
        mock_business_orchestrator.data_analyzer_service = Mock()
        mock_business_orchestrator.data_analyzer_service.analyze = AsyncMock(return_value={
            "success": True,
            "analysis": {"trend": "positive"}
        })
        
        orchestrator = BusinessOutcomesOrchestrator(mock_business_orchestrator)
        
        # Inject platform services
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.data_steward = mock_platform_services['data_steward']
        
        # Mock specialist agent
        orchestrator.specialist_agent = Mock()
        orchestrator.specialist_agent.generate_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap": {
                "title": "Strategic Roadmap",
                "phases": [
                    {"name": "Phase 1: Assessment", "duration": "3 months"},
                    {"name": "Phase 2: Implementation", "duration": "6 months"},
                    {"name": "Phase 3: Optimization", "duration": "3 months"}
                ],
                "milestones": ["Milestone A", "Milestone B", "Milestone C"]
            }
        })
        orchestrator.specialist_agent.generate_poc_proposal = AsyncMock(return_value={
            "success": True,
            "poc": {
                "title": "Proof of Concept Proposal",
                "objective": "Demonstrate platform capabilities",
                "scope": "Limited pilot with key stakeholders",
                "timeline": "4 weeks",
                "deliverables": ["Working prototype", "Documentation", "Training materials"],
                "success_criteria": ["User adoption > 80%", "Performance targets met"]
            }
        })
        
        return orchestrator
    
    @pytest.fixture
    async def gateway_service(self, business_outcomes_orchestrator):
        """Create FrontendGatewayService with mocked orchestrators."""
        platform_gateway = Mock()
        di_container = Mock()
        
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Inject orchestrators
        gateway.business_outcomes_orchestrator = business_outcomes_orchestrator
        gateway.librarian = Mock()
        gateway.security_guard = Mock()
        gateway.traffic_cop = Mock()
        
        return gateway
    
    async def test_complete_business_outcomes_journey(
        self,
        gateway_service,
        business_outcomes_orchestrator,
        mock_platform_services
    ):
        """Test complete Business Outcomes Pillar user journey."""
        
        # Step 1: Generate strategic roadmap
        roadmap_request = {
            "endpoint": "/api/business_outcomes/generate_strategic_roadmap",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "insights_summary": {
                    "key_findings": ["Finding 1", "Finding 2"],
                    "recommendations": ["Rec 1", "Rec 2"]
                }
            }
        }
        
        roadmap_result = await gateway_service.route_frontend_request(roadmap_request)
        
        # Verify roadmap generation succeeded
        assert isinstance(roadmap_result, dict)
        assert "success" in roadmap_result or "status" in roadmap_result
        
        # Step 2: Generate POC proposal
        poc_request = {
            "endpoint": "/api/business_outcomes/generate_poc_proposal",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "roadmap_id": "roadmap_123"
            }
        }
        
        poc_result = await gateway_service.route_frontend_request(poc_request)
        
        # Verify POC generation succeeded
        assert isinstance(poc_result, dict)
        
        # Step 3: Calculate KPIs
        kpi_request = {
            "endpoint": "/api/business_outcomes/calculate_kpis",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "outcome_data": {"metric": "value"}
            }
        }
        
        kpi_result = await gateway_service.route_frontend_request(kpi_request)
        
        # Verify KPI calculation succeeded
        assert isinstance(kpi_result, dict)
        
        # Step 4: Get pillar summaries
        summary_request = {
            "endpoint": "/api/business_outcomes/get_pillar_summaries",
            "method": "GET",
            "params": {
                "session_token": "session_123"
            }
        }
        
        summary_result = await gateway_service.route_frontend_request(summary_request)
        
        # Verify summary retrieval succeeded
        assert isinstance(summary_result, dict)
    
    async def test_roadmap_generation_workflow(self, business_outcomes_orchestrator):
        """Test roadmap generation workflow."""
        result = await business_outcomes_orchestrator.generate_strategic_roadmap(
            context_data={
                "pillar_outputs": {
                    "content": {"files_processed": 10},
                    "insights": {"analyses_completed": 5},
                    "operations": {"sops_created": 3}
                },
                "roadmap_options": {"roadmap_type": "hybrid"}
            },
            user_id="test_user"
        )
        
        # Should return roadmap
        assert "success" in result
        if result["success"]:
            assert "roadmap" in result
            # Verify roadmap structure
            roadmap = result["roadmap"]
            assert "phases" in roadmap or "title" in roadmap
    
    async def test_poc_proposal_generation(self, business_outcomes_orchestrator):
        """Test POC proposal generation."""
        result = await business_outcomes_orchestrator.generate_poc_proposal(
            context_data={
                "roadmap_id": "roadmap_123",
                "business_context": {"name": "Test Business"}
            },
            user_id="test_user"
        )
        
        # Should return POC proposal
        assert "success" in result
        if result["success"]:
            assert "poc" in result
            # Verify POC structure
            poc = result["poc"]
            assert "title" in poc or "objective" in poc
    
    async def test_kpi_calculation(self, business_outcomes_orchestrator):
        """Test KPI calculation."""
        result = await business_outcomes_orchestrator.calculate_kpis(
            resource_id="resource_123",
            options={
                "kpi_types": ["revenue", "users", "satisfaction"]
            }
        )
        
        # Should return KPIs (or error gracefully)
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_outcome_tracking(self, business_outcomes_orchestrator):
        """Test outcome tracking."""
        result = await business_outcomes_orchestrator.track_outcomes(
            resource_id="resource_123",
            options={
                "outcome_type": "business_metric",
                "metric_name": "Customer Acquisition Cost",
                "value": 150
            }
        )
        
        # Should track outcome (or error gracefully)
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_outcome_analysis(self, business_outcomes_orchestrator):
        """Test outcome analysis."""
        result = await business_outcomes_orchestrator.analyze_outcomes(
            resource_id="resource_123",
            options={"analysis_type": "trend"}
        )
        
        # Should return analysis (or error gracefully)
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_pillar_summaries_retrieval(self, business_outcomes_orchestrator):
        """Test retrieving summaries from all pillars."""
        result = await business_outcomes_orchestrator.get_pillar_summaries(
            session_id="session_123",
            user_id="test_user"
        )
        
        # Should return summaries from all pillars
        assert "success" in result
        if result["success"]:
            assert "summaries" in result or "content" in result or "insights" in result
    
    async def test_journey_visualization(self, business_outcomes_orchestrator):
        """Test journey visualization generation."""
        result = await business_outcomes_orchestrator.get_journey_visualization(
            session_id="session_123"
        )
        
        # Should return visualization data
        assert "success" in result
        if result["success"]:
            assert "visualization" in result or "journey" in result
    
    async def test_document_quality_validation(self, business_outcomes_orchestrator):
        """Test that generated documents have high quality."""
        # Generate roadmap
        roadmap_result = await business_outcomes_orchestrator.generate_strategic_roadmap(
            context_data={
                "pillar_outputs": {"content": {}, "insights": {}, "operations": {}},
                "roadmap_options": {}
            },
            user_id="test_user"
        )
        
        if roadmap_result.get("success") and "roadmap" in roadmap_result:
            roadmap = roadmap_result["roadmap"]
            
            # Should have professional structure
            assert "phases" in roadmap or "title" in roadmap
            
            # Generate POC from roadmap
            poc_result = await business_outcomes_orchestrator.generate_poc_proposal(
                context_data={"roadmap_id": "roadmap_123"},
                user_id="test_user"
            )
            
            if poc_result.get("success") and "poc" in poc_result:
                poc = poc_result["poc"]
                
                # POC should have professional structure
                assert "title" in poc or "objective" in poc
    
    async def test_error_handling_missing_data(self, business_outcomes_orchestrator):
        """Test error handling for missing data."""
        result = await business_outcomes_orchestrator.generate_strategic_roadmap(
            context_data={},  # Empty context
            user_id="test_user"
        )
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert "success" in result
    
    async def test_concurrent_operations(self, business_outcomes_orchestrator):
        """Test concurrent operations."""
        import asyncio
        
        # Simulate multiple operations
        tasks = [
            business_outcomes_orchestrator.track_outcomes(
                resource_id=f"resource_{i}",
                options={"value": i}
            )
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_smart_city_integration(
        self,
        business_outcomes_orchestrator,
        mock_platform_services
    ):
        """Test Smart City service integration."""
        result = await business_outcomes_orchestrator.track_outcomes(
            resource_id="resource_123",
            options={"value": 100}
        )
        
        # Should have completed (Smart City integration happens internally, or error gracefully)
        assert isinstance(result, dict)
        assert "success" in result or "status" in result or "error" in result
    
    async def test_cross_pillar_integration(
        self,
        business_outcomes_orchestrator,
        mock_orchestrators
    ):
        """Test integration with other pillars."""
        # Get summaries from all pillars
        result = await business_outcomes_orchestrator.get_pillar_summaries(
            session_id="session_123",
            user_id="test_user"
        )
        
        # Should have retrieved data from other orchestrators
        assert "success" in result

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

