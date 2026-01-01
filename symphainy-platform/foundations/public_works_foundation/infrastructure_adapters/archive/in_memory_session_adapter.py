"""
In-Memory Session Adapter - Raw technology wrapper for in-memory session management

Provides in-memory session storage for development and testing.
This adapter implements the SessionProtocol for in-memory infrastructure.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from foundations.public_works_foundation.abstraction_contracts.session_protocol import (
    SessionProtocol, SessionContext, Session, SessionToken, SessionAnalytics,
    SessionStatus, SessionType, SecurityLevel
)


class InMemorySessionAdapter(SessionProtocol):
    """
    In-Memory Session Adapter - Raw technology wrapper for in-memory session management
    
    Provides in-memory session storage for development and testing.
    This adapter implements the SessionProtocol for in-memory infrastructure.
    """
    
    def __init__(self, 
                 session_ttl: int = 3600,
                 token_ttl: int = 1800):
        """Initialize In-Memory Session Adapter."""
        self.session_ttl = session_ttl
        self.token_ttl = token_ttl
        self.logger = logging.getLogger("in_memory_session_adapter")
        
        # In-memory storage
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.analytics: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Initialized In-Memory Session Adapter")
    
    async def create_session(self, 
                           context: SessionContext,
                           session_data: Dict[str, Any]) -> Session:
        """Create a new session in memory."""
        try:
            session_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Create session object
            session = Session(
                session_id=session_id,
                user_id=session_data.get("user_id"),
                agent_id=session_data.get("agent_id"),
                session_type=SessionType(session_data.get("session_type", "user")),
                status=SessionStatus.ACTIVE,
                created_at=now,
                expires_at=now + timedelta(seconds=self.session_ttl),
                last_accessed=now,
                security_level=SecurityLevel(session_data.get("security_level", "medium")),
                metadata=session_data.get("metadata", {}),
                tags=session_data.get("tags", [])
            )
            
            # Store in memory
            self.sessions[session_id] = {
                "session_id": session_id,
                "user_id": session.user_id,
                "agent_id": session.agent_id,
                "session_type": session.session_type.value,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
                "last_accessed": session.last_accessed.isoformat(),
                "security_level": session.security_level.value,
                "metadata": session.metadata,
                "tags": session.tags
            }
            
            # Initialize analytics
            self.analytics[session_id] = {
                "session_id": session_id,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "last_activity": now.isoformat(),
                "security_events": 0,
                "metadata": {}
            }
            
            self.logger.info(f"Created session {session_id} for user {session.user_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session(self, 
                         session_id: str,
                         context: SessionContext) -> Optional[Session]:
        """Get session by ID from memory."""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return None
            
            # Check if session is expired
            if session_data.get("expires_at"):
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                if datetime.utcnow() > expires_at:
                    # Mark as expired
                    session_data["status"] = SessionStatus.EXPIRED.value
                    return None
            
            # Update last accessed
            session_data["last_accessed"] = datetime.utcnow().isoformat()
            
            return Session(
                session_id=session_data["session_id"],
                user_id=session_data.get("user_id"),
                agent_id=session_data.get("agent_id"),
                session_type=SessionType(session_data.get("session_type", "user")),
                status=SessionStatus(session_data.get("status", "active")),
                created_at=datetime.fromisoformat(session_data["created_at"]),
                expires_at=datetime.fromisoformat(session_data["expires_at"]) if session_data.get("expires_at") else None,
                last_accessed=datetime.fromisoformat(session_data["last_accessed"]),
                security_level=SecurityLevel(session_data.get("security_level", "medium")),
                metadata=session_data.get("metadata", {}),
                tags=session_data.get("tags", [])
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def update_session(self, 
                           session_id: str,
                           updates: Dict[str, Any],
                           context: SessionContext) -> bool:
        """Update session data in memory."""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return False
            
            # Update fields
            for key, value in updates.items():
                if key in ["user_id", "agent_id", "session_type", "security_level", "metadata", "tags"]:
                    session_data[key] = value
            
            session_data["updated_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Updated session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    async def delete_session(self, 
                           session_id: str,
                           context: SessionContext) -> bool:
        """Delete session from memory."""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.analytics:
                del self.analytics[session_id]
            
            self.logger.info(f"Deleted session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def validate_session(self, 
                             session_id: str,
                             context: SessionContext) -> bool:
        """Validate session exists and is active."""
        try:
            session = await self.get_session(session_id, context)
            return session is not None and session.status == SessionStatus.ACTIVE
            
        except Exception as e:
            self.logger.error(f"Failed to validate session {session_id}: {e}")
            return False
    
    async def refresh_session(self, 
                            session_id: str,
                            context: SessionContext) -> Optional[Session]:
        """Refresh session expiration in memory."""
        try:
            session = await self.get_session(session_id, context)
            if not session:
                return None
            
            # Update expiration
            new_expires_at = datetime.utcnow() + timedelta(seconds=self.session_ttl)
            self.sessions[session_id]["expires_at"] = new_expires_at.isoformat()
            
            # Return updated session
            return await self.get_session(session_id, context)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh session {session_id}: {e}")
            return None
    
    async def revoke_session(self, 
                           session_id: str,
                           context: SessionContext) -> bool:
        """Revoke session access in memory."""
        try:
            if session_id in self.sessions:
                self.sessions[session_id]["status"] = SessionStatus.REVOKED.value
            
            self.logger.info(f"Revoked session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke session {session_id}: {e}")
            return False
    
    async def list_sessions(self, 
                          context: SessionContext,
                          filters: Optional[Dict[str, Any]] = None) -> List[Session]:
        """List sessions with optional filters from memory."""
        try:
            sessions = []
            for session_data in self.sessions.values():
                # Apply filters
                if filters:
                    if "user_id" in filters and session_data.get("user_id") != filters["user_id"]:
                        continue
                    if "agent_id" in filters and session_data.get("agent_id") != filters["agent_id"]:
                        continue
                    if "status" in filters and session_data.get("status") != filters["status"]:
                        continue
                
                session = Session(
                    session_id=session_data["session_id"],
                    user_id=session_data.get("user_id"),
                    agent_id=session_data.get("agent_id"),
                    session_type=SessionType(session_data.get("session_type", "user")),
                    status=SessionStatus(session_data.get("status", "active")),
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    expires_at=datetime.fromisoformat(session_data["expires_at"]) if session_data.get("expires_at") else None,
                    last_accessed=datetime.fromisoformat(session_data["last_accessed"]),
                    security_level=SecurityLevel(session_data.get("security_level", "medium")),
                    metadata=session_data.get("metadata", {}),
                    tags=session_data.get("tags", [])
                )
                sessions.append(session)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def create_session_token(self, 
                                 session_id: str,
                                 token_type: str,
                                 context: SessionContext) -> SessionToken:
        """Create a session token in memory."""
        try:
            token_id = str(uuid.uuid4())
            token_value = str(uuid.uuid4())
            now = datetime.utcnow()
            
            token = SessionToken(
                token_id=token_id,
                session_id=session_id,
                token_type=token_type,
                token_value=token_value,
                expires_at=now + timedelta(seconds=self.token_ttl),
                created_at=now,
                metadata={"context": context.metadata}
            )
            
            # Store token in memory
            self.tokens[token_value] = {
                "token_id": token_id,
                "session_id": session_id,
                "token_type": token_type,
                "token_value": token_value,
                "expires_at": token.expires_at.isoformat(),
                "created_at": token.created_at.isoformat(),
                "metadata": token.metadata
            }
            
            self.logger.info(f"Created token {token_id} for session {session_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create token for session {session_id}: {e}")
            raise
    
    async def validate_session_token(self, 
                                   token_value: str,
                                   context: SessionContext) -> Optional[Session]:
        """Validate session token and return session from memory."""
        try:
            token_data = self.tokens.get(token_value)
            if not token_data:
                return None
            
            # Check if token is expired
            if token_data.get("expires_at"):
                expires_at = datetime.fromisoformat(token_data["expires_at"])
                if datetime.utcnow() > expires_at:
                    return None
            
            # Get session
            session = await self.get_session(token_data["session_id"], context)
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to validate token: {e}")
            return None
    
    async def revoke_session_token(self, 
                                 token_id: str,
                                 context: SessionContext) -> bool:
        """Revoke session token in memory."""
        try:
            # Find token by ID
            for token_value, token_data in self.tokens.items():
                if token_data["token_id"] == token_id:
                    del self.tokens[token_value]
                    break
            
            self.logger.info(f"Revoked token {token_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke token {token_id}: {e}")
            return False
    
    async def get_session_analytics(self, 
                                   session_id: str,
                                   context: SessionContext) -> SessionAnalytics:
        """Get session analytics from memory."""
        try:
            analytics_data = self.analytics.get(session_id)
            if not analytics_data:
                return SessionAnalytics(session_id=session_id)
            
            return SessionAnalytics(
                session_id=analytics_data["session_id"],
                total_requests=analytics_data.get("total_requests", 0),
                successful_requests=analytics_data.get("successful_requests", 0),
                failed_requests=analytics_data.get("failed_requests", 0),
                average_response_time=analytics_data.get("average_response_time", 0.0),
                last_activity=datetime.fromisoformat(analytics_data["last_activity"]),
                security_events=analytics_data.get("security_events", 0),
                metadata=analytics_data.get("metadata", {})
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for session {session_id}: {e}")
            return SessionAnalytics(session_id=session_id)
    
    async def update_session_analytics(self, 
                                     session_id: str,
                                     analytics_data: Dict[str, Any],
                                     context: SessionContext) -> bool:
        """Update session analytics in memory."""
        try:
            current_analytics = self.analytics.get(session_id, {})
            
            # Update analytics
            current_analytics.update({
                "session_id": session_id,
                "total_requests": analytics_data.get("total_requests", current_analytics.get("total_requests", 0)),
                "successful_requests": analytics_data.get("successful_requests", current_analytics.get("successful_requests", 0)),
                "failed_requests": analytics_data.get("failed_requests", current_analytics.get("failed_requests", 0)),
                "average_response_time": analytics_data.get("average_response_time", current_analytics.get("average_response_time", 0.0)),
                "last_activity": datetime.utcnow().isoformat(),
                "security_events": analytics_data.get("security_events", current_analytics.get("security_events", 0)),
                "metadata": analytics_data.get("metadata", current_analytics.get("metadata", {}))
            })
            
            self.analytics[session_id] = current_analytics
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update analytics for session {session_id}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check in-memory session infrastructure health."""
        try:
            return {
                "status": "healthy",
                "adapter": "in_memory_session",
                "session_count": len(self.sessions),
                "token_count": len(self.tokens),
                "analytics_count": len(self.analytics),
                "session_ttl": self.session_ttl,
                "token_ttl": self.token_ttl,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter": "in_memory_session",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
