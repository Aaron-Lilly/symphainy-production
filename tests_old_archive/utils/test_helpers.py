#!/usr/bin/env python3
"""
Test Helpers - Common Test Patterns and Utilities

Provides reusable test utilities and patterns for testing across all layers.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from unittest.mock import Mock, MagicMock, AsyncMock

class AsyncTestHelper:
    """Helper for async test operations."""
    
    @staticmethod
    async def wait_for_condition(
        condition: Callable,
        timeout: float = 5.0,
        interval: float = 0.1,
        error_message: str = "Condition not met"
    ) -> bool:
        """
        Wait for a condition to become true.
        
        Args:
            condition: Async callable that returns bool
            timeout: Maximum time to wait
            interval: Check interval
            error_message: Error message if timeout
        
        Returns:
            True if condition met, raises TimeoutError otherwise
        """
        start_time = datetime.now().timestamp()
        
        while True:
            if await condition():
                return True
            
            elapsed = datetime.now().timestamp() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"{error_message} (timeout: {timeout}s)")
            
            await asyncio.sleep(interval)
    
    @staticmethod
    async def retry_async(
        func: Callable,
        max_retries: int = 3,
        delay: float = 0.5,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Retry an async function with exponential backoff.
        
        Args:
            func: Async function to retry
            max_retries: Maximum number of retries
            delay: Initial delay between retries
            exceptions: Exceptions to catch and retry
        
        Returns:
            Function result
        
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await func()
            except exceptions as e:
                last_exception = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))
                else:
                    raise last_exception
        
        raise last_exception

class ServiceInitializationHelper:
    """Helper for service initialization patterns."""
    
    @staticmethod
    async def initialize_service_with_dependencies(
        service_class,
        di_container,
        platform_gateway,
        curator_foundation=None,
        **kwargs
    ):
        """
        Initialize a service with all dependencies.
        
        Args:
            service_class: Service class to instantiate
            di_container: DI Container instance
            platform_gateway: Platform Gateway instance
            curator_foundation: Optional Curator Foundation
            **kwargs: Additional service-specific arguments
        
        Returns:
            Initialized service instance
        """
        # Register Curator if provided
        if curator_foundation:
            di_container.foundation_services["CuratorFoundationService"] = curator_foundation
        
        # Create service instance
        service = service_class(
            service_name=kwargs.get("service_name", "TestService"),
            realm_name=kwargs.get("realm_name", "test"),
            platform_gateway=platform_gateway,
            di_container=di_container,
            **{k: v for k, v in kwargs.items() if k not in ["service_name", "realm_name"]}
        )
        
        # Initialize service
        await service.initialize()
        
        return service
    
    @staticmethod
    def create_mock_service_dependencies():
        """Create mock dependencies for service testing."""
        mock_di_container = MagicMock()
        mock_platform_gateway = MagicMock()
        mock_curator = MagicMock()
        
        # Setup mock DI container
        mock_di_container.get_utility = MagicMock(return_value=MagicMock())
        mock_di_container.get_abstraction = MagicMock(return_value=MagicMock())
        mock_di_container.get_foundation_service = MagicMock(return_value=mock_curator)
        mock_di_container.foundation_services = {"CuratorFoundationService": mock_curator}
        
        # Setup mock platform gateway
        mock_platform_gateway.get_abstraction = MagicMock(return_value=MagicMock())
        mock_platform_gateway.validate_access = MagicMock(return_value=True)
        
        # Setup mock curator
        mock_curator.get_registered_services = AsyncMock(
            return_value={"services": {}}
        )
        mock_curator.register_service = AsyncMock(return_value=True)
        
        return {
            "di_container": mock_di_container,
            "platform_gateway": mock_platform_gateway,
            "curator": mock_curator
        }

class MockDataGenerator:
    """Helper for generating test data."""
    
    @staticmethod
    def create_sample_file_data(
        file_id: Optional[str] = None,
        file_name: str = "test_file.pdf",
        file_type: str = "application/pdf",
        content: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Create sample file data for testing."""
        return {
            "file_id": file_id or f"file_{datetime.now().timestamp()}",
            "file_name": file_name,
            "file_type": file_type,
            "file_size": len(content) if content else 1024,
            "content": content or b"Sample file content",
            "metadata": {
                "uploaded_at": datetime.utcnow().isoformat(),
                "uploaded_by": "test_user"
            }
        }
    
    @staticmethod
    def create_sample_insights_data(
        resource_id: Optional[str] = None,
        analysis_type: str = "descriptive"
    ) -> Dict[str, Any]:
        """Create sample insights data for testing."""
        return {
            "resource_id": resource_id or f"resource_{datetime.now().timestamp()}",
            "analysis_type": analysis_type,
            "insights": {
                "summary": "Test insights summary",
                "key_findings": ["Finding 1", "Finding 2"],
                "recommendations": ["Recommendation 1", "Recommendation 2"]
            },
            "visualization": {
                "type": "chart",
                "data": {"x": [1, 2, 3], "y": [10, 20, 30]}
            }
        }
    
    @staticmethod
    def create_sample_workflow_data(
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create sample workflow data for testing."""
        return {
            "workflow_id": workflow_id or f"workflow_{datetime.now().timestamp()}",
            "workflow_name": "Test Workflow",
            "steps": [
                {"step_id": "step_1", "action": "validate", "params": {}},
                {"step_id": "step_2", "action": "process", "params": {}},
                {"step_id": "step_3", "action": "finalize", "params": {}}
            ],
            "status": "pending"
        }
    
    @staticmethod
    def create_sample_roadmap_data(
        roadmap_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create sample roadmap data for testing."""
        return {
            "roadmap_id": roadmap_id or f"roadmap_{datetime.now().timestamp()}",
            "milestones": [
                {"milestone_id": "m1", "name": "Phase 1", "status": "planned"},
                {"milestone_id": "m2", "name": "Phase 2", "status": "planned"}
            ],
            "timeline": {
                "start_date": datetime.utcnow().isoformat(),
                "end_date": None
            }
        }

class AssertionHelper:
    """Helper for common test assertions."""
    
    @staticmethod
    def assert_service_initialized(service, service_name: str = None):
        """Assert that a service is properly initialized."""
        assert service is not None, f"Service should not be None"
        assert hasattr(service, "is_initialized"), "Service should have is_initialized attribute"
        assert service.is_initialized, f"{service_name or 'Service'} should be initialized"
    
    @staticmethod
    def assert_success_response(response: Dict[str, Any], expected_keys: List[str] = None):
        """Assert that a response indicates success."""
        assert response is not None, "Response should not be None"
        assert "status" in response, "Response should have 'status' key"
        assert response["status"] == "success", f"Response status should be 'success', got: {response.get('status')}"
        
        if expected_keys:
            for key in expected_keys:
                assert key in response, f"Response should have '{key}' key"
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any], error_message: str = None):
        """Assert that a response indicates an error."""
        assert response is not None, "Response should not be None"
        assert "status" in response, "Response should have 'status' key"
        assert response["status"] in ["error", "failed"], f"Response status should indicate error, got: {response.get('status')}"
        
        if error_message:
            assert "message" in response, "Error response should have 'message' key"
            assert error_message.lower() in response["message"].lower(), f"Error message should contain '{error_message}'"
    
    @staticmethod
    def assert_service_registered(service, curator, service_name: str):
        """Assert that a service is registered with Curator."""
        # This would need actual curator implementation
        # For now, just check service has registration capability
        assert hasattr(service, "register_with_curator") or hasattr(service, "register_capability"), \
            f"{service_name} should have registration capability"

