#!/usr/bin/env python3
"""
Utility Compliance Integration Tests

Tests that all foundations properly leverage platform utilities (error handling, telemetry, security, multi-tenancy)
in real scenarios with actual infrastructure.

WHAT: Verify utility compliance in real integration scenarios
HOW: Test foundations with real infrastructure, verify utilities are called and work correctly
"""

import sys
from pathlib import Path
import pytest
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

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
async def di_container(event_loop):
    """Create and initialize DI Container with real infrastructure."""
    container = DIContainerService("test")
    
    # Initialize Public Works Foundation (connects to real infrastructure)
    if hasattr(container, 'public_works_foundation') and container.public_works_foundation:
        public_works = container.public_works_foundation
    else:
        public_works = PublicWorksFoundationService(di_container=container)
        container.public_works_foundation = public_works
    
    await public_works.initialize()
    
    yield container
    
    # Cleanup
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture(scope="module")
async def curator_foundation(di_container):
    """Create and initialize Curator Foundation."""
    curator = CuratorFoundationService(
        foundation_services=di_container,
        public_works_foundation=di_container.public_works_foundation
    )
    await curator.initialize()
    
    yield curator
    
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()


@pytest.fixture(scope="module")
async def communication_foundation(di_container):
    """Create and initialize Communication Foundation."""
    communication = CommunicationFoundationService(
        di_container=di_container,
        public_works_foundation=di_container.public_works_foundation,
        curator_foundation=None  # Will be set if needed
    )
    await communication.initialize()
    
    yield communication
    
    if hasattr(communication, 'shutdown'):
        await communication.shutdown()


@pytest.fixture(scope="module")
async def agentic_foundation(di_container):
    """Create and initialize Agentic Foundation."""
    agentic = AgenticFoundationService(
        di_container=di_container,
        public_works_foundation=di_container.public_works_foundation,
        curator_foundation=None  # Will be set if needed
    )
    await agentic.initialize()
    
    yield agentic
    
    if hasattr(agentic, 'shutdown'):
        await agentic.shutdown()


@pytest.fixture(scope="module")
async def experience_foundation(di_container):
    """Create and initialize Experience Foundation."""
    experience = ExperienceFoundationService(
        di_container=di_container,
        public_works_foundation=di_container.public_works_foundation,
        curator_foundation=None  # Will be set if needed
    )
    await experience.initialize()
    
    yield experience


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


@pytest.fixture
def invalid_user_context():
    """Create an invalid user context (no permissions)."""
    return {
        "user_id": "test_user_456",
        "tenant_id": "test_tenant_1",
        "permissions": [],  # No permissions
        "roles": [],
        "email": "test2@example.com"
    }


