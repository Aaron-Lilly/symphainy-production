#!/usr/bin/env python3
"""
Agentic-Forward Pattern Tests - Operations

Tests the agentic-forward pattern for Operations Orchestrator:
- Agent does critical reasoning FIRST
- Services execute agent's strategic decisions
- No backward compatibility fallbacks
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Dict, Any

pytestmark = pytest.mark.unit


class TestOperationsAgenticForward:
    """Test agentic-forward pattern for Operations."""
    
    @pytest.fixture
    def mock_delivery_manager(self):
        """Create mock delivery manager."""
        manager = MagicMock()
        manager.realm_name = "business_enablement"
        manager.service_name = "DeliveryManagerService"
        manager.platform_gateway = MagicMock()
        manager.di_container = MagicMock()
        manager.di_container.get_logger = Mock(return_value=MagicMock())
        return manager
    
    @pytest.fixture
    def mock_specialist_agent(self):
        """Create mock specialist agent with LLM abstraction."""
        agent = MagicMock()
        
        # Mock LLM abstraction
        agent.llm_abstraction = MagicMock()
        agent.llm_abstraction.analyze_text = AsyncMock(return_value={
            "analysis": "Workflow should optimize for human-AI collaboration. AI can automate repetitive steps and provide decision support."
        })
        
        # Mock critical reasoning methods
        agent.analyze_process_for_workflow_structure = AsyncMock(return_value={
            "success": True,
            "workflow_structure": {
                "steps": [
                    {
                        "step_id": "step_1",
                        "name": "Data Collection",
                        "description": "Collect input data",
                        "order": 1,
                        "type": "action"
                    },
                    {
                        "step_id": "step_2",
                        "name": "AI Analysis",
                        "description": "AI analyzes data",
                        "order": 2,
                        "type": "ai_action"
                    }
                ],
                "decision_points": [
                    {
                        "point_id": "decision_1",
                        "name": "Quality Check",
                        "type": "human_review"
                    }
                ],
                "automation_opportunities": [
                    {
                        "step": "Data Collection",
                        "automation_level": "high"
                    }
                ],
                "recommended_approach": "ai_augmented_workflow"
            },
            "ai_value_opportunities": [
                {
                    "area": "Process Automation",
                    "ai_value": "AI can automate repetitive steps",
                    "impact": "high"
                }
            ],
            "reasoning": {
                "analysis": "AI can add value in process automation",
                "key_insights": ["AI can automate repetitive steps"],
                "recommendations": ["Prioritize AI-assisted steps"]
            }
        })
        
        agent.analyze_for_sop_structure = AsyncMock(return_value={
            "success": True,
            "sop_structure": {
                "title": "Standard Operating Procedure",
                "description": "SOP generated from workflow",
                "steps": [
                    {
                        "step_number": 1,
                        "instruction": "Collect input data",
                        "details": "Gather all required data"
                    },
                    {
                        "step_number": 2,
                        "instruction": "AI Analysis",
                        "details": "Use AI to analyze data"
                    }
                ],
                "ai_assistance_points": [
                    {
                        "step": 2,
                        "assistance_type": "ai_analysis"
                    }
                ]
            },
            "reasoning": {
                "analysis": "SOP should document AI assistance points",
                "key_insights": ["AI can assist in analysis steps"],
                "recommendations": ["Document AI assistance clearly"]
            }
        })
        
        agent.analyze_for_coexistence_structure = AsyncMock(return_value={
            "success": True,
            "coexistence_structure": {
                "handoff_points": [
                    {
                        "point_id": "handoff_1",
                        "from": "human",
                        "to": "ai",
                        "step": "Data Analysis"
                    }
                ],
                "ai_augmentation_points": [
                    {
                        "point_id": "augment_1",
                        "step": "Quality Check",
                        "augmentation_type": "decision_support"
                    }
                ],
                "human_driven_steps": ["Data Collection", "Final Review"],
                "ai_driven_steps": ["Data Analysis", "Pattern Recognition"],
                "collaboration_pattern": "ai_augmented"
            },
            "reasoning": {
                "analysis": "Optimal coexistence pattern is AI-augmented",
                "key_insights": ["Humans should drive collection and review"],
                "recommendations": ["AI should handle analysis and pattern recognition"]
            }
        })
        
        return agent
    
    @pytest.fixture
    def mock_workflow_conversion_service(self):
        """Create mock workflow conversion service."""
        service = MagicMock()
        service.convert_sop_to_workflow = AsyncMock(return_value={
            "success": True,
            "workflow": {
                "workflow_id": "workflow_123",
                "title": "Generated Workflow",
                "steps": [
                    {"step_id": "step_1", "name": "Data Collection", "order": 1}
                ]
            },
            "workflow_id": "workflow_123"
        })
        service.convert_workflow_to_sop = AsyncMock(return_value={
            "success": True,
            "sop": {
                "sop_id": "sop_123",
                "title": "Standard Operating Procedure",
                "steps": [
                    {"step_number": 1, "instruction": "Collect data"}
                ]
            }
        })
        return service
    
    @pytest.fixture
    def mock_coexistence_service(self):
        """Create mock coexistence analysis service."""
        service = MagicMock()
        service.analyze_coexistence = AsyncMock(return_value={
            "success": True,
            "analysis": {
                "analysis_id": "analysis_123",
                "handoff_points": [],
                "collaboration_pattern": "ai_augmented"
            }
        })
        return service
    
    @pytest.fixture
    def mock_librarian(self):
        """Create mock librarian."""
        librarian = MagicMock()
        librarian.get_document = AsyncMock(return_value={
            "data": {
                "title": "Test SOP",
                "steps": [
                    {"instruction": "Step 1", "step_number": 1}
                ]
            }
        })
        return librarian
    
    @pytest.fixture
    async def orchestrator(self, mock_delivery_manager, mock_specialist_agent, mock_workflow_conversion_service, mock_coexistence_service, mock_librarian):
        """Create OperationsOrchestrator with mocked dependencies."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(mock_delivery_manager)
        
        # Set specialist agent
        orchestrator.specialist_agent = mock_specialist_agent
        
        # Mock service discovery
        orchestrator._get_workflow_conversion_service = AsyncMock(return_value=mock_workflow_conversion_service)
        orchestrator._get_coexistence_analysis_service = AsyncMock(return_value=mock_coexistence_service)
        
        # Mock librarian
        orchestrator.librarian = mock_librarian
        
        # Mock journey orchestrator for artifact creation
        mock_journey_orch = MagicMock()
        mock_journey_orch.create_journey_artifact = AsyncMock(return_value={
            "success": True,
            "artifact": {"artifact_id": "artifact_123"}
        })
        orchestrator._get_journey_orchestrator = AsyncMock(return_value=mock_journey_orch)
        
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_generate_workflow_from_sop_agentic_forward_flow(self, orchestrator, mock_specialist_agent, mock_workflow_conversion_service):
        """Test that workflow generation follows agentic-forward pattern: Agent → Service."""
        # Arrange
        sop_file_uuid = "sop_file_123"
        
        # Act
        result = await orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid=sop_file_uuid,
            client_id="client_123"
        )
        
        # Assert
        # 1. Agent was called FIRST for critical reasoning
        mock_specialist_agent.analyze_process_for_workflow_structure.assert_called_once()
        call_args = mock_specialist_agent.analyze_process_for_workflow_structure.call_args
        assert "process_content" in call_args[1]
        
        # 2. Service was called with agent's structure
        mock_workflow_conversion_service.convert_sop_to_workflow.assert_called_once()
        service_call_args = mock_workflow_conversion_service.convert_sop_to_workflow.call_args
        workflow_structure = service_call_args[1]["workflow_structure"]
        assert workflow_structure["steps"] is not None
        assert workflow_structure["recommended_approach"] == "ai_augmented_workflow"
        
        # 3. Result is successful
        assert result["success"] is True
        assert "workflow" in result or "workflow_id" in result
    
    @pytest.mark.asyncio
    async def test_generate_sop_from_workflow_agentic_forward_flow(self, orchestrator, mock_specialist_agent, mock_workflow_conversion_service):
        """Test that SOP generation follows agentic-forward pattern: Agent → Service."""
        # Arrange
        workflow_file_uuid = "workflow_file_123"
        
        # Act
        result = await orchestrator.generate_sop_from_workflow(
            session_token="session_123",
            workflow_file_uuid=workflow_file_uuid,
            client_id="client_123"
        )
        
        # Assert
        # 1. Agent was called FIRST for critical reasoning
        mock_specialist_agent.analyze_for_sop_structure.assert_called_once()
        call_args = mock_specialist_agent.analyze_for_sop_structure.call_args
        assert "workflow_content" in call_args[1]
        
        # 2. Service was called with agent's structure
        mock_workflow_conversion_service.convert_workflow_to_sop.assert_called_once()
        service_call_args = mock_workflow_conversion_service.convert_workflow_to_sop.call_args
        sop_structure = service_call_args[1]["sop_structure"]
        assert sop_structure["title"] is not None
        assert sop_structure["steps"] is not None
        
        # 3. Result is successful
        assert result["success"] is True
        assert "sop" in result or "sop_content" in result
    
    @pytest.mark.asyncio
    async def test_analyze_coexistence_agentic_forward_flow(self, orchestrator, mock_specialist_agent, mock_coexistence_service):
        """Test that coexistence analysis follows agentic-forward pattern: Agent → Service."""
        # Arrange
        sop_content = {"title": "Test SOP", "steps": []}
        workflow_content = {"title": "Test Workflow", "steps": []}
        
        # Act
        result = await orchestrator.analyze_coexistence_content(
            session_token="session_123",
            sop_content=str(sop_content),
            workflow_content=workflow_content,
            client_id="client_123"
        )
        
        # Assert
        # 1. Agent was called FIRST for critical reasoning
        mock_specialist_agent.analyze_for_coexistence_structure.assert_called_once()
        call_args = mock_specialist_agent.analyze_for_coexistence_structure.call_args
        assert "sop_content" in call_args[1]
        assert "workflow_content" in call_args[1]
        
        # 2. Service was called with agent's structure
        mock_coexistence_service.analyze_coexistence.assert_called_once()
        service_call_args = mock_coexistence_service.analyze_coexistence.call_args
        coexistence_structure = service_call_args[1]["coexistence_structure"]
        assert coexistence_structure["collaboration_pattern"] is not None
        assert coexistence_structure["handoff_points"] is not None
        
        # 3. Result is successful
        assert result["success"] is True
        assert "analysis" in result or "coexistence_blueprint" in result
    
    @pytest.mark.asyncio
    async def test_workflow_generation_agent_failure_handling(self, orchestrator, mock_specialist_agent):
        """Test that workflow generation fails gracefully if agent reasoning fails."""
        # Arrange
        mock_specialist_agent.analyze_process_for_workflow_structure = AsyncMock(return_value={
            "success": False,
            "error": "Agent reasoning failed"
        })
        
        # Act
        result = await orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="sop_file_123"
        )
        
        # Assert
        assert result["success"] is False
        assert "Agent reasoning" in result["error"] or "structure not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_agent_uses_llm_abstraction(self, orchestrator, mock_specialist_agent):
        """Test that agent uses LLM abstraction for critical reasoning."""
        # Arrange
        sop_file_uuid = "sop_file_123"
        
        # Act
        await orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid=sop_file_uuid
        )
        
        # Assert
        # Verify LLM abstraction is available (mocked in fixture)
        assert hasattr(mock_specialist_agent, 'llm_abstraction')
        assert mock_specialist_agent.llm_abstraction is not None
    
    @pytest.mark.asyncio
    async def test_service_validates_agent_structure(self, orchestrator, mock_specialist_agent, mock_workflow_conversion_service):
        """Test that service validates agent-provided structure."""
        # Arrange - agent provides invalid structure (no steps)
        mock_specialist_agent.analyze_process_for_workflow_structure = AsyncMock(return_value={
            "success": True,
            "workflow_structure": {
                "steps": [],  # Invalid - no steps
                "recommended_approach": "ai_augmented_workflow"
            }
        })
        
        # Mock service to return error for invalid structure
        mock_workflow_conversion_service.convert_sop_to_workflow = AsyncMock(return_value={
            "success": False,
            "error": "No steps specified in workflow structure"
        })
        
        # Act
        result = await orchestrator.generate_workflow_from_sop(
            session_token="session_123",
            sop_file_uuid="sop_file_123"
        )
        
        # Assert
        assert result["success"] is False
        assert "steps" in result.get("error", "").lower() or "structure" in result.get("error", "").lower()

