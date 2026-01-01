#!/usr/bin/env python3
"""
Test Datasets for Business Enablement Tests

Provides sample test data for:
- Documents (PDF, DOCX, HTML, etc.)
- Data files (CSV, JSON, etc.)
- Workflows
- Business scenarios

These datasets are used in functionality, integration, and E2E tests.
"""

from typing import Dict, Any, List
import json

# ============================================================================
# SAMPLE DOCUMENTS
# ============================================================================

SAMPLE_DOCUMENT_PDF = b"%PDF-1.4\n%Test PDF Content\n"
SAMPLE_DOCUMENT_DOCX = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Minimal DOCX header
SAMPLE_DOCUMENT_HTML = b"<html><body><h1>Test Document</h1><p>This is a test document for content analysis.</p></body></html>"
SAMPLE_DOCUMENT_TEXT = b"This is a sample text document for testing file parsing and content analysis capabilities."

def get_sample_document(format: str = "text") -> bytes:
    """Get sample document in specified format."""
    formats = {
        "pdf": SAMPLE_DOCUMENT_PDF,
        "docx": SAMPLE_DOCUMENT_DOCX,
        "html": SAMPLE_DOCUMENT_HTML,
        "text": SAMPLE_DOCUMENT_TEXT,
    }
    return formats.get(format.lower(), SAMPLE_DOCUMENT_TEXT)

# ============================================================================
# SAMPLE DATA FILES
# ============================================================================

SAMPLE_CSV_DATA = """id,name,value,date
1,Item A,100.50,2024-01-01
2,Item B,200.75,2024-01-02
3,Item C,150.25,2024-01-03
4,Item D,300.00,2024-01-04
5,Item E,175.50,2024-01-05"""

SAMPLE_JSON_DATA = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin", "score": 95},
        {"id": 2, "name": "Bob", "role": "user", "score": 87},
        {"id": 3, "name": "Charlie", "role": "user", "score": 92},
    ],
    "metadata": {
        "total": 3,
        "average_score": 91.33,
        "last_updated": "2024-01-01T00:00:00Z"
    }
}

def get_sample_csv_data() -> str:
    """Get sample CSV data."""
    return SAMPLE_CSV_DATA

def get_sample_json_data() -> Dict[str, Any]:
    """Get sample JSON data."""
    return SAMPLE_JSON_DATA.copy()

# ============================================================================
# SAMPLE WORKFLOWS
# ============================================================================

SAMPLE_WORKFLOW_DEFINITION = {
    "id": "test_workflow_001",
    "name": "Test Workflow",
    "description": "A test workflow for Business Enablement testing",
    "nodes": [
        {
            "id": "start",
            "name": "Start",
            "type": "start",
            "properties": {}
        },
        {
            "id": "process",
            "name": "Process Data",
            "type": "task",
            "properties": {
                "service": "DataAnalyzerService",
                "action": "analyze"
            }
        },
        {
            "id": "end",
            "name": "End",
            "type": "end",
            "properties": {}
        }
    ],
    "edges": [
        {
            "id": "edge_1",
            "source": "start",
            "target": "process",
            "condition": None
        },
        {
            "id": "edge_2",
            "source": "process",
            "target": "end",
            "condition": None
        }
    ],
    "properties": {
        "version": "1.0",
        "created_by": "test_suite"
    }
}

def get_sample_workflow_definition() -> Dict[str, Any]:
    """Get sample workflow definition."""
    return SAMPLE_WORKFLOW_DEFINITION.copy()

# ============================================================================
# SAMPLE BUSINESS SCENARIOS
# ============================================================================

SAMPLE_CONTENT_ANALYSIS_SCENARIO = {
    "scenario_id": "content_analysis_001",
    "name": "Document Analysis Request",
    "description": "User uploads a document and requests analysis",
    "steps": [
        {
            "step": 1,
            "action": "upload_document",
            "data": {
                "filename": "test_document.pdf",
                "file_data": SAMPLE_DOCUMENT_PDF
            }
        },
        {
            "step": 2,
            "action": "request_analysis",
            "data": {
                "analysis_type": "content_analysis",
                "options": {
                    "extract_entities": True,
                    "generate_summary": True
                }
            }
        },
        {
            "step": 3,
            "action": "expect_result",
            "data": {
                "result_type": "analysis_report",
                "expected_fields": ["summary", "entities", "insights"]
            }
        }
    ]
}

SAMPLE_INSIGHTS_GENERATION_SCENARIO = {
    "scenario_id": "insights_generation_001",
    "name": "Insights Generation Request",
    "description": "User requests insights from business data",
    "steps": [
        {
            "step": 1,
            "action": "provide_data",
            "data": {
                "data_source": "business_metrics",
                "data": SAMPLE_JSON_DATA
            }
        },
        {
            "step": 2,
            "action": "request_insights",
            "data": {
                "insight_type": "trend_analysis",
                "timeframe": "quarterly"
            }
        },
        {
            "step": 3,
            "action": "expect_result",
            "data": {
                "result_type": "insights_report",
                "expected_fields": ["trends", "recommendations", "metrics"]
            }
        }
    ]
}

SAMPLE_OPERATIONS_OPTIMIZATION_SCENARIO = {
    "scenario_id": "operations_optimization_001",
    "name": "Operations Optimization Request",
    "description": "User requests optimization of business operations",
    "steps": [
        {
            "step": 1,
            "action": "provide_process_data",
            "data": {
                "process_name": "order_fulfillment",
                "process_data": {
                    "steps": ["receive", "process", "fulfill", "ship"],
                    "bottlenecks": ["processing", "shipping"]
                }
            }
        },
        {
            "step": 2,
            "action": "request_optimization",
            "data": {
                "optimization_goals": ["reduce_time", "improve_efficiency"],
                "constraints": ["budget", "resources"]
            }
        },
        {
            "step": 3,
            "action": "expect_result",
            "data": {
                "result_type": "optimization_plan",
                "expected_fields": ["sop", "workflow", "recommendations"]
            }
        }
    ]
}

def get_sample_scenario(scenario_type: str) -> Dict[str, Any]:
    """Get sample business scenario by type."""
    scenarios = {
        "content_analysis": SAMPLE_CONTENT_ANALYSIS_SCENARIO,
        "insights_generation": SAMPLE_INSIGHTS_GENERATION_SCENARIO,
        "operations_optimization": SAMPLE_OPERATIONS_OPTIMIZATION_SCENARIO,
    }
    return scenarios.get(scenario_type, {}).copy()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_test_file(filename: str, content: bytes, directory: str = "/tmp") -> str:
    """Create a test file and return its path."""
    import os
    filepath = os.path.join(directory, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath

def cleanup_test_file(filepath: str):
    """Clean up a test file."""
    import os
    if os.path.exists(filepath):
        os.remove(filepath)

