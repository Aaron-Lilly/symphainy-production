#!/usr/bin/env python3
"""
Business Outcomes Orchestrator Unit Tests

Tests for the Business Outcomes Orchestrator that composes business outcomes services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from utilities import UserContext

@pytest.mark.unit
@pytest.mark.business_enablement
class TestBusinessOutcomesOrchestratorUnit:
    """Unit tests for Business Outcomes Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_di_container):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = BusinessOutcomesOrchestrator(business_orchestrator=mock_biz_orch)
        
        assert orchestrator.name == "BusinessOutcomesOrchestrator"
        assert orchestrator.liaison_agent is None
    
    @pytest.mark.asyncio
    async def test_orchestrator_discovers_enabling_services(self, mock_di_container, mock_curator):
        """Test orchestrator discovers business outcomes enabling services."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        mock_services = {
            "ROICalculatorService": MagicMock(),
            "BusinessMetricsService": MagicMock()
        }
        
        async def mock_get_service(name):
            if name in mock_services:
                return mock_services[name]
            raise Exception(f"{name} not found")
        
        mock_curator.get_service = AsyncMock(side_effect=mock_get_service)
        mock_di_container.curator = mock_curator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = BusinessOutcomesOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        assert orchestrator.roi_calculator_service is not None
        assert orchestrator.business_metrics_service is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_integrates_liaison_agent(self, mock_di_container):
        """Test orchestrator integrates with liaison agent."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = BusinessOutcomesOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        assert orchestrator.liaison_agent is not None
        assert hasattr(orchestrator.liaison_agent, 'process_user_query')
    
    @pytest.mark.asyncio
    async def test_orchestrator_calculates_roi(self, mock_di_container):
        """Test orchestrator can calculate ROI."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        mock_roi_calculator = MagicMock()
        mock_roi_calculator.calculate_roi = AsyncMock(return_value={
            "success": True,
            "roi": 2.5,
            "payback_period_months": 18
        })
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = BusinessOutcomesOrchestrator(business_orchestrator=mock_biz_orch)
        orchestrator.roi_calculator_service = mock_roi_calculator
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await orchestrator.analyze_roi({
            "investment": 100000,
            "expected_return": 250000,
            "user_context": user_context
        })
        
        mock_roi_calculator.calculate_roi.assert_called_once()
        assert result["success"] is True
        assert "roi" in result
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_check(self, mock_di_container):
        """Test orchestrator health check."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.business_outcomes_orchestrator import BusinessOutcomesOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = BusinessOutcomesOrchestrator(business_orchestrator=mock_biz_orch)
        
        health = await orchestrator.health_check()
        
        assert "status" in health
        assert "orchestrator_name" in health or "name" in health

