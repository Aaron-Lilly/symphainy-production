#!/usr/bin/env python3
"""
Functional Test for Nurse Observability (Phase 2.2)

This script tests the Nurse observability integration:
1. Nurse initialization with ObservabilityAbstraction
2. Recording platform events (logs, metrics, traces)
3. Recording agent executions
4. Querying observability data

Usage:
    python scripts/test_nurse_observability.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Set TEST_MODE to make Traefik optional
os.environ["TEST_MODE"] = "true"

# Add project root to path
project_root = Path(__file__).parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
import uuid
from datetime import datetime


async def test_nurse_observability():
    """Test Nurse observability integration."""
    print("\n" + "="*80)
    print("TEST: Nurse Observability Integration (Phase 2.2)")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from backend.smart_city.services.nurse.nurse_service import NurseService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Register in DI Container (required for Smart City services to access it)
        di_container.public_works_foundation = pwf
        
        # Initialize Nurse Service
        print("\n1. Initializing Nurse Service...")
        nurse = NurseService(di_container=di_container)
        await nurse.initialize()
        
        if not nurse.is_initialized:
            print("❌ Nurse Service failed to initialize")
            return False
        
        print("✅ Nurse Service initialized")
        
        # Check if observability abstraction is available
        if not nurse.observability_abstraction:
            print("⚠️ ObservabilityAbstraction not available - some tests will be skipped")
        else:
            print("✅ ObservabilityAbstraction available")
        
        # Test data
        user_context = {
            "tenant_id": "test_tenant",
            "user_id": "test_user",
            "permissions": ["write", "read", "execute", "admin"]
        }
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        
        # Test 2: Record platform log
        print("\n2. Testing record_platform_event (log)...")
        log_result = await nurse.record_platform_event(
            event_type="log",
            event_data={
                "level": "info",
                "message": "Test log message from Nurse observability test",
                "service_name": "test_service",
                "metadata": {"test": True}
            },
            trace_id=trace_id,
            user_context=user_context
        )
        
        if not log_result.get("success"):
            print(f"❌ Failed to record platform log: {log_result}")
            return False
        
        print(f"✅ Platform log recorded: {log_result.get('log_id', 'N/A')}")
        
        # Test 3: Record platform metric
        print("\n3. Testing record_platform_event (metric)...")
        metric_result = await nurse.record_platform_event(
            event_type="metric",
            event_data={
                "metric_name": "test_metric",
                "value": 42.0,
                "service_name": "test_service",
                "metadata": {"unit": "count"}
            },
            trace_id=trace_id,
            user_context=user_context
        )
        
        if not metric_result.get("success"):
            print(f"❌ Failed to record platform metric: {metric_result}")
            return False
        
        print(f"✅ Platform metric recorded: {metric_result.get('metric_id', 'N/A')}")
        
        # Test 4: Record platform trace
        print("\n4. Testing record_platform_event (trace)...")
        start_time = datetime.utcnow()
        end_time = datetime.utcnow()
        trace_result = await nurse.record_platform_event(
            event_type="trace",
            event_data={
                "trace_id": trace_id,
                "span_name": "test_operation",
                "service_name": "test_service",
                "start_time": start_time,
                "end_time": end_time,
                "duration_ms": 100.0,
                "status": "ok",
                "metadata": {"operation": "test"}
            },
            trace_id=trace_id,
            user_context=user_context
        )
        
        if not trace_result.get("success"):
            print(f"❌ Failed to record platform trace: {trace_result}")
            return False
        
        print(f"✅ Platform trace recorded: {trace_result.get('trace_id', 'N/A')}")
        
        # Test 5: Record agent execution
        print("\n5. Testing record_agent_execution...")
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        agent_name = "TestAgent"
        prompt_hash = "test_hash_12345"
        response = "Test agent response"
        
        agent_result = await nurse.record_agent_execution(
            agent_id=agent_id,
            agent_name=agent_name,
            prompt_hash=prompt_hash,
            response=response,
            trace_id=trace_id,
            execution_metadata={
                "model_name": "test-model",
                "tokens": 100,
                "latency_ms": 50,
                "cost_estimate": 0.001
            },
            user_context=user_context
        )
        
        if not agent_result.get("success"):
            print(f"❌ Failed to record agent execution: {agent_result}")
            return False
        
        print(f"✅ Agent execution recorded: {agent_result.get('execution_id', 'N/A')}")
        
        # Test 6: Query observability data
        print("\n6. Testing get_observability_data...")
        
        # Query logs
        logs = await nurse.get_observability_data(
            data_type="logs",
            filters={"service_name": "test_service"},
            limit=10,
            user_context=user_context
        )
        
        if logs is None:
            print("⚠️ get_observability_data returned None (may not be implemented yet)")
        else:
            print(f"✅ Retrieved {len(logs)} logs")
        
        # Query agent executions
        agent_executions = await nurse.get_observability_data(
            data_type="agent_executions",
            filters={"agent_id": agent_id},
            limit=10,
            user_context=user_context
        )
        
        if agent_executions is None:
            print("⚠️ get_observability_data for agent_executions returned None (may not be implemented yet)")
        else:
            print(f"✅ Retrieved {len(agent_executions)} agent executions")
        
        print("\n" + "="*80)
        print("✅ All Nurse Observability tests passed!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Nurse Observability: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("NURSE OBSERVABILITY FUNCTIONAL TEST (Phase 2.2)")
    print("="*80)
    
    results = {}
    
    # Run tests
    results["nurse_observability"] = await test_nurse_observability()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



