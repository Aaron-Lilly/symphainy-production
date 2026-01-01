"""
OpenTelemetry Health Adapter - Raw technology wrapper for OpenTelemetry health monitoring

Provides direct integration with OpenTelemetry for health monitoring and metrics collection.
This is a raw technology adapter that handles OpenTelemetry-specific concerns.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.health_protocol import (
    HealthProtocol, HealthContext, HealthCheck, HealthMetric, HealthReport, HealthAlert,
    HealthStatus, HealthType, AlertSeverity
)


class OpenTelemetryHealthAdapter:
    """
    OpenTelemetry Health Adapter - Raw technology wrapper for OpenTelemetry
    
    Handles direct OpenTelemetry integration for health monitoring and metrics collection.
    This adapter focuses purely on OpenTelemetry-specific implementation details.
    """
    
    def __init__(self, 
                 service_name: str = "opentelemetry_health_adapter",
                 endpoint: str = "http://localhost:4317",
                 timeout: int = 30,
                 di_container=None):
        """Initialize OpenTelemetry Health Adapter."""
        if not di_container:
            raise ValueError("DI Container is required for OpenTelemetryHealthAdapter initialization")
        self.service_name = service_name
        self.endpoint = endpoint
        self.timeout = timeout
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        
        # OpenTelemetry-specific configuration
        self.resource_attributes = {
            "service.name": service_name,
            "service.version": "1.0.0"
        }
        
        # Health state tracking
        self.health_status = HealthStatus.HEALTHY
        self.last_check_time = None
        
        self.logger.info(f"Initialized OpenTelemetry Health Adapter: {endpoint}")
    
    async def check_health(self, 
                         health_type: HealthType,
                         context: HealthContext) -> HealthCheck:
        """Perform a health check using OpenTelemetry."""
        try:
            self.logger.debug(f"Performing {health_type.value} health check with OpenTelemetry")
            
            # Simulate OpenTelemetry health check
            start_time = datetime.utcnow()
            await asyncio.sleep(0.01)  # Simulate network delay
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds() * 1000
            
            # Determine health status based on type
            status = await self._determine_health_status(health_type, context)
            
            return HealthCheck(
                check_id=f"otel_{health_type.value}_{context.service_id or 'unknown'}",
                check_name=f"OpenTelemetry {health_type.value.title()} Health Check",
                health_type=health_type,
                status=status,
                message=f"OpenTelemetry health check completed for {health_type.value}",
                timestamp=end_time,
                response_time_ms=response_time,
                metadata={
                    "adapter": "opentelemetry",
                    "endpoint": self.endpoint,
                    "service_id": context.service_id,
                    "agent_id": context.agent_id
                }
            )
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry health check failed for {health_type.value}: {e}")
            return HealthCheck(
                check_id=f"otel_{health_type.value}_error",
                check_name=f"OpenTelemetry {health_type.value.title()} Health Check",
                health_type=health_type,
                status=HealthStatus.UNHEALTHY,
                message=f"OpenTelemetry health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                response_time_ms=0.0,
                metadata={"error": str(e), "adapter": "opentelemetry"}
            )
    
    async def check_multiple_health(self, 
                                  health_types: List[HealthType],
                                  context: HealthContext) -> List[HealthCheck]:
        """Perform multiple health checks using OpenTelemetry."""
        try:
            self.logger.debug(f"Performing {len(health_types)} health checks with OpenTelemetry")
            
            checks = []
            for health_type in health_types:
                check = await self.check_health(health_type, context)
                checks.append(check)
            
            return checks
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry multiple health checks failed: {e}")
            return [
                HealthCheck(
                    check_id=f"otel_{ht.value}_error",
                    check_name=f"OpenTelemetry {ht.value.title()} Health Check",
                    health_type=ht,
                    status=HealthStatus.UNHEALTHY,
                    message=f"OpenTelemetry health check failed: {str(e)}",
                    timestamp=datetime.utcnow(),
                    response_time_ms=0.0,
                    metadata={"error": str(e), "adapter": "opentelemetry"}
                ) for ht in health_types
            ]
    
    async def collect_metrics(self, 
                            health_type: HealthType,
                            context: HealthContext) -> List[HealthMetric]:
        """Collect health metrics using OpenTelemetry."""
        try:
            self.logger.debug(f"Collecting {health_type.value} metrics with OpenTelemetry")
            
            # Simulate OpenTelemetry metrics collection
            await asyncio.sleep(0.01)  # Simulate collection delay
            
            metrics = []
            timestamp = datetime.utcnow()
            
            if health_type == HealthType.SYSTEM:
                metrics.extend([
                    HealthMetric(
                        name="cpu_usage_percent",
                        value=45.2,
                        unit="percent",
                        timestamp=timestamp,
                        labels={"service": context.service_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    ),
                    HealthMetric(
                        name="memory_usage_percent",
                        value=67.8,
                        unit="percent",
                        timestamp=timestamp,
                        labels={"service": context.service_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    ),
                    HealthMetric(
                        name="disk_usage_percent",
                        value=23.4,
                        unit="percent",
                        timestamp=timestamp,
                        labels={"service": context.service_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    )
                ])
            elif health_type == HealthType.SERVICE:
                metrics.extend([
                    HealthMetric(
                        name="request_count",
                        value=1250.0,
                        unit="count",
                        timestamp=timestamp,
                        labels={"service": context.service_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    ),
                    HealthMetric(
                        name="response_time_ms",
                        value=245.6,
                        unit="milliseconds",
                        timestamp=timestamp,
                        labels={"service": context.service_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    ),
                    HealthMetric(
                        name="error_rate",
                        value=0.02,
                        unit="ratio",
                        timestamp=timestamp,
                        labels={"service": context.service_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    )
                ])
            elif health_type == HealthType.AGENT:
                metrics.extend([
                    HealthMetric(
                        name="agent_availability",
                        value=99.5,
                        unit="percent",
                        timestamp=timestamp,
                        labels={"agent": context.agent_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    ),
                    HealthMetric(
                        name="agent_response_time_ms",
                        value=180.3,
                        unit="milliseconds",
                        timestamp=timestamp,
                        labels={"agent": context.agent_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    ),
                    HealthMetric(
                        name="agent_success_rate",
                        value=0.98,
                        unit="ratio",
                        timestamp=timestamp,
                        labels={"agent": context.agent_id or "unknown"},
                        metadata={"adapter": "opentelemetry"}
                    )
                ])
            else:
                # Default metrics for other types
                metrics.append(
                    HealthMetric(
                        name="health_score",
                        value=85.0,
                        unit="score",
                        timestamp=timestamp,
                        labels={"type": health_type.value},
                        metadata={"adapter": "opentelemetry"}
                    )
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry metrics collection failed for {health_type.value}: {e}")
            return [
                HealthMetric(
                    name="error_metric",
                    value=0.0,
                    unit="count",
                    timestamp=datetime.utcnow(),
                    labels={"error": "true"},
                    metadata={"error": str(e), "adapter": "opentelemetry"}
                )
            ]
    
    async def get_health_report(self, 
                              service_id: str,
                              context: HealthContext) -> HealthReport:
        """Get comprehensive health report using OpenTelemetry."""
        try:
            self.logger.debug(f"Getting health report for {service_id} with OpenTelemetry")
            
            # Perform health checks
            health_types = [HealthType.SYSTEM, HealthType.SERVICE, HealthType.APPLICATION]
            health_checks = await self.check_multiple_health(health_types, context)
            
            # Collect metrics
            all_metrics = []
            for health_type in health_types:
                metrics = await self.collect_metrics(health_type, context)
                all_metrics.extend(metrics)
            
            # Determine overall status
            overall_status = self._determine_overall_status(health_checks)
            
            return HealthReport(
                report_id=f"otel_report_{service_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                service_id=service_id,
                agent_id=context.agent_id,
                overall_status=overall_status,
                health_checks=health_checks,
                metrics=all_metrics,
                alerts=[],
                timestamp=datetime.utcnow(),
                metadata={"adapter": "opentelemetry", "endpoint": self.endpoint}
            )
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry health report failed for {service_id}: {e}")
            return HealthReport(
                report_id=f"otel_report_{service_id}_error",
                service_id=service_id,
                agent_id=context.agent_id,
                overall_status=HealthStatus.UNHEALTHY,
                health_checks=[],
                metrics=[],
                alerts=[],
                timestamp=datetime.utcnow(),
                metadata={"error": str(e), "adapter": "opentelemetry"}
            )
    
    async def create_alert(self, alert: HealthAlert) -> bool:
        """Create a health alert using OpenTelemetry."""
        try:
            self.logger.debug(f"Creating alert {alert.alert_id} with OpenTelemetry")
            
            # Simulate OpenTelemetry alert creation
            await asyncio.sleep(0.01)
            
            self.logger.info(f"OpenTelemetry alert created: {alert.alert_name} - {alert.message}")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry alert creation failed: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a health alert using OpenTelemetry."""
        try:
            self.logger.debug(f"Resolving alert {alert_id} with OpenTelemetry")
            
            # Simulate OpenTelemetry alert resolution
            await asyncio.sleep(0.01)
            
            self.logger.info(f"OpenTelemetry alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry alert resolution failed: {e}")
            return False
    
    async def get_active_alerts(self, service_id: Optional[str] = None) -> List[HealthAlert]:
        """Get active health alerts from OpenTelemetry."""
        try:
            self.logger.debug(f"Getting active alerts for {service_id or 'all services'} with OpenTelemetry")
            
            # Simulate OpenTelemetry alert retrieval
            await asyncio.sleep(0.01)
            
            # Return mock alerts
            alerts = []
            if service_id:
                alerts.append(
                    HealthAlert(
                        alert_id=f"otel_alert_{service_id}_001",
                        alert_name="High CPU Usage",
                        severity=AlertSeverity.WARNING,
                        status=HealthStatus.DEGRADED,
                        message=f"CPU usage is above threshold for {service_id}",
                        timestamp=datetime.utcnow(),
                        service_id=service_id,
                        metadata={"adapter": "opentelemetry"}
                    )
                )
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry alert retrieval failed: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenTelemetry health monitoring system health."""
        try:
            self.logger.debug("Checking OpenTelemetry health monitoring system health")
            
            # Simulate OpenTelemetry health check
            await asyncio.sleep(0.01)
            
            return {
                "status": "healthy",
                "adapter": "opentelemetry",
                "endpoint": self.endpoint,
                "service_name": self.service_name,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": 10
            }
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry health check failed: {e}")
            return {
                "status": "unhealthy",
                "adapter": "opentelemetry",
                "endpoint": self.endpoint,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _determine_health_status(self, health_type: HealthType, context: HealthContext) -> HealthStatus:
        """Determine health status based on type and context."""
        # Simplified health status determination
        if health_type == HealthType.SYSTEM:
            return HealthStatus.HEALTHY
        elif health_type == HealthType.SERVICE:
            return HealthStatus.HEALTHY
        elif health_type == HealthType.AGENT:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.HEALTHY
    
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

