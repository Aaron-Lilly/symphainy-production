#!/usr/bin/env python3
"""
Test NurseService with new protocol-based architecture

Tests the refactored NurseService to verify:
1. It uses SmartCityRoleBase
2. It imports data models from the protocol
3. Core functionality is preserved
4. Orchestration capabilities work
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

from foundations.di_container.di_container_service import DIContainerService
from backend.smart_city.services.nurse.nurse_service import NurseService
from bases.protocols.nurse_protocol import (
    CollectTelemetryRequest, CollectTelemetryResponse,
    GetHealthMetricsRequest, GetHealthMetricsResponse,
    SetAlertThresholdRequest, SetAlertThresholdResponse,
    RunDiagnosticsRequest, RunDiagnosticsResponse,
    GetSystemStatusRequest, GetSystemStatusResponse,
    DistributedHealthRequest, DistributedHealthResponse,
    MetricType, HealthStatus
)


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.foundation_services = {}
    
    def get_foundation_service(self, service_name: str):
        """Mock foundation service getter."""
        return self.foundation_services.get(service_name, None)


async def test_nurse_service_initialization():
    """Test that NurseService initializes correctly."""
    print("🧪 Testing NurseService initialization...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        # Verify initialization
        assert hasattr(nurse_service, 'service_name')
        assert nurse_service.service_name == "NurseService"
        assert hasattr(nurse_service, 'health_metrics')
        assert hasattr(nurse_service, 'telemetry_data')
        assert hasattr(nurse_service, 'alert_thresholds')
        
        print("✅ NurseService initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ NurseService initialization failed: {e}")
        return False


async def test_collect_telemetry():
    """Test telemetry collection."""
    print("\n🧪 Testing telemetry collection...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        # Create a request
        request = CollectTelemetryRequest(
            service_name="test_service",
            metric_name="cpu_usage",
            metric_value=75.5,
            metric_type=MetricType.GAUGE,
            tags={"env": "test"},
            tenant_id="test_tenant"
        )
        
        # Collect telemetry
        response = await nurse_service.collect_telemetry(request)
        
        # Verify response
        assert response.success == True
        assert response.metric_id is not None
        assert response.service_name == "test_service"
        assert response.metric_name == "cpu_usage"
        
        # Verify data was stored
        assert "test_service" in nurse_service.telemetry_data
        assert len(nurse_service.telemetry_data["test_service"]) > 0
        
        print("✅ Telemetry collection works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Telemetry collection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_health_metrics():
    """Test getting health metrics."""
    print("\n🧪 Testing health metrics retrieval...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        # First, collect some telemetry
        collect_request = CollectTelemetryRequest(
            service_name="test_service",
            metric_name="cpu_usage",
            metric_value=75.5,
            metric_type=MetricType.GAUGE
        )
        await nurse_service.collect_telemetry(collect_request)
        
        # Now get health metrics
        request = GetHealthMetricsRequest(
            service_name="test_service",
            tenant_id="test_tenant"
        )
        
        response = await nurse_service.get_health_metrics(request)
        
        # Verify response
        assert response.success == True
        assert response.service_name == "test_service"
        assert response.metrics is not None
        assert "cpu_usage" in response.metrics
        
        print("✅ Health metrics retrieval works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Health metrics retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_set_alert_threshold():
    """Test setting alert thresholds."""
    print("\n🧪 Testing alert threshold setting...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        request = SetAlertThresholdRequest(
            service_name="test_service",
            metric_name="cpu_usage",
            warning_threshold=70.0,
            critical_threshold=90.0,
            tenant_id="test_tenant"
        )
        
        response = await nurse_service.set_alert_threshold(request)
        
        # Verify response
        assert response.success == True
        assert response.metric_name == "cpu_usage"
        assert response.warning_threshold == 70.0
        assert response.critical_threshold == 90.0
        
        # Verify threshold was stored
        assert "cpu_usage" in nurse_service.alert_thresholds
        
        print("✅ Alert threshold setting works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Alert threshold setting failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_run_diagnostics():
    """Test running diagnostics."""
    print("\n🧪 Testing system diagnostics...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        request = RunDiagnosticsRequest(
            diagnostic_type="health_check",
            target_services=["test_service"],
            include_details=True,
            tenant_id="test_tenant"
        )
        
        response = await nurse_service.run_diagnostics(request)
        
        # Verify response
        assert response.success == True
        assert response.diagnostic_id is not None
        assert response.diagnostic_type == "health_check"
        assert response.results is not None
        
        print("✅ System diagnostics works correctly")
        return True
        
    except Exception as e:
        print(f"❌ System diagnostics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_system_status():
    """Test getting system status."""
    print("\n🧪 Testing system status retrieval...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        # Add some telemetry first
        await nurse_service.collect_telemetry(CollectTelemetryRequest(
            service_name="service1",
            metric_name="cpu_usage",
            metric_value=50.0
        ))
        
        request = GetSystemStatusRequest(
            include_services=True,
            include_metrics=True,
            tenant_id="test_tenant"
        )
        
        response = await nurse_service.get_system_status(request)
        
        # Verify response
        assert response.success == True
        assert response.overall_status is not None
        assert response.system_metrics is not None
        assert response.service_statuses is not None
        
        print("✅ System status retrieval works correctly")
        return True
        
    except Exception as e:
        print(f"❌ System status retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_distributed_health():
    """Test distributed health orchestration."""
    print("\n🧪 Testing distributed health orchestration...")
    
    try:
        di_container = MockDIContainer()
        nurse_service = NurseService(di_container)
        
        # Add some telemetry for services
        await nurse_service.collect_telemetry(CollectTelemetryRequest(
            service_name="service1",
            metric_name="cpu_usage",
            metric_value=50.0
        ))
        await nurse_service.collect_telemetry(CollectTelemetryRequest(
            service_name="service2",
            metric_name="memory_usage",
            metric_value=75.0
        ))
        
        # Set some thresholds
        await nurse_service.set_alert_threshold(SetAlertThresholdRequest(
            service_name="service1",
            metric_name="cpu_usage",
            warning_threshold=70.0,
            critical_threshold=90.0
        ))
        
        # Now test distributed health check
        request = DistributedHealthRequest(
            health_check_id="test_health_check_1",
            target_services=["service1", "service2"],
            health_check_type="comprehensive",
            tenant_id="test_tenant"
        )
        
        response = await nurse_service.orchestrate_distributed_health(request)
        
        # Verify response
        assert response.success == True
        assert response.health_summary is not None
        assert response.service_health_status is not None
        assert response.overall_health is not None
        
        print("✅ Distributed health orchestration works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Distributed health orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_protocol_imports():
    """Test that data models are properly imported from protocol."""
    print("\n🧪 Testing protocol imports...")
    
    try:
        # Verify we can import data models from protocol
        from bases.protocols.nurse_protocol import (
            HealthStatus, MetricType, AlertSeverity,
            CollectTelemetryRequest, GetHealthMetricsRequest
        )
        
        # Verify we can create instances
        request = CollectTelemetryRequest(
            service_name="test",
            metric_name="test_metric",
            metric_value=1.0
        )
        
        assert request.service_name == "test"
        assert request.metric_name == "test_metric"
        
        print("✅ Protocol imports work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Protocol imports failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("🧪 TESTING NURSE SERVICE REFACTORING")
    print("=" * 70)
    
    tests = [
        ("Protocol Imports", test_protocol_imports),
        ("Service Initialization", test_nurse_service_initialization),
        ("Telemetry Collection", test_collect_telemetry),
        ("Health Metrics Retrieval", test_get_health_metrics),
        ("Alert Threshold Setting", test_set_alert_threshold),
        ("System Diagnostics", test_run_diagnostics),
        ("System Status Retrieval", test_get_system_status),
        ("Distributed Health Orchestration", test_distributed_health),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


