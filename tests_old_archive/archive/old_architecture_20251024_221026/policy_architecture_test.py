#!/usr/bin/env python3
"""
Policy Architecture Test - Comprehensive test for policy infrastructure

Tests the complete 5-layer policy architecture:
1. PolicyProtocol (abstraction contracts)
2. Policy Adapters (OPA, Simple Rules)
3. PolicyAbstraction (infrastructure coordination)
4. PolicyCompositionService (infrastructure business logic)
5. PolicyService (agentic business logic)
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

from foundations.public_works_foundation.abstraction_contracts.policy_protocol import (
    PolicyContext, PolicyResult, PolicyDecision, PolicyType
)
from foundations.public_works_foundation.infrastructure_adapters.simple_rules_adapter import SimpleRulesAdapter
from foundations.public_works_foundation.infrastructure_adapters.opa_policy_adapter import OPAPolicyAdapter
from foundations.public_works_foundation.infrastructure_abstractions.policy_abstraction import PolicyAbstraction
from foundations.public_works_foundation.composition_services.policy_composition_service import PolicyCompositionService
from foundations.agentic_foundation.business_services.policy_service import PolicyService


async def test_policy_protocol():
    """Test PolicyProtocol contracts and data structures."""
    print("🧪 Testing PolicyProtocol...")
    
    # Test PolicyContext
    context = PolicyContext(
        user_id="test_user",
        tenant_id="test_tenant",
        agent_id="test_agent",
        resource="test_resource",
        action="read",
        environment="test",
        metadata={"test_key": "test_value"}
    )
    
    assert context.user_id == "test_user"
    assert context.tenant_id == "test_tenant"
    assert context.agent_id == "test_agent"
    assert context.resource == "test_resource"
    assert context.action == "read"
    assert context.environment == "test"
    assert context.metadata["test_key"] == "test_value"
    
    # Test PolicyResult
    result = PolicyResult(
        decision=PolicyDecision.ALLOW,
        policy_id="test_policy",
        policy_name="Test Policy",
        reason="Test reason",
        metadata={"test": "metadata"}
    )
    
    assert result.decision == PolicyDecision.ALLOW
    assert result.policy_id == "test_policy"
    assert result.policy_name == "Test Policy"
    assert result.reason == "Test reason"
    assert result.metadata["test"] == "metadata"
    
    print("✅ PolicyProtocol tests passed")


async def test_simple_rules_adapter():
    """Test SimpleRulesAdapter."""
    print("🧪 Testing SimpleRulesAdapter...")
    
    adapter = SimpleRulesAdapter()
    
    # Test health check
    health = await adapter.health_check()
    assert health["status"] == "healthy"
    assert health["adapter"] == "simple_rules"
    
    # Test policy evaluation
    context = PolicyContext(
        user_id="test_user",
        tenant_id="test_tenant",
        agent_id="test_agent",
        resource="test_resource",
        action="read",
        environment="production"
    )
    
    result = await adapter.evaluate_policy("access_control_basic", context)
    assert result.policy_id == "access_control_basic"
    assert result.decision in [PolicyDecision.ALLOW, PolicyDecision.DENY, PolicyDecision.WARN, PolicyDecision.UNKNOWN]
    
    # Test list policies
    policies = await adapter.list_policies()
    assert len(policies) > 0
    assert any(p["policy_id"] == "access_control_basic" for p in policies)
    
    print("✅ SimpleRulesAdapter tests passed")


async def test_opa_adapter():
    """Test OPAPolicyAdapter."""
    print("🧪 Testing OPAPolicyAdapter...")
    
    adapter = OPAPolicyAdapter()
    
    # Test health check
    health = await adapter.health_check()
    assert health["adapter"] == "opa"
    
    # Test policy evaluation
    context = PolicyContext(
        user_id="test_user",
        tenant_id="test_tenant",
        agent_id="test_agent",
        resource="test_resource",
        action="read",
        environment="production"
    )
    
    result = await adapter.evaluate_policy("test_policy", context)
    assert result.policy_id == "test_policy"
    assert result.decision in [PolicyDecision.ALLOW, PolicyDecision.DENY, PolicyDecision.WARN, PolicyDecision.UNKNOWN]
    
    print("✅ OPAPolicyAdapter tests passed")


async def test_policy_abstraction():
    """Test PolicyAbstraction."""
    print("🧪 Testing PolicyAbstraction...")
    
    # Test with simple rules adapter
    abstraction = PolicyAbstraction(adapter_type="simple_rules")
    
    # Test health check
    health = await abstraction.health_check()
    assert health["abstraction_layer"] == "policy_abstraction"
    assert health["adapter_type"] == "simple_rules"
    
    # Test policy evaluation
    context = PolicyContext(
        user_id="test_user",
        tenant_id="test_tenant",
        agent_id="test_agent",
        resource="test_resource",
        action="read",
        environment="production"
    )
    
    result = await abstraction.evaluate_policy("access_control_basic", context)
    assert result.policy_id == "access_control_basic"
    assert result.metadata["adapter_type"] == "simple_rules"
    assert result.metadata["abstraction_layer"] == "policy_abstraction"
    
    # Test adapter switching
    switch_result = await abstraction.switch_adapter("opa")
    assert switch_result == True
    assert abstraction.adapter_type == "opa"
    
    print("✅ PolicyAbstraction tests passed")


async def test_policy_composition_service():
    """Test PolicyCompositionService."""
    print("🧪 Testing PolicyCompositionService...")
    
    # Create abstraction and composition service
    abstraction = PolicyAbstraction(adapter_type="simple_rules")
    composition_service = PolicyCompositionService(abstraction)
    
    # Test health check
    health = await composition_service.health_check()
    assert health["service"] == "policy_composition_service"
    
    # Test policy orchestration
    context = PolicyContext(
        user_id="test_user",
        tenant_id="test_tenant",
        agent_id="test_agent",
        resource="test_resource",
        action="read",
        environment="production"
    )
    
    result = await composition_service.orchestrate_policy_evaluation(
        "access_control",
        context
    )
    assert result["workflow_type"] == "access_control"
    assert "final_decision" in result
    assert "policy_results" in result
    
    # Test policy chain evaluation
    chain_result = await composition_service.evaluate_policy_chain(
        ["access_control_basic", "agent_behavior_basic"],
        context
    )
    assert chain_result["success"] == True
    assert "final_decision" in chain_result
    assert "policy_results" in chain_result
    
    # Test policy metrics
    metrics = await composition_service.get_policy_metrics()
    assert metrics["success"] == True
    assert "policy_counts" in metrics
    assert "total_policies" in metrics
    
    print("✅ PolicyCompositionService tests passed")


async def test_policy_service():
    """Test PolicyService."""
    print("🧪 Testing PolicyService...")
    
    # Create dependencies
    abstraction = PolicyAbstraction(adapter_type="simple_rules")
    composition_service = PolicyCompositionService(abstraction)
    policy_service = PolicyService(abstraction, composition_service)
    
    # Test health check
    health = await policy_service.health_check()
    assert health["service"] == "policy_service"
    assert "enforcement_types" in health
    
    # Test policy enforcement
    context = PolicyContext(
        user_id="test_user",
        tenant_id="test_tenant",
        agent_id="test_agent",
        resource="test_resource",
        action="read",
        environment="production"
    )
    
    # Test LLM operations enforcement
    llm_result = await policy_service.enforce_agent_policies(
        "llm_operations",
        context
    )
    assert llm_result["operation_type"] == "llm_operations"
    assert "operation_allowed" in llm_result
    
    # Test MCP operations enforcement
    mcp_result = await policy_service.enforce_agent_policies(
        "mcp_operations",
        context
    )
    assert mcp_result["operation_type"] == "mcp_operations"
    assert "operation_allowed" in mcp_result
    
    # Test tool operations enforcement
    tool_result = await policy_service.enforce_agent_policies(
        "tool_operations",
        context
    )
    assert tool_result["operation_type"] == "tool_operations"
    assert "operation_allowed" in tool_result
    
    # Test agent behavior enforcement
    behavior_result = await policy_service.enforce_agent_policies(
        "agent_behavior",
        context
    )
    assert behavior_result["operation_type"] == "agent_behavior"
    assert "operation_allowed" in behavior_result
    
    # Test compliance check
    compliance_result = await policy_service.check_agent_compliance(
        "test_agent",
        context
    )
    assert compliance_result["agent_id"] == "test_agent"
    assert "is_compliant" in compliance_result
    
    # Test policy recommendations
    recommendations = await policy_service.get_agent_policy_recommendations(
        "test_agent",
        context
    )
    assert recommendations["agent_id"] == "test_agent"
    assert "recommended_policies" in recommendations
    
    print("✅ PolicyService tests passed")


async def test_integration():
    """Test end-to-end integration."""
    print("🧪 Testing end-to-end integration...")
    
    # Create complete policy infrastructure
    abstraction = PolicyAbstraction(adapter_type="simple_rules")
    composition_service = PolicyCompositionService(abstraction)
    policy_service = PolicyService(abstraction, composition_service)
    
    # Test complete workflow
    context = PolicyContext(
        user_id="integration_user",
        tenant_id="integration_tenant",
        agent_id="integration_agent",
        resource="integration_resource",
        action="write",
        environment="production",
        metadata={"integration_test": True}
    )
    
    # 1. Check agent compliance
    compliance = await policy_service.check_agent_compliance("integration_agent", context)
    print(f"   Compliance check: {compliance['is_compliant']}")
    
    # 2. Enforce policies for different operations
    operations = ["llm_operations", "mcp_operations", "tool_operations", "agent_behavior"]
    for operation in operations:
        result = await policy_service.enforce_agent_policies(operation, context)
        print(f"   {operation}: {'Allowed' if result.get('operation_allowed') else 'Denied'}")
    
    # 3. Get policy recommendations
    recommendations = await policy_service.get_agent_policy_recommendations("integration_agent", context)
    print(f"   Policy recommendations: {len(recommendations.get('recommended_policies', []))} policies")
    
    # 4. Test policy orchestration
    orchestration = await composition_service.orchestrate_policy_evaluation(
        "security_validation",
        context
    )
    print(f"   Security validation: {orchestration.get('final_decision', 'unknown')}")
    
    print("✅ End-to-end integration tests passed")


async def main():
    """Run all policy architecture tests."""
    print("🚀 Starting Policy Architecture Tests")
    print("=" * 50)
    
    try:
        await test_policy_protocol()
        await test_simple_rules_adapter()
        await test_opa_adapter()
        await test_policy_abstraction()
        await test_policy_composition_service()
        await test_policy_service()
        await test_integration()
        
        print("=" * 50)
        print("🎉 All Policy Architecture Tests Passed!")
        print(f"✅ Test completed at {datetime.utcnow().isoformat()}")
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Policy Architecture Tests Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

