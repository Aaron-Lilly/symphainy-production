#!/usr/bin/env python3
"""
Unit Tests for SOPBuilderService

Tests the SOP Builder Service functionality including:
- Service initialization
- Wizard session management
- Wizard step processing
- SOP completion
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.journey.services.sop_builder_service.sop_builder_service import SOPBuilderService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class TestSOPBuilderService:
    """Test SOPBuilderService functionality."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        container.get_utility = Mock(return_value=None)
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def sop_builder_service(self, mock_di_container, mock_platform_gateway):
        """Create SOPBuilderService instance."""
        service = SOPBuilderService(
            service_name="SOPBuilderService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        
        # Mock RealmServiceBase methods
        service.get_librarian_api = AsyncMock(return_value=service.librarian)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        # Initialize service
        await service.initialize()
        
        return service
    
    async def test_service_initialization(self, sop_builder_service):
        """Test service initializes correctly."""
        assert sop_builder_service is not None
        assert sop_builder_service.service_name == "SOPBuilderService"
        assert sop_builder_service.realm_name == "journey"
        assert sop_builder_service.is_initialized is True
    
    async def test_start_wizard_session(self, sop_builder_service):
        """Test starting a wizard session."""
        # Execute
        result = await sop_builder_service.start_wizard_session()
        
        # Assert
        assert result["success"] is True
        assert "session_token" in result
        assert result["current_step"] == 1
        assert result["total_steps"] == 5
        assert "next_prompt" in result
        
        # Verify session stored
        assert result["session_token"] in sop_builder_service.wizard_sessions
    
    async def test_process_wizard_step_title(self, sop_builder_service):
        """Test processing wizard step 1 (title)."""
        # Setup - start wizard
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        
        # Execute - provide title
        result = await sop_builder_service.process_wizard_step(session_token, "Customer Onboarding SOP")
        
        # Assert
        assert result["success"] is True
        assert result["current_step"] == 2
        assert "next_prompt" in result
        assert "description" in result["next_prompt"].lower()
        
        # Verify title stored
        session = sop_builder_service.wizard_sessions[session_token]
        assert session["sop_data"]["title"] == "Customer Onboarding SOP"
    
    async def test_process_wizard_step_description(self, sop_builder_service):
        """Test processing wizard step 2 (description)."""
        # Setup - start wizard and provide title
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "Customer Onboarding SOP")
        
        # Execute - provide description
        result = await sop_builder_service.process_wizard_step(session_token, "Standard procedure for onboarding new customers")
        
        # Assert
        assert result["success"] is True
        assert result["current_step"] == 3
        assert "step" in result["next_prompt"].lower()
        
        # Verify description stored
        session = sop_builder_service.wizard_sessions[session_token]
        assert "onboarding" in session["sop_data"]["description"].lower()
    
    async def test_process_wizard_step_steps(self, sop_builder_service):
        """Test processing wizard step 3 (steps)."""
        # Setup - start wizard and provide title/description
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "Customer Onboarding SOP")
        await sop_builder_service.process_wizard_step(session_token, "Standard procedure")
        
        # Execute - provide first step
        result = await sop_builder_service.process_wizard_step(session_token, "Collect customer information")
        
        # Assert
        assert result["success"] is True
        assert result["current_step"] == 3  # Still on step 3 (can add multiple steps)
        assert "added" in result["next_prompt"].lower() or "step" in result["next_prompt"].lower()
        
        # Verify step stored
        session = sop_builder_service.wizard_sessions[session_token]
        assert len(session["sop_data"]["steps"]) == 1
        assert session["sop_data"]["steps"][0]["instruction"] == "Collect customer information"
    
    async def test_process_wizard_step_multiple_steps(self, sop_builder_service):
        """Test adding multiple steps in wizard."""
        # Setup
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "SOP Title")
        await sop_builder_service.process_wizard_step(session_token, "SOP Description")
        
        # Execute - add multiple steps
        await sop_builder_service.process_wizard_step(session_token, "Step 1")
        await sop_builder_service.process_wizard_step(session_token, "Step 2")
        result = await sop_builder_service.process_wizard_step(session_token, "Step 3")
        
        # Assert
        assert result["success"] is True
        session = sop_builder_service.wizard_sessions[session_token]
        assert len(session["sop_data"]["steps"]) == 3
    
    async def test_process_wizard_step_done(self, sop_builder_service):
        """Test moving to review step by saying 'done'."""
        # Setup
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "SOP Title")
        await sop_builder_service.process_wizard_step(session_token, "SOP Description")
        await sop_builder_service.process_wizard_step(session_token, "Step 1")
        
        # Execute - say "done"
        result = await sop_builder_service.process_wizard_step(session_token, "done")
        
        # Assert
        assert result["success"] is True
        assert result["current_step"] == 4  # Moved to review step
    
    async def test_process_wizard_step_review_complete(self, sop_builder_service):
        """Test completing wizard from review step."""
        # Setup - get to review step
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "SOP Title")
        await sop_builder_service.process_wizard_step(session_token, "SOP Description")
        await sop_builder_service.process_wizard_step(session_token, "Step 1")
        await sop_builder_service.process_wizard_step(session_token, "done")
        
        # Execute - complete
        result = await sop_builder_service.process_wizard_step(session_token, "complete")
        
        # Assert
        assert result["success"] is True
        assert result["current_step"] == 5
    
    async def test_process_wizard_step_invalid_session(self, sop_builder_service):
        """Test processing step with invalid session token."""
        # Execute
        result = await sop_builder_service.process_wizard_step("invalid_token", "Some input")
        
        # Assert
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    async def test_complete_wizard_success(self, sop_builder_service):
        """Test successfully completing wizard."""
        # Setup - create complete wizard session
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "Customer Onboarding SOP")
        await sop_builder_service.process_wizard_step(session_token, "Standard procedure")
        await sop_builder_service.process_wizard_step(session_token, "Collect customer information")
        await sop_builder_service.process_wizard_step(session_token, "Verify customer identity")
        await sop_builder_service.process_wizard_step(session_token, "done")
        await sop_builder_service.process_wizard_step(session_token, "complete")
        
        # Execute
        result = await sop_builder_service.complete_wizard(session_token)
        
        # Assert
        assert result["success"] is True
        assert "sop" in result
        assert result["sop"]["title"] == "Customer Onboarding SOP"
        assert len(result["sop"]["steps"]) == 2
        assert result["sop"]["steps"][0]["instruction"] == "Collect customer information"
        assert "sop_id" in result["sop"]
        
        # Verify session marked as completed
        session = sop_builder_service.wizard_sessions[session_token]
        assert session["status"] == "completed"
    
    async def test_complete_wizard_missing_title(self, sop_builder_service):
        """Test completing wizard without title."""
        # Setup - create incomplete wizard session
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        # Don't provide title
        
        # Execute
        result = await sop_builder_service.complete_wizard(session_token)
        
        # Assert
        assert result["success"] is False
        assert "title" in result["error"].lower()
    
    async def test_complete_wizard_no_steps(self, sop_builder_service):
        """Test completing wizard without steps."""
        # Setup - create wizard with title but no steps
        start_result = await sop_builder_service.start_wizard_session()
        session_token = start_result["session_token"]
        await sop_builder_service.process_wizard_step(session_token, "SOP Title")
        await sop_builder_service.process_wizard_step(session_token, "Description")
        await sop_builder_service.process_wizard_step(session_token, "done")
        await sop_builder_service.process_wizard_step(session_token, "complete")
        
        # Execute
        result = await sop_builder_service.complete_wizard(session_token)
        
        # Assert
        assert result["success"] is False
        assert "step" in result["error"].lower()
    
    async def test_complete_wizard_invalid_session(self, sop_builder_service):
        """Test completing wizard with invalid session token."""
        # Execute
        result = await sop_builder_service.complete_wizard("invalid_token")
        
        # Assert
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    async def test_get_service_capabilities(self, sop_builder_service):
        """Test service capabilities retrieval."""
        # Execute
        capabilities = await sop_builder_service.get_service_capabilities()
        
        # Assert
        assert capabilities["service_name"] == "SOPBuilderService"
        assert capabilities["realm"] == "journey"
        assert "sop_building" in capabilities["capabilities"]
        assert "start_wizard_session" in capabilities["soa_apis"]







