#!/usr/bin/env python3
"""
Operations Journey Orchestrator - Journey Realm

WHAT: Orchestrates operations operations (SOP/workflow conversion, coexistence analysis)
HOW: Delegates to Journey realm services while preserving UI integration

This orchestrator is in the Journey realm and orchestrates operations operations.
It extends Smart City capabilities to provide operations management capabilities.

Architecture:
- Journey Realm: Operations orchestration
- Orchestrates Journey realm services (WorkflowConversionService, SOPBuilderService, CoexistenceAnalysisService)
- Uses Smart City services (ContentSteward, DataSteward) via Curator
- Self-initializing (doesn't require OperationsManager)
"""

import os
import sys
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class OperationsJourneyOrchestrator(OrchestratorBase):
    """
    Operations Journey Orchestrator - Journey Realm
    
    Orchestrates operations operations:
    - SOP to Workflow conversion
    - Workflow to SOP conversion
    - Coexistence analysis
    - Interactive SOP creation
    - Interactive blueprint creation
    - AI-optimized blueprint generation
    
    Extends OrchestratorBase for Smart City access and orchestrator capabilities.
    Preserves MVP UI integration while delegating to Journey realm services.
    
    Key Principles:
    - Journey Realm: Operations orchestration
    - Orchestrates Journey realm services (WorkflowConversionService, SOPBuilderService, CoexistenceAnalysisService)
    - Uses Smart City services (ContentSteward, DataSteward) via Curator
    - Self-initializing (doesn't require OperationsManager)
    - Solution context integration for enhanced prompting
    """
    
    def __init__(self, platform_gateway, di_container):
        """
        Initialize Operations Journey Orchestrator.
        
        Args:
            platform_gateway: Platform Gateway instance
            di_container: DI Container instance
        """
        # Self-initializing - doesn't require OperationsManager
        super().__init__(
            service_name="OperationsJourneyOrchestratorService",
            realm_name="journey",  # ✅ Journey realm
            platform_gateway=platform_gateway,
            di_container=di_container
        )
        # Set a shorter orchestrator name for MVP UI compatibility
        self.orchestrator_name = "OperationsJourneyOrchestrator"
        
        # Journey realm services (lazy initialization - created on first use)
        self._workflow_conversion_service = None
        self._sop_builder_service = None
        self._coexistence_analysis_service = None
        
        # Agents (lazy initialization)
        self._operations_specialist_agent = None
        self._operations_liaison_agent = None
        
        # Workflows (lazy initialization)
        self._sop_to_workflow_workflow = None
        self._workflow_to_sop_workflow = None
        self._coexistence_analysis_workflow = None
        self._interactive_sop_creation_workflow = None
        self._interactive_blueprint_creation_workflow = None
        self._ai_optimized_blueprint_workflow = None
        self._workflow_visualization_workflow = None
        self._sop_visualization_workflow = None
        
        # MVP Journey Orchestrator (for solution context)
        self._mvp_journey_orchestrator = None
    
    async def _get_workflow_conversion_service(self):
        """Lazy initialization of Workflow Conversion Service (Journey realm service)."""
        if self._workflow_conversion_service is None:
            try:
                # Try to get via Curator first
                workflow_service = await self.get_enabling_service("WorkflowConversionService")
                if workflow_service:
                    self._workflow_conversion_service = workflow_service
                    self.logger.info("✅ Workflow Conversion Service discovered via Curator")
                    return workflow_service
                
                # Fallback: Import and initialize directly
                self.logger.warning("⚠️ Workflow Conversion Service not found via Curator, initializing directly")
                from backend.journey.services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
                
                self._workflow_conversion_service = WorkflowConversionService(
                    service_name="WorkflowConversionService",
                    realm_name="journey",  # ✅ Journey realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._workflow_conversion_service.initialize()
                self.logger.info("✅ Workflow Conversion Service initialized (Journey realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Workflow Conversion Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._workflow_conversion_service
    
    async def _get_sop_builder_service(self):
        """Lazy initialization of SOP Builder Service (Journey realm service)."""
        if self._sop_builder_service is None:
            try:
                # Try to get via Curator first
                sop_service = await self.get_enabling_service("SOPBuilderService")
                if sop_service:
                    self._sop_builder_service = sop_service
                    self.logger.info("✅ SOP Builder Service discovered via Curator")
                    return sop_service
                
                # Fallback: Import and initialize directly
                self.logger.warning("⚠️ SOP Builder Service not found via Curator, initializing directly")
                from backend.journey.services.sop_builder_service.sop_builder_service import SOPBuilderService
                
                self._sop_builder_service = SOPBuilderService(
                    service_name="SOPBuilderService",
                    realm_name="journey",  # ✅ Journey realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._sop_builder_service.initialize()
                self.logger.info("✅ SOP Builder Service initialized (Journey realm)")
                
            except Exception as e:
                self.logger.error(f"❌ SOP Builder Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._sop_builder_service
    
    async def _get_coexistence_analysis_service(self):
        """Lazy initialization of Coexistence Analysis Service (Journey realm service)."""
        if self._coexistence_analysis_service is None:
            try:
                # Try to get via Curator first
                coexistence_service = await self.get_enabling_service("CoexistenceAnalysisService")
                if coexistence_service:
                    self._coexistence_analysis_service = coexistence_service
                    self.logger.info("✅ Coexistence Analysis Service discovered via Curator")
                    return coexistence_service
                
                # Fallback: Import and initialize directly
                self.logger.warning("⚠️ Coexistence Analysis Service not found via Curator, initializing directly")
                from backend.journey.services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
                
                self._coexistence_analysis_service = CoexistenceAnalysisService(
                    service_name="CoexistenceAnalysisService",
                    realm_name="journey",  # ✅ Journey realm service
                    platform_gateway=self.platform_gateway,
                    di_container=self.di_container
                )
                await self._coexistence_analysis_service.initialize()
                self.logger.info("✅ Coexistence Analysis Service initialized (Journey realm)")
                
            except Exception as e:
                self.logger.error(f"❌ Coexistence Analysis Service initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._coexistence_analysis_service
    
    async def _get_operations_specialist_agent(self):
        """Lazy initialization of Operations Specialist Agent."""
        if self._operations_specialist_agent is None:
            try:
                # Try to get via Curator first
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    # Try to discover agent via Curator
                    agent = await curator.discover_service_by_name("OperationsSpecialistAgent")
                    if agent:
                        self._operations_specialist_agent = agent
                        self.logger.info("✅ Operations Specialist Agent discovered via Curator")
                        return agent
                
                # Fallback: Initialize using OrchestratorBase helper (via Agentic Foundation factory)
                self.logger.info("🔄 Operations Specialist Agent not found via Curator, initializing via factory")
                from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.agents.operations_specialist_agent import OperationsSpecialistAgent
                from backend.business_enablement.protocols.business_specialist_agent_protocol import SpecialistCapability
                
                agent = await self.initialize_agent(
                    OperationsSpecialistAgent,
                    "OperationsSpecialistAgent",
                    agent_type="specialist",
                    capabilities=[
                        "workflow_design",
                        "sop_creation",
                        "coexistence_analysis",
                        "process_optimization",
                        "blueprint_generation"
                    ],
                    required_roles=[],
                    specialist_capability=SpecialistCapability.PROCESS_OPTIMIZATION
                )
                
                if agent:
                    self._operations_specialist_agent = agent
                    # Give specialist agent access to orchestrator (for MCP server access)
                    if hasattr(agent, 'set_orchestrator'):
                        agent.set_orchestrator(self)
                    self.logger.info("✅ Operations Specialist Agent initialized via factory")
                    return agent
                else:
                    self.logger.error("❌ Failed to initialize Operations Specialist Agent via factory")
                    return None
                
            except Exception as e:
                self.logger.error(f"❌ Operations Specialist Agent initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._operations_specialist_agent
    
    async def _get_operations_liaison_agent(self):
        """Lazy initialization of Operations Liaison Agent."""
        if self._operations_liaison_agent is None:
            try:
                # Try to get via Curator first
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    agent = await curator.discover_service_by_name("OperationsLiaisonAgent")
                    if agent:
                        self._operations_liaison_agent = agent
                        self.logger.info("✅ Operations Liaison Agent discovered via Curator")
                        return agent
                
                # Fallback: Initialize using OrchestratorBase helper (via Agentic Foundation factory)
                self.logger.info("🔄 Operations Liaison Agent not found via Curator, initializing via factory")
                from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.agents.operations_liaison_agent import OperationsLiaisonAgent
                
                agent = await self.initialize_agent(
                    OperationsLiaisonAgent,
                    "OperationsLiaisonAgent",
                    agent_type="liaison",
                    capabilities=[
                        "sop_creation_guidance",
                        "workflow_design_help",
                        "coexistence_analysis_support",
                        "blueprint_creation_assistance"
                    ],
                    required_roles=[]
                )
                
                if agent:
                    self._operations_liaison_agent = agent
                    # Set pillar for this liaison agent
                    if hasattr(agent, 'pillar'):
                        agent.pillar = "operations"
                    self.logger.info("✅ Operations Liaison Agent initialized via factory")
                    return agent
                else:
                    self.logger.error("❌ Failed to initialize Operations Liaison Agent via factory")
                    # Note: No fallback - factory initialization is the only supported path
                    # Direct initialization would require full SDK setup which is not recommended
                    return None
                
            except Exception as e:
                self.logger.error(f"❌ Operations Liaison Agent initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._operations_liaison_agent
    
    async def _get_mvp_journey_orchestrator(self):
        """Get MVP Journey Orchestrator for solution context."""
        if self._mvp_journey_orchestrator is None:
            try:
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                    if mvp_orchestrator:
                        self._mvp_journey_orchestrator = mvp_orchestrator
                        self.logger.info("✅ MVP Journey Orchestrator discovered via Curator")
                        return mvp_orchestrator
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover MVP Journey Orchestrator: {e}")
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
        saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "operations_sop_to_workflow,operations_coexistence_analysis")
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
            "operations_sop_to_workflow": {
                "extract_sop_structure": "revert_sop_parsing",
                "analyze_workflow_requirements": "clear_analysis_cache",
                "generate_workflow": "delete_workflow_draft",
                "validate_workflow": "mark_workflow_as_invalid",
                "store_workflow": "delete_stored_workflow"
            },
            "operations_coexistence_analysis": {
                "fetch_sop_content": "clear_sop_cache",
                "fetch_workflow_content": "clear_workflow_cache",
                "analyze_coexistence": "revert_analysis",
                "generate_blueprint": "delete_blueprint_draft",
                "store_blueprint": "delete_stored_blueprint"
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
            operation: Operation name (e.g., "operations_sop_to_workflow")
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
    
    async def _get_sop_to_workflow_workflow(self):
        """Lazy initialization of SOP to Workflow Workflow."""
        if self._sop_to_workflow_workflow is None:
            try:
                from .workflows.sop_to_workflow_workflow import SOPToWorkflowWorkflow
                
                self._sop_to_workflow_workflow = SOPToWorkflowWorkflow(self)
                self.logger.info("✅ SOP to Workflow Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ SOP to Workflow Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._sop_to_workflow_workflow
    
    async def _get_workflow_to_sop_workflow(self):
        """Lazy initialization of Workflow to SOP Workflow."""
        if self._workflow_to_sop_workflow is None:
            try:
                from .workflows.workflow_to_sop_workflow import WorkflowToSOPWorkflow
                
                self._workflow_to_sop_workflow = WorkflowToSOPWorkflow(self)
                self.logger.info("✅ Workflow to SOP Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Workflow to SOP Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._workflow_to_sop_workflow
    
    async def _get_coexistence_analysis_workflow(self):
        """Lazy initialization of Coexistence Analysis Workflow."""
        if self._coexistence_analysis_workflow is None:
            try:
                from .workflows.coexistence_analysis_workflow import CoexistenceAnalysisWorkflow
                
                self._coexistence_analysis_workflow = CoexistenceAnalysisWorkflow(self)
                self.logger.info("✅ Coexistence Analysis Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Coexistence Analysis Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._coexistence_analysis_workflow
    
    async def _get_interactive_sop_creation_workflow(self):
        """Lazy initialization of Interactive SOP Creation Workflow."""
        if self._interactive_sop_creation_workflow is None:
            try:
                from .workflows.interactive_sop_creation_workflow import InteractiveSOPCreationWorkflow
                
                self._interactive_sop_creation_workflow = InteractiveSOPCreationWorkflow(self)
                self.logger.info("✅ Interactive SOP Creation Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Interactive SOP Creation Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._interactive_sop_creation_workflow
    
    async def _get_interactive_blueprint_creation_workflow(self):
        """Lazy initialization of Interactive Blueprint Creation Workflow."""
        if self._interactive_blueprint_creation_workflow is None:
            try:
                from .workflows.interactive_blueprint_creation_workflow import InteractiveBlueprintCreationWorkflow
                
                self._interactive_blueprint_creation_workflow = InteractiveBlueprintCreationWorkflow(self)
                self.logger.info("✅ Interactive Blueprint Creation Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Interactive Blueprint Creation Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._interactive_blueprint_creation_workflow
    
    async def _get_ai_optimized_blueprint_workflow(self):
        """Lazy initialization of AI-Optimized Blueprint Workflow."""
        if self._ai_optimized_blueprint_workflow is None:
            try:
                from .workflows.ai_optimized_blueprint_workflow import AIOptimizedBlueprintWorkflow
                
                self._ai_optimized_blueprint_workflow = AIOptimizedBlueprintWorkflow(self)
                self.logger.info("✅ AI-Optimized Blueprint Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ AI-Optimized Blueprint Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._ai_optimized_blueprint_workflow
    
    async def _get_workflow_visualization_workflow(self):
        """Lazy initialization of Workflow Visualization Workflow."""
        if self._workflow_visualization_workflow is None:
            try:
                from .workflows.workflow_visualization_workflow import WorkflowVisualizationWorkflow
                
                self._workflow_visualization_workflow = WorkflowVisualizationWorkflow(self)
                self.logger.info("✅ Workflow Visualization Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ Workflow Visualization Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._workflow_visualization_workflow
    
    async def _get_sop_visualization_workflow(self):
        """Lazy initialization of SOP Visualization Workflow."""
        if self._sop_visualization_workflow is None:
            try:
                from .workflows.sop_visualization_workflow import SOPVisualizationWorkflow
                
                self._sop_visualization_workflow = SOPVisualizationWorkflow(self)
                self.logger.info("✅ SOP Visualization Workflow initialized")
                
            except Exception as e:
                self.logger.error(f"❌ SOP Visualization Workflow initialization failed: {e}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return None
        
        return self._sop_visualization_workflow
    
    async def initialize(self) -> bool:
        """
        Initialize Operations Journey Orchestrator.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self._realm_service.log_operation_with_telemetry(
            "operations_journey_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up RealmServiceBase)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Operations Journey Orchestrator...")
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Operations Journey Orchestrator initialized successfully")
            
            # Complete telemetry tracking
            await self._realm_service.log_operation_with_telemetry(
                "operations_journey_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Operations Journey Orchestrator: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            await self._realm_service.log_operation_with_telemetry(
                "operations_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Operations Journey Orchestrator with Curator for discovery."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                service_metadata = {
                    "service_name": self.service_name,
                    "service_type": "operations_journey_orchestration",
                    "realm_name": self.realm_name,
                    "capabilities": [
                        "sop_to_workflow",
                        "workflow_to_sop",
                        "coexistence_analysis",
                        "interactive_sop_creation",
                        "interactive_blueprint_creation",
                        "ai_optimized_blueprint",
                        "workflow_visualization",
                        "sop_visualization"
                    ],
                    "description": "Orchestrates operations workflows and composes Journey realm services"
                }
                await curator.register_service(self, service_metadata)
                self.logger.info("✅ Registered Operations Journey Orchestrator with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def execute_sop_to_workflow_workflow(
        self,
        sop_content: Dict[str, Any],
        workflow_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute SOP to workflow conversion with solution context integration and optional Saga guarantees.
        
        Delegates to SOPToWorkflowWorkflow which orchestrates:
        - Agent critical reasoning (OperationsSpecialistAgent)
        - Workflow structure generation
        - WorkflowConversionService execution
        
        Args:
            sop_content: SOP content (structure from parsing)
            workflow_options: Optional workflow generation options
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with workflow structure, workflow_id, and saga_id (if Saga was used)
        """
        # Prepare user context for Saga
        enhanced_user_context = user_context.copy() if user_context else {}
        enhanced_user_context.update({
            "sop_content": sop_content
        })
        
        # Define milestones for SOP to workflow operation
        milestones = ["extract_sop_structure", "analyze_workflow_requirements", "generate_workflow", "validate_workflow", "store_workflow"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="operations_sop_to_workflow",
            workflow_func=lambda: self._execute_sop_to_workflow_workflow_internal(
                sop_content=sop_content,
                workflow_options=workflow_options,
                user_context=enhanced_user_context
            ),
            milestones=milestones,
            user_context=enhanced_user_context
        )
    
    async def _execute_sop_to_workflow_workflow_internal(
        self,
        sop_content: Dict[str, Any],
        workflow_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute SOP to workflow workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            sop_content: SOP content (structure from parsing)
            workflow_options: Optional workflow generation options
            user_context: Optional user context
        
        Returns:
            Dict with workflow structure, workflow_id, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context or {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            # Enhance user_context with solution context
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for SOP to workflow conversion")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Enhance workflow_options with solution context if available
            enhanced_workflow_options = (workflow_options or {}).copy()
            if enhanced_user_context.get("solution_context"):
                solution_context = enhanced_user_context["solution_context"]
                enhanced_workflow_options["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_workflow_options["strategic_focus"] = solution_structure.get("strategic_focus", "")
                enhanced_workflow_options["solution_context"] = solution_context
            
            # Get SOP to Workflow Workflow
            workflow = await self._get_sop_to_workflow_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "SOP to Workflow Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                sop_content=sop_content,
                workflow_options=enhanced_workflow_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ SOP to workflow workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_sop_to_workflow_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_workflow_to_sop_workflow(
        self,
        workflow_content: Dict[str, Any],
        sop_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow to SOP conversion with solution context integration.
        
        Delegates to WorkflowToSOPWorkflow which orchestrates:
        - Agent critical reasoning (OperationsSpecialistAgent)
        - SOP structure generation
        - WorkflowConversionService execution
        
        Args:
            workflow_content: Workflow content (structure from parsing)
            sop_options: Optional SOP generation options
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with SOP structure, sop_id, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for workflow to SOP conversion")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Enhance sop_options with solution context if available
            enhanced_sop_options = (sop_options or {}).copy()
            if enhanced_user_context.get("solution_context"):
                solution_context = enhanced_user_context["solution_context"]
                enhanced_sop_options["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_sop_options["strategic_focus"] = solution_structure.get("strategic_focus", "")
                enhanced_sop_options["solution_context"] = solution_context
            
            # Get Workflow to SOP Workflow
            workflow = await self._get_workflow_to_sop_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "Workflow to SOP Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                workflow_content=workflow_content,
                sop_options=enhanced_sop_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow to SOP workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_workflow_to_sop_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_coexistence_analysis_workflow(
        self,
        coexistence_content: Dict[str, Any],
        analysis_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute coexistence analysis with solution context integration.
        
        Delegates to CoexistenceAnalysisWorkflow which orchestrates:
        - Agent critical reasoning (OperationsSpecialistAgent)
        - Coexistence analysis
        - CoexistenceAnalysisService execution
        
        Args:
            coexistence_content: Coexistence content (current state, target state, etc.)
            analysis_options: Optional analysis options
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with analysis results, recommendations, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for coexistence analysis")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Enhance analysis_options with solution context if available
            enhanced_analysis_options = (analysis_options or {}).copy()
            if enhanced_user_context.get("solution_context"):
                solution_context = enhanced_user_context["solution_context"]
                enhanced_analysis_options["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_analysis_options["strategic_focus"] = solution_structure.get("strategic_focus", "")
                enhanced_analysis_options["solution_context"] = solution_context
            
            # Get Coexistence Analysis Workflow
            workflow = await self._get_coexistence_analysis_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "Coexistence Analysis Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                coexistence_content=coexistence_content,
                analysis_options=enhanced_analysis_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Coexistence analysis workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_coexistence_analysis_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_interactive_sop_creation_workflow(
        self,
        action: str,
        user_message: Optional[str] = None,
        session_token: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute interactive SOP creation workflow.
        
        Delegates to InteractiveSOPCreationWorkflow which orchestrates:
        - SOPBuilderService wizard
        - OperationsLiaisonAgent conversational interface
        - Solution context integration
        
        Args:
            action: Action type ("start", "chat", "publish")
            user_message: User's chat message (for "chat" action)
            session_token: Session token for SOP creation wizard
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with response, session_token, sop_structure, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for interactive SOP creation")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Get Interactive SOP Creation Workflow
            workflow = await self._get_interactive_sop_creation_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "Interactive SOP Creation Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                action=action,
                user_message=user_message,
                session_token=session_token,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive SOP creation workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_interactive_sop_creation_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_interactive_blueprint_creation_workflow(
        self,
        user_message: str,
        session_token: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute interactive blueprint creation workflow.
        
        Delegates to InteractiveBlueprintCreationWorkflow which orchestrates:
        - OperationsSpecialistAgent conversational interface
        - Blueprint structure generation
        - Solution context integration
        
        Args:
            user_message: User's chat message
            session_token: Optional session token
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with response, blueprint_structure, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for interactive blueprint creation")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Get Interactive Blueprint Creation Workflow
            workflow = await self._get_interactive_blueprint_creation_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "Interactive Blueprint Creation Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                user_message=user_message,
                session_token=session_token,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive blueprint creation workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_interactive_blueprint_creation_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_ai_optimized_blueprint_workflow(
        self,
        sop_file_ids: Optional[List[str]] = None,
        workflow_file_ids: Optional[List[str]] = None,
        optimization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute AI-optimized blueprint generation workflow.
        
        Delegates to AIOptimizedBlueprintWorkflow which orchestrates:
        - Data mash queries for available SOP/workflow files
        - Agent critical reasoning (OperationsSpecialistAgent)
        - Blueprint optimization
        - Recommendations and implementation roadmap
        
        Args:
            sop_file_ids: Optional list of SOP file IDs to use
            workflow_file_ids: Optional list of workflow file IDs to use
            optimization_options: Optional optimization options
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with blueprint_structure, recommendations, roadmap, etc.
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for AI-optimized blueprint")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Enhance optimization_options with solution context if available
            enhanced_optimization_options = (optimization_options or {}).copy()
            if enhanced_user_context.get("solution_context"):
                solution_context = enhanced_user_context["solution_context"]
                enhanced_optimization_options["user_goals"] = solution_context.get("user_goals", "")
                solution_structure = solution_context.get("solution_structure", {})
                enhanced_optimization_options["strategic_focus"] = solution_structure.get("strategic_focus", "")
                enhanced_optimization_options["solution_context"] = solution_context
            
            # Get AI-Optimized Blueprint Workflow
            workflow = await self._get_ai_optimized_blueprint_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "AI-Optimized Blueprint Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                sop_file_ids=sop_file_ids,
                workflow_file_ids=workflow_file_ids,
                optimization_options=enhanced_optimization_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ AI-optimized blueprint workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_ai_optimized_blueprint_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_workflow_visualization_workflow(
        self,
        workflow_file_id: Optional[str] = None,
        workflow_content: Optional[Dict[str, Any]] = None,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow visualization workflow.
        
        Delegates to WorkflowVisualizationWorkflow which prepares workflow structure for display.
        
        Args:
            workflow_file_id: Optional workflow file identifier
            workflow_content: Optional workflow content
            visualization_options: Optional visualization options
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with workflow visualization data
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for workflow visualization")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Get Workflow Visualization Workflow
            workflow = await self._get_workflow_visualization_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "Workflow Visualization Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                workflow_file_id=workflow_file_id,
                workflow_content=workflow_content,
                visualization_options=visualization_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow visualization workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_workflow_visualization_workflow")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_sop_visualization_workflow(
        self,
        sop_file_id: Optional[str] = None,
        sop_content: Optional[Dict[str, Any]] = None,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute SOP visualization workflow.
        
        Delegates to SOPVisualizationWorkflow which prepares SOP structure for display.
        
        Args:
            sop_file_id: Optional SOP file identifier
            sop_content: Optional SOP content
            visualization_options: Optional visualization options
            user_context: Optional user context (includes workflow_id, session_id)
        
        Returns:
            Dict with SOP visualization data
        """
        try:
            # Get solution context from session if available
            enhanced_user_context = user_context.copy() if user_context else {}
            session_id = enhanced_user_context.get("session_id")
            
            if session_id:
                mvp_orchestrator = await self._get_mvp_journey_orchestrator()
                if mvp_orchestrator:
                    try:
                        solution_context = await mvp_orchestrator.get_solution_context(session_id)
                        if solution_context:
                            enhanced_user_context["solution_context"] = solution_context
                            self.logger.info("✅ Solution context retrieved and added to user_context for SOP visualization")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to get solution context: {e}")
            
            # Get SOP Visualization Workflow
            workflow = await self._get_sop_visualization_workflow()
            if not workflow:
                return {
                    "success": False,
                    "error": "SOP Visualization Workflow not available"
                }
            
            # Execute workflow with enhanced context
            result = await workflow.execute(
                sop_file_id=sop_file_id,
                sop_content=sop_content,
                visualization_options=visualization_options,
                user_context=enhanced_user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ SOP visualization workflow execution failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "execute_sop_visualization_workflow")
            return {
                "success": False,
                "error": str(e)
            }

