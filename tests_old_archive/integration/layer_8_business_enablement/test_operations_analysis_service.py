#!/usr/bin/env python3
"""
Functional tests for OperationsAnalysisService.

Tests workflow analysis and visualization capabilities.
Note: This service does NOT execute workflows - that's Conductor Service's responsibility.
"""

import pytest
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestOperationsAnalysisServiceFunctional:
    """Functional tests for OperationsAnalysisService."""
    
    @pytest.fixture(scope="function")
    async def operations_analysis_service(self, smart_city_infrastructure):
        """Create OperationsAnalysisService instance."""
        from backend.business_enablement.enabling_services.operations_analysis_service import OperationsAnalysisService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        di_container = smart_city_infrastructure["di_container"]
        
        service = OperationsAnalysisService(
            service_name="OperationsAnalysisService",
            realm_name="business_enablement",
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        
        initialized = await service.initialize()
        assert initialized, "OperationsAnalysisService should initialize successfully"
        
        return service
    
    @pytest.fixture(scope="function")
    def mock_user_context(self) -> Dict[str, Any]:
        """Create a mock user context."""
        return {
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_123",
            "email": "test@example.com",
            "permissions": ["read", "write"]
        }
    
    @pytest.fixture(scope="function")
    def sample_workflow_definition(self) -> Dict[str, Any]:
        """Create a sample workflow definition for testing."""
        return {
            "name": "Test Workflow",
            "description": "A test workflow for analysis",
            "steps": [
                {
                    "id": "step_1",
                    "name": "Start Process",
                    "description": "Initialize the process",
                    "properties": {"type": "start"}
                },
                {
                    "id": "step_2",
                    "name": "Process Data",
                    "description": "Process the input data",
                    "properties": {"type": "task"}
                },
                {
                    "id": "step_3",
                    "name": "End Process",
                    "description": "Complete the process",
                    "properties": {"type": "end"}
                }
            ]
        }
    
    async def test_service_initialization(self, operations_analysis_service):
        """Test that OperationsAnalysisService initializes correctly."""
        assert operations_analysis_service is not None
        assert operations_analysis_service.is_initialized is True
        assert operations_analysis_service.workflow_diagramming_orchestration is not None
        assert operations_analysis_service.bpmn_processing is not None
        assert operations_analysis_service.librarian is not None
        assert operations_analysis_service.data_steward is not None
        
        logger.info("✅ OperationsAnalysisService initialized correctly")
    
    async def test_visualize_workflow_basic(
        self,
        operations_analysis_service,
        sample_workflow_definition,
        mock_user_context
    ):
        """Test basic workflow visualization."""
        result = await operations_analysis_service.visualize_workflow(
            workflow_definition=sample_workflow_definition,
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "workflow_id" in result
        assert "visualization_id" in result
        assert "visualization" in result or "definition_id" in result
        
        logger.info(f"✅ Workflow visualized successfully: {result.get('workflow_id')}")
    
    async def test_visualize_workflow_without_steps(
        self,
        operations_analysis_service,
        mock_user_context
    ):
        """Test workflow visualization with invalid definition (no steps)."""
        invalid_workflow = {
            "name": "Invalid Workflow",
            "description": "Workflow without steps"
        }
        
        result = await operations_analysis_service.visualize_workflow(
            workflow_definition=invalid_workflow,
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "steps" in result.get("message", "").lower() or "must have" in result.get("message", "").lower()
        
        logger.info("✅ Invalid workflow correctly rejected")
    
    async def test_get_workflow_analysis(
        self,
        operations_analysis_service,
        sample_workflow_definition,
        mock_user_context
    ):
        """Test retrieving workflow analysis."""
        # First, visualize a workflow
        visualize_result = await operations_analysis_service.visualize_workflow(
            workflow_definition=sample_workflow_definition,
            user_context=mock_user_context
        )
        
        assert visualize_result.get("success") is True
        workflow_id = visualize_result.get("workflow_id")
        
        # Then, get the analysis
        analysis_result = await operations_analysis_service.get_workflow_analysis(
            workflow_id=workflow_id,
            user_context=mock_user_context
        )
        
        assert isinstance(analysis_result, dict)
        assert analysis_result.get("success") is True
        assert analysis_result.get("workflow_id") == workflow_id
        assert "status" in analysis_result or "visualization" in analysis_result
        
        logger.info(f"✅ Workflow analysis retrieved successfully: {workflow_id}")
    
    async def test_get_workflow_analysis_not_found(
        self,
        operations_analysis_service,
        mock_user_context
    ):
        """Test retrieving analysis for non-existent workflow."""
        result = await operations_analysis_service.get_workflow_analysis(
            workflow_id="nonexistent_workflow_123",
            user_context=mock_user_context
        )
        
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "not found" in result.get("message", "").lower()
        
        logger.info("✅ Non-existent workflow correctly handled")
    
    async def test_visualize_workflow_security_validation(
        self,
        operations_analysis_service,
        sample_workflow_definition
    ):
        """Test that workflow visualization requires proper permissions."""
        # User context without permissions
        unauthorized_context = {
            "user_id": "unauthorized_user",
            "tenant_id": "test_tenant_123",
            "permissions": []  # No permissions
        }
        
        # This should raise PermissionError
        with pytest.raises(PermissionError):
            await operations_analysis_service.visualize_workflow(
                workflow_definition=sample_workflow_definition,
                user_context=unauthorized_context
            )
        
        logger.info("✅ Security validation tested")
    
    async def test_health_check(self, operations_analysis_service):
        """Test health check."""
        health = await operations_analysis_service.health_check()
        
        assert isinstance(health, dict)
        assert health.get("status") == "healthy"
        assert health.get("service_name") == "OperationsAnalysisService"
        assert "analyzed_workflows" in health
        
        logger.info("✅ Health check passed")
    
    async def test_get_service_capabilities(self, operations_analysis_service):
        """Test service capabilities."""
        capabilities = await operations_analysis_service.get_service_capabilities()
        
        assert isinstance(capabilities, dict)
        assert capabilities.get("service_name") == "OperationsAnalysisService"
        assert capabilities.get("service_type") == "enabling_service"
        assert "workflow_visualization" in capabilities.get("capabilities", [])
        assert "workflow_analysis" in capabilities.get("capabilities", [])
        assert "visualize_workflow" in capabilities.get("soa_apis", [])
        assert "get_workflow_analysis" in capabilities.get("soa_apis", [])
        
        logger.info("✅ Service capabilities verified")
    
    async def test_architecture_verification(self, operations_analysis_service, smart_city_infrastructure):
        """Verify the service follows the 5-layer architecture pattern."""
        # Verify it uses Platform Gateway for abstractions
        assert operations_analysis_service.platform_gateway is not None
        
        # Verify it uses Smart City services via RealmServiceBase
        assert operations_analysis_service.librarian is not None
        assert operations_analysis_service.data_steward is not None
        
        # Verify it uses infrastructure abstractions
        assert operations_analysis_service.workflow_diagramming_orchestration is not None
        assert operations_analysis_service.bpmn_processing is not None
        
        # Verify it's registered with Curator (via RealmServiceBase)
        # This is implicit - if initialize() succeeded, registration worked
        
        logger.info("✅ Architecture verification passed (5-layer pattern)")

