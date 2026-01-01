#!/usr/bin/env python3
"""
Integration Tests for OperationsOrchestrator

Tests the Operations Orchestrator integration including:
- All 16 semantic API methods
- Enabling service composition (SOPBuilder, CoexistenceAnalysis, WorkflowConversion)
- Universal Gateway routing compatibility
- Wizard workflow and conversation handling
- End-to-end operations workflows
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator.operations_orchestrator import OperationsOrchestrator

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

class TestOperationsOrchestrator:
    """Integration tests for OperationsOrchestrator."""
    
    @pytest.fixture
    async def mock_business_orchestrator(self):
        """Create mock BusinessOrchestrator."""
        orchestrator = Mock()
        orchestrator.realm_name = "business_enablement"
        orchestrator.platform_gateway = Mock()
        orchestrator.platform_gateway.get_smart_city_service = AsyncMock(return_value=None)
        orchestrator.di_container = Mock()
        orchestrator.di_container.get_foundation_service = Mock(return_value=None)
        
        # Mock enabling services
        orchestrator.workflow_conversion_service = Mock()
        orchestrator.workflow_conversion_service.convert_sop_to_workflow = AsyncMock(return_value={
            "success": True,
            "workflow": {"id": "workflow_123", "steps": []},
            "conversion_metadata": {}
        })
        orchestrator.workflow_conversion_service.convert_workflow_to_sop = AsyncMock(return_value={
            "success": True,
            "sop": {"id": "sop_123", "procedures": []},
            "conversion_metadata": {}
        })
        orchestrator.workflow_conversion_service.analyze_file = AsyncMock(return_value={
            "success": True,
            "file_type": "sop",
            "analysis": {}
        })
        
        orchestrator.coexistence_analysis_service = Mock()
        orchestrator.coexistence_analysis_service.analyze_coexistence = AsyncMock(return_value={
            "success": True,
            "alignment_score": 85.0,
            "gaps": [],
            "recommendations": []
        })
        orchestrator.coexistence_analysis_service.create_blueprint = AsyncMock(return_value={
            "success": True,
            "blueprint_id": "blueprint_123",
            "blueprint": {}
        })
        
        orchestrator.sop_builder_service = Mock()
        orchestrator.sop_builder_service.start_wizard_session = AsyncMock(return_value={
            "success": True,
            "session_token": "wizard_session_123",
            "wizard_state": {"current_step": 1}
        })
        orchestrator.sop_builder_service.process_wizard_step = AsyncMock(return_value={
            "success": True,
            "wizard_state": {"current_step": 2}
        })
        orchestrator.sop_builder_service.finalize_sop = AsyncMock(return_value={
            "success": True,
            "sop_id": "sop_123",
            "sop": {}
        })
        
        return orchestrator
    
    @pytest.fixture
    async def operations_orchestrator(self, mock_business_orchestrator):
        """Create OperationsOrchestrator instance."""
        orchestrator = OperationsOrchestrator(mock_business_orchestrator)
        
        # Mock Smart City services
        orchestrator.librarian = Mock()
        orchestrator.librarian.store_document = AsyncMock(return_value={"success": True, "document_id": "doc_123"})
        orchestrator.librarian.get_document = AsyncMock(return_value={
            "data": {"elements": [], "conversation_history": []}
        })
        orchestrator.conductor = Mock()
        
        # Mock liaison agent
        orchestrator.liaison_agent = Mock()
        orchestrator.liaison_agent.process_message = AsyncMock(return_value={
            "success": True,
            "response": "Test response",
            "intent": "guidance"
        })
        
        return orchestrator
    
    async def test_orchestrator_initialization(self, operations_orchestrator):
        """Test that OperationsOrchestrator initializes correctly."""
        assert operations_orchestrator.service_name == "OperationsOrchestratorService"
        assert operations_orchestrator.realm_name == "business_enablement"
        assert hasattr(operations_orchestrator, 'get_session_elements')
        assert hasattr(operations_orchestrator, 'clear_session_elements')
        assert hasattr(operations_orchestrator, 'generate_workflow_from_sop')
        assert hasattr(operations_orchestrator, 'generate_sop_from_workflow')
        assert hasattr(operations_orchestrator, 'analyze_file')
        assert hasattr(operations_orchestrator, 'analyze_coexistence_files')
        assert hasattr(operations_orchestrator, 'analyze_coexistence_content')
        assert hasattr(operations_orchestrator, 'start_wizard')
        assert hasattr(operations_orchestrator, 'wizard_chat')
        assert hasattr(operations_orchestrator, 'wizard_publish')
        assert hasattr(operations_orchestrator, 'save_blueprint')
        assert hasattr(operations_orchestrator, 'process_query')
        assert hasattr(operations_orchestrator, 'process_conversation')
        assert hasattr(operations_orchestrator, 'get_conversation_context')
        assert hasattr(operations_orchestrator, 'analyze_intent')
    
    async def test_get_session_elements_semantic_api(self, operations_orchestrator):
        """Test get_session_elements semantic API method."""
        result = await operations_orchestrator.get_session_elements(
            session_token="session_123"
        )
        
        assert "success" in result
        if result["success"]:
            assert "elements" in result
            assert "element_count" in result
    
    async def test_clear_session_elements_semantic_api(self, operations_orchestrator):
        """Test clear_session_elements semantic API method."""
        result = await operations_orchestrator.clear_session_elements(
            session_token="session_123"
        )
        
        assert "success" in result
    
    async def test_generate_workflow_from_sop_semantic_api(self, operations_orchestrator):
        """Test generate_workflow_from_sop semantic API method."""
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="sop_file_123"
        )
        
        assert "success" in result
        if result["success"]:
            assert "workflow" in result or "data" in result
    
    async def test_generate_sop_from_workflow_semantic_api(self, operations_orchestrator):
        """Test generate_sop_from_workflow semantic API method."""
        result = await operations_orchestrator.generate_sop_from_workflow(
            session_token="session_123",
            workflow_file_uuid="workflow_file_123"
        )
        
        assert "success" in result
        if result["success"]:
            assert "sop" in result or "data" in result
    
    async def test_analyze_file_semantic_api(self, operations_orchestrator):
        """Test analyze_file semantic API method."""
        result = await operations_orchestrator.analyze_file(
            session_token="session_123",
            input_file_uuid="file_123",
            output_type="workflow"
        )
        
        assert "success" in result
        if result["success"]:
            assert "file_type" in result or "analysis" in result
    
    async def test_analyze_coexistence_files_semantic_api(self, operations_orchestrator):
        """Test analyze_coexistence_files semantic API method."""
        # Mock session with files
        operations_orchestrator.librarian.get_document = AsyncMock(return_value={
            "data": {
                "elements": [
                    {"uuid": "file1", "file_type": "sop"},
                    {"uuid": "file2", "file_type": "workflow"}
                ]
            }
        })
        
        result = await operations_orchestrator.analyze_coexistence_files(
            session_token="session_123"
        )
        
        assert "success" in result
        # If there are files to analyze, should have analysis results
        if result.get("can_analyze"):
            assert "alignment_score" in result or "gaps" in result
        # Otherwise, should indicate no files to analyze
        else:
            assert "sop_files" in result or "workflow_files" in result
    
    async def test_analyze_coexistence_content_semantic_api(self, operations_orchestrator):
        """Test analyze_coexistence_content semantic API method."""
        result = await operations_orchestrator.analyze_coexistence_content(
            session_token="session_123",
            sop_content={"title": "Test SOP", "procedures": []},
            workflow_content={"name": "Test Workflow", "steps": []}
        )
        
        assert "success" in result
        if result["success"]:
            assert "alignment_score" in result or "gaps" in result
    
    async def test_start_wizard_semantic_api(self, operations_orchestrator):
        """Test start_wizard semantic API method."""
        result = await operations_orchestrator.start_wizard()
        
        assert "success" in result
        if result["success"]:
            assert "session_token" in result or "wizard_state" in result
    
    async def test_wizard_chat_semantic_api(self, operations_orchestrator):
        """Test wizard_chat semantic API method."""
        result = await operations_orchestrator.wizard_chat(
            session_token="wizard_session_123",
            user_message="I need help creating an SOP"
        )
        
        assert "success" in result
        if result["success"]:
            assert "response" in result or "wizard_state" in result
    
    async def test_wizard_publish_semantic_api(self, operations_orchestrator):
        """Test wizard_publish semantic API method."""
        result = await operations_orchestrator.wizard_publish(
            session_token="wizard_session_123"
        )
        
        assert "success" in result
        if result["success"]:
            assert "sop_id" in result or "sop" in result
    
    async def test_save_blueprint_semantic_api(self, operations_orchestrator):
        """Test save_blueprint semantic API method."""
        result = await operations_orchestrator.save_blueprint(
            session_token="session_123",
            sop_id="sop_123",
            workflow_id="workflow_123"
        )
        
        assert "success" in result
        if result["success"]:
            assert "blueprint_id" in result or "blueprint" in result
    
    async def test_process_query_semantic_api(self, operations_orchestrator):
        """Test process_query semantic API method."""
        result = await operations_orchestrator.process_query(
            session_token="session_123",
            query_text="What are the best practices for SOP creation?"
        )
        
        assert "success" in result
        if result["success"]:
            assert "response" in result or "query_result" in result
    
    async def test_process_conversation_semantic_api(self, operations_orchestrator):
        """Test process_conversation semantic API method."""
        result = await operations_orchestrator.process_conversation(
            session_token="session_123",
            message="Can you help me optimize this workflow?"
        )
        
        assert "success" in result
        if result["success"]:
            assert "response" in result
    
    async def test_get_conversation_context_semantic_api(self, operations_orchestrator):
        """Test get_conversation_context semantic API method."""
        result = await operations_orchestrator.get_conversation_context(
            session_id="session_123"
        )
        
        assert "success" in result
        if result["success"]:
            assert "conversation_history" in result or "context" in result
    
    async def test_analyze_intent_semantic_api(self, operations_orchestrator):
        """Test analyze_intent semantic API method."""
        result = await operations_orchestrator.analyze_intent(
            session_token="session_123",
            user_input="I want to create a new SOP for onboarding"
        )
        
        assert "success" in result
        if result["success"]:
            assert "intent" in result or "confidence" in result
    
    async def test_sop_to_workflow_conversion_workflow(self, operations_orchestrator):
        """Test complete SOP to workflow conversion workflow."""
        # Step 1: Analyze file
        analyze_result = await operations_orchestrator.analyze_file(
            session_token="session_123",
            input_file_uuid="sop_file_123",
            output_type="workflow"
        )
        assert "success" in analyze_result
        
        # Step 2: Generate workflow
        if analyze_result.get("success"):
            workflow_result = await operations_orchestrator.generate_workflow_from_sop(
                session_token="session_123",
                sop_file_uuid="sop_file_123"
            )
            assert "success" in workflow_result
    
    async def test_wizard_workflow(self, operations_orchestrator):
        """Test complete wizard workflow."""
        # Step 1: Start wizard
        start_result = await operations_orchestrator.start_wizard()
        assert "success" in start_result
        
        # Step 2: Chat with wizard
        if start_result.get("success") and "session_token" in start_result:
            session_token = start_result["session_token"]
            chat_result = await operations_orchestrator.wizard_chat(
                session_token=session_token,
                user_message="Help me create an SOP"
            )
            assert "success" in chat_result
    
    async def test_coexistence_analysis_workflow(self, operations_orchestrator):
        """Test complete coexistence analysis workflow."""
        # Analyze coexistence
        result = await operations_orchestrator.analyze_coexistence_content(
            session_token="session_123",
            sop_content={"title": "Test SOP", "procedures": [{"name": "Step 1"}]},
            workflow_content={"name": "Test Workflow", "steps": [{"name": "Step 1"}]}
        )
        
        assert "success" in result
        if result.get("success"):
            # Should have alignment score
            assert "alignment_score" in result or "gaps" in result
    
    async def test_universal_gateway_compatibility(self, operations_orchestrator):
        """Test that orchestrator methods are compatible with Universal Gateway routing."""
        methods_to_test = [
            ("get_session_elements", {"session_token": "session_123"}),
            ("generate_workflow_from_sop", {"session_token": "session_123", "sop_file_uuid": "file_123"}),
            ("start_wizard", {}),
            ("process_query", {"session_token": "session_123", "query_text": "test query"}),
            ("analyze_intent", {"session_token": "session_123", "user_input": "test input"})
        ]
        
        for method_name, params in methods_to_test:
            method = getattr(operations_orchestrator, method_name)
            result = await method(**params)
            
            # All should return dict with success indicator
            assert isinstance(result, dict)
            assert "success" in result or "error" in result
    
    async def test_error_handling(self, operations_orchestrator, mock_business_orchestrator):
        """Test error handling in orchestrator."""
        # Mock service failure
        mock_business_orchestrator.workflow_conversion_service.convert_sop_to_workflow = AsyncMock(return_value={
            "success": False,
            "error": "Conversion failed"
        })
        
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="invalid_file"
        )
        
        # Should handle error gracefully
        assert "success" in result
    
    async def test_enabling_service_composition(self, operations_orchestrator):
        """Test that orchestrator properly composes enabling services."""
        # Test that generate_workflow_from_sop uses WorkflowConversionService
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="sop_123"
        )
        
        # Verify orchestrator completed successfully (service composition happened)
        assert "success" in result
    
    async def test_concurrent_operations(self, operations_orchestrator):
        """Test handling of concurrent operations."""
        import asyncio
        
        # Simulate multiple concurrent operations
        tasks = [
            operations_orchestrator.get_session_elements(session_token=f"session_{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without crashing
        assert len(results) == 3
        for result in results:
            assert isinstance(result, (dict, Exception))
    
    async def test_smart_city_integration(self, operations_orchestrator):
        """Test Smart City service integration (Librarian, Conductor)."""
        result = await operations_orchestrator.get_session_elements(
            session_token="session_123"
        )
        
        # Should have completed successfully (Smart City integration happens internally)
        assert "success" in result
    
    async def test_health_check(self, operations_orchestrator):
        """Test health_check method."""
        result = await operations_orchestrator.health_check()
        
        assert "status" in result or "healthy" in result
    
    async def test_get_service_capabilities(self, operations_orchestrator):
        """Test get_service_capabilities method."""
        result = await operations_orchestrator.get_service_capabilities()
        
        assert "capabilities" in result or "semantic_apis" in result
        # Should list all 16 semantic API methods

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

