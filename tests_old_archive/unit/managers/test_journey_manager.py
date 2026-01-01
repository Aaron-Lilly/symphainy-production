#!/usr/bin/env python3
"""
Unit Tests - Journey Manager Service

Tests for the Journey Manager service implementation.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

pytestmark = [pytest.mark.unit, pytest.mark.managers, pytest.mark.fast]

class TestJourneyManagerService:
    """Test Journey Manager Service functionality."""
    
    @pytest.mark.asyncio
    async def test_journey_manager_initialization(self, mock_journey_manager):
        """Test Journey Manager can be initialized."""
        assert mock_journey_manager is not None
        assert mock_journey_manager.service_name == "JourneyManagerService"
        assert mock_journey_manager.realm_name == "journey"
    
    @pytest.mark.asyncio
    async def test_journey_manager_has_infrastructure_abstractions(self, mock_journey_manager):
        """Test Journey Manager has infrastructure abstractions."""
        assert hasattr(mock_journey_manager, 'session_abstraction')
        assert hasattr(mock_journey_manager, 'state_management_abstraction')
    
    @pytest.mark.asyncio
    async def test_journey_manager_has_smart_city_services(self, mock_journey_manager):
        """Test Journey Manager has Smart City service references."""
        assert hasattr(mock_journey_manager, 'traffic_cop')
        assert hasattr(mock_journey_manager, 'conductor')
        assert hasattr(mock_journey_manager, 'post_office')
    
    @pytest.mark.asyncio
    async def test_journey_manager_has_micro_modules(self, mock_journey_manager):
        """Test Journey Manager has all required micro-modules."""
        assert hasattr(mock_journey_manager, 'initialization_module')
        assert hasattr(mock_journey_manager, 'journey_design_module')
        assert hasattr(mock_journey_manager, 'experience_orchestration_module')
        assert hasattr(mock_journey_manager, 'roadmap_management_module')
        assert hasattr(mock_journey_manager, 'soa_mcp_module')
        assert hasattr(mock_journey_manager, 'utilities_module')
    
    @pytest.mark.asyncio
    async def test_journey_manager_type(self, mock_journey_manager):
        """Test Journey Manager has correct manager type."""
        # Manager type is string, not enum in mock
        assert mock_journey_manager.manager_type == "journey_manager"
    
    @pytest.mark.asyncio
    async def test_journey_manager_orchestration_scope(self, mock_journey_manager):
        """Test Journey Manager has correct orchestration scope."""
        from bases.manager_service_base import OrchestrationScope
        assert mock_journey_manager.orchestration_scope == OrchestrationScope.CROSS_DIMENSIONAL
    
    @pytest.mark.asyncio
    async def test_journey_manager_governance_level(self, mock_journey_manager):
        """Test Journey Manager has MODERATE governance level."""
        from bases.manager_service_base import GovernanceLevel
        assert mock_journey_manager.governance_level == GovernanceLevel.MODERATE

