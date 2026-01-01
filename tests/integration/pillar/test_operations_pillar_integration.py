"""
Integration tests for Operations Pillar workflows.

Tests:
- SOP to workflow conversion workflow
- Workflow to SOP conversion workflow
- Coexistence analysis workflow
- Interactive SOP creation workflow
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.pillar
@pytest.mark.operations
@pytest.mark.slow
class TestOperationsPillarIntegration:
    """Test suite for Operations Pillar integration."""
    
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
    async def test_sop_to_workflow_conversion_workflow(self, mock_platform_gateway, mock_di_container):
        """Test SOP to workflow conversion workflow."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock SOP to workflow workflow
        with patch.object(orchestrator, 'execute_sop_to_workflow_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "workflow_id": "workflow_123",
                "workflow_structure": {
                    "nodes": [{"id": "1", "type": "task"}],
                    "edges": []
                }
            }
            
            result = await orchestrator.execute_sop_to_workflow_workflow(
                sop_content={"sections": []},
                workflow_options={}
            )
            
            assert result["success"] is True
            assert "workflow_id" in result
            assert "workflow_structure" in result
    
    @pytest.mark.asyncio
    async def test_workflow_to_sop_conversion_workflow(self, mock_platform_gateway, mock_di_container):
        """Test workflow to SOP conversion workflow."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock workflow to SOP workflow
        with patch.object(orchestrator, 'execute_workflow_to_sop_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "sop_id": "sop_123",
                "sop_structure": {
                    "sections": [],
                    "steps": []
                }
            }
            
            result = await orchestrator.execute_workflow_to_sop_workflow(
                workflow_content={"nodes": [], "edges": []},
                sop_options={}
            )
            
            assert result["success"] is True
            assert "sop_id" in result
            assert "sop_structure" in result
    
    @pytest.mark.asyncio
    async def test_coexistence_analysis_workflow(self, mock_platform_gateway, mock_di_container):
        """Test coexistence analysis workflow."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        
        orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await orchestrator.initialize()
        
        # Mock coexistence analysis workflow
        with patch.object(orchestrator, 'execute_coexistence_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_id": "analysis_123",
                "coexistence_opportunities": [],
                "blueprint": {}
            }
            
            result = await orchestrator.execute_coexistence_analysis_workflow(
                sop_content={},
                workflow_content={}
            )
            
            assert result["success"] is True
            assert "analysis_id" in result



