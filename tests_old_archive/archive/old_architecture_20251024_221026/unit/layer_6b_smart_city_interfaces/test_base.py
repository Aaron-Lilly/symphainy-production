#!/usr/bin/env python3
"""
Base test class for Layer 5B: Smart City Interfaces tests.

Provides common fixtures and utilities for testing the Smart City Interfaces
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
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService


class SmartCityInterfacesTestBase:
    """Base class for Smart City Interfaces tests."""
    
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
    async def curator_foundation(self, utility_foundation, public_works_foundation):
        """Create Curator Foundation Service instance."""
        service = CuratorFoundationService(utility_foundation, public_works_foundation)
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
    
    @pytest_asyncio.fixture
    async def mock_curator_foundation(self):
        """Create mock curator foundation for isolated testing."""
        mock = Mock()
        mock.logger = Mock()
        mock.logger.info = Mock()
        mock.logger.error = Mock()
        mock.logger.warning = Mock()
        mock.logger.debug = Mock()
        
        # Add required methods
        mock.register_capability = AsyncMock()
        mock.discover_capabilities = AsyncMock()
        mock.validate_pattern = AsyncMock()
        mock.detect_anti_patterns = AsyncMock()
        
        return mock
    
    @pytest_asyncio.fixture
    async def mock_supabase_client(self):
        """Create mock Supabase client for testing."""
        mock = Mock()
        mock.table = Mock()
        mock.auth = Mock()
        mock.storage = Mock()
        mock.rpc = Mock()
        return mock


