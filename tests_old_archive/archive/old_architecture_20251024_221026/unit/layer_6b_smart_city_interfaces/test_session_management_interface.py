#!/usr/bin/env python3
"""
Tests for Session Management Interface.

Tests the session management interface data models and concrete implementations
for Smart City session operations.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.interfaces.session_management_interface import (
    SessionData,
    SessionValidationResult,
    SessionInitiationRequest,
    SessionInitiationResponse,
    ISessionManagement
)
from tests.unit.layer_5b_smart_city_interfaces.test_base import SmartCityInterfacesTestBase


class TestSessionData:
    """Test SessionData data model."""
    
    def test_session_data_creation(self):
        """Test creating a session data."""
        session_data = SessionData(
            session_id="session_001",
            user_id="user_001",
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            expires_at=datetime(2024, 1, 1, 23, 59, 59),
            metadata={"device_type": "desktop", "location": "office"},
            state="active"
        )
        
        assert session_data.session_id == "session_001"
        assert session_data.user_id == "user_001"
        assert session_data.created_at == datetime(2024, 1, 1, 0, 0, 0)
        assert session_data.expires_at == datetime(2024, 1, 1, 23, 59, 59)
        assert session_data.metadata["device_type"] == "desktop"
        assert session_data.metadata["location"] == "office"
        assert session_data.state == "active"
    
    def test_session_data_defaults(self):
        """Test session data with default values."""
        session_data = SessionData(
            session_id="session_002",
            user_id="user_002",
            created_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        
        assert session_data.session_id == "session_002"
        assert session_data.user_id == "user_002"
        assert session_data.created_at == datetime(2024, 1, 1, 0, 0, 0)
        assert session_data.expires_at is not None  # Should be set by __post_init__
        assert session_data.metadata == {}
        assert session_data.state == "active"
    
    def test_session_data_serialization(self):
        """Test session data serialization."""
        from dataclasses import asdict
        
        session_data = SessionData(
            session_id="serializable_session",
            user_id="serializable_user",
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            expires_at=datetime(2024, 1, 1, 23, 59, 59),
            metadata={"serializable": True},
            state="active"
        )
        
        session_dict = asdict(session_data)
        
        assert isinstance(session_dict, dict)
        assert session_dict["session_id"] == "serializable_session"
        assert session_dict["user_id"] == "serializable_user"
        assert session_dict["state"] == "active"
        assert session_dict["metadata"]["serializable"] is True


class TestSessionValidationResult:
    """Test SessionValidationResult data model."""
    
    def test_session_validation_result_valid(self):
        """Test creating a valid session validation result."""
        validation_result = SessionValidationResult(
            is_valid=True,
            session_id="session_001",
            user_id="user_001",
            expires_at=datetime(2024, 1, 1, 23, 59, 59),
            metadata={"validated": True}
        )
        
        assert validation_result.is_valid is True
        assert validation_result.session_id == "session_001"
        assert validation_result.user_id == "user_001"
        assert validation_result.expires_at == datetime(2024, 1, 1, 23, 59, 59)
        assert validation_result.metadata["validated"] is True
        assert validation_result.error_message is None
    
    def test_session_validation_result_invalid(self):
        """Test creating an invalid session validation result."""
        validation_result = SessionValidationResult(
            is_valid=False,
            session_id="session_001",
            user_id="user_001",
            expires_at=None,
            metadata=None,
            error_message="Session expired"
        )
        
        assert validation_result.is_valid is False
        assert validation_result.session_id == "session_001"
        assert validation_result.user_id == "user_001"
        assert validation_result.expires_at is None
        assert validation_result.metadata is None
        assert validation_result.error_message == "Session expired"


class TestSessionInitiationRequest:
    """Test SessionInitiationRequest data model."""
    
    def test_session_initiation_request_creation(self):
        """Test creating a session initiation request."""
        request = SessionInitiationRequest(
            user_id="user_001",
            session_type="analytics",
            metadata={"device_type": "mobile", "app_version": "1.0.0"},
            duration_hours=12
        )
        
        assert request.user_id == "user_001"
        assert request.session_type == "analytics"
        assert request.metadata["device_type"] == "mobile"
        assert request.metadata["app_version"] == "1.0.0"
        assert request.duration_hours == 12
    
    def test_session_initiation_request_defaults(self):
        """Test session initiation request with default values."""
        request = SessionInitiationRequest(user_id="user_002")
        
        assert request.user_id == "user_002"
        assert request.session_type == "default"
        assert request.metadata == {}
        assert request.duration_hours == 24


class TestSessionInitiationResponse:
    """Test SessionInitiationResponse data model."""
    
    def test_session_initiation_response_success(self):
        """Test creating a successful session initiation response."""
        response = SessionInitiationResponse(
            success=True,
            session_id="session_001",
            user_id="user_001",
            expires_at=datetime(2024, 1, 1, 23, 59, 59),
            metadata={"created": True}
        )
        
        assert response.success is True
        assert response.session_id == "session_001"
        assert response.user_id == "user_001"
        assert response.expires_at == datetime(2024, 1, 1, 23, 59, 59)
        assert response.metadata["created"] is True
        assert response.error_message is None
    
    def test_session_initiation_response_failure(self):
        """Test creating a failed session initiation response."""
        response = SessionInitiationResponse(
            success=False,
            session_id="",
            user_id="user_001",
            expires_at=datetime(2024, 1, 1, 0, 0, 0),
            metadata=None,
            error_message="User not found"
        )
        
        assert response.success is False
        assert response.session_id == ""
        assert response.user_id == "user_001"
        assert response.error_message == "User not found"


class TestSessionManagementInterface(SmartCityInterfacesTestBase):
    """Test ISessionManagement implementation."""
    
    @pytest.mark.asyncio
    async def test_session_management_interface_initialization(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test session management interface initialization."""
        # Create a concrete implementation for testing
        class TestSessionManagementInterface(ISessionManagement):
            def __init__(self):
                self.sessions = {}
                self.session_count = 0
            
            async def validate_session(self, session_id: str, user_context=None) -> SessionValidationResult:
                session_data = self.sessions.get(session_id)
                if session_data:
                    return SessionValidationResult(
                        is_valid=True,
                        session_id=session_id,
                        user_id=session_data["user_id"],
                        expires_at=session_data["expires_at"],
                        metadata=session_data.get("metadata", {})
                    )
                else:
                    return SessionValidationResult(
                        is_valid=False,
                        session_id=session_id,
                        user_id="",
                        expires_at=None,
                        metadata=None,
                        error_message="Session not found"
                    )
            
            async def initiate_session(self, request: SessionInitiationRequest, user_context=None) -> SessionInitiationResponse:
                self.session_count += 1
                session_id = f"session_{self.session_count}"
                expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59)
                
                self.sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": request.user_id,
                    "created_at": datetime.utcnow(),
                    "expires_at": expires_at,
                    "metadata": request.metadata or {},
                    "state": "active"
                }
                
                return SessionInitiationResponse(
                    success=True,
                    session_id=session_id,
                    user_id=request.user_id,
                    expires_at=expires_at,
                    metadata={"session_type": request.session_type}
                )
            
            async def terminate_session(self, session_id: str, user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    return {"status": "terminated", "session_id": session_id, "message": "Session terminated successfully"}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def extend_session(self, session_id: str, additional_hours: int, user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    session_data = self.sessions[session_id]
                    current_expires = session_data["expires_at"]
                    from datetime import timedelta
                    new_expires = current_expires + timedelta(hours=additional_hours)
                    session_data["expires_at"] = new_expires
                    return {"status": "extended", "session_id": session_id, "new_expires_at": new_expires}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def get_session_data(self, session_id: str, user_context=None) -> Optional[SessionData]:
                session_data = self.sessions.get(session_id)
                if session_data:
                    return SessionData(
                        session_id=session_data["session_id"],
                        user_id=session_data["user_id"],
                        created_at=session_data["created_at"],
                        expires_at=session_data["expires_at"],
                        metadata=session_data.get("metadata", {}),
                        state=session_data.get("state", "active")
                    )
                return None
            
            async def update_session_metadata(self, session_id: str, metadata: Dict[str, Any], user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    self.sessions[session_id]["metadata"].update(metadata)
                    return {"status": "updated", "session_id": session_id, "message": "Session metadata updated"}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def list_user_sessions(self, user_id: str, user_context=None) -> List[SessionData]:
                sessions = []
                for session_data in self.sessions.values():
                    if session_data["user_id"] == user_id:
                        sessions.append(SessionData(
                            session_id=session_data["session_id"],
                            user_id=session_data["user_id"],
                            created_at=session_data["created_at"],
                            expires_at=session_data["expires_at"],
                            metadata=session_data.get("metadata", {}),
                            state=session_data.get("state", "active")
                        ))
                return sessions
            
            async def cleanup_expired_sessions(self, user_context=None) -> Dict[str, Any]:
                current_time = datetime.utcnow()
                expired_count = 0
                
                for session_id, session_data in list(self.sessions.items()):
                    if session_data["expires_at"] < current_time:
                        del self.sessions[session_id]
                        expired_count += 1
                
                return {"status": "cleaned", "expired_sessions": expired_count, "message": f"Cleaned {expired_count} expired sessions"}
            
            async def refresh_session(self, session_id: str, duration_hours: int = 24, user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    session_data = self.sessions[session_id]
                    from datetime import timedelta
                    new_expires = datetime.utcnow() + timedelta(hours=duration_hours)
                    session_data["expires_at"] = new_expires
                    return {"status": "refreshed", "session_id": session_id, "new_expires_at": new_expires}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def get_session_state(self, session_id: str, user_context=None) -> Dict[str, Any]:
                session_data = self.sessions.get(session_id)
                if session_data:
                    return {
                        "session_id": session_id,
                        "state": session_data.get("state", "active"),
                        "user_id": session_data["user_id"],
                        "created_at": session_data["created_at"],
                        "expires_at": session_data["expires_at"],
                        "is_expired": session_data["expires_at"] < datetime.utcnow()
                    }
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def get_session_analytics(self, user_context=None) -> Dict[str, Any]:
                total_sessions = len(self.sessions)
                active_sessions = len([s for s in self.sessions.values() if s.get("state") == "active"])
                expired_sessions = len([s for s in self.sessions.values() if s["expires_at"] < datetime.utcnow()])
                
                return {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "expired_sessions": expired_sessions,
                    "analytics_timestamp": datetime.utcnow().isoformat()
                }
        
        interface = TestSessionManagementInterface()
        
        assert interface is not None
        assert hasattr(interface, 'validate_session')
        assert hasattr(interface, 'initiate_session')
        assert hasattr(interface, 'terminate_session')
        assert hasattr(interface, 'extend_session')
        assert hasattr(interface, 'get_session_data')
    
    @pytest.mark.asyncio
    async def test_session_management_interface_operations(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test session management interface operations."""
        class TestSessionManagementInterface(ISessionManagement):
            def __init__(self):
                self.sessions = {}
                self.session_count = 0
            
            async def validate_session(self, session_id: str, user_context=None) -> SessionValidationResult:
                session_data = self.sessions.get(session_id)
                if session_data:
                    return SessionValidationResult(
                        is_valid=True,
                        session_id=session_id,
                        user_id=session_data["user_id"],
                        expires_at=session_data["expires_at"],
                        metadata=session_data.get("metadata", {})
                    )
                else:
                    return SessionValidationResult(
                        is_valid=False,
                        session_id=session_id,
                        user_id="",
                        expires_at=None,
                        metadata=None,
                        error_message="Session not found"
                    )
            
            async def initiate_session(self, request: SessionInitiationRequest, user_context=None) -> SessionInitiationResponse:
                self.session_count += 1
                session_id = f"session_{self.session_count}"
                expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59)
                
                self.sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": request.user_id,
                    "created_at": datetime.utcnow(),
                    "expires_at": expires_at,
                    "metadata": request.metadata or {},
                    "state": "active"
                }
                
                return SessionInitiationResponse(
                    success=True,
                    session_id=session_id,
                    user_id=request.user_id,
                    expires_at=expires_at,
                    metadata={"session_type": request.session_type}
                )
            
            async def terminate_session(self, session_id: str, user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    return {"status": "terminated", "session_id": session_id, "message": "Session terminated successfully"}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def extend_session(self, session_id: str, additional_hours: int, user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    session_data = self.sessions[session_id]
                    current_expires = session_data["expires_at"]
                    from datetime import timedelta
                    new_expires = current_expires + timedelta(hours=additional_hours)
                    session_data["expires_at"] = new_expires
                    return {"status": "extended", "session_id": session_id, "new_expires_at": new_expires}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def get_session_data(self, session_id: str, user_context=None) -> Optional[SessionData]:
                session_data = self.sessions.get(session_id)
                if session_data:
                    return SessionData(
                        session_id=session_data["session_id"],
                        user_id=session_data["user_id"],
                        created_at=session_data["created_at"],
                        expires_at=session_data["expires_at"],
                        metadata=session_data.get("metadata", {}),
                        state=session_data.get("state", "active")
                    )
                return None
            
            async def update_session_metadata(self, session_id: str, metadata: Dict[str, Any], user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    self.sessions[session_id]["metadata"].update(metadata)
                    return {"status": "updated", "session_id": session_id, "message": "Session metadata updated"}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def list_user_sessions(self, user_id: str, user_context=None) -> List[SessionData]:
                sessions = []
                for session_data in self.sessions.values():
                    if session_data["user_id"] == user_id:
                        sessions.append(SessionData(
                            session_id=session_data["session_id"],
                            user_id=session_data["user_id"],
                            created_at=session_data["created_at"],
                            expires_at=session_data["expires_at"],
                            metadata=session_data.get("metadata", {}),
                            state=session_data.get("state", "active")
                        ))
                return sessions
            
            async def cleanup_expired_sessions(self, user_context=None) -> Dict[str, Any]:
                current_time = datetime.utcnow()
                expired_count = 0
                
                for session_id, session_data in list(self.sessions.items()):
                    if session_data["expires_at"] < current_time:
                        del self.sessions[session_id]
                        expired_count += 1
                
                return {"status": "cleaned", "expired_sessions": expired_count, "message": f"Cleaned {expired_count} expired sessions"}
            
            async def refresh_session(self, session_id: str, duration_hours: int = 24, user_context=None) -> Dict[str, Any]:
                if session_id in self.sessions:
                    session_data = self.sessions[session_id]
                    from datetime import timedelta
                    new_expires = datetime.utcnow() + timedelta(hours=duration_hours)
                    session_data["expires_at"] = new_expires
                    return {"status": "refreshed", "session_id": session_id, "new_expires_at": new_expires}
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def get_session_state(self, session_id: str, user_context=None) -> Dict[str, Any]:
                session_data = self.sessions.get(session_id)
                if session_data:
                    return {
                        "session_id": session_id,
                        "state": session_data.get("state", "active"),
                        "user_id": session_data["user_id"],
                        "created_at": session_data["created_at"],
                        "expires_at": session_data["expires_at"],
                        "is_expired": session_data["expires_at"] < datetime.utcnow()
                    }
                return {"status": "not_found", "session_id": session_id, "message": "Session not found"}
            
            async def get_session_analytics(self, user_context=None) -> Dict[str, Any]:
                total_sessions = len(self.sessions)
                active_sessions = len([s for s in self.sessions.values() if s.get("state") == "active"])
                expired_sessions = len([s for s in self.sessions.values() if s["expires_at"] < datetime.utcnow()])
                
                return {
                    "total_sessions": total_sessions,
                    "active_sessions": active_sessions,
                    "expired_sessions": expired_sessions,
                    "analytics_timestamp": datetime.utcnow().isoformat()
                }
        
        interface = TestSessionManagementInterface()
        
        # Test initiate_session
        request = SessionInitiationRequest(
            user_id="user_001",
            session_type="analytics",
            metadata={"device_type": "desktop", "location": "office"},
            duration_hours=12
        )
        
        response = await interface.initiate_session(request)
        assert response.success is True
        assert response.session_id is not None
        assert response.user_id == "user_001"
        assert response.metadata["session_type"] == "analytics"
        
        session_id = response.session_id
        
        # Test validate_session
        validation_result = await interface.validate_session(session_id)
        assert validation_result.is_valid is True
        assert validation_result.session_id == session_id
        assert validation_result.user_id == "user_001"
        assert validation_result.error_message is None
        
        # Test get_session_data
        session_data = await interface.get_session_data(session_id)
        assert session_data is not None
        assert session_data.session_id == session_id
        assert session_data.user_id == "user_001"
        assert session_data.state == "active"
        assert session_data.metadata["device_type"] == "desktop"
        
        # Test update_session_metadata
        update_result = await interface.update_session_metadata(session_id, {"last_activity": "2024-01-01T12:00:00Z"})
        assert update_result["status"] == "updated"
        
        # Verify metadata update
        updated_session_data = await interface.get_session_data(session_id)
        assert updated_session_data.metadata["last_activity"] == "2024-01-01T12:00:00Z"
        assert updated_session_data.metadata["device_type"] == "desktop"  # Should preserve existing metadata
        
        # Test extend_session
        extend_result = await interface.extend_session(session_id, 2)
        assert extend_result["status"] == "extended"
        assert "new_expires_at" in extend_result
        
        # Test list_user_sessions
        user_sessions = await interface.list_user_sessions("user_001")
        assert len(user_sessions) == 1
        assert user_sessions[0].session_id == session_id
        assert user_sessions[0].user_id == "user_001"
        
        # Test terminate_session
        terminate_result = await interface.terminate_session(session_id)
        assert terminate_result["status"] == "terminated"
        
        # Verify termination
        terminated_validation = await interface.validate_session(session_id)
        assert terminated_validation.is_valid is False
        assert terminated_validation.error_message == "Session not found"
        
        # Test cleanup_expired_sessions
        cleanup_result = await interface.cleanup_expired_sessions()
        assert cleanup_result["status"] == "cleaned"
        assert "expired_sessions" in cleanup_result