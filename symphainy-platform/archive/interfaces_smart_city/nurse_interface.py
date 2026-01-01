#!/usr/bin/env python3
"""
Nurse Interface

Defines the contracts for Nurse service operations.
This interface matches the existing NurseService APIs.

WHAT (Interface Role): I define the contracts for health monitoring and telemetry
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Metric type levels."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


# Request Models
class CollectTelemetryRequest(BaseModel):
    """Request to collect telemetry data."""
    service_name: str = Field(..., description="Name of the service")
    metric_name: str = Field(..., description="Name of the metric")
    metric_value: float = Field(..., description="Value of the metric")
    metric_type: Optional[MetricType] = Field(MetricType.GAUGE, description="Type of the metric")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Metric tags")
    timestamp: Optional[str] = Field(None, description="Metric timestamp (ISO format)")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant telemetry")


class GetHealthMetricsRequest(BaseModel):
    """Request to get health metrics."""
    service_name: Optional[str] = Field(None, description="Specific service name (all if None)")
    metric_names: Optional[List[str]] = Field(None, description="Specific metric names (all if None)")
    time_range_minutes: Optional[int] = Field(60, description="Time range in minutes")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class SetAlertThresholdRequest(BaseModel):
    """Request to set alert thresholds."""
    service_name: str = Field(..., description="Name of the service")
    metric_name: str = Field(..., description="Name of the metric")
    warning_threshold: Optional[float] = Field(None, description="Warning threshold value")
    critical_threshold: Optional[float] = Field(None, description="Critical threshold value")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant alerts")


class RunDiagnosticsRequest(BaseModel):
    """Request to run system diagnostics."""
    diagnostic_type: str = Field(..., description="Type of diagnostic to run")
    target_services: Optional[List[str]] = Field(None, description="Specific services to diagnose (all if None)")
    include_details: Optional[bool] = Field(True, description="Include detailed diagnostic information")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant diagnostics")


class GetSystemStatusRequest(BaseModel):
    """Request to get overall system status."""
    include_services: Optional[bool] = Field(True, description="Include individual service status")
    include_metrics: Optional[bool] = Field(True, description="Include system metrics")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


# Response Models
class CollectTelemetryResponse(BaseModel):
    """Response for telemetry collection."""
    success: bool = Field(..., description="Telemetry collection success status")
    metric_id: Optional[str] = Field(None, description="Collected metric ID")
    service_name: Optional[str] = Field(None, description="Service name")
    metric_name: Optional[str] = Field(None, description="Metric name")
    collected_at: Optional[str] = Field(None, description="Collection timestamp")
    message: str = Field(..., description="Response message")


class GetHealthMetricsResponse(BaseModel):
    """Response for health metrics."""
    success: bool = Field(..., description="Metrics retrieval success status")
    service_name: Optional[str] = Field(None, description="Service name")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Health metrics data")
    time_range: Optional[Dict[str, str]] = Field(None, description="Time range for metrics")
    retrieved_at: Optional[str] = Field(None, description="Retrieval timestamp")
    message: str = Field(..., description="Response message")


class SetAlertThresholdResponse(BaseModel):
    """Response for alert threshold setting."""
    success: bool = Field(..., description="Threshold setting success status")
    service_name: Optional[str] = Field(None, description="Service name")
    metric_name: Optional[str] = Field(None, description="Metric name")
    warning_threshold: Optional[float] = Field(None, description="Set warning threshold")
    critical_threshold: Optional[float] = Field(None, description="Set critical threshold")
    set_at: Optional[str] = Field(None, description="Setting timestamp")
    message: str = Field(..., description="Response message")


class RunDiagnosticsResponse(BaseModel):
    """Response for system diagnostics."""
    success: bool = Field(..., description="Diagnostics execution success status")
    diagnostic_id: Optional[str] = Field(None, description="Diagnostic execution ID")
    diagnostic_type: Optional[str] = Field(None, description="Type of diagnostic run")
    results: Optional[Dict[str, Any]] = Field(None, description="Diagnostic results")
    services_checked: Optional[List[str]] = Field(None, description="Services that were checked")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    message: str = Field(..., description="Response message")


class GetSystemStatusResponse(BaseModel):
    """Response for system status."""
    success: bool = Field(..., description="Status retrieval success status")
    overall_status: Optional[HealthStatus] = Field(None, description="Overall system health status")
    system_metrics: Optional[Dict[str, Any]] = Field(None, description="System metrics")
    service_statuses: Optional[Dict[str, HealthStatus]] = Field(None, description="Individual service statuses")
    alerts: Optional[List[Dict[str, Any]]] = Field(None, description="Active alerts")
    checked_at: Optional[str] = Field(None, description="Status check timestamp")
    message: str = Field(..., description="Response message")


# Interface Definition
class INurse:
    """
    Nurse Interface

    Defines the contracts for Nurse service operations.
    This interface matches the existing NurseService APIs.
    """

    # Telemetry Collection
    async def collect_telemetry(self, request: CollectTelemetryRequest) -> CollectTelemetryResponse:
        """Collect telemetry data from services."""
        pass

    # Health Monitoring
    async def get_health_metrics(self, request: GetHealthMetricsRequest) -> GetHealthMetricsResponse:
        """Get health metrics for services."""
        pass

    # Alert Management
    async def set_alert_threshold(self, request: SetAlertThresholdRequest) -> SetAlertThresholdResponse:
        """Set alert thresholds for monitoring."""
        pass

    # System Diagnostics
    async def run_diagnostics(self, request: RunDiagnosticsRequest) -> RunDiagnosticsResponse:
        """Run system diagnostics."""
        pass

    # System Status
    async def get_system_status(self, request: GetSystemStatusRequest) -> GetSystemStatusResponse:
        """Get overall system status."""
        pass























