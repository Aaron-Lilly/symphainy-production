#!/usr/bin/env python3
"""
Test Script for Loki Integration

Quick test to verify Loki adapter and abstraction are working.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

async def test_loki_adapter():
    """Test Loki adapter directly."""
    print("🧪 Testing Loki Adapter...")
    
    try:
        from foundations.public_works_foundation.infrastructure_adapters.loki_adapter import LokiAdapter
        
        # Initialize adapter
        adapter = LokiAdapter(
            endpoint="http://localhost:3101",  # External port
            tenant_id="symphainy-platform"
        )
        
        # Test connection
        print("  📡 Testing connection...")
        connected = await adapter.connect()
        if connected:
            print("  ✅ Loki adapter connection successful!")
        else:
            print("  ⚠️ Loki adapter connection failed (Loki may not be running)")
            return False
        
        # Test push logs
        print("  📤 Testing log push...")
        from datetime import datetime
        test_logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "line": "Test log entry from integration test",
                "labels": {
                    "service_name": "test_service",
                    "level": "info"
                }
            }
        ]
        push_result = await adapter.push_logs(test_logs)
        if push_result:
            print("  ✅ Log push successful!")
        else:
            print("  ⚠️ Log push failed")
            return False
        
        # Test query logs
        print("  🔍 Testing log query...")
        query_result = await adapter.query_logs(
            query='{service_name="test_service"}',
            limit=10
        )
        if query_result.get("status") == "success":
            print(f"  ✅ Log query successful! Found {len(query_result.get('data', {}).get('result', []))} streams")
        else:
            print(f"  ⚠️ Log query failed: {query_result.get('error')}")
            return False
        
        await adapter.close()
        print("  ✅ Loki adapter test complete!")
        return True
        
    except Exception as e:
        print(f"  ❌ Loki adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_log_aggregation_abstraction():
    """Test Log Aggregation abstraction."""
    print("\n🧪 Testing Log Aggregation Abstraction...")
    
    try:
        from foundations.public_works_foundation.infrastructure_adapters.loki_adapter import LokiAdapter
        from foundations.public_works_foundation.infrastructure_abstractions.log_aggregation_abstraction import LogAggregationAbstraction
        from foundations.public_works_foundation.abstraction_contracts.log_aggregation_protocol import LogEntry, LogQuery
        from datetime import datetime
        
        # Create mock DI container
        class MockDIContainer:
            def get_logger(self, name):
                import logging
                return logging.getLogger(name)
        
        # Initialize adapter and abstraction
        adapter = LokiAdapter(
            endpoint="http://localhost:3101",
            tenant_id="symphainy-platform"
        )
        
        abstraction = LogAggregationAbstraction(
            loki_adapter=adapter,
            config_adapter=None,
            service_name="test_log_aggregation",
            di_container=MockDIContainer()
        )
        
        # Test push logs
        print("  📤 Testing abstraction log push...")
        test_entries = [
            LogEntry(
                line="Test log from abstraction",
                timestamp=datetime.utcnow(),
                service_name="test_service",
                level="info"
            )
        ]
        push_result = await abstraction.push_logs(test_entries)
        if push_result:
            print("  ✅ Abstraction log push successful!")
        else:
            print("  ⚠️ Abstraction log push failed")
            return False
        
        # Test query logs
        print("  🔍 Testing abstraction log query...")
        query = LogQuery(
            query='{service_name="test_service"}',
            limit=10
        )
        log_entries = await abstraction.query_logs(query)
        print(f"  ✅ Abstraction log query successful! Found {len(log_entries)} entries")
        
        # Test search logs
        print("  🔎 Testing abstraction log search...")
        search_result = await abstraction.search_logs({
            "service_name": "test_service",
            "level": "info",
            "time_range": {"hours": 1}
        })
        if search_result.get("status") == "success":
            print(f"  ✅ Abstraction log search successful! Found {search_result.get('count', 0)} entries")
        else:
            print(f"  ⚠️ Abstraction log search failed: {search_result.get('error')}")
        
        # Test get metrics
        print("  📊 Testing abstraction log metrics...")
        metrics = await abstraction.get_log_metrics({"hours": 1})
        if metrics.get("status") == "success":
            print(f"  ✅ Abstraction log metrics successful! Volume: {metrics.get('volume', 0)}")
        else:
            print(f"  ⚠️ Abstraction log metrics failed: {metrics.get('error')}")
        
        await adapter.close()
        print("  ✅ Log Aggregation abstraction test complete!")
        return True
        
    except Exception as e:
        print(f"  ❌ Log Aggregation abstraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Loki Integration Tests\n")
    
    results = []
    
    # Test 1: Loki Adapter
    results.append(await test_loki_adapter())
    
    # Test 2: Log Aggregation Abstraction
    results.append(await test_log_aggregation_abstraction())
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary:")
    print(f"  ✅ Passed: {sum(results)}/{len(results)}")
    print(f"  ❌ Failed: {len(results) - sum(results)}/{len(results)}")
    print("="*60)
    
    if all(results):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

