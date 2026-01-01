#!/usr/bin/env python3
"""
Session Manager Micro-Module

Manages user experience sessions, state, and lifecycle.

WHAT (Micro-Module): I manage user experience sessions and state
HOW (Implementation): I store session data, track state changes, and manage session lifecycle
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from utilities import UserContext
from config.environment_loader import EnvironmentLoader


class SessionManagerModule:
    """
    Session Manager Micro-Module
    
    Provides functionality to create, manage, and track user experience sessions.
    """
    
    def __init__(self, environment: EnvironmentLoader, logger: Optional[logging.Logger] = None):
        """Initialize Session Manager Module."""
        self.environment = environment
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        
        # In-memory session store (for MVP)
        # In a real system, this would be a persistent store (e.g., Redis, database)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Session configuration
        self.session_timeout = timedelta(hours=24)  # 24 hour session timeout
        self.max_sessions_per_user = 5  # Maximum concurrent sessions per user
        
        self.logger.info("🎫 Session Manager Module initialized")
    
    async def initialize(self):
        """Initialize the Session Manager Module."""
        self.logger.info("🚀 Initializing Session Manager Module...")
        # Load any configurations or connect to persistent storage here
        self.is_initialized = True
        self.logger.info("✅ Session Manager Module initialized successfully")
    
    async def shutdown(self):
        """Shutdown the Session Manager Module."""
        self.logger.info("🛑 Shutting down Session Manager Module...")
        # Clean up resources or close connections here
        self.is_initialized = False
        self.logger.info("✅ Session Manager Module shutdown successfully")
    
    async def create_session(self, user_context: UserContext, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user experience session.
        
        Args:
            user_context: Context of the user.
            session_data: Initial session configuration and preferences.
            
        Returns:
            A dictionary containing the session ID and initial state.
        """
        self.logger.debug(f"Creating session for user: {user_context.user_id}")
        
        try:
            # Check if user has reached maximum session limit
            user_sessions = [s for s in self.sessions.values() if s.get("user_id") == user_context.user_id]
            if len(user_sessions) >= self.max_sessions_per_user:
                return {
                    "success": False,
                    "error": "Maximum session limit reached",
                    "message": f"User can have maximum {self.max_sessions_per_user} concurrent sessions"
                }
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create session data
            session_info = {
                "session_id": session_id,
                "user_id": user_context.user_id,
                "user_context": user_context,
                "session_data": session_data,
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + self.session_timeout).isoformat(),
                "state": {
                    "current_pillar": None,
                    "navigation_history": [],
                    "preferences": session_data.get("preferences", {}),
                    "ui_state": {},
                    "data_context": {}
                }
            }
            
            # Store session
            self.sessions[session_id] = session_info
            
            self.logger.info(f"✅ Session created: {session_id} for user: {user_context.user_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "session_info": session_info,
                "message": "Session created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create session: {e}")
            return {"success": False, "error": str(e), "message": "Failed to create session"}
    
    async def get_session_state(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Retrieve the current state of a user session.
        
        Args:
            session_id: The ID of the session.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the session state.
        """
        self.logger.debug(f"Getting session state for: {session_id}")
        
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}
            
            session = self.sessions[session_id]
            
            # Check if session belongs to user
            if session.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to session"}
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session.get("expires_at", ""))
            if datetime.utcnow() > expires_at:
                # Mark session as expired
                session["status"] = "expired"
                return {"success": False, "error": "Session expired"}
            
            # Update last accessed time
            session["last_accessed"] = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "session_id": session_id,
                "session_state": session.get("state", {}),
                "session_info": {
                    "status": session.get("status"),
                    "created_at": session.get("created_at"),
                    "last_accessed": session.get("last_accessed"),
                    "expires_at": session.get("expires_at")
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session state: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get session state"}
    
    async def update_session_state(self, session_id: str, state_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Update the state of a user session.
        
        Args:
            session_id: The ID of the session.
            state_data: The new state data.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the success of the update.
        """
        self.logger.debug(f"Updating session state for: {session_id}")
        
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}
            
            session = self.sessions[session_id]
            
            # Check if session belongs to user
            if session.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to session"}
            
            # Check if session is active
            if session.get("status") != "active":
                return {"success": False, "error": "Session is not active"}
            
            # Update session state
            current_state = session.get("state", {})
            current_state.update(state_data)
            session["state"] = current_state
            session["last_accessed"] = datetime.utcnow().isoformat()
            
            # Update navigation history if current pillar changed
            if "current_pillar" in state_data:
                navigation_history = current_state.get("navigation_history", [])
                navigation_history.append({
                    "pillar": state_data["current_pillar"],
                    "timestamp": datetime.utcnow().isoformat()
                })
                current_state["navigation_history"] = navigation_history
            
            self.logger.info(f"✅ Session state updated: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "state_updated": True,
                "message": "Session state updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update session state: {e}")
            return {"success": False, "error": str(e), "message": "Failed to update session state"}
    
    async def terminate_session(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Terminate a user experience session.
        
        Args:
            session_id: The ID of the session to terminate.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the termination status.
        """
        self.logger.debug(f"Terminating session: {session_id}")
        
        try:
            if session_id not in self.sessions:
                return {"success": False, "error": "Session not found"}
            
            session = self.sessions[session_id]
            
            # Check if session belongs to user
            if session.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to session"}
            
            # Mark session as terminated
            session["status"] = "terminated"
            session["terminated_at"] = datetime.utcnow().isoformat()
            
            # Remove from active sessions (keep for audit purposes)
            # In a real system, you might want to archive the session data
            
            self.logger.info(f"✅ Session terminated: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "terminated": True,
                "message": "Session terminated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to terminate session: {e}")
            return {"success": False, "error": str(e), "message": "Failed to terminate session"}
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """
        Clean up expired sessions.
        
        Returns:
            A dictionary indicating the cleanup results.
        """
        self.logger.info("Cleaning up expired sessions...")
        
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                expires_at = datetime.fromisoformat(session.get("expires_at", ""))
                if current_time > expires_at and session.get("status") == "active":
                    session["status"] = "expired"
                    expired_sessions.append(session_id)
            
            self.logger.info(f"✅ Cleaned up {len(expired_sessions)} expired sessions")
            
            return {
                "success": True,
                "expired_sessions": expired_sessions,
                "cleanup_count": len(expired_sessions),
                "message": f"Cleaned up {len(expired_sessions)} expired sessions"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup expired sessions: {e}")
            return {"success": False, "error": str(e), "message": "Failed to cleanup expired sessions"}
    
    async def get_user_sessions(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Get all sessions for a user.
        
        Args:
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the user's sessions.
        """
        self.logger.debug(f"Getting sessions for user: {user_context.user_id}")
        
        try:
            user_sessions = [
                {
                    "session_id": session_id,
                    "status": session.get("status"),
                    "created_at": session.get("created_at"),
                    "last_accessed": session.get("last_accessed"),
                    "expires_at": session.get("expires_at"),
                    "current_pillar": session.get("state", {}).get("current_pillar")
                }
                for session_id, session in self.sessions.items()
                if session.get("user_id") == user_context.user_id
            ]
            
            return {
                "success": True,
                "user_id": user_context.user_id,
                "sessions": user_sessions,
                "session_count": len(user_sessions)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user sessions: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get user sessions"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the Session Manager Module."""
        return {
            "module_name": "SessionManagerModule",
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_sessions": len([s for s in self.sessions.values() if s.get("status") == "active"]),
            "total_sessions": len(self.sessions),
            "message": "Session Manager Module is operational."
        }
