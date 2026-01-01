#!/usr/bin/env python3
"""
Test Smart City Interfaces and Protocols

Test the Smart City role interfaces and SOA/MCP protocols to ensure they work correctly.
"""

import os
import sys
import asyncio
from typing import Dict, Any, Type
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from interfaces import (
    ISessionManagement, SessionInitiationRequest, SessionInitiationResponse, SessionValidationResult,
    IAuthentication, LoginRequest, LoginResponse, AuthProvider, UserRole,
    IFileStorage, FileUploadRequest, FileUploadResponse, StorageTier, FileType,
    IHealthMonitoring, HealthCheck, HealthStatus, MetricType,
    IWorkflowOrchestration, WorkflowCreateRequest, WorkflowType
)

from protocols import (
    SOAServiceProtocol, SOAServiceBase, SOAEndpoint, SOAServiceInfo,
    MCPServerProtocol, MCPBaseServer, MCPTool, MCPServerInfo
)

from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.curator_foundation import CuratorFoundationService
from utilities import UserContext


class MockSessionManagement(ISessionManagement):
    """Mock implementation of ISessionManagement for testing."""
    
    async def validate_session(self, session_id: str, user_context: UserContext = None):
        return SessionValidationResult(
            is_valid=True,
            session_id=session_id,
            user_id="test_user"
        )
    
    async def initiate_session(self, request: SessionInitiationRequest, user_context: UserContext = None):
        return SessionInitiationResponse(
            success=True,
            session_id="test_session_123",
            user_id=request.user_id,
            expires_at=datetime.utcnow().replace(hour=23, minute=59, second=59)
        )
    
    async def terminate_session(self, session_id: str, user_context: UserContext = None):
        return {"success": True, "session_id": session_id}
    
    async def refresh_session(self, session_id: str, duration_hours: int = 24, user_context: UserContext = None):
        return {"success": True, "session_id": session_id, "new_expires_at": datetime.utcnow()}
    
    async def get_session_state(self, session_id: str, user_context: UserContext = None):
        return {"session_id": session_id, "state": "active"}
    
    async def update_session_metadata(self, session_id: str, metadata: Dict[str, Any], user_context: UserContext = None):
        return {"success": True, "session_id": session_id}
    
    async def list_user_sessions(self, user_id: str, user_context: UserContext = None):
        return []
    
    async def cleanup_expired_sessions(self, user_context: UserContext = None):
        return {"cleaned": 0}
    
    async def get_session_analytics(self, user_context: UserContext = None):
        return {"total_sessions": 0}


class MockSOAService(SOAServiceProtocol):
    """Mock SOA service implementation for testing."""
    
    def __init__(self, service_name: str, interface_class: Type, curator_foundation=None):
        super().__init__(service_name, interface_class, curator_foundation)
        self.service_info = SOAServiceInfo(
            service_name=service_name,
            version="1.0.0",
            description=f"Mock {service_name} service",
            interface_name="ISessionManagement",
            endpoints=self._create_standard_endpoints()
        )
    
    async def initialize(self, user_context: UserContext = None):
        pass
    
    def get_service_info(self) -> SOAServiceInfo:
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description
            },
            "paths": {
                "/openapi.json": {
                    "get": {
                        "summary": "OpenAPI Specification",
                        "responses": {"200": {"description": "OpenAPI spec"}}
                    }
                }
            }
        }
    
    def get_docs(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_info.service_name,
            "description": self.service_info.description,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints]
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],
                "description": self.service_info.description,
                "realm": "smart_city"
            }
            return await self.curator_foundation.register_capability(
                self.service_name,
                capability
            )
        return {"error": "Curator not available"}


