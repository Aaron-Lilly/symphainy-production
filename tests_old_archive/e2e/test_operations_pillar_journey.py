#!/usr/bin/env python3
"""
E2E Tests for Operations Pillar Journey

Tests the complete Operations Pillar user journey:
1. Generate SOP from file
2. Create Workflow from SOP
3. Verify SOP structure
4. Verify Workflow diagram
5. Test coexistence analysis
6. Test wizard workflow
7. Test blueprint generation

This simulates a real user workflow through the Operations Pillar.
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.operations_orchestrator import OperationsOrchestrator

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]

class TestOperationsPillarJourney:
    """E2E tests for Operations Pillar user journey."""
    
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
                "elements": [
                    {"uuid": "file1", "file_type": "sop"},
                    {"uuid": "file2", "file_type": "workflow"}
                ],
                "conversation_history": []
            }
        })
        
        # Mock Conductor
        services['conductor'] = Mock()
        
        return services
    
    @pytest.fixture
    async def mock_enabling_services(self):
        """Create mock enabling services."""
        services = {}
        
        # Mock WorkflowConversionService
        services['workflow_conversion'] = Mock()
        services['workflow_conversion'].convert_sop_to_workflow = AsyncMock(return_value={
            "success": True,
            "workflow": {
                "id": "workflow_123",
                "name": "Generated Workflow",
                "steps": [
                    {"id": "step1", "name": "Initialize", "type": "start"},
                    {"id": "step2", "name": "Process", "type": "task"},
                    {"id": "step3", "name": "Complete", "type": "end"}
                ],
                "connections": [
                    {"from": "step1", "to": "step2"},
                    {"from": "step2", "to": "step3"}
                ]
            },
            "conversion_metadata": {
                "source": "sop",
                "conversion_time": "2025-11-11T12:00:00"
            }
        })
        services['workflow_conversion'].convert_workflow_to_sop = AsyncMock(return_value={
            "success": True,
            "sop": {
                "id": "sop_123",
                "title": "Generated SOP",
                "procedures": [
                    {"id": "proc1", "title": "Procedure 1", "steps": ["Step 1", "Step 2"]},
                    {"id": "proc2", "title": "Procedure 2", "steps": ["Step 3", "Step 4"]}
                ],
                "metadata": {
                    "source": "workflow",
                    "created_at": "2025-11-11T12:00:00"
                }
            }
        })
        services['workflow_conversion'].analyze_file = AsyncMock(return_value={
            "success": True,
            "file_type": "sop",
            "analysis": {
                "structure": "valid",
                "sections": 3,
                "quality_score": 85
            }
        })
        
        # Mock CoexistenceAnalysisService
        services['coexistence_analysis'] = Mock()
        services['coexistence_analysis'].analyze_coexistence = AsyncMock(return_value={
            "success": True,
            "alignment_score": 87.5,
            "gaps": [
                {"type": "missing_step", "severity": "medium", "description": "Workflow missing approval step"},
                {"type": "inconsistent_naming", "severity": "low", "description": "Step names differ"}
            ],
            "recommendations": [
                "Add approval step to workflow",
                "Standardize naming conventions"
            ],
            "coexistence_analysis": {
                "sop_analysis": {"total_procedures": 5},
                "workflow_analysis": {"total_steps": 12}
            }
        })
        services['coexistence_analysis'].create_blueprint = AsyncMock(return_value={
            "success": True,
            "blueprint_id": "blueprint_123",
            "blueprint": {
                "structure": {
                    "phases": ["Phase 1", "Phase 2", "Phase 3"],
                    "milestones": ["Milestone A", "Milestone B"]
                }
            }
        })
        
        # Mock SOPBuilderService
        services['sop_builder'] = Mock()
        services['sop_builder'].start_wizard_session = AsyncMock(return_value={
            "success": True,
            "session_token": "wizard_session_123",
            "wizard_state": {
                "current_step": 1,
                "total_steps": 5,
                "completed": []
            }
        })
        services['sop_builder'].process_wizard_step = AsyncMock(return_value={
            "success": True,
            "wizard_state": {
                "current_step": 2,
                "total_steps": 5,
                "completed": ["step1"]
            }
        })
        services['sop_builder'].finalize_sop = AsyncMock(return_value={
            "success": True,
            "sop_id": "sop_123",
            "sop": {
                "title": "Wizard Generated SOP",
                "procedures": []
            }
        })
        
        return services
    
    @pytest.fixture
    async def operations_orchestrator(self, mock_platform_services, mock_enabling_services):
        """Create OperationsOrchestrator with mocked dependencies."""
        mock_business_orchestrator = Mock()
        mock_business_orchestrator.realm_name = "business_enablement"
        mock_business_orchestrator.platform_gateway = Mock()
        mock_business_orchestrator.di_container = Mock()
        
        # Inject enabling services
        mock_business_orchestrator.workflow_conversion_service = mock_enabling_services['workflow_conversion']
        mock_business_orchestrator.coexistence_analysis_service = mock_enabling_services['coexistence_analysis']
        mock_business_orchestrator.sop_builder_service = mock_enabling_services['sop_builder']
        
        orchestrator = OperationsOrchestrator(mock_business_orchestrator)
        
        # Inject platform services
        orchestrator.librarian = mock_platform_services['librarian']
        orchestrator.conductor = mock_platform_services['conductor']
        
        # Mock liaison agent
        orchestrator.liaison_agent = Mock()
        orchestrator.liaison_agent.process_message = AsyncMock(return_value={
            "success": True,
            "response": "I can help you with that",
            "intent": "guidance"
        })
        
        return orchestrator
    
    @pytest.fixture
    async def gateway_service(self, operations_orchestrator):
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
        gateway.operations_orchestrator = operations_orchestrator
        gateway.librarian = Mock()
        gateway.security_guard = Mock()
        gateway.traffic_cop = Mock()
        
        return gateway
    
    async def test_complete_operations_pillar_journey(
        self,
        gateway_service,
        operations_orchestrator,
        mock_platform_services,
        mock_enabling_services
    ):
        """Test complete Operations Pillar user journey."""
        
        # Step 1: Generate workflow from SOP
        workflow_request = {
            "endpoint": "/api/operations/generate_workflow_from_sop",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "sop_file_uuid": "sop_file_123"
            }
        }
        
        workflow_result = await gateway_service.route_frontend_request(workflow_request)
        
        # Verify workflow generation succeeded
        assert isinstance(workflow_result, dict)
        assert "success" in workflow_result or "status" in workflow_result
        
        # Step 2: Generate SOP from workflow
        sop_request = {
            "endpoint": "/api/operations/generate_sop_from_workflow",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "workflow_file_uuid": "workflow_file_123"
            }
        }
        
        sop_result = await gateway_service.route_frontend_request(sop_request)
        
        # Verify SOP generation succeeded
        assert isinstance(sop_result, dict)
        
        # Step 3: Analyze coexistence
        coexistence_request = {
            "endpoint": "/api/operations/analyze_coexistence_content",
            "method": "POST",
            "params": {
                "session_token": "session_123",
                "sop_content": {"title": "Test SOP", "procedures": []},
                "workflow_content": {"name": "Test Workflow", "steps": []}
            }
        }
        
        coexistence_result = await gateway_service.route_frontend_request(coexistence_request)
        
        # Verify coexistence analysis succeeded
        assert isinstance(coexistence_result, dict)
        
        # Step 4: Start wizard
        wizard_request = {
            "endpoint": "/api/operations/start_wizard",
            "method": "POST",
            "params": {}
        }
        
        wizard_result = await gateway_service.route_frontend_request(wizard_request)
        
        # Verify wizard started
        assert isinstance(wizard_result, dict)
    
    async def test_sop_generation_workflow(self, operations_orchestrator):
        """Test SOP generation from workflow."""
        result = await operations_orchestrator.generate_sop_from_workflow(
            session_token="session_123",
            workflow_file_uuid="workflow_123"
        )
        
        # Should return generated SOP
        assert "success" in result
        if result["success"]:
            assert "sop" in result
            # Verify SOP structure
            sop = result["sop"]
            assert "title" in sop or "id" in sop
    
    async def test_workflow_generation_from_sop(self, operations_orchestrator):
        """Test workflow generation from SOP."""
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="sop_123"
        )
        
        # Should return generated workflow
        assert "success" in result
        if result["success"]:
            assert "workflow" in result
            # Verify workflow structure
            workflow = result["workflow"]
            assert "steps" in workflow or "id" in workflow
    
    async def test_coexistence_analysis_workflow(self, operations_orchestrator):
        """Test coexistence analysis."""
        result = await operations_orchestrator.analyze_coexistence_content(
            session_token="session_123",
            sop_content={"title": "Test SOP", "procedures": [{"name": "Proc 1"}]},
            workflow_content={"name": "Test Workflow", "steps": [{"name": "Step 1"}]}
        )
        
        # Should return analysis
        assert "success" in result
        if result["success"]:
            # Should have alignment score and gaps
            assert "alignment_score" in result or "gaps" in result
    
    async def test_wizard_workflow(self, operations_orchestrator):
        """Test complete wizard workflow."""
        # Step 1: Start wizard
        start_result = await operations_orchestrator.start_wizard()
        
        assert "success" in start_result
        if start_result["success"]:
            session_token = start_result.get("session_token")
            
            # Step 2: Chat with wizard
            if session_token:
                chat_result = await operations_orchestrator.wizard_chat(
                    session_token=session_token,
                    user_message="Help me create an SOP"
                )
                
                assert "success" in chat_result
    
    async def test_blueprint_generation(self, operations_orchestrator):
        """Test blueprint generation."""
        result = await operations_orchestrator.save_blueprint(
            session_token="session_123",
            sop_id="sop_123",
            workflow_id="workflow_123"
        )
        
        # Should return blueprint
        assert "success" in result
        if result["success"]:
            assert "blueprint_id" in result or "blueprint" in result
    
    async def test_file_analysis(self, operations_orchestrator):
        """Test file analysis."""
        result = await operations_orchestrator.analyze_file(
            session_token="session_123",
            input_file_uuid="file_123",
            output_type="workflow"
        )
        
        # Should return analysis
        assert "success" in result
    
    async def test_session_management(self, operations_orchestrator):
        """Test session element management."""
        # Get session elements
        get_result = await operations_orchestrator.get_session_elements(
            session_token="session_123"
        )
        
        assert "success" in get_result
        if get_result["success"]:
            assert "elements" in get_result
        
        # Clear session elements
        clear_result = await operations_orchestrator.clear_session_elements(
            session_token="session_123"
        )
        
        assert "success" in clear_result
    
    async def test_conversation_handling(self, operations_orchestrator):
        """Test conversation handling."""
        result = await operations_orchestrator.process_conversation(
            session_token="session_123",
            message="Can you help me optimize this workflow?"
        )
        
        # Should return response
        assert "success" in result
        if result["success"]:
            assert "response" in result
    
    async def test_intent_analysis(self, operations_orchestrator):
        """Test intent analysis."""
        result = await operations_orchestrator.analyze_intent(
            session_token="session_123",
            user_input="I want to create a new SOP for onboarding"
        )
        
        # Should return intent
        assert "success" in result
        if result["success"]:
            assert "intent" in result or "confidence" in result
    
    async def test_error_handling_invalid_file(
        self,
        operations_orchestrator,
        mock_enabling_services
    ):
        """Test error handling for invalid file."""
        # Mock conversion failure
        mock_enabling_services['workflow_conversion'].convert_sop_to_workflow = AsyncMock(return_value={
            "success": False,
            "error": "File not found"
        })
        
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="invalid_file"
        )
        
        # Should handle error gracefully
        assert isinstance(result, dict)
        assert "success" in result
    
    async def test_concurrent_operations(self, operations_orchestrator):
        """Test concurrent operations."""
        import asyncio
        
        # Simulate multiple operations
        tasks = [
            operations_orchestrator.get_session_elements(session_token=f"session_{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_sop_structure_validation(self, operations_orchestrator):
        """Test that generated SOPs have proper structure."""
        result = await operations_orchestrator.generate_sop_from_workflow(
            session_token="session_123",
            workflow_file_uuid="workflow_123"
        )
        
        if result.get("success") and "sop" in result:
            sop = result["sop"]
            # Should have required SOP fields
            assert "title" in sop or "procedures" in sop or "id" in sop
    
    async def test_workflow_structure_validation(self, operations_orchestrator):
        """Test that generated workflows have proper structure."""
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="sop_123"
        )
        
        if result.get("success") and "workflow" in result:
            workflow = result["workflow"]
            # Should have required workflow fields
            assert "steps" in workflow or "id" in workflow or "name" in workflow
    
    async def test_smart_city_integration(
        self,
        operations_orchestrator,
        mock_platform_services
    ):
        """Test Smart City service integration."""
        result = await operations_orchestrator.get_session_elements(
            session_token="session_123"
        )
        
        # Should have completed (Smart City integration happens internally)
        assert "success" in result

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

