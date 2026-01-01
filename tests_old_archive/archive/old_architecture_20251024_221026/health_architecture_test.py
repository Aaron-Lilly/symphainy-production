#!/usr/bin/env python3
"""
Health Architecture Test - Comprehensive test for health monitoring infrastructure

Tests the complete 5-layer health monitoring architecture:
1. HealthProtocol (abstraction contracts)
2. Health Adapters (OpenTelemetry, Simple Health)
3. HealthAbstraction (infrastructure coordination)
4. HealthCompositionService (infrastructure business logic)
5. HealthService (agentic business logic)
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

from foundations.public_works_foundation.abstraction_contracts.health_protocol import (
    HealthContext, HealthCheck, HealthMetric, HealthReport, HealthAlert,
    HealthStatus, HealthType, AlertSeverity
)
from foundations.public_works_foundation.infrastructure_adapters.simple_health_adapter import SimpleHealthAdapter
from foundations.public_works_foundation.infrastructure_adapters.opentelemetry_health_adapter import OpenTelemetryHealthAdapter
from foundations.public_works_foundation.infrastructure_abstractions.health_abstraction import HealthAbstraction
from foundations.public_works_foundation.composition_services.health_composition_service import HealthCompositionService
from foundations.agentic_foundation.business_services.health_service import HealthService


async def test_health_protocol():
    """Test HealthProtocol contracts and data structures."""
    print("🧪 Testing HealthProtocol...")
    
    # Test HealthContext
    context = HealthContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="test",
        region="us-west-2",
        metadata={"test_key": "test_value"}
    )
    
    assert context.service_id == "test_service"
    assert context.agent_id == "test_agent"
    assert context.tenant_id == "test_tenant"
    assert context.environment == "test"
    assert context.region == "us-west-2"
    assert context.metadata["test_key"] == "test_value"
    
    # Test HealthCheck
    check = HealthCheck(
        check_id="test_check",
        check_name="Test Health Check",
        health_type=HealthType.SYSTEM,
        status=HealthStatus.HEALTHY,
        message="Test health check passed",
        timestamp=datetime.utcnow(),
        response_time_ms=100.0,
        metadata={"test": "metadata"}
    )
    
    assert check.check_id == "test_check"
    assert check.check_name == "Test Health Check"
    assert check.health_type == HealthType.SYSTEM
    assert check.status == HealthStatus.HEALTHY
    assert check.message == "Test health check passed"
    assert check.response_time_ms == 100.0
    assert check.metadata["test"] == "metadata"
    
    # Test HealthMetric
    metric = HealthMetric(
        name="test_metric",
        value=85.5,
        unit="percent",
        timestamp=datetime.utcnow(),
        labels={"service": "test"},
        metadata={"adapter": "test"}
    )
    
    assert metric.name == "test_metric"
    assert metric.value == 85.5
    assert metric.unit == "percent"
    assert metric.labels["service"] == "test"
    assert metric.metadata["adapter"] == "test"
    
    # Test HealthAlert
    alert = HealthAlert(
        alert_id="test_alert",
        alert_name="Test Alert",
        severity=AlertSeverity.WARNING,
        status=HealthStatus.DEGRADED,
        message="Test alert message",
        timestamp=datetime.utcnow(),
        service_id="test_service",
        agent_id="test_agent",
        metadata={"test": "alert"}
    )
    
    assert alert.alert_id == "test_alert"
    assert alert.alert_name == "Test Alert"
    assert alert.severity == AlertSeverity.WARNING
    assert alert.status == HealthStatus.DEGRADED
    assert alert.message == "Test alert message"
    assert alert.service_id == "test_service"
    assert alert.agent_id == "test_agent"
    assert alert.metadata["test"] == "alert"
    
    print("✅ HealthProtocol tests passed")


async def test_simple_health_adapter():
    """Test SimpleHealthAdapter."""
    print("🧪 Testing SimpleHealthAdapter...")
    
    adapter = SimpleHealthAdapter()
    
    # Test health check
    health = await adapter.health_check()
    assert health["status"] == "healthy"
    assert health["adapter"] == "simple_health"
    
    # Test health check
    context = HealthContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    check = await adapter.check_health(HealthType.SYSTEM, context)
    assert check.health_type == HealthType.SYSTEM
    assert check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    
    # Test metrics collection
    metrics = await adapter.collect_metrics(HealthType.SYSTEM, context)
    assert len(metrics) > 0
    assert any(m.name == "cpu_usage_percent" for m in metrics)
    assert any(m.name == "memory_usage_percent" for m in metrics)
    assert any(m.name == "disk_usage_percent" for m in metrics)
    
    # Test health report
    report = await adapter.get_health_report("test_service", context)
    assert report.service_id == "test_service"
    assert report.overall_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    assert len(report.health_checks) > 0
    assert len(report.metrics) > 0
    
    print("✅ SimpleHealthAdapter tests passed")


async def test_opentelemetry_adapter():
    """Test OpenTelemetryHealthAdapter."""
    print("🧪 Testing OpenTelemetryHealthAdapter...")
    
    adapter = OpenTelemetryHealthAdapter()
    
    # Test health check
    health = await adapter.health_check()
    assert health["adapter"] == "opentelemetry"
    
    # Test health check
    context = HealthContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    check = await adapter.check_health(HealthType.SYSTEM, context)
    assert check.health_type == HealthType.SYSTEM
    assert check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN]
    
    # Test metrics collection
    metrics = await adapter.collect_metrics(HealthType.SYSTEM, context)
    assert len(metrics) > 0
    assert any(m.name == "cpu_usage_percent" for m in metrics)
    assert any(m.name == "memory_usage_percent" for m in metrics)
    assert any(m.name == "disk_usage_percent" for m in metrics)
    
    print("✅ OpenTelemetryHealthAdapter tests passed")


async def test_health_abstraction():
    """Test HealthAbstraction."""
    print("🧪 Testing HealthAbstraction...")
    
    # Test with simple health adapter
    abstraction = HealthAbstraction(adapter_type="simple_health")
    
    # Test health check
    health = await abstraction.health_check()
    assert health["abstraction_layer"] == "health_abstraction"
    assert health["adapter_type"] == "simple_health"
    
    # Test health check
    context = HealthContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    check = await abstraction.check_health(HealthType.SYSTEM, context)
    assert check.health_type == HealthType.SYSTEM
    assert check.metadata["adapter_type"] == "simple_health"
    assert check.metadata["abstraction_layer"] == "health_abstraction"
    
    # Test adapter switching
    switch_result = await abstraction.switch_adapter("opentelemetry")
    assert switch_result == True
    assert abstraction.adapter_type == "opentelemetry"
    
    print("✅ HealthAbstraction tests passed")


async def test_health_composition_service():
    """Test HealthCompositionService."""
    print("🧪 Testing HealthCompositionService...")
    
    # Create abstraction and composition service
    abstraction = HealthAbstraction(adapter_type="simple_health")
    composition_service = HealthCompositionService(abstraction)
    
    # Test health check
    health = await composition_service.health_check()
    assert health["service"] == "health_composition_service"
    
    # Test health orchestration
    context = HealthContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    result = await composition_service.orchestrate_health_monitoring(
        "system_health",
        context
    )
    assert result["workflow_type"] == "system_health"
    assert "overall_status" in result
    assert "health_checks" in result
    
    # Test health assessment
    assessment = await composition_service.perform_health_assessment(
        "test_service",
        context
    )
    assert assessment["success"] == True
    assert "overall_status" in assessment
    assert "health_report" in assessment
    assert "assessment" in assessment
    
    # Test health metrics
    metrics = await composition_service.get_health_metrics()
    assert metrics["success"] == True
    assert "adapter_health" in metrics
    assert "available_workflows" in metrics
    
    print("✅ HealthCompositionService tests passed")


async def test_health_service():
    """Test HealthService."""
    print("🧪 Testing HealthService...")
    
    # Create dependencies
    abstraction = HealthAbstraction(adapter_type="simple_health")
    composition_service = HealthCompositionService(abstraction)
    health_service = HealthService(abstraction, composition_service)
    
    # Test health check
    health = await health_service.health_check()
    assert health["service"] == "health_service"
    assert "monitoring_types" in health
    
    # Test health monitoring
    context = HealthContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    # Test LLM health monitoring
    llm_result = await health_service.monitor_agent_health(
        "llm_health",
        context
    )
    assert llm_result["operation_type"] == "llm_health"
    assert "operation_healthy" in llm_result
    
    # Test MCP health monitoring
    mcp_result = await health_service.monitor_agent_health(
        "mcp_health",
        context
    )
    assert mcp_result["operation_type"] == "mcp_health"
    assert "operation_healthy" in mcp_result
    
    # Test tool health monitoring
    tool_result = await health_service.monitor_agent_health(
        "tool_health",
        context
    )
    assert tool_result["operation_type"] == "tool_health"
    assert "operation_healthy" in tool_result
    
    # Test agent health monitoring
    agent_result = await health_service.monitor_agent_health(
        "agent_health",
        context
    )
    assert agent_result["operation_type"] == "agent_health"
    assert "operation_healthy" in agent_result
    
    # Test agent health assessment
    assessment = await health_service.assess_agent_health(
        "test_agent",
        context
    )
    assert assessment["agent_id"] == "test_agent"
    assert "overall_status" in assessment
    assert "health_assessment" in assessment
    assert "health_score" in assessment
    assert "recommendations" in assessment
    
    # Test agent health metrics
    metrics = await health_service.get_agent_health_metrics(
        "test_agent",
        context
    )
    assert metrics["agent_id"] == "test_agent"
    assert "agent_metrics" in metrics
    assert "system_metrics" in metrics
    assert "analysis" in metrics
    
    # Test health alert creation
    alert_result = await health_service.create_agent_health_alert(
        "test_agent",
        "Test Alert",
        AlertSeverity.WARNING,
        "Test alert message"
    )
    assert "success" in alert_result
    assert "alert_id" in alert_result
    
    print("✅ HealthService tests passed")


async def test_integration():
    """Test end-to-end integration."""
    print("🧪 Testing end-to-end integration...")
    
    # Create complete health monitoring infrastructure
    abstraction = HealthAbstraction(adapter_type="simple_health")
    composition_service = HealthCompositionService(abstraction)
    health_service = HealthService(abstraction, composition_service)
    
    # Test complete workflow
    context = HealthContext(
        service_id="integration_service",
        agent_id="integration_agent",
        tenant_id="integration_tenant",
        environment="production",
        region="us-west-2",
        metadata={"integration_test": True}
    )
    
    # 1. Assess agent health
    assessment = await health_service.assess_agent_health("integration_agent", context)
    print(f"   Agent health assessment: {assessment['overall_status']}")
    print(f"   Health score: {assessment.get('health_score', 0):.1f}")
    
    # 2. Monitor health for different operations
    operations = ["llm_health", "mcp_health", "tool_health", "agent_health"]
    for operation in operations:
        result = await health_service.monitor_agent_health(operation, context)
        print(f"   {operation}: {'Healthy' if result.get('operation_healthy') else 'Unhealthy'}")
    
    # 3. Get agent health metrics
    metrics = await health_service.get_agent_health_metrics("integration_agent", context)
    print(f"   Agent metrics: {len(metrics.get('agent_metrics', []))} metrics")
    print(f"   System metrics: {len(metrics.get('system_metrics', []))} metrics")
    
    # 4. Test health orchestration
    orchestration = await composition_service.orchestrate_health_monitoring(
        "comprehensive_health",
        context
    )
    print(f"   Comprehensive health: {orchestration.get('overall_status', 'unknown')}")
    
    # 5. Test health assessment
    health_assessment = await composition_service.perform_health_assessment(
        "integration_service",
        context
    )
    print(f"   Health assessment: {health_assessment.get('overall_status', 'unknown')}")
    
    print("✅ End-to-end integration tests passed")


async def main():
    """Run all health architecture tests."""
    print("🚀 Starting Health Architecture Tests")
    print("=" * 50)
    
    try:
        await test_health_protocol()
        await test_simple_health_adapter()
        await test_opentelemetry_adapter()
        await test_health_abstraction()
        await test_health_composition_service()
        await test_health_service()
        await test_integration()
        
        print("=" * 50)
        print("🎉 All Health Architecture Tests Passed!")
        print(f"✅ Test completed at {datetime.utcnow().isoformat()}")
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Health Architecture Tests Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

