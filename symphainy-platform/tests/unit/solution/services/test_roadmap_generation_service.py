#!/usr/bin/env python3
"""
Unit Tests for RoadmapGenerationService

Tests the Roadmap Generation Service functionality including:
- Service initialization
- Roadmap generation from pillar outputs
- Comprehensive strategic plan creation
- Flexible input handling (partial pillars)
"""

import pytest
import os
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.solution.services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class TestRoadmapGenerationService:
    """Test RoadmapGenerationService functionality."""
    
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
    async def roadmap_generation_service(self, mock_di_container, mock_platform_gateway):
        """Create RoadmapGenerationService instance."""
        service = RoadmapGenerationService(
            service_name="RoadmapGenerationService",
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
                },
                "column_embeddings": {
                    "count": 23
                },
                "semantic_graph": {
                    "entities": 45,
                    "relationships": 28
                },
                "arango_storage": {
                    "documents": 96
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
                        {"product": "Product A", "revenue": 1200000, "growth": 0.15},
                        {"product": "Product B", "revenue": 980000, "growth": 0.08}
                    ]
                },
                "visualizations": []
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
                        "status": "draft",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "sops": [
                    {
                        "artifact_id": "artifact_124",
                        "title": "Customer Onboarding SOP",
                        "status": "draft",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "coexistence_blueprints": [
                    {
                        "artifact_id": "artifact_125",
                        "title": "SOP-Workflow Coexistence Blueprint",
                        "status": "draft",
                        "alignment_score": 0.85,
                        "gaps_identified": 3,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
    
    async def test_service_initialization(self, roadmap_generation_service):
        """Test service initializes correctly."""
        assert roadmap_generation_service is not None
        assert roadmap_generation_service.service_name == "RoadmapGenerationService"
        assert roadmap_generation_service.realm_name == "solution"
        assert roadmap_generation_service.is_initialized is True
    
    async def test_generate_roadmap_all_pillars(
        self,
        roadmap_generation_service,
        sample_content_pillar_output,
        sample_insights_pillar_output,
        sample_operations_pillar_output
    ):
        """Test roadmap generation with all three pillars."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output,
            "insights_pillar": sample_insights_pillar_output,
            "operations_pillar": sample_operations_pillar_output
        }
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs,
            business_context={"business_name": "Test Business"}
        )
        
        # Assert
        assert result["success"] is True
        assert "roadmap_id" in result
        assert "roadmap" in result
        assert "visualization" in result
        
        roadmap = result["roadmap"]
        assert "phases" in roadmap
        assert "milestones" in roadmap
        assert "timeline" in roadmap
        assert "dependencies" in roadmap
        assert len(roadmap["phases"]) > 0
        assert len(roadmap["milestones"]) > 0
        assert roadmap["pillar_sources"] == ["content", "insights", "operations"]
    
    async def test_generate_roadmap_content_only(
        self,
        roadmap_generation_service,
        sample_content_pillar_output
    ):
        """Test roadmap generation with only content pillar."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        assert "roadmap" in result
        roadmap = result["roadmap"]
        assert "content" in roadmap["pillar_sources"]
        assert len(roadmap["phases"]) > 0
    
    async def test_generate_roadmap_insights_only(
        self,
        roadmap_generation_service,
        sample_insights_pillar_output
    ):
        """Test roadmap generation with only insights pillar."""
        # Setup
        pillar_outputs = {
            "insights_pillar": sample_insights_pillar_output
        }
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        assert "roadmap" in result
        roadmap = result["roadmap"]
        assert "insights" in roadmap["pillar_sources"]
    
    async def test_generate_roadmap_operations_only(
        self,
        roadmap_generation_service,
        sample_operations_pillar_output
    ):
        """Test roadmap generation with only operations pillar."""
        # Setup
        pillar_outputs = {
            "operations_pillar": sample_operations_pillar_output
        }
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        assert "roadmap" in result
        roadmap = result["roadmap"]
        assert "operations" in roadmap["pillar_sources"]
    
    async def test_generate_roadmap_no_pillars(self, roadmap_generation_service):
        """Test roadmap generation with no pillar outputs."""
        # Setup
        pillar_outputs = {}
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is False
        assert "No pillar outputs available" in result["error"]
    
    async def test_generate_roadmap_with_business_context(
        self,
        roadmap_generation_service,
        sample_content_pillar_output,
        sample_insights_pillar_output
    ):
        """Test roadmap generation with business context."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output,
            "insights_pillar": sample_insights_pillar_output
        }
        business_context = {
            "business_name": "Acme Corp",
            "budget": 200000,
            "timeline_days": 120
        }
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs,
            business_context=business_context
        )
        
        # Assert
        assert result["success"] is True
        roadmap = result["roadmap"]
        assert roadmap["name"] == "Acme Corp"
    
    async def test_create_comprehensive_strategic_plan(
        self,
        roadmap_generation_service,
        sample_content_pillar_output,
        sample_insights_pillar_output,
        sample_operations_pillar_output
    ):
        """Test comprehensive strategic plan creation."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output,
            "insights_pillar": sample_insights_pillar_output,
            "operations_pillar": sample_operations_pillar_output
        }
        business_context = {
            "pillar_outputs": pillar_outputs,
            "objectives": ["Objective 1", "Objective 2"],
            "business_name": "Test Business",
            "budget": 150000,
            "timeline_days": 90,
            "roadmap_type": "hybrid"
        }
        
        # Execute
        result = await roadmap_generation_service.create_comprehensive_strategic_plan(
            business_context=business_context
        )
        
        # Assert
        assert result["success"] is True
        assert "plan_id" in result
        assert "comprehensive_planning" in result
        
        plan = result["comprehensive_planning"]
        assert "roadmap" in plan
        assert "goals" in plan
        assert "performance_metrics" in plan
        assert "objectives" in plan
        assert len(plan["goals"]) > 0
        assert plan["performance_metrics"]["total_phases"] > 0
    
    async def test_create_comprehensive_strategic_plan_extracts_objectives(
        self,
        roadmap_generation_service,
        sample_content_pillar_output
    ):
        """Test that comprehensive plan extracts objectives from pillars if not provided."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        business_context = {
            "pillar_outputs": pillar_outputs,
            "business_name": "Test Business"
        }
        
        # Execute
        result = await roadmap_generation_service.create_comprehensive_strategic_plan(
            business_context=business_context
        )
        
        # Assert
        assert result["success"] is True
        plan = result["comprehensive_planning"]
        assert "objectives" in plan
        assert len(plan["objectives"]) > 0
    
    async def test_extract_objectives_from_pillars(
        self,
        roadmap_generation_service,
        sample_content_pillar_output,
        sample_insights_pillar_output,
        sample_operations_pillar_output
    ):
        """Test objective extraction from pillar outputs."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output,
            "insights_pillar": sample_insights_pillar_output,
            "operations_pillar": sample_operations_pillar_output
        }
        
        # Execute
        objectives = roadmap_generation_service._extract_objectives_from_pillars(pillar_outputs)
        
        # Assert
        assert len(objectives) > 0
        assert any("semantic" in obj.lower() or "data model" in obj.lower() for obj in objectives)
        assert any("analytics" in obj.lower() or "insights" in obj.lower() for obj in objectives)
        assert any("process" in obj.lower() or "workflow" in obj.lower() or "sop" in obj.lower() for obj in objectives)
    
    async def test_extract_objectives_from_pillars_no_pillars(self, roadmap_generation_service):
        """Test objective extraction with no pillar outputs."""
        # Setup
        pillar_outputs = {}
        
        # Execute
        objectives = roadmap_generation_service._extract_objectives_from_pillars(pillar_outputs)
        
        # Assert
        assert len(objectives) > 0
        assert "strategic value" in objectives[0].lower() or "platform" in objectives[0].lower()
    
    async def test_generate_roadmap_visualization_data(
        self,
        roadmap_generation_service,
        sample_content_pillar_output
    ):
        """Test that roadmap includes visualization data."""
        # Setup
        pillar_outputs = {
            "content_pillar": sample_content_pillar_output
        }
        
        # Execute
        result = await roadmap_generation_service.generate_roadmap(
            pillar_outputs=pillar_outputs
        )
        
        # Assert
        assert result["success"] is True
        assert "visualization" in result
        visualization = result["visualization"]
        assert "type" in visualization
        assert "data" in visualization
        assert "phases" in visualization["data"]
        assert "milestones" in visualization["data"]







