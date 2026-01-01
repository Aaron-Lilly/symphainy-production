#!/usr/bin/env python3
"""
SOP to Workflow Workflow

WHAT: Orchestrates SOP to workflow conversion
HOW: Agent critical reasoning + WorkflowConversionService execution

This workflow implements the SOP to workflow conversion flow:
1. Agent critical reasoning (OperationsSpecialistAgent) - analyzes SOP structure
2. Workflow structure generation
3. WorkflowConversionService execution
4. Solution context integration for enhanced prompting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class SOPToWorkflowWorkflow:
    """
    Workflow for converting SOP to workflow.
    
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
        sop_content: Dict[str, Any],
        workflow_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute SOP to workflow conversion workflow.
        
        Args:
            sop_content: SOP content (structure from parsing)
            workflow_options: Optional workflow generation options
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with workflow structure, workflow_id, etc.
        """
        try:
            self.logger.info("📊 Starting SOP to workflow conversion workflow")
            
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
            
            # Step 2: Agent critical reasoning - analyze SOP for workflow structure
            self.logger.info("🤖 Agent critical reasoning: Analyzing SOP for workflow structure")
            
            # Enhance context with solution context if available
            enhanced_context = (workflow_options or {}).copy()
            if user_context and user_context.get("solution_context"):
                solution_context = user_context["solution_context"]
                enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
            
            reasoning_result = await specialist_agent.analyze_process_for_workflow_structure(
                process_content=sop_content,
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
            
            workflow_structure = reasoning_result.get("workflow_structure", {})
            self.logger.info(f"✅ Agent reasoning complete: Generated workflow structure with {len(workflow_structure.get('nodes', []))} nodes")
            
            # Step 3: Execute workflow generation using WorkflowConversionService
            workflow_service = await self.orchestrator._get_workflow_conversion_service()
            if not workflow_service:
                return {
                    "success": False,
                    "error": "WorkflowConversionService not available",
                    "workflow_id": workflow_id
                }
            
            self.logger.info("⚙️ Executing workflow generation via WorkflowConversionService")
            
            result = await workflow_service.convert_sop_to_workflow(
                workflow_structure=workflow_structure,
                sop_content=sop_content,
                options=workflow_options,
                user_context=user_context
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Workflow generation failed"),
                    "workflow_id": workflow_id
                }
            
            # Step 4: Enhance result with workflow_id and metadata
            result["workflow_id"] = workflow_id
            result["agent_reasoning"] = reasoning_result.get("reasoning", "")
            result["workflow_structure"] = workflow_structure
            
            self.logger.info(f"✅ SOP to workflow conversion complete: workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ SOP to workflow conversion workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }


