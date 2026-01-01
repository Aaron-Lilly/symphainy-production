#!/usr/bin/env python3
"""
Business Outcomes Solution Orchestrator Service

WHAT: Orchestrates business outcomes operations (roadmap generation, POC proposals)
HOW: Lightweight shell that composes business outcomes journey orchestrators and orchestrates platform correlation

This service is the "One Stop Shopping" for all business outcomes operations:
1. Business Outcomes Operations → delegates to BusinessOutcomesJourneyOrchestrator (Journey realm)
2. Platform Correlation → orchestrates all platform services (auth, session, workflow, events, telemetry)

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Routes to BusinessOutcomesJourneyOrchestrator (Journey realm)
- Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Ensures all platform correlation data follows business outcomes operations through journey
- Registered with Curator for discovery
"""

import os
import sys
import uuid
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class BusinessOutcomesSolutionOrchestratorService(OrchestratorBase):
    """
    Business Outcomes Solution Orchestrator Service - Lightweight shell with platform correlation.
    
    "One Stop Shopping" for:
    1. Business Outcomes Operations (via BusinessOutcomesJourneyOrchestratorService)
    2. Platform Correlation Data (auth, session, workflow, events, telemetry)
    
    Orchestrates business outcomes operations:
    1. Pillar Summary Compilation: Aggregate summaries from Content, Insights, Operations pillars
    2. Roadmap Generation: Generate strategic roadmaps from pillar outputs
    3. POC Proposal Generation: Generate comprehensive POC proposals
    
    Key Principles:
    - Routes to BusinessOutcomesJourneyOrchestrator (Journey realm)
    - Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
    - Ensures all platform correlation data follows business outcomes operations through journey
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
        Initialize Business Outcomes Solution Orchestrator Service.
        
        Args:
            service_name: Service name (typically "BusinessOutcomesSolutionOrchestratorService")
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
        self.business_outcomes_journey_orchestrator = None  # Business outcomes operations orchestration
        
        # Solution Orchestrators (for pillar summary compilation)
        self.data_solution_orchestrator = None
        self.insights_solution_orchestrator = None
        self.operations_solution_orchestrator = None
        
        # Platform correlation services (discovered via Curator)
        self.security_guard = None
        self.traffic_cop = None
        self.conductor = None
        self.post_office = None
        self.nurse = None
    
    async def initialize(self) -> bool:
        """
        Initialize Business Outcomes Solution Orchestrator Service.
        
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
            "business_outcomes_solution_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase and _realm_service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Business Outcomes Solution Orchestrator Service...")
            
            # Journey orchestrators will be lazy-loaded when methods are called
            # Solution orchestrators will be lazy-loaded when methods are called
            # Platform correlation services will be lazy-loaded when methods are called
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Business Outcomes Solution Orchestrator Service initialized successfully")
            
            # Complete telemetry tracking (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "business_outcomes_solution_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Business Outcomes Solution Orchestrator Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure in telemetry (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "business_outcomes_solution_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Business Outcomes Solution Orchestrator Service with Curator for discovery."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                await curator.register_service(
                    service_name=self.service_name,
                    service_instance=self,
                    realm_name=self.realm_name,
                    capabilities=[
                        "pillar_summary_compilation",
                        "roadmap_generation",
                        "poc_proposal_generation"
                    ],
                    soa_apis=[
                        "orchestrate_pillar_summaries_compilation",
                        "orchestrate_roadmap_generation",
                        "orchestrate_poc_proposal_generation"
                    ],
                    additional_metadata={
                        "orchestrator_type": "solution",
                        "pillar": "business_outcomes"
                    }
                )
                self.logger.info("✅ Registered Business Outcomes Solution Orchestrator Service with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def _discover_business_outcomes_journey_orchestrator(self):
        """Discover BusinessOutcomesJourneyOrchestratorService via Curator, or lazy-initialize if not found."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                journey_orchestrator = await curator.discover_service_by_name("BusinessOutcomesJourneyOrchestratorService")
                if journey_orchestrator:
                    orchestrator_realm = getattr(journey_orchestrator, 'realm_name', None)
                    if orchestrator_realm == "journey":
                        self.logger.info("✅ Discovered BusinessOutcomesJourneyOrchestratorService via Curator")
                        return journey_orchestrator
            
            # If not found via discovery, lazy-initialize it
            self.logger.info("🔄 BusinessOutcomesJourneyOrchestratorService not found - lazy-initializing...")
            try:
                from backend.journey.orchestrators.business_outcomes_journey_orchestrator.business_outcomes_journey_orchestrator import BusinessOutcomesJourneyOrchestrator
                
                platform_gateway = self.platform_gateway
                if not platform_gateway:
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                
                journey_orchestrator = BusinessOutcomesJourneyOrchestrator(
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await journey_orchestrator.initialize()
                self.logger.info("✅ BusinessOutcomesJourneyOrchestratorService lazy-initialized successfully")
                return journey_orchestrator
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize BusinessOutcomesJourneyOrchestratorService: {init_error}")
                return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover BusinessOutcomesJourneyOrchestratorService: {e}")
            return None
    
    async def _discover_data_solution_orchestrator(self):
        """Discover DataSolutionOrchestratorService via Curator."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                data_solution = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                if data_solution:
                    self.logger.info("✅ Discovered DataSolutionOrchestratorService via Curator")
                    return data_solution
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover DataSolutionOrchestratorService: {e}")
        return None
    
    async def _discover_insights_solution_orchestrator(self):
        """Discover InsightsSolutionOrchestratorService via Curator."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                insights_solution = await curator.discover_service_by_name("InsightsSolutionOrchestratorService")
                if insights_solution:
                    self.logger.info("✅ Discovered InsightsSolutionOrchestratorService via Curator")
                    return insights_solution
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover InsightsSolutionOrchestratorService: {e}")
        return None
    
    async def _discover_operations_solution_orchestrator(self):
        """Discover OperationsSolutionOrchestratorService via Curator."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                operations_solution = await curator.discover_service_by_name("OperationsSolutionOrchestratorService")
                if operations_solution:
                    self.logger.info("✅ Discovered OperationsSolutionOrchestratorService via Curator")
                    return operations_solution
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover OperationsSolutionOrchestratorService: {e}")
        return None
    
    async def _get_mvp_journey_orchestrator(self):
        """Get MVP Journey Orchestrator for solution context retrieval."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                if mvp_orchestrator:
                    return mvp_orchestrator
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover MVPJourneyOrchestratorService: {e}")
        return None
    
    async def _orchestrate_platform_correlation(
        self,
        operation: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate platform correlation data to follow business outcomes operations through journey.
        
        "One Stop Shopping" for all platform correlation:
        - Security Guard: Validate auth & tenant
        - Traffic Cop: Manage session/state
        - Conductor: Track workflow
        - Post Office: Publish events & messaging
        - Nurse: Record telemetry & observability
        
        Args:
            operation: Operation name (e.g., "roadmap_generation", "poc_proposal_generation")
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
                    session_id=correlation_context.get("session_id")
                )
                if session_state:
                    correlation_context["session_state"] = session_state
            except Exception as e:
                self.logger.warning(f"⚠️ Session state retrieval failed: {e}")
        
        # 3. Conductor: Track workflow
        if self.conductor and workflow_id:
            try:
                await self.conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=operation,
                    status="in_progress",
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow tracking failed: {e}")
        
        return correlation_context
    
    async def orchestrate_pillar_summaries_compilation(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compile summaries from all pillars with platform correlation and optional Saga guarantees.
        
        ⭐ KEY STRATEGIC FEATURE: Aggregate outputs from Content, Insights, Operations pillars.
        
        Flow:
        1. Execute with Saga if enabled (Capability by Design, Optional by Policy)
        2. Get Content pillar summary (via DataSolutionOrchestrator)
        3. Get Insights pillar summary (via InsightsSolutionOrchestrator)
        4. Get Operations pillar summary (via OperationsSolutionOrchestrator)
        5. Get solution context from MVP Journey Orchestrator
        6. Compile into unified summary
        
        Args:
            session_id: Session identifier
            user_context: Optional user context
        
        Returns:
            Dict with compiled summaries, solution context, and saga_id (if Saga was used)
        """
        # Define milestones for pillar summary compilation
        milestones = ["fetch_content_summary", "fetch_insights_summary", "fetch_operations_summary", "compile_summaries", "store_summary"]
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="pillar_summaries_compilation",
            workflow_func=lambda: self._execute_pillar_summaries_compilation_workflow(
                session_id=session_id,
                user_context=user_context
            ),
            milestones=milestones,
            user_context=user_context
        )
    
    async def _execute_pillar_summaries_compilation_workflow(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute pillar summaries compilation workflow (called by Saga or directly).
        
        This is the actual workflow implementation, extracted for reuse.
        
        Args:
            session_id: Session identifier
            user_context: Optional user context
        
        Returns:
            Dict with compiled summaries and solution context
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="pillar_summaries_compilation",
            user_context=user_context
        )
        
        # ⭐ WAL logging (if enabled via policy)
        if self._wal_enabled():
            await self._write_to_wal(
                operation="pillar_summaries_compilation",
                data={"session_id": session_id},
                correlation_context=correlation_context
            )
        
        # Get summaries from each Solution Orchestrator
        summaries = {}
        
        # Content pillar summary
        if not self.data_solution_orchestrator:
            self.data_solution_orchestrator = await self._discover_data_solution_orchestrator()
        
        if self.data_solution_orchestrator:
            try:
                content_summary = await self.data_solution_orchestrator.orchestrate_content_pillar_summary(
                    session_id=session_id,
                    user_context=correlation_context
                )
                if content_summary.get("success"):
                    summaries["content"] = content_summary.get("summary", {})
                    self.logger.info("✅ Content pillar summary retrieved")
                else:
                    self.logger.warning(f"⚠️ Content pillar summary failed: {content_summary.get('error')}")
                    summaries["content"] = {}
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Content pillar summary: {e}")
                summaries["content"] = {}
        else:
            self.logger.warning("⚠️ DataSolutionOrchestratorService not available")
            summaries["content"] = {}
        
        # Insights pillar summary
        if not self.insights_solution_orchestrator:
            self.insights_solution_orchestrator = await self._discover_insights_solution_orchestrator()
        
        if self.insights_solution_orchestrator:
            try:
                insights_summary = await self.insights_solution_orchestrator.orchestrate_insights_pillar_summary(
                    session_id=session_id,
                    user_context=correlation_context
                )
                if insights_summary.get("success"):
                    summaries["insights"] = insights_summary.get("summary", {})
                    self.logger.info("✅ Insights pillar summary retrieved")
                else:
                    self.logger.warning(f"⚠️ Insights pillar summary failed: {insights_summary.get('error')}")
                    summaries["insights"] = {}
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Insights pillar summary: {e}")
                summaries["insights"] = {}
        else:
            self.logger.warning("⚠️ InsightsSolutionOrchestratorService not available")
            summaries["insights"] = {}
        
        # Operations pillar summary
        if not self.operations_solution_orchestrator:
            self.operations_solution_orchestrator = await self._discover_operations_solution_orchestrator()
        
        if self.operations_solution_orchestrator:
            try:
                operations_summary = await self.operations_solution_orchestrator.orchestrate_operations_pillar_summary(
                    session_id=session_id,
                    user_context=correlation_context
                )
                if operations_summary.get("success"):
                    summaries["operations"] = operations_summary.get("summary", {})
                    self.logger.info("✅ Operations pillar summary retrieved")
                else:
                    self.logger.warning(f"⚠️ Operations pillar summary failed: {operations_summary.get('error')}")
                    summaries["operations"] = {}
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get Operations pillar summary: {e}")
                summaries["operations"] = {}
        else:
            self.logger.warning("⚠️ OperationsSolutionOrchestratorService not available")
            summaries["operations"] = {}
        
        # Get solution context
        mvp_orchestrator = await self._get_mvp_journey_orchestrator()
        solution_context = None
        if mvp_orchestrator:
            try:
                solution_context = await mvp_orchestrator.get_solution_context(session_id)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get solution context: {e}")
        
        # Record completion
        await self._record_platform_correlation_completion(
            operation="pillar_summaries_compilation",
            result={"summaries_count": len(summaries)},
            correlation_context=correlation_context
        )
        
        return {
            "success": True,
            "summaries": summaries,
            "solution_context": solution_context,
            "workflow_id": correlation_context.get("workflow_id")
        }
    
    async def orchestrate_roadmap_generation(
        self,
        pillar_summaries: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        roadmap_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate roadmap generation with platform correlation.
        
        ⭐ KEY STRATEGIC FEATURE: Demonstrate how platform creates solutions.
        
        Flow:
        1. If summaries not provided, compile them
        2. Get solution context
        3. Route to Business Outcomes Journey Orchestrator
        4. Execute roadmap generation workflow
        
        Args:
            pillar_summaries: Optional pre-compiled pillar summaries
            session_id: Optional session identifier (used if summaries not provided)
            roadmap_options: Optional roadmap generation options
            user_context: Optional user context
        
        Returns:
            Dict with roadmap generation result
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="roadmap_generation",
            user_context=user_context
        )
        
        # ⭐ WAL logging (if enabled via policy)
        if self._wal_enabled():
            await self._write_to_wal(
                operation="roadmap_generation",
                data={
                    "session_id": session_id,
                    "has_pillar_summaries": pillar_summaries is not None,
                    "roadmap_options": roadmap_options
                },
                correlation_context=correlation_context
            )
        
        # If summaries not provided, compile them
        if not pillar_summaries and session_id:
            compilation_result = await self.orchestrate_pillar_summaries_compilation(
                session_id=session_id,
                user_context=correlation_context
            )
            pillar_summaries = compilation_result.get("summaries", {})
            solution_context = compilation_result.get("solution_context")
            if solution_context:
                enhanced_user_context = correlation_context.copy()
                enhanced_user_context["solution_context"] = solution_context
                user_context = enhanced_user_context
        
        # Get Business Outcomes Journey Orchestrator
        if not self.business_outcomes_journey_orchestrator:
            self.business_outcomes_journey_orchestrator = await self._discover_business_outcomes_journey_orchestrator()
        
        if not self.business_outcomes_journey_orchestrator:
            return {
                "success": False,
                "error": "BusinessOutcomesJourneyOrchestrator not available"
            }
        
        # Execute roadmap generation
        result = await self.business_outcomes_journey_orchestrator.execute_roadmap_generation_workflow(
            pillar_summaries=pillar_summaries or {},
            roadmap_options=roadmap_options,
            user_context=correlation_context
        )
        
        # Record completion
        await self._record_platform_correlation_completion(
            operation="roadmap_generation",
            result=result,
            correlation_context=correlation_context
        )
        
        return result
    
    async def orchestrate_poc_proposal_generation(
        self,
        pillar_summaries: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        poc_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate POC proposal generation with platform correlation.
        
        ⭐ KEY STRATEGIC FEATURE: Demonstrate how platform implements solutions.
        
        Flow:
        1. If summaries not provided, compile them
        2. Get solution context
        3. Route to Business Outcomes Journey Orchestrator
        4. Execute POC proposal generation workflow
        
        Args:
            pillar_summaries: Optional pre-compiled pillar summaries
            session_id: Optional session identifier (used if summaries not provided)
            poc_options: Optional POC proposal generation options
            user_context: Optional user context
        
        Returns:
            Dict with POC proposal generation result
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="poc_proposal_generation",
            user_context=user_context
        )
        
        # ⭐ WAL logging (if enabled via policy)
        if self._wal_enabled():
            await self._write_to_wal(
                operation="poc_proposal_generation",
                data={
                    "session_id": session_id,
                    "has_pillar_summaries": pillar_summaries is not None,
                    "poc_options": poc_options
                },
                correlation_context=correlation_context
            )
        
        # If summaries not provided, compile them
        if not pillar_summaries and session_id:
            compilation_result = await self.orchestrate_pillar_summaries_compilation(
                session_id=session_id,
                user_context=correlation_context
            )
            pillar_summaries = compilation_result.get("summaries", {})
            solution_context = compilation_result.get("solution_context")
            if solution_context:
                enhanced_user_context = correlation_context.copy()
                enhanced_user_context["solution_context"] = solution_context
                user_context = enhanced_user_context
        
        # Get Business Outcomes Journey Orchestrator
        if not self.business_outcomes_journey_orchestrator:
            self.business_outcomes_journey_orchestrator = await self._discover_business_outcomes_journey_orchestrator()
        
        if not self.business_outcomes_journey_orchestrator:
            return {
                "success": False,
                "error": "BusinessOutcomesJourneyOrchestrator not available"
            }
        
        # Execute POC proposal generation
        result = await self.business_outcomes_journey_orchestrator.execute_poc_proposal_generation_workflow(
            pillar_summaries=pillar_summaries or {},
            poc_options=poc_options,
            user_context=correlation_context
        )
        
        # Record completion
        await self._record_platform_correlation_completion(
            operation="poc_proposal_generation",
            result=result,
            correlation_context=correlation_context
        )
        
        return result
    
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
            wal_operations_str = config_adapter.get("WAL_OPERATIONS", "roadmap_generation,poc_proposal_generation")
        else:
            import os
            wal_enabled = os.getenv("WAL_ENABLED", "false").lower() == "true"
            wal_operations_str = os.getenv("WAL_OPERATIONS", "roadmap_generation,poc_proposal_generation")
            if wal_enabled or wal_operations_str:
                self.logger.warning("⚠️ [BUSINESS_OUTCOMES_SOLUTION] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
        
        # Parse wal operations
        if isinstance(wal_operations_str, str):
            wal_operations = wal_operations_str.split(",")
        else:
            wal_operations = ["roadmap_generation", "poc_proposal_generation"]
        
        # Store policy for later use
        if not hasattr(self, '_wal_policy'):
            self._wal_policy = {
                "enable_wal": wal_enabled,
                "log_operations": [op.strip() for op in wal_operations],
                "namespace": "business_outcomes_operations"
            }
        
        return self._wal_policy.get("enable_wal", False)
    
    async def _write_to_wal(
        self,
        operation: str,
        data: Dict[str, Any],
        correlation_context: Dict[str, Any]
    ):
        """
        Write to WAL if enabled.
        
        ⭐ REAL WAL INTEGRATION: Uses DataStewardService WAL capability.
        """
        if not self._wal_enabled():
            return
        
        # Check if this operation should be logged
        if operation not in self._wal_policy.get("log_operations", []):
            return
        
        try:
            # Get Data Steward service for WAL capability
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                self.logger.warning("⚠️ DataStewardService not available - WAL logging skipped")
                return
            
            # Build WAL payload
            wal_payload = {
                "operation": operation,
                "data": data,
                "workflow_id": correlation_context.get("workflow_id"),
                "session_id": correlation_context.get("session_id"),
                "user_id": correlation_context.get("user_id", "anonymous"),
                "timestamp": correlation_context.get("timestamp")
            }
            
            # Write to WAL via Data Steward
            wal_result = await data_steward.write_to_log(
                namespace=self._wal_policy.get("namespace", "business_outcomes_operations"),
                payload=wal_payload,
                target="business_outcomes_operations",
                lifecycle={
                    "retry_count": 3,
                    "delay_seconds": 5,
                    "ttl_seconds": 86400  # 24 hours
                },
                user_context=correlation_context
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
            saga_operations_str = config_adapter.get("SAGA_OPERATIONS", "pillar_summaries_compilation,roadmap_generation,poc_proposal_generation")
        else:
            import os
            saga_enabled = os.getenv("SAGA_ENABLED", "false").lower() == "true"
            saga_operations_str = os.getenv("SAGA_OPERATIONS", "pillar_summaries_compilation,roadmap_generation,poc_proposal_generation")
            if saga_enabled or saga_operations_str:
                self.logger.warning("⚠️ [BUSINESS_OUTCOMES_SOLUTION] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
        
        # Parse saga operations
        if isinstance(saga_operations_str, str):
            saga_operations = saga_operations_str.split(",")
        else:
            saga_operations = ["pillar_summaries_compilation", "roadmap_generation", "poc_proposal_generation"]
        
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
            "pillar_summaries_compilation": {
                "fetch_content_summary": "clear_content_cache",
                "fetch_insights_summary": "clear_insights_cache",
                "fetch_operations_summary": "clear_operations_cache",
                "compile_summaries": "delete_compiled_summary",
                "store_summary": "delete_stored_summary"
            },
            "roadmap_generation": {
                "analyze_pillar_outputs": "clear_analysis_cache",
                "identify_opportunities": "revert_opportunity_identification",
                "generate_roadmap_structure": "delete_roadmap_draft",
                "apply_business_logic": "revert_business_analysis",
                "store_roadmap": "delete_stored_roadmap"
            },
            "poc_proposal_generation": {
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
            operation: Operation name (e.g., "pillar_summaries_compilation")
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
    
    async def _record_platform_correlation_completion(
        self,
        operation: str,
        result: Dict[str, Any],
        correlation_context: Dict[str, Any]
    ):
        """Record completion in platform correlation services."""
        workflow_id = correlation_context.get("workflow_id")
        
        # Conductor: Track workflow completion
        if self.conductor and workflow_id:
            try:
                await self.conductor.track_workflow_step(
                    workflow_id=workflow_id,
                    step_name=operation,
                    status="completed" if result.get("success") else "failed",
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Workflow tracking failed: {e}")
        
        # Post Office: Publish completion event
        if self.post_office and workflow_id:
            try:
                await self.post_office.publish_event(
                    event_type="business_outcomes_operation_complete",
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
        if self.nurse and workflow_id:
            try:
                await self.nurse.record_platform_event(
                    event_type="log",
                    event_data={
                        "level": "info" if result.get("success") else "error",
                        "message": f"Business outcomes operation completed: {operation}",
                        "service_name": self.__class__.__name__,
                        "operation": operation,
                        "success": result.get("success")
                    },
                    trace_id=workflow_id,
                    user_context=correlation_context
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Telemetry recording failed: {e}")
    
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
        Handle HTTP requests for Business Outcomes solution.
        
        Routes:
        - GET /pillar-summaries?session_id=... -> orchestrate_pillar_summaries_compilation
        - POST /roadmap -> orchestrate_roadmap_generation
        - POST /poc-proposal -> orchestrate_poc_proposal_generation
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            params: Request parameters
            user_context: Optional user context
            headers: Optional HTTP headers (for compatibility with gateway)
            query_params: Optional query parameters (for compatibility with gateway)
        """
        try:
            # Merge user_context from params if provided
            if not user_context:
                user_context = params.get("user_context", {})
            
            # Route based on path
            if path == "pillar-summaries" and method == "GET":
                # Get session_id from params, query_params, or user_context
                session_id = params.get("session_id") or (query_params or {}).get("session_id") or (user_context or {}).get("session_id")
                if not session_id:
                    return {"success": False, "error": "session_id is required"}
                return await self.orchestrate_pillar_summaries_compilation(
                    session_id=session_id,
                    user_context=user_context
                )
            
            elif path == "roadmap" and method == "POST":
                return await self.orchestrate_roadmap_generation(
                    pillar_summaries=params.get("pillar_summaries"),
                    session_id=params.get("session_id"),
                    roadmap_options=params.get("roadmap_options"),
                    user_context=user_context
                )
            
            elif path == "poc-proposal" and method == "POST":
                return await self.orchestrate_poc_proposal_generation(
                    pillar_summaries=params.get("pillar_summaries"),
                    session_id=params.get("session_id"),
                    poc_options=params.get("poc_options"),
                    user_context=user_context
                )
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown route: {method} {path}"
                }
        
        except Exception as e:
            self.logger.error(f"❌ Handle request failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }

