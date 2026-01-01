#!/usr/bin/env python3
"""
Curator Phase 2 Refactoring Integration Tests

Tests the new Phase 2 refactoring functionality:
- Extended CapabilityDefinition with semantic_mapping and contracts
- Service Protocol Registry
- Route Registry (endpoint registry)
- Service Mesh Policy Reporter

WHAT: Verify Phase 2 refactoring works correctly
HOW: Test new services and registration methods with real infrastructure
"""

import sys
from pathlib import Path
import pytest
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.curator_foundation.models.capability_definition import CapabilityDefinition


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def di_container(event_loop):
    """Create and initialize DI Container with real infrastructure."""
    container = DIContainerService("test")
    
    # Initialize Public Works Foundation (connects to real infrastructure)
    if hasattr(container, 'public_works_foundation') and container.public_works_foundation:
        public_works = container.public_works_foundation
    else:
        public_works = PublicWorksFoundationService(di_container=container)
        container.public_works_foundation = public_works
    
    await public_works.initialize()
    
    yield container
    
    # Cleanup
    if hasattr(public_works, 'shutdown'):
        await public_works.shutdown()


@pytest.fixture(scope="module")
async def curator_foundation(di_container):
    """Create and initialize Curator Foundation."""
    curator = CuratorFoundationService(
        foundation_services=di_container,
        public_works_foundation=di_container.public_works_foundation
    )
    await curator.initialize()
    
    yield curator
    
    if hasattr(curator, 'shutdown'):
        await curator.shutdown()


# ============================================================================
# TESTS
# ============================================================================

class TestPhase2ServicesInitialization:
    """Test that new Phase 2 services initialize correctly."""
    
    def test_service_protocol_registry_initialized(self, curator_foundation):
        """Test that ServiceProtocolRegistryService is initialized."""
        assert hasattr(curator_foundation, 'service_protocol_registry')
        assert curator_foundation.service_protocol_registry is not None
        assert curator_foundation.service_protocol_registry.service_name == "service_protocol_registry"
    
    def test_route_registry_initialized(self, curator_foundation):
        """Test that RouteRegistryService is initialized."""
        assert hasattr(curator_foundation, 'route_registry')
        assert curator_foundation.route_registry is not None
        assert curator_foundation.route_registry.service_name == "route_registry"
    
    def test_service_mesh_metadata_reporter_initialized(self, curator_foundation):
        """Test that ServiceMeshMetadataReporterService is initialized."""
        assert hasattr(curator_foundation, 'service_mesh_metadata_reporter')
        assert curator_foundation.service_mesh_metadata_reporter is not None
        assert curator_foundation.service_mesh_metadata_reporter.service_name == "service_mesh_metadata_reporter"


class TestExtendedCapabilityDefinition:
    """Test extended CapabilityDefinition with semantic_mapping and contracts."""
    
    def test_capability_definition_creation(self):
        """Test creating a CapabilityDefinition with new fields."""
        capability = CapabilityDefinition(
            service_name="TestFileParserService",
            interface_name="IFileParser",
            endpoints=["/api/v1/content-pillar/upload-file"],
            tools=["upload_file_tool"],
            description="Test file parsing capability",
            realm="business_enablement",
            version="1.0.0",
            semantic_mapping={
                "domain_capability": "content.upload_file",
                "semantic_api": "/api/v1/content-pillar/upload-file",
                "user_journey": "upload_document_for_analysis"
            },
            contracts={
                "soa_api": {
                    "protocol": "IFileParser",
                    "method": "parse_file"
                },
                "rest_api": {
                    "endpoint": "/api/v1/content-pillar/upload-file",
                    "method": "POST",
                    "handler": "parse_file"
                },
                "mcp_tool": {
                    "tool_name": "upload_file_tool",
                    "mcp_server": "content_pillar_mcp_server"
                }
            }
        )
        
        assert capability.service_name == "TestFileParserService"
        assert capability.interface_name == "IFileParser"
        assert capability.semantic_mapping is not None
        assert capability.semantic_mapping["domain_capability"] == "content.upload_file"
        assert capability.contracts is not None
        assert capability.contracts["rest_api"]["endpoint"] == "/api/v1/content-pillar/upload-file"
        assert capability.registered_at is not None
    
    @pytest.mark.asyncio
    async def test_register_domain_capability(self, curator_foundation):
        """Test registering a domain capability with extended CapabilityDefinition."""
        capability = CapabilityDefinition(
            service_name="TestFileParserService",
            interface_name="IFileParser",
            endpoints=["/api/v1/content-pillar/upload-file"],
            tools=["upload_file_tool"],
            description="Test file parsing capability",
            realm="business_enablement",
            version="1.0.0",
            semantic_mapping={
                "domain_capability": "content.upload_file",
                "semantic_api": "/api/v1/content-pillar/upload-file",
                "user_journey": "upload_document_for_analysis"
            },
            contracts={
                "rest_api": {
                    "endpoint": "/api/v1/content-pillar/upload-file",
                    "method": "POST",
                    "handler": "parse_file"
                }
            }
        )
        
        result = await curator_foundation.register_domain_capability(capability)
        
        assert result is True
        
        # Verify route was automatically registered
        routes = await curator_foundation.discover_routes(
            pillar="content-pillar",
            service_name="TestFileParserService"
        )
        assert len(routes) > 0
        assert any(route["path"] == "/api/v1/content-pillar/upload-file" for route in routes)


