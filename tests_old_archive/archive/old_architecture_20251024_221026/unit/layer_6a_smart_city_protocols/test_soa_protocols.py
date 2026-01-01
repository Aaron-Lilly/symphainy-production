#!/usr/bin/env python3
"""
Tests for SOA Service Protocols.

Tests the SOA service protocol definitions, base classes, and data models
for Smart City SOA services.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.protocols import (
    SOAServiceProtocol,
    SOAServiceBase,
    SOAEndpoint,
    SOAServiceInfo
)
from foundations.utility_foundation.utilities import UserContext
from .test_base import SmartCityProtocolsTestBase


class TestSOAEndpoint:
    """Test SOAEndpoint data model."""
    
    def test_soa_endpoint_creation(self):
        """Test creating an SOA endpoint."""
        endpoint = SOAEndpoint(
            path="/api/test",
            method="GET",
            summary="Test endpoint",
            description="A test endpoint for SOA services",
            parameters=[{"name": "id", "type": "string", "required": True}],
            request_schema={"type": "object", "properties": {"id": {"type": "string"}}},
            response_schema={"type": "object", "properties": {"result": {"type": "string"}}},
            tags=["test", "api"]
        )
        
        assert endpoint.path == "/api/test"
        assert endpoint.method == "GET"
        assert endpoint.summary == "Test endpoint"
        assert endpoint.description == "A test endpoint for SOA services"
        assert len(endpoint.parameters) == 1
        assert endpoint.parameters[0]["name"] == "id"
        assert endpoint.request_schema["type"] == "object"
        assert endpoint.response_schema["type"] == "object"
        assert "test" in endpoint.tags
        assert "api" in endpoint.tags
    
    def test_soa_endpoint_defaults(self):
        """Test SOA endpoint with default values."""
        endpoint = SOAEndpoint(
            path="/api/minimal",
            method="POST",
            summary="Minimal endpoint",
            description="A minimal endpoint"
        )
        
        assert endpoint.path == "/api/minimal"
        assert endpoint.method == "POST"
        assert endpoint.summary == "Minimal endpoint"
        assert endpoint.description == "A minimal endpoint"
        assert endpoint.parameters == []
        assert endpoint.request_schema is None
        assert endpoint.response_schema is None
        assert endpoint.tags == []
    
    def test_soa_endpoint_serialization(self):
        """Test SOA endpoint serialization."""
        from dataclasses import asdict
        
        endpoint = SOAEndpoint(
            path="/api/serialize",
            method="PUT",
            summary="Serializable endpoint",
            description="Test serialization",
            tags=["serialization"]
        )
        
        endpoint_dict = asdict(endpoint)
        
        assert isinstance(endpoint_dict, dict)
        assert endpoint_dict["path"] == "/api/serialize"
        assert endpoint_dict["method"] == "PUT"
        assert endpoint_dict["summary"] == "Serializable endpoint"
        assert endpoint_dict["description"] == "Test serialization"
        assert endpoint_dict["tags"] == ["serialization"]


class TestSOAServiceInfo:
    """Test SOAServiceInfo data model."""
    
    def test_soa_service_info_creation(self):
        """Test creating SOA service info."""
        endpoints = [
            SOAEndpoint(
                path="/api/health",
                method="GET",
                summary="Health check",
                description="Service health check endpoint"
            ),
            SOAEndpoint(
                path="/api/data",
                method="POST",
                summary="Data processing",
                description="Process data endpoint"
            )
        ]
        
        service_info = SOAServiceInfo(
            service_name="test_service",
            version="1.0.0",
            description="A test SOA service",
            interface_name="TestServiceInterface",
            endpoints=endpoints,
            tags=["test", "soa"]
        )
        
        assert service_info.service_name == "test_service"
        assert service_info.version == "1.0.0"
        assert service_info.description == "A test SOA service"
        assert service_info.interface_name == "TestServiceInterface"
        assert len(service_info.endpoints) == 2
        assert service_info.endpoints[0].path == "/api/health"
        assert service_info.endpoints[1].path == "/api/data"
        assert "test" in service_info.tags
        assert "soa" in service_info.tags
    
    def test_soa_service_info_defaults(self):
        """Test SOA service info with default values."""
        service_info = SOAServiceInfo(
            service_name="minimal_service",
            version="1.0.0",
            description="Minimal service",
            interface_name="MinimalInterface",
            endpoints=[]
        )
        
        assert service_info.service_name == "minimal_service"
        assert service_info.version == "1.0.0"
        assert service_info.description == "Minimal service"
        assert service_info.interface_name == "MinimalInterface"
        assert service_info.endpoints == []
        assert service_info.tags == []


class TestSOAServiceProtocol:
    """Test SOAServiceProtocol abstract class."""
    
    def test_soa_service_protocol_interface(self):
        """Test SOA service protocol interface methods."""
        # Check that SOAServiceProtocol has the required abstract methods
        assert hasattr(SOAServiceProtocol, 'get_service_info')
        assert hasattr(SOAServiceProtocol, 'get_openapi_spec')
        assert hasattr(SOAServiceProtocol, 'get_docs')
        
        # Check that these are abstract methods
        assert getattr(SOAServiceProtocol.get_service_info, '__isabstractmethod__', False)
        assert getattr(SOAServiceProtocol.get_openapi_spec, '__isabstractmethod__', False)
        assert getattr(SOAServiceProtocol.get_docs, '__isabstractmethod__', False)


class TestSOAServiceBase(SmartCityProtocolsTestBase):
    """Test SOAServiceBase implementation."""
    
    @pytest.mark.asyncio
    async def test_soa_service_base_initialization(self, mock_utility_foundation, mock_public_works_foundation):
        """Test SOA service base initialization."""
        # Create a concrete implementation for testing
        class TestSOAService(SOAServiceBase):
            def __init__(self, utility_foundation, curator_foundation=None):
                super().__init__("test_soa_service", utility_foundation, curator_foundation)
            
            async def get_service_info(self) -> SOAServiceInfo:
                return SOAServiceInfo(
                    service_name="test_service",
                    version="1.0.0",
                    description="Test service",
                    interface_name="TestInterface",
                    endpoints=[]
                )
            
            def get_openapi_spec(self) -> Dict[str, Any]:
                return {"openapi": "3.0.0", "info": {"title": "Test Service"}}
            
            def get_docs(self) -> Dict[str, Any]:
                return {"title": "Test Service Documentation"}
            
            async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
                return {"status": "registered"}
        
        service = TestSOAService(mock_utility_foundation)
        
        assert service is not None
        assert service.service_name == "test_soa_service"
        assert service.utility_foundation == mock_utility_foundation
    
    @pytest.mark.asyncio
    async def test_soa_service_base_methods(self, mock_utility_foundation, mock_public_works_foundation):
        """Test SOA service base method implementations."""
        class TestSOAService(SOAServiceBase):
            def __init__(self, utility_foundation, curator_foundation=None):
                super().__init__("test_soa_service", utility_foundation, curator_foundation)
            
            async def get_service_info(self) -> SOAServiceInfo:
                return SOAServiceInfo(
                    service_name="test_service",
                    version="1.0.0",
                    description="Test service",
                    interface_name="TestInterface",
                    endpoints=[
                        SOAEndpoint(
                            path="/api/test",
                            method="GET",
                            summary="Test endpoint",
                            description="A test endpoint"
                        )
                    ]
                )
            
            async def validate_request(self, endpoint: str, method: str, user_context: UserContext = None) -> bool:
                return endpoint == "/api/test" and method == "GET"
            
            async def process_request(self, endpoint: str, method: str, data: Dict[str, Any] = None, user_context: UserContext = None) -> Dict[str, Any]:
                return {"endpoint": endpoint, "method": method, "data": data}
        
        service = TestSOAService(mock_utility_foundation)
        
        # Test get_service_info
        service_info = await service.get_service_info()
        assert service_info.service_name == "test_service"
        assert service_info.version == "1.0.0"
        
        # Test get_service_info endpoints
        service_info = await service.get_service_info()
        endpoints = service_info.endpoints
        assert len(endpoints) == 1
        assert endpoints[0].path == "/api/test"
        assert endpoints[0].method == "GET"
        
        # Test get_openapi_spec (returns error since soa_protocol is not initialized)
        openapi_spec = await service.get_openapi_spec()
        assert "error" in openapi_spec
        assert openapi_spec["error"] == "SOA protocol not initialized"
        
        # Test get_docs (returns error since soa_protocol is not initialized)
        docs = await service.get_docs()
        assert "error" in docs
        assert docs["error"] == "SOA protocol not initialized"
        
        # Test register_with_curator (returns error since curator_foundation is not available)
        register_result = await service.register_with_curator()
        assert "error" in register_result
        assert register_result["error"] == "Curator Foundation Service not available"
    
    @pytest.mark.asyncio
    async def test_soa_service_base_health_check(self, mock_utility_foundation, mock_public_works_foundation):
        """Test SOA service base health check."""
        class TestSOAService(SOAServiceBase):
            def __init__(self, utility_foundation, curator_foundation=None):
                super().__init__("test_soa_service", utility_foundation, curator_foundation)
            
            async def get_service_info(self) -> SOAServiceInfo:
                return SOAServiceInfo(
                    service_name="test_service",
                    version="1.0.0",
                    description="Test service",
                    interface_name="TestInterface",
                    endpoints=[]
                )
            
            def get_openapi_spec(self) -> Dict[str, Any]:
                return {"openapi": "3.0.0", "info": {"title": "Test Service"}}
            
            def get_docs(self) -> Dict[str, Any]:
                return {"title": "Test Service Documentation"}
            
            async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
                return {"status": "registered"}
        
        service = TestSOAService(mock_utility_foundation)
        
        # Test health check (inherited from FoundationServiceBase)
        health_status = await service.get_service_health()
        
        assert health_status is not None
        assert "service" in health_status
        assert "status" in health_status
        assert "timestamp" in health_status
        assert health_status["service"] == "test_soa_service"
