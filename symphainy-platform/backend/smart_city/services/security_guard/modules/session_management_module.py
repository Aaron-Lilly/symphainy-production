#!/usr/bin/env python3
"""
Session Management Module - Security Guard Micro-Module

Handles session creation, validation, and management operations.
Part of the Security Guard Service micro-modular architecture.

WHAT (Session Role): I handle session creation, validation, and management
HOW (Session Implementation): I use infrastructure abstractions for session management
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import audit context
from utilities.audit_context_utility_integrated import AuditContext


class SessionManagementModule:
    """
    Session Management Module - Security Guard Micro-Module
    
    Handles session creation, validation, and management operations.
    Part of the Security Guard Service micro-modular architecture.
    
    WHAT (Session Role): I handle session creation, validation, and management
    HOW (Session Implementation): I use infrastructure abstractions for session management
    """
    
    def __init__(self, session_abstraction=None, service_name: str = "session_management_module"):
        """Initialize Session Management Module."""
        self.service_name = service_name
        self.session_abstraction = session_abstraction
        self.logger = self.service.di_container.get_logger(f"SessionManagementModule-{service_name}")
        
        # Session statistics
        self.session_stats = {
            "sessions_created": 0,
            "sessions_validated": 0,
            "sessions_invalidated": 0
        }
        
        self.logger.info(f"✅ Session Management Module '{service_name}' initialized")
    
    async def initialize(self):
        """Initialize Session Management Module."""
        try:
            self.logger.info(f"🚀 Initializing Session Management Module '{self.service_name}'...")
            self.logger.info(f"✅ Session Management Module '{self.service_name}' initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Session Management Module '{self.service_name}': {e}")
            raise
    
    async def create_session(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Create session using session abstraction."""
        try:
            if self.session_abstraction:
                session_id = await self.session_abstraction.create_session(user_id, tenant_id)
                
                # Create audit context
                audit_ctx = AuditContext(
                    audit_id=str(uuid.uuid4()),
                    user_id=user_id,
                    tenant_id=tenant_id,
                    action="create_session",
                    resource="user_session",
                    service_name=self.service_name,
                    outcome="success",
                    details={"session_id": session_id}
                )
                
                self.session_stats["sessions_created"] += 1
                self.logger.info(f"Session created: {session_id} for user {user_id}")
                return {
                    "success": True,
                    "session_id": session_id,
                    "audit_context": audit_ctx
                }
            
            return {
                "success": False,
                "message": "Session abstraction not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session creation failed: {e}")
            return {
                "success": False,
                "message": f"Session creation failed: {e}"
            }
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate session using session abstraction."""
        try:
            if self.session_abstraction:
                session_valid = await self.session_abstraction.validate_session(session_id)
                
                if session_valid:
                    self.session_stats["sessions_validated"] += 1
                    self.logger.info(f"Session validated: {session_id}")
                    return {
                        "success": True,
                        "message": "Session valid"
                    }
            
            return {
                "success": False,
                "message": "Session invalid"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session validation failed: {e}")
            return {
                "success": False,
                "message": f"Session validation failed: {e}"
            }
    
    async def invalidate_session(self, session_id: str) -> Dict[str, Any]:
        """Invalidate session."""
        try:
            if self.session_abstraction:
                # Use session abstraction to invalidate session
                invalidated = await self.session_abstraction.invalidate_session(session_id)
                
                if invalidated:
                    self.session_stats["sessions_invalidated"] += 1
                    self.logger.info(f"Session invalidated: {session_id}")
                    return {
                        "success": True,
                        "message": "Session invalidated"
                    }
            
            return {
                "success": False,
                "message": "Session invalidation failed"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Session invalidation failed: {e}")
            return {
                "success": False,
                "message": f"Session invalidation failed: {e}"
            }
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information."""
        try:
            if self.session_abstraction:
                session_info = await self.session_abstraction.get_session_info(session_id)
                return {
                    "success": True,
                    "session_info": session_info
                }
            
            return {
                "success": False,
                "message": "Session abstraction not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session info: {e}")
            return {
                "success": False,
                "message": f"Failed to get session info: {e}"
            }
    
    async def get_session_metrics(self) -> Dict[str, Any]:
        """Get session management metrics."""
        try:
            return {
                "sessions_created": self.session_stats["sessions_created"],
                "sessions_validated": self.session_stats["sessions_validated"],
                "sessions_invalidated": self.session_stats["sessions_invalidated"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session metrics: {e}")
            return {}
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return [
            "session_creation",
            "session_validation",
            "session_invalidation",
            "session_info_retrieval",
            "session_metrics"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "SessionManagementModule",
            "service_name": self.service_name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "session_abstraction_available": self.session_abstraction is not None,
            "metrics": await self.get_session_metrics()
        }



