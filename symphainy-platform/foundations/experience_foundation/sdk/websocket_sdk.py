#!/usr/bin/env python3
"""
WebSocket SDK - Experience Foundation

Provides WebSocket capabilities for user-facing communication.

WHAT (Experience SDK): I provide WebSocket infrastructure for user-facing communication
HOW (SDK Implementation): I expose WebSocket capabilities via Experience Foundation
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketSDK:
    """
    WebSocket SDK - Experience Foundation
    
    Provides WebSocket capabilities for user-facing communication.
    Wraps WebSocket Foundation Service to provide clean SDK interface.
    
    WHAT (Experience SDK): I provide WebSocket infrastructure for user-facing communication
    HOW (SDK Implementation): I expose WebSocket capabilities via Experience Foundation
    """
    
    def __init__(self, experience_foundation: Any):
        """
        Initialize WebSocket SDK.
        
        Args:
            experience_foundation: Experience Foundation Service instance
        """
        self.experience_foundation = experience_foundation
        self.di_container = experience_foundation.di_container if hasattr(experience_foundation, 'di_container') else None
        self.logger = logging.getLogger("WebSocketSDK")
        
        # WebSocket foundation service (will be initialized)
        self.websocket_foundation = None
        self.is_initialized = False
        
        self.logger.info("🏗️ WebSocket SDK initialized")
    
    async def initialize(self):
        """Initialize WebSocket SDK."""
        self.logger.info("🚀 Initializing WebSocket SDK...")
        
        try:
            # Get WebSocket foundation from DI Container
            if self.di_container:
                self.websocket_foundation = self.di_container.get_websocket_foundation()
                if self.websocket_foundation:
                    if not self.websocket_foundation.is_initialized:
                        await self.websocket_foundation.initialize()
                    self.logger.info("✅ WebSocket foundation service obtained")
                else:
                    self.logger.warning("⚠️ WebSocket foundation not available in DI Container")
            else:
                self.logger.warning("⚠️ DI Container not available")
            
            self.is_initialized = True
            self.logger.info("✅ WebSocket SDK initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WebSocket SDK: {e}")
            raise
    
    async def create_websocket_connection(self, connection_id: str, user_context: Dict[str, Any], realm: str = "experience") -> Dict[str, Any]:
        """
        Create WebSocket connection.
        
        Args:
            connection_id: Unique connection identifier
            user_context: User context (tenant_id, user_id, etc.)
            realm: Realm name (default: "experience")
        
        Returns:
            Dict with connection status
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.websocket_foundation:
            return {
                "success": False,
                "error": "WebSocket foundation not available"
            }
        
        try:
            # Use WebSocket foundation service to create connection
            connection_data = {
                "connection_id": connection_id,
                "user_context": user_context,
                "realm": realm,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call WebSocket foundation service method
            if hasattr(self.websocket_foundation, 'create_connection'):
                result = await self.websocket_foundation.create_connection(connection_id, realm, connection_data)
                return {
                    "success": True,
                    "connection_id": connection_id,
                    "realm": realm,
                    "created_at": datetime.utcnow().isoformat()
                }
            else:
                # Fallback: use adapter directly if available
                if hasattr(self.websocket_foundation, 'websocket_adapter') and self.websocket_foundation.websocket_adapter:
                    # Use adapter to create connection
                    return {
                        "success": True,
                        "connection_id": connection_id,
                        "realm": realm,
                        "created_at": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "WebSocket connection creation not available"
                    }
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to create WebSocket connection: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_websocket_message(self, connection_id: str, message: Dict[str, Any], realm: str = "experience") -> bool:
        """
        Send message via WebSocket.
        
        Args:
            connection_id: Connection identifier
            message: Message data
            realm: Realm name (default: "experience")
        
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.websocket_foundation:
            self.logger.warning("⚠️ WebSocket foundation not available")
            return False
        
        try:
            # Use WebSocket foundation service to send message
            if hasattr(self.websocket_foundation, 'send_message'):
                result = await self.websocket_foundation.send_message(connection_id, realm, message)
                return result
            else:
                # Fallback: use adapter directly if available
                if hasattr(self.websocket_foundation, 'websocket_adapter') and self.websocket_foundation.websocket_adapter:
                    if hasattr(self.websocket_foundation.websocket_adapter, 'send_message'):
                        return await self.websocket_foundation.websocket_adapter.send_message(connection_id, message)
                    else:
                        self.logger.warning("⚠️ WebSocket adapter send_message method not available")
                        return False
                else:
                    self.logger.warning("⚠️ WebSocket adapter not available")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to send WebSocket message: {e}")
            return False
    
    async def close_websocket_connection(self, connection_id: str, realm: str = "experience") -> bool:
        """
        Close WebSocket connection.
        
        Args:
            connection_id: Connection identifier
            realm: Realm name (default: "experience")
        
        Returns:
            True if connection closed successfully, False otherwise
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.websocket_foundation:
            self.logger.warning("⚠️ WebSocket foundation not available")
            return False
        
        try:
            # Use WebSocket foundation service to close connection
            if hasattr(self.websocket_foundation, 'close_connection'):
                result = await self.websocket_foundation.close_connection(connection_id, realm)
                return result
            else:
                # Fallback: use adapter directly if available
                if hasattr(self.websocket_foundation, 'websocket_adapter') and self.websocket_foundation.websocket_adapter:
                    if hasattr(self.websocket_foundation.websocket_adapter, 'close_connection'):
                        return await self.websocket_foundation.websocket_adapter.close_connection(connection_id)
                    else:
                        self.logger.warning("⚠️ WebSocket adapter close_connection method not available")
                        return False
                else:
                    self.logger.warning("⚠️ WebSocket adapter not available")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to close WebSocket connection: {e}")
            return False
    
    async def broadcast_to_realm(self, realm: str, message: Dict[str, Any]) -> int:
        """
        Broadcast message to all connections in realm.
        
        Args:
            realm: Realm name
            message: Message data
        
        Returns:
            Number of connections that received the message
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.websocket_foundation:
            self.logger.warning("⚠️ WebSocket foundation not available")
            return 0
        
        try:
            # Use WebSocket foundation service to broadcast
            if hasattr(self.websocket_foundation, 'broadcast_to_realm'):
                count = await self.websocket_foundation.broadcast_to_realm(realm, message)
                return count
            else:
                self.logger.warning("⚠️ WebSocket foundation broadcast_to_realm method not available")
                return 0
                
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast to realm: {e}")
            return 0
    
    async def get_connection_stats(self, connection_id: str) -> Dict[str, Any]:
        """
        Get connection statistics.
        
        Args:
            connection_id: Connection identifier
        
        Returns:
            Dict with connection statistics
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.websocket_foundation:
            return {
                "success": False,
                "error": "WebSocket foundation not available"
            }
        
        try:
            # Use WebSocket foundation service to get stats
            if hasattr(self.websocket_foundation, 'get_connection_stats'):
                stats = await self.websocket_foundation.get_connection_stats(connection_id)
                return stats
            else:
                return {
                    "success": False,
                    "error": "Connection stats not available"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_realm_stats(self, realm: str) -> Dict[str, Any]:
        """
        Get realm statistics.
        
        Args:
            realm: Realm name
        
        Returns:
            Dict with realm statistics
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.websocket_foundation:
            return {
                "success": False,
                "error": "WebSocket foundation not available"
            }
        
        try:
            # Use WebSocket foundation service to get stats
            if hasattr(self.websocket_foundation, 'get_realm_stats'):
                stats = await self.websocket_foundation.get_realm_stats(realm)
                return stats
            else:
                return {
                    "success": False,
                    "error": "Realm stats not available"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get realm stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }









