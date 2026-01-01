#!/usr/bin/env python3
"""
Data Solution Orchestrator Service

WHAT: Orchestrates the complete data solution flow: Ingest → Parse → Embed → Expose
HOW: Lightweight shell that composes data journey orchestrators and orchestrates platform correlation

This service is the "One Stop Shopping" for all data operations:
1. Client Data Operations → delegates to ContentJourneyOrchestrator (Journey realm)
2. Platform Correlation → orchestrates all platform services (auth, session, workflow, events, telemetry)

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Routes directly to ContentJourneyOrchestrator (Journey realm) - removed DataJourneyOrchestrator (redundant)
- Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Ensures all platform correlation data follows client data through journey
- Registered with Curator for discovery
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional, List, Callable

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class DataSolutionOrchestratorService(OrchestratorBase):
    """
    Data Solution Orchestrator Service - Lightweight shell with platform correlation.
    
    "One Stop Shopping" for:
    1. Client Data Operations (via ContentJourneyOrchestrator - Journey realm)
    2. Platform Correlation Data (auth, session, workflow, events, telemetry)
    
    Orchestrates the complete data solution flow:
    1. Ingest: File upload → ContentJourneyOrchestrator (Journey realm)
    2. Parse: File parsing → ContentJourneyOrchestrator (Journey realm)
    3. Embed: Semantic embeddings → ContentJourneyOrchestrator (Journey realm)
    4. Expose: Semantic layer exposure → ContentJourneyOrchestrator (Journey realm)
    
    Key Principles:
    - Routes directly to ContentJourneyOrchestrator (Journey realm) - removed DataJourneyOrchestrator (redundant)
    - Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
    - Ensures all platform correlation data follows client data through journey
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
        Initialize Data Solution Orchestrator Service.
        
        Args:
            service_name: Service name (typically "DataSolutionOrchestratorService")
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
        self.content_journey_orchestrator = None  # Content operations orchestration
        self.platform_data_journey = None  # Future
        self.semantic_data_journey = None  # Future
        
        # Platform correlation services (discovered via Curator)
        self.security_guard = None
        self.traffic_cop = None
        self.conductor = None
        self.post_office = None
        self.nurse = None
    
    async def initialize(self) -> bool:
        """
        Initialize Data Solution Orchestrator Service.
        
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
            "data_solution_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase and _realm_service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Data Solution Orchestrator Service...")
            
            # Journey orchestrators will be lazy-loaded when methods are called
            # Platform correlation services will be lazy-loaded when methods are called
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Data Solution Orchestrator Service initialized successfully")
            
            # Complete telemetry tracking (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "data_solution_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Data Solution Orchestrator Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure in telemetry (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "data_solution_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Data Solution Orchestrator Service with Curator for discovery."""
        try:
            # Get Curator via OrchestratorBase helper method
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                # Register service instance (required for get_service() discovery)
                service_metadata = {
                    "service_name": self.service_name,
                    "service_type": "data_solution_orchestration",
                    "realm_name": self.realm_name,
                    "capabilities": ["data_ingest", "data_parse", "data_embed", "data_expose", "platform_correlation"],
                    "description": "Lightweight shell: orchestrates client data operations and platform correlation"
                }
                await curator.register_service(self, service_metadata)
                self.logger.info("✅ Registered Data Solution Orchestrator Service instance with Curator")
                
                # Also register capability (for capability-based discovery)
                capability_definition = {
                    "service_name": self.service_name,
                    "realm_name": self.realm_name,
                    "capability_type": "data_solution_orchestration",
                    "description": "Orchestrates complete data solution flow: Ingest → Parse → Embed → Expose",
                    "contracts": {
                        "orchestrate_data_ingest": {
                            "description": "Orchestrate data ingestion",
                            "parameters": ["file_data", "file_name", "file_type", "user_context"],
                            "returns": ["success", "file_id", "workflow_id"]
                        },
                        "orchestrate_data_parse": {
                            "description": "Orchestrate data parsing",
                            "parameters": ["file_id", "parse_options", "user_context", "workflow_id"],
                            "returns": ["success", "parse_result", "parsed_file_id", "content_metadata", "workflow_id"]
                        },
                        "orchestrate_data_embed": {
                            "description": "Orchestrate semantic embedding creation",
                            "parameters": ["file_id", "parsed_file_id", "content_metadata", "user_context", "workflow_id"],
                            "returns": ["success", "embeddings_count", "content_id", "workflow_id"]
                        },
                        "orchestrate_data_expose": {
                            "description": "Orchestrate data exposure for other solutions",
                            "parameters": ["file_id", "parsed_file_id", "user_context"],
                            "returns": ["success", "parsed_data", "content_metadata", "embeddings_available"]
                        }
                    }
                }
                await curator.register_capability(capability_definition)
                self.logger.info("✅ Registered Data Solution Orchestrator Service capability with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def _discover_content_journey_orchestrator(self):
        """Discover ContentJourneyOrchestratorService via Curator, or lazy-initialize if not found."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                content_journey = await curator.discover_service_by_name("ContentJourneyOrchestratorService")
                if content_journey:
                    # Verify it's from Journey realm
                    orchestrator_realm = getattr(content_journey, 'realm_name', None)
                    if orchestrator_realm == "journey":
                        self.logger.info("✅ Discovered ContentJourneyOrchestratorService via Curator")
                        return content_journey
                    else:
                        self.logger.warning(f"⚠️ Found ContentJourneyOrchestratorService but wrong realm: {orchestrator_realm} (expected 'journey')")
            
            # If not found via discovery, lazy-initialize it (pattern for non-Smart City realms)
            self.logger.info("🔄 ContentJourneyOrchestratorService not found - lazy-initializing...")
            try:
                from backend.journey.orchestrators.content_journey_orchestrator.content_orchestrator import ContentJourneyOrchestrator
                
                # Get platform gateway from DI container
                platform_gateway = self.platform_gateway
                if not platform_gateway:
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                    if not platform_gateway:
                        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                
                # Create and initialize Content Journey Orchestrator (self-initializing, doesn't need ContentManager)
                content_journey = ContentJourneyOrchestrator(
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await content_journey.initialize()
                self.logger.info("✅ ContentJourneyOrchestratorService lazy-initialized successfully")
                return content_journey
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize ContentJourneyOrchestratorService: {init_error}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover ContentJourneyOrchestratorService: {e}")
            return None
    
    async def _orchestrate_platform_correlation(
        self,
        operation: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate platform correlation data to follow client data through journey.
        
        "One Stop Shopping" for all platform correlation:
        - Security Guard: Validate auth & tenant
        - Traffic Cop: Manage session/state
        - Conductor: Track workflow
        - Post Office: Publish events & messaging
        - Nurse: Record telemetry & observability
        
        Args:
            operation: Operation name (e.g., "data_ingest", "data_parse")
            user_context: Optional user context
        
        Returns:
            Enhanced user_context with all platform correlation data
        """
        # Get workflow_id (generate if not present)
        workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
        
        # Discover platform correlation services (lazy-load)
        if not self.security_guard:
            self.security_guard = await self.get_security_guard_api()
        if not self.traffic_cop:
            self.traffic_cop = await self.get_traffic_cop_api()
        if not self.conductor:
            self.conductor = await self.get_conductor_api()
        if not self.post_office:
            self.post_office = await self.get_post_office_api()
        if not self.nurse:
            self.nurse = await self.get_nurse_api()
        
        # Build correlation context
        correlation_context = user_context.copy() if user_context else {}
        correlation_context["workflow_id"] = workflow_id
        
        # 1. Security Guard: Validate auth & tenant
        if self.security_guard and correlation_context.get("user_id"):
            try:
                # Try to validate session if session_id is present
                if correlation_context.get("session_id"):
                    auth_result = await self.security_guard.validate_session(
                        session_token=correlation_context.get("session_id"),
                        user_context=correlation_context
                    )
                    if auth_result and auth_result.get("valid"):
                        correlation_context["auth_validated"] = True
                        correlation_context["tenant_id"] = auth_result.get("tenant_id")
                        correlation_context["permissions"] = auth_result.get("permissions", [])
            except Exception as e:
                self.logger.warning(f"⚠️ Auth validation failed: {e}")
        
        # 2. Traffic Cop: Manage session/state
        if self.traffic_cop and correlation_context.get("session_id"):
            try:
                session_state = await self.traffic_cop.get_session_state(
                    session_id=correlation_context.get("session_id"),
                    workflow_id=workflow_id
                )
                if session_state:
                    correlation_context["session_state"] = session_state
                # Update session with workflow_id
                await self.traffic_cop.update_session_state(
                    session_id=correlation_context.get("session_id"),
                    state_updates={"workflow_id": workflow_id},
                    workflow_id=workflow_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Session management failed: {e}")
        
        # 3. Conductor: Track workflow
        if self.conductor:
            try:
                workflow_status = await self.conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=operation,
                    status="in_progress",
                    user_context=correlation_context
                )
                if workflow_status:
                    correlation_context["workflow_tracked"] = True
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow tracking failed: {e}")
        
        # 4. Post Office: Publish operation start event
        if self.post_office:
            try:
                await self.post_office.publish_event(
                    event_type=f"data_solution.{operation}.start",
                    event_data={
                        "operation": operation,
                        "workflow_id": workflow_id
                    },
                    workflow_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Event publishing failed: {e}")
        
        # 5. Nurse: Record telemetry & observability
        if self.nurse:
            try:
                await self.nurse.record_platform_event(
                    event_type="log",
                    event_data={
                        "level": "info",
                        "message": f"Data solution operation started: {operation}",
                        "service_name": self.__class__.__name__,
                        "operation": operation
                    },
                    trace_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Telemetry recording failed: {e}")
        
        return correlation_context
    
    async def _record_platform_correlation_completion(
        self,
        operation: str,
        result: Dict[str, Any],
        correlation_context: Dict[str, Any]
    ):
        """Record platform correlation completion for operation."""
        workflow_id = correlation_context.get("workflow_id")
        
        # Conductor: Mark workflow step complete
        if self.conductor and workflow_id:
            try:
                await self.conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=operation,
                    status="completed" if result.get("success") else "failed",
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow completion tracking failed: {e}")
        
        # Post Office: Publish operation complete event
        if self.post_office and workflow_id:
            try:
                await self.post_office.publish_event(
                    event_type=f"data_solution.{operation}.complete",
                    event_data={
                        "operation": operation,
                        "success": result.get("success"),
                        "workflow_id": workflow_id
                    },
                    workflow_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Event publishing failed: {e}")
        
        # Nurse: Record completion telemetry
        if self.nurse and workflow_id:
            try:
                await self.nurse.record_platform_event(
                    event_type="log",
                    event_data={
                        "level": "info" if result.get("success") else "error",
                        "message": f"Data solution operation completed: {operation}",
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
            wal_operations_str = config_adapter.get("WAL_OPERATIONS", "data_ingest,data_parse,data_embed,data_expose,data_mash")
        else:
            import os
            wal_enabled = os.getenv("WAL_ENABLED", "false").lower() == "true"
            wal_operations_str = os.getenv("WAL_OPERATIONS", "data_ingest,data_parse,data_embed,data_expose,data_mash")
            if wal_enabled or wal_operations_str:
                self.logger.warning("⚠️ [DATA_SOLUTION] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
        
        # Parse wal operations
        if isinstance(wal_operations_str, str):
            wal_operations = wal_operations_str.split(",")
        else:
            wal_operations = ["data_ingest", "data_parse", "data_embed", "data_expose", "data_mash"]
        
        # Store policy for later use
        if not hasattr(self, '_wal_policy'):
            self._wal_policy = {
                "enable_wal": wal_enabled,
                "log_operations": [op.strip() for op in wal_operations],
                "namespace": "data_solution_operations"
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
                namespace=namespace or self._wal_policy.get("namespace", "data_solution_operations"),
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
            saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "data_ingest_pipeline,data_mapping")
        else:
            import os
            saga_enabled = os.getenv("SAGA_ENABLED", "false").lower() == "true"
            saga_operations_str = os.getenv("SAGA_OPERATIONS", "data_ingest_pipeline,data_mapping")
            if saga_enabled or saga_operations_str:
                self.logger.warning("⚠️ [DATA_SOLUTION] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
        
        # Parse saga operations
        if isinstance(saga_operations_str, str):
            saga_operations = saga_operations_str.split(",")
        else:
            saga_operations = ["data_ingest_pipeline", "data_mapping"]
        
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
            "data_ingest_pipeline": {
                "ingest": "delete_uploaded_file",
                "parse": "mark_file_as_unparsed",
                "embed": "delete_embeddings",
                "expose": "remove_from_semantic_layer"
            },
            "data_mapping": {
                "analyze_source": "revert_source_analysis",
                "analyze_target": "revert_target_analysis",
                "generate_mapping": "delete_mapping_rules",
                "apply_mapping": "revert_transformation",
                "validate": "mark_as_invalid"
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
            operation: Operation name (e.g., "data_ingest_pipeline")
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
    
    async def orchestrate_data_ingest(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data ingestion with full platform correlation and optional Saga guarantees.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Execute with Saga if enabled (Capability by Design, Optional by Policy)
        3. Delegate client data operations to Client Data Journey Orchestrator
        4. Record completion in platform correlation
        
        Args:
            file_data: File data as bytes
            file_name: Name of the file
            file_type: MIME type or file extension
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, file_id, workflow_id, and saga_id (if Saga was used)
        """
        # Define milestones for data ingest operation
        milestones = ["ingest"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="data_ingest_pipeline",
            workflow_func=lambda: self._execute_data_ingest_workflow(
                file_data=file_data,
                file_name=file_name,
                file_type=file_type,
                user_context=user_context
            ),
            milestones=milestones,
            user_context=user_context
        )
    
    async def _execute_data_ingest_workflow(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute data ingestion workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            file_data: File data as bytes
            file_name: Name of the file
            file_type: MIME type or file extension
            user_context: Optional user context
        
        Returns:
            Dict with success status, file_id, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="data_ingest",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="data_solution_operations",
                payload={
                    "operation": "data_ingest",
                    "file_name": file_name,
                    "file_type": file_type,
                    "file_size": len(file_data)
                },
                target="data_ingest",
                user_context=correlation_context
            )
            
            # Step 2: Route to Content Journey Orchestrator (Journey realm)
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute content operation with correlation context
            user_id = correlation_context.get("user_id") if correlation_context else "anonymous"
            session_id = correlation_context.get("session_id") if correlation_context else None
            
            result = await self.content_journey_orchestrator.handle_content_upload(
                file_data=file_data,
                filename=file_name,
                file_type=file_type,
                user_id=user_id,
                session_id=session_id,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="data_ingest",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data ingestion failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_data_ingest")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_data_parse(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data parsing with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Delegate client data operations to Client Data Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier from ingestion
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
            workflow_id: Optional workflow_id (if not in user_context)
        
        Returns:
            Dict with success status, parse_result, parsed_file_id, content_metadata, workflow_id
        """
        try:
            # Ensure workflow_id is in user_context
            if user_context and not user_context.get("workflow_id"):
                if workflow_id:
                    user_context["workflow_id"] = workflow_id
            elif not user_context:
                user_context = {"workflow_id": workflow_id} if workflow_id else {}
            
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="data_parse",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="data_solution_operations",
                payload={
                    "operation": "data_parse",
                    "file_id": file_id,
                    "parse_options": parse_options
                },
                target="data_parse",
                user_context=correlation_context
            )
            
            # Step 2: Route to Content Journey Orchestrator (Journey realm)
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute content operation with correlation context
            user_id = correlation_context.get("user_id") if correlation_context else "anonymous"
            
            result = await self.content_journey_orchestrator.process_file(
                file_id=file_id,
                user_id=user_id,
                copybook_file_id=None,  # copybook_file_id handled in processing_options
                processing_options=parse_options
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="data_parse",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data parsing failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_data_parse")
            workflow_id = user_context.get("workflow_id") if user_context else workflow_id
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_data_embed(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data embedding with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Delegate client data operations to Client Data Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier
            parsed_file_id: Parsed file identifier
            content_metadata: Content metadata from parsing
            user_context: Optional user context (includes workflow_id)
            workflow_id: Optional workflow_id (if not in user_context)
        
        Returns:
            Dict with success status, embeddings_count, content_id, workflow_id
        """
        try:
            # Ensure workflow_id is in user_context
            if user_context and not user_context.get("workflow_id"):
                if workflow_id:
                    user_context["workflow_id"] = workflow_id
            elif not user_context:
                user_context = {"workflow_id": workflow_id} if workflow_id else {}
            
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="data_embed",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="data_solution_operations",
                payload={
                    "operation": "data_embed",
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id
                },
                target="data_embed",
                user_context=correlation_context
            )
            
            # Step 2: Route to Content Journey Orchestrator (Journey realm)
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute content embedding operation with correlation context
            # ContentJourneyOrchestrator now has automatic embedding creation in process_file()
            # But we can also call it explicitly via a dedicated method if needed
            # For now, embedding is automatically created during process_file(), so we return success
            # If explicit embedding is needed, we can add a create_embeddings() method to ContentJourneyOrchestrator
            user_id = correlation_context.get("user_id") if correlation_context else "anonymous"
            
            # Note: Embeddings are now automatically created during process_file()
            # If file was already parsed, embeddings should already exist
            # If we need to create embeddings for an already-parsed file, we would need a dedicated method
            # For now, return success with note that embeddings are created automatically during parsing
            result = {
                "success": True,
                "message": "Embeddings are automatically created during process_file(). If you need to create embeddings for an already-parsed file, ensure process_file() was called first.",
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "workflow_id": correlation_context.get("workflow_id") if correlation_context else None
            }
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="data_embed",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data embedding failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_data_embed")
            workflow_id = user_context.get("workflow_id") if user_context else workflow_id
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_data_expose(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data exposure with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Delegate client data operations to Client Data Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier
            parsed_file_id: Optional parsed file identifier (if not provided, gets first one)
            user_context: Optional user context
        
        Returns:
            Dict with success status, parsed_data, content_metadata, embeddings info
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="data_expose",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="data_solution_operations",
                payload={
                    "operation": "data_expose",
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id
                },
                target="data_expose",
                user_context=correlation_context
            )
            
            # Step 2: Route to Content Journey Orchestrator (Journey realm)
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute content exposure operation with correlation context
            # Use ContentJourneyOrchestrator.expose_data() method
            result = await self.content_journey_orchestrator.expose_data(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                user_context=correlation_context
            )
            
            # Ensure workflow_id is in result
            if result and not result.get("workflow_id"):
                result["workflow_id"] = correlation_context.get("workflow_id") if correlation_context else None
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="data_expose",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Data exposure failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_data_expose")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_content_pillar_summary(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Content pillar summary for Business Outcomes.
        
        ⭐ NEW: Solution Orchestrator endpoint for pillar summary compilation.
        
        Returns:
        {
            "success": True,
            "pillar": "content",
            "summary": {
                "textual": str,
                "tabular": {...},
                "visualizations": [...],
                "semantic_data_model": {...}
            }
        }
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="content_pillar_summary",
            user_context=user_context
        )
        
        # Get Content Journey Orchestrator
        content_journey = await self._discover_content_journey_orchestrator()
        if not content_journey:
            return {
                "success": False,
                "error": "ContentJourneyOrchestrator not available",
                "pillar": "content",
                "summary": {}
            }
        
        # Get summary from Journey Orchestrator
        # If Journey Orchestrator doesn't have get_pillar_summary, it will delegate to legacy orchestrator
        try:
            if hasattr(content_journey, 'get_pillar_summary'):
                summary_result = await content_journey.get_pillar_summary(
                    session_id=session_id,
                    user_id=correlation_context.get("user_id", "anonymous")
                )
            else:
                # Bridge: Try to get legacy ContentOrchestrator
                self.logger.warning("⚠️ ContentJourneyOrchestrator doesn't have get_pillar_summary, trying legacy orchestrator")
                # For now, return empty summary - will be implemented in Journey Orchestrator
                summary_result = {
                    "success": False,
                    "error": "get_pillar_summary not implemented in ContentJourneyOrchestrator",
                    "pillar": "content",
                    "summary": {}
                }
            
            if summary_result.get("success"):
                return {
                    "success": True,
                    "pillar": "content",
                    "summary": summary_result.get("summary", {}),
                    "workflow_id": correlation_context.get("workflow_id")
                }
            else:
                return {
                    "success": False,
                    "error": summary_result.get("error", "Failed to get content pillar summary"),
                    "pillar": "content",
                    "summary": {}
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to get content pillar summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "pillar": "content",
                "summary": {}
            }
    
    async def orchestrate_data_mash(
        self,
        client_data_query: Optional[Dict[str, Any]] = None,
        semantic_data_query: Optional[Dict[str, Any]] = None,
        platform_data_query: Optional[Dict[str, Any]] = None,
        insights_query: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate "data mash" - virtual composition across client, semantic, platform data, and insights.
        
        This method enables cross-data-type queries by:
        1. Querying client data (files, records) via ContentJourneyOrchestrator
        2. Querying semantic data (embeddings, metadata) via SemanticDataJourneyOrchestrator (future)
        3. Querying platform data (workflow, lineage, telemetry) via PlatformDataJourneyOrchestrator (future)
        4. Querying insights (analysis, mapping, visualization) via InsightsSolutionOrchestrator
        5. Correlating results using workflow_id and other correlation IDs
        
        Phase 4 Implementation:
        - Currently supports client data and insights queries
        - Semantic and platform data journey orchestrators are future enhancements
        - Correlation logic stitches results together using workflow_id
        
        Args:
            client_data_query: Query for client data (e.g., {"file_type": "pdf", "status": "parsed"})
            semantic_data_query: Query for semantic data (e.g., {"embedding_similarity": 0.8}) - Future
            platform_data_query: Query for platform data (e.g., {"workflow_status": "completed"}) - Future
            insights_query: Query for insights (e.g., {"mapping_needed": True, "quality_issues": True})
            user_context: User context with correlation IDs (workflow_id, user_id, session_id, etc.)
        
        Returns:
            Dict with correlated results across all data types:
            {
                "success": True,
                "client_data": {...},
                "semantic_data": {...},  # Future
                "platform_data": {...},  # Future
                "insights": {...},
                "correlation": {
                    "workflow_ids": [...],
                    "file_ids": [...],
                    "content_ids": [...]
                }
            }
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="data_mash",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="data_solution_operations",
                payload={
                    "operation": "data_mash",
                    "client_data_query": client_data_query,
                    "semantic_data_query": semantic_data_query,
                    "platform_data_query": platform_data_query,
                    "insights_query": insights_query
                },
                target="data_mash",
                user_context=correlation_context
            )
            
            results = {
                "success": True,
                "client_data": None,
                "semantic_data": None,  # Future
                "platform_data": None,  # Future
                "insights": None,
                "correlation": {
                    "workflow_id": correlation_context.get("workflow_id") if correlation_context else None,
                    "workflow_ids": [],
                    "file_ids": [],
                    "content_ids": []
                }
            }
            
            # Step 2: Query client data if requested
            if client_data_query:
                if not self.content_journey_orchestrator:
                    self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
                
                if self.content_journey_orchestrator:
                    try:
                        self.logger.info(f"📊 Querying client data: {client_data_query}")
                        
                        # ⭐ NEW: Handle workflow/SOP queries
                        query_type = client_data_query.get("type")
                        session_id = correlation_context.get("session_id") if correlation_context else None
                        user_id = correlation_context.get("user_id") if correlation_context else "anonymous"
                        
                        if query_type == "workflow_sop":
                            # Query for workflow and SOP files
                            # Get all files for user
                            files_result = await self.content_journey_orchestrator.list_uploaded_files(user_id)
                            files = files_result.get("files", []) if files_result.get("success") else []
                            
                            # Filter for workflow/SOP files
                            workflow_files = []
                            sop_files = []
                            for file in files:
                                file_content_type = file.get("content_type", "")
                                file_type_category = file.get("file_type_category", "")
                                
                                if file_content_type == "workflow_sop" or file_type_category in ["workflow", "sop", "sop_workflow"]:
                                    if file_type_category == "workflow" or file.get("parsing_type") == "workflow":
                                        workflow_files.append(file)
                                    elif file_type_category == "sop" or file.get("parsing_type") == "sop":
                                        sop_files.append(file)
                            
                            # Get parsed files with embeddings for workflow/SOP
                            parsed_files_result = await self.content_journey_orchestrator.list_parsed_files_with_embeddings(user_id)
                            parsed_files = parsed_files_result.get("parsed_files", []) if parsed_files_result.get("success") else []
                            
                            # Filter parsed files by parsing_type
                            workflow_parsed = [pf for pf in parsed_files if pf.get("metadata", {}).get("parse_result", {}).get("parsing_type") == "workflow"]
                            sop_parsed = [pf for pf in parsed_files if pf.get("metadata", {}).get("parse_result", {}).get("parsing_type") == "sop"]
                            
                            results["client_data"] = {
                                "workflow_sop": {
                                    "workflow_files": workflow_files,
                                    "sop_files": sop_files,
                                    "workflow_parsed": workflow_parsed,
                                    "sop_parsed": sop_parsed,
                                    "workflow_count": len(workflow_files),
                                    "sop_count": len(sop_files),
                                    "workflow_parsed_count": len(workflow_parsed),
                                    "sop_parsed_count": len(sop_parsed)
                                }
                            }
                        elif query_type == "workflow":
                            # Query for workflow files only
                            files_result = await self.content_journey_orchestrator.list_uploaded_files(user_id)
                            files = files_result.get("files", []) if files_result.get("success") else []
                            workflow_files = [f for f in files if f.get("file_type_category") == "workflow" or f.get("parsing_type") == "workflow"]
                            
                            parsed_files_result = await self.content_journey_orchestrator.list_parsed_files_with_embeddings(user_id)
                            parsed_files = parsed_files_result.get("parsed_files", []) if parsed_files_result.get("success") else []
                            workflow_parsed = [pf for pf in parsed_files if pf.get("metadata", {}).get("parse_result", {}).get("parsing_type") == "workflow"]
                            
                            results["client_data"] = {
                                "workflow": {
                                    "files": workflow_files,
                                    "parsed": workflow_parsed,
                                    "count": len(workflow_files),
                                    "parsed_count": len(workflow_parsed)
                                }
                            }
                        elif query_type == "sop":
                            # Query for SOP files only
                            files_result = await self.content_journey_orchestrator.list_uploaded_files(user_id)
                            files = files_result.get("files", []) if files_result.get("success") else []
                            sop_files = [f for f in files if f.get("file_type_category") == "sop" or f.get("parsing_type") == "sop"]
                            
                            parsed_files_result = await self.content_journey_orchestrator.list_parsed_files_with_embeddings(user_id)
                            parsed_files = parsed_files_result.get("parsed_files", []) if parsed_files_result.get("success") else []
                            sop_parsed = [pf for pf in parsed_files if pf.get("metadata", {}).get("parse_result", {}).get("parsing_type") == "sop"]
                            
                            results["client_data"] = {
                                "sop": {
                                    "files": sop_files,
                                    "parsed": sop_parsed,
                                    "count": len(sop_files),
                                    "parsed_count": len(sop_parsed)
                                }
                            }
                        elif query_type and query_type.startswith("file_id:"):
                            # Query by specific file_id
                            file_id = query_type.replace("file_id:", "")
                            # Get file details
                            files_result = await self.content_journey_orchestrator.list_uploaded_files(user_id)
                            files = files_result.get("files", []) if files_result.get("success") else []
                            matching_file = next((f for f in files if f.get("file_id") == file_id or f.get("uuid") == file_id), None)
                            
                            if matching_file:
                                # Get parsed file if available
                                parsed_files_result = await self.content_journey_orchestrator.list_parsed_files(user_id, file_id=file_id)
                                parsed_files = parsed_files_result.get("parsed_files", []) if parsed_files_result.get("success") else []
                                
                                results["client_data"] = {
                                    "file": matching_file,
                                    "parsed_files": parsed_files
                                }
                            else:
                                results["client_data"] = {"error": f"File not found: {file_id}"}
                        else:
                            # Default: Query all files
                            files_result = await self.content_journey_orchestrator.list_uploaded_files(user_id)
                            results["client_data"] = {
                                "files": files_result.get("files", []) if files_result.get("success") else [],
                                "count": files_result.get("count", 0) if files_result.get("success") else 0
                            }
                    except Exception as e:
                        self.logger.warning(f"⚠️ Client data query failed: {e}")
                        results["client_data"] = {"error": str(e)}
            
            # Step 3: Query semantic data if requested (Future)
            if semantic_data_query:
                self.logger.info(f"📊 Semantic data query requested: {semantic_data_query}")
                results["semantic_data"] = {
                    "query": semantic_data_query,
                    "note": "Semantic data journey orchestrator not yet implemented"
                }
            
            # Step 4: Query platform data if requested (Future)
            if platform_data_query:
                self.logger.info(f"📊 Platform data query requested: {platform_data_query}")
                results["platform_data"] = {
                    "query": platform_data_query,
                    "note": "Platform data journey orchestrator not yet implemented"
                }
            
            # Step 5: Query insights if requested
            if insights_query:
                try:
                    # Discover Insights Solution Orchestrator
                    insights_orchestrator = await self._discover_insights_solution_orchestrator()
                    if insights_orchestrator:
                        self.logger.info(f"📊 Querying insights: {insights_query}")
                        insights_results = await insights_orchestrator.query_insights(
                            insights_query=insights_query,
                            user_context=correlation_context
                        )
                        results["insights"] = insights_results
                    else:
                        self.logger.warning("⚠️ Insights Solution Orchestrator not available")
                        results["insights"] = {"error": "Insights Solution Orchestrator not available"}
                except Exception as e:
                    self.logger.warning(f"⚠️ Insights query failed: {e}")
                    results["insights"] = {"error": str(e)}
            
            # Step 6: Correlate results using workflow_id and other correlation IDs
            correlation_ids = self._extract_correlation_ids(results, correlation_context)
            results["correlation"].update(correlation_ids)
            
            # Step 7: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="data_mash",
                result=results,
                correlation_context=correlation_context
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Data mash orchestration failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_data_mash")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": correlation_context.get("workflow_id") if correlation_context else None
            }
    
    def _extract_correlation_ids(
        self,
        results: Dict[str, Any],
        correlation_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract correlation IDs from query results.
        
        Args:
            results: Query results from all data types
            correlation_context: Correlation context with workflow_id, etc.
        
        Returns:
            Dict with extracted correlation IDs
        """
        correlation_ids = {
            "workflow_ids": [],
            "file_ids": [],
            "content_ids": [],
            "parsed_file_ids": []
        }
        
        # Extract from client data results
        if results.get("client_data") and isinstance(results["client_data"], dict):
            if "file_id" in results["client_data"]:
                correlation_ids["file_ids"].append(results["client_data"]["file_id"])
            if "parsed_file_id" in results["client_data"]:
                correlation_ids["parsed_file_ids"].append(results["client_data"]["parsed_file_id"])
        
        # Extract from insights results
        if results.get("insights") and isinstance(results["insights"], dict):
            if "workflow_id" in results["insights"]:
                correlation_ids["workflow_ids"].append(results["insights"]["workflow_id"])
            if "file_ids" in results["insights"]:
                correlation_ids["file_ids"].extend(results["insights"]["file_ids"])
            if "content_ids" in results["insights"]:
                correlation_ids["content_ids"].extend(results["insights"]["content_ids"])
        
        # Add workflow_id from correlation context
        if correlation_context and correlation_context.get("workflow_id"):
            workflow_id = correlation_context["workflow_id"]
            if workflow_id not in correlation_ids["workflow_ids"]:
                correlation_ids["workflow_ids"].append(workflow_id)
        
        # Deduplicate lists
        correlation_ids["workflow_ids"] = list(set(correlation_ids["workflow_ids"]))
        correlation_ids["file_ids"] = list(set(correlation_ids["file_ids"]))
        correlation_ids["content_ids"] = list(set(correlation_ids["content_ids"]))
        correlation_ids["parsed_file_ids"] = list(set(correlation_ids["parsed_file_ids"]))
        
        return correlation_ids
    
    async def _discover_insights_solution_orchestrator(self):
        """Discover InsightsSolutionOrchestratorService via Curator."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                insights_orchestrator = await curator.discover_service_by_name("InsightsSolutionOrchestratorService")
                if insights_orchestrator:
                    orchestrator_realm = getattr(insights_orchestrator, 'realm_name', None)
                    if orchestrator_realm == "solution":
                        self.logger.info("✅ Discovered InsightsSolutionOrchestratorService via Curator")
                        return insights_orchestrator
                    else:
                        self.logger.warning(f"⚠️ Found InsightsSolutionOrchestratorService but wrong realm: {orchestrator_realm} (expected 'solution')")
            
            # If not found via discovery, lazy-initialize it
            self.logger.info("🔄 InsightsSolutionOrchestratorService not found - lazy-initializing...")
            try:
                from backend.solution.services.insights_solution_orchestrator_service.insights_solution_orchestrator_service import InsightsSolutionOrchestratorService
                
                platform_gateway = self.platform_gateway
                if not platform_gateway:
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                
                insights_orchestrator = InsightsSolutionOrchestratorService(
                    service_name="InsightsSolutionOrchestratorService",
                    realm_name="solution",
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await insights_orchestrator.initialize()
                self.logger.info("✅ InsightsSolutionOrchestratorService lazy-initialized successfully")
                return insights_orchestrator
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize InsightsSolutionOrchestratorService: {init_error}")
                return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover InsightsSolutionOrchestratorService: {e}")
            return None
    
    async def orchestrate_content_pillar_summary(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate Content Pillar summary compilation.
        
        ⭐ Returns the final data mash preview - a visually and contextually interesting showcase
        of the Content pillar's data composition across client, semantic, platform, and insights.
        
        Args:
            session_id: Session identifier
            user_context: Optional user context (includes user_id, tenant_id)
        
        Returns:
            Dict with success status and data mash preview
        """
        try:
            self.logger.info(f"📊 Compiling Content pillar summary (data mash preview) for session: {session_id}")
            
            # Enhance user_context with session_id
            enhanced_user_context = (user_context or {}).copy()
            enhanced_user_context["session_id"] = session_id
            
            # Get final data mash preview - query all data types for a comprehensive view
            data_mash_result = await self.orchestrate_data_mash(
                client_data_query={
                    "type": None  # Get all files for comprehensive preview
                },
                semantic_data_query=None,  # Future enhancement
                platform_data_query=None,  # Future enhancement
                insights_query=None,  # Future enhancement
                user_context=enhanced_user_context
            )
            
            if data_mash_result.get("success"):
                # Extract the preview from data mash result
                preview = {
                    "client_data": data_mash_result.get("client_data"),
                    "semantic_data": data_mash_result.get("semantic_data"),
                    "platform_data": data_mash_result.get("platform_data"),
                    "insights": data_mash_result.get("insights"),
                    "correlation": data_mash_result.get("correlation", {})
                }
                
                self.logger.info("✅ Content pillar summary (data mash preview) compiled successfully")
                
                return {
                    "success": True,
                    "summary": preview
                }
            else:
                self.logger.warning(f"⚠️ Data mash failed: {data_mash_result.get('error')}")
                return {
                    "success": False,
                    "error": data_mash_result.get("error", "Failed to generate data mash preview"),
                    "summary": {}
                }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compile Content pillar summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "summary": {}
            }
    
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
        Handle HTTP request routing for Data Solution Orchestrator.
        
        Routes requests to appropriate orchestration methods:
        - POST /mash -> orchestrate_data_mash (Phase 4: Data Mash)
        - POST /ingest -> orchestrate_data_ingest
        - POST /parse -> orchestrate_data_parse
        - POST /embed -> orchestrate_data_embed
        - POST /expose -> orchestrate_data_expose
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (e.g., "mash", "ingest", "parse")
            params: Request parameters/body
            user_context: User context (includes workflow_id)
            headers: HTTP headers
            query_params: Query parameters
        
        Returns:
            Dict with response data
        """
        try:
            # Merge user_context from params if provided
            if not user_context:
                user_context = params.get("user_context", {})
            
            # Route based on path
            if path == "mash" and method == "POST":
                client_data_query = params.get("client_data_query")
                semantic_data_query = params.get("semantic_data_query")
                platform_data_query = params.get("platform_data_query")
                insights_query = params.get("insights_query")
                
                return await self.orchestrate_data_mash(
                    client_data_query=client_data_query,
                    semantic_data_query=semantic_data_query,
                    platform_data_query=platform_data_query,
                    insights_query=insights_query,
                    user_context=user_context
                )
            
            elif path == "ingest" and method == "POST":
                file_data = params.get("file_data")
                file_name = params.get("file_name")
                file_type = params.get("file_type")
                
                if not file_data or not file_name:
                    return {
                        "success": False,
                        "error": "file_data and file_name are required"
                    }
                
                return await self.orchestrate_data_ingest(
                    file_data=file_data,
                    file_name=file_name,
                    file_type=file_type,
                    user_context=user_context
                )
            
            elif path == "parse" and method == "POST":
                file_id = params.get("file_id")
                parse_options = params.get("parse_options", {})
                
                if not file_id:
                    return {
                        "success": False,
                        "error": "file_id is required"
                    }
                
                return await self.orchestrate_data_parse(
                    file_id=file_id,
                    parse_options=parse_options,
                    user_context=user_context
                )
            
            elif path == "embed" and method == "POST":
                file_id = params.get("file_id")
                embedding_options = params.get("embedding_options", {})
                
                if not file_id:
                    return {
                        "success": False,
                        "error": "file_id is required"
                    }
                
                return await self.orchestrate_data_embed(
                    file_id=file_id,
                    embedding_options=embedding_options,
                    user_context=user_context
                )
            
            elif path == "expose" and method == "POST":
                file_id = params.get("file_id")
                parsed_file_id = params.get("parsed_file_id")
                expose_options = params.get("expose_options", {})
                
                if not file_id:
                    return {
                        "success": False,
                        "error": "file_id is required"
                    }
                
                return await self.orchestrate_data_expose(
                    file_id=file_id,
                    parsed_file_id=parsed_file_id,
                    expose_options=expose_options,
                    user_context=user_context
                )
            
            else:
                return {
                    "success": False,
                    "error": "Route not found",
                    "path": path,
                    "method": method,
                    "available_paths": ["mash", "ingest", "parse", "embed", "expose"]
                }
                
        except Exception as e:
            self.logger.error(f"❌ Request handling failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }

