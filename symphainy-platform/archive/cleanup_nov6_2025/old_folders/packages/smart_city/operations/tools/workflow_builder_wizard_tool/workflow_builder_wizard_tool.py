"""
Workflow Builder Wizard Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from .micro_modules.workflow_builder_ai_engine import WorkflowBuilderAIEngine
from .micro_modules.workflow_builder_parser import WorkflowBuilderParser
from .micro_modules.workflow_builder_validator import WorkflowBuilderValidator
from .micro_modules.workflow_builder_statistics import WorkflowBuilderStatistics
from .micro_modules.workflow_builder_formatter import WorkflowBuilderFormatter
from typing import Dict, Any, List, Optional
from datetime import datetime


class WorkflowBuilderWizardTool(BaseMCP):
    """
    Workflow Builder Wizard Tool for Operations Pillar.
    Guides users to create workflows from free-form descriptions via chat.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "workflow_builder_wizard_tool"
        self.pillar = "operations"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("WorkflowBuilderWizardTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("WorkflowBuilderWizardTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.ai_engine = WorkflowBuilderAIEngine(self._logger, self._config)
            self.parser = WorkflowBuilderParser(self._logger, self._config)
            self.validator = WorkflowBuilderValidator(self._logger, self._config)
            self.statistics = WorkflowBuilderStatistics(self._logger, self._config)
            self.formatter = WorkflowBuilderFormatter(self._logger, self._config)
            
            self._logger.info("WorkflowBuilderWizardTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing WorkflowBuilderWizardTool micro-modules: {e}")
            raise e
    
    async def build_workflow(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        draft_workflow: Optional[Dict[str, Any]] = None, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build workflow using micro-module architecture.
        
        Args:
            user_input: User input for workflow building
            conversation_history: Conversation history
            draft_workflow: Current workflow draft
            session_token: Session token for Smart City integration
            
        Returns:
            Wizard response with updated workflow draft
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "response": "Session validation failed. Please refresh and try again.",
                        "workflow": draft_workflow,
                        "status": "error",
                        "next_actions": ["refresh_session"],
                        "metadata": {"error": "invalid_session"}
                    }
            
            # Process user input
            workflow = draft_workflow.copy() if draft_workflow else None
            
            # Find the last workflow in the conversation history, if any
            if not workflow and conversation_history:
                for turn in reversed(conversation_history):
                    if isinstance(turn.get("agent"), dict) and "workflow" in turn["agent"]:
                        workflow = turn["agent"]["workflow"]
                        break
            
            user_input_lower = user_input.strip().lower()
            
            # Handle different user intents
            if user_input_lower in ["review", "let's review", "show workflow", "show me my workflow", "yes, let's review"]:
                return await self._handle_review_request(workflow, session_token)
            elif user_input_lower in ["publish", "finalize", "done", "ready to publish"]:
                return await self._handle_publish_request(workflow, session_token)
            elif any(kw in user_input_lower for kw in ["show", "see", "display", "workflow"]):
                return await self._handle_display_request(workflow)
            elif user_input_lower in ["help", "what can i do", "instructions"]:
                return await self._handle_help_request()
            elif user_input_lower in ["clear", "reset", "start over"]:
                return await self._handle_reset_request(session_token)
            elif any(kw in user_input_lower for kw in ["add node", "add step", "add process"]):
                return await self._handle_node_addition(user_input, workflow, session_token)
            elif any(kw in user_input_lower for kw in ["connect", "link", "edge", "flow"]):
                return await self._handle_edge_addition(user_input, workflow, session_token)
            else:
                # Default: add a node or continue building
                return await self._handle_node_addition(user_input, workflow, session_token)
                
        except Exception as e:
            self._logger.error(f"Error in WorkflowBuilderWizardTool.build_workflow: {e}")
            return {
                "response": f"An error occurred while processing your request: {str(e)}",
                "workflow": draft_workflow,
                "status": "error",
                "next_actions": ["retry", "help"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_review_request(
        self, 
        workflow: Optional[Dict[str, Any]], 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Handle workflow review request."""
        try:
            if workflow and workflow.get("nodes"):
                return {
                    "response": "Here's your current workflow draft. When you're ready, just say 'publish' and I'll finalize your workflow.",
                    "workflow": workflow,
                    "status": "review",
                    "next_actions": ["publish", "add_node", "add_edge", "edit_node"],
                    "metadata": {
                        "node_count": len(workflow.get("nodes", [])),
                        "edge_count": len(workflow.get("edges", [])),
                        "session_token": session_token
                    }
                }
            else:
                return {
                    "response": "You haven't started building your workflow yet. Let's add some nodes first!",
                    "workflow": None,
                    "status": "empty",
                    "next_actions": ["add_node", "help"],
                    "metadata": {"session_token": session_token}
                }
                
        except Exception as e:
            self._logger.error(f"Error handling review request: {e}")
            return {
                "response": f"Error reviewing workflow: {str(e)}",
                "workflow": workflow,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_publish_request(
        self, 
        workflow: Optional[Dict[str, Any]], 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Handle workflow publish request."""
        try:
            if workflow and workflow.get("nodes"):
                # Validate workflow before publishing
                validation_result = await self.validator.validate_workflow_for_publishing(workflow)
                if validation_result["valid"]:
                    return {
                        "response": "Great! I'll publish your workflow now. (Please use the 'publish' action to finalize.)",
                        "workflow": workflow,
                        "status": "ready_to_publish",
                        "next_actions": ["confirm_publish", "edit_node"],
                        "metadata": {
                            "validation_result": validation_result,
                            "session_token": session_token,
                            "publish_ready": True
                        }
                    }
                else:
                    return {
                        "response": f"Your workflow needs some adjustments before publishing: {', '.join(validation_result['errors'])}",
                        "workflow": workflow,
                        "status": "needs_validation",
                        "next_actions": ["fix_validation_errors", "review"],
                        "metadata": {
                            "validation_result": validation_result,
                            "session_token": session_token
                        }
                    }
            else:
                return {
                    "response": "You need to add at least one node before publishing your workflow.",
                    "workflow": workflow,
                    "status": "empty",
                    "next_actions": ["add_node"],
                    "metadata": {"session_token": session_token}
                }
                
        except Exception as e:
            self._logger.error(f"Error handling publish request: {e}")
            return {
                "response": f"Error publishing workflow: {str(e)}",
                "workflow": workflow,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_display_request(self, workflow: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle workflow display request."""
        try:
            return {
                "response": "Would you like to review your workflow draft here in our chat session, or are you ready to publish it?",
                "workflow": workflow,
                "status": "display_request",
                "next_actions": ["review", "publish"],
                "metadata": {"has_workflow": workflow is not None}
            }
            
        except Exception as e:
            self._logger.error(f"Error handling display request: {e}")
            return {
                "response": f"Error displaying workflow: {str(e)}",
                "workflow": workflow,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_help_request(self) -> Dict[str, Any]:
        """Handle help request."""
        try:
            help_text = """
            I'm here to help you build a workflow. Here's what you can do:
            
            • **Add nodes**: Describe a process or step, and I'll add it as a node
            • **Connect nodes**: Say "connect A to B" to link nodes together
            • **Review**: Say "review" to see your current workflow draft
            • **Publish**: Say "publish" when you're ready to finalize your workflow
            • **Reset**: Say "clear" to start over
            • **Help**: Say "help" anytime for these instructions
            
            Let's start by adding your first node!
            """
            return {
                "response": help_text,
                "workflow": None,
                "status": "help",
                "next_actions": ["add_node", "review"],
                "metadata": {"help_shown": True}
            }
            
        except Exception as e:
            self._logger.error(f"Error handling help request: {e}")
            return {
                "response": f"Error showing help: {str(e)}",
                "workflow": None,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_reset_request(self, session_token: Optional[str]) -> Dict[str, Any]:
        """Handle reset request."""
        try:
            return {
                "response": "I've cleared your workflow draft. Let's start fresh! What's the first process or step?",
                "workflow": None,
                "status": "reset",
                "next_actions": ["add_node"],
                "metadata": {"session_token": session_token, "reset": True}
            }
            
        except Exception as e:
            self._logger.error(f"Error handling reset request: {e}")
            return {
                "response": f"Error resetting workflow: {str(e)}",
                "workflow": None,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_node_addition(
        self, 
        user_input: str, 
        workflow: Optional[Dict[str, Any]], 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Handle node addition."""
        try:
            if not workflow:
                workflow = {
                    "name": "Untitled Workflow",
                    "description": "",
                    "nodes": [],
                    "edges": [],
                    "created_by": None,
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "metadata": {"session_token": session_token}
                }
            
            node_id = f"node_{len(workflow['nodes']) + 1}"
            
            # Create node with Smart City metadata
            new_node = {
                "id": node_id,
                "label": f"Process {len(workflow['nodes']) + 1}",
                "type": "process",
                "description": user_input,
                "position": {"x": 100 + len(workflow['nodes']) * 200, "y": 100},
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {"session_token": session_token}
            }
            
            workflow["nodes"].append(new_node)
            
            # Update workflow metadata
            workflow["updated_at"] = datetime.utcnow().isoformat()
            workflow["node_count"] = len(workflow["nodes"])
            
            return {
                "response": f"Node '{new_node['label']}' added: '{user_input}'. Would you like to add another node, connect nodes, review your workflow, or publish?",
                "workflow": workflow,
                "status": "node_added",
                "next_actions": ["add_node", "add_edge", "review", "publish"],
                "metadata": {
                    "node_id": node_id,
                    "total_nodes": len(workflow["nodes"]),
                    "session_token": session_token
                }
            }
            
        except Exception as e:
            self._logger.error(f"Error handling node addition: {e}")
            return {
                "response": f"Error adding node: {str(e)}",
                "workflow": workflow,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_edge_addition(
        self, 
        user_input: str, 
        workflow: Optional[Dict[str, Any]], 
        session_token: Optional[str]
    ) -> Dict[str, Any]:
        """Handle edge addition."""
        try:
            if not workflow or not workflow.get("nodes"):
                return {
                    "response": "You need to add at least two nodes before you can connect them.",
                    "workflow": workflow,
                    "status": "insufficient_nodes",
                    "next_actions": ["add_node"],
                    "metadata": {"session_token": session_token}
                }
            
            # Simple edge parsing - in practice, you'd use more sophisticated NLP
            edge_id = f"edge_{len(workflow['edges']) + 1}"
            
            # For now, connect the last two nodes
            nodes = workflow["nodes"]
            if len(nodes) >= 2:
                from_node = nodes[-2]["id"]
                to_node = nodes[-1]["id"]
                
                new_edge = {
                    "id": edge_id,
                    "from_node": from_node,
                    "to_node": to_node,
                    "label": "flows to",
                    "created_at": datetime.utcnow().isoformat(),
                    "metadata": {"session_token": session_token}
                }
                
                workflow["edges"].append(new_edge)
                workflow["updated_at"] = datetime.utcnow().isoformat()
                workflow["edge_count"] = len(workflow["edges"])
                
                return {
                    "response": f"Connected '{nodes[-2]['label']}' to '{nodes[-1]['label']}'. Would you like to add more nodes, connect more nodes, review, or publish?",
                    "workflow": workflow,
                    "status": "edge_added",
                    "next_actions": ["add_node", "add_edge", "review", "publish"],
                    "metadata": {
                        "edge_id": edge_id,
                        "total_edges": len(workflow["edges"]),
                        "session_token": session_token
                    }
                }
            else:
                return {
                    "response": "You need at least two nodes to create a connection. Let's add another node first!",
                    "workflow": workflow,
                    "status": "need_more_nodes",
                    "next_actions": ["add_node"],
                    "metadata": {"session_token": session_token}
                }
                
        except Exception as e:
            self._logger.error(f"Error handling edge addition: {e}")
            return {
                "response": f"Error adding edge: {str(e)}",
                "workflow": workflow,
                "status": "error",
                "next_actions": ["retry"],
                "metadata": {"error": str(e)}
            }
    
    async def description_to_workflow(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None, 
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert description to workflow structure."""
        try:
            return await self.parser.description_to_workflow(user_input, session_token)
        except Exception as e:
            self._logger.error(f"Error in WorkflowBuilderWizardTool.description_to_workflow: {e}")
            return {
                "name": "Error Generating Workflow",
                "description": "Failed to generate workflow from description",
                "nodes": [],
                "edges": [],
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "metadata": {"error": str(e), "session_token": session_token}
            }
    
    async def get_workflow_statistics(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the workflow."""
        try:
            return await self.statistics.get_workflow_statistics(workflow)
        except Exception as e:
            self._logger.error(f"Error getting workflow statistics: {e}")
            return {"error": str(e)}
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get information about tool capabilities and supported features."""
        return {
            "architecture": "micro-module",
            "modules": [
                "workflow_builder_ai_engine",
                "workflow_builder_parser",
                "workflow_builder_validator",
                "workflow_builder_statistics",
                "workflow_builder_formatter"
            ],
            "features": [
                "workflow_creation",
                "node_management",
                "edge_management",
                "validation_engine",
                "description_parsing",
                "statistics_analytics",
                "formatting"
            ]
        }

