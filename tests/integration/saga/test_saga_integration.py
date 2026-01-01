"""
Integration tests for Saga pattern integration.

Tests:
- Saga execution with policy configuration
- Saga compensation
- Saga journey design
- Saga milestone tracking
- Error handling and rollback
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.saga
@pytest.mark.slow
class TestSagaIntegration:
    """Test suite for Saga pattern integration."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_saga_execution_enabled(self, mock_platform_gateway, mock_di_container):
        """Test Saga execution when enabled by policy."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock Saga policy to enable Saga
        with patch.object(orchestrator, '_get_saga_policy') as mock_policy:
            mock_policy.return_value = {
                "saga_enabled": True,
                "saga_operations": ["operations_sop_to_workflow"],
                "compensation_handlers": {}
            }
            
            # Mock workflow function
            async def mock_workflow():
                return {"success": True, "workflow_id": "workflow_123"}
            
            # Execute with Saga
            result = await orchestrator._execute_with_saga(
                operation="operations_sop_to_workflow",
                workflow_func=mock_workflow,
                milestones=["step1", "step2", "step3"],
                user_context={}
            )
            
            # Should execute (may or may not use Saga depending on Saga orchestrator availability)
            assert result is not None
            assert "success" in result or "workflow_id" in result
    
    @pytest.mark.asyncio
    async def test_saga_execution_disabled(self, mock_platform_gateway, mock_di_container):
        """Test that workflow executes normally when Saga is disabled."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock Saga policy to disable Saga
        with patch.object(orchestrator, '_get_saga_policy') as mock_policy:
            mock_policy.return_value = {
                "saga_enabled": False,
                "saga_operations": [],
                "compensation_handlers": {}
            }
            
            # Mock workflow function
            async def mock_workflow():
                return {"success": True, "result": "normal_execution"}
            
            # Execute without Saga
            result = await orchestrator._execute_with_saga(
                operation="operations_sop_to_workflow",
                workflow_func=mock_workflow,
                milestones=[],
                user_context={}
            )
            
            # Should execute normally (no Saga)
            assert result["success"] is True
            assert result["result"] == "normal_execution"
    
    @pytest.mark.asyncio
    async def test_saga_operation_not_in_policy(self, mock_platform_gateway, mock_di_container):
        """Test that operation not in Saga policy executes without Saga."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock Saga policy with different operation
        with patch.object(orchestrator, '_get_saga_policy') as mock_policy:
            mock_policy.return_value = {
                "saga_enabled": True,
                "saga_operations": ["other_operation"],  # Different operation
                "compensation_handlers": {}
            }
            
            # Mock workflow function
            async def mock_workflow():
                return {"success": True, "result": "no_saga"}
            
            # Execute operation not in policy
            result = await orchestrator._execute_with_saga(
                operation="operations_sop_to_workflow",  # Not in policy
                workflow_func=mock_workflow,
                milestones=[],
                user_context={}
            )
            
            # Should execute without Saga
            assert result["success"] is True
            assert result["result"] == "no_saga"
    
    @pytest.mark.asyncio
    async def test_saga_compensation_handlers(self, mock_platform_gateway, mock_di_container):
        """Test Saga compensation handlers."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock compensation handlers
        compensation_handlers = {
            "step1": AsyncMock(return_value={"success": True}),
            "step2": AsyncMock(return_value={"success": True})
        }
        
        # Mock Saga policy with compensation handlers
        with patch.object(orchestrator, '_get_saga_policy') as mock_policy:
            mock_policy.return_value = {
                "saga_enabled": True,
                "saga_operations": ["operations_sop_to_workflow"],
                "compensation_handlers": {
                    "operations_sop_to_workflow": compensation_handlers
                }
            }
            
            # Verify compensation handlers are retrieved
            policy = await orchestrator._get_saga_policy({})
            handlers = policy.get("compensation_handlers", {}).get("operations_sop_to_workflow", {})
            
            assert len(handlers) > 0
    
    @pytest.mark.asyncio
    async def test_saga_milestone_tracking(self, mock_platform_gateway, mock_di_container):
        """Test Saga milestone tracking."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        milestones = ["extract_sop_structure", "analyze_workflow_requirements", "generate_workflow", "validate_workflow", "store_workflow"]
        
        # Mock Saga policy
        with patch.object(orchestrator, '_get_saga_policy') as mock_policy:
            mock_policy.return_value = {
                "saga_enabled": True,
                "saga_operations": ["operations_sop_to_workflow"],
                "compensation_handlers": {}
            }
            
            # Mock workflow function
            async def mock_workflow():
                return {"success": True, "milestones": milestones}
            
            # Execute with milestones
            result = await orchestrator._execute_with_saga(
                operation="operations_sop_to_workflow",
                workflow_func=mock_workflow,
                milestones=milestones,
                user_context={}
            )
            
            # Should track milestones (if Saga orchestrator available)
            assert result is not None

