"""
SOP Manager Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SOPManager:
    """
    SOP Manager following Smart City patterns.
    Handles SOP creation, modification, and management.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("SOPManager micro-module initialized")
    
    async def add_step_to_sop(
        self, 
        sop: Optional[Dict[str, Any]], 
        user_input: str, 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Add a step to the SOP."""
        try:
            if not sop:
                sop = {
                    "title": "Untitled SOP",
                    "description": "",
                    "steps": [],
                    "created_by": None,
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "metadata": {"session_token": session_token}
                }
            
            # Create new step
            step_number = len(sop.get("steps", [])) + 1
            new_step = {
                "step_number": step_number,
                "title": f"Step {step_number}",
                "description": user_input,
                "responsible_role": None,
                "expected_output": None,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"session_token": session_token}
            }
            
            sop["steps"].append(new_step)
            sop["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "response": f"Step {step_number} added: '{user_input}'. Would you like to add another step, review your SOP, or publish?",
                "sop": sop,
                "status": "step_added",
                "next_actions": ["add_step", "review", "publish"],
                "metadata": {
                    "step_number": step_number,
                    "total_steps": len(sop["steps"]),
                    "session_token": session_token
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error adding step to SOP: {e}")
            return {
                "response": f"Error adding step: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def update_sop_title(
        self, 
        sop: Dict[str, Any], 
        new_title: str, 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Update SOP title."""
        try:
            sop["title"] = new_title
            sop["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "response": f"SOP title updated to '{new_title}'",
                "sop": sop,
                "status": "title_updated",
                "next_actions": ["review", "publish"],
                "metadata": {"session_token": session_token}
            }
            
        except Exception as e:
            self.logger.error(f"Error updating SOP title: {e}")
            return {
                "response": f"Error updating title: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def update_sop_description(
        self, 
        sop: Dict[str, Any], 
        new_description: str, 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Update SOP description."""
        try:
            sop["description"] = new_description
            sop["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "response": f"SOP description updated",
                "sop": sop,
                "status": "description_updated",
                "next_actions": ["review", "publish"],
                "metadata": {"session_token": session_token}
            }
            
        except Exception as e:
            self.logger.error(f"Error updating SOP description: {e}")
            return {
                "response": f"Error updating description: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def update_step_details(
        self, 
        sop: Dict[str, Any], 
        step_number: int, 
        **kwargs
    ) -> Dict[str, Any]:
        """Update step details."""
        try:
            if not sop.get("steps") or step_number < 1 or step_number > len(sop["steps"]):
                return {
                    "response": f"Invalid step number: {step_number}",
                    "sop": sop,
                    "status": "error",
                    "next_actions": ["retry"],
                    "metadata": {"error": "invalid_step_number"}
                }
            
            step_index = step_number - 1
            step = sop["steps"][step_index]
            
            # Update step with provided fields
            for key, value in kwargs.items():
                if key in ["title", "description", "responsible_role", "expected_output"]:
                    step[key] = value
            
            step["updated_at"] = datetime.utcnow().isoformat()
            sop["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "response": f"Step {step_number} updated successfully",
                "sop": sop,
                "status": "step_updated",
                "next_actions": ["review", "publish"],
                "metadata": {"step_number": step_number}
            }
            
        except Exception as e:
            self.logger.error(f"Error updating step details: {e}")
            return {
                "response": f"Error updating step: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def remove_step_from_sop(
        self, 
        sop: Dict[str, Any], 
        step_number: int, 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Remove step from SOP."""
        try:
            if not sop.get("steps") or step_number < 1 or step_number > len(sop["steps"]):
                return {
                    "response": f"Invalid step number: {step_number}",
                    "sop": sop,
                    "status": "error",
                    "next_actions": ["retry"],
                    "metadata": {"error": "invalid_step_number"}
                }
            
            # Remove step
            removed_step = sop["steps"].pop(step_number - 1)
            
            # Renumber remaining steps
            for i, step in enumerate(sop["steps"]):
                step["step_number"] = i + 1
            
            sop["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "response": f"Step {step_number} removed successfully",
                "sop": sop,
                "status": "step_removed",
                "next_actions": ["review", "publish"],
                "metadata": {
                    "removed_step": removed_step,
                    "total_steps": len(sop["steps"]),
                    "session_token": session_token
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error removing step from SOP: {e}")
            return {
                "response": f"Error removing step: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def reorder_sop_steps(
        self, 
        sop: Dict[str, Any], 
        new_order: List[int], 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Reorder SOP steps."""
        try:
            if not sop.get("steps"):
                return {
                    "response": "No steps to reorder",
                    "sop": sop,
                    "status": "error",
                    "next_actions": ["add_step"],
                    "metadata": {"error": "no_steps"}
                }
            
            if len(new_order) != len(sop["steps"]):
                return {
                    "response": "Invalid reorder: must include all steps",
                    "sop": sop,
                    "status": "error",
                    "next_actions": ["retry"],
                    "metadata": {"error": "invalid_reorder"}
                }
            
            # Reorder steps
            reordered_steps = []
            for new_index in new_order:
                if 1 <= new_index <= len(sop["steps"]):
                    reordered_steps.append(sop["steps"][new_index - 1])
                else:
                    return {
                        "response": f"Invalid step number in reorder: {new_index}",
                        "sop": sop,
                        "status": "error",
                        "next_actions": ["retry"],
                        "metadata": {"error": "invalid_step_number"}
                    }
            
            # Update step numbers
            for i, step in enumerate(reordered_steps):
                step["step_number"] = i + 1
            
            sop["steps"] = reordered_steps
            sop["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "response": "Steps reordered successfully",
                "sop": sop,
                "status": "steps_reordered",
                "next_actions": ["review", "publish"],
                "metadata": {
                    "new_order": new_order,
                    "session_token": session_token
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error reordering SOP steps: {e}")
            return {
                "response": f"Error reordering steps: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def get_sop_structure(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get SOP structure information."""
        try:
            steps = sop.get("steps", [])
            return {
                "title": sop.get("title", "Untitled"),
                "description": sop.get("description", ""),
                "total_steps": len(steps),
                "step_titles": [step.get("title", f"Step {i+1}") for i, step in enumerate(steps)],
                "created_at": sop.get("created_at"),
                "updated_at": sop.get("updated_at"),
                "version": sop.get("version", "1.0.0")
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SOP structure: {e}")
            return {"error": str(e)}
    
    async def get_sop_metadata(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get SOP metadata."""
        try:
            return {
                "title": sop.get("title"),
                "description": sop.get("description"),
                "version": sop.get("version"),
                "created_at": sop.get("created_at"),
                "updated_at": sop.get("updated_at"),
                "created_by": sop.get("created_by"),
                "metadata": sop.get("metadata", {}),
                "step_count": len(sop.get("steps", []))
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SOP metadata: {e}")
            return {"error": str(e)}

