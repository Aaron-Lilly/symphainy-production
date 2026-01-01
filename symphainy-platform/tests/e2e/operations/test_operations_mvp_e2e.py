#!/usr/bin/env python3
"""
End-to-End Tests for Operations MVP

Tests complete Operations MVP workflows:
1. SOP → Workflow conversion with artifact creation
2. Workflow → SOP conversion with artifact creation
3. Wizard-based SOP creation with artifact creation
4. Coexistence analysis with blueprint artifact creation
5. Full workflow: Wizard → SOP → Workflow → Coexistence Analysis

Verifies that Operations MVP actually works end-to-end with real services (no hardcoded cheats).
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../'))

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


class TestOperationsMVPE2E:
    """End-to-end tests for Operations MVP workflows."""
    
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
    async def setup_services(self, mock_di_container, mock_platform_gateway):
        """Set up all real services for E2E testing."""
        from backend.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
        from backend.journey.services.sop_builder_service.sop_builder_service import SOPBuilderService
        from backend.journey.services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
        
        # Create WorkflowConversionService
        workflow_service = WorkflowConversionService(
            service_name="WorkflowConversionService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        workflow_service.librarian = Mock()
        workflow_service.librarian.get_document = AsyncMock()
        workflow_service.get_librarian_api = AsyncMock(return_value=workflow_service.librarian)
        workflow_service.get_content_steward_api = AsyncMock(return_value=Mock())
        workflow_service.register_with_curator = AsyncMock(return_value=True)
        workflow_service.log_operation_with_telemetry = AsyncMock()
        workflow_service.handle_error_with_audit = AsyncMock()
        workflow_service.record_health_metric = AsyncMock()
        await workflow_service.initialize()
        
        # Create SOPBuilderService
        sop_service = SOPBuilderService(
            service_name="SOPBuilderService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        sop_service.librarian = Mock()
        sop_service.get_librarian_api = AsyncMock(return_value=sop_service.librarian)
        sop_service.register_with_curator = AsyncMock(return_value=True)
        sop_service.log_operation_with_telemetry = AsyncMock()
        sop_service.handle_error_with_audit = AsyncMock()
        sop_service.record_health_metric = AsyncMock()
        await sop_service.initialize()
        
        # Create CoexistenceAnalysisService
        coexistence_service = CoexistenceAnalysisService(
            service_name="CoexistenceAnalysisService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        coexistence_service.librarian = Mock()
        coexistence_service.librarian.get_document = AsyncMock()
        coexistence_service.get_librarian_api = AsyncMock(return_value=coexistence_service.librarian)
        coexistence_service.register_with_curator = AsyncMock(return_value=True)
        coexistence_service.log_operation_with_telemetry = AsyncMock()
        coexistence_service.handle_error_with_audit = AsyncMock()
        coexistence_service.record_health_metric = AsyncMock()
        await coexistence_service.initialize()
        
        return {
            "workflow_service": workflow_service,
            "sop_service": sop_service,
            "coexistence_service": coexistence_service
        }
    
    @pytest.fixture
    async def journey_orchestrator(self):
        """Create mock Journey Orchestrator for artifact creation."""
        journey_orch = Mock()
        journey_orch.create_journey_artifact = AsyncMock(return_value={
            "success": True,
            "artifact": {
                "artifact_id": "artifact_123",
                "artifact_type": "workflow",
                "status": "draft",
                "client_id": "client_123"
            }
        })
        return journey_orch
    
    @pytest.fixture
    async def operations_orchestrator(
        self,
        mock_delivery_manager,
        setup_services,
        journey_orchestrator
    ):
        """Create OperationsOrchestrator with real services."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        # Inject real services
        orchestrator._workflow_conversion_service = setup_services["workflow_service"]
        orchestrator._sop_builder_service = setup_services["sop_service"]
        orchestrator._coexistence_analysis_service = setup_services["coexistence_service"]
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
    
    async def test_e2e_sop_to_workflow_with_artifact(
        self,
        operations_orchestrator,
        setup_services,
        journey_orchestrator
    ):
        """E2E: Convert SOP to workflow and create artifact."""
        # Setup - SOP file
        sop_file = {
            "document_id": "sop_file_123",
            "data": {
                "title": "Customer Onboarding SOP",
                "description": "Standard procedure for onboarding",
                "steps": [
                    {"step_number": 1, "instruction": "Collect customer information", "details": "Gather name, email"},
                    {"step_number": 2, "instruction": "Verify customer identity", "details": "Check ID documents"},
                    {"step_number": 3, "instruction": "Create customer account", "details": "Set up account in system"}
                ]
            }
        }
        setup_services["workflow_service"].librarian.get_document.return_value = sop_file
        
        # Execute
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test_session",
            sop_file_uuid="sop_file_123",
            client_id="client_123"
        )
        
        # Assert - Real service was used
        assert result["success"] is True
        assert "workflow" in result or "workflow_content" in result
        workflow = result.get("workflow") or result.get("workflow_content", {})
        assert "workflow_id" in workflow
        assert len(workflow.get("steps", [])) == 3
        
        # Assert - Artifact was created (Week 7)
        assert "artifact_id" in result
        assert result["status"] == "draft"
        journey_orchestrator.create_journey_artifact.assert_called_once()
        
        # Verify artifact creation call
        call_args = journey_orchestrator.create_journey_artifact.call_args
        assert call_args[1]["artifact_type"] == "workflow"
        assert call_args[1]["client_id"] == "client_123"
        assert call_args[1]["status"] == "draft"
    
    async def test_e2e_wizard_to_sop_with_artifact(
        self,
        operations_orchestrator,
        journey_orchestrator
    ):
        """E2E: Create SOP via wizard and create artifact."""
        # Step 1: Start wizard
        start_result = await operations_orchestrator.start_wizard()
        assert start_result["success"] is True
        session_token = start_result.get("session_token") or "test_wizard_session"
        
        # Step 2: Build SOP through wizard
        await operations_orchestrator.wizard_chat(session_token, "Customer Onboarding SOP")
        await operations_orchestrator.wizard_chat(session_token, "Standard procedure for onboarding new customers")
        await operations_orchestrator.wizard_chat(session_token, "Collect customer information")
        await operations_orchestrator.wizard_chat(session_token, "Verify customer identity")
        await operations_orchestrator.wizard_chat(session_token, "done")
        await operations_orchestrator.wizard_chat(session_token, "complete")
        
        # Step 3: Complete wizard and create artifact
        result = await operations_orchestrator.wizard_publish(
            session_token=session_token,
            client_id="client_123"
        )
        
        # Assert - Real service was used
        assert result["success"] is True
        assert "sop" in result or "sop_content" in result
        sop = result.get("sop") or result.get("sop_content", {})
        assert "sop_id" in sop
        assert sop["title"] == "Customer Onboarding SOP"
        assert len(sop.get("steps", [])) >= 2
        
        # Assert - Artifact was created (Week 7)
        assert "artifact_id" in result
        assert result["status"] == "draft"
        journey_orchestrator.create_journey_artifact.assert_called_once()
        
        # Verify artifact creation call
        call_args = journey_orchestrator.create_journey_artifact.call_args
        assert call_args[1]["artifact_type"] == "sop"
        assert call_args[1]["client_id"] == "client_123"
    
    async def test_e2e_coexistence_analysis_with_artifact(
        self,
        operations_orchestrator,
        journey_orchestrator
    ):
        """E2E: Analyze coexistence and create blueprint artifact."""
        sop_content = {
            "title": "Customer Onboarding SOP",
            "steps": [
                {"step_number": 1, "instruction": "Collect customer information"},
                {"step_number": 2, "instruction": "Verify customer identity"},
                {"step_number": 3, "instruction": "Create customer account"}
            ]
        }
        workflow_content = {
            "title": "Customer Onboarding Workflow",
            "steps": [
                {"step_id": "step_1", "name": "Collect customer information", "order": 1},
                {"step_id": "step_2", "name": "Verify customer identity", "order": 2},
                {"step_id": "step_3", "name": "Create customer account", "order": 3},
                {"step_id": "step_4", "name": "Send welcome email", "order": 4}
            ]
        }
        
        # Execute
        result = await operations_orchestrator.analyze_coexistence_content(
            session_token="test_session",
            sop_content=sop_content,
            workflow_content=workflow_content,
            client_id="client_123"
        )
        
        # Assert - Real service was used
        assert result["success"] is True
        assert "blueprint" in result or "coexistence_blueprint" in result
        blueprint = result.get("blueprint") or result.get("coexistence_blueprint", {})
        assert "blueprint_id" in blueprint
        assert "analysis" in blueprint
        
        # Assert - Artifact was created (Week 7)
        assert "artifact_id" in result
        assert result["status"] == "draft"
        journey_orchestrator.create_journey_artifact.assert_called_once()
        
        # Verify artifact creation call
        call_args = journey_orchestrator.create_journey_artifact.call_args
        assert call_args[1]["artifact_type"] == "coexistence_blueprint"
        assert call_args[1]["client_id"] == "client_123"
    
    async def test_e2e_full_workflow_wizard_to_coexistence(
        self,
        operations_orchestrator,
        setup_services,
        journey_orchestrator
    ):
        """E2E: Complete workflow - Wizard → SOP → Workflow → Coexistence Analysis."""
        client_id = "client_123"
        
        # Step 1: Create SOP via wizard
        start_result = await operations_orchestrator.start_wizard()
        session_token = start_result.get("session_token") or "test_wizard_session"
        
        await operations_orchestrator.wizard_chat(session_token, "Customer Onboarding SOP")
        await operations_orchestrator.wizard_chat(session_token, "Standard procedure")
        await operations_orchestrator.wizard_chat(session_token, "Collect customer information")
        await operations_orchestrator.wizard_chat(session_token, "Verify customer identity")
        await operations_orchestrator.wizard_chat(session_token, "done")
        await operations_orchestrator.wizard_chat(session_token, "complete")
        
        sop_result = await operations_orchestrator.wizard_publish(
            session_token=session_token,
            client_id=client_id
        )
        assert sop_result["success"] is True
        sop_artifact_id = sop_result["artifact_id"]
        sop_data = sop_result.get("sop") or sop_result.get("sop_content", {})
        
        # Step 2: Convert SOP to Workflow
        sop_file = {
            "document_id": "sop_file_123",
            "data": sop_data
        }
        setup_services["workflow_service"].librarian.get_document.return_value = sop_file
        
        workflow_result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test_session",
            sop_file_uuid="sop_file_123",
            client_id=client_id
        )
        assert workflow_result["success"] is True
        workflow_artifact_id = workflow_result["artifact_id"]
        workflow_data = workflow_result.get("workflow") or workflow_result.get("workflow_content", {})
        
        # Step 3: Analyze coexistence
        coexistence_result = await operations_orchestrator.analyze_coexistence_content(
            session_token="test_session",
            sop_content=sop_data,
            workflow_content=workflow_data,
            client_id=client_id
        )
        assert coexistence_result["success"] is True
        blueprint_artifact_id = coexistence_result["artifact_id"]
        
        # Assert - All artifacts created
        assert sop_artifact_id is not None
        assert workflow_artifact_id is not None
        assert blueprint_artifact_id is not None
        
        # Verify all artifact creation calls
        assert journey_orchestrator.create_journey_artifact.call_count == 3
        
        # Verify artifact types
        calls = journey_orchestrator.create_journey_artifact.call_args_list
        artifact_types = [call[1]["artifact_type"] for call in calls]
        assert "sop" in artifact_types
        assert "workflow" in artifact_types
        assert "coexistence_blueprint" in artifact_types
    
    async def test_e2e_no_hardcoded_cheats_verification(
        self,
        operations_orchestrator,
        setup_services
    ):
        """E2E: Verify no hardcoded cheats - all operations use real services."""
        # This test verifies that results come from real service logic, not hardcoded returns
        
        # Test 1: Workflow conversion produces real workflow structure
        sop_file = {
            "document_id": "sop_file_123",
            "data": {
                "title": "Test SOP",
                "steps": [
                    {"step_number": 1, "instruction": "Step A"},
                    {"step_number": 2, "instruction": "Step B"}
                ]
            }
        }
        setup_services["workflow_service"].librarian.get_document.return_value = sop_file
        
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test",
            sop_file_uuid="sop_file_123"
        )
        
        # Verify: Real conversion happened (steps converted, structure changed)
        assert result["success"] is True
        workflow = result.get("workflow") or result.get("workflow_content", {})
        assert "workflow_id" in workflow  # Generated by service
        assert workflow["conversion_type"] == "sop_to_workflow"  # Set by service
        assert workflow["source_file_uuid"] == "sop_file_123"  # From service logic
        assert len(workflow["steps"]) == 2  # Converted by service
        assert workflow["steps"][0]["step_id"] is not None  # Generated by service
        
        # Test 2: Wizard produces real SOP structure
        wizard_result = await operations_orchestrator.start_wizard()
        session_token = wizard_result.get("session_token") or "test_wizard"
        
        await operations_orchestrator.wizard_chat(session_token, "Test SOP")
        await operations_orchestrator.wizard_chat(session_token, "Test description")
        await operations_orchestrator.wizard_chat(session_token, "Test step")
        await operations_orchestrator.wizard_chat(session_token, "done")
        await operations_orchestrator.wizard_chat(session_token, "complete")
        
        sop_result = await operations_orchestrator.wizard_publish(session_token=session_token)
        
        # Verify: Real SOP structure from wizard
        assert sop_result["success"] is True
        sop = sop_result.get("sop") or sop_result.get("sop_content", {})
        assert "sop_id" in sop  # Generated by service
        assert sop["title"] == "Test SOP"  # From wizard input
        assert sop["source"] == "wizard"  # Set by service
        assert len(sop["steps"]) > 0  # From wizard steps
        
        # Test 3: Coexistence analysis produces real analysis
        coexistence_result = await operations_orchestrator.analyze_coexistence_content(
            session_token="test",
            sop_content={"title": "SOP", "steps": [{"step_number": 1, "instruction": "Step A"}]},
            workflow_content={"title": "Workflow", "steps": [{"step_id": "step_1", "name": "Step A", "order": 1}, {"step_id": "step_2", "name": "Step B", "order": 2}]}
        )
        
        # Verify: Real analysis structure
        assert coexistence_result["success"] is True
        blueprint = coexistence_result.get("blueprint") or coexistence_result.get("coexistence_blueprint", {})
        assert "blueprint_id" in blueprint  # Generated by service
        assert "analysis" in blueprint  # Created by service
        analysis = blueprint["analysis"]
        assert "sop_step_count" in analysis  # Calculated by service
        assert "workflow_step_count" in analysis  # Calculated by service
        assert analysis["workflow_step_count"] == 2  # Real count
        assert analysis["sop_step_count"] == 1  # Real count
        assert "opportunities" in analysis  # Identified by service logic







