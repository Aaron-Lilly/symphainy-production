#!/usr/bin/env python3
"""
Session Coordinator Micro-Module

Manages session coordination and cross-pillar communication.

WHAT (Micro-Module): I manage session coordination and cross-pillar communication
HOW (Implementation): I coordinate sessions across different pillars and services
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from config.environment_loader import EnvironmentLoader
from utilities import UserContext


class SessionCoordinatorModule:
    """
    Session Coordinator Micro-Module
    
    Manages session coordination and cross-pillar communication.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, environment: Optional[EnvironmentLoader] = None):
        """Initialize Session Coordinator Module."""
        self.logger = logger or logging.getLogger(__name__)
        self.environment = environment
        self.is_initialized = False
        
        # Session storage (in-memory for MVP)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hour session timeout
        
        self.logger.info("🎫 Session Coordinator Module initialized")
    
    async def initialize(self):
        """Initialize the Session Coordinator Module."""
        self.logger.info("🚀 Initializing Session Coordinator Module...")
        self.is_initialized = True
        self.logger.info("✅ Session Coordinator Module initialized successfully")
    
    async def create_session(
        self, 
        user_context: UserContext, 
        session_type: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new session for cross-pillar coordination.
        
        Args:
            user_context: Context of the user
            session_type: Type of session to create
            
        Returns:
            A dictionary containing session information
        """
        self.logger.info(f"Creating session for user: {user_context.user_id}")
        
        try:
            session_id = f"session_{user_context.user_id}_{int(datetime.utcnow().timestamp())}"
            
            session_data = {
                "session_id": session_id,
                "user_id": user_context.user_id,
                "user_context": user_context,
                "session_type": session_type,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + self.session_timeout).isoformat(),
                "status": "active",
                "pillar_sessions": {},
                "cross_pillar_data": {}
            }
            
            # Store session
            self.sessions[session_id] = session_data
            
            return {
                "success": True,
                "session_id": session_id,
                "expires_at": session_data["expires_at"],
                "message": "Session created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create session: {str(e)}"
            }
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session data if found, None otherwise
        """
        self.logger.info(f"Getting session: {session_id}")
        
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            # Check if session has expired
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                session["status"] = "expired"
                return None
            
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to get session: {str(e)}")
            return None
    
    async def update_session(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update session data.
        
        Args:
            session_id: The session ID
            updates: Updates to apply
            
        Returns:
            A dictionary containing update results
        """
        self.logger.info(f"Updating session: {session_id}")
        
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Update session data
            session.update(updates)
            session["last_updated"] = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "message": "Session updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update session: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to update session: {str(e)}"
            }
    
    async def add_pillar_session(
        self, 
        session_id: str, 
        pillar: str, 
        pillar_session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add pillar-specific session data.
        
        Args:
            session_id: The main session ID
            pillar: The pillar name
            pillar_session_data: Pillar-specific session data
            
        Returns:
            A dictionary containing the result
        """
        self.logger.info(f"Adding pillar session for {pillar} to session: {session_id}")
        
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Add pillar session data
            session["pillar_sessions"][pillar] = {
                **pillar_session_data,
                "added_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "message": f"Pillar session added for {pillar}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add pillar session: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to add pillar session: {str(e)}"
            }
    
    async def get_cross_pillar_data(
        self, 
        session_id: str, 
        pillar: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cross-pillar data for a specific pillar.
        
        Args:
            session_id: The session ID
            pillar: The pillar name
            
        Returns:
            Cross-pillar data if found, None otherwise
        """
        self.logger.info(f"Getting cross-pillar data for {pillar} in session: {session_id}")
        
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            return session["cross_pillar_data"].get(pillar)
            
        except Exception as e:
            self.logger.error(f"Failed to get cross-pillar data: {str(e)}")
            return None
    
    async def set_cross_pillar_data(
        self, 
        session_id: str, 
        pillar: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set cross-pillar data for a specific pillar.
        
        Args:
            session_id: The session ID
            pillar: The pillar name
            data: Data to store
            
        Returns:
            A dictionary containing the result
        """
        self.logger.info(f"Setting cross-pillar data for {pillar} in session: {session_id}")
        
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Set cross-pillar data
            session["cross_pillar_data"][pillar] = {
                **data,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "message": f"Cross-pillar data set for {pillar}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to set cross-pillar data: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to set cross-pillar data: {str(e)}"
            }
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """
        Clean up expired sessions.
        
        Returns:
            A dictionary containing cleanup results
        """
        self.logger.info("Cleaning up expired sessions")
        
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                expires_at = datetime.fromisoformat(session["expires_at"])
                if current_time > expires_at:
                    expired_sessions.append(session_id)
            
            # Remove expired sessions
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            return {
                "success": True,
                "expired_sessions_removed": len(expired_sessions),
                "active_sessions": len(self.sessions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to cleanup expired sessions: {str(e)}"
            }
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics for monitoring."""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len([s for s in self.sessions.values() if s["status"] == "active"]),
            "expired_sessions": len([s for s in self.sessions.values() if s["status"] == "expired"]),
            "timestamp": datetime.utcnow().isoformat()
        }
