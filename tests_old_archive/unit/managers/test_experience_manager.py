#!/usr/bin/env python3
"""
Unit Tests - Experience Manager Service

Tests for the Experience Manager service implementation.
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

pytestmark = [pytest.mark.unit, pytest.mark.managers, pytest.mark.fast]

class TestExperienceManagerService:
    """Test Experience Manager Service functionality."""
    
    @pytest.mark.asyncio
    async def test_experience_manager_initialization(self, mock_experience_manager):
        """Test Experience Manager can be initialized."""
        assert mock_experience_manager is not None
        assert mock_experience_manager.service_name == "ExperienceManagerService"
        assert mock_experience_manager.realm_name == "experience"
    
    @pytest.mark.asyncio
    async def test_experience_manager_has_infrastructure_abstractions(self, mock_experience_manager):
        """Test Experience Manager has infrastructure abstractions."""
        assert hasattr(mock_experience_manager, 'session_abstraction')
        assert hasattr(mock_experience_manager, 'state_management_abstraction')
    
    @pytest.mark.asyncio
    async def test_experience_manager_has_smart_city_services(self, mock_experience_manager):
        """Test Experience Manager has Smart City service references."""
        assert hasattr(mock_experience_manager, 'security_guard')
        assert hasattr(mock_experience_manager, 'traffic_cop')
        assert hasattr(mock_experience_manager, 'post_office')
    
    @pytest.mark.asyncio
    async def test_experience_manager_has_micro_modules(self, mock_experience_manager):
        """Test Experience Manager has all required micro-modules."""
        assert hasattr(mock_experience_manager, 'initialization_module')
        assert hasattr(mock_experience_manager, 'experience_coordination_module')
        assert hasattr(mock_experience_manager, 'delivery_orchestration_module')
        assert hasattr(mock_experience_manager, 'soa_mcp_module')
        assert hasattr(mock_experience_manager, 'utilities_module')
    
    @pytest.mark.asyncio
    async def test_experience_manager_type(self, mock_experience_manager):
        """Test Experience Manager has correct manager type."""
        # Manager type is string, not enum in mock
        assert mock_experience_manager.manager_type == "experience_manager"
    
    @pytest.mark.asyncio
    async def test_experience_manager_orchestration_scope(self, mock_experience_manager):
        """Test Experience Manager has correct orchestration scope."""
        from bases.manager_service_base import OrchestrationScope
        assert mock_experience_manager.orchestration_scope == OrchestrationScope.CROSS_DIMENSIONAL
    
    @pytest.mark.asyncio
    async def test_experience_manager_governance_level(self, mock_experience_manager):
        """Test Experience Manager has MODERATE governance level."""
        from bases.manager_service_base import GovernanceLevel
        assert mock_experience_manager.governance_level == GovernanceLevel.MODERATE

