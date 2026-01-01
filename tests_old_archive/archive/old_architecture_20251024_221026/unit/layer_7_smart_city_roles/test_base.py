"""
Base test class for Layer 7: Smart City Roles tests.

This layer tests the concrete smart city role implementations that use
the interfaces defined in Layer 5B. Smart city roles are the actual
services that implement business logic using the platform's abstractions.
"""

import pytest
import pytest_asyncio
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, MagicMock
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
from foundations.utility_foundation.utilities.security.security_service import UserContext


class SmartCityRolesTestBase:
    """Base class for Smart City Roles tests."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client."""
        mock_client = Mock()
        mock_client.table.return_value = Mock()
        mock_client.table.return_value.insert.return_value = Mock()
        mock_client.table.return_value.select.return_value = Mock()
        mock_client.table.return_value.update.return_value = Mock()
        mock_client.table.return_value.delete.return_value = Mock()
        mock_client.table.return_value.execute.return_value = Mock()
        return mock_client
    
    @pytest.fixture
    def mock_environment_loader(self):
        """Mock environment loader."""
        mock_loader = Mock(spec=EnvironmentLoader)
        mock_loader.is_multi_tenant_enabled.return_value = True
        mock_loader.get_multi_tenant_config.return_value = {
            "enabled": True,
            "default_tenant_type": "organization",
            "max_tenants_per_user": 5,
            "tenant_limits": {"individual": 1, "organization": 50, "enterprise": 1000},
            "tenant_features": {
                "individual": ["basic_analytics"],
                "organization": ["basic_analytics", "team_collaboration"],
                "enterprise": ["basic_analytics", "team_collaboration", "advanced_insights"]
            },
            "security_guard": {"mcp_server_url": "http://localhost:8001"},
            "caching": {"tenant_cache_ttl": 3600, "user_context_cache_ttl": 1800},
            "rls": {"enabled": True, "strict_isolation": True}
        }
        mock_loader.get_tenant_config.return_value = {
            "max_users": 50,
            "features": ["basic_analytics", "team_collaboration"],
            "type": "organization"
        }
        return mock_loader
    
    @pytest.fixture
    def mock_utility_foundation(self):
        """Mock utility foundation service."""
        mock_foundation = Mock(spec=UtilityFoundationService)
        mock_foundation.log_operation_with_telemetry = AsyncMock()
        mock_foundation.handle_error_with_audit = AsyncMock()
        mock_foundation.track_utility_usage = AsyncMock()
        mock_foundation.record_health_metric = AsyncMock()
        mock_foundation.health_check = AsyncMock(return_value={"status": "healthy"})
        
        # Mock the attributes that FoundationServiceBase expects
        mock_foundation.logger = Mock()
        mock_foundation.error_handler = Mock()
        mock_foundation.error_handler.handle_error = Mock()  # Make it synchronous
        
        # Mock health service with proper async behavior
        mock_health_service = Mock()
        mock_health_service.health_check = AsyncMock(return_value={
            "service": "test_service",
            "status": "running",
            "uptime_seconds": 100.0,
            "timestamp": "2025-01-01T00:00:00"
        })
        mock_foundation.health_service = mock_health_service
        
        mock_foundation.telemetry_service = Mock()
        mock_foundation.security_service = Mock()
        mock_foundation.tool_factory = Mock()
        
        return mock_foundation
    
    @pytest.fixture
    def mock_public_works_foundation(self):
        """Mock public works foundation service."""
        mock_foundation = Mock(spec=PublicWorksFoundationService)
        mock_foundation.get_smart_city_abstractions = AsyncMock(return_value={
            "multi_tenant_management": Mock(),
            "user_context_with_tenant": Mock(),
            "tenant_validation": Mock(),
            "audit_logging": Mock()
        })
        mock_foundation.get_smart_city_realm_abstractions = Mock(return_value={
            "multi_tenant_management": Mock(),
            "user_context_with_tenant": Mock(),
            "tenant_validation": Mock(),
            "audit_logging": Mock()
        })
        mock_foundation.get_abstraction_for_role = AsyncMock(return_value=Mock())
        mock_foundation.has_abstraction = AsyncMock(return_value=True)
        mock_foundation.get_abstraction = AsyncMock(return_value=Mock())
        return mock_foundation
    
    @pytest.fixture
    def mock_curator_foundation(self):
        """Mock curator foundation service."""
        mock_foundation = Mock(spec=CuratorFoundationService)
        mock_foundation.register_capability = AsyncMock()
        mock_foundation.validate_pattern = AsyncMock(return_value={"valid": True})
        mock_foundation.detect_anti_patterns = AsyncMock(return_value=[])
        return mock_foundation
    
    @pytest.fixture
    def sample_user_context(self):
        """Sample user context for testing."""
        return UserContext(
            user_id="user_001",
            email="user@testorg.com",
            full_name="Test User",
            session_id="session_001",
            permissions=["read", "write"],
            tenant_id="tenant_001"
        )
    
    @pytest.fixture
    def sample_tenant_data(self):
        """Sample tenant data for testing."""
        return {
            "id": "tenant_001",
            "name": "Test Organization",
            "type": "organization",
            "admin_user_id": "user_admin_001",
            "admin_email": "admin@testorg.com",
            "max_users": 50,
            "features": ["basic_analytics", "team_collaboration"],
            "metadata": {"test": True}
        }
    
    def assert_service_initialization(self, service, expected_attributes=None):
        """Assert that a smart city role service is properly initialized."""
        assert service is not None
        assert hasattr(service, 'logger')
        assert hasattr(service, 'initialize')
        
        if expected_attributes:
            for attr in expected_attributes:
                assert hasattr(service, attr), f"Service missing attribute: {attr}"
    
    def assert_abstraction_access(self, service, abstraction_name):
        """Assert that a service can access smart city abstractions."""
        assert hasattr(service, 'smart_city_abstractions')
        assert hasattr(service, 'get_smart_city_abstractions')
        assert hasattr(service, 'get_abstraction_for_role')
        assert hasattr(service, 'has_abstraction')
        assert hasattr(service, 'get_abstraction')
    
    def assert_multi_tenant_capabilities(self, service):
        """Assert that a service has multi-tenant capabilities."""
        assert hasattr(service, 'tenant_cache')
        assert hasattr(service, 'user_context_cache')
        assert hasattr(service, 'audit_logs')
    
    def assert_health_check(self, health_result):
        """Assert that a health check result is valid (HealthService pattern)."""
        assert health_result is not None
        assert isinstance(health_result, dict)
        
        # Standard HealthService fields (from health_service.health_check())
        assert "service" in health_result
        assert "status" in health_result
        assert "uptime_seconds" in health_result
        assert "timestamp" in health_result
        
        # Valid status values from HealthService.ServiceStatus
        assert health_result["status"] in [
            "initializing", "running", "stopping", "stopped", 
            "error", "maintenance", "degraded"
        ]
        
        # Type checks
        assert isinstance(health_result["service"], str)
        assert isinstance(health_result["uptime_seconds"], (int, float))
        assert isinstance(health_result["timestamp"], str)
        
        # Optional fields that may be present
        if "initialized" in health_result:
            assert isinstance(health_result["initialized"], bool)
        if "metrics" in health_result:
            assert isinstance(health_result["metrics"], dict)
        if "response_time" in health_result:
            assert isinstance(health_result["response_time"], (int, float))
