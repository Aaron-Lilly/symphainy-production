"""
Test Traffic Cop Service - Smart City Role for Session and State Management

Tests the Traffic Cop service which handles session routing, state synchronization,
and cross-pillar communication coordination.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any

from backend.smart_city.services.traffic_cop.traffic_cop_service import TrafficCopService
from foundations.utility_foundation.utilities.security.security_service import UserContext
from tests.unit.layer_7_smart_city_roles.test_base import SmartCityRolesTestBase


class TestTrafficCopService(SmartCityRolesTestBase):
    """Test Traffic Cop Service implementation."""
    
    @pytest.mark.asyncio
    async def test_traffic_cop_service_initialization(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Traffic Cop service initialization."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test basic initialization
        self.assert_service_initialization(service, [
            'utility_foundation', 'public_works_foundation', 'curator_foundation',
            'session_management', 'state_management', 'redis_streams'
        ])
        
        assert service.utility_foundation == mock_utility_foundation
        assert service.public_works_foundation == mock_public_works_foundation
        assert service.curator_foundation == mock_curator_foundation
    
    @pytest.mark.asyncio
    async def test_traffic_cop_service_initialization_async(self, mock_utility_foundation, mock_curator_foundation, mock_public_works_foundation):
        """Test Traffic Cop service async initialization."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            curator_foundation=mock_curator_foundation,
            public_works_foundation=mock_public_works_foundation
        )
        
        # Test async initialization
        await service.initialize()
        
        # Verify micro-modules are initialized
        assert service.session_management is not None
        assert service.state_management is not None
    
    @pytest.mark.asyncio
    async def test_traffic_cop_session_management(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Traffic Cop session management operations."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test create_session
        session_request = {
            "user_id": "user_001",
            "session_type": "analytics",
            "metadata": {"device": "desktop"}
        }
        session_result = await service.create_session(session_request, sample_user_context)
        assert session_result is not None
        assert isinstance(session_result, dict)
        assert "session_id" in session_result
        
        # Test get_session
        session_id = session_result["session_id"]
        get_session_result = await service.get_session(session_id, sample_user_context)
        assert get_session_result is not None
        assert isinstance(get_session_result, dict)
        assert "session_id" in get_session_result
        
        # Test update_session
        update_data = {"status": "active", "metadata": {"last_activity": datetime.utcnow().isoformat()}}
        update_result = await service.update_session(session_id, update_data, sample_user_context)
        assert update_result is not None
        assert isinstance(update_result, dict)
        assert "status" in update_result
        
        # Test terminate_session
        terminate_result = await service.terminate_session(session_id, sample_user_context)
        assert terminate_result is not None
        assert isinstance(terminate_result, dict)
        assert "status" in terminate_result
    
    @pytest.mark.asyncio
    async def test_traffic_cop_state_management(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Traffic Cop state management operations."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test set_state
        state_request = {
            "session_id": "session_001",
            "state_key": "user_preferences",
            "state_value": {"theme": "dark", "language": "en"},
            "priority": "high"
        }
        set_state_result = await service.set_state(state_request, sample_user_context)
        assert set_state_result is not None
        assert isinstance(set_state_result, dict)
        assert "status" in set_state_result
        
        # Test get_state
        get_state_result = await service.get_state("session_001", "user_preferences", sample_user_context)
        assert get_state_result is not None
        assert isinstance(get_state_result, dict)
        assert "state_value" in get_state_result
        
        # Test sync_state
        sync_request = {
            "session_id": "session_001",
            "target_pillars": ["analytics", "content"],
            "state_keys": ["user_preferences"]
        }
        sync_result = await service.sync_state(sync_request, sample_user_context)
        assert sync_result is not None
        assert isinstance(sync_result, dict)
        assert "synced" in sync_result
    
    @pytest.mark.asyncio
    async def test_traffic_cop_routing_operations(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Traffic Cop routing operations."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test route_request
        routing_request = {
            "request_type": "analytics_query",
            "target_pillar": "analytics",
            "payload": {"query": "user_engagement"},
            "priority": "normal"
        }
        routing_result = await service.route_request(routing_request, sample_user_context)
        assert routing_result is not None
        assert isinstance(routing_result, dict)
        assert "routed" in routing_result
        
        # Test get_routing_status
        status_result = await service.get_routing_status("request_001", sample_user_context)
        assert status_result is not None
        assert isinstance(status_result, dict)
        assert "status" in status_result
    
    @pytest.mark.asyncio
    async def test_traffic_cop_analytics_operations(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Traffic Cop analytics operations."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test get_session_analytics
        session_analytics = await service.get_session_analytics(sample_user_context)
        assert session_analytics is not None
        assert isinstance(session_analytics, dict)
        assert "total_sessions" in session_analytics
        assert "active_sessions" in session_analytics
        
        # Test get_routing_analytics
        routing_analytics = await service.get_routing_analytics(sample_user_context)
        assert routing_analytics is not None
        assert isinstance(routing_analytics, dict)
        assert "total_requests" in routing_analytics
        assert "success_rate" in routing_analytics
        
        # Test get_state_analytics
        state_analytics = await service.get_state_analytics(sample_user_context)
        assert state_analytics is not None
        assert isinstance(state_analytics, dict)
        assert "total_states" in state_analytics
        assert "sync_count" in state_analytics
    
    @pytest.mark.asyncio
    async def test_traffic_cop_health_check(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation):
        """Test Traffic Cop health check."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test health check
        health_result = await service.get_service_health()
        self.assert_health_check(health_result)
        
        # Verify standard HealthService health check structure
        assert health_result["service"] == "TrafficCopService"
        if "initialized" in health_result:
            assert health_result["initialized"] is True
    
    @pytest.mark.asyncio
    async def test_traffic_cop_soa_protocol_compliance(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation):
        """Test Traffic Cop SOA protocol compliance."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test get_service_info
        service_info = service.get_service_info()
        assert service_info is not None
        assert hasattr(service_info, 'service_name')
        assert hasattr(service_info, 'version')
        assert hasattr(service_info, 'description')
        assert hasattr(service_info, 'endpoints')
        
        # Test get_openapi_spec
        openapi_spec = service.get_openapi_spec()
        assert openapi_spec is not None
        assert isinstance(openapi_spec, dict)
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        
        # Test get_docs
        docs = service.get_docs()
        assert docs is not None
        assert isinstance(docs, dict)
        assert "title" in docs
    
    @pytest.mark.asyncio
    async def test_traffic_cop_error_handling(self, mock_utility_foundation, mock_public_works_foundation, mock_curator_foundation, sample_user_context):
        """Test Traffic Cop error handling."""
        service = TrafficCopService(
            utility_foundation=mock_utility_foundation,
            public_works_foundation=mock_public_works_foundation,
            curator_foundation=mock_curator_foundation
        )
        
        await service.initialize()
        
        # Test error handling for invalid session
        invalid_session_result = await service.get_session("invalid_session", sample_user_context)
        assert invalid_session_result is not None
        assert isinstance(invalid_session_result, dict)
        assert "error" in invalid_session_result or "status" in invalid_session_result
        
        # Test error handling for invalid state
        invalid_state_result = await service.get_state("session_001", "invalid_state", sample_user_context)
        assert invalid_state_result is not None
        assert isinstance(invalid_state_result, dict)
        assert "error" in invalid_state_result or "status" in invalid_state_result

