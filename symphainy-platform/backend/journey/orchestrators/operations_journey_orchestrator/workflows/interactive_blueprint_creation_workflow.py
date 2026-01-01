#!/usr/bin/env python3
"""
Interactive Blueprint Creation Workflow

WHAT: Orchestrates interactive coexistence blueprint creation via conversational chat
HOW: OperationsSpecialistAgent conversational interface + blueprint generation

This workflow implements the interactive blueprint creation flow:
1. Process user chat messages
2. Agent reasoning for blueprint generation
3. Generate coexistence blueprint
4. Solution context integration for enhanced prompting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class InteractiveBlueprintCreationWorkflow:
    """
    Workflow for interactive coexistence blueprint creation.
    
    Uses OperationsSpecialistAgent for conversational interface and blueprint generation.
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
        user_message: str,
        session_token: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute interactive blueprint creation workflow.
        
        Args:
            user_message: User's chat message
            session_token: Optional session token (for multi-turn conversations)
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with response, blueprint_structure, recommendations, etc.
        """
        try:
            self.logger.info("📊 Starting interactive blueprint creation workflow")
            
            # Generate workflow ID
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            
            # Step 1: Get Operations Specialist Agent
            specialist_agent = await self.orchestrator._get_operations_specialist_agent()
            if not specialist_agent:
                return {
                    "success": False,
                    "error": "Operations Specialist Agent not available",
                    "workflow_id": workflow_id
                }
            
            # Step 2: Enhance context with solution context if available
            enhanced_context = {}
            if user_context and user_context.get("solution_context"):
                solution_context = user_context["solution_context"]
                enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
            
            # Step 3: Process user message via agent
            self.logger.info("🤖 Processing user message via Operations Specialist Agent")
            
            # Use agent's process_request for blueprint creation
            # The agent will reason about the user's message and generate blueprint recommendations
            agent_result = await specialist_agent.process_request({
                "operation": "analyze_for_coexistence_structure",
                "sop_content": {"description": user_message},  # Use user message as SOP description
                "workflow_content": {},  # Empty workflow - agent will reason about it
                "business_context": enhanced_context,
                "user_id": user_context.get("user_id", "anonymous") if user_context else "anonymous"
            })
            
            if not agent_result.get("success"):
                return {
                    "success": False,
                    "error": agent_result.get("error", "Agent processing failed"),
                    "workflow_id": workflow_id
                }
            
            # Extract blueprint structure and recommendations from agent result
            coexistence_structure = agent_result.get("coexistence_structure", {})
            reasoning = agent_result.get("reasoning", {})
            recommendations = reasoning.get("recommendations", []) if isinstance(reasoning, dict) else []
            response_message = reasoning.get("analysis", "I've analyzed your requirements and generated a coexistence blueprint.") if isinstance(reasoning, dict) else "I've analyzed your requirements and generated a coexistence blueprint."
            
            # Build blueprint structure from coexistence structure
            blueprint_structure = {
                "coexistence_structure": coexistence_structure,
                "handoff_points": coexistence_structure.get("handoff_points", []),
                "ai_augmentation_points": coexistence_structure.get("ai_augmentation_points", []),
                "collaboration_pattern": coexistence_structure.get("collaboration_pattern", "")
            }
            
            # Step 4: Build result
            result = {
                "success": True,
                "session_token": session_token or str(uuid.uuid4()),
                "message": response_message,
                "blueprint_structure": blueprint_structure,
                "recommendations": recommendations,
                "workflow_id": workflow_id,
                "agent_reasoning": agent_result.get("reasoning", "")
            }
            
            self.logger.info(f"✅ Interactive blueprint creation complete: workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive blueprint creation workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }

