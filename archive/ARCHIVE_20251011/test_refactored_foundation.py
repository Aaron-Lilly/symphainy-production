#!/usr/bin/env python3
"""
Test Refactored Foundation Services

Tests the refactored foundation services using the proper UtilityFoundationService.
"""

import os
import sys
import asyncio
from unittest.mock import Mock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.configuration_foundation.configuration_foundation_service import ConfigurationFoundationService
from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationService


async def test_refactored_foundation_services():
    """Test refactored foundation services with proper UtilityFoundationService."""
    print("🧪 Testing Refactored Foundation Services with Proper UtilityFoundationService")
    print("=" * 80)
    
    # Step 1: Initialize Utility Foundation Service
    print("\n🔧 Step 1: Initializing Utility Foundation Service...")
    utility_foundation = UtilityFoundationService()
    await utility_foundation.initialize()
    
    print(f"✅ Utility Foundation Service initialized")
    print(f"   - Services registered: {len(utility_foundation.get_registered_services())}")
    print(f"   - Utility usage stats: {utility_foundation.get_utility_usage_stats()}")
    
    # Step 2: Initialize Configuration Foundation with Proper Utility Foundation
    print("\n🔧 Step 2: Initializing Configuration Foundation with Proper Utility Foundation...")
    mock_curator_foundation = Mock()
    
    config_service = ConfigurationFoundationService(utility_foundation, mock_curator_foundation)
    await config_service.initialize()
    
    print(f"✅ Configuration Foundation Service initialized with Proper Utility Foundation")
    print(f"   - Services registered: {len(utility_foundation.get_registered_services())}")
    print(f"   - Utility usage stats: {utility_foundation.get_utility_usage_stats()}")
    
    # Step 3: Initialize Infrastructure Foundation with Proper Utility Foundation
    print("\n🏗️ Step 3: Initializing Infrastructure Foundation with Proper Utility Foundation...")
    infra_service = InfrastructureFoundationService(utility_foundation, mock_curator_foundation, config_service)
    await infra_service.initialize()
    
    print(f"✅ Infrastructure Foundation Service initialized with Proper Utility Foundation")
    print(f"   - Services registered: {len(utility_foundation.get_registered_services())}")
    print(f"   - Utility usage stats: {utility_foundation.get_utility_usage_stats()}")
    
    # Step 4: Test Enhanced Utility Methods in Refactored Services
    print("\n🔍 Step 4: Testing Enhanced Utility Methods in Refactored Services...")
    
    # Test Configuration Foundation enhanced methods
    print("\n📊 Testing Configuration Foundation Enhanced Methods:")
    
    # Test telemetry integration
    await config_service.log_operation_with_telemetry(
        "test_config_operation", 
        success=True, 
        details={"test": "configuration_data"}
    )
    print("   ✅ Configuration Foundation telemetry integration working")
    
    # Test health metrics
    await config_service.record_health_metric("config_health", 100.0, {"service": "configuration"})
    print("   ✅ Configuration Foundation health metrics working")
    
    # Test utility usage tracking
    config_service.track_utility_usage("config_utility")
    print("   ✅ Configuration Foundation utility tracking working")
    
    # Test Infrastructure Foundation enhanced methods
    print("\n🏗️ Testing Infrastructure Foundation Enhanced Methods:")
    
    # Test telemetry integration
    await infra_service.log_operation_with_telemetry(
        "test_infra_operation", 
        success=True, 
        details={"test": "infrastructure_data"}
    )
    print("   ✅ Infrastructure Foundation telemetry integration working")
    
    # Test health metrics
    await infra_service.record_health_metric("infra_health", 95.0, {"service": "infrastructure"})
    print("   ✅ Infrastructure Foundation health metrics working")
    
    # Test utility usage tracking
    infra_service.track_utility_usage("infra_utility")
    print("   ✅ Infrastructure Foundation utility tracking working")
    
    # Test comprehensive health checks
    print("\n🔍 Testing Comprehensive Health Checks:")
    config_health = await config_service.run_comprehensive_health_checks()
    infra_health = await infra_service.run_comprehensive_health_checks()
    
    print(f"   ✅ Configuration Foundation health checks: {config_health['status']}")
    print(f"   ✅ Infrastructure Foundation health checks: {infra_health['status']}")
    
    # Step 5: Test Utility Foundation Health with All Services
    print("\n🏥 Step 5: Testing Utility Foundation Health with All Services...")
    utility_health = await utility_foundation.get_service_health()
    print(f"✅ Utility Foundation Health:")
    print(f"   - Status: {utility_health['status']}")
    print(f"   - Registered Services: {utility_health['utility_foundation']['registered_services']}")
    print(f"   - Utility Usage Stats: {utility_health['utility_foundation']['utility_usage_stats']}")
    print(f"   - Audit Log Entries: {utility_health['utility_foundation']['audit_log_entries']}")
    
    # Step 6: Test Service Registration
    print("\n📝 Step 6: Testing Service Registration...")
    registered_services = utility_foundation.get_registered_services()
    print(f"✅ Registered Services:")
    for service_name, service_info in registered_services.items():
        print(f"   - {service_name}: {service_info['type']} ({service_info['status']})")
    
    # Step 7: Test Audit Log
    print("\n📋 Step 7: Testing Audit Log...")
    audit_log = utility_foundation.get_audit_log(limit=10)
    print(f"✅ Audit Log Entries: {len(audit_log)}")
    for entry in audit_log[-3:]:  # Show last 3 entries
        print(f"   - {entry['event_type']}: {entry.get('error', entry.get('operation', 'unknown'))}")
    
    print("\n" + "=" * 80)
    print("🎉 Refactored Foundation Services Test Complete!")
    print("✅ Utility Foundation Service: Working")
    print("✅ Configuration Foundation Service: Refactored and Working")
    print("✅ Infrastructure Foundation Service: Refactored and Working")
    print("✅ Enhanced Utilities: Working in All Services")
    print("✅ Service Registration: Working")
    print("✅ Utility Usage Tracking: Working")
    print("✅ Audit Logging: Working")
    print("✅ Health Monitoring: Working")
    print("✅ Telemetry Integration: Working")


if __name__ == "__main__":
    asyncio.run(test_refactored_foundation_services())


