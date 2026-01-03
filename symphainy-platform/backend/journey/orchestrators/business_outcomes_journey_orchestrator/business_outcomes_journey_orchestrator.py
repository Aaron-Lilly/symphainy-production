#!/usr/bin/env python3
"""
Business Outcomes Journey Orchestrator - Journey Realm

WHAT: Orchestrates business outcomes operations (roadmap generation, POC proposals)
HOW: Delegates to Journey realm services while preserving UI integration

This orchestrator is in the Journey realm and orchestrates business outcomes operations.
It extends Smart City capabilities to provide strategic planning and business value capabilities.

Architecture:
- Journey Realm: Operations orchestration
- Orchestrates Journey realm services (RoadmapGenerationService, POCGenerationService)
- Uses Smart City services (ContentSteward, DataSteward) via Curator
- Self-initializing (doesn't require BusinessOutcomesManager)
- Solution context integration for enhanced prompting
"""

import os
import sys
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class BusinessOutcomesJourneyOrchestrator(OrchestratorBase):
    """
    Business Outcomes Journey Orchestrator - Journey Realm
    
    Orchestrates business outcomes operations:
    - Pillar summary compilation
    - Strategic roadmap generation
    - POC proposal generation
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to Journey realm services.
    
    Key Principles:
    - Journey Realm: Operations orchestration
    - Orchestrates Journey realm services (RoadmapGenerationService, POCGenerationService)
    - Uses Smart City services (ContentSteward, DataSteward) via Curator
    - Self-initializing (doesn't require BusinessOutcomesManager)
    - Solution context integration for enhanced prompting
    """
    
    def __init__(self, platform_gateway, di_container):
        """
        Initialize Business Outcomes Journey Orchestrator.
        
        Args:
            platform_gateway: Platform Gateway instance
            di_container: DI Container instance
        """
        # Self-initializing - doesn't require BusinessOutcomesManager
        super().__init__(
            service_name="BusinessOutcomesJourneyOrchestratorService",
            realm_name="journey",  # ✅ Journey realm
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        # Set a shorter orchestrator name for MVP UI compatibility
        self.orchestrator_name = "BusinessOutcomesJourneyOrchestrator"
        
        # Journey realm services (lazy initialization - created on first use)
        self._roadmap_generation_service = None
        self._poc_generation_service = None
        self._metrics_calculator_service = None
        
        # Agents (lazy initialization)
        self._business_outcomes_specialist_agent = None
        self._business_outcomes_liaison_agent = None
        
        # MVP Journey Orchestrator (for solution context)
        self._mvp_journey_orchestrator = None
    
    async def _get_roadmap_generation_service(self):
        """Lazy initialization of Roadmap Generation Service (Journey realm service)."""
        if self._roadmap_generation_service is None:
            try:
                # Try to get via Curator first
                roadmap_service = await self.get_enabling_service("RoadmapGenerationService")
                if roadmap_service:
                    self._roadmap_generation_service = roadmap_service
                    self.logger.info("✅ Roadmap Generation Service discovered via Curator")
                    return roadmap_service
                
                # Fallback: Import and initialize directly
                self.logger.warning("⚠️ Roadmap Generation Service not found via Curator, initializing directly")
                from backend.journey.services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
                
                self._roadmap_generation_service = RoadmapGenerationService(
                    service_name="RoadmapGenerationService",
                    realm_name="journey",  # ✅ Journey realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._roadmap_generation_service.initialize()
                self.logger.info("✅ Roadmap Generation Service initialized (Journey realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Roadmap Generation Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._roadmap_generation_service
    
    async def _get_poc_generation_service(self):
        """Lazy initialization of POC Generation Service (Journey realm service)."""
        if self._poc_generation_service is None:
            try:
                # Try to get via Curator first
                poc_service = await self.get_enabling_service("POCGenerationService")
                if poc_service:
                    self._poc_generation_service = poc_service
                    self.logger.info("✅ POC Generation Service discovered via Curator")
                    return poc_service
                
                # Fallback: Import and initialize directly
                self.logger.warning("⚠️ POC Generation Service not found via Curator, initializing directly")
                from backend.journey.services.poc_generation_service.poc_generation_service import POCGenerationService
                
                self._poc_generation_service = POCGenerationService(
                    service_name="POCGenerationService",
                    realm_name="journey",  # ✅ Journey realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._poc_generation_service.initialize()
                self.logger.info("✅ POC Generation Service initialized (Journey realm)")
                
            except Exception as e:
                self.logger.error(f"❌ POC Generation Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._poc_generation_service
    
    async def _get_metrics_calculator_service(self):
        """Lazy initialization of Metrics Calculator Service."""
        if self._metrics_calculator_service is None:
            try:
                metrics_service = await self.get_enabling_service("MetricsCalculatorService")
                if metrics_service:
                    self._metrics_calculator_service = metrics_service
                    self.logger.info("✅ Metrics Calculator Service discovered via Curator")
                    return metrics_service
            except Exception as e:
                self.logger.warning(f"⚠️ Metrics Calculator Service not available: {e}")
        return self._metrics_calculator_service
    
    async def _get_business_outcomes_specialist_agent(self):
        """Lazy initialization of Business Outcomes Specialist Agent."""
        if self._business_outcomes_specialist_agent is None:
            try:
                from backend.journey.orchestrators.business_outcomes_journey_orchestrator.agents.business_outcomes_specialist_agent import BusinessOutcomesSpecialistAgent
                
                # Initialize agent using OrchestratorBase helper
                self._business_outcomes_specialist_agent = await self.initialize_agent(
                    BusinessOutcomesSpecialistAgent,
                    "BusinessOutcomesSpecialistAgent",
                    agent_type="specialist",
                    capabilities=["strategic_planning", "business_value_analysis", "roadmap_generation", "poc_proposal_generation"],
                    required_roles=["specialist_agent"]
                )
                
                if self._business_outcomes_specialist_agent:
                    self.logger.info("✅ Business Outcomes Specialist Agent initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Business Outcomes Specialist Agent initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._business_outcomes_specialist_agent
    
    async def _get_mvp_journey_orchestrator(self):
        """Get MVP Journey Orchestrator for solution context retrieval."""
        if self._mvp_journey_orchestrator is None:
            try:
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                    if mvp_orchestrator:
                        self._mvp_journey_orchestrator = mvp_orchestrator
                        return mvp_orchestrator
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover MVPJourneyOrchestratorService: {e}")
        return self._mvp_journey_orchestrator
    
    # ========================================================================
    # SAGA INTEGRATION (Capability by Design, Optional by Policy)
    # ========================================================================
    
    async def _get_policy_configuration_service(self):
        """Lazy initialization of Policy Configuration Service."""
        if not hasattr(self, '_policy_config_service') or self._policy_config_service is None:
            try:
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    self._policy_config_service = await curator.discover_service_by_name("PolicyConfigurationService")
                    if self._policy_config_service:
                        self.logger.info("✅ Discovered PolicyConfigurationService")
            except Exception as e:
                self.logger.warning(f"⚠️ PolicyConfigurationService not available: {e}")
                self._policy_config_service = None
        
        return self._policy_config_service
    
    async def _get_saga_policy(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get Saga policy from PolicyConfigurationService.
        
        Merges policy from service with orchestrator-specific compensation handlers.
        
        Args:
            user_context: Optional user context
        
        Returns:
            Dict with Saga policy (enable_saga, saga_operations, compensation_handlers)
        """
        # Get Policy Configuration Service
        policy_service = await self._get_policy_configuration_service()
        
        if policy_service:
            try:
                # Get policy from service
                policy_result = await policy_service.get_saga_policy(
                    orchestrator_name=self.service_name,
                    user_context=user_context
                )
                
                if policy_result.get("success"):
                    policy = policy_result.get("policy", {})
                    # Merge compensation handlers from orchestrator
                    policy["compensation_handlers"] = self._get_compensation_handlers()
                    return policy
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Saga policy from PolicyConfigurationService: {e}")
        
        # Fallback to ConfigAdapter if PolicyConfigurationService not available
        config_adapter = self._get_config_adapter()
        saga_enabled_str = config_adapter.get("SAGA_ENABLED", "false")
        saga_enabled = saga_enabled_str.lower() == "true" if isinstance(saga_enabled_str, str) else bool(saga_enabled_str)
        saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "business_outcomes_roadmap_generation,business_outcomes_poc_proposal")
        saga_operations = saga_operations_str.split(",") if isinstance(saga_operations_str, str) else []
        
        return {
            "enable_saga": saga_enabled,
            "saga_operations": [op.strip() for op in saga_operations],
            "compensation_handlers": self._get_compensation_handlers()
        }
    
    async def _saga_enabled(self, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if Saga is enabled via policy.
        
        ⭐ CAPABILITY BY DESIGN, OPTIONAL BY POLICY:
        - Saga capability is built into the architecture
        - Enabled/disabled via policy configuration
        - Default: disabled (no overhead)
        
        Args:
            user_context: Optional user context for policy retrieval
        
        Returns:
            bool indicating if Saga is enabled
        """
        # Get policy (cached or fresh)
        if not hasattr(self, '_saga_policy') or self._saga_policy is None:
            self._saga_policy = await self._get_saga_policy(user_context)
        
        return self._saga_policy.get("enable_saga", False)
    
    def _get_compensation_handlers(self) -> Dict[str, Dict[str, str]]:
        """
        Get compensation handlers for this orchestrator's operations.
        
        Returns:
            Dict mapping operation -> milestone -> compensation_handler
        """
        return {
            "business_outcomes_roadmap_generation": {
                "analyze_pillar_outputs": "clear_analysis_cache",
                "identify_opportunities": "revert_opportunity_identification",
                "generate_roadmap_structure": "delete_roadmap_draft",
                "apply_business_logic": "revert_business_analysis",
                "store_roadmap": "delete_stored_roadmap"
            },
            "business_outcomes_poc_proposal": {
                "analyze_requirements": "clear_requirements_cache",
                "calculate_financials": "revert_financial_calculations",
                "assess_risk": "revert_risk_assessment",
                "generate_poc_structure": "delete_poc_draft",
                "store_poc": "delete_stored_poc"
            }
        }
    
    async def _get_saga_journey_orchestrator(self):
        """Lazy initialization of Saga Journey Orchestrator."""
        if not hasattr(self, '_saga_orchestrator') or self._saga_orchestrator is None:
            try:
                curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
                if curator:
                    self._saga_orchestrator = await curator.discover_service_by_name("SagaJourneyOrchestratorService")
                    if self._saga_orchestrator:
                        self.logger.info("✅ Discovered SagaJourneyOrchestratorService")
            except Exception as e:
                self.logger.warning(f"⚠️ SagaJourneyOrchestratorService not available: {e}")
                self._saga_orchestrator = None
        
        return self._saga_orchestrator
    
    async def _execute_with_saga(
        self,
        operation: str,
        workflow_func,
        milestones: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow with Saga guarantees if enabled by policy.
        
        Pattern: "Capability by Design, Optional by Policy"
        
        Args:
            operation: Operation name (e.g., "business_outcomes_roadmap_generation")
            workflow_func: Async function that executes the workflow
            milestones: List of milestone names for this operation
            user_context: Optional user context
        
        Returns:
            Dict with workflow result, including saga_id if Saga was used
        """
        # Get policy if not cached
        if not hasattr(self, '_saga_policy') or self._saga_policy is None:
            self._saga_policy = await self._get_saga_policy(user_context)
        
        if not await self._saga_enabled(user_context):
            # Execute without Saga (normal flow)
            return await workflow_func()
        
        if operation not in self._saga_policy.get("saga_operations", []):
            # Execute without Saga (operation not in policy)
            return await workflow_func()
        
        # Get Saga Journey Orchestrator
        saga_orchestrator = await self._get_saga_journey_orchestrator()
        if not saga_orchestrator:
            self.logger.warning("⚠️ Saga Journey Orchestrator not available, executing without Saga")
            return await workflow_func()
        
        # Get compensation handlers for this operation
        compensation_handlers = self._saga_policy.get("compensation_handlers", {}).get(operation, {})
        
        # Design Saga journey
        saga_journey = await saga_orchestrator.design_saga_journey(
            journey_type=operation,
            requirements={
                "operation": operation,
                "milestones": milestones
            },
            compensation_handlers=compensation_handlers,
            user_context=user_context
        )
        
        if not saga_journey.get("success"):
            self.logger.warning(f"⚠️ Saga journey design failed: {saga_journey.get('error')}, executing without Saga")
            return await workflow_func()
        
        # Execute Saga journey
        saga_execution = await saga_orchestrator.execute_saga_journey(
            journey_id=saga_journey["journey_id"],
            user_id=user_context.get("user_id") if user_context else "anonymous",
            context={"operation": operation},
            user_context=user_context
        )
        
        if not saga_execution.get("success"):
            self.logger.warning(f"⚠️ Saga execution start failed: {saga_execution.get('error')}, executing without Saga")
            return await workflow_func()
        
        saga_id = saga_execution["saga_id"]
        
        # Execute workflow as Saga milestone
        try:
            result = await workflow_func()
            
            # Advance Saga step (success)
            await saga_orchestrator.advance_saga_step(
                saga_id=saga_id,
                journey_id=saga_journey["journey_id"],
                user_id=user_context.get("user_id") if user_context else "anonymous",
                step_result={"status": "complete", **result},
                user_context=user_context
            )
            
            result["saga_id"] = saga_id
            return result
            
        except Exception as e:
            # Advance Saga step (failure) - triggers automatic compensation
            await saga_orchestrator.advance_saga_step(
                saga_id=saga_id,
                journey_id=saga_journey["journey_id"],
                user_id=user_context.get("user_id") if user_context else "anonymous",
                step_result={"status": "failed", "error": str(e)},
                user_context=user_context
            )
            raise
    
    async def compile_pillar_summaries(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compile summaries from all pillars.
        
        Flow:
        1. Get Content pillar summary (via DataSolutionOrchestrator)
        2. Get Insights pillar summary (via InsightsSolutionOrchestrator)
        3. Get Operations pillar summary (via OperationsSolutionOrchestrator)
        4. Compile into unified summary with solution context
        """
        # Get solution context
        mvp_orchestrator = await self._get_mvp_journey_orchestrator()
        solution_context = None
        if mvp_orchestrator:
            try:
                solution_context = await mvp_orchestrator.get_solution_context(session_id)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get solution context: {e}")
        
        # Note: Pillar summaries are compiled by BusinessOutcomesSolutionOrchestratorService
        # This method is kept for Journey Orchestrator interface compatibility
        # In practice, the Solution Orchestrator handles the compilation
        
        return {
            "success": True,
            "message": "Pillar summaries should be compiled via BusinessOutcomesSolutionOrchestratorService",
            "solution_context": solution_context
        }
    
    async def execute_roadmap_generation_workflow(
        self,
        pillar_summaries: Dict[str, Any],
        roadmap_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute roadmap generation with solution context and optional Saga guarantees.
        
        ⭐ KEY STRATEGIC FEATURE: Demonstrate how platform creates solutions.
        
        Flow:
        1. Execute with Saga if enabled (Capability by Design, Optional by Policy)
        2. Get solution context for enhanced prompting
        3. Get Business Outcomes Specialist Agent
        4. Agent does critical reasoning first (agentic-forward pattern)
        5. Execute roadmap generation using RoadmapGenerationService
        
        Args:
            pillar_summaries: Compiled summaries from all pillars
            roadmap_options: Optional roadmap generation options
            user_context: Optional user context (includes solution_context if available)
        
        Returns:
            Dict with roadmap generation result and saga_id (if Saga was used)
        """
        # Prepare user context for Saga
        enhanced_user_context = user_context.copy() if user_context else {}
        enhanced_user_context.update({
            "pillar_summaries": pillar_summaries
        })
        
        # Define milestones for roadmap generation operation
        milestones = ["analyze_pillar_outputs", "identify_opportunities", "generate_roadmap_structure", "apply_business_logic", "store_roadmap"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="business_outcomes_roadmap_generation",
            workflow_func=lambda: self._execute_roadmap_generation_workflow_internal(
                pillar_summaries=pillar_summaries,
                roadmap_options=roadmap_options,
                user_context=enhanced_user_context
            ),
            milestones=milestones,
            user_context=enhanced_user_context
        )
    
    async def _execute_roadmap_generation_workflow_internal(
        self,
        pillar_summaries: Dict[str, Any],
        roadmap_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute roadmap generation workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            pillar_summaries: Compiled summaries from all pillars
            roadmap_options: Optional roadmap generation options
            user_context: Optional user context
        
        Returns:
            Dict with roadmap generation result
        """
        try:
            # Get solution context for enhanced prompting
            solution_context = user_context.get("solution_context") if user_context else None
            
            # Get Business Outcomes Specialist Agent
            specialist_agent = await self._get_business_outcomes_specialist_agent()
            if not specialist_agent:
                return {
                    "success": False,
                    "error": "Business Outcomes Specialist Agent not available"
                }
            
            # Agent does critical reasoning first (agentic-forward pattern)
            reasoning_result = await specialist_agent.analyze_for_strategic_roadmap(
                pillar_summaries=pillar_summaries,
                solution_context=solution_context,
                roadmap_options=roadmap_options or {},
                user_context=user_context or {}
            )
            
            if not reasoning_result.get("success"):
                return {
                    "success": False,
                    "error": "Agent reasoning failed",
                    "reasoning_error": reasoning_result.get("error")
                }
            
            roadmap_structure = reasoning_result.get("roadmap_structure", {})
            
            # Execute roadmap generation using RoadmapGenerationService
            roadmap_service = await self._get_roadmap_generation_service()
            if not roadmap_service:
                return {
                    "success": False,
                    "error": "RoadmapGenerationService not available"
                }
            
            result = await roadmap_service.generate_roadmap(
                business_context={
                    "pillar_summaries": pillar_summaries,
                    "solution_context": solution_context,
                    "roadmap_structure": roadmap_structure
                },
                options=roadmap_options,
                user_context=user_context
            )
            
            # Add agent reasoning to result
            if result.get("success"):
                result["agent_reasoning"] = reasoning_result.get("reasoning_text")
                result["roadmap_structure"] = roadmap_structure
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Roadmap generation workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_poc_proposal_generation_workflow(
        self,
        pillar_summaries: Dict[str, Any],
        poc_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute POC proposal generation with solution context.
        
        ⭐ KEY STRATEGIC FEATURE: Demonstrate how platform implements solutions.
        
        Flow:
        1. Get solution context for enhanced prompting
        2. Get Business Outcomes Specialist Agent
        3. Agent does critical reasoning first (agentic-forward pattern)
        4. Execute POC proposal generation using POCGenerationService
        
        Args:
            pillar_summaries: Compiled summaries from all pillars
            poc_options: Optional POC proposal generation options
            user_context: Optional user context (includes solution_context if available)
        
        Returns:
            Dict with POC proposal generation result
        """
        try:
            # Get solution context for enhanced prompting
            solution_context = user_context.get("solution_context") if user_context else None
            
            # Get Business Outcomes Specialist Agent
            specialist_agent = await self._get_business_outcomes_specialist_agent()
            if not specialist_agent:
                return {
                    "success": False,
                    "error": "Business Outcomes Specialist Agent not available"
                }
            
            # Agent does critical reasoning first (agentic-forward pattern)
            reasoning_result = await specialist_agent.analyze_for_poc_proposal(
                pillar_summaries=pillar_summaries,
                solution_context=solution_context,
                poc_options=poc_options or {},
                user_context=user_context or {}
            )
            
            if not reasoning_result.get("success"):
                return {
                    "success": False,
                    "error": "Agent reasoning failed",
                    "reasoning_error": reasoning_result.get("error")
                }
            
            poc_structure = reasoning_result.get("poc_structure", {})
            
            # Execute POC proposal generation using POCGenerationService
            poc_service = await self._get_poc_generation_service()
            if not poc_service:
                return {
                    "success": False,
                    "error": "POCGenerationService not available"
                }
            
            result = await poc_service.generate_poc_proposal(
                pillar_summaries=pillar_summaries,
                poc_options=poc_options,
                user_context=user_context
            )
            
            # Add agent reasoning to result
            if result.get("success"):
                result["agent_reasoning"] = reasoning_result.get("reasoning_text")
                result["poc_structure"] = poc_structure
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ POC proposal generation workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # UNIFIED SOA API → MCP TOOL PATTERN (Phase 3.2.5)
    # ============================================================================
    
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """
        Define Business Outcomes Journey Orchestrator SOA APIs.
        
        UNIFIED PATTERN: MCP Server automatically registers these as MCP Tools.
        
        Returns:
            Dict of SOA API definitions with handlers, input schemas, and descriptions
        """
        return {
            "execute_roadmap_generation_workflow": {
                "handler": self.execute_roadmap_generation_workflow,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pillar_summaries": {
                            "type": "object",
                            "description": "Compiled summaries from all pillars"
                        },
                        "roadmap_options": {
                            "type": "object",
                            "description": "Optional roadmap generation options"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes solution_context if available)"
                        }
                    },
                    "required": ["pillar_summaries"]
                },
                "description": "Execute roadmap generation with solution context and optional Saga guarantees"
            },
            "execute_poc_proposal_generation_workflow": {
                "handler": self.execute_poc_proposal_generation_workflow,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pillar_summaries": {
                            "type": "object",
                            "description": "Compiled summaries from all pillars"
                        },
                        "poc_options": {
                            "type": "object",
                            "description": "Optional POC proposal generation options"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes solution_context if available)"
                        }
                    },
                    "required": ["pillar_summaries"]
                },
                "description": "Execute POC proposal generation with solution context"
            }
        }
    
    async def _initialize_mcp_server(self):
        """
        Initialize Business Outcomes Realm MCP Server (unified pattern).
        
        MCP Server automatically registers tools from _define_soa_api_handlers().
        """
        from .mcp_server.business_outcomes_mcp_server import BusinessOutcomesMCPServer
        
        self.mcp_server = BusinessOutcomesMCPServer(
            orchestrator=self,
            di_container=self.di_container
        )
        await self.mcp_server.initialize()


