#!/usr/bin/env python3
"""
File Parser Service Refactored - Comprehensive Test

Tests that the refactored file_parser_service:
1. Uses full utility pattern (telemetry, security, tenant, error handling, health metrics)
2. Uses Phase 2 Curator registration pattern
3. Provides equivalent or better functionality than prior version
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Dict, Any, Optional

# Mock the DIContainerService and its dependencies
class MockDIContainerService:
    def __init__(self, name="test"):
        self.name = name
        self._services = {}
        self._utilities = {}
        self.logger = MagicMock()
        self.logger.info = MagicMock()
        self.logger.warning = MagicMock()
        self.logger.error = MagicMock()
        
        # Mock utility services
        self.mock_security_utility = MagicMock()
        self.mock_security_utility.check_permissions = AsyncMock(return_value=True)
        self.mock_tenant_utility = MagicMock()
        self.mock_tenant_utility.validate_tenant_access = AsyncMock(return_value=True)
        self.mock_telemetry_utility = MagicMock()
        self.mock_telemetry_utility.log_operation_with_telemetry = AsyncMock()
        self.mock_error_handler_utility = MagicMock()
        self.mock_error_handler_utility.handle_error_with_audit = AsyncMock()
        self.mock_health_utility = MagicMock()
        self.mock_health_utility.record_health_metric = AsyncMock()
        
        self._utilities["security_authorization_utility"] = self.mock_security_utility
        self._utilities["tenant_management_utility"] = self.mock_tenant_utility
        self._utilities["telemetry_reporting_utility"] = self.mock_telemetry_utility
        self._utilities["error_handler"] = self.mock_error_handler_utility
        self._utilities["health_management_utility"] = self.mock_health_utility

    def get_logger(self, name):
        return self.logger

    def get_utility(self, utility_name: str):
        return self._utilities.get(utility_name)

    def get_service(self, service_name: str):
        return self._services.get(service_name)

    def register_service(self, service_name: str, service_instance: Any):
        self._services[service_name] = service_instance

    def get_foundation_service(self, name: str):
        return self._services.get(name)


# Mock Public Works Foundation
class MockPublicWorksFoundation:
    def __init__(self):
        self.is_initialized = True
        self._abstractions = {}
        
        # Mock document intelligence abstraction
        self.mock_document_intelligence = MagicMock()
        from bases.contracts.document_intelligence import DocumentProcessingResult, DocumentChunk, DocumentEntity
        from datetime import datetime
        
        # Mock successful processing result
        mock_result = DocumentProcessingResult(
            result_id="test_result_123",
            filename="test.pdf",
            success=True,
            text_length=100,
            chunks=[
                DocumentChunk(
                    chunk_id="chunk_1",
                    text="Sample text content",
                    start_position=0,
                    end_position=20,
                    length=20
                )
            ],
            entities=[
                DocumentEntity(
                    entity_id="entity_1",
                    text="Sample Entity",
                    label="PERSON",
                    start_position=0,
                    end_position=14,
                    confidence=0.95
                )
            ],
            metadata={"file_type": "pdf", "page_count": 1},
            timestamp=datetime.utcnow()
        )
        self.mock_document_intelligence.process_document = AsyncMock(return_value=mock_result)
        self._abstractions["document_intelligence"] = self.mock_document_intelligence

    def get_abstraction(self, name: str):
        return self._abstractions.get(name)


# Mock Platform Gateway
class MockPlatformGateway:
    def __init__(self, public_works=None):
        self.public_works = public_works or MockPublicWorksFoundation()
    
    def get_abstraction(self, realm_name: str, abstraction_name: str):
        return self.public_works.get_abstraction(abstraction_name)


# Mock Smart City Services
class MockContentSteward:
    def __init__(self):
        self.get_file = AsyncMock(return_value={
            "file_id": "test_file_123",
            "filename": "test.pdf",
            "data": b"%PDF-1.4\nSample PDF content",
            "metadata": {
                "file_type": "pdf",
                "size": 100,
                "content_type": "application/pdf"
            }
        })


class MockLibrarian:
    def __init__(self):
        self.search_knowledge = AsyncMock(return_value={"results": []})


class MockDataSteward:
    def __init__(self):
        self.get_policy_for_content = AsyncMock(return_value={"policy": {}})


@pytest.fixture
def mock_di_container():
    """Fixture to provide a mocked DI container."""
    return MockDIContainerService()


@pytest.fixture
def mock_platform_gateway():
    """Fixture to provide a mocked platform gateway."""
    return MockPlatformGateway()


@pytest.fixture
def mock_content_steward():
    """Fixture to provide a mocked Content Steward."""
    return MockContentSteward()


@pytest.fixture
def mock_librarian():
    """Fixture to provide a mocked Librarian."""
    return MockLibrarian()


@pytest.fixture
def mock_data_steward():
    """Fixture to provide a mocked Data Steward."""
    return MockDataSteward()


@pytest.fixture
async def file_parser_service(mock_di_container, mock_platform_gateway, mock_content_steward, mock_librarian, mock_data_steward):
    """Fixture to provide a File Parser Service instance."""
    from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
    
    service = FileParserService(
        service_name="FileParserService",
        realm_name="business_enablement",
        platform_gateway=mock_platform_gateway,
        di_container=mock_di_container
    )
    
    # Mock Smart City services
    service.content_steward = mock_content_steward
    service.librarian = mock_librarian
    service.data_steward = mock_data_steward
    
    # Mock utility access methods (from mixins)
    service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
    service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
    service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
    service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
    service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
    
    # Mock Curator
    service.get_curator = MagicMock(return_value=MagicMock())
    service.get_librarian_api = AsyncMock(return_value=mock_librarian)
    service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
    service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
    
    # Mock register_with_curator
    service.register_with_curator = AsyncMock(return_value=True)
    
    # Mock retrieve_document to return valid document
    service.retrieve_document = AsyncMock(return_value={
        "file_id": "test_file_123",
        "filename": "test.pdf",
        "data": b"%PDF-1.4\nSample PDF content",
        "metadata": {
            "file_type": "pdf",
            "size": 100,
            "content_type": "application/pdf"
        }
    })
    
    # Initialize service
    await service.initialize()
    
    return service


class TestFileParserUtilityUsage:
    """Test that file_parser_service uses utilities correctly."""
    
    @pytest.mark.asyncio
    async def test_initialize_uses_telemetry(self, file_parser_service, mock_di_container):
        """Test that initialize() uses telemetry utilities."""
        # Reset mocks
        mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_di_container.mock_health_utility.record_health_metric.reset_mock()
        
        # Re-initialize to trigger telemetry
        await file_parser_service.initialize()
        
        # Verify telemetry was called (start and complete)
        assert mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "initialize() should call log_operation_with_telemetry at least twice (start and complete)"
        
        # Check for start call
        start_calls = [c for c in mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_args_list 
                      if "start" in str(c)]
        assert len(start_calls) > 0, "Should have telemetry start call"
        
        # Check for complete call
        complete_calls = [c for c in mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_args_list 
                         if "complete" in str(c)]
        assert len(complete_calls) > 0, "Should have telemetry complete call"
        
        # Verify health metric was recorded
        assert mock_di_container.mock_health_utility.record_health_metric.called, \
            "initialize() should record health metric"
    
    @pytest.mark.asyncio
    async def test_parse_file_uses_telemetry(self, file_parser_service, mock_di_container):
        """Test that parse_file() uses telemetry utilities."""
        # Reset mocks
        mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_di_container.mock_health_utility.record_health_metric.reset_mock()
        
        # Call parse_file
        result = await file_parser_service.parse_file("test_file_123")
        
        # Verify telemetry was called (start and complete)
        assert mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "parse_file() should call log_operation_with_telemetry at least twice (start and complete)"
        
        # Verify health metric was recorded
        assert mock_di_container.mock_health_utility.record_health_metric.called, \
            "parse_file() should record health metric"
    
    @pytest.mark.asyncio
    async def test_parse_file_uses_security_validation(self, mock_di_container, mock_platform_gateway, mock_content_steward, mock_librarian, mock_data_steward):
        """Test that parse_file() validates security."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = mock_content_steward
        service.librarian = mock_librarian
        service.data_steward = mock_data_steward
        
        # Mock utility access methods (from mixins)
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock Curator and APIs
        service.get_curator = MagicMock(return_value=MagicMock())
        service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        service.register_with_curator = AsyncMock(return_value=True)
        service.retrieve_document = AsyncMock(return_value={
            "file_id": "test_file_123",
            "filename": "test.pdf",
            "data": b"%PDF-1.4\nSample PDF content",
            "metadata": {"file_type": "pdf"}
        })
        
        await service.initialize()
        
        # Reset and set security to deny access
        mock_di_container.mock_security_utility.check_permissions.reset_mock()
        mock_di_container.mock_security_utility.check_permissions.return_value = False
        
        # Ensure get_security returns the mock
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        
        user_context = {"user_id": "unauthorized_user", "tenant_id": "test_tenant"}
        
        # Call parse_file with user_context
        with pytest.raises(PermissionError, match="Access denied"):
            await service.parse_file("test_file_123", user_context=user_context)
        
        # Verify security was checked
        assert mock_di_container.mock_security_utility.check_permissions.called, \
            "parse_file() should check permissions when user_context is provided"
        
        call_args = mock_di_container.mock_security_utility.check_permissions.call_args
        assert call_args[0][0] == user_context, "Should pass user_context to security check"
        assert call_args[0][1] == "file_parsing", "Should check 'file_parsing' resource"
        assert call_args[0][2] == "execute", "Should check 'execute' action"
    
    @pytest.mark.asyncio
    async def test_parse_file_uses_tenant_validation(self, mock_di_container, mock_platform_gateway, mock_content_steward, mock_librarian, mock_data_steward):
        """Test that parse_file() validates tenant access."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = mock_content_steward
        service.librarian = mock_librarian
        service.data_steward = mock_data_steward
        
        # Mock utility access methods (from mixins)
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock Curator and APIs
        service.get_curator = MagicMock(return_value=MagicMock())
        service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        service.register_with_curator = AsyncMock(return_value=True)
        service.retrieve_document = AsyncMock(return_value={
            "file_id": "test_file_123",
            "filename": "test.pdf",
            "data": b"%PDF-1.4\nSample PDF content",
            "metadata": {"file_type": "pdf"}
        })
        
        await service.initialize()
        
        # Set tenant to deny access
        mock_di_container.mock_tenant_utility.validate_tenant_access.return_value = False
        mock_di_container.mock_tenant_utility.validate_tenant_access.reset_mock()
        
        user_context = {"user_id": "test_user", "tenant_id": "unauthorized_tenant"}
        
        # Call parse_file with user_context
        with pytest.raises(PermissionError, match="Tenant access denied"):
            await service.parse_file("test_file_123", user_context=user_context)
        
        # Verify tenant was validated
        assert mock_di_container.mock_tenant_utility.validate_tenant_access.called, \
            "parse_file() should validate tenant access when user_context is provided"
        
        call_args = mock_di_container.mock_tenant_utility.validate_tenant_access.call_args
        assert call_args[0][0] == "unauthorized_tenant", "Should pass tenant_id to tenant validation"
    
    @pytest.mark.asyncio
    async def test_parse_file_uses_error_handling(self, mock_di_container, mock_platform_gateway, mock_content_steward, mock_librarian, mock_data_steward):
        """Test that parse_file() uses error handling."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = mock_content_steward
        service.librarian = mock_librarian
        service.data_steward = mock_data_steward
        
        # Mock utility access methods (from mixins)
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock Curator and APIs
        service.get_curator = MagicMock(return_value=MagicMock())
        service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        service.register_with_curator = AsyncMock(return_value=True)
        
        await service.initialize()
        
        # Reset mocks
        mock_di_container.mock_error_handler_utility.handle_error_with_audit.reset_mock()
        
        # Force an actual exception
        service.retrieve_document = AsyncMock(side_effect=Exception("Test error"))
        
        try:
            await service.parse_file("test_file_123")
        except Exception:
            pass
        
        # Verify error handling was called
        assert mock_di_container.mock_error_handler_utility.handle_error_with_audit.called, \
            "parse_file() should use error handling when exceptions occur"
    
    @pytest.mark.asyncio
    async def test_detect_file_type_uses_utilities(self, file_parser_service, mock_di_container):
        """Test that detect_file_type() uses utilities."""
        # Reset mocks
        mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_di_container.mock_health_utility.record_health_metric.reset_mock()
        
        # Call detect_file_type
        result = await file_parser_service.detect_file_type("test_file_123")
        
        # Verify telemetry was called
        assert mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "detect_file_type() should call log_operation_with_telemetry (start and complete)"
        
        # Verify health metric was recorded
        assert mock_di_container.mock_health_utility.record_health_metric.called, \
            "detect_file_type() should record health metric"


