#!/usr/bin/env python3
"""
Workflow to SOP Workflow

WHAT: Orchestrates workflow to SOP conversion
HOW: Agent critical reasoning + WorkflowConversionService execution

This workflow implements the workflow to SOP conversion flow:
1. Agent critical reasoning (OperationsSpecialistAgent) - analyzes workflow structure
2. SOP structure generation
3. WorkflowConversionService execution
4. Solution context integration for enhanced prompting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class WorkflowToSOPWorkflow:
    """
    Workflow for converting workflow to SOP.
    
    Uses agentic-forward pattern:
    - Agent does critical reasoning first
    - Service executes based on agent's strategic decisions
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
        workflow_content: Dict[str, Any],
        sop_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow to SOP conversion workflow.
        
        Args:
            workflow_content: Workflow content (structure from parsing)
            sop_options: Optional SOP generation options
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with SOP structure, sop_id, etc.
        """
        try:
            self.logger.info("📊 Starting workflow to SOP conversion workflow")
            
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
            
            # Step 2: Agent critical reasoning - analyze workflow for SOP structure
            self.logger.info("🤖 Agent critical reasoning: Analyzing workflow for SOP structure")
            
            # Enhance context with solution context if available
            enhanced_context = (sop_options or {}).copy()
            if user_context and user_context.get("solution_context"):
                solution_context = user_context["solution_context"]
                enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
            
            reasoning_result = await specialist_agent.analyze_for_sop_structure(
                workflow_content=workflow_content,
                context=enhanced_context,
                user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous"
            )
            
            if not reasoning_result.get("success"):
                return {
                    "success": False,
                    "error": "Agent reasoning failed",
                    "workflow_id": workflow_id,
                    "reasoning_error": reasoning_result.get("error")
                }
            
            sop_structure = reasoning_result.get("sop_structure", {})
            self.logger.info(f"✅ Agent reasoning complete: Generated SOP structure with {len(sop_structure.get('sections', []))} sections")
            
            # Step 3: Execute SOP generation using WorkflowConversionService
            workflow_service = await self.orchestrator._get_workflow_conversion_service()
            if not workflow_service:
                return {
                    "success": False,
                    "error": "WorkflowConversionService not available",
                    "workflow_id": workflow_id
                }
            
            self.logger.info("⚙️ Executing SOP generation via WorkflowConversionService")
            
            result = await workflow_service.convert_workflow_to_sop(
                workflow_content=workflow_content,
                sop_structure=sop_structure,
                options=sop_options,
                user_context=user_context
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "SOP generation failed"),
                    "workflow_id": workflow_id
                }
            
            # Step 4: Enhance result with workflow_id and metadata
            result["workflow_id"] = workflow_id
            result["agent_reasoning"] = reasoning_result.get("reasoning", "")
            result["sop_structure"] = sop_structure
            
            self.logger.info(f"✅ Workflow to SOP conversion complete: workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow to SOP conversion workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }

