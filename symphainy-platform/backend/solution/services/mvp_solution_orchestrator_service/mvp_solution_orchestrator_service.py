#!/usr/bin/env python3
"""
MVP Solution Orchestrator Service

WHAT: Orchestrates MVP solution with platform correlation
HOW: Lightweight shell that composes MVP journey orchestrator and orchestrates platform correlation

This service is the "One Stop Shopping" for MVP solution:
1. MVP Operations → delegates to MVPJourneyOrchestratorService (Journey realm)
2. Platform Correlation → orchestrates all platform services (auth, session, workflow, events, telemetry)

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Routes to MVPJourneyOrchestratorService (Journey realm)
- Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Ensures all platform correlation data follows MVP operations through journey
- Registered with Curator for discovery
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class MVPSolutionOrchestratorService(OrchestratorBase):
    """
    MVP Solution Orchestrator Service - Lightweight shell with platform correlation.
    
    "One Stop Shopping" for:
    1. MVP Operations (via MVPJourneyOrchestratorService)
    2. Platform Correlation Data (auth, session, workflow, events, telemetry)
    
    Orchestrates MVP solution:
    1. Session Creation: Create MVP session with free navigation
    2. Pillar Navigation: Navigate between 4 pillars (Content, Insights, Operations, Business Outcomes)
    3. Guide Agent Integration: Guide users through MVP journey
    
    Key Principles:
    - Routes to MVPJourneyOrchestratorService (Journey realm)
    - Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
    - Ensures all platform correlation data follows MVP operations through journey
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
        Initialize MVP Solution Orchestrator Service.
        
        Args:
            service_name: Service name (typically "MVPSolutionOrchestratorService")
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
        self.mvp_journey_orchestrator = None  # MVP operations orchestration
        
        # Platform correlation services (discovered via Curator)
        self.security_guard = None
        self.traffic_cop = None
        self.conductor = None
        self.post_office = None
        self.nurse = None
    
    async def initialize(self) -> bool:
        """
        Initialize MVP Solution Orchestrator Service.
        
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
            "mvp_solution_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase and _realm_service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing MVP Solution Orchestrator Service...")
            
            # Journey orchestrators will be lazy-loaded when methods are called
            # Platform correlation services will be lazy-loaded when methods are called
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ MVP Solution Orchestrator Service initialized successfully")
            
            # Complete telemetry tracking (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "mvp_solution_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MVP Solution Orchestrator Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure in telemetry (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "mvp_solution_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register MVP Solution Orchestrator Service with Curator for discovery."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                await curator.register_service(
                    service_name="MVPSolutionOrchestratorService",
                    service_instance=self,
                    realm_name="solution",
                    capabilities=[
                        {
                            "name": "mvp_orchestration",
                            "protocol": "MVPSolutionOrchestratorProtocol",
                            "description": "Orchestrate MVP solution with platform correlation",
                            "contracts": {
                                "soa_api": {
                                    "api_name": "orchestrate_mvp_session",
                                    "endpoint": "/api/v1/mvp-solution/session",
                                    "method": "POST",
                                    "handler": self.orchestrate_mvp_session,
                                    "metadata": {
                                        "description": "Create MVP session with platform correlation",
                                        "parameters": ["user_id", "session_type", "user_context"]
                                    }
                                },
                                "domain_capability": "solution.orchestrate_mvp",
                                "semantic_api": "/api/v1/mvp-solution/session",
                                "user_journey": "create_mvp_session"
                            }
                        }
                    ]
                )
                self.logger.info("✅ Registered MVPSolutionOrchestratorService with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def _discover_mvp_journey_orchestrator(self):
        """Discover MVPJourneyOrchestratorService via Curator."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                mvp_journey = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                if mvp_journey:
                    # Verify it's from Journey realm
                    orchestrator_realm = getattr(mvp_journey, 'realm_name', None)
                    if orchestrator_realm == "journey":
                        self.logger.info("✅ Discovered MVPJourneyOrchestratorService via Curator")
                        return mvp_journey
                    else:
                        self.logger.warning(f"⚠️ Found MVPJourneyOrchestratorService but wrong realm: {orchestrator_realm} (expected 'journey')")
            
            # If not found via discovery, lazy-initialize it
            self.logger.info("🔄 MVPJourneyOrchestratorService not found - lazy-initializing...")
            try:
                from backend.journey.services.mvp_journey_orchestrator_service.mvp_journey_orchestrator_service import MVPJourneyOrchestratorService
                
                # Get platform gateway from DI container
                platform_gateway = self.platform_gateway
                if not platform_gateway:
                    platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                    if not platform_gateway:
                        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
                
                # Create and initialize MVP Journey Orchestrator Service
                mvp_journey = MVPJourneyOrchestratorService(
                    service_name="MVPJourneyOrchestratorService",
                    realm_name="journey",
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await mvp_journey.initialize()
                self.logger.info("✅ MVPJourneyOrchestratorService lazy-initialized successfully")
                return mvp_journey
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize MVPJourneyOrchestratorService: {init_error}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover MVPJourneyOrchestratorService: {e}")
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
            operation: Operation name (e.g., "mvp_session")
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
        
        # Traffic Cop: Session management
        if not self.traffic_cop:
            self.traffic_cop = await self.get_foundation_service("TrafficCopService")
        
        if self.traffic_cop and user_context:
            try:
                session_id = user_context.get("session_id")
                if session_id:
                    correlation_context["session_id"] = session_id
            except Exception as e:
                self.logger.warning(f"⚠️ Traffic Cop session management failed: {e}")
        
        # Conductor: Workflow tracking
        if not self.conductor:
            self.conductor = await self.get_foundation_service("ConductorService")
        
        if self.conductor:
            try:
                await self.conductor.track_workflow(
                    workflow_id=workflow_id,
                    operation=operation,
                    status="in_progress",
                    metadata={"user_id": correlation_context.get("user_id", "anonymous")}
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Conductor workflow tracking failed: {e}")
        
        # Post Office: Publish event
        if not self.post_office:
            self.post_office = await self.get_foundation_service("PostOfficeService")
        
        if self.post_office:
            try:
                await self.post_office.publish_event(
                    event_type=f"{operation}_started",
                    event_data={
                        "workflow_id": workflow_id,
                        "operation": operation,
                        "user_id": correlation_context.get("user_id", "anonymous")
                    },
                    correlation_id=workflow_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Post Office event publishing failed: {e}")
        
        # Nurse: Telemetry
        if not self.nurse:
            self.nurse = await self.get_foundation_service("NurseService")
        
        if self.nurse:
            try:
                await self.nurse.record_telemetry(
                    metric_name=f"{operation}_start",
                    value=1.0,
                    metadata={
                        "workflow_id": workflow_id,
                        "operation": operation
                    }
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Nurse telemetry recording failed: {e}")
        
        return correlation_context
    
    async def _record_platform_correlation_completion(
        self,
        operation: str,
        result: Dict[str, Any],
        correlation_context: Dict[str, Any]
    ):
        """
        Record platform correlation completion.
        
        Args:
            operation: Operation name
            result: Operation result
            correlation_context: Correlation context from _orchestrate_platform_correlation
        """
        workflow_id = correlation_context.get("workflow_id")
        
        # Conductor: Update workflow status
        if self.conductor and workflow_id:
            try:
                await self.conductor.track_workflow(
                    workflow_id=workflow_id,
                    operation=operation,
                    status="completed" if result.get("success") else "failed",
                    metadata={"result": result}
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Conductor workflow tracking failed: {e}")
        
        # Post Office: Publish completion event
        if self.post_office and workflow_id:
            try:
                await self.post_office.publish_event(
                    event_type=f"{operation}_completed",
                    event_data={
                        "workflow_id": workflow_id,
                        "operation": operation,
                        "success": result.get("success", False)
                    },
                    correlation_id=workflow_id
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Post Office event publishing failed: {e}")
        
        # Nurse: Record completion telemetry
        if self.nurse and workflow_id:
            try:
                await self.nurse.record_telemetry(
                    metric_name=f"{operation}_complete",
                    value=1.0,
                    metadata={
                        "workflow_id": workflow_id,
                        "operation": operation,
                        "success": result.get("success", False)
                    }
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Nurse telemetry recording failed: {e}")
    
    async def orchestrate_mvp_session(
        self,
        user_id: str,
        session_type: str = "mvp",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate MVP session creation with platform correlation.
        
        Flow:
        1. Orchestrate platform correlation (workflow_id, lineage, telemetry)
        2. Delegate to MVPJourneyOrchestratorService to create session
        3. Record completion in platform correlation
        
        Args:
            user_id: User identifier
            session_type: Type of session (default: "mvp")
            user_context: Optional user context
        
        Returns:
            Dict with session details including workflow_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="mvp_session",
                user_context=user_context or {"user_id": user_id}
            )
            
            # Step 2: Get MVP Journey Orchestrator
            if not self.mvp_journey_orchestrator:
                self.mvp_journey_orchestrator = await self._discover_mvp_journey_orchestrator()
            
            if not self.mvp_journey_orchestrator:
                return {
                    "success": False,
                    "error": "MVPJourneyOrchestratorService not available",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
            # Step 3: Extract solution context from user_context if present
            solution_context = None
            if user_context and "solution_structure" in user_context:
                solution_context = {
                    "solution_structure": user_context.get("solution_structure"),
                    "reasoning": user_context.get("reasoning"),
                    "user_goals": user_context.get("user_goals"),
                    "created_at": self._get_timestamp()
                }
                self.logger.info("📋 Solution context found in user_context, will store in session")
            
            # Step 4: Create session via MVP Journey Orchestrator
            # Include solution_context in correlation_context so it gets stored in session
            enhanced_correlation_context = correlation_context.copy()
            if solution_context:
                enhanced_correlation_context["solution_context"] = solution_context
            
            session_result = await self.mvp_journey_orchestrator.start_mvp_journey(
                user_id=user_id,
                initial_pillar=None,  # Free navigation
                user_context=enhanced_correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation="mvp_session",
                result=session_result,
                correlation_context=correlation_context
            )
            
            # Step 5: Add workflow_id to result
            if session_result.get("success"):
                session_result["workflow_id"] = correlation_context.get("workflow_id")
            
            return session_result
            
        except Exception as e:
            self.logger.error(f"❌ MVP session orchestration failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_mvp_session")
            
            workflow_id = None
            if user_context:
                workflow_id = user_context.get("workflow_id")
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def orchestrate_pillar_navigation(
        self,
        session_id: str,
        pillar: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate navigation to a specific pillar.
        
        Flow:
        1. Orchestrate platform correlation
        2. Delegate to MVPJourneyOrchestratorService to navigate
        3. Record completion in platform correlation
        
        Args:
            session_id: Session identifier
            pillar: Pillar name (content, insights, operations, business-outcomes)
            user_context: Optional user context
        
        Returns:
            Dict with pillar context
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation=f"mvp_navigate_{pillar}",
                user_context=user_context or {}
            )
            
            # Step 2: Get MVP Journey Orchestrator
            if not self.mvp_journey_orchestrator:
                self.mvp_journey_orchestrator = await self._discover_mvp_journey_orchestrator()
            
            if not self.mvp_journey_orchestrator:
                return {
                    "success": False,
                    "error": "MVPJourneyOrchestratorService not available",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
            # Step 3: Navigate to pillar via MVP Journey Orchestrator
            navigation_result = await self.mvp_journey_orchestrator.navigate_to_pillar(
                session_id=session_id,
                pillar_id=pillar,  # MVPJourneyOrchestratorService uses pillar_id parameter
                user_context=correlation_context
            )
            
            # Step 4: Record completion in platform correlation
            await self._record_platform_correlation_completion(
                operation=f"mvp_navigate_{pillar}",
                result=navigation_result,
                correlation_context=correlation_context
            )
            
            # Step 5: Add workflow_id to result
            if navigation_result.get("success"):
                navigation_result["workflow_id"] = correlation_context.get("workflow_id")
            
            return navigation_result
            
        except Exception as e:
            self.logger.error(f"❌ Pillar navigation orchestration failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_pillar_navigation")
            
            workflow_id = None
            if user_context:
                workflow_id = user_context.get("workflow_id")
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
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
        Handle HTTP request routing for MVP Solution Orchestrator.
        
        Routes requests to appropriate orchestration methods:
        - POST /session -> orchestrate_mvp_session
        - POST /navigate -> orchestrate_pillar_navigation
        - GET /health -> health check
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (e.g., "session", "navigate")
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
            if path == "session" and method == "POST":
                user_id = params.get("user_id", "anonymous")
                session_type = params.get("session_type", "mvp")
                
                return await self.orchestrate_mvp_session(
                    user_id=user_id,
                    session_type=session_type,
                    user_context=user_context
                )
            
            elif path == "navigate" and method == "POST":
                session_id = params.get("session_id")
                pillar = params.get("pillar") or params.get("pillar_id")
                
                if not session_id or not pillar:
                    return {
                        "success": False,
                        "error": "session_id and pillar are required"
                    }
                
                return await self.orchestrate_pillar_navigation(
                    session_id=session_id,
                    pillar=pillar,
                    user_context=user_context
                )
            
            elif path == "guidance" and method == "POST":
                user_goals = params.get("user_goals", "")
                
                if not user_goals:
                    return {
                        "success": False,
                        "error": "user_goals is required"
                    }
                
                return await self.get_guide_agent_guidance(
                    user_goals=user_goals,
                    user_context=user_context
                )
            
            elif path == "customize" and method == "POST":
                solution_structure = params.get("solution_structure")
                user_customizations = params.get("user_customizations", {})
                
                if not solution_structure:
                    return {
                        "success": False,
                        "error": "solution_structure is required"
                    }
                
                return await self.customize_solution(
                    solution_structure=solution_structure,
                    user_customizations=user_customizations,
                    user_context=user_context
                )
            
            elif path == "health" and method == "GET":
                return {
                    "status": "healthy",
                    "service": "mvp_solution",
                    "timestamp": self._get_timestamp()
                }
            
            else:
                return {
                    "success": False,
                    "error": "Route not found",
                    "path": path,
                    "method": method,
                    "available_paths": ["session", "navigate", "guidance", "health"]
                }
                
        except Exception as e:
            self.logger.error(f"❌ Request handling failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def get_guide_agent_guidance(
        self,
        user_goals: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get guidance from Guide Agent for MVP journey (AGENTIC-FORWARD PATTERN).
        
        Flow:
        1. Orchestrate platform correlation
        2. Delegate to MVPJourneyOrchestratorService Guide Agent
        3. Agent performs CRITICAL REASONING to create solution structure
        4. Return guidance with solution structure specification
        
        Args:
            user_goals: User's stated goals
            user_context: Optional user context
        
        Returns:
            Dict with solution_structure, reasoning, and guidance
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="mvp_guide_agent_guidance",
                user_context=user_context or {}
            )
            
            # Step 2: Get MVP Journey Orchestrator
            if not self.mvp_journey_orchestrator:
                self.mvp_journey_orchestrator = await self._discover_mvp_journey_orchestrator()
            
            if not self.mvp_journey_orchestrator:
                return {
                    "success": False,
                    "error": "MVPJourneyOrchestratorService not available",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
            # Step 3: AGENTIC-FORWARD: Agent does critical reasoning FIRST
            if hasattr(self.mvp_journey_orchestrator, 'guide_agent') and self.mvp_journey_orchestrator.guide_agent:
                # Call the critical reasoning method
                if hasattr(self.mvp_journey_orchestrator.guide_agent, 'analyze_user_goals_for_solution_structure'):
                    solution_structure_result = await self.mvp_journey_orchestrator.guide_agent.analyze_user_goals_for_solution_structure(
                        user_goals=user_goals,
                        user_context=correlation_context,
                        existing_data=user_context.get("existing_data") if user_context else None
                    )
                    
                    # Step 4: Record completion
                    await self._record_platform_correlation_completion(
                        operation="mvp_guide_agent_guidance",
                        result=solution_structure_result,
                        correlation_context=correlation_context
                    )
                    
                    # Add workflow_id to result
                    if solution_structure_result.get("success"):
                        solution_structure_result["workflow_id"] = correlation_context.get("workflow_id")
                    
                    return solution_structure_result
                else:
                    # Fallback to old method if critical reasoning not available
                    self.logger.warning("⚠️ Guide Agent does not have analyze_user_goals_for_solution_structure, using fallback")
                    return {
                        "success": False,
                        "error": "Guide Agent critical reasoning method not available",
                        "workflow_id": correlation_context.get("workflow_id")
                    }
            else:
                return {
                    "success": False,
                    "error": "Guide Agent not available",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
        except Exception as e:
            self.logger.error(f"❌ Guide Agent guidance failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "get_guide_agent_guidance")
            
            workflow_id = None
            if user_context:
                workflow_id = user_context.get("workflow_id")
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def customize_solution(
        self,
        solution_structure: Dict[str, Any],
        user_customizations: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Customize solution structure based on user preferences (AGENTIC-FORWARD PATTERN).
        
        Flow:
        1. Orchestrate platform correlation
        2. Delegate to MVPJourneyOrchestratorService Guide Agent
        3. Agent validates and refines customizations
        4. Return customized solution structure
        
        Args:
            solution_structure: Agent-created solution structure
            user_customizations: User's customization preferences
            user_context: Optional user context
        
        Returns:
            Dict with customized solution_structure
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="mvp_customize_solution",
                user_context=user_context or {}
            )
            
            # Step 2: Get MVP Journey Orchestrator
            if not self.mvp_journey_orchestrator:
                self.mvp_journey_orchestrator = await self._discover_mvp_journey_orchestrator()
            
            if not self.mvp_journey_orchestrator:
                return {
                    "success": False,
                    "error": "MVPJourneyOrchestratorService not available",
                    "workflow_id": correlation_context.get("workflow_id")
                }
            
            # Step 3: Apply user customizations to solution structure
            customized_structure = solution_structure.copy()
            
            # Apply pillar customizations
            if "pillars" in user_customizations:
                for user_pillar in user_customizations["pillars"]:
                    pillar_name = user_pillar.get("name")
                    for pillar in customized_structure.get("pillars", []):
                        if pillar["name"] == pillar_name:
                            # Update enabled status
                            if "enabled" in user_pillar:
                                pillar["enabled"] = user_pillar["enabled"]
                            # Update priority
                            if "priority" in user_pillar:
                                pillar["priority"] = user_pillar["priority"]
                            # Update customizations
                            if "customizations" in user_pillar:
                                pillar["customizations"].update(user_pillar["customizations"])
            
            # Apply other customizations
            if "recommended_data_types" in user_customizations:
                customized_structure["recommended_data_types"] = user_customizations["recommended_data_types"]
            
            if "strategic_focus" in user_customizations:
                customized_structure["strategic_focus"] = user_customizations["strategic_focus"]
            
            # Step 4: Record completion
            result = {
                "success": True,
                "solution_structure": customized_structure,
                "customizations_applied": user_customizations
            }
            
            await self._record_platform_correlation_completion(
                operation="mvp_customize_solution",
                result=result,
                correlation_context=correlation_context
            )
            
            result["workflow_id"] = correlation_context.get("workflow_id")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Solution customization failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "customize_solution")
            
            workflow_id = None
            if user_context:
                workflow_id = user_context.get("workflow_id")
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }


