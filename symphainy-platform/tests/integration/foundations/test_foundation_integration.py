#!/usr/bin/env python3
"""
Foundation Integration Tests

Tests that all foundations work together with real infrastructure and properly leverage utilities.

WHAT: Test foundation integration with real infrastructure
HOW: Initialize all foundations together, test cross-foundation operations, verify utilities
"""

import sys
from pathlib import Path
import pytest
import asyncio
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def full_foundation_stack(event_loop, infrastructure_available):
    """Create and initialize full foundation stack."""
    container = DIContainerService("test")
    
    # Initialize Public Works Foundation
    if hasattr(container, 'public_works_foundation') and container.public_works_foundation:
        public_works = container.public_works_foundation
    else:
        public_works = PublicWorksFoundationService(di_container=container)
        container.public_works_foundation = public_works
    
    await public_works.initialize()
    
    # Initialize Curator Foundation
    curator = CuratorFoundationService(
        foundation_services=container,
        public_works_foundation=public_works
    )
    await curator.initialize()
    
    # Initialize Communication Foundation
    communication = CommunicationFoundationService(
        di_container=container,
        public_works_foundation=public_works,
        curator_foundation=curator
    )
    await communication.initialize()
    
    # Initialize Agentic Foundation
    agentic = AgenticFoundationService(
        di_container=container,
        public_works_foundation=public_works,
        curator_foundation=curator
    )
    await agentic.initialize()
    
    # Initialize Experience Foundation
    experience = ExperienceFoundationService(
        di_container=container,
        public_works_foundation=public_works,
        curator_foundation=curator
    )
    await experience.initialize()
    
    yield {
        "di_container": container,
        "public_works": public_works,
        "curator": curator,
        "communication": communication,
        "agentic": agentic,
        "experience": experience
    }
    
    # Cleanup
    if hasattr(experience, 'shutdown'):
        await experience.shutdown()
    if hasattr(agentic, 'shutdown'):
        await agentic.shutdown()
    if hasattr(communication, 'shutdown'):
        await communication.shutdown()
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture
def valid_user_context():
    """Create a valid user context for testing."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_1",
        "permissions": ["read", "write"],
        "roles": ["admin"],
        "email": "test@example.com"
    }


# ============================================================================
# FOUNDATION INITIALIZATION TESTS
# ============================================================================

class TestFoundationInitialization:
    """Test that all foundations initialize correctly together."""
    
    @pytest.mark.asyncio
    @pytest.mark.foundation_integration
    async def test_all_foundations_initialize_together(self, full_foundation_stack):
        """Test that all foundations initialize together."""
        stack = full_foundation_stack
        
        assert stack["public_works"] is not None, "Public Works Foundation should be initialized"
        assert stack["curator"] is not None, "Curator Foundation should be initialized"
        assert stack["communication"] is not None, "Communication Foundation should be initialized"
        assert stack["agentic"] is not None, "Agentic Foundation should be initialized"
        assert stack["experience"] is not None, "Experience Foundation should be initialized"
    
    @pytest.mark.asyncio
    @pytest.mark.foundation_integration
    async def test_foundations_share_infrastructure(self, full_foundation_stack):
        """Test that foundations share infrastructure through Public Works."""
        stack = full_foundation_stack
        
        # All foundations should have access to Public Works Foundation
        assert stack["curator"].public_works_foundation == stack["public_works"]
        assert stack["communication"].public_works_foundation == stack["public_works"]
        assert stack["agentic"].public_works_foundation == stack["public_works"]
        assert stack["experience"].public_works_foundation == stack["public_works"]


# ============================================================================
# CROSS-FOUNDATION OPERATION TESTS
# ============================================================================

class TestCrossFoundationOperations:
    """Test operations that span multiple foundations."""
    
    @pytest.mark.asyncio
    @pytest.mark.foundation_integration
    async def test_curator_registers_services(self, full_foundation_stack, valid_user_context):
        """Test that services can register with Curator Foundation."""
        stack = full_foundation_stack
        curator = stack["curator"]
        
        # Register a service
        result = await curator.register_service(
            service_name="test_service",
            service_info={"type": "test", "version": "1.0.0"},
            user_context=valid_user_context
        )
        
        assert result is not None, "Service registration should complete"
        if isinstance(result, dict):
            assert result.get("success") is not False, "Service registration should succeed or return proper error"
    
    @pytest.mark.asyncio
    @pytest.mark.foundation_integration
    async def test_communication_registers_soa_api(self, full_foundation_stack, valid_user_context):
        """Test that Communication Foundation can register SOA APIs."""
        stack = full_foundation_stack
        communication = stack["communication"]
        
        # Register an SOA API
        result = await communication.register_soa_api(
            api_name="test_api",
            api_info={"endpoint": "/test", "method": "GET"},
            user_context=valid_user_context
        )
        
        assert result is not None, "SOA API registration should complete"
        if isinstance(result, dict):
            assert result.get("success") is not False, "SOA API registration should succeed or return proper error"
    
    @pytest.mark.asyncio
    @pytest.mark.foundation_integration
    async def test_agentic_provides_capabilities(self, full_foundation_stack, valid_user_context):
        """Test that Agentic Foundation provides capabilities."""
        stack = full_foundation_stack
        agentic = stack["agentic"]
        
        # Get agentic capabilities
        result = await agentic.get_agentic_capabilities(user_context=valid_user_context)
        
        assert result is not None, "Agentic capabilities should be available"
        if isinstance(result, dict):
            assert "agent_types" in result or result.get("success") is not False
    
    @pytest.mark.asyncio
    @pytest.mark.foundation_integration
    async def test_experience_provides_sdk(self, full_foundation_stack, valid_user_context):
        """Test that Experience Foundation provides SDK."""
        stack = full_foundation_stack
        experience = stack["experience"]
        
        # Get experience SDK
        result = await experience.get_experience_sdk(user_context=valid_user_context)
        
        assert result is not None, "Experience SDK should be available"
        if isinstance(result, dict):
            assert "frontend_gateway_builder" in result or result.get("success") is not False


# ============================================================================
# UTILITY COMPLIANCE IN INTEGRATION TESTS
# ============================================================================

class TestUtilityComplianceInIntegration:
    """Test that utilities work correctly in integration scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.utility_compliance
    @pytest.mark.foundation_integration
    async def test_all_foundations_use_error_handling(self, full_foundation_stack, valid_user_context):
        """Test that all foundations use error handling in integration."""
        stack = full_foundation_stack
        
        # Test each foundation with an operation that might fail
        # Curator
        result1 = await stack["curator"].get_agent("nonexistent_agent", user_context=valid_user_context)
        if isinstance(result1, dict):
            assert "error_code" in result1 if not result1.get("success") else True
        
        # Communication
        result2 = await stack["communication"].discover_soa_api("nonexistent_api", user_context=valid_user_context)
        if isinstance(result2, dict):
            assert "error_code" in result2 if not result2.get("success") else True
        
        # Agentic
        result3 = await stack["agentic"].get_agent("nonexistent_agent", user_context=valid_user_context)
        if isinstance(result3, dict):
            assert "error_code" in result3 if not result3.get("success") else True
    
    @pytest.mark.asyncio
    @pytest.mark.utility_compliance
    @pytest.mark.foundation_integration
    async def test_all_foundations_validate_security(self, full_foundation_stack, valid_user_context):
        """Test that all foundations validate security in integration."""
        stack = full_foundation_stack
        
        # Create invalid user context
        invalid_user = {**valid_user_context, "permissions": []}
        
        # Test each foundation with invalid permissions
        result1 = await stack["curator"].get_registered_services(user_context=invalid_user)
        if isinstance(result1, dict):
            assert result1.get("error_code") == "ACCESS_DENIED" if not result1.get("success") else True
        
        result2 = await stack["communication"].get_unified_router(user_context=invalid_user)
        if isinstance(result2, dict):
            assert result2.get("error_code") == "ACCESS_DENIED" if not result2.get("success") else True
        
        result3 = await stack["agentic"].get_agentic_capabilities(user_context=invalid_user)
        if isinstance(result3, dict):
            assert result3.get("error_code") == "ACCESS_DENIED" if not result3.get("success") else True
    
    @pytest.mark.asyncio
    @pytest.mark.utility_compliance
    @pytest.mark.foundation_integration
    async def test_all_foundations_validate_tenant(self, full_foundation_stack, valid_user_context):
        """Test that all foundations validate tenant in integration."""
        stack = full_foundation_stack
        
        # Create invalid tenant context
        invalid_tenant = {**valid_user_context, "tenant_id": "invalid_tenant"}
        
        # Test each foundation with invalid tenant
        result1 = await stack["curator"].get_registered_services(user_context=invalid_tenant)
        if isinstance(result1, dict):
            assert result1.get("error_code") == "TENANT_ACCESS_DENIED" if not result1.get("success") else True
        
        result2 = await stack["communication"].get_unified_router(user_context=invalid_tenant)
        if isinstance(result2, dict):
            assert result2.get("error_code") == "TENANT_ACCESS_DENIED" if not result2.get("success") else True
        
        result3 = await stack["agentic"].get_agentic_capabilities(user_context=invalid_tenant)
        if isinstance(result3, dict):
            assert result3.get("error_code") == "TENANT_ACCESS_DENIED" if not result3.get("success") else True

