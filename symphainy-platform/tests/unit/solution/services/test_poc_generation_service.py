#!/usr/bin/env python3
"""
Unit Tests for POCGenerationService

Tests the POC Generation Service functionality including:
- Service initialization
- POC proposal generation from pillar outputs
- Financial calculations (ROI, NPV, IRR, payback)
- Executive summary generation
- Proposal validation
- Flexible input handling (partial pillars)
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.solution.services.poc_generation_service.poc_generation_service import POCGenerationService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class TestPOCGenerationService:
    """Test POCGenerationService functionality."""
    
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
    async def poc_generation_service(self, mock_di_container, mock_platform_gateway):
        """Create POCGenerationService instance."""
        service = POCGenerationService(
            service_name="POCGenerationService",
            realm_name="solution",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.librarian = Mock()
        service.solution_composer = None
        
        # Mock RealmServiceBase methods
        service.get_librarian_api = AsyncMock(return_value=service.librarian)
        service.get_enabling_service = AsyncMock(return_value=None)
        service.register_with_curator = AsyncMock(return_value=True)
        service.log_operation_with_telemetry = AsyncMock()
        service.handle_error_with_audit = AsyncMock()
        service.record_health_metric = AsyncMock()
        
        # Initialize service
        await service.initialize()
        
        return service
    
    @pytest.fixture
    def sample_content_pillar_output(self):
        """Create sample content pillar output."""
        return {
            "success": True,
            "semantic_data_model": {
                "structured_files": {
                    "count": 5,
                    "files": ["file1.csv", "file2.csv", "file3.csv", "file4.csv", "file5.csv"]
                },
                "unstructured_files": {
                    "count": 3,
                    "files": ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
                }
            }
        }
    
    @pytest.fixture
    def sample_insights_pillar_output(self):
        """Create sample insights pillar output."""
        return {
            "success": True,
            "summary": {
                "textual": "Q4 revenue shows 15% growth. Product A is strongest with $1.2M (15% growth).",
                "tabular": {
                    "revenue_breakdown": [
                        {"product": "Product A", "revenue": 1200000, "growth": 0.15}
                    ]
                }
            }
        }
    
    @pytest.fixture
    def sample_operations_pillar_output(self):
        """Create sample operations pillar output."""
        return {
            "success": True,
            "artifacts": {
                "workflows": [
                    {
                        "artifact_id": "artifact_123",
                        "title": "Customer Onboarding Workflow",
                        "status": "draft"
                    }
                ],
                "sops": [
                    {
                        "artifact_id": "artifact_124",
                        "title": "Customer Onboarding SOP",
                        "status": "draft"
                    }
                ],
                "coexistence_blueprints": [
                    {
                        "artifact_id": "artifact_125",
                        "title": "SOP-Workflow Coexistence Blueprint",
                        "status": "draft",
                        "alignment_score": 0.85
                    }
                ]
            }
        }
    
    async def test_service_initialization(self, poc_generation_service):
        """Test service initializes correctly."""
        assert poc_generation_service is not None
        assert poc_generation_service.service_name == "POCGenerationService"
        assert poc_generation_service.realm_name == "solution"
        assert poc_generation_service.is_initialized is True
    
    async def test_generate_poc_proposal_all_pillars(
        self,
        poc_generation_service,
        sample_content_pillar_output,
        sample_insights_pillar_output,
        sample_operations_pillar_output
    ):
        """Test POC proposal generation with all three pillars."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output,
            "insights_pillar": sample_insights_pillar_output,
            "operations_pillar": sample_operations_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs,
            poc_type="hybrid"
        )
        
        # Assert
        assert result["success"] is True
        assert "poc_proposal" in result
        
        proposal = result["poc_proposal"]
        assert "proposal_id" in proposal
        assert "objectives" in proposal
        assert "scope" in proposal
        assert "timeline" in proposal
        assert "resource_requirements" in proposal
        assert "success_criteria" in proposal
        assert "financials" in proposal
        assert "executive_summary" in proposal
        assert len(proposal["objectives"]) > 0
        assert len(proposal["success_criteria"]) > 0
        assert proposal["pillar_sources"] == ["content", "insights", "operations"]
    
    async def test_generate_poc_proposal_content_only(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test POC proposal generation with only content pillar."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs,
            poc_type="data_focused"
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        assert "content" in proposal["pillar_sources"]
        assert proposal["poc_type"] == "data_focused"
    
    async def test_generate_poc_proposal_insights_only(
        self,
        poc_generation_service,
        sample_insights_pillar_output
    ):
        """Test POC proposal generation with only insights pillar."""
        # Setup
        pillar_outputs = {
            "insights_pillar": sample_insights_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs,
            poc_type="analytics_focused"
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        assert "insights" in proposal["pillar_sources"]
        assert proposal["poc_type"] == "analytics_focused"
    
    async def test_generate_poc_proposal_operations_only(
        self,
        poc_generation_service,
        sample_operations_pillar_output
    ):
        """Test POC proposal generation with only operations pillar."""
        # Setup
        pillar_outputs = {
            "operations_pillar": sample_operations_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs,
            poc_type="process_focused"
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        assert "operations" in proposal["pillar_sources"]
        assert proposal["poc_type"] == "process_focused"
    
    async def test_generate_poc_proposal_no_pillars(self, poc_generation_service):
        """Test POC proposal generation with no pillar outputs."""
        # Setup
        pillar_outputs = {}
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is False
        assert "No pillar outputs available" in result["error"]
    
    async def test_generate_poc_proposal_with_options(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test POC proposal generation with custom options."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        options = {
            "name": "Custom POC Name",
            "budget": 200000,
            "timeline_days": 120
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs,
            poc_type="hybrid",
            options=options
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        assert proposal["name"] == "Custom POC Name"
    
    async def test_calculate_financials(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test financial calculations for POC proposal."""
        # Setup - generate a proposal first
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        proposal_result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        poc_proposal = proposal_result["poc_proposal"]
        
        # Execute
        result = await poc_generation_service.calculate_financials(poc_proposal)
        
        # Assert
        assert result["success"] is True
        assert "financials" in result
        
        financials = result["financials"]
        assert "estimated_cost" in financials
        assert "annual_benefits" in financials
        assert "roi_percentage" in financials
        assert "npv" in financials
        assert "irr_percentage" in financials
        assert "payback_period_years" in financials
        assert financials["estimated_cost"] >= 0
        assert financials["annual_benefits"] >= 0
    
    async def test_generate_executive_summary(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test executive summary generation."""
        # Setup - generate a proposal first
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        proposal_result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        poc_proposal = proposal_result["poc_proposal"]
        
        # Execute
        result = await poc_generation_service.generate_executive_summary(poc_proposal)
        
        # Assert
        assert result["success"] is True
        assert "executive_summary" in result
        assert len(result["executive_summary"]) > 0
        assert "POC" in result["executive_summary"] or "proof of concept" in result["executive_summary"].lower()
    
    async def test_validate_poc_proposal_valid(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test POC proposal validation with valid proposal."""
        # Setup - generate a proposal first
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        proposal_result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        poc_proposal = proposal_result["poc_proposal"]
        
        # Execute
        result = await poc_generation_service.validate_poc_proposal(poc_proposal)
        
        # Assert
        assert result["success"] is True
        assert result["is_valid"] is True
        assert len(result["missing_fields"]) == 0
    
    async def test_validate_poc_proposal_invalid(
        self,
        poc_generation_service
    ):
        """Test POC proposal validation with invalid proposal."""
        # Setup - create incomplete proposal
        incomplete_proposal = {
            "proposal_id": "test_123",
            "name": "Test POC"
            # Missing required fields
        }
        
        # Execute
        result = await poc_generation_service.validate_poc_proposal(incomplete_proposal)
        
        # Assert
        assert result["success"] is False
        assert result["is_valid"] is False
        assert len(result["missing_fields"]) > 0
    
    async def test_poc_proposal_includes_scope(
        self,
        poc_generation_service,
        sample_content_pillar_output,
        sample_operations_pillar_output
    ):
        """Test that POC proposal includes detailed scope."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output,
            "operations_pillar": sample_operations_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        scope = proposal["scope"]
        assert "in_scope" in scope
        assert "out_of_scope" in scope
        assert "assumptions" in scope
        assert "risks" in scope
        assert len(scope["in_scope"]) > 0
    
    async def test_poc_proposal_includes_timeline(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test that POC proposal includes timeline."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        timeline = proposal["timeline"]
        assert "start_date" in timeline
        assert "end_date" in timeline
        assert "duration_days" in timeline
        assert "phases" in timeline
        assert timeline["duration_days"] > 0
        assert len(timeline["phases"]) > 0
    
    async def test_poc_proposal_includes_resource_requirements(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test that POC proposal includes resource requirements."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        resources = proposal["resource_requirements"]
        assert "team_size" in resources
        assert "roles" in resources
        assert "effort_person_days" in resources
        assert "estimated_cost" in resources
        assert resources["team_size"] > 0
        assert len(resources["roles"]) > 0
    
    async def test_poc_proposal_financials_calculated(
        self,
        poc_generation_service,
        sample_content_pillar_output
    ):
        """Test that POC proposal includes calculated financials."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        
        # Execute
        result = await poc_generation_service.generate_poc_proposal(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        proposal = result["poc_proposal"]
        financials = proposal["financials"]
        assert "estimated_cost" in financials
        assert "annual_benefits" in financials
        assert "roi_percentage" in financials
        assert "npv" in financials
        assert "irr_percentage" in financials
        assert "payback_period_years" in financials
        assert "currency" in financials
        assert financials["currency"] == "USD"







