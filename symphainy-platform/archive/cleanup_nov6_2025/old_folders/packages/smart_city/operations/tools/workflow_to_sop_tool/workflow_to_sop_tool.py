"""
Workflow to SOP Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from typing import Dict, Any, List, Optional
from datetime import datetime


class WorkflowToSOPTool(BaseMCP):
    """
    Workflow to SOP Tool for Operations Pillar.
    Converts workflow graphs to SOP structures.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "workflow_to_sop_tool"
        self.pillar = "operations"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("WorkflowToSOPTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("WorkflowToSOPTool initialized with Smart City patterns")
    
    async def convert_workflow_to_sop(
        self, 
        workflow_dict: Dict[str, Any], 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert workflow graph to SOP structure.
        
        Args:
            workflow_dict: Workflow graph dictionary
            session_token: Session token for Smart City integration
            
        Returns:
            SOP structure dictionary
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "error": "Invalid session token",
                        "sop": None
                    }
            
            # Normalize workflow input
            workflow = await self._normalize_workflow_input(workflow_dict)
            
            if not workflow or not workflow.get("nodes"):
                # Create minimal SOP if no workflow
                sop_dict = {
                    "title": "Generated SOP",
                    "description": "Auto-generated from workflow.",
                    "steps": [{
                        "step_number": 1,
                        "title": "Start",
                        "description": "Begin the process.",
                        "responsible_role": None,
                        "expected_output": None,
                        "created_at": datetime.utcnow().isoformat()
                    }],
                    "created_at": datetime.utcnow().isoformat(),
                    "created_by": None,
                    "version": "1.0.0",
                    "metadata": {"session_token": session_token}
                }
            else:
                # Convert nodes to SOP steps
                steps = await self._nodes_to_sop_steps(workflow.get("nodes", []))
                
                sop_dict = {
                    "title": workflow.get("name", "Generated SOP"),
                    "description": workflow.get("description", "Auto-generated from workflow."),
                    "steps": [step for step in steps],
                    "created_at": datetime.utcnow().isoformat(),
                    "created_by": None,
                    "version": workflow.get("version", "1.0"),
                    "metadata": {
                        **workflow.get("metadata", {}),
                        "session_token": session_token,
                        "converted_from_workflow": True
                    }
                }
            
            # Enhance with LLM if available
            sop_dict = await self._enhance_sop_with_llm(sop_dict)
            
            return {
                "sop": sop_dict,
                "conversion_metadata": {
                    "original_workflow_nodes": len(workflow.get("nodes", [])),
                    "generated_sop_steps": len(sop_dict.get("steps", [])),
                    "conversion_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            self._logger.error(f"Error converting workflow to SOP: {e}")
            return {
                "error": f"Conversion failed: {str(e)}",
                "sop": None
            }
    
    async def _normalize_workflow_input(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize workflow input."""
        try:
            if not workflow_input:
                return None
            
            # Ensure required fields exist
            normalized = {
                "name": workflow_input.get("name", "Untitled Workflow"),
                "description": workflow_input.get("description", ""),
                "nodes": workflow_input.get("nodes", []),
                "edges": workflow_input.get("edges", []),
                "version": workflow_input.get("version", "1.0"),
                "metadata": workflow_input.get("metadata", {})
            }
            
            return normalized
            
        except Exception as e:
            self._logger.error(f"Error normalizing workflow input: {e}")
            return workflow_input
    
    async def _nodes_to_sop_steps(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert workflow nodes to SOP steps."""
        try:
            steps = []
            for idx, node in enumerate(nodes):
                label = node.get("label") or node.get("id") or f"Step {idx+1}"
                node_type = node.get("type") or "unknown"
                
                # Infer responsible role from type or metadata
                responsible_role = None
                if node_type == "ai":
                    responsible_role = "AI"
                elif node_type == "human":
                    responsible_role = "Human"
                elif node_type == "handoff":
                    responsible_role = "Handoff"
                elif node.get("metadata", {}).get("actor"):
                    responsible_role = node["metadata"]["actor"]
                
                step = {
                    "step_number": idx + 1,
                    "title": label,
                    "description": node.get("description", label),
                    "responsible_role": responsible_role,
                    "expected_output": None,
                    "created_at": datetime.utcnow().isoformat(),
                    "metadata": {
                        "original_node_id": node.get("id"),
                        "original_node_type": node_type
                    }
                }
                steps.append(step)
            
            return steps
            
        except Exception as e:
            self._logger.error(f"Error converting nodes to SOP steps: {e}")
            return []
    
    async def _enhance_sop_with_llm(self, sop_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance SOP with LLM gap filling."""
        try:
            # Placeholder for LLM enhancement
            # In a real implementation, this would use an LLM to fill in missing fields
            
            enhanced_sop = sop_dict.copy()
            
            # Simple enhancement - add expected outputs if missing
            for step in enhanced_sop.get("steps", []):
                if not step.get("expected_output"):
                    # Infer expected output from step description
                    description = step.get("description", "").lower()
                    if any(word in description for word in ["create", "generate", "produce"]):
                        step["expected_output"] = "Generated content or document"
                    elif any(word in description for word in ["review", "check", "validate"]):
                        step["expected_output"] = "Approval or validation result"
                    elif any(word in description for word in ["extract", "analyze", "process"]):
                        step["expected_output"] = "Processed data or analysis"
                    else:
                        step["expected_output"] = "Completed task output"
            
            return enhanced_sop
            
        except Exception as e:
            self._logger.error(f"Error enhancing SOP with LLM: {e}")
            return sop_dict

