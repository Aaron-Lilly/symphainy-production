#!/usr/bin/env python3
"""
Coexistence Analysis Workflow

WHAT: Orchestrates coexistence analysis for human-AI collaboration
HOW: Agent critical reasoning + CoexistenceAnalysisService execution

This workflow implements the coexistence analysis flow:
1. Agent critical reasoning (OperationsSpecialistAgent) - analyzes current/target states
2. Coexistence blueprint generation
3. CoexistenceAnalysisService execution
4. Solution context integration for enhanced prompting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class CoexistenceAnalysisWorkflow:
    """
    Workflow for analyzing human-AI coexistence.
    
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
        coexistence_content: Dict[str, Any],
        analysis_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute coexistence analysis workflow.
        
        Args:
            coexistence_content: Coexistence content
                - current_state: Current process state
                - target_state: Target process state
                - workflow_data: Optional workflow data
                - sop_data: Optional SOP data
            analysis_options: Optional analysis options
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with analysis results, recommendations, blueprint, etc.
        """
        try:
            self.logger.info("📊 Starting coexistence analysis workflow")
            
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
            
            # Step 2: Agent critical reasoning - analyze coexistence
            self.logger.info("🤖 Agent critical reasoning: Analyzing coexistence")
            
            # Enhance context with solution context if available
            enhanced_context = (analysis_options or {}).copy()
            if user_context and user_context.get("solution_context"):
                solution_context = user_context["solution_context"]
                enhanced_context["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_context["strategic_focus"] = solution_structure.get("strategic_focus", "")
            
            # Get SOP and workflow content from coexistence_content
            sop_content = coexistence_content.get("sop_content", coexistence_content.get("current_state", {}))
            workflow_content = coexistence_content.get("workflow_content", coexistence_content.get("target_state", {}))
            
            reasoning_result = await specialist_agent.analyze_for_coexistence_structure(
                sop_content=sop_content,
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
            
            coexistence_structure = reasoning_result.get("coexistence_structure", {})
            self.logger.info("✅ Agent reasoning complete: Generated coexistence blueprint analysis")
            
            # Step 3: Execute coexistence analysis using CoexistenceAnalysisService
            coexistence_service = await self.orchestrator._get_coexistence_analysis_service()
            if not coexistence_service:
                return {
                    "success": False,
                    "error": "CoexistenceAnalysisService not available",
                    "workflow_id": workflow_id
                }
            
            self.logger.info("⚙️ Executing coexistence analysis via CoexistenceAnalysisService")
            
            # Extract SOP and workflow content
            sop_content = coexistence_content.get("sop_content", "")
            workflow_content = coexistence_content.get("workflow_content", {})
            
            # Convert sop_content to string if needed
            sop_content_str = sop_content if isinstance(sop_content, str) else str(sop_content) if sop_content else ""
            
            result = await coexistence_service.analyze_coexistence(
                coexistence_structure=coexistence_structure,
                sop_content=sop_content_str,
                workflow_content=workflow_content,
                options=analysis_options,
                user_context=user_context
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error", "Coexistence analysis failed"),
                    "workflow_id": workflow_id
                }
            
            # Step 4: Enhance result with workflow_id and agent reasoning
            result["workflow_id"] = workflow_id
            result["agent_reasoning"] = reasoning_result.get("reasoning", {})
            result["coexistence_structure"] = coexistence_structure
            
            self.logger.info(f"✅ Coexistence analysis complete: workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Coexistence analysis workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }

