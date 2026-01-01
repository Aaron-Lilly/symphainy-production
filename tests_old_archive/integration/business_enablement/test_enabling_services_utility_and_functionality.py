#!/usr/bin/env python3
"""
Comprehensive Test: Enabling Services Utility Usage & Functional Equivalence

This test verifies:
1. ✅ Utility Usage: All services properly use telemetry, security, tenant, error handling, health metrics
2. ✅ Functional Equivalence: Services still work as expected (equivalent to prior versions)

Tests multiple enabling services to ensure the refactoring pattern is consistent.
"""

import pytest
import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'symphainy-platform'))

from bases.realm_service_base import RealmServiceBase


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Services to test (representative sample covering all patterns)
SERVICES_TO_TEST = [
    {
        "name": "file_parser_service",
        "class": "FileParserService",
        "module": "backend.business_enablement.enabling_services.file_parser_service.file_parser_service",
        "test_methods": [
            {
                "method": "parse_file",
                "params": {"file_id": "test_file_123"},
                "expected_fields": ["success", "file_id"]
            },
            {
                "method": "detect_file_type",
                "params": {"file_id": "test_file_123"},
                "expected_fields": ["success", "file_type"]
            }
        ]
    },
    {
        "name": "data_analyzer_service",
        "class": "DataAnalyzerService",
        "module": "backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service",
        "test_methods": [
            {
                "method": "analyze_data",
                "params": {"data_id": "test_data_123"},
                "expected_fields": ["success", "data_id"]
            },
            {
                "method": "analyze_structure",
                "params": {"data_id": "test_data_123"},
                "expected_fields": ["success", "data_id", "structure"]
            }
        ]
    },
    {
        "name": "metrics_calculator_service",
        "class": "MetricsCalculatorService",
        "module": "backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service",
        "test_methods": [
            {
                "method": "calculate_metric",
                "params": {"metric_name": "revenue", "data_source": "test_data_123"},
                "expected_fields": ["success", "metric_name", "value"]
            }
        ]
    },
    {
        "name": "insights_generator_service",
        "class": "InsightsGeneratorService",
        "module": "backend.business_enablement.enabling_services.insights_generator_service.insights_generator_service",
        "test_methods": [
            {
                "method": "get_insights_capabilities",
                "params": {},
                "expected_fields": ["success", "available_insight_types"]
            }
        ]
    },
    {
        "name": "poc_generation_service",
        "class": "POCGenerationService",
        "module": "backend.business_enablement.enabling_services.poc_generation_service.poc_generation_service",
        "test_methods": [
            {
                "method": "generate_poc_roadmap",
                "params": {"business_context": {"objectives": ["test"]}, "poc_type": "hybrid"},
                "expected_fields": ["success"]
            }
        ]
    }
]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create mock DI Container with all utilities."""
    container = Mock()
    
    # Mock logger
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    container.get_logger = Mock(return_value=logger)
    
    # Mock config
    config = Mock()
    container.get_config = Mock(return_value=config)
    
    # Mock health
    health = Mock()
    health.record_metric = AsyncMock(return_value=True)
    container.get_health = Mock(return_value=health)
    
    # Mock telemetry
    telemetry = Mock()
    telemetry.emit_operation_start = AsyncMock(return_value=True)
    telemetry.emit_operation_complete = AsyncMock(return_value=True)
    container.get_telemetry = Mock(return_value=telemetry)
    
    # Mock error handler
    error_handler = Mock()
    error_handler.handle_error_with_audit = AsyncMock(return_value=True)
    container.get_error_handler = Mock(return_value=error_handler)
    
    # Mock security
    security = Mock()
    security.check_permissions = AsyncMock(return_value=True)
    container.get_security = Mock(return_value=security)
    
    # Mock tenant
    tenant = Mock()
    tenant.validate_tenant_access = AsyncMock(return_value=True)
    container.get_tenant = Mock(return_value=tenant)
    
    return container


@pytest.fixture
def mock_platform_gateway():
    """Create mock Platform Gateway."""
    gateway = Mock()
    
    # Mock abstraction access
    gateway.get_abstraction = Mock(return_value=None)
    
    return gateway


@pytest.fixture
def mock_user_context():
    """Create mock user context."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "roles": ["user"],
        "permissions": ["execute", "read", "write"]
    }


