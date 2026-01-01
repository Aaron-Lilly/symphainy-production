"""
SOP to Workflow Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class SOPToWorkflowTool(BaseMCP):
    """
    SOP to Workflow Tool for Operations Pillar.
    Converts SOP structures to workflow graphs.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "sop_to_workflow_tool"
        self.pillar = "operations"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("SOPToWorkflowTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("SOPToWorkflowTool initialized with Smart City patterns")
    
    async def convert_sop_to_workflow(
        self, 
        sop_input: Dict[str, Any], 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert SOP structure to workflow graph.
        
        Args:
            sop_input: SOP structure dictionary
            session_token: Session token for Smart City integration
            
        Returns:
            Workflow graph dictionary
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "error": "Invalid session token",
                        "workflow": None
                    }
            
            # Extract steps from SOP
            steps = await self._extract_steps_from_sop(sop_input)
            
            if not steps:
                # Create minimal workflow if no steps
                workflow_dict = {
                    "nodes": [{
                        "id": "1",
                        "label": "Start",
                        "type": "process",
                        "description": "Begin the process",
                        "position": {"x": 100, "y": 100},
                        "metadata": {"source": "SOP"}
                    }],
                    "edges": [],
                    "name": "Generated Workflow",
                    "version": "1.0",
                    "description": "Auto-generated from SOP."
                }
            else:
                # Create nodes from steps
                nodes = []
                for idx, step in enumerate(steps):
                    node = await self._step_to_node(step, idx)
                    nodes.append(node)
                
                # Create edges (sequential for now)
                edges = []
                for i in range(len(nodes) - 1):
                    edge = {
                        "id": f"edge_{i+1}",
                        "from_node": nodes[i]["id"],
                        "to_node": nodes[i+1]["id"],
                        "label": "flows to",
                        "created_at": datetime.utcnow().isoformat(),
                        "metadata": {"source": "SOP"}
                    }
                    edges.append(edge)
                
                workflow_dict = {
                    "nodes": nodes,
                    "edges": edges,
                    "name": sop_input.get("title", "Generated Workflow"),
                    "version": sop_input.get("version", "1.0"),
                    "description": sop_input.get("description", "Auto-generated from SOP."),
                    "created_at": datetime.utcnow().isoformat(),
                    "metadata": {
                        **sop_input.get("metadata", {}),
                        "session_token": session_token,
                        "converted_from_sop": True
                    }
                }
            
            return {
                "workflow": workflow_dict,
                "conversion_metadata": {
                    "original_sop_steps": len(steps),
                    "generated_workflow_nodes": len(workflow_dict.get("nodes", [])),
                    "generated_workflow_edges": len(workflow_dict.get("edges", [])),
                    "conversion_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self._logger.error(f"Error converting SOP to workflow: {e}")
            return {
                "error": f"Conversion failed: {str(e)}",
                "workflow": None
            }
    
    async def _extract_steps_from_sop(self, sop_input: Dict[str, Any]) -> List[str]:
        """Extract steps from SOP input."""
        try:
            if isinstance(sop_input, dict) and "steps" in sop_input:
                # SOPModel dict: extract step descriptions
                steps = []
                for step in sop_input["steps"]:
                    if isinstance(step, dict) and step.get("description"):
                        steps.append(step["description"])
                    elif isinstance(step, str):
                        steps.append(step)
                return steps
            elif isinstance(sop_input, str):
                # SOP text: parse step descriptions
                return await self._parse_sop_steps(sop_input)
            else:
                return []
                
        except Exception as e:
            self._logger.error(f"Error extracting steps from SOP: {e}")
            return []
    
    async def _parse_sop_steps(self, sop_text: str) -> List[str]:
        """Parse SOP text into individual steps."""
        try:
            # Split by lines or numbered steps
            lines = [line.strip() for line in sop_text.splitlines() if line.strip()]
            steps = []
            
            for line in lines:
                # Match "Step X: ..." or numbered/bulleted steps
                match = re.match(r"^(Step \d+:|\d+\.|- )?(.+)$", line)
                if match:
                    steps.append(match.group(2).strip())
            
            return steps if steps else lines
            
        except Exception as e:
            self._logger.error(f"Error parsing SOP steps: {e}")
            return []
    
    async def _step_to_node(self, step: str, idx: int) -> Dict[str, Any]:
        """Convert step to workflow node."""
        try:
            # Infer node type from step content
            step_lower = step.lower()
            if any(word in step_lower for word in ["ai", "automate", "extract", "screen", "classify"]):
                node_type = "ai"
            elif any(word in step_lower for word in ["review", "approve", "human", "sign", "validate"]):
                node_type = "human"
            elif any(word in step_lower for word in ["handoff", "transfer", "pass"]):
                node_type = "handoff"
            else:
                node_type = "process"
            
            return {
                "id": str(idx + 1),
                "label": step,
                "type": node_type,
                "description": step,
                "position": {"x": 100 + idx * 200, "y": 100},
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"source": "SOP"}
            }
            
        except Exception as e:
            self._logger.error(f"Error converting step to node: {e}")
            return {
                "id": str(idx + 1),
                "label": step,
                "type": "process",
                "description": step,
                "position": {"x": 100 + idx * 200, "y": 100},
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"source": "SOP", "error": str(e)}
            }