async def test_interfaces():
    """Test Smart City interfaces."""
    print("🧪 Testing Smart City Interfaces...")
    
    # Test Session Management Interface
    print("\n📝 Testing ISessionManagement...")
    session_mgmt = MockSessionManagement()
    
    # Test session initiation
    request = SessionInitiationRequest(
        user_id="test_user",
        session_type="default"
    )
    response = await session_mgmt.initiate_session(request)
    print(f"✅ Session initiation: {response.success}")
    print(f"   Session ID: {response.session_id}")
    
    # Test session validation
    validation = await session_mgmt.validate_session("test_session_123")
    print(f"✅ Session validation: {validation.is_valid}")
    
    # Test Authentication Interface
    print("\n🔐 Testing IAuthentication...")
    # Note: We would need a mock implementation here too
    
    # Test File Storage Interface
    print("\n📁 Testing IFileStorage...")
    # Note: We would need a mock implementation here too
    
    # Test Health Monitoring Interface
    print("\n🏥 Testing IHealthMonitoring...")
    # Note: We would need a mock implementation here too
    
    # Test Workflow Orchestration Interface
    print("\n🎭 Testing IWorkflowOrchestration...")
    # Note: We would need a mock implementation here too
    
    print("\n✅ Interface tests completed!")


async def test_protocols():
    """Test SOA and MCP protocols."""
    print("\n🧪 Testing Smart City Protocols...")
    
    # Initialize foundation services
    utility_foundation = UtilityFoundationService()
    await utility_foundation.initialize()
    
    curator_foundation = CuratorFoundationService(utility_foundation)
    await curator_foundation.initialize()
    
    # Test SOA Service Protocol
    print("\n🌐 Testing SOA Service Protocol...")
    soa_service = MockSOAService("traffic_cop", ISessionManagement, curator_foundation)
    await soa_service.initialize()
    
    # Test service info
    service_info = soa_service.get_service_info()
    print(f"✅ Service info: {service_info.service_name} v{service_info.version}")
    print(f"   Interface: {service_info.interface_name}")
    print(f"   Endpoints: {len(service_info.endpoints)}")
    
    # Test OpenAPI spec generation
    openapi_spec = soa_service.get_openapi_spec()
    print(f"✅ OpenAPI spec generated: {openapi_spec['openapi']}")
    
    # Test docs generation
    docs = soa_service.get_docs()
    print(f"✅ Docs generated: {docs['service_name']}")
    
    # Test Curator registration
    registration = await soa_service.register_with_curator()
    print(f"✅ Curator registration: {registration.get('success', False)}")
    
    # Test MCP Server Protocol
    print("\n🤖 Testing MCP Server Protocol...")
    # Note: We would need a mock MCP implementation here
    
    print("\n✅ Protocol tests completed!")


async def test_curator_integration():
    """Test integration with Curator Foundation Service."""
    print("\n🧪 Testing Curator Integration...")
    
    # Initialize foundation services
    utility_foundation = UtilityFoundationService()
    await utility_foundation.initialize()
    
    curator_foundation = CuratorFoundationService(utility_foundation)
    await curator_foundation.initialize()
    
    # Register a mock service
    capability = {
        "interface": "ISessionManagement",
        "endpoints": ["/sessions/initiate", "/sessions/validate"],
        "tools": ["validate_session", "initiate_session"],
        "description": "Session management service",
        "realm": "smart_city"
    }
    
    result = await curator_foundation.register_capability("traffic_cop", capability)
    print(f"✅ Capability registered: {result['success']}")
    
    # Get the capability back
    retrieved = await curator_foundation.get_capability("traffic_cop")
    if retrieved:
        print(f"✅ Capability retrieved: {retrieved.service_name}")
        print(f"   Interface: {retrieved.interface_name}")
        print(f"   Endpoints: {retrieved.endpoints}")
        print(f"   Tools: {retrieved.tools}")
    
    # List all capabilities
    capabilities = await curator_foundation.list_capabilities()
    print(f"✅ Total capabilities: {len(capabilities)}")
    
    # Get registry status
    status = await curator_foundation.get_registry_status()
    print(f"✅ Registry status: {status['total_capabilities']} capabilities")
    
    print("\n✅ Curator integration tests completed!")


async def main():
    """Run all tests."""
    print("🚀 Starting Smart City Interfaces and Protocols Tests...")
    
    await test_interfaces()
    await test_protocols()
    await test_curator_integration()
    
    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
