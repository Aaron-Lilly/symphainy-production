#!/usr/bin/env python3
"""
Performance Monitoring Mixin

Focused mixin for performance monitoring patterns - extracts telemetry and health
functionality from base classes into a reusable, testable component.

WHAT (Performance Monitoring Role): I provide telemetry and health monitoring patterns
HOW (Performance Monitoring Mixin): I centralize performance tracking and health reporting
"""

from typing import Dict, Any, Optional
import time
from datetime import datetime


class PerformanceMonitoringMixin:
    """
    Mixin for performance monitoring and health reporting patterns.
    
    Provides consistent telemetry collection, health monitoring, and performance
    tracking across all services with proper error handling.
    """
    
    def _init_performance_monitoring(self, di_container: Any):
        """Initialize performance monitoring patterns."""
        if not di_container:
            raise ValueError(
                "DI Container is required for PerformanceMonitoringMixin initialization. "
                "Services must be created with a valid DI Container instance."
            )
        
        self.di_container = di_container
        
        # Get logger from DI Container (should be available - DI Container initializes logging in __init__)
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError(
                f"DI Container does not have get_logger method. "
                f"This indicates a platform initialization failure or incorrect DI Container instance."
            )
        
        try:
            # Use DI Container's get_logger method to create logger for this mixin
            logger_service = di_container.get_logger(f"{self.__class__.__name__}.performance_monitoring")
            if not logger_service:
                raise RuntimeError(
                    f"DI Container.get_logger() returned None. "
                    f"Logging service should be available - this indicates a platform initialization failure."
                )
            # SmartCityLoggingService has .logger attribute and methods like .info(), .error(), etc.
            self.logger = logger_service
        except Exception as e:
            raise RuntimeError(
                f"Failed to get logger from DI Container: {e}. "
                f"DI Container must initialize logging utility before services can use it. "
                f"This indicates a platform initialization failure."
            ) from e
        
        # Performance tracking
        self.performance_metrics = {}
        self.start_time = datetime.utcnow()
        
        # Get utilities
        self.health = self.di_container.get_utility("health")
        self.telemetry = self.di_container.get_utility("telemetry")
        
        self.logger.debug("Performance monitoring mixin initialized")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            health_data = await self.health.run_all_health_checks()
            
            # Add service-specific health information
            health_data.update({
                "service_name": getattr(self, 'service_name', 'unknown'),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "is_initialized": getattr(self, 'is_initialized', False),
                "performance_metrics": self.performance_metrics.copy()
            })
            
            return health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "service_name": getattr(self, 'service_name', 'unknown'),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def track_performance(self, operation: str, duration: float, metadata: Optional[Dict[str, Any]] = None):
        """Track performance metrics for an operation."""
        try:
            if operation not in self.performance_metrics:
                self.performance_metrics[operation] = {
                    "count": 0,
                    "total_duration": 0.0,
                    "avg_duration": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0.0,
                    "last_execution": None
                }
            
            metrics = self.performance_metrics[operation]
            metrics["count"] += 1
            metrics["total_duration"] += duration
            metrics["avg_duration"] = metrics["total_duration"] / metrics["count"]
            metrics["min_duration"] = min(metrics["min_duration"], duration)
            metrics["max_duration"] = max(metrics["max_duration"], duration)
            metrics["last_execution"] = datetime.utcnow().isoformat()
            
            # Send telemetry (async)
            tags = {k: str(v) for k, v in (metadata or {}).items() if isinstance(v, (str, int, float, bool))}
            await self.telemetry.record_metric(
                f"operation.{operation}.duration",
                duration,
                tags
            )
            
        except Exception as e:
            self.logger.error(f"Failed to track performance for {operation}: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()
    
    def reset_performance_metrics(self):
        """Reset performance metrics."""
        self.performance_metrics.clear()
        self.logger.debug("Performance metrics reset")
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and metadata."""
        try:
            return {
                "service_name": getattr(self, 'service_name', 'unknown'),
                "service_type": self.__class__.__name__,
                "capabilities": getattr(self, 'capabilities', []),
                "dependencies": getattr(self, 'dependencies', []),
                "configuration": getattr(self, 'configuration', {}),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "performance_metrics": self.get_performance_metrics()
            }
        except Exception as e:
            self.logger.error(f"Failed to get service capabilities: {e}")
            return {"error": str(e)}
    
    async def record_platform_error_event(self, error_type: str, metadata: Dict[str, Any] = None):
        """
        Record a platform-generated error event for reporting to Nurse Service.
        
        This reports platform errors (service errors, operation failures, etc.) to Nurse
        for tracking, monitoring, and health management. This is distinct from telemetry
        as a data source (e.g., vehicle telemetry) which would be ingested separately.
        
        Args:
            error_type: Type of error event (e.g., "error_occurred", "operation_failed")
            metadata: Optional metadata dictionary with error details
        """
        try:
            await self.telemetry.record_platform_error_event(error_type, metadata)
        except Exception as e:
            self.logger.error(f"Failed to record platform error event {error_type}: {e}")
    
    async def record_platform_operation_event(self, operation_name: str, metadata: Dict[str, Any] = None):
        """
        Record a platform-generated operation event for reporting to Nurse Service.
        
        This reports platform operations (service operations, workflow steps, etc.) to Nurse
        for tracking and metrics. This is distinct from telemetry as a data source.
        
        Args:
            operation_name: Name of the operation event (e.g., "file_parsed", "workflow_completed")
            metadata: Optional metadata dictionary with operation details
        """
        try:
            await self.telemetry.record_platform_operation_event(operation_name, metadata)
        except Exception as e:
            self.logger.error(f"Failed to record platform operation event {operation_name}: {e}")
    
    async def record_telemetry_event(self, event_name: str, data: Dict[str, Any]):
        """
        DEPRECATED: Use record_platform_error_event() or record_platform_operation_event() instead.
        
        This method is kept for backward compatibility but delegates to platform-specific methods.
        """
        try:
            # Check if this is an error event
            if "error" in event_name.lower():
                await self.record_platform_error_event(event_name, data)
            else:
                await self.record_platform_operation_event(event_name, data)
        except Exception as e:
            self.logger.error(f"Failed to record telemetry event {event_name}: {e}")
    
    async def record_telemetry_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record telemetry metric."""
        try:
            # Convert metadata dict to tags dict (TelemetryReportingUtility expects tags, not metadata)
            tags = {k: str(v) for k, v in (metadata or {}).items() if isinstance(v, (str, int, float, bool))}
            await self.telemetry.record_metric(metric_name, value, tags)
        except Exception as e:
            self.logger.error(f"Failed to record telemetry metric {metric_name}: {e}")
    
    async def handle_error_with_audit(self, error: Exception, operation: str, details: Optional[Dict[str, Any]] = None):
        """Handle error with audit logging."""
        try:
            self.logger.error(f"❌ Error in {operation}: {error}")
            error_data = {
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
            if details:
                error_data.update(details)
            await self.record_platform_error_event("error_occurred", error_data)
        except Exception as audit_error:
            self.logger.error(f"Failed to audit error: {audit_error}")
    
    async def log_operation_with_telemetry(self, operation: str, success: bool = True, details: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log operation with telemetry."""
        try:
            if success:
                self.logger.info(f"✅ {operation} completed successfully")
            else:
                self.logger.warning(f"⚠️ {operation} completed with issues")
            
            # Support both 'details' and 'metadata' for backward compatibility
            operation_data = details or metadata or {}
            
            await self.record_platform_operation_event(f"operation_{operation}", {
                "success": success,
                "details": operation_data
            })
        except Exception as e:
            self.logger.error(f"Failed to log operation {operation}: {e}")
    
    async def record_health_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record health metric."""
        try:
            await self.record_telemetry_metric(f"health.{metric_name}", value, metadata)
        except Exception as e:
            self.logger.error(f"Failed to record health metric {metric_name}: {e}")
