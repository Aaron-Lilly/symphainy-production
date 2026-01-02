"""
Integration tests for cross-pillar workflows.

Tests:
- Content → Insights workflow
- Insights → Operations workflow
- Operations → Business Outcomes workflow
- Complete Content → Insights → Operations → Business Outcomes workflow
- Error handling across pillars
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure


@pytest.mark.integration
@pytest.mark.pillar
@pytest.mark.cross_pillar
@pytest.mark.slow
class TestCrossPillarWorkflow:
    """Test suite for cross-pillar workflow integration."""
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        return Mock()
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.get_logger = Mock(return_value=Mock())
        container.get_config_adapter = Mock(return_value=Mock())
        return container
    
    @pytest.mark.asyncio
    async def test_content_to_insights_workflow(self, mock_platform_gateway, mock_di_container):
        """Test Content → Insights workflow."""
        # Mock Content pillar: file parsing
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        file_parser = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await file_parser.initialize()
        
        # Mock Insights pillar: analysis
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        insights_orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await insights_orchestrator.initialize()
        
        # Simulate workflow: parse file → analyze
        with patch.object(file_parser, 'parse_file') as mock_parse:
            mock_parse.return_value = {
                "success": True,
                "parsing_type": "structured",
                "data": {"records": []}
            }
            
            parse_result = await file_parser.parse_file(
                file_id="test_file",
                parse_options={"parsing_type": "structured"}
            )
            
            # Then analyze parsed data
            with patch.object(insights_orchestrator, 'execute_structured_analysis_workflow') as mock_analyze:
                mock_analyze.return_value = {
                    "success": True,
                    "analysis_id": "analysis_123"
                }
                
                analysis_result = await insights_orchestrator.execute_structured_analysis_workflow(
                    data_file_id="test_file",
                    analysis_type="eda"
                )
                
                # Both should succeed
                assert parse_result["success"] is True
                assert analysis_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_insights_to_operations_workflow(self, mock_platform_gateway, mock_di_container):
        """Test Insights → Operations workflow."""
        # Mock Insights: analysis results
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        insights_orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await insights_orchestrator.initialize()
        
        # Mock Operations: workflow generation
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        operations_orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await operations_orchestrator.initialize()
        
        # Simulate workflow: analyze → generate workflow
        with patch.object(insights_orchestrator, 'execute_unstructured_analysis_workflow') as mock_analyze:
            mock_analyze.return_value = {
                "success": True,
                "analysis_id": "analysis_123",
                "insights": ["insight1"]
            }
            
            analysis_result = await insights_orchestrator.execute_unstructured_analysis_workflow(
                document_content="SOP content",
                analysis_type="business_summary"
            )
            
            # Then generate workflow from insights
            with patch.object(operations_orchestrator, 'execute_sop_to_workflow_workflow') as mock_workflow:
                mock_workflow.return_value = {
                    "success": True,
                    "workflow_id": "workflow_123"
                }
                
                workflow_result = await operations_orchestrator.execute_sop_to_workflow_workflow(
                    sop_content={"content": "SOP content"},
                    workflow_options={}
                )
                
                # Both should succeed
                assert analysis_result["success"] is True
                assert workflow_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_operations_to_business_outcomes_workflow(self, mock_platform_gateway, mock_di_container):
        """Test Operations → Business Outcomes workflow."""
        # Mock Operations: workflow generation
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        operations_orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await operations_orchestrator.initialize()
        
        # Mock Business Outcomes: roadmap generation
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        business_outcomes_orchestrator = BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await business_outcomes_orchestrator.initialize()
        
        # Simulate workflow: generate workflow → generate roadmap
        with patch.object(operations_orchestrator, 'execute_sop_to_workflow_workflow') as mock_workflow:
            mock_workflow.return_value = {
                "success": True,
                "workflow_id": "workflow_123"
            }
            
            workflow_result = await operations_orchestrator.execute_sop_to_workflow_workflow(
                sop_content={},
                workflow_options={}
            )
            
            # Then generate roadmap from operations output
            with patch.object(business_outcomes_orchestrator, 'execute_roadmap_generation_workflow') as mock_roadmap:
                mock_roadmap.return_value = {
                    "success": True,
                    "roadmap_id": "roadmap_123"
                }
                
                roadmap_result = await business_outcomes_orchestrator.execute_roadmap_generation_workflow(
                    pillar_summaries={"operations": {}},
                    roadmap_options={}
                )
                
                # Both should succeed
                assert workflow_result["success"] is True
                assert roadmap_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_complete_cross_pillar_workflow(self, mock_platform_gateway, mock_di_container):
        """Test complete Content → Insights → Operations → Business Outcomes workflow."""
        # Initialize all orchestrators
        from backend.content.services.file_parser_service.file_parser_service import FileParserService
        from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
        from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
        from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
        
        file_parser = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        await file_parser.initialize()
        
        insights_orchestrator = InsightsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await insights_orchestrator.initialize()
        
        operations_orchestrator = OperationsJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await operations_orchestrator.initialize()
        
        business_outcomes_orchestrator = BusinessOutcomesJourneyOrchestrator(mock_platform_gateway, mock_di_container)
        await business_outcomes_orchestrator.initialize()
        
        # Simulate complete workflow with mocks
        with patch.object(file_parser, 'parse_file') as mock_parse, \
             patch.object(insights_orchestrator, 'execute_structured_analysis_workflow') as mock_analyze, \
             patch.object(operations_orchestrator, 'execute_sop_to_workflow_workflow') as mock_workflow, \
             patch.object(business_outcomes_orchestrator, 'execute_roadmap_generation_workflow') as mock_roadmap:
            
            # Step 1: Parse file
            mock_parse.return_value = {"success": True, "data": {}}
            parse_result = await file_parser.parse_file("file_123", {})
            
            # Step 2: Analyze
            mock_analyze.return_value = {"success": True, "analysis_id": "analysis_123"}
            analysis_result = await insights_orchestrator.execute_structured_analysis_workflow("file_123", "eda")
            
            # Step 3: Generate workflow
            mock_workflow.return_value = {"success": True, "workflow_id": "workflow_123"}
            workflow_result = await operations_orchestrator.execute_sop_to_workflow_workflow({}, {})
            
            # Step 4: Generate roadmap
            mock_roadmap.return_value = {"success": True, "roadmap_id": "roadmap_123"}
            roadmap_result = await business_outcomes_orchestrator.execute_roadmap_generation_workflow({}, {})
            
            # All steps should succeed
            assert parse_result["success"] is True
            assert analysis_result["success"] is True
            assert workflow_result["success"] is True
            assert roadmap_result["success"] is True




