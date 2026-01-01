#!/usr/bin/env python3
"""
WebSocket Protocol - Real-time Communication Interface

Defines the WebSocket protocol for real-time communication between realms
and clients using WebSocket connections.

WHAT (Abstraction Contract): I define the WebSocket interface for real-time communication
HOW (Protocol Definition): I specify the contract for WebSocket operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum


class WebSocketConnectionStatus(Enum):
    """WebSocket connection status enumeration."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class WebSocketMessageType(Enum):
    """WebSocket message type enumeration."""
    TEXT = "text"
    BINARY = "binary"
    PING = "ping"
    PONG = "pong"
    CLOSE = "close"
    ERROR = "error"


class WebSocketConnection:
    """WebSocket connection definition."""
    
    def __init__(self, connection_id: str, client_id: str, realm: str,
                 websocket, connection_data: Dict[str, Any]):
        """Initialize WebSocket connection."""
        self.connection_id = connection_id
        self.client_id = client_id
        self.realm = realm
        self.websocket = websocket
        self.connection_data = connection_data
        self.status = WebSocketConnectionStatus.CONNECTED
        self.connected_at = datetime.now()
        self.last_ping = datetime.now()
        self.message_count = 0
        self.error_count = 0


class WebSocketMessage:
    """WebSocket message definition."""
    
    def __init__(self, message_id: str, connection_id: str, message_type: WebSocketMessageType,
                 content: Any, timestamp: Optional[datetime] = None):
        """Initialize WebSocket message."""
        self.message_id = message_id
        self.connection_id = connection_id
        self.message_type = message_type
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.delivered = False
        self.error_message = None


class WebSocketProtocol(ABC):
    """WebSocket protocol interface for real-time communication."""
    
    @abstractmethod
    async def connect(self, client_id: str, realm: str, 
                     connection_data: Dict[str, Any]) -> Optional[WebSocketConnection]:
        """Connect WebSocket client to realm."""
        pass
    
    @abstractmethod
    async def disconnect(self, connection_id: str) -> bool:
        """Disconnect WebSocket connection."""
        pass
    
    @abstractmethod
    async def send_message(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to WebSocket connection."""
        pass
    
    @abstractmethod
    async def broadcast_to_realm(self, realm: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections in realm."""
        pass
    
    @abstractmethod
    async def broadcast_to_all(self, message: WebSocketMessage) -> int:
        """Broadcast message to all connections."""
        pass
    
    @abstractmethod
    async def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get WebSocket connection by ID."""
        pass
    
    @abstractmethod
    async def get_connections_by_realm(self, realm: str) -> List[WebSocketConnection]:
        """Get all connections for realm."""
        pass
    
    @abstractmethod
    async def get_connections_by_client(self, client_id: str) -> List[WebSocketConnection]:
        """Get all connections for client."""
        pass
    
    @abstractmethod
    async def ping_connection(self, connection_id: str) -> bool:
        """Ping WebSocket connection."""
        pass
    
    @abstractmethod
    async def get_connection_stats(self, connection_id: str) -> Dict[str, Any]:
        """Get connection statistics."""
        pass
    
    @abstractmethod
    async def get_realm_stats(self, realm: str) -> Dict[str, Any]:
        """Get realm statistics."""
        pass
    
    @abstractmethod
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global WebSocket statistics."""
        pass


class WebSocketServerProtocol(ABC):
    """WebSocket server protocol interface."""
    
    @abstractmethod
    async def start_server(self, host: str = "localhost", port: int = 8765,
                          path: str = "/websocket") -> bool:
        """Start WebSocket server."""
        pass
    
    @abstractmethod
    async def stop_server(self) -> bool:
        """Stop WebSocket server."""
        pass
    
    @abstractmethod
    async def register_handler(self, path: str, handler: Callable) -> bool:
        """Register WebSocket handler for path."""
        pass
    
    @abstractmethod
    async def unregister_handler(self, path: str) -> bool:
        """Unregister WebSocket handler for path."""
        pass
    
    @abstractmethod
    async def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        pass


class WebSocketClientProtocol(ABC):
    """WebSocket client protocol interface."""
    
    @abstractmethod
    async def connect_to_server(self, server_url: str, client_id: str,
                               connection_data: Dict[str, Any]) -> Optional[WebSocketConnection]:
        """Connect to WebSocket server."""
        pass
    
    @abstractmethod
    async def disconnect_from_server(self, connection_id: str) -> bool:
        """Disconnect from WebSocket server."""
        pass
    
    @abstractmethod
    async def send_message_to_server(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to WebSocket server."""
        pass
    
    @abstractmethod
    async def listen_for_messages(self, connection_id: str, handler: Callable) -> bool:
        """Listen for messages from server."""
        pass
    
    @abstractmethod
    async def stop_listening(self, connection_id: str) -> bool:
        """Stop listening for messages."""
        pass


class WebSocketManagerProtocol(ABC):
    """WebSocket manager protocol interface."""
    
    @abstractmethod
    async def create_connection(self, client_id: str, realm: str,
                              connection_data: Dict[str, Any]) -> Optional[WebSocketConnection]:
        """Create WebSocket connection."""
        pass
    
    @abstractmethod
    async def close_connection(self, connection_id: str) -> bool:
        """Close WebSocket connection."""
        pass
    
    @abstractmethod
    async def send_message(self, connection_id: str, message_type: WebSocketMessageType,
                          content: Any) -> bool:
        """Send message to connection."""
        pass
    
    @abstractmethod
    async def broadcast_message(self, realm: str, message_type: WebSocketMessageType,
                               content: Any) -> int:
        """Broadcast message to realm."""
        pass
    
    @abstractmethod
    async def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information."""
        pass
    
    @abstractmethod
    async def get_realm_connections(self, realm: str) -> List[Dict[str, Any]]:
        """Get all connections for realm."""
        pass
    
    @abstractmethod
    async def cleanup_stale_connections(self) -> int:
        """Cleanup stale connections."""
        pass
    
    @abstractmethod
    async def get_manager_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        pass