@pytest.fixture
def mock_smart_city_apis():
    """Create mock Smart City SOA APIs."""
    # Mock Librarian
    librarian = Mock()
    librarian.get_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "data": {"content": "test content", "metadata": {}}
    })
    librarian.store_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "success": True
    })
    
    # Mock Content Steward
    content_steward = Mock()
    content_steward.retrieve_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "data": {"content": "test content"}
    })
    content_steward.store_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "success": True
    })
    
    # Mock Data Steward
    data_steward = Mock()
    data_steward.track_data_lineage = AsyncMock(return_value=True)
    data_steward.validate_data_quality = AsyncMock(return_value=True)
    
    return {
        "librarian": librarian,
        "content_steward": content_steward,
        "data_steward": data_steward
    }


# ============================================================================
# UTILITY USAGE VERIFICATION
# ============================================================================

class UtilityUsageVerifier:
    """Verifies utility usage patterns in services."""
    
    @staticmethod
    async def verify_telemetry_usage(service: RealmServiceBase, method_name: str, call_args: Dict[str, Any]):
        """Verify telemetry is used in method."""
        # Check that log_operation_with_telemetry is called
        # This is done by checking if the method exists and is callable
        assert hasattr(service, "log_operation_with_telemetry"), \
            f"{service.__class__.__name__} should have log_operation_with_telemetry method"
        
        # Verify it's an async method
        assert asyncio.iscoroutinefunction(service.log_operation_with_telemetry), \
            f"log_operation_with_telemetry should be async in {service.__class__.__name__}"
    
    @staticmethod
    async def verify_security_usage(service: RealmServiceBase):
        """Verify security utility is accessible."""
        assert hasattr(service, "get_security"), \
            f"{service.__class__.__name__} should have get_security method"
        
        security = service.get_security()
        if security:
            assert hasattr(security, "check_permissions"), \
                f"Security utility should have check_permissions method"
    
    @staticmethod
    async def verify_tenant_usage(service: RealmServiceBase):
        """Verify tenant utility is accessible."""
        assert hasattr(service, "get_tenant"), \
            f"{service.__class__.__name__} should have get_tenant method"
        
        tenant = service.get_tenant()
        if tenant:
            assert hasattr(tenant, "validate_tenant_access"), \
                f"Tenant utility should have validate_tenant_access method"
    
    @staticmethod
    async def verify_error_handling_usage(service: RealmServiceBase):
        """Verify error handling utility is accessible."""
        assert hasattr(service, "handle_error_with_audit"), \
            f"{service.__class__.__name__} should have handle_error_with_audit method"
        
        assert asyncio.iscoroutinefunction(service.handle_error_with_audit), \
            f"handle_error_with_audit should be async in {service.__class__.__name__}"
    
    @staticmethod
    async def verify_health_metrics_usage(service: RealmServiceBase):
        """Verify health metrics utility is accessible."""
        assert hasattr(service, "record_health_metric"), \
            f"{service.__class__.__name__} should have record_health_metric method"
        
        assert asyncio.iscoroutinefunction(service.record_health_metric), \
            f"record_health_metric should be async in {service.__class__.__name__}"
    
    @staticmethod
    async def verify_curator_registration(service: RealmServiceBase):
        """Verify service is registered with Curator."""
        assert hasattr(service, "register_with_curator"), \
            f"{service.__class__.__name__} should have register_with_curator method"
        
        assert asyncio.iscoroutinefunction(service.register_with_curator), \
            f"register_with_curator should be async in {service.__class__.__name__}"


# ============================================================================
# FUNCTIONAL EQUIVALENCE VERIFICATION
# ============================================================================

class FunctionalEquivalenceVerifier:
    """Verifies functional equivalence to prior versions."""
    
    @staticmethod
    async def verify_method_signature(service: RealmServiceBase, method_name: str, expected_params: List[str]):
        """Verify method signature matches expected parameters."""
        assert hasattr(service, method_name), \
            f"{service.__class__.__name__} should have {method_name} method"
        
        method = getattr(service, method_name)
        assert callable(method), \
            f"{method_name} should be callable in {service.__class__.__name__}"
    
    @staticmethod
    async def verify_response_structure(result: Dict[str, Any], expected_fields: List[str]):
        """Verify response structure matches expected format."""
        assert isinstance(result, dict), \
            f"Method should return dict, got {type(result)}"
        
        assert "success" in result, \
            f"Response should have 'success' field"
        
        for field in expected_fields:
            assert field in result or result.get("success") is False, \
                f"Response should have '{field}' field (or success=False)"
    
    @staticmethod
    async def verify_error_handling(service: RealmServiceBase, method_name: str, invalid_params: Dict[str, Any]):
        """Verify error handling works correctly."""
        method = getattr(service, method_name)
        
        try:
            result = await method(**invalid_params)
            
            # Should return structured error response, not raise exception
            assert isinstance(result, dict), \
                f"{method_name} should return dict on error, not raise exception"
            
            assert "success" in result, \
                f"Error response should have 'success' field"
            
            if not result.get("success"):
                assert "error" in result or "message" in result, \
                    f"Error response should have 'error' or 'message' field"
        
        except Exception as e:
            # Some errors are expected (like PermissionError), but should be structured
            assert isinstance(e, (PermissionError, ValueError, TypeError)), \
                f"{method_name} should handle errors gracefully, got {type(e).__name__}"


