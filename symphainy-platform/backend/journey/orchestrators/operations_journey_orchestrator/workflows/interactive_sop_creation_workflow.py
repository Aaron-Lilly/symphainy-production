#!/usr/bin/env python3
"""
Interactive SOP Creation Workflow

WHAT: Orchestrates interactive SOP creation via conversational chat/wizard
HOW: SOPBuilderService wizard + OperationsLiaisonAgent conversational interface

This workflow implements the interactive SOP creation flow:
1. Start wizard session (if action="start")
2. Process chat messages (if action="chat")
3. Publish SOP (if action="publish")
4. Solution context integration for enhanced prompting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class InteractiveSOPCreationWorkflow:
    """
    Workflow for interactive SOP creation.
    
    Combines:
    - SOPBuilderService wizard for structured SOP creation
    - OperationsLiaisonAgent for conversational interface
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: OperationsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        action: str,
        user_message: Optional[str] = None,
        session_token: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute interactive SOP creation workflow.
        
        Args:
            action: Action type ("start", "chat", "publish")
            user_message: User's chat message (for "chat" action)
            session_token: Session token for SOP creation wizard
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with response, session_token, sop_structure, etc.
        """
        try:
            self.logger.info(f"📊 Starting interactive SOP creation workflow: action={action}")
            
            # Generate workflow ID
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            
            # Step 1: Get SOP Builder Service
            sop_service = await self.orchestrator._get_sop_builder_service()
            if not sop_service:
                return {
                    "success": False,
                    "error": "SOPBuilderService not available",
                    "workflow_id": workflow_id
                }
            
            # Step 2: Get Operations Liaison Agent (for conversational interface)
            liaison_agent = await self.orchestrator._get_operations_liaison_agent()
            
            # Step 3: Handle action
            if action == "start":
                # Start wizard session
                self.logger.info("🚀 Starting SOP creation wizard session")
                
                # Enhance context with solution context if available
                enhanced_context = {}
                if user_context and user_context.get("solution_context"):
                    solution_context = user_context["solution_context"]
                    enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                    solution_structure = solution_context.get("solution_structure", {})
                    enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
                
                # Start wizard via SOPBuilderService
                wizard_result = await sop_service.start_wizard_session(
                    user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous",
                    context=enhanced_context
                )
                
                if not wizard_result.get("success"):
                    return {
                        "success": False,
                        "error": wizard_result.get("error", "Failed to start wizard session"),
                        "workflow_id": workflow_id
                    }
                
                session_token = wizard_result.get("session_token")
                
                # Get initial guidance from liaison agent
                if liaison_agent:
                    try:
                        guidance = await liaison_agent.process_message(
                            message="I want to create a new SOP. Can you guide me through the process?",
                            context={
                                "session_token": session_token,
                                "action": "start_sop_creation",
                                **enhanced_context
                            },
                            user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                        )
                        initial_message = guidance.get("response", "Welcome! Let's create your SOP together.")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Liaison agent guidance failed: {e}")
                        initial_message = "Welcome! Let's create your SOP together. I'll guide you through the process."
                else:
                    initial_message = "Welcome! Let's create your SOP together. I'll guide you through the process."
                
                return {
                    "success": True,
                    "session_token": session_token,
                    "message": initial_message,
                    "workflow_id": workflow_id,
                    "wizard_state": wizard_result.get("wizard_state", {})
                }
            
            elif action == "chat":
                # Process chat message
                if not user_message:
                    return {
                        "success": False,
                        "error": "User message is required for chat action",
                        "workflow_id": workflow_id
                    }
                
                if not session_token:
                    return {
                        "success": False,
                        "error": "Session token is required for chat action",
                        "workflow_id": workflow_id
                    }
                
                self.logger.info(f"💬 Processing chat message: session_token={session_token}")
                
                # Enhance context with solution context if available
                enhanced_context = {}
                if user_context and user_context.get("solution_context"):
                    solution_context = user_context["solution_context"]
                    enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                    solution_structure = solution_context.get("solution_structure", {})
                    enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
                
                # Process via liaison agent (conversational) or wizard (structured)
                # Try liaison agent first for natural conversation
                if liaison_agent:
                    try:
                        agent_response = await liaison_agent.process_message(
                            message=user_message,
                            context={
                                "session_token": session_token,
                                "action": "sop_creation_chat",
                                **enhanced_context
                            },
                            user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
                        )
                        
                        response_message = agent_response.get("response", "")
                        
                        # If agent suggests wizard step, process via wizard
                        if agent_response.get("suggest_wizard_step"):
                            wizard_result = await sop_service.process_wizard_step(
                                session_token=session_token,
                                user_input=user_message,
                                user_context=user_context
                            )
                            if wizard_result.get("success"):
                                response_message = wizard_result.get("response", response_message)
                        
                        return {
                            "success": True,
                            "session_token": session_token,
                            "message": response_message,
                            "workflow_id": workflow_id,
                            "wizard_state": agent_response.get("wizard_state")
                        }
                    except Exception as e:
                        self.logger.warning(f"⚠️ Liaison agent processing failed, falling back to wizard: {e}")
                
                # Fallback: Process via wizard directly
                wizard_result = await sop_service.process_wizard_step(
                    session_token=session_token,
                    user_input=user_message,
                    user_context=user_context
                )
                
                if not wizard_result.get("success"):
                    return {
                        "success": False,
                        "error": wizard_result.get("error", "Failed to process wizard step"),
                        "workflow_id": workflow_id
                    }
                
                return {
                    "success": True,
                    "session_token": session_token,
                    "message": wizard_result.get("response", ""),
                    "workflow_id": workflow_id,
                    "wizard_state": wizard_result.get("wizard_state", {})
                }
            
            elif action == "publish":
                # Publish SOP
                if not session_token:
                    return {
                        "success": False,
                        "error": "Session token is required for publish action",
                        "workflow_id": workflow_id
                    }
                
                self.logger.info(f"📝 Publishing SOP: session_token={session_token}")
                
                # Complete wizard and generate SOP
                wizard_result = await sop_service.complete_wizard(
                    session_token=session_token,
                    user_context=user_context
                )
                
                if not wizard_result.get("success"):
                    return {
                        "success": False,
                        "error": wizard_result.get("error", "Failed to complete wizard"),
                        "workflow_id": workflow_id
                    }
                
                sop_structure = wizard_result.get("sop_structure", {})
                sop_id = wizard_result.get("sop_id")
                
                return {
                    "success": True,
                    "sop_id": sop_id,
                    "sop_structure": sop_structure,
                    "workflow_id": workflow_id,
                    "message": "SOP created successfully!"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "workflow_id": workflow_id
                }
            
        except Exception as e:
            self.logger.error(f"❌ Interactive SOP creation workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }









