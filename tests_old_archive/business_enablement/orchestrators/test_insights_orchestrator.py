#!/usr/bin/env python3
"""
Insights Orchestrator Unit Tests

Tests for the Insights Orchestrator that composes insights enabling services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from utilities import UserContext

@pytest.mark.unit
@pytest.mark.business_enablement
class TestInsightsOrchestratorUnit:
    """Unit tests for Insights Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_di_container):
        """Test orchestrator initializes correctly."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = InsightsOrchestrator(business_orchestrator=mock_biz_orch)
        
        assert orchestrator.name == "InsightsOrchestrator"
        assert orchestrator.liaison_agent is None
    
    @pytest.mark.asyncio
    async def test_orchestrator_discovers_enabling_services(self, mock_di_container, mock_curator):
        """Test orchestrator discovers insights enabling services."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        mock_services = {
            "DataAnalyzerService": MagicMock(),
            "MetricsCalculatorService": MagicMock(),
            "PatternDetectorService": MagicMock()
        }
        
        async def mock_get_service(name):
            if name in mock_services:
                return mock_services[name]
            raise Exception(f"{name} not found")
        
        mock_curator.get_service = AsyncMock(side_effect=mock_get_service)
        mock_di_container.curator = mock_curator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = InsightsOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        assert orchestrator.data_analyzer_service is not None
        assert orchestrator.metrics_calculator_service is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_integrates_liaison_agent(self, mock_di_container):
        """Test orchestrator integrates with liaison agent."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = InsightsOrchestrator(business_orchestrator=mock_biz_orch)
        await orchestrator.initialize()
        
        assert orchestrator.liaison_agent is not None
        assert hasattr(orchestrator.liaison_agent, 'process_user_query')
    
    @pytest.mark.asyncio
    async def test_orchestrator_generates_insights(self, mock_di_container):
        """Test orchestrator can generate insights from data."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_data = AsyncMock(return_value={
            "success": True,
            "insights": ["Pattern 1", "Pattern 2"]
        })
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = InsightsOrchestrator(business_orchestrator=mock_biz_orch)
        orchestrator.data_analyzer_service = mock_analyzer
        
        user_context = UserContext(
            user_id="user_123",
            tenant_id="tenant_456",
            roles=["user"]
        )
        
        result = await orchestrator.generate_insights({
            "data_source": "content_123",
            "user_context": user_context
        })
        
        mock_analyzer.analyze_data.assert_called_once()
        assert result["success"] is True
        assert "insights" in result
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_check(self, mock_di_container):
        """Test orchestrator health check."""
        from backend.business_enablement.business_orchestrator.use_cases.mvp.insights_orchestrator import InsightsOrchestrator
        
        mock_biz_orch = MagicMock()
        mock_biz_orch.di_container = mock_di_container
        
        orchestrator = InsightsOrchestrator(business_orchestrator=mock_biz_orch)
        
        health = await orchestrator.health_check()
        
        assert "status" in health
        assert "orchestrator_name" in health or "name" in health

