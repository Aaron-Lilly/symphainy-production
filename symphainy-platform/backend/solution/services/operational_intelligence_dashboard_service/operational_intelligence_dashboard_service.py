#!/usr/bin/env python3
"""
Operational Intelligence Dashboard Service

WHAT: Provides unified operational intelligence dashboard combining Saga, WAL, and agent insights
HOW: Composes Saga Execution Dashboard, WAL Operations Dashboard, and Solution Analytics

This service provides comprehensive operational visibility:
- Unified view of Saga execution, WAL operations, and agent insights
- Real-time monitoring and alerting
- Cross-component intelligence
- Operational health metrics
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class OperationalIntelligenceDashboardService(RealmServiceBase):
    """
    Operational Intelligence Dashboard Service for Solution realm.
    
    Provides unified operational intelligence by composing:
    - Saga Execution Dashboard
    - WAL Operations Dashboard
    - Solution Analytics with Agent Insights
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Operational Intelligence Dashboard Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.saga_execution_dashboard = None
        self.wal_operations_dashboard = None
        self.solution_analytics = None
    
    async def initialize(self) -> bool:
        """
        Initialize Operational Intelligence Dashboard Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "operational_intelligence_dashboard_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Discover dashboard services via Curator
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    self.saga_execution_dashboard = await curator.get_service("SagaExecutionDashboardService")
                    self.logger.info("✅ Discovered SagaExecutionDashboardService")
                except Exception:
                    self.logger.warning("⚠️ SagaExecutionDashboardService not yet available")
                
                try:
                    self.wal_operations_dashboard = await curator.get_service("WALOperationsDashboardService")
                    self.logger.info("✅ Discovered WALOperationsDashboardService")
                except Exception:
                    self.logger.warning("⚠️ WALOperationsDashboardService not yet available")
                
                try:
                    self.solution_analytics = await curator.get_service("SolutionAnalyticsService")
                    self.logger.info("✅ Discovered SolutionAnalyticsService")
                except Exception:
                    self.logger.warning("⚠️ SolutionAnalyticsService not yet available")
            
            # 2. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "operational_intelligence_dashboard",
                        "protocol": "OperationalIntelligenceDashboardProtocol",
                        "description": "Get unified operational intelligence dashboard",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_operational_intelligence_dashboard",
                                "endpoint": "/api/v1/solution/dashboard/operational-intelligence",
                                "method": "POST",
                                "handler": self.get_operational_intelligence_dashboard,
                                "metadata": {
                                    "description": "Get unified operational intelligence dashboard",
                                    "parameters": ["solution_id", "namespace", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.operational_intelligence_dashboard",
                            "semantic_api": "/api/v1/solution/dashboard/operational-intelligence"
                        }
                    }
                ],
                soa_apis=[
                    "get_operational_intelligence_dashboard",
                    "get_operational_alerts",
                    "get_operational_health_summary"
                ],
                mcp_tools=[]
            )
            
            # Record health metric
            await self.record_health_metric(
                "operational_intelligence_dashboard_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "operational_intelligence_dashboard_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Operational Intelligence Dashboard Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "operational_intelligence_dashboard_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "operational_intelligence_dashboard_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Operational Intelligence Dashboard Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs (Operational Intelligence Dashboard)
    # ========================================================================
    
    async def get_operational_intelligence_dashboard(
        self,
        solution_id: Optional[str] = None,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get unified operational intelligence dashboard (SOA API).
        
        Combines:
        - Saga execution status and insights
        - WAL operations status and triage
        - Solution analytics with agent insights
        - Cross-component alerts and recommendations
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_operational_intelligence_dashboard_start",
            success=True,
            details={"solution_id": solution_id, "namespace": namespace}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_operational_intelligence_dashboard", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_operational_intelligence_dashboard",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_operational_intelligence_dashboard_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_operational_intelligence_dashboard_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            dashboard_data = {
                "solution_id": solution_id,
                "namespace": namespace,
                "saga_execution": {},
                "wal_operations": {},
                "solution_analytics": {},
                "operational_alerts": [],
                "health_summary": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get Saga execution dashboard data
            if self.saga_execution_dashboard and solution_id:
                try:
                    # For now, we'll use a placeholder saga_id
                    # In production, you'd map solution_id to saga_id
                    saga_result = await self.saga_execution_dashboard.get_saga_execution_dashboard(
                        saga_id=f"saga_{solution_id}",
                        user_context=user_context
                    )
                    if saga_result.get("success"):
                        dashboard_data["saga_execution"] = saga_result.get("dashboard", {})
                except Exception as e:
                    self.logger.debug(f"Could not get Saga execution data: {e}")
            
            # Get WAL operations dashboard data
            if self.wal_operations_dashboard:
                try:
                    wal_result = await self.wal_operations_dashboard.get_wal_operations_dashboard(
                        namespace=namespace,
                        user_context=user_context
                    )
                    if wal_result.get("success"):
                        dashboard_data["wal_operations"] = wal_result.get("dashboard", {})
                except Exception as e:
                    self.logger.debug(f"Could not get WAL operations data: {e}")
            
            # Get Solution analytics with agent insights
            if self.solution_analytics and solution_id:
                try:
                    analytics_result = await self.solution_analytics.get_solution_analytics_with_agent_insights(
                        solution_id=solution_id,
                        user_context=user_context
                    )
                    if analytics_result.get("success"):
                        dashboard_data["solution_analytics"] = analytics_result
                except Exception as e:
                    self.logger.debug(f"Could not get Solution analytics: {e}")
            
            # Generate operational alerts from all components
            alerts = []
            
            # Alerts from Saga execution
            saga_status = dashboard_data["saga_execution"].get("status")
            if saga_status == "failed":
                alerts.append({
                    "level": "critical",
                    "source": "saga_execution",
                    "message": f"Saga execution failed: {solution_id}",
                    "recommendation": "Review compensation history and retry"
                })
            
            saga_escalation = dashboard_data["saga_execution"].get("agent_insights", {}).get("escalation_assessment", {}).get("needs_escalation", False)
            if saga_escalation:
                alerts.append({
                    "level": "warning",
                    "source": "saga_execution",
                    "message": "Saga execution requires escalation",
                    "recommendation": "Review agent monitoring insights"
                })
            
            # Alerts from WAL operations
            wal_metrics = dashboard_data["wal_operations"].get("metrics", {})
            if wal_metrics.get("failure_rate", 0) > 0.1:  # > 10% failure rate
                alerts.append({
                    "level": "warning",
                    "source": "wal_operations",
                    "message": f"High WAL failure rate: {wal_metrics.get('failure_rate', 0):.1%}",
                    "recommendation": "Review failed WAL entries and retry"
                })
            
            wal_pending = wal_metrics.get("pending_count", 0)
            if wal_pending > 100:
                alerts.append({
                    "level": "info",
                    "source": "wal_operations",
                    "message": f"High number of pending WAL entries: {wal_pending}",
                    "recommendation": "Monitor WAL processing queue"
                })
            
            # Alerts from Solution analytics
            analytics_performance = dashboard_data["solution_analytics"].get("analytics", {}).get("performance", {})
            performance_score = analytics_performance.get("performance_score", 100)
            if performance_score < 70:
                alerts.append({
                    "level": "warning",
                    "source": "solution_analytics",
                    "message": f"Solution performance below threshold: {performance_score}/100",
                    "recommendation": "Review optimization recommendations"
                })
            
            dashboard_data["operational_alerts"] = alerts
            
            # Generate health summary
            dashboard_data["health_summary"] = {
                "overall_status": "healthy",
                "saga_status": saga_status or "unknown",
                "wal_health": "healthy" if wal_metrics.get("success_rate", 1.0) > 0.9 else "degraded",
                "solution_health": "healthy" if performance_score >= 70 else "degraded",
                "alerts_count": {
                    "critical": len([a for a in alerts if a["level"] == "critical"]),
                    "warning": len([a for a in alerts if a["level"] == "warning"]),
                    "info": len([a for a in alerts if a["level"] == "info"])
                }
            }
            
            # Determine overall status
            if dashboard_data["health_summary"]["alerts_count"]["critical"] > 0:
                dashboard_data["health_summary"]["overall_status"] = "critical"
            elif dashboard_data["health_summary"]["alerts_count"]["warning"] > 0:
                dashboard_data["health_summary"]["overall_status"] = "warning"
            
            result = {
                "success": True,
                "dashboard": dashboard_data
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_operational_intelligence_dashboard_success", 1.0, {
                "solution_id": solution_id,
                "overall_status": dashboard_data["health_summary"]["overall_status"]
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_operational_intelligence_dashboard_complete", success=True, details={
                "solution_id": solution_id,
                "alerts_count": len(alerts)
            })
            
            self.logger.info(f"✅ Operational intelligence dashboard retrieved: {solution_id or 'all'}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_operational_intelligence_dashboard", details={
                "solution_id": solution_id,
                "namespace": namespace
            })
            
            # Record health metric (failure)
            await self.record_health_metric("get_operational_intelligence_dashboard_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_operational_intelligence_dashboard_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get operational intelligence dashboard failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_operational_alerts(
        self,
        solution_id: Optional[str] = None,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get operational alerts (extracted from dashboard)."""
        dashboard_result = await self.get_operational_intelligence_dashboard(
            solution_id=solution_id,
            namespace=namespace,
            user_context=user_context
        )
        
        if dashboard_result.get("success"):
            return {
                "success": True,
                "alerts": dashboard_result["dashboard"]["operational_alerts"]
            }
        return dashboard_result
    
    async def get_operational_health_summary(
        self,
        solution_id: Optional[str] = None,
        namespace: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get operational health summary (extracted from dashboard)."""
        dashboard_result = await self.get_operational_intelligence_dashboard(
            solution_id=solution_id,
            namespace=namespace,
            user_context=user_context
        )
        
        if dashboard_result.get("success"):
            return {
                "success": True,
                "health_summary": dashboard_result["dashboard"]["health_summary"]
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
            "saga_dashboard_available": self.saga_execution_dashboard is not None,
            "wal_dashboard_available": self.wal_operations_dashboard is not None,
            "solution_analytics_available": self.solution_analytics is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "solution_service",
            "realm": "solution",
            "layer": "solution_dashboard",
            "capabilities": ["operational_intelligence", "unified_monitoring", "cross_component_analytics"],
            "soa_apis": [
                "get_operational_intelligence_dashboard",
                "get_operational_alerts",
                "get_operational_health_summary"
            ],
            "mcp_tools": [],
            "composes": "saga_execution_dashboard, wal_operations_dashboard, solution_analytics"
        }










