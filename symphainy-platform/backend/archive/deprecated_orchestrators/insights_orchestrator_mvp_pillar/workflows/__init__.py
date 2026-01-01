#!/usr/bin/env python3
"""
Insights Orchestrator Workflows

Analysis workflows for different content types:
- StructuredAnalysisWorkflow: Structured data analysis (VARK-style)
- UnstructuredAnalysisWorkflow: Unstructured data analysis (APG/AAR)
- HybridAnalysisWorkflow: Combined analysis
"""

from .structured_analysis_workflow import StructuredAnalysisWorkflow
from .unstructured_analysis_workflow import UnstructuredAnalysisWorkflow
from .hybrid_analysis_workflow import HybridAnalysisWorkflow

__all__ = [
    "StructuredAnalysisWorkflow",
    "UnstructuredAnalysisWorkflow",
    "HybridAnalysisWorkflow"
]







