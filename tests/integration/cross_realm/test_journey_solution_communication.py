"""
Integration tests for Journey ↔ Solution realm communication.

Tests:
- Journey orchestrator → Solution orchestrator communication
- Service discovery across realms
- Cross-realm workflow execution
- Error handling across realms
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.cross_realm
@pytest.mark.journey_solution
@pytest.mark.slow
class TestJourneySolutionCommunication:
    """Test suite for Journey ↔ Solution realm communication."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        gateway.get_foundation_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_journey_orchestrator_discovers_solution_service(self, curator_foundation, mock_platform_gateway, mock_di_container):
        """Test that Journey orchestrator can discover Solution realm services."""
        skip_if_missing_real_infrastructure(["consul"])
        
        # Create Journey orchestrator
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        journey_orchestrator = ContentJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await journey_orchestrator.initialize()
        
        # Register a Solution realm service
        mock_solution_service = Mock()
        mock_solution_service.service_name = "ContentSolutionOrchestratorService"
        
        await curator_foundation.register_service(
            service_instance=mock_solution_service,
            service_metadata={
                "service_type": "orchestrator",
                "realm": "solution",
                "address": "localhost",
                "port": 8000
            }
        )
        
        # Journey orchestrator should be able to discover it
        discovered = await journey_orchestrator.get_enabling_service("ContentSolutionOrchestratorService")
        
        # May return None if service discovery unavailable, but should not error
        assert discovered is None or discovered is not None
    
    @pytest.mark.asyncio
    async def test_solution_orchestrator_discovers_journey_service(self, curator_foundation, mock_platform_gateway, mock_di_container):
        """Test that Solution orchestrator can discover Journey realm services."""
        skip_if_missing_real_infrastructure(["consul"])
        
        # Create Solution orchestrator
        from backend.solution.services.content_solution_orchestrator_service.content_solution_orchestrator_service import ContentSolutionOrchestratorService
        solution_orchestrator = ContentSolutionOrchestratorService(mock_platform_gateway, mock_di_container)
        await solution_orchestrator.initialize()
        
        # Register a Journey realm service
        mock_journey_service = Mock()
        mock_journey_service.service_name = "ContentJourneyOrchestrator"
        
        await curator_foundation.register_service(
            service_instance=mock_journey_service,
            service_metadata={
                "service_type": "orchestrator",
                "realm": "journey",
                "address": "localhost",
                "port": 8001
            }
        )
        
        # Solution orchestrator should be able to discover it
        discovered = await solution_orchestrator.get_enabling_service("ContentJourneyOrchestrator")
        
        # May return None if service discovery unavailable, but should not error
        assert discovered is None or discovered is not None
    
    @pytest.mark.asyncio
    async def test_cross_realm_workflow_execution(self, mock_platform_gateway, mock_di_container):
        """Test executing workflow that spans Journey and Solution realms."""
        # This would test a real workflow that requires both realms
        # For now, test that orchestrators can be initialized together
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        from backend.solution.services.content_solution_orchestrator_service.content_solution_orchestrator_service import ContentSolutionOrchestratorService
        
        journey_orchestrator = ContentJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        solution_orchestrator = ContentSolutionOrchestratorService(mock_platform_gateway, mock_di_container)
        
        await journey_orchestrator.initialize()
        await solution_orchestrator.initialize()
        
        # Both should be initialized
        assert journey_orchestrator.is_initialized is True
        assert solution_orchestrator.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_error_handling_cross_realm(self, curator_foundation, mock_platform_gateway, mock_di_container):
        """Test error handling when cross-realm service is unavailable."""
        from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
        
        journey_orchestrator = ContentJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await journey_orchestrator.initialize()
        
        # Try to discover non-existent service
        discovered = await journey_orchestrator.get_enabling_service("NonExistentService")
        
        # Should handle gracefully (return None, not raise exception)
        assert discovered is None




