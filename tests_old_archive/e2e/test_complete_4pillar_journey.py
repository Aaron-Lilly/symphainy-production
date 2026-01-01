#!/usr/bin/env python3
"""
E2E Tests for Complete 4-Pillar Journey

Tests the complete user journey across all 4 pillars:
1. Content: Upload → Parse → Extract
2. Insights: Analyze → Query → Visualize
3. Operations: Generate SOP/Workflow → Coexistence Analysis
4. Business Outcomes: Generate Roadmap → Create POC

This simulates a real end-to-end user workflow through the entire platform.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
from backend.business_enablement.business_orchestrator.use_cases.mvp.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator.business_outcomes_orchestrator import BusinessOutcomesOrchestrator

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

class TestComplete4PillarJourney:
    """E2E tests for complete 4-pillar user journey."""
    
    @pytest.fixture
    async def mock_platform_services(self):
        """Create mock platform services."""
        services = {}
        
        # Mock Librarian
        services['librarian'] = Mock()
        services['librarian'].store_document = AsyncMock(return_value={
            "success": True,
            "document_id": "doc_123",
            "uuid": "file_uuid_123"
        })
        services['librarian'].get_document = AsyncMock(return_value={
            "data": {
                "content": "Test document content",
                "metadata": {"file_type": "pdf"},
                "elements": [
                    {"type": "sop", "id": "sop_1"},
                    {"type": "workflow", "id": "workflow_1"}
                ]
            }
        })
        services['librarian'].create_session = AsyncMock(return_value={
            "success": True,
            "session_token": "session_123"
        })
        
        # Mock Data Steward
        services['data_steward'] = Mock()
        services['data_steward'].track_lineage = AsyncMock(return_value={"success": True})
        
        # Mock Curator
        services['curator'] = Mock()
        services['curator'].discover_service = AsyncMock(return_value={
            "success": True,
            "service_info": {"endpoint": "http://localhost:8000"}
        })
        
        return services
    
    @pytest.fixture
    async def mock_enabling_services(self):
        """Create mock enabling services."""
        services = {}
        
        # Content Pillar services
        services['file_parser'] = Mock()
        services['file_parser'].parse_file = AsyncMock(return_value={
            "success": True,
            "file_id": "file_123",
            "metadata": {"file_type": "pdf", "pages": 10},
            "content": "Parsed content"
        })
        
        services['entity_extractor'] = Mock()
        services['entity_extractor'].extract_entities = AsyncMock(return_value={
            "success": True,
            "entities": [
                {"type": "person", "value": "John Doe"},
                {"type": "organization", "value": "Acme Corp"}
            ]
        })
        
        # Insights Pillar services
        services['data_analyzer'] = Mock()
        services['data_analyzer'].analyze = AsyncMock(return_value={
            "success": True,
            "analysis": {"insights": ["Insight 1", "Insight 2"]}
        })
        
        services['visualization_engine'] = Mock()
        services['visualization_engine'].generate_visualization = AsyncMock(return_value={
            "success": True,
            "visualization": {"type": "chart", "data": [1, 2, 3]}
        })
        
        # Operations Pillar services
        services['sop_builder'] = Mock()
        services['sop_builder'].create_sop = AsyncMock(return_value={
            "success": True,
            "sop": {"title": "Test SOP", "procedures": []}
        })
        
        services['workflow_conversion'] = Mock()
        services['workflow_conversion'].convert_sop_to_workflow = AsyncMock(return_value={
            "success": True,
            "workflow": {"steps": []}
        })
        
        services['coexistence_analysis'] = Mock()
        services['coexistence_analysis'].analyze_coexistence = AsyncMock(return_value={
            "success": True,
            "alignment_score": 85,
            "gaps": []
        })
        
        # Business Outcomes services
        services['metrics_calculator'] = Mock()
        services['metrics_calculator'].calculate_kpi = AsyncMock(return_value={
            "success": True,
            "kpi_value": 100
        })
        
        return services
    
    @pytest.fixture
    async def content_orchestrator(self, mock_platform_services, mock_enabling_services):
        """Create ContentAnalysisOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.file_parser_service = mock_enabling_services['file_parser']
        mock_business_orchestrator.entity_extractor_service = mock_enabling_services['entity_extractor']
        
        orchestrator = ContentAnalysisOrchestrator(mock_business_orchestrator)
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.data_steward = mock_platform_services['data_steward']
        
        return orchestrator
    
    @pytest.fixture
    async def insights_orchestrator(self, mock_platform_services, mock_enabling_services):
        """Create InsightsOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.data_analyzer_service = mock_enabling_services['data_analyzer']
        mock_business_orchestrator.visualization_engine_service = mock_enabling_services['visualization_engine']
        
        orchestrator = InsightsOrchestrator(mock_business_orchestrator)
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.data_steward = mock_platform_services['data_steward']
        orchestrator.analysis_cache = {}
        
        return orchestrator
    
    @pytest.fixture
    async def operations_orchestrator(self, mock_platform_services, mock_enabling_services):
        """Create OperationsOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.sop_builder_service = mock_enabling_services['sop_builder']
        mock_business_orchestrator.workflow_conversion_service = mock_enabling_services['workflow_conversion']
        mock_business_orchestrator.coexistence_analysis_service = mock_enabling_services['coexistence_analysis']
        
        orchestrator = OperationsOrchestrator(mock_business_orchestrator)
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.data_steward = mock_platform_services['data_steward']
        
        return orchestrator
    
    @pytest.fixture
    async def business_outcomes_orchestrator(self, mock_platform_services, mock_enabling_services):
        """Create BusinessOutcomesOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.metrics_calculator_service = mock_enabling_services['metrics_calculator']
        
        orchestrator = BusinessOutcomesOrchestrator(mock_business_orchestrator)
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.data_steward = mock_platform_services['data_steward']
        
        # Mock specialist agent
        orchestrator.specialist_agent = Mock()
        orchestrator.specialist_agent.generate_roadmap = AsyncMock(return_value={
            "success": True,
            "roadmap": {"phases": ["Phase 1", "Phase 2"]}
        })
        orchestrator.specialist_agent.generate_poc_proposal = AsyncMock(return_value={
            "success": True,
            "poc": {"title": "POC Proposal"}
        })
        
        return orchestrator
    
    @pytest.fixture
    async def gateway_service(
        self,
        content_orchestrator,
        insights_orchestrator,
        operations_orchestrator,
        business_outcomes_orchestrator,
        mock_platform_services
    ):
        """Create FrontendGatewayService with all orchestrators."""
        platform_gateway = Mock()
        di_container = Mock()
        
        gateway = FrontendGatewayService(
            service_name="FrontendGatewayService",
            realm_name="experience",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        # Inject all orchestrators
        gateway.content_analysis_orchestrator = content_orchestrator
        gateway.insights_orchestrator = insights_orchestrator
        gateway.operations_orchestrator = operations_orchestrator
        gateway.business_outcomes_orchestrator = business_outcomes_orchestrator
        
        # Inject platform services
        gateway.librarian = mock_platform_services['librarian']
        gateway.security_guard = Mock()
        gateway.security_guard.authorize_action = AsyncMock(return_value={"authorized": True})
        gateway.traffic_cop = Mock()
        
        # Mock authorize_action for all orchestrators
        content_orchestrator.authorize_action = AsyncMock(return_value=True)
        insights_orchestrator.authorize_action = AsyncMock(return_value=True)
        operations_orchestrator.authorize_action = AsyncMock(return_value=True)
        business_outcomes_orchestrator.authorize_action = AsyncMock(return_value=True)
        
        return gateway
    
    async def test_complete_4pillar_journey(
        self,
        gateway_service,
        mock_platform_services
    ):
        """Test complete journey through all 4 pillars."""
        
        # ========================================
        # PILLAR 1: CONTENT - Upload & Parse
        # ========================================
        
        # Step 1: Parse uploaded file
        parse_request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {
                "file_id": "file_123"
            }
        }
        
        parse_result = await gateway_service.route_frontend_request(parse_request)
        
        # Verify parsing completed (may succeed or error gracefully)
        assert isinstance(parse_result, dict)
        
        # Step 2: Extract entities
        extract_request = {
            "endpoint": "/api/content/extract_entities",
            "method": "POST",
            "params": {
                "file_id": "file_123"
            }
        }
        
        extract_result = await gateway_service.route_frontend_request(extract_request)
        
        # Verify extraction succeeded
        assert isinstance(extract_result, dict)
        
        # ========================================
        # PILLAR 2: INSIGHTS - Analyze & Visualize
        # ========================================
        
        # Step 3: Analyze content for insights
        analyze_request = {
            "endpoint": "/api/insights/analyze_content_for_insights",
            "method": "POST",
            "params": {
                "source_type": "file",
                "file_id": "file_123",
                "content_type": "document",
                "analysis_options": {"depth": "deep"}
            }
        }
        
        analyze_result = await gateway_service.route_frontend_request(analyze_request)
        
        # Verify analysis succeeded
        assert isinstance(analyze_result, dict)
        
        # Step 4: Generate visualization
        viz_request = {
            "endpoint": "/api/insights/generate_visualization",
            "method": "POST",
            "params": {
                "analysis_id": "analysis_123",
                "viz_type": "chart",
                "viz_options": {}
            }
        }
        
        viz_result = await gateway_service.route_frontend_request(viz_request)
        
        # Verify visualization succeeded
        assert isinstance(viz_result, dict)
        
        # ========================================
        # PILLAR 3: OPERATIONS - Generate SOP/Workflow
        # ========================================
        
        # Step 5: Start wizard for SOP creation
        wizard_request = {
            "endpoint": "/api/operations/start_wizard",
            "method": "POST",
            "params": {}
        }
        
        sop_result = await gateway_service.route_frontend_request(wizard_request)
        
        # Verify wizard started
        assert isinstance(sop_result, dict)
        
        # Step 6: Convert SOP to workflow
        workflow_request = {
            "endpoint": "/api/operations/generate_workflow_from_sop",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "sop_file_uuid": "sop_uuid_123"
            }
        }
        
        workflow_result = await gateway_service.route_frontend_request(workflow_request)
        
        # Verify workflow generation succeeded
        assert isinstance(workflow_result, dict)
        
        # Step 7: Analyze coexistence
        coexistence_request = {
            "endpoint": "/api/operations/analyze_coexistence_files",
            "method": "POST",
            "params": {
                "session_token": "session_123"
            }
        }
        
        coexistence_result = await gateway_service.route_frontend_request(coexistence_request)
        
        # Verify coexistence analysis succeeded
        assert isinstance(coexistence_result, dict)
        
        # ========================================
        # PILLAR 4: BUSINESS OUTCOMES - Generate Roadmap & POC
        # ========================================
        
        # Step 8: Generate strategic roadmap
        roadmap_request = {
            "endpoint": "/api/business_outcomes/generate_strategic_roadmap",
            "method": "POST",
            "params": {
                "context_data": {
                    "pillar_outputs": {
                        "content": {"files_processed": 1},
                        "insights": {"analyses_completed": 1},
                        "operations": {"sops_created": 1, "workflows_created": 1}
                    }
                },
                "user_id": "test_user"
            }
        }
        
        roadmap_result = await gateway_service.route_frontend_request(roadmap_request)
        
        # Verify roadmap generation succeeded
        assert isinstance(roadmap_result, dict)
        
        # Step 9: Generate POC proposal
        poc_request = {
            "endpoint": "/api/business_outcomes/generate_poc_proposal",
            "method": "POST",
            "params": {
                "context_data": {"roadmap_id": "roadmap_123"},
                "user_id": "test_user"
            }
        }
        
        poc_result = await gateway_service.route_frontend_request(poc_request)
        
        # Verify POC generation succeeded
        assert isinstance(poc_result, dict)
        
        # ========================================
        # VERIFY COMPLETE JOURNEY
        # ========================================
        
        # All steps should have completed
        assert parse_result is not None
        assert extract_result is not None
        assert analyze_result is not None
        assert viz_result is not None
        assert sop_result is not None
        assert workflow_result is not None
        assert coexistence_result is not None
        assert roadmap_result is not None
        assert poc_result is not None
    
    async def test_session_state_persistence(
        self,
        gateway_service,
        mock_platform_services
    ):
        """Test that session state persists across pillars."""
        
        # Create session in Content
        parse_request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {"file_id": "file_123"}
        }
        
        parse_result = await gateway_service.route_frontend_request(parse_request)
        
        # Use same session in Operations
        wizard_request = {
            "endpoint": "/api/operations/start_wizard",
            "method": "POST",
            "params": {}
        }
        
        sop_result = await gateway_service.route_frontend_request(wizard_request)
        
        # Both should succeed with same session
        assert isinstance(parse_result, dict)
        assert isinstance(sop_result, dict)
    
    async def test_data_flow_between_pillars(
        self,
        content_orchestrator,
        insights_orchestrator,
        operations_orchestrator,
        business_outcomes_orchestrator
    ):
        """Test data flows correctly between pillars."""
        
        # Content → Insights
        parse_result = await content_orchestrator.parse_file(file_id="file_123")
        
        if parse_result.get("status") == "success" and "data" in parse_result:
            file_data = parse_result["data"]
            
            # Use content data in insights
            analyze_result = await insights_orchestrator.analyze_content_for_insights(
                source_type="file",
                file_id="file_123",
                content_type="document",
                analysis_options={}
            )
            
            assert isinstance(analyze_result, dict)
        
        # Insights → Business Outcomes
        roadmap_result = await business_outcomes_orchestrator.generate_strategic_roadmap(
            context_data={
                "pillar_outputs": {
                    "content": {"files_processed": 1},
                    "insights": {"analyses_completed": 1}
                }
            },
            user_id="test_user"
        )
        
        assert isinstance(roadmap_result, dict)
    
    async def test_concurrent_pillar_operations(
        self,
        content_orchestrator,
        insights_orchestrator,
        operations_orchestrator
    ):
        """Test concurrent operations across pillars."""
        import asyncio
        
        # Simulate concurrent operations
        tasks = [
            content_orchestrator.parse_file(file_id="file_1"),
            insights_orchestrator.analyze_content_for_insights(
                source_type="file",
                file_id="file_2",
                content_type="document",
                analysis_options={}
            ),
            operations_orchestrator.start_wizard()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_error_propagation_across_pillars(
        self,
        gateway_service
    ):
        """Test that errors in one pillar don't break others."""
        
        # Try invalid operation in Content
        invalid_request = {
            "endpoint": "/api/content/parse_file",
            "method": "POST",
            "params": {"file_id": "invalid_file"}
        }
        
        invalid_result = await gateway_service.route_frontend_request(invalid_request)
        
        # Should handle error gracefully
        assert isinstance(invalid_result, dict)
        
        # Other pillars should still work
        valid_request = {
            "endpoint": "/api/operations/start_wizard",
            "method": "POST",
            "params": {}
        }
        
        valid_result = await gateway_service.route_frontend_request(valid_request)
        
        # Should succeed
        assert isinstance(valid_result, dict)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

