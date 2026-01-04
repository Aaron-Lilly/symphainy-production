#!/usr/bin/env python3
"""
WebSocket Session Management Module - Traffic Cop Service

Handles WebSocket connection linking to Traffic Cop sessions and message routing.
WebSocket connections are created via Agentic/Experience SDKs (which use Communication Foundation),
but are linked to Traffic Cop sessions for session/state management.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class WebSocketSessionManagement:
    """WebSocket session management module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def link_websocket_to_session(
        self, 
        websocket_id: str, 
        session_id: str,
        agent_type: Optional[str] = None,  # "guide" or "liaison"
        pillar: Optional[str] = None        # For liaison agents: "content", "insights", etc.
    ) -> Dict[str, Any]:
        """
        Link WebSocket connection (from Agentic SDK) to Traffic Cop session.
        
        Args:
            websocket_id: WebSocket connection ID from Agentic SDK
            session_id: Traffic Cop session ID
            agent_type: Type of agent ("guide" or "liaison")
            pillar: Pillar name for liaison agents (content, insights, operations, business_outcomes)
        
        Returns:
            Dict with success status and connection details
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "link_websocket_to_session_start",
            success=True,
            details={"websocket_id": websocket_id, "session_id": session_id, "agent_type": agent_type, "pillar": pillar}
        )
        
        try:
            # Verify session exists
            session_data = await self.service.session_abstraction.get_session(session_id)
            if not session_data:
                await self.service.record_health_metric("link_websocket_session_not_found", 1.0, {"session_id": session_id})
                await self.service.log_operation_with_telemetry("link_websocket_to_session_complete", success=False, details={"error": "session_not_found"})
                return {
                    "success": False,
                    "error": "Session not found",
                    "websocket_id": websocket_id,
                    "session_id": session_id
                }
            
            # Check if connection registry is available (Redis-backed for horizontal scaling)
            if not self.service.websocket_connection_registry:
                await self.service.record_health_metric("link_websocket_registry_unavailable", 1.0, {"session_id": session_id})
                await self.service.log_operation_with_telemetry("link_websocket_to_session_complete", success=False, details={"error": "registry_unavailable"})
                return {
                    "success": False,
                    "error": "WebSocket Connection Registry not available",
                    "websocket_id": websocket_id,
                    "session_id": session_id
                }
            
            # Store connection with metadata in Redis
            connection_info = {
                "websocket_id": websocket_id,
                "session_id": session_id,
                "agent_type": agent_type,
                "pillar": pillar,
                "linked_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Register connection in Redis (for horizontal scaling)
            metadata = {
                "linked_at": connection_info["linked_at"],
                "status": "active"
            }
            registered = await self.service.websocket_connection_registry.register_connection(
                websocket_id=websocket_id,
                session_id=session_id,
                agent_type=agent_type,
                pillar=pillar,
                metadata=metadata
            )
            
            if not registered:
                await self.service.record_health_metric("link_websocket_registration_failed", 1.0, {"session_id": session_id})
                await self.service.log_operation_with_telemetry("link_websocket_to_session_complete", success=False, details={"error": "registration_failed"})
                return {
                    "success": False,
                    "error": "Failed to register connection in Redis",
                    "websocket_id": websocket_id,
                    "session_id": session_id
                }
            
            # Get connection count for session (from Redis)
            session_connections = await self.service.websocket_connection_registry.get_session_connections(session_id)
            
            # Update session data with WebSocket connection info
            session_updates = {
                "websocket_connections": {
                    "count": len(session_connections),
                    "connections": {
                        websocket_id: {
                            "agent_type": agent_type,
                            "pillar": pillar,
                            "linked_at": connection_info["linked_at"]
                        }
                    }
                }
            }
            await self.service.session_abstraction.update_session(session_id, session_updates)
            
            # Record health metric
            await self.service.record_health_metric(
                "websocket_linked_to_session",
                1.0,
                {"websocket_id": websocket_id, "session_id": session_id, "agent_type": agent_type, "pillar": pillar}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "link_websocket_to_session_complete",
                success=True,
                details={"websocket_id": websocket_id, "session_id": session_id, "agent_type": agent_type, "pillar": pillar}
            )
            
            return {
                "success": True,
                "websocket_id": websocket_id,
                "session_id": session_id,
                "agent_type": agent_type,
                "pillar": pillar,
                "linked_at": connection_info["linked_at"]
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "link_websocket_to_session")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "link_websocket_to_session_complete",
                success=False,
                details={"websocket_id": websocket_id, "session_id": session_id, "error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "websocket_id": websocket_id,
                "session_id": session_id
            }
    
    async def get_session_websockets(
        self, 
        session_id: str,
        agent_type: Optional[str] = None,  # Filter by agent type
        pillar: Optional[str] = None        # Filter by pillar (for liaison agents)
    ) -> List[str]:
        """
        Get all WebSocket connection IDs for a session.
        
        Args:
            session_id: Traffic Cop session ID
            agent_type: Optional filter by agent type
            pillar: Optional filter by pillar (for liaison agents)
        
        Returns:
            List of WebSocket connection IDs
        """
        try:
            # Check if connection registry is available
            if not self.service.websocket_connection_registry:
                self.service.logger.warning("⚠️ WebSocket Connection Registry not available")
                return []
            
            # Get connections from Redis (with optional filters)
            connections = await self.service.websocket_connection_registry.get_session_connections(
                session_id=session_id,
                agent_type=agent_type,
                pillar=pillar
            )
            
            # Extract websocket_ids
            websocket_ids = [conn.get("websocket_id") for conn in connections if conn.get("websocket_id")]
            
            return websocket_ids
            
        except Exception as e:
            self.service.logger.error(f"Failed to get session WebSocket connections: {e}")
            return []
    
    async def route_websocket_message(self, websocket_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route WebSocket message with session context.
        
        Args:
            websocket_id: WebSocket connection ID
            message: Message to route
        
        Returns:
            Routed message with session context
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "route_websocket_message_start",
            success=True,
            details={"websocket_id": websocket_id}
        )
        
        try:
            # Check if connection registry is available
            if not self.service.websocket_connection_registry:
                await self.service.record_health_metric("route_websocket_message_registry_unavailable", 1.0, {"websocket_id": websocket_id})
                await self.service.log_operation_with_telemetry("route_websocket_message_complete", success=False, details={"error": "registry_unavailable"})
                return {
                    "success": False,
                    "error": "WebSocket Connection Registry not available",
                    "websocket_id": websocket_id
                }
            
            # Find session for this WebSocket connection (search Redis)
            # Note: This requires searching, which is less efficient. Consider storing websocket_id -> session_id mapping.
            # For now, we'll need to search all sessions or require session_id in message
            # TODO: Add websocket_id -> session_id index for faster lookup
            session_id = None
            connection_info = None
            
            # Try to get session_id from message metadata if available
            if isinstance(message, dict) and "session_id" in message:
                session_id = message.get("session_id")
                connection_info = await self.service.websocket_connection_registry.get_connection(websocket_id, session_id)
            else:
                # Search pattern - this is inefficient but works
                # In practice, messages should include session_id
                self.service.logger.warning(f"⚠️ Routing WebSocket message without session_id - may be inefficient")
                # For now, return error - caller should include session_id
                await self.service.record_health_metric("route_websocket_message_no_session_id", 1.0, {"websocket_id": websocket_id})
                await self.service.log_operation_with_telemetry("route_websocket_message_complete", success=False, details={"error": "no_session_id"})
                return {
                    "success": False,
                    "error": "WebSocket message must include session_id for routing",
                    "websocket_id": websocket_id
                }
            
            if not session_id or not connection_info:
                await self.service.record_health_metric("route_websocket_message_no_session", 1.0, {"websocket_id": websocket_id})
                await self.service.log_operation_with_telemetry("route_websocket_message_complete", success=False, details={"error": "no_session"})
                return {
                    "success": False,
                    "error": "WebSocket connection not linked to any session",
                    "websocket_id": websocket_id
                }
            
            # Get session data for context
            session_data = await self.service.session_abstraction.get_session(session_id)
            
            # Add session context to message
            routed_message = {
                **message,
                "session_context": {
                    "session_id": session_id,
                    "user_id": session_data.get("user_id") if session_data else None,
                    "agent_type": connection_info.get("agent_type") if connection_info else None,
                    "pillar": connection_info.get("pillar") if connection_info else None,
                    "routed_at": datetime.utcnow().isoformat()
                }
            }
            
            # Record health metric
            await self.service.record_health_metric(
                "websocket_message_routed",
                1.0,
                {"websocket_id": websocket_id, "session_id": session_id}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "route_websocket_message_complete",
                success=True,
                details={"websocket_id": websocket_id, "session_id": session_id}
            )
            
            return {
                "success": True,
                "message": routed_message,
                "session_id": session_id
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "route_websocket_message")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "route_websocket_message_complete",
                success=False,
                details={"websocket_id": websocket_id, "error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "websocket_id": websocket_id
            }
    
    async def unlink_websocket_from_session(self, websocket_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Unlink WebSocket connection from Traffic Cop session.
        
        Args:
            websocket_id: WebSocket connection ID
            session_id: Optional session ID (if not provided, will search all sessions)
        
        Returns:
            Dict with success status
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "unlink_websocket_from_session_start",
            success=True,
            details={"websocket_id": websocket_id, "session_id": session_id}
        )
        
        try:
            # Check if connection registry is available
            if not self.service.websocket_connection_registry:
                await self.service.record_health_metric("unlink_websocket_registry_unavailable", 1.0, {"websocket_id": websocket_id})
                await self.service.log_operation_with_telemetry("unlink_websocket_from_session_complete", success=False, details={"error": "registry_unavailable"})
                return {
                    "success": False,
                    "error": "WebSocket Connection Registry not available",
                    "websocket_id": websocket_id,
                    "session_id": session_id
                }
            
            # Unregister connection from Redis
            removed = await self.service.websocket_connection_registry.unregister_connection(
                websocket_id=websocket_id,
                session_id=session_id
            )
            
            if removed and session_id:
                # Get updated connection count
                session_connections = await self.service.websocket_connection_registry.get_session_connections(session_id)
                
                # Update session data
                session_updates = {
                    "websocket_connections": {
                        "count": len(session_connections),
                        "connections": {}
                    }
                }
                await self.service.session_abstraction.update_session(session_id, session_updates)
            
            if removed:
                # Record health metric
                await self.service.record_health_metric(
                    "websocket_unlinked_from_session",
                    1.0,
                    {"websocket_id": websocket_id, "session_id": session_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "unlink_websocket_from_session_complete",
                    success=True,
                    details={"websocket_id": websocket_id, "session_id": session_id}
                )
                
                return {
                    "success": True,
                    "websocket_id": websocket_id,
                    "session_id": session_id
                }
            else:
                await self.service.record_health_metric("unlink_websocket_not_found", 1.0, {"websocket_id": websocket_id})
                await self.service.log_operation_with_telemetry("unlink_websocket_from_session_complete", success=False, details={"error": "not_found"})
                return {
                    "success": False,
                    "error": "WebSocket connection not found",
                    "websocket_id": websocket_id
                }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "unlink_websocket_from_session")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "unlink_websocket_from_session_complete",
                success=False,
                details={"websocket_id": websocket_id, "error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "websocket_id": websocket_id
            }