class MockServiceFactory:
    """Factory for creating mock services with common patterns."""
    
    @staticmethod
    def create_mock_realm_service(
        service_name: str,
        realm_name: str,
        platform_gateway=None,
        di_container=None
    ) -> MagicMock:
        """Create a mock realm service with standard structure."""
        mock_service = MagicMock()
        mock_service.service_name = service_name
        mock_service.realm_name = realm_name
        mock_service.platform_gateway = platform_gateway or MagicMock()
        mock_service.di_container = di_container or MagicMock()
        mock_service.logger = MagicMock()
        mock_service.is_initialized = False
        
        mock_service.initialize = AsyncMock(return_value=True)
        mock_service.get_service_capabilities = AsyncMock(return_value={"capabilities": []})
        mock_service.health_check = AsyncMock(return_value={"status": "healthy"})
        
        return mock_service
    
    @staticmethod
    def create_mock_smart_city_service(
        service_name: str,
        di_container=None
    ) -> MagicMock:
        """Create a mock Smart City service with standard structure."""
        mock_service = MagicMock()
        mock_service.service_name = service_name
        mock_service.role_name = service_name.lower().replace("service", "")
        mock_service.di_container = di_container or MagicMock()
        mock_service.logger = MagicMock()
        mock_service.is_initialized = False
        
        mock_service.initialize = AsyncMock(return_value=True)
        mock_service.register_capability = AsyncMock(return_value=True)
        mock_service.health_check = AsyncMock(return_value={"status": "healthy"})
        
        return mock_service


