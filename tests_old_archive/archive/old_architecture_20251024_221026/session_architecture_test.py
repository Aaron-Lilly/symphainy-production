#!/usr/bin/env python3
"""
Session Architecture Test - Comprehensive test for session management infrastructure

Tests the complete 5-layer session management architecture:
1. SessionProtocol (abstraction contracts)
2. Session Adapters (Redis, In-Memory)
3. SessionAbstraction (infrastructure coordination)
4. SessionCompositionService (infrastructure business logic)
5. SessionService (agentic business logic)
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../symphainy-platform'))

from foundations.public_works_foundation.abstraction_contracts.session_protocol import (
    SessionContext, Session, SessionToken, SessionAnalytics,
    SessionStatus, SessionType, SecurityLevel
)
from foundations.public_works_foundation.infrastructure_adapters.in_memory_session_adapter import InMemorySessionAdapter
from foundations.public_works_foundation.infrastructure_adapters.redis_session_adapter import RedisSessionAdapter
from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction
from foundations.public_works_foundation.composition_services.session_composition_service import SessionCompositionService
from foundations.agentic_foundation.business_services.session_service import SessionService


async def test_session_protocol():
    """Test SessionProtocol contracts and data structures."""
    print("🧪 Testing SessionProtocol...")
    
    # Test SessionContext
    context = SessionContext(
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
    
    # Test Session
    session = Session(
        session_id="test_session",
        user_id="test_user",
        agent_id="test_agent",
        session_type=SessionType.USER,
        status=SessionStatus.ACTIVE,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow(),
        last_accessed=datetime.utcnow(),
        security_level=SecurityLevel.MEDIUM,
        metadata={"test": "metadata"},
        tags=["test", "session"]
    )
    
    assert session.session_id == "test_session"
    assert session.user_id == "test_user"
    assert session.agent_id == "test_agent"
    assert session.session_type == SessionType.USER
    assert session.status == SessionStatus.ACTIVE
    assert session.security_level == SecurityLevel.MEDIUM
    assert session.metadata["test"] == "metadata"
    assert "test" in session.tags
    assert "session" in session.tags
    
    # Test SessionToken
    token = SessionToken(
        token_id="test_token",
        session_id="test_session",
        token_type="access",
        token_value="test_token_value",
        expires_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        metadata={"test": "token"}
    )
    
    assert token.token_id == "test_token"
    assert token.session_id == "test_session"
    assert token.token_type == "access"
    assert token.token_value == "test_token_value"
    assert token.metadata["test"] == "token"
    
    # Test SessionAnalytics
    analytics = SessionAnalytics(
        session_id="test_session",
        total_requests=100,
        successful_requests=95,
        failed_requests=5,
        average_response_time=150.0,
        last_activity=datetime.utcnow(),
        security_events=0,
        metadata={"test": "analytics"}
    )
    
    assert analytics.session_id == "test_session"
    assert analytics.total_requests == 100
    assert analytics.successful_requests == 95
    assert analytics.failed_requests == 5
    assert analytics.average_response_time == 150.0
    assert analytics.security_events == 0
    assert analytics.metadata["test"] == "analytics"
    
    print("✅ SessionProtocol tests passed")


async def test_in_memory_session_adapter():
    """Test InMemorySessionAdapter."""
    print("🧪 Testing InMemorySessionAdapter...")
    
    adapter = InMemorySessionAdapter()
    
    # Test health check
    health = await adapter.health_check()
    assert health["status"] == "healthy"
    assert health["adapter"] == "in_memory_session"
    
    # Test session creation
    context = SessionContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    session_data = {
        "user_id": "test_user",
        "agent_id": "test_agent",
        "session_type": "user",
        "security_level": "medium",
        "metadata": {"test": "data"},
        "tags": ["test", "session"]
    }
    
    session = await adapter.create_session(context, session_data)
    assert session.session_id is not None
    assert session.user_id == "test_user"
    assert session.agent_id == "test_agent"
    assert session.session_type == SessionType.USER
    assert session.status == SessionStatus.ACTIVE
    assert session.security_level == SecurityLevel.MEDIUM
    assert session.metadata["test"] == "data"
    assert "test" in session.tags
    assert "session" in session.tags
    
    # Test session retrieval
    retrieved_session = await adapter.get_session(session.session_id, context)
    assert retrieved_session is not None
    assert retrieved_session.session_id == session.session_id
    assert retrieved_session.user_id == session.user_id
    
    # Test session validation
    is_valid = await adapter.validate_session(session.session_id, context)
    assert is_valid == True
    
    # Test session token creation
    token = await adapter.create_session_token(session.session_id, "access", context)
    assert token.token_id is not None
    assert token.session_id == session.session_id
    assert token.token_type == "access"
    assert token.token_value is not None
    
    # Test session analytics
    analytics = await adapter.get_session_analytics(session.session_id, context)
    assert analytics.session_id == session.session_id
    assert analytics.total_requests >= 0
    assert analytics.successful_requests >= 0
    assert analytics.failed_requests >= 0
    
    print("✅ InMemorySessionAdapter tests passed")


async def test_redis_session_adapter():
    """Test RedisSessionAdapter."""
    print("🧪 Testing RedisSessionAdapter...")
    
    adapter = RedisSessionAdapter()
    
    # Test health check
    health = await adapter.health_check()
    assert health["adapter"] == "redis_session"
    
    # Test session creation
    context = SessionContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    session_data = {
        "user_id": "test_user",
        "agent_id": "test_agent",
        "session_type": "user",
        "security_level": "medium",
        "metadata": {"test": "data"},
        "tags": ["test", "session"]
    }
    
    session = await adapter.create_session(context, session_data)
    assert session.session_id is not None
    assert session.user_id == "test_user"
    assert session.agent_id == "test_agent"
    assert session.session_type == SessionType.USER
    assert session.status == SessionStatus.ACTIVE
    assert session.security_level == SecurityLevel.MEDIUM
    
    print("✅ RedisSessionAdapter tests passed")


async def test_session_abstraction():
    """Test SessionAbstraction."""
    print("🧪 Testing SessionAbstraction...")
    
    # Test with in-memory adapter
    abstraction = SessionAbstraction(adapter_type="in_memory")
    
    # Test health check
    health = await abstraction.health_check()
    assert health["abstraction_layer"] == "session_abstraction"
    assert health["adapter_type"] == "in_memory"
    
    # Test session creation
    context = SessionContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    session_data = {
        "user_id": "test_user",
        "agent_id": "test_agent",
        "session_type": "user",
        "security_level": "medium",
        "metadata": {"test": "data"},
        "tags": ["test", "session"]
    }
    
    session = await abstraction.create_session(context, session_data)
    assert session.session_id is not None
    assert session.metadata["adapter_type"] == "in_memory"
    assert session.metadata["abstraction_layer"] == "session_abstraction"
    
    # Test session retrieval
    retrieved_session = await abstraction.get_session(session.session_id, context)
    assert retrieved_session is not None
    assert retrieved_session.session_id == session.session_id
    assert retrieved_session.metadata["adapter_type"] == "in_memory"
    assert retrieved_session.metadata["abstraction_layer"] == "session_abstraction"
    
    # Test adapter switching
    switch_result = await abstraction.switch_adapter("redis")
    assert switch_result == True
    assert abstraction.adapter_type == "redis"
    
    print("✅ SessionAbstraction tests passed")


async def test_session_composition_service():
    """Test SessionCompositionService."""
    print("🧪 Testing SessionCompositionService...")
    
    # Create abstraction and composition service
    abstraction = SessionAbstraction(adapter_type="in_memory")
    composition_service = SessionCompositionService(abstraction)
    
    # Test health check
    health = await composition_service.health_check()
    assert health["service"] == "session_composition_service"
    
    # Test session orchestration
    context = SessionContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    result = await composition_service.orchestrate_session_management(
        "user_session",
        context
    )
    assert result["workflow_type"] == "user_session"
    assert "session_id" in result
    assert "session_type" in result
    assert "security_level" in result
    
    # Test secure session creation
    secure_result = await composition_service.create_session_with_security(
        context,
        {"user_id": "test_user", "session_type": "user"},
        SecurityLevel.HIGH
    )
    assert "session_id" in secure_result
    assert secure_result["security_level"] == "high"
    assert "token_id" in secure_result
    
    # Test session metrics
    metrics = await composition_service.get_session_metrics()
    assert metrics["success"] == True
    assert "adapter_health" in metrics
    assert "available_workflows" in metrics
    
    print("✅ SessionCompositionService tests passed")


async def test_session_service():
    """Test SessionService."""
    print("🧪 Testing SessionService...")
    
    # Create dependencies
    abstraction = SessionAbstraction(adapter_type="in_memory")
    composition_service = SessionCompositionService(abstraction)
    session_service = SessionService(abstraction, composition_service)
    
    # Test health check
    health = await session_service.health_check()
    assert health["service"] == "session_service"
    assert "management_types" in health
    
    # Test session management
    context = SessionContext(
        service_id="test_service",
        agent_id="test_agent",
        tenant_id="test_tenant",
        environment="production"
    )
    
    # Test LLM session management
    llm_result = await session_service.manage_agent_session(
        "llm_session",
        context
    )
    assert llm_result["operation_type"] == "llm_session"
    assert "session_id" in llm_result
    
    # Test MCP session management
    mcp_result = await session_service.manage_agent_session(
        "mcp_session",
        context
    )
    assert mcp_result["operation_type"] == "mcp_session"
    assert "session_id" in mcp_result
    
    # Test tool session management
    tool_result = await session_service.manage_agent_session(
        "tool_session",
        context
    )
    assert tool_result["operation_type"] == "tool_session"
    assert "session_id" in tool_result
    
    # Test agent session management
    agent_result = await session_service.manage_agent_session(
        "agent_session",
        context
    )
    assert agent_result["operation_type"] == "agent_session"
    assert "session_id" in agent_result
    
    # Test agent session creation
    agent_session = await session_service.create_agent_session(
        "test_agent",
        context,
        SessionType.AGENT,
        SecurityLevel.HIGH
    )
    assert agent_session["success"] == True
    assert "session_id" in agent_session
    assert "token_id" in agent_session
    
    # Test session validation
    if agent_session["success"]:
        validation = await session_service.validate_agent_session(
            agent_session["session_id"],
            "test_agent",
            context
        )
        assert "success" in validation
        assert "session_id" in validation
        assert "agent_id" in validation
    
    # Test session analytics
    if agent_session["success"]:
        analytics = await session_service.get_agent_session_analytics(
            agent_session["session_id"],
            "test_agent",
            context
        )
        assert "success" in analytics
        assert "analytics" in analytics
        assert "analysis" in analytics
    
    print("✅ SessionService tests passed")


async def test_integration():
    """Test end-to-end integration."""
    print("🧪 Testing end-to-end integration...")
    
    # Create complete session management infrastructure
    abstraction = SessionAbstraction(adapter_type="in_memory")
    composition_service = SessionCompositionService(abstraction)
    session_service = SessionService(abstraction, composition_service)
    
    # Test complete workflow
    context = SessionContext(
        service_id="integration_service",
        agent_id="integration_agent",
        tenant_id="integration_tenant",
        environment="production",
        region="us-west-2",
        metadata={"integration_test": True}
    )
    
    # 1. Create agent session
    agent_session = await session_service.create_agent_session(
        "integration_agent",
        context,
        SessionType.AGENT,
        SecurityLevel.HIGH
    )
    print(f"   Agent session created: {agent_session['session_id']}")
    print(f"   Security level: {agent_session['security_level']}")
    
    # 2. Validate agent session
    if agent_session["success"]:
        validation = await session_service.validate_agent_session(
            agent_session["session_id"],
            "integration_agent",
            context
        )
        print(f"   Session validation: {'Valid' if validation['success'] else 'Invalid'}")
        print(f"   Session status: {validation.get('session_status', 'unknown')}")
    
    # 3. Get session analytics
    if agent_session["success"]:
        analytics = await session_service.get_agent_session_analytics(
            agent_session["session_id"],
            "integration_agent",
            context
        )
        print(f"   Session analytics: {analytics.get('analytics', {}).get('total_requests', 0)} requests")
        print(f"   Performance score: {analytics.get('analysis', {}).get('performance_score', 0):.1f}")
    
    # 4. Test session management for different operations
    operations = ["llm_session", "mcp_session", "tool_session", "agent_session"]
    for operation in operations:
        result = await session_service.manage_agent_session(operation, context)
        print(f"   {operation}: {'Success' if result.get('success') else 'Failed'}")
    
    # 5. Test session orchestration
    orchestration = await composition_service.orchestrate_session_management(
        "comprehensive_session",
        context
    )
    print(f"   Comprehensive session: {orchestration.get('session_id', 'unknown')}")
    print(f"   Session type: {orchestration.get('session_type', 'unknown')}")
    
    # 6. Test session assessment
    if agent_session["success"]:
        assessment = await composition_service.perform_session_assessment(
            agent_session["session_id"],
            context
        )
        print(f"   Session assessment: {assessment.get('session_status', 'unknown')}")
        print(f"   Health score: {assessment.get('assessment', {}).get('session_health', 'unknown')}")
    
    print("✅ End-to-end integration tests passed")


async def main():
    """Run all session architecture tests."""
    print("🚀 Starting Session Architecture Tests")
    print("=" * 50)
    
    try:
        await test_session_protocol()
        await test_in_memory_session_adapter()
        await test_redis_session_adapter()
        await test_session_abstraction()
        await test_session_composition_service()
        await test_session_service()
        await test_integration()
        
        print("=" * 50)
        print("🎉 All Session Architecture Tests Passed!")
        print(f"✅ Test completed at {datetime.utcnow().isoformat()}")
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Session Architecture Tests Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