class TestFileParserCuratorRegistration:
    """Test that file_parser_service registers with Curator correctly."""
    
    @pytest.mark.asyncio
    async def test_register_with_curator_called(self, file_parser_service):
        """Test that register_with_curator() is called during initialization."""
        assert file_parser_service.register_with_curator.called, \
            "register_with_curator() should be called during initialization"
    
    @pytest.mark.asyncio
    async def test_curator_registration_uses_phase2_pattern(self, file_parser_service):
        """Test that Curator registration uses Phase 2 pattern (CapabilityDefinition structure)."""
        # Get the call arguments
        call_args = file_parser_service.register_with_curator.call_args
        
        # Verify capabilities is a list
        assert "capabilities" in call_args.kwargs, "Should pass 'capabilities' to register_with_curator"
        capabilities = call_args.kwargs["capabilities"]
        assert isinstance(capabilities, list), "Capabilities should be a list"
        assert len(capabilities) > 0, "Should have at least one capability"
        
        # Verify each capability has the Phase 2 structure
        for capability in capabilities:
            assert "name" in capability, "Capability should have 'name' field"
            assert "protocol" in capability, "Capability should have 'protocol' field"
            assert "contracts" in capability, "Capability should have 'contracts' field (Phase 2 pattern)"
            assert "soa_api" in capability["contracts"], "Capability should have 'soa_api' contract"
            
            # Verify soa_api structure
            soa_api = capability["contracts"]["soa_api"]
            assert "api_name" in soa_api, "soa_api should have 'api_name'"
            assert "endpoint" in soa_api, "soa_api should have 'endpoint'"
            assert "method" in soa_api, "soa_api should have 'method'"
            assert "handler" in soa_api, "soa_api should have 'handler'"
    
    @pytest.mark.asyncio
    async def test_all_capabilities_registered(self, file_parser_service):
        """Test that all expected capabilities are registered."""
        call_args = file_parser_service.register_with_curator.call_args
        capabilities = call_args.kwargs["capabilities"]
        
        capability_names = [c["name"] for c in capabilities]
        
        # Verify expected capabilities
        assert "file_parsing" in capability_names, "Should register 'file_parsing' capability"
        assert "format_detection" in capability_names, "Should register 'format_detection' capability"
        assert "content_extraction" in capability_names, "Should register 'content_extraction' capability"
        assert "metadata_extraction" in capability_names, "Should register 'metadata_extraction' capability"
        assert "get_supported_formats" in capability_names, "Should register 'get_supported_formats' capability"