class TestServiceProtocolRegistry:
    """Test Service Protocol Registry functionality."""
    
    @pytest.mark.asyncio
    async def test_register_service_protocol(self, curator_foundation):
        """Test registering a service protocol."""
        protocol_definition = {
            "methods": {
                "parse_file": {
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "file_type": {"type": "string"}
                        }
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "parsed_content": {"type": "string"},
                            "metadata": {"type": "object"}
                        }
                    },
                    "semantic_mapping": {
                        "domain_capability": "content.upload_file",
                        "user_journey": "upload_document_for_analysis"
                    }
                }
            }
        }
        
        result = await curator_foundation.register_service_protocol(
            service_name="TestFileParserService",
            protocol_name="IFileParser",
            protocol=protocol_definition
        )
        
        assert result is True
        
        # Verify protocol was registered
        protocol = await curator_foundation.service_protocol_registry.get_service_protocol(
            service_name="TestFileParserService",
            protocol_name="IFileParser"
        )
        assert protocol is not None
        assert "protocol" in protocol
        assert "parse_file" in protocol["protocol"]["methods"]
    
    @pytest.mark.asyncio
    async def test_list_protocols(self, curator_foundation):
        """Test listing all registered protocols."""
        protocols = await curator_foundation.service_protocol_registry.list_protocols()
        
        assert isinstance(protocols, list)
        # Should have at least the one we registered
        assert len(protocols) > 0


class TestRouteRegistry:
    """Test Route Registry (endpoint registry) functionality."""
    
    @pytest.mark.asyncio
    async def test_register_route(self, curator_foundation):
        """Test registering a route in endpoint registry."""
        route_metadata = {
            "route_id": "test_route_123",
            "path": "/api/v1/content-pillar/test-route",
            "method": "POST",
            "pillar": "content-pillar",
            "realm": "business_enablement",
            "service_name": "TestService",
            "capability_name": "test_capability",
            "handler": "test_handler",
            "description": "Test route",
            "version": "v1",
            "defined_by": "business_enablement_realm"
        }
        
        result = await curator_foundation.register_route(route_metadata)
        
        assert result is True
        
        # Verify route was registered
        route = await curator_foundation.route_registry.get_route("test_route_123")
        assert route is not None
        assert route["path"] == "/api/v1/content-pillar/test-route"
        assert route["pillar"] == "content-pillar"
    
    @pytest.mark.asyncio
    async def test_discover_routes_by_pillar(self, curator_foundation):
        """Test discovering routes by pillar."""
        routes = await curator_foundation.discover_routes(pillar="content-pillar")
        
        assert isinstance(routes, list)
        # Should have at least the routes we registered
        assert len(routes) > 0
        assert all(route["pillar"] == "content-pillar" for route in routes)
    
    @pytest.mark.asyncio
    async def test_discover_routes_by_realm(self, curator_foundation):
        """Test discovering routes by realm."""
        routes = await curator_foundation.discover_routes(realm="business_enablement")
        
        assert isinstance(routes, list)
        # Should have at least the routes we registered
        assert len(routes) > 0
        assert all(route["realm"] == "business_enablement" for route in routes)
    
    @pytest.mark.asyncio
    async def test_discover_routes_by_service(self, curator_foundation):
        """Test discovering routes by service name."""
        routes = await curator_foundation.discover_routes(service_name="TestService")
        
        assert isinstance(routes, list)
        # Should have at least the route we registered
        assert len(routes) > 0
        assert all(route["service_name"] == "TestService" for route in routes)


