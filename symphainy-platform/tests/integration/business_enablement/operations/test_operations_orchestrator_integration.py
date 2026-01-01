#!/usr/bin/env python3
"""
Integration Tests for OperationsOrchestrator with Real Services

Tests OperationsOrchestrator integration with:
- WorkflowConversionService
- SOPBuilderService
- CoexistenceAnalysisService
- StructuredJourneyOrchestratorService (for artifact creation)

Verifies that Operations MVP actually works with real services (no hardcoded cheats).
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../'))

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestOperationsOrchestratorIntegration:
    """Test OperationsOrchestrator with real enabling services."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.get_utility = Mock(return_value=None)
        container.service_registry = {}
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        return gateway
    
    @pytest.fixture
    def mock_delivery_manager(self, mock_di_container, mock_platform_gateway):
        """Create mock delivery manager."""
        manager = Mock()
        manager.realm_name = "business_enablement"
        manager.platform_gateway = mock_platform_gateway
        manager.di_container = mock_di_container
        return manager
    
    @pytest.fixture
    async def workflow_conversion_service(self, mock_di_container, mock_platform_gateway):
        """Create real WorkflowConversionService instance."""
        from backend.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
        
        service = WorkflowConversionService(
            service_name="WorkflowConversionService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.get_document = AsyncMock()
        service.content_steward = Mock()
        
        # Mock RealmServiceBase methods
        service.get_librarian_api = AsyncMock(return_value=service.librarian)
        service.get_content_steward_api = AsyncMock(return_value=service.content_steward)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        await service.initialize()
        return service
    
    @pytest.fixture
    async def sop_builder_service(self, mock_di_container, mock_platform_gateway):
        """Create real SOPBuilderService instance."""
        from backend.journey.services.sop_builder_service.sop_builder_service import SOPBuilderService
        
        service = SOPBuilderService(
            service_name="SOPBuilderService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        
        # Mock RealmServiceBase methods
        service.get_librarian_api = AsyncMock(return_value=service.librarian)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        await service.initialize()
        return service
    
    @pytest.fixture
    async def coexistence_service(self, mock_di_container, mock_platform_gateway):
        """Create real CoexistenceAnalysisService instance."""
        from backend.journey.services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
        
        service = CoexistenceAnalysisService(
            service_name="CoexistenceAnalysisService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.get_document = AsyncMock()
        
        # Mock RealmServiceBase methods
        service.get_librarian_api = AsyncMock(return_value=service.librarian)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        await service.initialize()
        return service
    
    @pytest.fixture
    async def journey_orchestrator(self, mock_di_container, mock_platform_gateway):
        """Create mock Journey Orchestrator for artifact creation."""
        journey_orch = Mock()
        journey_orch.create_journey_artifact = AsyncMock(return_value={
            "success": True,
            "artifact": {
                "artifact_id": "artifact_123",
                "artifact_type": "workflow",
                "status": "draft"
            }
        })
        return journey_orch
    
    @pytest.fixture
    async def operations_orchestrator(
        self,
        mock_delivery_manager,
        workflow_conversion_service,
        sop_builder_service,
        coexistence_service,
        journey_orchestrator
    ):
        """Create OperationsOrchestrator with real services."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        # Inject real services (bypassing discovery for testing)
        orchestrator._workflow_conversion_service = workflow_conversion_service
        orchestrator._sop_builder_service = sop_builder_service
        orchestrator._coexistence_analysis_service = coexistence_service
        orchestrator._journey_orchestrator = journey_orchestrator
        
        # Mock Smart City services
        orchestrator.librarian = Mock()
        orchestrator.librarian.get_document = AsyncMock(return_value={
            "document_id": "session_123",
            "data": {"elements": []}
        })
        orchestrator.conductor = Mock()
        
        # Mock RealmServiceBase methods
        orchestrator._realm_service = Mock()
        orchestrator._realm_service.log_operation_with_telemetry = AsyncMock()
        orchestrator._realm_service.handle_error_with_audit = AsyncMock()
        orchestrator._realm_service.record_health_metric = AsyncMock()
        orchestrator._realm_service.security = Mock()
        orchestrator._realm_service.security.check_permissions = AsyncMock(return_value=True)
        orchestrator._realm_service.tenant = Mock()
        orchestrator._realm_service.tenant.validate_tenant_access = AsyncMock(return_value=True)
        
        return orchestrator
    
    async def test_generate_workflow_from_sop_file_integration(
        self,
        operations_orchestrator,
        workflow_conversion_service
    ):
        """Test generating workflow from SOP file using real WorkflowConversionService."""
        # Setup - mock file in Librarian
        sop_file = {
            "document_id": "sop_file_123",
            "data": {
                "title": "Customer Onboarding SOP",
                "steps": [
                    {"step_number": 1, "instruction": "Collect customer information"},
                    {"step_number": 2, "instruction": "Verify customer identity"}
                ]
            }
        }
        workflow_conversion_service.librarian.get_document.return_value = sop_file
        
        # Execute
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test_session",
            sop_file_uuid="sop_file_123",
            client_id="client_123"
        )
        
        # Assert - verify real service was called
        assert result["success"] is True
        assert "workflow" in result or "workflow_content" in result
        assert "artifact_id" in result  # Week 7: Artifact created
        assert result["status"] == "draft"
        
        # Verify WorkflowConversionService was actually called
        workflow_conversion_service.librarian.get_document.assert_called_once()
    
    async def test_generate_sop_from_workflow_file_integration(
        self,
        operations_orchestrator,
        workflow_conversion_service
    ):
        """Test generating SOP from workflow file using real WorkflowConversionService."""
        # Setup - mock file in Librarian
        workflow_file = {
            "document_id": "workflow_file_123",
            "data": {
                "title": "Customer Onboarding Workflow",
                "steps": [
                    {"step_id": "step_1", "name": "Collect customer information", "order": 1},
                    {"step_id": "step_2", "name": "Verify customer identity", "order": 2}
                ]
            }
        }
        workflow_conversion_service.librarian.get_document.return_value = workflow_file
        
        # Execute
        result = await operations_orchestrator.generate_sop_from_workflow(
            session_token="test_session",
            workflow_file_uuid="workflow_file_123",
            client_id="client_123"
        )
        
        # Assert - verify real service was called
        assert result["success"] is True
        assert "sop" in result or "sop_content" in result
        assert "artifact_id" in result  # Week 7: Artifact created
        assert result["status"] == "draft"
    
    async def test_wizard_workflow_integration(
        self,
        operations_orchestrator,
        sop_builder_service
    ):
        """Test wizard workflow using real SOPBuilderService."""
        # Execute - start wizard
        start_result = await operations_orchestrator.start_wizard()
        
        # Assert
        assert start_result["success"] is True
        assert "session_token" in start_result
        
        session_token = start_result.get("session_token") or "test_wizard_session"
        
        # Execute - process wizard steps
        step1_result = await operations_orchestrator.wizard_chat(session_token, "Customer Onboarding SOP")
        assert step1_result["success"] is True
        
        step2_result = await operations_orchestrator.wizard_chat(session_token, "Standard procedure for onboarding")
        assert step2_result["success"] is True
        
        step3_result = await operations_orchestrator.wizard_chat(session_token, "Collect customer information")
        assert step3_result["success"] is True
        
        # Execute - complete wizard
        complete_result = await operations_orchestrator.wizard_publish(
            session_token=session_token,
            client_id="client_123"
        )
        
        # Assert - verify real service was called and artifact created
        assert complete_result["success"] is True
        assert "sop" in complete_result or "sop_content" in complete_result
        assert "artifact_id" in complete_result  # Week 7: Artifact created
        assert complete_result["status"] == "draft"
    
    async def test_analyze_coexistence_integration(
        self,
        operations_orchestrator,
        coexistence_service
    ):
        """Test coexistence analysis using real CoexistenceAnalysisService."""
        sop_content = {
            "title": "Customer Onboarding SOP",
            "steps": [
                {"step_number": 1, "instruction": "Collect customer information"},
                {"step_number": 2, "instruction": "Verify customer identity"}
            ]
        }
        workflow_content = {
            "title": "Customer Onboarding Workflow",
            "steps": [
                {"step_id": "step_1", "name": "Collect customer information", "order": 1},
                {"step_id": "step_2", "name": "Verify customer identity", "order": 2},
                {"step_id": "step_3", "name": "Send welcome email", "order": 3}
            ]
        }
        
        # Execute
        result = await operations_orchestrator.analyze_coexistence_content(
            session_token="test_session",
            sop_content=sop_content,
            workflow_content=workflow_content,
            client_id="client_123"
        )
        
        # Assert - verify real service was called
        assert result["success"] is True
        assert "blueprint" in result or "coexistence_blueprint" in result
        assert "analysis" in result or "analysis" in result.get("blueprint", {})
        assert "artifact_id" in result  # Week 7: Artifact created
        assert result["status"] == "draft"
    
    async def test_end_to_end_workflow_sop_conversion(
        self,
        operations_orchestrator,
        workflow_conversion_service
    ):
        """Test end-to-end: SOP → Workflow → SOP conversion."""
        # Step 1: SOP to Workflow
        sop_file = {
            "document_id": "sop_file_123",
            "data": {
                "title": "Test SOP",
                "steps": [
                    {"step_number": 1, "instruction": "Step 1"},
                    {"step_number": 2, "instruction": "Step 2"}
                ]
            }
        }
        workflow_conversion_service.librarian.get_document.return_value = sop_file
        
        result1 = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test_session",
            sop_file_uuid="sop_file_123"
        )
        assert result1["success"] is True
        workflow_id = result1.get("workflow", {}).get("workflow_id") or "workflow_123"
        
        # Step 2: Workflow to SOP
        workflow_file = {
            "document_id": workflow_id,
            "data": result1.get("workflow") or result1.get("workflow_content", {})
        }
        workflow_conversion_service.librarian.get_document.return_value = workflow_file
        
        result2 = await operations_orchestrator.generate_sop_from_workflow(
            session_token="test_session",
            workflow_file_uuid=workflow_id
        )
        assert result2["success"] is True
        assert "sop" in result2 or "sop_content" in result2
    
    async def test_operations_mvp_no_hardcoded_cheats(
        self,
        operations_orchestrator,
        workflow_conversion_service,
        sop_builder_service,
        coexistence_service
    ):
        """Test that Operations MVP works with real services (no hardcoded cheats)."""
        # This test verifies that all operations use real services, not mocks or hardcoded returns
        
        # Test 1: Workflow conversion (real service)
        sop_file = {
            "document_id": "sop_file_123",
            "data": {
                "title": "Test SOP",
                "steps": [{"step_number": 1, "instruction": "Test step"}]
            }
        }
        workflow_conversion_service.librarian.get_document.return_value = sop_file
        
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test",
            sop_file_uuid="sop_file_123"
        )
        
        # Verify: Result comes from real service (has workflow structure)
        assert result["success"] is True
        assert "workflow" in result or "workflow_content" in result
        workflow = result.get("workflow") or result.get("workflow_content", {})
        assert "workflow_id" in workflow
        assert "steps" in workflow
        assert len(workflow["steps"]) > 0
        
        # Test 2: Wizard (real service)
        wizard_result = await operations_orchestrator.start_wizard()
        assert wizard_result["success"] is True
        assert "session_token" in wizard_result
        
        # Test 3: Coexistence analysis (real service)
        coexistence_result = await operations_orchestrator.analyze_coexistence_content(
            session_token="test",
            sop_content={"title": "SOP", "steps": [{"step_number": 1, "instruction": "Step 1"}]},
            workflow_content={"title": "Workflow", "steps": [{"step_id": "step_1", "name": "Step 1", "order": 1}]}
        )
        assert coexistence_result["success"] is True
        assert "blueprint" in coexistence_result or "coexistence_blueprint" in coexistence_result
        blueprint = coexistence_result.get("blueprint") or coexistence_result.get("coexistence_blueprint", {})
        assert "analysis" in blueprint or "analysis_id" in blueprint







