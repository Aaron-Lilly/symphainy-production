#!/usr/bin/env python3
"""
Real-Time Coordinator Micro-Module

Manages real-time coordination, WebSocket connections, and live updates across the platform.

WHAT (Micro-Module): I manage real-time coordination and live updates
HOW (Implementation): I handle WebSocket connections, broadcast updates, and coordinate real-time events
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import json

from utilities import UserContext
from config.environment_loader import EnvironmentLoader


class RealTimeCoordinatorModule:
    """
    Real-Time Coordinator Micro-Module
    
    Provides functionality to manage real-time coordination and live updates.
    """
    
    def __init__(self, environment: EnvironmentLoader, logger: Optional[logging.Logger] = None):
        """Initialize Real-Time Coordinator Module."""
        self.environment = environment
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        
        # WebSocket connections (for MVP)
        # In a real system, this would be a proper WebSocket server or message queue
        self.connections: Dict[str, Dict[str, Any]] = {}
        
        # Session to connection mapping
        self.session_connections: Dict[str, Set[str]] = {}
        
        # User to connection mapping
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Real-time event queue
        self.event_queue: List[Dict[str, Any]] = []
        
        # Event types that can be broadcast
        self.event_types = [
            "ui_state_update",
            "data_update",
            "progress_update",
            "notification",
            "error",
            "system_message",
            "pillar_update",
            "session_update"
        ]
        
        self.logger.info("⚡ Real-Time Coordinator Module initialized")
    
    async def initialize(self):
        """Initialize the Real-Time Coordinator Module."""
        self.logger.info("🚀 Initializing Real-Time Coordinator Module...")
        
        # Start background task for processing events
        self.event_processor_task = asyncio.create_task(self._process_event_queue())
        
        self.is_initialized = True
        self.logger.info("✅ Real-Time Coordinator Module initialized successfully")
    
    async def shutdown(self):
        """Shutdown the Real-Time Coordinator Module."""
        self.logger.info("🛑 Shutting down Real-Time Coordinator Module...")
        
        # Cancel background task
        if hasattr(self, 'event_processor_task'):
            self.event_processor_task.cancel()
            try:
                await self.event_processor_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for connection_id in list(self.connections.keys()):
            await self._close_connection(connection_id)
        
        self.is_initialized = False
        self.logger.info("✅ Real-Time Coordinator Module shutdown successfully")
    
    async def register_connection(self, connection_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Register a new WebSocket connection.
        
        Args:
            connection_id: Unique identifier for the connection.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing connection status and configuration.
        """
        self.logger.debug(f"Registering connection: {connection_id} for user: {user_context.user_id}")
        
        try:
            # Create connection record
            connection_info = {
                "connection_id": connection_id,
                "user_id": user_context.user_id,
                "user_context": user_context,
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "subscribed_events": set(),
                "session_id": None
            }
            
            # Store connection
            self.connections[connection_id] = connection_info
            
            # Update user connections mapping
            if user_context.user_id not in self.user_connections:
                self.user_connections[user_context.user_id] = set()
            self.user_connections[user_context.user_id].add(connection_id)
            
            self.logger.info(f"✅ Connection registered: {connection_id}")
            
            return {
                "success": True,
                "connection_id": connection_id,
                "connection_status": "active",
                "user_id": user_context.user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register connection: {e}")
            return {"success": False, "error": str(e), "message": "Failed to register connection"}
    
    async def associate_connection_with_session(self, connection_id: str, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Associate a WebSocket connection with a user session.
        
        Args:
            connection_id: The WebSocket connection identifier.
            session_id: The session identifier.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the association status.
        """
        self.logger.debug(f"Associating connection {connection_id} with session {session_id}")
        
        try:
            if connection_id not in self.connections:
                return {"success": False, "error": "Connection not found"}
            
            connection = self.connections[connection_id]
            
            # Verify user ownership
            if connection.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to connection"}
            
            # Update connection with session info
            connection["session_id"] = session_id
            connection["last_activity"] = datetime.utcnow().isoformat()
            
            # Update session connections mapping
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(connection_id)
            
            self.logger.info(f"✅ Connection {connection_id} associated with session {session_id}")
            
            return {
                "success": True,
                "connection_id": connection_id,
                "session_id": session_id,
                "associated": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to associate connection with session: {e}")
            return {"success": False, "error": str(e), "message": "Failed to associate connection with session"}
    
    async def broadcast_to_sessions(self, update_data: Dict[str, Any], target_sessions: List[str], user_context: UserContext) -> Dict[str, Any]:
        """
        Broadcast real-time updates to specific user sessions.
        
        Args:
            update_data: The update data to broadcast.
            target_sessions: List of session IDs to receive the update.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the broadcast status.
        """
        self.logger.debug(f"Broadcasting to {len(target_sessions)} sessions")
        
        try:
            broadcast_results = {}
            
            for session_id in target_sessions:
                # Get connections for this session
                session_connections = self.session_connections.get(session_id, set())
                
                session_result = {
                    "session_id": session_id,
                    "connections_found": len(session_connections),
                    "broadcast_success": 0,
                    "broadcast_failed": 0
                }
                
                for connection_id in session_connections:
                    if connection_id in self.connections:
                        # Send update to connection
                        send_result = await self._send_to_connection(connection_id, update_data)
                        if send_result.get("success"):
                            session_result["broadcast_success"] += 1
                        else:
                            session_result["broadcast_failed"] += 1
                
                broadcast_results[session_id] = session_result
            
            total_success = sum(result["broadcast_success"] for result in broadcast_results.values())
            total_failed = sum(result["broadcast_failed"] for result in broadcast_results.values())
            
            self.logger.info(f"✅ Broadcast completed: {total_success} successful, {total_failed} failed")
            
            return {
                "success": True,
                "broadcast_results": broadcast_results,
                "total_success": total_success,
                "total_failed": total_failed,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast to sessions: {e}")
            return {"success": False, "error": str(e), "message": "Failed to broadcast to sessions"}
    
    async def broadcast_state_update(self, session_id: str, state_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Broadcast UI state update to session connections.
        
        Args:
            session_id: The session ID.
            state_data: The state data to broadcast.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the broadcast status.
        """
        self.logger.debug(f"Broadcasting state update for session: {session_id}")
        
        try:
            update_data = {
                "event_type": "ui_state_update",
                "session_id": session_id,
                "state_data": state_data,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_context.user_id
            }
            
            # Add to event queue for processing
            self.event_queue.append(update_data)
            
            return {
                "success": True,
                "session_id": session_id,
                "event_queued": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast state update: {e}")
            return {"success": False, "error": str(e), "message": "Failed to broadcast state update"}
    
    async def coordinate_updates(self, coordination_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Coordinate real-time updates across the platform.
        
        Args:
            coordination_data: Data for real-time coordination.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the coordination status.
        """
        self.logger.debug("Coordinating real-time updates")
        
        try:
            event_type = coordination_data.get("event_type", "system_message")
            target_sessions = coordination_data.get("target_sessions", [])
            message_data = coordination_data.get("message_data", {})
            
            # Create coordination event
            coordination_event = {
                "event_type": event_type,
                "coordination_data": coordination_data,
                "user_id": user_context.user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to event queue
            self.event_queue.append(coordination_event)
            
            # If specific sessions are targeted, broadcast immediately
            if target_sessions:
                broadcast_result = await self.broadcast_to_sessions(
                    coordination_event, target_sessions, user_context
                )
                return {
                    "success": True,
                    "coordination_event": coordination_event,
                    "broadcast_result": broadcast_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "success": True,
                "coordination_event": coordination_event,
                "event_queued": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate updates: {e}")
            return {"success": False, "error": str(e), "message": "Failed to coordinate updates"}
    
    async def _process_event_queue(self):
        """Background task to process event queue."""
        while self.is_initialized:
            try:
                if self.event_queue:
                    event = self.event_queue.pop(0)
                    await self._process_event(event)
                else:
                    await asyncio.sleep(0.1)  # Small delay when queue is empty
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error processing event queue: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    async def _process_event(self, event: Dict[str, Any]):
        """Process a single event from the queue."""
        try:
            event_type = event.get("event_type")
            
            if event_type == "ui_state_update":
                await self._process_ui_state_update(event)
            elif event_type == "system_message":
                await self._process_system_message(event)
            else:
                self.logger.debug(f"Processing event type: {event_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Error processing event: {e}")
    
    async def _process_ui_state_update(self, event: Dict[str, Any]):
        """Process UI state update event."""
        session_id = event.get("session_id")
        if session_id and session_id in self.session_connections:
            connections = self.session_connections[session_id]
            for connection_id in connections:
                await self._send_to_connection(connection_id, event)
    
    async def _process_system_message(self, event: Dict[str, Any]):
        """Process system message event."""
        # Broadcast to all active connections
        for connection_id in self.connections:
            await self._send_to_connection(connection_id, event)
    
    async def _send_to_connection(self, connection_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send data to a specific connection."""
        try:
            if connection_id not in self.connections:
                return {"success": False, "error": "Connection not found"}
            
            connection = self.connections[connection_id]
            
            # Update last activity
            connection["last_activity"] = datetime.utcnow().isoformat()
            
            # In a real implementation, this would send via WebSocket
            # For MVP, we'll just log the data
            self.logger.debug(f"Sending to connection {connection_id}: {data.get('event_type', 'unknown')}")
            
            return {"success": True, "connection_id": connection_id}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send to connection {connection_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _close_connection(self, connection_id: str):
        """Close a WebSocket connection."""
        try:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                user_id = connection.get("user_id")
                session_id = connection.get("session_id")
                
                # Remove from user connections
                if user_id and user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                
                # Remove from session connections
                if session_id and session_id in self.session_connections:
                    self.session_connections[session_id].discard(connection_id)
                
                # Remove connection
                del self.connections[connection_id]
                
                self.logger.info(f"✅ Connection closed: {connection_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to close connection {connection_id}: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the Real-Time Coordinator Module."""
        return {
            "module_name": "RealTimeCoordinatorModule",
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_connections": len(self.connections),
            "active_sessions": len(self.session_connections),
            "event_queue_size": len(self.event_queue),
            "supported_event_types": self.event_types,
            "message": "Real-Time Coordinator Module is operational."
        }
