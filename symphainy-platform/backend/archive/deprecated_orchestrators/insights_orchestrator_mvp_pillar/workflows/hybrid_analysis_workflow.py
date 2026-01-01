#!/usr/bin/env python3
"""
Hybrid Data Analysis Workflow

WHAT: Orchestrates hybrid data analysis (both structured and unstructured)
HOW: Combines both structured and unstructured workflows

This workflow runs both analysis types and combines results.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class HybridAnalysisWorkflow:
    """
    Workflow for hybrid data analysis (combined structured + unstructured).
    
    Runs both workflows and merges results.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: InsightsOrchestrator instance (provides services and workflows)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        content_metadata_id: Optional[str] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute hybrid data analysis workflow.
        
        Args:
            source_type: 'file' or 'content_metadata'
            file_id: File identifier (if source_type='file')
            content_metadata_id: Content metadata ID from ArangoDB (if source_type='content_metadata')
            analysis_options: Optional analysis configuration
        
        Returns:
            Dict[str, Any]: Combined analysis result
        """
        try:
            self.logger.info(f"🔀 Starting hybrid data analysis workflow: source_type={source_type}")
            
            # Import workflows
            from .structured_analysis_workflow import StructuredAnalysisWorkflow
            from .unstructured_analysis_workflow import UnstructuredAnalysisWorkflow
            
            # Run both workflows
            structured_workflow = StructuredAnalysisWorkflow(self.orchestrator)
            unstructured_workflow = UnstructuredAnalysisWorkflow(self.orchestrator)
            
            structured_result = await structured_workflow.execute(
                source_type=source_type,
                file_id=file_id,
                content_metadata_id=content_metadata_id,
                analysis_options=analysis_options
            )
            
            unstructured_result = await unstructured_workflow.execute(
                source_type=source_type,
                file_id=file_id,
                content_metadata_id=content_metadata_id,
                analysis_options=analysis_options
            )
            
            # Merge results
            merged_result = self._merge_results(structured_result, unstructured_result)
            
            self.logger.info(f"✅ Hybrid data analysis workflow complete")
            
            return merged_result
            
        except Exception as e:
            self.logger.error(f"❌ Hybrid analysis workflow failed: {e}")
            return {
                "success": False,
                "error": "Hybrid workflow execution failed",
                "error_details": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _merge_results(
        self,
        structured_result: Dict[str, Any],
        unstructured_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge structured and unstructured analysis results."""
        # Use structured result as base, add unstructured insights
        merged = structured_result.copy()
        
        # Update content_type
        if merged.get("metadata"):
            merged["metadata"]["content_type"] = "hybrid"
        
        # Merge insights
        if unstructured_result.get("insights"):
            merged["insights"] = merged.get("insights", []) + unstructured_result["insights"]
        
        # Add unstructured summary to textual summary
        if unstructured_result.get("summary", {}).get("textual"):
            merged["summary"]["textual"] += "\n\n" + unstructured_result["summary"]["textual"]
        
        return merged







