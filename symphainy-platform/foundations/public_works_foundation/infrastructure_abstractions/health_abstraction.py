"""
Health Abstraction - Infrastructure abstraction for health monitoring

Coordinates health adapters and handles infrastructure-level concerns like
error handling, retries, logging, and adapter selection.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.health_protocol import (
    HealthProtocol, HealthContext, HealthCheck, HealthMetric, HealthReport, HealthAlert,
    HealthStatus, HealthType, AlertSeverity
)

# Alias for backward compatibility
HealthCheckResult = HealthCheck

class HealthAbstraction:
    """
    Health Abstraction - Infrastructure abstraction for health monitoring
    
    Coordinates different health adapters and handles infrastructure-level concerns.
    This layer provides swappable health monitoring engines and infrastructure coordination.
    
    NOTE: This abstraction accepts a health adapter via dependency injection.
          All adapter creation happens in Public Works Foundation Service.
    """
    
    def __init__(self,
                 health_adapter: HealthProtocol,  # Required: Accept adapter via DI
                 config_adapter=None,
                 service_name: str = "health_abstraction",
                 di_container=None):
        """
        Initialize Health Abstraction.
        
        Args:
            health_adapter: Health adapter implementing HealthProtocol (required)
            config_adapter: Configuration adapter (optional)
            service_name: Service name for logging (optional)
            di_container: DI Container for logging (required)
        """
        if not health_adapter:
            raise ValueError("HealthAbstraction requires health_adapter via dependency injection")
        
        self.service_name = service_name
        if not di_container:
            raise ValueError("DI Container is required for HealthAbstraction initialization")
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        self.config_adapter = config_adapter
        
        # Use injected adapter
        self.adapter = health_adapter
        self.adapter_type = getattr(health_adapter, 'adapter_type', 'unknown')
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"Initialized Health Abstraction with {self.adapter_type} adapter")
    
    async def check_health(self, 
                         health_type: HealthType,
                         context: Dict[str, Any] = None) -> HealthCheck:
        """Check health with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Checking {health_type.value} health with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Check health with retry logic
            result = await self._check_with_retry(
                self.adapter.check_health,
                health_type,
                enhanced_context
            )
            
            # Add infrastructure-level metadata
            result.metadata = result.metadata or {}
            result.metadata.update({
                "adapter_type": self.adapter_type,
                "abstraction_layer": "health_abstraction",
                "checked_at": datetime.utcnow().isoformat()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Health check failed for {health_type.value}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def check_multiple_health(self, 
                                  health_types: List[HealthType],
                                  context: Dict[str, Any] = None) -> List[HealthCheck]:
        """Check multiple health types with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Checking {len(health_types)} health types with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Check health with retry logic
            results = await self._check_with_retry(
                self.adapter.check_multiple_health,
                health_types,
                enhanced_context
            )
            
            # Add infrastructure-level metadata to all results
            for result in results:
                result.metadata = result.metadata or {}
                result.metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "health_abstraction",
                    "checked_at": datetime.utcnow().isoformat()
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Multiple health checks failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def collect_health_metrics(self, 
                            health_type: HealthType,
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collect health metrics with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Collecting {health_type.value} metrics with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Collect metrics with retry logic
            metrics = await self._check_with_retry(
                self.adapter.collect_metrics,
                health_type,
                enhanced_context
            )
            
            # Add infrastructure-level metadata to all metrics
            for metric in metrics:
                metric.metadata = metric.metadata or {}
                metric.metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "health_abstraction",
                    "collected_at": datetime.utcnow().isoformat()
                })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed for {health_type.value}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_health_report(self, 
                              service_id: str,
                              context: Dict[str, Any] = None) -> HealthReport:
        """Get health report with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting health report for {service_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Get report with retry logic
            report = await self._check_with_retry(
                self.adapter.get_health_report,
                service_id,
                enhanced_context
            )
            
            # Add infrastructure-level metadata
            report.metadata = report.metadata or {}
            report.metadata.update({
                "adapter_type": self.adapter_type,
                "abstraction_layer": "health_abstraction",
                "generated_at": datetime.utcnow().isoformat()
            })
            
            return report
            
        except Exception as e:
            self.logger.error(f"Health report failed for {service_id}: {e}")
            raise  # Re-raise for service layer to handle

        """Create health alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Creating alert {alert.alert_id} with {self.adapter_type}")
            
            # Create alert with retry logic
            result = await self._check_with_retry(
                self.adapter.create_alert,
                alert
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Alert creation failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def resolve_health_alert(self, alert_id: str) -> bool:
        """Resolve health alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Resolving alert {alert_id} with {self.adapter_type}")
            
            # Resolve alert with retry logic
            result = await self._check_with_retry(
                self.adapter.resolve_alert,
                alert_id
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Alert resolution failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_active_alerts(self, service_id: str = None) -> List[HealthAlert]:
        """Get active alerts with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting active alerts for {service_id or 'all services'} with {self.adapter_type}")
            
            # Get alerts with retry logic
            alerts = await self._check_with_retry(
                self.adapter.get_active_alerts,
                service_id
            )
            
            # Add infrastructure-level metadata to all alerts
            for alert in alerts:
                alert.metadata = alert.metadata or {}
                alert.metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "health_abstraction",
                    "retrieved_at": datetime.utcnow().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Alert retrieval failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health monitoring infrastructure health."""
        try:
            self.logger.debug("Checking health monitoring infrastructure health")
            
            # Check adapter health
            adapter_health = await self.adapter.health_check()
            
            # Add abstraction-level health info
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction_layer": "health_abstraction",
                "adapter_type": self.adapter_type,
                "adapter_health": adapter_health,
                "infrastructure_metrics": {
                    "max_retries": self.max_retries,
                    "retry_delay": self.retry_delay,
                    "timeout": self.timeout
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health monitoring infrastructure health check failed: {e}")
    
            raise  # Re-raise for service layer to handle

        """Add infrastructure-level context enhancements."""
        # Add infrastructure metadata
        enhanced_metadata = context.metadata or {}
        enhanced_metadata.update({
            "abstraction_layer": "health_abstraction",
            "adapter_type": self.adapter_type,
            "check_timestamp": datetime.utcnow().isoformat()
        })
        
        # Create enhanced context
        return HealthContext(
            service_id=context.service_id,
            agent_id=context.agent_id,
            tenant_id=context.tenant_id,
            environment=context.environment,
            region=context.region,
            metadata=enhanced_metadata
        )
    
    async def _check_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
                raise  # Re-raise for service layer to handle

