#!/usr/bin/env python3
"""
WebSocket Infrastructure Adapter

Raw WebSocket client wrapper for AGUI communication.
Thin wrapper around websockets library with no business logic.
"""

from typing import Dict, Any, List, Optional, Callable
import json
import logging
import uuid
import asyncio

try:
    import websockets
    from websockets.server import serve
    from websockets.client import connect
    from websockets.exceptions import ConnectionClosed, WebSocketException
except ImportError:
    websockets = None
    serve = None
    connect = None
    ConnectionClosed = Exception
    WebSocketException = Exception


class WebSocketAdapter:
    """Raw WebSocket adapter for AGUI communication."""
    
    def __init__(self, host: str = "localhost", port: int = 8765, path: str = "/agui",
                 enable_ssl: bool = False, max_connections: int = 100, **kwargs):
        """
        Initialize WebSocket adapter.
        
        Args:
            host: WebSocket host
            port: WebSocket port
            path: WebSocket path
            enable_ssl: Enable SSL/TLS
            max_connections: Maximum connections
        """
        self.host = host
        self.port = port
        self.path = path
        self.enable_ssl = enable_ssl
        self.max_connections = max_connections
        self.logger = logging.getLogger("WebSocketAdapter")
        
        # WebSocket server and connections
        self.server = None
        self.connections = {}
        self.connection_count = 0
        self.message_handler = None
        
        # Initialize WebSocket
        self._initialize_websocket()
    
    def _initialize_websocket(self):
        """Initialize WebSocket adapter."""
        if websockets is None:
            self.logger.error("websockets library not installed")
            return
            
        try:
            self.logger.info("✅ WebSocket adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket adapter: {e}")
    
    async def start_server(self, message_handler: Callable = None) -> bool:
        """
        Start WebSocket server.
        
        Args:
            message_handler: Message handler function
            
        Returns:
            bool: Success status
        """
        if websockets is None:
            return False
            
        try:
            self.message_handler = message_handler
            
            # Start WebSocket server
            self.server = await serve(
                self._handle_connection,
                self.host,
                self.port,
                subprotocols=["agui-v1"]
            )
            
            self.logger.info(f"✅ WebSocket server started on {self.host}:{self.port}{self.path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            return False
    
    async def stop_server(self) -> bool:
        """
        Stop WebSocket server.
        
        Returns:
            bool: Success status
        """
        try:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                self.server = None
            
            # Close all connections
            for connection_id in list(self.connections.keys()):
                await self.close_connection(connection_id)
            
            self.logger.info("✅ WebSocket server stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop WebSocket server: {e}")
            return False
    
    async def _handle_connection(self, websocket, path):
        """Handle WebSocket connection."""
        if self.connection_count >= self.max_connections:
            await websocket.close(code=1013, reason="Server overloaded")
            return
        
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = websocket
        self.connection_count += 1
        
        try:
            self.logger.info(f"New WebSocket connection: {connection_id}")
            async for message in websocket:
                await self._handle_message(connection_id, message)
        except ConnectionClosed:
            self.logger.info(f"WebSocket connection closed: {connection_id}")
        except WebSocketException as e:
            self.logger.error(f"WebSocket error for {connection_id}: {e}")
        finally:
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.connection_count -= 1
    
    async def _handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message."""
        try:
            # Parse JSON message
            data = json.loads(message)
            
            # Call message handler if provided
            if self.message_handler:
                await self.message_handler(connection_id, data)
            else:
                self.logger.debug(f"Received message from {connection_id}: {data}")
                
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON message from {connection_id}")
        except Exception as e:
            self.logger.error(f"Error handling message from {connection_id}: {e}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific connection.
        
        Args:
            connection_id: Connection ID
            message: Message to send
            
        Returns:
            bool: Success status
        """
        if connection_id not in self.connections:
            self.logger.warning(f"Connection {connection_id} not found")
            return False
            
        try:
            await self.connections[connection_id].send(json.dumps(message))
            self.logger.debug(f"Message sent to {connection_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {connection_id}: {e}")
            return False
    
    async def broadcast_message(self, message: Dict[str, Any], 
                              exclude_connections: List[str] = None) -> int:
        """
        Broadcast message to all connections.
        
        Args:
            message: Message to broadcast
            exclude_connections: Connections to exclude
            
        Returns:
            int: Number of connections that received the message
        """
        exclude_connections = exclude_connections or []
        sent_count = 0
        
        for connection_id, websocket in self.connections.items():
            if connection_id not in exclude_connections:
                try:
                    await websocket.send(json.dumps(message))
                    sent_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to broadcast to {connection_id}: {e}")
        
        self.logger.info(f"Broadcast message to {sent_count} connections")
        return sent_count
    
    async def close_connection(self, connection_id: str) -> bool:
        """
        Close specific connection.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            bool: Success status
        """
        if connection_id not in self.connections:
            return False
            
        try:
            await self.connections[connection_id].close()
            del self.connections[connection_id]
            self.connection_count -= 1
            
            self.logger.info(f"Connection {connection_id} closed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close connection {connection_id}: {e}")
            return False
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information.
        
        Returns:
            Dict: Connection information
        """
        return {
            "host": self.host,
            "port": self.port,
            "path": self.path,
            "enable_ssl": self.enable_ssl,
            "max_connections": self.max_connections,
            "active_connections": self.connection_count,
            "server_running": self.server is not None
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            if websockets is None:
                return {
                    "healthy": False,
                    "error": "websockets library not installed"
                }
            
            if self.server is None:
                return {
                    "healthy": False,
                    "error": "WebSocket server not running"
                }
            
            return {
                "healthy": True,
                "active_connections": self.connection_count,
                "max_connections": self.max_connections,
                "server_running": True
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }




