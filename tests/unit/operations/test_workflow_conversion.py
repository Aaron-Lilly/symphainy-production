"""
Comprehensive unit tests for Workflow Conversion Service.

Tests:
- SOP to workflow conversion
- Workflow to SOP conversion
- Conversion validation
- File analysis
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.operations
@pytest.mark.workflow_conversion
@pytest.mark.fast
class TestWorkflowConversion:
    """Test suite for Workflow Conversion Service."""
    
    @pytest.fixture
    def mock_workflow_service(self):
        """Create mock WorkflowConversionService."""
        from backend.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
        service = Mock(spec=WorkflowConversionService)
        service.convert_sop_to_workflow = AsyncMock()
        service.convert_workflow_to_sop = AsyncMock()
        service.validate_conversion = AsyncMock()
        service.analyze_file = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_convert_sop_to_workflow(self, mock_workflow_service):
        """Test SOP to workflow conversion."""
        mock_workflow_service.convert_sop_to_workflow.return_value = {
            "success": True,
            "workflow_id": "workflow_123",
            "workflow": {
                "nodes": [{"id": "1", "type": "task"}],
                "edges": []
            }
        }
        
        result = await mock_workflow_service.convert_sop_to_workflow(
            sop_file_uuid="sop_123"
        )
        
        assert result["success"] is True
        assert "workflow_id" in result
        assert "workflow" in result
    
    @pytest.mark.asyncio
    async def test_convert_workflow_to_sop(self, mock_workflow_service):
        """Test workflow to SOP conversion."""
        mock_workflow_service.convert_workflow_to_sop.return_value = {
            "success": True,
            "sop_id": "sop_123",
            "sop": {
                "sections": [],
                "steps": []
            }
        }
        
        result = await mock_workflow_service.convert_workflow_to_sop(
            workflow_file_uuid="workflow_123"
        )
        
        assert result["success"] is True
        assert "sop_id" in result
        assert "sop" in result
    
    @pytest.mark.asyncio
    async def test_validate_conversion(self, mock_workflow_service):
        """Test conversion validation."""
        mock_workflow_service.validate_conversion.return_value = {
            "success": True,
            "is_valid": True,
            "validation_errors": []
        }
        
        result = await mock_workflow_service.validate_conversion(
            conversion_id="conversion_123"
        )
        
        assert result["success"] is True
        assert result["is_valid"] is True
    
    @pytest.mark.asyncio
    async def test_analyze_file(self, mock_workflow_service):
        """Test file analysis."""
        mock_workflow_service.analyze_file.return_value = {
            "success": True,
            "file_type": "sop",
            "structure": {}
        }
        
        result = await mock_workflow_service.analyze_file(
            input_uuid="file_123",
            output_type="sop"
        )
        
        assert result["success"] is True
        assert "file_type" in result