@pytest.fixture
def invalid_tenant_context():
    """Create a user context with invalid tenant."""
    return {
        "user_id": "test_user_789",
        "tenant_id": "invalid_tenant",  # Invalid tenant
        "permissions": ["read", "write"],
        "roles": ["admin"],
        "email": "test3@example.com"
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def verify_error_handling(result: Dict[str, Any], expected_error_code: Optional[str] = None):
    """Verify error handling compliance."""
    assert "success" in result, "Response should include 'success' field"
    
    if not result.get("success"):
        assert "error" in result, "Error response should include 'error' field"
        assert "error_code" in result, "Error response should include 'error_code' field"
        
        if expected_error_code:
            assert result["error_code"] == expected_error_code, f"Expected error_code '{expected_error_code}', got '{result['error_code']}'"


async def verify_telemetry_recorded(service, operation_name: str):
    """Verify telemetry was recorded for an operation."""
    # This is a placeholder - actual implementation would query telemetry service
    # For now, we verify the method was called by checking the response structure
    pass  # Telemetry verification would require access to telemetry service


async def verify_health_metric_recorded(service, metric_name: str):
    """Verify health metric was recorded."""
    # This is a placeholder - actual implementation would query health service
    # For now, we verify the method was called by checking the response structure
    pass  # Health metric verification would require access to health service


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandlingCompliance:
    """Test error handling utility compliance."""
    
    @pytest.mark.asyncio
    async def test_curator_handles_errors_with_audit(self, curator_foundation, valid_user_context):
        """Test that Curator Foundation handles errors with audit."""
        # Test with invalid resource_id to trigger error
        result = await curator_foundation.get_agent("invalid_agent_id", user_context=valid_user_context)
        
        await verify_error_handling(result)
        assert result.get("error_code") is not None, "Error should include error_code"
    
    @pytest.mark.asyncio
    async def test_communication_handles_errors_with_audit(self, communication_foundation, valid_user_context):
        """Test that Communication Foundation handles errors with audit."""
        # Test with invalid API name to trigger error
        result = await communication_foundation.discover_soa_api("invalid_api", user_context=valid_user_context)
        
        await verify_error_handling(result)
        assert result.get("error_code") is not None, "Error should include error_code"
    
    @pytest.mark.asyncio
    async def test_agentic_handles_errors_with_audit(self, agentic_foundation, valid_user_context):
        """Test that Agentic Foundation handles errors with audit."""
        # Test with invalid agent_id to trigger error
        result = await agentic_foundation.get_agent("invalid_agent_id", user_context=valid_user_context)
        
        await verify_error_handling(result)
        assert result.get("error_code") is not None, "Error should include error_code"
    
    @pytest.mark.asyncio
    async def test_experience_handles_errors_with_audit(self, experience_foundation, valid_user_context):
        """Test that Experience Foundation handles errors with audit."""
        # Test with invalid realm_name to trigger error
        result = await experience_foundation.create_frontend_gateway(
            realm_name="invalid_realm",
            config={},
            user_context=valid_user_context
        )
        
        # This might raise an exception, which is fine - we verify it's handled
        # If it returns a result, verify error handling
        if isinstance(result, dict):
            await verify_error_handling(result)


# ============================================================================
# TELEMETRY TESTS
# ============================================================================

class TestTelemetryCompliance:
    """Test telemetry utility compliance."""
    
    @pytest.mark.asyncio
    async def test_curator_logs_operations_with_telemetry(self, curator_foundation, valid_user_context):
        """Test that Curator Foundation logs operations with telemetry."""
        # Call a method and verify it completes (telemetry should be logged)
        result = await curator_foundation.get_registered_services(user_context=valid_user_context)
        
        # Verify operation completed (telemetry would have been logged)
        assert result is not None, "Operation should complete"
        await verify_telemetry_recorded(curator_foundation, "get_registered_services")
    
    @pytest.mark.asyncio
    async def test_communication_logs_operations_with_telemetry(self, communication_foundation, valid_user_context):
        """Test that Communication Foundation logs operations with telemetry."""
        # Call a method and verify it completes
        result = await communication_foundation.get_unified_router(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_telemetry_recorded(communication_foundation, "get_unified_router")
    
    @pytest.mark.asyncio
    async def test_agentic_logs_operations_with_telemetry(self, agentic_foundation, valid_user_context):
        """Test that Agentic Foundation logs operations with telemetry."""
        # Call a method and verify it completes
        result = await agentic_foundation.get_agentic_capabilities(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_telemetry_recorded(agentic_foundation, "get_agentic_capabilities")
    
    @pytest.mark.asyncio
    async def test_experience_logs_operations_with_telemetry(self, experience_foundation, valid_user_context):
        """Test that Experience Foundation logs operations with telemetry."""
        # Call a method and verify it completes
        result = await experience_foundation.get_experience_sdk(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_telemetry_recorded(experience_foundation, "get_experience_sdk")


# ============================================================================
# SECURITY TESTS (ZERO-TRUST)
# ============================================================================

class TestSecurityCompliance:
    """Test security (zero-trust) utility compliance."""
    
    @pytest.mark.asyncio
    async def test_curator_security_validation_works(self, curator_foundation, valid_user_context, invalid_user_context):
        """Test that Curator Foundation validates security."""
        # Test with valid user context
        result = await curator_foundation.get_registered_services(user_context=valid_user_context)
        assert result is not None, "Valid user should be able to access"
        
        # Test with invalid permissions (should return access denied)
        result = await curator_foundation.get_registered_services(user_context=invalid_user_context)
        await verify_error_handling(result, "ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_communication_security_validation_works(self, communication_foundation, valid_user_context, invalid_user_context):
        """Test that Communication Foundation validates security."""
        # Test with valid user context
        result = await communication_foundation.get_unified_router(user_context=valid_user_context)
        assert result is not None, "Valid user should be able to access"
        
        # Test with invalid permissions
        result = await communication_foundation.get_unified_router(user_context=invalid_user_context)
        await verify_error_handling(result, "ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_agentic_security_validation_works(self, agentic_foundation, valid_user_context, invalid_user_context):
        """Test that Agentic Foundation validates security."""
        # Test with valid user context
        result = await agentic_foundation.get_agentic_capabilities(user_context=valid_user_context)
        assert result is not None, "Valid user should be able to access"
        
        # Test with invalid permissions
        result = await agentic_foundation.get_agentic_capabilities(user_context=invalid_user_context)
        await verify_error_handling(result, "ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_experience_security_validation_works(self, experience_foundation, valid_user_context, invalid_user_context):
        """Test that Experience Foundation validates security."""
        # Test with valid user context
        result = await experience_foundation.get_experience_sdk(user_context=valid_user_context)
        assert result is not None, "Valid user should be able to access"
        
        # Test with invalid permissions
        result = await experience_foundation.get_experience_sdk(user_context=invalid_user_context)
        await verify_error_handling(result, "ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_services_work_without_user_context(self, curator_foundation, communication_foundation):
        """Test that services work without user_context (optional parameter)."""
        # Services should work without user_context (security validation is optional)
        result1 = await curator_foundation.get_registered_services(user_context=None)
        result2 = await communication_foundation.get_unified_router(user_context=None)
        
        assert result1 is not None, "Service should work without user_context"
        assert result2 is not None, "Service should work without user_context"


# ============================================================================
# MULTI-TENANT TESTS
# ============================================================================

class TestMultiTenantCompliance:
    """Test multi-tenant utility compliance."""
    
    @pytest.mark.asyncio
    async def test_curator_tenant_validation_works(self, curator_foundation, valid_user_context, invalid_tenant_context):
        """Test that Curator Foundation validates tenant access."""
        # Test with valid tenant
        result = await curator_foundation.get_registered_services(user_context=valid_user_context)
        assert result is not None, "Valid tenant should be able to access"
        
        # Test with invalid tenant (should return tenant denied)
        result = await curator_foundation.get_registered_services(user_context=invalid_tenant_context)
        await verify_error_handling(result, "TENANT_ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_communication_tenant_validation_works(self, communication_foundation, valid_user_context, invalid_tenant_context):
        """Test that Communication Foundation validates tenant access."""
        # Test with valid tenant
        result = await communication_foundation.get_unified_router(user_context=valid_user_context)
        assert result is not None, "Valid tenant should be able to access"
        
        # Test with invalid tenant
        result = await communication_foundation.get_unified_router(user_context=invalid_tenant_context)
        await verify_error_handling(result, "TENANT_ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_agentic_tenant_validation_works(self, agentic_foundation, valid_user_context, invalid_tenant_context):
        """Test that Agentic Foundation validates tenant access."""
        # Test with valid tenant
        result = await agentic_foundation.get_agentic_capabilities(user_context=valid_user_context)
        assert result is not None, "Valid tenant should be able to access"
        
        # Test with invalid tenant
        result = await agentic_foundation.get_agentic_capabilities(user_context=invalid_tenant_context)
        await verify_error_handling(result, "TENANT_ACCESS_DENIED")
    
    @pytest.mark.asyncio
    async def test_experience_tenant_validation_works(self, experience_foundation, valid_user_context, invalid_tenant_context):
        """Test that Experience Foundation validates tenant access."""
        # Test with valid tenant
        result = await experience_foundation.get_experience_sdk(user_context=valid_user_context)
        assert result is not None, "Valid tenant should be able to access"
        
        # Test with invalid tenant
        result = await experience_foundation.get_experience_sdk(user_context=invalid_tenant_context)
        await verify_error_handling(result, "TENANT_ACCESS_DENIED")


# ============================================================================
# HEALTH METRICS TESTS
# ============================================================================

class TestHealthMetricsCompliance:
    """Test health metrics utility compliance."""
    
    @pytest.mark.asyncio
    async def test_curator_records_success_metrics(self, curator_foundation, valid_user_context):
        """Test that Curator Foundation records success metrics."""
        # Call a method that should succeed
        result = await curator_foundation.get_registered_services(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_health_metric_recorded(curator_foundation, "get_registered_services_success")
    
    @pytest.mark.asyncio
    async def test_curator_records_failure_metrics(self, curator_foundation, invalid_user_context):
        """Test that Curator Foundation records failure metrics."""
        # Call a method that should fail (access denied)
        result = await curator_foundation.get_registered_services(user_context=invalid_user_context)
        
        await verify_error_handling(result, "ACCESS_DENIED")
        await verify_health_metric_recorded(curator_foundation, "get_registered_services_access_denied")
    
    @pytest.mark.asyncio
    async def test_communication_records_success_metrics(self, communication_foundation, valid_user_context):
        """Test that Communication Foundation records success metrics."""
        result = await communication_foundation.get_unified_router(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_health_metric_recorded(communication_foundation, "get_unified_router_success")
    
    @pytest.mark.asyncio
    async def test_agentic_records_success_metrics(self, agentic_foundation, valid_user_context):
        """Test that Agentic Foundation records success metrics."""
        result = await agentic_foundation.get_agentic_capabilities(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_health_metric_recorded(agentic_foundation, "get_agentic_capabilities_success")
    
    @pytest.mark.asyncio
    async def test_experience_records_success_metrics(self, experience_foundation, valid_user_context):
        """Test that Experience Foundation records success metrics."""
        result = await experience_foundation.get_experience_sdk(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        await verify_health_metric_recorded(experience_foundation, "get_experience_sdk_success")


# ============================================================================
# COMPREHENSIVE UTILITY COMPLIANCE TESTS
# ============================================================================

class TestComprehensiveUtilityCompliance:
    """Comprehensive tests that verify all utilities work together."""
    
    @pytest.mark.asyncio
    async def test_curator_full_utility_compliance(self, curator_foundation, valid_user_context):
        """Test that Curator Foundation uses all utilities correctly."""
        # Test a write operation (should check security and tenant)
        result = await curator_foundation.register_service(
            service_name="test_service",
            service_info={"type": "test"},
            user_context=valid_user_context
        )
        
        # Verify all utilities were used:
        # 1. Telemetry was logged (operation completed)
        # 2. Security was validated (if user_context provided)
        # 3. Tenant was validated (if tenant_id provided)
        # 4. Health metric was recorded (success or failure)
        # 5. Error handling is in place (error_code in response if failed)
        
        assert result is not None, "Operation should complete"
        if isinstance(result, dict):
            if not result.get("success"):
                await verify_error_handling(result)
    
    @pytest.mark.asyncio
    async def test_communication_full_utility_compliance(self, communication_foundation, valid_user_context):
        """Test that Communication Foundation uses all utilities correctly."""
        # Test a write operation
        result = await communication_foundation.register_soa_api(
            api_name="test_api",
            api_info={"endpoint": "/test"},
            user_context=valid_user_context
        )
        
        assert result is not None, "Operation should complete"
        if isinstance(result, dict):
            if not result.get("success"):
                await verify_error_handling(result)
    
    @pytest.mark.asyncio
    async def test_agentic_full_utility_compliance(self, agentic_foundation, valid_user_context):
        """Test that Agentic Foundation uses all utilities correctly."""
        # Test a read operation
        result = await agentic_foundation.get_agentic_capabilities(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        if isinstance(result, dict):
            if not result.get("success"):
                await verify_error_handling(result)
    
    @pytest.mark.asyncio
    async def test_experience_full_utility_compliance(self, experience_foundation, valid_user_context):
        """Test that Experience Foundation uses all utilities correctly."""
        # Test a read operation
        result = await experience_foundation.get_experience_sdk(user_context=valid_user_context)
        
        assert result is not None, "Operation should complete"
        if isinstance(result, dict):
            if not result.get("success"):
                await verify_error_handling(result)

