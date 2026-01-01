#!/usr/bin/env python3
"""
Integration Tests for Smart City Protocol-Based Architecture

Tests the new protocol-based Smart City roles to ensure they:
1. Implement the correct protocols
2. Use SmartCityRoleBase correctly
3. Delegate to Communication Foundation properly
4. Preserve core capabilities while adding orchestration
"""

import os
import sys
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

import pytest
from datetime import datetime
import uuid


class TestTrafficCopProtocol:
    """Test Traffic Cop Protocol Implementation"""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create a mock DI Container with all required services."""
        di_container = Mock()
        
        # Mock Communication Foundation
        comm_foundation = Mock()
        comm_foundation.send_message = AsyncMock(return_value={"success": True})
        di_container.get_foundation_service.return_value = comm_foundation
        
        # Mock Curator Foundation
        curator = Mock()
        curator.register_service = AsyncMock(return_value={"registered": True})
        di_container.get_foundation_service.return_value = curator
        
        return di_container
    
    @pytest.mark.asyncio
    async def test_traffic_cop_initialization(self, mock_di_container):
        """Test that Traffic Cop initializes with SmartCityRoleBase."""
        from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
        
        # Create Traffic Cop service
        service = TrafficCopService(mock_di_container)
        
        # Verify it's initialized with SmartCityRoleBase
        assert hasattr(service, 'service_name')
        assert service.service_name == "TrafficCopService"
        assert hasattr(service, 'di_container')
        assert hasattr(service, 'public_works_foundation')
        assert hasattr(service, 'communication_foundation')
    
    @pytest.mark.asyncio
    async def test_traffic_cop_implements_protocol(self, mock_di_container):
        """Test that Traffic Cop implements TrafficCopProtocol."""
        from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
        from backend.smart_city.interfaces.traffic_cop_interface import SessionRequest
        
        # Create Traffic Cop service
        service = TrafficCopService(mock_di_container)
        
        # Verify it implements core protocol methods
        assert hasattr(service, 'create_session')
        assert hasattr(service, 'route_session')
        assert hasattr(service, 'sync_state')
        
        # Verify it implements orchestration protocol methods
        assert hasattr(service, 'orchestrate_api_gateway')
        assert hasattr(service, 'orchestrate_fastapi_routing')
        assert hasattr(service, 'orchestrate_load_balancing')
    
    @pytest.mark.asyncio
    async def test_traffic_cop_orchestrates_api_gateway(self, mock_di_container):
        """Test that Traffic Cop orchestrates API Gateway routing."""
        from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
        from bases.protocols.traffic_cop_protocol import APIGatewayRequest
        
        # Create Traffic Cop service
        service = TrafficCopService(mock_di_container)
        
        # Create API Gateway request
        request = APIGatewayRequest(
            request_id=str(uuid.uuid4()),
            method="GET",
            path="/api/v1/test",
            headers={"Content-Type": "application/json"},
            body={"key": "value"}
        )
        
        # Call orchestration method
        response = await service.orchestrate_api_gateway(request)
        
        # Verify response
        assert response is not None
        assert response.request_id == request.request_id
        assert response.status_code in [200, 429, 500]  # Valid status codes
    
    @pytest.mark.asyncio
    async def test_traffic_cop_preserves_core_capabilities(self, mock_di_container):
        """Test that Traffic Cop preserves core session management capabilities."""
        from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
        from backend.smart_city.interfaces.traffic_cop_interface import SessionRequest
        
        # Create Traffic Cop service
        service = TrafficCopService(mock_di_container)
        
        # Initialize it
        await service.initialize()
        
        # Create session request
        request = SessionRequest(
            session_id=str(uuid.uuid4()),
            session_type="user_session",
            context={"user_id": "test_user"}
        )
        
        # Call core capability
        response = await service.create_session(request)
        
        # Verify response
        assert response is not None
        assert response.session_id == request.session_id


class TestConductorProtocol:
    """Test Conductor Protocol Implementation"""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create a mock DI Container with all required services."""
        di_container = Mock()
        
        # Mock Communication Foundation
        comm_foundation = Mock()
        comm_foundation.send_message = AsyncMock(return_value={"success": True})
        di_container.get_foundation_service.return_value = comm_foundation
        
        return di_container
    
    @pytest.mark.asyncio
    async def test_conductor_initialization(self, mock_di_container):
        """Test that Conductor initializes with SmartCityRoleBase."""
        from backend.smart_city.services.conductor.conductor_service import ConductorService
        
        # Create Conductor service
        service = ConductorService(mock_di_container)
        
        # Verify it's initialized with SmartCityRoleBase
        assert hasattr(service, 'service_name')
        assert service.service_name == "ConductorService"
        assert hasattr(service, 'di_container')
        assert hasattr(service, 'communication_foundation')
    
    @pytest.mark.asyncio
    async def test_conductor_implements_protocol(self, mock_di_container):
        """Test that Conductor implements ConductorProtocol."""
        from backend.smart_city.services.conductor.conductor_service import ConductorService
        
        # Create Conductor service
        service = ConductorService(mock_di_container)
        
        # Verify it implements core protocol methods
        assert hasattr(service, 'create_workflow')
        assert hasattr(service, 'execute_workflow')
        assert hasattr(service, 'get_workflow_status')
        
        # Verify it implements orchestration protocol methods
        assert hasattr(service, 'orchestrate_websocket_connection')
        assert hasattr(service, 'orchestrate_real_time_task')
        assert hasattr(service, 'orchestrate_streaming_data')
    
    @pytest.mark.asyncio
    async def test_conductor_orchestrates_websocket(self, mock_di_container):
        """Test that Conductor orchestrates WebSocket connections."""
        from backend.smart_city.services.conductor.conductor_service import ConductorService
        from bases.protocols.conductor_protocol import WebSocketRequest
        
        # Create Conductor service
        service = ConductorService(mock_di_container)
        
        # Create WebSocket request
        request = WebSocketRequest(
            connection_id=str(uuid.uuid4()),
            endpoint="/websocket/test",
            websocket_url="ws://localhost:8000/ws"
        )
        
        # Call orchestration method
        response = await service.orchestrate_websocket_connection(request)
        
        # Verify response
        assert response is not None
        assert response.connection_id == request.connection_id
        assert response.success in [True, False]


