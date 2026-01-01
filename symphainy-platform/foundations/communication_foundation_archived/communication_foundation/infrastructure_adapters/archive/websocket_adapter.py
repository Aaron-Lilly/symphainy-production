#!/usr/bin/env python3
"""
WebSocket Adapter - Real-time Communication Infrastructure

WebSocket adapter that provides real-time communication infrastructure
for all realms using existing Public Works WebSocket abstractions.

WHAT (Infrastructure Adapter): I provide real-time WebSocket communication infrastructure
HOW (Infrastructure Implementation): I leverage Public Works WebSocket abstractions
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Import Public Works Foundation for WebSocket abstractions
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import DI Container for dependency injection
from foundations.di_container.di_container_service import DIContainerService

# Import existing WebSocket adapter from Public Works
from foundations.public_works_foundation.infrastructure_adapters.websocket_adapter import WebSocketAdapter as PublicWorksWebSocketAdapter

logger = logging.getLogger(__name__)


class WebSocketAdapter:
    """
    WebSocket Adapter - Real-time Communication Infrastructure
    
    Provides real-time WebSocket communication infrastructure for all realms
    using existing Public Works WebSocket abstractions.
    
    WHAT (Infrastructure Adapter): I provide real-time WebSocket communication infrastructure
    HOW (Infrastructure Implementation): I leverage Public Works WebSocket abstractions
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize WebSocket Adapter."""
        self.logger = logging.getLogger("WebSocketAdapter")
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Public Works WebSocket adapter
        self.public_works_websocket_adapter = None
        
        # WebSocket connections registry
        self.connections = {}
        
        # Realm-specific WebSocket managers
        self.realm_managers = {
            "smart_city": {},
            "business_enablement": {},
            "experience": {},
            "journey_solution": {}
        }
        
        # WebSocket configuration
        self.websocket_config = {
            "host": "localhost",
            "port": 8765,
            "path": "/websocket",
            "max_connections": 1000,
            "ping_interval": 30,
            "ping_timeout": 10
        }
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ WebSocket Adapter initialized")
    
    async def initialize(self):
        """Initialize WebSocket Adapter."""
        self.logger.info("🚀 Initializing WebSocket Adapter...")
        
        try:
            # Get WebSocket adapter from Public Works Foundation (required - no fallback)
            self.public_works_websocket_adapter = self.public_works_foundation.get_websocket_adapter()
            
            if not self.public_works_websocket_adapter:
                raise RuntimeError(
                    "WebSocket adapter not available from Public Works Foundation. "
                    "Ensure Public Works Foundation is initialized and provides websocket adapter."
                )
            
            # Initialize Public Works WebSocket adapter
            await self.public_works_websocket_adapter.initialize()
            
            # Setup WebSocket handlers
            await self._setup_websocket_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ WebSocket Adapter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WebSocket Adapter: {e}")
            raise
    
    async def _setup_websocket_handlers(self):
        """Setup WebSocket handlers for different realms."""
        self.logger.info("🔧 Setting up WebSocket handlers...")
        
        # Setup realm-specific handlers
        for realm in self.realm_managers.keys():
            await self._setup_realm_handler(realm)
        
        self.logger.info("✅ WebSocket handlers setup complete")
    
    async def _setup_realm_handler(self, realm: str):
        """Setup WebSocket handler for specific realm."""
        self.logger.info(f"🔧 Setting up WebSocket handler for {realm}...")
        
        # Create realm-specific handler
        async def realm_websocket_handler(websocket, path):
            """Handle WebSocket connections for specific realm."""
            client_id = f"{realm}_{datetime.now().timestamp()}"
            
            try:
                # Register connection
                await self._register_connection(client_id, realm, websocket)
                
                # Handle WebSocket messages
                async for message in websocket:
                    await self._handle_websocket_message(client_id, realm, message)
                    
            except Exception as e:
                self.logger.error(f"❌ WebSocket handler error for {realm}: {e}")
            finally:
                # Unregister connection
                await self._unregister_connection(client_id, realm)
        
        # Register handler with Public Works WebSocket adapter
        if self.public_works_websocket_adapter:
            await self.public_works_websocket_adapter.register_handler(
                path=f"/{realm}",
                handler=realm_websocket_handler
            )
        
        self.logger.info(f"✅ WebSocket handler setup complete for {realm}")
    
    async def _register_connection(self, client_id: str, realm: str, websocket):
        """Register WebSocket connection."""
        self.connections[client_id] = {
            "realm": realm,
            "websocket": websocket,
            "connected_at": datetime.now(),
            "last_ping": datetime.now()
        }
        
        self.realm_managers[realm][client_id] = self.connections[client_id]
        
        self.logger.info(f"✅ WebSocket connection registered: {client_id} for {realm}")
    
    async def _unregister_connection(self, client_id: str, realm: str):
        """Unregister WebSocket connection."""
        if client_id in self.connections:
            del self.connections[client_id]
        
        if client_id in self.realm_managers[realm]:
            del self.realm_managers[realm][client_id]
        
        self.logger.info(f"✅ WebSocket connection unregistered: {client_id} for {realm}")
    
    async def _handle_websocket_message(self, client_id: str, realm: str, message: str):
        """Handle WebSocket message."""
        try:
            # Parse message
            message_data = await self._parse_websocket_message(message)
            
            # Route message to appropriate handler
            await self._route_websocket_message(client_id, realm, message_data)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle WebSocket message: {e}")
    
    async def _parse_websocket_message(self, message: str) -> Dict[str, Any]:
        """Parse WebSocket message."""
        try:
            import json
            return json.loads(message)
        except json.JSONDecodeError:
            return {"type": "text", "content": message}
    
    async def _route_websocket_message(self, client_id: str, realm: str, message_data: Dict[str, Any]):
        """Route WebSocket message to appropriate handler."""
        message_type = message_data.get("type", "unknown")
        
        if message_type == "ping":
            await self._handle_ping(client_id, realm)
        elif message_type == "pong":
            await self._handle_pong(client_id, realm)
        elif message_type == "message":
            await self._handle_realm_message(client_id, realm, message_data)
        else:
            self.logger.warning(f"⚠️ Unknown WebSocket message type: {message_type}")
    
    async def _handle_ping(self, client_id: str, realm: str):
        """Handle ping message."""
        await self._send_websocket_message(client_id, {"type": "pong", "timestamp": datetime.now().isoformat()})
    
    async def _handle_pong(self, client_id: str, realm: str):
        """Handle pong message."""
        if client_id in self.connections:
            self.connections[client_id]["last_ping"] = datetime.now()
    
    async def _handle_realm_message(self, client_id: str, realm: str, message_data: Dict[str, Any]):
        """Handle realm-specific message."""
        # This would be implemented with actual realm-specific message handling
        self.logger.info(f"📨 Handling realm message for {realm}: {message_data}")
    
    async def start(self):
        """Start WebSocket Adapter."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting WebSocket Adapter...")
        
        try:
            # Start Public Works WebSocket adapter
            if self.public_works_websocket_adapter:
                await self.public_works_websocket_adapter.start()
            
            self.is_running = True
            self.logger.info("✅ WebSocket Adapter started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start WebSocket Adapter: {e}")
            raise
    
    async def stop(self):
        """Stop WebSocket Adapter."""
        self.logger.info("🛑 Stopping WebSocket Adapter...")
        
        try:
            # Stop Public Works WebSocket adapter
            if self.public_works_websocket_adapter:
                await self.public_works_websocket_adapter.stop()
            
            # Close all connections
            for client_id in list(self.connections.keys()):
                await self._unregister_connection(client_id, self.connections[client_id]["realm"])
            
            self.is_running = False
            self.logger.info("✅ WebSocket Adapter stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop WebSocket Adapter: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown WebSocket Adapter."""
        await self.stop()
        self.logger.info("🔌 WebSocket Adapter shutdown complete")
    
    # Public API methods
    
    async def send_websocket_message(self, client_id: str, message: Dict[str, Any]):
        """Send WebSocket message to specific client."""
        if client_id in self.connections:
            websocket = self.connections[client_id]["websocket"]
            try:
                import json
                await websocket.send(json.dumps(message))
                self.logger.info(f"✅ WebSocket message sent to {client_id}")
            except Exception as e:
                self.logger.error(f"❌ Failed to send WebSocket message to {client_id}: {e}")
    
    async def broadcast_to_realm(self, realm: str, message: Dict[str, Any]):
        """Broadcast message to all clients in realm."""
        if realm in self.realm_managers:
            for client_id in self.realm_managers[realm]:
                await self.send_websocket_message(client_id, message)
    
    async def get_connection_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information for client."""
        return self.connections.get(client_id)
    
    async def get_realm_connections(self, realm: str) -> List[str]:
        """Get all connection IDs for realm."""
        return list(self.realm_managers.get(realm, {}).keys())
    
    async def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return len(self.connections)
    
    async def get_realm_connection_count(self, realm: str) -> int:
        """Get number of active connections for realm."""
        return len(self.realm_managers.get(realm, {}))
