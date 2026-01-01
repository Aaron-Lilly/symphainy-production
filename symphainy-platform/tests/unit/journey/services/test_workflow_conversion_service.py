#!/usr/bin/env python3
"""
Unit Tests for WorkflowConversionService

Tests the Workflow Conversion Service functionality including:
- Service initialization
- SOP to workflow conversion
- Workflow to SOP conversion
- File analysis
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class TestWorkflowConversionService:
    """Test WorkflowConversionService functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.get_utility = Mock(return_value=None)
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def workflow_conversion_service(self, mock_di_container, mock_platform_gateway):
        """Create WorkflowConversionService instance."""
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
        
        # Initialize service
        await service.initialize()
        
        return service
    
    @pytest.fixture
    def sample_sop_file(self):
        """Create sample SOP file document."""
        return {
            "document_id": "sop_file_123",
            "data": {
                "title": "Customer Onboarding SOP",
                "description": "Standard operating procedure for customer onboarding",
                "steps": [
                    {
                        "step_number": 1,
                        "instruction": "Collect customer information",
                        "details": "Gather name, email, phone number"
                    },
                    {
                        "step_number": 2,
                        "instruction": "Verify customer identity",
                        "details": "Check ID documents"
                    },
                    {
                        "step_number": 3,
                        "instruction": "Create customer account",
                        "details": "Set up account in system"
                    }
                ]
            },
            "metadata": {
                "file_type": "sop",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    @pytest.fixture
    def sample_workflow_file(self):
        """Create sample workflow file document."""
        return {
            "document_id": "workflow_file_123",
            "data": {
                "title": "Customer Onboarding Workflow",
                "description": "Workflow for customer onboarding process",
                "steps": [
                    {
                        "step_id": "step_1",
                        "name": "Collect customer information",
                        "description": "Gather name, email, phone number",
                        "order": 1,
                        "type": "action"
                    },
                    {
                        "step_id": "step_2",
                        "name": "Verify customer identity",
                        "description": "Check ID documents",
                        "order": 2,
                        "type": "action"
                    },
                    {
                        "step_id": "step_3",
                        "name": "Create customer account",
                        "description": "Set up account in system",
                        "order": 3,
                        "type": "action"
                    }
                ]
            },
            "metadata": {
                "file_type": "workflow",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    
    async def test_service_initialization(self, workflow_conversion_service):
        """Test service initializes correctly."""
        assert workflow_conversion_service is not None
        assert workflow_conversion_service.service_name == "WorkflowConversionService"
        assert workflow_conversion_service.realm_name == "journey"
        assert workflow_conversion_service.is_initialized is True
    
    async def test_convert_sop_to_workflow_success(self, workflow_conversion_service, sample_sop_file):
        """Test successful SOP to workflow conversion."""
        # Setup
        workflow_conversion_service.librarian.get_document.return_value = sample_sop_file
        
        # Execute
        result = await workflow_conversion_service.convert_sop_to_workflow("sop_file_123")
        
        # Assert
        assert result["success"] is True
        assert "workflow" in result
        assert "workflow_id" in result["workflow"]
        assert result["workflow"]["title"] == "Customer Onboarding SOP"
        assert len(result["workflow"]["steps"]) == 3
        assert result["workflow"]["steps"][0]["name"] == "Collect customer information"
        assert result["workflow"]["conversion_type"] == "sop_to_workflow"
        assert result["workflow"]["source_file_uuid"] == "sop_file_123"
    
    async def test_convert_sop_to_workflow_file_not_found(self, workflow_conversion_service):
        """Test SOP to workflow conversion when file not found."""
        # Setup
        workflow_conversion_service.librarian.get_document.return_value = None
        
        # Execute
        result = await workflow_conversion_service.convert_sop_to_workflow("nonexistent_file")
        
        # Assert
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    async def test_convert_sop_to_workflow_plain_text(self, workflow_conversion_service):
        """Test SOP to workflow conversion with plain text content."""
        # Setup
        plain_text_sop = {
            "document_id": "sop_file_123",
            "data": "Step 1: Collect information\nStep 2: Verify identity\nStep 3: Create account",
            "metadata": {"file_type": "sop"}
        }
        workflow_conversion_service.librarian.get_document.return_value = plain_text_sop
        
        # Execute
        result = await workflow_conversion_service.convert_sop_to_workflow("sop_file_123")
        
        # Assert
        assert result["success"] is True
        assert "workflow" in result
        assert len(result["workflow"]["steps"]) > 0
    
    async def test_convert_workflow_to_sop_success(self, workflow_conversion_service, sample_workflow_file):
        """Test successful workflow to SOP conversion."""
        # Setup
        workflow_conversion_service.librarian.get_document.return_value = sample_workflow_file
        
        # Execute
        result = await workflow_conversion_service.convert_workflow_to_sop("workflow_file_123")
        
        # Assert
        assert result["success"] is True
        assert "sop" in result
        assert "sop_id" in result["sop"]
        assert result["sop"]["title"] == "Customer Onboarding Workflow"
        assert len(result["sop"]["steps"]) == 3
        assert result["sop"]["steps"][0]["instruction"] == "Collect customer information"
        assert result["sop"]["conversion_type"] == "workflow_to_sop"
        assert result["sop"]["source_file_uuid"] == "workflow_file_123"
    
    async def test_convert_workflow_to_sop_file_not_found(self, workflow_conversion_service):
        """Test workflow to SOP conversion when file not found."""
        # Setup
        workflow_conversion_service.librarian.get_document.return_value = None
        
        # Execute
        result = await workflow_conversion_service.convert_workflow_to_sop("nonexistent_file")
        
        # Assert
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    async def test_analyze_file_to_workflow(self, workflow_conversion_service, sample_sop_file):
        """Test file analysis converting to workflow."""
        # Setup
        workflow_conversion_service.librarian.get_document.return_value = sample_sop_file
        
        # Execute
        result = await workflow_conversion_service.analyze_file("sop_file_123", "workflow")
        
        # Assert
        assert result["success"] is True
        assert "workflow" in result
    
    async def test_analyze_file_to_sop(self, workflow_conversion_service, sample_workflow_file):
        """Test file analysis converting to SOP."""
        # Setup
        workflow_conversion_service.librarian.get_document.return_value = sample_workflow_file
        
        # Execute
        result = await workflow_conversion_service.analyze_file("workflow_file_123", "sop")
        
        # Assert
        assert result["success"] is True
        assert "sop" in result
    
    async def test_analyze_file_invalid_output_type(self, workflow_conversion_service):
        """Test file analysis with invalid output type."""
        # Execute
        result = await workflow_conversion_service.analyze_file("file_123", "invalid_type")
        
        # Assert
        assert result["success"] is False
        assert "invalid" in result["error"].lower()
    
    async def test_convert_sop_to_workflow_no_librarian(self, mock_di_container, mock_platform_gateway):
        """Test conversion when Librarian is not available."""
        service = WorkflowConversionService(
            service_name="WorkflowConversionService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock methods
        service.get_librarian_api = AsyncMock(return_value=None)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        await service.initialize()
        
        # Execute
        result = await service.convert_sop_to_workflow("sop_file_123")
        
        # Assert
        assert result["success"] is False
        assert "not available" in result["error"].lower()
    
    async def test_get_service_capabilities(self, workflow_conversion_service):
        """Test service capabilities retrieval."""
        # Execute
        capabilities = await workflow_conversion_service.get_service_capabilities()
        
        # Assert
        assert capabilities["service_name"] == "WorkflowConversionService"
        assert capabilities["realm"] == "journey"
        assert "workflow_conversion" in capabilities["capabilities"]
        assert "convert_sop_to_workflow" in capabilities["soa_apis"]







