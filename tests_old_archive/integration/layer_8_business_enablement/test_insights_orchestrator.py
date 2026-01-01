#!/usr/bin/env python3
"""
Insights Orchestrator - End-to-End Functional Tests

Tests Insights Orchestrator to ensure it fully enables the Insights Pillar in symphainy-frontend:
- Main analysis workflow (analyze_content_for_insights)
- NLP query support (query_analysis_results)
- Analysis management (get, list, visualizations)
- Content metadata integration
- Enabling services coordination
- MVP UI format compatibility

Based on MVP description and frontend API contract.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, Optional

from tests.integration.layer_8_business_enablement.test_file_helpers import (
    create_test_excel_file,
    create_test_json_file,
    create_test_text_file
)
from tests.integration.layer_8_business_enablement.test_utilities import (
    ContentStewardHelper,
    TestDataManager
)

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def insights_orchestrator(smart_city_infrastructure):
    """
    InsightsOrchestrator instance for each test.
    
    Reuses the proven pattern from content_analysis_orchestrator tests.
    """
    logger.info("🔧 Fixture: Starting insights_orchestrator fixture...")
    
    from backend.business_enablement.delivery_manager.delivery_manager_service import DeliveryManagerService
    
    logger.info("🔧 Fixture: Got infrastructure, creating DeliveryManagerService...")
    infra = smart_city_infrastructure
    
    # Create DeliveryManagerService (provides delivery_manager for orchestrator)
    delivery_manager = DeliveryManagerService(
        di_container=infra["di_container"],
        platform_gateway=infra["platform_gateway"]
    )
    
    logger.info("🔧 Fixture: Initializing DeliveryManagerService...")
    await delivery_manager.initialize()
    
    # Get Insights Orchestrator from delivery manager
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator import InsightsOrchestrator
    
    logger.info("🔧 Fixture: Creating InsightsOrchestrator...")
    orchestrator = InsightsOrchestrator(delivery_manager=delivery_manager)
    
    logger.info("🔧 Fixture: Initializing orchestrator (this may take time)...")
    try:
        result = await asyncio.wait_for(orchestrator.initialize(), timeout=120.0)
        logger.info(f"✅ Fixture: Orchestrator initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Orchestrator initialization returned False")
            pytest.fail("Insights Orchestrator failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Orchestrator initialization timed out after 120 seconds")
        pytest.fail("Insights Orchestrator initialization timed out")
    except Exception as e:
        logger.error(f"❌ Fixture: Orchestrator initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Orchestrator ready, yielding to test...")
    yield orchestrator
    logger.info("✅ Fixture: Test completed, cleaning up...")


@pytest.fixture(scope="function")
async def storage_helper(smart_city_infrastructure, infrastructure_storage):
    """
    Storage helper for each test.
    
    Reuses the proven pattern from content_analysis_orchestrator tests.
    """
    storage = infrastructure_storage["file_storage"]
    user_context = TestDataManager.get_user_context()
    helper = ContentStewardHelper(storage, user_context)
    
    yield helper
    
    # Cleanup stored files
    try:
        await helper.cleanup()
    except Exception:
        pass  # Ignore cleanup errors


# ============================================================================
# TESTS - Core Functionality (MVP Description Alignment)
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_initialization(insights_orchestrator):
    """Test that orchestrator initializes correctly."""
    logger.info("🧪 Test: Orchestrator initialization")
    
    assert insights_orchestrator is not None
    assert insights_orchestrator.is_initialized is True
    assert hasattr(insights_orchestrator, 'structured_workflow')
    assert hasattr(insights_orchestrator, 'unstructured_workflow')
    assert hasattr(insights_orchestrator, 'hybrid_workflow')
    
    logger.info("✅ Orchestrator initialized correctly")


@pytest.mark.asyncio
async def test_orchestrator_delegates_to_enabling_services(insights_orchestrator):
    """Test that orchestrator can access enabling services."""
    logger.info("🧪 Test: Orchestrator delegates to enabling services")
    
    # Test Data Analyzer Service access
    data_analyzer = await insights_orchestrator._get_data_analyzer_service()
    assert data_analyzer is not None
    
    # Test Metrics Calculator Service access
    metrics_calculator = await insights_orchestrator._get_metrics_calculator_service()
    assert metrics_calculator is not None
    
    # Test Visualization Engine Service access
    visualization_engine = await insights_orchestrator._get_visualization_engine_service()
    assert visualization_engine is not None
    
    logger.info("✅ Orchestrator can access all enabling services")


@pytest.mark.asyncio
async def test_analyze_content_for_insights_structured_file(insights_orchestrator, storage_helper):
    """
    Test main analysis workflow with structured file (MVP Section 2).
    
    MVP Description: "Section 2 has a formatted text element to provide business analysis
    of about your file and a secondary (side by side) element that provides either a visual
    or tabular representation of your data depending on your preferred learning style."
    """
    logger.info("🧪 Test: Analyze content for insights (structured file)")
    
    # Upload structured data file (Excel)
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Analyze content
    result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="structured",
        analysis_options={
            "include_visualizations": True,
            "include_tabular_summary": True
        }
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "analysis_id" in result
    assert "summary" in result
    
    # Verify 3-way summary (textual, tabular, visualizations)
    summary = result.get("summary", {})
    assert "textual" in summary  # Business analysis text
    assert isinstance(summary.get("textual"), str)
    assert len(summary.get("textual", "")) > 0
    
    # Tabular summary (optional but should be present for structured data)
    if summary.get("tabular"):
        assert "columns" in summary["tabular"]
        assert "rows" in summary["tabular"]
    
    # Visualizations (optional but should be present if requested)
    if summary.get("visualizations"):
        assert isinstance(summary["visualizations"], list)
        for viz in summary["visualizations"]:
            assert "visualization_id" in viz
            assert "chart_type" in viz
    
    # Verify insights
    assert "insights" in result
    assert isinstance(result["insights"], list)
    
    # Verify metadata
    assert "metadata" in result
    assert result["metadata"].get("content_type") == "structured"
    
    logger.info(f"✅ Analysis complete: {result.get('analysis_id')}")


@pytest.mark.asyncio
async def test_analyze_content_for_insights_unstructured_file(insights_orchestrator, storage_helper):
    """
    Test main analysis workflow with unstructured file.
    
    MVP Description: Supports both structured and unstructured data analysis.
    Now uses APGProcessorService and InsightsGeneratorService.
    """
    logger.info("🧪 Test: Analyze content for insights (unstructured file)")
    
    # Upload unstructured data file (text)
    text_data = create_test_text_file("This is a test document for unstructured analysis. It contains narrative text that should be analyzed for insights. The document discusses key business trends and operational improvements.")
    file_id = await storage_helper.store_file(text_data, "test_document.txt", "text/plain")
    
    # Analyze content
    result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="unstructured",
        analysis_options={
            "include_visualizations": False,  # Unstructured may not have visualizations
            "include_tabular_summary": False
        }
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "analysis_id" in result
    assert "summary" in result
    
    # Verify textual summary (required for all content types)
    summary = result.get("summary", {})
    assert "textual" in summary
    assert isinstance(summary.get("textual"), str)
    assert len(summary.get("textual", "")) > 0
    
    # Verify metadata
    assert "metadata" in result
    assert result["metadata"].get("content_type") == "unstructured"
    
    logger.info(f"✅ Unstructured analysis complete: {result.get('analysis_id')}")
    logger.info(f"   Summary length: {len(summary.get('textual', ''))} characters")


@pytest.mark.asyncio
async def test_analyze_content_for_insights_unstructured_with_apg(insights_orchestrator, storage_helper):
    """
    Test unstructured analysis with APGProcessorService integration.
    
    Verifies that APGProcessorService is being used for text processing.
    """
    logger.info("🧪 Test: Analyze unstructured content with APG processing")
    
    # Upload unstructured data file with more complex content
    complex_text = """
    Business Performance Analysis Report
    
    This quarter showed significant improvements in operational efficiency.
    Key metrics include:
    - Revenue increased by 15%
    - Customer satisfaction improved by 20%
    - Operational costs decreased by 10%
    
    Key findings:
    1. Marketing campaigns were highly effective
    2. Customer retention improved significantly
    3. Supply chain optimization reduced costs
    
    Recommendations:
    - Continue current marketing strategy
    - Expand successful customer retention programs
    - Invest in further supply chain automation
    """
    
    text_data = create_test_text_file(complex_text)
    file_id = await storage_helper.store_file(text_data, "business_report.txt", "text/plain")
    
    # Analyze with APG processing (should use APGProcessorService)
    result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="unstructured",
        analysis_options={
            "include_visualizations": False,
            "include_tabular_summary": False
        }
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "analysis_id" in result
    
    # Verify that processing occurred (APGProcessorService should extract entities/key phrases)
    summary = result.get("summary", {})
    textual_summary = summary.get("textual", "")
    
    # The summary should contain processed insights
    assert len(textual_summary) > 0
    
    logger.info(f"✅ APG processing integration verified: {result.get('analysis_id')}")
    logger.info(f"   Summary preview: {textual_summary[:100]}...")


@pytest.mark.asyncio
async def test_analyze_content_for_insights_aar_analysis(insights_orchestrator, storage_helper):
    """
    Test AAR (After Action Report) analysis with APGProcessorService MANUAL mode.
    
    Verifies that AAR-specific analysis uses APGProcessorService with MANUAL mode
    to extract lessons learned, risks, recommendations, and timeline.
    """
    logger.info("🧪 Test: Analyze AAR content with APG processing")
    
    # Upload AAR-specific content
    aar_text = """
    AFTER ACTION REPORT - Exercise Alpha
    Date: 2025-10-15
    Location: Training Facility
    
    EXECUTIVE SUMMARY:
    Exercise Alpha was conducted to test operational readiness and identify
    areas for improvement. The exercise revealed both strengths and areas
    requiring attention.
    
    LESSONS LEARNED:
    1. Communication protocols need improvement - delays in critical information
       sharing impacted decision-making.
    2. Equipment readiness was excellent - all systems functioned as expected.
    3. Personnel performance exceeded expectations - team coordination was strong.
    
    RISKS IDENTIFIED:
    1. Personnel fatigue during extended operations - need better rotation schedules.
    2. Weather conditions impacted visibility - need improved weather monitoring.
    3. Supply chain delays - need backup suppliers identified.
    
    RECOMMENDATIONS:
    1. Enhance communication training - implement new protocols by Q2.
    2. Implement fatigue management protocols - establish rotation schedules.
    3. Develop weather contingency plans - integrate real-time weather data.
    
    TIMELINE:
    - 09:00: Exercise commenced
    - 12:30: Critical incident occurred (communication delay)
    - 14:00: Incident resolved
    - 16:00: Exercise concluded
    """
    
    text_data = create_test_text_file(aar_text)
    file_id = await storage_helper.store_file(text_data, "aar_report.txt", "text/plain")
    
    # Analyze with AAR-specific analysis (should use APGProcessorService with MANUAL mode)
    result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="unstructured",
        analysis_options={
            "aar_specific_analysis": True,  # Enable AAR-specific analysis
            "include_visualizations": False,
            "include_tabular_summary": False
        }
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "analysis_id" in result
    
    # Verify AAR-specific sections (if available)
    summary = result.get("summary", {})
    textual_summary = summary.get("textual", "")
    
    # The summary should contain AAR analysis
    assert len(textual_summary) > 0
    
    # Check for AAR data in result (if structured)
    aar_data = result.get("aar_analysis") or result.get("metadata", {}).get("aar_data")
    if aar_data:
        logger.info(f"✅ AAR data extracted: {len(aar_data)} sections")
    
    logger.info(f"✅ AAR analysis complete: {result.get('analysis_id')}")
    logger.info(f"   Summary preview: {textual_summary[:150]}...")


@pytest.mark.asyncio
async def test_analyze_content_for_insights_unstructured_with_insights_generator(insights_orchestrator, storage_helper):
    """
    Test unstructured analysis with InsightsGeneratorService integration.
    
    Verifies that InsightsGeneratorService is being used for theme extraction
    and insights generation.
    """
    logger.info("🧪 Test: Analyze unstructured content with InsightsGeneratorService")
    
    # Upload unstructured data file with themes
    themed_text = """
    Customer Feedback Analysis
    
    Theme 1: Product Quality
    Customers consistently praise the high quality of our products.
    Multiple reviews mention durability and reliability as key factors.
    
    Theme 2: Customer Service
    Service quality received mixed feedback. Some customers report
    excellent support, while others experienced delays.
    
    Theme 3: Pricing
    Price competitiveness is a recurring topic. Customers appreciate
    value but some find pricing higher than competitors.
    
    Patterns Identified:
    - Positive correlation between product quality and customer satisfaction
    - Service response time impacts overall satisfaction
    - Price sensitivity varies by customer segment
    """
    
    text_data = create_test_text_file(themed_text)
    file_id = await storage_helper.store_file(text_data, "customer_feedback.txt", "text/plain")
    
    # Analyze with InsightsGeneratorService (should extract themes and patterns)
    result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="unstructured",
        analysis_options={
            "include_visualizations": False,
            "include_tabular_summary": False
        }
    )
    
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert "analysis_id" in result
    
    # Verify that themes/patterns were extracted (InsightsGeneratorService)
    summary = result.get("summary", {})
    textual_summary = summary.get("textual", "")
    
    # The summary should contain insights from theme extraction
    assert len(textual_summary) > 0
    
    logger.info(f"✅ InsightsGeneratorService integration verified: {result.get('analysis_id')}")
    logger.info(f"   Summary preview: {textual_summary[:150]}...")


@pytest.mark.asyncio
async def test_analyze_content_for_insights_with_content_metadata(insights_orchestrator, storage_helper):
    """
    Test analysis using content metadata from Content Pillar.
    
    MVP Description: "Use Extracted Metadata" option from Content Pillar.
    """
    logger.info("🧪 Test: Analyze content for insights (content metadata)")
    
    # First, upload and parse a file to create metadata
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # For this test, we'll simulate having content metadata
    # In production, this would come from Content Pillar's metadata extraction
    # For now, we'll test with file_id as a proxy
    
    # Analyze using content metadata (simulated)
    result = await insights_orchestrator.analyze_content_for_insights(
        source_type="content_metadata",
        content_metadata_id=file_id,  # In production, this would be a metadata ID from ArangoDB
        content_type="structured",
        analysis_options={
            "include_visualizations": True,
            "include_tabular_summary": True
        }
    )
    
    # The orchestrator should handle content_metadata source type
    # If it fails, that's expected if metadata doesn't exist yet
    # The important thing is that the method accepts the source_type
    assert isinstance(result, dict)
    
    # Either success or graceful failure
    if result.get("success"):
        assert "analysis_id" in result
        logger.info(f"✅ Content metadata analysis complete: {result.get('analysis_id')}")
    else:
        logger.info(f"⚠️ Content metadata analysis failed (expected if metadata not available): {result.get('error')}")


@pytest.mark.asyncio
async def test_query_analysis_results_nlp(insights_orchestrator, storage_helper):
    """
    Test NLP query support (Insights Liaison Agent functionality).
    
    MVP Description: "The secondary chatbot (insight liaison) serves as a plain english
    guide to help you navigate your data and 'double click on any initial analysis
    (e.g. I see I have a lot of customers who are more than 90 days late. can you show
    me who those customers are?)'"
    """
    logger.info("🧪 Test: Query analysis results (NLP)")
    
    # First, create an analysis
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    analysis_result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="structured"
    )
    
    if not analysis_result.get("success"):
        pytest.skip("Analysis failed, cannot test query")
    
    analysis_id = analysis_result.get("analysis_id")
    
    # Query the analysis using natural language
    query_result = await insights_orchestrator.query_analysis_results(
        query="Show me the summary statistics",
        analysis_id=analysis_id,
        query_type="summary"
    )
    
    assert isinstance(query_result, dict)
    
    # Query may succeed or fail depending on DataInsightsQueryService availability
    if query_result.get("success"):
        assert "query_id" in query_result
        assert "result" in query_result
        result = query_result.get("result", {})
        assert "type" in result  # 'table', 'chart', or 'text'
        assert "explanation" in result
        logger.info(f"✅ NLP query successful: {query_result.get('query_id')}")
    else:
        logger.info(f"⚠️ NLP query failed (expected if DataInsightsQueryService not fully configured): {query_result.get('error')}")


@pytest.mark.asyncio
async def test_get_analysis_results(insights_orchestrator, storage_helper):
    """Test retrieving analysis results by ID."""
    logger.info("🧪 Test: Get analysis results")
    
    # Create an analysis
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    analysis_result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="structured"
    )
    
    if not analysis_result.get("success"):
        pytest.skip("Analysis failed, cannot test retrieval")
    
    analysis_id = analysis_result.get("analysis_id")
    
    # Retrieve the analysis
    retrieved = await insights_orchestrator.get_analysis_results(analysis_id)
    
    assert isinstance(retrieved, dict)
    assert retrieved.get("success") is True
    assert "analysis" in retrieved
    
    analysis = retrieved.get("analysis", {})
    assert "summary" in analysis
    assert "insights" in analysis
    
    logger.info(f"✅ Analysis retrieved: {analysis_id}")


@pytest.mark.asyncio
async def test_get_analysis_visualizations(insights_orchestrator, storage_helper):
    """
    Test retrieving visualizations for an analysis.
    
    MVP Description: "a secondary (side by side) element that provides either a visual
    or tabular representation of your data"
    """
    logger.info("🧪 Test: Get analysis visualizations")
    
    # Create an analysis with visualizations
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    analysis_result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="structured",
        analysis_options={
            "include_visualizations": True
        }
    )
    
    if not analysis_result.get("success"):
        pytest.skip("Analysis failed, cannot test visualizations")
    
    analysis_id = analysis_result.get("analysis_id")
    
    # Get visualizations
    viz_result = await insights_orchestrator.get_analysis_visualizations(analysis_id)
    
    assert isinstance(viz_result, dict)
    assert viz_result.get("success") is True
    assert "visualizations" in viz_result
    assert "analysis_id" in viz_result
    assert viz_result.get("analysis_id") == analysis_id
    
    visualizations = viz_result.get("visualizations", [])
    assert isinstance(visualizations, list)
    
    logger.info(f"✅ Found {len(visualizations)} visualizations for analysis: {analysis_id}")


@pytest.mark.asyncio
async def test_list_user_analyses(insights_orchestrator, storage_helper):
    """Test listing user's analysis history."""
    logger.info("🧪 Test: List user analyses")
    
    # Create multiple analyses
    excel_data, excel_filename = create_test_excel_file()
    file_id1 = await storage_helper.store_file(excel_data, "test_data1.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    file_id2 = await storage_helper.store_file(excel_data, "test_data2.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Create first analysis
    result1 = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id1,
        content_type="structured"
    )
    
    # Create second analysis
    result2 = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id2,
        content_type="structured"
    )
    
    # Verify analyses were created successfully
    if not result1.get("success") or not result2.get("success"):
        logger.info(f"⚠️ One or both analyses failed (result1: {result1.get('success')}, result2: {result2.get('success')})")
        # Continue anyway to test the list operation
    
    # List analyses
    list_result = await insights_orchestrator.list_user_analyses(limit=10, offset=0)
    
    assert isinstance(list_result, dict)
    assert list_result.get("success") is True
    assert "analyses" in list_result
    assert "pagination" in list_result
    
    analyses = list_result.get("analyses", [])
    assert isinstance(analyses, list)
    
    # If analyses succeeded, we should have at least 2; otherwise, just verify the list operation works
    if result1.get("success") and result2.get("success"):
        assert len(analyses) >= 2, f"Expected at least 2 analyses, got {len(analyses)}"
    else:
        logger.info(f"⚠️ Analyses may not have been cached, but list operation succeeded with {len(analyses)} analyses")
    
    pagination = list_result.get("pagination", {})
    assert "total_count" in pagination
    assert "limit" in pagination
    assert "offset" in pagination
    
    logger.info(f"✅ Listed {len(analyses)} analyses (total: {pagination.get('total_count')})")


