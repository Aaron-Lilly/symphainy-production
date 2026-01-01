#!/usr/bin/env python3
"""
Session Manager Service

WHAT: Manages user session lifecycle, state persistence, and session security
HOW: Creates/manages sessions, persists state via TrafficCop, tracks workflows

This service provides session management by composing Smart City services
(TrafficCop for session/state storage, SecurityGuard for authentication)
and Business Enablement orchestrators for workflow state.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SessionManagerService(RealmServiceBase):
    """
    Session Manager Service for Experience realm.
    
    Manages user session lifecycle, state persistence, and session security
    by composing Smart City services (TrafficCop for session/state storage,
    SecurityGuard for authentication) and orchestrators for workflow tracking.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Session Manager Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.security_guard = None
        self.traffic_cop = None
        
        # Session cache
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Session configuration
        self.session_ttl = 3600  # 1 hour in seconds
        self.max_sessions_per_user = 5
    
    async def initialize(self) -> bool:
        """Initialize Session Manager Service."""
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.security_guard = await self.get_security_guard_api()
            self.traffic_cop = await self.get_traffic_cop_api()
            
            # 2. Register with Curator
            await self.register_with_curator(
                capabilities=["session_management", "state_persistence", "session_security", "workflow_tracking"],
                soa_apis=[
                    "create_session", "get_session", "update_session", "destroy_session",
                    "persist_session_state", "restore_session_state", "validate_session",
                    "track_workflow_state", "get_session_history", "cleanup_expired_sessions"
                ],
                mcp_tools=[],  # Experience services provide SOA APIs, not MCP tools
                additional_metadata={
                    "layer": "experience",
                    "session_management": True,
                    "composes": "smart_city_services"
                }
            )
            
            self.logger.info("✅ Session Manager Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Session Manager Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs (Session Lifecycle)
    # ========================================================================
    
    async def create_session(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user session (SOA API).
        
        Args:
            user_id: User ID
            context: Optional session context data
        
        Returns:
            Session data
        """
        try:
            # Check max sessions per user
            user_sessions = [s for s in self.sessions.values() if s.get("user_id") == user_id]
            if len(user_sessions) >= self.max_sessions_per_user:
                # Cleanup oldest session
                oldest = min(user_sessions, key=lambda s: s["created_at"])
                await self.destroy_session(oldest["session_id"])
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create session with orchestrator context and conversations
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "context": context or {},
                "state": {},
                "workflow_states": {},
                # NEW: Orchestrator context for tracking orchestrator workflows
                "orchestrator_context": {
                    "active_orchestrators": [],
                    "enabling_services": {},
                    "workflow_delegation_chain": []
                },
                # NEW: Agent conversations (Guide and Liaison agents)
                "conversations": {
                    "guide_agent": {
                        "conversation_id": f"conv_guide_{session_id}",
                        "messages": [],
                        "orchestrator_context": {}
                    },
                    "content_liaison": {
                        "conversation_id": f"conv_content_{session_id}",
                        "messages": [],
                        "orchestrator_context": {}
                    },
                    "insights_liaison": {
                        "conversation_id": f"conv_insights_{session_id}",
                        "messages": [],
                        "orchestrator_context": {}
                    },
                    "operations_liaison": {
                        "conversation_id": f"conv_operations_{session_id}",
                        "messages": [],
                        "orchestrator_context": {}
                    },
                    "business_outcomes_liaison": {
                        "conversation_id": f"conv_business_outcomes_{session_id}",
                        "messages": [],
                        "orchestrator_context": {}
                    }
                },
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.session_ttl)).isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Store in cache
            self.sessions[session_id] = session
            
            # Persist via Librarian
            await self.persist_session_state(session_id, session)
            
            self.logger.info(f"✅ Session created: {session_id} for user {user_id}")
            
            return {
                "success": True,
                "session": session
            }
            
        except Exception as e:
            self.logger.error(f"❌ Create session failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get session data (SOA API).
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data
        """
        try:
            # Check cache first
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Validate not expired
                expires_at = datetime.fromisoformat(session["expires_at"])
                if datetime.utcnow() > expires_at:
                    await self.destroy_session(session_id)
                    return {
                        "success": False,
                        "error": "Session expired"
                    }
                
                # Update last activity
                session["last_activity"] = datetime.utcnow().isoformat()
                
                return {
                    "success": True,
                    "session": session
                }
            
            # Try to restore from storage
            restored = await self.restore_session_state(session_id)
            if restored["success"]:
                return restored
            
            return {
                "success": False,
                "error": "Session not found"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get session failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_session(
        self,
        session_id: str,
        state_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update session state (SOA API).
        
        Args:
            session_id: Session ID
            state_data: State data to update
        
        Returns:
            Updated session
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return session_result
            
            session = session_result["session"]
            
            # Update state
            session["state"].update(state_data)
            session["last_activity"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.sessions[session_id] = session
            
            # Persist
            await self.persist_session_state(session_id, session)
            
            self.logger.info(f"✅ Session updated: {session_id}")
            
            return {
                "success": True,
                "session": session
            }
            
        except Exception as e:
            self.logger.error(f"❌ Update session failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def destroy_session(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Destroy session (SOA API).
        
        Args:
            session_id: Session ID
        
        Returns:
            Destroy result
        """
        try:
            # Remove from cache
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Note: Could also delete from storage via Librarian
            # For now, we'll let it expire naturally
            
            self.logger.info(f"✅ Session destroyed: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "destroyed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Destroy session failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (State Management)
    # ========================================================================
    
    async def persist_session_state(
        self,
        session_id: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Persist session state to storage (SOA API).
        
        Args:
            session_id: Session ID
            state: Session state to persist
        
        Returns:
            Persistence result
        """
        try:
            # Store via TrafficCop (Smart City role for session/state management)
            if self.traffic_cop:
                result = await self.traffic_cop.persist_session_state(
                    session_id=session_id,
                    state=state
                )
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "persisted_at": datetime.utcnow().isoformat()
                }
            else:
                # Fallback to local storage only
                self.logger.warning("⚠️ TrafficCop not available, using local cache only")
                return {
                    "success": True,
                    "session_id": session_id,
                    "persisted_at": datetime.utcnow().isoformat(),
                    "cached_only": True
                }
            
        except Exception as e:
            self.logger.error(f"❌ Persist session state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def restore_session_state(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Restore session state from storage (SOA API).
        
        Args:
            session_id: Session ID
        
        Returns:
            Restored session
        """
        try:
            # Restore via TrafficCop (Smart City role for session/state management)
            if self.traffic_cop:
                result = await self.traffic_cop.restore_session_state(session_id)
                
                if result.get("success"):
                    session = result.get("session")
                    
                    # Validate not expired
                    expires_at = datetime.fromisoformat(session["expires_at"])
                    if datetime.utcnow() > expires_at:
                        return {
                            "success": False,
                            "error": "Session expired"
                        }
                    
                    # Update cache
                    self.sessions[session_id] = session
                    
                    self.logger.info(f"✅ Session state restored: {session_id}")
                    
                    return {
                        "success": True,
                        "session": session
                    }
            
            return {
                "success": False,
                "error": "Session not found in storage"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Restore session state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_session(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Validate session integrity (SOA API).
        
        Args:
            session_id: Session ID
        
        Returns:
            Validation result
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            
            if not session_result["success"]:
                return {
                    "valid": False,
                    "error": session_result.get("error")
                }
            
            session = session_result["session"]
            
            # Validate expiration
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                return {
                    "valid": False,
                    "error": "Session expired"
                }
            
            # Validate via SecurityGuard
            auth_result = await self.authenticate_request({
                "session_id": session_id,
                "user_id": session["user_id"]
            })
            
            return {
                "valid": True,
                "session_id": session_id,
                "authenticated": auth_result.get("authenticated", False)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Validate session failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Workflow Tracking)
    # ========================================================================
    
    async def track_workflow_state(
        self,
        session_id: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Track workflow state in session (SOA API).
        
        Args:
            session_id: Session ID
            workflow_id: Workflow ID
        
        Returns:
            Workflow state
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return session_result
            
            session = session_result["session"]
            
            # Track workflow
            if "workflow_states" not in session:
                session["workflow_states"] = {}
            
            session["workflow_states"][workflow_id] = {
                "workflow_id": workflow_id,
                "tracked_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Update session
            await self.update_session(session_id, session["state"])
            
            self.logger.info(f"✅ Workflow tracked: {workflow_id} in session {session_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Track workflow state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_history(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get session history (SOA API).
        
        Args:
            session_id: Session ID
        
        Returns:
            Session history
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return session_result
            
            session = session_result["session"]
            
            # Get history
            history = {
                "session_id": session_id,
                "user_id": session["user_id"],
                "created_at": session["created_at"],
                "last_activity": session["last_activity"],
                "workflow_count": len(session.get("workflow_states", {})),
                "state_updates": len(session.get("state", {}))
            }
            
            return {
                "success": True,
                "history": history
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get session history failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """
        Cleanup expired sessions (SOA API).
        
        Returns:
            Cleanup result
        """
        try:
            now = datetime.utcnow()
            expired = []
            
            for session_id, session in list(self.sessions.items()):
                expires_at = datetime.fromisoformat(session["expires_at"])
                if now > expires_at:
                    await self.destroy_session(session_id)
                    expired.append(session_id)
            
            self.logger.info(f"✅ Cleaned up {len(expired)} expired sessions")
            
            return {
                "success": True,
                "cleaned_up": len(expired),
                "expired_sessions": expired
            }
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup expired sessions failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "active_sessions": len(self.sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ========================================================================
    # SOA APIs (Agent Conversation Management - NEW)
    # ========================================================================
    
    async def add_conversation_message(
        self,
        session_id: str,
        agent_type: str,  # "guide_agent", "content_liaison", etc.
        role: str,  # "user" or "assistant"
        content: str,
        orchestrator_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add message to conversation history (SOA API).
        
        Args:
            session_id: Session ID
            agent_type: Type of agent ("guide_agent", "content_liaison", etc.)
            role: Message role ("user" or "assistant")
            content: Message content
            orchestrator_context: Optional orchestrator context
        
        Returns:
            Result with message added
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = session_result["session"]
            
            # Ensure conversations dict exists
            if "conversations" not in session:
                session["conversations"] = {}
            
            # Ensure agent conversation exists
            if agent_type not in session["conversations"]:
                session["conversations"][agent_type] = {
                    "conversation_id": f"conv_{agent_type}_{session_id}",
                    "messages": [],
                    "orchestrator_context": {}
                }
            
            # Add message
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if orchestrator_context:
                message["orchestrator_context"] = orchestrator_context
                # Update conversation orchestrator context
                session["conversations"][agent_type]["orchestrator_context"].update(orchestrator_context)
            
            session["conversations"][agent_type]["messages"].append(message)
            session["last_activity"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.sessions[session_id] = session
            
            # Persist
            await self.persist_session_state(session_id, session)
            
            self.logger.info(f"✅ Conversation message added: {agent_type} in session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "agent_type": agent_type,
                "message_count": len(session["conversations"][agent_type]["messages"])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Add conversation message failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_conversation_history(
        self,
        session_id: str,
        agent_type: str
    ) -> Dict[str, Any]:
        """
        Get conversation history for agent (SOA API).
        
        Args:
            session_id: Session ID
            agent_type: Type of agent
        
        Returns:
            Conversation history
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = session_result["session"]
            
            # Get conversation
            if "conversations" not in session or agent_type not in session["conversations"]:
                return {
                    "success": True,
                    "conversation_id": None,
                    "messages": [],
                    "orchestrator_context": {}
                }
            
            conversation = session["conversations"][agent_type]
            
            return {
                "success": True,
                "conversation_id": conversation.get("conversation_id"),
                "messages": conversation.get("messages", []),
                "orchestrator_context": conversation.get("orchestrator_context", {})
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get conversation history failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_conversation_orchestrator_context(
        self,
        session_id: str,
        agent_type: str,
        orchestrator_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update orchestrator context in conversation (SOA API).
        
        Args:
            session_id: Session ID
            agent_type: Type of agent
            orchestrator_context: Orchestrator context to update
        
        Returns:
            Update result
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = session_result["session"]
            
            # Ensure conversations dict exists
            if "conversations" not in session:
                session["conversations"] = {}
            
            # Ensure agent conversation exists
            if agent_type not in session["conversations"]:
                session["conversations"][agent_type] = {
                    "conversation_id": f"conv_{agent_type}_{session_id}",
                    "messages": [],
                    "orchestrator_context": {}
                }
            
            # Update orchestrator context
            session["conversations"][agent_type]["orchestrator_context"].update(orchestrator_context)
            session["last_activity"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.sessions[session_id] = session
            
            # Persist
            await self.persist_session_state(session_id, session)
            
            self.logger.info(f"✅ Conversation orchestrator context updated: {agent_type} in session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "agent_type": agent_type
            }
            
        except Exception as e:
            self.logger.error(f"❌ Update conversation orchestrator context failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Orchestrator Context Management - NEW)
    # ========================================================================
    
    async def track_orchestrator_workflow(
        self,
        session_id: str,
        orchestrator_name: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track orchestrator workflow in session (SOA API).
        
        Args:
            session_id: Session ID
            orchestrator_name: Name of orchestrator
            workflow_data: Workflow data
        
        Returns:
            Tracking result
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = session_result["session"]
            
            # Ensure orchestrator_context exists
            if "orchestrator_context" not in session:
                session["orchestrator_context"] = {
                    "active_orchestrators": [],
                    "enabling_services": {},
                    "workflow_delegation_chain": []
                }
            
            # Add or update orchestrator workflow
            workflow_entry = {
                "orchestrator_name": orchestrator_name,
                "workflow_id": workflow_data.get("workflow_id"),
                "status": workflow_data.get("status", "active"),
                "started_at": workflow_data.get("started_at", datetime.utcnow().isoformat()),
                "enabling_services": workflow_data.get("enabling_services", [])
            }
            
            # Update or add to active orchestrators
            active_orchestrators = session["orchestrator_context"]["active_orchestrators"]
            existing = next((o for o in active_orchestrators if o.get("orchestrator_name") == orchestrator_name), None)
            
            if existing:
                existing.update(workflow_entry)
            else:
                active_orchestrators.append(workflow_entry)
            
            session["last_activity"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.sessions[session_id] = session
            
            # Persist
            await self.persist_session_state(session_id, session)
            
            self.logger.info(f"✅ Orchestrator workflow tracked: {orchestrator_name} in session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "orchestrator_name": orchestrator_name,
                "workflow_id": workflow_data.get("workflow_id")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Track orchestrator workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_orchestrator_state(
        self,
        session_id: str,
        orchestrator_name: str
    ) -> Dict[str, Any]:
        """
        Get orchestrator state from session (SOA API).
        
        Args:
            session_id: Session ID
            orchestrator_name: Name of orchestrator
        
        Returns:
            Orchestrator state
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = session_result["session"]
            
            # Get orchestrator context
            orchestrator_context = session.get("orchestrator_context", {})
            active_orchestrators = orchestrator_context.get("active_orchestrators", [])
            
            # Find orchestrator
            orchestrator = next((o for o in active_orchestrators if o.get("orchestrator_name") == orchestrator_name), None)
            
            if orchestrator:
                return {
                    "success": True,
                    "orchestrator_name": orchestrator_name,
                    "state": orchestrator
                }
            else:
                return {
                    "success": True,
                    "orchestrator_name": orchestrator_name,
                    "state": None
                }
            
        except Exception as e:
            self.logger.error(f"❌ Get orchestrator state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_enabling_service_status(
        self,
        session_id: str,
        service_name: str,
        status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update enabling service status in session (SOA API).
        
        Args:
            session_id: Session ID
            service_name: Name of enabling service
            status: Service status data
        
        Returns:
            Update result
        """
        try:
            # Get session
            session_result = await self.get_session(session_id)
            if not session_result["success"]:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            session = session_result["session"]
            
            # Ensure orchestrator_context exists
            if "orchestrator_context" not in session:
                session["orchestrator_context"] = {
                    "active_orchestrators": [],
                    "enabling_services": {},
                    "workflow_delegation_chain": []
                }
            
            # Update enabling service status
            enabling_services = session["orchestrator_context"]["enabling_services"]
            if service_name not in enabling_services:
                enabling_services[service_name] = {}
            
            enabling_services[service_name].update(status)
            enabling_services[service_name]["last_used"] = datetime.utcnow().isoformat()
            
            session["last_activity"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.sessions[session_id] = session
            
            # Persist
            await self.persist_session_state(session_id, session)
            
            self.logger.info(f"✅ Enabling service status updated: {service_name} in session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "service_name": service_name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Update enabling service status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "experience_service",
            "realm": "experience",
            "layer": "session_management",
            "capabilities": [
                "session_management", "state_persistence", "session_security", "workflow_tracking",
                "agent_conversation_management", "orchestrator_tracking"  # NEW
            ],
            "soa_apis": [
                "create_session", "get_session", "update_session", "destroy_session",
                "persist_session_state", "restore_session_state", "validate_session",
                "track_workflow_state", "get_session_history", "cleanup_expired_sessions",
                # NEW: Agent conversation management
                "add_conversation_message", "get_conversation_history", "update_conversation_orchestrator_context",
                # NEW: Orchestrator tracking
                "track_orchestrator_workflow", "get_orchestrator_state", "update_enabling_service_status"
            ],
            "mcp_tools": [],
            "composes": "smart_city_services"
        }


