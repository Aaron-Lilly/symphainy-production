#!/usr/bin/env python3
"""
Workflow Manager Service Functionality Tests

Tests Workflow Manager Service core functionality:
- Workflow execution
- Workflow status retrieval
- Task scheduling

Uses mock Workflow Orchestration Abstraction.
"""

# Path is configured in pytest.ini - no manipulation needed

import pytest

from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

from tests.fixtures.test_datasets import get_sample_workflow_definition
from bases.contracts.workflow_orchestration import WorkflowStatus

@pytest.mark.business_enablement
@pytest.mark.functional
class TestWorkflowManagerServiceFunctionality:
    """Test Workflow Manager Service functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_workflow_orchestration(self):
        """Create mock Workflow Orchestration Abstraction."""
        mock_abstraction = Mock()
        mock_abstraction.create_workflow = AsyncMock(return_value="test_workflow_001")
        mock_abstraction.execute_workflow = AsyncMock(return_value="test_execution_001")
        mock_abstraction.get_execution_status = AsyncMock(return_value=WorkflowStatus.RUNNING)
        mock_abstraction.get_execution_result = AsyncMock(return_value={"result": "success"})
        return mock_abstraction
    
    @pytest.fixture
    def mock_conductor(self):
        """Create mock Conductor API."""
        mock_api = Mock()
        mock_api.create_workflow = AsyncMock(return_value={"workflow_id": "test_workflow_001"})
        mock_api.execute_workflow = AsyncMock(return_value={"execution_id": "test_execution_001"})
        return mock_api
    
    @pytest.fixture
    async def workflow_manager_service(self, mock_di_container, mock_platform_gateway, mock_workflow_orchestration, mock_conductor):
        """Create Workflow Manager Service instance."""
        # Path is already set at module level, but ensure it's in sys.path
        # project_root is already absolute, just ensure it's added
        from backend.business_enablement.enabling_services.workflow_manager_service.workflow_manager_service import WorkflowManagerService
        
        # Set up mocks
        mock_platform_gateway.get_abstraction.return_value = mock_workflow_orchestration
        
        service = WorkflowManagerService(
            service_name="WorkflowManagerService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City APIs
        service.conductor = mock_conductor
        service.librarian = Mock()
        service.data_steward = Mock()
        service.workflow_orchestration = mock_workflow_orchestration
        
        # Mock RealmServiceBase methods
        service.store_document = AsyncMock(return_value={"document_id": "test_doc_001"})
        service.retrieve_document = AsyncMock(return_value={"data": {}, "metadata": {}})
        service.track_data_lineage = AsyncMock(return_value=True)
        
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, workflow_manager_service, mock_workflow_orchestration):
        """Test workflow execution."""
        workflow_def = get_sample_workflow_definition()
        
        result = await workflow_manager_service.execute_workflow(
            workflow_definition=workflow_def,
            context={"test": "data"}
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert "success" in result or "workflow_id" in result or "execution_id" in result
    
    @pytest.mark.asyncio
    async def test_get_workflow_status(self, workflow_manager_service, mock_workflow_orchestration):
        """Test workflow status retrieval."""
        workflow_id = "test_workflow_001"
        
        # Add to active_workflows for testing
        workflow_manager_service.active_workflows[workflow_id] = {
            "execution_id": "test_execution_001",
            "status": "running",
            "started_at": "2024-01-01T00:00:00"
        }
        
        status = await workflow_manager_service.get_workflow_status(workflow_id)
        
        assert status is not None
        assert isinstance(status, dict)
        assert "status" in status or "workflow_id" in status