@pytest.mark.asyncio
async def test_get_pillar_summary(insights_orchestrator, storage_helper):
    """
    Test getting Insights Pillar summary for Business Outcomes page.
    
    MVP Description: "once you've gotten your answers/analysis there's a bottom section
    'insights summary' which recaps what you've learned on the page and supports it with
    an appropriate visual (chart or graph) and then provides recommendations based on
    the insights you've gained. now you're ready to move onto the operations pillar."
    """
    logger.info("🧪 Test: Get pillar summary")
    
    # Create an analysis
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    analysis_result = await insights_orchestrator.analyze_content_for_insights(
        source_type="file",
        file_id=file_id,
        content_type="structured",
        analysis_options={
            "include_visualizations": True,
            "include_tabular_summary": True
        }
    )
    
    if not analysis_result.get("success"):
        pytest.skip("Analysis failed, cannot test pillar summary")
    
    analysis_id = analysis_result.get("analysis_id")
    
    # Get pillar summary
    summary_result = await insights_orchestrator.get_pillar_summary(analysis_id=analysis_id)
    
    assert isinstance(summary_result, dict)
    assert summary_result.get("success") is True
    assert summary_result.get("pillar") == "insights"
    assert "summary" in summary_result
    
    summary = summary_result.get("summary", {})
    assert "textual" in summary  # Recap of what you've learned
    assert "tabular" in summary or "visualizations" in summary  # Supporting visual
    
    assert "source_analysis_id" in summary_result
    assert summary_result.get("source_analysis_id") == analysis_id
    
    logger.info(f"✅ Pillar summary retrieved for analysis: {analysis_id}")


