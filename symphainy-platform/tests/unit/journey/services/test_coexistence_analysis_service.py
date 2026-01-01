#!/usr/bin/env python3
"""
Unit Tests for CoexistenceAnalysisService

Tests the Coexistence Analysis Service functionality including:
- Service initialization
- Coexistence analysis
- Blueprint generation
- Gap and opportunity identification
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.journey.services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class TestCoexistenceAnalysisService:
    """Test CoexistenceAnalysisService functionality."""
    
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
    async def coexistence_service(self, mock_di_container, mock_platform_gateway):
        """Create CoexistenceAnalysisService instance."""
        service = CoexistenceAnalysisService(
            service_name="CoexistenceAnalysisService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.librarian.get_document = AsyncMock()
        
        # Mock RealmServiceBase methods
        service.get_librarian_api = AsyncMock(return_value=service.librarian)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        # Initialize service
        await service.initialize()
        
        return service
    
    @pytest.fixture
    def sample_sop_content(self):
        """Create sample SOP content."""
        return {
            "title": "Customer Onboarding SOP",
            "description": "Standard operating procedure",
            "steps": [
                {"step_number": 1, "instruction": "Collect customer information", "details": "Gather name, email"},
                {"step_number": 2, "instruction": "Verify customer identity", "details": "Check ID"},
                {"step_number": 3, "instruction": "Create customer account", "details": "Set up account"}
            ]
        }
    
    @pytest.fixture
    def sample_workflow_content(self):
        """Create sample workflow content."""
        return {
            "title": "Customer Onboarding Workflow",
            "description": "Workflow for onboarding",
            "steps": [
                {"step_id": "step_1", "name": "Collect customer information", "description": "Gather name, email", "order": 1},
                {"step_id": "step_2", "name": "Verify customer identity", "description": "Check ID", "order": 2},
                {"step_id": "step_3", "name": "Create customer account", "description": "Set up account", "order": 3},
                {"step_id": "step_4", "name": "Send welcome email", "description": "Email confirmation", "order": 4}
            ]
        }
    
    @pytest.fixture
    def sample_sop_file(self):
        """Create sample SOP file document."""
        return {
            "document_id": "sop_file_123",
            "data": {
                "title": "Customer Onboarding SOP",
                "steps": [
                    {"step_number": 1, "instruction": "Collect customer information"},
                    {"step_number": 2, "instruction": "Verify customer identity"}
                ]
            },
            "metadata": {"file_type": "sop"}
        }
    
    @pytest.fixture
    def sample_workflow_file(self):
        """Create sample workflow file document."""
        return {
            "document_id": "workflow_file_123",
            "data": {
                "title": "Customer Onboarding Workflow",
                "steps": [
                    {"step_id": "step_1", "name": "Collect customer information", "order": 1},
                    {"step_id": "step_2", "name": "Verify customer identity", "order": 2},
                    {"step_id": "step_3", "name": "Send welcome email", "order": 3}
                ]
            },
            "metadata": {"file_type": "workflow"}
        }
    
    async def test_service_initialization(self, coexistence_service):
        """Test service initializes correctly."""
        assert coexistence_service is not None
        assert coexistence_service.service_name == "CoexistenceAnalysisService"
        assert coexistence_service.realm_name == "journey"
        assert coexistence_service.is_initialized is True
    
    async def test_analyze_coexistence_success(self, coexistence_service, sample_sop_content, sample_workflow_content):
        """Test successful coexistence analysis."""
        # Execute
        result = await coexistence_service.analyze_coexistence(
            sample_sop_content,
            sample_workflow_content
        )
        
        # Assert
        assert result["success"] is True
        assert "analysis" in result
        assert "blueprint" in result
        assert "coexistence_blueprint" in result  # Alias
        
        # Check analysis structure
        analysis = result["analysis"]
        assert "analysis_id" in analysis
        assert analysis["sop_step_count"] == 3
        assert analysis["workflow_step_count"] == 4
        assert "gaps" in analysis
        assert "opportunities" in analysis
        assert "recommendations" in analysis
        
        # Check blueprint structure
        blueprint = result["blueprint"]
        assert "blueprint_id" in blueprint
        assert "sop_summary" in blueprint
        assert "workflow_summary" in blueprint
        assert "optimization_opportunities" in blueprint
        assert "gaps_to_address" in blueprint
    
    async def test_analyze_coexistence_identifies_gaps(self, coexistence_service):
        """Test that analysis identifies gaps (SOP steps not in workflow)."""
        sop_content = {
            "title": "SOP",
            "steps": [
                {"step_number": 1, "instruction": "Step A"},
                {"step_number": 2, "instruction": "Step B"},
                {"step_number": 3, "instruction": "Step C (SOP only)"}
            ]
        }
        workflow_content = {
            "title": "Workflow",
            "steps": [
                {"step_id": "step_1", "name": "Step A", "order": 1},
                {"step_id": "step_2", "name": "Step B", "order": 2}
            ]
        }
        
        # Execute
        result = await coexistence_service.analyze_coexistence(sop_content, workflow_content)
        
        # Assert
        assert result["success"] is True
        gaps = result["analysis"]["gaps"]
        assert len(gaps) > 0
        assert any("Step C" in str(gap) for gap in gaps)
    
    async def test_analyze_coexistence_identifies_opportunities(self, coexistence_service):
        """Test that analysis identifies opportunities (workflow steps not in SOP)."""
        sop_content = {
            "title": "SOP",
            "steps": [
                {"step_number": 1, "instruction": "Step A"},
                {"step_number": 2, "instruction": "Step B"}
            ]
        }
        workflow_content = {
            "title": "Workflow",
            "steps": [
                {"step_id": "step_1", "name": "Step A", "order": 1},
                {"step_id": "step_2", "name": "Step B", "order": 2},
                {"step_id": "step_3", "name": "Step C (Workflow only)", "order": 3}
            ]
        }
        
        # Execute
        result = await coexistence_service.analyze_coexistence(sop_content, workflow_content)
        
        # Assert
        assert result["success"] is True
        opportunities = result["analysis"]["opportunities"]
        assert len(opportunities) > 0
        assert any("Step C" in str(opp) for opp in opportunities)
    
    async def test_analyze_coexistence_well_aligned(self, coexistence_service):
        """Test analysis when SOP and workflow are well-aligned."""
        sop_content = {
            "title": "SOP",
            "steps": [
                {"step_number": 1, "instruction": "Step A"},
                {"step_number": 2, "instruction": "Step B"}
            ]
        }
        workflow_content = {
            "title": "Workflow",
            "steps": [
                {"step_id": "step_1", "name": "Step A", "order": 1},
                {"step_id": "step_2", "name": "Step B", "order": 2}
            ]
        }
        
        # Execute
        result = await coexistence_service.analyze_coexistence(sop_content, workflow_content)
        
        # Assert
        assert result["success"] is True
        gaps = result["analysis"]["gaps"]
        opportunities = result["analysis"]["opportunities"]
        # Should have no gaps or opportunities if well-aligned
        assert len(gaps) == 0
        assert len(opportunities) == 0
        # Should have positive recommendation
        recommendations = result["analysis"]["recommendations"]
        assert any("well-aligned" in str(rec).lower() or "good" in str(rec).lower() for rec in recommendations)
    
    async def test_analyze_coexistence_plain_text_sop(self, coexistence_service):
        """Test analysis with plain text SOP content."""
        sop_content = "Step 1: Collect information\nStep 2: Verify identity\nStep 3: Create account"
        workflow_content = {
            "title": "Workflow",
            "steps": [
                {"step_id": "step_1", "name": "Collect information", "order": 1},
                {"step_id": "step_2", "name": "Verify identity", "order": 2}
            ]
        }
        
        # Execute
        result = await coexistence_service.analyze_coexistence(sop_content, workflow_content)
        
        # Assert
        assert result["success"] is True
        assert "analysis" in result
        assert "blueprint" in result
    
    async def test_create_blueprint_success(self, coexistence_service, sample_sop_file, sample_workflow_file):
        """Test successful blueprint creation from file IDs."""
        # Setup
        coexistence_service.librarian.get_document.side_effect = [
            sample_sop_file,
            sample_workflow_file
        ]
        
        # Execute
        result = await coexistence_service.create_blueprint("sop_file_123", "workflow_file_123")
        
        # Assert
        assert result["success"] is True
        assert "blueprint" in result
        assert "blueprint_id" in result["blueprint"]
        assert result["blueprint"]["sop_id"] == "sop_file_123"
        assert result["blueprint"]["workflow_id"] == "workflow_file_123"
    
    async def test_create_blueprint_sop_not_found(self, coexistence_service):
        """Test blueprint creation when SOP file not found."""
        # Setup
        coexistence_service.librarian.get_document.return_value = None
        
        # Execute
        result = await coexistence_service.create_blueprint("nonexistent_sop", "workflow_file_123")
        
        # Assert
        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert "sop" in result["error"].lower() or "nonexistent" in result["error"].lower()
    
    async def test_create_blueprint_workflow_not_found(self, coexistence_service, sample_sop_file):
        """Test blueprint creation when workflow file not found."""
        # Setup
        coexistence_service.librarian.get_document.side_effect = [
            sample_sop_file,
            None  # Workflow not found
        ]
        
        # Execute
        result = await coexistence_service.create_blueprint("sop_file_123", "nonexistent_workflow")
        
        # Assert
        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert "workflow" in result["error"].lower() or "nonexistent" in result["error"].lower()
    
    async def test_create_blueprint_no_librarian(self, mock_di_container, mock_platform_gateway):
        """Test blueprint creation when Librarian is not available."""
        service = CoexistenceAnalysisService(
            service_name="CoexistenceAnalysisService",
            realm_name="journey",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock methods
        service.get_librarian_api = AsyncMock(return_value=None)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        await service.initialize()
        
        # Execute
        result = await service.create_blueprint("sop_file_123", "workflow_file_123")
        
        # Assert
        assert result["success"] is False
        assert "not available" in result["error"].lower()
    
    async def test_get_service_capabilities(self, coexistence_service):
        """Test service capabilities retrieval."""
        # Execute
        capabilities = await coexistence_service.get_service_capabilities()
        
        # Assert
        assert capabilities["service_name"] == "CoexistenceAnalysisService"
        assert capabilities["realm"] == "journey"
        assert "coexistence_analysis" in capabilities["capabilities"]
        assert "analyze_coexistence" in capabilities["soa_apis"]