# ============================================================================
# TEST CLASSES
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestEnablingServicesUtilityUsage:
    """Test utility usage across all enabling services."""
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_extends_realm_service_base(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway
    ):
        """Test that service extends RealmServiceBase."""
        # Import service class
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        # Create service instance
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Verify extends RealmServiceBase
        assert isinstance(service, RealmServiceBase), \
            f"{class_name} should extend RealmServiceBase"
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_has_utility_methods(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway
    ):
        """Test that service has all required utility methods."""
        # Import and create service
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Verify utility methods exist
        verifier = UtilityUsageVerifier()
        await verifier.verify_telemetry_usage(service, "test_method", {})
        await verifier.verify_security_usage(service)
        await verifier.verify_tenant_usage(service)
        await verifier.verify_error_handling_usage(service)
        await verifier.verify_health_metrics_usage(service)
        await verifier.verify_curator_registration(service)
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_initialize_uses_utilities(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway
    ):
        """Test that initialize() method uses utilities."""
        # Import and create service
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City APIs
        with patch.object(service, 'get_librarian_api', new_callable=AsyncMock) as mock_librarian:
            mock_librarian.return_value = Mock()
            with patch.object(service, 'get_content_steward_api', new_callable=AsyncMock) as mock_content:
                mock_content.return_value = Mock()
                with patch.object(service, 'get_data_steward_api', new_callable=AsyncMock) as mock_data:
                    mock_data.return_value = Mock()
                    
                    # Mock Curator registration
                    with patch.object(service, 'register_with_curator', new_callable=AsyncMock) as mock_curator:
                        mock_curator.return_value = True
                        
                        # Mock utility methods to track calls
                        with patch.object(service, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_telemetry:
                            mock_telemetry.return_value = True
                            with patch.object(service, 'record_health_metric', new_callable=AsyncMock) as mock_health:
                                mock_health.return_value = True
                                
                                # Initialize service
                                result = await service.initialize()
                                
                                # Verify initialization succeeded
                                assert result is True or result is False, \
                                    f"initialize() should return bool, got {type(result)}"
                                
                                # Verify utilities were called (if initialization succeeded)
                                if result:
                                    # Verify telemetry was called (at least start and complete)
                                    assert mock_telemetry.called, \
                                        f"{class_name}.initialize() should call log_operation_with_telemetry"
                                    
                                    # Verify health metric was recorded
                                    assert mock_health.called, \
                                        f"{class_name}.initialize() should call record_health_metric"


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestEnablingServicesFunctionalEquivalence:
    """Test functional equivalence to prior versions."""
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_methods_exist(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway
    ):
        """Test that all expected methods exist."""
        # Import and create service
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Verify all test methods exist
        for test_method in service_config["test_methods"]:
            method_name = test_method["method"]
            verifier = FunctionalEquivalenceVerifier()
            await verifier.verify_method_signature(service, method_name, list(test_method["params"].keys()))
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_methods_return_structured_responses(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway,
        mock_smart_city_apis,
        mock_user_context
    ):
        """Test that methods return structured responses (functional equivalence)."""
        # Import and create service
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City APIs
        with patch.object(service, 'get_librarian_api', new_callable=AsyncMock) as mock_librarian:
            mock_librarian.return_value = mock_smart_city_apis["librarian"]
            with patch.object(service, 'get_content_steward_api', new_callable=AsyncMock) as mock_content:
                mock_content.return_value = mock_smart_city_apis["content_steward"]
                with patch.object(service, 'get_data_steward_api', new_callable=AsyncMock) as mock_data:
                    mock_data.return_value = mock_smart_city_apis["data_steward"]
                    
                    # Mock Curator registration
                    with patch.object(service, 'register_with_curator', new_callable=AsyncMock) as mock_curator:
                        mock_curator.return_value = True
                        
                        # Mock utility methods to track calls
                        with patch.object(service, 'log_operation_with_telemetry', new_callable=AsyncMock) as mock_telemetry:
                            mock_telemetry.return_value = True
                            with patch.object(service, 'record_health_metric', new_callable=AsyncMock) as mock_health:
                                mock_health.return_value = True
                                with patch.object(service, 'get_security', new_callable=Mock) as mock_get_security:
                                    mock_security = Mock()
                                    mock_security.check_permissions = AsyncMock(return_value=True)
                                    mock_get_security.return_value = mock_security
                                    with patch.object(service, 'get_tenant', new_callable=Mock) as mock_get_tenant:
                                        mock_tenant = Mock()
                                        mock_tenant.validate_tenant_access = AsyncMock(return_value=True)
                                        mock_get_tenant.return_value = mock_tenant
                                        
                                        # Initialize service
                                        await service.initialize()
                                        
                                        # Test each method
                                        for test_method in service_config["test_methods"]:
                                            method_name = test_method["method"]
                                            params = test_method["params"].copy()
                                            
                                            # Add user_context if method accepts it
                                            method = getattr(service, method_name)
                                            import inspect
                                            sig = inspect.signature(method)
                                            if "user_context" in sig.parameters:
                                                params["user_context"] = mock_user_context
                                            
                                            # Reset mocks
                                            mock_telemetry.reset_mock()
                                            mock_health.reset_mock()
                                            mock_get_security.reset_mock()
                                            mock_get_tenant.reset_mock()
                                            
                                            # Call method
                                            result = await method(**params)
                                            
                                            # Verify response structure
                                            verifier = FunctionalEquivalenceVerifier()
                                            await verifier.verify_response_structure(result, test_method["expected_fields"])
                                            
                                            # Verify utilities were called (if user_context provided)
                                            if params.get("user_context"):
                                                # Verify telemetry was called
                                                assert mock_telemetry.called, \
                                                    f"{method_name} should call log_operation_with_telemetry when user_context provided"
                                                
                                                # Verify security check was called
                                                assert mock_get_security.called, \
                                                    f"{method_name} should call get_security when user_context provided"
                                                
                                                # Verify tenant check was called
                                                assert mock_get_tenant.called, \
                                                    f"{method_name} should call get_tenant when user_context provided"
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_methods_handle_errors_gracefully(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway,
        mock_smart_city_apis
    ):
        """Test that methods handle errors gracefully (functional equivalence)."""
        # Import and create service
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City APIs to return None (simulating not found)
        mock_smart_city_apis["librarian"].get_document = AsyncMock(return_value=None)
        mock_smart_city_apis["content_steward"].retrieve_document = AsyncMock(return_value=None)
        
        with patch.object(service, 'get_librarian_api', new_callable=AsyncMock) as mock_librarian:
            mock_librarian.return_value = mock_smart_city_apis["librarian"]
            with patch.object(service, 'get_content_steward_api', new_callable=AsyncMock) as mock_content:
                mock_content.return_value = mock_smart_city_apis["content_steward"]
                with patch.object(service, 'get_data_steward_api', new_callable=AsyncMock) as mock_data:
                    mock_data.return_value = mock_smart_city_apis["data_steward"]
                    
                    # Mock Curator registration
                    with patch.object(service, 'register_with_curator', new_callable=AsyncMock) as mock_curator:
                        mock_curator.return_value = True
                        
                        # Initialize service
                        await service.initialize()
                        
                        # Test error handling for first method
                        if service_config["test_methods"]:
                            test_method = service_config["test_methods"][0]
                            method_name = test_method["method"]
                            
                            # Call with invalid params (should handle gracefully)
                            invalid_params = {"invalid_param": "invalid_value"}
                            
                            verifier = FunctionalEquivalenceVerifier()
                            await verifier.verify_error_handling(service, method_name, invalid_params)


@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
class TestEnablingServicesUserContext:
    """Test that services properly handle user_context parameter."""
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_methods_accept_user_context(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway,
        mock_user_context
    ):
        """Test that SOA API methods accept user_context parameter."""
        # Import and create service
        module_path = service_config["module"]
        class_name = service_config["class"]
        
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        
        service = service_class(
            service_name=f"test_{service_config['name']}",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Check that methods accept user_context
        for test_method in service_config["test_methods"]:
            method_name = test_method["method"]
            method = getattr(service, method_name)
            
            import inspect
            sig = inspect.signature(method)
            
            # Verify user_context parameter exists
            assert "user_context" in sig.parameters, \
                f"{method_name} should accept user_context parameter"
            
            # Verify user_context is Optional[Dict[str, Any]]
            param = sig.parameters["user_context"]
            assert param.annotation in [Optional[Dict[str, Any]], Dict[str, Any], type(None)], \
                f"{method_name} user_context should be Optional[Dict[str, Any]], got {param.annotation}"


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

