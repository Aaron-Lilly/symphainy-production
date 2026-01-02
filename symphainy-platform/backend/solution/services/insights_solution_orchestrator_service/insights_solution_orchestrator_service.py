#!/usr/bin/env python3
"""
Insights Solution Orchestrator Service

WHAT: Orchestrates insights operations with platform correlation
HOW: Lightweight shell that composes insights journey orchestrators and orchestrates platform correlation

This service is the "One Stop Shopping" for all insights operations:
1. Insights Operations → delegates to InsightsJourneyOrchestrator (Journey realm)
2. Platform Correlation → orchestrates all platform services (auth, session, workflow, events, telemetry)

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Routes to InsightsJourneyOrchestrator (Journey realm)
- Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Ensures all platform correlation data follows insights operations through journey
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


class InsightsSolutionOrchestratorService(OrchestratorBase):
    """
    Insights Solution Orchestrator Service - Lightweight shell with platform correlation.
    
    "One Stop Shopping" for:
    1. Insights Operations (via InsightsJourneyOrchestratorService)
    2. Platform Correlation Data (auth, session, workflow, events, telemetry)
    
    Orchestrates insights operations:
    1. Data Mapping: Map source files to target schemas
    2. Data Analysis: Analyze data for insights
    3. Quality Validation: Validate data quality
    4. Cleanup Actions: Generate cleanup recommendations
    
    Key Principles:
    - Routes to InsightsJourneyOrchestrator (Journey realm)
    - Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
    - Ensures all platform correlation data follows insights operations through journey
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
        Initialize Insights Solution Orchestrator Service.
        
        Args:
            service_name: Service name (typically "InsightsSolutionOrchestratorService")
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
        self.insights_journey_orchestrator = None  # Insights operations orchestration
        
        # Platform correlation services (discovered via Curator)
        self.security_guard = None
        self.traffic_cop = None
        self.conductor = None
        self.post_office = None
        self.nurse = None
    
    async def initialize(self) -> bool:
        """
        Initialize Insights Solution Orchestrator Service.
        
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
            "insights_solution_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase and _realm_service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Insights Solution Orchestrator Service...")
            
            # Journey orchestrators will be lazy-loaded when methods are called
            # Platform correlation services will be lazy-loaded when methods are called
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Insights Solution Orchestrator Service initialized successfully")
            
            # Complete telemetry tracking (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "insights_solution_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Insights Solution Orchestrator Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure in telemetry (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "insights_solution_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Insights Solution Orchestrator Service with Curator for discovery."""
        try:
            # Get Curator via OrchestratorBase helper method
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                # Register service instance (required for get_service() discovery)
                service_metadata = {
                    "service_name": self.service_name,
                    "service_type": "insights_solution_orchestration",
                    "realm_name": self.realm_name,
                    "capabilities": ["data_mapping", "data_analysis", "eda_analysis", "vark_analysis", "business_summary", "unstructured_analysis", "visualization", "quality_validation", "cleanup_actions", "platform_correlation"],
                    "description": "Lightweight shell: orchestrates insights operations and platform correlation"
                }
                await curator.register_service(self, service_metadata)
                self.logger.info("✅ Registered Insights Solution Orchestrator Service instance with Curator")
                
                # Also register capability (for capability-based discovery)
                capability_definition = {
                    "service_name": self.service_name,
                    "realm_name": self.realm_name,
                    "capability_type": "insights_solution_orchestration",
                    "description": "Orchestrates insights operations: Data Mapping, Analysis, Quality Validation",
                    "contracts": {
                        "orchestrate_insights_mapping": {
                            "description": "Orchestrate data mapping from source to target",
                            "parameters": ["source_file_id", "target_file_id", "mapping_options", "user_context"],
                            "returns": ["success", "mapping_id", "mapping_results", "workflow_id"]
                        },
                        "orchestrate_insights_analysis": {
                            "description": "Orchestrate insights analysis (EDA, VARK, business summary, unstructured)",
                            "parameters": ["file_id", "analysis_type", "analysis_options", "user_context"],
                            "returns": ["success", "analysis_id", "analysis_results", "workflow_id"]
                        },
                        "orchestrate_insights_visualization": {
                            "description": "Orchestrate visualization generation",
                            "parameters": ["content_id", "visualization_options", "user_context"],
                            "returns": ["success", "visualization_id", "visualization_data", "workflow_id"]
                        }
                    }
                }
                await curator.register_capability(capability_definition)
                self.logger.info("✅ Registered Insights Solution Orchestrator Service capability with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def _discover_insights_journey_orchestrator(self):
        """Discover InsightsJourneyOrchestratorService via Curator, or lazy-initialize if not found."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                insights_journey = await curator.discover_service_by_name("InsightsJourneyOrchestratorService")
                if insights_journey:
                    # Verify it's from Journey realm
                    orchestrator_realm = getattr(insights_journey, 'realm_name', None)
                    if orchestrator_realm == "journey":
                        self.logger.info("✅ Discovered InsightsJourneyOrchestratorService via Curator")
                        return insights_journey
                    else:
                        self.logger.warning(f"⚠️ Found InsightsJourneyOrchestratorService but wrong realm: {orchestrator_realm} (expected 'journey')")
            
            # If not found via discovery, lazy-initialize it (pattern for non-Smart City realms)
            self.logger.info("🔄 InsightsJourneyOrchestratorService not found - lazy-initializing...")
            try:
                from backend.journey.orchestrators.insights_journey_orchestrator.insights_journey_orchestrator import InsightsJourneyOrchestrator
                
                # Get platform gateway from DI container
                platform_gateway = self.platform_gateway
                if not platform_gateway:
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                    if not platform_gateway:
                        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                
                # Create and initialize Insights Journey Orchestrator (self-initializing)
                insights_journey = InsightsJourneyOrchestrator(
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await insights_journey.initialize()
                self.logger.info("✅ InsightsJourneyOrchestratorService lazy-initialized successfully")
                return insights_journey
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize InsightsJourneyOrchestratorService: {init_error}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover InsightsJourneyOrchestratorService: {e}")
            return None
    
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
            operation: Operation name (e.g., "insights_mapping")
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Correlation context with user_id, session_id, workflow_id, etc.
        """
        correlation_context = {}
        
        # ✅ Preserve workflow_id from user_context if provided (for end-to-end correlation)
        # Only generate new UUID if workflow_id is not already present
        if user_context and user_context.get("workflow_id"):
            workflow_id = user_context.get("workflow_id")
        else:
            # Generate new workflow_id only if not provided
            workflow_id = str(uuid.uuid4())
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
        
        # Traffic Cop: Session management
        if not self.traffic_cop:
            self.traffic_cop = await self.get_foundation_service("TrafficCopService")
        
        if self.traffic_cop and user_context:
            try:
                session_id = user_context.get("session_id")
                if session_id:
                    # Get or create session state
                    session_state = await self.traffic_cop.get_session_state(session_id)
                    if session_state:
                        correlation_context["session_id"] = session_id
                        correlation_context["session_state"] = session_state
            except Exception as e:
                self.logger.warning(f"⚠️ Traffic Cop session management failed: {e}")
        
        # Conductor: Workflow tracking
        if not self.conductor:
            self.conductor = await self.get_foundation_service("ConductorService")
        
        if self.conductor and workflow_id:
            try:
                # Start workflow tracking
                await self.conductor.start_workflow(
                    workflow_id=workflow_id,
                    workflow_type="insights_operation",
                    operation=operation,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Conductor workflow tracking failed: {e}")
        
        return correlation_context
    
    async def _record_platform_correlation_completion(
        self,
        operation: str,
        result: Dict[str, Any],
        correlation_context: Dict[str, Any]
    ):
        """Record completion in platform correlation services."""
        workflow_id = correlation_context.get("workflow_id")
        
        # Conductor: Complete workflow tracking
        if self.conductor and workflow_id:
            try:
                await self.conductor.complete_workflow(
                    workflow_id=workflow_id,
                    success=result.get("success", False),
                    result_data=result
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Conductor workflow completion failed: {e}")
        
        # Post Office: Publish completion event
        if not self.post_office:
            self.post_office = await self.get_foundation_service("PostOfficeService")
        
        if self.post_office and workflow_id:
            try:
                await self.post_office.publish_event(
                    event_type="insights_operation_complete",
                    event_data={
                        "operation": operation,
                        "success": result.get("success", False),
                        "result": result
                    },
                    workflow_id=workflow_id,
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
                        "message": f"Insights solution operation completed: {operation}",
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
        # Get from ConfigAdapter (required)
        config_adapter = self._get_config_adapter()
        wal_enabled = config_adapter.get("WAL_ENABLED", "false")
        if isinstance(wal_enabled, str):
            wal_enabled = wal_enabled.lower() == "true"
        else:
            wal_enabled = bool(wal_enabled)
        wal_operations_str = config_adapter.get("WAL_OPERATIONS", "insights_mapping,insights_analysis,insights_visualization")
        
        # Parse wal operations
        if isinstance(wal_operations_str, str):
            wal_operations = wal_operations_str.split(",")
        else:
            wal_operations = ["insights_mapping", "insights_analysis", "insights_visualization"]
        
        # Store policy for later use
        if not hasattr(self, '_wal_policy'):
            self._wal_policy = {
                "enable_wal": wal_enabled,
                "log_operations": [op.strip() for op in wal_operations],
                "namespace": "insights_solution_operations"
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
                namespace=namespace or self._wal_policy.get("namespace", "insights_solution_operations"),
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
        
        # Fallback to ConfigAdapter if PolicyConfigurationService not available
        config_adapter = self._get_config_adapter()
        saga_enabled = config_adapter.get("SAGA_ENABLED", "false")
        if isinstance(saga_enabled, str):
            saga_enabled = saga_enabled.lower() == "true"
        else:
            saga_enabled = bool(saga_enabled)
        saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "data_mapping")
        
        # Parse saga operations
        if isinstance(saga_operations_str, str):
            saga_operations = saga_operations_str.split(",")
        else:
            saga_operations = ["data_mapping"]
        
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
            operation: Operation name (e.g., "data_mapping")
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
    
    async def orchestrate_insights_mapping(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data mapping with full platform correlation and optional Saga guarantees.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Execute with Saga if enabled (Capability by Design, Optional by Policy)
        3. Route to Insights Journey Orchestrator
        4. Record completion in platform correlation
        
        Args:
            source_file_id: Source file identifier
            target_file_id: Target file identifier
            mapping_options: Optional mapping configuration
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, mapping_id, mapping_results, workflow_id, and saga_id (if Saga was used)
        """
        # Define milestones for data mapping operation
        milestones = ["analyze_source", "analyze_target", "generate_mapping", "apply_mapping", "validate"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="data_mapping",
            workflow_func=lambda: self._execute_insights_mapping_workflow(
                source_file_id=source_file_id,
                target_file_id=target_file_id,
                mapping_options=mapping_options,
                user_context=user_context
            ),
            milestones=milestones,
            user_context=user_context
        )
    
    async def _execute_insights_mapping_workflow(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute insights mapping workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            source_file_id: Source file identifier
            target_file_id: Target file identifier
            mapping_options: Optional mapping configuration
            user_context: Optional user context
        
        Returns:
            Dict with success status, mapping_id, mapping_results, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="insights_mapping",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="insights_solution_operations",
                payload={
                    "operation": "insights_mapping",
                    "source_file_id": source_file_id,
                    "target_file_id": target_file_id,
                    "mapping_options": mapping_options
                },
                target="insights_mapping",
                user_context=correlation_context
            )
            
            # Step 2: Route to Insights Journey Orchestrator (Journey realm)
            if not self.insights_journey_orchestrator:
                self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
            
            if not self.insights_journey_orchestrator:
                raise ValueError("InsightsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute mapping operation with correlation context
            result = await self.insights_journey_orchestrator.execute_data_mapping_workflow(
                source_file_id=source_file_id,
                target_file_id=target_file_id,
                mapping_options=mapping_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="insights_mapping",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights mapping failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_insights_mapping")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_insights_analysis(
        self,
        file_id: str,
        analysis_type: str,
        analysis_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate insights analysis with full platform correlation.
        
        Supports analysis types:
        - "eda": Exploratory Data Analysis
        - "vark": VARK learning style analysis
        - "business_summary": Business narrative summary
        - "unstructured": Unstructured document analysis
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Route to Insights Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier
            analysis_type: Type of analysis ("eda", "vark", "business_summary", "unstructured")
            analysis_options: Optional analysis configuration
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, analysis_id, analysis_results, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation=f"insights_analysis_{analysis_type}",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="insights_solution_operations",
                payload={
                    "operation": "insights_analysis",
                    "analysis_type": analysis_type,
                    "file_id": file_id,
                    "analysis_options": analysis_options
                },
                target="insights_analysis",
                user_context=correlation_context
            )
            
            # Step 2: Route to Insights Journey Orchestrator (Journey realm)
            if not self.insights_journey_orchestrator:
                self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
            
            if not self.insights_journey_orchestrator:
                raise ValueError("InsightsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute analysis operation with correlation context
            # ✅ Extract content_id from request if provided (for EDA analysis which requires embeddings)
            enhanced_analysis_options = (analysis_options or {}).copy()
            # content_id can come from the request body (passed through from frontend)
            # We'll check if it's in the request params that were passed to handle_request
            # For now, we'll rely on it being in analysis_options if provided
            
            result = await self.insights_journey_orchestrator.execute_analysis_workflow(
                file_id=file_id,
                analysis_type=analysis_type,
                analysis_options=enhanced_analysis_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation=f"insights_analysis_{analysis_type}",
                result=result,
                correlation_context=correlation_context
            )
            
            # ✅ Ensure workflow_id from correlation_context is in the result (for end-to-end correlation)
            if correlation_context.get("workflow_id") and not result.get("workflow_id"):
                result["workflow_id"] = correlation_context.get("workflow_id")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights analysis failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_insights_analysis")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_insights_pillar_summary(
        self,
        session_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Insights pillar summary for Business Outcomes.
        
        ⭐ NEW: Solution Orchestrator endpoint for pillar summary compilation.
        
        Returns:
        {
            "success": True,
            "pillar": "insights",
            "summary": {
                "textual": str,
                "tabular": {...},
                "visualizations": [...]
            }
        }
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="insights_pillar_summary",
            user_context=user_context
        )
        
        # Get Insights Journey Orchestrator
        if not self.insights_journey_orchestrator:
            self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
        
        if not self.insights_journey_orchestrator:
            return {
                "success": False,
                "error": "InsightsJourneyOrchestrator not available",
                "pillar": "insights",
                "summary": {}
            }
        
        # Get summary from Journey Orchestrator
        try:
            if hasattr(self.insights_journey_orchestrator, 'get_pillar_summary'):
                summary_result = await self.insights_journey_orchestrator.get_pillar_summary(
                    analysis_id=analysis_id
                )
            else:
                # Bridge: Try to get legacy InsightsOrchestrator
                self.logger.warning("⚠️ InsightsJourneyOrchestrator doesn't have get_pillar_summary, trying legacy orchestrator")
                summary_result = {
                    "success": False,
                    "error": "get_pillar_summary not implemented in InsightsJourneyOrchestrator",
                    "pillar": "insights",
                    "summary": {}
                }
            
            if summary_result.get("success"):
                return {
                    "success": True,
                    "pillar": "insights",
                    "summary": summary_result.get("summary", {}),
                    "workflow_id": correlation_context.get("workflow_id")
                }
            else:
                return {
                    "success": False,
                    "error": summary_result.get("error", "Failed to get insights pillar summary"),
                    "pillar": "insights",
                    "summary": {}
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to get insights pillar summary: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "pillar": "insights",
                "summary": {}
            }
    
    async def orchestrate_insights_visualization(
        self,
        content_id: str,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate visualization generation with full platform correlation.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Route to Insights Journey Orchestrator
        3. Record completion in platform correlation
        
        Args:
            content_id: Content metadata identifier
            visualization_options: Optional visualization configuration
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, visualization_id, visualization_data, and workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="insights_visualization",
                user_context=user_context
            )
            
            # ⭐ WAL logging (if enabled via policy)
            await self._write_to_wal(
                namespace="insights_solution_operations",
                payload={
                    "operation": "insights_visualization",
                    "content_id": content_id,
                    "visualization_options": visualization_options
                },
                target="insights_visualization",
                user_context=correlation_context
            )
            
            # Step 2: Route to Insights Journey Orchestrator (Journey realm)
            if not self.insights_journey_orchestrator:
                self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
            
            if not self.insights_journey_orchestrator:
                raise ValueError("InsightsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute visualization operation with correlation context
            result = await self.insights_journey_orchestrator.execute_visualization_workflow(
                content_id=content_id,
                visualization_options=visualization_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="insights_visualization",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights visualization failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_insights_visualization")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_insights_data_quality(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        quality_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate holistic data quality evaluation.
        
        This method:
        1. Orchestrates platform correlation
        2. Routes to InsightsJourneyOrchestrator for data quality evaluation
        3. Returns comprehensive quality report with validation rules, metrics, and recommendations
        
        Args:
            file_id: File identifier
            parsed_file_id: Optional parsed file identifier
            quality_options: Optional quality evaluation options
            user_context: Optional user context
        
        Returns:
            Dict with quality report
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="insights_data_quality",
                user_context=user_context
            )
            
            # Step 2: Route to Insights Journey Orchestrator
            if not self.insights_journey_orchestrator:
                self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
            
            if not self.insights_journey_orchestrator:
                raise ValueError("InsightsJourneyOrchestratorService not available")
            
            # Step 3: Execute data quality evaluation workflow
            result = await self.insights_journey_orchestrator.execute_data_quality_evaluation_workflow(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                quality_options=quality_options,
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="insights_data_quality",
                result=result,
                correlation_context=correlation_context
            )
            
            # Step 5: Write to WAL if enabled
            if await self._wal_enabled():
                await self._write_to_wal(
                    operation="insights_data_quality",
                    file_id=file_id,
                    parsed_file_id=parsed_file_id,
                    result=result,
                    user_context=correlation_context
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights data quality evaluation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_insights_data_quality")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def query_insights(
        self,
        insights_query: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query insights across all three data types (client, semantic, platform).
        
        This method enables cross-data-type queries for insights operations:
        - Find all mappings for files with quality issues
        - Find all analyses for files with low confidence scores
        - Find all visualizations for workflows with errors
        - Find all insights correlated with specific workflow_ids, file_ids, or content_ids
        
        Phase 4 Implementation:
        - Queries insights data via InsightsJourneyOrchestrator
        - Composes client data, semantic data, and platform data through data mash
        - Correlates results using workflow_id and other correlation IDs
        
        Args:
            insights_query: Query specification (e.g., {
                "mapping_needed": True,
                "quality_issues": True,
                "workflow_ids": ["workflow_123"],
                "file_ids": ["file_456"],
                "content_ids": ["content_789"]
            })
            user_context: User context with correlation IDs (workflow_id, user_id, session_id, etc.)
        
        Returns:
            Dict with query results:
            {
                "success": True,
                "insights": {
                    "mappings": [...],
                    "analyses": [...],
                    "visualizations": [...]
                },
                "correlation": {
                    "workflow_ids": [...],
                    "file_ids": [...],
                    "content_ids": [...]
                },
                "workflow_id": "..."
            }
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="query_insights",
                user_context=user_context
            )
            
            # Step 2: Route to Insights Journey Orchestrator (Journey realm)
            if not self.insights_journey_orchestrator:
                self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
            
            if not self.insights_journey_orchestrator:
                raise ValueError("InsightsJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute insights query with data mash composition
            # The journey orchestrator will compose client, semantic, and platform data
            result = await self.insights_journey_orchestrator.query_insights_with_data_mash(
                insights_query=insights_query,
                user_context=correlation_context
            )
            
            # Step 4: Extract correlation IDs from results
            correlation_ids = {
                "workflow_ids": [],
                "file_ids": [],
                "content_ids": []
            }
            
            # Extract workflow_ids
            if correlation_context and correlation_context.get("workflow_id"):
                correlation_ids["workflow_ids"].append(correlation_context["workflow_id"])
            
            # Extract from query results
            if isinstance(result, dict):
                if "workflow_id" in result:
                    if result["workflow_id"] not in correlation_ids["workflow_ids"]:
                        correlation_ids["workflow_ids"].append(result["workflow_id"])
                if "workflow_ids" in result:
                    correlation_ids["workflow_ids"].extend(result["workflow_ids"])
                if "file_ids" in result:
                    correlation_ids["file_ids"].extend(result["file_ids"])
                if "content_ids" in result:
                    correlation_ids["content_ids"].extend(result["content_ids"])
            
            # Deduplicate
            correlation_ids["workflow_ids"] = list(set(correlation_ids["workflow_ids"]))
            correlation_ids["file_ids"] = list(set(correlation_ids["file_ids"]))
            correlation_ids["content_ids"] = list(set(correlation_ids["content_ids"]))
            
            # Add correlation to result
            if isinstance(result, dict):
                result["correlation"] = correlation_ids
                result["workflow_id"] = correlation_context.get("workflow_id") if correlation_context else None
            
            # Step 5: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="query_insights",
                result=result,
                correlation_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Insights query failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "query_insights")
            workflow_id = user_context.get("workflow_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_insights_pillar_summary(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate Insights Pillar summary compilation.
        
        ⭐ Uses orchestrate_summary to select the most appropriate and interesting output
        from available realm/pillar outputs (structured insights, unstructured insights, AAR, data map).
        Returns a visually and contextually interesting showcase.
        
        Args:
            session_id: Session identifier
            user_context: Optional user context (includes user_id, tenant_id)
        
        Returns:
            Dict with success status and selected showcase output
        """
        try:
            self.logger.info(f"📊 Compiling Insights pillar summary (orchestrate_summary) for session: {session_id}")
            
            # Get Insights Journey Orchestrator
            if not self.insights_journey_orchestrator:
                self.insights_journey_orchestrator = await self._discover_insights_journey_orchestrator()
            
            if not self.insights_journey_orchestrator:
                return {
                    "success": False,
                    "error": "InsightsJourneyOrchestrator not available",
                    "summary": {}
                }
            
            # Enhance user_context with session_id
            enhanced_user_context = (user_context or {}).copy()
            enhanced_user_context["session_id"] = session_id
            
            # Try to get orchestrate_summary from Insights Journey Orchestrator
            selected_output = None
            
            try:
                # Check if orchestrate_summary method exists
                if hasattr(self.insights_journey_orchestrator, 'orchestrate_summary'):
                    summary_result = await self.insights_journey_orchestrator.orchestrate_summary(
                        session_id=session_id,
                        user_context=enhanced_user_context
                    )
                    if summary_result and summary_result.get("success"):
                        selected_output = summary_result.get("summary") or summary_result.get("output")
                elif hasattr(self.insights_journey_orchestrator, 'get_best_output'):
                    # Alternative method name
                    summary_result = await self.insights_journey_orchestrator.get_best_output(
                        session_id=session_id,
                        user_context=enhanced_user_context
                    )
                    if summary_result and summary_result.get("success"):
                        selected_output = summary_result.get("output") or summary_result.get("summary")
            except Exception as e:
                self.logger.warning(f"⚠️ orchestrate_summary not available, selecting best output manually: {e}")
            
            # If orchestrate_summary doesn't exist, manually select the best output
            if not selected_output:
                # Get available analyses and select the most interesting one
                available_outputs = []
                
                # Try to get structured insights
                try:
                    # This would require querying for structured analysis results
                    # For now, we'll return a placeholder structure
                    pass
                except Exception as e:
                    self.logger.debug(f"Could not get structured insights: {e}")
                
                # Try to get unstructured insights
                try:
                    # This would require querying for unstructured analysis results
                    pass
                except Exception as e:
                    self.logger.debug(f"Could not get unstructured insights: {e}")
                
                # Try to get AAR
                try:
                    # This would require querying for AAR results
                    pass
                except Exception as e:
                    self.logger.debug(f"Could not get AAR: {e}")
                
                # Try to get data mapping
                try:
                    # This would require querying for data mapping results
                    pass
                except Exception as e:
                    self.logger.debug(f"Could not get data mapping: {e}")
                
                # Select the most interesting output (prioritize: data_mapping > AAR > structured > unstructured)
                # For now, return a placeholder that indicates orchestrate_summary needs to be implemented
                selected_output = {
                    "type": "placeholder",
                    "message": "orchestrate_summary method needs to be implemented in InsightsJourneyOrchestrator to select the best output",
                    "available_types": ["structured_insights", "unstructured_insights", "aar", "data_mapping"]
                }
            
            self.logger.info("✅ Insights pillar summary (orchestrate_summary) compiled successfully")
            
            return {
                "success": True,
                "summary": selected_output
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compile Insights pillar summary: {e}")
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
        Handle HTTP request routing for Insights Solution Orchestrator.
        
        Routes requests to appropriate orchestration methods:
        - POST /analyze -> orchestrate_insights_analysis
        - POST /mapping -> orchestrate_insights_mapping
        - POST /visualize -> orchestrate_insights_visualization
        - POST /data-quality -> orchestrate_insights_data_quality
        - POST /query -> query_insights (Phase 4: Data Mash)
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (e.g., "analyze", "mapping")
            params: Request parameters/body
            user_context: User context (includes workflow_id)
            headers: HTTP headers
            query_params: Query parameters
        
        Returns:
            Dict with response data
        """
        try:
            # ✅ DEBUG: Log entry to handle_request (both logger and print for visibility)
            debug_msg = f"🔍 [InsightsSolutionOrchestratorService.handle_request] Called: {method} {path}, headers keys: {list(headers.keys()) if headers else 'None'}, params keys: {list(params.keys()) if params else 'None'}"
            print(debug_msg)
            self.logger.info(debug_msg)
            
            # Merge user_context from params if provided
            if not user_context:
                user_context = params.get("user_context", {})
            
            # ✅ Extract workflow_id (priority: params > headers, since FrontendGatewayService adds it to params)
            workflow_id_found = None
            if params and params.get("workflow_id"):
                workflow_id_found = params.get("workflow_id")
                if not user_context:
                    user_context = {}
                user_context["workflow_id"] = workflow_id_found
                self.logger.info(f"✅ Extracted workflow_id from params: {workflow_id_found}")
            elif headers:
                workflow_id_from_header = headers.get("X-Workflow-Id") or headers.get("x-workflow-id")
                if workflow_id_from_header:
                    workflow_id_found = workflow_id_from_header
                    if not user_context:
                        user_context = {}
                    user_context["workflow_id"] = workflow_id_found
                    self.logger.info(f"✅ Extracted workflow_id from header: {workflow_id_found}")
            
            if not workflow_id_found:
                self.logger.warning(f"⚠️ No workflow_id found in params or headers. params keys: {list(params.keys()) if params else 'None'}, headers keys: {list(headers.keys()) if headers else 'None'}")
            
            # Route based on path
            if path == "analyze" and method == "POST":
                file_id = params.get("file_id")
                analysis_type = params.get("analysis_type") or query_params.get("type", "eda")
                analysis_options = params.get("options", {}) or params.get("analysis_options", {})
                
                # ✅ Extract content_id from params if provided (for EDA analysis which requires embeddings)
                content_id = params.get("content_id")
                if content_id:
                    analysis_options["content_id"] = content_id
                
                if not file_id:
                    return {
                        "success": False,
                        "error": "file_id is required"
                    }
                
                # ✅ Ensure workflow_id is in user_context if provided in headers
                if not user_context:
                    user_context = {}
                if headers:
                    workflow_id_from_header = headers.get("X-Workflow-Id") or headers.get("x-workflow-id")
                    if workflow_id_from_header and not user_context.get("workflow_id"):
                        user_context["workflow_id"] = workflow_id_from_header
                
                return await self.orchestrate_insights_analysis(
                    file_id=file_id,
                    analysis_type=analysis_type,
                    analysis_options=analysis_options,
                    user_context=user_context
                )
            
            elif path == "mapping" and method == "POST":
                source_file_id = params.get("source_file_id")
                target_file_id = params.get("target_file_id")
                mapping_options = params.get("mapping_options", {})
                
                if not source_file_id or not target_file_id:
                    return {
                        "success": False,
                        "error": "source_file_id and target_file_id are required"
                    }
                
                return await self.orchestrate_insights_mapping(
                    source_file_id=source_file_id,
                    target_file_id=target_file_id,
                    mapping_options=mapping_options,
                    user_context=user_context
                )
            
            elif path == "visualize" and method == "POST":
                content_id = params.get("content_id")
                visualization_options = params.get("visualization_options", {})
                
                if not content_id:
                    return {
                        "success": False,
                        "error": "content_id is required"
                    }
                
                return await self.orchestrate_insights_visualization(
                    content_id=content_id,
                    visualization_options=visualization_options,
                    user_context=user_context
                )
            
            elif path == "data-quality" and method == "POST":
                file_id = params.get("file_id")
                parsed_file_id = params.get("parsed_file_id")
                quality_options = params.get("quality_options", {})
                
                if not file_id:
                    return {
                        "success": False,
                        "error": "file_id is required"
                    }
                
                return await self.orchestrate_insights_data_quality(
                    file_id=file_id,
                    parsed_file_id=parsed_file_id,
                    quality_options=quality_options,
                    user_context=user_context
                )
            
            elif path == "query" and method == "POST":
                insights_query = params.get("insights_query", {})
                
                if not insights_query:
                    return {
                        "success": False,
                        "error": "insights_query is required"
                    }
                
                return await self.query_insights(
                    insights_query=insights_query,
                    user_context=user_context
                )
            
            elif path == "analysis/visualization" and method == "POST":
                # Handle visualization analysis endpoint
                content_id = params.get("content_id") or params.get("file_url")
                visualization_options = params.get("visualization_options", {})
                session_id = params.get("session_id")
                
                if not content_id:
                    return {
                        "success": False,
                        "error": "content_id or file_url is required"
                    }
                
                # Use file_url as file_id if provided
                file_id = content_id if not params.get("file_url") else params.get("file_url")
                
                return await self.orchestrate_insights_visualization(
                    content_id=file_id,
                    visualization_options=visualization_options,
                    user_context=user_context
                )
            
            elif path == "analysis/anomaly-detection" and method == "POST":
                # Handle anomaly detection endpoint
                file_id = params.get("file_id") or params.get("file_url")
                analysis_options = params.get("analysis_options", {})
                session_id = params.get("session_id")
                
                if not file_id:
                    return {
                        "success": False,
                        "error": "file_id or file_url is required"
                    }
                
                # Enable anomaly detection in analysis options
                analysis_options["anomaly_detection"] = True
                
                return await self.orchestrate_insights_analysis(
                    file_id=file_id,
                    analysis_type="eda",  # EDA with anomaly detection
                    analysis_options=analysis_options,
                    user_context=user_context
                )
            
            else:
                return {
                    "success": False,
                    "error": "Route not found",
                    "path": path,
                    "method": method
                }
                
        except Exception as e:
            self.logger.error(f"❌ Request handling failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }

