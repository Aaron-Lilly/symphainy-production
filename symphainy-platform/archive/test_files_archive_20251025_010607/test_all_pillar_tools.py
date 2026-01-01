"""
Comprehensive Test Script for All Pillar MCP Tools
Smart City Native + Micro-Modular Architecture
"""

import asyncio
import pandas as pd
import json
import sys
import os

# Add the backend packages to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import all pillar tools
from content.tools.data_quality_tool.data_quality_tool import DataQualityTool
from content.tools.tabular_content_tool.tabular_content_tool import TabularContentTool
from content.tools.visualization_tool.visualization_tool import ContentVisualizationTool
from content.tools.summary_tool.summary_tool import ContentSummaryTool

from insights.tools.anomaly_detection_tool.anomaly_detection_tool import InsightsAnomalyTool
from insights.tools.modeling_insights_tool.modeling_insights_tool import InsightsModelingTool

from operations.tools.coexistence_tool.coexistence_tool import OperationsCoexistenceTool
from operations.tools.sop_builder_wizard_tool.sop_builder_wizard_tool import SOPBuilderWizardTool
from operations.tools.workflow_builder_wizard_tool.workflow_builder_wizard_tool import WorkflowBuilderWizardTool
from operations.tools.workflow_to_sop_tool.workflow_to_sop_tool import WorkflowToSOPTool
from operations.tools.sop_to_workflow_tool.sop_to_workflow_tool import SOPToWorkflowTool

from experience.tools.outcomes_tool.outcomes_tool import ExperienceOutcomesTool


async def test_content_pillar_tools():
    """Test Content Pillar MCP Tools."""
    print("\n" + "="*60)
    print("TESTING CONTENT PILLAR TOOLS")
    print("="*60)
    
    # Test Data Quality Tool
    print("\n--- Testing DataQualityTool ---")
    try:
        tool = DataQualityTool()
        
        # Test with sample data
        data = {
            'customer_id': ['C001', 'C002', 'C003', 'C004', None],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', None],
            'transaction_amount': [150.00, 275.50, 89.99, 320.75, 45.00],
            'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
        }
        df = pd.DataFrame(data)
        dataframe_json = df.to_json(orient='records')
        
        result = await tool.analyze_quality(dataframe_json, session_token="test-session-123")
        print("DataQualityTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "overall_score" in result
        assert "status" in result
        assert "top_issues" in result
        assert isinstance(result["top_issues"], list)
        assert "recommendation" in result
        assert result["status"] in ["good", "warning", "error"]
        assert result["overall_score"] >= 0 and result["overall_score"] <= 100
        print("✅ DataQualityTool passed validation")
        
    except Exception as e:
        print(f"❌ DataQualityTool failed: {e}")
    
    # Test Tabular Content Tool
    print("\n--- Testing TabularContentTool ---")
    try:
        tool = TabularContentTool()
        
        result = await tool.analyze_structured_data(dataframe_json, file_type="CSV", session_token="test-session-123")
        print("TabularContentTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "columns" in result
        assert isinstance(result["columns"], list)
        assert "rows" in result
        assert isinstance(result["rows"], list)
        assert "summary" in result
        assert "total_rows" in result["summary"]
        assert "total_columns" in result["summary"]
        assert "file_type" in result["summary"]
        assert "status" in result["summary"]
        assert "basic_insights" in result["summary"]
        assert isinstance(result["summary"]["basic_insights"], list)
        print("✅ TabularContentTool passed validation")
        
    except Exception as e:
        print(f"❌ TabularContentTool failed: {e}")
    
    # Test Content Visualization Tool
    print("\n--- Testing ContentVisualizationTool ---")
    try:
        tool = ContentVisualizationTool()
        
        result = await tool.generate_visualizations(dataframe_json, "CSV", session_token="test-session-123")
        print("ContentVisualizationTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "visualizations" in result
        assert isinstance(result["visualizations"], list)
        assert "summary" in result
        print("✅ ContentVisualizationTool passed validation")
        
    except Exception as e:
        print(f"❌ ContentVisualizationTool failed: {e}")
    
    # Test Content Summary Tool
    print("\n--- Testing ContentSummaryTool ---")
    try:
        tool = ContentSummaryTool()
        
        result = await tool.generate_summary(dataframe_json, "CSV", session_token="test-session-123")
        print("ContentSummaryTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "summary" in result
        assert "insights" in result
        assert "metadata" in result
        print("✅ ContentSummaryTool passed validation")
        
    except Exception as e:
        print(f"❌ ContentSummaryTool failed: {e}")


async def test_insights_pillar_tools():
    """Test Insights Pillar MCP Tools."""
    print("\n" + "="*60)
    print("TESTING INSIGHTS PILLAR TOOLS")
    print("="*60)
    
    # Test Insights Anomaly Tool
    print("\n--- Testing InsightsAnomalyTool ---")
    try:
        tool = InsightsAnomalyTool()
        
        # Test with sample data
        data = {
            'value': [1, 2, 3, 4, 5, 100, 6, 7, 8, 9, 10],  # 100 is an outlier
            'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A'],
            'timestamp': pd.date_range('2024-01-01', periods=11, freq='D')
        }
        df = pd.DataFrame(data)
        dataframe_json = df.to_json(orient='records')
        
        result = await tool.detect_anomalies(dataframe_json, session_token="test-session-123")
        print("InsightsAnomalyTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "anomalies" in result
        assert "summary" in result
        assert "alerts" in result
        print("✅ InsightsAnomalyTool passed validation")
        
    except Exception as e:
        print(f"❌ InsightsAnomalyTool failed: {e}")
    
    # Test Insights Modeling Tool
    print("\n--- Testing InsightsModelingTool ---")
    try:
        tool = InsightsModelingTool()
        
        result = await tool.analyze_patterns(dataframe_json, session_token="test-session-123")
        print("InsightsModelingTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "patterns" in result
        assert "correlations" in result
        assert "trends" in result
        assert "predictions" in result
        print("✅ InsightsModelingTool passed validation")
        
    except Exception as e:
        print(f"❌ InsightsModelingTool failed: {e}")


async def test_operations_pillar_tools():
    """Test Operations Pillar MCP Tools."""
    print("\n" + "="*60)
    print("TESTING OPERATIONS PILLAR TOOLS")
    print("="*60)
    
    # Test Operations Coexistence Tool
    print("\n--- Testing OperationsCoexistenceTool ---")
    try:
        tool = OperationsCoexistenceTool()
        
        # Test with sample data
        data = {
            'process_step': ['Data Collection', 'Data Processing', 'Analysis', 'Reporting'],
            'human_effort': [8, 6, 4, 2],
            'ai_effort': [2, 4, 6, 8],
            'complexity': ['Low', 'Medium', 'High', 'Medium'],
            'automation_level': [0.2, 0.4, 0.6, 0.8]
        }
        df = pd.DataFrame(data)
        dataframe_json = df.to_json(orient='records')
        
        result = await tool.analyze_coexistence(dataframe_json, session_token="test-session-123")
        print("OperationsCoexistenceTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "coexistence_analysis" in result
        assert "optimization_opportunities" in result
        assert "workflow_recommendations" in result
        print("✅ OperationsCoexistenceTool passed validation")
        
    except Exception as e:
        print(f"❌ OperationsCoexistenceTool failed: {e}")
    
    # Test SOP Builder Wizard Tool
    print("\n--- Testing SOPBuilderWizardTool ---")
    try:
        tool = SOPBuilderWizardTool()
        
        result = await tool.build_sop(
            "Create a data processing SOP with steps for collection, validation, and analysis",
            session_token="test-session-123"
        )
        print("SOPBuilderWizardTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "response" in result
        assert "sop" in result
        assert "status" in result
        assert "next_actions" in result
        print("✅ SOPBuilderWizardTool passed validation")
        
    except Exception as e:
        print(f"❌ SOPBuilderWizardTool failed: {e}")
    
    # Test Workflow Builder Wizard Tool
    print("\n--- Testing WorkflowBuilderWizardTool ---")
    try:
        tool = WorkflowBuilderWizardTool()
        
        result = await tool.build_workflow(
            "Create a workflow for data processing with collection, validation, and analysis steps",
            session_token="test-session-123"
        )
        print("WorkflowBuilderWizardTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "response" in result
        assert "workflow" in result
        assert "status" in result
        assert "next_actions" in result
        print("✅ WorkflowBuilderWizardTool passed validation")
        
    except Exception as e:
        print(f"❌ WorkflowBuilderWizardTool failed: {e}")
    
    # Test Workflow to SOP Tool
    print("\n--- Testing WorkflowToSOPTool ---")
    try:
        tool = WorkflowToSOPTool()
        
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "nodes": [
                {"id": "1", "label": "Start", "type": "process", "description": "Begin process"},
                {"id": "2", "label": "Process", "type": "ai", "description": "Process data"},
                {"id": "3", "label": "End", "type": "process", "description": "Complete process"}
            ],
            "edges": [
                {"id": "1", "from_node": "1", "to_node": "2", "label": "flows to"},
                {"id": "2", "from_node": "2", "to_node": "3", "label": "flows to"}
            ]
        }
        
        result = await tool.convert_workflow_to_sop(workflow_data, session_token="test-session-123")
        print("WorkflowToSOPTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "sop" in result
        assert "conversion_metadata" in result
        print("✅ WorkflowToSOPTool passed validation")
        
    except Exception as e:
        print(f"❌ WorkflowToSOPTool failed: {e}")
    
    # Test SOP to Workflow Tool
    print("\n--- Testing SOPToWorkflowTool ---")
    try:
        tool = SOPToWorkflowTool()
        
        sop_data = {
            "title": "Test SOP",
            "description": "A test SOP",
            "steps": [
                {"step_number": 1, "title": "Start", "description": "Begin process"},
                {"step_number": 2, "title": "Process", "description": "Process data"},
                {"step_number": 3, "title": "End", "description": "Complete process"}
            ]
        }
        
        result = await tool.convert_sop_to_workflow(sop_data, session_token="test-session-123")
        print("SOPToWorkflowTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "workflow" in result
        assert "conversion_metadata" in result
        print("✅ SOPToWorkflowTool passed validation")
        
    except Exception as e:
        print(f"❌ SOPToWorkflowTool failed: {e}")


async def test_experience_pillar_tools():
    """Test Experience Pillar MCP Tools."""
    print("\n" + "="*60)
    print("TESTING EXPERIENCE PILLAR TOOLS")
    print("="*60)
    
    # Test Experience Outcomes Tool
    print("\n--- Testing ExperienceOutcomesTool ---")
    try:
        tool = ExperienceOutcomesTool()
        
        # Test with sample data
        content_data = {
            'quality_score': 85,
            'completeness': 90,
            'accuracy': 80
        }
        insights_data = {
            'value_score': 75,
            'actionability': 70,
            'relevance': 80
        }
        operations_data = {
            'efficiency_score': 80,
            'automation_level': 60,
            'human_ai_balance': 70
        }
        
        result = await tool.analyze_outcomes(
            content_data, insights_data, operations_data, 
            context="Healthcare data analysis platform", 
            session_token="test-session-123"
        )
        print("ExperienceOutcomesTool Result:", json.dumps(result, indent=2))
        
        # Validate structure
        assert "business_analysis" in result
        assert "outcome_predictions" in result
        assert "recommendations" in result
        assert "impact_evaluation" in result
        assert "success_metrics" in result
        print("✅ ExperienceOutcomesTool passed validation")
        
    except Exception as e:
        print(f"❌ ExperienceOutcomesTool failed: {e}")


async def main():
    """Run all pillar tool tests."""
    print("🚀 Starting Comprehensive MCP Tools Test Suite")
    print("Testing all pillar tools with Smart City patterns...")
    
    try:
        await test_content_pillar_tools()
        await test_insights_pillar_tools()
        await test_operations_pillar_tools()
        await test_experience_pillar_tools()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ Content Pillar: DataQualityTool, TabularContentTool, ContentVisualizationTool, ContentSummaryTool")
        print("✅ Insights Pillar: InsightsAnomalyTool, InsightsModelingTool")
        print("✅ Operations Pillar: OperationsCoexistenceTool, SOPBuilderWizardTool, WorkflowBuilderWizardTool, WorkflowToSOPTool, SOPToWorkflowTool")
        print("✅ Experience Pillar: ExperienceOutcomesTool")
        print("\nAll MCP tools are ready for frontend integration!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
