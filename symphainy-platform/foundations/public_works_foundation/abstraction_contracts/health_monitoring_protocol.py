#!/usr/bin/env python3
"""
Health Monitoring Protocol

Abstraction contract for health monitoring and system diagnostics.
Defines interfaces for health monitoring operations.
"""

from typing import Protocol
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Metric type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"


@dataclass
class HealthMetric:
    """Health metric data."""
    name: str
    value: float
    unit: str
    status: HealthStatus
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class HealthCheck:
    """Health check result."""
    service_name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: List[HealthMetric] = None


class HealthMonitoringProtocol(Protocol):
    """Protocol for health monitoring operations."""
    
    async def get_system_health(self) -> HealthCheck:
        """
        Get overall system health.
        
        Returns:
            HealthCheck: System health status
        """
        ...
    
    async def get_service_health(self, service_name: str) -> HealthCheck:
        """
        Get health for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            HealthCheck: Service health status
        """
        ...
    
    async def get_health_metrics(self, metric_type: MetricType) -> List[HealthMetric]:
        """
        Get health metrics by type.
        
        Args:
            metric_type: Type of metrics to retrieve
            
        Returns:
            List[HealthMetric]: Health metrics
        """
        ...
    
    async def set_health_threshold(self, metric_name: str, threshold: float) -> bool:
        """
        Set health threshold for a metric.
        
        Args:
            metric_name: Name of the metric
            threshold: Threshold value
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_health_history(self, service_name: str, hours: int = 24) -> List[HealthCheck]:
        """
        Get health history for a service.
        
        Args:
            service_name: Name of the service
            hours: Number of hours to retrieve
            
        Returns:
            List[HealthCheck]: Health history
        """
        ...
    
    async def start_health_monitoring(self, service_name: str, interval: int = 30) -> bool:
        """
        Start health monitoring for a service.
        
        Args:
            service_name: Name of the service
            interval: Monitoring interval in seconds
            
        Returns:
            bool: Success status
        """
        ...
    
    async def stop_health_monitoring(self, service_name: str) -> bool:
        """
        Stop health monitoring for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            bool: Success status
        """
        ...