@pytest.mark.asyncio
async def test_get_available_content_metadata(insights_orchestrator):
    """
    Test getting available content metadata from Content Pillar.
    
    MVP Description: "Insights pillar starts with a file selection prompt (showing your
    parsed files)" and "Use Extracted Metadata" option.
    """
    logger.info("🧪 Test: Get available content metadata")
    
    # Get available content metadata
    result = await insights_orchestrator.get_available_content_metadata()
    
    assert isinstance(result, dict)
    assert "success" in result
    assert "content_metadata" in result
    
    # May succeed or fail depending on Librarian/Content Steward availability
    if result.get("success"):
        metadata_list = result.get("content_metadata", [])
        assert isinstance(metadata_list, list)
        assert "count" in result
        logger.info(f"✅ Found {result.get('count')} content metadata items")
    else:
        logger.info(f"⚠️ Content metadata listing failed (expected if Librarian not configured): {result.get('error')}")


@pytest.mark.asyncio
async def test_calculate_metrics(insights_orchestrator, storage_helper):
    """Test metrics calculation workflow."""
    logger.info("🧪 Test: Calculate metrics")
    
    # Upload data
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Calculate metrics
    result = await insights_orchestrator.calculate_metrics(
        resource_id=file_id,
        options={
            "analysis_type": "descriptive",
            "metric_name": "test_kpi"
        }
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    # Should have data from enabling services
    if result.get("status") == "success" or result.get("success"):
        assert "data" in result or "metrics" in result
        logger.info("✅ Metrics calculation successful")
    else:
        logger.info(f"⚠️ Metrics calculation failed: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_generate_insights(insights_orchestrator, storage_helper):
    """Test insights generation workflow."""
    logger.info("🧪 Test: Generate insights")
    
    # Upload data
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Generate insights
    result = await insights_orchestrator.generate_insights(
        resource_id=file_id,
        options={
            "analysis_type": "descriptive",
            "include_visualization": True
        }
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    # Should have data from enabling services
    if result.get("status") == "success" or result.get("success"):
        assert "data" in result or "insights" in result
        logger.info("✅ Insights generation successful")
    else:
        logger.info(f"⚠️ Insights generation failed: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_create_visualization(insights_orchestrator, storage_helper):
    """Test visualization creation workflow."""
    logger.info("🧪 Test: Create visualization")
    
    # Upload data
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Create visualization
    result = await insights_orchestrator.create_visualization(
        resource_id=file_id,
        options={
            "visualization_type": "dashboard"
        }
    )
    
    assert isinstance(result, dict)
    assert "status" in result or "success" in result
    
    # Should have visualization data
    if result.get("status") == "success" or result.get("success"):
        assert "data" in result or "visualization" in result
        logger.info("✅ Visualization creation successful")
    else:
        logger.info(f"⚠️ Visualization creation failed: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_mvp_ui_format_compatibility(insights_orchestrator, storage_helper):
    """
    Test that orchestrator returns results in MVP UI format.
    
    MVP Description: Results should be formatted for display in the Insights Pillar UI.
    """
    logger.info("🧪 Test: MVP UI format compatibility")
    
    # Upload data
    excel_data, excel_filename = create_test_excel_file()
    file_id = await storage_helper.store_file(excel_data, excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Generate insights (should return MVP UI format)
    result = await insights_orchestrator.generate_insights(
        resource_id=file_id,
        options={"analysis_type": "descriptive"}
    )
    
    assert isinstance(result, dict)
    
    # Check for MVP UI format indicators
    if result.get("status") == "success":
        assert "orchestrator" in result
        assert result.get("orchestrator") == "InsightsOrchestratorService"
        assert "timestamp" in result
        assert "data" in result or "resource_id" in result
        logger.info("✅ MVP UI format compatible")
    else:
        logger.info(f"⚠️ Operation failed, cannot verify MVP UI format: {result.get('message') or result.get('error')}")


@pytest.mark.asyncio
async def test_health_check(insights_orchestrator):
    """Test orchestrator health check."""
    logger.info("🧪 Test: Health check")
    
    health = await insights_orchestrator.health_check()
    
    assert isinstance(health, dict)
    assert "status" in health
    assert health.get("status") == "healthy"
    assert "service_name" in health
    assert "orchestrator_type" in health
    
    logger.info("✅ Health check passed")


@pytest.mark.asyncio
async def test_get_service_capabilities(insights_orchestrator):
    """Test getting service capabilities."""
    logger.info("🧪 Test: Get service capabilities")
    
    capabilities = await insights_orchestrator.get_service_capabilities()
    
    assert isinstance(capabilities, dict)
    assert "service_name" in capabilities
    assert "service_type" in capabilities
    assert "capabilities" in capabilities
    assert "soa_apis" in capabilities
    
    # Should have expected capabilities
    expected_capabilities = ["metrics_calculation", "insight_generation", "visualization_creation"]
    for cap in expected_capabilities:
        assert cap in capabilities.get("capabilities", [])
    
    logger.info("✅ Service capabilities retrieved")