class TestFileParserFunctionalEquivalence:
    """Test that file_parser_service provides equivalent functionality."""
    
    @pytest.mark.asyncio
    async def test_parse_file_returns_expected_structure(self, file_parser_service):
        """Test that parse_file() returns expected structure."""
        result = await file_parser_service.parse_file("test_file_123")
        
        # Verify result structure
        assert isinstance(result, dict), "parse_file() should return a dict"
        assert "success" in result, "Result should have 'success' field"
        assert result["success"] is True, "parse_file() should succeed with valid file"
        assert "file_id" in result, "Result should have 'file_id' field"
        assert "parsed_document_id" in result, "Result should have 'parsed_document_id' field"
        assert "file_type" in result, "Result should have 'file_type' field"
        assert "content" in result, "Result should have 'content' field"
        assert "structure" in result, "Result should have 'structure' field"
        assert "metadata" in result, "Result should have 'metadata' field"
    
    @pytest.mark.asyncio
    async def test_parse_file_handles_file_not_found(self, file_parser_service):
        """Test that parse_file() handles file not found gracefully."""
        # Make retrieve_document return None
        file_parser_service.retrieve_document = AsyncMock(return_value=None)
        
        result = await file_parser_service.parse_file("nonexistent_file")
        
        # Verify graceful failure
        assert isinstance(result, dict), "parse_file() should return a dict even on failure"
        assert result["success"] is False, "parse_file() should indicate failure"
        assert "message" in result, "Result should have 'message' field"
        assert "file not found" in result["message"].lower(), "Should indicate file not found"
    
    @pytest.mark.asyncio
    async def test_detect_file_type_returns_string(self, file_parser_service):
        """Test that detect_file_type() returns a string."""
        result = await file_parser_service.detect_file_type("test_file_123")
        
        # Verify result
        assert isinstance(result, str), "detect_file_type() should return a string"
        assert result in file_parser_service.supported_formats or result == "unknown", \
            "detect_file_type() should return a supported format or 'unknown'"
    
    @pytest.mark.asyncio
    async def test_get_supported_formats_returns_list(self, file_parser_service):
        """Test that get_supported_formats() returns expected structure."""
        result = await file_parser_service.get_supported_formats()
        
        # Verify result structure
        assert isinstance(result, dict), "get_supported_formats() should return a dict"
        assert "formats" in result or "supported_formats" in result, \
            "Result should have 'formats' or 'supported_formats' field"
        
        formats = result.get("formats") or result.get("supported_formats", [])
        assert isinstance(formats, list), "Formats should be a list"
        assert len(formats) > 0, "Should have at least one supported format"


