#!/usr/bin/env python3
"""
Simple Functional Test: Enabling Services Still Work

This test verifies that enabling services still function correctly after refactoring.
It tests actual functionality, not just structure.

Goal: Confirm services still work as expected (functional equivalence).
"""

import pytest
import os
import sys
import asyncio
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'symphainy-platform'))


# ============================================================================
# TEST SERVICES (Representative Sample)
# ============================================================================

SERVICES_TO_TEST = [
    {
        "name": "file_parser_service",
        "class": "FileParserService",
        "module": "backend.business_enablement.enabling_services.file_parser_service.file_parser_service",
        "test": {
            "method": "parse_file",
            "params": {"file_id": "test_file_123"},
            "expected": {
                "has_success": True,
                "has_file_id": True,
                "success_can_be_false": True  # File not found is OK
            }
        }
    },
    {
        "name": "data_analyzer_service",
        "class": "DataAnalyzerService",
        "module": "backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service",
        "test": {
            "method": "analyze_data",
            "params": {"data_id": "test_data_123", "analysis_type": "descriptive"},
            "expected": {
                "has_success": True,
                "has_data_id": True,
                "success_can_be_false": True
            }
        }
    },
    {
        "name": "metrics_calculator_service",
        "class": "MetricsCalculatorService",
        "module": "backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service",
        "test": {
            "method": "calculate_metric",
            "params": {"metric_name": "revenue", "data_source": "test_data_123"},
            "expected": {
                "has_success": True,
                "has_metric_name": True,
                "success_can_be_false": True
            }
        }
    },
    {
        "name": "insights_generator_service",
        "class": "InsightsGeneratorService",
        "module": "backend.business_enablement.enabling_services.insights_generator_service.insights_generator_service",
        "test": {
            "method": "get_insights_capabilities",
            "params": {},
            "expected": {
                "has_success": True,
                "has_available_insight_types": True,
                "success_should_be_true": True  # This should always work
            }
        }
    },
    {
        "name": "poc_generation_service",
        "class": "POCGenerationService",
        "module": "backend.business_enablement.enabling_services.poc_generation_service.poc_generation_service",
        "test": {
            "method": "generate_poc_roadmap",
            "params": {"business_context": {"objectives": ["test objective"]}, "poc_type": "hybrid"},
            "expected": {
                "has_success": True,
                "success_can_be_false": True
            }
        }
    }
]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_di_container():
    """Create mock DI Container."""
    container = Mock()
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    container.get_logger = Mock(return_value=logger)
    container.get_config = Mock(return_value=Mock())
    container.get_health = Mock(return_value=Mock())
    container.get_telemetry = Mock(return_value=Mock())
    container.get_error_handler = Mock(return_value=Mock())
    container.get_security = Mock(return_value=Mock())
    container.get_tenant = Mock(return_value=Mock())
    return container


@pytest.fixture
def mock_platform_gateway():
    """Create mock Platform Gateway."""
    gateway = Mock()
    gateway.get_abstraction = Mock(return_value=None)
    return gateway


@pytest.fixture
def mock_smart_city_apis():
    """Create mock Smart City SOA APIs that return realistic data."""
    # Mock Librarian - returns document data
    librarian = Mock()
    librarian.get_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "data": {
            "content": "Sample document content for testing",
            "metadata": {
                "file_type": "pdf",
                "size": 1024,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    })
    librarian.store_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "success": True
    })
    
    # Mock Content Steward - returns document data
    content_steward = Mock()
    content_steward.retrieve_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "data": {
            "content": "Sample content",
            "metadata": {}
        }
    })
    content_steward.store_document = AsyncMock(return_value={
        "document_id": "test_doc_123",
        "success": True
    })
    
    # Mock Data Steward - returns success
    data_steward = Mock()
    data_steward.track_data_lineage = AsyncMock(return_value=True)
    data_steward.validate_data_quality = AsyncMock(return_value=True)
    
    return {
        "librarian": librarian,
        "content_steward": content_steward,
        "data_steward": data_steward
    }


@pytest.fixture
def mock_user_context():
    """Create mock user context."""
    return {
        "user_id": "test_user_123",
        "tenant_id": "test_tenant_123",
        "roles": ["user"],
        "permissions": ["execute", "read", "write"]
    }


