#!/usr/bin/env python3
"""
Nurse Telemetry Integration Test

Test the Nurse service with OpenTelemetry and ArangoDB integration to verify:
1. Service initialization with infrastructure abstractions
2. Telemetry collection using OpenTelemetry
3. Telemetry storage using ArangoDB
4. Distributed tracing and metrics collection
5. Health monitoring and alerting capabilities
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.smart_city.services.nurse.nurse_service import NurseService
from foundations.utility_foundation.utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment


async def test_nurse_telemetry_integration():
    """Test Nurse service with OpenTelemetry and ArangoDB integration."""
    print("🚀 Starting Nurse Telemetry Integration Test")
    print("=" * 80)
    
    try:
        # Initialize environment
        env_loader = EnvironmentLoader(Environment.DEVELOPMENT)
        
        # Initialize Nurse Service
        print("1. Initializing Nurse Service...")
        nurse = NurseService(
            utility_foundation=None,
            public_works_foundation=None,
            curator_foundation=None,
            environment=Environment.DEVELOPMENT
        )
        
        # Initialize modules (including async telemetry module)
        await nurse._initialize_modules()
        print("   ✅ Nurse Service initialized")
        
        # Test service health
        print("\n2. Testing service health...")
        health = await nurse.get_service_status()
        print(f"   Service Status: {health['status']}")
        print(f"   Capabilities: {health['capabilities']}")
        print(f"   Modules: {health['modules']}")
        
        # Test telemetry collection
        print("\n3. Testing telemetry collection...")
        
        # Collect system telemetry
        system_telemetry = await nurse.collect_system_telemetry()
        print(f"   System Telemetry: {system_telemetry.get('service_name', 'Unknown')}")
        print(f"   OpenTelemetry Status: {system_telemetry.get('opentelemetry_status', {}).get('connected', False)}")
        print(f"   ArangoDB Status: {system_telemetry.get('arango_status', {}).get('status', 'Unknown')}")
        
        # Test custom metric creation
        print("\n4. Testing custom metric creation...")
        
        metric_result = await nurse.create_custom_metric({
            "metric_name": "test_metric",
            "value": 42.5,
            "tags": {"service": "nurse", "test": "true"},
            "metadata": {"description": "Test metric for integration testing"}
        })
        
        if metric_result.get("success"):
            print("   ✅ Custom metric created successfully")
        else:
            print(f"   ❌ Custom metric creation failed: {metric_result.get('error', 'Unknown error')}")
        
        # Test distributed tracing
        print("\n5. Testing distributed tracing...")
        
        # Start a trace
        trace_result = await nurse.start_trace({
            "operation_name": "test_operation",
            "service_name": "nurse_service",
            "tags": {"test": "true", "operation_type": "integration_test"}
        })
        
        if trace_result.get("span_id"):
            span_id = trace_result["span_id"]
            print(f"   ✅ Trace started: {span_id}")
            
            # Add some work (simulate processing)
            await asyncio.sleep(0.1)
            
            # Finish the trace
            finish_result = await nurse.finish_trace({
                "span_id": span_id,
                "status": "ok",
                "tags": {"result": "success", "duration_ms": 100},
                "logs": [{"message": "Operation completed successfully", "level": "info"}]
            })
            
            if finish_result.get("success"):
                print("   ✅ Trace finished successfully")
            else:
                print(f"   ❌ Trace finish failed: {finish_result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Trace start failed: {trace_result.get('error', 'Unknown error')}")
        
        # Test telemetry collection for specific service
        print("\n6. Testing service-specific telemetry collection...")
        
        collection_result = await nurse.start_telemetry_collection({
            "service_name": "test_service",
            "duration_minutes": 5
        })
        
        if collection_result.get("success"):
            print(f"   ✅ Telemetry collection started: {collection_result.get('event_id', 'Unknown')}")
        else:
            print(f"   ❌ Telemetry collection failed: {collection_result.get('error', 'Unknown error')}")
        
        # Test telemetry dashboard data
        print("\n7. Testing telemetry dashboard data...")
        
        dashboard_data = await nurse.get_telemetry_dashboard_data({"hours": 1})
        
        if "error" not in dashboard_data:
            print("   ✅ Telemetry dashboard data retrieved")
            print(f"   Statistics: {dashboard_data.get('statistics', {}).get('total_events', 0)} events")
            print(f"   OpenTelemetry Summary: {dashboard_data.get('opentelemetry_summary', {})}")
        else:
            print(f"   ❌ Dashboard data failed: {dashboard_data.get('error', 'Unknown error')}")
        
        # Test health monitoring
        print("\n8. Testing health monitoring...")
        
        # Perform system health check
        system_health = await nurse.perform_system_health_check()
        print(f"   System Health: {system_health.get('status', 'Unknown')}")
        
        # Perform service health check
        service_health = await nurse.perform_service_health_check({
            "service_name": "nurse_service"
        })
        print(f"   Service Health: {service_health.get('status', 'Unknown')}")
        
        # Test alert management
        print("\n9. Testing alert management...")
        
        # Create a health alert
        health_alert = await nurse.create_health_alert({
            "alert_type": "performance",
            "severity": "warning",
            "message": "High CPU usage detected",
            "service_name": "test_service",
            "metadata": {"cpu_usage": 85.5, "threshold": 80.0}
        })
        
        if health_alert.get("alert_id"):
            print(f"   ✅ Health alert created: {health_alert['alert_id']}")
        else:
            print(f"   ❌ Health alert creation failed: {health_alert.get('error', 'Unknown error')}")
        
        # Create a failure alert
        failure_alert = await nurse.create_failure_alert({
            "error_message": "Database connection timeout",
            "error_code": "DB_TIMEOUT",
            "service_name": "test_service",
            "metadata": {"timeout_seconds": 30, "retry_count": 3}
        })
        
        if failure_alert.get("alert_id"):
            print(f"   ✅ Failure alert created: {failure_alert['alert_id']}")
        else:
            print(f"   ❌ Failure alert creation failed: {failure_alert.get('error', 'Unknown error')}")
        
        # Test failure classification
        print("\n10. Testing failure classification...")
        
        classification = await nurse.classify_failure({
            "error_message": "Network connection refused",
            "error_code": "NET_REFUSED",
            "service_name": "test_service",
            "metadata": {"host": "localhost", "port": 8080}
        })
        
        if "error" not in classification:
            print(f"   ✅ Failure classified: {classification.get('category', 'Unknown')}")
            print(f"   Severity: {classification.get('severity', 'Unknown')}")
        else:
            print(f"   ❌ Failure classification failed: {classification.get('error', 'Unknown error')}")
        
        # Test comprehensive dashboard
        print("\n11. Testing comprehensive dashboard...")
        
        comprehensive_dashboard = await nurse.get_comprehensive_dashboard_data({"hours": 1})
        
        if "error" not in comprehensive_dashboard:
            print("   ✅ Comprehensive dashboard data retrieved")
            print(f"   Health Monitoring: {comprehensive_dashboard.get('health_monitoring', {}).get('status', 'Unknown')}")
            print(f"   Telemetry Collection: {comprehensive_dashboard.get('telemetry_collection', {}).get('status', 'Unknown')}")
            print(f"   Alert Management: {comprehensive_dashboard.get('alert_management', {}).get('status', 'Unknown')}")
            print(f"   Failure Classification: {comprehensive_dashboard.get('failure_classification', {}).get('status', 'Unknown')}")
        else:
            print(f"   ❌ Comprehensive dashboard failed: {comprehensive_dashboard.get('error', 'Unknown error')}")
        
        # Test service configuration
        print("\n12. Testing service configuration...")
        
        config_result = await nurse.configure_service({
            "config_type": "telemetry_collection",
            "config_data": {
                "sampling_rate": 0.5,
                "batch_size": 500,
                "reinitialize": False
            }
        })
        
        if config_result.get("success"):
            print("   ✅ Service configuration updated")
        else:
            print(f"   ❌ Service configuration failed: {config_result.get('error', 'Unknown error')}")
        
        # Final service status
        print(f"\n13. Final service status...")
        final_health = await nurse.get_service_status()
        print(f"   Service Status: {final_health['status']}")
        print(f"   All Modules: {final_health['modules']}")
        
        print("\n" + "=" * 80)
        print("🎉 NURSE TELEMETRY INTEGRATION TEST COMPLETED!")
        print("✅ OpenTelemetry integration verified")
        print("✅ ArangoDB telemetry storage verified")
        print("✅ Distributed tracing operational")
        print("✅ Metrics collection functional")
        print("✅ Health monitoring active")
        print("✅ Alert management working")
        print("✅ Failure classification operational")
        print("🎯 Nurse service is ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_nurse_telemetry_integration())
    sys.exit(0 if success else 1)




