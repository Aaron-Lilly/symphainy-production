#!/usr/bin/env python3
"""
Unit Tests for SOPBuilderService

Tests the SOP Builder enabling service functionality including:
- Service initialization
- Wizard session management
- SOP creation and validation
- Template handling
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.business_enablement.enabling_services.sop_builder_service.sop_builder_service import SOPBuilderService
from utilities import UserContext

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

class TestSOPBuilderService:
    """Test SOPBuilderService functionality."""
    
    @pytest.fixture
    async def mock_di_container(self):
        """Create mock DI container."""
        container = Mock()
        container.get_foundation_service = Mock(return_value=None)
        return container
    
    @pytest.fixture
    async def mock_platform_gateway(self):
        """Create mock platform gateway."""
        gateway = Mock()
        gateway.get_smart_city_service = AsyncMock(return_value=None)
        return gateway
    
    @pytest.fixture
    async def sop_builder_service(self, mock_di_container, mock_platform_gateway):
        """Create SOPBuilderService instance."""
        service = SOPBuilderService(
            service_name="SOPBuilderService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services to avoid initialization issues
        service.librarian = Mock()
        service.librarian.store_document = AsyncMock(return_value={"success": True})
        service.data_steward = Mock()
        service.curator = Mock()
        service.curator.register_service = AsyncMock(return_value=True)
        
        return service
    
    @pytest.fixture
    def sample_user_context(self):
        """Create sample user context."""
        return UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["read", "write"],
            tenant_id="test_tenant_456"
        )
    
    async def test_service_initialization(self, sop_builder_service):
        """Test that SOPBuilderService initializes correctly."""
        assert sop_builder_service.service_name == "SOPBuilderService"
        assert sop_builder_service.realm_name == "business_enablement"
        assert hasattr(sop_builder_service, 'sop_templates')
        assert hasattr(sop_builder_service, 'wizard_sessions')
        assert len(sop_builder_service.sop_templates) == 3  # standard, technical, administrative
    
    async def test_sop_templates_structure(self, sop_builder_service):
        """Test that SOP templates have correct structure."""
        templates = sop_builder_service.sop_templates
        
        # Check standard template
        assert "standard" in templates
        assert "sections" in templates["standard"]
        assert "required_fields" in templates["standard"]
        assert "purpose" in templates["standard"]["sections"]
        assert "title" in templates["standard"]["required_fields"]
        
        # Check technical template
        assert "technical" in templates
        assert "step_by_step" in templates["technical"]["sections"]
        
        # Check administrative template
        assert "administrative" in templates
        assert "policy" in templates["administrative"]["sections"]
    
    async def test_start_wizard_session(self, sop_builder_service, sample_user_context):
        """Test starting a wizard session."""
        result = await sop_builder_service.start_wizard_session(
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "session_token" in result
        assert "wizard_state" in result
        assert result["wizard_state"]["current_step"] == 1
        assert result["wizard_state"]["total_steps"] == 5
        
        # Verify session is stored
        session_token = result["session_token"]
        assert session_token in sop_builder_service.wizard_sessions
    
    async def test_process_wizard_step(self, sop_builder_service, sample_user_context):
        """Test processing a wizard step."""
        # Start session first
        start_result = await sop_builder_service.start_wizard_session(
            user_context=sample_user_context
        )
        session_token = start_result["session_token"]
        
        # Process first step (answering the SOP type question)
        step_result = await sop_builder_service.process_wizard_step(
            session_token=session_token,
            user_input="standard",
            user_context=sample_user_context
        )
        
        assert step_result["success"] is True
        assert "wizard_state" in step_result
        
        # Verify session was updated
        session = sop_builder_service.wizard_sessions[session_token]
        assert session["current_step"] > 1  # Should have progressed
        assert "sop_data" in session
    
    async def test_validate_sop_success(self, sop_builder_service):
        """Test SOP validation with valid data."""
        sop_data = {
            "title": "Test SOP",
            "purpose": "Define testing procedures",
            "procedures": ["Step 1: Prepare", "Step 2: Execute", "Step 3: Verify"],
            "scope": "All testing activities",
            "responsibilities": "QA Team"
        }
        
        result = await sop_builder_service.validate_sop(
            sop_data=sop_data
        )
        
        assert result["valid"] is True
        assert result["score"] >= 60  # Should have decent score with all required fields
        assert len(result["errors"]) == 0
    
    async def test_validate_sop_missing_required_fields(self, sop_builder_service):
        """Test SOP validation with missing required fields."""
        sop_data = {
            "title": "Test SOP"
            # Missing purpose and procedures (required fields)
        }
        
        result = await sop_builder_service.validate_sop(
            sop_data=sop_data
        )
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("purpose" in str(error).lower() for error in result["errors"])
    
    async def test_create_sop_with_data(self, sop_builder_service, sample_user_context):
        """Test SOP creation with provided data."""
        sop_data = {
            "title": "Software Testing SOP",
            "purpose": "Define testing procedures",
            "procedures": "Prepare test environment, Execute tests, Document results",
            "scope": "All software components",
            "responsibilities": "QA Team",
            "quality_control": "Peer review required"
        }
        
        result = await sop_builder_service.create_sop(
            description="Software testing procedures",
            sop_data=sop_data,
            template_type="standard",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "sop_id" in result
        assert "sop_content" in result
        assert result["template_type"] == "standard"
    
    async def test_create_sop_from_description(self, sop_builder_service, sample_user_context):
        """Test SOP creation from description only - may fail validation without complete data."""
        result = await sop_builder_service.create_sop(
            description="Create a standard SOP for testing procedures",
            template_type="standard",  # Use standard template which has fewer required fields
            user_context=sample_user_context
        )
        
        # Auto-generated SOPs from description alone may not pass validation
        # This is expected behavior - wizard or complete data is better approach
        if result.get("success"):
            # If it succeeds, verify structure
            assert "sop_id" in result
            assert result["template_type"] == "standard"
        else:
            # If it fails validation, verify we get proper error info
            assert "error" in result
            assert "validation_results" in result
            assert result["validation_results"]["valid"] is False
            # This is acceptable - description alone may not be enough for complete SOP
    
    async def test_wizard_session_not_found(self, sop_builder_service, sample_user_context):
        """Test processing wizard step with invalid session token."""
        result = await sop_builder_service.process_wizard_step(
            session_token="invalid_session_token",
            user_input="test input",
            user_context=sample_user_context
        )
        
        assert result["success"] is False
        assert "error" in result or "message" in result
    
    async def test_sop_scoring_algorithm(self, sop_builder_service):
        """Test SOP scoring algorithm."""
        # Minimal SOP (should have lower score due to missing fields)
        minimal_sop = {
            "title": "Test",
            "purpose": "Test"
            # Missing procedures (required)
        }
        
        minimal_result = await sop_builder_service.validate_sop(
            sop_data=minimal_sop
        )
        
        # Comprehensive SOP (should have high score)
        comprehensive_sop = {
            "title": "Comprehensive Testing Standard Operating Procedure",
            "purpose": "This SOP defines comprehensive testing procedures for all software components",
            "procedures": "Step 1: Prepare test environment, Step 2: Execute tests, Step 3: Verify results",
            "scope": "Applies to all software testing activities",
            "responsibilities": "QA Team leads testing",
            "quality_control": "Peer review required",
            "sections": {
                "purpose": "Define testing",
                "scope": "All activities",
                "responsibilities": "QA Team",
                "procedures": "Testing steps",
                "quality_control": "Reviews"
            }
        }
        
        comprehensive_result = await sop_builder_service.validate_sop(
            sop_data=comprehensive_sop
        )
        
        # Comprehensive SOP should score higher (or at least be valid if minimal is not)
        assert comprehensive_result["valid"] is True
        assert comprehensive_result["score"] >= 85  # Should be high quality
        
        # Minimal should have lower score or be invalid
        if not minimal_result["valid"]:
            assert len(minimal_result["errors"]) > 0
        else:
            assert minimal_result["score"] < comprehensive_result["score"]
    
    async def test_multi_step_wizard_flow(self, sop_builder_service, sample_user_context):
        """Test a multi-step wizard flow."""
        # Start wizard
        start_result = await sop_builder_service.start_wizard_session(
            user_context=sample_user_context
        )
        session_token = start_result["session_token"]
        
        # Step 1: SOP type
        step1 = await sop_builder_service.process_wizard_step(
            session_token=session_token,
            user_input="technical",
            user_context=sample_user_context
        )
        assert step1["success"] is True
        
        # Step 2: Additional input
        step2 = await sop_builder_service.process_wizard_step(
            session_token=session_token,
            user_input="System maintenance procedures for database servers",
            user_context=sample_user_context
        )
        assert step2["success"] is True
        
        # Verify session progressed
        session = sop_builder_service.wizard_sessions[session_token]
        assert session["current_step"] > 1

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
