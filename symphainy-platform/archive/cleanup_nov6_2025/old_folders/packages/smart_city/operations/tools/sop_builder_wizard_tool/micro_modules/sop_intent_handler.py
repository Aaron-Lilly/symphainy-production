"""
SOP Intent Handler Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SOPIntentHandler:
    """
    SOP Intent Handler following Smart City patterns.
    Handles user intent routing and response generation.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("SOPIntentHandler micro-module initialized")
    
    async def route_user_intent(self, user_input: str) -> str:
        """Route user input to appropriate intent."""
        try:
            user_input_lower = user_input.strip().lower()
            
            # Intent patterns
            if any(keyword in user_input_lower for keyword in ["review", "show", "display", "see"]):
                return "review"
            elif any(keyword in user_input_lower for keyword in ["publish", "finalize", "done", "ready"]):
                return "publish"
            elif any(keyword in user_input_lower for keyword in ["help", "what", "how", "instructions"]):
                return "help"
            elif any(keyword in user_input_lower for keyword in ["reset", "clear", "start over"]):
                return "reset"
            elif any(keyword in user_input_lower for keyword in ["show", "display", "see"]):
                return "display"
            else:
                return "add_step"
                
        except Exception as e:
            self.logger.error(f"Error routing user intent: {e}")
            return "add_step"
    
    async def handle_review_request(
        self, 
        sop: Optional[Dict[str, Any]], 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Handle SOP review request."""
        try:
            if sop and sop.get("steps"):
                return {
                    "response": "Here's your current SOP draft. When you're ready, just say 'publish' and I'll finalize your SOP.",
                    "sop": sop,
                    "status": "review",
                    "next_actions": ["publish", "add_step", "edit_step", "remove_step"],
                    "metadata": {
                        "step_count": len(sop.get("steps", [])),
                        "session_token": session_token
                    }
                }
            else:
                return {
                    "response": "You haven't started building your SOP yet. Let's add some steps first!",
                    "sop": None,
                    "status": "empty",
                    "next_actions": ["add_step", "help"],
                    "metadata": {"session_token": session_token}
                }
                
        except Exception as e:
            self.logger.error(f"Error handling review request: {e}")
            return {
                "response": f"Error reviewing SOP: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def handle_publish_request(
        self, 
        sop: Optional[Dict[str, Any]], 
        session_token: Optional[str], 
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle SOP publish request."""
        try:
            if sop and sop.get("steps"):
                if validation_result.get("valid", False):
                    return {
                        "response": "Great! I'll publish your SOP now. (Please use the 'publish' action to finalize.)",
                        "sop": sop,
                        "status": "ready_to_publish",
                        "next_actions": ["confirm_publish", "edit_step"],
                        "metadata": {
                            "validation_result": validation_result,
                            "session_token": session_token,
                            "publish_ready": True
                        }
                    }
                else:
                    return {
                        "response": f"Your SOP needs some adjustments before publishing: {', '.join(validation_result.get('errors', []))}",
                        "sop": sop,
                        "status": "needs_validation",
                        "next_actions": ["fix_validation_errors", "review"],
                        "metadata": {
                            "validation_result": validation_result,
                            "session_token": session_token
                        }
                    }
            else:
                return {
                    "response": "You need to add at least one step before publishing your SOP.",
                    "sop": sop,
                    "status": "empty",
                    "next_actions": ["add_step"],
                    "metadata": {"session_token": session_token}
                }
                
        except Exception as e:
            self.logger.error(f"Error handling publish request: {e}")
            return {
                "response": f"Error publishing SOP: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def handle_display_request(self, sop: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle SOP display request."""
        try:
            return {
                "response": "Would you like to review your SOP draft here in our chat session, or are you ready to publish it?",
                "sop": sop,
                "status": "display_request",
                "next_actions": ["review", "publish"],
                "metadata": {"has_sop": sop is not None}
            }
            
        except Exception as e:
            self.logger.error(f"Error handling display request: {e}")
            return {
                "response": f"Error displaying SOP: {str(e)}",
                "sop": sop,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def handle_help_request(self) -> Dict[str, Any]:
        """Handle help request."""
        try:
            help_text = """
            I'm here to help you build a Standard Operating Procedure (SOP). Here's what you can do:
            
            • **Add steps**: Describe a process step, and I'll add it to your SOP
            • **Review**: Say "review" to see your current SOP draft
            • **Publish**: Say "publish" when you're ready to finalize your SOP
            • **Reset**: Say "clear" to start over
            • **Help**: Say "help" anytime for these instructions
            
            Let's start by adding your first step!
            """
            return {
                "response": help_text,
                "sop": None,
                "status": "help",
                "next_actions": ["add_step", "review"],
                "metadata": {"help_shown": True}
            }
            
        except Exception as e:
            self.logger.error(f"Error handling help request: {e}")
            return {
                "response": f"Error showing help: {str(e)}",
                "sop": None,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def handle_reset_request(self, session_token: Optional[str]) -> Dict[str, Any]:
        """Handle reset request."""
        try:
            return {
                "response": "I've cleared your SOP draft. Let's start fresh! What's the first step in your process?",
                "sop": None,
                "status": "reset",
                "next_actions": ["add_step"],
                "metadata": {"session_token": session_token, "reset": True}
            }
            
        except Exception as e:
            self.logger.error(f"Error handling reset request: {e}")
            return {
                "response": f"Error resetting SOP: {str(e)}",
                "sop": None,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        return ["add_step", "review", "publish", "display", "help", "reset"]
    
    async def get_intent_patterns(self) -> Dict[str, List[str]]:
        """Get intent patterns for matching."""
        return {
            "review": ["review", "show", "display", "see"],
            "publish": ["publish", "finalize", "done", "ready"],
            "help": ["help", "what", "how", "instructions"],
            "reset": ["reset", "clear", "start over"],
            "display": ["show", "display", "see"],
            "add_step": ["add", "step", "process", "procedure"]
        }
    
    async def get_intent_statistics(self, user_inputs: List[str]) -> Dict[str, Any]:
        """Get statistics about user intent patterns."""
        try:
            intent_counts = {}
            for input_text in user_inputs:
                intent = await self.route_user_intent(input_text)
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
            return {
                "total_inputs": len(user_inputs),
                "intent_distribution": intent_counts,
                "most_common_intent": max(intent_counts, key=intent_counts.get) if intent_counts else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting intent statistics: {e}")
            return {"error": str(e)}
    
    async def get_intent_guidance(self, user_input: str) -> Dict[str, Any]:
        """Get guidance for user input."""
        try:
            intent = await self.route_user_intent(user_input)
            
            guidance = {
                "detected_intent": intent,
                "suggestions": [],
                "next_actions": []
            }
            
            if intent == "add_step":
                guidance["suggestions"].append("Describe the process step in detail")
                guidance["next_actions"] = ["add_step", "review"]
            elif intent == "review":
                guidance["suggestions"].append("Review your current SOP draft")
                guidance["next_actions"] = ["review", "publish"]
            elif intent == "publish":
                guidance["suggestions"].append("Publish your SOP when ready")
                guidance["next_actions"] = ["publish", "review"]
            elif intent == "help":
                guidance["suggestions"].append("Get help with SOP building")
                guidance["next_actions"] = ["help", "add_step"]
            elif intent == "reset":
                guidance["suggestions"].append("Start over with a new SOP")
                guidance["next_actions"] = ["reset", "add_step"]
            
            return guidance
            
        except Exception as e:
            self.logger.error(f"Error getting intent guidance: {e}")
            return {"error": str(e)}

