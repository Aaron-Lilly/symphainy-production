#!/usr/bin/env python3
"""
MVP User Journey End-to-End Tests

Tests the complete MVP user journey from landing page through all pillars
to final business outcome, based on MVP_Description_For_Business_and_Technical_Readiness.md
"""

import pytest
from typing import Dict, Any
from tests.utils.test_helpers import (
    MockDataGenerator,
    AssertionHelper,
    AsyncTestHelper
)

@pytest.mark.e2e
@pytest.mark.mvp
class TestMVPUserJourney:
    """End-to-end tests for the complete MVP user journey."""
    
    # ========================================================================
    # TEST SCENARIO 1: Landing Page → Content Pillar
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_landing_page_to_content_pillar(
        self,
        real_business_orchestrator,
        mock_mvp_journey_orchestrator
    ):
        """
        Test Scenario: User lands on page → GuideAgent prompts → User directed to Content Pillar
        
        MVP Flow:
        1. Landing page welcomes user
        2. GuideAgent prompts user about goals
        3. GuideAgent suggests data to share (volumetric data, operating procedures, etc.)
        4. User is directed to Content Pillar
        """
        # Mock GuideAgent interaction
        guide_agent_response = {
            "status": "success",
            "suggested_data_types": [
                "volumetric_data",
                "operating_procedures",
                "financial_reports",
                "testing_results"
            ],
            "next_pillar": "content"
        }
        
        # Verify journey orchestrator can start MVP journey
        journey_response = await mock_mvp_journey_orchestrator.start_mvp_journey(
            user_id="test_user",
            goals="Understand business operations and improve efficiency"
        )
        
        AssertionHelper.assert_success_response(journey_response)
        assert journey_response.get("current_pillar") == "content", "Should start at Content Pillar"
    
    # ========================================================================
    # TEST SCENARIO 2: Content Pillar → File Upload & Parsing
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_content_pillar_file_upload_and_parsing(
        self,
        real_business_orchestrator
    ):
        """
        Test Scenario: Content Pillar → File Upload → Parsing → Preview
        
        MVP Flow:
        1. Dashboard shows available files
        2. User uploads file (supports multiple types including mainframe binary/copybooks)
        3. File is parsed to AI-friendly format (parquet, JSON Structured, or JSON Chunks)
        4. User can preview parsed data
        5. ContentLiaisonAgent allows interaction with parsed file
        """
        # Create sample file data
        file_data = MockDataGenerator.create_sample_file_data(
            file_name="test_operations_manual.pdf",
            file_type="application/pdf"
        )
        
        # Test file upload (via Business Orchestrator → Content Operations)
        upload_result = await real_business_orchestrator.execute_use_case(
            use_case="data_operations",
            request={
                "action": "transform_data",
                "params": {
                    "resource_id": file_data["file_id"],
                    "options": {
                        "transformation_rules": {
                            "format": "json_structured",
                            "parse_documents": True
                        }
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(upload_result)
        assert "data" in upload_result, "Should contain parsed data"
        
        # Test ContentLiaisonAgent interaction (would be via agentic foundation)
        # For now, verify file is accessible
        assert upload_result["data"].get("transformation", {}).get("success"), \
            "File transformation should succeed"
    
    # ========================================================================
    # TEST SCENARIO 3: Content Pillar → Insights Pillar
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_content_to_insights_pillar(
        self,
        real_business_orchestrator,
        mock_mvp_journey_orchestrator
    ):
        """
        Test Scenario: Content Pillar → Insights Pillar with file selection
        
        MVP Flow:
        1. Insights pillar shows file selection prompt (parsed files)
        2. User selects file(s)
        3. Section 2 displays business analysis and visual/tabular representation
        4. InsightLiaison chatbot helps navigate data
        5. User can "double click" on analysis (e.g., "show customers 90+ days late")
        6. Insights summary with recommendations is generated
        """
        # Advance journey to Insights pillar
        journey_progress = await mock_mvp_journey_orchestrator.advance_to_next_pillar(
            journey_id="test_journey",
            current_pillar="content",
            next_pillar="insights"
        )
        
        assert journey_progress.get("current_pillar") == "insights", \
            "Should advance to Insights pillar"
        
        # Test insights generation with file selection
        insights_result = await real_business_orchestrator.execute_use_case(
            use_case="insights",
            request={
                "action": "generate_insights",
                "params": {
                    "resource_id": "test_file_parsed",
                    "options": {
                        "analysis_type": "descriptive",
                        "include_visualization": True,
                        "preferred_style": "visual"  # or "tabular"
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(insights_result)
        assert "data" in insights_result, "Should contain insights data"
        
        # Verify insights structure
        insights_data = insights_result["data"]
        assert "analysis" in insights_data, "Should have business analysis"
        assert "visualization" in insights_data or "tabular" in insights_data, \
            "Should have visual or tabular representation"
        
        # Test "double click" interaction (drill-down analysis)
        drill_down_result = await real_business_orchestrator.execute_use_case(
            use_case="insights",
            request={
                "action": "analyze_trends",
                "params": {
                    "resource_id": "test_file_parsed",
                    "options": {
                        "query": "show customers who are more than 90 days late",
                        "analysis_options": {"filter": {"days_late": ">90"}}
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(drill_down_result)
        
        # Test insights summary generation
        summary_result = await real_business_orchestrator.execute_use_case(
            use_case="insights",
            request={
                "action": "create_visualization",
                "params": {
                    "resource_id": "test_file_parsed",
                    "options": {
                        "type": "insights_summary",
                        "chart_type": "recommendations_chart"
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(summary_result)
        assert "visualization" in summary_result.get("data", {}), \
            "Should generate insights summary visualization"
    
    # ========================================================================
    # TEST SCENARIO 4: Insights Pillar → Operations Pillar
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_insights_to_operations_pillar(
        self,
        real_business_orchestrator,
        mock_mvp_journey_orchestrator
    ):
        """
        Test Scenario: Insights Pillar → Operations Pillar → Workflow/SOP/Coexistence
        
        MVP Flow:
        1. Operations pillar shows 3 cards: select existing file, upload new, generate from scratch
        2. User selects file(s) and clicks generate
        3. Section 2: File(s) translated to visual elements (workflow and SOP)
        4. If only one generated, prompt to use AI to create the other
        5. Section 3 "Coexistence": Generate coexistence blueprint with analysis/recommendations
        """
        # Advance journey to Operations pillar
        journey_progress = await mock_mvp_journey_orchestrator.advance_to_next_pillar(
            journey_id="test_journey",
            current_pillar="insights",
            next_pillar="operations"
        )
        
        assert journey_progress.get("current_pillar") == "operations", \
            "Should advance to Operations pillar"
        
        # Test workflow generation from file
        workflow_result = await real_business_orchestrator.execute_use_case(
            use_case="operations",
            request={
                "action": "build_sop",
                "params": {
                    "resource_id": "test_file_parsed",
                    "options": {
                        "workflow_definition": {
                            "steps": [
                                {"name": "receive_order", "type": "action"},
                                {"name": "process_payment", "type": "action"},
                                {"name": "fulfill_order", "type": "action"}
                            ]
                        },
                        "generate_visualization": True
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(workflow_result)
        assert "workflow" in workflow_result.get("data", {}), \
            "Should generate workflow"
        assert "visualization" in workflow_result.get("data", {}), \
            "Should generate SOP visualization"
        
        # Test SOP to workflow conversion (if only SOP generated, create workflow)
        sop_to_workflow_result = await real_business_orchestrator.execute_use_case(
            use_case="operations",
            request={
                "action": "convert_sop_to_workflow",
                "params": {
                    "resource_id": "test_sop_document",
                    "options": {}
                }
            }
        )
        
        AssertionHelper.assert_success_response(sop_to_workflow_result)
        
        # Test coexistence blueprint generation
        coexistence_result = await real_business_orchestrator.execute_use_case(
            use_case="operations",
            request={
                "action": "optimize_process",
                "params": {
                    "resource_id": "test_workflow_and_sop",
                    "options": {
                        "workflow_definition": {
                            "steps": [],
                            "analysis_type": "coexistence"
                        },
                        "generate_blueprint": True
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(coexistence_result)
        assert "optimization" in coexistence_result.get("data", {}), \
            "Should generate coexistence blueprint"
    
    # ========================================================================
    # TEST SCENARIO 5: Operations Pillar → Business Outcome Pillar
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_operations_to_business_outcomes_pillar(
        self,
        real_business_orchestrator,
        mock_mvp_journey_orchestrator
    ):
        """
        Test Scenario: Operations Pillar → Business Outcome Pillar → Roadmap & POC
        
        MVP Flow:
        1. Business Outcome pillar displays summaries from other pillars:
           - Content: What was uploaded
           - Insights: Insights Summary
           - Operations: Coexistence Blueprint
        2. Experience Liaison prompts for additional context/files
        3. Final analysis: Roadmap and POC proposal
        """
        # Advance journey to Business Outcomes pillar
        journey_progress = await mock_mvp_journey_orchestrator.advance_to_next_pillar(
            journey_id="test_journey",
            current_pillar="operations",
            next_pillar="business_outcomes"
        )
        
        assert journey_progress.get("current_pillar") == "business_outcomes", \
            "Should advance to Business Outcomes pillar"
        
        # Collect pillar summaries
        pillar_summaries = {
            "content": {
                "files_uploaded": ["test_operations_manual.pdf"],
                "files_parsed": ["test_operations_manual_parsed.json"]
            },
            "insights": {
                "summary": "Key insights about business operations",
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "visualization": "insights_chart_123"
            },
            "operations": {
                "coexistence_blueprint": "coexistence_blueprint_123",
                "workflow": "workflow_123",
                "sop": "sop_123"
            }
        }
        
        # Test roadmap generation
        roadmap_result = await real_business_orchestrator.execute_use_case(
            use_case="business_outcomes",
            request={
                "action": "generate_roadmap",
                "params": {
                    "resource_id": "journey_summary",
                    "options": {
                        "pillar_summaries": pillar_summaries,
                        "additional_context": {
                            "budget": 100000,
                            "timeline": "6 months",
                            "team_size": 5
                        }
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(roadmap_result)
        assert "roadmap" in roadmap_result.get("data", {}), \
            "Should generate roadmap"
        
        # Test KPI tracking
        kpi_result = await real_business_orchestrator.execute_use_case(
            use_case="business_outcomes",
            request={
                "action": "track_outcomes",
                "params": {
                    "resource_id": "journey_summary",
                    "options": {
                        "metric_name": "journey_completion_kpi",
                        "report_type": "outcome_summary"
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(kpi_result)
        
        # Test outcome analysis
        outcome_analysis = await real_business_orchestrator.execute_use_case(
            use_case="business_outcomes",
            request={
                "action": "analyze_outcomes",
                "params": {
                    "resource_id": "journey_summary",
                    "options": {
                        "analysis_options": {
                            "include_recommendations": True,
                            "generate_poc_proposal": True
                        }
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(outcome_analysis)
        assert "analysis" in outcome_analysis.get("data", {}), \
            "Should generate outcome analysis"
    
    # ========================================================================
    # TEST SCENARIO 6: Complete End-to-End Journey
    # ========================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_complete_mvp_journey_e2e(
        self,
        real_business_orchestrator,
        mock_mvp_journey_orchestrator,
        real_session_manager_service
    ):
        """
        Test Scenario: Complete MVP journey from landing to final outcome
        
        Tests the complete flow:
        1. Landing page → Content Pillar
        2. Content Pillar → File upload & parsing
        3. Content → Insights Pillar → Analysis & visualization
        4. Insights → Operations Pillar → Workflow/SOP/Coexistence
        5. Operations → Business Outcomes → Roadmap & POC
        """
        # Step 1: Start journey (Landing → Content)
        session = await real_session_manager_service.create_session(
            user_id="test_user_e2e",
            session_data={"journey_type": "mvp"}
        )
        
        journey_start = await mock_mvp_journey_orchestrator.start_mvp_journey(
            user_id="test_user_e2e",
            goals="Improve business operations efficiency"
        )
        
        AssertionHelper.assert_success_response(journey_start)
        journey_id = journey_start.get("journey_id")
        
        # Step 2: Content Pillar - File upload
        file_data = MockDataGenerator.create_sample_file_data(
            file_name="operations_data.pdf"
        )
        
        upload_result = await real_business_orchestrator.execute_use_case(
            use_case="data_operations",
            request={
                "action": "transform_data",
                "params": {
                    "resource_id": file_data["file_id"],
                    "options": {"transformation_rules": {"format": "json_structured"}}
                }
            }
        )
        
        AssertionHelper.assert_success_response(upload_result)
        parsed_file_id = upload_result.get("data", {}).get("transformation", {}).get("transformed_data_id")
        
        # Step 3: Insights Pillar - Generate insights
        insights_result = await real_business_orchestrator.execute_use_case(
            use_case="insights",
            request={
                "action": "generate_insights",
                "params": {
                    "resource_id": parsed_file_id,
                    "options": {
                        "analysis_type": "descriptive",
                        "include_visualization": True
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(insights_result)
        
        # Step 4: Operations Pillar - Generate workflow/SOP
        operations_result = await real_business_orchestrator.execute_use_case(
            use_case="operations",
            request={
                "action": "build_sop",
                "params": {
                    "resource_id": parsed_file_id,
                    "options": {
                        "workflow_definition": {"steps": []},
                        "generate_visualization": True
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(operations_result)
        
        # Step 5: Business Outcomes - Generate roadmap
        outcomes_result = await real_business_orchestrator.execute_use_case(
            use_case="business_outcomes",
            request={
                "action": "generate_roadmap",
                "params": {
                    "resource_id": journey_id,
                    "options": {
                        "pillar_summaries": {
                            "content": {"files": [parsed_file_id]},
                            "insights": insights_result.get("data", {}),
                            "operations": operations_result.get("data", {})
                        }
                    }
                }
            }
        )
        
        AssertionHelper.assert_success_response(outcomes_result)
        
        # Verify complete journey
        journey_status = await mock_mvp_journey_orchestrator.get_journey_progress(journey_id)
        assert journey_status.get("current_pillar") == "business_outcomes", \
            "Journey should complete at Business Outcomes pillar"
        assert journey_status.get("progress", 0) >= 90, \
            "Journey should be near completion (90%+)"
        
        # Verify all outputs are available
        assert "roadmap" in outcomes_result.get("data", {}), \
            "Final roadmap should be generated"
        assert "kpis" in outcomes_result.get("data", {}), \
            "KPIs should be tracked"

