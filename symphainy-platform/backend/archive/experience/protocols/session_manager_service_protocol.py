#!/usr/bin/env python3
"""
Session Manager Service Protocol

Defines the contract for session management services in the Experience realm.
Handles user session lifecycle, state management, and session coordination.

WHAT (Session Manager Role): I manage user sessions and coordinate session state
HOW (Session Manager Service): I create, maintain, and terminate user sessions
"""

from typing import Dict, Any, Optional, List, runtime_checkable
from bases.protocols.service_protocol import ServiceProtocol


@runtime_checkable
class SessionManagerServiceProtocol(ServiceProtocol):
    """
    Protocol for Session Manager services in the Experience realm.
    
    Session Manager services handle:
    - User session lifecycle management
    - Session state coordination
    - Session security and validation
    - Multi-session coordination
    """
    
    # ============================================================================
    # SESSION LIFECYCLE MANAGEMENT
    # ============================================================================
    
    async def create_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user session.
        
        Args:
            user_id: ID of the user
            session_data: Initial session data
            
        Returns:
            Dict[str, Any]: Created session information
        """
        ...
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information by ID.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Optional[Dict[str, Any]]: Session data if found
        """
        ...
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update session data.
        
        Args:
            session_id: ID of the session
            updates: Data updates to apply
            
        Returns:
            bool: True if update successful
        """
        ...
    
    async def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a user session.
        
        Args:
            session_id: ID of the session to terminate
            
        Returns:
            bool: True if termination successful
        """
        ...
    
    # ============================================================================
    # SESSION STATE MANAGEMENT
    # ============================================================================
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session state.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Dict[str, Any]: Current session state
        """
        ...
    
    async def update_session_state(self, session_id: str, state_updates: Dict[str, Any]) -> bool:
        """
        Update session state.
        
        Args:
            session_id: ID of the session
            state_updates: State updates to apply
            
        Returns:
            bool: True if state update successful
        """
        ...
    
    async def validate_session_state(self, session_id: str) -> bool:
        """
        Validate session state integrity.
        
        Args:
            session_id: ID of the session
            
        Returns:
            bool: True if state is valid
        """
        ...
    
    # ============================================================================
    # SESSION SECURITY & VALIDATION
    # ============================================================================
    
    async def validate_session(self, session_id: str, user_context: Dict[str, Any]) -> bool:
        """
        Validate session security and permissions.
        
        Args:
            session_id: ID of the session
            user_context: User context for validation
            
        Returns:
            bool: True if session is valid
        """
        ...
    
    async def refresh_session_token(self, session_id: str) -> Optional[str]:
        """
        Refresh session authentication token.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Optional[str]: New token if refresh successful
        """
        ...
    
    async def check_session_permissions(self, session_id: str, required_permissions: List[str]) -> bool:
        """
        Check if session has required permissions.
        
        Args:
            session_id: ID of the session
            required_permissions: List of required permissions
            
        Returns:
            bool: True if session has all required permissions
        """
        ...
    
    # ============================================================================
    # MULTI-SESSION COORDINATION
    # ============================================================================
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of user sessions
        """
        ...
    
    async def coordinate_user_sessions(self, user_id: str) -> Dict[str, Any]:
        """
        Coordinate multiple sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict[str, Any]: Session coordination result
        """
        ...
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            int: Number of sessions cleaned up
        """
        ...
