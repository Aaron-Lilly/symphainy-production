#!/usr/bin/env python3
"""
Mock Infrastructure Patcher - Inject Mocks into Platform

Patches infrastructure adapters to use mocks during test execution.
This ensures the platform uses mocked infrastructure while maintaining
the exact same interfaces and behavior as production.

WHAT (Test Infrastructure Role): I inject mock adapters into the platform during tests
HOW (Test Infrastructure Implementation): I use monkey patching to replace real adapters with mocks
"""

import pytest
import sys
import logging
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Import mock adapters
from tests.fixtures.mock_infrastructure_adapters import MockAdapterFactory


class InfrastructureMockPatcher:
    """Patches infrastructure adapters to use mocks."""
    
    def __init__(self):
        """Initialize the patcher."""
        self.patches = []
        self.mock_factory = MockAdapterFactory()
    
    def start(self):
        """Start patching infrastructure adapters."""
        # Import mock adapters
        from tests.fixtures.mock_infrastructure_adapters import (
            MockSupabaseFileManagementAdapter,
            MockOpenTelemetryHealthAdapter,
            MockTelemetryAdapter,
            MockRedisAdapter,
            MockArangoDBAdapter
        )
        
        # Patch Supabase File Management Adapter
        supabase_patch = patch(
            'foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter.SupabaseFileManagementAdapter',
            MockSupabaseFileManagementAdapter
        )
        supabase_patch.start()
        self.patches.append(supabase_patch)
        
        # Patch OpenTelemetry Health Adapter
        otel_health_patch = patch(
            'foundations.public_works_foundation.infrastructure_adapters.opentelemetry_health_adapter.OpenTelemetryHealthAdapter',
            MockOpenTelemetryHealthAdapter
        )
        otel_health_patch.start()
        self.patches.append(otel_health_patch)
        
        # Patch Telemetry Adapter
        telemetry_patch = patch(
            'foundations.public_works_foundation.infrastructure_adapters.telemetry_adapter.TelemetryAdapter',
            MockTelemetryAdapter
        )
        telemetry_patch.start()
        self.patches.append(telemetry_patch)
        
        # Patch Redis Adapter
        redis_patch = patch(
            'foundations.public_works_foundation.infrastructure_adapters.redis_adapter.RedisAdapter',
            MockRedisAdapter
        )
        redis_patch.start()
        self.patches.append(redis_patch)
        
        # Patch ArangoDB Adapter
        arango_patch = patch(
            'foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter.ArangoDBAdapter',
            MockArangoDBAdapter
        )
        arango_patch.start()
        self.patches.append(arango_patch)
        
        # Create a wrapper class for ArangoContentMetadataAdapter that matches its signature
        class MockArangoContentMetadataAdapter(MockArangoDBAdapter):
            """Mock ArangoDB Content Metadata Adapter - uses same interface as ArangoDBAdapter."""
            
            async def create_content_collections(self) -> bool:
                """Create content collections in mock storage."""
                collections = [
                    "content_metadata",
                    "content_schemas",
                    "content_insights",
                    "content_relationships",
                    "content_analysis"
                ]
                for collection_name in collections:
                    await self.create_collection(collection_name)
                return True
            
            async def create_content_indexes(self) -> bool:
                """Create content indexes in mock storage."""
                # Mock indexes - just return success
                self.logger.info("✅ Mock content indexes created")
                return True
        
        # Patch ArangoDB Content Metadata Adapter (archived - skip if module doesn't exist)
        try:
            arango_metadata_patch = patch(
                'foundations.public_works_foundation.infrastructure_adapters.arango_content_metadata_adapter.ArangoContentMetadataAdapter',
                MockArangoContentMetadataAdapter
            )
            arango_metadata_patch.start()
            self.patches.append(arango_metadata_patch)
        except (ModuleNotFoundError, AttributeError):
            # Module was archived, skip patching
            pass
        
        # Patch ArangoDB Tool Storage Adapter (different constructor - no database params)
        from tests.fixtures.mock_infrastructure_adapters import MockArangoDBAdapter
        
        class MockArangoDBToolStorageAdapter:
            """Mock ArangoDB Tool Storage Adapter - mirrors production interface."""
            def __init__(self, service_name: str = "arangodb_tool_storage_adapter"):
                self.service_name = service_name
                self._tools = {}
                self.logger = logging.getLogger(f"MockArangoDBToolStorageAdapter-{service_name}")
                self.logger.info(f"✅ Mock ArangoDBToolStorageAdapter initialized")
            
            async def save_tool(self, tool):
                """Save tool in mock storage."""
                if tool.name not in self._tools:
                    self._tools[tool.name] = {}
                self._tools[tool.name][tool.version] = tool
                return True
            
            async def get_tool(self, name: str, version: str = None):
                """Get tool from mock storage."""
                if name not in self._tools:
                    return None
                if version:
                    return self._tools[name].get(version)
                # Return latest version
                if self._tools[name]:
                    return list(self._tools[name].values())[-1]
                return None
        
        arango_tool_patch = patch(
            'foundations.public_works_foundation.infrastructure_adapters.arangodb_tool_storage_adapter.ArangoDBToolStorageAdapter',
            MockArangoDBToolStorageAdapter
        )
        arango_tool_patch.start()
        self.patches.append(arango_tool_patch)
    
    def stop(self):
        """Stop all patches."""
        for patch_obj in self.patches:
            patch_obj.stop()
        self.patches.clear()


@pytest.fixture(scope="session", autouse=True)
def mock_infrastructure():
    """Automatically patch infrastructure adapters for all tests."""
    patcher = InfrastructureMockPatcher()
    patcher.start()
    yield patcher
    patcher.stop()


@pytest.fixture
def infrastructure_mocks(mock_infrastructure):
    """Provide access to mock infrastructure adapters."""
    return {
        "factory": MockAdapterFactory(),
        "patcher": mock_infrastructure
    }