class Phase2RegistrationHelper:
    """Helper for verifying Phase 2 Curator registration patterns."""
    
    @staticmethod
    def assert_phase2_registration(call_args: Dict[str, Any]):
        """
        Assert that Curator registration uses Phase 2 pattern.
        
        Args:
            call_args: Arguments passed to register_service (from mock.call_args[1])
        
        Raises:
            AssertionError: If registration doesn't match Phase 2 pattern
        """
        assert "service_id" in call_args, "Phase 2 registration must include 'service_id'"
        assert "service_name" in call_args, "Phase 2 registration must include 'service_name'"
        assert "service_type" in call_args, "Phase 2 registration must include 'service_type'"
        assert "realm_name" in call_args, "Phase 2 registration must include 'realm_name'"
        assert "capabilities" in call_args, "Phase 2 registration must include 'capabilities'"
        assert isinstance(call_args["capabilities"], list), "Capabilities must be a list"
        
        # Check capability definition structure
        if call_args["capabilities"]:
            capability = call_args["capabilities"][0]
            assert "name" in capability, "Capability must have 'name'"
            assert "protocol" in capability, "Capability must have 'protocol'"
            assert "description" in capability, "Capability must have 'description'"
            assert "contracts" in capability, "Capability must have 'contracts'"
            assert "semantic_mapping" in capability, "Capability must have 'semantic_mapping'"
            
            # Check contracts structure
            contracts = capability.get("contracts", {})
            if "soa_api" in contracts:
                soa_api = contracts["soa_api"]
                assert "api_name" in soa_api, "SOA API must have 'api_name'"
                assert "handler" in soa_api, "SOA API must have 'handler'"
            
            if "mcp_tool" in contracts:
                mcp_tool = contracts["mcp_tool"]
                assert "tool_name" in mcp_tool, "MCP tool must have 'tool_name'"
    
    @staticmethod
    def assert_user_context_parameter(method):
        """
        Assert that method accepts user_context parameter.
        
        Args:
            method: Method to check
        
        Raises:
            AssertionError: If method doesn't accept user_context
        """
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        assert "user_context" in params, f"Method {method.__name__} must accept 'user_context' parameter"
    
    @staticmethod
    def create_user_context(
        user_id: str = "test_user",
        tenant_id: str = "test_tenant",
        permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a user context for testing.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            permissions: List of permissions
        
        Returns:
            User context dictionary
        """
        if permissions is None:
            permissions = ["read", "write", "execute"]
        
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "permissions": permissions,
            "roles": ["user"]
        }

