#!/usr/bin/env python3
"""
Messaging Adapter - Asynchronous Communication Infrastructure

Messaging adapter that provides asynchronous communication infrastructure
for all realms using existing Public Works messaging abstractions.

WHAT (Infrastructure Adapter): I provide asynchronous messaging communication infrastructure
HOW (Infrastructure Implementation): I leverage Public Works messaging abstractions
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# Import Public Works Foundation for messaging abstractions
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import DI Container for dependency injection
from foundations.di_container.di_container_service import DIContainerService

# Import existing messaging abstractions from Public Works
from foundations.public_works_foundation.infrastructure_abstractions.messaging_abstraction import MessagingAbstraction

logger = logging.getLogger(__name__)


class MessagingAdapter:
    """
    Messaging Adapter - Asynchronous Communication Infrastructure
    
    Provides asynchronous messaging communication infrastructure for all realms
    using existing Public Works messaging abstractions.
    
    WHAT (Infrastructure Adapter): I provide asynchronous messaging communication infrastructure
    HOW (Infrastructure Implementation): I leverage Public Works messaging abstractions
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize Messaging Adapter."""
        self.logger = logging.getLogger("MessagingAdapter")
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Public Works messaging abstraction
        self.messaging_abstraction = None
        
        # Message queues for different realms
        self.realm_queues = {
            "smart_city": [],
            "business_enablement": [],
            "experience": [],
            "journey_solution": []
        }
        
        # Message handlers
        self.message_handlers = {}
        
        # Messaging configuration
        self.messaging_config = {
            "default_retention_hours": 168,  # 7 days
            "max_messages_per_recipient": 1000,
            "message_timeout_seconds": 300,
            "retry_attempts": 3,
            "retry_delay_seconds": 5
        }
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🏗️ Messaging Adapter initialized")
    
    async def initialize(self):
        """Initialize Messaging Adapter."""
        self.logger.info("🚀 Initializing Messaging Adapter...")
        
        try:
            # Get messaging abstraction from Public Works Foundation
            self.messaging_abstraction = self.public_works_foundation.get_messaging_abstraction()
            
            if not self.messaging_abstraction:
                # Create new messaging abstraction if not available (migrated from Post Office)
                from foundations.public_works_foundation.infrastructure_adapters.redis_messaging_adapter import RedisMessagingAdapter
                from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter
                
                redis_messaging_adapter = RedisMessagingAdapter()
                config_adapter = ConfigAdapter()
                
                self.messaging_abstraction = MessagingAbstraction(
                    messaging_adapter=redis_messaging_adapter,
                    config_adapter=config_adapter
                )
            
            # Initialize messaging abstraction
            await self.messaging_abstraction.initialize()
            
            # Setup message handlers
            await self._setup_message_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ Messaging Adapter initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Messaging Adapter: {e}")
            raise
    
    async def _setup_message_handlers(self):
        """Setup message handlers for different realms."""
        self.logger.info("🔧 Setting up message handlers...")
        
        # Setup realm-specific message handlers
        for realm in self.realm_queues.keys():
            await self._setup_realm_message_handler(realm)
        
        self.logger.info("✅ Message handlers setup complete")
    
    async def _setup_realm_message_handler(self, realm: str):
        """Setup message handler for specific realm."""
        self.logger.info(f"🔧 Setting up message handler for {realm}...")
        
        # Create realm-specific message handler
        async def realm_message_handler(message_data: Dict[str, Any]):
            """Handle messages for specific realm."""
            try:
                # Process message
                await self._process_realm_message(realm, message_data)
                
            except Exception as e:
                self.logger.error(f"❌ Message handler error for {realm}: {e}")
        
        # Register handler
        self.message_handlers[realm] = realm_message_handler
        
        self.logger.info(f"✅ Message handler setup complete for {realm}")
    
    async def _process_realm_message(self, realm: str, message_data: Dict[str, Any]):
        """Process message for specific realm."""
        message_type = message_data.get("type", "unknown")
        message_content = message_data.get("content", {})
        
        if message_type == "notification":
            await self._handle_notification_message(realm, message_content)
        elif message_type == "command":
            await self._handle_command_message(realm, message_content)
        elif message_type == "response":
            await self._handle_response_message(realm, message_content)
        else:
            self.logger.warning(f"⚠️ Unknown message type: {message_type}")
    
    async def _handle_notification_message(self, realm: str, message_content: Dict[str, Any]):
        """Handle notification message."""
        self.logger.info(f"📨 Handling notification message for {realm}: {message_content}")
        # This would be implemented with actual notification handling
    
    async def _handle_command_message(self, realm: str, message_content: Dict[str, Any]):
        """Handle command message."""
        self.logger.info(f"📨 Handling command message for {realm}: {message_content}")
        # This would be implemented with actual command handling
    
    async def _handle_response_message(self, realm: str, message_content: Dict[str, Any]):
        """Handle response message."""
        self.logger.info(f"📨 Handling response message for {realm}: {message_content}")
        # This would be implemented with actual response handling
    
    async def start(self):
        """Start Messaging Adapter."""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 Starting Messaging Adapter...")
        
        try:
            # Start messaging abstraction
            if self.messaging_abstraction:
                await self.messaging_abstraction.start()
            
            self.is_running = True
            self.logger.info("✅ Messaging Adapter started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Messaging Adapter: {e}")
            raise
    
    async def stop(self):
        """Stop Messaging Adapter."""
        self.logger.info("🛑 Stopping Messaging Adapter...")
        
        try:
            # Stop messaging abstraction
            if self.messaging_abstraction:
                await self.messaging_abstraction.stop()
            
            self.is_running = False
            self.logger.info("✅ Messaging Adapter stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop Messaging Adapter: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown Messaging Adapter."""
        await self.stop()
        self.logger.info("🔌 Messaging Adapter shutdown complete")
    
    # Public API methods
    
    async def send_message(self, target_realm: str, message_type: str, message_content: Dict[str, Any], 
                         sender: str = "system", priority: str = "normal") -> Optional[str]:
        """Send message to target realm."""
        try:
            message_data = {
                "type": message_type,
                "content": message_content,
                "sender": sender,
                "target_realm": target_realm,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            
            # Use Public Works messaging abstraction
            if self.messaging_abstraction:
                message_context = await self.messaging_abstraction.send_message(
                    message_type=message_type,
                    sender=sender,
                    recipient=target_realm,
                    message_content=message_content
                )
                
                if message_context:
                    self.logger.info(f"✅ Message sent to {target_realm}: {message_type}")
                    return message_context.message_id
                else:
                    self.logger.error(f"❌ Failed to send message to {target_realm}")
                    return None
            else:
                self.logger.error("❌ Messaging abstraction not available")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send message to {target_realm}: {e}")
            return None
    
    async def receive_message(self, realm: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Receive message for realm."""
        try:
            # Use Public Works messaging abstraction
            if self.messaging_abstraction:
                message_context = await self.messaging_abstraction.receive_message(
                    recipient=realm,
                    message_id=message_id
                )
                
                if message_context:
                    return {
                        "message_id": message_context.message_id,
                        "type": message_context.message_type,
                        "content": message_context.message_content,
                        "sender": message_context.sender,
                        "timestamp": message_context.timestamp
                    }
                else:
                    return None
            else:
                self.logger.error("❌ Messaging abstraction not available")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to receive message for {realm}: {e}")
            return None
    
    async def get_message_queue(self, realm: str) -> List[Dict[str, Any]]:
        """Get message queue for realm."""
        return self.realm_queues.get(realm, [])
    
    async def clear_message_queue(self, realm: str):
        """Clear message queue for realm."""
        self.realm_queues[realm] = []
        self.logger.info(f"✅ Message queue cleared for {realm}")
    
    async def get_messaging_stats(self) -> Dict[str, Any]:
        """Get messaging statistics."""
        return {
            "total_queues": len(self.realm_queues),
            "queue_sizes": {realm: len(queue) for realm, queue in self.realm_queues.items()},
            "is_running": self.is_running,
            "is_initialized": self.is_initialized
        }
