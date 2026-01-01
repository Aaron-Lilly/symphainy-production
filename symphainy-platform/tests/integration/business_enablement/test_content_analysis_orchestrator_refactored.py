#!/usr/bin/env python3
"""
Content Analysis Orchestrator Refactored - Comprehensive Test

Tests that the refactored ContentAnalysisOrchestrator:
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


# Mock Platform Gateway
class MockPlatformGateway:
    def __init__(self):
        pass
    
    def get_abstraction(self, realm_name: str, abstraction_name: str):
        return None


# Mock Delivery Manager
class MockDeliveryManager:
    def __init__(self, di_container, platform_gateway):
        self.realm_name = "business_enablement"
        self.platform_gateway = platform_gateway
        self.di_container = di_container
        self.session_manager = None


# Mock Enabling Services
class MockFileParserService:
    def __init__(self):
        self.parse_file = AsyncMock(return_value={
            "success": True,
            "file_id": "test_file_123",
            "parsed_document_id": "parsed_123",
            "file_type": "pdf",
            "content": "Sample content",
            "structure": {"chunks": 1, "entities": 0, "page_count": 1},
            "metadata": {},
            "entities": []
        })
        self.extract_metadata = AsyncMock(return_value={
            "success": True,
            "metadata": {"file_type": "pdf", "size": 100}
        })


class MockDataAnalyzerService:
    def __init__(self):
        self.extract_entities = AsyncMock(return_value={
            "success": True,
            "entities": [
                {"text": "Entity 1", "label": "PERSON", "confidence": 0.95}
            ]
        })


# Mock Smart City Services
class MockContentSteward:
    def __init__(self):
        self.process_upload = AsyncMock(return_value={
            "success": True,
            "uuid": "file_uuid_123",
            "file_id": "file_uuid_123"
        })


class MockLibrarian:
    def __init__(self):
        self.query_documents = AsyncMock(return_value={
            "documents": [
                {
                    "uuid": "file_123",
                    "file_id": "file_123",
                    "ui_name": "test.pdf",
                    "original_filename": "test.pdf",
                    "file_type": "pdf",
                    "mime_type": "application/pdf",
                    "content_type": "unstructured",
                    "size_bytes": 100,
                    "uploaded_at": "2024-01-01T00:00:00",
                    "parsed": False
                }
            ]
        })
        self.get_document = AsyncMock(return_value={
            "uuid": "file_123",
            "file_id": "file_123",
            "ui_name": "test.pdf",
            "original_filename": "test.pdf",
            "file_type": "pdf",
            "mime_type": "application/pdf",
            "content_type": "unstructured",
            "size_bytes": 100,
            "uploaded_at": "2024-01-01T00:00:00",
            "parsed": False,
            "metadata": {},
            "parse_result": {}
        })


@pytest.fixture
def mock_di_container():
    """Fixture to provide a mocked DI container."""
    return MockDIContainerService()


@pytest.fixture
def mock_platform_gateway():
    """Fixture to provide a mocked platform gateway."""
    return MockPlatformGateway()


@pytest.fixture
def mock_delivery_manager(mock_di_container, mock_platform_gateway):
    """Fixture to provide a mocked delivery manager."""
    return MockDeliveryManager(mock_di_container, mock_platform_gateway)


@pytest.fixture
def mock_file_parser_service():
    """Fixture to provide a mocked File Parser Service."""
    return MockFileParserService()


@pytest.fixture
def mock_data_analyzer_service():
    """Fixture to provide a mocked Data Analyzer Service."""
    return MockDataAnalyzerService()


@pytest.fixture
def mock_content_steward():
    """Fixture to provide a mocked Content Steward."""
    return MockContentSteward()


@pytest.fixture
def mock_librarian():
    """Fixture to provide a mocked Librarian."""
    return MockLibrarian()


@pytest.fixture
def content_analysis_orchestrator(mock_di_container, mock_platform_gateway, mock_delivery_manager, mock_file_parser_service, mock_data_analyzer_service, mock_content_steward, mock_librarian):
    """Fixture to provide a Content Analysis Orchestrator instance (not initialized)."""
    from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
    
    orchestrator = ContentAnalysisOrchestrator(mock_delivery_manager)
    
    # Mock utility access methods (via _realm_service)
    orchestrator._realm_service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
    orchestrator._realm_service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
    orchestrator._realm_service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
    orchestrator._realm_service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
    orchestrator._realm_service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
    
    # Mock Curator
    orchestrator._realm_service.get_curator = MagicMock(return_value=MagicMock())
    orchestrator._realm_service.register_with_curator = AsyncMock(return_value=True)
    
    # Mock enabling service discovery
    orchestrator.get_enabling_service = AsyncMock(side_effect=lambda name: {
        "FileParserService": mock_file_parser_service,
        "DataAnalyzerService": mock_data_analyzer_service
    }.get(name))
    
    # Mock Smart City services
    orchestrator.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
    orchestrator.get_librarian_api = AsyncMock(return_value=mock_librarian)
    orchestrator.track_data_lineage = AsyncMock(return_value=True)
    
    # Mock agent initialization (skip actual agent creation for tests)
    orchestrator.initialize_agent = AsyncMock(return_value=MagicMock())
    
    # Mock MCP server (create a mock instance)
    mock_mcp_server = MagicMock()
    orchestrator.mcp_server = mock_mcp_server
    
    # Mock super().initialize() to avoid RealmServiceBase initialization issues
    orchestrator._realm_service.initialize = AsyncMock(return_value=True)
    
    # Store lazy service getters
    orchestrator._file_parser_service = mock_file_parser_service
    orchestrator._data_analyzer_service = mock_data_analyzer_service
    
    return orchestrator


class TestOrchestratorUtilityUsage:
    """Test that ContentAnalysisOrchestrator uses utilities correctly."""
    
    @pytest.mark.asyncio
    async def test_initialize_uses_telemetry(self, content_analysis_orchestrator, mock_di_container):
        """Test that initialize() uses telemetry utilities."""
        # Reset mocks
        mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_di_container.mock_health_utility.record_health_metric.reset_mock()
        
        # Mock MCP server import
        with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator.ContentAnalysisMCPServer') as mock_mcp_class:
            mock_mcp_server = MagicMock()
            mock_mcp_class.return_value = mock_mcp_server
            content_analysis_orchestrator.mcp_server = mock_mcp_server
            
            # Initialize to trigger telemetry
            await content_analysis_orchestrator.initialize()
        
        # Verify telemetry was called (start and complete)
        assert mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "initialize() should call log_operation_with_telemetry at least twice (start and complete)"
        
        # Verify health metric was recorded
        assert mock_di_container.mock_health_utility.record_health_metric.called, \
            "initialize() should record health metric"
    
    @pytest.mark.asyncio
    async def test_analyze_document_uses_telemetry(self, content_analysis_orchestrator, mock_di_container):
        """Test that analyze_document() uses telemetry utilities."""
        # Reset mocks
        mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_di_container.mock_health_utility.record_health_metric.reset_mock()
        
        # Call analyze_document
        result = await content_analysis_orchestrator.analyze_document("test_doc_123", ["structure"])
        
        # Verify telemetry was called (start and complete)
        assert mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "analyze_document() should call log_operation_with_telemetry at least twice (start and complete)"
        
        # Verify health metric was recorded
        assert mock_di_container.mock_health_utility.record_health_metric.called, \
            "analyze_document() should record health metric"
    
    @pytest.mark.asyncio
    async def test_analyze_document_uses_security_validation(self, mock_di_container, mock_platform_gateway, mock_delivery_manager, mock_file_parser_service, mock_data_analyzer_service, mock_content_steward, mock_librarian):
        """Test that analyze_document() validates security."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(mock_delivery_manager)
        
        # Mock utility access methods
        orchestrator._realm_service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        orchestrator._realm_service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        orchestrator._realm_service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        orchestrator._realm_service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        orchestrator._realm_service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock other dependencies
        orchestrator._realm_service.register_with_curator = AsyncMock(return_value=True)
        orchestrator.get_enabling_service = AsyncMock(side_effect=lambda name: {
            "FileParserService": mock_file_parser_service,
            "DataAnalyzerService": mock_data_analyzer_service
        }.get(name))
        orchestrator.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        orchestrator.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator.track_data_lineage = AsyncMock(return_value=True)
        orchestrator.initialize_agent = AsyncMock(return_value=MagicMock())
        
        with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator.ContentAnalysisMCPServer'):
            await orchestrator.initialize()
        
        # Set security to deny access
        mock_di_container.mock_security_utility.check_permissions.reset_mock()
        mock_di_container.mock_security_utility.check_permissions.return_value = False
        
        # Ensure get_security returns the mock
        orchestrator._realm_service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        
        user_context = {"user_id": "unauthorized_user", "tenant_id": "test_tenant"}
        
        # Call analyze_document with user_context
        with pytest.raises(PermissionError, match="Access denied"):
            await orchestrator.analyze_document("test_doc_123", ["structure"], user_context=user_context)
        
        # Verify security was checked
        assert mock_di_container.mock_security_utility.check_permissions.called, \
            "analyze_document() should check permissions when user_context is provided"
    
    @pytest.mark.asyncio
    async def test_parse_file_uses_telemetry(self, content_analysis_orchestrator, mock_di_container):
        """Test that parse_file() uses telemetry utilities."""
        # Reset mocks
        mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.reset_mock()
        mock_di_container.mock_health_utility.record_health_metric.reset_mock()
        
        # Call parse_file
        result = await content_analysis_orchestrator.parse_file("test_file_123")
        
        # Verify telemetry was called
        assert mock_di_container.mock_telemetry_utility.log_operation_with_telemetry.call_count >= 2, \
            "parse_file() should call log_operation_with_telemetry (start and complete)"
        
        # Verify health metric was recorded
        assert mock_di_container.mock_health_utility.record_health_metric.called, \
            "parse_file() should record health metric"