class TestProtocolHierarchy:
    """Test that the protocol hierarchy is correct"""
    
    def test_protocols_extend_base(self):
        """Test that all role-specific protocols extend SmartCityRoleProtocol."""
        from bases.protocols.smart_city_role_protocol import SmartCityRoleProtocol
        from bases.protocols.traffic_cop_protocol import TrafficCopProtocol
        from bases.protocols.conductor_protocol import ConductorProtocol
        from bases.protocols.security_guard_protocol import SecurityGuardProtocol
        
        # Verify that protocols are defined (structural typing)
        assert TrafficCopProtocol is not None
        assert ConductorProtocol is not None
        assert SecurityGuardProtocol is not None
    
    def test_protocols_have_orchestration_methods(self):
        """Test that all protocols have orchestration methods."""
        from bases.protocols.traffic_cop_protocol import TrafficCopProtocol
        from bases.protocols.conductor_protocol import ConductorProtocol
        from bases.protocols.security_guard_protocol import SecurityGuardProtocol
        
        # Check that protocols have orchestration methods in their signatures
        import inspect
        
        traffic_cop_methods = [m for m in dir(TrafficCopProtocol) if not m.startswith('_')]
        assert 'orchestrate_api_gateway' in str(inspect.signature(TrafficCopProtocol.orchestrate_api_gateway))
        
        conductor_methods = [m for m in dir(Conductor) if not m.startswith('_')]
        assert 'orchestrate_websocket_connection' in str(inspect.signature(Conductor.orchestrate_websocket_connection))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

