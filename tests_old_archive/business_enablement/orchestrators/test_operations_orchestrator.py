#!/usr/bin/env python3
"""
Operations Orchestrator Unit Tests

Tests for the Operations Orchestrator that composes operations enabling services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from utilities import UserContext

@pytest.mark.unit
@pytest.mark.business_enablement
class TestOperationsOrchestratorUnit:
    """Unit tests for Operations Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_di_container):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = OperationsOrchestrator(business_orchestrator=mock_biz_orch)
        
        assert orchestrator.name == "OperationsOrchestrator"
        assert orchestrator.liaison_agent is None
    
    @pytest.mark.asyncio
    async def test_orchestrator_discovers_enabling_services(self, mock_di_container, mock_curator):
        """Test orchestrator discovers operations enabling services."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        mock_services = {
            "SOPGeneratorService": MagicMock(),
            "WorkflowBuilderService": MagicMock()
        }
        
        async def mock_get_service(name):
            if name in mock_services:
                return mock_services[name]
            raise Exception(f"{name} not found")
        
        mock_curator.get_service = AsyncMock(side_effect=mock_get_service)
        mock_di_container.curator = mock_curator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = OperationsOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        assert orchestrator.sop_generator_service is not None
        assert orchestrator.workflow_builder_service is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_integrates_liaison_agent(self, mock_di_container):
        """Test orchestrator integrates with liaison agent."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = OperationsOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        assert orchestrator.liaison_agent is not None
        assert hasattr(orchestrator.liaison_agent, 'process_user_query')
    
    @pytest.mark.asyncio
    async def test_orchestrator_generates_sop(self, mock_di_container):
        """Test orchestrator can generate SOPs."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        mock_sop_generator = MagicMock()
        mock_sop_generator.generate_sop = AsyncMock(return_value={
            "success": True,
            "sop": {"title": "Test SOP", "steps": ["Step 1", "Step 2"]}
        })
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = OperationsOrchestrator(business_orchestrator=mock_biz_orch)
        orchestrator.sop_generator_service = mock_sop_generator
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await orchestrator.create_sop({
            "context": "test process",
            "user_context": user_context
        })
        
        mock_sop_generator.generate_sop.assert_called_once()
        assert result["success"] is True
        assert "sop" in result
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_check(self, mock_di_container):
        """Test orchestrator health check."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.operations_orchestrator import OperationsOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = OperationsOrchestrator(business_orchestrator=mock_biz_orch)
        
        health = await orchestrator.health_check()
        
        assert "status" in health
        assert "orchestrator_name" in health or "name" in health

