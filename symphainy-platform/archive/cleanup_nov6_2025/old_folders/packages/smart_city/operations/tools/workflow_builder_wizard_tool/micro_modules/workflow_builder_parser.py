"""
Workflow Builder Parser Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class WorkflowBuilderParser:
    """
    Workflow Builder Parser following Smart City patterns.
    Handles parsing of descriptions into workflow structures.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("WorkflowBuilderParser micro-module initialized")
    
    async def description_to_workflow(
        self, 
        user_input: str, 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Convert description to workflow structure."""
        try:
            # Create basic workflow structure
            workflow = {
                "name": "Generated Workflow",
                "description": user_input,
                "nodes": [],
                "edges": [],
                "created_by": None,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "metadata": {
                    "generated_from_description": True,
                    "session_token": session_token
                }
            }
            
            # Parse description into steps
            steps = await self._parse_description_to_steps(user_input)
            
            # Create nodes from steps
            for i, step in enumerate(steps):
                node = {
                    "id": f"node_{i+1}",
                    "label": f"Step {i+1}",
                    "type": "process",
                    "description": step,
                    "position": {"x": 100 + i * 200, "y": 100},
                    "created_at": datetime.utcnow().isoformat(),
                    "metadata": {"parsed_from_description": True}
                }
                workflow["nodes"].append(node)
            
            # Create edges between consecutive nodes
            for i in range(len(workflow["nodes"]) - 1):
                edge = {
                    "id": f"edge_{i+1}",
                    "from_node": workflow["nodes"][i]["id"],
                    "to_node": workflow["nodes"][i+1]["id"],
                    "label": "flows to",
                    "created_at": datetime.utcnow().isoformat(),
                    "metadata": {"parsed_from_description": True}
                }
                workflow["edges"].append(edge)
            
            return workflow
            
        except Exception as e:
            self.logger.error(f"Error parsing description to workflow: {e}")
            return {
                "name": "Error Generating Workflow",
                "description": "Failed to generate workflow from description",
                "nodes": [],
                "edges": [],
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "metadata": {"error": str(e), "session_token": session_token}
            }
    
    async def _parse_description_to_steps(self, description: str) -> List[str]:
        """Parse description into individual steps."""
        try:
            steps = []
            
            # Split by common step indicators
            step_patterns = [
                r'\d+\.\s*([^\.]+\.)',  # "1. Step description."
                r'Step\s+\d+:\s*([^\.]+\.)',  # "Step 1: Step description."
                r'-\s*([^\.]+\.)',  # "- Step description."
                r'\*\s*([^\.]+\.)',  # "* Step description."
            ]
            
            # Try each pattern
            for pattern in step_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE)
                if matches:
                    for match in matches:
                        step_text = match.strip()
                        if len(step_text) > 5:  # Only include substantial steps
                            steps.append(step_text)
                    break
            
            # If no structured steps found, try to split by sentences
            if not steps:
                sentences = re.split(r'[.!?]+', description)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 10:  # Only include substantial sentences
                        steps.append(sentence)
            
            # If still no steps, create a single step from the whole description
            if not steps:
                steps.append(description)
            
            return steps
            
        except Exception as e:
            self.logger.error(f"Error parsing description to steps: {e}")
            return [description]

