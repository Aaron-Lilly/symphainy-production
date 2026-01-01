"""
Health Service - Agent-specific health monitoring business logic

Handles agent-specific health monitoring, health assessment,
and health-based decision making for agent operations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.health_protocol import (
    HealthContext, HealthCheck, HealthMetric, HealthReport, HealthAlert,
    HealthStatus, HealthType, AlertSeverity
)
from foundations.public_works_foundation.infrastructure_abstractions.health_abstraction import HealthAbstraction
from foundations.public_works_foundation.composition_services.health_composition_service import HealthCompositionService

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class HealthService(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Health Service - Agent-specific health monitoring business logic
    
    Handles agent-specific health monitoring and health-based decision making.
    This service applies health monitoring to agent operations and behaviors.
    """
    
    def __init__(self, 
                 health_abstraction: HealthAbstraction,
                 health_composition_service: HealthCompositionService,
                 curator_foundation=None,
                 di_container=None):
        """Initialize Health Service."""
        if not di_container:
            raise ValueError("DI Container is required for HealthService initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.health_abstraction = health_abstraction
        self.health_composition_service = health_composition_service
        self.curator_foundation = curator_foundation
        self.service_name = "health_service"
        
        # Agent-specific health monitoring
        self.agent_health_monitoring = {
            "llm_health": self._monitor_llm_health,
            "mcp_health": self._monitor_mcp_health,
            "tool_health": self._monitor_tool_health,
            "agent_health": self._monitor_agent_health
        }
        
        self.logger.info("Initialized Health Service for agent-specific monitoring")
    
    async def monitor_agent_health(self, 
                                 operation_type: str,
                                 context: HealthContext,
                                 operation_data: Dict[str, Any] = None,
                                 user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor health for agent operations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("monitor_agent_health_start", success=True, details={"operation_type": operation_type})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_health", "read"):
                        await self.record_health_metric("monitor_agent_health_access_denied", 1.0, {"operation_type": operation_type})
                        await self.log_operation_with_telemetry("monitor_agent_health_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("monitor_agent_health_tenant_denied", 1.0, {"operation_type": operation_type})
                            await self.log_operation_with_telemetry("monitor_agent_health_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Monitoring health for {operation_type} operation")
            
            # Get monitoring function
            monitoring_func = self.agent_health_monitoring.get(operation_type)
            if not monitoring_func:
                return {
                    "success": False,
                    "error": f"Unknown operation type: {operation_type}",
                    "operation_type": operation_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Monitor health
            result = await monitoring_func(context, operation_data)
            
            # Add service metadata
            result.update({
                "operation_type": operation_type,
                "monitored_at": datetime.utcnow().isoformat(),
                "health_service": self.service_name
            })
            
            # Record success metric
            await self.record_health_metric("monitor_agent_health_success", 1.0, {"operation_type": operation_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("monitor_agent_health_complete", success=True, details={"operation_type": operation_type})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "monitor_agent_health", details={"operation_type": operation_type})
            self.logger.error(f"Health monitoring failed for {operation_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation_type": operation_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def assess_agent_health(self, 
                                agent_id: str,
                                context: HealthContext,
                                user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assess overall agent health."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("assess_agent_health_start", success=True, details={"agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_health", "read"):
                        await self.record_health_metric("assess_agent_health_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("assess_agent_health_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("assess_agent_health_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("assess_agent_health_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Assessing health for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = HealthContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Perform comprehensive health assessment
            assessment = await self.health_composition_service.perform_health_assessment(
                f"agent_{agent_id}",
                agent_context,
                include_metrics=True
            )
            
            # Get agent-specific health report
            health_report = await self.health_abstraction.get_health_report(
                f"agent_{agent_id}",
                agent_context
            )
            
            result = {
                "success": True,
                "agent_id": agent_id,
                "overall_status": health_report.overall_status.value,
                "health_assessment": assessment,
                "health_score": self._calculate_agent_health_score(health_report),
                "recommendations": self._generate_health_recommendations(health_report),
                "assessed_at": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("assess_agent_health_success", 1.0, {"agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("assess_agent_health_complete", success=True, details={"agent_id": agent_id})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "assess_agent_health", details={"agent_id": agent_id})
            self.logger.error(f"Health assessment failed for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_agent_health_metrics(self, 
                                     agent_id: str,
                                     context: HealthContext) -> Dict[str, Any]:
        """Get agent-specific health metrics."""
        try:
            self.logger.debug(f"Getting health metrics for agent {agent_id}")
            
            # Create agent-specific context
            agent_context = HealthContext(
                service_id=context.service_id,
                agent_id=agent_id,
                tenant_id=context.tenant_id,
                environment=context.environment,
                region=context.region,
                metadata=context.metadata or {}
            )
            
            # Collect agent metrics
            agent_metrics = await self.health_abstraction.collect_metrics(
                HealthType.AGENT,
                agent_context
            )
            
            # Collect system metrics for context
            system_metrics = await self.health_abstraction.collect_metrics(
                HealthType.SYSTEM,
                agent_context
            )
            
            # Analyze metrics
            metrics_analysis = self._analyze_agent_metrics(agent_metrics, system_metrics)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_metrics": [
                    {
                        "name": metric.name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat()
                    } for metric in agent_metrics
                ],
                "system_metrics": [
                    {
                        "name": metric.name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat()
                    } for metric in system_metrics
                ],
                "analysis": metrics_analysis,
                "collected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get health metrics for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_agent_health_alert(self, 
                                      agent_id: str,
                                      alert_name: str,
                                      severity: AlertSeverity,
                                      message: str,
                                      user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a health alert for a specific agent."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_agent_health_alert_start", success=True, 
                                                   details={"agent_id": agent_id, "alert_name": alert_name})
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_health", "write"):
                        await self.record_health_metric("create_agent_health_alert_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("create_agent_health_alert_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("create_agent_health_alert_tenant_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("create_agent_health_alert_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.debug(f"Creating health alert for agent {agent_id}: {alert_name}")
            
            # Create agent-specific alert
            result = await self.health_composition_service.create_health_alert(
                alert_name=alert_name,
                severity=severity,
                message=message,
                service_id=f"agent_{agent_id}",
                agent_id=agent_id
            )
            
            # Record success metric
            await self.record_health_metric("create_agent_health_alert_success", 1.0, {"agent_id": agent_id, "alert_name": alert_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_agent_health_alert_complete", success=True, 
                                                   details={"agent_id": agent_id, "alert_name": alert_name})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_agent_health_alert", details={"agent_id": agent_id, "alert_name": alert_name})
            self.logger.error(f"Failed to create health alert for agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "alert_name": alert_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health service health."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("health_check_start", success=True)
            
            self.logger.debug("Checking health service health")
            
            # Check underlying services
            abstraction_health = await self.health_abstraction.health_check()
            composition_health = await self.health_composition_service.health_check()
            
            result = {
                "status": "healthy" if all(
                    h.get("status") == "healthy" 
                    for h in [abstraction_health, composition_health]
                ) else "unhealthy",
                "service": self.service_name,
                "abstraction_health": abstraction_health,
                "composition_health": composition_health,
                "monitoring_types": list(self.agent_health_monitoring.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("health_check_success", 1.0, {"status": result["status"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("health_check_complete", success=True, details={"status": result["status"]})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "health_check")
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # AGENT-SPECIFIC HEALTH MONITORING
    # ============================================================================
    
    async def _monitor_llm_health(self, 
                                context: HealthContext, 
                                operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor health for LLM operations."""
        try:
            # Check LLM-specific health
            llm_health = await self.health_abstraction.check_health(
                HealthType.APPLICATION,
                context
            )
            
            # Collect LLM metrics
            llm_metrics = await self.health_abstraction.collect_metrics(
                HealthType.APPLICATION,
                context
            )
            
            # Determine if LLM operation is healthy
            is_healthy = llm_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            
            return {
                "success": True,
                "operation_healthy": is_healthy,
                "health_status": llm_health.status.value,
                "health_message": llm_health.message,
                "metrics_count": len(llm_metrics),
                "monitoring_type": "llm_health"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "monitoring_type": "llm_health"
            }
    
    async def _monitor_mcp_health(self, 
                                context: HealthContext, 
                                operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor health for MCP operations."""
        try:
            # Check MCP-specific health
            mcp_health = await self.health_abstraction.check_health(
                HealthType.SERVICE,
                context
            )
            
            # Collect MCP metrics
            mcp_metrics = await self.health_abstraction.collect_metrics(
                HealthType.SERVICE,
                context
            )
            
            # Determine if MCP operation is healthy
            is_healthy = mcp_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            
            return {
                "success": True,
                "operation_healthy": is_healthy,
                "health_status": mcp_health.status.value,
                "health_message": mcp_health.message,
                "metrics_count": len(mcp_metrics),
                "monitoring_type": "mcp_health"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "monitoring_type": "mcp_health"
            }
    
    async def _monitor_tool_health(self, 
                                 context: HealthContext, 
                                 operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor health for Tool operations."""
        try:
            # Check tool-specific health
            tool_health = await self.health_abstraction.check_health(
                HealthType.APPLICATION,
                context
            )
            
            # Collect tool metrics
            tool_metrics = await self.health_abstraction.collect_metrics(
                HealthType.APPLICATION,
                context
            )
            
            # Determine if tool operation is healthy
            is_healthy = tool_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            
            return {
                "success": True,
                "operation_healthy": is_healthy,
                "health_status": tool_health.status.value,
                "health_message": tool_health.message,
                "metrics_count": len(tool_metrics),
                "monitoring_type": "tool_health"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "monitoring_type": "tool_health"
            }
    
    async def _monitor_agent_health(self, 
                                  context: HealthContext, 
                                  operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Monitor health for general agent operations."""
        try:
            # Check agent-specific health
            agent_health = await self.health_abstraction.check_health(
                HealthType.AGENT,
                context
            )
            
            # Collect agent metrics
            agent_metrics = await self.health_abstraction.collect_metrics(
                HealthType.AGENT,
                context
            )
            
            # Determine if agent operation is healthy
            is_healthy = agent_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            
            return {
                "success": True,
                "operation_healthy": is_healthy,
                "health_status": agent_health.status.value,
                "health_message": agent_health.message,
                "metrics_count": len(agent_metrics),
                "monitoring_type": "agent_health"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "monitoring_type": "agent_health"
            }
    
    def _calculate_agent_health_score(self, health_report: HealthReport) -> float:
        """Calculate agent health score."""
        if not health_report.health_checks:
            return 0.0
        
        # Simple scoring based on health status
        status_scores = {
            HealthStatus.HEALTHY: 100.0,
            HealthStatus.DEGRADED: 60.0,
            HealthStatus.UNHEALTHY: 20.0,
            HealthStatus.UNKNOWN: 50.0
        }
        
        total_score = sum(status_scores.get(check.status, 0.0) for check in health_report.health_checks)
        return total_score / len(health_report.health_checks)
    
    def _generate_health_recommendations(self, health_report: HealthReport) -> List[str]:
        """Generate health recommendations based on health report."""
        recommendations = []
        
        for check in health_report.health_checks:
            if check.status == HealthStatus.UNHEALTHY:
                recommendations.append(f"Critical: {check.message}")
            elif check.status == HealthStatus.DEGRADED:
                recommendations.append(f"Warning: {check.message}")
        
        if not recommendations:
            recommendations.append("Agent health is optimal")
        
        return recommendations
    
    def _analyze_agent_metrics(self, agent_metrics: List[HealthMetric], system_metrics: List[HealthMetric]) -> Dict[str, Any]:
        """Analyze agent metrics and provide insights."""
        return {
            "agent_metrics_count": len(agent_metrics),
            "system_metrics_count": len(system_metrics),
            "key_metrics": {
                "availability": next((m.value for m in agent_metrics if "availability" in m.name), 0.0),
                "response_time": next((m.value for m in agent_metrics if "response_time" in m.name), 0.0),
                "error_rate": next((m.value for m in agent_metrics if "error_rate" in m.name), 0.0)
            },
            "system_context": {
                "cpu_usage": next((m.value for m in system_metrics if "cpu" in m.name), 0.0),
                "memory_usage": next((m.value for m in system_metrics if "memory" in m.name), 0.0)
            }
        }

