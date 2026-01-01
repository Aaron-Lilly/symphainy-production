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
            
            # Store WebSocket connection info
            if session_id not in self.service.websocket_connections:
                self.service.websocket_connections[session_id] = {}
            
            # Store connection with metadata
            connection_info = {
                "websocket_id": websocket_id,
                "session_id": session_id,
                "agent_type": agent_type,
                "pillar": pillar,
                "linked_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Key by agent_type and pillar for easy lookup
            if agent_type:
                if agent_type not in self.service.websocket_connections[session_id]:
                    self.service.websocket_connections[session_id][agent_type] = {}
                
                if pillar:
                    # Liaison agent with pillar
                    self.service.websocket_connections[session_id][agent_type][pillar] = connection_info
                else:
                    # Guide agent (no pillar)
                    self.service.websocket_connections[session_id][agent_type]["default"] = connection_info
            else:
                # No agent type specified - store as generic
                self.service.websocket_connections[session_id][websocket_id] = connection_info
            
            # Update session data with WebSocket connection info
            session_updates = {
                "websocket_connections": {
                    "count": len(self.service.websocket_connections[session_id]),
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
            if session_id not in self.service.websocket_connections:
                return []
            
            connections = self.service.websocket_connections[session_id]
            websocket_ids = []
            
            if agent_type:
                if agent_type in connections:
                    if pillar:
                        # Specific liaison agent for pillar
                        if pillar in connections[agent_type]:
                            conn_info = connections[agent_type][pillar]
                            websocket_ids.append(conn_info["websocket_id"])
                    else:
                        # All connections for agent type
                        for key, conn_info in connections[agent_type].items():
                            if isinstance(conn_info, dict) and "websocket_id" in conn_info:
                                websocket_ids.append(conn_info["websocket_id"])
            else:
                # All connections for session
                for key, value in connections.items():
                    if isinstance(value, dict):
                        if "websocket_id" in value:
                            websocket_ids.append(value["websocket_id"])
                        elif isinstance(value, dict):
                            # Nested structure (agent_type -> pillar)
                            for nested_key, nested_value in value.items():
                                if isinstance(nested_value, dict) and "websocket_id" in nested_value:
                                    websocket_ids.append(nested_value["websocket_id"])
                    elif isinstance(key, str) and len(key) > 20:  # Likely a websocket_id
                        websocket_ids.append(key)
            
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
            # Find session for this WebSocket connection
            session_id = None
            connection_info = None
            
            for sid, connections in self.service.websocket_connections.items():
                for key, value in connections.items():
                    if isinstance(value, dict):
                        if value.get("websocket_id") == websocket_id:
                            session_id = sid
                            connection_info = value
                            break
                        elif isinstance(value, dict):
                            # Nested structure
                            for nested_value in value.values():
                                if isinstance(nested_value, dict) and nested_value.get("websocket_id") == websocket_id:
                                    session_id = sid
                                    connection_info = nested_value
                                    break
                    elif key == websocket_id:
                        session_id = sid
                        connection_info = {"websocket_id": websocket_id}
                        break
                
                if session_id:
                    break
            
            if not session_id:
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
            # Find and remove connection
            if session_id:
                sessions_to_check = [session_id]
            else:
                sessions_to_check = list(self.service.websocket_connections.keys())
            
            removed = False
            for sid in sessions_to_check:
                if sid in self.service.websocket_connections:
                    connections = self.service.websocket_connections[sid]
                    
                    # Remove from nested structure
                    for key, value in list(connections.items()):
                        if isinstance(value, dict):
                            if value.get("websocket_id") == websocket_id:
                                del connections[key]
                                removed = True
                                break
                            elif isinstance(value, dict):
                                # Nested structure (agent_type -> pillar)
                                for nested_key, nested_value in list(value.items()):
                                    if isinstance(nested_value, dict) and nested_value.get("websocket_id") == websocket_id:
                                        del value[nested_key]
                                        removed = True
                                        break
                        elif key == websocket_id:
                            del connections[key]
                            removed = True
                            break
                    
                    if removed:
                        # Update session data
                        session_updates = {
                            "websocket_connections": {
                                "count": len(connections),
                                "connections": {}
                            }
                        }
                        await self.service.session_abstraction.update_session(sid, session_updates)
                        break
            
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

