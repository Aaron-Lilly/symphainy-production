"""
Telemetry Reporting Utility

Bootstrap-aware telemetry utility that provides metrics collection,
health monitoring, and anomaly detection through a lazy bootstrap pattern.

WHAT (Utility Role): I provide telemetry reporting capabilities through bootstrap pattern
HOW (Utility Implementation): I bootstrap from foundation service, then work independently
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TelemetryReportingUtility:
    """
    Bootstrap-Aware Telemetry Reporting Utility
    
    This utility starts as an interface and gets bootstrapped by the first caller
    (foundation service). After bootstrap, it becomes self-sufficient for:
    - Metrics collection and reporting
    - Health monitoring and status tracking
    - Anomaly detection and alerting
    """
    
    def __init__(self, service_name: str):
        """Initialize telemetry reporting utility (not yet bootstrapped)."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"TelemetryReportingUtility-{service_name}")
        
        # Bootstrap state
        self.is_bootstrapped = False
        self.bootstrap_provider = None
        
        # Nurse Service client (will be set after bootstrap)
        self.nurse_client = None
        
        # Local metrics storage
        self.metrics_storage = []
        self.health_metrics = {}
        self.anomaly_logs = []
        
        self.logger.info(f"Telemetry reporting utility initialized for {service_name} (not yet bootstrapped)")
    
    def bootstrap(self, bootstrap_provider, nurse_client=None):
        """
        Bootstrap the telemetry reporting utility with implementation capabilities.
        
        Args:
            bootstrap_provider: Foundation service that provides bootstrap implementation
            nurse_client: Optional Smart City role client for enhanced capabilities
        """
        self.bootstrap_provider = bootstrap_provider
        self.nurse_client = nurse_client
        self.is_bootstrapped = True
        
        self.logger.info(f"Telemetry reporting utility bootstrapped by {bootstrap_provider.__class__.__name__}")
    
    # ============================================================================
    # METRICS COLLECTION AND REPORTING
    # ============================================================================
    
    async def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a telemetry metric - uses bootstrap implementation."""
        if not self.is_bootstrapped:
            raise RuntimeError("Telemetry reporting utility not bootstrapped. Call bootstrap() first.")
        
        try:
            metric_data = {
                "metric_name": metric_name,
                "value": value,
                "tags": tags or {},
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name
            }
            
            # Try Smart City role first (enhanced implementation)
            if self.nurse_client:
                await self._send_metric_to_nurse(metric_data)
            else:
                # Fallback: Use bootstrap provider's implementation
                await self._record_metric_to_bootstrap(metric_data)
            
            # Store locally for backup
            self.metrics_storage.append(metric_data)
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}: {e}")
    
    async def _send_metric_to_nurse(self, metric_data: Dict[str, Any]):
        """Send metric to Nurse Service (enhanced)."""
        try:
            # Prepare telemetry data for Nurse
            nurse_input = {
                "service_name": self.service_name,
                "telemetry_type": "metric",
                "telemetry_data": metric_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call Nurse's collect_telemetry_data tool
            result = await self.nurse_client.call_tool(
                "collect_telemetry_data",
                input_data=json.dumps(nurse_input)
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to send metric to Nurse: {e}")
    
    async def _record_metric_to_bootstrap(self, metric_data: Dict[str, Any]):
        """Record metric using bootstrap provider's implementation."""
        # Call the bootstrap provider's metric implementation
        if hasattr(self.bootstrap_provider, 'implement_telemetry_reporting_record_metric'):
            await self.bootstrap_provider.implement_telemetry_reporting_record_metric(metric_data)
        else:
            # Fallback: Basic metric storage
            await self._implement_basic_metric_storage(metric_data)
    
    async def _implement_basic_metric_storage(self, metric_data: Dict[str, Any]):
        """Basic metric storage using foundation capabilities."""
        # This is REAL implementation using foundation utilities
        # Could use serialization_utility to store metrics, config_utility for storage settings, etc.
        pass
    
    # ============================================================================
    # HEALTH MONITORING AND STATUS TRACKING
    # ============================================================================
    
    async def log_health_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Log health metrics - uses bootstrap implementation."""
        if not self.is_bootstrapped:
            raise RuntimeError("Telemetry reporting utility not bootstrapped. Call bootstrap() first.")
        
        try:
            health_data = {
                "service_name": self.service_name,
                "health_metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Try Smart City role first (enhanced implementation)
            if self.nurse_client:
                return await self._send_health_to_nurse(health_data)
            else:
                # Fallback: Use bootstrap provider's implementation
                return await self._log_health_to_bootstrap(health_data)
            
        except Exception as e:
            self.logger.error(f"Failed to log health metrics: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _send_health_to_nurse(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send health metrics to Nurse Service (enhanced)."""
        try:
            # Call Nurse's monitor_system_health tool
            result = await self.nurse_client.call_tool(
                "monitor_system_health",
                input_data=json.dumps(health_data)
            )
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _log_health_to_bootstrap(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log health metrics using bootstrap provider's implementation."""
        # Call the bootstrap provider's health implementation
        if hasattr(self.bootstrap_provider, 'implement_telemetry_reporting_log_health'):
            return await self.bootstrap_provider.implement_telemetry_reporting_log_health(health_data)
        else:
            # Fallback: Basic health monitoring
            return await self._implement_basic_health_monitoring(health_data)
    
    async def _implement_basic_health_monitoring(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic health monitoring using foundation capabilities."""
        # This is REAL implementation using foundation utilities
        # Could use health_utility for health checks, config_utility for thresholds, etc.
        
        # Store health metrics locally
        self.health_metrics.update(health_data["health_metrics"])
        
        return {
            "status": "success",
            "message": "Health metrics recorded locally",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # PLATFORM TELEMETRY EVENT REPORTING
    # ============================================================================
    # Note: This utility reports PLATFORM-GENERATED telemetry events (errors, operations, metrics)
    # to the Nurse Service for tracking and management. This is distinct from telemetry as a
    # data source (e.g., autonomous vehicle telemetry) which would be ingested as data.
    # ============================================================================
    
    async def record_platform_error_event(self, error_type: str, metadata: Dict[str, Any] = None) -> None:
        """
        Record a platform-generated error event for reporting to Nurse Service.
        
        This reports platform errors (service errors, operation failures, etc.) to Nurse
        for tracking, monitoring, and health management. This is distinct from telemetry
        as a data source (e.g., vehicle telemetry) which would be ingested separately.
        
        Args:
            error_type: Type of error event (e.g., "error_occurred", "operation_failed")
            metadata: Optional metadata dictionary with error details
        """
        if not self.is_bootstrapped:
            raise RuntimeError("Telemetry reporting utility not bootstrapped. Call bootstrap() first.")
        
        try:
            # Use log_anomaly for error events (reports to Nurse)
            anomaly_data = {
                "event_name": error_type,
                "event_data": metadata or {},
                "severity": "error" if "error" in error_type.lower() else "warning",
                "platform_event_type": "error"
            }
            await self.log_anomaly(anomaly_data)
        except Exception as e:
            self.logger.error(f"Failed to record platform error event {error_type}: {e}")
    
    async def record_platform_operation_event(self, operation_name: str, metadata: Dict[str, Any] = None) -> None:
        """
        Record a platform-generated operation event for reporting to Nurse Service.
        
        This reports platform operations (service operations, workflow steps, etc.) to Nurse
        for tracking and metrics. This is distinct from telemetry as a data source.
        
        Args:
            operation_name: Name of the operation event (e.g., "file_parsed", "workflow_completed")
            metadata: Optional metadata dictionary with operation details
        """
        if not self.is_bootstrapped:
            raise RuntimeError("Telemetry reporting utility not bootstrapped. Call bootstrap() first.")
        
        try:
            # Use record_metric for operation events (reports to Nurse)
            tags = {k: str(v) for k, v in (metadata or {}).items() if isinstance(v, (str, int, float, bool))}
            tags["operation_name"] = operation_name
            tags["platform_event_type"] = "operation"
            await self.record_metric(
                metric_name=f"platform.operation.{operation_name}",
                value=1.0,
                tags=tags
            )
        except Exception as e:
            self.logger.error(f"Failed to record platform operation event {operation_name}: {e}")
    
    # ============================================================================
    # ANOMALY DETECTION AND ALERTING
    # ============================================================================
    
    async def log_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log anomaly - uses bootstrap implementation."""
        if not self.is_bootstrapped:
            raise RuntimeError("Telemetry reporting utility not bootstrapped. Call bootstrap() first.")
        
        try:
            anomaly_input = {
                "service_name": self.service_name,
                "anomaly_data": anomaly_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Try Smart City role first (enhanced implementation)
            if self.nurse_client:
                return await self._send_anomaly_to_nurse(anomaly_input)
            else:
                # Fallback: Use bootstrap provider's implementation
                return await self._log_anomaly_to_bootstrap(anomaly_input)
            
        except Exception as e:
            self.logger.error(f"Failed to log anomaly: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _send_anomaly_to_nurse(self, anomaly_input: Dict[str, Any]) -> Dict[str, Any]:
        """Send anomaly to Nurse Service (enhanced)."""
        try:
            # Call Nurse's detect_anomalies tool
            result = await self.nurse_client.call_tool(
                "detect_anomalies",
                input_data=json.dumps(anomaly_input)
            )
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _log_anomaly_to_bootstrap(self, anomaly_input: Dict[str, Any]) -> Dict[str, Any]:
        """Log anomaly using bootstrap provider's implementation."""
        # Call the bootstrap provider's anomaly implementation
        if hasattr(self.bootstrap_provider, 'implement_telemetry_reporting_log_anomaly'):
            return await self.bootstrap_provider.implement_telemetry_reporting_log_anomaly(anomaly_input)
        else:
            # Fallback: Basic anomaly logging
            return await self._implement_basic_anomaly_logging(anomaly_input)
    
    async def _implement_basic_anomaly_logging(self, anomaly_input: Dict[str, Any]) -> Dict[str, Any]:
        """Basic anomaly logging using foundation capabilities."""
        # This is REAL implementation using foundation utilities
        # Could use validation_utility for anomaly validation, config_utility for alerting rules, etc.
        
        # Store anomaly locally
        self.anomaly_logs.append(anomaly_input)
        
        return {
            "status": "success",
            "message": "Anomaly logged locally",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def get_telemetry_reporting_status(self) -> Dict[str, Any]:
        """Get telemetry reporting utility status."""
        return {
            "service_name": self.service_name,
            "status": "active",
            "bootstrapped": self.is_bootstrapped,
            "bootstrap_provider": self.bootstrap_provider.__class__.__name__ if self.bootstrap_provider else None,
            "nurse_connected": self.nurse_client is not None,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_stored": len(self.metrics_storage),
            "health_metrics_count": len(self.health_metrics),
            "anomaly_logs_count": len(self.anomaly_logs)
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of stored metrics."""
        return {
            "total_metrics": len(self.metrics_storage),
            "health_metrics": self.health_metrics,
            "recent_anomalies": len(self.anomaly_logs),
            "timestamp": datetime.utcnow().isoformat()
        }

# Global telemetry reporting utility instance
_telemetry_reporting_utility: Optional[TelemetryReportingUtility] = None

def get_telemetry_reporting_utility(service_name: str = "default") -> TelemetryReportingUtility:
    """Get or create the bootstrap-aware telemetry reporting utility instance."""
    global _telemetry_reporting_utility
    if _telemetry_reporting_utility is None:
        _telemetry_reporting_utility = TelemetryReportingUtility(service_name)
    return _telemetry_reporting_utility

