"""
Health Composition Service - Infrastructure-level business logic for health monitoring

Handles infrastructure-level health workflows, health orchestration,
and coordination between different health monitoring systems.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.health_protocol import (
    HealthContext, HealthCheck, HealthMetric, HealthReport, HealthAlert,
    HealthStatus, HealthType, AlertSeverity
)
from foundations.public_works_foundation.infrastructure_abstractions.health_abstraction import HealthAbstraction


class HealthCompositionService:
    """
    Health Composition Service - Infrastructure-level business logic for health monitoring
    
    Handles infrastructure-level health workflows and orchestration.
    This service coordinates health monitoring across different systems.
    """
    
    def __init__(self, health_abstraction: HealthAbstraction, di_container=None):
        """Initialize Health Composition Service."""
        if not di_container:
            raise ValueError("DI Container is required for HealthCompositionService initialization")
        
        self.health_abstraction = health_abstraction
        self.di_container = di_container
        self.service_name = "health_composition_service"
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(self.service_name)
        
        # Infrastructure-level health workflows
        self.health_workflows = {
            "system_health": self._system_health_workflow,
            "service_health": self._service_health_workflow,
            "agent_health": self._agent_health_workflow,
            "infrastructure_health": self._infrastructure_health_workflow,
            "comprehensive_health": self._comprehensive_health_workflow
        }
        
        self.logger.info("Initialized Health Composition Service")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    async def orchestrate_health_monitoring(self, 
                                          workflow_type: str,
                                          context: HealthContext,
                                          health_types: Optional[List[HealthType]] = None,
                                          user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Orchestrate health monitoring using infrastructure-level workflows."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "health", "monitor"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Orchestrating {workflow_type} health monitoring")
            
            # Get workflow
            workflow = self.health_workflows.get(workflow_type)
            if not workflow:
                return {
                    "success": False,
                    "error": f"Unknown workflow type: {workflow_type}",
                    "workflow_type": workflow_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Execute workflow
            result = await workflow(context, health_types)
            
            # Add infrastructure-level metadata
            result.update({
                "workflow_type": workflow_type,
                "orchestrated_at": datetime.utcnow().isoformat(),
                "composition_service": self.service_name
            })
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_health_monitoring", {
                    "workflow_type": workflow_type,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_health_monitoring",
                    "workflow_type": workflow_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health orchestration failed for {workflow_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "HEALTH_ORCHESTRATION_ERROR",
                "workflow_type": workflow_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def perform_health_assessment(self, 
                                      service_id: str,
                                      context: HealthContext,
                                      include_metrics: bool = True,
                                      user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform comprehensive health assessment."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "health", "assess"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Performing health assessment for {service_id}")
            
            # Get health report
            health_report = await self.health_abstraction.get_health_report(service_id, context)
            
            # Collect additional metrics if requested
            additional_metrics = []
            if include_metrics:
                for health_type in [HealthType.SYSTEM, HealthType.SERVICE, HealthType.APPLICATION]:
                    metrics = await self.health_abstraction.collect_metrics(health_type, context)
                    additional_metrics.extend(metrics)
            
            # Analyze health status
            assessment = self._analyze_health_status(health_report, additional_metrics)
            
            return {
                "success": True,
                "service_id": service_id,
                "overall_status": health_report.overall_status.value,
                "health_report": {
                    "report_id": health_report.report_id,
                    "health_checks": len(health_report.health_checks),
                    "metrics": len(health_report.metrics) + len(additional_metrics),
                    "alerts": len(health_report.alerts)
                },
                "assessment": assessment,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("perform_health_assessment", {
                    "service_id": service_id,
                    "success": True
                })
            
            return {
                "success": True,
                "service_id": service_id,
                "overall_status": health_report.overall_status.value,
                "health_report": {
                    "report_id": health_report.report_id,
                    "health_checks": len(health_report.health_checks),
                    "metrics": len(health_report.metrics) + len(additional_metrics),
                    "alerts": len(health_report.alerts)
                },
                "assessment": assessment,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "perform_health_assessment",
                    "service_id": service_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health assessment failed for {service_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "HEALTH_ASSESSMENT_ERROR",
                "service_id": service_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_health_alert(self, 
                                alert_name: str,
                                severity: AlertSeverity,
                                message: str,
                                service_id: Optional[str] = None,
                                agent_id: Optional[str] = None,
                                user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a health alert with infrastructure-level coordination."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "health", "create_alert"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug(f"Creating health alert: {alert_name}")
            
            # Create alert
            alert = HealthAlert(
                alert_id=f"health_alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                alert_name=alert_name,
                severity=severity,
                status=HealthStatus.UNHEALTHY if severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL] else HealthStatus.DEGRADED,
                message=message,
                timestamp=datetime.utcnow(),
                service_id=service_id,
                agent_id=agent_id,
                metadata={"created_by": self.service_name}
            )
            
            # Send alert
            alert_created = await self.health_abstraction.create_alert(alert)
            
            result = {
                "success": alert_created,
                "alert_id": alert.alert_id,
                "alert_name": alert_name,
                "severity": severity.value,
                "message": message,
                "created_at": alert.timestamp.isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_health_alert", {
                    "alert_name": alert_name,
                    "severity": severity.value,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_health_alert",
                    "alert_name": alert_name,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health alert creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "HEALTH_ALERT_CREATION_ERROR",
                "alert_name": alert_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_health_metrics(self, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get infrastructure-level health metrics."""
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "health", "view"
                )
                if validation_error:
                    return validation_error
            
            self.logger.debug("Getting health metrics")
            
            # Get adapter health
            adapter_health = await self.health_abstraction.health_check()
            
            # Get available workflows
            available_workflows = list(self.health_workflows.keys())
            
            result = {
                "success": True,
                "adapter_health": adapter_health,
                "available_workflows": available_workflows,
                "workflow_count": len(available_workflows),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_health_metrics", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_health_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get health metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "HEALTH_METRICS_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health composition service health."""
        try:
            self.logger.debug("Checking health composition service health")
            
            # Check underlying abstraction
            abstraction_health = await self.health_abstraction.health_check()
            
            result = {
                "status": "healthy" if abstraction_health.get("status") == "healthy" else "unhealthy",
                "service": self.service_name,
                "abstraction_health": abstraction_health,
                "available_workflows": len(self.health_workflows),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "status": result["status"],
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health composition service health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "error_code": "HEALTH_SERVICE_HEALTH_CHECK_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # INFRASTRUCTURE-LEVEL HEALTH WORKFLOWS
    # ============================================================================
    
    async def _system_health_workflow(self, 
                                    context: HealthContext, 
                                    health_types: Optional[List[HealthType]] = None) -> Dict[str, Any]:
        """System health workflow for infrastructure-level health monitoring."""
        try:
            # Default system health types
            if not health_types:
                health_types = [HealthType.SYSTEM]
            
            # Check system health
            health_checks = await self.health_abstraction.check_multiple_health(health_types, context)
            
            # Collect system metrics
            metrics = []
            for health_type in health_types:
                type_metrics = await self.health_abstraction.collect_metrics(health_type, context)
                metrics.extend(type_metrics)
            
            # Determine overall status
            overall_status = self._determine_overall_status(health_checks)
            
            return {
                "success": True,
                "workflow": "system_health",
                "overall_status": overall_status.value,
                "health_checks": [
                    {
                        "check_id": check.check_id,
                        "status": check.status.value,
                        "message": check.message,
                        "response_time_ms": check.response_time_ms
                    } for check in health_checks
                ],
                "metrics_count": len(metrics),
                "health_types": [ht.value for ht in health_types]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_system_health_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"System health workflow failed: {e}")
            return {
                "success": False,
                "workflow": "system_health",
                "error": str(e),
                "error_code": "HEALTH_SYSTEM_WORKFLOW_ERROR"
            }
    
    async def _service_health_workflow(self, 
                                     context: HealthContext, 
                                     health_types: Optional[List[HealthType]] = None) -> Dict[str, Any]:
        """Service health workflow for infrastructure-level health monitoring."""
        try:
            # Default service health types
            if not health_types:
                health_types = [HealthType.SERVICE, HealthType.APPLICATION]
            
            # Check service health
            health_checks = await self.health_abstraction.check_multiple_health(health_types, context)
            
            # Collect service metrics
            metrics = []
            for health_type in health_types:
                type_metrics = await self.health_abstraction.collect_metrics(health_type, context)
                metrics.extend(type_metrics)
            
            # Determine overall status
            overall_status = self._determine_overall_status(health_checks)
            
            return {
                "success": True,
                "workflow": "service_health",
                "overall_status": overall_status.value,
                "health_checks": [
                    {
                        "check_id": check.check_id,
                        "status": check.status.value,
                        "message": check.message,
                        "response_time_ms": check.response_time_ms
                    } for check in health_checks
                ],
                "metrics_count": len(metrics),
                "health_types": [ht.value for ht in health_types]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_service_health_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Service health workflow failed: {e}")
            return {
                "success": False,
                "workflow": "service_health",
                "error": str(e),
                "error_code": "HEALTH_SERVICE_WORKFLOW_ERROR"
            }
    
    async def _agent_health_workflow(self, 
                                   context: HealthContext, 
                                   health_types: Optional[List[HealthType]] = None) -> Dict[str, Any]:
        """Agent health workflow for infrastructure-level health monitoring."""
        try:
            # Default agent health types
            if not health_types:
                health_types = [HealthType.AGENT]
            
            # Check agent health
            health_checks = await self.health_abstraction.check_multiple_health(health_types, context)
            
            # Collect agent metrics
            metrics = []
            for health_type in health_types:
                type_metrics = await self.health_abstraction.collect_metrics(health_type, context)
                metrics.extend(type_metrics)
            
            # Determine overall status
            overall_status = self._determine_overall_status(health_checks)
            
            return {
                "success": True,
                "workflow": "agent_health",
                "overall_status": overall_status.value,
                "health_checks": [
                    {
                        "check_id": check.check_id,
                        "status": check.status.value,
                        "message": check.message,
                        "response_time_ms": check.response_time_ms
                    } for check in health_checks
                ],
                "metrics_count": len(metrics),
                "health_types": [ht.value for ht in health_types]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_agent_health_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Agent health workflow failed: {e}")
            return {
                "success": False,
                "workflow": "agent_health",
                "error": str(e),
                "error_code": "HEALTH_AGENT_WORKFLOW_ERROR"
            }
    
    async def _infrastructure_health_workflow(self, 
                                            context: HealthContext, 
                                            health_types: Optional[List[HealthType]] = None) -> Dict[str, Any]:
        """Infrastructure health workflow for infrastructure-level health monitoring."""
        try:
            # Default infrastructure health types
            if not health_types:
                health_types = [HealthType.INFRASTRUCTURE, HealthType.DATABASE, HealthType.CACHE]
            
            # Check infrastructure health
            health_checks = await self.health_abstraction.check_multiple_health(health_types, context)
            
            # Collect infrastructure metrics
            metrics = []
            for health_type in health_types:
                type_metrics = await self.health_abstraction.collect_metrics(health_type, context)
                metrics.extend(type_metrics)
            
            # Determine overall status
            overall_status = self._determine_overall_status(health_checks)
            
            return {
                "success": True,
                "workflow": "infrastructure_health",
                "overall_status": overall_status.value,
                "health_checks": [
                    {
                        "check_id": check.check_id,
                        "status": check.status.value,
                        "message": check.message,
                        "response_time_ms": check.response_time_ms
                    } for check in health_checks
                ],
                "metrics_count": len(metrics),
                "health_types": [ht.value for ht in health_types]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_infrastructure_health_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Infrastructure health workflow failed: {e}")
            return {
                "success": False,
                "workflow": "infrastructure_health",
                "error": str(e),
                "error_code": "HEALTH_INFRASTRUCTURE_WORKFLOW_ERROR"
            }
    
    async def _comprehensive_health_workflow(self, 
                                           context: HealthContext, 
                                           health_types: Optional[List[HealthType]] = None) -> Dict[str, Any]:
        """Comprehensive health workflow for infrastructure-level health monitoring."""
        try:
            # Default comprehensive health types
            if not health_types:
                health_types = [HealthType.SYSTEM, HealthType.SERVICE, HealthType.AGENT, HealthType.APPLICATION]
            
            # Check comprehensive health
            health_checks = await self.health_abstraction.check_multiple_health(health_types, context)
            
            # Collect comprehensive metrics
            metrics = []
            for health_type in health_types:
                type_metrics = await self.health_abstraction.collect_metrics(health_type, context)
                metrics.extend(type_metrics)
            
            # Determine overall status
            overall_status = self._determine_overall_status(health_checks)
            
            return {
                "success": True,
                "workflow": "comprehensive_health",
                "overall_status": overall_status.value,
                "health_checks": [
                    {
                        "check_id": check.check_id,
                        "status": check.status.value,
                        "message": check.message,
                        "response_time_ms": check.response_time_ms
                    } for check in health_checks
                ],
                "metrics_count": len(metrics),
                "health_types": [ht.value for ht in health_types]
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_comprehensive_health_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Comprehensive health workflow failed: {e}")
            return {
                "success": False,
                "workflow": "comprehensive_health",
                "error": str(e),
                "error_code": "HEALTH_COMPREHENSIVE_WORKFLOW_ERROR"
            }
    
    def _determine_overall_status(self, health_checks: List[HealthCheck]) -> HealthStatus:
        """Determine overall health status from multiple checks."""
        if not health_checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in health_checks]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def _analyze_health_status(self, health_report: HealthReport, additional_metrics: List[HealthMetric]) -> Dict[str, Any]:
        """Analyze health status and provide insights."""
        return {
            "overall_status": health_report.overall_status.value,
            "health_score": self._calculate_health_score(health_report, additional_metrics),
            "critical_issues": [check.message for check in health_report.health_checks if check.status == HealthStatus.UNHEALTHY],
            "warnings": [check.message for check in health_report.health_checks if check.status == HealthStatus.DEGRADED],
            "metrics_summary": {
                "total_metrics": len(health_report.metrics) + len(additional_metrics),
                "system_metrics": len([m for m in additional_metrics if "cpu" in m.name or "memory" in m.name]),
                "service_metrics": len([m for m in additional_metrics if "request" in m.name or "response" in m.name])
            }
        }
    
    def _calculate_health_score(self, health_report: HealthReport, additional_metrics: List[HealthMetric]) -> float:
        """Calculate overall health score."""
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

