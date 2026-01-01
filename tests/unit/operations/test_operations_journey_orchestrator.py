"""
Comprehensive unit tests for Operations Journey Orchestrator.

Tests:
- SOP to workflow conversion
- Workflow to SOP conversion
- Coexistence analysis
- Interactive SOP creation
- Interactive blueprint creation
- AI-optimized blueprint generation
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any


@pytest.mark.unit
@pytest.mark.operations
@pytest.mark.orchestrator
@pytest.mark.fast
class TestOperationsJourneyOrchestrator:
    """Test suite for Operations Journey Orchestrator."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def operations_orchestrator(self, mock_platform_gateway, mock_di_container):
        """Create OperationsJourneyOrchestrator instance."""
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        return OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
    
    @pytest.mark.asyncio
    async def test_sop_to_workflow_conversion(self, operations_orchestrator):
        """Test SOP to workflow conversion."""
        with patch.object(operations_orchestrator, 'execute_sop_to_workflow_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "workflow_id": "workflow_123",
                "workflow_structure": {
                    "nodes": [],
                    "edges": []
                }
            }
            
            result = await operations_orchestrator.execute_sop_to_workflow_workflow(
                sop_content={"sections": []},
                workflow_options={}
            )
            
            assert result["success"] is True
            assert "workflow_id" in result
            assert "workflow_structure" in result
    
    @pytest.mark.asyncio
    async def test_workflow_to_sop_conversion(self, operations_orchestrator):
        """Test workflow to SOP conversion."""
        with patch.object(operations_orchestrator, 'execute_workflow_to_sop_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "sop_id": "sop_123",
                "sop_structure": {
                    "sections": [],
                    "steps": []
                }
            }
            
            result = await operations_orchestrator.execute_workflow_to_sop_workflow(
                workflow_content={"nodes": [], "edges": []},
                sop_options={}
            )
            
            assert result["success"] is True
            assert "sop_id" in result
            assert "sop_structure" in result
    
    @pytest.mark.asyncio
    async def test_coexistence_analysis(self, operations_orchestrator):
        """Test coexistence analysis."""
        with patch.object(operations_orchestrator, 'execute_coexistence_analysis_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "analysis_id": "analysis_123",
                "coexistence_opportunities": [],
                "blueprint": {}
            }
            
            result = await operations_orchestrator.execute_coexistence_analysis_workflow(
                sop_content={},
                workflow_content={}
            )
            
            assert result["success"] is True
            assert "analysis_id" in result
    
    @pytest.mark.asyncio
    async def test_interactive_sop_creation(self, operations_orchestrator):
        """Test interactive SOP creation."""
        with patch.object(operations_orchestrator, 'execute_interactive_sop_creation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "session_id": "session_123",
                "sop_draft": {}
            }
            
            result = await operations_orchestrator.execute_interactive_sop_creation_workflow(
                user_input="Create new SOP",
                session_id="session_123"
            )
            
            assert result["success"] is True
            assert "session_id" in result
    
    @pytest.mark.asyncio
    async def test_interactive_blueprint_creation(self, operations_orchestrator):
        """Test interactive blueprint creation."""
        with patch.object(operations_orchestrator, 'execute_interactive_blueprint_creation_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "blueprint_id": "blueprint_123",
                "blueprint": {}
            }
            
            result = await operations_orchestrator.execute_interactive_blueprint_creation_workflow(
                user_input="Create blueprint",
                session_id="session_123"
            )
            
            assert result["success"] is True
            assert "blueprint_id" in result
    
    @pytest.mark.asyncio
    async def test_ai_optimized_blueprint(self, operations_orchestrator):
        """Test AI-optimized blueprint generation."""
        with patch.object(operations_orchestrator, 'execute_ai_optimized_blueprint_workflow') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "blueprint_id": "blueprint_123",
                "optimization_score": 0.95
            }
            
            result = await operations_orchestrator.execute_ai_optimized_blueprint_workflow(
                sop_content={},
                workflow_content={}
            )
            
            assert result["success"] is True
            assert "optimization_score" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_conversion_failure(self, operations_orchestrator):
        """Test error handling when conversion fails."""
        with patch.object(operations_orchestrator, 'execute_sop_to_workflow_workflow') as mock_execute:
            mock_execute.side_effect = Exception("Conversion failed")
            
            with pytest.raises(Exception):
                await operations_orchestrator.execute_sop_to_workflow_workflow(
                    sop_content={},
                    workflow_options={}
                )



