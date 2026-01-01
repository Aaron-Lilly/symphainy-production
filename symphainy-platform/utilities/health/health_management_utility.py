"""
Health Management Utility

Platform-specific health management utility for Smart City services.
Refactored from HealthService to be a self-contained utility.

WHAT (Utility Role): I provide standardized health monitoring and reporting for platform operations
HOW (Utility Implementation): I monitor service health, collect metrics, and provide health reports
"""

import asyncio
import psutil
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class ServiceStatus(Enum):
    """Service status enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"


@dataclass
class HealthMetrics:
    """Service health metrics."""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    timestamp: datetime
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class HealthReport:
    """Comprehensive health report."""
    service_name: str
    overall_status: HealthStatus
    service_status: ServiceStatus
    timestamp: datetime
    uptime_seconds: float
    health_checks: List[HealthCheck]
    metrics: HealthMetrics
    issues: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.recommendations is None:
            self.recommendations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HealthManagementUtility:
    """
    Platform-specific health management utility for Smart City services.
    
    Refactored from HealthService to be a self-contained utility.
    Provides health monitoring patterns used across the platform including:
    - Service health monitoring
    - Performance metrics collection
    - Health check execution
    - Health report generation
    - Status management
    """
    
    def __init__(self, service_name: str):
        """Initialize health management utility."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"HealthManagementUtility-{service_name}")
        
        # Service state
        self._status = ServiceStatus.INITIALIZING
        self._start_time = datetime.utcnow()
        self._metrics = HealthMetrics(start_time=self._start_time)
        
        # Request tracking
        self._request_times = []
        self._max_request_history = 100
        
        # Health checks registry
        self._health_checks: Dict[str, Callable] = {}
        self._custom_health_checks: Dict[str, Callable] = {}
        
        # Initialize default health checks
        self._initialize_default_health_checks()
        
        self.logger.info(f"Health management utility initialized for {service_name}")
    
    # ============================================================================
    # STATUS MANAGEMENT
    # ============================================================================
    
    def set_status(self, status: ServiceStatus):
        """Set service status."""
        old_status = self._status
        self._status = status
        self.logger.info(f"Service status changed from {old_status.value} to {status.value}")
    
    def get_status(self) -> ServiceStatus:
        """Get current service status."""
        return self._status
    
    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return self._status in [ServiceStatus.RUNNING, ServiceStatus.MAINTENANCE]
    
    def is_running(self) -> bool:
        """Check if service is running."""
        return self._status == ServiceStatus.RUNNING
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return (datetime.utcnow() - self._start_time).total_seconds()
    
    # ============================================================================
    # METRICS COLLECTION
    # ============================================================================
    
    def record_request(self, success: bool, response_time_ms: float = 0.0):
        """Record a request for metrics."""
        self._metrics.total_requests += 1
        self._metrics.operation_count += 1
        
        if success:
            self._metrics.successful_requests += 1
        else:
            self._metrics.failed_requests += 1
        
        self._metrics.last_request_time = datetime.utcnow()
        
        if response_time_ms > 0:
            self._request_times.append(response_time_ms)
            if len(self._request_times) > self._max_request_history:
                self._request_times.pop(0)
            
            self._metrics.average_response_time = sum(self._request_times) / len(self._request_times)
        
        # Update system metrics
        self._update_system_metrics()
    
    def record_operation(self, operation_name: str, success: bool, duration_ms: float = 0.0):
        """Record a specific operation."""
        self.record_request(success, duration_ms)
        self.logger.debug(f"Recorded operation '{operation_name}': success={success}, duration={duration_ms}ms")
    
    def _update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # Memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            self._metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # CPU usage
            self._metrics.cpu_usage_percent = process.cpu_percent()
            
            # Uptime
            self._metrics.uptime_seconds = self.get_uptime()
            
        except Exception as e:
            self.logger.warning(f"Failed to update system metrics: {e}")
    
    def get_metrics(self) -> HealthMetrics:
        """Get current health metrics."""
        self._update_system_metrics()
        return self._metrics
    
    # ============================================================================
    # HEALTH CHECKS
    # ============================================================================
    
    def _initialize_default_health_checks(self):
        """Initialize default health checks."""
        self._health_checks.update({
            "service_status": self._check_service_status,
            "memory_usage": self._check_memory_usage,
            "cpu_usage": self._check_cpu_usage,
            "request_success_rate": self._check_request_success_rate,
            "response_time": self._check_response_time
        })
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register a custom health check."""
        self._custom_health_checks[name] = check_func
        self.logger.info(f"Registered custom health check: {name}")
    
    def unregister_health_check(self, name: str):
        """Unregister a custom health check."""
        if name in self._custom_health_checks:
            del self._custom_health_checks[name]
            self.logger.info(f"Unregistered custom health check: {name}")
    
    async def run_health_check(self, name: str) -> HealthCheck:
        """Run a specific health check."""
        start_time = datetime.utcnow()
        
        try:
            # Check if it's a custom health check
            if name in self._custom_health_checks:
                check_func = self._custom_health_checks[name]
            elif name in self._health_checks:
                check_func = self._health_checks[name]
            else:
                return HealthCheck(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check '{name}' not found",
                    response_time_ms=0.0,
                    timestamp=start_time
                )
            
            # Run the health check
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                name=name,
                status=result.get("status", HealthStatus.UNKNOWN),
                message=result.get("message", "Health check completed"),
                response_time_ms=response_time,
                timestamp=start_time,
                details=result.get("details", {})
            )
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.logger.error(f"Health check '{name}' failed: {e}")
            
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                response_time_ms=response_time,
                timestamp=start_time
            )
    
    async def run_all_health_checks(self) -> List[HealthCheck]:
        """Run all registered health checks."""
        all_checks = {**self._health_checks, **self._custom_health_checks}
        results = []
        
        for name in all_checks.keys():
            result = await self.run_health_check(name)
            results.append(result)
        
        return results
    
    # ============================================================================
    # DEFAULT HEALTH CHECKS
    # ============================================================================
    
    def _check_service_status(self) -> Dict[str, Any]:
        """Check service status."""
        if self._status == ServiceStatus.RUNNING:
            return {"status": HealthStatus.HEALTHY, "message": "Service is running"}
        elif self._status == ServiceStatus.INITIALIZING:
            return {"status": HealthStatus.DEGRADED, "message": "Service is initializing"}
        elif self._status == ServiceStatus.MAINTENANCE:
            return {"status": HealthStatus.MAINTENANCE, "message": "Service is in maintenance mode"}
        else:
            return {"status": HealthStatus.UNHEALTHY, "message": f"Service status: {self._status.value}"}
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage."""
        memory_mb = self._metrics.memory_usage_mb
        
        if memory_mb < 100:  # Less than 100MB
            status = HealthStatus.HEALTHY
            message = f"Memory usage: {memory_mb:.1f}MB"
        elif memory_mb < 500:  # Less than 500MB
            status = HealthStatus.DEGRADED
            message = f"Memory usage: {memory_mb:.1f}MB (elevated)"
        else:  # More than 500MB
            status = HealthStatus.UNHEALTHY
            message = f"Memory usage: {memory_mb:.1f}MB (high)"
        
        return {
            "status": status,
            "message": message,
            "details": {"memory_mb": memory_mb}
        }
    
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage."""
        cpu_percent = self._metrics.cpu_usage_percent
        
        if cpu_percent < 50:  # Less than 50%
            status = HealthStatus.HEALTHY
            message = f"CPU usage: {cpu_percent:.1f}%"
        elif cpu_percent < 80:  # Less than 80%
            status = HealthStatus.DEGRADED
            message = f"CPU usage: {cpu_percent:.1f}% (elevated)"
        else:  # More than 80%
            status = HealthStatus.UNHEALTHY
            message = f"CPU usage: {cpu_percent:.1f}% (high)"
        
        return {
            "status": status,
            "message": message,
            "details": {"cpu_percent": cpu_percent}
        }
    
    def _check_request_success_rate(self) -> Dict[str, Any]:
        """Check request success rate."""
        total = self._metrics.total_requests
        if total == 0:
            return {"status": HealthStatus.UNKNOWN, "message": "No requests recorded"}
        
        success_rate = (self._metrics.successful_requests / total) * 100
        
        if success_rate >= 95:  # 95% or higher
            status = HealthStatus.HEALTHY
            message = f"Success rate: {success_rate:.1f}%"
        elif success_rate >= 90:  # 90% or higher
            status = HealthStatus.DEGRADED
            message = f"Success rate: {success_rate:.1f}% (degraded)"
        else:  # Less than 90%
            status = HealthStatus.UNHEALTHY
            message = f"Success rate: {success_rate:.1f}% (poor)"
        
        return {
            "status": status,
            "message": message,
            "details": {
                "success_rate": success_rate,
                "total_requests": total,
                "successful_requests": self._metrics.successful_requests,
                "failed_requests": self._metrics.failed_requests
            }
        }
    
    def _check_response_time(self) -> Dict[str, Any]:
        """Check average response time."""
        avg_time = self._metrics.average_response_time
        
        if avg_time == 0:
            return {"status": HealthStatus.UNKNOWN, "message": "No response time data"}
        
        if avg_time < 100:  # Less than 100ms
            status = HealthStatus.HEALTHY
            message = f"Avg response time: {avg_time:.1f}ms"
        elif avg_time < 500:  # Less than 500ms
            status = HealthStatus.DEGRADED
            message = f"Avg response time: {avg_time:.1f}ms (slow)"
        else:  # More than 500ms
            status = HealthStatus.UNHEALTHY
            message = f"Avg response time: {avg_time:.1f}ms (very slow)"
        
        return {
            "status": status,
            "message": message,
            "details": {"average_response_time_ms": avg_time}
        }
    
    # ============================================================================
    # HEALTH REPORTS
    # ============================================================================
    
    async def generate_health_report(self) -> HealthReport:
        """Generate comprehensive health report."""
        # Run all health checks
        health_checks = await self.run_all_health_checks()
        
        # Determine overall status
        overall_status = self._determine_overall_status(health_checks)
        
        # Collect issues and recommendations
        issues, recommendations = self._analyze_health_checks(health_checks)
        
        # Update metrics
        self._update_system_metrics()
        
        return HealthReport(
            service_name=self.service_name,
            overall_status=overall_status,
            service_status=self._status,
            timestamp=datetime.utcnow(),
            uptime_seconds=self.get_uptime(),
            health_checks=health_checks,
            metrics=self._metrics,
            issues=issues,
            recommendations=recommendations
        )
    
    def _determine_overall_status(self, health_checks: List[HealthCheck]) -> HealthStatus:
        """Determine overall health status from individual checks."""
        if not health_checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in health_checks]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif HealthStatus.MAINTENANCE in statuses:
            return HealthStatus.MAINTENANCE
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def _analyze_health_checks(self, health_checks: List[HealthCheck]) -> tuple[List[str], List[str]]:
        """Analyze health checks for issues and recommendations."""
        issues = []
        recommendations = []
        
        for check in health_checks:
            if check.status == HealthStatus.UNHEALTHY:
                issues.append(f"{check.name}: {check.message}")
            elif check.status == HealthStatus.DEGRADED:
                issues.append(f"{check.name}: {check.message}")
            
            # Add recommendations based on check results
            if check.name == "memory_usage" and check.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]:
                recommendations.append("Consider optimizing memory usage or increasing available memory")
            elif check.name == "cpu_usage" and check.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]:
                recommendations.append("Consider optimizing CPU usage or scaling resources")
            elif check.name == "response_time" and check.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]:
                recommendations.append("Consider optimizing response time or scaling resources")
        
        return issues, recommendations
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health utility status summary."""
        return {
            "service_name": self.service_name,
            "utility_type": "health_management",
            "status": "operational",
            "service_status": self._status.value,
            "uptime_seconds": self.get_uptime(),
            "total_requests": self._metrics.total_requests,
            "health_checks_registered": len(self._health_checks) + len(self._custom_health_checks),
            "timestamp": datetime.utcnow().isoformat()
        }

