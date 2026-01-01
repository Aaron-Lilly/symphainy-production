#!/usr/bin/env python3
"""
Operations Solution Orchestrator Service

WHAT: Orchestrates operations operations (SOP/workflow generation, coexistence)
HOW: Lightweight shell that composes operations journey orchestrators and orchestrates platform correlation

This service is the "One Stop Shopping" for all operations operations:
1. Operations Operations → delegates to OperationsJourneyOrchestrator (Journey realm)
2. Platform Correlation → orchestrates all platform services (auth, session, workflow, events, telemetry)

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Routes to OperationsJourneyOrchestrator (Journey realm)
- Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Ensures all platform correlation data follows operations operations through journey
- Registered with Curator for discovery
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class OperationsSolutionOrchestratorService(OrchestratorBase):
    """
    Operations Solution Orchestrator Service - Lightweight shell with platform correlation.
    
    "One Stop Shopping" for:
    1. Operations Operations (via OperationsJourneyOrchestratorService)
    2. Platform Correlation Data (auth, session, workflow, events, telemetry)
    
    Orchestrates operations operations:
    1. Workflow Generation: Convert SOPs to workflows
    2. SOP Generation: Convert workflows to SOPs
    3. Coexistence Analysis: Analyze human-AI coexistence
    4. Interactive SOP Creation: Conversational SOP creation
    5. Interactive Blueprint Creation: Conversational coexistence blueprint creation
    6. AI-Optimized Blueprint: Generate optimized blueprint from available documents
    
    Key Principles:
    - Routes to OperationsJourneyOrchestrator (Journey realm)
    - Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
    - Ensures all platform correlation data follows operations operations through journey
    - workflow_id propagation for end-to-end tracking
    - Registered with Curator for discovery
    """
    
    def __init__(
        self,
        service_name: str,
        realm_name: str,
        platform_gateway: Any,
        di_container: Any,
        delivery_manager: Any = None
    ):
        """
        Initialize Operations Solution Orchestrator Service.
        
        Args:
            service_name: Service name (typically "OperationsSolutionOrchestratorService")
            realm_name: Realm name (typically "solution")
            platform_gateway: Platform Gateway instance
            di_container: DI Container instance
            delivery_manager: Delivery Manager reference (optional, for orchestrator management)
        """
        super().__init__(
            service_name=service_name,
            realm_name=realm_name,
            platform_gateway=platform_gateway,
            di_container=di_container,
            delivery_manager=delivery_manager
        )
        
        # Journey orchestrators (discovered via Curator)
        self.operations_journey_orchestrator = None  # Operations operations orchestration
        
        # Platform correlation services (discovered via Curator)
        self.security_guard = None
        self.traffic_cop = None
        self.conductor = None
        self.post_office = None
        self.nurse = None
        
        # Data Solution Orchestrator (for data mash queries)
        self.data_solution_orchestrator = None
    
    async def initialize(self) -> bool:
        """
        Initialize Operations Solution Orchestrator Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        
        Returns:
            True if initialization successful, False otherwise
        """
        # Start telemetry tracking (via _realm_service delegation)
        await self._realm_service.log_operation_with_telemetry(
            "operations_solution_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase and _realm_service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Operations Solution Orchestrator Service...")
            
            # Journey orchestrators will be lazy-loaded when methods are called
            # Platform correlation services will be lazy-loaded when methods are called
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Operations Solution Orchestrator Service initialized successfully")
            
            # Complete telemetry tracking (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "operations_solution_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Operations Solution Orchestrator Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure in telemetry (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "operations_solution_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Operations Solution Orchestrator Service with Curator for discovery."""
        try:
            # Get Curator via OrchestratorBase helper method
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                # Register service instance (required for get_service() discovery)
                service_metadata = {
                    "service_name": self.service_name,
                    "service_type": "operations_solution_orchestration",
                    "realm_name": self.realm_name,
                    "capabilities": [
                        "workflow_generation",
                        "sop_generation",
                        "coexistence_analysis",
                        "interactive_sop_creation",
                        "interactive_blueprint_creation",
                        "ai_optimized_blueprint",
                        "workflow_visualization",
                        "sop_visualization",
                        "platform_correlation"
                    ],
                    "description": "Lightweight shell: orchestrates operations operations and platform correlation"
                }
                await curator.register_service(self, service_metadata)
                self.logger.info("✅ Registered Operations Solution Orchestrator Service instance with Curator")
                
                # Also register capability (for capability-based discovery)
                capability_definition = {
                    "service_name": self.service_name,
                    "realm_name": self.realm_name,
                    "capability_type": "operations_solution_orchestration",
                    "description": "Orchestrates operations operations: Workflow Generation, SOP Generation, Coexistence Analysis",
                    "contracts": {
                        "orchestrate_operations_workflow_generation": {
                            "description": "Orchestrate workflow generation from SOP",
                            "parameters": ["sop_file_id", "sop_content", "workflow_options", "user_context"],
                            "returns": ["success", "workflow_id", "workflow_structure", "workflow_id"]
                        },
                        "orchestrate_operations_sop_generation": {
                            "description": "Orchestrate SOP generation from workflow",
                            "parameters": ["workflow_file_id", "workflow_content", "sop_options", "user_context"],
                            "returns": ["success", "sop_id", "sop_structure", "workflow_id"]
                        },
                        "orchestrate_operations_coexistence_analysis": {
                            "description": "Orchestrate coexistence analysis",
                            "parameters": ["coexistence_content", "analysis_options", "user_context"],
                            "returns": ["success", "analysis_id", "analysis_results", "workflow_id"]
                        }
                    }
                }
                await curator.register_capability(capability_definition)
                self.logger.info("✅ Registered Operations Solution Orchestrator Service capability with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def _discover_operations_journey_orchestrator(self):
        """Discover OperationsJourneyOrchestratorService via Curator, or lazy-initialize if not found."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                operations_journey = await curator.discover_service_by_name("OperationsJourneyOrchestratorService")
                if operations_journey:
                    # Verify it's from Journey realm
                    orchestrator_realm = getattr(operations_journey, 'realm_name', None)
                    if orchestrator_realm == "journey":
                        self.logger.info("✅ Discovered OperationsJourneyOrchestratorService via Curator")
                        return operations_journey
                    else:
                        self.logger.warning(f"⚠️ Found OperationsJourneyOrchestratorService but wrong realm: {orchestrator_realm} (expected 'journey')")
            
            # If not found via discovery, lazy-initialize it (pattern for non-Smart City realms)
            self.logger.info("🔄 OperationsJourneyOrchestratorService not found - lazy-initializing...")
            try:
                from backend.journey.orchestrators.operations_journey_orchestrator.operations_journey_orchestrator import OperationsJourneyOrchestrator
                
                # Get platform gateway from DI container
                platform_gateway = self.platform_gateway
                if not platform_gateway:
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                    if not platform_gateway:
                        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                
                # Create and initialize Operations Journey Orchestrator (self-initializing)
                operations_journey = OperationsJourneyOrchestrator(
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await operations_journey.initialize()
                self.logger.info("✅ OperationsJourneyOrchestratorService lazy-initialized successfully")
                return operations_journey
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize OperationsJourneyOrchestratorService: {init_error}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover OperationsJourneyOrchestratorService: {e}")
            return None
    
    async def _get_data_solution_orchestrator(self):
        """Get Data Solution Orchestrator for data mash queries."""
        if not self.data_solution_orchestrator:
            try:
                curator = await self.get_foundation_service("CuratorFoundationService")
                if curator:
                    data_orchestrator = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                    if data_orchestrator:
                        self.data_solution_orchestrator = data_orchestrator
                        self.logger.info("✅ Discovered DataSolutionOrchestratorService via Curator")
                        return data_orchestrator
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover DataSolutionOrchestratorService: {e}")
        return self.data_solution_orchestrator
    
    async def _orchestrate_platform_correlation(
        self,
        operation: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate platform correlation services.
        
        Platform correlation includes:
        - Security Guard: Auth and tenant validation
        - Traffic Cop: Session and state management
        - Conductor: Workflow tracking
        - Post Office: Events and messaging
        - Nurse: Telemetry and observability
        
        Args:
            operation: Operation name (e.g., "operations_workflow_generation")
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Correlation context with user_id, session_id, workflow_id, etc.
        """
        correlation_context = {}
        
        # Generate or get workflow_id
        workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
        correlation_context["workflow_id"] = workflow_id
        
        # Security Guard: Auth and tenant validation
        if not self.security_guard:
            self.security_guard = await self.get_foundation_service("SecurityGuardService")
        
        if self.security_guard and user_context:
            try:
                user_id = user_context.get("user_id", "anonymous")
                tenant_id = user_context.get("tenant_id")
                
                # Validate user and tenant
                if tenant_id:
                    validation_result = await self.security_guard.validate_tenant_access(
                        user_id=user_id,
                        tenant_id=tenant_id,
                        operation=operation
                    )
                    if validation_result.get("valid"):
                        correlation_context["user_id"] = user_id
                        correlation_context["tenant_id"] = tenant_id
                    else:
                        self.logger.warning(f"⚠️ Tenant validation failed: {validation_result.get('error')}")
                else:
                    correlation_context["user_id"] = user_id
            except Exception as e:
                self.logger.warning(f"⚠️ Security Guard validation failed: {e}")
        
        # Traffic Cop: Session and state management
        if not self.traffic_cop:
            self.traffic_cop = await self.get_foundation_service("TrafficCopService")
        
        if self.traffic_cop and user_context:
            try:
                session_id = user_context.get("session_id")
                if session_id:
                    # Get or create session
                    session = await self.traffic_cop.get_session(session_id)
                    if session:
                        correlation_context["session_id"] = session_id
                        correlation_context["session"] = session
                    else:
                        # Create new session if needed
                        new_session = await self.traffic_cop.create_session(
                            user_id=correlation_context.get("user_id", "anonymous"),
                            workflow_id=workflow_id
                        )
                        if new_session:
                            correlation_context["session_id"] = new_session.get("session_id")
                            correlation_context["session"] = new_session
            except Exception as e:
                self.logger.warning(f"⚠️ Traffic Cop session management failed: {e}")
        
        # Conductor: Workflow tracking
        if not self.conductor:
            self.conductor = await self.get_foundation_service("ConductorService")
        
        if self.conductor and workflow_id:
            try:
                workflow_status = await self.conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=operation,
                    step_status="in_progress",
                    metadata={"operation": operation}
                )
                if workflow_status:
                    correlation_context["workflow_tracked"] = True
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow tracking failed: {e}")
        
        return correlation_context
    
    async def _record_platform_correlation_completion(
        self,
        operation: str,
        result: Dict[str, Any],
        correlation_context: Optional[Dict[str, Any]] = None
    ):
        """
        Record completion in platform correlation services.
        
        Args:
            operation: Operation name
            result: Operation result
            correlation_context: Correlation context
        """
        workflow_id = correlation_context.get("workflow_id") if correlation_context else None
        
        # Conductor: Mark workflow step complete
        if self.conductor and workflow_id:
            try:
                await self.conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=operation,
                    step_status="completed" if result.get("success") else "failed",
                    metadata={"operation": operation, "result": result}
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow completion tracking failed: {e}")
        
        # Post Office: Publish event
        if not self.post_office:
            self.post_office = await self.get_foundation_service("PostOfficeService")
        
        if self.post_office and workflow_id:
            try:
                await self.post_office.publish_event(
                    event_type="operations_operation_complete",
                    event_data={
                        "operation": operation,
                        "success": result.get("success"),
                        "result": result
                    },
                    trace_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Event publishing failed: {e}")
        
        # Nurse: Record completion telemetry
        if not self.nurse:
            self.nurse = await self.get_foundation_service("NurseService")
        
        if self.nurse and workflow_id:
            try:
                await self.nurse.record_platform_event(
                    event_type="log",
                    event_data={
                        "level": "info" if result.get("success") else "error",
                        "message": f"Operations operation completed: {operation}",
                        "service_name": self.__class__.__name__,
                        "operation": operation,
                        "success": result.get("success")
                    },
                    trace_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Telemetry recording failed: {e}")
    
    def _wal_enabled(self) -> bool:
        """
        Check if WAL is enabled via policy.
        
        ⭐ CAPABILITY BY DESIGN, OPTIONAL BY POLICY:
        - WAL capability is built into the architecture
        - Enabled/disabled via policy configuration
        - Default: disabled (no overhead)
        """
        # Policy-based WAL enablement
        # Check ConfigAdapter (preferred) or environment variable
        config_adapter = self._get_config_adapter()
        if config_adapter:
            wal_enabled = config_adapter.get("WAL_ENABLED", "false")
            if isinstance(wal_enabled, str):
                wal_enabled = wal_enabled.lower() == "true"
            else:
                wal_enabled = bool(wal_enabled)
            wal_operations_str = config_adapter.get("WAL_OPERATIONS", "operations_workflow_generation,operations_sop_generation,operations_coexistence_analysis,interactive_sop_creation,interactive_blueprint_creation,workflow_visualization,sop_visualization,ai_optimized_blueprint")
        else:
            import os
            wal_enabled = os.getenv("WAL_ENABLED", "false").lower() == "true"
            wal_operations_str = os.getenv("WAL_OPERATIONS", "operations_workflow_generation,operations_sop_generation,operations_coexistence_analysis,interactive_sop_creation,interactive_blueprint_creation,workflow_visualization,sop_visualization,ai_optimized_blueprint")
            if wal_enabled or wal_operations_str:
                self.logger.warning("⚠️ [OPERATIONS_SOLUTION] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
        
        # Parse wal operations
        if isinstance(wal_operations_str, str):
            wal_operations = wal_operations_str.split(",")
        else:
            wal_operations = ["operations_workflow_generation", "operations_sop_generation", "operations_coexistence_analysis", "interactive_sop_creation", "interactive_blueprint_creation", "workflow_visualization", "sop_visualization", "ai_optimized_blueprint"]
        
        # Store policy for later use
        if not hasattr(self, '_wal_policy'):
            self._wal_policy = {
                "enable_wal": wal_enabled,
                "log_operations": [op.strip() for op in wal_operations],
                "namespace": "operations_solution_operations"
            }
        
        return self._wal_policy.get("enable_wal", False)
    
    async def _write_to_wal(
        self,
        namespace: str,
        payload: Dict[str, Any],
        target: str,
        user_context: Optional[Dict[str, Any]] = None
    ):
        """
        Write to WAL if enabled.
        
        ⭐ REAL WAL INTEGRATION: Uses DataStewardService WAL capability.
        """
        if not self._wal_enabled():
            return
        
        # Check if this operation should be logged
        operation = payload.get("operation", "")
        if operation and operation not in self._wal_policy.get("log_operations", []):
            return
        
        try:
            # Get Data Steward service for WAL capability
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                self.logger.warning("⚠️ DataStewardService not available - WAL logging skipped")
                return
            
            # Build WAL payload with correlation context
            wal_payload = {
                **payload,
                "workflow_id": user_context.get("workflow_id") if user_context else None,
                "session_id": user_context.get("session_id") if user_context else None,
                "user_id": user_context.get("user_id", "anonymous") if user_context else "anonymous",
                "timestamp": user_context.get("timestamp") if user_context else None
            }
            
            # Write to WAL via Data Steward
            wal_result = await data_steward.write_to_log(
                namespace=namespace or self._wal_policy.get("namespace", "operations_solution_operations"),
                payload=wal_payload,
                target=target,
                lifecycle={
                    "retry_count": 3,
                    "delay_seconds": 5,
                    "ttl_seconds": 86400  # 24 hours
                },
                user_context=user_context
            )
            
            if wal_result.get("success"):
                self.logger.debug(f"✅ WAL entry written: {wal_result.get('log_id')}")
            else:
                self.logger.warning(f"⚠️ WAL write failed: {wal_result.get('error')}")
                
        except Exception as e:
            # WAL failure should not block operations
            self.logger.warning(f"⚠️ WAL write failed (non-blocking): {e}")
    
    async def _get_policy_configuration_service(self):
        """Lazy initialization of Policy Configuration Service."""
        if not hasattr(self, '_policy_config_service') or self._policy_config_service is None:
            try:
                curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
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
        
        # Fallback to ConfigAdapter (preferred) or environment variables if service not available
        config_adapter = self._get_config_adapter()
        if config_adapter:
            saga_enabled = config_adapter.get("SAGA_ENABLED", "false")
            if isinstance(saga_enabled, str):
                saga_enabled = saga_enabled.lower() == "true"
            else:
                saga_enabled = bool(saga_enabled)
            saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "operations_workflow_generation,operations_coexistence_analysis,interactive_sop_creation")
        else:
            import os
            saga_enabled = os.getenv("SAGA_ENABLED", "false").lower() == "true"
            saga_operations_str = os.getenv("SAGA_OPERATIONS", "operations_workflow_generation,operations_coexistence_analysis,interactive_sop_creation")
            if saga_enabled or saga_operations_str:
                self.logger.warning("⚠️ [OPERATIONS_SOLUTION] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
        
        # Parse saga operations
        if isinstance(saga_operations_str, str):
            saga_operations = saga_operations_str.split(",")
        else:
            saga_operations = ["operations_workflow_generation", "operations_coexistence_analysis", "interactive_sop_creation"]
        
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
            "operations_workflow_generation": {
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
            },
            "interactive_sop_creation": {
                "start_wizard": "delete_wizard_session",
                "collect_steps": "clear_wizard_state",
                "generate_sop": "delete_sop_draft",
                "validate_sop": "mark_sop_as_invalid",
                "publish_sop": "delete_published_sop"
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
            operation: Operation name (e.g., "operations_workflow_generation")
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
    
    async def orchestrate_operations_pillar_summary(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Operations pillar summary for Business Outcomes.
        
        ⭐ NEW: Solution Orchestrator endpoint for pillar summary compilation.
        
        Returns:
        {
            "success": True,
            "pillar": "operations",
            "summary": {
                "textual": str,
                "tabular": {...},
                "visualizations": [...],
                "artifacts": {...}
            }
        }
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="operations_pillar_summary",
            user_context=user_context
        )
        
        # Get Operations Journey Orchestrator
        if not self.operations_journey_orchestrator:
            self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
        
        if not self.operations_journey_orchestrator:
            return {
                "success": False,
                "error": "OperationsJourneyOrchestrator not available",
                "pillar": "operations",
                "summary": {}
            }
        
        # Get summary from Journey Orchestrator
        try:
            if hasattr(self.operations_journey_orchestrator, 'get_pillar_summary'):
                summary_result = await self.operations_journey_orchestrator.get_pillar_summary(
                    session_id=session_id,
                    user_id=correlation_context.get("user_id", "anonymous")
                )
            else:
                # Bridge: Try to get legacy OperationsOrchestrator
                self.logger.warning("⚠️ OperationsJourneyOrchestrator doesn't have get_pillar_summary, trying legacy orchestrator")
                summary_result = {
                    "success": False,
                    "error": "get_pillar_summary not implemented in OperationsJourneyOrchestrator",
                    "pillar": "operations",
                    "summary": {}
                }
            
            if summary_result.get("success"):
                return {
                    "success": True,
                    "pillar": "operations",
                    "summary": summary_result.get("summary", {}),
                    "workflow_id": correlation_context.get("workflow_id")
                }
            else:
                return {
                    "success": False,
                    "error": summary_result.get("error", "Failed to get operations pillar summary"),
                    "pillar": "operations",
                    "summary": {}
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to get operations pillar summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "pillar": "operations",
                "summary": {}
            }
    
    async def orchestrate_operations_workflow_generation(
        self,
        sop_file_id: Optional[str] = None,
        sop_content: Optional[Dict[str, Any]] = None,
        workflow_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate workflow generation from SOP with full platform correlation and optional Saga guarantees.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Execute with Saga if enabled (Capability by Design, Optional by Policy)
        3. Get SOP content from data mash if sop_file_id provided
        4. Route to Operations Journey Orchestrator
        5. Record completion in platform correlation
        
        Args:
            sop_file_id: Optional SOP file identifier (if provided, will fetch from data mash)
            sop_content: Optional SOP content (if provided, will use directly)
            workflow_options: Optional workflow generation options
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, workflow_id, workflow_structure, and saga_id (if Saga was used)
        """
        # Define milestones for workflow generation operation
        milestones = ["extract_sop_structure", "analyze_workflow_requirements", "generate_workflow", "validate_workflow", "store_workflow"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="operations_workflow_generation",
            workflow_func=lambda: self._execute_operations_workflow_generation_workflow(
                sop_file_id=sop_file_id,
                sop_content=sop_content,
                workflow_options=workflow_options,
                user_context=user_context
            ),
            milestones=milestones,
            user_context=user_context
        )
    
    async def _execute_operations_workflow_generation_workflow(
        self,
        sop_file_id: Optional[str] = None,
        sop_content: Optional[Dict[str, Any]] = None,
        workflow_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute operations workflow generation workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            sop_file_id: Optional SOP file identifier
            sop_content: Optional SOP content
            workflow_options: Optional workflow generation options
            user_context: Optional user context
        
        Returns:
            Dict with success status, workflow_id, workflow_structure, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="operations_workflow_generation",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "operations_workflow_generation",
                    "sop_file_id": sop_file_id,
                    "workflow_options": workflow_options
                },
                target="operations_workflow_generation",
                user_context=correlation_context
            )
            
            # Step 2: Get SOP content from data mash if sop_file_id provided
            if sop_file_id and not sop_content:
                data_mash = await self._get_data_solution_orchestrator()
                if data_mash:
                    self.logger.info(f"📊 Fetching SOP content from data mash: {sop_file_id}")
                    sop_data = await data_mash.orchestrate_data_mash(
                        client_data_query={"type": "file_id:" + sop_file_id},
                        user_context=correlation_context
                    )
                    if sop_data.get("success") and sop_data.get("client_data", {}).get("file"):
                        # Extract parsed SOP structure from file metadata
                        file_data = sop_data["client_data"]["file"]
                        parsed_files = sop_data["client_data"].get("parsed_files", [])
                        if parsed_files:
                            parse_result = parsed_files[0].get("metadata", {}).get("parse_result", {})
                            if parse_result.get("parsing_type") == "sop":
                                sop_content = parse_result.get("structure", {})
                                self.logger.info(f"✅ Extracted SOP structure from parsed file: {len(sop_content.get('sections', []))} sections")
                            else:
                                self.logger.warning(f"⚠️ File {sop_file_id} is not a parsed SOP file")
                        else:
                            self.logger.warning(f"⚠️ No parsed files found for SOP file: {sop_file_id}")
                else:
                    self.logger.warning("⚠️ DataSolutionOrchestratorService not available - cannot fetch SOP content")
            
            if not sop_content:
                return {
                    "success": False,
                    "error": "SOP content not provided and could not be fetched from data mash",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
            # Step 3: Route to Operations Journey Orchestrator (Journey realm)
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 4: Execute workflow generation with correlation context
            result = await self.operations_journey_orchestrator.execute_sop_to_workflow_workflow(
                sop_content=sop_content,
                workflow_options=workflow_options,
                user_context=correlation_context
            )
            
            # Step 5: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="operations_workflow_generation",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Operations workflow generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_operations_workflow_generation")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_operations_sop_generation(
        self,
        workflow_file_id: Optional[str] = None,
        workflow_content: Optional[Dict[str, Any]] = None,
        sop_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate SOP generation from workflow with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation
        2. Get workflow content from data mash if workflow_file_id provided
        3. Route to Operations Journey Orchestrator
        4. Record completion in platform correlation
        
        Args:
            workflow_file_id: Optional workflow file identifier
            workflow_content: Optional workflow content
            sop_options: Optional SOP generation options
            user_context: Optional user context
        
        Returns:
            Dict with success status, sop_id, sop_structure, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="operations_sop_generation",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "operations_sop_generation",
                    "workflow_file_id": workflow_file_id,
                    "sop_options": sop_options
                },
                target="operations_sop_generation",
                user_context=correlation_context
            )
            
            # Step 2: Get workflow content from data mash if workflow_file_id provided
            if workflow_file_id and not workflow_content:
                data_mash = await self._get_data_solution_orchestrator()
                if data_mash:
                    self.logger.info(f"📊 Fetching workflow content from data mash: {workflow_file_id}")
                    workflow_data = await data_mash.orchestrate_data_mash(
                        client_data_query={"type": "file_id:" + workflow_file_id},
                        user_context=correlation_context
                    )
                    if workflow_data.get("success") and workflow_data.get("client_data", {}).get("file"):
                        file_data = workflow_data["client_data"]["file"]
                        parsed_files = workflow_data["client_data"].get("parsed_files", [])
                        if parsed_files:
                            parse_result = parsed_files[0].get("metadata", {}).get("parse_result", {})
                            if parse_result.get("parsing_type") == "workflow":
                                workflow_content = parse_result.get("structure", {})
                                self.logger.info(f"✅ Extracted workflow structure from parsed file: {len(workflow_content.get('nodes', []))} nodes")
                else:
                    self.logger.warning("⚠️ DataSolutionOrchestratorService not available - cannot fetch workflow content")
            
            if not workflow_content:
                return {
                    "success": False,
                    "error": "Workflow content not provided and could not be fetched from data mash",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
            # Step 3: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 4: Execute SOP generation with correlation context
            result = await self.operations_journey_orchestrator.execute_workflow_to_sop_workflow(
                workflow_content=workflow_content,
                sop_options=sop_options,
                user_context=correlation_context
            )
            
            # Step 5: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="operations_sop_generation",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Operations SOP generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_operations_sop_generation")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_operations_coexistence_analysis(
        self,
        coexistence_content: Dict[str, Any],
        analysis_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate coexistence analysis with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation
        2. Route to Operations Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            coexistence_content: Coexistence content (current state, target state, etc.)
            analysis_options: Optional analysis options
            user_context: Optional user context
        
        Returns:
            Dict with success status, analysis_id, analysis_results, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="operations_coexistence_analysis",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "operations_coexistence_analysis",
                    "coexistence_content": coexistence_content,
                    "analysis_options": analysis_options
                },
                target="operations_coexistence_analysis",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute coexistence analysis with correlation context
            result = await self.operations_journey_orchestrator.execute_coexistence_analysis_workflow(
                coexistence_content=coexistence_content,
                analysis_options=analysis_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="operations_coexistence_analysis",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Operations coexistence analysis failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_operations_coexistence_analysis")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_interactive_sop_creation_start(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start interactive SOP creation session.
        
        Args:
            user_context: Optional user context
        
        Returns:
            Dict with success status, session_token, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="interactive_sop_creation_start",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "interactive_sop_creation_start",
                    "wizard_options": wizard_options
                },
                target="interactive_sop_creation_start",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute interactive SOP creation start
            result = await self.operations_journey_orchestrator.execute_interactive_sop_creation_workflow(
                action="start",
                user_message=None,
                session_token=None,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="interactive_sop_creation_start",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive SOP creation start failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_interactive_sop_creation_start")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_interactive_sop_creation_chat(
        self,
        user_message: str,
        session_token: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process chat message in interactive SOP creation.
        
        Args:
            user_message: User's chat message
            session_token: Session token for SOP creation wizard
            user_context: Optional user context
        
        Returns:
            Dict with success status, response, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="interactive_sop_creation_chat",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "interactive_sop_creation_chat",
                    "session_token": session_token,
                    "user_message": user_message
                },
                target="interactive_sop_creation_chat",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute interactive SOP creation chat
            result = await self.operations_journey_orchestrator.execute_interactive_sop_creation_workflow(
                action="chat",
                user_message=user_message,
                session_token=session_token,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="interactive_sop_creation_chat",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive SOP creation chat failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_interactive_sop_creation_chat")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_interactive_sop_creation_publish(
        self,
        session_token: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Publish SOP from interactive creation session.
        
        Args:
            session_token: Session token for SOP creation wizard
            user_context: Optional user context
        
        Returns:
            Dict with success status, sop_id, sop_structure, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="interactive_sop_creation_publish",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "interactive_sop_creation_publish",
                    "session_token": session_token,
                    "publish_options": publish_options
                },
                target="interactive_sop_creation_publish",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute interactive SOP creation publish
            result = await self.operations_journey_orchestrator.execute_interactive_sop_creation_workflow(
                action="publish",
                user_message=None,
                session_token=session_token,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="interactive_sop_creation_publish",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive SOP creation publish failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_interactive_sop_creation_publish")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_interactive_blueprint_creation(
        self,
        user_message: str,
        session_token: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process chat message in interactive blueprint creation.
        
        Args:
            user_message: User's chat message
            session_token: Optional session token
            user_context: Optional user context
        
        Returns:
            Dict with success status, response, blueprint_structure, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="interactive_blueprint_creation",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "interactive_blueprint_creation",
                    "session_token": session_token,
                    "user_message": user_message
                },
                target="interactive_blueprint_creation",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute interactive blueprint creation
            result = await self.operations_journey_orchestrator.execute_interactive_blueprint_creation_workflow(
                user_message=user_message,
                session_token=session_token,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="interactive_blueprint_creation",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Interactive blueprint creation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_interactive_blueprint_creation")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_workflow_visualization(
        self,
        workflow_file_id: Optional[str] = None,
        workflow_content: Optional[Dict[str, Any]] = None,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate workflow visualization with full platform correlation.
        
        Prepares workflow structure for display/visualization (not conversion).
        
        Flow:
        1. Orchestrate platform correlation
        2. Route to Operations Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            workflow_file_id: Optional workflow file identifier
            workflow_content: Optional workflow content
            visualization_options: Optional visualization options
            user_context: Optional user context
        
        Returns:
            Dict with visualization_data, diagram_type, etc.
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="workflow_visualization",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "workflow_visualization",
                    "workflow_file_id": workflow_file_id
                },
                target="workflow_visualization",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute workflow visualization with correlation context
            result = await self.operations_journey_orchestrator.execute_workflow_visualization_workflow(
                workflow_file_id=workflow_file_id,
                workflow_content=workflow_content,
                visualization_options=visualization_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="workflow_visualization",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Workflow visualization failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_workflow_visualization")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_sop_visualization(
        self,
        sop_file_id: Optional[str] = None,
        sop_content: Optional[Dict[str, Any]] = None,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate SOP visualization with full platform correlation.
        
        Prepares SOP structure for display/visualization (not conversion).
        
        Flow:
        1. Orchestrate platform correlation
        2. Route to Operations Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            sop_file_id: Optional SOP file identifier
            sop_content: Optional SOP content
            visualization_options: Optional visualization options
            user_context: Optional user context
        
        Returns:
            Dict with visualization_data, format_type, etc.
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="sop_visualization",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "sop_visualization",
                    "sop_file_id": sop_file_id
                },
                target="sop_visualization",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute SOP visualization with correlation context
            result = await self.operations_journey_orchestrator.execute_sop_visualization_workflow(
                sop_file_id=sop_file_id,
                sop_content=sop_content,
                visualization_options=visualization_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="sop_visualization",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ SOP visualization failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_sop_visualization")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_ai_optimized_blueprint(
        self,
        sop_file_ids: Optional[List[str]] = None,
        workflow_file_ids: Optional[List[str]] = None,
        optimization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-optimized coexistence blueprint from available documents.
        
        Args:
            sop_file_ids: Optional list of SOP file IDs
            workflow_file_ids: Optional list of workflow file IDs
            optimization_options: Optional optimization options
            user_context: Optional user context
        
        Returns:
            Dict with success status, blueprint_structure, recommendations, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="ai_optimized_blueprint",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="operations_solution_operations",
                payload={
                    "operation": "ai_optimized_blueprint",
                    "sop_file_ids": sop_file_ids,
                    "workflow_file_ids": workflow_file_ids,
                    "optimization_options": optimization_options
                },
                target="ai_optimized_blueprint",
                user_context=correlation_context
            )
            
            # Step 2: Route to Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                raise ValueError("OperationsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute AI-optimized blueprint generation
            result = await self.operations_journey_orchestrator.execute_ai_optimized_blueprint_workflow(
                sop_file_ids=sop_file_ids,
                workflow_file_ids=workflow_file_ids,
                optimization_options=optimization_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="ai_optimized_blueprint",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ AI-optimized blueprint generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_ai_optimized_blueprint")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_operations_pillar_summary(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate Operations Pillar summary compilation.
        
        ⭐ Returns the coexistence blueprint - a visually and contextually interesting showcase
        of how workflows and SOPs coexist and interact.
        
        Args:
            session_id: Session identifier
            user_context: Optional user context (includes user_id, tenant_id)
        
        Returns:
            Dict with success status and coexistence blueprint
        """
        try:
            self.logger.info(f"📊 Compiling Operations pillar summary (coexistence blueprint) for session: {session_id}")
            
            # Get Operations Journey Orchestrator
            if not self.operations_journey_orchestrator:
                self.operations_journey_orchestrator = await self._discover_operations_journey_orchestrator()
            
            if not self.operations_journey_orchestrator:
                return {
                    "success": False,
                    "error": "OperationsJourneyOrchestrator not available",
                    "summary": {}
                }
            
            # Enhance user_context with session_id
            enhanced_user_context = (user_context or {}).copy()
            enhanced_user_context["session_id"] = session_id
            
            # Get the most recent coexistence analysis result (which contains the blueprint)
            # First, try to get workflows and SOPs for the session
            try:
                # Query for workflows and SOPs via Content Journey Orchestrator (they're stored as files)
                data_solution = await self._get_data_solution_orchestrator()
                if data_solution:
                    # Get workflow and SOP files via data mash
                    data_mash_result = await data_solution.orchestrate_data_mash(
                        client_data_query={"type": "workflow_sop"},
                        user_context=enhanced_user_context
                    )
                    
                    if data_mash_result.get("success"):
                        workflow_sop_data = data_mash_result.get("client_data", {}).get("workflow_sop", {})
                        workflows = workflow_sop_data.get("workflow_parsed", [])
                        sops = workflow_sop_data.get("sop_parsed", [])
                        
                        # If we have workflows and SOPs, perform coexistence analysis to get blueprint
                        if workflows and sops:
                            # Use the first workflow and SOP for coexistence analysis
                            workflow_content = workflows[0].get("metadata", {}).get("parse_result", {}) if workflows else {}
                            sop_content = sops[0].get("metadata", {}).get("parse_result", {}) if sops else {}
                            
                            coexistence_content = {
                                "current_state": {
                                    "workflows": [workflow_content] if workflow_content else [],
                                    "sops": [sop_content] if sop_content else []
                                },
                                "target_state": {
                                    "workflows": [workflow_content] if workflow_content else [],
                                    "sops": [sop_content] if sop_content else []
                                }
                            }
                            
                            # Perform coexistence analysis to get blueprint
                            coexistence_result = await self.orchestrate_operations_coexistence_analysis(
                                coexistence_content=coexistence_content,
                                analysis_options={},
                                user_context=enhanced_user_context
                            )
                            
                            if coexistence_result.get("success"):
                                # Extract blueprint from coexistence result
                                blueprint = coexistence_result.get("blueprint") or coexistence_result.get("analysis_results") or coexistence_result
                                
                                self.logger.info("✅ Operations pillar summary (coexistence blueprint) compiled successfully")
                                
                                return {
                                    "success": True,
                                    "summary": blueprint
                                }
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get coexistence blueprint via analysis: {e}")
            
            # Fallback: Return a placeholder structure indicating blueprint needs to be generated
            # This happens if there are no workflows/SOPs yet, or if coexistence analysis hasn't been run
            blueprint = {
                "type": "coexistence_blueprint",
                "message": "Coexistence blueprint will be generated when workflows and SOPs are available and coexistence analysis is performed",
                "workflow_count": 0,
                "sop_count": 0
            }
            
            self.logger.info("✅ Operations pillar summary (coexistence blueprint placeholder) compiled")
            
            return {
                "success": True,
                "summary": blueprint
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compile Operations pillar summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "summary": {}
            }
    
    async def _get_data_solution_orchestrator(self):
        """Get Data Solution Orchestrator for data mash queries."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                data_solution = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                if data_solution:
                    return data_solution
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover DataSolutionOrchestratorService: {e}")
        return None
    
    async def handle_request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle HTTP requests for Operations solution.
        
        Routes:
        - POST /workflow-from-sop -> orchestrate_operations_workflow_generation
        - POST /sop-from-workflow -> orchestrate_operations_sop_generation
        - POST /coexistence-analysis -> orchestrate_operations_coexistence_analysis
        - POST /interactive-sop/start -> orchestrate_interactive_sop_creation_start
        - POST /interactive-sop/chat -> orchestrate_interactive_sop_creation_chat
        - POST /interactive-sop/publish -> orchestrate_interactive_sop_creation_publish
        - POST /interactive-blueprint/chat -> orchestrate_interactive_blueprint_creation
        - POST /ai-optimized-blueprint -> orchestrate_ai_optimized_blueprint
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            params: Request parameters
            user_context: Optional user context
        
        Returns:
            Response dictionary
        """
        try:
            # Route to appropriate method based on path
            if path == "workflow-from-sop" and method == "POST":
                return await self.orchestrate_operations_workflow_generation(
                    sop_file_id=params.get("sop_file_id"),
                    sop_content=params.get("sop_content"),
                    workflow_options=params.get("workflow_options"),
                    user_context=user_context
                )
            elif path == "sop-from-workflow" and method == "POST":
                return await self.orchestrate_operations_sop_generation(
                    workflow_file_id=params.get("workflow_file_id"),
                    workflow_content=params.get("workflow_content"),
                    sop_options=params.get("sop_options"),
                    user_context=user_context
                )
            elif path == "coexistence-analysis" and method == "POST":
                return await self.orchestrate_operations_coexistence_analysis(
                    coexistence_content=params.get("coexistence_content"),
                    analysis_options=params.get("analysis_options"),
                    user_context=user_context
                )
            elif path == "interactive-sop/start" and method == "POST":
                return await self.orchestrate_interactive_sop_creation_start(
                    user_context=user_context
                )
            elif path == "interactive-sop/chat" and method == "POST":
                return await self.orchestrate_interactive_sop_creation_chat(
                    user_message=params.get("message"),
                    session_token=params.get("session_token"),
                    user_context=user_context
                )
            elif path == "interactive-sop/publish" and method == "POST":
                return await self.orchestrate_interactive_sop_creation_publish(
                    session_token=params.get("session_token"),
                    user_context=user_context
                )
            elif path == "interactive-blueprint/chat" and method == "POST":
                return await self.orchestrate_interactive_blueprint_creation(
                    user_message=params.get("message"),
                    session_token=params.get("session_token"),
                    user_context=user_context
                )
            elif path == "ai-optimized-blueprint" and method == "POST":
                return await self.orchestrate_ai_optimized_blueprint(
                    sop_file_ids=params.get("sop_file_ids"),
                    workflow_file_ids=params.get("workflow_file_ids"),
                    optimization_options=params.get("optimization_options"),
                    user_context=user_context
                )
            elif path == "workflow-visualization" and method == "POST":
                return await self.orchestrate_workflow_visualization(
                    workflow_file_id=params.get("workflow_file_id"),
                    workflow_content=params.get("workflow_content"),
                    visualization_options=params.get("visualization_options"),
                    user_context=user_context
                )
            elif path == "sop-visualization" and method == "POST":
                return await self.orchestrate_sop_visualization(
                    sop_file_id=params.get("sop_file_id"),
                    sop_content=params.get("sop_content"),
                    visualization_options=params.get("visualization_options"),
                    user_context=user_context
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown route: {method} {path}",
                    "workflow_id": user_context.get("workflow_id") if user_context else None
                }
                
        except Exception as e:
            self.logger.error(f"❌ Request handling failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "handle_request")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": user_context.get("workflow_id") if user_context else None
            }

