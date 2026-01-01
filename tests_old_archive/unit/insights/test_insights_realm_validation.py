#!/usr/bin/env python3
"""
Insights Realm Validation Test

Simple validation test to verify Insights realm structure works:
- InsightsManagerService can be initialized
- Insights Orchestrator can be discovered
- Enabling services can be discovered via get_enabling_service()
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

pytestmark = [pytest.mark.unit, pytest.mark.fast]


class TestInsightsRealmValidation:
    """Validation tests for Insights realm structure."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "insights"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=Mock())
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_curator(self):
        """Create mock Curator."""
        curator = Mock()
        curator.registered_services = {}
        curator.discover_service_by_name = AsyncMock(return_value=None)
        return curator
    
    @pytest.mark.asyncio
    async def test_insights_manager_service_initialization(self, mock_di_container, mock_platform_gateway):
        """Test that InsightsManagerService can be initialized."""
        from backend.insights.InsightsManagerService.insights_manager_service import InsightsManagerService
        
        # Create InsightsManagerService
        insights_manager = InsightsManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Verify basic properties
        assert insights_manager.service_name == "InsightsManagerService"
        assert insights_manager.realm_name == "insights"
        assert insights_manager.manager_type.value == "insights_manager"
        assert insights_manager.orchestration_scope.value == "realm_only"
        assert insights_manager.governance_level.value == "moderate"
        
        # Verify micro-modules are initialized
        assert hasattr(insights_manager, 'initialization_module')
        assert hasattr(insights_manager, 'soa_mcp_module')
        assert hasattr(insights_manager, 'utilities_module')
        
        # Verify state
        assert insights_manager.insights_orchestrator is None  # Not discovered yet
        assert insights_manager.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_insights_manager_can_discover_orchestrator(self, mock_di_container, mock_platform_gateway, mock_curator):
        """Test that InsightsManagerService can discover Insights Orchestrator via Curator."""
        from backend.insights.InsightsManagerService.insights_manager_service import InsightsManagerService
        
        # Mock Insights Orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.service_name = "InsightsOrchestratorService"
        mock_orchestrator.realm_name = "insights"
        
        # Setup Curator to return orchestrator
        mock_curator.discover_service_by_name = AsyncMock(return_value=mock_orchestrator)
        mock_di_container.get_foundation_service = Mock(return_value=mock_curator)
        
        # Create InsightsManagerService
        insights_manager = InsightsManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Mock get_curator method
        insights_manager.get_curator = Mock(return_value=mock_curator)
        
        # Test discovery
        orchestrator = await insights_manager.get_insights_orchestrator()
        
        # Verify orchestrator was discovered
        assert orchestrator is not None
        assert orchestrator.service_name == "InsightsOrchestratorService"
        assert orchestrator.realm_name == "insights"
        
        # Verify Curator was called
        mock_curator.discover_service_by_name.assert_called_with("InsightsOrchestrator")
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_uses_insights_manager(self, mock_di_container, mock_platform_gateway):
        """Test that Insights Orchestrator can be initialized with InsightsManagerService."""
        from backend.insights.InsightsManagerService.insights_manager_service import InsightsManagerService
        from backend.insights.orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        
        # Create InsightsManagerService
        insights_manager = InsightsManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Create Insights Orchestrator with InsightsManagerService
        orchestrator = InsightsOrchestrator(insights_manager=insights_manager)
        
        # Verify orchestrator properties
        assert orchestrator.service_name == "InsightsOrchestratorService"
        assert orchestrator.realm_name == "insights"
        assert orchestrator.insights_manager == insights_manager
        assert orchestrator.delivery_manager == insights_manager  # Backward compatibility
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_can_discover_enabling_services(self, mock_di_container, mock_platform_gateway):
        """Test that Insights Orchestrator can discover enabling services via get_enabling_service()."""
        from backend.insights.InsightsManagerService.insights_manager_service import InsightsManagerService
        from backend.insights.orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
        
        # Mock enabling service
        mock_data_analyzer = Mock()
        mock_data_analyzer.service_name = "DataAnalyzerService"
        mock_data_analyzer.realm_name = "business_enablement"
        
        # Create InsightsManagerService
        insights_manager = InsightsManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Create Insights Orchestrator
        orchestrator = InsightsOrchestrator(insights_manager=insights_manager)
        
        # Mock get_enabling_service to return data analyzer
        orchestrator.get_enabling_service = AsyncMock(return_value=mock_data_analyzer)
        
        # Test enabling service discovery
        data_analyzer = await orchestrator._get_data_analyzer_service()
        
        # Verify enabling service was discovered
        assert data_analyzer is not None
        assert data_analyzer.service_name == "DataAnalyzerService"
        assert data_analyzer.realm_name == "business_enablement"  # Enabling services stay in business_enablement
        
        # Verify get_enabling_service was called
        orchestrator.get_enabling_service.assert_called_with("DataAnalyzerService")
    
    def test_insights_realm_structure(self):
        """Test that Insights realm has correct structure."""
        import os
        
        # Get project root (tests directory is in symphainy_source/tests)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        insights_realm_path = os.path.join(project_root, "symphainy-platform/backend/insights")
        
        # Check main directories exist
        assert os.path.exists(os.path.join(insights_realm_path, "InsightsManagerService")), f"InsightsManagerService directory not found"
        assert os.path.exists(os.path.join(insights_realm_path, "orchestrators")), f"orchestrators directory not found"
        assert os.path.exists(os.path.join(insights_realm_path, "agents")), f"agents directory not found"
        assert os.path.exists(os.path.join(insights_realm_path, "mcp_server")), f"mcp_server directory not found"
        
        # Check key files exist
        assert os.path.exists(os.path.join(insights_realm_path, "InsightsManagerService/insights_manager_service.py")), "InsightsManagerService file not found"
        assert os.path.exists(os.path.join(insights_realm_path, "orchestrators/insights_orchestrator/insights_orchestrator.py")), "Insights orchestrator file not found"
        assert os.path.exists(os.path.join(insights_realm_path, "agents/insights_liaison_agent.py")), "Insights liaison agent file not found"
        assert os.path.exists(os.path.join(insights_realm_path, "mcp_server/insights_mcp_server.py")), "Insights MCP server file not found"
    
    def test_insights_manager_service_capabilities(self, mock_di_container, mock_platform_gateway):
        """Test that InsightsManagerService exposes correct capabilities."""
        from backend.insights.InsightsManagerService.insights_manager_service import InsightsManagerService
        
        # Create InsightsManagerService
        insights_manager = InsightsManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Test capabilities method
        capabilities = insights_manager.get_capabilities()
        
        # Verify capabilities structure
        assert "service_name" in capabilities
        assert "realm" in capabilities
        assert "manager_type" in capabilities
        assert "capabilities" in capabilities
        assert capabilities["service_name"] == "InsightsManagerService"
        assert capabilities["realm"] == "insights"
        assert "data_analysis" in capabilities["capabilities"]
        assert "insights_generation" in capabilities["capabilities"]

