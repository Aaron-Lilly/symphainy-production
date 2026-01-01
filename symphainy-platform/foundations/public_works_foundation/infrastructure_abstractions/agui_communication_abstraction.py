#!/usr/bin/env python3
"""
AGUI Communication Abstraction

Infrastructure abstraction for AGUI communication using WebSocket.
Implements AGUICommunicationProtocol using WebSocketAdapter.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
import logging
import uuid

from ..abstraction_contracts.agui_communication_protocol import (
    AGUICommunicationProtocol, AGUIMessage, AGUIResponse, AGUIEvent
)
from ..infrastructure_adapters.websocket_adapter import WebSocketAdapter

class AGUICommunicationAbstraction(AGUICommunicationProtocol):
    """AGUI communication abstraction using WebSocket."""
    
    def __init__(self, websocket_adapter: WebSocketAdapter, di_container=None, **kwargs):
        """
        Initialize AGUI communication abstraction.
        
        Args:
            websocket_adapter: WebSocket adapter instance
            di_container: Dependency injection container
        """
        self.websocket_adapter = websocket_adapter
        self.di_container = di_container
        self.service_name = "agui_communication_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # AGUI configuration
        self.message_handlers = {}
        self.event_handlers = {}
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the AGUI communication abstraction."""
        try:
            # Set up message handler
            self.websocket_adapter.message_handler = self._handle_agui_message
            
            self.logger.info("✅ AGUI communication abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AGUI communication abstraction: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _handle_agui_message(self, connection_id: str, data: Dict[str, Any]) -> None:
        """Handle AGUI message from WebSocket."""
        try:
            message_type = data.get("type", "unknown")
            
            if message_type == "agui_message":
                await self._process_agui_message(connection_id, data)
            elif message_type == "agui_event":
                await self._process_agui_event(connection_id, data)
            elif message_type == "ping":
                await self._send_pong(connection_id)
            else:
                self.logger.warning(f"Unknown AGUI message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Error handling AGUI message from {connection_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _process_agui_message(self, connection_id: str, data: Dict[str, Any]) -> None:
        """Process AGUI message."""
        try:
            message = AGUIMessage(
                message_id=data.get("message_id"),
                action=data.get("action"),
                payload=data.get("payload", {}),
                timestamp=datetime.now(),
                connection_id=connection_id
            )
            
            # Route to appropriate handler
            if message.action in self.message_handlers:
                handler = self.message_handlers[message.action]
                response = await handler(message)
                await self._send_response(connection_id, response)
            else:
                # Default handler
                response = AGUIResponse(
                    response_id=str(uuid.uuid4()),
                    message_id=message.message_id,
                    success=False,
                    error=f"No handler for action: {message.action}",
                    timestamp=datetime.now()
                )
                await self._send_response(connection_id, response)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to process AGUI message: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _process_agui_event(self, connection_id: str, data: Dict[str, Any]) -> None:
        """Process AGUI event."""
        try:
            event = AGUIEvent(
                event_id=data.get("event_id"),
                event_type=data.get("event_type"),
                data=data.get("data", {}),
                timestamp=datetime.now(),
                connection_id=connection_id
            )
            
            # Route to appropriate handler
            if event.event_type in self.event_handlers:
                handler = self.event_handlers[event.event_type]
                await handler(event)
            else:
                self.logger.debug(f"No handler for event type: {event.event_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to process AGUI event: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _send_response(self, connection_id: str, response: AGUIResponse) -> None:
        """Send AGUI response."""
        try:
            response_data = {
                "type": "agui_response",
                "response_id": response.response_id,
                "message_id": response.message_id,
                "success": response.success,
                "data": response.data,
                "error": response.error,
                "timestamp": response.timestamp.isoformat()
            }
            
            await self.websocket_adapter.send_message(connection_id, response_data)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send AGUI response: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _send_error_response(self, connection_id: str, error: str) -> None:
        """Send error response."""
        try:
            error_response = {
                "type": "agui_response",
                "success": False,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_adapter.send_message(connection_id, error_response)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send error response: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _send_pong(self, connection_id: str) -> None:
        """Send pong response."""
        try:
            pong_data = {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_adapter.send_message(connection_id, pong_data)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send pong: {e}")
            raise  # Re-raise for service layer to handle
    
    # ============================================================================
    # AGUI COMMUNICATION PROTOCOL IMPLEMENTATION
    # ============================================================================
    
    async def send_message(self, connection_id: str, message: AGUIMessage) -> bool:
        """
        Send AGUI message.
        
        Args:
            connection_id: Connection ID
            message: AGUI message
            
        Returns:
            bool: Success status
        """
        try:
            message_data = {
                "type": "agui_message",
                "message_id": message.message_id,
                "action": message.action,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat()
            }
            
            success = await self.websocket_adapter.send_message(connection_id, message_data)
            
            if success:
                self.logger.info(f"✅ AGUI message sent to {connection_id}: {message.action}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send AGUI message: {e}")
            raise  # Re-raise for service layer to handle
    
    async def broadcast_message(self, message: AGUIMessage, exclude_connections: List[str] = None) -> int:
        """
        Broadcast AGUI message.
        
        Args:
            message: AGUI message
            exclude_connections: Connections to exclude
            
        Returns:
            int: Number of connections that received the message
        """
        try:
            message_data = {
                "type": "agui_message",
                "message_id": message.message_id,
                "action": message.action,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat()
            }
            
            sent_count = await self.websocket_adapter.broadcast_message(
                message_data, exclude_connections
            )
            
            self.logger.info(f"✅ AGUI message broadcasted to {sent_count} connections")
            
            return sent_count
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast AGUI message: {e}")
            raise  # Re-raise for service layer to handle
    
    async def send_event(self, connection_id: str, event: AGUIEvent) -> bool:
        """
        Send AGUI event.
        
        Args:
            connection_id: Connection ID
            event: AGUI event
            
        Returns:
            bool: Success status
        """
        try:
            event_data = {
                "type": "agui_event",
                "event_id": event.event_id,
                "event_type": event.event_type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }
            
            success = await self.websocket_adapter.send_message(connection_id, event_data)
            
            if success:
                self.logger.info(f"✅ AGUI event sent to {connection_id}: {event.event_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send AGUI event: {e}")
            raise  # Re-raise for service layer to handle
    
    async def broadcast_event(self, event: AGUIEvent, exclude_connections: List[str] = None) -> int:
        """
        Broadcast AGUI event.
        
        Args:
            event: AGUI event
            exclude_connections: Connections to exclude
            
        Returns:
            int: Number of connections that received the event
        """
        try:
            event_data = {
                "type": "agui_event",
                "event_id": event.event_id,
                "event_type": event.event_type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }
            
            sent_count = await self.websocket_adapter.broadcast_message(
                event_data, exclude_connections
            )
            
            self.logger.info(f"✅ AGUI event broadcasted to {sent_count} connections")
            
            return sent_count
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast AGUI event: {e}")
            raise  # Re-raise for service layer to handle
    
    def register_message_handler(self, action: str, handler: Callable):
        """
        Register message handler.
        
        Args:
            action: Message action
            handler: Handler function
        """
        self.message_handlers[action] = handler
        self.logger.info(f"Message handler registered for action: {action}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register event handler.
        
        Args:
            event_type: Event type
            handler: Handler function
        """
        self.event_handlers[event_type] = handler
        self.logger.info(f"Event handler registered for type: {event_type}")
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information.
        
        Returns:
            Dict: Connection information
        """
        try:
            result = await self.websocket_adapter.get_connection_info()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection info: {e}")
            raise  # Re-raise for service layer to handle
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            websocket_health = await self.websocket_adapter.health_check()
            
            health_status = {
                "healthy": websocket_health.get("healthy", False),
                "websocket_adapter": websocket_health,
                "message_handlers": len(self.message_handlers),
                "event_handlers": len(self.event_handlers),
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise  # Re-raise for service layer to handle
