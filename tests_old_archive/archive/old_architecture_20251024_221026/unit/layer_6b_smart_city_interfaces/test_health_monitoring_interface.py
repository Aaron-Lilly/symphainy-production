#!/usr/bin/env python3
"""
Tests for Health Monitoring Interface.

Tests the health monitoring interface data models and concrete implementations
for Smart City health monitoring operations.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.interfaces.health_monitoring_interface import (
    HealthStatus,
    MetricType,
    AlertSeverity,
    HealthCheck,
    MetricData,
    AlertRule,
    Alert,
    TelemetryData,
    IHealthMonitoring
)
from tests.unit.layer_5b_smart_city_interfaces.test_base import SmartCityInterfacesTestBase


class TestHealthStatus:
    """Test HealthStatus enum."""
    
    def test_health_status_values(self):
        """Test health status enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"
        assert HealthStatus.DOWN.value == "down"


class TestMetricType:
    """Test MetricType enum."""
    
    def test_metric_type_values(self):
        """Test metric type enum values."""
        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"


class TestAlertSeverity:
    """Test AlertSeverity enum."""
    
    def test_alert_severity_values(self):
        """Test alert severity enum values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestHealthCheck:
    """Test HealthCheck data model."""
    
    def test_health_check_creation(self):
        """Test creating a health check."""
        health_check = HealthCheck(
            service_name="test_service",
            status=HealthStatus.HEALTHY,
            message="Service is running normally",
            timestamp=datetime(2024, 1, 1, 0, 0, 0),
            response_time_ms=150.5,
            details={"endpoint": "/api/health", "status_code": 200}
        )
        
        assert health_check.service_name == "test_service"
        assert health_check.status == HealthStatus.HEALTHY
        assert health_check.message == "Service is running normally"
        assert health_check.timestamp == datetime(2024, 1, 1, 0, 0, 0)
        assert health_check.response_time_ms == 150.5
        assert health_check.details["endpoint"] == "/api/health"
        assert health_check.details["status_code"] == 200
    
    def test_health_check_defaults(self):
        """Test health check with default values."""
        health_check = HealthCheck(
            service_name="minimal_service",
            status=HealthStatus.UNKNOWN,
            message="",
            timestamp=datetime(2024, 1, 1, 0, 0, 0),
            response_time_ms=0.0
        )
        
        assert health_check.service_name == "minimal_service"
        assert health_check.status == HealthStatus.UNKNOWN
        assert health_check.message == ""
        assert health_check.details == {}


class TestMetricData:
    """Test MetricData data model."""
    
    def test_metric_data_creation(self):
        """Test creating metric data."""
        metric_data = MetricData(
            name="cpu_usage",
            value=75.5,
            metric_type=MetricType.GAUGE,
            timestamp=datetime(2024, 1, 1, 0, 0, 0),
            tags={"service": "test_service", "instance": "instance_001"},
            labels={"environment": "production", "region": "us-east-1"}
        )
        
        assert metric_data.name == "cpu_usage"
        assert metric_data.value == 75.5
        assert metric_data.metric_type == MetricType.GAUGE
        assert metric_data.timestamp == datetime(2024, 1, 1, 0, 0, 0)
        assert metric_data.tags["service"] == "test_service"
        assert metric_data.tags["instance"] == "instance_001"
        assert metric_data.labels["environment"] == "production"
        assert metric_data.labels["region"] == "us-east-1"
    
    def test_metric_data_defaults(self):
        """Test metric data with default values."""
        metric_data = MetricData(
            name="memory_usage",
            value=1024.0,
            metric_type=MetricType.GAUGE,
            timestamp=datetime(2024, 1, 1, 0, 0, 0)
        )
        
        assert metric_data.name == "memory_usage"
        assert metric_data.value == 1024.0
        assert metric_data.metric_type == MetricType.GAUGE
        assert metric_data.tags == {}
        assert metric_data.labels == {}


class TestAlertRule:
    """Test AlertRule data model."""
    
    def test_alert_rule_creation(self):
        """Test creating an alert rule."""
        alert_rule = AlertRule(
            rule_id="rule_001",
            name="High CPU Usage",
            metric_name="cpu_usage",
            condition="value > 80",
            severity=AlertSeverity.WARNING,
            enabled=True,
            cooldown_minutes=10,
            description="Alert when CPU usage exceeds 80%"
        )
        
        assert alert_rule.rule_id == "rule_001"
        assert alert_rule.name == "High CPU Usage"
        assert alert_rule.metric_name == "cpu_usage"
        assert alert_rule.condition == "value > 80"
        assert alert_rule.severity == AlertSeverity.WARNING
        assert alert_rule.enabled is True
        assert alert_rule.cooldown_minutes == 10
        assert alert_rule.description == "Alert when CPU usage exceeds 80%"
    
    def test_alert_rule_defaults(self):
        """Test alert rule with default values."""
        alert_rule = AlertRule(
            rule_id="rule_002",
            name="Basic Rule",
            metric_name="memory_usage",
            condition="value > 90",
            severity=AlertSeverity.ERROR
        )
        
        assert alert_rule.rule_id == "rule_002"
        assert alert_rule.name == "Basic Rule"
        assert alert_rule.metric_name == "memory_usage"
        assert alert_rule.condition == "value > 90"
        assert alert_rule.severity == AlertSeverity.ERROR
        assert alert_rule.enabled is True
        assert alert_rule.cooldown_minutes == 5
        assert alert_rule.description == "Alert when memory_usage value > 90"


class TestAlert:
    """Test Alert data model."""
    
    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            alert_id="alert_001",
            rule_id="rule_001",
            service_name="test_service",
            severity=AlertSeverity.WARNING,
            message="CPU usage is 85%",
            triggered_at=datetime(2024, 1, 1, 0, 0, 0),
            metadata={"instance": "instance_001", "value": 85.0}
        )
        
        assert alert.alert_id == "alert_001"
        assert alert.rule_id == "rule_001"
        assert alert.service_name == "test_service"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "CPU usage is 85%"
        assert alert.triggered_at == datetime(2024, 1, 1, 0, 0, 0)
        assert alert.resolved_at is None
        assert alert.is_active is True
        assert alert.metadata["instance"] == "instance_001"
        assert alert.metadata["value"] == 85.0
    
    def test_alert_defaults(self):
        """Test alert with default values."""
        alert = Alert(
            alert_id="alert_002",
            rule_id="rule_002",
            service_name="minimal_service",
            severity=AlertSeverity.ERROR,
            message="Basic alert message",
            triggered_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        
        assert alert.alert_id == "alert_002"
        assert alert.rule_id == "rule_002"
        assert alert.service_name == "minimal_service"
        assert alert.severity == AlertSeverity.ERROR
        assert alert.message == "Basic alert message"
        assert alert.resolved_at is None
        assert alert.is_active is True
        assert alert.metadata == {}


class TestTelemetryData:
    """Test TelemetryData data model."""
    
    def test_telemetry_data_creation(self):
        """Test creating telemetry data."""
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = start_time + timedelta(milliseconds=150)
        
        telemetry_data = TelemetryData(
            trace_id="trace_001",
            span_id="span_001",
            operation_name="api_call",
            service_name="test_service",
            start_time=start_time,
            end_time=end_time,
            duration_ms=150.0,
            status="success",
            tags={"endpoint": "/api/test", "method": "GET"},
            logs=[{"level": "info", "message": "Request processed"}]
        )
        
        assert telemetry_data.trace_id == "trace_001"
        assert telemetry_data.span_id == "span_001"
        assert telemetry_data.operation_name == "api_call"
        assert telemetry_data.service_name == "test_service"
        assert telemetry_data.start_time == start_time
        assert telemetry_data.end_time == end_time
        assert telemetry_data.duration_ms == 150.0
        assert telemetry_data.status == "success"
        assert telemetry_data.tags["endpoint"] == "/api/test"
        assert telemetry_data.tags["method"] == "GET"
        assert len(telemetry_data.logs) == 1
        assert telemetry_data.logs[0]["level"] == "info"
    
    def test_telemetry_data_defaults(self):
        """Test telemetry data with default values."""
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = start_time + timedelta(milliseconds=100)
        
        telemetry_data = TelemetryData(
            trace_id="trace_002",
            span_id="span_002",
            operation_name="minimal_operation",
            service_name="minimal_service",
            start_time=start_time,
            end_time=end_time,
            duration_ms=100.0,
            status="success"
        )
        
        assert telemetry_data.trace_id == "trace_002"
        assert telemetry_data.span_id == "span_002"
        assert telemetry_data.operation_name == "minimal_operation"
        assert telemetry_data.service_name == "minimal_service"
        assert telemetry_data.tags == {}
        assert telemetry_data.logs == []


class TestHealthMonitoringInterface(SmartCityInterfacesTestBase):
    """Test IHealthMonitoring implementation."""
    
    @pytest.mark.asyncio
    async def test_health_monitoring_interface_initialization(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test health monitoring interface initialization."""
        # Create a concrete implementation for testing
        class TestHealthMonitoringInterface(IHealthMonitoring):
            def __init__(self):
                self.health_checks = {}
                self.metrics = []
                self.alert_rules = {}
                self.alerts = []
                self.telemetry_data = []
            
            async def check_service_health(self, service_name: str, user_context=None) -> HealthCheck:
                health_check = HealthCheck(
                    service_name=service_name,
                    status=HealthStatus.HEALTHY,
                    message="Service is running normally",
                    timestamp=datetime.utcnow(),
                    response_time_ms=150.5,
                    details={"check_type": "basic"}
                )
                self.health_checks[service_name] = health_check
                return health_check
            
            async def check_all_services_health(self, user_context=None) -> List[HealthCheck]:
                return list(self.health_checks.values())
            
            async def get_overall_health(self, user_context=None) -> Dict[str, Any]:
                return {
                    "status": "healthy",
                    "total_services": len(self.health_checks),
                    "healthy_services": len([h for h in self.health_checks.values() if h.status == HealthStatus.HEALTHY]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            async def record_metric(self, metric: MetricData, user_context=None) -> Dict[str, Any]:
                self.metrics.append(metric)
                return {"status": "recorded", "metric_name": metric.name}
            
            async def get_metrics(self, metric_name: str, start_time: datetime, end_time: datetime, user_context=None) -> List[MetricData]:
                filtered_metrics = [m for m in self.metrics if m.name == metric_name and start_time <= m.timestamp <= end_time]
                return filtered_metrics
            
            async def get_metric_summary(self, metric_name: str, start_time: datetime, end_time: datetime, user_context=None) -> Dict[str, Any]:
                filtered_metrics = [m for m in self.metrics if m.name == metric_name and start_time <= m.timestamp <= end_time]
                if not filtered_metrics:
                    return {"metric_name": metric_name, "count": 0, "avg": 0, "min": 0, "max": 0}
                
                values = [m.value for m in filtered_metrics]
                return {
                    "metric_name": metric_name,
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
            
            async def create_alert_rule(self, rule: AlertRule, user_context=None) -> Dict[str, Any]:
                self.alert_rules[rule.rule_id] = rule
                return {"status": "created", "rule_id": rule.rule_id}
            
            async def update_alert_rule(self, rule_id: str, rule: AlertRule, user_context=None) -> Dict[str, Any]:
                if rule_id in self.alert_rules:
                    self.alert_rules[rule_id] = rule
                    return {"status": "updated", "rule_id": rule_id}
                return {"status": "not_found", "rule_id": rule_id}
            
            async def delete_alert_rule(self, rule_id: str, user_context=None) -> Dict[str, Any]:
                if rule_id in self.alert_rules:
                    del self.alert_rules[rule_id]
                    return {"status": "deleted", "rule_id": rule_id}
                return {"status": "not_found", "rule_id": rule_id}
            
            async def get_active_alerts(self, user_context=None) -> List[Alert]:
                return [alert for alert in self.alerts if alert.is_active]
            
            async def resolve_alert(self, alert_id: str, user_context=None) -> Dict[str, Any]:
                for alert in self.alerts:
                    if alert.alert_id == alert_id and alert.is_active:
                        alert.is_active = False
                        alert.resolved_at = datetime.utcnow()
                        return {"status": "resolved", "alert_id": alert_id}
                return {"status": "not_found", "alert_id": alert_id}
            
            async def record_telemetry(self, telemetry: TelemetryData, user_context=None) -> Dict[str, Any]:
                self.telemetry_data.append(telemetry)
                return {"status": "recorded", "trace_id": telemetry.trace_id}
            
            async def get_trace(self, trace_id: str, user_context=None) -> List[TelemetryData]:
                return [t for t in self.telemetry_data if t.trace_id == trace_id]
            
            async def get_service_traces(self, service_name: str, start_time: datetime, end_time: datetime, user_context=None) -> List[TelemetryData]:
                return [t for t in self.telemetry_data if t.service_name == service_name and start_time <= t.start_time <= end_time]
            
            async def get_health_dashboard_data(self, user_context=None) -> Dict[str, Any]:
                return {
                    "overall_health": "healthy",
                    "services": list(self.health_checks.keys()),
                    "active_alerts": len([a for a in self.alerts if a.is_active]),
                    "total_metrics": len(self.metrics),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            async def get_health_analytics(self, start_time: datetime, end_time: datetime, user_context=None) -> Dict[str, Any]:
                return {
                    "period": {"start": start_time.isoformat(), "end": end_time.isoformat()},
                    "health_trend": "stable",
                    "alert_frequency": len([a for a in self.alerts if start_time <= a.triggered_at <= end_time]),
                    "metric_count": len([m for m in self.metrics if start_time <= m.timestamp <= end_time])
                }
        
        interface = TestHealthMonitoringInterface()
        
        assert interface is not None
        assert hasattr(interface, 'check_service_health')
        assert hasattr(interface, 'check_all_services_health')
        assert hasattr(interface, 'get_overall_health')
        assert hasattr(interface, 'record_metric')
        assert hasattr(interface, 'get_metrics')
        assert hasattr(interface, 'get_metric_summary')
        assert hasattr(interface, 'create_alert_rule')
        assert hasattr(interface, 'update_alert_rule')
        assert hasattr(interface, 'delete_alert_rule')
        assert hasattr(interface, 'get_active_alerts')
        assert hasattr(interface, 'resolve_alert')
        assert hasattr(interface, 'record_telemetry')
        assert hasattr(interface, 'get_trace')
        assert hasattr(interface, 'get_service_traces')
        assert hasattr(interface, 'get_health_dashboard_data')
        assert hasattr(interface, 'get_health_analytics')
    
    @pytest.mark.asyncio
    async def test_health_monitoring_interface_operations(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test health monitoring interface operations."""
        class TestHealthMonitoringInterface(IHealthMonitoring):
            def __init__(self):
                self.health_checks = {}
                self.metrics = []
                self.alert_rules = {}
                self.alerts = []
                self.telemetry_data = []
            
            async def check_service_health(self, service_name: str, user_context=None) -> HealthCheck:
                health_check = HealthCheck(
                    service_name=service_name,
                    status=HealthStatus.HEALTHY,
                    message="Service is running normally",
                    timestamp=datetime.utcnow(),
                    response_time_ms=150.5,
                    details={"check_type": "basic"}
                )
                self.health_checks[service_name] = health_check
                return health_check
            
            async def check_all_services_health(self, user_context=None) -> List[HealthCheck]:
                return list(self.health_checks.values())
            
            async def get_overall_health(self, user_context=None) -> Dict[str, Any]:
                return {
                    "status": "healthy",
                    "total_services": len(self.health_checks),
                    "healthy_services": len([h for h in self.health_checks.values() if h.status == HealthStatus.HEALTHY]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            async def record_metric(self, metric: MetricData, user_context=None) -> Dict[str, Any]:
                self.metrics.append(metric)
                return {"status": "recorded", "metric_name": metric.name}
            
            async def get_metrics(self, metric_name: str, start_time: datetime, end_time: datetime, user_context=None) -> List[MetricData]:
                filtered_metrics = [m for m in self.metrics if m.name == metric_name and start_time <= m.timestamp <= end_time]
                return filtered_metrics
            
            async def get_metric_summary(self, metric_name: str, start_time: datetime, end_time: datetime, user_context=None) -> Dict[str, Any]:
                filtered_metrics = [m for m in self.metrics if m.name == metric_name and start_time <= m.timestamp <= end_time]
                if not filtered_metrics:
                    return {"metric_name": metric_name, "count": 0, "avg": 0, "min": 0, "max": 0}
                
                values = [m.value for m in filtered_metrics]
                return {
                    "metric_name": metric_name,
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
            
            async def create_alert_rule(self, rule: AlertRule, user_context=None) -> Dict[str, Any]:
                self.alert_rules[rule.rule_id] = rule
                return {"status": "created", "rule_id": rule.rule_id}
            
            async def update_alert_rule(self, rule_id: str, rule: AlertRule, user_context=None) -> Dict[str, Any]:
                if rule_id in self.alert_rules:
                    self.alert_rules[rule_id] = rule
                    return {"status": "updated", "rule_id": rule_id}
                return {"status": "not_found", "rule_id": rule_id}
            
            async def delete_alert_rule(self, rule_id: str, user_context=None) -> Dict[str, Any]:
                if rule_id in self.alert_rules:
                    del self.alert_rules[rule_id]
                    return {"status": "deleted", "rule_id": rule_id}
                return {"status": "not_found", "rule_id": rule_id}
            
            async def get_active_alerts(self, user_context=None) -> List[Alert]:
                return [alert for alert in self.alerts if alert.is_active]
            
            async def resolve_alert(self, alert_id: str, user_context=None) -> Dict[str, Any]:
                for alert in self.alerts:
                    if alert.alert_id == alert_id and alert.is_active:
                        alert.is_active = False
                        alert.resolved_at = datetime.utcnow()
                        return {"status": "resolved", "alert_id": alert_id}
                return {"status": "not_found", "alert_id": alert_id}
            
            async def record_telemetry(self, telemetry: TelemetryData, user_context=None) -> Dict[str, Any]:
                self.telemetry_data.append(telemetry)
                return {"status": "recorded", "trace_id": telemetry.trace_id}
            
            async def get_trace(self, trace_id: str, user_context=None) -> List[TelemetryData]:
                return [t for t in self.telemetry_data if t.trace_id == trace_id]
            
            async def get_service_traces(self, service_name: str, start_time: datetime, end_time: datetime, user_context=None) -> List[TelemetryData]:
                return [t for t in self.telemetry_data if t.service_name == service_name and start_time <= t.start_time <= end_time]
            
            async def get_health_dashboard_data(self, user_context=None) -> Dict[str, Any]:
                return {
                    "overall_health": "healthy",
                    "services": list(self.health_checks.keys()),
                    "active_alerts": len([a for a in self.alerts if a.is_active]),
                    "total_metrics": len(self.metrics),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            async def get_health_analytics(self, start_time: datetime, end_time: datetime, user_context=None) -> Dict[str, Any]:
                return {
                    "period": {"start": start_time.isoformat(), "end": end_time.isoformat()},
                    "health_trend": "stable",
                    "alert_frequency": len([a for a in self.alerts if start_time <= a.triggered_at <= end_time]),
                    "metric_count": len([m for m in self.metrics if start_time <= m.timestamp <= end_time])
                }
        
        interface = TestHealthMonitoringInterface()
        
        # Test check_service_health
        health_check = await interface.check_service_health("test_service")
        assert health_check.service_name == "test_service"
        assert health_check.status == HealthStatus.HEALTHY
        assert health_check.message == "Service is running normally"
        assert health_check.response_time_ms == 150.5
        assert health_check.details["check_type"] == "basic"
        
        # Test check_all_services_health
        all_health_checks = await interface.check_all_services_health()
        assert len(all_health_checks) == 1
        assert all_health_checks[0].service_name == "test_service"
        
        # Test get_overall_health
        overall_health = await interface.get_overall_health()
        assert overall_health["status"] == "healthy"
        assert overall_health["total_services"] == 1
        assert overall_health["healthy_services"] == 1
        assert "timestamp" in overall_health
        
        # Test record_metric
        metric_data = MetricData(
            name="cpu_usage",
            value=75.5,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.utcnow(),
            tags={"service": "test_service"},
            labels={"environment": "production"}
        )
        
        record_result = await interface.record_metric(metric_data)
        assert record_result["status"] == "recorded"
        assert record_result["metric_name"] == "cpu_usage"
        
        # Test get_metrics
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow()
        metrics = await interface.get_metrics("cpu_usage", start_time, end_time)
        assert len(metrics) == 1
        assert metrics[0].name == "cpu_usage"
        assert metrics[0].value == 75.5
        
        # Test get_metric_summary
        summary = await interface.get_metric_summary("cpu_usage", start_time, end_time)
        assert summary["metric_name"] == "cpu_usage"
        assert summary["count"] == 1
        assert summary["avg"] == 75.5
        assert summary["min"] == 75.5
        assert summary["max"] == 75.5
        
        # Test create_alert_rule
        alert_rule = AlertRule(
            rule_id="rule_001",
            name="High CPU Usage",
            metric_name="cpu_usage",
            condition="value > 80",
            severity=AlertSeverity.WARNING,
            enabled=True,
            cooldown_minutes=10,
            description="Alert when CPU usage exceeds 80%"
        )
        
        create_result = await interface.create_alert_rule(alert_rule)
        assert create_result["status"] == "created"
        assert create_result["rule_id"] == "rule_001"
        
        # Test update_alert_rule
        updated_rule = AlertRule(
            rule_id="rule_001",
            name="High CPU Usage Updated",
            metric_name="cpu_usage",
            condition="value > 85",
            severity=AlertSeverity.ERROR,
            enabled=True,
            cooldown_minutes=15,
            description="Updated alert when CPU usage exceeds 85%"
        )
        
        update_result = await interface.update_alert_rule("rule_001", updated_rule)
        assert update_result["status"] == "updated"
        
        # Test get_active_alerts (should be empty initially)
        active_alerts = await interface.get_active_alerts()
        assert len(active_alerts) == 0
        
        # Create an alert manually for testing
        alert = Alert(
            alert_id="alert_001",
            rule_id="rule_001",
            service_name="test_service",
            severity=AlertSeverity.WARNING,
            message="CPU usage is 85%",
            triggered_at=datetime.utcnow(),
            metadata={"value": 85.0}
        )
        interface.alerts.append(alert)
        
        # Test get_active_alerts
        active_alerts = await interface.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0].alert_id == "alert_001"
        assert active_alerts[0].is_active is True
        
        # Test resolve_alert
        resolve_result = await interface.resolve_alert("alert_001")
        assert resolve_result["status"] == "resolved"
        assert resolve_result["alert_id"] == "alert_001"
        
        # Verify alert is resolved
        active_alerts = await interface.get_active_alerts()
        assert len(active_alerts) == 0
        
        # Test record_telemetry
        start_time_telemetry = datetime.utcnow()
        end_time_telemetry = start_time_telemetry + timedelta(milliseconds=150)
        
        telemetry_data = TelemetryData(
            trace_id="trace_001",
            span_id="span_001",
            operation_name="api_call",
            service_name="test_service",
            start_time=start_time_telemetry,
            end_time=end_time_telemetry,
            duration_ms=150.0,
            status="success",
            tags={"endpoint": "/api/test"},
            logs=[{"level": "info", "message": "Request processed"}]
        )
        
        telemetry_result = await interface.record_telemetry(telemetry_data)
        assert telemetry_result["status"] == "recorded"
        assert telemetry_result["trace_id"] == "trace_001"
        
        # Test get_trace
        trace = await interface.get_trace("trace_001")
        assert len(trace) == 1
        assert trace[0].trace_id == "trace_001"
        assert trace[0].span_id == "span_001"
        assert trace[0].operation_name == "api_call"
        
        # Test get_service_traces
        service_traces = await interface.get_service_traces("test_service", start_time_telemetry - timedelta(minutes=1), end_time_telemetry + timedelta(minutes=1))
        assert len(service_traces) == 1
        assert service_traces[0].service_name == "test_service"
        
        # Test get_health_dashboard_data
        dashboard_data = await interface.get_health_dashboard_data()
        assert dashboard_data["overall_health"] == "healthy"
        assert "test_service" in dashboard_data["services"]
        assert dashboard_data["active_alerts"] == 0
        assert dashboard_data["total_metrics"] == 1
        assert "timestamp" in dashboard_data
        
        # Test get_health_analytics
        analytics_start = datetime.utcnow() - timedelta(hours=1)
        analytics_end = datetime.utcnow()
        analytics = await interface.get_health_analytics(analytics_start, analytics_end)
        assert analytics["period"]["start"] == analytics_start.isoformat()
        assert analytics["period"]["end"] == analytics_end.isoformat()
        assert analytics["health_trend"] == "stable"
        assert analytics["alert_frequency"] == 1  # We created one alert
        assert analytics["metric_count"] == 1  # We recorded one metric
        
        # Test delete_alert_rule
        delete_result = await interface.delete_alert_rule("rule_001")
        assert delete_result["status"] == "deleted"
        
        # Test delete non-existent rule
        delete_nonexistent_result = await interface.delete_alert_rule("non_existent")
        assert delete_nonexistent_result["status"] == "not_found"