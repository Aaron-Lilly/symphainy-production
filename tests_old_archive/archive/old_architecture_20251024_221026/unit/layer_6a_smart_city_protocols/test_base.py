#!/usr/bin/env python3
"""
Base test class for Layer 5A: Smart City Protocols tests.

Provides common fixtures and utilities for testing the Smart City Protocols
with real implementations and proper dependency injection.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from config.environment_loader import EnvironmentLoader
from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from backend.smart_city.protocols import (
    SOAServiceProtocol,
    SOAServiceBase,
    SOAEndpoint,
    SOAServiceInfo,
    MCPServerProtocol,
    MCPBaseServer,
    MCPTool,
    MCPServerInfo
)


class SmartCityProtocolsTestBase:
    """Base class for Smart City Protocols tests."""
    
    @pytest_asyncio.fixture
    async def env_loader(self):
        """Create EnvironmentLoader instance."""
        return EnvironmentLoader()
    
    @pytest_asyncio.fixture
    async def utility_foundation(self):
        """Create Utility Foundation Service instance."""
        service = UtilityFoundationService()
        await service.initialize()
        return service
    
    @pytest_asyncio.fixture
    async def public_works_foundation(self, utility_foundation):
        """Create Public Works Foundation Service instance."""
        service = PublicWorksFoundationService(utility_foundation)
        await service.initialize()
        return service
    
    @pytest_asyncio.fixture
    async def mock_utility_foundation(self):
        """Create mock utility foundation for isolated testing."""
        mock = Mock()
        mock.logger = Mock()
        mock.logger.info = Mock()
        mock.logger.error = Mock()
        mock.logger.warning = Mock()
        mock.logger.debug = Mock()
        
        # Add required methods
        mock.log_operation_with_telemetry = AsyncMock()
        mock.handle_error_with_audit = AsyncMock()
        mock.track_utility_usage = Mock()
        mock.record_health_metric = AsyncMock()
        
        return mock
    
    @pytest_asyncio.fixture
    async def mock_public_works_foundation(self):
        """Create mock public works foundation for isolated testing."""
        mock = Mock()
        mock.logger = Mock()
        mock.logger.info = Mock()
        mock.logger.error = Mock()
        mock.logger.warning = Mock()
        mock.logger.debug = Mock()
        
        # Add required methods
        mock.get_abstraction_creation_service = Mock()
        mock.get_abstraction_access_service = Mock()
        mock.get_abstraction_discovery_service = Mock()
        mock.get_abstraction_management_service = Mock()
        
        return mock
