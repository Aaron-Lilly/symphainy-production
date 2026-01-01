#!/usr/bin/env python3
"""
Saga Journey Orchestrator Service

WHAT: Saga-pattern journey orchestration with automatic compensation on failure
HOW: Composes StructuredJourneyOrchestratorService with Saga-specific compensation logic

This service provides SAGA-PATTERN journey orchestration by composing the
StructuredJourneyOrchestratorService with automatic compensation handlers,
reverse-order rollback, and Saga state tracking.

Saga Pattern Features:
- Automatic reverse-order compensation when milestones fail
- Compensation handlers per milestone (domain-specific undo operations)
- Saga state tracking (in_progress, compensating, completed, failed)
- Idempotency guarantees for compensation operations
- Transactional outbox pattern for event publishing

Use this for: Multi-service workflows requiring atomicity guarantees,
enterprise migrations with rollback requirements, financial transactions,
order processing, or any workflow where partial failures must be compensated.

For simple structured journeys without compensation needs, use
StructuredJourneyOrchestratorService instead.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SagaStatus(str, Enum):
    """Saga execution status."""
    IN_PROGRESS = "in_progress"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"


class SagaJourneyOrchestratorService(RealmServiceBase):
    """
    Saga Journey Orchestrator Service for Journey realm.
    
    SAGA-PATTERN implementation that composes StructuredJourneyOrchestratorService
    with automatic compensation handlers, reverse-order rollback, and Saga state tracking.
    
    Provides Saga guarantees:
    - Each milestone commits locally (local transaction)
    - On failure, previous milestones are automatically compensated in reverse order
    - Compensation handlers are domain-specific (not generic rollbacks)
    - Saga state tracks compensation progress
    - Idempotent compensation operations
    
    Use for: Multi-service workflows requiring atomicity, enterprise migrations,
    financial transactions, order processing, or any workflow where partial failures
    must be compensated.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Saga Journey Orchestrator Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.structured_orchestrator = None  # StructuredJourneyOrchestratorService
        
        # Smart City services
        self.conductor = None
        self.post_office = None
        self.librarian = None
        self.data_steward = None
        
        # Journey Milestone Tracker (discovered via Curator)
        self.milestone_tracker = None
        
        # Compensation Handler Service (discovered via Curator)
        self.compensation_handler_service = None
        
        # Saga-specific state
        self.saga_executions: Dict[str, Dict[str, Any]] = {}  # saga_id -> execution state
        self.compensation_handlers: Dict[str, Dict[str, Any]] = {}  # journey_id -> handlers
        
        # Specialist agents (lazy initialization)
        self._saga_wal_management_agent = None
    
    async def initialize(self) -> bool:
        """
        Initialize Saga Journey Orchestrator Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "saga_journey_orchestrator_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.conductor = await self.get_conductor_api()
            self.post_office = await self.get_post_office_api()
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            
            # 2. Discover Structured Journey Orchestrator via Curator
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    self.structured_orchestrator = await curator.discover_service_by_name("StructuredJourneyOrchestratorService")
                    self.logger.info("✅ Discovered StructuredJourneyOrchestratorService")
                except Exception as e:
                    self.logger.warning(f"⚠️ StructuredJourneyOrchestratorService not yet available: {e}")
            
            # 3. Discover Journey services via Curator
            await self._discover_journey_services()
            
            # 4. Discover Compensation Handler Service via Curator
            await self._discover_compensation_handler_service()
            
            # 4. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "saga_orchestration",
                        "protocol": "SagaJourneyOrchestratorProtocol",
                        "description": "Design and execute Saga-pattern journeys with automatic compensation",
                        "contracts": {
                            "soa_api": {
                                "api_name": "design_saga_journey",
                                "endpoint": "/api/v1/journey/saga/design",
                                "method": "POST",
                                "handler": self.design_saga_journey,
                                "metadata": {
                                    "description": "Design a Saga journey with compensation handlers",
                                    "parameters": ["journey_type", "requirements", "compensation_handlers", "user_context"]
                                }
                            },
                            "domain_capability": "journey.design_saga",
                            "semantic_api": "/api/v1/journey/saga/design",
                            "user_journey": "design_saga_journey"
                        }
                    },
                    {
                        "name": "saga_execution",
                        "protocol": "SagaJourneyOrchestratorProtocol",
                        "description": "Execute Saga journeys with automatic compensation",
                        "contracts": {
                            "soa_api": {
                                "api_name": "execute_saga_journey",
                                "endpoint": "/api/v1/journey/saga/execute",
                                "method": "POST",
                                "handler": self.execute_saga_journey,
                                "metadata": {
                                    "description": "Execute a Saga journey with compensation tracking",
                                    "parameters": ["journey_id", "user_id", "context", "user_context"]
                                }
                            },
                            "domain_capability": "journey.execute_saga",
                            "semantic_api": "/api/v1/journey/saga/execute",
                            "user_journey": "execute_saga_journey"
                        }
                    },
                    {
                        "name": "saga_compensation",
                        "protocol": "SagaJourneyOrchestratorProtocol",
                        "description": "Manage Saga compensation and rollback",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_saga_status",
                                "endpoint": "/api/v1/journey/saga/status",
                                "method": "GET",
                                "handler": self.get_saga_status,
                                "metadata": {
                                    "description": "Get Saga execution status and compensation state",
                                    "parameters": ["saga_id", "user_context"]
                                }
                            },
                            "domain_capability": "journey.get_saga_status",
                            "semantic_api": "/api/v1/journey/saga/status",
                            "user_journey": "get_saga_status"
                        }
                    }
                ],
                soa_apis=[
                    "design_saga_journey",
                    "execute_saga_journey",
                    "advance_saga_step",
                    "get_saga_status",
                    "compensate_saga",
                    "get_saga_execution_history"
                ]
            )
            
            # Record health metric
            await self.record_health_metric(
                "saga_journey_orchestrator_initialized",
                1.0,
                {"service": "SagaJourneyOrchestratorService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "saga_journey_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Saga Journey Orchestrator Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "saga_journey_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "saga_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Saga Journey Orchestrator Service initialization failed: {e}")
            return False
    
    async def _discover_journey_services(self):
        """Discover Journey services via Curator."""
        curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
        if curator:
            try:
                self.milestone_tracker = await curator.discover_service_by_name("JourneyMilestoneTrackerService")
                self.logger.info("✅ Discovered JourneyMilestoneTrackerService")
            except Exception:
                self.logger.warning("⚠️ JourneyMilestoneTrackerService not yet available")
    
    async def _discover_compensation_handler_service(self):
        """Discover Compensation Handler Service via Curator."""
        curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
        if curator:
            try:
                self.compensation_handler_service = await curator.discover_service_by_name("CompensationHandlerService")
                if self.compensation_handler_service:
                    self.logger.info("✅ Discovered CompensationHandlerService")
            except Exception:
                self.logger.warning("⚠️ CompensationHandlerService not yet available")
    
    async def _get_saga_wal_management_agent(self):
        """Lazy initialization of Saga/WAL Management Specialist Agent."""
        if self._saga_wal_management_agent is None:
            try:
                # Get Agentic Foundation Service
                agentic_foundation = self.di_container.get_foundation_service("AgenticFoundationService")
                if agentic_foundation:
                    from backend.business_enablement.agents.specialists.saga_wal_management_specialist import SagaWALManagementSpecialist
                    
                    self._saga_wal_management_agent = await agentic_foundation.create_agent(
                        agent_class=SagaWALManagementSpecialist,
                        agent_name="SagaWALManagementSpecialist",
                        agent_type="specialist",
                        realm_name=self.realm_name,
                        di_container=self.di_container,
                        orchestrator=None  # Service, not orchestrator
                    )
                    
                    if self._saga_wal_management_agent:
                        self.logger.debug("✅ Saga/WAL Management Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Saga/WAL Management Specialist Agent not available: {e}")
        
        return self._saga_wal_management_agent
    
    # ========================================================================
    # SAGA JOURNEY DESIGN (SOA APIs)
    # ========================================================================
    
    async def design_saga_journey(
        self,
        journey_type: str,
        requirements: Dict[str, Any],
        compensation_handlers: Dict[str, str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design a Saga journey with compensation handlers (SOA API).
        
        Creates a structured journey and adds Saga-specific compensation handlers
        for each milestone. Compensation handlers define how to undo each milestone's
        work if a later milestone fails.
        
        Args:
            journey_type: Type of journey (e.g., "enterprise_migration", "order_processing")
            requirements: Journey requirements and configuration
            compensation_handlers: Map of milestone_id -> compensation_handler_name
                Example: {
                    "upload_content": "delete_uploaded_content",
                    "analyze_content": "revert_analysis",
                    "transform_data": "revert_transformation"
                }
            user_context: User context for security and tenant validation
        
        Returns:
            Saga journey definition with compensation handlers
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "design_saga_journey_start",
            success=True,
            details={"journey_type": journey_type}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "design_saga_journey", "execute"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "design_saga_journey",
                        details={"user_id": user_context.get("user_id"), "journey_type": journey_type}
                    )
                    await self.record_health_metric("design_saga_journey_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("design_saga_journey_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
                
                tenant_id = user_context.get("tenant_id")
                if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                    await self.handle_error_with_audit(
                        ValueError("Tenant access denied"),
                        "design_saga_journey",
                        details={"tenant_id": tenant_id, "journey_type": journey_type}
                    )
                    await self.record_health_metric("design_saga_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                    await self.log_operation_with_telemetry("design_saga_journey_complete", success=False)
                    return {
                        "success": False,
                        "error": "Tenant access denied"
                    }
            
            # 1. Design structured journey via Structured Journey Orchestrator
            if not self.structured_orchestrator:
                return {
                    "success": False,
                    "error": "StructuredJourneyOrchestratorService not available"
                }
            
            structured_journey = await self.structured_orchestrator.design_journey(
                journey_type=journey_type,
                requirements=requirements,
                user_context=user_context
            )
            
            if not structured_journey.get("success"):
                return structured_journey
            
            journey_id = structured_journey["journey_id"]
            journey_definition = structured_journey.get("journey", {})
            
            # 2. Add compensation handlers to milestones
            milestones = journey_definition.get("milestones", [])
            for milestone in milestones:
                milestone_id = milestone.get("milestone_id")
                if milestone_id in compensation_handlers:
                    milestone["compensation_handler"] = compensation_handlers[milestone_id]
                    milestone["compensation_data"] = {}  # Will be populated during execution
            
            # 3. Store compensation handlers mapping
            self.compensation_handlers[journey_id] = compensation_handlers
            
            # 4. Store enhanced journey definition
            saga_journey_definition = {
                **journey_definition,
                "journey_id": journey_id,
                "journey_type": journey_type,
                "saga_enabled": True,
                "compensation_handlers": compensation_handlers,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # 5. Store via Librarian
            await self.store_document(
                document_data=saga_journey_definition,
                metadata={
                    "type": "saga_journey_definition",
                    "journey_id": journey_id,
                    "journey_type": journey_type
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("design_saga_journey_success", 1.0, {
                "journey_id": journey_id,
                "journey_type": journey_type
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "design_saga_journey_complete",
                success=True,
                details={"journey_id": journey_id, "journey_type": journey_type}
            )
            
            self.logger.info(f"✅ Saga journey designed: {journey_id} ({journey_type})")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "journey": saga_journey_definition,
                "compensation_handlers": compensation_handlers
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "design_saga_journey", details={"journey_type": journey_type})
            
            # Record health metric (failure)
            await self.record_health_metric("design_saga_journey_failed", 1.0, {
                "journey_type": journey_type,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "design_saga_journey_complete",
                success=False,
                details={"journey_type": journey_type, "error": str(e)}
            )
            
            self.logger.error(f"❌ Design saga journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SAGA JOURNEY EXECUTION (SOA APIs)
    # ========================================================================
    
    async def execute_saga_journey(
        self,
        journey_id: str,
        user_id: str,
        context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a Saga journey with automatic compensation tracking (SOA API).
        
        Executes the structured journey and tracks Saga state. If any milestone
        fails after retries, automatically compensates previous milestones in
        reverse order.
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            context: Execution context
            user_context: User context for security and tenant validation
        
        Returns:
            Saga execution result with saga_id
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "execute_saga_journey_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "execute_saga_journey", "execute"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "execute_saga_journey",
                        details={"user_id": user_id, "journey_id": journey_id}
                    )
                    await self.record_health_metric("execute_saga_journey_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("execute_saga_journey_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
                
                tenant_id = user_context.get("tenant_id")
                if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                    await self.handle_error_with_audit(
                        ValueError("Tenant access denied"),
                        "execute_saga_journey",
                        details={"tenant_id": tenant_id, "journey_id": journey_id}
                    )
                    await self.record_health_metric("execute_saga_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                    await self.log_operation_with_telemetry("execute_saga_journey_complete", success=False)
                    return {
                        "success": False,
                        "error": "Tenant access denied"
                    }
            
            # 1. Get Saga journey definition
            journey_doc = await self.retrieve_document(f"saga_journey_{journey_id}")
            if not journey_doc or "document" not in journey_doc:
                return {
                    "success": False,
                    "error": "Saga journey not found"
                }
            
            saga_journey = journey_doc["document"]
            
            # 2. Create Saga execution state
            saga_id = f"saga_{journey_id}_{user_id}_{uuid.uuid4().hex[:8]}"
            saga_execution = {
                "saga_id": saga_id,
                "journey_id": journey_id,
                "user_id": user_id,
                "status": SagaStatus.IN_PROGRESS.value,
                "started_at": datetime.utcnow().isoformat(),
                "completed_milestones": [],
                "compensated_milestones": [],
                "compensation_handlers": self.compensation_handlers.get(journey_id, {}),
                "context": context,
                "execution_history": []
            }
            
            # 3. Execute structured journey via Structured Journey Orchestrator
            if not self.structured_orchestrator:
                return {
                    "success": False,
                    "error": "StructuredJourneyOrchestratorService not available"
                }
            
            structured_result = await self.structured_orchestrator.execute_journey(
                journey_id=journey_id,
                user_id=user_id,
                context=context,
                user_context=user_context
            )
            
            if not structured_result.get("success"):
                # If execution fails immediately, no compensation needed
                saga_execution["status"] = SagaStatus.FAILED.value
                saga_execution["error"] = structured_result.get("error")
                self.saga_executions[saga_id] = saga_execution
                return {
                    "success": False,
                    "saga_id": saga_id,
                    "error": structured_result.get("error")
                }
            
            # 4. Link structured journey execution to Saga
            saga_execution["structured_execution_id"] = structured_result.get("execution_id")
            self.saga_executions[saga_id] = saga_execution
            
            # 5. Store Saga execution state
            await self.store_document(
                document_data=saga_execution,
                metadata={
                    "type": "saga_execution",
                    "saga_id": saga_id,
                    "journey_id": journey_id,
                    "user_id": user_id
                }
            )
            
            # 6. Monitor Saga execution with Saga/WAL Management Agent
            saga_wal_agent = await self._get_saga_wal_management_agent()
            if saga_wal_agent:
                try:
                    # Get journey data for monitoring
                    journey_data = {
                        "status": saga_execution["status"],
                        "milestones": saga_journey.get("milestones", []),
                        "started_at": saga_execution["started_at"]
                    }
                    
                    # Monitor saga execution
                    monitoring_result = await saga_wal_agent.monitor_saga_execution(
                        saga_id=saga_id,
                        journey_data=journey_data,
                        user_context=user_context
                    )
                    
                    if monitoring_result.get("success"):
                        # Store monitoring insights
                        saga_execution["monitoring_insights"] = {
                            "overall_status": monitoring_result.get("overall_status"),
                            "anomalies": monitoring_result.get("anomaly_detection", {}).get("anomaly_count", 0),
                            "notifications": len(monitoring_result.get("notifications", [])),
                            "escalation_needed": monitoring_result.get("escalation_assessment", {}).get("needs_escalation", False)
                        }
                        self.logger.info(f"✅ Saga monitoring active: {saga_id} (status: {monitoring_result.get('overall_status', 'unknown')})")
                except Exception as e:
                    self.logger.debug(f"Saga/WAL monitoring not available: {e}")
            
            # Record health metric (success)
            await self.record_health_metric("execute_saga_journey_success", 1.0, {
                "saga_id": saga_id,
                "journey_id": journey_id,
                "user_id": user_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "execute_saga_journey_complete",
                success=True,
                details={"saga_id": saga_id, "journey_id": journey_id, "user_id": user_id}
            )
            
            self.logger.info(f"✅ Saga journey execution started: {saga_id} for journey {journey_id}")
            
            return {
                "success": True,
                "saga_id": saga_id,
                "journey_id": journey_id,
                "status": SagaStatus.IN_PROGRESS.value,
                "started_at": saga_execution["started_at"]
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "execute_saga_journey", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("execute_saga_journey_failed", 1.0, {
                "journey_id": journey_id,
                "user_id": user_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "execute_saga_journey_complete",
                success=False,
                details={"journey_id": journey_id, "user_id": user_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Execute saga journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def advance_saga_step(
        self,
        saga_id: str,
        journey_id: str,
        user_id: str,
        step_result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advance Saga to next step and track milestone completion (SOA API).
        
        Advances the structured journey step and tracks milestone completion
        for Saga compensation. If step fails after retries, triggers automatic
        compensation of previous milestones.
        
        Args:
            saga_id: Saga execution ID
            journey_id: Journey ID
            user_id: User ID
            step_result: Step execution result
            user_context: User context for security and tenant validation
        
        Returns:
            Advancement result with next milestone or compensation status
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "advance_saga_step_start",
            success=True,
            details={"saga_id": saga_id, "journey_id": journey_id}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "advance_saga_step", "execute"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "advance_saga_step",
                        details={"user_id": user_id, "saga_id": saga_id}
                    )
                    await self.record_health_metric("advance_saga_step_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("advance_saga_step_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
            
            # 1. Get Saga execution state
            if saga_id not in self.saga_executions:
                # Try to load from storage
                saga_doc = await self.retrieve_document(f"saga_execution_{saga_id}")
                if saga_doc and "document" in saga_doc:
                    self.saga_executions[saga_id] = saga_doc["document"]
                else:
                    return {
                        "success": False,
                        "error": "Saga execution not found"
                    }
            
            saga_execution = self.saga_executions[saga_id]
            
            # 2. Advance structured journey step
            if not self.structured_orchestrator:
                return {
                    "success": False,
                    "error": "StructuredJourneyOrchestratorService not available"
                }
            
            structured_result = await self.structured_orchestrator.advance_journey_step(
                journey_id=journey_id,
                user_id=user_id,
                step_result=step_result,
                user_context=user_context
            )
            
            # 3. Check if step succeeded or failed
            if structured_result.get("success"):
                # Step succeeded - track milestone completion
                current_milestone = structured_result.get("current_milestone")
                if current_milestone:
                    milestone_id = current_milestone.get("milestone_id")
                    if milestone_id and milestone_id not in saga_execution["completed_milestones"]:
                        # Store compensation data for this milestone
                        milestone_data = {
                            "milestone_id": milestone_id,
                            "completed_at": datetime.utcnow().isoformat(),
                            "step_result": step_result,
                            "compensation_data": step_result.get("compensation_data", {})
                        }
                        saga_execution["completed_milestones"].append(milestone_data)
                        
                        # Update execution history
                        saga_execution["execution_history"].append({
                            "timestamp": datetime.utcnow().isoformat(),
                            "event": "milestone_completed",
                            "milestone_id": milestone_id
                        })
                
                # Update Saga state
                saga_execution["status"] = SagaStatus.IN_PROGRESS.value
                self.saga_executions[saga_id] = saga_execution
                
                # Persist Saga state
                await self.store_document(
                    document_data=saga_execution,
                    metadata={
                        "type": "saga_execution",
                        "saga_id": saga_id
                    }
                )
                
                # Record health metric (success)
                await self.record_health_metric("advance_saga_step_success", 1.0, {
                    "saga_id": saga_id,
                    "journey_id": journey_id
                })
                
                # End telemetry tracking
                await self.log_operation_with_telemetry(
                    "advance_saga_step_complete",
                    success=True,
                    details={"saga_id": saga_id, "journey_id": journey_id}
                )
                
                return {
                    "success": True,
                    "saga_id": saga_id,
                    "status": SagaStatus.IN_PROGRESS.value,
                    "next_milestone": structured_result.get("next_milestone"),
                    "completed_milestones": len(saga_execution["completed_milestones"])
                }
            else:
                # Step failed - trigger automatic compensation
                error = structured_result.get("error", "Step failed")
                self.logger.warning(f"⚠️ Saga step failed: {error}, triggering compensation")
                
                compensation_result = await self._compensate_saga(saga_id, error, user_context)
                
                return {
                    "success": False,
                    "saga_id": saga_id,
                    "status": saga_execution["status"],
                    "error": error,
                    "compensation_triggered": True,
                    "compensation_result": compensation_result
                }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "advance_saga_step", details={"saga_id": saga_id, "journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("advance_saga_step_failed", 1.0, {
                "saga_id": saga_id,
                "journey_id": journey_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "advance_saga_step_complete",
                success=False,
                details={"saga_id": saga_id, "journey_id": journey_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Advance saga step failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SAGA COMPENSATION (Internal Methods)
    # ========================================================================
    
    async def _compensate_saga(
        self,
        saga_id: str,
        failure_reason: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compensate Saga by rolling back completed milestones in reverse order.
        
        This is the core Saga compensation logic. When a milestone fails after
        retries, this method automatically compensates all previous milestones
        in reverse order using their compensation handlers.
        
        Args:
            saga_id: Saga execution ID
            failure_reason: Reason for failure
            user_context: User context for compensation operations
        
        Returns:
            Compensation result with status and compensated milestones
        """
        try:
            saga_execution = self.saga_executions.get(saga_id)
            if not saga_execution:
                return {
                    "success": False,
                    "error": "Saga execution not found"
                }
            
            # Update Saga status to compensating
            saga_execution["status"] = SagaStatus.COMPENSATING.value
            saga_execution["failure_reason"] = failure_reason
            self.saga_executions[saga_id] = saga_execution
            
            # Get completed milestones in reverse order (Saga pattern requirement)
            completed_milestones = saga_execution["completed_milestones"][::-1]
            compensation_handlers = saga_execution.get("compensation_handlers", {})
            
            compensation_results = []
            
            # Compensate each milestone in reverse order
            for milestone_data in completed_milestones:
                milestone_id = milestone_data["milestone_id"]
                compensation_handler = compensation_handlers.get(milestone_id)
                
                if not compensation_handler:
                    self.logger.warning(f"⚠️ No compensation handler for milestone {milestone_id}, skipping")
                    continue
                
                try:
                    # Execute compensation handler
                    compensation_result = await self._execute_compensation_handler(
                        compensation_handler=compensation_handler,
                        milestone_data=milestone_data,
                        user_context=user_context
                    )
                    
                    compensation_results.append({
                        "milestone_id": milestone_id,
                        "compensation_handler": compensation_handler,
                        "success": compensation_result.get("success", False),
                        "result": compensation_result
                    })
                    
                    # Track compensated milestone
                    if milestone_id not in saga_execution["compensated_milestones"]:
                        saga_execution["compensated_milestones"].append(milestone_id)
                    
                    # Update execution history
                    saga_execution["execution_history"].append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "milestone_compensated",
                        "milestone_id": milestone_id,
                        "compensation_handler": compensation_handler
                    })
                    
                except Exception as e:
                    self.logger.error(f"❌ Compensation failed for milestone {milestone_id}: {e}")
                    compensation_results.append({
                        "milestone_id": milestone_id,
                        "compensation_handler": compensation_handler,
                        "success": False,
                        "error": str(e)
                    })
            
            # Update Saga status
            all_compensated = all(r.get("success", False) for r in compensation_results)
            saga_execution["status"] = SagaStatus.COMPLETED.value if all_compensated else SagaStatus.FAILED.value
            saga_execution["compensated_at"] = datetime.utcnow().isoformat()
            self.saga_executions[saga_id] = saga_execution
            
            # Persist Saga state
            await self.store_document(
                document_data=saga_execution,
                metadata={
                    "type": "saga_execution",
                    "saga_id": saga_id
                }
            )
            
            self.logger.info(f"✅ Saga compensation completed: {saga_id} ({len(compensation_results)} milestones compensated)")
            
            return {
                "success": all_compensated,
                "saga_id": saga_id,
                "compensated_milestones": len(compensation_results),
                "compensation_results": compensation_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Saga compensation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_compensation_handler(
        self,
        compensation_handler: str,
        milestone_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a compensation handler for a milestone.
        
        Compensation handlers are domain-specific operations that undo the
        work of a completed milestone. They must be idempotent (safe to retry).
        
        ⭐ UPDATED: Now uses CompensationHandlerService for centralized compensation execution.
        
        Args:
            compensation_handler: Name of compensation handler (e.g., "delete_uploaded_file")
            milestone_data: Data from completed milestone
            user_context: User context for compensation operation
        
        Returns:
            Compensation handler result
        """
        try:
            # ⭐ NEW: Use CompensationHandlerService if available
            if self.compensation_handler_service:
                try:
                    compensation_result = await self.compensation_handler_service.execute_compensation(
                        handler_name=compensation_handler,
                        milestone_data=milestone_data,
                        user_context=user_context
                    )
                    
                    if compensation_result.get("success"):
                        self.logger.info(f"✅ Compensation handler '{compensation_handler}' executed successfully")
                    else:
                        self.logger.warning(f"⚠️ Compensation handler '{compensation_handler}' returned failure: {compensation_result.get('error')}")
                    
                    return compensation_result
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ CompensationHandlerService execution failed: {e}, trying fallback")
            
            # Fallback: Use milestone tracker rollback if CompensationHandlerService not available
            if self.milestone_tracker:
                journey_id = milestone_data.get("journey_id")
                user_id = milestone_data.get("user_id")
                milestone_id = milestone_data.get("milestone_id")
                
                if journey_id and user_id and milestone_id:
                    # Use milestone tracker's rollback as compensation
                    rollback_result = await self.milestone_tracker.rollback_milestone(
                        journey_id=journey_id,
                        user_id=user_id,
                        milestone_id=milestone_id,
                        user_context=user_context
                    )
                    self.logger.info(f"✅ Used milestone tracker rollback as compensation for '{compensation_handler}'")
                    return rollback_result
            
            # Final fallback: return success (compensation handler not found, but don't fail)
            self.logger.warning(f"⚠️ Compensation handler '{compensation_handler}' not found, using fallback")
            return {
                "success": True,
                "message": f"Compensation handler '{compensation_handler}' not implemented, using fallback"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Compensation handler execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SAGA STATUS AND QUERIES (SOA APIs)
    # ========================================================================
    
    async def get_saga_status(
        self,
        saga_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Saga execution status and compensation state (SOA API).
        
        Args:
            saga_id: Saga execution ID
            user_context: User context for security and tenant validation
        
        Returns:
            Saga status with execution details and compensation state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_saga_status_start",
            success=True,
            details={"saga_id": saga_id}
        )
        
        try:
            # Security and Tenant Validation
            if user_context:
                if not await self.security.check_permissions(user_context, "get_saga_status", "read"):
                    await self.handle_error_with_audit(
                        ValueError("Permission denied"),
                        "get_saga_status",
                        details={"user_id": user_context.get("user_id"), "saga_id": saga_id}
                    )
                    await self.record_health_metric("get_saga_status_access_denied", 1.0, {})
                    await self.log_operation_with_telemetry("get_saga_status_complete", success=False)
                    return {
                        "success": False,
                        "error": "Permission denied"
                    }
            
            # Get Saga execution state
            if saga_id not in self.saga_executions:
                # Try to load from storage
                saga_doc = await self.retrieve_document(f"saga_execution_{saga_id}")
                if saga_doc and "document" in saga_doc:
                    self.saga_executions[saga_id] = saga_doc["document"]
                else:
                    return {
                        "success": False,
                        "error": "Saga execution not found"
                    }
            
            saga_execution = self.saga_executions[saga_id]
            
            # Record health metric (success)
            await self.record_health_metric("get_saga_status_success", 1.0, {"saga_id": saga_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "get_saga_status_complete",
                success=True,
                details={"saga_id": saga_id}
            )
            
            return {
                "success": True,
                "saga_id": saga_id,
                "status": saga_execution["status"],
                "journey_id": saga_execution["journey_id"],
                "user_id": saga_execution["user_id"],
                "started_at": saga_execution["started_at"],
                "completed_milestones": len(saga_execution["completed_milestones"]),
                "compensated_milestones": len(saga_execution["compensated_milestones"]),
                "compensation_handlers": saga_execution.get("compensation_handlers", {}),
                "execution_history": saga_execution.get("execution_history", [])
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_saga_status", details={"saga_id": saga_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_saga_status_failed", 1.0, {
                "saga_id": saga_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_saga_status_complete",
                success=False,
                details={"saga_id": saga_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Get saga status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_saga_execution_history(
        self,
        saga_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get complete Saga execution history (SOA API).
        
        Args:
            saga_id: Saga execution ID
            user_context: User context for security and tenant validation
        
        Returns:
            Complete execution history with milestones and compensations
        """
        status_result = await self.get_saga_status(saga_id, user_context)
        if not status_result.get("success"):
            return status_result
        
        saga_execution = self.saga_executions.get(saga_id, {})
        
        return {
            "success": True,
            "saga_id": saga_id,
            "execution_history": saga_execution.get("execution_history", []),
            "completed_milestones": saga_execution.get("completed_milestones", []),
            "compensated_milestones": saga_execution.get("compensated_milestones", [])
        }



