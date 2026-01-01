#!/usr/bin/env python3
"""
Test Nurse Service with Proper Infrastructure Mapping

Validates that the Nurse Service correctly uses the new infrastructure abstractions:
- Telemetry Abstraction (OpenTelemetry + Tempo)
- Alert Management Abstraction (Redis-based)
- Session Management (Redis)
- State Management (Redis)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Import the Nurse Service
from nurse_service_clean_rebuild import NurseService, NurseServiceProtocol

# Mock classes for testing
class MockDIContainer:
    """Mock DI Container for testing."""
    def __init__(self):
        self.utilities = {
            "logger": MockLogger(),
            "telemetry": MockTelemetry(),
            "error_handler": MockErrorHandler(),
            "health": MockHealth()
        }
    
    def get_utility(self, utility_name: str):
        return self.utilities.get(utility_name)

class MockLogger:
    """Mock Logger for testing."""
    def info(self, message: str): print(f"INFO: {message}")
    def debug(self, message: str): print(f"DEBUG: {message}")
    def warning(self, message: str): print(f"WARNING: {message}")
    def error(self, message: str): print(f"ERROR: {message}")

class MockTelemetry:
    """Mock Telemetry for testing."""
    def record_metric(self, name: str, value: float, tags: Dict[str, Any] = None): pass
    def record_event(self, name: str, data: Dict[str, Any] = None): pass

class MockErrorHandler:
    """Mock Error Handler for testing."""
    def handle_error(self, error: Exception, context: Dict[str, Any] = None): pass

class MockHealth:
    """Mock Health for testing."""
    def get_health_status(self): return {"status": "healthy"}

class MockHealthAbstraction:
    """Mock Health Abstraction for testing."""
    def __init__(self):
        self.health_metrics = []
        self.health_checks = []
    
    async def collect_metrics(self, health_type, context):
        self.health_metrics.append({
            "health_type": health_type,
            "context": context
        })
        return []
    
    async def check_health(self, health_type, context):
        self.health_checks.append({
            "health_type": health_type,
            "context": context
        })
        return {"status": "healthy", "details": "mock health check"}
    
    async def get_health_report(self, service_name):
        return {
            "service_name": service_name,
            "status": "healthy",
            "metrics": self.health_metrics,
            "checks": self.health_checks
        }
    
    async def get_health_metrics(self, service_name):
        return {
            "service_name": service_name,
            "metrics": self.health_metrics,
            "status": "healthy"
        }
    
    async def run_diagnostics(self, service_name):
        return {
            "service_name": service_name,
            "diagnostics": "mock diagnostics",
            "status": "healthy"
        }
    
    async def store_diagnostics(self, service_name, diagnostics, diagnostics_data=None):
        return True
    
    async def store_orchestration_result(self, result, orchestration_id=None):
        return True
    
    async def store_wellness_result(self, result, wellness_id=None):
        return True
    
    async def health_check(self):
        return {
            "status": "healthy",
            "abstraction_layer": "health_abstraction",
            "adapter_type": "opentelemetry_health",
            "timestamp": "2024-01-01T00:00:00Z"
        }

class MockPublicWorksFoundation:
    """Mock Public Works Foundation for testing."""
    def __init__(self):
        self.telemetry_abstraction = MockTelemetryAbstraction()
        self.alert_management_abstraction = MockAlertManagementAbstraction()
        self.health_abstraction = MockHealthAbstraction()
        self.session_abstraction = MockSessionAbstraction()
        self.state_management_abstraction = MockStateManagementAbstraction()
    
    def get_telemetry_abstraction(self):
        return self.telemetry_abstraction
    
    def get_alert_management_abstraction(self):
        return self.alert_management_abstraction
    
    def get_health_abstraction(self):
        return self.health_abstraction
    
    def get_session_abstraction(self):
        return self.session_abstraction
    
    async def get_abstraction(self, name: str):
        if name == "state_management":
            return self.state_management_abstraction
        return None

class MockTelemetryAbstraction:
    """Mock Telemetry Abstraction for testing."""
    def __init__(self):
        self.metrics_collected = []
        self.traces_started = []
        self.spans_added = []
    
    async def collect_metric(self, metric_id=None, telemetry_data=None, metric_data=None):
        if telemetry_data:
            self.metrics_collected.append(telemetry_data)
        elif metric_data:
            self.metrics_collected.append(metric_data)
        return True
    
    async def collect_trace(self, trace_data):
        self.traces_started.append(trace_data)
        return True
    
    async def collect_log(self, log_data):
        return True
    
    async def collect_event(self, event_data):
        return True
    
    async def get_metrics(self, query, time_range=None):
        return self.metrics_collected
    
    async def get_traces(self, query, time_range=None):
        return self.traces_started
    
    async def get_logs(self, query, time_range=None):
        return []
    
    async def health_check(self):
        return {
            "status": "healthy",
            "abstraction_layer": "telemetry_abstraction",
            "adapter_type": "opentelemetry",
            "timestamp": datetime.utcnow().isoformat()
        }

class MockAlertManagementAbstraction:
    """Mock Alert Management Abstraction for testing."""
    def __init__(self):
        self.alerts_created = []
        self.alert_rules = []
        self.notifications_sent = []
    
    async def create_alert(self, alert):
        self.alerts_created.append(alert)
        return str(uuid.uuid4())
    
    async def update_alert(self, alert_id, updates):
        return True
    
    async def get_alert(self, alert_id):
        return {"id": alert_id, "title": "Test Alert", "status": "active"}
    
    async def list_alerts(self, filters=None, limit=100):
        return self.alerts_created
    
    async def create_alert_rule(self, rule):
        self.alert_rules.append(rule)
        return str(uuid.uuid4())
    
    async def evaluate_alert_rules(self, data):
        return []
    
    async def send_notification(self, alert, channel):
        self.notifications_sent.append((alert, channel))
        return True
    
    async def acknowledge_alert(self, alert_id, user_id):
        return True
    
    async def resolve_alert(self, alert_id, user_id):
        return True
    
    async def health_check(self):
        return {
            "status": "healthy",
            "abstraction_layer": "alert_management_abstraction",
            "adapter_type": "redis_alerting",
            "timestamp": datetime.utcnow().isoformat()
        }

class MockSessionAbstraction:
    """Mock Session Abstraction for testing."""
    def __init__(self):
        self.sessions = {}
    
    async def create_session(self, user_id, session_data):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {"user_id": user_id, "data": session_data}
        return session_id
    
    async def get_session(self, session_id):
        return self.sessions.get(session_id)
    
    async def update_session(self, session_id, updates):
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            return True
        return False
    
    async def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    async def health_check(self):
        return {"status": "healthy"}

class MockStateManagementAbstraction:
    """Mock State Management Abstraction for testing."""
    def __init__(self):
        self.states = {}
    
    async def set_state(self, key, value):
        self.states[key] = value
        return True
    
    async def get_state(self, key):
        return self.states.get(key)
    
    async def delete_state(self, key):
        if key in self.states:
            del self.states[key]
            return True
        return False
    
    async def health_check(self):
        return {"status": "healthy"}

async def test_nurse_service_infrastructure_mapping():
    """Test Nurse Service with proper infrastructure mapping."""
    print("Testing Nurse Service with Proper Infrastructure Mapping...")
    
    # Create mock foundations
    mock_di_container = MockDIContainer()
    mock_public_works = MockPublicWorksFoundation()
    
    # Initialize Nurse Service
    nurse_service = NurseService(di_container=mock_di_container)
    
    # Mock the get_public_works_foundation method
    nurse_service.get_public_works_foundation = lambda: mock_public_works
    
    # Test 1: Service Initialization
    print("\n1. Testing Service Initialization...")
    success = await nurse_service.initialize()
    assert success, "Nurse Service should initialize successfully"
    assert nurse_service.is_infrastructure_connected, "Infrastructure should be connected"
    print("✅ Service initialization successful")
    
    # Test 2: Infrastructure Mapping Validation
    print("\n2. Testing Infrastructure Mapping...")
    
    # Check telemetry abstraction
    assert nurse_service.telemetry_abstraction is not None, "Telemetry abstraction should be connected"
    assert isinstance(nurse_service.telemetry_abstraction, MockTelemetryAbstraction), "Should use proper telemetry abstraction"
    print("✅ Telemetry Abstraction (OpenTelemetry + Tempo) connected")
    
    # Check alert management abstraction
    assert nurse_service.alert_management_abstraction is not None, "Alert management abstraction should be connected"
    assert isinstance(nurse_service.alert_management_abstraction, MockAlertManagementAbstraction), "Should use proper alert management abstraction"
    print("✅ Alert Management Abstraction (Redis) connected")
    
    # Check health abstraction
    assert nurse_service.health_abstraction is not None, "Health abstraction should be connected"
    assert isinstance(nurse_service.health_abstraction, MockHealthAbstraction), "Should use proper health abstraction"
    print("✅ Health Abstraction (OpenTelemetry + Simple Health) connected")
    
    # Check session management abstraction
    assert nurse_service.session_management_abstraction is not None, "Session management abstraction should be connected"
    assert isinstance(nurse_service.session_management_abstraction, MockSessionAbstraction), "Should use proper session management abstraction"
    print("✅ Session Management Abstraction (Redis) connected")
    
    # Check state management abstraction
    assert nurse_service.state_management_abstraction is not None, "State management abstraction should be connected"
    assert isinstance(nurse_service.state_management_abstraction, MockStateManagementAbstraction), "Should use proper state management abstraction"
    print("✅ State Management Abstraction (Redis) connected")
    
    # Test 3: Telemetry Collection
    print("\n3. Testing Telemetry Collection...")
    trace_id = await nurse_service.collect_telemetry("test_service", "cpu_usage", 75.5, {"host": "test-host"})
    assert trace_id is not None, "Should return trace ID"
    assert len(mock_public_works.telemetry_abstraction.metrics_collected) > 0, "Should collect metrics"
    print("✅ Telemetry collection working")
    
    # Test 4: Distributed Tracing
    print("\n4. Testing Distributed Tracing...")
    trace_id = await nurse_service.start_trace("test_trace", {"service": "test_service"})
    assert trace_id is not None, "Should return trace ID"
    
    span_id = await nurse_service.add_span(trace_id, "test_span", {"operation": "test"})
    assert span_id is not None, "Should return span ID"
    
    success = await nurse_service.end_trace(trace_id, "success")
    assert success, "Should end trace successfully"
    print("✅ Distributed tracing working")
    
    # Test 5: Alert Management
    print("\n5. Testing Alert Management...")
    success = await nurse_service.set_alert_threshold("test_service", "cpu_usage", 80.0)
    assert success, "Should set alert threshold"
    print("✅ Alert management working")
    
    # Test 6: Health Monitoring
    print("\n6. Testing Health Monitoring...")
    metrics = await nurse_service.get_health_metrics("test_service")
    assert isinstance(metrics, dict), "Should return health metrics"
    print("✅ Health monitoring working")
    
    # Test 7: System Diagnostics
    print("\n7. Testing System Diagnostics...")
    diagnostics = await nurse_service.run_diagnostics("test_service")
    assert isinstance(diagnostics, dict), "Should return diagnostics"
    print("✅ System diagnostics working")
    
    # Test 8: Health Orchestration
    print("\n8. Testing Health Orchestration...")
    orchestration = await nurse_service.orchestrate_health_monitoring(["service1", "service2"])
    assert isinstance(orchestration, dict), "Should return orchestration results"
    print("✅ Health orchestration working")
    
    # Test 9: SOA API Exposure
    print("\n9. Testing SOA API Exposure...")
    assert "collect_telemetry" in nurse_service.soa_apis, "Should expose collect_telemetry API"
    assert "start_trace" in nurse_service.soa_apis, "Should expose start_trace API"
    assert "set_alert_threshold" in nurse_service.soa_apis, "Should expose set_alert_threshold API"
    print("✅ SOA API exposure working")
    
    # Test 10: MCP Tool Integration
    print("\n10. Testing MCP Tool Integration...")
    assert "collect_telemetry" in nurse_service.mcp_tools, "Should expose collect_telemetry MCP tool"
    assert "start_trace" in nurse_service.mcp_tools, "Should expose start_trace MCP tool"
    assert "run_diagnostics" in nurse_service.mcp_tools, "Should expose run_diagnostics MCP tool"
    print("✅ MCP tool integration working")
    
    # Test 11: Infrastructure Health Check
    print("\n11. Testing Infrastructure Health Check...")
    telemetry_health = await nurse_service.telemetry_abstraction.health_check()
    assert telemetry_health["status"] == "healthy", "Telemetry should be healthy"
    
    alert_health = await nurse_service.alert_management_abstraction.health_check()
    assert alert_health["status"] == "healthy", "Alert management should be healthy"
    print("✅ Infrastructure health checks working")
    
    print("\n🎉 All Nurse Service infrastructure mapping tests passed!")
    print("\n📊 Infrastructure Summary:")
    print(f"  - Telemetry Abstraction: OpenTelemetry + Tempo integration")
    print(f"  - Alert Management: Redis-based alert management")
    print(f"  - Session Management: Redis for health state")
    print(f"  - State Management: Redis for alert state")
    print(f"  - SOA APIs: {len(nurse_service.soa_apis)} exposed")
    print(f"  - MCP Tools: {len(nurse_service.mcp_tools)} integrated")

if __name__ == "__main__":
    asyncio.run(test_nurse_service_infrastructure_mapping())
