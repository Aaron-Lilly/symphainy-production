#!/usr/bin/env python3
"""
WebSocket Gateway Service - Post Office

Single authoritative WebSocket ingress point for the platform.
All WebSocket connections go through this service.

WHAT (Post Office Role): I provide WebSocket transport for messaging
HOW (Service Implementation): I accept connections, validate sessions, route to Redis channels
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Set
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect
from bases.smart_city_role_base import SmartCityRoleBase

logger = logging.getLogger(__name__)


class WebSocketGatewayService(SmartCityRoleBase):
    """
    WebSocket Gateway Service - Single authoritative WebSocket ingress point.
    
    WHAT (Post Office Role): I provide WebSocket transport for messaging
    HOW (Service Implementation): I accept connections, validate sessions, route to Redis channels
    
    Architecture:
    - Extends SmartCityRoleBase (direct abstraction access, no Platform Gateway)
    - Accepts WebSocket connections via FastAPI endpoint
    - Validates sessions via Traffic Cop (direct abstraction access)
    - Routes messages to Redis channels (direct abstraction access)
    - Manages connection lifecycle
    """
    
    def __init__(self, di_container: Any, post_office_service: Any = None):
        """Initialize WebSocket Gateway Service."""
        super().__init__(
            service_name="WebSocketGatewayService",
            role_name="post_office",
            di_container=di_container
        )
        
        # Reference to parent Post Office service
        self.post_office_service = post_office_service
        
        # Infrastructure Abstractions (direct access - Smart City privilege)
        self.session_abstraction = None  # Traffic Cop
        self.messaging_abstraction = None  # Redis
        
        # Connection Management
        self.local_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.channel_connections: Dict[str, Set[str]] = defaultdict(set)  # channel -> connection_ids
        
        # Connection tracking (in-memory for Phase 1, will move to Redis in Phase 2)
        self.connection_limits = {
            "max_per_user": 5,
            "max_global": 1000
        }
        self.user_connections: Dict[str, int] = defaultdict(int)
        self.global_connections = 0
        
        # Service state
        self.is_ready_flag = False
        self.instance_id = f"ws-gateway-{uuid.uuid4().hex[:8]}"
        self.started_at = datetime.utcnow()
        
        if self.logger:
            self.logger.info(f"✅ WebSocket Gateway Service initialized (instance: {self.instance_id})")
    
    async def initialize(self) -> bool:
        """Initialize WebSocket Gateway Service with infrastructure connections."""
        try:
            if self.logger:
                self.logger.info("🔌 Initializing WebSocket Gateway Service infrastructure...")
            
            # Get abstractions directly (Smart City privilege - no Platform Gateway)
            self.session_abstraction = self.get_session_abstraction()
            if not self.session_abstraction:
                raise Exception("Session Abstraction (Traffic Cop) not available")
            
            self.messaging_abstraction = self.get_messaging_abstraction()
            if not self.messaging_abstraction:
                raise Exception("Messaging Abstraction (Redis) not available")
            
            # Check readiness
            self.is_ready_flag = await self.is_ready()
            
            if self.logger:
                self.logger.info(f"✅ WebSocket Gateway Service initialized and ready: {self.is_ready_flag}")
            
            return self.is_ready_flag
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to initialize WebSocket Gateway Service: {e}")
            self.is_ready_flag = False
            return False
    
    async def is_ready(self) -> bool:
        """Check if gateway is ready to accept connections."""
        try:
            # Check Redis connectivity
            redis_ready = False
            if self.messaging_abstraction:
                try:
                    # Try to ping Redis
                    if hasattr(self.messaging_abstraction, 'ping'):
                        redis_ready = await self.messaging_abstraction.ping()
                    else:
                        # Fallback: check if abstraction is initialized
                        redis_ready = self.messaging_abstraction is not None
                except:
                    redis_ready = False
            
            # Check Traffic Cop (session abstraction)
            traffic_cop_ready = self.session_abstraction is not None
            
            # Check Post Office service
            post_office_ready = (
                self.post_office_service is not None and
                hasattr(self.post_office_service, 'is_initialized') and
                self.post_office_service.is_initialized
            )
            
            ready = redis_ready and traffic_cop_ready and post_office_ready
            self.is_ready_flag = ready
            
            return ready
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking readiness: {e}")
            return False
    
    async def handle_connection(self, websocket: WebSocket, session_token: Optional[str] = None):
        """
        Handle WebSocket connection - main entry point.
        
        Args:
            websocket: FastAPI WebSocket connection
            session_token: Optional session token for authentication
        """
        connection_id = None
        
        try:
            # 1. Accept connection immediately (required by FastAPI/Starlette)
            await websocket.accept()
            
            if self.logger:
                self.logger.debug(f"🔌 WebSocket connection accepted (session_token: {session_token})")
            
            # 2. Validate session and register connection
            connection_id = await self._register_connection(websocket, session_token)
            
            if not connection_id:
                # Registration failed, connection already closed
                return
            
            # 3. Send welcome message
            await self._send_welcome_message(websocket, connection_id)
            
            # 4. Message loop
            async for message in websocket.iter_text():
                await self._handle_incoming_message(connection_id, message)
                
        except WebSocketDisconnect:
            if self.logger:
                self.logger.info(f"🔌 WebSocket disconnected: {connection_id}")
            await self._handle_disconnect(connection_id)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error handling WebSocket connection {connection_id}: {e}")
            await self._handle_disconnect(connection_id)
    
    async def _register_connection(
        self,
        websocket: WebSocket,
        session_token: Optional[str]
    ) -> Optional[str]:
        """Register WebSocket connection with Traffic Cop and local tracking."""
        try:
            # Validate session via Traffic Cop (direct abstraction access)
            session = None
            if session_token and self.session_abstraction:
                try:
                    # Use session abstraction to validate
                    if hasattr(self.session_abstraction, 'validate_session'):
                        session = await self.session_abstraction.validate_session(session_token)
                    elif hasattr(self.session_abstraction, 'get_session'):
                        session = await self.session_abstraction.get_session(session_token)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"⚠️ Session validation failed: {e}")
            
            # Check connection limits
            session_id_key = session_token or "anonymous"
            
            if self.user_connections[session_id_key] >= self.connection_limits["max_per_user"]:
                if self.logger:
                    self.logger.warning(f"🚫 Connection limit exceeded for user: {session_id_key}")
                await websocket.close(code=4004, reason="Connection limit exceeded")
                return None
            
            if self.global_connections >= self.connection_limits["max_global"]:
                if self.logger:
                    self.logger.warning("🚫 Global connection limit exceeded")
                await websocket.close(code=4005, reason="Server at capacity")
                return None
            
            # Generate connection ID
            connection_id = f"ws_{session_id_key}_{uuid.uuid4().hex[:8]}"
            
            # Register locally
            self.local_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "connection_id": connection_id,
                "session_token": session_token,
                "user_id": session.get("user_id") if session else None,
                "connected_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Update connection counts
            self.user_connections[session_id_key] += 1
            self.global_connections += 1
            
            if self.logger:
                self.logger.info(
                    f"✅ WebSocket connection registered: {connection_id} "
                    f"(user: {session_id_key}, global: {self.global_connections})"
                )
            
            return connection_id
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to register connection: {e}")
            try:
                await websocket.close(code=4000, reason="Registration failed")
            except:
                pass
            return None
    
    async def _send_welcome_message(self, websocket: WebSocket, connection_id: str):
        """Send welcome message to newly connected client."""
        try:
            welcome_message = {
                "type": "system",
                "message": "Connected to WebSocket Gateway. Ready to receive messages.",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_json(welcome_message)
            
            if self.logger:
                self.logger.debug(f"✅ Welcome message sent to {connection_id}")
                
        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️ Failed to send welcome message: {e}")
    
    async def _handle_incoming_message(self, connection_id: str, message: str):
        """Handle incoming message from WebSocket connection."""
        try:
            # Parse message
            data = json.loads(message)
            
            # Update last activity
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
            
            # Extract channel from new format: { channel: "guide" | "pillar:content", intent: "...", payload: {...} }
            # Or fallback to old format for transition: { agent_type: "...", pillar: "...", message: "..." }
            channel = data.get("channel")
            
            # If no channel, try to construct from old format
            if not channel:
                agent_type = data.get("agent_type", "guide")
                pillar = data.get("pillar")
                if agent_type == "guide":
                    channel = "guide"
                elif pillar:
                    channel = f"pillar:{pillar}"
                else:
                    channel = "guide"  # Default fallback
            
            # Route to Redis channel (pass full data, gateway doesn't need to parse payload)
            await self._route_to_channel(connection_id, channel, data)
            
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.warning(f"⚠️ Invalid JSON message from {connection_id}: {e}")
            await self._send_error(connection_id, "Invalid message format")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error handling message from {connection_id}: {e}")
            await self._send_error(connection_id, "Message processing failed")
    
    async def _route_to_channel(self, connection_id: str, channel: str, message: Dict[str, Any]):
        """Route message to appropriate Redis channel."""
        try:
            # Map channel to Redis channel name
            redis_channel = f"websocket:{channel}"
            
            # Add connection metadata to message
            message_with_metadata = {
                "connection_id": connection_id,
                "channel": channel,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "gateway_instance": self.instance_id
            }
            
            # Publish to Redis channel (direct abstraction access)
            if self.messaging_abstraction:
                if hasattr(self.messaging_abstraction, 'publish'):
                    await self.messaging_abstraction.publish(
                        redis_channel,
                        json.dumps(message_with_metadata)
                    )
                elif hasattr(self.messaging_abstraction, 'send_message'):
                    await self.messaging_abstraction.send_message(
                        redis_channel,
                        message_with_metadata
                    )
            
            # Track channel subscription
            self.channel_connections[channel].add(connection_id)
            
            if self.logger:
                self.logger.debug(
                    f"📤 Routed message from {connection_id} to channel {redis_channel}"
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to route message to channel {channel}: {e}")
            raise
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to connection."""
        try:
            websocket = self.local_connections.get(connection_id)
            if websocket:
                error_response = {
                    "type": "error",
                    "message": error_message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_response)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️ Failed to send error to {connection_id}: {e}")
    
    async def _handle_disconnect(self, connection_id: Optional[str]):
        """Handle WebSocket disconnection."""
        if not connection_id:
            return
        
        try:
            # Remove from local connections
            if connection_id in self.local_connections:
                del self.local_connections[connection_id]
            
            # Remove from metadata
            if connection_id in self.connection_metadata:
                metadata = self.connection_metadata[connection_id]
                session_token = metadata.get("session_token", "anonymous")
                
                # Update connection counts
                self.user_connections[session_token] = max(0, self.user_connections[session_token] - 1)
                self.global_connections = max(0, self.global_connections - 1)
                
                # Remove from channel subscriptions
                for channel, connections in self.channel_connections.items():
                    connections.discard(connection_id)
                
                del self.connection_metadata[connection_id]
            
            if self.logger:
                self.logger.info(f"✅ Connection cleaned up: {connection_id}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error during disconnect cleanup: {e}")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to a specific connection.
        
        Used by Post Office SOA APIs to send messages to WebSocket connections.
        
        Args:
            connection_id: Connection ID to send message to
            message: Message dictionary to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            websocket = self.local_connections.get(connection_id)
            if not websocket:
                if self.logger:
                    self.logger.warning(f"⚠️ Connection not found: {connection_id}")
                return False
            
            await websocket.send_json(message)
            
            if self.logger:
                self.logger.debug(f"📤 Sent message to connection {connection_id}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to send message to {connection_id}: {e}")
            return False
    
    def get_connection_count(self) -> Dict[str, int]:
        """Get current connection statistics."""
        return {
            "global": self.global_connections,
            "per_user": dict(self.user_connections),
            "by_channel": {channel: len(connections) for channel, connections in self.channel_connections.items()}
        }