class TestOrchestratorCuratorRegistration:
    """Test that ContentAnalysisOrchestrator registers with Curator correctly."""
    
    @pytest.mark.asyncio
    async def test_register_with_curator_called(self, content_analysis_orchestrator):
        """Test that register_with_curator() is called during initialization."""
        # Reset the mock to track calls
        content_analysis_orchestrator._realm_service.register_with_curator.reset_mock()
        
        # Mock MCP server import by patching the module attribute
        import sys
        module_path = 'backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator'
        if module_path in sys.modules:
            original_mcp = getattr(sys.modules[module_path], 'ContentAnalysisMCPServer', None)
            mock_mcp_server = MagicMock()
            sys.modules[module_path].ContentAnalysisMCPServer = MagicMock(return_value=mock_mcp_server)
            content_analysis_orchestrator.mcp_server = mock_mcp_server
            
            try:
                # Initialize
                await content_analysis_orchestrator.initialize()
            finally:
                # Restore original if it existed
                if original_mcp:
                    sys.modules[module_path].ContentAnalysisMCPServer = original_mcp
        
        assert content_analysis_orchestrator._realm_service.register_with_curator.called, \
            "register_with_curator() should be called during initialization"
    
    @pytest.mark.asyncio
    async def test_curator_registration_uses_phase2_pattern(self, content_analysis_orchestrator):
        """Test that Curator registration uses Phase 2 pattern (CapabilityDefinition structure)."""
        # Get the call arguments
        call_args = content_analysis_orchestrator._realm_service.register_with_curator.call_args
        
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
    async def test_all_capabilities_registered(self, content_analysis_orchestrator):
        """Test that all expected capabilities are registered."""
        call_args = content_analysis_orchestrator._realm_service.register_with_curator.call_args
        capabilities = call_args.kwargs["capabilities"]
        
        capability_names = [c["name"] for c in capabilities]
        
        # Verify expected capabilities
        assert "file_upload" in capability_names, "Should register 'file_upload' capability"
        assert "file_parsing" in capability_names, "Should register 'file_parsing' capability"
        assert "content_analysis" in capability_names, "Should register 'content_analysis' capability"
        assert "entity_extraction" in capability_names, "Should register 'entity_extraction' capability"
    
    @pytest.mark.asyncio
    async def test_mcp_tools_registered(self, content_analysis_orchestrator):
        """Test that MCP tools are registered in capability contracts."""
        call_args = content_analysis_orchestrator._realm_service.register_with_curator.call_args
        capabilities = call_args.kwargs["capabilities"]
        
        # Check that at least one capability has mcp_tool contract
        has_mcp_tool = any("mcp_tool" in c.get("contracts", {}) for c in capabilities)
        assert has_mcp_tool, "At least one capability should have 'mcp_tool' contract"


