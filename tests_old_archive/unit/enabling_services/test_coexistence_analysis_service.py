#!/usr/bin/env python3
"""
Unit Tests for CoexistenceAnalysisService

Tests the Coexistence Analysis enabling service functionality including:
- Service initialization
- SOP/Workflow coexistence analysis
- Gap analysis
- Blueprint generation
- Pattern evaluation
"""

import pytest

import os
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from backend.business_enablement.enabling_services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
from utilities import UserContext

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]

class TestCoexistenceAnalysisService:
    """Test CoexistenceAnalysisService functionality."""
    
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
    async def coexistence_service(self, mock_di_container, mock_platform_gateway):
        """Create CoexistenceAnalysisService instance."""
        service = CoexistenceAnalysisService(
            service_name="CoexistenceAnalysisService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services to avoid initialization issues
        service.librarian = Mock()
        service.librarian.store_document = AsyncMock(return_value={"success": True})
        service.librarian.get_document = AsyncMock(return_value=None)
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
    
    @pytest.fixture
    def sample_sop_content(self):
        """Create sample SOP content."""
        return """
        Title: Software Testing Standard Operating Procedure
        Purpose: Define comprehensive testing procedures
        
        Procedures:
        1. Review requirements and test plan
        2. Set up test environment
        3. Execute test cases
        4. Document test results
        5. Perform peer review
        
        Scope: All software components
        Responsibilities: QA Team
        """
    
    @pytest.fixture
    def sample_workflow_content(self):
        """Create sample workflow content."""
        return {
            "workflow_id": "wf_test_123",
            "name": "Software Testing Workflow",
            "steps": [
                {"step": 1, "action": "Review requirements", "responsible": "QA Lead"},
                {"step": 2, "action": "Setup environment", "responsible": "DevOps"},
                {"step": 3, "action": "Execute tests", "responsible": "QA Engineer"},
                {"step": 4, "action": "Document results", "responsible": "QA Engineer"}
            ]
        }
    
    async def test_service_initialization(self, coexistence_service):
        """Test that CoexistenceAnalysisService initializes correctly."""
        assert coexistence_service.service_name == "CoexistenceAnalysisService"
        assert coexistence_service.realm_name == "business_enablement"
        assert hasattr(coexistence_service, 'coexistence_patterns')
        assert len(coexistence_service.coexistence_patterns) > 0
    
    async def test_analyze_coexistence_success(self, coexistence_service, sample_sop_content, sample_workflow_content, sample_user_context):
        """Test successful coexistence analysis."""
        result = await coexistence_service.analyze_coexistence(
            sop_content=sample_sop_content,
            workflow_content=sample_workflow_content,
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "coexistence_analysis" in result
        assert "alignment_score" in result["coexistence_analysis"]
        assert "gaps" in result["coexistence_analysis"]
        assert "recommendations" in result["coexistence_analysis"]
        assert "sop_analysis" in result
        assert "workflow_analysis" in result
        assert "processing_time" in result
        
        # Verify alignment score is reasonable
        alignment_score = result["coexistence_analysis"]["alignment_score"]
        assert 0 <= alignment_score <= 100
    
    async def test_analyze_coexistence_with_gaps(self, coexistence_service, sample_user_context):
        """Test coexistence analysis with obvious gaps."""
        # SOP with 5 procedures
        sop_content = """
        Procedures:
        1. Step one with quality control
        2. Step two
        3. Step three
        4. Step four
        5. Step five
        """
        
        # Workflow with only 1 step (should trigger count mismatch)
        workflow_content = {
            "steps": [
                {"step": 1, "action": "Do something"}
            ]
        }
        
        result = await coexistence_service.analyze_coexistence(
            sop_content=sop_content,
            workflow_content=workflow_content,
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        gaps = result["coexistence_analysis"]["gaps"]
        
        # Should detect misalignment (5 procedures vs 1 step = difference >2, should create gap)
        assert len(gaps) > 0
        assert result["coexistence_analysis"]["alignment_score"] < 100
    
    async def test_optimize_coexistence_not_found(self, coexistence_service, sample_user_context):
        """Test optimization with non-existent analysis."""
        result = await coexistence_service.optimize_coexistence(
            analysis_id="non_existent_analysis",
            user_context=sample_user_context
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    async def test_optimize_coexistence_with_analysis(self, coexistence_service, sample_sop_content, sample_workflow_content, sample_user_context):
        """Test optimization with existing analysis."""
        # First, perform analysis
        analysis_result = await coexistence_service.analyze_coexistence(
            sop_content=sample_sop_content,
            workflow_content=sample_workflow_content,
            user_context=sample_user_context
        )
        
        # Mock librarian to return the analysis
        analysis_id = "test_analysis_123"
        coexistence_service.librarian.get_document = AsyncMock(return_value={
            "data": {
                "gap_analysis": {"gaps": ["Gap 1", "Gap 2"]},
                "alignment_score": 75
            }
        })
        
        # Now optimize
        result = await coexistence_service.optimize_coexistence(
            analysis_id=analysis_id,
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "optimization_strategies" in result
        assert len(result["optimization_strategies"]) > 0
    
    async def test_create_blueprint(self, coexistence_service, sample_user_context):
        """Test blueprint creation."""
        result = await coexistence_service.create_blueprint(
            sop_id="sop_123",
            workflow_id="wf_456",
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "blueprint" in result
        
        blueprint = result["blueprint"]
        assert "blueprint_id" in blueprint
        assert "sop_id" in blueprint
        assert "workflow_id" in blueprint
        assert "implementation_phases" in blueprint
        assert "success_metrics" in blueprint
        assert "coexistence_pattern" in blueprint
    
    async def test_evaluate_patterns(self, coexistence_service, sample_user_context):
        """Test pattern evaluation."""
        current_state = {
            "process_count": 5,
            "automation_level": "low",
            "complexity": "medium"
        }
        
        target_state = {
            "process_count": 5,
            "automation_level": "high",
            "complexity": "low"
        }
        
        result = await coexistence_service.evaluate_patterns(
            current_state=current_state,
            target_state=target_state,
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "current_pattern" in result
        assert "target_pattern" in result
        assert "transition_path" in result
        assert "estimated_duration_days" in result
    
    async def test_pattern_library_structure(self, coexistence_service):
        """Test that coexistence patterns have correct structure."""
        patterns = coexistence_service.coexistence_patterns
        
        # Verify each pattern has required fields
        for pattern_name, pattern in patterns.items():
            assert "description" in pattern
            assert "characteristics" in pattern
            assert isinstance(pattern["characteristics"], list)
    
    async def test_sop_analysis(self, coexistence_service, sample_sop_content):
        """Test SOP analysis component."""
        result = await coexistence_service._analyze_sop(sample_sop_content)
        
        assert "total_procedures" in result
        assert "procedures" in result
        assert isinstance(result["total_procedures"], int)
        assert result["total_procedures"] >= 0
    
    async def test_workflow_analysis(self, coexistence_service, sample_workflow_content):
        """Test workflow analysis component."""
        result = await coexistence_service._analyze_workflow(sample_workflow_content)
        
        assert "total_steps" in result
        assert "steps" in result
        assert isinstance(result["total_steps"], int)
        assert result["total_steps"] > 0
    
    async def test_gap_analysis(self, coexistence_service):
        """Test gap analysis logic."""
        sop_analysis = {
            "total_procedures": 6,
            "procedures": ["1", "2", "3", "4", "5", "6"],
            "has_quality_control": False,
            "has_responsibilities": False
        }
        
        workflow_analysis = {
            "total_steps": 2,
            "steps": [{"step": 1}, {"step": 2}],
            "has_automation": False,
            "has_validation": False
        }
        
        result = await coexistence_service._perform_gap_analysis(
            sop_analysis, workflow_analysis
        )
        
        assert "gaps" in result
        assert isinstance(result["gaps"], list)
        # Should detect step count mismatch (6 procedures vs 2 steps = difference >2)
        assert len(result["gaps"]) > 0
    
    async def test_alignment_score_calculation(self, coexistence_service):
        """Test alignment score calculation."""
        # Perfect alignment
        gap_analysis = {"gaps": []}
        score = coexistence_service._calculate_alignment_score(gap_analysis)
        assert score == 100
        
        # Some gaps (gaps should be dict objects with severity)
        gap_analysis_with_gaps = {
            "gaps": [
                {"type": "count_mismatch", "description": "Gap 1", "severity": "high"},
                {"type": "missing_validation", "description": "Gap 2", "severity": "medium"},
                {"type": "other", "description": "Gap 3", "severity": "low"}
            ]
        }
        score_with_gaps = coexistence_service._calculate_alignment_score(gap_analysis_with_gaps)
        assert score_with_gaps < 100
        assert score_with_gaps >= 0
    
    async def test_empty_sop_content(self, coexistence_service, sample_workflow_content, sample_user_context):
        """Test analysis with empty SOP content."""
        result = await coexistence_service.analyze_coexistence(
            sop_content="",
            workflow_content=sample_workflow_content,
            user_context=sample_user_context
        )
        
        # Should still complete without crashing
        assert "success" in result
        assert result["success"] is True
        # Empty SOP (0 procedures) vs workflow with steps should create gaps
        assert "coexistence_analysis" in result
    
    async def test_empty_workflow_content(self, coexistence_service, sample_sop_content, sample_user_context):
        """Test analysis with empty workflow content."""
        result = await coexistence_service.analyze_coexistence(
            sop_content=sample_sop_content,
            workflow_content={"steps": []},
            user_context=sample_user_context
        )
        
        # Should still complete without crashing
        assert "success" in result
        assert result["success"] is True
        # SOP with procedures vs empty workflow (0 steps) should create gaps
        assert "coexistence_analysis" in result
    
    async def test_complex_workflow_structure(self, coexistence_service, sample_sop_content, sample_user_context):
        """Test analysis with complex workflow structure."""
        complex_workflow = {
            "workflow_id": "complex_wf",
            "name": "Complex Testing Workflow",
            "steps": [
                {"step": 1, "action": "Initial review", "responsible": "Team Lead", "parallel": False},
                {"step": 2, "action": "Setup phase 1", "responsible": "DevOps", "parallel": True},
                {"step": 3, "action": "Setup phase 2", "responsible": "DevOps", "parallel": True},
                {"step": 4, "action": "Execute tests", "responsible": "QA", "parallel": False},
                {"step": 5, "action": "Review results", "responsible": "Team Lead", "parallel": False}
            ],
            "decision_points": ["After step 4"],
            "loops": ["Steps 2-4 if tests fail"]
        }
        
        result = await coexistence_service.analyze_coexistence(
            sop_content=sample_sop_content,
            workflow_content=complex_workflow,
            user_context=sample_user_context
        )
        
        assert result["success"] is True
        assert "workflow_analysis" in result
        # Complex workflows should be analyzed properly
        assert result["workflow_analysis"]["total_steps"] == 5

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

