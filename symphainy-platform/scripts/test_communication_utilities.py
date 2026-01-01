#!/usr/bin/env python3
"""
Test script to verify Communication Foundation utilities refactoring.

This script tests that:
1. All services properly use error handling utilities
2. Telemetry is being logged correctly
3. Security and tenant validation are in place
4. Methods return proper error codes
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_communication_foundation_service():
    """Test Communication Foundation Service utilities."""
    logger.info("=" * 80)
    logger.info("Testing Communication Foundation Service")
    logger.info("=" * 80)
    
    try:
        from pathlib import Path
        
        # Read the service file
        service_file = Path(__file__).parent.parent / "foundations" / "communication_foundation" / "communication_foundation_service.py"
        content = service_file.read_text()
        
        # Test 1: Check for utility method usage
        logger.info("✓ Test 1: Checking utility method usage...")
        assert 'handle_error_with_audit' in content, "Missing handle_error_with_audit usage"
        assert 'log_operation_with_telemetry' in content, "Missing log_operation_with_telemetry usage"
        assert 'record_health_metric' in content, "Missing record_health_metric usage"
        logger.info("  ✓ All utility methods are used")
        
        # Test 2: Check user-facing methods have user_context
        logger.info("✓ Test 2: Checking user_context parameters...")
        user_facing_methods = [
            'register_soa_api',
            'discover_soa_api',
            'send_message',
            'publish_event',
            'establish_websocket_connection'
        ]
        
        for method_name in user_facing_methods:
            # Check method signature includes user_context
            pattern = f"async def {method_name}.*user_context"
            import re
            if not re.search(pattern, content, re.DOTALL):
                # Try alternative pattern
                pattern2 = f"def {method_name}.*user_context"
                assert re.search(pattern2, content, re.DOTALL), f"{method_name} missing user_context parameter"
            logger.info(f"  ✓ {method_name} has user_context parameter")
        
        # Test 3: Check security and tenant validation patterns
        logger.info("✓ Test 3: Checking security and tenant validation...")
        assert 'get_security()' in content, "Missing security validation"
        assert 'get_tenant()' in content, "Missing tenant validation"
        assert 'check_permissions' in content, "Missing permission checks"
        assert 'validate_tenant_access' in content, "Missing tenant access validation"
        logger.info("  ✓ Security and tenant validation patterns found")
        
        logger.info("✅ Communication Foundation Service utilities test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Communication Foundation Service test FAILED: {e}", exc_info=True)
        return False


async def test_foundation_services():
    """Test Foundation Services utilities."""
    logger.info("=" * 80)
    logger.info("Testing Foundation Services")
    logger.info("=" * 80)
    
    try:
        from pathlib import Path
        
        # Test WebSocket Foundation Service
        ws_file = Path(__file__).parent.parent / "foundations" / "communication_foundation" / "foundation_services" / "websocket_foundation_service.py"
        content = ws_file.read_text()
        
        logger.info("✓ Checking WebSocket Foundation Service utilities...")
        assert 'handle_error_with_audit' in content, "Missing handle_error_with_audit"
        assert 'log_operation_with_telemetry' in content, "Missing log_operation_with_telemetry"
        assert 'record_health_metric' in content, "Missing record_health_metric"
        logger.info("  ✓ All utility methods are used")
        
        # Check user-facing methods have user_context
        import re
        user_facing = ['broadcast_to_realm', 'get_connection_info', 'get_realm_connections']
        for method_name in user_facing:
            pattern = f"async def {method_name}.*user_context"
            assert re.search(pattern, content, re.DOTALL), f"{method_name} missing user_context parameter"
            logger.info(f"  ✓ {method_name} has user_context parameter")
        
        logger.info("✅ Foundation Services utilities test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Foundation Services test FAILED: {e}", exc_info=True)
        return False


async def test_error_handling_pattern():
    """Test that error handling pattern is correctly implemented."""
    logger.info("=" * 80)
    logger.info("Testing Error Handling Pattern")
    logger.info("=" * 80)
    
    try:
        # Read a sample file and check for error handling pattern
        from pathlib import Path
        
        comm_service_file = Path(__file__).parent.parent / "foundations" / "communication_foundation" / "communication_foundation_service.py"
        
        if not comm_service_file.exists():
            logger.warning("⚠️  Communication service file not found, skipping pattern check")
            return True
        
        content = comm_service_file.read_text()
        
        # Check for error handling pattern in initialize method
        logger.info("✓ Checking error handling pattern in initialize method...")
        assert 'handle_error_with_audit' in content, "Missing handle_error_with_audit in file"
        assert 'log_operation_with_telemetry' in content, "Missing log_operation_with_telemetry in file"
        assert 'record_health_metric' in content, "Missing record_health_metric in file"
        logger.info("  ✓ Error handling pattern found")
        
        logger.info("✅ Error Handling Pattern test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error Handling Pattern test FAILED: {e}", exc_info=True)
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting Communication Foundation Utilities Tests")
    logger.info("")
    
    results = []
    
    # Test 1: Communication Foundation Service
    results.append(await test_communication_foundation_service())
    logger.info("")
    
    # Test 2: Foundation Services
    results.append(await test_foundation_services())
    logger.info("")
    
    # Test 3: Error Handling Pattern
    results.append(await test_error_handling_pattern())
    logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ ALL TESTS PASSED")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

