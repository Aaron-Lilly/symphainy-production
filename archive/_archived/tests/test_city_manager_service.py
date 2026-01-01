#!/usr/bin/env python3
"""
Test City Manager Service
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
from foundations.utility_foundation.utilities.logging.logging_service import SmartCityLoggingService
from config.environment_loader import EnvironmentLoader

async def test_city_manager_service():
    """Test City Manager service functionality."""
    print("🏛️ Testing City Manager Service...")
    
    # Initialize logging
    logging_service = SmartCityLoggingService("test_city_manager")
    logger = logging_service
    
    try:
        # Initialize environment loader
        env_loader = EnvironmentLoader()
        
        # Create City Manager service
        city_manager = CityManagerService(
            utility_foundation=None,
            public_works_foundation=None
        )
        
        # Initialize the service
        print("  📋 Initializing City Manager service...")
        await city_manager.initialize()
        print("  ✅ City Manager service initialized successfully")
        
        # Test service health
        print("  🏥 Testing service health...")
        health_status = await city_manager.get_service_health()
        print(f"  📊 Health Status: {health_status}")
        
        # Test policy management
        print("  📜 Testing policy management...")
        policy_result = await city_manager.create_city_policy({
            "id": "test_policy_001",
            "policy_type": "data_governance",
            "policy_name": "test_policy",
            "policy_content": {
                "description": "Test data governance policy",
                "rules": ["encrypt_sensitive_data", "audit_access"],
                "enforcement_level": "mandatory"
            }
        })
        print(f"  📋 Policy Management Result: {policy_result}")
        
        # Test resource allocation
        print("  💰 Testing resource allocation...")
        allocation_result = await city_manager.allocate_city_resources({
            "resources": {
                "cpu": 1000,
                "memory": 2048,
                "storage": 100
            },
            "allocation_type": "compute",
            "priority": "high",
            "requester": "test_service"
        })
        print(f"  💸 Resource Allocation Result: {allocation_result}")
        
        # Test governance enforcement
        print("  ⚖️ Testing governance enforcement...")
        governance_result = await city_manager.check_city_compliance(
            "test_component", 
            "data_governance",
            {"data_type": "sensitive", "encrypted": True}
        )
        print(f"  🏛️ Governance Enforcement Result: {governance_result}")
        
        # Test strategic coordination
        print("  🎯 Testing strategic coordination...")
        coordination_result = await city_manager.coordinate_city_roles({
            "coordination_type": "service_integration",
            "participating_services": ["security_guard", "traffic_cop", "post_office"],
            "coordination_goal": "end_to_end_workflow"
        })
        print(f"  🤝 Strategic Coordination Result: {coordination_result}")
        
        # Test city health monitoring
        print("  🏥 Testing city health monitoring...")
        health_result = await city_manager.check_city_health()
        print(f"  📊 City Health Result: {health_result}")
        
        # Test emergency coordination
        print("  🚨 Testing emergency coordination...")
        emergency_result = await city_manager.detect_emergency({
            "emergency_type": "service_failure",
            "affected_services": ["traffic_cop"],
            "severity": "high",
            "escalation_required": True
        })
        print(f"  🆘 Emergency Coordination Result: {emergency_result}")
        
        print("  ✅ All City Manager tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing City Manager service: {e}")
        logger.error(f"Error testing City Manager service: {e}")
        return False

async def main():
    """Main test function."""
    print("🏛️ City Manager Service Test Suite")
    print("=" * 50)
    
    success = await test_city_manager_service()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