class TestServiceMeshPolicyReporter:
    """Test Service Mesh Policy Reporter functionality."""
    
    @pytest.mark.asyncio
    async def test_report_service_mesh_policies(self, curator_foundation):
        """Test reporting service mesh policies."""
        policies = {
            "source": "business_enablement_realm",
            "policies": {
                "load_balancing": "round_robin",
                "timeout": "30s",
                "circuit_breakers": {
                    "failure_threshold": 5,
                    "timeout": "60s"
                },
                "traffic_splitting": [
                    {"version": "v1", "weight": 80},
                    {"version": "v2", "weight": 20}
                ],
                "intentions": [
                    {"service": "TestService", "allow": True}
                ]
            }
        }
        
        result = await curator_foundation.report_service_mesh_policies(
            service_name="TestService",
            policies=policies
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_service_mesh_policy_report(self, curator_foundation):
        """Test getting aggregated service mesh policy report."""
        # First report a policy
        policies = {
            "source": "business_enablement_realm",
            "policies": {
                "load_balancing": "round_robin",
                "timeout": "30s"
            }
        }
        await curator_foundation.report_service_mesh_policies(
            service_name="TestService",
            policies=policies
        )
        
        # Get aggregated report
        report = await curator_foundation.get_service_mesh_policy_report("TestService")
        
        assert report is not None
        assert "service" in report
        assert report["service"] == "TestService"
        assert "policies" in report
        assert report["policies"]["source"] == "domain_reported"
        assert "load_balancing" in report["policies"]
        assert report["policies"]["load_balancing"] == "round_robin"


class TestEndToEndPhase2Flow:
    """Test end-to-end Phase 2 registration flow."""
    
    @pytest.mark.asyncio
    async def test_complete_registration_flow(self, curator_foundation):
        """Test complete registration flow: capability → protocol → route → policies."""
        # 1. Register capability with extended CapabilityDefinition
        capability = CapabilityDefinition(
            service_name="E2ETestService",
            interface_name="IE2ETest",
            endpoints=["/api/v1/content-pillar/e2e-test"],
            tools=["e2e_test_tool"],
            description="E2E test capability",
            realm="business_enablement",
            version="1.0.0",
            semantic_mapping={
                "domain_capability": "content.e2e_test",
                "semantic_api": "/api/v1/content-pillar/e2e-test",
                "user_journey": "e2e_test_journey"
            },
            contracts={
                "rest_api": {
                    "endpoint": "/api/v1/content-pillar/e2e-test",
                    "method": "POST",
                    "handler": "e2e_test_handler"
                }
            }
        )
        
        capability_result = await curator_foundation.register_domain_capability(capability)
        assert capability_result is True
        
        # 2. Register protocol
        protocol_result = await curator_foundation.register_service_protocol(
            service_name="E2ETestService",
            protocol_name="IE2ETest",
            protocol={
                "methods": {
                    "e2e_test_method": {
                        "input_schema": {},
                        "output_schema": {}
                    }
                }
            }
        )
        assert protocol_result is True
        
        # 3. Verify route was automatically registered
        routes = await curator_foundation.discover_routes(
            service_name="E2ETestService"
        )
        assert len(routes) > 0
        
        # 4. Report service mesh policies
        policies_result = await curator_foundation.report_service_mesh_policies(
            service_name="E2ETestService",
            policies={
                "source": "business_enablement_realm",
                "policies": {
                    "load_balancing": "round_robin",
                    "timeout": "30s"
                }
            }
        )
        assert policies_result is True
        
        # 5. Get aggregated policy report
        policy_report = await curator_foundation.get_service_mesh_policy_report("E2ETestService")
        assert policy_report is not None
        assert policy_report["service"] == "E2ETestService"
        
        print("\n✅ End-to-end Phase 2 registration flow completed successfully!")








