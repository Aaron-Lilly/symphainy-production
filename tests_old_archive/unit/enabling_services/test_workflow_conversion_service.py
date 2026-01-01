#!/usr/bin/env python3
"""
Unit Tests for WorkflowConversionService

Tests the Workflow Conversion enabling service functionality including:
- Service initialization
- SOP to Workflow conversion
- Workflow to SOP conversion
- File analysis
- Conversion validation
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.business_enablement.enabling_services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
from utilities import UserContext

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

class TestWorkflowConversionService:
    """Test WorkflowConversionService functionality."""
    
    @pytest.fixture
    async def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        return container
    
    @pytest.fixture
    async def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def workflow_conversion_service(self, mock_di_container, mock_platform_gateway):
        """Create WorkflowConversionService instance."""
        service = WorkflowConversionService(
            service_name="WorkflowConversionService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services to avoid initialization issues
        service.librarian = Mock()
        service.librarian.store_document = AsyncMock(return_value={"success": True})
        service.librarian.get_document = AsyncMock(return_value=None)
        service.data_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        
        return service
    
    @pytest.fixture
    def sample_user_context(self):
        """Create sample user context."""
        return UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["read", "write"],
            tenant_id="test_tenant_456"
        )
    
    @pytest.fixture
    def sample_sop_content(self):
        """Create sample SOP content."""
        return """
        Title: Software Testing Standard Operating Procedure
        Purpose: Define comprehensive testing procedures
        
        Procedures:
        1. Review requirements and test plan
        2. Set up test environment
        3. Execute test cases
        4. Document test results
        5. Perform peer review
        
        Scope: All software components
        Responsibilities: QA Team
        """
    
    @pytest.fixture
    def sample_workflow_data(self):
        """Create sample workflow data."""
        return {
            "workflow_id": "wf_test_123",
            "name": "Software Testing Workflow",
            "steps": [
                {"step": 1, "action": "Review requirements", "responsible": "QA Lead"},
                {"step": 2, "action": "Setup environment", "responsible": "DevOps"},
                {"step": 3, "action": "Execute tests", "responsible": "QA Engineer"},
                {"step": 4, "action": "Document results", "responsible": "QA Engineer"}
            ]
        }
    
    async def test_service_initialization(self, workflow_conversion_service):
        """Test that WorkflowConversionService initializes correctly."""
        assert workflow_conversion_service.service_name == "WorkflowConversionService"
        assert workflow_conversion_service.realm_name == "business_enablement"
    
    async def test_convert_sop_to_workflow_success(self, workflow_conversion_service, sample_sop_content, sample_user_context):
        """Test successful SOP to Workflow conversion."""
        # Mock librarian to return SOP content
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"content": sample_sop_content}
        })
        
        result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid="sop_test_123",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "workflow" in result
        assert "workflow_id" in result
        assert "sop_text" in result
        assert "processing_time" in result
        assert "session_state" in result
        assert result["session_state"]["has_workflow"] is True
    
    async def test_convert_sop_to_workflow_not_found(self, workflow_conversion_service, sample_user_context):
        """Test SOP to Workflow conversion with missing SOP."""
        # Mock librarian to return None
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value=None)
        
        result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid="non_existent_sop",
            user_context=sample_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    async def test_convert_workflow_to_sop_success(self, workflow_conversion_service, sample_workflow_data, sample_user_context):
        """Test successful Workflow to SOP conversion."""
        # Mock librarian to return workflow data
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"workflow": sample_workflow_data}
        })
        
        result = await workflow_conversion_service.convert_workflow_to_sop(
            workflow_file_uuid="wf_test_123",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "sop" in result
        assert "sop_id" in result
        assert "workflow_text" in result
        assert "processing_time" in result
        assert "session_state" in result
        assert result["session_state"]["has_sop"] is True
    
    async def test_convert_workflow_to_sop_not_found(self, workflow_conversion_service, sample_user_context):
        """Test Workflow to SOP conversion with missing workflow."""
        # Mock librarian to return None
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value=None)
        
        result = await workflow_conversion_service.convert_workflow_to_sop(
            workflow_file_uuid="non_existent_workflow",
            user_context=sample_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    async def test_analyze_file_to_workflow(self, workflow_conversion_service, sample_sop_content, sample_user_context):
        """Test file analysis with workflow output type."""
        # Mock librarian to return SOP content
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"content": sample_sop_content}
        })
        
        result = await workflow_conversion_service.analyze_file(
            input_file_uuid="file_test_123",
            output_type="workflow",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "workflow" in result
    
    async def test_analyze_file_to_sop(self, workflow_conversion_service, sample_workflow_data, sample_user_context):
        """Test file analysis with SOP output type."""
        # Mock librarian to return workflow data
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"workflow": sample_workflow_data}
        })
        
        result = await workflow_conversion_service.analyze_file(
            input_file_uuid="file_test_123",
            output_type="sop",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "sop" in result
    
    async def test_analyze_file_invalid_output_type(self, workflow_conversion_service, sample_user_context):
        """Test file analysis with invalid output type."""
        result = await workflow_conversion_service.analyze_file(
            input_file_uuid="file_test_123",
            output_type="invalid_type",
            user_context=sample_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "unknown output type" in result["error"].lower()
    
    async def test_validate_conversion_not_found(self, workflow_conversion_service, sample_user_context):
        """Test conversion validation with non-existent conversion."""
        # Mock librarian to return None
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value=None)
        
        result = await workflow_conversion_service.validate_conversion(
            conversion_id="non_existent_conversion",
            user_context=sample_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_validate_conversion_success(self, workflow_conversion_service, sample_user_context):
        """Test successful conversion validation."""
        # Mock librarian to return conversion data
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {
                "conversion_id": "test_conversion_123",
                "source_type": "sop",
                "target_type": "workflow",
                "workflow": {
                    "steps": [{"step": 1, "action": "Test"}]
                }
            }
        })
        
        result = await workflow_conversion_service.validate_conversion(
            conversion_id="test_conversion_123",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "valid" in result
        assert "validation_score" in result
        assert "errors" in result
        assert "warnings" in result
    
    async def test_parse_sop_steps(self, workflow_conversion_service, sample_sop_content):
        """Test SOP step parsing."""
        steps = workflow_conversion_service._parse_sop_steps(sample_sop_content)
        
        assert isinstance(steps, list)
        assert len(steps) > 0
        # Sample SOP has 5 numbered procedures
        assert len(steps) >= 5
    
    async def test_generate_workflow_from_steps(self, workflow_conversion_service):
        """Test workflow generation from steps."""
        steps = [
            {"step": 1, "description": "Review requirements", "action": "Review requirements", "responsible": "Team Lead"},
            {"step": 2, "description": "Setup environment", "action": "Setup environment", "responsible": "DevOps"},
            {"step": 3, "description": "Execute tests", "action": "Execute tests", "responsible": "QA"},
            {"step": 4, "description": "Document results", "action": "Document results", "responsible": "QA"}
        ]
        
        workflow = workflow_conversion_service._generate_workflow_from_steps(
            steps, source_sop_uuid="sop_test_123"
        )
        
        assert "name" in workflow
        assert "steps" in workflow
        assert len(workflow["steps"]) == len(steps)
        assert "metadata" in workflow
        assert workflow["metadata"]["source_sop_uuid"] == "sop_test_123"
    
    async def test_generate_sop_from_workflow(self, workflow_conversion_service, sample_workflow_data):
        """Test SOP generation from workflow."""
        sop = workflow_conversion_service._generate_sop_from_workflow(
            sample_workflow_data, source_workflow_uuid="wf_test_123"
        )
        
        assert "title" in sop
        assert "procedures" in sop
        assert "metadata" in sop
        assert sop["metadata"]["source"] == "workflow_conversion"
        assert len(sop["procedures"]) == len(sample_workflow_data["steps"])
    
    async def test_empty_sop_content(self, workflow_conversion_service, sample_user_context):
        """Test conversion with empty SOP content."""
        # Mock librarian to return empty content
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"content": ""}
        })
        
        result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid="empty_sop",
            user_context=sample_user_context
        )
        
        # Should still complete (may generate minimal workflow)
        assert "success" in result
    
    async def test_empty_workflow_data(self, workflow_conversion_service, sample_user_context):
        """Test conversion with empty workflow data."""
        # Mock librarian to return empty workflow
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"workflow": {"steps": []}}
        })
        
        result = await workflow_conversion_service.convert_workflow_to_sop(
            workflow_file_uuid="empty_workflow",
            user_context=sample_user_context
        )
        
        # Should still complete (may generate minimal SOP)
        assert "success" in result
    
    async def test_complex_sop_with_multiple_sections(self, workflow_conversion_service, sample_user_context):
        """Test conversion of complex SOP with multiple sections."""
        complex_sop = """
        Title: Complex Testing Procedure
        Purpose: Comprehensive testing
        
        Section 1: Preparation
        1. Review requirements
        2. Setup environment
        
        Section 2: Execution
        3. Run unit tests
        4. Run integration tests
        5. Run system tests
        
        Section 3: Reporting
        6. Generate reports
        7. Review with team
        """
        
        # Mock librarian to return complex SOP
        workflow_conversion_service.librarian.get_document = AsyncMock(return_value={
            "data": {"content": complex_sop}
        })
        
        result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_uuid="complex_sop",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "workflow" in result
        # Should extract all numbered steps (7 in this case)
        assert len(result["workflow"]["steps"]) >= 7

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

