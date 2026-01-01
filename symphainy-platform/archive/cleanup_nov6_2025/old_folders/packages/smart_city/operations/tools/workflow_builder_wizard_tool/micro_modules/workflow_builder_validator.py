"""
Workflow Builder Validator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class WorkflowBuilderValidator:
    """
    Workflow Builder Validator following Smart City patterns.
    Handles workflow validation and quality assessment.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("WorkflowBuilderValidator micro-module initialized")
    
    async def validate_workflow_for_publishing(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow before publishing."""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check for required fields
            if not workflow.get("name") or workflow["name"] == "Untitled Workflow":
                validation_result["errors"].append("Workflow needs a proper name")
                validation_result["valid"] = False
            
            if not workflow.get("nodes"):
                validation_result["errors"].append("Workflow must have at least one node")
                validation_result["valid"] = False
            
            # Check node quality
            if workflow.get("nodes"):
                for i, node in enumerate(workflow["nodes"]):
                    if not node.get("description") or len(node["description"].strip()) < 5:
                        validation_result["warnings"].append(f"Node {i+1} description is quite short")
                    
                    if not node.get("type"):
                        validation_result["warnings"].append(f"Node {i+1} doesn't specify a type")
            
            # Check for disconnected nodes
            if workflow.get("nodes") and workflow.get("edges"):
                connected_nodes = set()
                for edge in workflow["edges"]:
                    connected_nodes.add(edge.get("from_node"))
                    connected_nodes.add(edge.get("to_node"))
                
                all_nodes = {node["id"] for node in workflow["nodes"]}
                disconnected_nodes = all_nodes - connected_nodes
                
                if disconnected_nodes:
                    validation_result["warnings"].append(f"Found {len(disconnected_nodes)} disconnected nodes")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating workflow: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }

