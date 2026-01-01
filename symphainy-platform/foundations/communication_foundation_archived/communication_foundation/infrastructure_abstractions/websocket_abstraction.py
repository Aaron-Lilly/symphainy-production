#!/usr/bin/env python3
"""
WebSocket Abstraction - Real-time Communication Implementation

WebSocket abstraction that provides real-time communication capabilities
for all realms using WebSocket connections.

WHAT (Infrastructure Abstraction): I provide WebSocket real-time communication
HOW (Infrastructure Implementation): I use WebSocket adapter for connection management
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import uuid

# Import abstraction contracts
from ..abstraction_contracts.websocket_protocol import (
    WebSocketProtocol, WebSocketConnection, WebSocketMessage, WebSocketMessageType,
    WebSocketConnectionStatus
)

# Import WebSocket foundation service (replacing old adapter)
from ..foundation_services.websocket_foundation_service import WebSocketFoundationService

# Import communication abstraction
from .communication_abstraction import CommunicationAbstraction

logger = logging.getLogger(__name__)


class WebSocketAbstraction(WebSocketProtocol):
    """
    WebSocket Abstraction - Real-time Communication Implementation
    
    Provides real-time communication capabilities for all realms using
    WebSocket connections managed by WebSocket adapter.
    
    WHAT (Infrastructure Abstraction): I provide WebSocket real-time communication
    HOW (Infrastructure Implementation): I use WebSocket adapter for connection management
    """
    
    def __init__(self, websocket_foundation: WebSocketFoundationService,
                 communication_abstraction: CommunicationAbstraction):
        """Initialize WebSocket Abstraction."""
        self.logger = logging.getLogger("WebSocketAbstraction")
        self.websocket_foundation = websocket_foundation
        self.communication_abstraction = communication_abstraction
        
        # Backward compatibility alias
        self.websocket_adapter = websocket_foundation
        
        # WebSocket connections registry
        self.connections = {}
        self.connection_history = []
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ WebSocket Abstraction initialized")
    
    async def initialize(self):
        """Initialize WebSocket Abstraction."""
        self.logger.info("🚀 Initializing WebSocket Abstraction...")
        
        try:
            # Initialize WebSocket foundation service (if available)
            if self.websocket_foundation:
                if not self.websocket_foundation.is_initialized:
                    await self.websocket_foundation.initialize()
            else:
                self.logger.warning("⚠️ WebSocket foundation service not available")
            
            # Initialize Communication Abstraction (if available)
            if self.communication_abstraction:
                await self.communication_abstraction.initialize()
            else:
                self.logger.warning("⚠️ Communication abstraction not available")
            
            self.is_initialized = True
            self.logger.info("✅ WebSocket Abstraction initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WebSocket Abstraction: {e}")
            raise
    
    async def start(self):
        """Start WebSocket Abstraction."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting WebSocket Abstraction...")
        
        try:
            # Start WebSocket adapter
            await self.websocket_adapter.start()
            
            # Start Communication Abstraction
            await self.communication_abstraction.start()
            
            self.is_running = True
            self.logger.info("✅ WebSocket Abstraction started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start WebSocket Abstraction: {e}")
            raise
    
    async def stop(self):
        """Stop WebSocket Abstraction."""
        self.logger.info("🛑 Stopping WebSocket Abstraction...")
        
        try:
            # Stop Communication Abstraction
            await self.communication_abstraction.stop()
            
            # Stop WebSocket adapter
            await self.websocket_adapter.stop()
            
            self.is_running = False
            self.logger.info("✅ WebSocket Abstraction stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop WebSocket Abstraction: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown WebSocket Abstraction."""
        await self.stop()
        self.logger.info("🔌 WebSocket Abstraction shutdown complete")
    
    # WebSocket Protocol Implementation
    
    async def connect(self, client_id: str, realm: str, 
                     connection_data: Dict[str, Any]) -> Optional[WebSocketConnection]:
        """Connect WebSocket client to realm."""
        try:
            connection_id = str(uuid.uuid4())
            
            # Create WebSocket connection
            connection = WebSocketConnection(
                connection_id=connection_id,
                client_id=client_id,
                realm=realm,
                websocket=None,  # Will be set by adapter
                connection_data=connection_data
            )
            
            # Establish connection via WebSocket adapter
            success = await self.websocket_adapter.establish_websocket_connection(
                client_id=client_id,
                realm=realm,
                connection_data=connection_data
            )
            
            if success:
                connection.status = WebSocketConnectionStatus.CONNECTED
                self.connections[connection_id] = connection
                self.connection_history.append(connection)
                
                self.logger.info(f"✅ WebSocket connected: {client_id} -> {realm}")
                return connection
            else:
                connection.status = WebSocketConnectionStatus.ERROR
                self.logger.error(f"❌ Failed to connect WebSocket: {client_id} -> {realm}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to connect WebSocket: {e}")
            return None
    
    async def disconnect(self, connection_id: str) -> bool:
        """Disconnect WebSocket connection."""
        try:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                
                # Disconnect via WebSocket adapter
                success = await self.websocket_adapter.disconnect_websocket(
                    realm=connection.realm,
                    client_id=connection.client_id
                )
                
                if success:
                    connection.status = WebSocketConnectionStatus.DISCONNECTED
                    del self.connections[connection_id]
                    
                    self.logger.info(f"✅ WebSocket disconnected: {connection_id}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to disconnect WebSocket: {connection_id}")
                    return False
            else:
                self.logger.warning(f"⚠️ WebSocket connection not found: {connection_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to disconnect WebSocket: {e}")
            return False
    
    async def send_message(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to WebSocket connection."""
        try:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                
                # Send message via WebSocket adapter
                success = await self.websocket_adapter.send_websocket_message(
                    client_id=connection.client_id,
                    message={
                        "type": message.message_type.value,
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat()
                    }
                )
                
                if success:
                    connection.message_count += 1
                    message.delivered = True
                    
                    self.logger.info(f"✅ WebSocket message sent: {connection_id}")
                    return True
                else:
                    message.error_message = "Failed to send message"
                    self.logger.error(f"❌ Failed to send WebSocket message: {connection_id}")
                    return False
            else:
                self.logger.warning(f"⚠️ WebSocket connection not found: {connection_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send WebSocket message: {e}")
            return False
    
    async def broadcast_to_realm(self, realm: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections in realm."""
        try:
            # Broadcast via WebSocket adapter
            sent_count = await self.websocket_adapter.broadcast_to_realm(
                realm=realm,
                message={
                    "type": message.message_type.value,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat()
                }
            )
            
            self.logger.info(f"✅ WebSocket broadcast to {realm}: {sent_count} messages sent")
            return sent_count
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast WebSocket message: {e}")
            return 0
    
    async def broadcast_to_all(self, message: WebSocketMessage) -> int:
        """Broadcast message to all connections."""
        try:
            total_sent = 0
            
            # Broadcast to all realms
            for realm in set(conn.realm for conn in self.connections.values()):
                sent_count = await self.broadcast_to_realm(realm, message)
                total_sent += sent_count
            
            self.logger.info(f"✅ WebSocket broadcast to all: {total_sent} messages sent")
            return total_sent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast WebSocket message to all: {e}")
            return 0
    
    async def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get WebSocket connection by ID."""
        return self.connections.get(connection_id)
    
    async def get_connections_by_realm(self, realm: str) -> List[WebSocketConnection]:
        """Get all connections for realm."""
        return [
            connection for connection in self.connections.values()
            if connection.realm == realm
        ]
    
    async def get_connections_by_client(self, client_id: str) -> List[WebSocketConnection]:
        """Get all connections for client."""
        return [
            connection for connection in self.connections.values()
            if connection.client_id == client_id
        ]
    
    async def ping_connection(self, connection_id: str) -> bool:
        """Ping WebSocket connection."""
        try:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                
                # Create ping message
                ping_message = WebSocketMessage(
                    message_id=str(uuid.uuid4()),
                    connection_id=connection_id,
                    message_type=WebSocketMessageType.PING,
                    content={"timestamp": datetime.now().isoformat()}
                )
                
                # Send ping message
                success = await self.send_message(connection_id, ping_message)
                
                if success:
                    connection.last_ping = datetime.now()
                    self.logger.info(f"✅ WebSocket ping sent: {connection_id}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to ping WebSocket: {connection_id}")
                    return False
            else:
                self.logger.warning(f"⚠️ WebSocket connection not found: {connection_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to ping WebSocket: {e}")
            return False
    
    async def get_connection_stats(self, connection_id: str) -> Dict[str, Any]:
        """Get connection statistics."""
        try:
            connection = self.connections.get(connection_id)
            if connection:
                return {
                    "connection_id": connection.connection_id,
                    "client_id": connection.client_id,
                    "realm": connection.realm,
                    "status": connection.status.value,
                    "connected_at": connection.connected_at.isoformat(),
                    "last_ping": connection.last_ping.isoformat(),
                    "message_count": connection.message_count,
                    "error_count": connection.error_count
                }
            else:
                return {
                    "connection_id": connection_id,
                    "status": "not_found"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection stats: {e}")
            return {
                "connection_id": connection_id,
                "status": "error",
                "error": str(e)
            }
    
    async def get_realm_stats(self, realm: str) -> Dict[str, Any]:
        """Get realm statistics."""
        try:
            realm_connections = await self.get_connections_by_realm(realm)
            
            return {
                "realm": realm,
                "connection_count": len(realm_connections),
                "active_connections": len([
                    conn for conn in realm_connections
                    if conn.status == WebSocketConnectionStatus.CONNECTED
                ]),
                "total_messages": sum(conn.message_count for conn in realm_connections),
                "total_errors": sum(conn.error_count for conn in realm_connections)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get realm stats: {e}")
            return {
                "realm": realm,
                "status": "error",
                "error": str(e)
            }
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global WebSocket statistics."""
        try:
            return {
                "total_connections": len(self.connections),
                "total_history": len(self.connection_history),
                "is_running": self.is_running,
                "is_initialized": self.is_initialized,
                "realm_stats": {
                    realm: await self.get_realm_stats(realm)
                    for realm in set(conn.realm for conn in self.connections.values())
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get global stats: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