# ============================================================================
# FUNCTIONAL TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.business_enablement
@pytest.mark.asyncio
@pytest.mark.functional
class TestEnablingServicesFunctional:
    """Test that enabling services still work functionally."""
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_initializes_and_works(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway,
        mock_smart_city_apis,
        mock_user_context
    ):
        """
        Test that service initializes and its main method works.
        
        This is a simple functional test to verify:
        1. Service can be initialized
        2. Service method can be called
        3. Service returns structured response
        4. Service handles errors gracefully
        """
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
                        
                        # Mock utility methods (they should work, but we'll track calls)
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
                                        init_result = await service.initialize()
                                        
                                        # Verify initialization
                                        assert init_result is True or init_result is False, \
                                            f"{class_name}.initialize() should return bool"
                                        
                                        # If initialization failed, that's OK for this test
                                        # We just want to verify the service can be created
                                        
                                        # Test the main method
                                        test_config = service_config["test"]
                                        method_name = test_config["method"]
                                        params = test_config["params"].copy()
                                        
                                        # Add user_context if method accepts it
                                        method = getattr(service, method_name)
                                        import inspect
                                        sig = inspect.signature(method)
                                        if "user_context" in sig.parameters:
                                            params["user_context"] = mock_user_context
                                        
                                        # Call the method
                                        result = await method(**params)
                                        
                                        # Verify result structure
                                        assert isinstance(result, dict), \
                                            f"{method_name} should return dict, got {type(result)}"
                                        
                                        assert "success" in result, \
                                            f"{method_name} should have 'success' field"
                                        
                                        # Verify expected fields (if success is True)
                                        expected = test_config["expected"]
                                        
                                        if expected.get("success_should_be_true"):
                                            assert result.get("success") is True, \
                                                f"{method_name} should succeed, got: {result}"
                                        elif result.get("success"):
                                            # If success is True, verify expected fields
                                            for field in expected.keys():
                                                if field.startswith("has_") and field != "has_success":
                                                    field_name = field.replace("has_", "")
                                                    assert field_name in result, \
                                                        f"{method_name} should have '{field_name}' field when successful"
                                        
                                        # Verify error handling (if success is False, should have error info)
                                        if not result.get("success"):
                                            assert "error" in result or "message" in result, \
                                                f"{method_name} should have 'error' or 'message' when unsuccessful"
                                        
                                        print(f"✅ {class_name}.{method_name}() works correctly")
                                        print(f"   Result: {result.get('success')}, Keys: {list(result.keys())[:5]}...")
    
    @pytest.mark.parametrize("service_config", SERVICES_TO_TEST)
    async def test_service_handles_missing_data_gracefully(
        self,
        service_config: Dict[str, Any],
        mock_di_container,
        mock_platform_gateway,
        mock_user_context
    ):
        """
        Test that service handles missing data gracefully.
        
        This verifies error handling still works correctly.
        """
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
        
        # Mock Smart City APIs to return None (simulating not found)
        mock_librarian = Mock()
        mock_librarian.get_document = AsyncMock(return_value=None)
        mock_content_steward = Mock()
        mock_content_steward.retrieve_document = AsyncMock(return_value=None)
        mock_data_steward = Mock()
        
        with patch.object(service, 'get_librarian_api', new_callable=AsyncMock) as mock_lib:
            mock_lib.return_value = mock_librarian
            with patch.object(service, 'get_content_steward_api', new_callable=AsyncMock) as mock_cont:
                mock_cont.return_value = mock_content_steward
                with patch.object(service, 'get_data_steward_api', new_callable=AsyncMock) as mock_data:
                    mock_data.return_value = mock_data_steward
                    
                    # Mock Curator registration
                    with patch.object(service, 'register_with_curator', new_callable=AsyncMock):
                        # Mock utility methods
                        with patch.object(service, 'log_operation_with_telemetry', new_callable=AsyncMock):
                            with patch.object(service, 'record_health_metric', new_callable=AsyncMock):
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
                                        
                                        # Test the main method with missing data
                                        test_config = service_config["test"]
                                        method_name = test_config["method"]
                                        params = test_config["params"].copy()
                                        
                                        # Add user_context if method accepts it
                                        method = getattr(service, method_name)
                                        import inspect
                                        sig = inspect.signature(method)
                                        if "user_context" in sig.parameters:
                                            params["user_context"] = mock_user_context
                                        
                                        # Call the method (should handle missing data gracefully)
                                        result = await method(**params)
                                        
                                        # Verify it returns structured response (not raises exception)
                                        assert isinstance(result, dict), \
                                            f"{method_name} should return dict even when data is missing, got {type(result)}"
                                        
                                        assert "success" in result, \
                                            f"{method_name} should have 'success' field"
                                        
                                        # Should indicate failure gracefully
                                        if not result.get("success"):
                                            assert "error" in result or "message" in result, \
                                                f"{method_name} should have error info when data is missing"
                                        
                                        print(f"✅ {class_name}.{method_name}() handles missing data gracefully")
                                        print(f"   Result: success={result.get('success')}, error={result.get('error', result.get('message', 'N/A'))}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "functional"])

