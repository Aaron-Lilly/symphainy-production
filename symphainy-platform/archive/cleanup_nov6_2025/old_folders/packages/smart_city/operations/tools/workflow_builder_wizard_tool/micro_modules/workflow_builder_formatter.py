"""
Workflow Builder Formatter Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class WorkflowBuilderFormatter:
    """
    Workflow Builder Formatter following Smart City patterns.
    Handles workflow formatting and presentation.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("WorkflowBuilderFormatter micro-module initialized")
    
    async def format_workflow_for_display(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Format workflow for display."""
        try:
            formatted_workflow = workflow.copy()
            
            # Add display-friendly formatting
            formatted_workflow["display_name"] = workflow.get("name", "Untitled Workflow")
            formatted_workflow["display_description"] = workflow.get("description", "No description")
            
            # Format nodes for display
            if workflow.get("nodes"):
                for node in formatted_workflow["nodes"]:
                    node["display_label"] = node.get("label", "Unlabeled Node")
                    node["display_description"] = node.get("description", "No description")
            
            # Format edges for display
            if workflow.get("edges"):
                for edge in formatted_workflow["edges"]:
                    edge["display_label"] = edge.get("label", "flows to")
            
            return formatted_workflow
            
        except Exception as e:
            self.logger.error(f"Error formatting workflow for display: {e}")
            return workflow

