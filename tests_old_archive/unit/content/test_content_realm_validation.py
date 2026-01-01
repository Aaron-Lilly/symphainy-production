#!/usr/bin/env python3
"""
Content Realm Validation Test

Simple validation test to verify Content realm structure works:
- ContentManagerService can be initialized
- Content Orchestrator can be discovered
- Enabling services can be discovered via get_enabling_service()
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any

pytestmark = [pytest.mark.unit, pytest.mark.fast]


class TestContentRealmValidation:
    """Validation tests for Content realm structure."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock()
        container.realm_name = "content"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=Mock())
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=Mock())
        return gateway
    
    @pytest.fixture
    def mock_curator(self):
        """Create mock Curator."""
        curator = Mock()
        curator.registered_services = {}
        curator.discover_service_by_name = AsyncMock(return_value=None)
        return curator
    
    @pytest.mark.asyncio
    async def test_content_manager_service_initialization(self, mock_di_container, mock_platform_gateway):
        """Test that ContentManagerService can be initialized."""
        from backend.content.ContentManagerService.content_manager_service import ContentManagerService
        
        # Create ContentManagerService
        content_manager = ContentManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Verify basic properties
        assert content_manager.service_name == "ContentManagerService"
        assert content_manager.realm_name == "content"
        assert content_manager.manager_type.value == "content_manager"
        assert content_manager.orchestration_scope.value == "realm_only"
        assert content_manager.governance_level.value == "moderate"
        
        # Verify micro-modules are initialized
        assert hasattr(content_manager, 'initialization_module')
        assert hasattr(content_manager, 'soa_mcp_module')
        assert hasattr(content_manager, 'utilities_module')
        
        # Verify state
        assert content_manager.content_orchestrator is None  # Not discovered yet
        assert content_manager.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_content_manager_can_discover_orchestrator(self, mock_di_container, mock_platform_gateway, mock_curator):
        """Test that ContentManagerService can discover Content Orchestrator via Curator."""
        from backend.content.ContentManagerService.content_manager_service import ContentManagerService
        
        # Mock Content Orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.service_name = "ContentAnalysisOrchestratorService"
        mock_orchestrator.realm_name = "content"
        
        # Setup Curator to return orchestrator
        mock_curator.discover_service_by_name = AsyncMock(return_value=mock_orchestrator)
        mock_di_container.get_foundation_service = Mock(return_value=mock_curator)
        
        # Create ContentManagerService
        content_manager = ContentManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Mock get_curator method
        content_manager.get_curator = Mock(return_value=mock_curator)
        
        # Test discovery
        orchestrator = await content_manager.get_content_orchestrator()
        
        # Verify orchestrator was discovered
        assert orchestrator is not None
        assert orchestrator.service_name == "ContentAnalysisOrchestratorService"
        assert orchestrator.realm_name == "content"
        
        # Verify Curator was called
        mock_curator.discover_service_by_name.assert_called_with("ContentAnalysisOrchestrator")
    
    @pytest.mark.asyncio
    async def test_content_orchestrator_uses_content_manager(self, mock_di_container, mock_platform_gateway):
        """Test that Content Orchestrator can be initialized with ContentManagerService."""
        from backend.content.ContentManagerService.content_manager_service import ContentManagerService
        from backend.content.orchestrators.content_orchestrator.content_analysis_orchestrator import ContentOrchestrator
        
        # Create ContentManagerService
        content_manager = ContentManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Create Content Orchestrator with ContentManagerService
        orchestrator = ContentOrchestrator(content_manager=content_manager)
        
        # Verify orchestrator properties
        assert orchestrator.service_name == "ContentAnalysisOrchestratorService"
        assert orchestrator.realm_name == "content"
        assert orchestrator.content_manager == content_manager
        assert orchestrator.delivery_manager == content_manager  # Backward compatibility
    
    @pytest.mark.asyncio
    async def test_content_orchestrator_can_discover_enabling_services(self, mock_di_container, mock_platform_gateway):
        """Test that Content Orchestrator can discover enabling services via get_enabling_service()."""
        from backend.content.ContentManagerService.content_manager_service import ContentManagerService
        from backend.content.orchestrators.content_orchestrator.content_analysis_orchestrator import ContentOrchestrator
        
        # Mock enabling service
        mock_file_parser = Mock()
        mock_file_parser.service_name = "FileParserService"
        mock_file_parser.realm_name = "business_enablement"
        
        # Create ContentManagerService
        content_manager = ContentManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Create Content Orchestrator
        orchestrator = ContentOrchestrator(content_manager=content_manager)
        
        # Mock get_enabling_service to return file parser
        orchestrator.get_enabling_service = AsyncMock(return_value=mock_file_parser)
        
        # Test enabling service discovery
        file_parser = await orchestrator._get_file_parser_service()
        
        # Verify enabling service was discovered
        assert file_parser is not None
        assert file_parser.service_name == "FileParserService"
        assert file_parser.realm_name == "business_enablement"  # Enabling services stay in business_enablement
        
        # Verify get_enabling_service was called
        orchestrator.get_enabling_service.assert_called_with("FileParserService")
    
    def test_content_realm_structure(self):
        """Test that Content realm has correct structure."""
        import os
        
        # Get project root (tests directory is in symphainy_source/tests)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        content_realm_path = os.path.join(project_root, "symphainy-platform/backend/content")
        
        # Check main directories exist
        assert os.path.exists(os.path.join(content_realm_path, "ContentManagerService")), f"ContentManagerService directory not found at {content_realm_path}/ContentManagerService"
        assert os.path.exists(os.path.join(content_realm_path, "orchestrators")), f"orchestrators directory not found"
        assert os.path.exists(os.path.join(content_realm_path, "agents")), f"agents directory not found"
        assert os.path.exists(os.path.join(content_realm_path, "mcp_server")), f"mcp_server directory not found"
        
        # Check key files exist
        assert os.path.exists(os.path.join(content_realm_path, "ContentManagerService/content_manager_service.py")), "ContentManagerService file not found"
        assert os.path.exists(os.path.join(content_realm_path, "orchestrators/content_orchestrator/content_analysis_orchestrator.py")), "Content orchestrator file not found"
        assert os.path.exists(os.path.join(content_realm_path, "agents/content_liaison_agent.py")), "Content liaison agent file not found"
        assert os.path.exists(os.path.join(content_realm_path, "mcp_server/content_analysis_mcp_server.py")), "Content MCP server file not found"
    
    def test_content_manager_service_capabilities(self, mock_di_container, mock_platform_gateway):
        """Test that ContentManagerService exposes correct capabilities."""
        from backend.content.ContentManagerService.content_manager_service import ContentManagerService
        
        # Create ContentManagerService
        content_manager = ContentManagerService(
            di_container=mock_di_container,
            platform_gateway=mock_platform_gateway
        )
        
        # Test capabilities method
        capabilities = content_manager.get_capabilities()
        
        # Verify capabilities structure
        assert "service_name" in capabilities
        assert "realm" in capabilities
        assert "manager_type" in capabilities
        assert "capabilities" in capabilities
        assert capabilities["service_name"] == "ContentManagerService"
        assert capabilities["realm"] == "content"
        assert "content_analysis" in capabilities["capabilities"]
        assert "document_processing" in capabilities["capabilities"]

