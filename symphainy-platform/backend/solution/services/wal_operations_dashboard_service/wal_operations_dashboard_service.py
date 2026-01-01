#!/usr/bin/env python3
"""
WAL Operations Dashboard Service

WHAT: Provides dashboard data for WAL operations monitoring
HOW: Composes Data Steward WAL module and Saga/WAL Management Agent insights

This service provides operational visibility into WAL operations:
- WAL entry triage
- Replay status
- WAL operations metrics
- Agent triage insights
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class WALOperationsDashboardService(RealmServiceBase):
    """
    WAL Operations Dashboard Service for Solution realm.
    
    Provides dashboard data for WAL operations monitoring by composing
    Data Steward WAL module and Saga/WAL Management Agent insights.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize WAL Operations Dashboard Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.data_steward = None
        self.saga_wal_agent = None
    
    async def initialize(self) -> bool:
        """
        Initialize WAL Operations Dashboard Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "wal_operations_dashboard_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Data Steward for WAL operations
            self.data_steward = await self.get_data_steward_api()
            
            # 2. Discover Saga/WAL Management Agent
            try:
                agentic_foundation = self.di_container.get_foundation_service("AgenticFoundationService")
                if agentic_foundation:
                    from backend.business_enablement.agents.specialists.saga_wal_management_specialist import SagaWALManagementSpecialist
                    
                    self.saga_wal_agent = await agentic_foundation.get_agent("SagaWALManagementSpecialist")
                    if self.saga_wal_agent:
                        self.logger.info("✅ Discovered SagaWALManagementSpecialist")
            except Exception as e:
                self.logger.debug(f"SagaWALManagementSpecialist not available: {e}")
            
            # 3. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "wal_operations_dashboard",
                        "protocol": "WALOperationsDashboardProtocol",
                        "description": "Get WAL operations dashboard data",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_wal_operations_dashboard",
                                "endpoint": "/api/v1/solution/dashboard/wal-operations",
                                "method": "POST",
                                "handler": self.get_wal_operations_dashboard,
                                "metadata": {
                                    "description": "Get WAL operations dashboard data",
                                    "parameters": ["namespace", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.wal_operations_dashboard",
                            "semantic_api": "/api/v1/solution/dashboard/wal-operations"
                        }
                    }
                ],
                soa_apis=[
                    "get_wal_operations_dashboard",
                    "get_wal_entry_triage",
                    "get_wal_replay_status",
                    "get_wal_operations_metrics"
                ],
                mcp_tools=[]
            )
            
            # Record health metric
            await self.record_health_metric(
                "wal_operations_dashboard_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "wal_operations_dashboard_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ WAL Operations Dashboard Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "wal_operations_dashboard_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "wal_operations_dashboard_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ WAL Operations Dashboard Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs (WAL Operations Dashboard)
    # ========================================================================
    
    async def get_wal_operations_dashboard(
        self,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive WAL operations dashboard data (SOA API).
        
        Includes:
        - WAL entry triage (pending, completed, failed, retrying)
        - Replay status
        - WAL operations metrics
        - Agent triage insights
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_wal_operations_dashboard_start",
            success=True,
            details={"namespace": namespace}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_wal_operations_dashboard", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_wal_operations_dashboard",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_wal_operations_dashboard_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_wal_operations_dashboard_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            dashboard_data = {
                "namespace": namespace or "all",
                "wal_entries": {
                    "pending": 0,
                    "completed": 0,
                    "failed": 0,
                    "retrying": 0,
                    "total": 0
                },
                "triage_categories": {},
                "replay_status": {},
                "agent_insights": {},
                "metrics": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get WAL entries from Data Steward (if available)
            if self.data_steward:
                try:
                    # Get recent WAL entries (last 24 hours)
                    from_timestamp = datetime.utcnow() - timedelta(days=1)
                    to_timestamp = datetime.utcnow()
                    
                    filters = {}
                    if namespace:
                        filters["namespace"] = namespace
                    
                    wal_entries = await self.data_steward.replay_log(
                        namespace=namespace or "all",
                        from_timestamp=from_timestamp,
                        to_timestamp=to_timestamp,
                        filters=filters,
                        user_context=user_context
                    )
                    
                    # Categorize WAL entries
                    for entry in wal_entries:
                        status = entry.get("status", "pending")
                        dashboard_data["wal_entries"][status] = dashboard_data["wal_entries"].get(status, 0) + 1
                        dashboard_data["wal_entries"]["total"] += 1
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get WAL entries: {e}")
            
            # Get agent triage insights
            if self.saga_wal_agent:
                try:
                    # Prepare WAL entries for triage
                    wal_entries_for_triage = []
                    if self.data_steward:
                        try:
                            from_timestamp = datetime.utcnow() - timedelta(hours=1)
                            to_timestamp = datetime.utcnow()
                            
                            wal_entries = await self.data_steward.replay_log(
                                namespace=namespace or "all",
                                from_timestamp=from_timestamp,
                                to_timestamp=to_timestamp,
                                filters={},
                                user_context=user_context
                            )
                            wal_entries_for_triage = wal_entries
                        except Exception:
                            pass
                    
                    triage_result = await self.saga_wal_agent.triage_wal_entries(
                        wal_entries=wal_entries_for_triage,
                        user_context=user_context
                    )
                    
                    if triage_result.get("success"):
                        dashboard_data["triage_categories"] = triage_result.get("triage_categories", {})
                        dashboard_data["agent_insights"] = {
                            "priority_entries": triage_result.get("priority_entries", []),
                            "recommendations": triage_result.get("recommendations", []),
                            "alerts": triage_result.get("alerts", [])
                        }
                except Exception as e:
                    self.logger.debug(f"Could not get agent triage insights: {e}")
            
            # Calculate metrics
            total = dashboard_data["wal_entries"]["total"]
            dashboard_data["metrics"] = {
                "success_rate": dashboard_data["wal_entries"]["completed"] / total if total > 0 else 0,
                "failure_rate": dashboard_data["wal_entries"]["failed"] / total if total > 0 else 0,
                "retry_rate": dashboard_data["wal_entries"]["retrying"] / total if total > 0 else 0,
                "pending_count": dashboard_data["wal_entries"]["pending"],
                "total_entries": total
            }
            
            result = {
                "success": True,
                "dashboard": dashboard_data
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_wal_operations_dashboard_success", 1.0, {"namespace": namespace})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_wal_operations_dashboard_complete", success=True, details={"namespace": namespace})
            
            self.logger.info(f"✅ WAL operations dashboard retrieved: {namespace or 'all'}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_wal_operations_dashboard", details={"namespace": namespace})
            
            # Record health metric (failure)
            await self.record_health_metric("get_wal_operations_dashboard_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_wal_operations_dashboard_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get WAL operations dashboard failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_wal_entry_triage(
        self,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get WAL entry triage (delegates to Saga/WAL Management Agent)."""
        if not self.saga_wal_agent:
            return {
                "success": False,
                "error": "Saga/WAL Management Agent not available"
            }
        
        try:
            # Get recent WAL entries
            wal_entries = []
            if self.data_steward:
                from_timestamp = datetime.utcnow() - timedelta(hours=1)
                to_timestamp = datetime.utcnow()
                
                wal_entries = await self.data_steward.replay_log(
                    namespace=namespace or "all",
                    from_timestamp=from_timestamp,
                    to_timestamp=to_timestamp,
                    filters={},
                    user_context=user_context
                )
            
            triage_result = await self.saga_wal_agent.triage_wal_entries(
                wal_entries=wal_entries,
                user_context=user_context
            )
            
            return triage_result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_wal_replay_status(
        self,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get WAL replay status."""
        if not self.data_steward:
            return {
                "success": False,
                "error": "Data Steward not available"
            }
        
        try:
            # Get recent WAL entries to determine replay status
            from_timestamp = datetime.utcnow() - timedelta(days=1)
            to_timestamp = datetime.utcnow()
            
            wal_entries = await self.data_steward.replay_log(
                namespace=namespace or "all",
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                filters={},
                user_context=user_context
            )
            
            return {
                "success": True,
                "replay_status": {
                    "entries_available": len(wal_entries),
                    "time_range": {
                        "from": from_timestamp.isoformat(),
                        "to": to_timestamp.isoformat()
                    },
                    "namespace": namespace or "all"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_wal_operations_metrics(
        self,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get WAL operations metrics."""
        dashboard_result = await self.get_wal_operations_dashboard(namespace, user_context)
        if dashboard_result.get("success"):
            return {
                "success": True,
                "metrics": dashboard_result["dashboard"]["metrics"]
            }
        return dashboard_result
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "data_steward_available": self.data_steward is not None,
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
            "capabilities": ["wal_operations_dashboard", "wal_triage", "wal_analytics"],
            "soa_apis": [
                "get_wal_operations_dashboard",
                "get_wal_entry_triage",
                "get_wal_replay_status",
                "get_wal_operations_metrics"
            ],
            "mcp_tools": [],
            "composes": "data_steward_wal, saga_wal_management_agent"
        }