class TestFileParserImprovements:
    """Test that refactored version provides improvements."""
    
    @pytest.mark.asyncio
    async def test_user_context_support(self, file_parser_service):
        """Test that methods support user_context parameter."""
        # Verify parse_file accepts user_context
        result = await file_parser_service.parse_file("test_file_123", user_context={"user_id": "test_user"})
        assert result["success"] is True, "parse_file() should work with user_context"
        
        # Verify detect_file_type accepts user_context
        result = await file_parser_service.detect_file_type("test_file_123", user_context={"user_id": "test_user"})
        assert isinstance(result, str), "detect_file_type() should work with user_context"
    
    @pytest.mark.asyncio
    async def test_security_enforcement(self, mock_di_container, mock_platform_gateway, mock_content_steward, mock_librarian, mock_data_steward):
        """Test that security is enforced when user_context is provided."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = mock_content_steward
        service.librarian = mock_librarian
        service.data_steward = mock_data_steward
        
        # Mock utility access methods (from mixins)
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock Curator and APIs
        service.get_curator = MagicMock(return_value=MagicMock())
        service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        service.register_with_curator = AsyncMock(return_value=True)
        service.retrieve_document = AsyncMock(return_value={
            "file_id": "test_file_123",
            "filename": "test.pdf",
            "data": b"%PDF-1.4\nSample PDF content",
            "metadata": {"file_type": "pdf"}
        })
        
        await service.initialize()
        
        # Reset and set security to deny
        mock_di_container.mock_security_utility.check_permissions.reset_mock()
        mock_di_container.mock_security_utility.check_permissions.return_value = False
        
        # Ensure get_security returns the mock
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        
        user_context = {"user_id": "unauthorized_user"}
        
        # Should raise PermissionError
        with pytest.raises(PermissionError):
            await service.parse_file("test_file_123", user_context=user_context)
    
    @pytest.mark.asyncio
    async def test_tenant_isolation(self, mock_di_container, mock_platform_gateway, mock_content_steward, mock_librarian, mock_data_steward):
        """Test that tenant isolation is enforced."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=mock_platform_gateway,
            di_container=mock_di_container
        )
        
        # Mock Smart City services
        service.content_steward = mock_content_steward
        service.librarian = mock_librarian
        service.data_steward = mock_data_steward
        
        # Mock utility access methods (from mixins)
        service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock Curator and APIs
        service.get_curator = MagicMock(return_value=MagicMock())
        service.get_librarian_api = AsyncMock(return_value=mock_librarian)
        service.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        service.get_data_steward_api = AsyncMock(return_value=mock_data_steward)
        service.register_with_curator = AsyncMock(return_value=True)
        service.retrieve_document = AsyncMock(return_value={
            "file_id": "test_file_123",
            "filename": "test.pdf",
            "data": b"%PDF-1.4\nSample PDF content",
            "metadata": {"file_type": "pdf"}
        })
        
        await service.initialize()
        
        # Reset and set tenant to deny
        mock_di_container.mock_tenant_utility.validate_tenant_access.reset_mock()
        mock_di_container.mock_tenant_utility.validate_tenant_access.return_value = False
        
        # Ensure get_tenant returns the mock
        service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        
        user_context = {"user_id": "test_user", "tenant_id": "unauthorized_tenant"}
        
        # Should raise PermissionError
        with pytest.raises(PermissionError, match="Tenant access denied"):
            await service.parse_file("test_file_123", user_context=user_context)

