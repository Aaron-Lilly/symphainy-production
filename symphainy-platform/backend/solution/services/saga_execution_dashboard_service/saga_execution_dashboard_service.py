#!/usr/bin/env python3
"""
Saga Execution Dashboard Service

WHAT: Provides dashboard data for Saga execution monitoring
HOW: Composes Saga Journey Orchestrator and Saga/WAL Management Agent insights

This service provides operational visibility into Saga execution:
- Saga status and milestones
- Compensation history
- Agent monitoring insights
- Execution health metrics
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SagaExecutionDashboardService(RealmServiceBase):
    """
    Saga Execution Dashboard Service for Solution realm.
    
    Provides dashboard data for Saga execution monitoring by composing
    Saga Journey Orchestrator and Saga/WAL Management Agent insights.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Saga Execution Dashboard Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.saga_journey_orchestrator = None
        self.saga_wal_agent = None
    
    async def initialize(self) -> bool:
        """
        Initialize Saga Execution Dashboard Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "saga_execution_dashboard_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Discover Saga Journey Orchestrator via Curator
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    self.saga_journey_orchestrator = await curator.get_service("SagaJourneyOrchestratorService")
                    self.logger.info("✅ Discovered SagaJourneyOrchestratorService")
                except Exception:
                    self.logger.warning("⚠️ SagaJourneyOrchestratorService not yet available")
                
                # Discover Saga/WAL Management Agent
                try:
                    agentic_foundation = self.di_container.get_foundation_service("AgenticFoundationService")
                    if agentic_foundation:
                        from backend.business_enablement.agents.specialists.saga_wal_management_specialist import SagaWALManagementSpecialist
                        
                        self.saga_wal_agent = await agentic_foundation.get_agent("SagaWALManagementSpecialist")
                        if self.saga_wal_agent:
                            self.logger.info("✅ Discovered SagaWALManagementSpecialist")
                except Exception as e:
                    self.logger.debug(f"SagaWALManagementSpecialist not available: {e}")
            
            # 2. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "saga_execution_dashboard",
                        "protocol": "SagaExecutionDashboardProtocol",
                        "description": "Get Saga execution dashboard data",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_saga_execution_dashboard",
                                "endpoint": "/api/v1/solution/dashboard/saga-execution",
                                "method": "POST",
                                "handler": self.get_saga_execution_dashboard,
                                "metadata": {
                                    "description": "Get Saga execution dashboard data",
                                    "parameters": ["saga_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.saga_execution_dashboard",
                            "semantic_api": "/api/v1/solution/dashboard/saga-execution"
                        }
                    }
                ],
                soa_apis=[
                    "get_saga_execution_dashboard",
                    "get_saga_status",
                    "get_saga_milestones",
                    "get_saga_compensation_history"
                ],
                mcp_tools=[]
            )
            
            # Record health metric
            await self.record_health_metric(
                "saga_execution_dashboard_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "saga_execution_dashboard_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Saga Execution Dashboard Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "saga_execution_dashboard_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "saga_execution_dashboard_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Saga Execution Dashboard Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs (Saga Execution Dashboard)
    # ========================================================================
    
    async def get_saga_execution_dashboard(
        self,
        saga_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive Saga execution dashboard data (SOA API).
        
        Includes:
        - Saga status and progress
        - Milestone completion
        - Compensation history
        - Agent monitoring insights
        - Execution health metrics
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_saga_execution_dashboard_start",
            success=True,
            details={"saga_id": saga_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_saga_execution_dashboard", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_saga_execution_dashboard",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_saga_execution_dashboard_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_saga_execution_dashboard_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            dashboard_data = {
                "saga_id": saga_id,
                "status": None,
                "progress": 0.0,
                "milestones": [],
                "compensation_history": [],
                "agent_insights": {},
                "health_metrics": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get Saga status from Saga Journey Orchestrator
            if self.saga_journey_orchestrator:
                try:
                    saga_status = await self.saga_journey_orchestrator.get_saga_status(
                        saga_id=saga_id,
                        user_context=user_context
                    )
                    
                    if saga_status.get("success"):
                        saga_data = saga_status.get("saga", {})
                        dashboard_data["status"] = saga_data.get("status")
                        dashboard_data["progress"] = saga_data.get("progress", 0.0)
                        dashboard_data["milestones"] = saga_data.get("milestones", [])
                        dashboard_data["compensation_history"] = saga_data.get("compensation_history", [])
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get Saga status: {e}")
            
            # Get agent monitoring insights
            if self.saga_wal_agent:
                try:
                    # Get journey data for monitoring
                    journey_data = {
                        "status": dashboard_data["status"],
                        "milestones": dashboard_data["milestones"],
                        "started_at": datetime.utcnow().isoformat()
                    }
                    
                    monitoring_result = await self.saga_wal_agent.monitor_saga_execution(
                        saga_id=saga_id,
                        journey_data=journey_data,
                        user_context=user_context
                    )
                    
                    if monitoring_result.get("success"):
                        dashboard_data["agent_insights"] = {
                            "overall_status": monitoring_result.get("overall_status"),
                            "anomaly_detection": monitoring_result.get("anomaly_detection", {}),
                            "notifications": monitoring_result.get("notifications", []),
                            "escalation_assessment": monitoring_result.get("escalation_assessment", {})
                        }
                except Exception as e:
                    self.logger.debug(f"Could not get agent insights: {e}")
            
            # Calculate health metrics
            dashboard_data["health_metrics"] = {
                "milestones_completed": len([m for m in dashboard_data["milestones"] if m.get("status") == "completed"]),
                "milestones_total": len(dashboard_data["milestones"]),
                "compensations_count": len(dashboard_data["compensation_history"]),
                "anomalies_detected": dashboard_data["agent_insights"].get("anomaly_detection", {}).get("anomaly_count", 0),
                "escalation_needed": dashboard_data["agent_insights"].get("escalation_assessment", {}).get("needs_escalation", False)
            }
            
            result = {
                "success": True,
                "dashboard": dashboard_data
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_saga_execution_dashboard_success", 1.0, {"saga_id": saga_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_saga_execution_dashboard_complete", success=True, details={"saga_id": saga_id})
            
            self.logger.info(f"✅ Saga execution dashboard retrieved: {saga_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_saga_execution_dashboard", details={"saga_id": saga_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_saga_execution_dashboard_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_saga_execution_dashboard_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get Saga execution dashboard failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_saga_status(
        self,
        saga_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get Saga status (delegates to Saga Journey Orchestrator)."""
        if not self.saga_journey_orchestrator:
            return {
                "success": False,
                "error": "Saga Journey Orchestrator not available"
            }
        
        return await self.saga_journey_orchestrator.get_saga_status(
            saga_id=saga_id,
            user_context=user_context
        )
    
    async def get_saga_milestones(
        self,
        saga_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get Saga milestones (delegates to Saga Journey Orchestrator)."""
        saga_status = await self.get_saga_status(saga_id, user_context)
        if saga_status.get("success"):
            return {
                "success": True,
                "milestones": saga_status.get("saga", {}).get("milestones", [])
            }
        return saga_status
    
    async def get_saga_compensation_history(
        self,
        saga_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get Saga compensation history (delegates to Saga Journey Orchestrator)."""
        saga_status = await self.get_saga_status(saga_id, user_context)
        if saga_status.get("success"):
            return {
                "success": True,
                "compensation_history": saga_status.get("saga", {}).get("compensation_history", [])
            }
        return saga_status
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "saga_orchestrator_available": self.saga_journey_orchestrator is not None,
            "saga_wal_agent_available": self.saga_wal_agent is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "solution_service",
            "realm": "solution",
            "layer": "solution_dashboard",
            "capabilities": ["saga_execution_dashboard", "saga_monitoring", "saga_analytics"],
            "soa_apis": [
                "get_saga_execution_dashboard",
                "get_saga_status",
                "get_saga_milestones",
                "get_saga_compensation_history"
            ],
            "mcp_tools": [],
            "composes": "saga_journey_orchestrator, saga_wal_management_agent"
        }










