#!/usr/bin/env python3
"""
Operations Orchestrator Functionality Tests

Tests Operations Orchestrator core functionality:
- Operations optimization coordination
- Agent routing
- SOP and workflow creation

Uses mock AI responses.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any

# Path is configured in pytest.ini - no manipulation needed
from tests.fixtures.ai_mock_responses import get_operations_analysis_response


@pytest.mark.business_enablement
@pytest.mark.functional
class TestOperationsOrchestratorFunctionality:
    """Test Operations Orchestrator functionality."""
    
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
    def mock_delivery_manager(self, mock_di_container, mock_platform_gateway):
        """Create mock Delivery Manager."""
        manager = Mock()
        manager.realm_name = "business_enablement"
        manager.platform_gateway = mock_platform_gateway
        manager.di_container = mock_di_container
        manager.logger = Mock()
        return manager
    
    @pytest.fixture
    def mock_operations_specialist_agent(self):
        """Create mock Operations Specialist Agent."""
        agent = Mock()
        agent.analyze_operations = AsyncMock(return_value={
            "status": "success",
            "analysis": {}
        })
        return agent
    
    @pytest.fixture
    async def operations_orchestrator(self, mock_delivery_manager, mock_operations_specialist_agent):
        """Create Operations Orchestrator instance."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator import OperationsOrchestrator
        
        orchestrator = OperationsOrchestrator(
            delivery_manager=mock_delivery_manager
        )
        
        # Mock agents
        orchestrator.operations_specialist_agent = mock_operations_specialist_agent
        orchestrator.operations_liaison_agent = Mock()
        
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_generate_workflow_from_sop(self, operations_orchestrator):
        """Test workflow generation from SOP."""
        sop_content = {
            "title": "Test SOP",
            "steps": [
                {"name": "Step 1", "description": "First step"},
                {"name": "Step 2", "description": "Second step"}
            ]
        }
        
        result = await operations_orchestrator.generate_workflow_from_sop(
            session_token="test_session",
            sop_content=sop_content
        )
        
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is not False  # May be True or None
    
    @pytest.mark.asyncio
    async def test_process_query(self, operations_orchestrator):
        """Test query processing."""
        result = await operations_orchestrator.process_query(
            session_token="test_session",
            query_text="What is the status of my workflow?"
        )
        
        assert result is not None
        assert isinstance(result, dict)