class TestOrchestratorFunctionalEquivalence:
    """Test that ContentAnalysisOrchestrator provides equivalent functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_document_returns_expected_structure(self, content_analysis_orchestrator):
        """Test that analyze_document() returns expected structure."""
        result = await content_analysis_orchestrator.analyze_document("test_doc_123", ["structure", "metadata", "entities"])
        
        # Verify result structure
        assert isinstance(result, dict), "analyze_document() should return a dict"
        assert "status" in result, "Result should have 'status' field"
        assert "resource_id" in result, "Result should have 'resource_id' field"
        assert "data" in result, "Result should have 'data' field"
        assert "orchestrator" in result, "Result should have 'orchestrator' field"
    
    @pytest.mark.asyncio
    async def test_parse_file_returns_expected_structure(self, content_analysis_orchestrator):
        """Test that parse_file() returns expected structure."""
        result = await content_analysis_orchestrator.parse_file("test_file_123")
        
        # Verify result structure
        assert isinstance(result, dict), "parse_file() should return a dict"
        assert "status" in result, "Result should have 'status' field"
        assert "resource_id" in result, "Result should have 'resource_id' field"
        assert "data" in result, "Result should have 'data' field"
        assert "parse_result" in result.get("data", {}), "Result should have 'parse_result' in data"
    
    @pytest.mark.asyncio
    async def test_handle_content_upload_returns_expected_structure(self, content_analysis_orchestrator):
        """Test that handle_content_upload() returns expected structure."""
        file_data = b"test file content"
        filename = "test.pdf"
        file_type = "application/pdf"
        
        result = await content_analysis_orchestrator.handle_content_upload(
            file_data=file_data,
            filename=filename,
            file_type=file_type,
            user_id="test_user"
        )
        
        # Verify result structure
        assert isinstance(result, dict), "handle_content_upload() should return a dict"
        assert "success" in result, "Result should have 'success' field"
        if result.get("success"):
            assert "file_id" in result, "Result should have 'file_id' field"
            assert "uuid" in result, "Result should have 'uuid' field"
    
    @pytest.mark.asyncio
    async def test_extract_entities_returns_expected_structure(self, content_analysis_orchestrator):
        """Test that extract_entities() returns expected structure."""
        result = await content_analysis_orchestrator.extract_entities("test_doc_123")
        
        # Verify result structure
        assert isinstance(result, dict), "extract_entities() should return a dict"
        assert "status" in result, "Result should have 'status' field"
        assert "resource_id" in result, "Result should have 'resource_id' field"
        assert "data" in result, "Result should have 'data' field"


class TestOrchestratorImprovements:
    """Test that refactored version provides improvements."""
    
    @pytest.mark.asyncio
    async def test_user_context_support(self, content_analysis_orchestrator):
        """Test that methods support user_context parameter."""
        # Verify analyze_document accepts user_context
        result = await content_analysis_orchestrator.analyze_document(
            "test_doc_123",
            ["structure"],
            user_context={"user_id": "test_user"}
        )
        assert result.get("status") == "success", "analyze_document() should work with user_context"
        
        # Verify parse_file accepts user_context
        result = await content_analysis_orchestrator.parse_file(
            "test_file_123",
            user_context={"user_id": "test_user"}
        )
        assert result.get("status") == "success", "parse_file() should work with user_context"
    
    @pytest.mark.asyncio
    async def test_security_enforcement(self, mock_di_container, mock_platform_gateway, mock_delivery_manager, mock_file_parser_service, mock_data_analyzer_service, mock_content_steward, mock_librarian):
        """Test that security is enforced when user_context is provided."""
        from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
        
        orchestrator = ContentAnalysisOrchestrator(mock_delivery_manager)
        
        # Mock utility access methods
        orchestrator._realm_service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        orchestrator._realm_service.get_tenant = MagicMock(return_value=mock_di_container.mock_tenant_utility)
        orchestrator._realm_service.log_operation_with_telemetry = mock_di_container.mock_telemetry_utility.log_operation_with_telemetry
        orchestrator._realm_service.handle_error_with_audit = mock_di_container.mock_error_handler_utility.handle_error_with_audit
        orchestrator._realm_service.record_health_metric = mock_di_container.mock_health_utility.record_health_metric
        
        # Mock other dependencies
        orchestrator._realm_service.register_with_curator = AsyncMock(return_value=True)
        orchestrator.get_enabling_service = AsyncMock(side_effect=lambda name: {
            "FileParserService": mock_file_parser_service,
            "DataAnalyzerService": mock_data_analyzer_service
        }.get(name))
        orchestrator.get_content_steward_api = AsyncMock(return_value=mock_content_steward)
        orchestrator.get_librarian_api = AsyncMock(return_value=mock_librarian)
        orchestrator.track_data_lineage = AsyncMock(return_value=True)
        orchestrator.initialize_agent = AsyncMock(return_value=MagicMock())
        
        with patch('backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator.ContentAnalysisMCPServer'):
            await orchestrator.initialize()
        
        # Set security to deny
        mock_di_container.mock_security_utility.check_permissions.reset_mock()
        mock_di_container.mock_security_utility.check_permissions.return_value = False
        
        # Ensure get_security returns the mock
        orchestrator._realm_service.get_security = MagicMock(return_value=mock_di_container.mock_security_utility)
        
        user_context = {"user_id": "unauthorized_user"}
        
        # Should raise PermissionError
        with pytest.raises(PermissionError):
            await orchestrator.analyze_document("test_doc_123", ["structure"], user_context=user_context)

