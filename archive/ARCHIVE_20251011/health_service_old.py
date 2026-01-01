"""
Health Check Service for MCP Servers

This service provides comprehensive health monitoring capabilities for all
MCP servers in the SymphAIny platform, based on proven patterns from symphainy-mvp.
"""

import asyncio
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

@dataclass
class ServiceMetrics:
    """Service performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    start_time: Optional[datetime] = None
    operation_count: int = 0

class ServiceStatus(Enum):
    """Service status enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"

class HealthService:
    """Health monitoring service for MCP servers."""

    def __init__(self, service_name: str):
        """Initialize the health service."""
        self.service_name = service_name
        self._status = ServiceStatus.INITIALIZING
        self._start_time = datetime.utcnow()
        self._metrics = ServiceMetrics()
        self._request_times = []
        self._max_request_history = 100
        self._health_checks = {}

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            start_time = datetime.utcnow()

            # Perform service-specific health check
            service_health = await self._health_check_service()

            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_request_time(response_time)

            # Collect system metrics
            system_metrics = await self._collect_system_metrics()

            health_data = {
                "service": self.service_name,
                "status": self._status.value,
                "uptime_seconds": self._metrics.uptime_seconds,
                "response_time": response_time,
                "metrics": {
                    "total_requests": self._metrics.total_requests,
                    "successful_requests": self._metrics.successful_requests,
                    "failed_requests": self._metrics.failed_requests,
                    "average_response_time": self._metrics.average_response_time,
                    "memory_usage_mb": system_metrics["memory_usage_mb"],
                    "cpu_usage_percent": system_metrics["cpu_usage_percent"]
                },
                "service_health": service_health,
                "timestamp": datetime.utcnow().isoformat()
            }

            self._metrics.total_requests += 1
            self._metrics.successful_requests += 1
            self._metrics.last_request_time = datetime.utcnow()

            return health_data

        except Exception as e:
            self._metrics.total_requests += 1
            self._metrics.failed_requests += 1
            self._metrics.last_request_time = datetime.utcnow()

            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _health_check_service(self) -> Dict[str, Any]:
        """Service-specific health check. Override in subclasses."""
        return {"status": "healthy"}

    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage_mb = memory.used / (1024 * 1024)

            # Get CPU usage
            cpu_usage_percent = psutil.cpu_percent(interval=1)

            return {
                "memory_usage_mb": memory_usage_mb,
                "cpu_usage_percent": cpu_usage_percent
            }
        except Exception:
            return {
                "memory_usage_mb": 0.0,
                "cpu_usage_percent": 0.0
            }

    def _record_request_time(self, response_time: float):
        """Record request response time for metrics."""
        self._request_times.append(response_time)

        # Keep only the last N request times
        if len(self._request_times) > self._max_request_history:
            self._request_times = self._request_times[-self._max_request_history:]

        # Update average response time
        if self._request_times:
            self._metrics.average_response_time = sum(self._request_times) / len(self._request_times)
    
    async def record_health_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a health metric."""
        try:
            # For now, we'll just log the metric
            # In a real implementation, this would be sent to a metrics system
            self.logger.info(f"Health metric recorded: {metric_name}={value}, tags={tags}")
            
            # Update internal metrics if it's a response time metric
            if metric_name == "response_time":
                self._record_request_time(value)
                
        except Exception as e:
            self.logger.error(f"Failed to record health metric {metric_name}: {e}")

    def set_status(self, status: ServiceStatus):
        """Set service status."""
        self._status = status

    def get_status(self) -> ServiceStatus:
        """Get current service status."""
        return self._status

    def get_metrics(self) -> ServiceMetrics:
        """Get current service metrics."""
        # Update uptime
        self._metrics.uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
        return self._metrics

    def get_uptime(self) -> timedelta:
        """Get service uptime."""
        return datetime.utcnow() - self._start_time

    def register_health_check(self, name: str, check_func):
        """Register a custom health check."""
        self._health_checks[name] = check_func

    async def run_custom_health_checks(self) -> Dict[str, Any]:
        """Run all registered custom health checks."""
        results = {}
        for name, check_func in self._health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    results[name] = await check_func()
                else:
                    results[name] = check_func()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        return results

    async def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health information including custom checks."""
        basic_health = await self.health_check()
        custom_checks = await self.run_custom_health_checks()
        
        return {
            **basic_health,
            "custom_health_checks": custom_checks
        }

# Global health service factory
def get_health_service(service_name: str, config=None) -> HealthService:
    """Get a health service instance."""
    return HealthService(service_name)







